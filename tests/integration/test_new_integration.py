"""
Integration tests for new.py module.
Test component interactions with real file system operations.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from config import Config
from new import app, empty


class TestEmptyCommandIntegration(unittest.TestCase):
    """Integration tests for empty command with real vault structure."""

    def setUp(self):
        """Set up temporary vault directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.vault_path = self.temp_path / "test_vault"
        self.vault_path.mkdir()
        (self.vault_path / ".obsidian").mkdir()
        (self.vault_path / "0_Inbox").mkdir()

        # Create the daily note directory to avoid journal.daily being invoked
        daily_dir = self.vault_path / "2_Areas" / "Journal" / "Daily"
        daily_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    @patch("new.load_config")
    def test_empty_creates_note_in_inbox(self, mock_load_config):
        """Test that empty command creates a note in the inbox folder."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("new.print"):
            with patch("new.daily_exists", return_value=True):
                empty(ctx, title="My Test Note", vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        expected_file = self.vault_path / "0_Inbox" / "my_test_note.md"
        self.assertTrue(expected_file.exists())

    @patch("new.load_config")
    def test_empty_note_content(self, mock_load_config):
        """Test that the created note has the correct content."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("new.print"):
            with patch("new.daily_exists", return_value=True):
                empty(
                    ctx,
                    title="Content Test",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags="python, test",
                )

        note_path = self.vault_path / "0_Inbox" / "content_test.md"
        self.assertTrue(note_path.exists())

        content = note_path.read_text(encoding="utf-8")
        self.assertIn("# Content Test", content)
        self.assertIn("**Tags**: #python #test", content)
        self.assertIn("**Created**:", content)

    @patch("new.load_config")
    def test_empty_handles_duplicate_filenames(self, mock_load_config):
        """Test that duplicate filenames get a counter suffix."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create the initial file
        existing_note = self.vault_path / "0_Inbox" / "duplicate_note.md"
        existing_note.write_text("# Existing note")

        ctx = MagicMock()
        with patch("new.print"):
            with patch("new.daily_exists", return_value=True):
                empty(
                    ctx,
                    title="Duplicate Note",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        expected_file = self.vault_path / "0_Inbox" / "duplicate_note_1.md"
        self.assertTrue(expected_file.exists())

    @patch("new.load_config")
    def test_empty_creates_inbox_if_missing(self, mock_load_config):
        """Test that empty command creates inbox folder if it doesn't exist."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="9_NewInbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("new.print"):
            with patch("new.daily_exists", return_value=True):
                empty(
                    ctx,
                    title="New Inbox Note",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        inbox_path = self.vault_path / "9_NewInbox"
        self.assertTrue(inbox_path.exists())
        self.assertTrue((inbox_path / "new_inbox_note.md").exists())

    @patch("new.load_config")
    def test_empty_creates_daily_note_if_missing(self, mock_load_config):
        """Test that empty command creates a daily note if it doesn't exist."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()

        with patch("new.print"):
            with patch("new.daily_exists", return_value=False):
                with patch("new.journal.daily"):
                    empty(
                        ctx,
                        title="Note With Daily",
                        vault_path=self.vault_path,
                        config_file="~/.sb_config.yml",
                        tags=None,
                    )

                ctx.invoke.assert_called()

    @patch("new.load_config")
    def test_empty_note_written_to_daily(self, mock_load_config):
        """Test that empty note link is written to the daily note."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        daily_note = self.vault_path / "2_Areas" / "Journal" / "Daily" / f"{today}.md"
        daily_note.write_text("# Today's Journal\n\n")

        ctx = MagicMock()
        with patch("new.print"):
            with patch("new.daily_exists", return_value=True):
                empty(
                    ctx,
                    title="Linked Note",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        daily_content = daily_note.read_text(encoding="utf-8")
        self.assertIn("[[linked_note.md]]", daily_content)

    @patch("new.load_config")
    def test_empty_with_special_characters_in_title(self, mock_load_config):
        """Test empty command handles special characters in title."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("new.print"):
            with patch("new.daily_exists", return_value=True):
                empty(
                    ctx,
                    title="Meeting @2024 #Goals!",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        note_path = self.vault_path / "0_Inbox" / "meeting_2024_goals.md"
        self.assertTrue(note_path.exists())
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("# Meeting @2024 #Goals!", content)

    @patch("new.load_config")
    def test_empty_reports_relative_path(self, mock_load_config):
        """Test that empty command prints the relative path to the created note."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        ctx = MagicMock()
        with patch("new.print") as mock_print:
            with patch("new.daily_exists", return_value=True):
                empty(
                    ctx,
                    title="Path Test Note",
                    vault_path=self.vault_path,
                    config_file="~/.sb_config.yml",
                    tags=None,
                )

        mock_print.assert_called_with(":white_check_mark: [green]Note created:[/green] 0_Inbox/path_test_note.md")


class TestNewCLIIntegration(unittest.TestCase):
    """Integration tests for new.py CLI interface."""

    def setUp(self):
        """Set up CLI runner and temporary vault."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.vault_path = self.temp_path / "test_vault"
        self.vault_path.mkdir()
        (self.vault_path / ".obsidian").mkdir()
        (self.vault_path / "0_Inbox").mkdir()

        daily_dir = self.vault_path / "2_Areas" / "Journal" / "Daily"
        daily_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    @patch("new.load_config")
    def test_cli_empty_command(self, mock_load_config):
        """Test empty command via CLI runner."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("new.daily_exists", return_value=True):
            result = self.runner.invoke(app, ["empty", "CLI Test Note", "--path", str(self.vault_path)])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue((self.vault_path / "0_Inbox" / "cli_test_note.md").exists())

    @patch("new.load_config")
    def test_cli_empty_command_with_tags(self, mock_load_config):
        """Test empty command with tags via CLI runner."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("new.daily_exists", return_value=True):
            result = self.runner.invoke(
                app,
                ["empty", "Tagged Note", "--path", str(self.vault_path), "--tags", "cli, test"],
            )

        self.assertEqual(result.exit_code, 0)
        note_path = self.vault_path / "0_Inbox" / "tagged_note.md"
        self.assertTrue(note_path.exists())
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("#cli #test", content)
