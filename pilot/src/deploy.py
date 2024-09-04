import os

from pilot.base.manager import BaseManager
from pilot.base.pipeline import BaseDeployPipeline
from pilot.default.deploy import DEPLOY_DEFAULTS
from pilot.src.docker import DockerManager
from pilot.src.aws import AWSManager

SECTION_NAME = 'deploy'
DEFAULT_SECTION = 'default_deploy'

class DeployManager(BaseManager):
    def __init__(self):
        super().__init__()
        self.section_name = SECTION_NAME
        self.default_section = DEFAULT_SECTION
        self.pipeline = None

    def init(self, **kwargs):
        if not self.config.has_section(self.section_name):
            self.config.add_section(self.section_name)

        for key, value in DEPLOY_DEFAULTS.items():
            self.config.set(self.section_name, key, kwargs.get(key, value)) 

        self.save_config()

    def select_pipeline(self):
        # Certifique-se de que o section_name está definido
        pipeline_type = self.config[self.section_name]['pipeline_type']

        if pipeline_type == 'remote_docker':
            self.pipeline = RemoteDockerDeployPipeline()
        elif pipeline_type == 'ecr':
            self.pipeline = EcrDeployPipeline()
        else:
            self.log.error(f"Pipeline '{pipeline_type}' não suportado.")

    def execute_deploy(self):
        self.select_pipeline()
        if self.pipeline:
            self.pipeline.execute()
        else:
            self.log.error("Pipeline não selecionado.")

    def update(self, **kwargs):
        raise NotImplementedError


class RemoteDockerDeployPipeline(BaseDeployPipeline):
    def __init__(self):
        super().__init__()
        self.section_name = SECTION_NAME
        self.default_section = DEFAULT_SECTION
        self.docker_manager = DockerManager()  # Inicializa o gerenciador Docker
        self.aws_manager = AWSManager()        # Inicializa o gerenciador AWS

    def execute(self):
        """Pipeline para buildar e publicar containers em máquinas remotas"""
        try:
            # 1. Verificar o contexto Docker usando o contexto armazenado
            self.docker_manager.mudar_contexto_docker(self.config['docker']['docker_context'])

            # 2. Obter a URL do CodeArtifact com token
            codeartifact_url = self.aws_manager.get_codeartifact_url()

            # 3. Obter a versão do pacote do CodeArtifact
            package_info = self.aws_manager.get_package_info(self.config['publish']['package_name'])

            # 4. Ordena as versões pela chave 'version' e retorna a última
            latest_package = max(package_info, key=lambda v: list(map(int, v['version'].split('.')))) #type:ignore
            latest_version = latest_package['version']
            self.log.info(f"Última versão do pacote '{self.config['publish']['package_name']}' obtida: {latest_version}")

            image_name = self.config['publish']['package_name']
            dockerfile_path = os.path.abspath(os.getcwd())

            # 5. Verifica se a imagem já existe e remove se necessário
            if self.docker_manager.verificar_existencia_imagem(image_name, latest_version):
                self.docker_manager.remover_imagem(image_name, latest_version)

            # 6. Build da imagem Docker
            self.docker_manager.build_docker_image(dockerfile_path, image_name, latest_version, codeartifact_url)

            # 7. Taguear a imagem com a versão do pacote
            self.docker_manager.tag_image(image_name, latest_version, "latest")

            self.log.info("Deploy completado com sucesso!")

        except Exception as e:
            self.log.error(str(e))


class EcrDeployPipeline(BaseDeployPipeline):
    def __init__(self):
        super().__init__()
        self.section_name = SECTION_NAME
        self.default_section = DEFAULT_SECTION
        self.docker_manager = DockerManager()  # Inicializa o gerenciador Docker
        self.aws_manager = AWSManager()        # Inicializa o gerenciador AWS
    
    def execute(self):
        """Pipeline para buildar e enviar uma imagem Docker para o ECR"""
        try:

            # 0. Verificar o contexto Docker usando o contexto armazenado
            self.docker_manager.mudar_contexto_docker('default')

            # 1. Obter a URL do CodeArtifact com token
            codeartifact_url = self.aws_manager.get_codeartifact_url()

            # 2. Obter a versão do pacote do CodeArtifact
            package_info = self.aws_manager.get_package_info(self.config['publish']['package_name'])

            # 3. Ordena as versões pela chave 'version' e retorna a última
            latest_package = max(package_info, key=lambda v: list(map(int, v['version'].split('.')))) #type:ignore
            latest_version = latest_package['version']
            self.log.info(f"Última versão do pacote '{self.config['publish']['package_name']}' obtida: {latest_version}")

            image_name = self.config['publish']['package_name']
            dockerfile_path = os.path.abspath(os.getcwd())

            # 4. Verifica se a imagem já existe e remove se necessário
            if self.docker_manager.verificar_existencia_imagem(image_name, latest_version):
                self.docker_manager.remover_imagem(image_name, latest_version)

            # 5. Build da imagem Docker
            self.docker_manager.build_docker_image(dockerfile_path, image_name, latest_version, codeartifact_url)

            # 6. Autenticar no ECR
            region = self.config.get('aws', 'aws_default_region', fallback='us-east-1')
            account_id = self.config.get('aws', 'aws_account_id')
            ecr_url = f"{account_id}.dkr.ecr.{region}.amazonaws.com"

            self.log.info("Autenticando no ECR...")
            auth_command = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {ecr_url}"
            self.ctx.run(auth_command)

            # 7. Taggear a imagem com as versões e latest
            self.log.info(f"Tagueando a imagem {image_name} com {latest_version} e 'latest'...")
            self.docker_manager.tag_image(image_name, "latest", f"{ecr_url}/{image_name}:latest")
            self.docker_manager.tag_image(image_name, latest_version, f"{ecr_url}/{image_name}:{latest_version}")

            # 8. Push da imagem para o ECR
            self.log.info(f"Fazendo push da imagem {image_name} para o ECR...")
            push_command_latest = f"docker push {ecr_url}/{image_name}:latest"
            push_command_version = f"docker push {ecr_url}/{image_name}:{latest_version}"

            self.ctx.run(push_command_latest)
            self.ctx.run(push_command_version)

            self.log.info(f"Imagem {image_name} enviada com sucesso para {ecr_url}.")

        except Exception as e:
            self.log.error(f"Erro durante o deploy no ECR: {str(e)}")
