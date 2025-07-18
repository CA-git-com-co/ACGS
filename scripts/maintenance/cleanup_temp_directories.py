#!/usr/bin/env python3
"""
ACGS-1 Temporary Directories Cleanup Script

Cleans up temporary directories and files while preserving important backups.
"""

import glob
import logging
import shutil
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Patterns to clean up
CLEANUP_PATTERNS = [
    "__pycache__/",
    ".pytest_cache/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".mypy_cache/",
    ".coverage",
    "reports/coverage/htmlcov/",
    ".tox/",
    ".cache/",
    "*.egg-info/",
    "build/",
    "dist/",
    ".DS_Store",
    "Thumbs.db",
    "*.tmp",
    "*.temp",
    "*.swp",
    "*.swo",
    "*~",
    ".pytest_cache/",
    "ACGS-PGP_Framework/*.aux",
    "ACGS-PGP_Framework/*.bbl",
    "ACGS-PGP_Framework/*.blg",
    "ACGS-PGP_Framework/*.out",
    "AlphaEvolve-ACGS_Integration_System/*.aux",
    "AlphaEvolve-ACGS_Integration_System/*.log",
]

# Directories to preserve (don't delete these)
PRESERVE_PATTERNS = ["backups/acgs_simple_backup_*"]


def is_preserved(path: str) -> bool:
    """Check if a path should be preserved."""
    for pattern in PRESERVE_PATTERNS:
        if glob.fnmatch.fnmatch(path, pattern):
            return True
    return False


def main():
    """Main execution function."""
    project_root = Path.cwd()
    logger.info(f"Starting cleanup of temporary directories in {project_root}")

    removed_count = 0
    skipped_count = 0

    for pattern in CLEANUP_PATTERNS:
        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            dir_pattern = pattern.rstrip("/")
            for dir_path in project_root.glob(f"**/{dir_pattern}"):
                if dir_path.is_dir() and not is_preserved(str(dir_path)):
                    try:
                        shutil.rmtree(dir_path)
                        logger.info(f"Removed directory: {dir_path}")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove {dir_path}: {e}")
                        skipped_count += 1
        # Handle file patterns
        else:
            for file_path in project_root.glob(f"**/{pattern}"):
                if file_path.is_file() and not is_preserved(str(file_path)):
                    try:
                        file_path.unlink()
                        logger.info(f"Removed file: {file_path}")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove {file_path}: {e}")
                        skipped_count += 1

    logger.info(
        f"Cleanup complete. Removed {removed_count} items, skipped {skipped_count} items."
    )


if __name__ == "__main__":
    main()
