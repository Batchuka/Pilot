from invoke import task
import os
import json
import configparser
from colorama import init, Fore, Style

# Inicializa a colorama
init(autoreset=True)

def log(message):
    print(message)

def get_config(config_file='project.conf'):
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        raise FileNotFoundError(Fore.RED + Style.BRIGHT + f"Arquivo de configuração '{config_file}' não encontrado.")
    config.read(config_file)
    if 'aws' not in config or 'deploy' not in config:
        raise KeyError(Fore.RED + Style.BRIGHT + "Seções 'aws' ou 'deploy' faltando no arquivo de configuração.")
    return config

def get_codeartifact_url(c, aws_config):
    try:
        command = f"aws codeartifact get-authorization-token --domain {aws_config['codeartifact_domain']} --domain-owner {aws_config['aws_account_id']} --query authorizationToken --output text"
        result = c.run(command, hide=True)
        codeartifact_token = result.stdout.strip()

        print('Successfully obtained codeartifact token')

        trusted_host = f"https://aws:{codeartifact_token}@{aws_config['codeartifact_domain']}-{aws_config['aws_account_id']}.d.codeartifact.{aws_config['aws_default_region']}.amazonaws.com/pypi/{aws_config['codeartifact_repository']}/simple/"

        return trusted_host

    except KeyError as e:
        print(Fore.RED + Style.BRIGHT + f"Missing environment variable for CodeArtifact: {e}")
        raise
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Error retrieving CodeArtifact URL: {e}")
        raise

def verificar_existencia_imagem(c, image_name, version):
    result = c.run(f"docker images -q {image_name}:{version}", hide=True, warn=True)
    return bool(result.stdout.strip())

def remover_imagem(c, image_name, version):
    log(f"Removendo imagem existente {image_name}:{version}...")
    c.run(f"docker rmi -f {image_name}:{version}")

def verificar_contexto_docker(c, expected_context):
    result = c.run("docker context show", hide=True, warn=True)
    current_context = result.stdout.strip()
    if current_context != expected_context:
        raise Exception(Fore.RED + Style.BRIGHT + f"Contexto Docker incorreto. Esperado: {expected_context}, Atual: {current_context}")

@task
def deploy(c):
    try:
        config = get_config()
        aws_config = config['aws']
        deploy_config = config['deploy']

        # Verificar o contexto Docker
        verificar_contexto_docker(c, deploy_config['docker_context'])

        # Obter a URL do CodeArtifact com token
        CODEARTIFACT_REPOSITORY_url = get_codeartifact_url(c, aws_config)

        # Obter a versão do pacote do CodeArtifact
        log("Obtendo a versão do pacote do CodeArtifact...")
        command = f"aws codeartifact list-package-versions --domain {aws_config['codeartifact_domain']} --domain-owner {aws_config['aws_account_id']} --repository {aws_config['codeartifact_repository']} --package {deploy_config['package_name']} --format pypi"
        result = c.run(command, hide=True, warn=True)
        
        if result.failed:
            raise Exception(Fore.RED + Style.BRIGHT + "Failed to list package versions from CodeArtifact")

        package_info = json.loads(result.stdout)
        package_version = package_info['versions'][-1]['version']
        image_name = aws_config['codeartifact_repository_name']
        dockerfile_path = os.path.abspath(os.getcwd())

        # Verifica se a imagem já existe e remove se necessário
        if verificar_existencia_imagem(c, image_name, package_version):
            remover_imagem(c, image_name, package_version)

        # Build da imagem Docker
        log("Buildando a imagem Docker...")
        c.run(f"docker build --build-arg CODEARTIFACT_REPOSITORY_URL={CODEARTIFACT_REPOSITORY_url} -t {image_name}:{package_version} {dockerfile_path}")

        # Taguear a imagem com a versão do pacote CodeArtifact e 'latest'
        log("Tagueando a imagem como 'latest'...")
        c.run(f"docker tag {image_name}:{package_version} {image_name}:latest")

        log("Deploy completado com sucesso!")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + "ERROR: " + str(e))

@task
def publish(ctx, project_path='.'):
    print(f"{BLUE} =========== Publishing Package on CodeArtifact ============ {RESET}")

    try:
        project_path = os.path.abspath(project_path)

        # Commit, tag e push
        summary = input("Enter commit summary: ")
        description = input("Enter commit description: ")

        latest_version = get_latest_version_tag()
        suggested_version = increment_version(latest_version.strip('v'))
        new_version = input(f"Enter new version (suggested: {suggested_version}): ") or suggested_version

        branch = os.popen('git branch --show-current').read().strip()

        os.system("git add .")
        os.system(f"git commit -m 'Summary: {summary} | Description: {description}'")
        os.system(f"git tag -a v{new_version} -m 'Release version {new_version}'")
        os.system(f"git push origin {branch} v{new_version}")

        # Build
        build(ctx, project_path='.')

        project_config = get_project_config(project_path)

        PROJECT_NAME    = project_config['project_name']
        PROJECT_VERSION = project_config['version']

        # Autenticar no CodeArtifact para client twine
        ctx.run(f"aws codeartifact login --tool twine --repository wmt-python-repository --domain wmt-libraries --domain-owner 435062120355 --region us-east-1", echo=True)

        # Publicar o pacote no CodeArtifact usando twine
        ctx.run(f"twine upload --repository codeartifact dist/*", echo=True)

        print(f"Package {PROJECT_NAME} was successfuly published on version {PROJECT_VERSION}")

    except Exception as e:
        print(f"Error during publishing process: {e}")

