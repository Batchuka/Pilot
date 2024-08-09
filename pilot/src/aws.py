import click
import subprocess
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

class AWSManager:
    def __init__(self):
        self.aws_config = {}

    def configure_aws(self):
        """
        Configura a AWS CLI se ainda não estiver configurada.
        """
        try:
            result = subprocess.run(['aws', 'configure', 'list'], capture_output=True, text=True)
            if 'None' in result.stdout:
                click.echo(click.style("AWS CLI não configurado. Configurando agora...", fg='yellow'))
                subprocess.run(['aws', 'configure'])
            else:
                click.echo(click.style("AWS CLI já está configurado.", fg='green'))
        except (NoCredentialsError, PartialCredentialsError) as e:
            click.echo(click.style(f"Erro na configuração da AWS CLI: {e}", fg='red'))

    def assume_role(self, role_arn, role_session_name="Session"):
        """
        Assume uma role na AWS e armazena as credenciais temporárias no CLI.
        """
        click.echo(click.style(f"Assumindo a role: {role_arn}", fg='yellow'))
        command = [
            'aws', 'sts', 'assume-role',
            '--role-arn', role_arn,
            '--role-session-name', role_session_name
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        credentials = result.stdout.strip()
        
        if result.returncode == 0:
            click.echo(click.style("Role assumida com sucesso. Credenciais armazenadas.", fg='green'))
        else:
            click.echo(click.style(f"Falha ao assumir role: {credentials}", fg='red'))
            return None

    def authenticate_pip_and_twine(self, aws_config):
        """
        Configura o pip e o twine para usar o CodeArtifact com as credenciais da AWS.
        """
        try:
            codeartifact_url = self.get_codeartifact_url(aws_config)
            click.echo(click.style(f"Autenticando pip e twine com o CodeArtifact: {codeartifact_url}", fg='yellow'))

            # Autenticar twine
            subprocess.run(f"aws codeartifact login --tool twine --repository {aws_config['codeartifact_repository']} --domain {aws_config['codeartifact_domain']} --domain-owner {aws_config['aws_account_id']} --region {aws_config['aws_default_region']}", shell=True, check=True)
            
            # Configurar pip.conf
            self.update_pip_conf(aws_config)

            click.echo(click.style("Autenticação configurada com sucesso.", fg='green'))
        except Exception as e:
            click.echo(click.style(f"Erro ao autenticar pip e twine: {e}", fg='red'))
            raise

    def get_codeartifact_url(self, aws_config):
        try:
            command = f"aws codeartifact get-authorization-token --domain {aws_config['codeartifact_domain']} --domain-owner {aws_config['aws_account_id']} --query authorizationToken --output text"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            codeartifact_token = result.stdout.strip()

            return f"https://aws:{codeartifact_token}@{aws_config['codeartifact_domain']}-{aws_config['aws_account_id']}.d.codeartifact.{aws_config['aws_default_region']}.amazonaws.com/pypi/{aws_config['codeartifact_repository']}/simple/"
        except Exception as e:
            click.echo(click.style(f"Erro ao obter URL do CodeArtifact: {e}", fg='red'))
            raise

    def update_pip_conf(self, aws_config):
        try:
            token = self.get_codeartifact_token(aws_config)
            pip_conf_path = os.path.expanduser('~/.config/pip/pip.conf')

            pip_conf_content = f"""
[global]
index-url = https://pypi.org/simple
extra-index-url = https://aws:{token}@{aws_config['codeartifact_domain']}-{aws_config['aws_account_id']}.d.codeartifact.{aws_config['aws_default_region']}.amazonaws.com/pypi/{aws_config['codeartifact_repository']}/simple/
trusted-host =
    pypi.org
    pypi.python.org
    files.pythonhosted.org
    {aws_config['codeartifact_domain']}-{aws_config['aws_account_id']}.d.codeartifact.{aws_config['aws_default_region']}.amazonaws.com
"""

            with open(pip_conf_path, 'w') as pip_conf_file:
                pip_conf_file.write(pip_conf_content)

            click.echo(click.style(f"pip.conf atualizado com sucesso em {pip_conf_path}", fg='green'))

        except Exception as e:
            click.echo(click.style(f"Erro ao atualizar o pip.conf: {e}", fg='red'))
            raise

    def get_codeartifact_token(self, aws_config):
        command = f"aws codeartifact get-authorization-token --domain {aws_config['codeartifact_domain']} --domain-owner {aws_config['aws_account_id']} --query authorizationToken --output text"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        return result.stdout.strip()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--role-arn', prompt='ARN da Role', help='ARN da role a ser assumida.')
@click.option('--session-name', default='Session', help='Nome da sessão para a role assumida.')
@click.pass_context
def assume_role(ctx, role_arn, session_name):
    aws_manager = AWSManager()
    aws_manager.assume_role(role_arn, session_name)

@cli.command()
@click.pass_context
def configure(ctx):
    aws_manager = AWSManager()
    aws_manager.configure_aws()

@cli.command()
@click.pass_context
def authenticate(ctx):
    aws_manager = AWSManager()
    aws_manager.authenticate_pip_and_twine(aws_manager.aws_config)

if __name__ == "__main__":
    cli()
