# pilot/src/pytrobot.py
import os
import subprocess
from pathlib import Path
from shutil import copyfile
from cookiecutter.main import cookiecutter
from pilot.base.manager import BaseManager

class PytrobotManager(BaseManager):

    def __init__(self):
        super().__init__()
        self.section_name = 'pytrobot'
        self.default_section = 'default_pytrobot'
        self.scaffold_path = Path(__file__).resolve().parent / "scaffold"

    def new_project(self, name, output_path='.'):
        """Cria um novo projeto PyTrobot com scaffold."""
        self.log.info(f"Criando novo projeto PyTrobot '{name}' em {output_path}...")
        output_path = Path(output_path).resolve()

        try:
            cookiecutter(template=self.scaffold_path, extra_context={'project_name': name}, output_dir=output_path)
            self.log.info(f"Projeto '{name}' criado com sucesso.")
        except Exception as e:
            self.log.error(f"Erro ao criar o projeto: {str(e)}")

    def create_state(self, output_path="."):
        """Cria um arquivo sample_state.py."""
        sample_state_path = self.scaffold_path / 'sample_state.py'
        dest_path = Path(output_path) / 'sample_state.py'
        copyfile(sample_state_path, dest_path)
        self.log.info(f"sample_state.py criado em: {dest_path}")

    def create_test_state(self, output_path="."):
        """Cria um arquivo test_sample_state.py."""
        test_state_path = self.scaffold_path / 'test_sample_state.py'
        dest_path = Path(output_path) / 'test_sample_state.py'
        copyfile(test_state_path, dest_path)
        self.log.info(f"test_sample_state.py criado em: {dest_path}")
