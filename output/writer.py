from pathlib import Path
from config import OUTPUT_FILENAME
from rich.console import Console

console = Console()

def save_dockerfile(content: str, destination: str = ".") -> str:
    out = Path(destination) / OUTPUT_FILENAME
    out.write_text(content)
    console.print(f"\n[bold green]Dockerfile saved to:[/bold green] {out.resolve()}")
    return str(out.resolve())