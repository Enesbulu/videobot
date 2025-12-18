from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.core.entities import Video
from typing import List


class ConsoleUI:
    def __init__(self):
        self.console = Console()

    def show_message(self, message: str, style: str = "white"):
        """Basit mesaj gösterir."""
        self.console.print(message, style=style)

    def show_header(self):
        self.console.print(Panel.fit(
            "[bold cyan]Video Downloader Bot[/bold cyan]\n"
            "[yellow]v0.3.0 - Architecture Edition[/yellow]",
            border_style="blue"
        ))

    def get_input(self, prompt: str) -> str:
        return self.console.input(f"[bold green]{prompt}[/bold green]").strip()

    def show_error(self, message: str):
        self.console.print(f"[bold red]❌ {message}[/bold red]")

    def show_success(self, message: str):
        self.console.print(f"[bold green]🎉 {message}[/bold green]")

    def show_video_table(self, videos: List[Video]):
        table = Table(title="Bulunan Videolar", show_lines=True)
        table.add_column("No", justify="right", style="cyan", no_wrap=True)
        table.add_column("Başlık", style="magenta")
        table.add_column("Çözünürlük", style="green")
        table.add_column("Süre", justify="right", style="yellow")

        for idx, video in enumerate(videos, 1):
            table.add_row(
                str(idx),
                video.title,
                video.resolution or "N/A",
                video.duration or "N/A",
            )
        self.console.print(table)

    def create_spinner(self, text: str):
        return self.console.status(f"[bold green]{text}[/bold green]", spinner="dots")
