import os
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def show_markdown(doc_name):
    """Exibe o conteúdo Markdown do documento especificado."""
    doc_path = os.path.join(os.path.dirname(__file__), f"{doc_name}.md")
    if not os.path.exists(doc_path):
        console.print(f"[bold red]Documentação {doc_name} não encontrada.[/bold red]")
        return
    with open(doc_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    md = Markdown(markdown_content)
    console.print(md, justify="left")
