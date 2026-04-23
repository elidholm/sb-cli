"""
Unit tests for bible.py module.
Mock all external dependencies to test functions in isolation.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import typer
from parameterized import parameterized

from bible import (
    _format_book_name,
    _get_adjacent_chapters,
    _get_links,
    _is_general_letters,
    _is_gospel,
    _is_history,
    _is_letters,
    _is_major_prophets,
    _is_minor_prophets,
    _is_new_testament,
    _is_old_testament,
    _is_pastoral_letters,
    _is_pauline_letters,
    _is_pentateuch,
    _is_poetry,
    _is_prison_letters,
    _is_prophetic,
    _is_synoptic_gospels,
    _is_valid_book,
    _is_valid_chapter,
    app,
    chapter,
)
from config import InvalidVaultError


class TestIsValidBook(unittest.TestCase):
    """Unit tests for _is_valid_book function."""

    @parameterized.expand(
        [
            ("Genesis",),
            ("genesis",),
            ("GENESIS",),
            ("Revelation",),
            ("John",),
            ("Psalms",),
            ("1 Samuel",),
            ("2 Kings",),
        ]
    )
    def test_valid_books(self, book):
        """Test that valid book names return True."""
        self.assertTrue(_is_valid_book(book))

    @parameterized.expand(
        [
            ("Genesi",),
            ("NotABook",),
            ("",),
            ("Hezekiah",),
            ("Gospel of Thomas",),
        ]
    )
    def test_invalid_books(self, book):
        """Test that invalid book names return False."""
        self.assertFalse(_is_valid_book(book))


class TestIsValidChapter(unittest.TestCase):
    """Unit tests for _is_valid_chapter function."""

    def test_first_chapter_valid(self):
        """Test chapter 1 is valid for any book."""
        self.assertTrue(_is_valid_chapter("Genesis", 1))

    def test_last_chapter_valid(self):
        """Test the last chapter is valid."""
        self.assertTrue(_is_valid_chapter("Genesis", 50))  # Genesis has 50 chapters

    def test_chapter_beyond_max_invalid(self):
        """Test chapter beyond the maximum is invalid."""
        self.assertFalse(_is_valid_chapter("Genesis", 51))

    def test_chapter_zero_invalid(self):
        """Test chapter 0 is invalid."""
        self.assertFalse(_is_valid_chapter("Genesis", 0))

    def test_negative_chapter_invalid(self):
        """Test negative chapter is invalid."""
        self.assertFalse(_is_valid_chapter("Genesis", -1))

    def test_unknown_book_invalid(self):
        """Test chapter for unknown book is invalid."""
        self.assertFalse(_is_valid_chapter("FakeBook", 1))

    def test_revelation_last_chapter(self):
        """Test Revelation's 22nd chapter is valid."""
        self.assertTrue(_is_valid_chapter("Revelation", 22))

    def test_revelation_beyond_last_chapter(self):
        """Test chapter 23 for Revelation is invalid."""
        self.assertFalse(_is_valid_chapter("Revelation", 23))

    def test_valid_chapter_exact_case(self):
        """Test chapter validation uses exact case matching for book names."""
        self.assertTrue(_is_valid_chapter("Genesis", 1))
        self.assertFalse(_is_valid_chapter("genesis", 1))  # Case-sensitive dict lookup

    def test_obadiah_single_chapter(self):
        """Test Obadiah which has only 1 chapter."""
        self.assertTrue(_is_valid_chapter("Obadiah", 1))
        self.assertFalse(_is_valid_chapter("Obadiah", 2))


class TestIsOldTestament(unittest.TestCase):
    """Unit tests for _is_old_testament function."""

    @parameterized.expand(
        [
            ("Genesis",),
            ("Psalms",),
            ("Malachi",),
            ("Deuteronomy",),
        ]
    )
    def test_old_testament_books(self, book):
        """Test that Old Testament books return True."""
        self.assertTrue(_is_old_testament(book))

    @parameterized.expand(
        [
            ("Matthew",),
            ("John",),
            ("Revelation",),
            ("Romans",),
        ]
    )
    def test_new_testament_books_are_not_old(self, book):
        """Test that New Testament books return False."""
        self.assertFalse(_is_old_testament(book))


class TestIsNewTestament(unittest.TestCase):
    """Unit tests for _is_new_testament function."""

    @parameterized.expand(
        [
            ("Matthew",),
            ("John",),
            ("Romans",),
            ("Revelation",),
        ]
    )
    def test_new_testament_books(self, book):
        """Test that New Testament books return True."""
        self.assertTrue(_is_new_testament(book))

    @parameterized.expand(
        [
            ("Genesis",),
            ("Psalms",),
            ("Malachi",),
        ]
    )
    def test_old_testament_books_are_not_new(self, book):
        """Test that Old Testament books return False."""
        self.assertFalse(_is_new_testament(book))


class TestIsPentateuch(unittest.TestCase):
    """Unit tests for _is_pentateuch function."""

    @parameterized.expand(
        [
            ("Genesis",),
            ("Exodus",),
            ("Leviticus",),
            ("Numbers",),
            ("Deuteronomy",),
        ]
    )
    def test_pentateuch_books(self, book):
        """Test that Pentateuch books return True."""
        self.assertTrue(_is_pentateuch(book))

    def test_non_pentateuch_book(self):
        """Test that non-Pentateuch books return False."""
        self.assertFalse(_is_pentateuch("Joshua"))
        self.assertFalse(_is_pentateuch("Matthew"))


class TestIsHistory(unittest.TestCase):
    """Unit tests for _is_history function."""

    @parameterized.expand(
        [
            ("Joshua",),
            ("Judges",),
            ("Ruth",),
            ("1 Samuel",),
            ("2 Kings",),
            ("Esther",),
            ("Matthew",),  # Gospels are also historical
            ("Mark",),
            ("Luke",),
            ("Acts",),
        ]
    )
    def test_history_books(self, book):
        """Test that historical books (including gospels and Acts) return True."""
        self.assertTrue(_is_history(book))

    def test_non_history_book(self):
        """Test that non-historical books return False."""
        self.assertFalse(_is_history("Genesis"))
        self.assertFalse(_is_history("Psalms"))


class TestIsPoetry(unittest.TestCase):
    """Unit tests for _is_poetry function."""

    @parameterized.expand(
        [
            ("Job",),
            ("Psalms",),
            ("Proverbs",),
            ("Ecclesiastes",),
            ("Song of Solomon",),
        ]
    )
    def test_poetry_books(self, book):
        """Test that poetic books return True."""
        self.assertTrue(_is_poetry(book))

    def test_non_poetry_book(self):
        """Test that non-poetic books return False."""
        self.assertFalse(_is_poetry("Genesis"))
        self.assertFalse(_is_poetry("Matthew"))


class TestIsMajorProphets(unittest.TestCase):
    """Unit tests for _is_major_prophets function."""

    @parameterized.expand(
        [
            ("Isaiah",),
            ("Jeremiah",),
            ("Lamentations",),
            ("Ezekiel",),
            ("Daniel",),
        ]
    )
    def test_major_prophets(self, book):
        """Test that major prophets return True."""
        self.assertTrue(_is_major_prophets(book))

    def test_non_major_prophet(self):
        """Test that non-major prophet books return False."""
        self.assertFalse(_is_major_prophets("Hosea"))
        self.assertFalse(_is_major_prophets("Matthew"))


class TestIsMinorProphets(unittest.TestCase):
    """Unit tests for _is_minor_prophets function."""

    @parameterized.expand(
        [
            ("Hosea",),
            ("Joel",),
            ("Amos",),
            ("Malachi",),
            ("Zechariah",),
        ]
    )
    def test_minor_prophets(self, book):
        """Test that minor prophets return True."""
        self.assertTrue(_is_minor_prophets(book))

    def test_non_minor_prophet(self):
        """Test that non-minor prophet books return False."""
        self.assertFalse(_is_minor_prophets("Isaiah"))
        self.assertFalse(_is_minor_prophets("Matthew"))


class TestIsProphetic(unittest.TestCase):
    """Unit tests for _is_prophetic function."""

    def test_major_prophets_are_prophetic(self):
        """Test that major prophets are prophetic."""
        self.assertTrue(_is_prophetic("Isaiah"))
        self.assertTrue(_is_prophetic("Ezekiel"))

    def test_minor_prophets_are_prophetic(self):
        """Test that minor prophets are prophetic."""
        self.assertTrue(_is_prophetic("Hosea"))
        self.assertTrue(_is_prophetic("Malachi"))

    def test_revelation_is_prophetic(self):
        """Test that Revelation is prophetic."""
        self.assertTrue(_is_prophetic("Revelation"))

    def test_non_prophetic_book(self):
        """Test that non-prophetic books return False."""
        self.assertFalse(_is_prophetic("Genesis"))
        self.assertFalse(_is_prophetic("Matthew"))


class TestIsGospel(unittest.TestCase):
    """Unit tests for _is_gospel and _is_synoptic_gospels functions."""

    @parameterized.expand(
        [
            ("Matthew",),
            ("Mark",),
            ("Luke",),
            ("John",),
        ]
    )
    def test_gospels(self, book):
        """Test that all four gospels return True for _is_gospel."""
        self.assertTrue(_is_gospel(book))

    @parameterized.expand(
        [
            ("Matthew",),
            ("Mark",),
            ("Luke",),
        ]
    )
    def test_synoptic_gospels(self, book):
        """Test that synoptic gospels return True for _is_synoptic_gospels."""
        self.assertTrue(_is_synoptic_gospels(book))

    def test_john_not_synoptic(self):
        """Test that John is not a synoptic gospel."""
        self.assertFalse(_is_synoptic_gospels("John"))

    def test_non_gospel(self):
        """Test that non-gospels return False."""
        self.assertFalse(_is_gospel("Acts"))
        self.assertFalse(_is_gospel("Genesis"))


class TestIsLetters(unittest.TestCase):
    """Unit tests for letter classification functions."""

    def test_pauline_letters(self):
        """Test Pauline letters."""
        self.assertTrue(_is_pauline_letters("Romans"))
        self.assertTrue(_is_pauline_letters("1 Corinthians"))
        self.assertTrue(_is_pauline_letters("Galatians"))
        self.assertFalse(_is_pauline_letters("Hebrews"))
        self.assertFalse(_is_pauline_letters("James"))

    def test_prison_letters(self):
        """Test Prison letters."""
        self.assertTrue(_is_prison_letters("Ephesians"))
        self.assertTrue(_is_prison_letters("Philippians"))
        self.assertTrue(_is_prison_letters("Colossians"))
        self.assertTrue(_is_prison_letters("Philemon"))
        self.assertFalse(_is_prison_letters("Romans"))

    def test_pastoral_letters(self):
        """Test Pastoral letters."""
        self.assertTrue(_is_pastoral_letters("1 Timothy"))
        self.assertTrue(_is_pastoral_letters("2 Timothy"))
        self.assertTrue(_is_pastoral_letters("Titus"))
        self.assertFalse(_is_pastoral_letters("Romans"))

    def test_general_letters(self):
        """Test General letters."""
        self.assertTrue(_is_general_letters("James"))
        self.assertTrue(_is_general_letters("1 Peter"))
        self.assertTrue(_is_general_letters("1 John"))
        self.assertTrue(_is_general_letters("Jude"))
        self.assertFalse(_is_general_letters("Romans"))

    def test_letters_includes_hebrews(self):
        """Test that Hebrews is included in letters."""
        self.assertTrue(_is_letters("Hebrews"))
        self.assertTrue(_is_letters("Romans"))
        self.assertTrue(_is_letters("James"))
        self.assertFalse(_is_letters("Matthew"))


class TestFormatBookName(unittest.TestCase):
    """Unit tests for _format_book_name function."""

    @parameterized.expand(
        [
            ("Genesis", "genesis"),
            ("1 Samuel", "1_samuel"),
            ("Song of Solomon", "song_of_solomon"),
            ("Revelation", "revelation"),
            ("2 Kings", "2_kings"),
        ]
    )
    def test_format_book_name(self, input_book, expected):
        """Test that book names are formatted correctly."""
        self.assertEqual(_format_book_name(input_book), expected)


class TestGetAdjacentChapters(unittest.TestCase):
    """Unit tests for _get_adjacent_chapters function."""

    def test_middle_chapter(self):
        """Test getting adjacent chapters for a middle chapter."""
        prev, nxt = _get_adjacent_chapters("Genesis", 2)
        self.assertEqual(prev, "genesis_1")
        self.assertEqual(nxt, "genesis_3")

    def test_first_chapter_of_book(self):
        """Test getting adjacent chapters for the first chapter of a book."""
        prev, nxt = _get_adjacent_chapters("Genesis", 1)
        # First chapter of the whole Bible, no previous
        self.assertIsNone(prev)
        self.assertEqual(nxt, "genesis_2")

    def test_last_chapter_of_book_not_bible(self):
        """Test getting adjacent chapters for the last chapter of a non-last book."""
        prev, nxt = _get_adjacent_chapters("Genesis", 50)
        self.assertEqual(prev, "genesis_49")
        self.assertEqual(nxt, "exodus_1")  # Next book starts at chapter 1

    def test_last_chapter_of_bible(self):
        """Test getting adjacent chapters for the last chapter of Revelation."""
        prev, nxt = _get_adjacent_chapters("Revelation", 22)
        self.assertEqual(prev, "revelation_21")
        self.assertIsNone(nxt)

    def test_transition_between_books(self):
        """Test transition from last chapter of one book to first of next."""
        prev, nxt = _get_adjacent_chapters("Exodus", 1)
        self.assertEqual(prev, "genesis_50")  # Last chapter of Genesis
        self.assertEqual(nxt, "exodus_2")

    def test_invalid_book(self):
        """Test with invalid book returns (None, None)."""
        prev, nxt = _get_adjacent_chapters("FakeBook", 1)
        self.assertIsNone(prev)
        self.assertIsNone(nxt)

    def test_invalid_chapter(self):
        """Test with out-of-range chapter returns (None, None)."""
        prev, nxt = _get_adjacent_chapters("Genesis", 0)
        self.assertIsNone(prev)
        self.assertIsNone(nxt)

        prev, nxt = _get_adjacent_chapters("Genesis", 51)
        self.assertIsNone(prev)
        self.assertIsNone(nxt)


class TestGetLinks(unittest.TestCase):
    """Unit tests for _get_links function."""

    def test_genesis_chapter_1_links(self):
        """Test links for Genesis chapter 1."""
        prev, nxt, misc = _get_links("Genesis", 1)
        self.assertEqual(prev, "N/A")  # No previous for first chapter of Bible
        self.assertEqual(nxt, "[[genesis_2]]")
        self.assertIn("the_bible", misc)
        self.assertIn("old_testament", misc)
        self.assertIn("pentateuch", misc)

    def test_revelation_chapter_22_links(self):
        """Test links for Revelation chapter 22 (last chapter of Bible)."""
        prev, nxt, misc = _get_links("Revelation", 22)
        self.assertEqual(prev, "[[revelation_21]]")
        self.assertEqual(nxt, "N/A")
        self.assertIn("the_bible", misc)
        self.assertIn("new_testament", misc)
        self.assertIn("prophetic_books", misc)

    def test_matthew_chapter_links(self):
        """Test links for Matthew (gospel, synoptic)."""
        prev, nxt, misc = _get_links("Matthew", 1)
        self.assertIn("gospels", misc)
        self.assertIn("synoptic_gospels", misc)
        self.assertIn("historical_books", misc)
        self.assertIn("new_testament", misc)

    def test_john_chapter_links(self):
        """Test links for John (gospel but not synoptic)."""
        prev, nxt, misc = _get_links("John", 1)
        self.assertIn("gospels", misc)
        self.assertNotIn("synoptic_gospels", misc)

    def test_romans_chapter_links(self):
        """Test links for Romans (Pauline letter)."""
        prev, nxt, misc = _get_links("Romans", 1)
        self.assertIn("pauline_letters", misc)
        self.assertIn("letters", misc)

    def test_psalms_chapter_links(self):
        """Test links for Psalms (poetry)."""
        prev, nxt, misc = _get_links("Psalms", 1)
        self.assertIn("poetic_books", misc)
        self.assertIn("old_testament", misc)


class TestChapterCommand(unittest.TestCase):
    """Unit tests for the chapter command."""

    @patch("bible.load_config")
    def test_chapter_invalid_vault(self, mock_load_config):
        """Test chapter command with invalid vault raises error."""
        mock_load_config.side_effect = InvalidVaultError("Invalid vault path")

        with patch("bible.print") as mock_print:
            with self.assertRaises(typer.Exit):
                ctx = MagicMock()
                chapter(ctx, book="Genesis", chapter=1, vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(":cross_mark: [bold red]Invalid vault path[/bold red]")

    @patch("bible.load_config")
    def test_chapter_invalid_book(self, mock_load_config):
        """Test chapter command with invalid book name."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config

        with patch("bible.print") as mock_print:
            with self.assertRaises(typer.Exit):
                ctx = MagicMock()
                chapter(ctx, book="FakeBook", chapter=1, vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(":cross_mark: [bold red]FakeBook is not a valid book of the Bible.[/bold red]")

    @patch("bible.load_config")
    def test_chapter_invalid_chapter_number(self, mock_load_config):
        """Test chapter command with invalid chapter number."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config

        with patch("bible.print") as mock_print:
            with self.assertRaises(typer.Exit):
                ctx = MagicMock()
                chapter(ctx, book="Genesis", chapter=99, vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(
            ":cross_mark: [bold red]Chapter 99 is not valid for the book of Genesis.[/bold red]"
        )

    @patch("bible.load_config")
    def test_chapter_already_exists(self, mock_load_config):
        """Test chapter command when note already exists."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_bible_path = MagicMock(spec=Path)
        mock_vault_path.__truediv__.return_value = mock_bible_path
        mock_bible_path.__truediv__.return_value = mock_bible_path

        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = True
        mock_bible_path.__truediv__.return_value = mock_note_path

        with patch("bible.print"):
            with self.assertRaises(typer.Exit) as cm:
                ctx = MagicMock()
                chapter(
                    ctx,
                    book="Genesis",
                    chapter=1,
                    date_read=None,
                    vault_path=None,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        self.assertEqual(cm.exception.exit_code, 0)

    @patch("bible.load_config")
    @patch("bible.daily_exists")
    def test_chapter_successful_creation(self, mock_daily_exists, mock_load_config):
        """Test successful chapter note creation."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        # Set up path mocks
        mock_bible_base = MagicMock(spec=Path)
        mock_bible_book_path = MagicMock(spec=Path)

        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.__str__ = lambda s: "genesis_01.md"

        mock_daily_exists.return_value = True  # Daily note already exists

        def vault_truediv(key):
            if "1_Projects" in str(key):
                return mock_bible_base
            return mock_bible_base

        mock_vault_path.__truediv__ = MagicMock(side_effect=lambda k: mock_bible_base)
        mock_bible_base.__truediv__ = MagicMock(side_effect=lambda k: mock_bible_book_path)
        mock_bible_book_path.__truediv__ = MagicMock(side_effect=lambda k: mock_note_path)
        mock_note_path.open = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
        mock_note_path.relative_to = MagicMock(return_value=Path("1_Projects/Bible-Study/Genesis/genesis_01.md"))

        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_note_path.open = MagicMock(return_value=mock_file)

        with patch("bible.print") as mock_print:
            ctx = MagicMock()
            chapter(
                ctx,
                book="Genesis",
                chapter=1,
                date_read="2024-01-01",
                vault_path=None,
                config_file="~/.sb_config.yml",
                tags=None,
            )

        mock_print.assert_called_with(
            ":white_check_mark: [green]Bible chapter summary created:[/green] 1_Projects/Bible-Study/Genesis/genesis_01.md"
        )


class TestAppConfiguration(unittest.TestCase):
    """Tests for bible Typer app configuration."""

    def test_app_has_chapter_command(self):
        """Test that the app has the chapter command registered."""
        self.assertIn("chapter", [cmd.name for cmd in app.registered_commands])
