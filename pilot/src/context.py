# pilot\src\context.py
from pilot.singleton import Singleton
from pilot.src.log import LogManager
from pilot.src.config import Config
from invoke import Context as InvokeContext
from invoke import UnexpectedExit

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
                result = self.invoke_context.run(command, hide=False)
            elif verbosity == 'vv':
                result = self.invoke_context.run(command, hide=True, warn=True)
            else:
                result = self.invoke_context.run(command, hide=True)
        except UnexpectedExit as e:
            # Captura exceções relacionadas a falhas na execução do comando
            self.log.error(f"Erro ao executar o comando: {command}\n{e.result.stderr}")
        except Exception as e:
            # Captura quaisquer outras exceções não esperadas
            self.log.error(f"Erro inesperado ao executar o comando: {command}\n{str(e)}")

    def get_click_option(self, option_name):
        """Obtém uma opção do contexto do Click."""
        if self.click_context:
            return self.click_context.params.get(option_name)
        return None