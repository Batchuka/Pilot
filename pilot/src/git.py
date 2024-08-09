# pilot/src/git.py
import os
import subprocess
import platform
from pathlib import Path
from shutil import copyfile, copytree

class GitManager:

    def __init__(self, repo_path):
        self.repo_path = Path(repo_path).resolve()
        self.hooks_path = self.repo_path / ".git" / "hooks"
        self.os_type = platform.system().lower()
        self.scripts_path = Path(__file__).resolve().parent.parent / "scripts" / ("linux" if "linux" in self.os_type else "windows")

    def initialize_hooks(self):
        """Instala os hooks no repositório atual."""
        self.install_hooks()
        self.configure_for_user()

    def install_hooks(self):
        """Copia os scripts de hook para o diretório de hooks do Git."""
        for script in self.scripts_path.glob("*"):
            hook_name = script.name
            dest_path = self.hooks_path / hook_name
            copyfile(script, dest_path)
            os.chmod(dest_path, 0o755)  # Permissão de execução

    def configure_for_user(self):
        """Configura o Git globalmente para sempre usar os hooks."""
        if self.os_type == 'windows':
            git_config_cmd = 'git config --global core.hooksPath C:/Users/{username}/.githooks'.format(username=os.getlogin())
        else:
            git_config_cmd = 'git config --global core.hooksPath ~/.githooks'

        subprocess.run(git_config_cmd, shell=True)

        # Copia os hooks para o diretório de hooks global
        global_hooks_path = Path.home() / ".githooks"
        global_hooks_path.mkdir(exist_ok=True)

        for script in self.scripts_path.glob("*"):
            dest_path = global_hooks_path / script.name
            copyfile(script, dest_path)
            os.chmod(dest_path, 0o755)  # Permissão de execução

    def apply_hooks_to_cloned_repo(self):
        """Copia os hooks para um repositório clonado."""
        self.install_hooks()

    def check_modifications_and_suggest_commit(self):
        """Verifica a quantidade de modificações e sugere um commit."""
        changed_files = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_path, capture_output=True, text=True).stdout
        num_changes = len(changed_files.splitlines())

        if num_changes > 10:  # Um limiar para sugerir commit
            print(f"Você tem {num_changes} arquivos modificados. Considere fazer um commit.")

    def prompt_for_tag_after_commit(self):
        """Pergunta ao usuário se deseja adicionar uma tag após um commit."""
        subprocess.run(["git", "commit"], cwd=self.repo_path)

        add_tag = input("Você deseja adicionar uma tag para este commit? (s/n): ")
        if add_tag.lower() == 's':
            severity = input("Qual a severidade das mudanças? (bugfix, feature, major): ")
            self.create_semantic_version_tag(severity)

    def create_semantic_version_tag(self, severity):
        """Cria uma tag de versão semântica com base na severidade."""
        last_tag = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], cwd=self.repo_path, capture_output=True, text=True).stdout.strip()
        major, minor, patch = map(int, last_tag.lstrip('v').split('.'))

        if severity == 'major':
            major += 1
            minor = 0
            patch = 0
        elif severity == 'feature':
            minor += 1
            patch = 0
        elif severity == 'bugfix':
            patch += 1

        new_tag = f"v{major}.{minor}.{patch}"
        subprocess.run(["git", "tag", "-a", new_tag, "-m", f'Release version {new_tag}'], cwd=self.repo_path)
        subprocess.run(["git", "push", "origin", new_tag], cwd=self.repo_path)

    def setup_repo(self):
        """Instala os hooks e configura o repositório."""
        self.initialize_hooks()
        self.check_modifications_and_suggest_commit()
        self.prompt_for_tag_after_commit()


# Uso da classe
# git_manager = GitManager('/caminho/para/seu/repo')
# git_manager.initialize_hooks()
# git_manager.apply_hooks_to_cloned_repo()
# git_manager.configure_for_user()
