#!/usr/bin/env python3

r"""
filename_squeeze_separators.py
-John Taylor
2025-10-27

Description:
  This script renames files and directories by squeezing (consolidating) separator
  characters. Multiple consecutive separators of the same type are reduced to a
  single character. Spaces (single or multiple) are converted to a single underscore.
  Hidden files (starting with '.') are skipped, and the script will not overwrite
  existing files.

Squeezing Rules:
  - Any spaces (one or more) are replaced with a single underscore
  - Multiple consecutive dots are squeezed to a single dot
  - Multiple consecutive hyphens are squeezed to a single hyphen
  - Multiple consecutive underscores are squeezed to a single underscore

Examples:
  "my  file.txt"         → "my_file.txt"
  "photos..backup"       → "photos.backup"
  "my---file.txt"        → "my-file.txt"
  "data___file.txt"      → "data_file.txt"
  "my. -_file.txt"       → "my._-_file.txt"

Features:
  - Recursive operation with --recursive / -r
  - Dry-run (no changes made) with --dry-run / -n
  - Safe rename logic that avoids overwriting
  - Extension filtering with --include and/or --exclude

Extension Filtering Logic:
  The two options, --include and --exclude, can be used separately or together.

    * If only --include is given -> only files with listed extensions are processed.
    * If only --exclude is given -> all files except those extensions are processed.
    * If both --include and --exclude are given ->
      A file will be processed only if its extension is present in --include
      **and not present in** --exclude. (Intersection logic)
"""

import os
import re
import argparse

PGM_VERSION = "1.0.0"
PGM_URL = "https://github.com/jftuga/filename_squeeze_separators"


def squeeze_separators(
    dirname: str,
    *,
    recursive: bool = False,
    dry_run: bool = False,
    include_exts: list[str] | None = None,
    exclude_exts: list[str] | None = None,
) -> int:
    """Squeeze separator characters in filenames within a directory.

    Renames files and directories by consolidating multiple consecutive separators
    of the same type into a single character. Spaces are converted to underscores.
    Hidden items and files that would overwrite existing ones are skipped. Works
    recursively if enabled. Respects include/exclude filters.

    Squeezing rules:
      - Any spaces → single underscore
      - Multiple dots → single dot
      - Multiple hyphens → single hyphen
      - Multiple underscores → single underscore

    Args:
        dirname: Directory to process.
        recursive: If True, process subdirectories recursively.
        dry_run: Show intended renames but do not perform them.
        include_exts: List of file extensions to include, or None for all.
        exclude_exts: List of file extensions to exclude, or None for none.

    Returns:
        Number of renamed items.
    """
    renamed_count = 0

    try:
        entries = [name for name in os.listdir(dirname) if not name.startswith(".")]
    except PermissionError:
        print(f'Permission denied: cannot access directory "{dirname}"')
        return 0
    except OSError as e:
        print(f'Error accessing "{dirname}": {e}')
        return 0

    for name in entries:
        old_path = os.path.join(dirname, name)
        if not os.path.exists(old_path):
            continue

        # Determine whether to skip based on extensions
        if os.path.isfile(old_path):
            _, ext = os.path.splitext(name)
            ext = ext.lower()

            # Inclusion filter
            if include_exts and ext not in [e.lower() for e in include_exts]:
                continue

            # Exclusion filter
            if exclude_exts and ext in [e.lower() for e in exclude_exts]:
                continue

        # Generate squeezed name
        if os.path.isfile(old_path):
            # For files: split extension and only squeeze the basename
            base_name, ext = os.path.splitext(name)
            squeezed_base = _apply_squeeze_rules(base_name)
            new_name = squeezed_base + ext
        else:
            # For directories: squeeze the entire name
            new_name = _apply_squeeze_rules(name)

        if new_name == name:
            if recursive and os.path.isdir(old_path):
                renamed_count += squeeze_separators(
                    old_path,
                    recursive=recursive,
                    dry_run=dry_run,
                    include_exts=include_exts,
                    exclude_exts=exclude_exts,
                )
            continue

        new_path = os.path.join(dirname, new_name)
        print(f'Renaming: "{old_path}" -> "{new_path}"')

        if os.path.exists(new_path):
            print(f'Skipping: "{new_name}" already exists.')
            continue

        if dry_run:
            print("  (dry-run) rename skipped.")
            renamed_count += 1
            # Still recurse into the directory with its current name
            if recursive and os.path.isdir(old_path):
                renamed_count += squeeze_separators(
                    old_path,  # Use old_path, not new_path
                    recursive=recursive,
                    dry_run=dry_run,
                    include_exts=include_exts,
                    exclude_exts=exclude_exts,
                )
            continue

        try:
            os.rename(old_path, new_path)
            renamed_count += 1
        except PermissionError:
            print(f'Permission denied: cannot rename "{old_path}"')
            continue
        except OSError as e:
            print(f'Error renaming "{old_path}": {e}')
            continue

        if recursive and os.path.isdir(new_path):
            renamed_count += squeeze_separators(
                new_path,
                recursive=recursive,
                dry_run=dry_run,
                include_exts=include_exts,
                exclude_exts=exclude_exts,
            )

    if renamed_count == 0:
        print(f'No files or directories were renamed in "{dirname}".')
    else:
        print(f'{renamed_count} item(s) renamed in "{dirname}"')
    return renamed_count


def _apply_squeeze_rules(text: str) -> str:
    """Apply squeezing rules to a string.

    Applies the following transformations in sequence:
      1. Any spaces → single underscore
      2. Multiple consecutive dots → single dot
      3. Multiple consecutive hyphens → single hyphen
      4. Multiple consecutive underscores → single underscore

    Args:
        text: String to process.

    Returns:
        Processed string with squeezed separators.
    """
    # Replace any spaces (one or more) with single underscore
    text = re.sub(r" +", "_", text)
    # Squeeze multiple dots to single dot
    text = re.sub(r"\.{2,}", ".", text)
    # Squeeze multiple hyphens to single hyphen
    text = re.sub(r"-{2,}", "-", text)
    # Squeeze multiple underscores to single underscore
    text = re.sub(r"_{2,}", "_", text)
    return text


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments using argparse.

    Returns:
        argparse.Namespace containing parsed arguments.

    CLI Description:
        Both --include and --exclude can be combined. When both are specified,
        a file is considered only if its extension:
          (a) Appears in the --include list
          (b) Does NOT appear in the --exclude list
        This is known as *intersection logic* - only files satisfying BOTH
        conditions above are renamed.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Rename files and directories by squeezing (consolidating) separator "
            "characters. Multiple consecutive separators of the same type are "
            "reduced to a single character. Spaces are converted to underscores. "
            "Hidden files are skipped; existing targets are not overwritten.\n\n"
            "Squeezing Rules:\n"
            "  - Any spaces → single underscore\n"
            "  - Multiple dots → single dot\n"
            "  - Multiple hyphens → single hyphen\n"
            "  - Multiple underscores → single underscore\n\n"
            "Extension Filtering Behavior:\n"
            "  --include EXT1,EXT2,... : process only these extensions\n"
            "  --exclude EXT1,EXT2,... : skip these extensions\n\n"
            "If both options are given, the intersection logic applies: a file must "
            "match --include and not match --exclude."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "directories",
        nargs="+",
        help="Directory paths to process (one or more).",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively process subdirectories.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes.",
    )
    parser.add_argument(
        "--include",
        metavar="EXTS",
        help="Comma-separated list of file extensions to include (e.g. '.txt,.jpg').",
    )
    parser.add_argument(
        "--exclude",
        metavar="EXTS",
        help="Comma-separated list of file extensions to exclude (e.g. '.log,.bak').",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f'%(prog)s {PGM_VERSION}\n{PGM_URL}'
    )

    return parser.parse_args()


def main() -> None:
    """Program entry point. Parses arguments and executes renaming."""
    args = parse_args()

    def parse_list(opt: str | None) -> list[str] | None:
        if not opt:
            return None
        return [ext.strip() for ext in opt.split(",") if ext.strip()]

    include_exts = parse_list(args.include)
    exclude_exts = parse_list(args.exclude)

    total_renamed = 0
    for dirname in args.directories:
        if not os.path.isdir(dirname):
            print(f' Skipping "{dirname}": not a directory or not accessible.')
            continue

        print(f'\nProcessing directory: "{dirname}"')
        total_renamed += squeeze_separators(
            dirname,
            recursive=args.recursive,
            dry_run=args.dry_run,
            include_exts=include_exts,
            exclude_exts=exclude_exts,
        )

    if args.dry_run:
        print(f"\n(Dry-run complete) {total_renamed} potential rename(s) found.")
    else:
        print(f"\nDone. {total_renamed} item(s) renamed.")


if __name__ == "__main__":
    main()
