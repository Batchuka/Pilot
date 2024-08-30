# pilot/src/build.py
import os
import shutil
import subprocess
from pathlib import Path
from pilot.base.manager import BaseManager
from pilot.src.pyproject import PyprojectManager

class BuildManager(BaseManager):

    def __init__(self):
        super().__init__()
        self.section_name = 'build'
        self.default_section = 'default_build'

    def build(self, project_path='.'):
        """Constrói o pacote do projeto."""
        project_path = os.path.abspath(project_path)
        self.log.info(f"Construindo projeto em: {project_path}")

        try:
            # Remover pastas de build do projeto
            self.remove_previous_build(project_path)

            # Criação do requirements para injetar as dependências adequadas
            # Função delegada para o PyprojectManager
            pyproject_manager = PyprojectManager()
            pyproject_manager.create_requirements_txt(project_path)

            # Constrói o pacote
            self.build_package(project_path)

            self.log.info(f"Build realizado com sucesso.")
        except Exception as e:
            self.log.error(f"Erro durante o processo de build: {e}")

    def remove_previous_build(self, project_path):
        """Remove artefatos antigos de build."""
        self.log.info("Limpando artefatos de builds antigos...")
        # Arquivos e pastas para remover
        paths_to_remove = ['dist', '*.egg-info', 'requirements.txt', 'setup.py']
        for path in paths_to_remove:
            for file_or_dir in Path(project_path).rglob(path):
                if os.path.exists(file_or_dir):
                    if os.path.isdir(file_or_dir):
                        shutil.rmtree(file_or_dir)
                    else:
                        os.remove(file_or_dir)
                    self.log.info(f"Removido: {file_or_dir}")

    def build_package(self, project_path):
        """Realiza o processo de build do pacote."""
        self.log.info("Construindo o pacote...")
        try:
            subprocess.run([sys.executable, '-m', 'build', project_path], check=True)
        except subprocess.CalledProcessError as e:
            self.log.error(f"Erro ao construir o pacote: {str(e)}")
