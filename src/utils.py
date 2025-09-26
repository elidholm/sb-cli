"""
Utility functions for managing the second-brain vault.
------------------------------------------------------

Functions:
    - find_vault_root: Locate the root of the second-brain vault.
    - sanitize_filename: Convert titles to safe filenames.
"""
import re
from pathlib import Path
from typing import Optional


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
