# pilot\src\config.py
import os
import inspect
import configparser
import sys

from pilot.singleton import Singleton
from pilot.src.log import LogManager

class Config(Singleton):

    def _initialize(self):
        self.log = LogManager()
        self.project_root = os.path.abspath(os.getcwd())
        self.config_file = os.path.join(self.project_root, 'pilot.conf')
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self, specific_config=None):
        """Carrega as configurações do arquivo pilot.conf ou de um arquivo específico."""
        try:
            config_path = self.config_file if not specific_config else os.path.join(self.project_root, specific_config)
            
            if not os.path.exists(config_path):
                self.log.error(f"Não encontrou 'pilot.conf' no caminho: {config_path}")
                return  # Retorna caso o arquivo não seja encontrado
            
            self.config.read(config_path)  # Lê o arquivo de configuração usando configparser
        except Exception as e:
            self.log.error(f"Erro ao carregar o arquivo de configuração: {str(e)}")
            sys.exit(1)  # Interrompe o processo com um código de saída 1 (indicando erro)

    def save_config(self):
        """Salva as configurações no arquivo .conf."""
        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
        except Exception as e:
            self.log.error(f"Erro ao salvar o arquivo de configuração: {str(e)}")

    def get_config(self):
        """Retorna a instância do ConfigParser."""
        return self.config

    def get(self, key, fallback=None):
        """Obtém o valor de uma chave usando a seção e a seção padrão da classe chamadora."""
        try:
            caller_class = self._get_caller_class()

            section_name = getattr(caller_class, 'section_name')
            default_section = getattr(caller_class, 'default_section')

            if section_name and self.config.get(section_name, key):
                return self.config.get(section_name, key)
            elif default_section and self.config.get(default_section, key):
                return self.config.get(default_section, key)

        except Exception as e:
            self.log.error(str(e))
            

    def _get_caller_class(self):
        """Obtém a instância da classe chamadora da stack de chamadas."""
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back.f_back  # Suba dois níveis na stack
            caller_instance = caller_frame.f_locals.get('self', None)
            if caller_instance:
                return caller_instance
        except Exception as e:
            self.log.error(f"Erro ao determinar a classe invocante: {str(e)}")
            return None
        finally:
            del frame  # Evita possíveis ciclos de referência
