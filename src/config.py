"""
Configuration management for the second-brain CLI tool.
-------------------------------------------------------

Classes:
    - Config: Configuration model for the CLI tool.
    - InvalidVaultError: Custom exception for invalid vault paths.

Functions:
    - load_config: Load configuration from file and override with command-line options.

"""

from pathlib import Path
from typing import Optional, Union
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_file_as

from utils import find_vault_root


# Default Configuration
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


def load_config(config_file: Path, vault_path: Optional[Path]) -> Config:
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
        config.vault_path = find_vault_root(VAULT_NAME)
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
