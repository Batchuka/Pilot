# pilot/src/pyproject_manager.py

import os
import tomllib
import tomli_w
from setuptools_scm import get_version
from pilot.src.log import Logger

class PyprojectManager:
    def __init__(self, project_path):
        self.project_path = project_path
        self.pyproject_file = os.path.join(project_path, 'pyproject.toml')
        self.log_manager = Logger()

        if not os.path.exists(self.pyproject_file):
            self.log_manager.error(f"pyproject.toml não foi encontrado em: {project_path}")

        self.log_manager.info(f"PyprojectManager inicializado para o projeto em {project_path}")
        self.config = self._load_pyproject()

    def _filter_stable_versions(self, dependencies):
        """
        Filtra as dependências para remover sufixos 'dirty' e 'post'.

        :param dependencies: Lista de dependências no formato 'nome==versão'.
        :return: Lista de dependências com apenas versões estáveis.
        """
        stable_dependencies = []
        for dep in dependencies:
            name, version = dep.split('==')
            if 'dirty' not in version and 'post' not in version:
                stable_dependencies.append(dep)
        return stable_dependencies

    def _load_pyproject(self):
        try:
            with open(self.pyproject_file, 'rb') as pyproject_file:
                config = tomllib.load(pyproject_file)
            self.log_manager.debug("pyproject.toml carregado com sucesso")
            return config
        except tomllib.TOMLDecodeError as e:
            self.log_manager.error(f"Falha ao decodificar pyproject.toml: {e}")

    def _get_version(self):
        try:
            scm_version = get_version(root=self.project_path, relative_to=__file__)
            self.log_manager.info(f"Versão do projeto obtida: {scm_version}")
            return scm_version
        except Exception as e:
            self.log_manager.error(f"Erro ao obter a versão: {e}")

    def _update_dependencies(self, requirements_path):
        """
        Atualiza as dependências do pyproject.toml com base em um arquivo requirements.txt.
        """
        try:
            with open(requirements_path, 'r') as req_file:
                dependencies = req_file.read().splitlines()

            stable_dependencies = self.filter_stable_versions(dependencies)

            self.config['project']['dependencies'] = stable_dependencies

            with open(self.pyproject_file, 'wb') as pyproject_file:
                tomli_w.dump(self.config, pyproject_file)

            self.log_manager.info("pyproject.toml atualizado com dependências atuais.")
        except Exception as e:
            self.log_manager.error(f"Erro ao atualizar dependências: {e}")
