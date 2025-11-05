"""
Unit tests for sb.py module.
Mock all external dependencies to test functions in isolation.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import typer
from git.exc import GitCommandError, InvalidGitRepositoryError
from parameterized import parameterized

from config import InvalidVaultError
from sb import app, info, sync


class TestSyncCommand(unittest.TestCase):
    """Unit tests for sync command."""

    @patch("sb.load_config")
    @patch("sb.git.Repo")
    def test_sync_successful_flow(self, mock_repo_class, mock_load_config):
        """Test successful sync with changes to commit."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.active_branch.name = "master"

        mock_repo.is_dirty.return_value = True
        mock_diff = Mock()
        mock_diff.a_path = "modified_file.md"
        mock_repo.index.diff.return_value = [mock_diff]
        mock_repo.untracked_files = ["new_file.md"]

        mock_commit = Mock()
        mock_commit.hexsha = "abc1234"
        mock_repo.index.commit.return_value = mock_commit

        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        with patch("sb.print") as mock_print:
            sync("master", "Test commit message", mock_config.vault_path)

            mock_print.assert_any_call(
                ":brain: Syncing Second Brain Vault at [green]/test/vault[/green] with remote repository branch [cyan]master[/cyan]..."
            )
            mock_print.assert_any_call("\n:package: Staging 2 file(s)...")
            mock_print.assert_any_call(":white_check_mark: Committed 2 file(s)")

    @patch("sb.load_config")
    @patch("sb.git.Repo")
    def test_sync_no_changes(self, mock_repo_class, mock_load_config):
        """Test sync when there are no changes to commit."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.active_branch.name = "master"
        mock_repo.is_dirty.return_value = False

        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        with patch("sb.print") as mock_print:
            sync("master", "Test commit", mock_config.vault_path)

            mock_print.assert_any_call(":white_check_mark: No changes to commit.")

    @patch("sb.load_config")
    @patch("sb.git.Repo")
    def test_sync_fetch_failure(self, mock_repo_class, mock_load_config):
        """Test sync when fetch operation fails."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.active_branch.name = "master"
        mock_repo.is_dirty.return_value = False

        mock_origin = Mock()
        mock_origin.fetch.side_effect = Exception("Network error")
        mock_repo.remote.return_value = mock_origin

        with patch("sb.print") as mock_print:
            with self.assertRaises(typer.Exit):
                sync("master", "Test commit", mock_config.vault_path)

            mock_print.assert_any_call(":cross_mark: [bold red]Failed to fetch from remote: Network error[/bold red]")

    @patch("sb.load_config")
    @patch("sb.git.Repo")
    def test_sync_rebase_failure(self, mock_repo_class, mock_load_config):
        """Test sync when rebase operation fails."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.active_branch.name = "master"
        mock_repo.is_dirty.return_value = False

        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        # Mock rebase failure
        mock_repo.git.rebase.side_effect = GitCommandError("rebase", "Conflict detected")

        with patch("sb.print") as mock_print:
            with self.assertRaises(typer.Exit):
                sync("master", "Test commit", mock_config.vault_path)

            mock_print.assert_any_call(
                ":cross_mark: [bold red]Rebase failed: Cmd('rebase') failed due to: 'Conflict detected'\n  cmdline: rebase[/bold red]"
            )

    @patch("sb.load_config")
    @patch("sb.git.Repo")
    def test_sync_push_failure(self, mock_repo_class, mock_load_config):
        """Test sync when push operation fails."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.active_branch.name = "master"
        mock_repo.is_dirty.return_value = False

        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        # Mock push failure
        mock_origin.push.side_effect = GitCommandError("push", "Permission denied")

        with patch("sb.print") as mock_print:
            with self.assertRaises(typer.Exit):
                sync("master", "Test commit", mock_config.vault_path)

            mock_print.assert_any_call(
                ":cross_mark: [bold red]Push failed: Cmd('push') failed due to: 'Permission denied'\n  cmdline: push[/bold red]"
            )

    @patch("sb.load_config")
    def test_sync_invalid_git_repository(self, mock_load_config):
        """Test sync with invalid git repository."""
        mock_config = Mock()
        mock_config.vault_path = Path("/invalid/vault")
        mock_load_config.return_value = mock_config

        with patch("sb.git.Repo") as mock_repo_class:
            mock_repo_class.side_effect = InvalidGitRepositoryError("Not a git repo")

            with patch("sb.print") as mock_print:
                with self.assertRaises(typer.Exit):
                    sync("master", "Test commit", mock_config.vault_path)

                mock_print.assert_any_call(
                    ":cross_mark: [bold red]'/invalid/vault' is not a valid git repository.[/bold red]"
                )

    @patch("sb.load_config")
    def test_sync_invalid_vault_error(self, mock_load_config):
        """Test sync when vault configuration is invalid."""
        mock_load_config.side_effect = InvalidVaultError("Invalid vault path")

        with patch("sb.print") as mock_print:
            with self.assertRaises(typer.Exit):
                sync("master", "Test commit", None)

            mock_print.assert_any_call(":cross_mark: [bold red]Invalid vault path[/bold red]")

    @patch("sb.load_config")
    @patch("sb.git.Repo")
    def test_sync_many_changed_files(self, mock_repo_class, mock_load_config):
        """Test sync with many changed files (more than 10)."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.active_branch.name = "master"
        mock_repo.is_dirty.return_value = True

        # Create 15 changed files
        mock_diff_files = [Mock(a_path=f"file_{i}.md") for i in range(10)]
        mock_repo.index.diff.return_value = mock_diff_files
        mock_repo.untracked_files = [f"new_file_{i}.md" for i in range(5)]

        mock_commit = Mock()
        mock_commit.hexsha = "abc1234"
        mock_repo.index.commit.return_value = mock_commit

        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        with patch("sb.print") as mock_print:
            sync("master", "Test commit", mock_config.vault_path)

            # Verify truncation message
            mock_print.assert_any_call("   ... and 5 more")

    @patch("sb.load_config")
    def test_sync_unexpected_error(self, mock_load_config):
        """Test sync with unexpected errors."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        with patch("sb.git.Repo") as mock_repo_class:
            mock_repo_class.side_effect = Exception("Unexpected disaster")

            with patch("sb.print") as mock_print:
                with self.assertRaises(typer.Exit):
                    sync("master", "Test commit", mock_config.vault_path)

                mock_print.assert_any_call(":cross_mark: [bold red]Unexpected error: Unexpected disaster[/bold red]")

    @patch("sb.load_config")
    @patch("sb.git.Repo")
    def test_sync_only_untracked_files(self, mock_repo_class, mock_load_config):
        """Test sync with only untracked files (no modified files)."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.active_branch.name = "main"
        mock_repo.is_dirty.return_value = True

        # Only untracked files, no modified files
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = ["file1.md", "file2.md"]

        mock_commit = Mock()
        mock_commit.hexsha = "abc1234"
        mock_repo.index.commit.return_value = mock_commit

        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        with patch("sb.print") as mock_print:
            sync("main", "Test commit", mock_config.vault_path)

            # Verify both files were counted
            mock_print.assert_any_call("\n:package: Staging 2 file(s)...")

    @patch("sb.load_config")
    @patch("sb.git.Repo")
    def test_sync_rebase_abort_failure(self, mock_repo_class, mock_load_config):
        """Test sync when rebase abort also fails."""
        mock_config = Mock()
        mock_config.vault_path = Path("/test/vault")
        mock_load_config.return_value = mock_config

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.active_branch.name = "main"
        mock_repo.is_dirty.return_value = False

        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        # Mock rebase failure
        mock_repo.git.rebase.side_effect = GitCommandError("rebase", "Conflict")
        # Mock abort also fails
        mock_repo.git.rebase.side_effect = [
            GitCommandError("rebase", "Conflict"),
            GitCommandError("rebase --abort", "Abort failed"),
        ]

        with patch("sb.print") as mock_print:
            with self.assertRaises(typer.Exit):
                sync("main", "Test commit", mock_config.vault_path)

            # Verify abort failure message
            mock_print.assert_any_call(
                "\t:warning: [yellow]Failed to abort rebase. Manual intervention may be needed.[/yellow]"
            )


class TestInfoCommand(unittest.TestCase):
    """Unit tests for info command."""

    @patch("sb.load_config")
    def test_info_successful(self, mock_load_config):
        """Test successful info command execution."""
        mock_config = Mock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        # Create mock inbox path
        mock_inbox_path = MagicMock(spec=Path)
        mock_inbox_path.exists.return_value = True
        mock_inbox_path.is_dir.return_value = True
        mock_inbox_path.glob.return_value = [Mock() for _ in range(2)]  # 2 files in inbox

        # Mock vault_path / inbox_folder to return mock_inbox_path
        mock_vault_path.__truediv__.return_value = mock_inbox_path
        mock_vault_path.exists.return_value = True
        mock_vault_path.is_dir.return_value = True

        # Mock glob for other folders (if needed by info command)
        mock_vault_path.glob.return_value = [Mock() for _ in range(3)]

        with patch("sb.print") as mock_print:
            info(vault_path=mock_config.vault_path)

        # Verify basic info was printed
        mock_print.assert_any_call("\n:open_file_folder: Folder Structure:")

    @patch("sb.load_config")
    def test_info_missing_folders(self, mock_load_config):
        """Test info command with missing folders."""
        mock_config = Mock()
        mock_vault_path = MagicMock(spec=Path)
        mock_vault_path.__str__.return_value = "/test/vault"
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        # Create mocks for different folder paths
        mock_inbox = MagicMock(spec=Path)
        mock_inbox.exists.return_value = True
        mock_inbox.is_dir.return_value = True
        mock_inbox.glob.return_value = []

        mock_projects = MagicMock(spec=Path)
        mock_projects.exists.return_value = True
        mock_projects.is_dir.return_value = True
        mock_projects.glob.return_value = []

        mock_areas = MagicMock(spec=Path)
        mock_areas.exists.return_value = False  # This folder is missing

        # Map folder names to their mocks
        folder_mocks = {
            "0_Inbox": mock_inbox,
            "1_Projects": mock_projects,
            "2_Areas": mock_areas,
        }

        def truediv_side_effect(folder_name):
            return folder_mocks.get(folder_name, MagicMock(spec=Path))

        mock_vault_path.__truediv__.side_effect = truediv_side_effect

        with patch("sb.print") as mock_print:
            info(vault_path=mock_config.vault_path)

        # Verify missing folders are reported
        mock_print.assert_any_call("\t:cross_mark: [red]2_Areas (missing)[/red]")

    @patch("sb.load_config")
    def test_info_empty_inbox(self, mock_load_config):
        """Test info command with empty inbox."""
        mock_config = Mock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        # Create mock inbox path
        mock_inbox_path = MagicMock(spec=Path)
        mock_inbox_path.exists.return_value = True
        mock_inbox_path.is_dir.return_value = True
        mock_inbox_path.glob.return_value = []  # No files in inbox

        # Mock vault_path / inbox_folder to return mock_inbox_path
        mock_vault_path.__truediv__.return_value = mock_inbox_path
        mock_vault_path.exists.return_value = True
        mock_vault_path.is_dir.return_value = True

        with patch("sb.print") as mock_print:
            info(vault_path=mock_config.vault_path)

        # Verify empty inbox message
        mock_print.assert_any_call("\n:inbox_tray: Inbox is empty :sparkles:")

    @patch("sb.load_config")
    def test_info_many_inbox_files(self, mock_load_config):
        """Test info command with many inbox files (triggering review suggestion)."""
        mock_config = Mock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        # Create mock inbox path
        mock_inbox_path = MagicMock(spec=Path)
        mock_inbox_path.exists.return_value = True
        mock_inbox_path.is_dir.return_value = True
        mock_inbox_path.glob.return_value = [Mock() for _ in range(8)]  # Many files in inbox

        # Mock vault_path / inbox_folder to return mock_inbox_path
        mock_vault_path.__truediv__.return_value = mock_inbox_path
        mock_vault_path.exists.return_value = True
        mock_vault_path.is_dir.return_value = True

        with patch("sb.print") as mock_print:
            info(vault_path=mock_config.vault_path)

        # Verify review suggestion
        mock_print.assert_any_call("\t:light_bulb: [yellow]Consider doing a weekly review![/yellow]")

    @patch("sb.load_config")
    def test_info_missing_inbox_folder(self, mock_load_config):
        """Test info command when inbox folder is missing."""
        mock_config = Mock()
        mock_vault_path = MagicMock(spec=Path)
        mock_config.vault_path = mock_vault_path
        mock_config.inbox_folder = "0_Inbox"
        mock_load_config.return_value = mock_config

        # Create mock inbox path
        mock_inbox_path = MagicMock(spec=Path)
        mock_inbox_path.exists.return_value = False
        mock_inbox_path.is_dir.return_value = True
        mock_inbox_path.glob.return_value = [Mock() for _ in range(8)]  # Many files in inbox

        # Mock vault_path / inbox_folder to return mock_inbox_path
        mock_vault_path.__truediv__.return_value = mock_inbox_path
        mock_vault_path.exists.return_value = True
        mock_vault_path.is_dir.return_value = True

        with patch("sb.print") as mock_print:
            info(vault_path=mock_config.vault_path)

        # Verify missing inbox message
        mock_print.assert_any_call("\n:cross_mark: [red]0_Inbox folder is missing![/red]")

    @patch("sb.load_config")
    def test_info_invalid_vault_error(self, mock_load_config):
        """Test info command when vault configuration is invalid."""
        mock_load_config.side_effect = InvalidVaultError("Invalid vault configuration")

        with patch("sb.print") as mock_print:
            with self.assertRaises(typer.Exit):
                info(vault_path=None)

        mock_print.assert_any_call(":cross_mark: [bold red]Invalid vault configuration[/bold red]")


class TestAppConfiguration(unittest.TestCase):
    """Tests for Typer app configuration."""

    def test_app_initialization(self):
        """Test that the Typer app is properly configured."""
        self.assertEqual(app.info.name, "sb")
        self.assertEqual(app.info.help, "Second Brain CLI - Manage your note-taking system")
        self.assertTrue(app.info.no_args_is_help)

    @parameterized.expand(
        [
            ("sync",),
            ("info",),
        ]
    )
    def test_app_has_commands(self, command_name):
        """Test that the app has the expected commands."""
        self.assertIn(command_name, [cmd.name for cmd in app.registered_commands])

    @parameterized.expand(
        [
            ("new",),
        ]
    )
    def test_app_has_subcommands(self, command_name):
        """Test that the app has the expected subcommands."""
        self.assertIn(command_name, [grp.name for grp in app.registered_groups])
