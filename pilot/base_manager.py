# pilot/base_manager.py

import configparser
from abc import ABC, abstractmethod

class BaseManager(ABC):
    """
    Classe BaseManager que fornece funcionalidades comuns para todos os Managers.
    """
    
    config_file = ".conf"  # Caminho para o arquivo de configuração

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.section_name = self.__class__.__name__.lower()  # Nome da seção baseado na classe filha
        self.load_config()

    def load_config(self):
        """Carrega as configurações do arquivo .conf."""
        self.config.read(self.config_file)
        if not self.config.has_section(self.section_name):
            self.config.add_section(self.section_name)

    def save_config(self):
        """Salva as configurações no arquivo .conf."""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    @abstractmethod
    def init(self, **kwargs):
        """Inicializa a sessão do manager no arquivo de configuração."""
        pass
