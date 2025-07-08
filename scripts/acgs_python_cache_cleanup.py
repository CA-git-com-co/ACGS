#!/usr/bin/env python3
"""
ACGS Python Cache and Build Artifacts Cleanup
Constitutional Hash: cdd01ef066bc6cf2

Safely removes Python cache files, build artifacts, and temporary files
while preserving constitutional compliance and ACGS functionality.
"""

import logging
import shutil
from pathlib import Path

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# Python cache and build patterns to clean
PYTHON_CLEANUP_PATTERNS = [
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache/",
    ".mypy_cache/",
    ".coverage",
    "htmlcov/",
    ".tox/",
    "*.egg-info/",
    "build/",
    "dist/",
    ".cache/",
    "*.tmp",
    "*.temp",
]

# Directories to preserve (never clean)
PROTECTED_DIRECTORIES = {
    ".git",
    "services/core",
    "services/shared",
    "config",
    "infrastructure/monitoring",
    "docs",
}


class ACGSPythonCacheCleanup:
    """Handles safe cleanup of Python cache and build artifacts."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.cleanup_stats = {
            "files_removed": 0,
            "directories_removed": 0,
            "bytes_freed": 0,
            "errors": [],
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for cleanup operations."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    def _get_size(self, path: Path) -> int:
        """Get size of file or directory in bytes."""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            try:
                for item in path.rglob("*"):
                    if item.is_file():
                        total += item.stat().st_size
            except (PermissionError, OSError):
                pass
            return total
        return 0

    def _is_protected_path(self, path: Path) -> bool:
        """Check if path is in a protected directory."""
        try:
            relative_path = path.relative_to(REPO_ROOT)
            path_str = str(relative_path)

            for protected in PROTECTED_DIRECTORIES:
                if path_str.startswith(protected):
                    return True
            return False
        except ValueError:
            return True  # If not under repo root, protect it

    def clean_pycache_directories(self) -> list[str]:
        """Remove __pycache__ directories."""
        self.logger.info("🗑️ Cleaning __pycache__ directories...")
        removed_dirs = []

        for pycache_dir in REPO_ROOT.rglob("__pycache__"):
            if pycache_dir.is_dir() and not self._is_protected_path(pycache_dir):
                try:
                    size = self._get_size(pycache_dir)
                    shutil.rmtree(pycache_dir)
                    removed_dirs.append(str(pycache_dir.relative_to(REPO_ROOT)))
                    self.cleanup_stats["directories_removed"] += 1
                    self.cleanup_stats["bytes_freed"] += size
                    self.logger.info(
                        f"  ✅ Removed: {pycache_dir.relative_to(REPO_ROOT)}"
                    )
                except Exception as e:
                    error_msg = f"Failed to remove {pycache_dir}: {e}"
                    self.cleanup_stats["errors"].append(error_msg)
                    self.logger.error(f"  ❌ {error_msg}")

        return removed_dirs

    def clean_pytest_cache(self) -> list[str]:
        """Remove .pytest_cache directories."""
        self.logger.info("🗑️ Cleaning .pytest_cache directories...")
        removed_dirs = []

        for pytest_cache in REPO_ROOT.rglob(".pytest_cache"):
            if pytest_cache.is_dir() and not self._is_protected_path(pytest_cache):
                try:
                    size = self._get_size(pytest_cache)
                    shutil.rmtree(pytest_cache)
                    removed_dirs.append(str(pytest_cache.relative_to(REPO_ROOT)))
                    self.cleanup_stats["directories_removed"] += 1
                    self.cleanup_stats["bytes_freed"] += size
                    self.logger.info(
                        f"  ✅ Removed: {pytest_cache.relative_to(REPO_ROOT)}"
                    )
                except Exception as e:
                    error_msg = f"Failed to remove {pytest_cache}: {e}"
                    self.cleanup_stats["errors"].append(error_msg)
                    self.logger.error(f"  ❌ {error_msg}")

        return removed_dirs

    def clean_mypy_cache(self) -> list[str]:
        """Remove .mypy_cache directories."""
        self.logger.info("🗑️ Cleaning .mypy_cache directories...")
        removed_dirs = []

        for mypy_cache in REPO_ROOT.rglob(".mypy_cache"):
            if mypy_cache.is_dir() and not self._is_protected_path(mypy_cache):
                try:
                    size = self._get_size(mypy_cache)
                    shutil.rmtree(mypy_cache)
                    removed_dirs.append(str(mypy_cache.relative_to(REPO_ROOT)))
                    self.cleanup_stats["directories_removed"] += 1
                    self.cleanup_stats["bytes_freed"] += size
                    self.logger.info(
                        f"  ✅ Removed: {mypy_cache.relative_to(REPO_ROOT)}"
                    )
                except Exception as e:
                    error_msg = f"Failed to remove {mypy_cache}: {e}"
                    self.cleanup_stats["errors"].append(error_msg)
                    self.logger.error(f"  ❌ {error_msg}")

        return removed_dirs

    def clean_pyc_files(self) -> list[str]:
        """Remove .pyc, .pyo, .pyd files."""
        self.logger.info("🗑️ Cleaning Python compiled files...")
        removed_files = []

        extensions = [".pyc", ".pyo", ".pyd"]

        for ext in extensions:
            for pyc_file in REPO_ROOT.rglob(f"*{ext}"):
                if pyc_file.is_file() and not self._is_protected_path(pyc_file):
                    try:
                        size = pyc_file.stat().st_size
                        pyc_file.unlink()
                        removed_files.append(str(pyc_file.relative_to(REPO_ROOT)))
                        self.cleanup_stats["files_removed"] += 1
                        self.cleanup_stats["bytes_freed"] += size
                        self.logger.info(
                            f"  ✅ Removed: {pyc_file.relative_to(REPO_ROOT)}"
                        )
                    except Exception as e:
                        error_msg = f"Failed to remove {pyc_file}: {e}"
                        self.cleanup_stats["errors"].append(error_msg)
                        self.logger.error(f"  ❌ {error_msg}")

        return removed_files

    def clean_temp_files(self) -> list[str]:
        """Remove temporary files."""
        self.logger.info("🗑️ Cleaning temporary files...")
        removed_files = []

        temp_patterns = ["*.tmp", "*.temp", "*~", "*.swp", "*.swo"]

        for pattern in temp_patterns:
            for temp_file in REPO_ROOT.rglob(pattern):
                if temp_file.is_file() and not self._is_protected_path(temp_file):
                    try:
                        size = temp_file.stat().st_size
                        temp_file.unlink()
                        removed_files.append(str(temp_file.relative_to(REPO_ROOT)))
                        self.cleanup_stats["files_removed"] += 1
                        self.cleanup_stats["bytes_freed"] += size
                        self.logger.info(
                            f"  ✅ Removed: {temp_file.relative_to(REPO_ROOT)}"
                        )
                    except Exception as e:
                        error_msg = f"Failed to remove {temp_file}: {e}"
                        self.cleanup_stats["errors"].append(error_msg)
                        self.logger.error(f"  ❌ {error_msg}")

        return removed_files

    def clean_coverage_files(self) -> list[str]:
        """Remove coverage files and directories."""
        self.logger.info("🗑️ Cleaning coverage files...")
        removed_items = []

        # Remove .coverage files
        for coverage_file in REPO_ROOT.rglob(".coverage*"):
            if coverage_file.is_file() and not self._is_protected_path(coverage_file):
                try:
                    size = coverage_file.stat().st_size
                    coverage_file.unlink()
                    removed_items.append(str(coverage_file.relative_to(REPO_ROOT)))
                    self.cleanup_stats["files_removed"] += 1
                    self.cleanup_stats["bytes_freed"] += size
                    self.logger.info(
                        f"  ✅ Removed: {coverage_file.relative_to(REPO_ROOT)}"
                    )
                except Exception as e:
                    error_msg = f"Failed to remove {coverage_file}: {e}"
                    self.cleanup_stats["errors"].append(error_msg)
                    self.logger.error(f"  ❌ {error_msg}")

        # Remove htmlcov directories
        for htmlcov_dir in REPO_ROOT.rglob("htmlcov"):
            if htmlcov_dir.is_dir() and not self._is_protected_path(htmlcov_dir):
                try:
                    size = self._get_size(htmlcov_dir)
                    shutil.rmtree(htmlcov_dir)
                    removed_items.append(str(htmlcov_dir.relative_to(REPO_ROOT)))
                    self.cleanup_stats["directories_removed"] += 1
                    self.cleanup_stats["bytes_freed"] += size
                    self.logger.info(
                        f"  ✅ Removed: {htmlcov_dir.relative_to(REPO_ROOT)}"
                    )
                except Exception as e:
                    error_msg = f"Failed to remove {htmlcov_dir}: {e}"
                    self.cleanup_stats["errors"].append(error_msg)
                    self.logger.error(f"  ❌ {error_msg}")

        return removed_items

    def run_cleanup(self) -> dict:
        """Run complete Python cache cleanup."""
        self.logger.info("🧹 Starting ACGS Python Cache Cleanup...")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

        # Run all cleanup operations
        self.clean_pycache_directories()
        self.clean_pytest_cache()
        self.clean_mypy_cache()
        self.clean_pyc_files()
        self.clean_temp_files()
        self.clean_coverage_files()

        # Format bytes freed
        bytes_freed = self.cleanup_stats["bytes_freed"]
        if bytes_freed > 1024 * 1024:
            size_str = f"{bytes_freed / (1024 * 1024):.1f} MB"
        elif bytes_freed > 1024:
            size_str = f"{bytes_freed / 1024:.1f} KB"
        else:
            size_str = f"{bytes_freed} bytes"

        self.logger.info("📊 Cleanup Summary:")
        self.logger.info(f"  Files removed: {self.cleanup_stats['files_removed']}")
        self.logger.info(
            f"  Directories removed: {self.cleanup_stats['directories_removed']}"
        )
        self.logger.info(f"  Space freed: {size_str}")
        self.logger.info(f"  Errors: {len(self.cleanup_stats['errors'])}")

        if self.cleanup_stats["errors"]:
            self.logger.warning("⚠️ Errors encountered:")
            for error in self.cleanup_stats["errors"]:
                self.logger.warning(f"  - {error}")

        return self.cleanup_stats


def main():
    """Main cleanup function."""
    print("🧹 ACGS Python Cache and Build Artifacts Cleanup")
    print("=" * 55)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Repository: {REPO_ROOT}")
    print()

    cleaner = ACGSPythonCacheCleanup()
    results = cleaner.run_cleanup()

    print("\n✅ Python cache cleanup completed!")
    return results


if __name__ == "__main__":
    main()
