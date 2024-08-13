# pilot\src\docker.py
from pilot.base.manager import BaseManager
from pilot.src.log import LogManager

class DockerManager(BaseManager):

    def __init__(self):
        super().__init__()
        self.section_name = 'docker'
        self.log_mng = LogManager()

    def init(self, **kwargs):
        """Inicializa a sessão 'docker' no arquivo de configuração."""
        self.log.info('Inicializando DockerManager...')
        if not self.config.has_section(self.section_name):
            self.config.add_section(self.section_name)

        # Adicione as configurações padrão do Docker aqui, se necessário
        self.save_config()

    def verificar_contexto_docker(self, expected_context):
        self.log.info('Verificando o contexto Docker...')
        result = self.ctx.run(f"docker context show")
        current_context = result.stdout.strip()
        if current_context != expected_context:
            raise Exception(f"Contexto Docker incorreto. Esperado: {expected_context}, Atual: {current_context}")

    def remover_imagem(self, image_name, version):
        self.log_mng.info(f"Removendo imagem.")
        self.ctx.run(f"docker rmi -f {image_name}:{version}")

    def verificar_existencia_imagem(self, image_name, version):
        self.log.info(f'Verificando a existência da imagem {image_name}:{version}...')
        result = self.ctx.run(f"docker images -q {image_name}:{version}")
        return bool(result.stdout.strip())

    def build_docker_image(self, dockerfile_path, image_name, package_version, codeartifact_url):

        try:
            self.log.info("Buildando a imagem Docker...")

            # Construir o comando Docker
            command = (
                f"docker build --build-arg CODEARTIFACT_REPOSITORY_URL={codeartifact_url} "
                f"-t {image_name}:{package_version} {dockerfile_path}"
            )
            
            # Executar o comando usando o contexto
            result = self.ctx.run(command)
            
            if result.ok:
                self.log.info(f"Imagem Docker {image_name}:{package_version} criada com sucesso.")
            else:
                self.log.error(f"Erro ao buildar a imagem Docker: {result.stderr}")
        
        except Exception as e:
            self.log.error(f"Erro durante o processo de build da imagem Docker: {e}")