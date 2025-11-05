"""
CLI tool for creating new notes in an Obsidian vault.
"""

import textwrap
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.prompt import Confirm, Prompt
from typing_extensions import Annotated

import bible
import journal
from config import InvalidVaultError, load_config
from utils import daily_exists, format_hashtags, sanitize_filename

app = typer.Typer(
    name="new",
    help="Commands to create new notes.",
    add_completion=False,
)
app.add_typer(journal.app, name="journal")
app.add_typer(bible.app, name="bible")


@app.callback(invoke_without_command=True)
def new_callback(ctx: typer.Context):
    """
    Create a new note. If no subcommand is provided, creates an empty note.
    """
    if ctx.invoked_subcommand is None:
        new_note = Confirm.ask("No subcommand provided. Create an empty note?", default=True)
        if new_note:
            ctx.invoke(empty)
        else:
            print("Use 'sb new --help' to see available subcommands.")
            ctx.exit()


@app.command(name="empty")
def empty(
    ctx: typer.Context,
    title: Annotated[Optional[str], typer.Argument(help="Title for the new note.")] = None,
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[
        str, typer.Option("--config", "-c", help="Path to the sb config file.")
    ] = "~/.sb_config.yml",
    tags: Annotated[
        Optional[str], typer.Option("--tags", "-t", help="Comma-separated tags to include in the note.")
    ] = None,
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

    daily_path = config.vault_path / "2_Areas/Journal/Daily" / (created_date + ".md")
    if not daily_exists(daily_path):
        ctx.invoke(journal.daily)
        print(f":spiral_notepad: [yellow]Created daily note for {created_date}.[/yellow]")

    content = textwrap.dedent(f"""\
            # {title}

            ---

            **Created**: {created_date} at {created_time}
            **Tags**: {format_hashtags(tags)}""")

    try:
        with note_path.open("w", encoding="utf-8") as f:
            f.write(content)
        with daily_path.open("a", encoding="utf-8") as f:
            f.write(f"[[{note_filename}]]")

    except Exception as exc:
        print(f":cross_mark: [bold red]Failed to create note: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    relative_path = note_path.relative_to(config.vault_path)
    print(f":white_check_mark: [green]Note created:[/green] {relative_path}")


if __name__ == "__main__":
    app()
