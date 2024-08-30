import os
import site
import json
from pathlib import Path
from pilot.base.manager import BaseManager

class VscodeManager(BaseManager):

    def __init__(self, project_root=None):
        super().__init__()
        self.section_name = 'vscode'
        self.default_section = 'default_vscode'
        self.project_root = Path(project_root).resolve() if project_root else Path(os.getcwd())
        self.vscode_dir = self.project_root / ".vscode"
        self.launch_file = self.vscode_dir / "launch.json"
        self.settings_file = self.vscode_dir / "settings.json"
        self.ensure_vscode_directory()

    def init(self):
        """Initializes the 'vscode' section in the config file and sets up the VS Code environment."""
        if not self.config.has_section(self.section_name):
            self.config.add_section(self.section_name)
            self.save_config()

        if not self.vscode_dir.exists():
            self.vscode_dir.mkdir()
            self.log.info(f".vscode directory created at: {self.vscode_dir}")

        self.install_extensions_and_update_vscode()

        self.update()

    def ensure_vscode_directory(self):
        """Ensures the .vscode directory exists in the project."""
        if not self.vscode_dir.exists():
            self.vscode_dir.mkdir()

    def update(self):
        """Updates VS Code settings including launch.json and settings.json."""
        self.update_launch_json()
        self.update_settings_json()

    def update_launch_json(self):
        """Cria ou atualiza o arquivo launch.json com as configurações necessárias."""
        # Carrega o conteúdo existente, se houver
        launch_config = self.load_json_file(self.launch_file) or {
            "version": "0.2.0",
            "configurations": []
        }

        def upsert_configuration(configs, new_config):
            """Insere ou atualiza uma configuração baseada no nome."""
            for i, config in enumerate(configs):
                if config['name'] == new_config['name']:
                    configs[i] = new_config
                    return
            configs.append(new_config)

        # Adiciona ou atualiza a configuração principal para __main__.py
        main_py_path = self.find_main_py()
        if main_py_path:
            main_config = {
                "name": "Play Full Execution",
                "type": "debugpy",
                "request": "launch",
                "program": str(main_py_path),
                "console": "integratedTerminal",
                "justMyCode": False
            }
            upsert_configuration(launch_config['configurations'], main_config)

        # Adiciona ou atualiza configurações para cada arquivo de teste
        test_configs = self.create_test_configs()
        for test_config in test_configs:
            upsert_configuration(launch_config['configurations'], test_config)

        # Salva o arquivo JSON atualizado
        self.save_json_file(self.launch_file, launch_config)

    def update_settings_json(self):
        """Cria ou atualiza o arquivo settings.json com as configurações necessárias."""
        settings = self.load_json_file(self.settings_file) or {}

        # Configurações padrão
        extra_paths = settings.get("python.analysis.extraPaths", [])
        auto_complete_paths = settings.get("python.autoComplete.extraPaths", [])

        # Adiciona o caminho do workspace folder se ainda não estiver presente
        if "${workspaceFolder}" not in extra_paths:
            extra_paths.append("${workspaceFolder}")
        if "${workspaceFolder}" not in auto_complete_paths:
            auto_complete_paths.append("${workspaceFolder}")

        # Adiciona outros caminhos, por exemplo, os pacotes instalados como -e, se ainda não estiverem presentes
        editable_paths = self.find_editable_packages_paths()
        for path in editable_paths:
            if path not in extra_paths:
                extra_paths.append(path)
            if path not in auto_complete_paths:
                auto_complete_paths.append(path)

        # Define o modo de verificação de tipo para 'strict'
        settings["python.analysis.typeCheckingMode"] = "strict"
        settings["python.autoComplete.extraPaths"] = auto_complete_paths
        settings["python.analysis.extraPaths"] = extra_paths
        settings["python.analysis.autoImportCompletions"] = True

        self.save_json_file(self.settings_file, settings)

    def find_main_py(self):
        """Finds the path to the __main__.py file in the project."""
        for root, dirs, files in os.walk(self.project_root):
            if "__main__.py" in files:
                return Path(root) / "__main__.py"
        return None

    def create_test_configs(self):
        """Creates launch configurations for each test file."""
        test_configs = []
        test_dir = self.project_root / "tests"
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    config = {
                        "name": f"Test | {file}",
                        "type": "debugpy",
                        "request": "launch",
                        "program": str(Path(root) / file),
                        "console": "integratedTerminal",
                        "justMyCode": True
                    }
                    test_configs.append(config)
        return test_configs

    def find_editable_packages_paths(self):
        """Find paths of packages installed in editable mode."""
        editable_paths = []
        site_packages = Path(self.get_site_packages_directory())

        for dist_info_dir in site_packages.glob('*.dist-info'):
            direct_url_path = dist_info_dir / 'direct_url.json'
            if direct_url_path.exists():
                with open(direct_url_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    package_url = data.get('url')
                    if package_url and package_url.startswith('file://'):
                        package_path = package_url[len('file://'):]
                        editable_paths.append(package_path)
        
        return editable_paths

    def get_site_packages_directory(self):
        """Get the site-packages directory of the current virtual environment."""
        return next(iter(site.getsitepackages()), None)

    def install_extensions_and_update_vscode(self, extensions=None, update_vscode=False):
        """Instala extensões Python no VS Code e atualiza o VS Code, se necessário.

        Args:
            extensions (list): Uma lista de IDs de extensões a serem instaladas. Se não for fornecida, serão instaladas as extensões padrão.
            update_vscode (bool): Se True, atualiza o VS Code para a última versão.
        """
        if extensions is None:
            extensions = [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.debugpy",
                "donjayamanne.python-environment-manager",
                "njpwerner.autodocstring"
            ]
        
        # Instala extensões fornecidas ou padrão
        for extension in extensions:
            try:
                self.log.info(f"Instalando a extensão {extension} no VS Code...")
                result = self.ctx.run(f"code --install-extension {extension}")
                if result.return_code == 0:
                    self.log.info(f"Extensão {extension} instalada com sucesso.")
                else:
                    self.log.error(f"Erro ao instalar a extensão {extension}: {result.stderr}")
            except Exception as e:
                self.log.error(f"Erro inesperado ao instalar a extensão {extension}: {str(e)}")

        # Atualiza o VS Code se necessário
        if update_vscode:
            try:
                self.log.info("Atualizando o VS Code para a última versão...")
                result = self.ctx.run("code --install-update")
                if result.return_code == 0:
                    self.log.info("VS Code atualizado com sucesso.")
                else:
                    self.log.error(f"Erro ao atualizar o VS Code: {result.stderr}")
            except Exception as e:
                self.log.error(f"Erro inesperado ao atualizar o VS Code: {str(e)}")

    def load_json_file(self, file_path):
        """Carrega um arquivo JSON, removendo comentários se necessário."""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Remove linhas de comentários que começam com `//`
                content = "\n".join(line for line in content.splitlines() if not line.strip().startswith("//"))
                
                # Carrega o JSON do conteúdo sem os comentários
                return json.loads(content)
            except json.JSONDecodeError as e:
                self.log.error(f"Erro ao carregar JSON: {str(e)}")
                return None
        return None

    def save_json_file(self, file_path, content):
        """Saves content to a JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4)
