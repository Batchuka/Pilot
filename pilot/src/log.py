# pilot/src/log.py
import logging
from colorama import init, Fore, Style

# Inicializa a colorama para colorir a saída no terminal
init(autoreset=True)

class LogManager:
    def __init__(self):
        self.logger = logging.getLogger('pilot')
        self.logger.setLevel(logging.DEBUG)  # Configura o nível mínimo de log

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Configura o nível mínimo do console

        # Define o formato das mensagens de log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

    def warning(self, message):
        self.logger.warning(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

    def error(self, message):
        self.logger.error(f"{Fore.RED}{message}{Style.RESET_ALL}")

    def debug(self, message):
        self.logger.debug(f"{Fore.BLUE}{message}{Style.RESET_ALL}")

# Exemplo de uso:
# log_manager = LogManager()
# log_manager.info("This is an info message")
# log_manager.warning("This is a warning message")
# log_manager.error("This is an error message")
# log_manager.debug("This is a debug message")
