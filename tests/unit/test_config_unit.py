"""
Unit tests for config.py module.
Mock all external dependencies to test functions in isolation.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from config import INBOX_FOLDER, VAULT_NAME, Config, InvalidVaultError, load_config


class TestConfigModel(unittest.TestCase):
    """Unit tests for Config class."""

    def test_config_defaults(self):
        """Test Config initialization with default values."""
        config = Config()
        self.assertIsNone(config.vault_path)
        self.assertEqual(config.inbox_folder, INBOX_FOLDER)

    def test_config_with_values(self):
        """Test Config initialization with specific values."""
        vault_path = Path("/test/vault")
        inbox = "1_CustomInbox"
        config = Config(vault_path=vault_path, inbox_folder=inbox)
        self.assertEqual(config.vault_path, vault_path)
        self.assertEqual(config.inbox_folder, inbox)

    def test_config_vault_path_optional(self):
        """Test that vault_path remains optional."""
        config = Config(inbox_folder="test_inbox")
        self.assertIsNone(config.vault_path)
        self.assertEqual(config.inbox_folder, "test_inbox")


class TestConfigLoadMethod(unittest.TestCase):
    """Unit tests for Config.load static method."""

    def test_load_nonexistent_file(self):
        """Test loading from non-existent config file returns None."""
        with patch("builtins.print") as mock_print:
            result = Config.load("/nonexistent/path/config.yaml")
            self.assertIsNone(result)
            mock_print.assert_called_once()

    def test_load_valid_yaml_file(self):
        """Test loading from valid YAML configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("vault_path: /test/vault\ninbox_folder: 1_CustomInbox\n")
            temp_path = f.name

        try:
            result = Config.load(temp_path)
            self.assertIsInstance(result, Config)
            self.assertEqual(result.vault_path, Path("/test/vault"))
            self.assertEqual(result.inbox_folder, "1_CustomInbox")
        finally:
            os.unlink(temp_path)

    def test_load_invalid_yaml_file(self):
        """Test loading from invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content:\n  - broken\n- yaml")
            temp_path = f.name

        try:
            # pydantic_yaml will raise an exception for invalid YAML
            with self.assertRaises(Exception):
                Config.load(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_partial_config(self):
        """Test loading YAML with partial configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("inbox_folder: 0_CustomInbox\n")
            temp_path = f.name

        try:
            result = Config.load(temp_path)
            self.assertIsInstance(result, Config)
            self.assertIsNone(result.vault_path)  # Not specified in YAML
            self.assertEqual(result.inbox_folder, "0_CustomInbox")
        finally:
            os.unlink(temp_path)


class TestLoadConfig(unittest.TestCase):
    """Unit tests for load_config function with mocked dependencies."""

    @patch("config.Config.load")
    @patch("config.find_vault_root")
    def test_load_config_no_file_no_cli_vault(self, mock_find_vault, mock_config_load):
        """Test load_config when no config file and no CLI vault path."""
        mock_config_load.return_value = None  # No config file

        mock_vault_path = MagicMock(spec=Path)
        mock_vault_path.expanduser.return_value = mock_vault_path
        mock_vault_path.exists.return_value = True
        mock_vault_path.is_dir.return_value = True

        mock_obsidian_path = MagicMock(spec=Path)
        mock_obsidian_path.exists.return_value = True
        mock_vault_path.__truediv__.return_value = mock_obsidian_path

        mock_find_vault.return_value = mock_vault_path

        config_file = Path("/nonexistent/config.yaml")
        result = load_config(config_file, vault_path=None)

        mock_config_load.assert_called_once_with(config_file.expanduser())
        mock_find_vault.assert_called_once_with(VAULT_NAME)
        self.assertEqual(result.vault_path, mock_vault_path)
        self.assertEqual(result.inbox_folder, INBOX_FOLDER)

        mock_vault_path.__truediv__.assert_called_with(".obsidian")

    @patch("config.Config.load")
    @patch("config.find_vault_root")
    def test_load_config_with_file_no_cli_vault(self, mock_find_vault, mock_config_load):
        """Test load_config with config file but no CLI vault path."""
        mock_vault_path = MagicMock(spec=Path)
        mock_vault_path.expanduser.return_value = mock_vault_path
        mock_vault_path.exists.return_value = True
        mock_vault_path.is_dir.return_value = True

        mock_obsidian_path = MagicMock(spec=Path)
        mock_obsidian_path.exists.return_value = True
        mock_vault_path.__truediv__.return_value = mock_obsidian_path

        mock_config = Config(vault_path=mock_vault_path, inbox_folder="0_Inbox")
        mock_config_load.return_value = mock_config

        config_file = Path("/existing/config.yaml")
        result = load_config(config_file, vault_path=None)

        mock_config_load.assert_called_once_with(config_file.expanduser())
        mock_find_vault.assert_not_called()  # Should not be called when vault_path is in config
        self.assertEqual(result.vault_path, mock_vault_path)
        self.assertEqual(result.inbox_folder, "0_Inbox")

        mock_vault_path.__truediv__.assert_called_with(".obsidian")

    @patch("config.Config.load")
    @patch("config.find_vault_root")
    def test_load_config_cli_vault_override(self, mock_find_vault, mock_config_load):
        """Test that CLI vault path overrides config file vault path."""
        mock_config_vault_path = MagicMock(spec=Path)
        mock_config_vault_path.expanduser.return_value = mock_config_vault_path
        mock_config_vault_path.exists.return_value = True
        mock_config_vault_path.is_dir.return_value = True
        mock_config_obsidian = MagicMock(spec=Path)
        mock_config_obsidian.exists.return_value = True
        mock_config_vault_path.__truediv__.return_value = mock_config_obsidian

        mock_cli_vault_path = MagicMock(spec=Path)
        mock_cli_vault_path.expanduser.return_value = mock_cli_vault_path
        mock_cli_vault_path.exists.return_value = True
        mock_cli_vault_path.is_dir.return_value = True
        mock_cli_obsidian = MagicMock(spec=Path)
        mock_cli_obsidian.exists.return_value = True
        mock_cli_vault_path.__truediv__.return_value = mock_cli_obsidian

        mock_config = Config(vault_path=mock_config_vault_path, inbox_folder="0_Inbox")
        mock_config_load.return_value = mock_config

        config_file = Path("/existing/config.yaml")

        result = load_config(config_file, vault_path=mock_cli_vault_path)

        self.assertEqual(result.vault_path, mock_cli_vault_path)
        self.assertEqual(result.inbox_folder, "0_Inbox")

        mock_cli_vault_path.__truediv__.assert_called_with(".obsidian")

    @patch("config.Config.load")
    @patch("config.find_vault_root")
    def test_load_config_no_vault_found(self, mock_find_vault, mock_config_load):
        """Test load_config when no vault can be found."""
        mock_config_load.return_value = None  # No config file
        mock_find_vault.return_value = None  # No vault found

        config_file = Path("/nonexistent/config.yaml")

        with self.assertRaises(InvalidVaultError) as context:
            load_config(config_file, vault_path=None)

        self.assertIn("No second-brain vault found.", str(context.exception))

    @patch("config.Config.load")
    @patch("config.find_vault_root")
    def test_load_config_invalid_vault_path(self, mock_find_vault, mock_config_load):
        """Test load_config with invalid vault path."""
        invalid_vault = Path("/invalid/vault")
        mock_config_load.return_value = Config(vault_path=invalid_vault)

        config_file = Path("/config.yaml")

        with patch.object(Path, "exists", return_value=False):
            with self.assertRaises(InvalidVaultError) as context:
                load_config(config_file, vault_path=None)

        self.assertIn(f"Invalid vault path: {invalid_vault}", str(context.exception))

    @patch("config.Config.load")
    @patch("config.find_vault_root")
    def test_load_config_non_obsidian_vault(self, mock_find_vault, mock_config_load):
        """Test load_config with vault that lacks .obsidian directory."""
        mock_vault_path = MagicMock(spec=Path)
        mock_vault_path.expanduser.return_value = mock_vault_path
        mock_vault_path.exists.return_value = True
        mock_vault_path.is_dir.return_value = True

        mock_obsidian_path = MagicMock(spec=Path)
        mock_obsidian_path.exists.return_value = False  # Simulate missing .obsidian
        mock_vault_path.__truediv__.return_value = mock_obsidian_path

        mock_config_load.return_value = Config(vault_path=mock_vault_path)
        config_file = Path("/config.yaml")

        with self.assertRaises(InvalidVaultError) as context:
            load_config(config_file, vault_path=None)

        self.assertIn("is not a valid Obsidian vault.", str(context.exception))

        mock_vault_path.__truediv__.assert_called_with(".obsidian")

    @patch("config.Config.load")
    @patch("config.find_vault_root")
    def test_load_config_path_expansion(self, mock_find_vault, mock_config_load):
        """Test that user home expansion is applied to vault path."""
        mock_config_load.return_value = Config(vault_path=Path("~/test_vault"))
        mock_find_vault.return_value = None

        config_file = Path("~/config.yaml")

        with patch.object(Path, "expanduser") as mock_expand:
            mock_expand.return_value = Path("/home/user/test_vault")

            with (
                patch.object(Path, "exists", return_value=True),
                patch.object(Path, "is_dir", return_value=True),
                patch("pathlib.Path.__truediv__") as mock_div,
            ):
                mock_div.return_value.exists.return_value = True

                try:
                    load_config(config_file, vault_path=None)
                    mock_expand.assert_called()
                except InvalidVaultError:
                    pass  # We're only testing path expansion


class TestInvalidVaultError(unittest.TestCase):
    """Tests for custom exception."""

    def test_invalid_vault_error_creation(self):
        """Test InvalidVaultError can be created with message."""
        message = "Test error message"
        exception = InvalidVaultError(message)
        self.assertIsInstance(exception, InvalidVaultError)
        self.assertEqual(str(exception), message)

    def test_config_with_only_inbox(self):
        """Test config file that only specifies inbox_folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_data = {"inbox_folder": "9_SpecialInbox"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            result = Config.load(config_path)
            assert result.vault_path is None
            assert result.inbox_folder == "9_SpecialInbox"
