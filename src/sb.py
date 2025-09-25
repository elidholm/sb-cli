#!/usr/bin/env python3
"""Second Brain CLI Tool
A command-line interface for managing your second-brain note system.
"""

from pathlib import Path
from typing import Optional
from rich import print

import typer

app = typer.Typer(
    name="sb",
    help="Second Brain CLI - Manage your note-taking system",
    add_completion=False,
)

# Configuration
VAULT_NAME = "second-brain"
INBOX_FOLDER = "0_Inbox"


def _find_vault_root() -> Optional[Path]:
    """Find the second-brain vault by searching up the directory tree.

    Returns:
        Optional[Path]: The path to the vault root if found, otherwise None.
    """
    current = Path.cwd()

    # Search up the directory tree
    while current != current.parent:
        potential_vault = current / VAULT_NAME
        if potential_vault.exists() and potential_vault.is_dir():
            return potential_vault
        current = current.parent

    # Also check if we're already inside the vault
    current = Path.cwd()
    while current != current.parent:
        if current.name == VAULT_NAME:
            return current
        current = current.parent

    return None


@app.command()
def info() -> None:
    """Display information about the current vault and system status."""
    vault_path = _find_vault_root()

    if not vault_path:
        print(":cross_mark: [bold red]No second-brain vault found![/bold red]")
        print("[red]Make sure you're in or under your vault directory.[/red]")
        return

    print(f":brain: Second Brain Vault: [green]{vault_path}[/green]")

    # Check folder structure
    folders = ["0_Inbox", "1_Projects", "2_Areas", "3_Resources", "4_Archive"]
    print("\n:open_file_folder: Folder Structure:")
    for folder in folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            md_files = list(folder_path.glob("**/*.md"))
            print(f"\t:white_check_mark: [green]{folder}[/green] ({len(md_files)} notes)")
        else:
            print(f"\t:cross_mark: [red]{folder} (missing)[/red]")

    # Inbox status
    inbox_path = vault_path / INBOX_FOLDER
    if inbox_path.exists() and inbox_path.is_dir():
        inbox_files = list(inbox_path.glob("*.md"))
        if inbox_files:
            print(f"\n:inbox_tray: Inbox has [yellow]{len(inbox_files)}[/yellow] unprocessed notes")
            if len(inbox_files) > 5:
                print("\t:light_bulb: [yellow]Consider doing a weekly review![/yellow]")
        else:
            print("\n:inbox_tray: Inbox is empty :sparkles:")
    else:
        print(f"\n:cross_mark: [red]{INBOX_FOLDER} folder is missing![/red]")


if __name__ == "__main__":
    app()
