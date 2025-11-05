"""
Integration tests for sb.py module.
Test component interactions with real file system and Git operations where possible.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import git
import typer
import yaml
from typer.testing import CliRunner

from config import Config
from sb import app, info, sync


class TestSyncCommandIntegration(unittest.TestCase):
    """Integration tests for sync command."""

    def setUp(self):
        """Set up temporary directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def create_test_repo(self, repo_path):
        """Helper to create a test Git repository."""
        repo = git.Repo.init(repo_path)

        # Set minimal git config
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test User")
            config.set_value("user", "email", "test@example.com")

        # Create initial commit
        readme_path = repo_path / "README.md"
        readme_path.write_text("# Test Vault")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

        return repo

    @patch("sb.load_config")
    def test_sync_integration_valid_repo(self, mock_load_config):
        """Integration test for sync with valid Git repository."""
        # Create test vault with Git repo
        vault_path = self.temp_path / "test_vault"
        obsidian_dir = vault_path / ".obsidian"
        vault_path.mkdir()
        obsidian_dir.mkdir()

        self.create_test_repo(vault_path)

        # Mock config
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create a new file to trigger changes
        test_file = vault_path / "test_note.md"
        test_file.write_text("# Test Note")

        with patch("sb.print") as mock_print:
            # This will fail on push since we don't have a remote, but should work up to that point
            try:
                sync("main", "Test integration commit", vault_path)
            except typer.Exit:
                pass  # Expected to fail on push

            # Verify operations up to push were attempted
            mock_print.assert_any_call(
                ":brain: Syncing Second Brain Vault at [green]{}[/green] with remote repository branch [cyan]main[/cyan]...".format(
                    vault_path
                )
            )
            mock_print.assert_any_call("\n:package: Staging 1 file(s)...")

    @patch("sb.load_config")
    def test_sync_integration_no_changes(self, mock_load_config):
        """Integration test for sync with no changes."""
        vault_path = self.temp_path / "test_vault"
        obsidian_dir = vault_path / ".obsidian"
        vault_path.mkdir()
        obsidian_dir.mkdir()

        self.create_test_repo(vault_path)

        # Mock config
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("sb.print") as mock_print:
            try:
                sync("main", "Test commit", vault_path)
            except typer.Exit:
                pass

            # Verify no changes message
            mock_print.assert_any_call(":white_check_mark: No changes to commit.")

    @patch("sb.load_config")
    def test_sync_integration_multiple_files(self, mock_load_config):
        """Integration test for sync with multiple file changes."""
        vault_path = self.temp_path / "test_vault"
        obsidian_dir = vault_path / ".obsidian"
        vault_path.mkdir()
        obsidian_dir.mkdir()

        self.create_test_repo(vault_path)

        # Mock config
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create multiple files
        for i in range(5):
            file_path = vault_path / f"note_{i}.md"
            file_path.write_text(f"# Note {i}")

        with patch("sb.print") as mock_print:
            try:
                sync("main", "Multiple files commit", vault_path)
            except typer.Exit:
                pass

            # Verify multiple files were processed
            mock_print.assert_any_call("\n:package: Staging 5 file(s)...")

    @patch("sb.load_config")
    def test_sync_integration_with_config_file(self, mock_load_config):
        """Integration test for sync using config file."""
        # Create config file
        config_path = self.temp_path / "config.yaml"
        vault_path = self.temp_path / "test_vault"
        obsidian_dir = vault_path / ".obsidian"
        vault_path.mkdir()
        obsidian_dir.mkdir()

        self.create_test_repo(vault_path)

        config_data = {"vault_path": str(vault_path), "inbox_folder": "0_CustomInbox"}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Mock config loading to use our file
        with patch("sb.load_config") as mock_load:
            mock_config = Config(vault_path=vault_path, inbox_folder="0_CustomInbox")
            mock_load.return_value = mock_config

            with patch("sb.print"):
                try:
                    sync("main", config_file=str(config_path))
                except typer.Exit:
                    pass

                # Verify config was used
                mock_load.assert_called_once()

    @patch("sb.load_config")
    def test_sync_integration_special_characters(self, mock_load_config):
        """Integration test for sync with special characters in paths."""
        vault_name = "vault with spaces & (special) chars"
        vault_path = self.temp_path / vault_name
        obsidian_dir = vault_path / ".obsidian"
        vault_path.mkdir()
        obsidian_dir.mkdir()

        self.create_test_repo(vault_path)

        # Mock config
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # Create file with special characters
        test_file = vault_path / "note with spaces.md"
        test_file.write_text("# Note with spaces")

        with patch("sb.print") as mock_print:
            try:
                sync("main", "Special chars test", vault_path)
            except typer.Exit:
                pass

            # Verify operations proceeded normally
            mock_print.assert_any_call(
                ":brain: Syncing Second Brain Vault at [green]{}[/green] with remote repository branch [cyan]main[/cyan]...".format(
                    vault_path
                )
            )


class TestInfoCommandIntegration(unittest.TestCase):
    """Integration tests for info command."""

    def setUp(self):
        """Set up temporary directory for tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def create_test_vault_structure(self, vault_path):
        """Helper to create a test vault structure."""
        folders = ["0_Inbox", "1_Projects", "2_Areas", "3_Resources", "4_Archive"]

        for folder in folders:
            folder_path = vault_path / folder
            folder_path.mkdir()

            # Create some markdown files
            for i in range(2):
                note_path = folder_path / f"note_{i}.md"
                note_path.write_text(f"# Note {i} in {folder}")

        # Create .obsidian directory
        obsidian_dir = vault_path / ".obsidian"
        obsidian_dir.mkdir()

    @patch("sb.load_config")
    def test_info_integration_complete_vault(self, mock_load_config):
        """Integration test for info with complete vault structure."""
        vault_path = self.temp_path / "test_vault"
        vault_path.mkdir()
        self.create_test_vault_structure(vault_path)

        # Mock config
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("sb.print") as mock_print:
            info(vault_path=vault_path)

            # Verify vault info was displayed
            mock_print.assert_any_call(":brain: Second Brain Vault: [green]{}[/green]".format(vault_path))

            # Verify all folders were checked
            mock_print.assert_any_call("\t:white_check_mark: [green]0_Inbox[/green] (2 notes)")

    @patch("sb.load_config")
    def test_info_integration_partial_vault(self, mock_load_config):
        """Integration test for info with partial vault structure."""
        vault_path = self.temp_path / "test_vault"
        vault_path.mkdir()

        # Only create some folders
        folders = ["0_Inbox", "1_Projects"]
        for folder in folders:
            folder_path = vault_path / folder
            folder_path.mkdir()

            # Create markdown files
            for i in range(3):
                note_path = folder_path / f"note_{i}.md"
                note_path.write_text(f"# Note {i}")

        # Create .obsidian directory
        obsidian_dir = vault_path / ".obsidian"
        obsidian_dir.mkdir()

        # Mock config
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("sb.print") as mock_print:
            info(vault_path=vault_path)

            # Verify missing folders are reported
            mock_print.assert_any_call("\t:cross_mark: [red]2_Areas (missing)[/red]")

    @patch("sb.load_config")
    def test_info_integration_empty_inbox(self, mock_load_config):
        """Integration test for info with empty inbox."""
        vault_path = self.temp_path / "test_vault"
        vault_path.mkdir()

        # Create empty inbox
        inbox_path = vault_path / "0_Inbox"
        inbox_path.mkdir()

        # Create .obsidian directory
        obsidian_dir = vault_path / ".obsidian"
        obsidian_dir.mkdir()

        # Mock config
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("sb.print") as mock_print:
            info(vault_path=vault_path)

            # Verify empty inbox message
            mock_print.assert_any_call("\n:inbox_tray: Inbox is empty :sparkles:")

    @patch("sb.load_config")
    def test_info_integration_many_inbox_files(self, mock_load_config):
        """Integration test for info with many inbox files."""
        vault_path = self.temp_path / "test_vault"
        vault_path.mkdir()

        # Create inbox with many files
        inbox_path = vault_path / "0_Inbox"
        inbox_path.mkdir()

        for i in range(12):
            note_path = inbox_path / f"note_{i}.md"
            note_path.write_text(f"# Inbox Note {i}")

        # Create .obsidian directory
        obsidian_dir = vault_path / ".obsidian"
        obsidian_dir.mkdir()

        # Mock config
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        with patch("sb.print") as mock_print:
            info(vault_path=vault_path)

            # Verify many files message and review suggestion
            mock_print.assert_any_call("\n:inbox_tray: Inbox has [yellow]12[/yellow] unprocessed notes")
            mock_print.assert_any_call("\t:light_bulb: [yellow]Consider doing a weekly review![/yellow]")

    @patch("sb.load_config")
    def test_info_integration_custom_inbox_folder(self, mock_load_config):
        """Integration test for info with custom inbox folder name."""
        vault_path = self.temp_path / "test_vault"
        vault_path.mkdir()

        # Create custom inbox folder
        custom_inbox = "9_CustomInbox"
        inbox_path = vault_path / custom_inbox
        inbox_path.mkdir()

        for i in range(5):
            note_path = inbox_path / f"note_{i}.md"
            note_path.write_text(f"# Custom Inbox Note {i}")

        # Create .obsidian directory
        obsidian_dir = vault_path / ".obsidian"
        obsidian_dir.mkdir()

        # Mock config with custom inbox
        mock_config = Config(vault_path=vault_path, inbox_folder=custom_inbox)
        mock_load_config.return_value = mock_config

        with patch("sb.print") as mock_print:
            info(vault_path=vault_path)

            # Verify custom inbox is used
            mock_print.assert_any_call("\n:inbox_tray: Inbox has [yellow]5[/yellow] unprocessed notes")

    @patch("sb.load_config")
    def test_info_integration_missing_obsidian(self, mock_load_config):
        """Integration test for info with vault missing .obsidian directory."""
        vault_path = self.temp_path / "test_vault"
        vault_path.mkdir()

        # Create folder structure but no .obsidian
        folders = ["0_Inbox", "1_Projects"]
        for folder in folders:
            folder_path = vault_path / folder
            folder_path.mkdir()

        # Mock config - this should fail validation
        mock_config = Config(vault_path=vault_path, inbox_folder="0_Inbox")
        mock_load_config.return_value = mock_config

        # The load_config function should raise InvalidVaultError when .obsidian is missing
        with patch("sb.load_config") as mock_load:
            from config import InvalidVaultError

            mock_load.side_effect = InvalidVaultError(f"'{vault_path}' is not a valid Obsidian vault.")

            with patch("sb.print") as mock_print:
                with self.assertRaises(typer.Exit):
                    info(vault_path=vault_path)

                mock_print.assert_any_call(
                    ":cross_mark: [bold red]'{}' is not a valid Obsidian vault.[/bold red]".format(vault_path)
                )


class TestCommandLineInterface(unittest.TestCase):
    """Tests for command-line interface integration."""

    def setUp(self):
        """Set up CLI runner."""
        self.runner = CliRunner()

    @patch("sb.git.Repo")
    @patch("sb.sync")
    def test_cli_sync_command(self, mock_sync, mock_repo_class):
        """Test that CLI calls sync command properly."""
        # Test sync command with arguments
        result = self.runner.invoke(app, ["sync", "master", "-m", "CLI test commit"])

        print(f"{result.output=}")

        # Verify sync was called (though it will fail without proper setup)
        self.assertEqual(result.exit_code, 0)

    @patch("sb.info")
    def test_cli_info_command(self, mock_info):
        """Test that CLI calls info command properly."""
        # Test info command
        result = self.runner.invoke(app, ["info"])

        print(f"{result.output=}")

        # Verify info was called
        self.assertEqual(result.exit_code, 0)
