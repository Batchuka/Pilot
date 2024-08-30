# pilot\src\aws.py
import os
import json
import subprocess

from pilot.base.manager import BaseManager
from pilot.default.aws import AWS_DEFAULTS

class AWSManager(BaseManager):

    def __init__(self):
        super().__init__()
        self.section_name = 'aws'

    def init(self, **kwargs):
        """
        Inicializa a sessão 'aws' no arquivo de configuração.
        """
        if not self.config.has_section(self.section_name):
            self.config.add_section(self.section_name)

        # Adiciona as configurações da AWS à sessão 'aws' usando os defaults
        for key, default_value in AWS_DEFAULTS.items():
            self.config.set(self.section_name, key, kwargs.get(key, default_value))

        self.save_config()

    def configure_aws(self):
        """
        Configura a AWS CLI se ainda não estiver configurada.
        """
        try:
            result = self.ctx.run("aws configure list")
            if result and 'None' in result.stdout:
                self.log.warning("AWS CLI não configurado. Configurando agora...")
                self.ctx.run("aws configure")
            else:
                self.log.info("AWS CLI já está configurado.")
        except Exception as e:
            self.log.error(f"Erro na configuração da AWS CLI: {e}")

    def assume_role(self, role_arn, role_session_name="Session"):
        """
        Assume uma role na AWS e armazena as credenciais temporárias no CLI.
        """
        self.log.info(f"Assumindo a role: {role_arn}")
        command = (
            f"aws sts assume-role "
            f"--role-arn {role_arn} "
            f"--role-session-name {role_session_name}"
        )
        result = self.ctx.run(command)
        if result: credentials = result.stdout.strip()
        
        if result and result.return_code == 0:
            credentials = result.stdout.strip()
            self.log.info("Role assumida com sucesso. Credenciais armazenadas.")
        else:
            self.log.warning(f"Falha ao assumir role: {result.stdout.strip() if result else 'No output'}")
            return None

    def authenticate_twine(self):
        """
        Configura o pip e o twine para usar o CodeArtifact com as credenciais da AWS.
        """
        try:
            codeartifact_url = self.get_codeartifact_url()
            self.log.info(f"Autenticando twine com o CodeArtifact: {codeartifact_url}")

            # Autenticar twine
            self.ctx.run(
                f"aws codeartifact login --tool twine "
                f"--repository {self.config['aws']['codeartifact_repository']} "
                f"--domain {self.config['aws']['codeartifact_domain']} "
                f"--domain-owner {self.config['aws']['aws_account_id']} "
                f"--region {self.config['aws']['aws_default_region']}"
            )
            
            # Configurar pip.conf
            self.update_pip_conf()

            self.log.info("Autenticação configurada com sucesso.")
        except Exception as e:
            self.log.error(f"Erro ao autenticar pip e twine: {e}")

    def authenticate_pip(self):
        """
        Configura o pip e o twine para usar o CodeArtifact com as credenciais da AWS.
        """
        try:
            codeartifact_url = self.get_codeartifact_url()
            self.log.info(f"Autenticando pip com o CodeArtifact: {codeartifact_url}")

            # Autenticar twine
            self.ctx.run(
                f"aws codeartifact login --tool twine "
                f"--repository {self.config['aws']['codeartifact_repository']} "
                f"--domain {self.config['aws']['codeartifact_domain']} "
                f"--domain-owner {self.config['aws']['aws_account_id']} "
                f"--region {self.config['aws']['aws_default_region']}"
            )
            
            # Configurar pip.conf
            self.update_pip_conf()

            self.log.info("Autenticação configurada com sucesso.")
        except Exception as e:
            self.log.error(f"Erro ao autenticar pip e twine: {e}")

    def update_pip_conf(self):
        self.log.info("Configurando pip.conf...")
        try:
            token = self.get_codeartifact_token()
            pip_conf_path = os.path.expanduser('~/.config/pip/pip.conf')

            pip_conf_content = f"""
[global]
index-url = https://pypi.org/simple
extra-index-url = https://aws:{token}@{self.config['aws']['codeartifact_domain']}-{self.config['aws']['aws_account_id']}.d.codeartifact.{self.config['aws']['aws_default_region']}.amazonaws.com/pypi/{self.config['aws']['codeartifact_repository']}/simple/
trusted-host =
    pypi.org
    pypi.python.org
    files.pythonhosted.org
    {self.config['aws']['codeartifact_domain']}-{self.config['aws']['aws_account_id']}.d.codeartifact.{self.config['aws']['aws_default_region']}.amazonaws.com
"""

            with open(pip_conf_path, 'w') as pip_conf_file:
                pip_conf_file.write(pip_conf_content)

            self.log.info(f"pip.conf atualizado com sucesso em {pip_conf_path}")

        except Exception as e:
            self.log.error(f"Erro ao atualizar o pip.conf: {e}")

    def get_codeartifact_token(self):
        self.log.info("Obtendo token no CodeArtfact...")
        command = (
            f"aws codeartifact get-authorization-token "
            f"--domain {self.config['aws']['codeartifact_domain']} "
            f"--domain-owner {self.config['aws']['aws_account_id']} "
            f"--query authorizationToken "
            f"--output text"
        )
        result = self.ctx.run(command)
        return result.stdout.strip()

    def get_codeartifact_url(self):
        self.log.info("Montando URL do CodeArtifact...")
        try:
            command = (
                f"aws codeartifact get-authorization-token "
                f"--domain {self.config['aws']['codeartifact_domain']} "
                f"--domain-owner {self.config['aws']['aws_account_id']} "
                f"--query authorizationToken "
                f"--output text"
            )
            result = self.ctx.run(command)
            codeartifact_token = result.stdout.strip()

            return (
                f"https://aws:{codeartifact_token}@"
                f"{self.config['aws']['codeartifact_domain']}-{self.config['aws']['aws_account_id']}.d.codeartifact."
                f"{self.config['aws']['aws_default_region']}.amazonaws.com/pypi/"
                f"{self.config['aws']['codeartifact_repository']}/simple/"
            )

        except Exception as e:
            self.log.error(f"Erro ao obter URL do CodeArtifact: {e}")

    def get_package_info(self, package_name):
        self.log.info("Obtendo a informações do pacote do CodeArtifact...")
        try:
            command = (
                f"aws codeartifact list-package-versions "
                f"--domain {self.config['aws']['codeartifact_domain']} "
                f"--domain-owner {self.config['aws']['aws_account_id']} "
                f"--repository {self.config['aws']['codeartifact_repository']} "
                f"--package {package_name} "
                f"--format pypi "
                f"--query versions"
            )
            result = self.ctx.run(command)

            package_info = json.loads(result.stdout)
            self.log.info(f"Informações do pacote {package_name} obtidas com sucesso.")
            return package_info

        except Exception as e:
            self.log.error(f"Erro ao obter informações do pacote {package_name}: {e}")

    def update(self, **kwargs):
        raise NotImplementedError

