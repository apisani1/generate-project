#!/usr/bin/env python3
"""
find-and-replace: A CLI tool to find and replace text in files using regular expressions
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

def find_files(file_pattern: str, directory: str, recursive: bool = False) -> List[str]:
    """
    Find files matching the pattern in the specified directory.

    Args:
        file_pattern: Glob pattern for file names
        directory: Directory to search in
        recursive: Whether to search recursively

    Returns:
        List of file paths matching the pattern
    """
    files = []

    if recursive:
        # Use pathlib for recursive globbing
        base_path = Path(directory)
        if not base_path.exists():
            print(f"Error: Directory '{directory}' does not exist.")
            return []

        # Use rglob for recursive search
        for file_path in base_path.rglob(file_pattern):
            if file_path.is_file():
                files.append(str(file_path))
    else:
        # Use glob for non-recursive search
        search_pattern = os.path.join(directory, file_pattern)
        files = [f for f in glob.glob(search_pattern) if os.path.isfile(f)]

    return sorted(files)

def process_file(file_path: str, pattern: str, replacement: str, no_confirm: bool = False) -> bool:
    """
    Process a single file for find and replace operations.

    Args:
        file_path: Path to the file to process
        pattern: Regular expression pattern to find
        replacement: Text to replace matches with
        no_confirm: Whether to skip confirmation prompts

    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Compile the regex pattern
        regex = re.compile(pattern)

        # Find all matches
        matches = list(regex.finditer(content))

        if not matches:
            print(f"No matches found in: {file_path}")
            return False

        print(f"\nFile: {file_path}")
        print(f"Found {len(matches)} match(es)")

        if not no_confirm:
            # Show matches and ask for confirmation
            for i, match in enumerate(matches, 1):
                start, end = match.span()
                line_num = content[:start].count('\n') + 1

                # Get context around the match
                lines = content.split('\n')
                context_line = lines[line_num - 1] if line_num <= len(lines) else ""

                print(f"\nMatch {i} (line {line_num}):")
                print(f"  Found: '{match.group()}'")
                print(f"  Context: {context_line}")
                print(f"  Replace with: '{replacement}'")

            response = input(f"\nReplace all {len(matches)} match(es) in this file? (y/n/q): ").lower()

            if response == 'q':
                print("Operation cancelled by user.")
                sys.exit(0)
            elif response != 'y':
                print("Skipping file.")
                return False

        # Perform the replacement
        new_content = regex.sub(replacement, content)

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

        print(f"✓ Successfully replaced {len(matches)} match(es) in: {file_path}")
        return True

    except re.error as e:
        print(f"Error: Invalid regular expression - {e}")
        return False
    except UnicodeDecodeError:
        print(f"Error: Cannot read file '{file_path}' - not a text file or encoding issue")
        return False
    except PermissionError:
        print(f"Error: Permission denied accessing file '{file_path}'")
        return False
    except Exception as e:
        print(f"Error processing file '{file_path}': {e}")
        return False

def main() -> None:
    """Main function to handle CLI arguments and orchestrate the find-and-replace operation."""

    parser = argparse.ArgumentParser(
        description="Find and replace text in files using regular expressions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  find-and-replace "*.py" /path/to/project "old_function" "new_function"
  find-and-replace "*.txt" . "hello.*world" "hi universe" -r -n
  find-and-replace "config.json" ~/projects "\"version\":\s*\"[^\"]*\"" "\"version\": \"2.0.0\"" -r
        """
    )

    parser.add_argument(
        'file_name',
        help='File name pattern (supports glob expressions like *.py, config.*, etc.)'
    )

    parser.add_argument(
        'directory',
        help='Directory to search in (supports glob expressions)'
    )

    parser.add_argument(
        'text_to_find',
        help='Regular expression pattern to find'
    )

    parser.add_argument(
        'text_to_replace',
        help='Text to replace matches with (can include regex groups like \\1, \\2)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively search subdirectories'
    )

    parser.add_argument(
        '-n', '--no-confirm',
        action='store_true',
        help='Do not ask for confirmation before making changes'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making actual changes'
    )

    args = parser.parse_args()

    # Validate regex pattern
    try:
        re.compile(args.text_to_find)
    except re.error as e:
        print(f"Error: Invalid regular expression pattern '{args.text_to_find}' - {e}")
        sys.exit(1)

    # Expand directory path
    directory = os.path.expanduser(args.directory)

    # Find matching files
    print(f"Searching for files matching '{args.file_name}' in '{directory}'...")
    if args.recursive:
        print("(Searching recursively)")

    files = find_files(args.file_name, directory, args.recursive)

    if not files:
        print("No matching files found.")
        sys.exit(0)

    print(f"Found {len(files)} file(s) to process:")
    for file_path in files:
        print(f"  {file_path}")

    if not args.no_confirm and not args.dry_run:
        response = input(f"\nProceed with processing {len(files)} file(s)? (y/n): ").lower()
        if response != 'y':
            print("Operation cancelled.")
            sys.exit(0)

    # Process files
    modified_count = 0

    for file_path in files:
        if args.dry_run:
            # For dry run, just show what would be found
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                regex = re.compile(args.text_to_find)
                matches = list(regex.finditer(content))

                if matches:
                    print(f"\n[DRY RUN] Would process: {file_path}")
                    print(f"[DRY RUN] Found {len(matches)} match(es)")
                    modified_count += 1

            except Exception as e:
                print(f"[DRY RUN] Error reading file '{file_path}': {e}")
        else:
            if process_file(file_path, args.text_to_find, args.text_to_replace, args.no_confirm):
                modified_count += 1

    # Summary
    print(f"\n{'=' * 50}")
    if args.dry_run:
        print(f"DRY RUN COMPLETE: {modified_count} file(s) would be modified")
    else:
        print(f"OPERATION COMPLETE: {modified_count} file(s) modified")
    print(f"Total files processed: {len(files)}")

if __name__ == "__main__":
    main()
