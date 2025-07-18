#!/usr/bin/env python3
"""
ACGS Dependency Cleanup Script

This script removes all dependency artifacts and prepares the project for
unified dependency management with UV and proper TOML configuration.

What it removes:
- All node_modules directories
- All Python virtual environments (venv, env, .venv)
- All build artifacts (dist, build, target, .next)
- All cache directories (__pycache__, .mypy_cache, .pytest_cache)
- All lock files (package-lock.json, yarn.lock, Cargo.lock, poetry.lock)
- All compiled artifacts (*.pyc, *.pyo, *.so)

What it preserves:
- Source code
- Configuration files (config/environments/pyproject.toml, Cargo.toml, package.json)
- Documentation
- Git repository
"""

import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("dependency_cleanup.log")],
)
logger = logging.getLogger(__name__)


class DependencyCleanup:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.removed_files = []
        self.removed_dirs = []
        self.total_size_freed = 0

        # Directories to remove completely
        self.dirs_to_remove = {
            "node_modules",
            "venv",
            "env",
            ".venv",
            "config/environments/development.env",
            "dist",
            "build",
            "out",
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".tox",
            ".nox",
            "htmlcov",
            ".coverage",
            ".next",
            ".nuxt",
            ".cache",
            ".parcel-cache",
            "target/debug",
            "target/release",
            ".gradle",
            ".m2",
            "vendor",
            "coverage",
        }

        # File patterns to remove
        self.files_to_remove = {
            "package-lock.json",
            "yarn.lock",
            "Cargo.lock",
            "poetry.lock",
            "Pipfile.lock",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "*.so",
            "*.dll",
            "*.dylib",
            "*.egg-info",
            "*.log",
            ".DS_Store",
            "Thumbs.db",
            "*.tmp",
            "*.temp",
        }

        # Directories to preserve (never remove)
        self.preserve_dirs = {
            ".git",
            ".github",
            "src",
            "lib",
            "services",
            "applications",
            "blockchain",
            "config",
            "infrastructure",
            "docs",
            "scripts",
            "tools",
            "tests",
            "test",
        }

    def get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        except (OSError, FileNotFoundError):
            pass
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}PB"

    def should_preserve_directory(self, dir_path: Path) -> bool:
        """Check if directory should be preserved"""
        # Check if any parent directory is in preserve list
        for parent in dir_path.parents:
            if parent.name in self.preserve_dirs:
                return True

        # Check if directory itself is in preserve list
        if dir_path.name in self.preserve_dirs:
            return True

        return False

    def remove_dependency_directories(self) -> None:
        """Remove all dependency directories"""
        logger.info("Removing dependency directories...")

        for root, dirs, files in os.walk(self.project_root, topdown=False):
            root_path = Path(root)

            # Skip if in preserve directory
            if self.should_preserve_directory(root_path):
                continue

            for dir_name in dirs:
                if dir_name in self.dirs_to_remove:
                    dir_path = root_path / dir_name

                    # Calculate size before removal
                    size = self.get_directory_size(dir_path)

                    try:
                        shutil.rmtree(dir_path)
                        self.removed_dirs.append(
                            str(dir_path.relative_to(self.project_root))
                        )
                        self.total_size_freed += size
                        logger.debug(
                            f"Removed directory: {dir_path} ({self.format_size(size)})"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to remove directory {dir_path}: {e}")

    def remove_dependency_files(self) -> None:
        """Remove dependency files"""
        logger.info("Removing dependency files...")

        for pattern in self.files_to_remove:
            if "*" in pattern:
                # Handle glob patterns
                for file_path in self.project_root.rglob(pattern):
                    if self.should_preserve_directory(file_path.parent):
                        continue

                    try:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        self.removed_files.append(
                            str(file_path.relative_to(self.project_root))
                        )
                        self.total_size_freed += size
                        logger.debug(f"Removed file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove file {file_path}: {e}")
            else:
                # Handle exact filenames
                for file_path in self.project_root.rglob(pattern):
                    if self.should_preserve_directory(file_path.parent):
                        continue

                    try:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        self.removed_files.append(
                            str(file_path.relative_to(self.project_root))
                        )
                        self.total_size_freed += size
                        logger.debug(f"Removed file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove file {file_path}: {e}")

    def remove_git_tracked_dependencies(self) -> None:
        """Remove dependency artifacts from Git tracking"""
        logger.info("Removing dependency artifacts from Git tracking...")

        # Patterns to remove from Git
        git_remove_patterns = [
            "node_modules/",
            "target/",
            "dist/",
            "build/",
            "__pycache__/",
            "*.pyc",
            "package-lock.json",
            "yarn.lock",
            "Cargo.lock",
            "poetry.lock",
        ]

        for pattern in git_remove_patterns:
            try:
                result = subprocess.run(
                    ["git", "rm", "-r", "--cached", "--ignore-unmatch", pattern],
                    check=False,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    logger.debug(f"Removed from Git: {pattern}")

            except subprocess.CalledProcessError as e:
                logger.debug(f"Git remove failed for {pattern}: {e}")

    def clean_empty_directories(self) -> None:
        """Remove empty directories"""
        logger.info("Cleaning empty directories...")

        removed_count = 0
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            root_path = Path(root)

            # Skip preserve directories
            if self.should_preserve_directory(root_path):
                continue

            # Skip root directory
            if root_path == self.project_root:
                continue

            # Check if directory is empty
            try:
                if not any(root_path.iterdir()):
                    root_path.rmdir()
                    removed_count += 1
                    logger.debug(f"Removed empty directory: {root_path}")
            except Exception as e:
                logger.debug(f"Failed to remove empty directory {root_path}: {e}")

        if removed_count > 0:
            logger.info(f"Removed {removed_count} empty directories")

    def generate_report(self) -> None:
        """Generate cleanup report"""
        logger.info("Generating cleanup report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_size_freed": self.format_size(self.total_size_freed),
            "total_size_freed_bytes": self.total_size_freed,
            "directories_removed": len(self.removed_dirs),
            "files_removed": len(self.removed_files),
            "removed_directories": self.removed_dirs[:20],  # Top 20
            "removed_files": self.removed_files[:50],  # Top 50
        }

        # Save report
        report_file = self.project_root / "dependency_cleanup_report.json"
        import json

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 60)
        print("🧹 DEPENDENCY CLEANUP COMPLETE")
        print("=" * 60)
        print(f"📊 Total space freed: {report['total_size_freed']}")
        print(f"📁 Directories removed: {report['directories_removed']}")
        print(f"📄 Files removed: {report['files_removed']}")
        print(f"📋 Report saved to: {report_file}")
        print("\n💡 Next steps:")
        print("1. Run 'python scripts/setup_dependency_management.py' to setup UV")
        print("2. Install dependencies with 'uv sync'")
        print("3. For Node.js: 'npm install'")
        print("4. For Rust: 'cargo build'")
        print("5. Commit changes to Git")

    def run_cleanup(self) -> bool:
        """Run the complete cleanup process"""
        logger.info("Starting ACGS dependency cleanup...")

        try:
            # Step 1: Remove dependency directories
            self.remove_dependency_directories()

            # Step 2: Remove dependency files
            self.remove_dependency_files()

            # Step 3: Remove from Git tracking
            self.remove_git_tracked_dependencies()

            # Step 4: Clean empty directories
            self.clean_empty_directories()

            # Step 5: Generate report
            self.generate_report()

            logger.info("✅ Dependency cleanup completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False


def main():
    """Main entry point"""
    print("🧹 ACGS Dependency Cleanup")
    print("This will remove ALL dependency artifacts and build files.")
    print("Make sure you have committed your work to Git!")

    response = input("\nContinue? (y/N): ").strip().lower()
    if response != "y":
        print("Cleanup cancelled.")
        return

    cleanup = DependencyCleanup()
    success = cleanup.run_cleanup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
