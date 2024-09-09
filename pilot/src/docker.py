# pilot\src\docker.py
from pilot.base.manager import BaseManager
from pilot.src.log import Logger

class DockerManager(BaseManager):

    def __init__(self):
        super().__init__()
        self.section_name = 'docker'
        self.log_mng = Logger()

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
            self.log.error(f"Contexto Docker incorreto. Esperado: {expected_context}, Atual: {current_context}")

    def mudar_contexto_docker(self, novo_contexto):

        self.log.info(f"Mudando o contexto Docker para: {novo_contexto}...")
        
        # Verifica o contexto atual
        result = self.ctx.run(f"docker context show")
        current_context = result.stdout.strip()
        
        # Se o contexto já estiver correto, não faz nada
        if current_context == novo_contexto:
            self.log.info(f"O contexto Docker já está definido para {novo_contexto}.")
            return
        
        # Muda para o novo contexto
        result = self.ctx.run(f"docker context use {novo_contexto}")
        
        if result is None or result.return_code != 0:
            self.log.error(f"Erro ao tentar mudar o contexto Docker para: {novo_contexto}")
        
        self.log.info(f"Contexto Docker alterado com sucesso para: {novo_contexto}.")

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

    def tag_image(self, source_image, source_tag, target_image, target_tag):
        """Tagueia a imagem Docker com múltiplas tags."""
        if isinstance(target_tag, str):
            target_tags = [target_tag]

        self.log.info(f"Tagueando a imagem '{source_image}:{source_tag}' com as tags: {', '.join(target_tags)}")
        try:
            for target_tag in target_tags:
                command = f"docker tag {source_image}:{source_tag} {target_image}:{target_tag}"
                result = self.ctx.run(command)

                if result.return_code == 0:
                    self.log.info(f"Imagem '{source_image}:{source_tag}' foi tagueada com sucesso como '{target_image}:{target_tag}'.")
                else:
                    self.log.error(f"Falha ao taguear a imagem '{source_image}:{source_tag}' como '{target_tag}': {result.stderr}")

        except Exception as e:
            self.log.error(f"Erro inesperado ao taguear a imagem '{source_image}:{source_tag}' com múltiplas tags: {str(e)}")

    def update(self, **kwargs):
        raise NotImplementedError
