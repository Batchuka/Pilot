# pilot/src/git.py
import os
import platform
from pathlib import Path
from shutil import copyfile, copytree

from pilot.base.manager import BaseManager

class GitManager(BaseManager):

    def __init__(self, repo_path=None):
        super().__init__()
        self.section_name = 'git'
        self.default_section = 'default_git'
        self.repo_path = Path(repo_path).resolve() if repo_path else None
        self.hooks_path = None
        self.os_type = platform.system().lower()
        self.scripts_path = Path(__file__).resolve().parent.parent / "scripts" / ("linux" if "linux" in self.os_type else "windows")

    def init(self):
        """Inicializa a sessão 'git' no arquivo de configuração e configura o ambiente Git."""
        if not self.config.has_section(self.section_name):
            self.config.add_section(self.section_name)
            self.save_config()

        repo_path = self.encontra_repo_git(Path(os.getcwd()))
        if repo_path:
            self.repo_path = repo_path
            self.config.set(self.section_name, 'repo_path', str(repo_path))
            self.save_config()
            self.log.info(f"Repositório Git encontrado em: {repo_path}")
            self.configura_repo()
        else:
            self.log.warning("Nenhum repositório Git encontrado na pasta atual ou nas pastas pai.")

    def encontra_repo_git(self, start_path):
        """Procura por um repositório Git na pasta atual ou nas pastas pai."""
        current_path = start_path
        while current_path != current_path.parent:
            if (current_path / ".git").exists():
                return current_path
            current_path = current_path.parent
        return None

    def instala_hooks(self):
        """Copia os scripts de hook para o diretório de hooks do Git."""
        self.hooks_path = self.repo_path / ".git" / "hooks"
        for script in self.scripts_path.glob("*"):
            hook_name = script.name
            dest_path = self.hooks_path / hook_name
            copyfile(script, dest_path)
            os.chmod(dest_path, 0o755)  # Permissão de execução

    def checa_diff_sugere_commit(self):
        """Verifica a quantidade de modificações e sugere um commit."""
        changed_files = self.ctx.run("git status --porcelain").stdout
        num_changes = len(changed_files.splitlines())

        if num_changes > 5:  # Um limiar para sugerir commit
            self.log.warning(f"Você tem MAIS DE {num_changes} ARQUIVOS MODIFICADOS! Considere fazer COMMITS MENORES.")

    def pergunta_severidade_alteracao(self):
        """Pergunta ao usuário sobre a severidade das mudanças para criar uma tag."""
        while True:
            severity_input = input("Minha alteração é (major[1], feature[2], bugfix[3]): ")
            type_mapping = {'1': "major", '2': "feature", '3': "bugfix"}
            severity = type_mapping.get(severity_input)

            if severity:
                return severity
            else:
                self.log.error("Tipo de alteração inválido. Por favor, escolha 1, 2 ou 3.")

    def cria_tag_semantica(self, severity):
        """Cria uma tag de versão semântica com base na severidade."""
        try:
            last_tag = self.ctx.run("git describe --tags --abbrev=0").stdout.strip()

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
            self.ctx.run(f'git tag -a \"{new_tag}\" -m \"Release version {new_tag}\"')
            self.log.info(f"Tag {new_tag} criada e enviada com sucesso.")
        except Exception as e:
            self.log.error(f"Erro ao criar tag semântica: {str(e)}")

    def configura_repo(self):
        """Instala os hooks e configura o repositório."""
        self.instala_hooks()

    def commit(self):
        """Executa o processo completo de commit, desde a criação da mensagem até o push."""
        # Verifica se há um repositório configurado
        if not self.repo_path:
            self.init()

        # Se ainda não houver repositório, encerra a operação
        if not self.repo_path:
            self.log.error("Não foi possível encontrar um repositório Git para operar.")
            return

        # Verifica a quantidade de mudanças e sugere um commit
        self.checa_diff_sugere_commit()

        # Coleta a mensagem de commit
        impact = input("Se aplicado, meu commit (irá...): ")
        modification = input("O meu commit (modificou...): ")

        # Pega a severidade da modificação
        severidade = self.pergunta_severidade_alteracao()

        commit_message = f"[Impacto]: {impact} [Modificações]: {modification} [Severidade]: {severidade}"
        commit_message = commit_message.encode('utf-8').decode('utf-8')

        # Executa o commit com a mensagem formatada
        result = self.ctx.run("git add .")

        if result.return_code == 0:
            commit_command = f'git commit -m "{commit_message}"'
            result = self.ctx.run(commit_command)
            
            if result.return_code == 0:
                self.log.info("Commit realizado com sucesso.")
            else:
                self.log.error("Erro ao realizar o commit.")
        else:
            self.log.error("Erro ao adicionar arquivos ao commit.")

        if result:
            self.log.info("Commit realizado com sucesso.")

            # Aplica tag no repo com base na severidade
            self.cria_tag_semantica(severidade)

        else:
            self.log.error("Falha ao adicionar tag semântica")
