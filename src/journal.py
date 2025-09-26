"""
CLI tool to create daily journal entries in an Obsidian vault.
--------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from rich import print
import textwrap

import typer
from typing_extensions import Annotated

from config import InvalidVaultError, load_config

app = typer.Typer(
    name="journal",
    help="Commands to manage journal entries.",
    no_args_is_help=True,
)


@app.command()
def daily(
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Path to the sb config file.")] = "~/.sb_config.yml",
) -> None:
    """Create a new daily journal entry."""
    try:
        config = load_config(Path(config_file), vault_path)
    except InvalidVaultError as exc:
        print(f":cross_mark: [bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    daily_path = config.vault_path / "2_Areas/Journal/Daily"
    daily_path.mkdir(parents=True, exist_ok=True)

    todays_date = datetime.now().strftime("%Y-%m-%d")
    note_path = daily_path / f"{todays_date}.md"

    if note_path.exists():
        print(f":information: [yellow]Daily note for {todays_date} already exists.[/yellow]")
        raise typer.Exit(code=0)

    created_time = datetime.now().strftime("%H:%M")

    content = textwrap.dedent(f"""\
            # {todays_date}

            # Daily Goals

            - [ ] 15 minutes of touch typing practice
            - [ ] Review and prioritize tasks for the day
            - [ ] Read three pages of the Bible
            - [ ] 3 Sporcle quizzes

            ## Today's Focus

            - [ ]

            ## What I Did

            ### Work/Projects

            ### Personal

            ### Learning

            ## Reflections

            ### What went well?

            ### What could be improved?

            ### Tomorrow's priorities

            -

            ## Captured Ideas

            <!-- Quick thoughts, links, or ideas to process later -->

            ---

            **Created**: {todays_date} at {created_time}
            **Energy Level**: /10
            **Mood**:
            **Weather**:
            **Tags**:""")

    try:
        with note_path.open("w", encoding="utf-8") as f:
            f.write(content)
    except Exception as exc:
        print(f":cross_mark: [bold red]Failed to create daily journal entry: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    relative_path = note_path.relative_to(config.vault_path)
    print(f":white_check_mark: [green]Daily journal created:[/green] {relative_path}")


if __name__ == "__main__":
    app()
