"""
Integration tests for journal.py module.
Test component interactions with real file system operations.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import typer
from typer.testing import CliRunner

from config import Config
from journal import app, daily, monthly, weekly


class TestDailyCommandIntegration(unittest.TestCase):
    """Integration tests for the daily command with real vault structure."""

    def setUp(self):
        """Set up temporary vault directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.vault_path = self.temp_path / "test_vault"
        self.vault_path.mkdir()
        (self.vault_path / ".obsidian").mkdir()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    @patch("journal.load_config")
    def test_daily_creates_note_file(self, mock_load_config):
        """Test that daily command creates a note file."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            daily(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        today = datetime.now().strftime("%Y-%m-%d")
        expected_path = self.vault_path / "2_Areas" / "Journal" / "Daily" / f"{today}.md"
        self.assertTrue(expected_path.exists())

    @patch("journal.load_config")
    def test_daily_note_content(self, mock_load_config):
        """Test that the daily note has the correct content structure."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            daily(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        today = datetime.now().strftime("%Y-%m-%d")
        note_path = self.vault_path / "2_Areas" / "Journal" / "Daily" / f"{today}.md"
        content = note_path.read_text(encoding="utf-8")

        self.assertIn(f"# {today}", content)
        self.assertIn("## Daily Goals", content)
        self.assertIn("## Today's Focus", content)
        self.assertIn("## Reflections", content)
        self.assertIn("#daily-journal", content)
        self.assertIn("#reflection", content)
        self.assertIn("**Yesterday**:", content)
        self.assertIn("**Tomorrow**:", content)

    @patch("journal.load_config")
    def test_daily_with_tags(self, mock_load_config):
        """Test that daily note includes custom tags."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            daily(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags="work, focus")

        today = datetime.now().strftime("%Y-%m-%d")
        note_path = self.vault_path / "2_Areas" / "Journal" / "Daily" / f"{today}.md"
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("#work #focus", content)

    @patch("journal.load_config")
    def test_daily_creates_directory_structure(self, mock_load_config):
        """Test that daily command creates the directory structure."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        daily_dir = self.vault_path / "2_Areas" / "Journal" / "Daily"
        self.assertFalse(daily_dir.exists())

        with patch("journal.print"):
            daily(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        self.assertTrue(daily_dir.exists())

    @patch("journal.load_config")
    def test_daily_already_exists_exits_gracefully(self, mock_load_config):
        """Test that creating a duplicate daily note exits with code 0."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create the note first
        daily_dir = self.vault_path / "2_Areas" / "Journal" / "Daily"
        daily_dir.mkdir(parents=True)
        today = datetime.now().strftime("%Y-%m-%d")
        existing_note = daily_dir / f"{today}.md"
        existing_note.write_text("# Existing daily note")

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit) as cm:
                daily(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        self.assertEqual(cm.exception.exit_code, 0)
        mock_print.assert_called()


class TestWeeklyCommandIntegration(unittest.TestCase):
    """Integration tests for the weekly command with real vault structure."""

    def setUp(self):
        """Set up temporary vault directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.vault_path = self.temp_path / "test_vault"
        self.vault_path.mkdir()
        (self.vault_path / ".obsidian").mkdir()
        (self.vault_path / "0_Inbox").mkdir()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    @patch("journal.load_config")
    def test_weekly_creates_note_file(self, mock_load_config):
        """Test that weekly command creates a note file."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            weekly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        week_num = int(datetime.now().strftime("%W")) + 1
        year = datetime.now().strftime("%Y")
        weekly_dir = self.vault_path / "2_Areas" / "Journal" / "Weekly-Review"
        expected_path = weekly_dir / f"{week_num}-{year}.md"
        self.assertTrue(expected_path.exists())

    @patch("journal.load_config")
    def test_weekly_content_structure(self, mock_load_config):
        """Test that the weekly review has the correct content structure."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            weekly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        week_num = int(datetime.now().strftime("%W")) + 1
        year = datetime.now().strftime("%Y")
        note_path = self.vault_path / "2_Areas" / "Journal" / "Weekly-Review" / f"{week_num}-{year}.md"
        content = note_path.read_text(encoding="utf-8")

        self.assertIn("## Inbox Processing", content)
        self.assertIn("## Projects Review", content)
        self.assertIn("## Next Week Planning", content)
        self.assertIn("#weekly-review", content)
        self.assertIn("#reflection", content)

    @patch("journal.load_config")
    def test_weekly_inbox_items_included(self, mock_load_config):
        """Test that inbox items are listed in the weekly review."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create some inbox items
        inbox_path = self.vault_path / "0_Inbox"
        (inbox_path / "note_1.md").write_text("# Note 1")
        (inbox_path / "note_2.md").write_text("# Note 2")

        with patch("journal.print"):
            weekly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        from datetime import datetime

        week_num = int(datetime.now().strftime("%W")) + 1
        year = datetime.now().strftime("%Y")
        note_path = self.vault_path / "2_Areas" / "Journal" / "Weekly-Review" / f"{week_num}-{year}.md"
        content = note_path.read_text(encoding="utf-8")

        self.assertIn("[[note_1]]", content)
        self.assertIn("[[note_2]]", content)

    @patch("journal.load_config")
    def test_weekly_empty_inbox(self, mock_load_config):
        """Test weekly review with empty inbox shows no items message."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            weekly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        from datetime import datetime

        week_num = int(datetime.now().strftime("%W")) + 1
        year = datetime.now().strftime("%Y")
        note_path = self.vault_path / "2_Areas" / "Journal" / "Weekly-Review" / f"{week_num}-{year}.md"
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("No items in inbox", content)

    @patch("journal.load_config")
    def test_weekly_with_tags(self, mock_load_config):
        """Test that weekly review includes custom tags."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            weekly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags="sprint, q1")

        from datetime import datetime

        week_num = int(datetime.now().strftime("%W")) + 1
        year = datetime.now().strftime("%Y")
        note_path = self.vault_path / "2_Areas" / "Journal" / "Weekly-Review" / f"{week_num}-{year}.md"
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("#sprint #q1", content)

    @patch("journal.load_config")
    def test_weekly_already_exists_exits_gracefully(self, mock_load_config):
        """Test that creating a duplicate weekly review exits with code 0."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create the weekly note first
        weekly_dir = self.vault_path / "2_Areas" / "Journal" / "Weekly-Review"
        weekly_dir.mkdir(parents=True)
        week_num = int(datetime.now().strftime("%W")) + 1
        year = datetime.now().strftime("%Y")
        existing_note = weekly_dir / f"{week_num}-{year}.md"
        existing_note.write_text("# Existing weekly note")

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit) as cm:
                weekly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        self.assertEqual(cm.exception.exit_code, 0)
        mock_print.assert_called()


class TestMonthlyCommandIntegration(unittest.TestCase):
    """Integration tests for the monthly command with real vault structure."""

    def setUp(self):
        """Set up temporary vault directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.vault_path = self.temp_path / "test_vault"
        self.vault_path.mkdir()
        (self.vault_path / ".obsidian").mkdir()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    @patch("journal.load_config")
    def test_monthly_creates_note_file(self, mock_load_config):
        """Test that monthly command creates a note file."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            monthly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        this_month = datetime.now().strftime("%b-%Y")
        expected_path = self.vault_path / "2_Areas" / "Journal" / "Monthly-Reflection" / f"{this_month}.md"
        self.assertTrue(expected_path.exists())

    @patch("journal.load_config")
    def test_monthly_content_structure(self, mock_load_config):
        """Test that the monthly reflection has the correct content structure."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            monthly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        this_month = datetime.now().strftime("%b-%Y")
        note_path = self.vault_path / "2_Areas" / "Journal" / "Monthly-Reflection" / f"{this_month}.md"
        content = note_path.read_text(encoding="utf-8")

        self.assertIn("## Projects Review", content)
        self.assertIn("## Areas Deep Dive", content)
        self.assertIn("## Celebrations & Gratitude", content)
        self.assertIn("## Next Month Planning", content)
        self.assertIn("#monthly-review", content)
        self.assertIn("#reflection", content)
        self.assertIn("**Previous Month**:", content)
        self.assertIn("**Next Month**:", content)

    @patch("journal.load_config")
    def test_monthly_with_tags(self, mock_load_config):
        """Test that monthly reflection includes custom tags."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("journal.print"):
            monthly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags="q1, milestone")

        from datetime import datetime

        this_month = datetime.now().strftime("%b-%Y")
        note_path = self.vault_path / "2_Areas" / "Journal" / "Monthly-Reflection" / f"{this_month}.md"
        content = note_path.read_text(encoding="utf-8")
        self.assertIn("#q1 #milestone", content)

    @patch("journal.load_config")
    def test_monthly_already_exists_exits_gracefully(self, mock_load_config):
        """Test that creating a duplicate monthly note exits with code 0."""
        from datetime import datetime

        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create the monthly note first
        monthly_dir = self.vault_path / "2_Areas" / "Journal" / "Monthly-Reflection"
        monthly_dir.mkdir(parents=True)
        this_month = datetime.now().strftime("%b-%Y")
        existing_note = monthly_dir / f"{this_month}.md"
        existing_note.write_text("# Existing monthly reflection")

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit) as cm:
                monthly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        self.assertEqual(cm.exception.exit_code, 0)
        mock_print.assert_called()

    @patch("journal.load_config")
    def test_monthly_creates_directory_structure(self, mock_load_config):
        """Test that monthly command creates the directory structure."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        monthly_dir = self.vault_path / "2_Areas" / "Journal" / "Monthly-Reflection"
        self.assertFalse(monthly_dir.exists())

        with patch("journal.print"):
            monthly(vault_path=self.vault_path, config_file="~/.sb_config.yml", tags=None)

        self.assertTrue(monthly_dir.exists())


class TestJournalCLIIntegration(unittest.TestCase):
    """Integration tests for journal CLI commands."""

    def setUp(self):
        """Set up CLI runner and temporary vault."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.vault_path = self.temp_path / "test_vault"
        self.vault_path.mkdir()
        (self.vault_path / ".obsidian").mkdir()
        (self.vault_path / "0_Inbox").mkdir()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    @patch("journal.load_config")
    def test_cli_daily_command(self, mock_load_config):
        """Test daily command via CLI runner."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        result = self.runner.invoke(app, ["daily", "--path", str(self.vault_path)])

        self.assertEqual(result.exit_code, 0)

        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        self.assertTrue((self.vault_path / "2_Areas" / "Journal" / "Daily" / f"{today}.md").exists())

    @patch("journal.load_config")
    def test_cli_weekly_command(self, mock_load_config):
        """Test weekly command via CLI runner."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        result = self.runner.invoke(app, ["weekly", "--path", str(self.vault_path)])

        self.assertEqual(result.exit_code, 0)

    @patch("journal.load_config")
    def test_cli_monthly_command(self, mock_load_config):
        """Test monthly command via CLI runner."""
        mock_config = Config(vault_path=self.vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        result = self.runner.invoke(app, ["monthly", "--path", str(self.vault_path)])

        self.assertEqual(result.exit_code, 0)
