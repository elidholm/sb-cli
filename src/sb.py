#!/usr/bin/env python
"""Second Brain CLI Tool
A command-line interface for managing your second-brain note system.
"""

from pathlib import Path
from typing import Optional, Union
from rich import print

from pydantic import BaseModel
from pydantic_yaml import parse_yaml_file_as

import typer
from typing_extensions import Annotated

app = typer.Typer(
    name="sb",
    help="Second Brain CLI - Manage your note-taking system",
    add_completion=False,
)

# Configuration
VAULT_NAME = "second-brain"
INBOX_FOLDER = "0_Inbox"


class InvalidVaultError(Exception):
    """Custom exception for invalid vault paths."""
    pass


class Config(BaseModel):
    """Configuration model for the second-brain CLI."""
    vault_path: Optional[Path] = None
    inbox_folder: str = INBOX_FOLDER

    @staticmethod
    def load(filename: Union[str, Path]) -> Optional["Config"]:
        """Load configuration from a YAML file.

        Args:
            filename (Union[str, Path]): Path to the configuration file.

        Returns:
            Optional[Config]: Loaded configuration object or None if config file not found.
        """
        if not Path(filename).exists():
            print(f":warning: [yellow]Config file {filename} not found. Using defaults.[/yellow]")
            return None
        return parse_yaml_file_as(Config, filename)


def _load_config(config_file: Path, vault_path: Optional[Path]) -> Config:
    """Load configuration from file and override with command-line options.

    Args:
        config_file (Path): Path to the configuration file.
        vault_path (Optional[Path]): Command-line specified vault path.

    Returns:
        Config: Loaded configuration object.

    Raises:
        InvalidVaultError: If the specified vault path is invalid.
    """
    config = Config.load(config_file.expanduser()) or Config()
    if not config.vault_path:
        config.vault_path = _find_vault_root()
    if vault_path:
        config.vault_path = vault_path

    if not config.vault_path:
        raise InvalidVaultError("No second-brain vault found.")

    config.vault_path = config.vault_path.expanduser()

    if not config.vault_path.exists() or not config.vault_path.is_dir():
        raise InvalidVaultError(f"Invalid vault path: {config.vault_path}")

    if not (config.vault_path / ".obsidian").exists():
        raise InvalidVaultError(f"{config.vault_path} is not a valid Obsidian vault.")

    return config


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
def info(
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Path to the sb config file.")] = "~/.sb_config.yml",
) -> None:
    """Display information about the current vault and system status."""
    try:
        config = _load_config(Path(config_file), vault_path)
    except InvalidVaultError as exc:
        print(f":cross_mark: [bold red]{exc}[/bold red]")
        return

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
