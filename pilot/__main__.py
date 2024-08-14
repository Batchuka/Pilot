# pilot\cli\__main__.py
import click
from pilot.docs import show_markdown, list_available_docs
from pilot.src.context import Context
from pilot.src.aws import AWSManager
from pilot.src.docker import DockerManager
from pilot.src.git import GitManager
from pilot.src.deploy import DeployManager

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
    """Inicializa o manager específico: aws, docker, git, etc."""
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
    else:
        click.echo(f"Manager '{manager}' não reconhecido.")

@cli.command()
def deploy():
    """Executa o processo de deploy configurado."""
    manager = DeployManager()
    manager.execute_deploy()

@click.command()
@click.option('-a', '--amend', is_flag=True, help='Faz append à mensagem de commit anterior.')
# @click.pass_context
def commit(amend):
    """Executa o processo completo de commit, com ou sem append na mensagem."""
    git_manager = GitManager()
    git_manager.execute_commit(amend = True)

# Comentário besta
if __name__ == "__main__":
    commit()
