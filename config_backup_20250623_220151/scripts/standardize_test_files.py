#!/usr/bin/env python3
"""
ACGS-1 Test File Naming Standardization Script

Renames test files to follow the standard naming convention:
- Python: test_*.py (not *_test.py)
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    project_root = Path.cwd()
    logger.info(f"Starting test file naming standardization in {project_root}")

    # Find all test files with incorrect naming pattern (*_test.py)
    incorrect_test_files = list(project_root.glob("**/*_test.py"))
    logger.info(
        f"Found {len(incorrect_test_files)} test files with incorrect naming pattern"
    )

    renamed_count = 0
    for test_file in incorrect_test_files:
        # Get the base name without extension
        base_name = test_file.stem
        # Remove "_test" suffix
        module_name = base_name.replace("_test", "")
        # Create new name with "test_" prefix
        new_name = f"test_{module_name}.py"
        new_path = test_file.parent / new_name

        # Check if destination already exists
        if new_path.exists():
            logger.warning(
                f"Cannot rename {test_file} to {new_path}: destination already exists"
            )
            continue

        try:
            # Rename the file
            test_file.rename(new_path)
            logger.info(f"Renamed: {test_file} -> {new_path}")
            renamed_count += 1
        except Exception as e:
            logger.error(f"Failed to rename {test_file}: {e}")

    logger.info(f"Standardization complete. Renamed {renamed_count} test files.")


if __name__ == "__main__":
    main()
