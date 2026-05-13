import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from analyzer import detect_project, read_project_files
from prompt import build_prompt
from llm import ask_ollama, extract_dockerfile
from output import save_dockerfile

app = typer.Typer()
console = Console()

SUPPORTED = ["python", "node", "go", "java", "rust"]

@app.command()
def generate(
    path: str = typer.Argument(".", help="Path to your project folder")
):
    console.print(Panel("[bold cyan]Dockerfile Generator — Phase 2[/bold cyan]", expand=False))

    # Step 1: Analyze
    console.print("\n[yellow]Analyzing project...[/yellow]")
    info = detect_project(path)
    files = read_project_files(path)

    # Show detected info in a table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("Language",  f"[bold green]{info['language']}[/bold green]")
    table.add_row("Framework", f"[bold green]{info['framework']}[/bold green]")
    table.add_row("Version",   f"[bold green]{info['version']}[/bold green]")
    console.print(table)

    if info["language"] not in SUPPORTED:
        console.print(f"\n[bold red]Language '{info['language']}' not supported yet.[/bold red]")
        console.print("[dim]Supported: python, node, go, java, rust[/dim]")
        raise typer.Exit(1)

    # Step 2: Build prompt
    console.print("\n[yellow]Building prompt...[/yellow]")
    prompt = build_prompt(info, files)

    # Step 3: Ask LLM
    console.print("\n[yellow]Asking Ollama (codellama)...[/yellow]")
    response = ask_ollama(prompt)

    # Step 4: Extract
    console.print("\n[yellow]Extracting Dockerfile...[/yellow]")
    dockerfile = extract_dockerfile(response)

    if not dockerfile:
        console.print("[bold red]Could not extract a valid Dockerfile.[/bold red]")
        console.print("[dim]Raw response:[/dim]")
        console.print(response)
        raise typer.Exit(1)

    # Step 5: Save
    save_dockerfile(dockerfile, path)

    # Show preview
    console.print("\n[bold cyan]Preview:[/bold cyan]")
    console.print(Panel(dockerfile, title="Dockerfile", border_style="green"))

if __name__ == "__main__":
    app()