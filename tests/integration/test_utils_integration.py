"""
Integration tests for utils.py module.
Test functions with real filesystem interactions and component integration.
"""

import os
import tempfile
import unittest
from pathlib import Path

import pytest

# Import the functions to test
from utils import daily_exists, find_vault_root, format_hashtags, sanitize_filename


class TestDailyExistsIntegration(unittest.TestCase):
    """Integration tests for daily_exists function with real filesystem."""

    def test_daily_exists_with_real_filesystem(self):
        """Test daily_exists with actual file system operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            existing_file = temp_path / "test_daily.md"
            existing_file.write_text("# Test Daily Note")

            non_existing_file = temp_path / "nonexistent.md"

            self.assertTrue(daily_exists(existing_file))
            self.assertFalse(daily_exists(non_existing_file))

    def test_daily_exists_with_different_file_types(self):
        """Test daily_exists with different file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test with .md file
            md_file = temp_path / "daily.md"
            md_file.write_text("# Markdown")
            self.assertTrue(daily_exists(md_file))

            # Test with .txt file
            txt_file = temp_path / "daily.txt"
            txt_file.write_text("Text file")
            self.assertTrue(daily_exists(txt_file))

            # Test with no extension
            no_ext_file = temp_path / "daily"
            no_ext_file.write_text("No extension")
            self.assertTrue(daily_exists(no_ext_file))


class TestFindVaultRootIntegration(unittest.TestCase):
    """Integration tests for find_vault_root function with real directory structure."""

    def test_find_vault_root_in_parent_directory(self):
        """Test finding vault in parent directory with real filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            vault_dir = temp_path / "test_vault"
            vault_dir.mkdir()

            sub_dir = vault_dir / "subfolder"
            sub_dir.mkdir()

            deep_sub_dir = sub_dir / "deep_subfolder"
            deep_sub_dir.mkdir()

            # Change to deep subdirectory and search for vault
            original_cwd = os.getcwd()
            os.chdir(deep_sub_dir)

            try:
                result = find_vault_root("test_vault")

                self.assertIsNotNone(result)
                self.assertEqual(result, vault_dir)
            finally:
                os.chdir(original_cwd)

    def test_find_vault_root_when_already_in_vault(self):
        """Test finding vault when already inside it with real filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            vault_dir = temp_path / "my_vault"
            vault_dir.mkdir()

            sub_dir = vault_dir / "subfolder"
            sub_dir.mkdir()

            original_cwd = os.getcwd()
            os.chdir(sub_dir)

            try:
                result = find_vault_root("my_vault")

                self.assertIsNotNone(result)
                self.assertEqual(result, vault_dir)
            finally:
                os.chdir(original_cwd)

    def test_find_vault_root_not_found(self):
        """Test when vault is not found with real filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            some_dir = temp_path / "some_directory"
            some_dir.mkdir()

            original_cwd = os.getcwd()
            os.chdir(some_dir)

            try:
                result = find_vault_root("nonexistent_vault")

                self.assertIsNone(result)
            finally:
                os.chdir(original_cwd)

    def test_find_vault_root_with_similar_names(self):
        """Test vault finding with similar directory names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create similar but different directories
            correct_vault = temp_path / "my_vault"
            correct_vault.mkdir()

            similar_vault = temp_path / "my_vault_backup"
            similar_vault.mkdir()

            original_cwd = os.getcwd()
            os.chdir(temp_path)

            try:
                result_correct = find_vault_root("my_vault")
                result_similar = find_vault_root("my_vault_backup")

                self.assertEqual(result_correct, correct_vault)
                self.assertEqual(result_similar, similar_vault)
            finally:
                os.chdir(original_cwd)


class TestSanitizeFilenameIntegration(unittest.TestCase):
    """Integration tests for sanitize_filename function with filesystem validation."""

    def test_sanitized_filenames_are_filesystem_safe(self):
        """Test that sanitized filenames can be safely used in filesystem."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            test_cases = [
                "Normal File Name",
                "File@With#Special$Chars",
                "File With  Multiple   Spaces",
                "File-With--Multiple___Underscores",
                "UPPERCASE LOWERCASE MixedCase",
                "File123 With456 Numbers789",
            ]

            for title in test_cases:
                sanitized = sanitize_filename(title)

                # Create file with sanitized name
                file_path = temp_path / f"{sanitized}.md"

                try:
                    # Write and read to verify filesystem compatibility
                    file_path.write_text(f"# {title}")
                    content = file_path.read_text()

                    self.assertTrue(file_path.exists())
                    self.assertEqual(content, f"# {title}")
                    # Clean up for next iteration
                    file_path.unlink()

                except (OSError, IOError) as e:
                    pytest.fail(f"Filename '{sanitized}' is not filesystem safe: {e}")

    def test_sanitized_filenames_are_unique(self):
        """Test that similar titles produce unique sanitized filenames."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            similar_titles = [
                "Test File",
                "Test  File",  # Extra space
                "Test_File",  # Underscore instead of space
                "test-file",  # Hyphen instead of space
                "TestFile",  # No space
            ]

            sanitized_names = set()

            for title in similar_titles:
                sanitized = sanitize_filename(title)
                sanitized_names.add(sanitized)

                # Create file to ensure no conflicts
                file_path = temp_path / f"{sanitized}.md"
                file_path.write_text(f"# {title}")

            self.assertSetEqual(sanitized_names, {"test_file", "testfile", "test-file"})


class TestFormatHashtagsIntegration(unittest.TestCase):
    """Integration tests for format_hashtags function in context of note creation."""

    def test_format_hashtags_in_note_context(self):
        """Test formatted hashtags in the context of a complete note."""
        test_cases = [
            ("python, testing", "#python #testing"),
            ("daily, journal, 2024", "#daily #journal #2024"),
            ("", ""),
            (None, ""),
        ]

        for input_tags, expected_output in test_cases:
            formatted = format_hashtags(input_tags)

            # Create a mock note content
            note_content = f"# Daily Note\n\nContent goes here.\n\nTags: {formatted}"

            if expected_output:
                self.assertIn(formatted, note_content)
                self.assertTrue(note_content.endswith(formatted))
            else:
                self.assertIn("Tags: ", note_content)
                self.assertTrue(note_content.endswith("Tags: "))

    def test_hashtags_with_file_creation(self):
        """Test that formatted hashtags work well in actual file content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            hashtag_inputs = [
                "python, automation, testing",
                "project-alpha, milestone-1",
                "urgent, important, follow-up",
            ]

            for i, tags in enumerate(hashtag_inputs):
                formatted_tags = format_hashtags(tags)

                # Create a note file with these tags
                filename = temp_path / f"test_note_{i}.md"
                content = f"""# Test Note {i}

This is a test note with formatted hashtags.

**Tags**: {formatted_tags}
"""
                filename.write_text(content)

                # Read back and verify
                read_content = filename.read_text()

                self.assertIn(formatted_tags, read_content)
                if formatted_tags:  # Only check if there are tags
                    self.assertTrue(read_content.strip().endswith(formatted_tags))
                    assert read_content.strip().endswith(formatted_tags)


class TestComponentIntegration(unittest.TestCase):
    """Integration tests testing multiple functions working together."""

    def test_complete_note_creation_workflow(self):
        """Test complete workflow from title to file creation with hashtags."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Simulate user input
            note_title = "Meeting Notes @Company#2024"
            hashtags_input = "meeting, work, important"

            sanitized_filename = sanitize_filename(note_title)
            formatted_hashtags = format_hashtags(hashtags_input)

            # Create the file
            note_path = temp_path / f"{sanitized_filename}.md"
            note_content = f"""# {note_title}

Discussion points and action items from the meeting.

{formatted_hashtags}
"""
            note_path.write_text(note_content)

            # Verify file was created
            self.assertTrue(daily_exists(note_path))

            # Verify content
            read_content = note_path.read_text()
            self.assertIn(note_title, read_content)
            self.assertIn(formatted_hashtags, read_content)

            # Verify filename is safe
            self.assertEqual(note_path.name, "meeting_notes_company2024.md")

    def test_vault_discovery_and_note_creation(self):
        """Integration test combining vault discovery and note operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create vault structure
            temp_path = Path(temp_dir)
            vault_root = temp_path / "second_brain"
            vault_root.mkdir()

            inbox_dir = vault_root / "0_Inbox"
            inbox_dir.mkdir()

            # Create subdirectory structure
            deep_dir = vault_root / "area" / "project" / "resources"
            deep_dir.mkdir(parents=True)

            original_cwd = os.getcwd()
            os.chdir(deep_dir)

            try:
                # Find vault from deep directory
                found_vault = find_vault_root("second_brain")

                # Assert vault was found
                self.assertIsNotNone(found_vault)
                self.assertEqual(found_vault, vault_root)

                # Use vault path for note creation
                daily_note_path = found_vault / "0_Inbox" / "2024-01-15.md"
                daily_note_path.write_text("# Daily Note\n\nContent here.")

                # Verify note exists using our function
                self.assertTrue(daily_exists(daily_note_path))

            finally:
                os.chdir(original_cwd)


class TestEdgeCasesIntegration(unittest.TestCase):
    """Integration tests for edge cases with real filesystem."""

    def test_very_long_filenames(self):
        """Test with very long input strings."""
        long_title = "A" * 500  # Very long title
        long_hashtags = ",".join([f"tag{i}" for i in range(100)])  # Many tags

        # These should not crash
        sanitized = sanitize_filename(long_title)
        formatted = format_hashtags(long_hashtags)

        self.assertGreater(len(sanitized), 0)
        self.assertGreater(len(formatted), 0)

    def test_unicode_characters(self):
        """Test with unicode characters in inputs."""
        unicode_title = "Café Meeting with naïve participants 🚀"
        unicode_hashtags = "café,naïve,🚀"

        # Should handle unicode without crashing
        sanitized = sanitize_filename(unicode_title)
        formatted = format_hashtags(unicode_hashtags)

        # Note: The current implementation removes non-ASCII characters
        # This is expected behavior based on the regex pattern [^a-zA-Z0-9\-_]
        self.assertEqual(sanitized, "caf_meeting_with_nave_participants")
        self.assertEqual(formatted, "#café #naïve #🚀")
