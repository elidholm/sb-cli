"""
CLI tool to create Bible study notes in an Obsidian vault.
----------------------------------------------------------
"""

from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Optional
from rich import print
import textwrap

import typer
from typing_extensions import Annotated

from config import InvalidVaultError, load_config
from utils import format_hashtags

app = typer.Typer(
    name="bible",
    help="Commands to manage bibly study notes.",
    no_args_is_help=True,
)


KJV_BIBLE_BOOKS = [
    # Old Testament
    ("Genesis", 50),
    ("Exodus", 40),
    ("Leviticus", 27),
    ("Numbers", 36),
    ("Deuteronomy", 34),
    ("Joshua", 24),
    ("Judges", 21),
    ("Ruth", 4),
    ("1 Samuel", 31),
    ("2 Samuel", 24),
    ("1 Kings", 22),
    ("2 Kings", 25),
    ("1 Chronicles", 29),
    ("2 Chronicles", 36),
    ("Ezra", 10),
    ("Nehemiah", 13),
    ("Esther", 10),
    ("Job", 42),
    ("Psalms", 150),
    ("Proverbs", 31),
    ("Ecclesiastes", 12),
    ("Song of Solomon", 8),
    ("Isaiah", 66),
    ("Jeremiah", 52),
    ("Lamentations", 5),
    ("Ezekiel", 48),
    ("Daniel", 12),
    ("Hosea", 14),
    ("Joel", 3),
    ("Amos", 9),
    ("Obadiah", 1),
    ("Jonah", 4),
    ("Micah", 7),
    ("Nahum", 3),
    ("Habakkuk", 3),
    ("Zephaniah", 3),
    ("Haggai", 2),
    ("Zechariah", 14),
    ("Malachi", 4),

    # New Testament
    ("Matthew", 28),
    ("Mark", 16),
    ("Luke", 24),
    ("John", 21),
    ("Acts", 28),
    ("Romans", 16),
    ("1 Corinthians", 16),
    ("2 Corinthians", 13),
    ("Galatians", 6),
    ("Ephesians", 6),
    ("Philippians", 4),
    ("Colossians", 4),
    ("1 Thessalonians", 5),
    ("2 Thessalonians", 3),
    ("1 Timothy", 6),
    ("2 Timothy", 4),
    ("Titus", 3),
    ("Philemon", 1),
    ("Hebrews", 13),
    ("James", 5),
    ("1 Peter", 5),
    ("2 Peter", 3),
    ("1 John", 5),
    ("2 John", 1),
    ("3 John", 1),
    ("Jude", 1),
    ("Revelation", 22),
]


def _format_book_name(book: str) -> str:
    """Format the book name to match the note naming convention.

    Args:
        book (str): The book of the Bible.

    Returns:
        str: Formatted book name.
    """
    return book.replace(" ", "_").lower()


def _get_adjacent_chapters(book: str, chapter: int) -> tuple[Optional[str], Optional[str]]:
    """Get the previous and next chapters for a given book and chapter.

    Args:
        book (str): The book of the Bible.
        chapter (int): The chapter number.

    Returns:
        tuple[Optional[str], Optional[str]]: A tuple containing the previous and next chapter references.
    """
    book_index = None
    current_book_chapters = None

    for i, (b, chapters) in enumerate(KJV_BIBLE_BOOKS):
        if b.lower() == book.lower():
            book_index = i
            current_book_chapters = chapters
            break

    if book_index is None:
        return None, None
    if chapter < 1 or chapter > current_book_chapters:
        return None, None

    previous_chapter = None
    next_chapter = None
    if chapter > 1:
        previous_chapter = f"{_format_book_name(book)}_{chapter - 1}"
    elif book_index > 0:
        prev_book, prev_chapters = KJV_BIBLE_BOOKS[book_index - 1]
        previous_chapter = f"{_format_book_name(prev_book)}_{prev_chapters}"

    if chapter < current_book_chapters:
        next_chapter = f"{_format_book_name(book)}_{chapter + 1}"
    elif book_index < len(KJV_BIBLE_BOOKS) - 1:
        next_book, _ = KJV_BIBLE_BOOKS[book_index + 1]
        next_chapter = f"{_format_book_name(next_book)}_1"

    return previous_chapter, next_chapter


@app.command()
def chapter(
    book: Annotated[str, typer.Argument(help="Book of the Bible (e.g., Genesis).")],
    chapter: Annotated[int, typer.Argument(help="Chapter number.")],
    date_read: Annotated[Optional[str], typer.Option("--date", "-d", help="Date when the chapter was read (YYYY-MM-DD).")] = None,
    vault_path: Annotated[Optional[Path], typer.Option("--path", "-p", help="Path to the Obsidian vault.")] = None,
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Path to the sb config file.")] = "~/.sb_config.yml",
    tags: Annotated[Optional[str], typer.Option("--tags", "-t", help="Comma-separated tags to include in the note.")] = None,
) -> None:
    """Create a new Bible chapter summary."""
    try:
        config = load_config(Path(config_file), vault_path)
    except InvalidVaultError as exc:
        print(f":cross_mark: [bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    bible_path = config.vault_path / "1_Projects/Bible-Study"
    bible_path.mkdir(parents=True, exist_ok=True)

    date_read = date_read or datetime.now().strftime("%Y-%m-%d")
    note_path = bible_path / f"{_format_book_name(book)}_{chapter}.md"

    if note_path.exists():
        print(f":information: [yellow]Chapter summary for {book} chapter {chapter} already exists.[/yellow]")
        raise typer.Exit(code=0)

    previous_chapter, next_chapter = _get_adjacent_chapters(book, chapter)
    prev = f"[[{previous_chapter}]]" if previous_chapter else "N/A"
    nxt = f"[[{next_chapter}]]" if next_chapter else "N/A"

    content = textwrap.dedent(f"""\
            # {book} | Chapter {chapter}

            **Date Read**: {date_read}

            ## Key Verses

            >

            ## Main Themes

            -
            -
            -

            ## Personal Insights

            ---

            **Tags**: #bible #{_format_book_name(book)} #chapter{chapter} {format_hashtags(tags)}
            **Next**: {nxt}
            **Previous**: {prev}""")

    try:
        with note_path.open("w", encoding="utf-8") as f:
            f.write(content)
    except Exception as exc:
        print(f":cross_mark: [bold red]Failed to create chapter summary: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    relative_path = note_path.relative_to(config.vault_path)
    print(f":white_check_mark: [green]Bible chapter summary created:[/green] {relative_path}")


if __name__ == "__main__":
    app()
