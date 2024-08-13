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

        for key, in DEPLOY_DEFAULTS.items():
            self.config.set(self.section_name, key, kwargs.get(key))

        self.save_config()

    def select_pipeline(self):
        # Certifique-se de que o section_name está definido
        pipeline_type = self.config[self.section_name]['pipeline_type']

        if pipeline_type == 'remote_docker':
            self.pipeline = RemoteDockerDeployPipeline()
        elif pipeline_type == 'ecs':
            self.pipeline = EcsDeployPipeline()
        else:
            self.log.error(f"Pipeline '{pipeline_type}' não suportado.")

    def execute_deploy(self):
        self.select_pipeline()
        if self.pipeline:
            self.pipeline.execute()
        else:
            self.log.error("Pipeline não selecionado.")

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
            # Verificar o contexto Docker usando o contexto armazenado
            self.docker_manager.verificar_contexto_docker(self.config['docker']['docker_context'])

            # Obter a URL do CodeArtifact com token
            codeartifact_url = self.aws_manager.get_codeartifact_url()

            # Obter a versão do pacote do CodeArtifact
            package_version = self.aws_manager.get_package_info(self.config['publish']['package_name'])

            image_name = self.config['aws']['codeartifact_repository_name']
            dockerfile_path = os.path.abspath(os.getcwd())

            # Verifica se a imagem já existe e remove se necessário
            if self.docker_manager.verificar_existencia_imagem(self.ctx, image_name, package_version):
                self.docker_manager.remover_imagem(image_name, package_version)

            # Build da imagem Docker
            self.docker_manager.build_docker_image(dockerfile_path, image_name, package_version, codeartifact_url)

            # Taguear a imagem com a versão do pacote CodeArtifact e 'latest'
            self.log.info("Tagueando a imagem como 'latest'...")
            self.docker_manager.tag_image(image_name, package_version, "latest")

            self.log.info("Deploy completado com sucesso!")
        except Exception as e:
            self.log.error(str(e))


class EcsDeployPipeline(BaseDeployPipeline):
    def __init__(self):
        super().__init__()
        self.section_name = SECTION_NAME
        self.default_section = DEFAULT_SECTION
        self.aws_manager = AWSManager()        # Inicializa o gerenciador AWS
    
    def execute(self):
        raise NotImplementedError