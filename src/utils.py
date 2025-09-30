"""
Utility functions for managing the second-brain vault.
------------------------------------------------------

Functions:
    - daily_exists: Check if a daily note for a given date exists.
    - find_vault_root: Locate the root of the second-brain vault.
    - sanitize_filename: Convert titles to safe filenames.
    - format_hashtags: Format a string of hashtags.
"""
import re
from pathlib import Path
from typing import Optional
from datetime import datetime


def daily_exists(date: datetime, daily_path: Path) -> bool:
    """Check if a daily note for the given date already exists in the inbox.

    Args:
        date (datetime): The date to check for.
        daily_path (Path): The path to the daily notes directory.

    Returns:
        bool: True if the daily note exists, False otherwise.
    """
    daily_filename = date.strftime("%Y-%m-%d") + ".md"
    daily_file_path = daily_path / daily_filename
    return daily_file_path.exists()


def find_vault_root(vault_name: str) -> Optional[Path]:
    """Find the second-brain vault by searching up the directory tree.

    Args:
        vault_name (str): The name of the vault directory to search for.

    Returns:
        Optional[Path]: The path to the vault root if found, otherwise None.
    """
    current = Path.cwd()

    # Search up the directory tree
    while current != current.parent:
        potential_vault = current / vault_name
        if potential_vault.exists() and potential_vault.is_dir():
            return potential_vault
        current = current.parent

    # Also check if we're already inside the vault
    current = Path.cwd()
    while current != current.parent:
        if current.name == vault_name:
            return current
        current = current.parent

    return None


def sanitize_filename(title: str) -> str:
    """Convert a title to a safe filename.

    Removes special characters and replaces paces with underscores.

    Args:
        title (str): The title to sanitize.

    Returns:
        str: A sanitized filename.
    """
    filename = title.strip().replace(" ", "_")
    filename = re.sub(r"[^a-zA-Z0-9\-_]", "", filename)
    filename = re.sub(r"-+", "-", filename)
    filename = re.sub(r"_+", "_", filename)
    filename = filename.strip("-_")

    if not filename:
        filename = "untitled"

    return filename.lower()


def format_hashtags(hashtags: Optional[str]) -> str:
    """Format a comma-separated string of hashtags into a space-separated string.

    Args:
        hashtags (Optional[str]): Comma-separated hashtags.

    Returns:
        str: Space-separated hashtags prefixed with '#'.
    """
    if not hashtags:
        return ""

    tags = [tag.strip() for tag in hashtags.split(",") if tag.strip()]
    return " ".join(f"#{tag}" for tag in tags)
