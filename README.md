# filename_squeeze_separators

A Python utility for cleaning up filenames by consolidating multiple consecutive separator characters while preserving intentional naming conventions. This tool takes a conservative approach, only modifying filenames that have problematic multiple separators or spaces.

## Table of Contents

- [Description](#description)
- [Disclaimer](#disclaimer)
  - [Squeezing Rules](#squeezing-rules)
  - [Examples](#examples)
  - [What Gets Preserved](#what-gets-preserved)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Display Version](#display-version)
  - [Basic Usage](#basic-usage)
  - [Recursive Mode](#recursive-mode)
  - [Dry-Run Mode](#dry-run-mode)
  - [Extension Filtering](#extension-filtering)
  - [Combined Options](#combined-options)
  - [Multiple Directories](#multiple-directories)
- [Command-Line Options](#command-line-options)
- [Extension Filtering Logic](#extension-filtering-logic)
- [Safety Features](#safety-features)
- [Testing](#testing)
  - [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
  - [TestSqueezeRulesFunction (14 tests)](#testsqueezerulesfunction-14-tests)
  - [TestBasicSqueezing (12 tests)](#testbasicsqueezing-12-tests)
  - [TestDirectorySqueezing (6 tests)](#testdirectorysqueezing-6-tests)
  - [TestDryRunMode (2 tests)](#testdryrunmode-2-tests)
  - [TestRecursiveOperation (6 tests)](#testrecursiveoperation-6-tests)
  - [TestExtensionFiltering (9 tests)](#testextensionfiltering-9-tests)
  - [TestEdgeCases (9 tests)](#testedgecases-9-tests)
  - [TestComplexScenarios (4 tests)](#testcomplexscenarios-4-tests)
- [Key Test Examples](#key-test-examples)
  - [Spaces to Underscores](#spaces-to-underscores)
  - [Dots Preserved and Squeezed](#dots-preserved-and-squeezed)
  - [Hyphens Preserved and Squeezed](#hyphens-preserved-and-squeezed)
  - [Underscores Preserved and Squeezed](#underscores-preserved-and-squeezed)
  - [Mixed Separators](#mixed-separators)
  - [Extension Preservation](#extension-preservation)
  - [Directory Handling](#directory-handling)
  - [Conservative Approach Validation](#conservative-approach-validation)
- [Implementation Details](#implementation-details)
  - [Architecture](#architecture)
  - [Algorithm](#algorithm)
  - [Squeeze Rules Implementation](#squeeze-rules-implementation)
- [Use Cases](#use-cases)
- [Acknowledgments](#acknowledgments)

## Description

This script renames files and directories by "squeezing" separator characters - reducing multiple consecutive separators of the same type to a single character. Spaces (single or multiple) are converted to underscores. The tool preserves single separators like dots, hyphens, and underscores, respecting intentional naming patterns.

## Disclaimer

The `filename_squeeze_separators.py` script was developed with AI assistance and has been validated through comprehensive testing. The included test suite (`filename_squeeze_separators_test.py`) provides 57 tests across 8 test classes, ensuring reliable and safe file operations. All tests pass successfully, confirming the script's correctness and stability. Users are still encouraged to use the `--dry-run` flag to preview changes before applying them to important files.

### Squeezing Rules

The script applies these transformations:

- **Any spaces** (one or more) are replaced with a single underscore
- **Multiple consecutive dots** are squeezed to a single dot
- **Multiple consecutive hyphens** are squeezed to a single hyphen
- **Multiple consecutive underscores** are squeezed to a single underscore

### Examples

```
"my  file.txt"         → "my_file.txt"
"photos..backup"       → "photos.backup"
"my---file.txt"        → "my-file.txt"
"data___file.txt"      → "data_file.txt"
"my. -_file.txt"       → "my._-_file.txt"
```

### What Gets Preserved

The conservative approach means these filenames remain unchanged:

```
"my-nice-file.txt"           → unchanged (single hyphens preserved)
"photos.backup"              → unchanged (single dot preserved)
"file_with_underscores.txt"  → unchanged (single underscores preserved)
"data.backup.2024"           → unchanged (single dots preserved)
```

## Features

- **Recursive operation** - Process entire directory trees
- **Dry-run mode** - Preview changes before committing
- **Extension filtering** - Include or exclude specific file types
- **Safe operation** - Never overwrites existing files
- **Hidden file handling** - Automatically skips hidden files (starting with '.')
- **Extension preservation** - File extensions are never modified
- **Directory support** - Works on both files and directories

## Requirements

- Python 3.11 or higher
- pytest (for running tests)
- uv (optional, for dependency management)

## Installation

Clone the repository:

```bash
git clone https://github.com/jftuga/filename_squeeze_separators.git
cd filename_squeeze_separators
```

**No additional dependencies are required for the main script.** For development and testing, you can use either uv or pip:

**Using uv (recommended):**
```bash
# Install uv if you don't have it
pip install uv

# Install dev dependencies
uv sync --group dev
```

**Using pip:**
```bash
pip install pytest
```

## Usage

### Display Version

Show the program version and repository URL:

```bash
python3 filename_squeeze_separators.py --version
```

### Basic Usage

Process files in a single directory:

```bash
python3 filename_squeeze_separators.py /path/to/directory
```

### Recursive Mode

Process all subdirectories:

```bash
python3 filename_squeeze_separators.py -r /path/to/directory
```

### Dry-Run Mode

Preview changes without making them:

```bash
python3 filename_squeeze_separators.py -n /path/to/directory
```

### Extension Filtering

Process only specific file types:

```bash
# Include only .txt and .md files
python3 filename_squeeze_separators.py --include .txt,.md /path/to/directory

# Exclude .log and .tmp files
python3 filename_squeeze_separators.py --exclude .log,.tmp /path/to/directory

# Combine include and exclude (intersection logic)
python3 filename_squeeze_separators.py --include .txt,.md --exclude .tmp /path/to/directory
```

### Combined Options

```bash
# Recursive dry-run with filtering
python3 filename_squeeze_separators.py -rn --include .txt,.jpg /path/to/directory
```

### Multiple Directories

Process multiple directories in one command:

```bash
python3 filename_squeeze_separators.py -r /path/one /path/two /path/three
```

## Command-Line Options

```
positional arguments:
  directories           Directory paths to process (one or more)

optional arguments:
  -h, --help            Show help message and exit
  -r, --recursive       Recursively process subdirectories
  -n, --dry-run         Show what would be done without making changes
  --include EXTS        Comma-separated list of file extensions to include
  --exclude EXTS        Comma-separated list of file extensions to exclude
  -v, --version         Output program version and URL and then exit
```

## Extension Filtering Logic

The `--include` and `--exclude` options can be used separately or together:

- **Only --include**: Process only files with the specified extensions
- **Only --exclude**: Process all files except those with the specified extensions
- **Both --include and --exclude**: Process files that are in the include list AND not in the exclude list (intersection logic)

Extension matching is case-insensitive. Filters do not apply to directories.

## Safety Features

- **No overwriting**: If the target filename already exists, the original file is skipped
- **Hidden files skipped**: Files starting with '.' are automatically skipped
- **Extension preservation**: File extensions are never modified (only the basename is processed)
- **Dry-run capability**: Test operations before committing changes
- **Error handling**: Permission errors and OS errors are caught and reported

## Testing

The project includes a comprehensive test suite with 57 tests using pytest.

### Running Tests

First, install the development dependencies using uv:

```bash
# Install dev dependencies (includes pytest)
uv sync --group dev
```

Then run the tests:

```bash
# Run all tests
pytest filename_squeeze_separators_test.py -v

# Run tests with verbose output
pytest filename_squeeze_separators_test.py -v -s

# Run specific test class
pytest filename_squeeze_separators_test.py::TestBasicSqueezing -v

# Run a single test
pytest filename_squeeze_separators_test.py::TestBasicSqueezing::test_squeeze_spaces_in_file -v
```

## Test Coverage

The test suite includes **57 comprehensive tests across 8 test classes**:

### TestSqueezeRulesFunction (14 tests)
Direct tests of the `_apply_squeeze_rules()` helper function:
- Single and multiple space handling
- Dot, hyphen, and underscore squeezing
- Single separator preservation
- Mixed separator combinations
- Leading and trailing separator handling

### TestBasicSqueezing (12 tests)
- Space conversion to underscores
- Individual separator type squeezing
- Single separator preservation in files
- Extension preservation
- Hidden file handling
- Multiple file processing

### TestDirectorySqueezing (6 tests)
- Directory name squeezing
- Single separator preservation in directories
- Directory extension handling
- Conservative approach validation

### TestDryRunMode (2 tests)
- Dry-run reporting without changes
- Multiple file dry-run scenarios

### TestRecursiveOperation (6 tests)
- Multi-level directory recursion
- Directory renaming with content processing
- Nested directory handling
- Non-recursive mode validation
- Recursive dry-run mode

### TestExtensionFiltering (9 tests)
- Include and exclude single/multiple extensions
- Intersection logic when both filters are used
- Case-insensitive extension matching
- Filter interaction with directories
- Recursive operations with filters

### TestEdgeCases (9 tests)
- Collision prevention (no overwriting)
- Empty directory handling
- Very long separator sequences
- Leading and trailing separators
- Multiple file extensions (.tar.gz)
- Unicode filename support
- Complex mixed separator scenarios

### TestComplexScenarios (4 tests)
- Large multi-level directory structures
- All flags combined (recursive + dry-run + filters)
- Conservative preservation validation
- Multiple files squeezing to same target name

## Key Test Examples

The test suite validates the conservative squeezing approach:

### Spaces to Underscores
```python
"my file.txt"      → "my_file.txt"      # Single space
"my   file.txt"    → "my_file.txt"      # Multiple spaces
```

### Dots Preserved and Squeezed
```python
"photos.backup"      → "photos.backup"    # Single dot preserved
"my..file.txt"       → "my.file.txt"      # Multiple dots squeezed
"config...backup"    → "config.backup"    # Many dots squeezed
```

### Hyphens Preserved and Squeezed
```python
"my-nice-file.txt"   → "my-nice-file.txt" # Single hyphens preserved
"my---file.txt"      → "my-file.txt"      # Multiple hyphens squeezed
```

### Underscores Preserved and Squeezed
```python
"my_file.txt"        → "my_file.txt"      # Single underscore preserved
"my___file.txt"      → "my_file.txt"      # Multiple underscores squeezed
```

### Mixed Separators
```python
"my. -_file.txt"     → "my._-_file.txt"   # Each type processed independently
"my  ..--__file.txt" → "my_.-_file.txt"   # Complex combination
```

### Extension Preservation
```python
"my  archive.tar.gz" → "my_archive.tar.gz" # Extension always preserved
"file..name.txt"     → "file.name.txt"     # Basename squeezed, extension intact
```

### Directory Handling
```python
# Directories renamed and contents processed
"my..dir/" with "my  file.txt" inside
    → "my.dir/" with "my_file.txt" inside
```

### Conservative Approach Validation
```python
# These remain unchanged (single separators respected)
"my-nice-file.txt"           → unchanged
"data.backup.txt"            → unchanged
"file_with_underscores.txt"  → unchanged
"photos.backup"              → unchanged
```

## Implementation Details

### Architecture

- **Main function**: `squeeze_separators()` handles directory traversal and file processing
- **Helper function**: `_apply_squeeze_rules()` applies the transformation logic
- **Separation of concerns**: File operations separated from string transformations
- **Type hints**: All functions use Python 3.11+ type annotations

### Algorithm

1. List all non-hidden items in the directory
2. For each item:
   - Check if it should be skipped based on extension filters (files only)
   - Apply squeeze rules (split extension for files, process entire name for directories)
   - Check if the new name would cause a collision
   - Rename the item (or report in dry-run mode)
   - If directory and recursive mode, process its contents

### Squeeze Rules Implementation

The rules are applied as a sequence of regex substitutions:

```python
text = re.sub(r" +", "_", text)      # Spaces to underscore
text = re.sub(r"\.{2,}", ".", text)  # Squeeze dots
text = re.sub(r"-{2,}", "-", text)   # Squeeze hyphens
text = re.sub(r"_{2,}", "_", text)   # Squeeze underscores
```

## Use Cases

- **Cleaning up downloaded files** with inconsistent naming
- **Organizing photo collections** with varied separator usage
- **Preparing files for web deployment** where spaces cause issues
- **Standardizing project directories** with mixed naming conventions
- **Batch processing** legacy file systems with problematic names

## Acknowledgments

- Developed with a focus on conservative, safe file operations
- Test suite designed to ensure reliability and prevent data loss
- Inspired by the need for intelligent filename cleanup tools
