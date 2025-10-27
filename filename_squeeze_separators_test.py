#!/usr/bin/env python3

"""
filename_squeeze_separators_test.py

Comprehensive test suite for filename_squeeze_separators.py using pytest.
Tests cover the squeeze logic (consolidating consecutive separators while
preserving single separators), dry-run mode, recursive operations, extension
filtering, and edge cases.
"""

import os
from pathlib import Path

import pytest

# Import the module to test
from filename_squeeze_separators import squeeze_separators, _apply_squeeze_rules


@pytest.fixture
def temp_test_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing.

    Args:
        tmp_path: Pytest's temporary path fixture.

    Returns:
        Path to the temporary test directory.
    """
    test_dir = tmp_path / "test_squeeze"
    test_dir.mkdir()
    return test_dir


def create_file(base_path: Path, filename: str) -> None:
    """Create a file with the given name in the base path.

    Args:
        base_path: Directory where the file should be created.
        filename: Name of the file to create.
    """
    filepath = base_path / filename
    filepath.touch()


def create_directory(base_path: Path, dirname: str) -> Path:
    """Create a directory with the given name in the base path.

    Args:
        base_path: Directory where the subdirectory should be created.
        dirname: Name of the directory to create.

    Returns:
        Path to the created directory.
    """
    dirpath = base_path / dirname
    dirpath.mkdir()
    return dirpath


def get_directory_contents(dirpath: Path) -> set[str]:
    """Get all filenames in a directory (non-recursive).

    Args:
        dirpath: Directory to list.

    Returns:
        Set of filenames in the directory.
    """
    return {item.name for item in dirpath.iterdir()}


class TestSqueezeRulesFunction:
    """Tests for the _apply_squeeze_rules helper function."""

    def test_single_space_to_underscore(self) -> None:
        """Test that single spaces are converted to underscores."""
        assert _apply_squeeze_rules("my file") == "my_file"

    def test_multiple_spaces_to_single_underscore(self) -> None:
        """Test that multiple spaces become single underscore."""
        assert _apply_squeeze_rules("my   file") == "my_file"

    def test_multiple_dots_squeezed(self) -> None:
        """Test that multiple consecutive dots become single dot."""
        assert _apply_squeeze_rules("my..file") == "my.file"

    def test_multiple_hyphens_squeezed(self) -> None:
        """Test that multiple consecutive hyphens become single hyphen."""
        assert _apply_squeeze_rules("my---file") == "my-file"

    def test_multiple_underscores_squeezed(self) -> None:
        """Test that multiple consecutive underscores become single underscore."""
        assert _apply_squeeze_rules("my___file") == "my_file"

    def test_single_dot_preserved(self) -> None:
        """Test that single dots are preserved."""
        assert _apply_squeeze_rules("my.file") == "my.file"

    def test_single_hyphen_preserved(self) -> None:
        """Test that single hyphens are preserved."""
        assert _apply_squeeze_rules("my-file") == "my-file"

    def test_single_underscore_preserved(self) -> None:
        """Test that single underscores are preserved."""
        assert _apply_squeeze_rules("my_file") == "my_file"

    def test_mixed_separators_independent(self) -> None:
        """Test that different separator types are processed independently."""
        assert _apply_squeeze_rules("my.._file") == "my._file"
        assert _apply_squeeze_rules("my. -_file") == "my._-_file"

    def test_leading_separators_squeezed(self) -> None:
        """Test that leading separators are squeezed."""
        assert _apply_squeeze_rules("___file") == "_file"
        assert _apply_squeeze_rules("...file") == ".file"

    def test_trailing_separators_squeezed(self) -> None:
        """Test that trailing separators are squeezed."""
        assert _apply_squeeze_rules("file___") == "file_"
        assert _apply_squeeze_rules("file...") == "file."

    def test_complex_mixed_separators(self) -> None:
        """Test complex combinations of separators."""
        assert _apply_squeeze_rules("my  ..--__file") == "my_.-_file"

    def test_no_change_needed(self) -> None:
        """Test strings that don't need any changes."""
        assert _apply_squeeze_rules("clean_file") == "clean_file"
        assert _apply_squeeze_rules("my-nice.file") == "my-nice.file"


class TestBasicSqueezing:
    """Tests for basic filename squeezing without recursion."""

    def test_squeeze_spaces_in_file(self, temp_test_dir: Path) -> None:
        """Test that spaces in filenames are converted to underscores."""
        create_file(temp_test_dir, "my file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my_file.txt" in get_directory_contents(temp_test_dir)
        assert "my file.txt" not in get_directory_contents(temp_test_dir)

    def test_squeeze_multiple_spaces(self, temp_test_dir: Path) -> None:
        """Test that multiple spaces become single underscore."""
        create_file(temp_test_dir, "my   file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my_file.txt" in get_directory_contents(temp_test_dir)

    def test_squeeze_multiple_dots(self, temp_test_dir: Path) -> None:
        """Test that multiple dots in basename are squeezed."""
        create_file(temp_test_dir, "my..file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my.file.txt" in get_directory_contents(temp_test_dir)

    def test_squeeze_multiple_hyphens(self, temp_test_dir: Path) -> None:
        """Test that multiple hyphens are squeezed."""
        create_file(temp_test_dir, "my---file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my-file.txt" in get_directory_contents(temp_test_dir)

    def test_squeeze_multiple_underscores(self, temp_test_dir: Path) -> None:
        """Test that multiple underscores are squeezed."""
        create_file(temp_test_dir, "my___file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my_file.txt" in get_directory_contents(temp_test_dir)

    def test_single_dot_preserved_in_file(self, temp_test_dir: Path) -> None:
        """Test that single dots in basename are preserved."""
        create_file(temp_test_dir, "my.file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 0
        assert "my.file.txt" in get_directory_contents(temp_test_dir)

    def test_single_hyphen_preserved_in_file(self, temp_test_dir: Path) -> None:
        """Test that single hyphens are preserved."""
        create_file(temp_test_dir, "my-file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 0
        assert "my-file.txt" in get_directory_contents(temp_test_dir)

    def test_extension_preserved(self, temp_test_dir: Path) -> None:
        """Test that file extensions are not altered."""
        create_file(temp_test_dir, "my  file.tar.gz")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my_file.tar.gz" in get_directory_contents(temp_test_dir)

    def test_no_extension_file(self, temp_test_dir: Path) -> None:
        """Test squeezing files without extensions."""
        create_file(temp_test_dir, "my  file")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my_file" in get_directory_contents(temp_test_dir)

    def test_hidden_files_skipped(self, temp_test_dir: Path) -> None:
        """Test that hidden files (starting with dot) are not processed."""
        create_file(temp_test_dir, ".hidden  file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 0
        assert ".hidden  file.txt" in get_directory_contents(temp_test_dir)

    def test_multiple_files(self, temp_test_dir: Path) -> None:
        """Test processing multiple files in same directory."""
        create_file(temp_test_dir, "file  one.txt")
        create_file(temp_test_dir, "file..two.txt")
        create_file(temp_test_dir, "file---three.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 3
        contents = get_directory_contents(temp_test_dir)
        assert "file_one.txt" in contents
        assert "file.two.txt" in contents
        assert "file-three.txt" in contents


class TestDirectorySqueezing:
    """Tests for squeezing directory names."""

    def test_directory_with_spaces(self, temp_test_dir: Path) -> None:
        """Test that directory names with spaces are squeezed."""
        create_directory(temp_test_dir, "my  dir")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my_dir" in get_directory_contents(temp_test_dir)
        assert "my  dir" not in get_directory_contents(temp_test_dir)

    def test_directory_with_multiple_dots(self, temp_test_dir: Path) -> None:
        """Test that multiple dots in directory names are squeezed."""
        create_directory(temp_test_dir, "my..dir")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my.dir" in get_directory_contents(temp_test_dir)

    def test_directory_single_dot_preserved(self, temp_test_dir: Path) -> None:
        """Test that single dots in directory names are preserved."""
        create_directory(temp_test_dir, "photos.backup")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 0
        assert "photos.backup" in get_directory_contents(temp_test_dir)

    def test_directory_single_hyphen_preserved(self, temp_test_dir: Path) -> None:
        """Test that single hyphens in directory names are preserved."""
        create_directory(temp_test_dir, "my-nice-folder")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 0
        assert "my-nice-folder" in get_directory_contents(temp_test_dir)

    def test_directory_no_extension_handling(self, temp_test_dir: Path) -> None:
        """Test that directories are not treated as having extensions."""
        create_directory(temp_test_dir, "folder..with..dots")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        # All dots should be squeezed (not treated as extension)
        assert "folder.with.dots" in get_directory_contents(temp_test_dir)


class TestDryRunMode:
    """Tests for dry-run mode where no actual changes are made."""

    def test_dry_run_no_changes(self, temp_test_dir: Path) -> None:
        """Test that dry-run mode reports changes without making them."""
        create_file(temp_test_dir, "my  file.txt")

        count = squeeze_separators(str(temp_test_dir), dry_run=True)

        assert count == 1
        # Original file should still exist
        assert "my  file.txt" in get_directory_contents(temp_test_dir)
        assert "my_file.txt" not in get_directory_contents(temp_test_dir)

    def test_dry_run_multiple_files(self, temp_test_dir: Path) -> None:
        """Test dry-run with multiple files."""
        create_file(temp_test_dir, "file  one.txt")
        create_file(temp_test_dir, "file..two.txt")
        create_file(temp_test_dir, "clean_file.txt")

        count = squeeze_separators(str(temp_test_dir), dry_run=True)

        assert count == 2
        contents = get_directory_contents(temp_test_dir)
        # Original names should remain
        assert "file  one.txt" in contents
        assert "file..two.txt" in contents
        assert "clean_file.txt" in contents


class TestRecursiveOperation:
    """Tests for recursive directory traversal."""

    def test_recursive_single_level(self, temp_test_dir: Path) -> None:
        """Test recursive operation on one subdirectory level."""
        subdir = create_directory(temp_test_dir, "subdir")
        create_file(subdir, "my  file.txt")

        count = squeeze_separators(str(temp_test_dir), recursive=True)

        assert count == 1
        assert "my_file.txt" in get_directory_contents(subdir)

    def test_recursive_multiple_levels(self, temp_test_dir: Path) -> None:
        """Test recursive operation through multiple directory levels."""
        level1 = create_directory(temp_test_dir, "level1")
        level2 = create_directory(level1, "level2")
        level3 = create_directory(level2, "level3")

        create_file(temp_test_dir, "root  file.txt")
        create_file(level1, "level1  file.txt")
        create_file(level2, "level2  file.txt")
        create_file(level3, "level3  file.txt")

        count = squeeze_separators(str(temp_test_dir), recursive=True)

        assert count == 4
        assert "root_file.txt" in get_directory_contents(temp_test_dir)
        assert "level1_file.txt" in get_directory_contents(level1)
        assert "level2_file.txt" in get_directory_contents(level2)
        assert "level3_file.txt" in get_directory_contents(level3)

    def test_recursive_with_directory_rename(self, temp_test_dir: Path) -> None:
        """Test that directories are renamed and their contents still processed."""
        subdir = create_directory(temp_test_dir, "my..subdir")
        create_file(subdir, "my  file.txt")
        create_file(subdir, "another..file.txt")

        count = squeeze_separators(str(temp_test_dir), recursive=True)

        # Should rename: directory + 2 files = 3
        assert count == 3

        # Directory should be renamed
        assert "my.subdir" in get_directory_contents(temp_test_dir)
        assert "my..subdir" not in get_directory_contents(temp_test_dir)

        # Files inside renamed directory should also be renamed
        new_subdir = temp_test_dir / "my.subdir"
        contents = get_directory_contents(new_subdir)
        assert "my_file.txt" in contents
        assert "another.file.txt" in contents

    def test_recursive_nested_directory_renames(self, temp_test_dir: Path) -> None:
        """Test renaming nested directories with files at each level."""
        level1 = create_directory(temp_test_dir, "dir..level1")
        level2 = create_directory(level1, "dir..level2")

        create_file(level1, "file..in..level1.txt")
        create_file(level2, "file..in..level2.txt")

        count = squeeze_separators(str(temp_test_dir), recursive=True)

        # Should rename: 2 directories + 2 files = 4
        assert count == 4

        # Check renamed directory structure
        new_level1 = temp_test_dir / "dir.level1"
        new_level2 = new_level1 / "dir.level2"

        assert new_level1.exists()
        assert new_level2.exists()
        assert "file.in.level1.txt" in get_directory_contents(new_level1)
        assert "file.in.level2.txt" in get_directory_contents(new_level2)

    def test_non_recursive_ignores_subdirs(self, temp_test_dir: Path) -> None:
        """Test that without recursive flag, subdirectory contents are ignored."""
        subdir = create_directory(temp_test_dir, "subdir")
        create_file(temp_test_dir, "root  file.txt")
        create_file(subdir, "sub  file.txt")

        count = squeeze_separators(str(temp_test_dir), recursive=False)

        # Only root file should be renamed
        assert count == 1
        assert "root_file.txt" in get_directory_contents(temp_test_dir)
        # Subdirectory file should remain unchanged
        assert "sub  file.txt" in get_directory_contents(subdir)

    def test_recursive_dry_run(self, temp_test_dir: Path) -> None:
        """Test recursive dry-run reports all potential changes."""
        subdir = create_directory(temp_test_dir, "my..subdir")
        create_file(subdir, "my  file.txt")

        count = squeeze_separators(str(temp_test_dir), recursive=True, dry_run=True)

        # Should count directory + file = 2
        assert count == 2

        # Nothing should actually change (dry-run)
        assert "my..subdir" in get_directory_contents(temp_test_dir)
        assert "my  file.txt" in get_directory_contents(subdir)


class TestExtensionFiltering:
    """Tests for include and exclude extension filters."""

    def test_include_single_extension(self, temp_test_dir: Path) -> None:
        """Test that only included extensions are processed."""
        create_file(temp_test_dir, "file  one.txt")
        create_file(temp_test_dir, "file  two.jpg")
        create_file(temp_test_dir, "file  three.pdf")

        count = squeeze_separators(str(temp_test_dir), include_exts=[".txt"])

        assert count == 1
        assert "file_one.txt" in get_directory_contents(temp_test_dir)
        assert "file  two.jpg" in get_directory_contents(temp_test_dir)
        assert "file  three.pdf" in get_directory_contents(temp_test_dir)

    def test_include_multiple_extensions(self, temp_test_dir: Path) -> None:
        """Test including multiple extensions."""
        create_file(temp_test_dir, "file  one.txt")
        create_file(temp_test_dir, "file  two.jpg")
        create_file(temp_test_dir, "file  three.pdf")

        count = squeeze_separators(
            str(temp_test_dir),
            include_exts=[".txt", ".jpg"]
        )

        assert count == 2
        contents = get_directory_contents(temp_test_dir)
        assert "file_one.txt" in contents
        assert "file_two.jpg" in contents
        assert "file  three.pdf" in contents

    def test_exclude_single_extension(self, temp_test_dir: Path) -> None:
        """Test that excluded extensions are skipped."""
        create_file(temp_test_dir, "file  one.txt")
        create_file(temp_test_dir, "file  two.jpg")
        create_file(temp_test_dir, "file  three.pdf")

        count = squeeze_separators(str(temp_test_dir), exclude_exts=[".jpg"])

        assert count == 2
        contents = get_directory_contents(temp_test_dir)
        assert "file_one.txt" in contents
        assert "file  two.jpg" in contents  # Should remain unchanged
        assert "file_three.pdf" in contents

    def test_exclude_multiple_extensions(self, temp_test_dir: Path) -> None:
        """Test excluding multiple extensions."""
        create_file(temp_test_dir, "file  one.txt")
        create_file(temp_test_dir, "file  two.jpg")
        create_file(temp_test_dir, "file  three.pdf")

        count = squeeze_separators(
            str(temp_test_dir),
            exclude_exts=[".jpg", ".pdf"]
        )

        assert count == 1
        contents = get_directory_contents(temp_test_dir)
        assert "file_one.txt" in contents
        assert "file  two.jpg" in contents
        assert "file  three.pdf" in contents

    def test_include_and_exclude_intersection(self, temp_test_dir: Path) -> None:
        """Test intersection logic when both include and exclude are specified."""
        create_file(temp_test_dir, "file  one.txt")
        create_file(temp_test_dir, "file  two.jpg")
        create_file(temp_test_dir, "file  three.pdf")
        create_file(temp_test_dir, "file  four.png")

        # Include txt and jpg, but exclude jpg -> only txt should be processed
        count = squeeze_separators(
            str(temp_test_dir),
            include_exts=[".txt", ".jpg"],
            exclude_exts=[".jpg"]
        )

        assert count == 1
        contents = get_directory_contents(temp_test_dir)
        assert "file_one.txt" in contents
        assert "file  two.jpg" in contents  # Excluded from include list
        assert "file  three.pdf" in contents  # Not in include list
        assert "file  four.png" in contents  # Not in include list

    def test_case_insensitive_extensions(self, temp_test_dir: Path) -> None:
        """Test that extension filtering is case-insensitive."""
        create_file(temp_test_dir, "file  one.TXT")
        create_file(temp_test_dir, "file  two.Jpg")

        count = squeeze_separators(str(temp_test_dir), include_exts=[".txt"])

        assert count == 1
        assert "file_one.TXT" in get_directory_contents(temp_test_dir)

    def test_filters_dont_affect_directories(self, temp_test_dir: Path) -> None:
        """Test that extension filters don't apply to directories."""
        create_directory(temp_test_dir, "my..dir")
        create_file(temp_test_dir, "my  file.txt")

        count = squeeze_separators(str(temp_test_dir), exclude_exts=[".txt"])

        # Directory should still be renamed even though txt files are excluded
        assert count == 1
        assert "my.dir" in get_directory_contents(temp_test_dir)
        assert "my  file.txt" in get_directory_contents(temp_test_dir)

    def test_recursive_with_filters(self, temp_test_dir: Path) -> None:
        """Test extension filters work correctly in recursive mode."""
        subdir = create_directory(temp_test_dir, "subdir")
        create_file(temp_test_dir, "root  file.txt")
        create_file(temp_test_dir, "root  file.jpg")
        create_file(subdir, "sub  file.txt")
        create_file(subdir, "sub  file.jpg")

        count = squeeze_separators(
            str(temp_test_dir),
            recursive=True,
            include_exts=[".txt"]
        )

        assert count == 2
        assert "root_file.txt" in get_directory_contents(temp_test_dir)
        assert "root  file.jpg" in get_directory_contents(temp_test_dir)
        assert "sub_file.txt" in get_directory_contents(subdir)
        assert "sub  file.jpg" in get_directory_contents(subdir)


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_existing_target_not_overwritten(self, temp_test_dir: Path) -> None:
        """Test that files are not renamed if target already exists."""
        create_file(temp_test_dir, "my_file.txt")  # Target already exists
        create_file(temp_test_dir, "my  file.txt")  # Would rename to above

        count = squeeze_separators(str(temp_test_dir))

        assert count == 0
        # Both files should still exist
        contents = get_directory_contents(temp_test_dir)
        assert "my_file.txt" in contents
        assert "my  file.txt" in contents

    def test_empty_directory(self, temp_test_dir: Path) -> None:
        """Test that empty directories are handled correctly."""
        count = squeeze_separators(str(temp_test_dir))

        assert count == 0

    def test_only_clean_files(self, temp_test_dir: Path) -> None:
        """Test directory with only files that don't need changes."""
        create_file(temp_test_dir, "clean_file1.txt")
        create_file(temp_test_dir, "clean_file2.txt")
        create_file(temp_test_dir, "my-nice-file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 0

    def test_very_long_separator_sequence(self, temp_test_dir: Path) -> None:
        """Test handling of very long sequences of separators."""
        create_file(temp_test_dir, "my..................file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "my.file.txt" in get_directory_contents(temp_test_dir)

    def test_leading_trailing_separators(self, temp_test_dir: Path) -> None:
        """Test separators at beginning and end of filename."""
        create_file(temp_test_dir, "___file___.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "_file_.txt" in get_directory_contents(temp_test_dir)

    def test_multiple_extensions(self, temp_test_dir: Path) -> None:
        """Test files with multiple extensions like .tar.gz."""
        create_file(temp_test_dir, "my  archive.tar.gz")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        # Extension (.gz) should be preserved
        assert "my_archive.tar.gz" in get_directory_contents(temp_test_dir)

    def test_unicode_filenames(self, temp_test_dir: Path) -> None:
        """Test handling of unicode characters in filenames."""
        create_file(temp_test_dir, "café  résumé.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        assert "café_résumé.txt" in get_directory_contents(temp_test_dir)

    def test_mixed_complex_separators(self, temp_test_dir: Path) -> None:
        """Test complex combinations of different separator types."""
        create_file(temp_test_dir, "my  ..--__file.txt")

        count = squeeze_separators(str(temp_test_dir))

        assert count == 1
        # Spaces->underscore, dots squeezed, hyphens squeezed, underscores squeezed
        assert "my_.-_file.txt" in get_directory_contents(temp_test_dir)


class TestComplexScenarios:
    """Tests for complex real-world scenarios."""

    def test_large_directory_structure(self, temp_test_dir: Path) -> None:
        """Test processing a large, complex directory structure."""
        # Create 3-level deep structure with files at each level
        dirs = {}
        dirs["level1_a"] = create_directory(temp_test_dir, "level..1..a")
        dirs["level1_b"] = create_directory(temp_test_dir, "level--1--b")
        dirs["level2_a1"] = create_directory(dirs["level1_a"], "level  2  a1")
        dirs["level2_a2"] = create_directory(dirs["level1_a"], "level  2  a2")
        dirs["level2_b1"] = create_directory(dirs["level1_b"], "level  2  b1")
        dirs["level3_a1a"] = create_directory(dirs["level2_a1"], "level___3___a1a")

        # Create files at each level
        create_file(temp_test_dir, "root  file.txt")
        create_file(dirs["level1_a"], "file  1a.txt")
        create_file(dirs["level1_b"], "file  1b.txt")
        create_file(dirs["level2_a1"], "file  2a1.txt")
        create_file(dirs["level2_a2"], "file  2a2.txt")
        create_file(dirs["level2_b1"], "file  2b1.txt")
        create_file(dirs["level3_a1a"], "file  3a1a.txt")

        count = squeeze_separators(str(temp_test_dir), recursive=True)

        # Should rename: 6 directories + 7 files = 13
        assert count == 13

    def test_mixed_operations_with_all_flags(self, temp_test_dir: Path) -> None:
        """Test complex scenario with recursive, dry-run, and filters combined."""
        subdir = create_directory(temp_test_dir, "my..subdir")
        create_file(temp_test_dir, "root  file.txt")
        create_file(temp_test_dir, "root  file.jpg")
        create_file(subdir, "sub  file.txt")
        create_file(subdir, "sub  file.jpg")

        count = squeeze_separators(
            str(temp_test_dir),
            recursive=True,
            dry_run=True,
            include_exts=[".txt"]
        )

        # Should count: directory + 2 txt files = 3
        assert count == 3

        # Nothing should actually change (dry-run)
        assert "my..subdir" in get_directory_contents(temp_test_dir)
        assert "root  file.txt" in get_directory_contents(temp_test_dir)
        assert "sub  file.txt" in get_directory_contents(subdir)

    def test_conservative_preservation(self, temp_test_dir: Path) -> None:
        """Test that the conservative squeeze approach preserves intentional naming."""
        # These should NOT be changed
        create_file(temp_test_dir, "my-nice-file.txt")
        create_file(temp_test_dir, "data.backup.txt")
        create_file(temp_test_dir, "file_with_underscores.txt")
        create_directory(temp_test_dir, "photos.backup")

        # These SHOULD be changed
        create_file(temp_test_dir, "bad  spaces.txt")
        create_file(temp_test_dir, "too..many..dots.txt")

        count = squeeze_separators(str(temp_test_dir), recursive=True)

        # Only 2 files should be renamed
        assert count == 2

        contents = get_directory_contents(temp_test_dir)
        # Unchanged files
        assert "my-nice-file.txt" in contents
        assert "data.backup.txt" in contents
        assert "file_with_underscores.txt" in contents
        assert "photos.backup" in contents
        # Changed files
        assert "bad_spaces.txt" in contents
        assert "too.many.dots.txt" in contents

    def test_parallel_squeeze_same_target(self, temp_test_dir: Path) -> None:
        """Test when multiple files would squeeze to the same name."""
        create_file(temp_test_dir, "my  file.txt")
        create_file(temp_test_dir, "my___file.txt")

        # Both would become "my_file.txt"
        count = squeeze_separators(str(temp_test_dir))

        # Only one should be renamed (first one encountered)
        # The second will be skipped because target already exists
        assert count == 1
        assert "my_file.txt" in get_directory_contents(temp_test_dir)
