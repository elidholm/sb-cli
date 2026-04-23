"""
Integration tests for bible.py module.
Test component interactions with real file system operations.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from bible import app, chapter
from config import Config


class TestChapterCommandIntegration(unittest.TestCase):
    """Integration tests for the chapter command with real vault structure."""

    def setUp(self):
        """Set up temporary vault directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.vault_path = self.temp_path / "test_vault"
        self.vault_path.mkdir()
        (self.vault_path / ".obsidian").mkdir()

        # Create required directory structure
        (self.vault_path / "1_Projects" / "Bible-Study").mkdir(parents=True)
        daily_dir = self.vault_path / "2_Areas" / "Journal" / "Daily"
        daily_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    @patch("bible.load_config")
    def test_chapter_creates_file(self, mock_load_config):
        """Test that chapter command creates a note file."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("bible.print"):
            with patch("bible.daily_exists", return_value=True):
                chapter(
                    ctx,
                    book="Genesis",
                    chapter=1,
                    date_read="2024-01-15",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        expected_path = self.vault_path / "1_Projects" / "Bible-Study" / "Genesis" / "genesis_01.md"
        self.assertTrue(expected_path.exists())

    @patch("bible.load_config")
    def test_chapter_content(self, mock_load_config):
        """Test that the created chapter note has the correct content."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("bible.print"):
            with patch("bible.daily_exists", return_value=True):
                chapter(
                    ctx,
                    book="Genesis",
                    chapter=1,
                    date_read="2024-01-15",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        note_path = self.vault_path / "1_Projects" / "Bible-Study" / "Genesis" / "genesis_01.md"
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("# Genesis | Chapter 1", content)
        self.assertIn("**Date Read**: 2024-01-15", content)
        self.assertIn("#bible", content)
        self.assertIn("#genesis", content)
        self.assertIn("[[the_bible]]", content)
        self.assertIn("[[old_testament]]", content)
        self.assertIn("[[pentateuch]]", content)

    @patch("bible.load_config")
    def test_chapter_with_tags(self, mock_load_config):
        """Test chapter creation with custom tags."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("bible.print"):
            with patch("bible.daily_exists", return_value=True):
                chapter(
                    ctx,
                    book="Psalms",
                    chapter=23,
                    date_read="2024-01-15",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags="devotional, favorite",
                )

        note_path = self.vault_path / "1_Projects" / "Bible-Study" / "Psalms" / "psalms_23.md"
        self.assertTrue(note_path.exists())
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("#devotional #favorite", content)

    @patch("bible.load_config")
    def test_chapter_creates_book_directory(self, mock_load_config):
        """Test that chapter command creates the book directory if needed."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        book_dir = self.vault_path / "1_Projects" / "Bible-Study" / "Revelation"
        self.assertFalse(book_dir.exists())

        ctx = MagicMock()
        with patch("bible.print"):
            with patch("bible.daily_exists", return_value=True):
                chapter(
                    ctx,
                    book="Revelation",
                    chapter=22,
                    date_read="2024-01-15",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        self.assertTrue(book_dir.exists())
        self.assertTrue((book_dir / "revelation_22.md").exists())

    @patch("bible.load_config")
    def test_chapter_already_exists_exits_gracefully(self, mock_load_config):
        """Test that creating a duplicate chapter exits with code 0."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create the note first
        book_dir = self.vault_path / "1_Projects" / "Bible-Study" / "Genesis"
        book_dir.mkdir(parents=True, exist_ok=True)
        existing_note = book_dir / "genesis_01.md"
        existing_note.write_text("# Existing note")

        ctx = MagicMock()
        with patch("bible.print"):
            with self.assertRaises(typer.Exit) as cm:
                chapter(
                    ctx,
                    book="Genesis",
                    chapter=1,
                    date_read="2024-01-15",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        self.assertEqual(cm.exception.exit_code, 0)

    @patch("bible.load_config")
    def test_chapter_new_testament_links(self, mock_load_config):
        """Test that New Testament chapter notes have NT-specific links."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("bible.print"):
            with patch("bible.daily_exists", return_value=True):
                chapter(
                    ctx,
                    book="Romans",
                    chapter=8,
                    date_read="2024-01-15",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        note_path = self.vault_path / "1_Projects" / "Bible-Study" / "Romans" / "romans_08.md"
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("[[new_testament]]", content)
        self.assertIn("[[pauline_letters]]", content)
        self.assertIn("[[letters]]", content)

    @patch("bible.load_config")
    def test_chapter_navigation_links(self, mock_load_config):
        """Test that navigation links (previous/next) are correct."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("bible.print"):
            with patch("bible.daily_exists", return_value=True):
                chapter(
                    ctx,
                    book="Genesis",
                    chapter=2,
                    date_read="2024-01-15",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        note_path = self.vault_path / "1_Projects" / "Bible-Study" / "Genesis" / "genesis_02.md"
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("**Previous**: [[genesis_1]]", content)
        self.assertIn("**Next**: [[genesis_3]]", content)

    @patch("bible.load_config")
    def test_chapter_writes_link_to_daily_note(self, mock_load_config):
        """Test that chapter note link is written to daily note."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        date_read = "2024-01-15"
        daily_note = self.vault_path / "2_Areas" / "Journal" / "Daily" / f"{date_read}.md"
        daily_note.write_text("# Daily Note\n\n")

        ctx = MagicMock()
        with patch("bible.print"):
            with patch("bible.daily_exists", return_value=True):
                chapter(
                    ctx,
                    book="Genesis",
                    chapter=3,
                    date_read=date_read,
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        daily_content = daily_note.read_text(encoding="utf-8")
        self.assertIn("[[genesis_03.md]]", daily_content)

    @patch("bible.load_config")
    def test_chapter_creates_daily_if_missing(self, mock_load_config):
        """Test that chapter command creates daily note if it doesn't exist."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("bible.print"):
            with patch("bible.daily_exists", return_value=False):
                chapter(
                    ctx,
                    book="Genesis",
                    chapter=4,
                    date_read="2024-01-15",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        ctx.invoke.assert_called()


class TestChapterCLIIntegration(unittest.TestCase):
    """Integration tests for the bible chapter CLI command."""

    def setUp(self):
        """Set up CLI runner and temporary vault."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.vault_path = self.temp_path / "test_vault"
        self.vault_path.mkdir()
        (self.vault_path / ".obsidian").mkdir()
        (self.vault_path / "1_Projects" / "Bible-Study").mkdir(parents=True)
        (self.vault_path / "2_Areas" / "Journal" / "Daily").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    @patch("bible.load_config")
    def test_cli_chapter_command(self, mock_load_config):
        """Test chapter command via CLI runner."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("bible.daily_exists", return_value=True):
            result = self.runner.invoke(
                app,
                ["Genesis", "1", "--path", str(self.vault_path), "--date", "2024-01-15"],
            )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue((self.vault_path / "1_Projects" / "Bible-Study" / "Genesis" / "genesis_01.md").exists())

    @patch("bible.load_config")
    def test_cli_chapter_invalid_book(self, mock_load_config):
        """Test CLI chapter command with invalid book."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        result = self.runner.invoke(
            app,
            ["NotABook", "1", "--path", str(self.vault_path)],
        )

        self.assertEqual(result.exit_code, 1)

    @patch("bible.load_config")
    def test_cli_chapter_invalid_chapter(self, mock_load_config):
        """Test CLI chapter command with invalid chapter number."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        result = self.runner.invoke(
            app,
            ["Genesis", "999", "--path", str(self.vault_path)],
        )

        self.assertEqual(result.exit_code, 1)
