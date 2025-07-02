#!/usr/bin/env python3
"""
ACGS-1 Duplicate Requirements Cleanup Script

Removes duplicate requirements files based on FILE_ORGANIZATION_CLEANUP_PLAN.md
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Files to remove based on FILE_ORGANIZATION_CLEANUP_PLAN.md
DUPLICATE_REQUIREMENTS = [
    "services/core/constitutional-ai/ac_service/requirements_new.txt",
    "services/core/formal-verification/fv_service/requirements_base.txt",
    "services/core/governance-synthesis/gs_service/requirements_new.txt",
    "services/core/auth/auth_service/requirements_simple.txt",
]


def backup_file(file_path: Path, backup_dir: Path) -> bool:
    """Backup a file before removing it."""
    try:
        relative_path = file_path.relative_to(Path.cwd())
        backup_path = backup_dir / relative_path

        # Create directory structure
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file to backup
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up: {file_path} -> {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to backup {file_path}: {e}")
        return False


def main():
    """Main execution function."""
    # Create backup directory

    backup_dir = (
        Path("backups")
        / f"requirements_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    backup_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting duplicate requirements cleanup")
    logger.info(f"Backup directory: {backup_dir}")

    removed_count = 0
    for req_file in DUPLICATE_REQUIREMENTS:
        file_path = Path(req_file)
        if file_path.exists():
            # Backup file
            if backup_file(file_path, backup_dir):
                # Remove file
                file_path.unlink()
                removed_count += 1
                logger.info(f"Removed duplicate requirements file: {file_path}")
        else:
            logger.info(f"File not found (already cleaned): {file_path}")

    logger.info(
        f"Cleanup complete. Removed {removed_count} duplicate requirements files."
    )


if __name__ == "__main__":
    main()
