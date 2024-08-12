# pilot\cli\__main__.py
import click
from pilot.docs import show_markdown
from pilot.src.aws import AWSManager
from pilot.src.docker import DockerManager
from pilot.src.git import GitManager

@click.group()
def cli():
    """CLI principal para o utilitário Pilot."""
    pass

@cli.command()
@click.argument('doc_name', default='readme')
def doc(doc_name):
    """Exibe a documentação especificada (aws, docker, etc.)."""
    show_markdown(doc_name)

@cli.command()
@click.argument('manager')
@click.pass_context
def init(ctx, manager):
    """Inicializa o manager específico :aws, docker, git, etc."""
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

if __name__ == "__main__":
    doc()
