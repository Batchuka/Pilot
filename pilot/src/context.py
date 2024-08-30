# pilot\src\context.py

from pilot.singleton import Singleton
from pilot.src.log import Logger
from pilot.src.config import Config
from pilot.default.context import CONTEXT_DEFAULTS

from invoke.context import Context as InvokeContext
from invoke.exceptions import UnexpectedExit

class CustomResult:
    def __init__(self, stdout="", stderr="", return_code=-1):
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code


class Context(Singleton):

    def _initialize(self):
        # Cria um contexto do Invoke para execução de comandos de terminal
        self.section_name = 'context'
        self.default_section = 'context_git'
        self.invoke_context = InvokeContext()
        self.log = Logger()
        self.config = Config().config
        self.init()

        # Inicializa o contexto do Click, se necessário
        self.click_context = None
    def init(self):
        """Inicializa a seção 'log' no arquivo de configuração."""
        if not self.config.has_section(self.section_name):
            self.config.add_section(self.section_name)
            for key, default_value in CONTEXT_DEFAULTS.items():
                self.config.set(self.section_name, key, self.config.get(self.section_name, key, fallback=default_value))
            Config().save_config()  # Salva as configurações no arquivo pilot.conf

    def set_click_context(self, click_ctx):
        """Define o contexto do Click."""
        self.click_context = click_ctx

    def run(self, command: str) -> CustomResult:
        """Executa um comando no terminal usando o Invoke e captura erros."""
        verbosity = self.config['context']['verbosity']

        try:
            # Determina se o output deve ser ocultado com base na verbosidade
            if verbosity == 'vvv':
                result = self.invoke_context.run(command, hide=False, warn=True)
            elif verbosity == 'vv':
                result = self.invoke_context.run(command, hide=True, warn=True)
            else:
                result = self.invoke_context.run(command, hide=True)

            # Verifica o return_code antes de retornar o resultado
            if result and result.return_code == 0:
                return CustomResult(stdout=result.stdout, stderr=result.stderr, return_code=result.return_code)
            else:
                self.log.warning(f"Comando retornou um código de saída diferente de 0")
                return CustomResult()


        except UnexpectedExit as e:
            self.log.error(f"Erro ao executar o comando: {command}\n{e.result.stderr}")
            return CustomResult(stdout=e.result.stdout, stderr=e.result.stderr, return_code=e.result.return_code)
        except Exception as e:
            self.log.error(f"Erro inesperado ao executar o comando: {command}\n{str(e)}")
            return CustomResult(stderr=str(e), return_code=-1)

    def get_click_option(self, option_name):
        """Obtém uma opção do contexto do Click."""
        if self.click_context:
            return self.click_context.params.get(option_name)
        return None