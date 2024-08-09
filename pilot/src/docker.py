# pilot/src/docker.py

import os
from configparser import ConfigParser
from pilot.src.log import LogManager

class DockerManager:
    
    def __init__(self, project_root):
        self.project_root = project_root
        self.config = self._load_config()
        self.log_mng = LogManager()

    def _load_config(self):
        config_path = os.path.join(self.project_root, 'docker.conf')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Docker configuration file not found at: {config_path}")

        config = ConfigParser()
        config.read(config_path)
        return config

    def verificar_contexto_docker(self, c, expected_context):
        result = c.run("docker context show", hide=True, warn=True)
        current_context = result.stdout.strip()
        if current_context != expected_context:
            raise Exception(f"Contexto Docker incorreto. Esperado: {expected_context}, Atual: {current_context}")

    def remover_imagem(self, c, image_name, version):
        self.log_mng.log(f"Removendo imagem existente {image_name}:{version}...")
        c.run(f"docker rmi -f {image_name}:{version}")

    def verificar_existencia_imagem(self, c, image_name, version):
        result = c.run(f"docker images -q {image_name}:{version}", hide=True, warn=True)
        return bool(result.stdout.strip())

    def get_config_value(self, section, key):
        """
        Retorna um valor específico do arquivo de configuração Docker.
        """
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        raise KeyError(f"Key '{key}' not found in section '{section}'.")

# Exemplo de uso:
# docker_manager = DockerManager('/caminho/para/seu/projeto')
# docker_manager.verificar_contexto_docker(context, 'expected_context')