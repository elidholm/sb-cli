"""
Unit tests for new.py module.
Mock all external dependencies to test functions in isolation.
"""

import unittest
from unittest.mock import MagicMock, patch

import typer
from parameterized import parameterized

from config import InvalidVaultError
from new import app, empty, format_hashtags, new_callback, sanitize_filename


class TestNewCallback(unittest.TestCase):
    """Unit tests for new_callback function."""

    @patch("new.Confirm.ask")
    def test_new_callback_no_subcommand_creates_empty_note(self, mock_confirm):
        """Test callback creates empty note when no subcommand provided and user confirms."""
        mock_confirm.return_value = True

        mock_ctx = MagicMock()
        mock_ctx.invoked_subcommand = None

        new_callback(mock_ctx)

        mock_confirm.assert_called_once_with("No subcommand provided. Create an empty note?", default=True)
        mock_ctx.invoke.assert_called_once()
        invoked_func = mock_ctx.invoke.call_args[0][0]

        self.assertEqual(invoked_func, empty)

    @patch("new.Confirm.ask")
    @patch("new.print")
    def test_new_callback_no_subcommand_declines_empty_note(self, mock_print, mock_confirm):
        """Test callback exits when no subcommand provided and user declines."""
        mock_confirm.return_value = False
        mock_ctx = MagicMock()
        mock_ctx.invoked_subcommand = None
        mock_ctx.exit = MagicMock()

        new_callback(mock_ctx)

        mock_confirm.assert_called_once_with("No subcommand provided. Create an empty note?", default=True)
        mock_print.assert_called_once_with("Use 'sb new --help' to see available subcommands.")
        mock_ctx.exit.assert_called_once()

    def test_new_callback_with_subcommand(self):
        """Test callback does nothing when subcommand is provided."""
        mock_ctx = MagicMock()
        mock_ctx.invoked_subcommand = "journal"

        new_callback(mock_ctx)

        # Should not attempt to create empty note when subcommand exists
        mock_ctx.invoke.assert_not_called()


class TestEmptyCommand(unittest.TestCase):
    """Unit tests for empty command function."""

    def setUp(self):
        self.mock_ctx = MagicMock()

    @patch("new.load_config")
    def test_empty_command_invalid_vault(self, mock_load_config):
        """Test empty command with invalid vault raises error."""
        mock_load_config.side_effect = InvalidVaultError("Invalid vault path")

        with patch("new.print") as mock_print:
            with self.assertRaises(typer.Exit):
                empty(self.mock_ctx, title="Test", vault_path=None, config_file="~/.sb_config.yml", tags=None)

        mock_print.assert_called_once_with(":cross_mark: [bold red]Invalid vault path[/bold red]")

    @parameterized.expand(
        [
            ("Normal Title", "normal_title"),
            ("Title with/slashes", "title_withslashes"),
            ("Title with\\backslashes", "title_withbackslashes"),
            ("Title with:colons", "title_withcolons"),
            ("Title with*asterisks", "title_withasterisks"),
            ("Title with?question", "title_withquestion"),
            ('Title with"quotes"', "title_withquotes"),
            ("Title with<angles>", "title_withangles"),
            ("Title with|pipe", "title_withpipe"),
        ]
    )
    def test_empty_command_filename_sanitization(self, input_title, expected):
        """Test various filename sanitization scenarios."""
        with self.subTest(title=expected):
            result = sanitize_filename(input_title)
            self.assertEqual(result, expected)

    @parameterized.expand(
        [
            (None, ""),
            ("", ""),
            ("tag1", "#tag1"),
            ("tag1,tag2", "#tag1 #tag2"),
            ("tag1, tag2", "#tag1 #tag2"),
            (" tag1 , tag2 ", "#tag1 #tag2"),
            ("multiple, tags, here", "#multiple #tags #here"),
        ]
    )
    def test_format_hashtags(self, input_tags, expected):
        """Test hashtag formatting function."""
        with self.subTest(tags=input_tags):
            result = format_hashtags(input_tags)
            self.assertEqual(result, expected)


class TestCLIInterface(unittest.TestCase):
    """Test the CLI interface using CliRunner."""

    @patch("new.journal.app")
    def test_cli_journal_subcommand(self, mock_journal_app):
        """Test CLI journal subcommand is available."""
        self.assertIn("journal", [group.name for group in app.registered_groups])

    @patch("new.bible.app")
    def test_cli_bible_subcommand(self, mock_bible_app):
        """Test CLI bible subcommand is available."""
        self.assertIn("bible", [group.name for group in app.registered_groups])
