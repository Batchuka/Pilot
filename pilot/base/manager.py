from abc import ABC, abstractmethod
from pilot.src.config import Config
from pilot.src.context import Context
from pilot.src.log import Logger

class BaseManager(ABC):
    """
    Interface BaseManager que define a estrutura básica para todos os Managers.
    """

    def __init__(self):
        self.config = Config().config  # Obtém a configuração a partir da instância Singleton Config
        self.save_config = Config().save_config
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

    @abstractmethod
    def init(self, **kwargs):
        """Inicializa a sessão do manager no arquivo de configuração."""
        pass
    
    @abstractmethod
    def update(self, **kwargs):
        """Executa o script de configuração do manger em questão."""
        pass

