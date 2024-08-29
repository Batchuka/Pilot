# pilot\base\pipeline.py
from abc import ABC, abstractmethod

from pilot.src.context import Context
from pilot.src.config import Config
from pilot.src.log import Logger

class BaseDeployPipeline:
    def __init__(self):
        self.config = Config().config
        self.ctx = Context()  # Instancia o contexto para uso nos managers
        self.log = Logger()
        self.section_name = None  # Para ser definido nas subclasses
        self.default_section = None  # Para ser definido nas subclasses

    def _check_required_attributes(self):
        """Verifica se os atributos obrigatórios foram definidos nas subclasses."""
        if not self.section_name:
            raise AttributeError(f"{self.__class__.__name__} deve definir 'section_name'")
        if not self.default_section:
            raise AttributeError(f"{self.__class__.__name__} deve definir 'default_section'")

    def authenticate(self):
        # Implementação de autenticação comum a todos os pipelines, se necessário
        pass
    
    @abstractmethod
    def execute(self):
        # Implementação de autenticação comum a todos os pipelines, se necessário
        pass
