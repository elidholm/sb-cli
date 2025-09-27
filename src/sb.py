#!/usr/bin/env python

"""Second Brain CLI Tool
A command-line interface for managing your second-brain note system.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from rich import print
from rich.prompt import Prompt
import textwrap

import typer
from typing_extensions import Annotated

from config import InvalidVaultError, load_config
from utils import format_hashtags, sanitize_filename
import journal

app = typer.Typer(
    name="sb",
    help="Second Brain CLI - Manage your note-taking system",
    add_completion=False,
    no_args_is_help=True,
)
app.add_typer(journal.app, name="journal")


@app.command()
def new(
    title: Annotated[Optional[str], typer.Argument(help="Title for the new note.")] = None,
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Path to the sb config file.")] = "~/.sb_config.yml",
    tags: Annotated[Optional[str], typer.Option("--tags", "-t", help="Comma-separated tags to include in the note.")] = None,
) -> None:
    """Create a new empty note in the inbox folder."""
    try:
        config = load_config(Path(config_file), vault_path)
    except InvalidVaultError as exc:
        print(f":cross_mark: [bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if not title:
        title = Prompt.ask(":spiral_notepad: Enter the title of the new note")

    note_filename = sanitize_filename(title)
    if not note_filename.endswith(".md"):
        note_filename += ".md"

    inbox_path = config.vault_path / config.inbox_folder
    inbox_path.mkdir(exist_ok=True)

    note_path = inbox_path / note_filename

    counter = 1
    original_path = note_path
    while note_path.exists():
        name_without_ext = original_path.stem
        note_filename = f"{name_without_ext}_{counter}.md"
        note_path = inbox_path / note_filename
        counter += 1

    created_date = datetime.now().strftime("%Y-%m-%d")
    created_time = datetime.now().strftime("%H:%M")

    content = textwrap.dedent(f"""\
            # {title}

            ---
            **Created**: {created_date} at {created_time}
            **Tags**: {format_hashtags(tags)}""")

    try:
        with note_path.open("w", encoding="utf-8") as f:
            f.write(content)
    except Exception as exc:
        print(f":cross_mark: [bold red]Failed to create note: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    relative_path = note_path.relative_to(config.vault_path)
    print(f":white_check_mark: [green]Note created:[/green] {relative_path}")


@app.command()
def info(
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Path to the sb config file.")] = "~/.sb_config.yml",
) -> None:
    """Display information about the current vault and system status."""
    try:
        config = load_config(Path(config_file), vault_path)
    except InvalidVaultError as exc:
        print(f":cross_mark: [bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    print(f":brain: Second Brain Vault: [green]{config.vault_path}[/green]")

    # Check folder structure
    folders = ["0_Inbox", "1_Projects", "2_Areas", "3_Resources", "4_Archive"]
    print("\n:open_file_folder: Folder Structure:")
    for folder in folders:
        folder_path = config.vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            md_files = list(folder_path.glob("**/*.md"))
            print(f"\t:white_check_mark: [green]{folder}[/green] ({len(md_files)} notes)")
        else:
            print(f"\t:cross_mark: [red]{folder} (missing)[/red]")

    # Inbox status
    inbox_path = config.vault_path / config.inbox_folder
    if inbox_path.exists() and inbox_path.is_dir():
        inbox_files = list(inbox_path.glob("*.md"))
        if inbox_files:
            print(f"\n:inbox_tray: Inbox has [yellow]{len(inbox_files)}[/yellow] unprocessed notes")
            if len(inbox_files) > 5:
                print("\t:light_bulb: [yellow]Consider doing a weekly review![/yellow]")
        else:
            print("\n:inbox_tray: Inbox is empty :sparkles:")
    else:
        print(f"\n:cross_mark: [red]{config.inbox_folder} folder is missing![/red]")


if __name__ == "__main__":
    app()
