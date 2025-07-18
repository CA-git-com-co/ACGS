#!/usr/bin/env python3
"""
Fix Python syntax errors - replace invalid // comments with # comments
"""

import re
import subprocess
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def fix_python_comments(file_path):
    """Fix invalid // comments in Python files."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Replace // comments with # comments
        # Pattern: whitespace + // + rest of line
        fixed_content = re.sub(
            r"^(\s*)//\s*(.*)$", r"\1# \2", content, flags=re.MULTILINE
        )

        if fixed_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            print(f"Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix Python syntax errors."""
    project_root = Path("/home/dislove/ACGS-1")
    services_dir = project_root / "services"

    if not services_dir.exists():
        print(f"Services directory not found: {services_dir}")
        return

    print("🔧 Fixing Python syntax errors...")

    # Find all Python files with // comments
    result = subprocess.run(
        [
            "find",
            str(services_dir),
            "-name",
            "*.py",
            "-exec",
            "grep",
            "-l",
            "// requires:",
            "{}",
            ";",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("No files with // comments found or error occurred")
        return

    files_to_fix = result.stdout.strip().split("\n")
    files_to_fix = [f for f in files_to_fix if f.strip()]

    print(f"Found {len(files_to_fix)} files to fix")

    fixed_count = 0
    for file_path in files_to_fix:
        if fix_python_comments(file_path):
            fixed_count += 1

    print(f"✅ Fixed {fixed_count} files")

    # Also fix any other // comment patterns
    print("🔧 Fixing additional // comment patterns...")

    # Find files with any // comments
    result = subprocess.run(
        [
            "find",
            str(services_dir),
            "-name",
            "*.py",
            "-exec",
            "grep",
            "-l",
            "//",
            "{}",
            ";",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        additional_files = result.stdout.strip().split("\n")
        additional_files = [
            f for f in additional_files if f.strip() and f not in files_to_fix
        ]

        additional_fixed = 0
        for file_path in additional_files:
            if fix_python_comments(file_path):
                additional_fixed += 1

        print(f"✅ Fixed {additional_fixed} additional files")

    print("🎉 Python syntax error fixing completed!")


if __name__ == "__main__":
    main()
