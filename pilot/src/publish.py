import os

from pilot.base.manager import BaseManager
from pilot.src.git import GitManager
from pilot.src.log import LogManager
# from pilot.src.build import BuildManager #type:ignore ← NÃO EXISTE

class PublishManager(BaseManager):
    def __init__(self, project_path='.'):
        super().__init__()
        self.project_path = os.path.abspath(project_path)
        self.git_manager = GitManager(self.project_path)
        # self.build_manager = BuildManager()

    def publish_package(self, ctx):
        try:
            self.log.info("Publishing Package on CodeArtifact...")

            # Build
            self.build_manager.build(ctx, project_path=self.project_path)

            # Carregar as configurações do projeto
            project_config = self.get_project_config(self.project_path)
            project_name = project_config['project_name']
            project_version = project_config['version']

            # Autenticar no CodeArtifact para client twine
            self.authenticate_codeartifact(ctx, project_config)

            # Publicar o pacote no CodeArtifact usando twine
            self.upload_to_codeartifact(ctx)

            self.log.info(f"Package {project_name} was successfully published on version {project_version}")

        except Exception as e:
            self.log.error(f"Error during publishing process: {e}")

    def authenticate_codeartifact(self, ctx, project_config):
        ctx.run(
            f"aws codeartifact login --tool twine --repository {project_config['codeartifact_repository']} "
            f"--domain {project_config['codeartifact_domain']} --domain-owner {project_config['aws_account_id']} "
            f"--region {project_config['aws_default_region']}", 
            echo=True
        )

    def upload_to_codeartifact(self, ctx):
        ctx.run("twine upload --repository codeartifact dist/*", echo=True)

