# pilot\src\context.py
from pilot.singleton import Singleton
from pilot.src.log import LogManager
from pilot.src.config import Config
from invoke import Context as InvokeContext
from invoke import UnexpectedExit

class CustomResult:
    def __init__(self, stdout="", stderr="", return_code=-1):
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code


class Context(Singleton):

    def _initialize(self):
        # Cria um contexto do Invoke para execução de comandos de terminal
        self.invoke_context = InvokeContext()
        self.log = LogManager()
        self.config = Config().config

        # Inicializa o contexto do Click, se necessário
        self.click_context = None

    def set_click_context(self, click_ctx):
        """Define o contexto do Click."""
        self.click_context = click_ctx

    def run(self, command):
        """Executa um comando no terminal usando o Invoke e captura erros."""
        verbosity = self.config['log']['verbosity']

        try:
            # Determina se o output deve ser ocultado com base na verbosidade
            if verbosity == 'vvv':
                result = self.invoke_context.run(command, hide=False, warn=True)
            elif verbosity == 'vv':
                result = self.invoke_context.run(command, hide=True, warn=True)
            else:
                result = self.invoke_context.run(command, hide=True)
            # Retorne o resultado normal se não houver erros
            return result
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