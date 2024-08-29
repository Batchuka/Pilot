# pilot/src/log.py
import logging

from pilot.singleton import Singleton

from colorama import init, Fore, Style

# Inicializa a colorama para colorir a saída no terminal
init(autoreset=True)

class Logger(Singleton):
    
    def _initialize(self):
        self.logger = logging.getLogger('pilot')
        self.logger.setLevel(logging.DEBUG)  # Configura o nível mínimo de log

        if not self.logger.hasHandlers():  # Verifica se o logger já tem handlers
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)  # Configura o nível mínimo do console

            # Define o formato das mensagens de log
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)

    def _add_spacing(self):
        """Adiciona uma linha em branco para espaçamento."""
        print('\n')

    def info(self, message):
        self._add_spacing()
        self.logger.info(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

    def warning(self, message):
        self._add_spacing()
        self.logger.warning(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

    def error(self, message):
        self._add_spacing()
        self.logger.error(f"{Fore.RED}{message}{Style.RESET_ALL}")

    def debug(self, message):
        self._add_spacing()
        self.logger.debug(f"{Fore.BLUE}{message}{Style.RESET_ALL}")
