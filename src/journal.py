"""
CLI tool to create daily journal entries in an Obsidian vault.
--------------------------------------------------------------
"""

import textwrap
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich import print
from typing_extensions import Annotated

from config import InvalidVaultError, load_config
from utils import format_hashtags

app = typer.Typer(
    name="journal",
    help="Commands to manage journal entries.",
    no_args_is_help=True,
)


@app.command(name="monthly")
def monthly(
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[
        str, typer.Option("--config", "-c", help="Path to the sb config file.")
    ] = "~/.sb_config.yml",
    tags: Annotated[
        Optional[str], typer.Option("--tags", "-t", help="Comma-separated tags to include in the note.")
    ] = None,
) -> None:
    """Create a new monthly reflection entry."""
    try:
        config = load_config(Path(config_file), vault_path)
    except InvalidVaultError as exc:
        print(f":cross_mark: [bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    monthly_path = config.vault_path / "2_Areas/Journal/Monthly-Reflection"
    monthly_path.mkdir(parents=True, exist_ok=True)

    this_month = datetime.now().strftime("%b-%Y")
    note_path = monthly_path / f"{this_month}.md"

    if note_path.exists():
        print(f":information: [yellow]Monthly reflection for {this_month} already exists.[/yellow]")
        raise typer.Exit(code=0)

    created_date = datetime.now().strftime("%Y-%m-%d")

    content = textwrap.dedent(f"""\
            # {this_month.replace("-", " - ")} Monthly Reflection

            **Review Date**: {created_date}
            **Overall Month Rating**: /10

            ## Month at a Glance

            **Theme for the Month**:
            **Major Events**:
            -
            -
            -

            ## Projects Review

            ### Completed Projects:

            - ✅ Project 1 - *Impact/Outcome*
            - ✅ Project 2 - *Impact/Outcome*

            ### Ongoing Projects Progress:

            | Project | Started | Progress | Blockers | Target Completion |
            |---------|---------|----------|----------|-------------------|
            |         |         | %        |          |                   |

            ### Projects to Archive/Pause:

            - [ ] Project → Reason for archiving
            - [ ] Project → Reason for pausing

            ## Areas Deep Dive

            ### Health & Wellness

            **Rating**: /10
            **Highlights**:
            **Improvements needed**:
            **Next month focus**:

            ### Work/Career

            **Rating**: /10
            **Major accomplishments**:
            **Challenges faced**:
            **Skills developed**:
            **Next month focus**:

            ### Relationships

            **Rating**: /10
            **Quality time with**:
            **Relationships that need attention**:
            **Next month focus**:

            ### Learning & Growth

            **Rating**: /10
            **New skills/knowledge**:
            **Books completed**:
            **Courses/Training**:
            **Next month focus**:

            ### Finances

            **Rating**: /10
            **Financial goals progress**:
            **Major expenses**:
            **Areas for improvement**:
            **Next month focus**:

            ### Personal/Spiritual

            **Rating**: /10
            **Spiritual practices**:
            **Personal development**:
            **Values alignment**:
            **Next month focus**:

            ## Knowledge System Review

            ### Notes Created:

            ### Most Valuable Notes:

            -
            -
            -

            ### System Improvements:

            **What's working well**:

            **What needs adjustment**:

            **Changes to implement**:

            ## Celebrations & Gratitude

            ### Proud moments:

            1.
            2.
            3.

            ### Grateful for:

            -
            -
            -

            ## Lessons & Insights

            ### Key learnings this month:

            ### Patterns I noticed:

            ### Habits that served me well:

            ### Habits to change:

            ## Next Month Planning

            ### Theme/Focus for Next Month:

            ### Top 3 Goals:

            1.
            2.
            3.

            ### Areas requiring attention:

            -
            -

            ### Experiments to try:

            -
            -

            ### Important dates/events:

            -
            -

            ## Metrics & Tracking

            <!-- Add any personal metrics you track -->

            ### Health Metrics:

            **Exercise days**: /30
            **Sleep average**: hours
            **Energy level average**: /10

            ### Productivity Metrics:

            **Deep work hours**:
            **Books read**:
            **Articles/papers read**:

            ### Relationship Metrics:

            **Quality time with family**:
            **Social activities**:
            **New connections made**:

            ---

            **Tags**: #monthly-review #reflection {format_hashtags(tags)}
            **Previous Month**: [[{(datetime.now() - timedelta(days=31)).strftime("%b-%Y")}]]
            **Next Month**: [[{(datetime.now() + timedelta(days=28)).strftime("%b-%Y")}]]""")

    try:
        with note_path.open("w", encoding="utf-8") as f:
            f.write(content)
    except Exception as exc:
        print(f":cross_mark: [bold red]Failed to create monthly reflection: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    relative_path = note_path.relative_to(config.vault_path)
    print(f":white_check_mark: [green]Monthly reflection created:[/green] {relative_path}")


@app.command(name="weekly")
def weekly(
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[
        str, typer.Option("--config", "-c", help="Path to the sb config file.")
    ] = "~/.sb_config.yml",
    tags: Annotated[
        Optional[str], typer.Option("--tags", "-t", help="Comma-separated tags to include in the note.")
    ] = None,
) -> None:
    """Create a new weekly review entry."""
    try:
        config = load_config(Path(config_file), vault_path)
    except InvalidVaultError as exc:
        print(f":cross_mark: [bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    weekly_path = config.vault_path / "2_Areas/Journal/Weekly-Review"
    weekly_path.mkdir(parents=True, exist_ok=True)

    this_week = f"{int(datetime.now().strftime('%W')) + 1}-{datetime.now().strftime('%Y')}"
    note_path = weekly_path / f"{this_week}.md"

    if note_path.exists():
        print(f":information: [yellow]Weekly review for {this_week} already exists.[/yellow]")
        raise typer.Exit(code=0)

    created_date = datetime.now().strftime("%Y-%m-%d")

    inbox_path = config.vault_path / config.inbox_folder
    if inbox_path.exists() and inbox_path.is_dir():
        inbox_files = [path.stem for path in list(inbox_path.glob("*.md"))]

    items_to_process = (
        "\n".join(f"- [ ] [[{item}]] → Move to:" for item in inbox_files) if inbox_files else "- [ ] No items in inbox."
    )

    content = textwrap.dedent(f"""\
# Week {this_week.replace("-", " - ")} Review

**Review Date**: {created_date}
**Energy This Week**: /10
**Overall Rating**: /10

## Inbox Processing

### Items to Process:

{items_to_process}

## Projects Review

### Active Projects Status:

| Project | Status | Next Action | Priority |
|---------|--------|-------------|----------|
|         | 🟢/🟡/🔴 |            | H/M/L    |
|         | 🟢/🟡/🔴 |            | H/M/L    |

### Projects to Archive:

- [ ] Completed project 1
- [ ] Stalled project 2

## Areas Review

### Health Check:

| Area | Current State | Needs Attention? | Action |
|------|---------------|------------------|--------|
|      | 🟢/🟡/🔴      | Yes/No          |        |
|      | 🟢/🟡/🔴      | Yes/No          |        |

## Wins This Week

-

## Challenges & Lessons

### What didn't go as planned?

### What did I learn?

### What would I do differently?

## Next Week Planning

### Top 3 Priorities:

1.
2.
3.

### Calendar & Commitments Review:

<!-- Check upcoming meetings, deadlines, appointments -->

### Areas Needing Focus:

-
-

## Learning & Growth

### This week I learned:

### Books/Articles read:

### Skills practiced:

---

**Tags**: #weekly-review #reflection {format_hashtags(tags)}
**Previous Week**: [[{(datetime.now() - timedelta(weeks=1)).strftime("%W-%Y")}]]
**Next Week**: [[{(datetime.now() + timedelta(weeks=1)).strftime("%W-%Y")}]]""")

    try:
        with note_path.open("w", encoding="utf-8") as f:
            f.write(content)
    except Exception as exc:
        print(f":cross_mark: [bold red]Failed to create weekly review: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    relative_path = note_path.relative_to(config.vault_path)
    print(f":white_check_mark: [green]Weekly review created:[/green] {relative_path}")


@app.command(name="daily")
def daily(
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[
        str, typer.Option("--config", "-c", help="Path to the sb config file.")
    ] = "~/.sb_config.yml",
    tags: Annotated[
        Optional[str], typer.Option("--tags", "-t", help="Comma-separated tags to include in the note.")
    ] = None,
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

            ## Daily Goals

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
            **Tags**: #daily-journal #reflection {format_hashtags(tags)}
            **Yesterday**: [[{(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")}]]
            **Tomorrow**: [[{(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}]]

            ---
            """)

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
