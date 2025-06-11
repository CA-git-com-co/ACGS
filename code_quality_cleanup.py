#!/usr/bin/env python3
"""
ACGS-1 Code Quality and Standards Cleanup

This script standardizes code formatting, removes unused imports, and enforces
coding standards across the ACGS-1 constitutional governance system.

Features:
- Python code formatting with Black
- TypeScript/JavaScript formatting with Prettier
- Rust code formatting with rustfmt
- Remove unused imports with autoflake
- Remove dead code and commented sections
- Standardize naming conventions
"""

import json
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeQualityCleanup:
    """Handles code quality cleanup and standardization."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.quality_report = {
            "python_files_formatted": [],
            "typescript_files_formatted": [],
            "rust_files_formatted": [],
            "unused_imports_removed": [],
            "dead_code_removed": [],
            "errors": [],
        }

    def install_formatting_tools(self):
        """Install required formatting tools."""
        logger.info("📦 Installing formatting tools...")

        tools = ["black", "autoflake", "isort", "flake8"]

        for tool in tools:
            try:
                subprocess.run(
                    ["pip", "install", tool], check=True, capture_output=True
                )
                logger.info(f"Installed {tool}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {tool}: {e}")
                self.quality_report["errors"].append(f"Tool installation error: {tool}")

    def format_python_files(self):
        """Format Python files with Black and isort."""
        logger.info("🐍 Formatting Python files...")

        python_files = list(self.project_root.glob("**/*.py"))
        formatted_count = 0

        for py_file in python_files:
            if self._should_format_file(py_file):
                try:
                    # Format with Black
                    result = subprocess.run(
                        ["black", "--line-length", "88", str(py_file)],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        # Sort imports with isort
                        subprocess.run(
                            ["isort", "--profile", "black", str(py_file)],
                            capture_output=True,
                        )

                        self.quality_report["python_files_formatted"].append(
                            str(py_file)
                        )
                        formatted_count += 1

                except Exception as e:
                    logger.error(f"Error formatting {py_file}: {e}")
                    self.quality_report["errors"].append(
                        f"Python formatting error: {py_file}"
                    )

        logger.info(f"Formatted {formatted_count} Python files")

    def remove_unused_imports(self):
        """Remove unused imports and variables."""
        logger.info("🧹 Removing unused imports...")

        python_files = list(self.project_root.glob("**/*.py"))
        cleaned_count = 0

        for py_file in python_files:
            if self._should_format_file(py_file):
                try:
                    result = subprocess.run(
                        [
                            "autoflake",
                            "--remove-all-unused-imports",
                            "--remove-unused-variables",
                            "--in-place",
                            str(py_file),
                        ],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        self.quality_report["unused_imports_removed"].append(
                            str(py_file)
                        )
                        cleaned_count += 1

                except Exception as e:
                    logger.error(f"Error cleaning imports in {py_file}: {e}")

        logger.info(f"Cleaned imports in {cleaned_count} files")

    def format_typescript_files(self):
        """Format TypeScript and JavaScript files."""
        logger.info("📜 Formatting TypeScript/JavaScript files...")

        # Check if prettier is available
        try:
            subprocess.run(
                ["npx", "prettier", "--version"], check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            logger.warning("Prettier not available, skipping TS/JS formatting")
            return

        js_files = (
            list(self.project_root.glob("**/*.ts"))
            + list(self.project_root.glob("**/*.tsx"))
            + list(self.project_root.glob("**/*.js"))
            + list(self.project_root.glob("**/*.jsx"))
        )

        formatted_count = 0

        for js_file in js_files:
            if self._should_format_file(js_file):
                try:
                    result = subprocess.run(
                        ["npx", "prettier", "--write", str(js_file)],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        self.quality_report["typescript_files_formatted"].append(
                            str(js_file)
                        )
                        formatted_count += 1

                except Exception as e:
                    logger.error(f"Error formatting {js_file}: {e}")

        logger.info(f"Formatted {formatted_count} TypeScript/JavaScript files")

    def format_rust_files(self):
        """Format Rust files with rustfmt."""
        logger.info("🦀 Formatting Rust files...")

        # Check if rustfmt is available
        try:
            subprocess.run(["rustfmt", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.warning("rustfmt not available, skipping Rust formatting")
            return

        rust_files = list(self.project_root.glob("**/*.rs"))
        formatted_count = 0

        for rust_file in rust_files:
            if self._should_format_file(rust_file):
                try:
                    result = subprocess.run(
                        ["rustfmt", str(rust_file)], capture_output=True, text=True
                    )

                    if result.returncode == 0:
                        self.quality_report["rust_files_formatted"].append(
                            str(rust_file)
                        )
                        formatted_count += 1

                except Exception as e:
                    logger.error(f"Error formatting {rust_file}: {e}")

        logger.info(f"Formatted {formatted_count} Rust files")

    def remove_commented_code(self):
        """Remove large blocks of commented-out code."""
        logger.info("🗑️ Removing commented-out code blocks...")

        python_files = list(self.project_root.glob("**/*.py"))
        cleaned_count = 0

        for py_file in python_files:
            if self._should_format_file(py_file):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Remove large blocks of commented code (5+ consecutive comment lines)
                    cleaned_lines = []
                    comment_block = []

                    for line in lines:
                        stripped = line.strip()
                        if stripped.startswith("#") and not stripped.startswith("# "):
                            comment_block.append(line)
                        else:
                            if len(comment_block) >= 5:
                                # This was a large commented block, skip it
                                pass
                            else:
                                # Keep small comment blocks
                                cleaned_lines.extend(comment_block)
                            comment_block = []
                            cleaned_lines.append(line)

                    # Handle remaining comment block
                    if len(comment_block) < 5:
                        cleaned_lines.extend(comment_block)

                    # Write back if changes were made
                    if len(cleaned_lines) != len(lines):
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.writelines(cleaned_lines)

                        self.quality_report["dead_code_removed"].append(str(py_file))
                        cleaned_count += 1

                except Exception as e:
                    logger.error(f"Error removing commented code in {py_file}: {e}")

        logger.info(f"Removed commented code from {cleaned_count} files")

    def run_linting_checks(self):
        """Run linting checks and report issues."""
        logger.info("🔍 Running linting checks...")

        try:
            # Run flake8 on Python files
            result = subprocess.run(
                [
                    "flake8",
                    "--max-line-length=88",
                    "--extend-ignore=E203,W503",
                    str(self.project_root / "services"),
                    str(self.project_root / "applications"),
                    str(self.project_root / "integrations"),
                ],
                capture_output=True,
                text=True,
            )

            if result.stdout:
                logger.info("Linting issues found:")
                logger.info(result.stdout)
            else:
                logger.info("No linting issues found")

        except Exception as e:
            logger.error(f"Error running linting checks: {e}")

    def _should_format_file(self, file_path: Path) -> bool:
        """Determine if file should be formatted."""
        exclude_patterns = [
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            "target",
            "migrations",
            "backup_",
            "archive",
            ".pytest_cache",
            "build",
            "dist",
            ".tox",
        ]
        return not any(pattern in str(file_path) for pattern in exclude_patterns)

    def run_code_quality_cleanup(self):
        """Run complete code quality cleanup process."""
        logger.info("🚀 Starting ACGS-1 Code Quality Cleanup...")

        # 1. Install formatting tools
        self.install_formatting_tools()

        # 2. Remove unused imports first
        self.remove_unused_imports()

        # 3. Format Python files
        self.format_python_files()

        # 4. Format TypeScript/JavaScript files
        self.format_typescript_files()

        # 5. Format Rust files
        self.format_rust_files()

        # 6. Remove commented-out code
        self.remove_commented_code()

        # 7. Run linting checks
        self.run_linting_checks()

        # 8. Save quality report
        report_path = self.project_root / "code_quality_report.json"
        with open(report_path, "w") as f:
            json.dump(self.quality_report, f, indent=2)

        logger.info(f"✅ Code quality cleanup completed. Report: {report_path}")

        # Summary
        total_files = (
            len(self.quality_report["python_files_formatted"])
            + len(self.quality_report["typescript_files_formatted"])
            + len(self.quality_report["rust_files_formatted"])
        )

        logger.info(f"📊 Summary:")
        logger.info(f"  - {total_files} files formatted")
        logger.info(
            f"  - {len(self.quality_report['unused_imports_removed'])} files cleaned of unused imports"
        )
        logger.info(
            f"  - {len(self.quality_report['dead_code_removed'])} files had dead code removed"
        )
        logger.info(f"  - {len(self.quality_report['errors'])} errors encountered")

        return self.quality_report


def main():
    """Main execution function."""
    cleanup = CodeQualityCleanup()
    cleanup.run_code_quality_cleanup()


if __name__ == "__main__":
    main()
