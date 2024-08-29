# pilot/src/package.py
import os
import tomllib
import tomli_w
from pathlib import Path
from pilot.base.manager import BaseManager

class PackageManager(BaseManager):

    def __init__(self):
        super().__init__()
        self.section_name = 'package'
        self.default_section = 'default_package'

    def create_requirements_txt(self, project_path, project_name):
        """Cria o arquivo requirements.txt baseado nas bibliotecas do projeto."""
        self.log.info("Criando requirements.txt...")

        # Caminho completo para o arquivo de requirements
        requirements_path = Path(project_path) / 'requirements.txt'

        # Função para gerar o conteúdo (pode reaproveitar a lógica do pytrobot)
        with open(requirements_path, 'w') as req_file:
            req_file.write(f"pytrobot==3.0.5\nboto3==1.26.141\ninvoke==2.2.0\n")  # Exemplo

        self.log.info(f"requirements.txt criado com sucesso em: {requirements_path}")

    def update_pyproject_toml(self, project_path):
        """Atualiza o arquivo pyproject.toml com as dependências atuais do projeto."""
        self.log.info("Atualizando pyproject.toml...")

        pyproject_file_path = Path(project_path) / 'pyproject.toml'
        if not pyproject_file_path.exists():
            self.log.error(f"Arquivo pyproject.toml não encontrado em {project_path}")
            return

        with open(pyproject_file_path, 'rb') as pyproject_file:
            pyproject_content = tomllib.load(pyproject_file)

        # Atualiza dependências (exemplo genérico)
        pyproject_content['project']['dependencies'] = ['pytrobot==3.0.5', 'invoke==2.2.0']

        with open(pyproject_file_path, 'wb') as pyproject_file:
            tomli_w.dump(pyproject_content, pyproject_file)

        self.log.info(f"pyproject.toml atualizado com sucesso.")
