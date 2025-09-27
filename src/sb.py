#!/usr/bin/env python

"""
Second Brain CLI Tool
---------------------

A command-line interface for managing your second-brain note system.
"""

from pathlib import Path
from typing import Optional
from rich import print

import typer
from typing_extensions import Annotated

from config import InvalidVaultError, load_config
import new

app = typer.Typer(
    name="sb",
    help="Second Brain CLI - Manage your note-taking system",
    add_completion=False,
    no_args_is_help=True,
)
app.add_typer(new.app, name="new")


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
