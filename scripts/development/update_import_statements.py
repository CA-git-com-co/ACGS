#!/usr/bin/env python3
"""
ACGS-1 Import Statement Update Script

Updates import statements to reflect the new directory structure
and resolves circular dependencies.
"""

import logging
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Path mappings for imports
IMPORT_MAPPINGS = {
    "from services.core.": "from services.core.",
    "from services.core.constitutional-ai.ac_service": "from services.core.constitutional-ai.ac_service",
    "from services.core.auth.auth_service": "from services.core.auth.auth_service",
    "from services.core.formal-verification.fv_service": "from services.core.formal-verification.fv_service",
    "from services.core.governance-synthesis.gs_service": "from services.core.governance-synthesis.gs_service",
    "from services.platform.integrity.integrity_service": "from services.platform.integrity.integrity_service",
    "from services.platform.pgc.pgc_service": "from services.platform.pgc.pgc_service",
    "from services.core.evolutionary-computation.ec_service": "from services.core.evolutionary-computation.ec_service",
}


def update_imports_in_file(file_path: Path) -> tuple[bool, int]:
    """Update import statements in a Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        updated_count = 0

        # Update import statements
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                updated_count += 1

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True, updated_count
        return False, 0
    except Exception as e:
        logger.error(f"Error updating imports in {file_path}: {e}")
        return False, 0


def main():
    """Main execution function."""
    project_root = Path.cwd()
    logger.info(f"Starting import statement updates in {project_root}")

    # Find all Python files
    python_files = list(project_root.glob("**/*.py"))
    # Filter out files in backup directories
    python_files = [f for f in python_files if "backup" not in str(f)]

    logger.info(f"Found {len(python_files)} Python files to process")

    updated_files = 0
    total_updates = 0

    for py_file in python_files:
        was_updated, update_count = update_imports_in_file(py_file)
        if was_updated:
            updated_files += 1
            total_updates += update_count
            logger.info(f"Updated imports in: {py_file} ({update_count} changes)")

    logger.info(
        f"Import update complete. Updated {updated_files} files with {total_updates} total changes."
    )


if __name__ == "__main__":
    main()
