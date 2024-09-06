# pilot\cli\__main__.py
import click
from pilot.docs import show_markdown, list_available_docs
from pilot.src.context import Context
from pilot.src.aws import AWSManager
from pilot.src.docker import DockerManager
from pilot.src.git import GitManager
from pilot.src.deploy import DeployManager
from pilot.src.vscode import VscodeManager
from pilot.src.publish import PublishManager

@click.group()
@click.option('--some-option', default='default_value')
@click.pass_context
def cli(ctx, some_option):
    # Obtenha a instância do contexto singleton
    context = Context()
    
    # Associe o contexto do Click ao singleton
    context.set_click_context(ctx)


@cli.command()
@click.argument('doc_name', default='help')
def doc(doc_name):
    """Exibe a documentação detalhada sobre: aws, docker, git, deploy, etc."""
    if doc_name == 'help':
        show_markdown('readme')
        list_available_docs()
    else:
        show_markdown(doc_name)

@cli.command()
@click.argument('manager')
@click.pass_context
def init(ctx, manager):
    """Inicializa o manager específico: aws, docker, git, vscode, etc."""
    if manager == 'aws':
        aws_manager = AWSManager()
        aws_manager.init()
        click.echo("AWS Manager inicializado.")
    elif manager == 'docker':
        docker_manager = DockerManager()
        docker_manager.init()
        click.echo("Docker Manager inicializado.")
    elif manager == 'git':
        git_manager = GitManager()
        git_manager.init()
        click.echo("Git Manager inicializado.")
    elif manager == 'vscode':
        vscode_manager = VscodeManager()
        vscode_manager.init()
        click.echo("Vscode Manager inicializado.")
    else:
        click.echo(f"Manager '{manager}' não reconhecido.")

@cli.command()
@click.argument('manager')
@click.pass_context
def update(ctx, manager):
    """Atualiza as configurações para o manager específico: vscode, etc."""
    if manager == 'vscode':
        vscode_manager = VscodeManager()
        vscode_manager.update()
        click.echo("Configurações do VS Code atualizadas.")
    else:
        click.echo(f"Manager '{manager}' não possui função de atualização.")

@cli.command()
def deploy():
    """Executa o processo de deploy configurado."""
    manager = DeployManager()
    manager.execute_deploy()

@cli.command()
def publish():
    """Executa o processo de deploy configurado."""
    raise NotImplementedError("... Em breve")

@cli.command()
@click.option('-a', '--amend', is_flag=True, help='Faz append à mensagem de commit anterior.')
@click.pass_context
def commit(ctx, amend):
    """Executa o processo completo de commit, com ou sem append na mensagem."""
    git_manager = GitManager()
    git_manager.execute_commit(amend)