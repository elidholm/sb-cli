#!/usr/bin/env python

"""
Second Brain CLI Tool
---------------------

A command-line interface for managing your second-brain note system.
"""

from pathlib import Path
from typing import Optional
from rich import print
from datetime import datetime
import git
from git.exc import GitCommandError, InvalidGitRepositoryError

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
def sync(
    branch: Annotated[str, typer.Argument(help="Git branch to sync with.")] = "master",
    message: Annotated[str, typer.Option("--message", "-m", help="Git commit message.")] = f"vault backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Path to the sb config file.")] = "~/.sb_config.yml",
) -> None:
    """Sync the local instance of the Second Brain vault with the remote Git repository.

    First pulls changes from the remote repository and rebases local commits on top of them, then pushes
    local commits to the remote repository.
    """
    try:
        config = load_config(Path(config_file), vault_path)
    except InvalidVaultError as exc:
        print(f":cross_mark: [bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    print(f":brain: Syncing Second Brain Vault at [green]{config.vault_path}[/green] with remote repository branch [cyan]{branch}[/cyan]...")

    try:
        git_repo = git.Repo(config.vault_path)

        current_branch = git_repo.active_branch.name
        print(f"Current local branch: [cyan]{current_branch}[/cyan]")

        if git_repo.is_dirty(untracked_files=True):
            changed_files = []
            if diff := git_repo.index.diff(None):
                changed_files.extend([file.a_path for file in diff])
            if untracked := git_repo.untracked_files:
                changed_files.extend(untracked)

            print(f"\n:package: Staging {len(changed_files)} file(s)...")
            git_repo.git.add(A=True)

            commit = git_repo.index.commit(message)
            print(f":white_check_mark: Committed {len(changed_files)} file(s)")
            print(f":pencil: Message: '{message}'")
            print(f":keycap_number_sign: Commit hash: {commit.hexsha[:7]}")

            if changed_files:
                print("\n:open_file_folder: Changed files:")
                for f in changed_files[:10]:  # Show first 10 files
                    print(f"   - {f}")
                if len(changed_files) > 10:
                    print(f"   ... and {len(changed_files) - 10} more")
        else:
            print(":white_check_mark: No changes to commit.")

        print("\n:arrows_counterclockwise: Fetching from remote...")
        try:
            origin = git_repo.remote(name="origin")
            origin.fetch()
            print(":white_check_mark: Fetch [green]complete[/green]")

        except Exception as exc:
            print(f":cross_mark: [bold red]Failed to fetch from remote: {exc}[/bold red]")
            raise typer.Exit(code=1) from exc

        print(f"\n:shuffle_tracks_button: Rebasing local '[cyan]{current_branch}[/cyan]' onto 'origin/[cyan]{branch}[/cyan]'...")
        try:
            git_repo.git.rebase(f"origin/{branch}")
            print(":white_check_mark: Rebase [green]successful[/green]")
        except GitCommandError as exc:
            print(f":cross_mark: [bold red]Rebase failed: {exc}[/bold red]")
            print("\tAttempting to abort rebase...")
            try:
                git_repo.git.rebase("--abort")
                print("\tRebase aborted.")
            except Exception:
                print("\t:warning: [yellow]Failed to abort rebase. Manual intervention may be needed.[/yellow]")
            raise typer.Exit(code=1) from exc

        print(f"\n:arrow_up: Pushing to 'origin/[cyan]{branch}[/cyan]'...")
        try:
            origin.push(refspec=f"{current_branch}:{branch}")
            print(":white_check_mark: Push [green]successful[/green]")
        except GitCommandError as exc:
            print(f":cross_mark: [bold red]Push failed: {exc}[/bold red]")
            print("\t[red]You may need to pull or force push manually.[/red]")
            raise typer.Exit(code=1) from exc

        print("\n:party_popper: [bold green]All operations completed successfully![/bold green]")

    except InvalidGitRepositoryError:
        print(f":cross_mark: [bold red]'{config.vault_path}' is not a valid git repository.[/bold red]")
        raise typer.Exit(code=1)
    except GitCommandError as exc:
        print(f":cross_mark: [bold red]Git command failed: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        print(f":cross_mark: [bold red]Unexpected error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc


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
