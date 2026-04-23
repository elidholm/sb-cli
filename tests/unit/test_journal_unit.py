"""
Unit tests for journal.py module.
Mock all external dependencies to test functions in isolation.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import typer

from config import InvalidVaultError
from journal import app, daily, monthly, weekly


class TestDailyCommand(unittest.TestCase):
    """Unit tests for the daily command."""

    @patch("journal.load_config")
    def test_daily_invalid_vault(self, mock_load_config):
        """Test daily command with invalid vault raises error."""
        mock_load_config.side_effect = InvalidVaultError("Invalid vault path")

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit):
                daily(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(":cross_mark: [bold red]Invalid vault path[/bold red]")

    @patch("journal.load_config")
    def test_daily_note_already_exists(self, mock_load_config):
        """Test daily command when note already exists."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_daily_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = True
        mock_daily_dir.__truediv__ = MagicMock(return_value=mock_note_path)
        mock_vault_path.__truediv__ = MagicMock(return_value=mock_daily_dir)
        mock_daily_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        with patch("journal.print"):
            with self.assertRaises(typer.Exit) as cm:
                daily(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        self.assertEqual(cm.exception.exit_code, 0)

    @patch("journal.load_config")
    def test_daily_successful_creation(self, mock_load_config):
        """Test successful daily note creation."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_daily_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.relative_to = MagicMock(return_value=Path("2_Areas/Journal/Daily/2024-01-15.md"))

        mock_vault_path.__truediv__ = MagicMock(return_value=mock_daily_dir)
        mock_daily_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_note_path.open = MagicMock(return_value=mock_file)

        with patch("journal.print") as mock_print:
            daily(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(
            ":white_check_mark: [green]Daily journal created:[/green] 2_Areas/Journal/Daily/2024-01-15.md"
        )

    @patch("journal.load_config")
    def test_daily_write_error(self, mock_load_config):
        """Test daily command when file write fails."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_daily_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.open.side_effect = OSError("Permission denied")

        mock_vault_path.__truediv__ = MagicMock(return_value=mock_daily_dir)
        mock_daily_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit):
                daily(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_any_call(
            ":cross_mark: [bold red]Failed to create daily journal entry: Permission denied[/bold red]"
        )

    @patch("journal.load_config")
    def test_daily_with_tags(self, mock_load_config):
        """Test daily command creates note with tags."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_daily_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.relative_to = MagicMock(return_value=Path("2_Areas/Journal/Daily/2024-01-15.md"))

        mock_vault_path.__truediv__ = MagicMock(return_value=mock_daily_dir)
        mock_daily_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        written_content = []

        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.write = MagicMock(side_effect=lambda s: written_content.append(s))
        mock_note_path.open = MagicMock(return_value=mock_file)

        with patch("journal.print"):
            daily(vault_path=None, config_file="~/.sb_config.yml", tags="test, daily")

        # Verify write was called with content
        mock_file.write.assert_called_once()
        content = mock_file.write.call_args[0][0]
        self.assertIn("#test #daily", content)


class TestWeeklyCommand(unittest.TestCase):
    """Unit tests for the weekly command."""

    @patch("journal.load_config")
    def test_weekly_invalid_vault(self, mock_load_config):
        """Test weekly command with invalid vault raises error."""
        mock_load_config.side_effect = InvalidVaultError("Invalid vault path")

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit):
                weekly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(":cross_mark: [bold red]Invalid vault path[/bold red]")

    @patch("journal.load_config")
    def test_weekly_note_already_exists(self, mock_load_config):
        """Test weekly command when note already exists."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        mock_weekly_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = True

        mock_inbox_path = MagicMock(spec=Path)
        mock_inbox_path.exists.return_value = False

        def vault_truediv(key):
            if "Weekly" in str(key):
                return mock_weekly_dir
            return mock_inbox_path

        mock_vault_path.__truediv__ = MagicMock(side_effect=vault_truediv)
        mock_weekly_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        with patch("journal.print"):
            with self.assertRaises(typer.Exit) as cm:
                weekly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        self.assertEqual(cm.exception.exit_code, 0)

    @patch("journal.load_config")
    def test_weekly_successful_creation(self, mock_load_config):
        """Test successful weekly review creation."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        mock_weekly_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.relative_to = MagicMock(return_value=Path("2_Areas/Journal/Weekly-Review/01-2024.md"))

        mock_inbox_path = MagicMock(spec=Path)
        mock_inbox_path.exists.return_value = False

        def vault_truediv(key):
            if "Weekly" in str(key) or "Journal" in str(key):
                return mock_weekly_dir
            return mock_inbox_path

        mock_vault_path.__truediv__ = MagicMock(side_effect=vault_truediv)
        mock_weekly_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_note_path.open = MagicMock(return_value=mock_file)

        with patch("journal.print") as mock_print:
            weekly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(
            ":white_check_mark: [green]Weekly review created:[/green] 2_Areas/Journal/Weekly-Review/01-2024.md"
        )

    @patch("journal.load_config")
    def test_weekly_with_inbox_items(self, mock_load_config):
        """Test weekly review creation when inbox has items."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        mock_weekly_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.relative_to = MagicMock(return_value=Path("2_Areas/Journal/Weekly-Review/01-2024.md"))

        mock_inbox_path = MagicMock(spec=Path)
        mock_inbox_path.exists.return_value = True
        mock_inbox_path.is_dir.return_value = True
        # Return mock paths with stem attribute for inbox files
        mock_inbox_item1 = MagicMock(spec=Path)
        mock_inbox_item1.stem = "note_1"
        mock_inbox_item2 = MagicMock(spec=Path)
        mock_inbox_item2.stem = "note_2"
        mock_inbox_path.glob.return_value = [mock_inbox_item1, mock_inbox_item2]

        def vault_truediv(key):
            if "Weekly" in str(key) or "Journal" in str(key):
                return mock_weekly_dir
            return mock_inbox_path

        mock_vault_path.__truediv__ = MagicMock(side_effect=vault_truediv)
        mock_weekly_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        written_content = []
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.write = MagicMock(side_effect=lambda s: written_content.append(s))
        mock_note_path.open = MagicMock(return_value=mock_file)

        with patch("journal.print"):
            weekly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        # Verify inbox items appear in content
        mock_file.write.assert_called_once()
        content = mock_file.write.call_args[0][0]
        self.assertIn("note_1", content)
        self.assertIn("note_2", content)

    @patch("journal.load_config")
    def test_weekly_write_error(self, mock_load_config):
        """Test weekly command when file write fails."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        mock_weekly_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.open.side_effect = OSError("Disk full")

        mock_inbox_path = MagicMock(spec=Path)
        mock_inbox_path.exists.return_value = False

        def vault_truediv(key):
            if "Weekly" in str(key) or "Journal" in str(key):
                return mock_weekly_dir
            return mock_inbox_path

        mock_vault_path.__truediv__ = MagicMock(side_effect=vault_truediv)
        mock_weekly_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit):
                weekly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_any_call(":cross_mark: [bold red]Failed to create weekly review: Disk full[/bold red]")


class TestMonthlyCommand(unittest.TestCase):
    """Unit tests for the monthly command."""

    @patch("journal.load_config")
    def test_monthly_invalid_vault(self, mock_load_config):
        """Test monthly command with invalid vault raises error."""
        mock_load_config.side_effect = InvalidVaultError("Invalid vault path")

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit):
                monthly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(":cross_mark: [bold red]Invalid vault path[/bold red]")

    @patch("journal.load_config")
    def test_monthly_note_already_exists(self, mock_load_config):
        """Test monthly command when note already exists."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_monthly_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = True

        mock_vault_path.__truediv__ = MagicMock(return_value=mock_monthly_dir)
        mock_monthly_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        with patch("journal.print"):
            with self.assertRaises(typer.Exit) as cm:
                monthly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        self.assertEqual(cm.exception.exit_code, 0)

    @patch("journal.load_config")
    def test_monthly_successful_creation(self, mock_load_config):
        """Test successful monthly reflection creation."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_monthly_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.relative_to = MagicMock(return_value=Path("2_Areas/Journal/Monthly-Reflection/Jan-2024.md"))

        mock_vault_path.__truediv__ = MagicMock(return_value=mock_monthly_dir)
        mock_monthly_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_note_path.open = MagicMock(return_value=mock_file)

        with patch("journal.print") as mock_print:
            monthly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_with(
            ":white_check_mark: [green]Monthly reflection created:[/green] 2_Areas/Journal/Monthly-Reflection/Jan-2024.md"
        )

    @patch("journal.load_config")
    def test_monthly_with_tags(self, mock_load_config):
        """Test monthly reflection with custom tags."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_monthly_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.relative_to = MagicMock(return_value=Path("2_Areas/Journal/Monthly-Reflection/Jan-2024.md"))

        mock_vault_path.__truediv__ = MagicMock(return_value=mock_monthly_dir)
        mock_monthly_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        written_content = []
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.write = MagicMock(side_effect=lambda s: written_content.append(s))
        mock_note_path.open = MagicMock(return_value=mock_file)

        with patch("journal.print"):
            monthly(vault_path=None, config_file="~/.sb_config.yml", tags="custom, review")

        mock_file.write.assert_called_once()
        content = mock_file.write.call_args[0][0]
        self.assertIn("#custom #review", content)

    @patch("journal.load_config")
    def test_monthly_write_error(self, mock_load_config):
        """Test monthly command when file write fails."""
        mock_config = MagicMock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_load_config.return_value = mock_config

        mock_monthly_dir = MagicMock(spec=Path)
        mock_note_path = MagicMock(spec=Path)
        mock_note_path.exists.return_value = False
        mock_note_path.open.side_effect = OSError("No space left")

        mock_vault_path.__truediv__ = MagicMock(return_value=mock_monthly_dir)
        mock_monthly_dir.__truediv__ = MagicMock(return_value=mock_note_path)

        with patch("journal.print") as mock_print:
            with self.assertRaises(typer.Exit):
                monthly(vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_any_call(
            ":cross_mark: [bold red]Failed to create monthly reflection: No space left[/bold red]"
        )


class TestAppConfiguration(unittest.TestCase):
    """Tests for journal Typer app configuration."""

    def test_app_has_expected_commands(self):
        """Test that the app has all expected commands registered."""
        command_names = [cmd.name for cmd in app.registered_commands]
        self.assertIn("daily", command_names)
        self.assertIn("weekly", command_names)
        self.assertIn("monthly", command_names)
