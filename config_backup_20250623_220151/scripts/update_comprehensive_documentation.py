#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Documentation Update Script

Updates all documentation files to reflect the new directory structure
and command patterns following the ACGS-1 reorganization.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Path mappings for documentation updates (old_path -> new_path)
PATH_MAPPINGS = {
    # Backend service mappings
    "src/backend/ac_service": "services/core/constitutional-ai/ac_service",
    "src/backend/auth_service": "services/core/auth/auth_service",
    "src/backend/fv_service": "services/core/formal-verification/fv_service",
    "src/backend/gs_service": "services/core/governance-synthesis/gs_service",
    "src/backend/integrity_service": "services/platform/integrity/integrity_service",
    "src/backend/pgc_service": "services/platform/pgc/pgc_service",
    "src/backend/ec_service": "services/core/evolutionary-computation/ec_service",
    "src/backend/shared": "services/shared",
    "src/backend/": "services/",
    # Frontend mappings
    "src/frontend/": "applications/legacy-frontend/",
    "frontend/": "applications/governance-dashboard/",
    # Blockchain mappings
    "quantumagi_core/": "blockchain/",
    "quantumagi-core/": "blockchain/",
    # Integration mappings
    "src/alphaevolve_gs_engine/": "integrations/alphaevolve-engine/",
    "alphaevolve_gs_engine/": "integrations/alphaevolve-engine/",
    # Infrastructure mappings
    "docker-compose.yml": "infrastructure/docker/docker-compose.yml",
    "k8s/": "infrastructure/kubernetes/",
    # Test mappings
    "tests/backend/": "tests/unit/services/",
    "tests/frontend/": "tests/unit/applications/",
}

# Command updates for documentation
COMMAND_UPDATES = {
    # Docker commands
    "docker-compose up": "docker-compose -f infrastructure/docker/docker-compose.yml up",
    "docker-compose down": "docker-compose -f infrastructure/docker/docker-compose.yml down",
    "docker-compose build": "docker-compose -f infrastructure/docker/docker-compose.yml build",
    # Service startup commands
    "cd src/backend/ac_service": "cd services/core/constitutional-ai/ac_service",
    "cd src/backend/auth_service": "cd services/core/auth/auth_service",
    "cd src/backend/fv_service": "cd services/core/formal-verification/fv_service",
    "cd src/backend/gs_service": "cd services/core/governance-synthesis/gs_service",
    "cd src/backend/integrity_service": "cd services/platform/integrity/integrity_service",
    "cd src/backend/pgc_service": "cd services/platform/pgc/pgc_service",
    "cd src/backend/ec_service": "cd services/core/evolutionary-computation/ec_service",
    # Blockchain commands
    "cd quantumagi_core": "cd blockchain",
    "cd quantumagi-core": "cd blockchain",
    # Frontend commands
    "cd src/frontend": "cd applications/legacy-frontend",
    "cd frontend": "cd applications/governance-dashboard",
    # Test commands
    "python -m pytest tests/backend/": "python -m pytest tests/unit/services/",
    "python -m pytest tests/frontend/": "python -m pytest tests/unit/applications/",
    # Build commands
    "./src/backend/": "./services/",
    "./quantumagi_core/": "./blockchain/",
    "./src/frontend/": "./applications/legacy-frontend/",
}


def update_documentation_file(file_path: Path) -> bool:
    """Update a single documentation file with new paths and commands."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Apply path mappings (most specific first)
        sorted_paths = sorted(
            PATH_MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True
        )
        for old_path, new_path in sorted_paths:
            content = content.replace(old_path, new_path)

        # Apply command updates
        for old_cmd, new_cmd in COMMAND_UPDATES.items():
            content = content.replace(old_cmd, new_cmd)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Updated documentation: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating {file_path}: {e}")
        return False


def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()

    logger.info(f"Starting documentation update for ACGS-1 project at {project_root}")

    # Find all documentation files
    doc_extensions = {".md", ".txt", ".rst"}
    doc_files = []

    for ext in doc_extensions:
        doc_files.extend(project_root.glob(f"**/*{ext}"))

    # Filter out files in backup directories
    doc_files = [f for f in doc_files if "backup" not in str(f)]

    logger.info(f"Found {len(doc_files)} documentation files to process")

    # Update each file
    updated_count = 0
    for doc_file in doc_files:
        if update_documentation_file(doc_file):
            updated_count += 1

    logger.info(f"Documentation update complete. Updated {updated_count} files.")

    # Generate report
    report_file = project_root / "DOCUMENTATION_UPDATE_REPORT.md"
    with open(report_file, "w") as f:
        f.write("# ACGS-1 Documentation Update Report\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Total documentation files: {len(doc_files)}\n")
        f.write(f"- Files updated: {updated_count}\n\n")
        f.write("## Updated Path References\n\n")
        for old_path, new_path in PATH_MAPPINGS.items():
            f.write(f"- `{old_path}` → `{new_path}`\n")

    logger.info(f"Report saved to: {report_file}")


if __name__ == "__main__":
    from datetime import datetime

    main()
