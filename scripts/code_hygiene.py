#!/usr/bin/env python3
"""
ACGS-2 Code Hygiene and Style Corrections Script

This script:
1. Fixes import issues (hyphenated module names)
2. Applies automated formatting
3. Removes unused imports and variables
4. Ensures proper file endings
5. Improves modular code organization

Usage:
    python scripts/code_hygiene.py [--fix] [--dry-run]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


class CodeHygieneManager:
    """Manages code hygiene and style corrections."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.report = {
            "import_fixes": [],
            "formatting_fixes": [],
            "unused_removals": [],
            "file_ending_fixes": [],
            "merge_conflict_fixes": [],
        }

    def fix_hyphenated_imports(self) -> None:
        """Fix imports with hyphenated module names."""
        print("🔧 Fixing hyphenated imports...")

        # Map of old hyphenated names to new underscore names
        import_mappings = {
            "services.core.constitutional-ai": "services.core.constitutional_ai",
            "services.core.governance-synthesis": "services.core.governance_synthesis",
            "services.core.policy-governance": "services.core.policy_governance",
            "services.core.formal-verification": "services.core.formal_verification",
            "services.core.evolutionary-computation": "services.core.evolutionary_computation",
            "services.core.self-evolving-ai": "services.core.self_evolving_ai",
            "services.core.governance-workflows": "services.core.governance_workflows",
        }

        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content

                # Fix imports
                for old_import, new_import in import_mappings.items():
                    # Fix various import patterns
                    patterns = [
                        (rf"from {re.escape(old_import)}", f"from {new_import}"),
                        (rf"import {re.escape(old_import)}", f"import {new_import}"),
                    ]

                    for pattern, replacement in patterns:
                        content = re.sub(pattern, replacement, content)

                # Write back if changed
                if content != original_content:
                    if not self.dry_run:
                        file_path.write_text(content, encoding="utf-8")

                    self.report["import_fixes"].append(
                        str(file_path.relative_to(self.project_root))
                    )
                    print(
                        f"  ✅ Fixed imports in {file_path.relative_to(self.project_root)}"
                    )

            except Exception as e:
                print(f"  ❌ Error processing {file_path}: {e}")

    def fix_merge_conflicts(self) -> None:
        """Fix merge conflict markers."""
        print("🔧 Fixing merge conflict markers...")

        conflict_patterns = [
            r"<<<<<<< HEAD.*?=======.*?>>>>>>> .*?\n",
            r"<<<<<<< .*?\n",
            r"=======\n",
            r">>>>>>> .*?\n",
        ]

        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content

                # Check for merge conflicts
                has_conflicts = any(
                    re.search(pattern, content, re.DOTALL)
                    for pattern in conflict_patterns
                )

                if has_conflicts:
                    print(
                        f"  ⚠️  Merge conflicts found in {file_path.relative_to(self.project_root)}"
                    )
                    self.report["merge_conflict_fixes"].append(
                        str(file_path.relative_to(self.project_root))
                    )

                    # For now, just report - manual resolution needed
                    if not self.dry_run:
                        print(f"    Manual resolution required for: {file_path}")

            except Exception as e:
                print(f"  ❌ Error checking {file_path}: {e}")

    def ensure_file_endings(self) -> None:
        """Ensure all files end with newline."""
        print("🔧 Ensuring proper file endings...")

        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                if content and not content.endswith("\n"):
                    if not self.dry_run:
                        file_path.write_text(content + "\n", encoding="utf-8")

                    self.report["file_ending_fixes"].append(
                        str(file_path.relative_to(self.project_root))
                    )
                    print(
                        f"  ✅ Added newline to {file_path.relative_to(self.project_root)}"
                    )

            except Exception as e:
                print(f"  ❌ Error processing {file_path}: {e}")

    def remove_unused_imports(self) -> None:
        """Remove unused imports using autoflake."""
        print("🔧 Removing unused imports...")

        cmd = [
            "python3",
            "-m",
            "autoflake",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--recursive",
            "--in-place" if not self.dry_run else "--check",
            ".",
        ]

        try:
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                print("  ✅ Unused imports removed")
                self.report["unused_removals"].append(
                    "autoflake completed successfully"
                )
            else:
                print(f"  ⚠️  autoflake not available or failed: {result.stderr}")

        except FileNotFoundError:
            print("  ⚠️  autoflake not installed, skipping unused import removal")

    def apply_formatting(self) -> None:
        """Apply Black formatting to fixable files."""
        print("🔧 Applying Black formatting...")

        # First, get list of files that can be formatted
        cmd_check = ["python3", "-m", "black", "--check", "--diff", "."]

        try:
            result = subprocess.run(
                cmd_check,
                check=False,
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if not self.dry_run:
                # Apply formatting, but skip files with parse errors
                cmd_format = ["python3", "-m", "black", "--safe", "."]
                format_result = subprocess.run(
                    cmd_format,
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if format_result.returncode == 0:
                    print("  ✅ Black formatting applied")
                    self.report["formatting_fixes"].append("Black formatting completed")
                else:
                    print(
                        f"  ⚠️  Some files could not be formatted: {format_result.stderr}"
                    )
            else:
                print("  ℹ️  Would apply Black formatting (dry run)")

        except FileNotFoundError:
            print("  ⚠️  Black not installed, skipping formatting")

    def organize_imports(self) -> None:
        """Organize imports using isort."""
        print("🔧 Organizing imports...")

        cmd = [
            "python3",
            "-m",
            "isort",
            "--profile",
            "black",
            "--check-only" if self.dry_run else "",
            ".",
        ]

        # Remove empty strings
        cmd = [arg for arg in cmd if arg]

        try:
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                print("  ✅ Import organization completed")
            else:
                print(f"  ⚠️  Some import issues found: {result.stderr}")

        except FileNotFoundError:
            print("  ⚠️  isort not installed, skipping import organization")

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "target",
            ".pytest_cache",
            "htmlcov",
            "build",
            "dist",
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

    def run_hygiene_fixes(self, apply_formatting: bool = True) -> dict[str, any]:
        """Run all code hygiene fixes."""
        print("🧹 Starting ACGS-2 Code Hygiene Fixes")
        print("=" * 50)

        # Fix merge conflicts first
        self.fix_merge_conflicts()

        # Fix import issues
        self.fix_hyphenated_imports()

        # Ensure proper file endings
        self.ensure_file_endings()

        # Remove unused imports
        self.remove_unused_imports()

        # Organize imports
        self.organize_imports()

        # Apply formatting last
        if apply_formatting:
            self.apply_formatting()

        print("\n✅ Code hygiene fixes completed!")
        return self.report


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Apply ACGS-2 code hygiene fixes")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--no-format", action="store_true", help="Skip formatting step")

    args = parser.parse_args()

    # Default to dry run unless --fix is specified
    dry_run = not args.fix or args.dry_run

    project_root = Path(__file__).parent.parent
    manager = CodeHygieneManager(project_root, dry_run=dry_run)

    report = manager.run_hygiene_fixes(apply_formatting=not args.no_format)

    # Print summary
    print("\n📋 Hygiene Fixes Summary:")
    for category, items in report.items():
        if items:
            print(f"  {category}: {len(items)} items")

    return 0


if __name__ == "__main__":
    sys.exit(main())
