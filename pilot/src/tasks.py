# pilot/src/tasks.py
import os
import json
import configparser
from invoke import task #type:ignore

from pilot.src.log import log
from pilot.src.docker import verificar_contexto_docker, remover_imagem, verificar_existencia_imagem
from pilot.src.aws import get_codeartifact_url
from pilot.src.git import GitManager
from pilot.src.pyproject import get_project_config, build

@task
def deploy(c):
    try:
        config = get_project_config('.')
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
            raise Exception("Failed to list package versions from CodeArtifact")

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
        log(f"ERROR: {str(e)}", "ERROR")

@task
def publish(ctx, project_path='.'):
    try:
        log(f"Publishing Package on CodeArtifact...")

        project_path = os.path.abspath(project_path)

        # Commit, tag e push
        summary = input("Enter commit summary: ")
        description = input("Enter commit description: ")

        git_manager = GitManager(project_path)
        latest_version = git_manager.get_latest_version_tag()
        suggested_version = git_manager.increment_version(latest_version.strip('v'))
        new_version = input(f"Enter new version (suggested: {suggested_version}): ") or suggested_version

        branch = git_manager.get_current_branch()

        git_manager.commit_and_tag(summary, description, new_version, branch)

        # Build
        build(ctx, project_path=project_path)

        project_config = get_project_config(project_path)
        PROJECT_NAME    = project_config['project_name']
        PROJECT_VERSION = project_config['version']

        # Autenticar no CodeArtifact para client twine
        ctx.run(f"aws codeartifact login --tool twine --repository {project_config['codeartifact_repository']} --domain {project_config['codeartifact_domain']} --domain-owner {project_config['aws_account_id']} --region {project_config['aws_default_region']}", echo=True)

        # Publicar o pacote no CodeArtifact usando twine
        ctx.run(f"twine upload --repository codeartifact dist/*", echo=True)

        log(f"Package {PROJECT_NAME} was successfuly published on version {PROJECT_VERSION}")
    except Exception as e:
        log(f"Error during publishing process: {e}", "ERROR")

@task
def aws(c, output_path='.'):
    output_path = os.path.abspath(output_path)
    config_file = os.path.join(output_path, 'project.conf')
    
    config = configparser.ConfigParser()

    # Verificar se o arquivo de configuração já existe
    if os.path.exists(config_file):
        config.read(config_file)
        
        # Verificar se a seção 'aws' já existe no arquivo de configuração
        if 'aws' in config:
            log(f"The 'aws' section already exists in {config_file}. No changes made.")
            return
    else:
        # Se o arquivo não existir, criar uma nova instância de ConfigParser
        config = configparser.ConfigParser()

    # Solicitar as informações ao usuário
    aws_access_key_id = input('Enter AWS Access Key ID: ')
    aws_secret_access_key = input('Enter AWS Secret Access Key: ')
    aws_default_region = input('Enter AWS Default Region: ')
    aws_account_id = input('Enter AWS Account ID: ')
    codeartifact_repository = input('Enter CodeArtifact Repository: ')
    codeartifact_domain = input('Enter CodeArtifact Domain: ')

    # Adicionar ou atualizar as configurações de AWS
    config['aws'] = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'aws_default_region': aws_default_region,
        'aws_account_id': aws_account_id,
        'codeartifact_repository': codeartifact_repository,
        'codeartifact_domain': codeartifact_domain
    }

    # Escrever as configurações no arquivo de configuração
    with open(config_file, 'w') as configfile:
        config.write(configfile)

    log(f"Configurations have been updated in {config_file}")