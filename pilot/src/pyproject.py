# pilot/src/pyproject_manager.py

import os
import tomllib
import tomli_w
from setuptools_scm import get_version
from pilot.base.manager import BaseManager


class PyprojectManager(BaseManager):

    def __init__(self):
        self.pyproject_file = os.path.join(self.project_root, 'pyproject.toml')

        if not os.path.exists(self.pyproject_file):
            self.log.error(f"pyproject.toml não foi encontrado em: {self.project_root}")

        self.log.info(f"PyprojectManager inicializado para o projeto em {self.project_root}")
        self.config = self._load_pyproject()

    def init(self, **kwargs):
        self.pyproject_file = os.path.join(self.project_root, 'pyproject.toml')

        if not os.path.exists(self.pyproject_file):
            self.log.error(f"pyproject.toml não foi encontrado em: {self.project_root}")

        self.log.info(f"PyprojectManager inicializado para o projeto em {self.project_root}")
        self.config = self._load_pyproject()

    def update(self, **kwargs):
        raise NotImplementedError


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

    def _load_pyproject(self) -> dict:
        try:
            with open(self.pyproject_file, 'rb') as pyproject_file:
                config = tomllib.load(pyproject_file)
            self.log.debug("pyproject.toml carregado com sucesso")
            return config
        except tomllib.TOMLDecodeError as e:
            self.log.error(f"Falha ao decodificar pyproject.toml: {e}")
            return {}  # Retorna um dicionário vazio em caso de erro
        except FileNotFoundError as e:
            self.log.error(f"Arquivo pyproject.toml não encontrado: {e}")
            return {}  # Retorna um dicionário vazio se o arquivo não for encontrado
        except Exception as e:
            self.log.error(f"Erro inesperado ao carregar pyproject.toml: {e}")
            return {}  # Retorna um dicionário vazio para outros erros inesperados

    def _get_version(self):
        try:
            scm_version = get_version(root=self.project_root, relative_to=__file__)
            self.log.info(f"Versão do projeto obtida: {scm_version}")
            return scm_version
        except Exception as e:
            self.log.error(f"Erro ao obter a versão: {e}")

    def _update_dependencies(self, requirements_path):
        """
        Atualiza as dependências do pyproject.toml com base em um arquivo requirements.txt.
        """
        try:
            with open(requirements_path, 'r') as req_file:
                dependencies = req_file.read().splitlines()

            stable_dependencies = self._filter_stable_versions(dependencies)

            self.config['project']['dependencies'] = stable_dependencies

            with open(self.pyproject_file, 'wb') as pyproject_file:
                tomli_w.dump(self.config, pyproject_file)

            self.log.info("pyproject.toml atualizado com dependências atuais.")
        except Exception as e:
            self.log.error(f"Erro ao atualizar dependências: {e}")
