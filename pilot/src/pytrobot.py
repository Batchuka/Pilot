# pilot/src/pytrobot.py
from pathlib import Path
from shutil import copyfile
from cookiecutter.main import cookiecutter
from pilot.base.manager import BaseManager

# Importa os módulos diretamente para obter o caminho
import pytrobot.scaffold.state.new_state as state_scaffold
import pytrobot.scaffold.state.test_new_state as test_state_scaffold
import pytrobot.scaffold.orchestrator.new_worker as worker_scaffold
import pytrobot.scaffold.orchestrator.test_new_worker as test_worker_scaffold

class PytrobotManager(BaseManager):

    def __init__(self):
        super().__init__()
        self.section_name = 'pytrobot'
        self.default_section = 'default_pytrobot'

    def init(self, **kwargs):
        raise NotImplementedError

    def update(self, **kwargs):
        raise NotImplementedError

    def new_project(self, name, project_type='state', output_path='.'):
        """Cria um novo projeto PyTrobot usando o scaffold."""
        self.log.info(f"Criando novo projeto PyTrobot '{name}' do tipo '{project_type}' em {output_path}...")
        output_path = Path(output_path).resolve()
        
        # Define o caminho correto do scaffold baseado no tipo de projeto
        if project_type == 'state':
            scaffold_path = Path(state_scaffold.__file__).resolve().parent / "project"
        elif project_type == 'orchestrator':
            scaffold_path = Path(worker_scaffold.__file__).resolve().parent / "project"
        else:
            raise ValueError(f"Tipo de projeto desconhecido: {project_type}")

        try:
            cookiecutter(template=scaffold_path, extra_context={'project_name': name}, output_dir=str(output_path))
            self.log.info(f"Projeto '{name}' criado com sucesso.")
        except Exception as e:
            self.log.error(f"Erro ao criar o projeto: {str(e)}")

    def create_state(self, output_path="."):
        """Cria um arquivo new_state.py."""
        state_file_path = Path(state_scaffold.__file__).resolve()
        dest_path = Path(output_path) / 'new_state.py'
        copyfile(state_file_path, dest_path)
        self.log.info(f"new_state.py criado em: {dest_path}")

    def create_test_state(self, output_path="."):
        """Cria um arquivo test_new_state.py."""
        test_state_file_path = Path(test_state_scaffold.__file__).resolve()
        dest_path = Path(output_path) / 'test_new_state.py'
        copyfile(test_state_file_path, dest_path)
        self.log.info(f"test_new_state.py criado em: {dest_path}")

    def create_worker(self, output_path="."):
        """Cria um arquivo new_worker.py."""
        worker_file_path = Path(worker_scaffold.__file__).resolve()
        dest_path = Path(output_path) / 'new_worker.py'
        copyfile(worker_file_path, dest_path)
        self.log.info(f"new_worker.py criado em: {dest_path}")

    def create_test_worker(self, output_path="."):
        """Cria um arquivo test_new_worker.py."""
        test_worker_file_path = Path(test_worker_scaffold.__file__).resolve()
        dest_path = Path(output_path) / 'test_new_worker.py'
        copyfile(test_worker_file_path, dest_path)
        self.log.info(f"test_new_worker.py criado em: {dest_path}")


