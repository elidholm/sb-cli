"""
Unit tests for utils.py module.
Mock all external dependencies to test functions in isolation.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Import the functions to test
from utils import daily_exists, find_vault_root, format_hashtags, sanitize_filename


class TestDailyExists(unittest.TestCase):
    """Unit tests for daily_exists function."""

    def setUp(self):
        """Set up any necessary test data."""
        self.mock_path = Mock(spec=Path)
        self.mock_path.exists.return_value = True

    def test_daily_exists_returns_true_when_path_exists(self):
        """Test that daily_exists returns True when path exists."""
        result = daily_exists(self.mock_path)

        self.assertTrue(result)
        self.mock_path.exists.assert_called_once()

    def test_daily_exists_returns_false_when_path_does_not_exist(self):
        """Test that daily_exists returns False when path doesn't exist."""
        self.mock_path.exists.return_value = False

        result = daily_exists(self.mock_path)

        self.assertFalse(result)
        self.mock_path.exists.assert_called_once()

    def test_daily_exists_with_none_path(self):
        """Test daily_exists with None path."""
        with self.assertRaises(AttributeError):
            daily_exists(None)


class TestFindVaultRoot(unittest.TestCase):
    """Unit tests for find_vault_root function."""

    @patch("utils.Path.cwd")
    def test_find_vault_root_found_in_parent_directory(self, mock_cwd):
        """Test finding vault in parent directory."""
        # Mock current directory structure
        mock_current = MagicMock(spec=Path)
        mock_parent = MagicMock(spec=Path)
        mock_grandparent = MagicMock(spec=Path)

        mock_current.parent = mock_parent
        mock_parent.parent = mock_grandparent
        mock_grandparent.parent = mock_grandparent  # Root condition

        mock_cwd.return_value = mock_current

        # Mock vault NOT found in current directory
        mock_current_path = MagicMock(spec=Path)
        mock_current_path.exists.return_value = False
        mock_current.__truediv__.return_value = mock_current_path

        # Mock vault found in parent directory
        mock_vault_path = MagicMock(spec=Path)
        mock_vault_path.exists.return_value = True
        mock_vault_path.is_dir.return_value = True

        mock_parent.__truediv__.return_value = mock_vault_path

        result = find_vault_root("test_vault")

        self.assertEqual(result, mock_vault_path)
        mock_parent.__truediv__.assert_called_with("test_vault")

    @patch("utils.Path.cwd")
    def test_find_vault_root_not_found(self, mock_cwd):
        """Test when vault is not found in directory tree."""
        mock_current = MagicMock(spec=Path)
        mock_parent = MagicMock(spec=Path)
        mock_current.parent = mock_parent
        mock_parent.parent = mock_parent  # Root condition
        mock_cwd.return_value = mock_current

        # Mock vault not found in current directory
        mock_current_vault_path = MagicMock(spec=Path)
        mock_current_vault_path.exists.return_value = False
        mock_current.__truediv__.return_value = mock_current_vault_path

        # Mock vault not found in parent directory (root)
        mock_parent_vault_path = MagicMock(spec=Path)
        mock_parent_vault_path.exists.return_value = False
        mock_parent.__truediv__.return_value = mock_parent_vault_path

        result = find_vault_root("nonexistent_vault")

        self.assertIsNone(result)

    @patch("utils.Path.cwd")
    def test_find_vault_root_found_when_already_inside_vault(self, mock_cwd):
        """Test finding vault when already inside it."""
        # Create a chain of mock directories
        mock_vault_dir = MagicMock(spec=Path)
        mock_vault_dir.name = "my_vault"
        mock_vault_dir.parent = MagicMock(spec=Path)
        mock_vault_dir.parent.parent = mock_vault_dir.parent  # Root condition

        mock_subdir = MagicMock(spec=Path)
        mock_subdir.name = "subfolder"
        mock_subdir.parent = mock_vault_dir

        mock_subdir_vault_path = MagicMock(spec=Path)
        mock_subdir_vault_path.exists.return_value = False
        mock_subdir.__truediv__.return_value = mock_subdir_vault_path

        mock_vault_child_path = MagicMock(spec=Path)
        mock_vault_child_path.exists.return_value = False
        mock_vault_dir.__truediv__.return_value = mock_vault_child_path

        mock_cwd.return_value = mock_subdir

        result = find_vault_root("my_vault")

        self.assertEqual(result, mock_vault_dir)

    @patch("utils.Path.cwd")
    def test_find_vault_root_not_found_when_not_inside_vault(self, mock_cwd):
        """Test not finding vault when not inside it."""
        mock_current = Mock(spec=Path)
        mock_current.name = "some_other_folder"
        mock_current.parent = mock_current  # Root condition

        mock_cwd.return_value = mock_current

        result = find_vault_root("target_vault")

        self.assertIsNone(result)

    @patch("utils.Path.cwd")
    def test_find_vault_root_empty_vault_name(self, mock_cwd):
        """Test find_vault_root with empty vault name."""
        vault_name = ""

        result = find_vault_root(vault_name)

        # Should return None since empty name won't match any directory
        self.assertIsNone(result)


class TestSanitizeFilename(unittest.TestCase):
    """Unit tests for sanitize_filename function."""

    def test_sanitize_filename_basic_case(self):
        """Test basic filename sanitization."""
        title = "My Test File"

        result = sanitize_filename(title)

        self.assertEqual(result, "my_test_file")

    def test_sanitize_filename_with_special_characters(self):
        """Test sanitization with special characters."""
        title = "File@Name#With$Special%Characters&"

        result = sanitize_filename(title)

        self.assertEqual(result, "filenamewithspecialcharacters")

    def test_sanitize_filename_with_multiple_spaces(self):
        """Test sanitization with multiple spaces."""
        title = "File   With    Multiple     Spaces"

        result = sanitize_filename(title)

        self.assertEqual(result, "file_with_multiple_spaces")

    def test_sanitize_filename_with_hyphens_and_underscores(self):
        """Test sanitization preserving hyphens and normalizing underscores."""
        title = "File-With--Multiple___Underscores---"

        result = sanitize_filename(title)

        self.assertEqual(result, "file-with-multiple_underscores")

    def test_sanitize_filename_with_leading_trailing_special_chars(self):
        """Test sanitization removing leading/trailing special characters."""
        title = "---__Test File__---"

        result = sanitize_filename(title)

        self.assertEqual(result, "test_file")

    def test_sanitize_filename_empty_string(self):
        """Test sanitization with empty string."""
        title = ""

        result = sanitize_filename(title)

        self.assertEqual(result, "untitled")

    def test_sanitize_filename_only_special_characters(self):
        """Test sanitization with only special characters."""
        title = "@#$%^&*()"

        result = sanitize_filename(title)

        self.assertEqual(result, "untitled")

    def test_sanitize_filename_with_numbers(self):
        """Test sanitization with numbers."""
        title = "File 123 with Numbers 456"

        result = sanitize_filename(title)

        self.assertEqual(result, "file_123_with_numbers_456")

    def test_sanitize_filename_whitespace_only(self):
        """Test sanitization with whitespace only."""
        title = "   \t\n  "

        result = sanitize_filename(title)

        self.assertEqual(result, "untitled")

    def test_sanitize_filename_mixed_case(self):
        """Test that output is always lowercase."""
        title = "MixedCase FILE Name"

        result = sanitize_filename(title)

        self.assertEqual(result, "mixedcase_file_name")
        self.assertTrue(result.islower())

    def test_sanitize_filename_none_input(self):
        """Test sanitize_filename with None input."""
        with self.assertRaises(AttributeError):
            sanitize_filename(None)


class TestFormatHashtags(unittest.TestCase):
    """Unit tests for format_hashtags function."""

    def test_format_hashtags_normal_case(self):
        """Test formatting normal comma-separated hashtags."""
        hashtags = "python, testing, automation"

        result = format_hashtags(hashtags)

        self.assertEqual(result, "#python #testing #automation")

    def test_format_hashtags_empty_string(self):
        """Test formatting with empty string."""
        hashtags = ""

        result = format_hashtags(hashtags)

        self.assertEqual(result, "")

    def test_format_hashtags_none_input(self):
        """Test formatting with None input."""
        hashtags = None

        result = format_hashtags(hashtags)

        self.assertEqual(result, "")

    def test_format_hashtags_with_extra_spaces(self):
        """Test formatting with extra spaces around commas."""
        hashtags = "  python , testing  ,automation  "

        result = format_hashtags(hashtags)

        self.assertEqual(result, "#python #testing #automation")

    def test_format_hashtags_single_tag(self):
        """Test formatting with single hashtag."""
        hashtags = "python"

        result = format_hashtags(hashtags)

        self.assertEqual(result, "#python")

    def test_format_hashtags_empty_tags(self):
        """Test formatting with empty tags in the list."""
        hashtags = "python,,testing,,automation"

        result = format_hashtags(hashtags)

        self.assertEqual(result, "#python #testing #automation")

    def test_format_hashtags_all_empty_tags(self):
        """Test formatting with all empty tags."""
        hashtags = ",,, ,,"

        result = format_hashtags(hashtags)

        self.assertEqual(result, "")

    def test_format_hashtags_with_special_characters(self):
        """Test formatting with special characters in tags."""
        hashtags = "python-3, unit_test, api_v2"

        result = format_hashtags(hashtags)

        self.assertEqual(result, "#python-3 #unit_test #api_v2")

    def test_format_hashtags_with_integer_input(self):
        """Test format_hashtags with integer input."""
        with self.assertRaises(AttributeError):
            format_hashtags(123)
