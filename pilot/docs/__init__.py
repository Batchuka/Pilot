# pilot/docs/__init__.py
import os

from rich.console import Console
from rich.markdown import Markdown
from rich.console import Console
from rich.table import Table

console = Console()

# Defina um dicionário de mapeamento entre os nomes dos documentos e seus arquivos correspondentes
DOCS_MAPPING = {
    'aws': 'aws.md',
    'docker': 'docker.md',
    'git': 'git.md',
    'docker_remote_pipeline': 'remote_docker.md',
    'deploy': 'deploy.md',
    'aws_conf': 'aws_conf.md',
    'deploy_conf': 'deploy_conf.md',
    'docker_conf': 'docker_conf.md',
    'git_conf': 'git_conf.md',
    'readme': 'readme.md'
}

def show_markdown(doc_name):
    """Exibe o conteúdo Markdown do documento especificado."""
    
    if doc_name in DOCS_MAPPING:
        doc_path = os.path.join(os.path.dirname(__file__), DOCS_MAPPING[doc_name])
        if not os.path.exists(doc_path):
            console.print(f"[bold red]Documentação {doc_name} não encontrada.[/bold red]")
            return
        with open(doc_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        md = Markdown(markdown_content)
        console.print(md, justify="left")
    else:
        console.print(f"[bold red]Documentação '{doc_name}' não encontrada.[/bold red]")
        list_available_docs()

def list_available_docs():
    """Lista as documentações disponíveis em colunas de 3 itens cada."""
    console.print("Documentações disponíveis:", style="bold blue")
    
    table = Table(show_header=False, box=None)
    
    # Configura três colunas para exibir as documentações
    table.add_column()
    table.add_column()
    table.add_column()

    # Divide os documentos em linhas de 3 colunas
    docs = list(DOCS_MAPPING.keys())
    for i in range(0, len(docs), 3):
        row = docs[i:i + 3]
        table.add_row(*row)

    console.print(table)
    console.print("\n\n")