"""
Integration tests for config.py module.
Test component interactions without mocking file system operations.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from config import Config, InvalidVaultError, load_config


class TestConfigIntegration(unittest.TestCase):
    """Integration tests for configuration loading with real file system."""

    def test_config_load_integration_valid_file(self):
        """Integration test for Config.load with real YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"

            config_data = {"vault_path": "/real/vault/path", "inbox_folder": "0_TestInbox"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            result = Config.load(config_path)
            self.assertIsInstance(result, Config)
            self.assertEqual(result.vault_path, Path("/real/vault/path"))
            self.assertEqual(result.inbox_folder, "0_TestInbox")

    def test_config_load_integration_missing_file(self):
        """Integration test for Config.load with missing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"

            result = Config.load(config_path)
            self.assertIsNone(result)

    def test_full_config_loading_integration(self):
        """Integration test for complete config loading workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir) / "test_vault"
            obsidian_dir = vault_path / ".obsidian"
            vault_path.mkdir()
            obsidian_dir.mkdir()

            config_path = Path(temp_dir) / "config.yaml"
            config_data = {"vault_path": str(vault_path), "inbox_folder": "0_TestInbox"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            result = load_config(config_path, vault_path=None)

            self.assertIsInstance(result, Config)
            self.assertEqual(result.vault_path, vault_path)
            self.assertEqual(result.inbox_folder, "0_TestInbox")

    def test_load_config_cli_override_integration(self):
        """Integration test for CLI vault path override."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_vault = Path(temp_dir) / "config_vault"
            cli_vault = Path(temp_dir) / "cli_vault"

            for vault in [config_vault, cli_vault]:
                obsidian_dir = vault / ".obsidian"
                vault.mkdir()
                obsidian_dir.mkdir()

            config_path = Path(temp_dir) / "config.yaml"
            config_data = {"vault_path": str(config_vault)}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            result = load_config(config_path, vault_path=cli_vault)
            self.assertIsInstance(result, Config)
            self.assertEqual(result.vault_path, cli_vault)

    def test_load_config_no_vault_integration(self):
        """Integration test when no vault is available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"

            with patch("config.find_vault_root", return_value=None):
                with self.assertRaises(InvalidVaultError) as context:
                    load_config(config_path, vault_path=None)

            self.assertIn("No second-brain vault found.", str(context.exception))

    def test_load_config_invalid_vault_integration(self):
        """Integration test with invalid vault path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            invalid_vault = Path("/nonexistent/vault/path")

            config_data = {"vault_path": str(invalid_vault)}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            with self.assertRaises(InvalidVaultError) as context:
                load_config(config_path, vault_path=None)

            self.assertIn("Invalid vault path:", str(context.exception))

    def test_load_config_non_obsidian_integration(self):
        """Integration test with directory that is not an Obsidian vault."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            non_vault_dir = Path(temp_dir) / "not_a_vault"
            non_vault_dir.mkdir()

            config_data = {"vault_path": str(non_vault_dir)}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            with self.assertRaises(InvalidVaultError) as context:
                load_config(config_path, vault_path=None)

            self.assertIn("is not a valid Obsidian vault", str(context.exception))

    def test_load_config_with_tilde_expansion(self):
        """Integration test for path expansion with tilde."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                vault_path = Path(temp_dir) / "test_vault"
                obsidian_dir = vault_path / ".obsidian"
                vault_path.mkdir()
                obsidian_dir.mkdir()

                config_path = Path(temp_dir) / "config.yaml"
                config_data = {"vault_path": "~/test_vault"}
                with open(config_path, "w") as f:
                    yaml.dump(config_data, f)

            original_expanduser = Path.expanduser

            def mock_expanduser(self):
                path_str = str(self)
                if path_str.startswith("~"):
                    return vault_path
                return original_expanduser(self)

            with patch.object(Path, "expanduser", mock_expanduser):
                result = load_config(config_path, vault_path=None)

            self.assertIsInstance(result, Config)
            self.assertEqual(result.vault_path, vault_path)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_config_with_only_inbox(self):
        """Test config file that only specifies inbox_folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_data = {"inbox_folder": "0_TestInbox"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            result = Config.load(config_path)
            self.assertIsInstance(result, Config)
            self.assertIsNone(result.vault_path)
            self.assertEqual(result.inbox_folder, "0_TestInbox")

    def test_config_with_extra_fields(self):
        """Test config file with extra fields (should be ignored by Pydantic)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_data = {
                "vault_path": "/test/vault",
                "inbox_folder": "0_TestInbox",
                "extra_field": "should_be_ignored",
                "another_extra": 123,
            }
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            result = Config.load(config_path)
            self.assertIsInstance(result, Config)
            self.assertEqual(result.vault_path, Path("/test/vault"))
            self.assertEqual(result.inbox_folder, "0_TestInbox")

    def test_special_characters_in_paths(self):
        """Test config with special characters in paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_name = "vault with spaces and (special) chars"
            vault_path = Path(temp_dir) / vault_name
            obsidian_dir = vault_path / ".obsidian"
            vault_path.mkdir()
            obsidian_dir.mkdir()

            config_path = Path(temp_dir) / "config.yaml"
            config_data = {"vault_path": str(vault_path), "inbox_folder": "inbox with spaces"}
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            result = load_config(config_path, vault_path=None)
            self.assertIsInstance(result, Config)
            self.assertEqual(result.vault_path, vault_path)
            self.assertEqual(result.inbox_folder, "inbox with spaces")
