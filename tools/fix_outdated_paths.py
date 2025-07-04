#!/usr/bin/env python3
"""
Fix Outdated Path References in ACGS-1 Scripts
Updates all scripts that still reference old services/ paths to use new services/ paths
"""

import logging
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PathUpdater:
    def __init__(self, project_root: str = "/mnt/persist/workspace"):
        self.project_root = Path(project_root)
        self.path_mappings = {
            "services/core/constitutional-ai/ac_service": "services/core/constitutional-ai/ac_service",
            "services/core/governance-synthesis/gs_service": "services/core/governance-synthesis/gs_service",
            "services/core/policy-governance/pgc_service": "services/core/policy-governance/pgc_service",
            "services/core/formal-verification/fv_service": "services/core/formal-verification/fv_service",
            "services/platform/authentication/auth_service": "services/platform/authentication/auth_service",
            "services/platform/integrity/integrity_service": "services/platform/integrity/integrity_service",
            "services/shared": "services/shared",
            "services": "services",
            "applications/legacy-frontend": "applications/legacy-frontend",
            "integrations/alphaevolve-engine": "integrations/alphaevolve-engine",
        }

    def find_files_with_old_paths(self) -> list[Path]:
        """Find all files that contain old path references."""
        logger.info("Scanning for files with outdated path references...")

        files_to_update = []

        # Scan shell scripts
        for script_file in self.project_root.glob("scripts/**/*.sh"):
            if self.file_contains_old_paths(script_file):
                files_to_update.append(script_file)

        # Scan Python scripts
        for script_file in self.project_root.glob("scripts/**/*.py"):
            if self.file_contains_old_paths(script_file):
                files_to_update.append(script_file)

        # Scan Docker files
        for docker_file in self.project_root.glob("**/Dockerfile*"):
            if self.file_contains_old_paths(docker_file):
                files_to_update.append(docker_file)

        # Scan docker-compose files
        for compose_file in self.project_root.glob("**/docker-compose*.yml"):
            if self.file_contains_old_paths(compose_file):
                files_to_update.append(compose_file)

        logger.info(f"Found {len(files_to_update)} files with outdated paths")
        return files_to_update

    def file_contains_old_paths(self, file_path: Path) -> bool:
        """Check if a file contains any old path references."""
        try:
            content = file_path.read_text(encoding="utf-8")
            for old_path in self.path_mappings.keys():
                if old_path in content:
                    return True
            return False
        except (UnicodeDecodeError, PermissionError):
            return False

    def update_file_paths(self, file_path: Path) -> tuple[bool, int]:
        """Update old paths in a single file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            replacements_made = 0

            # Apply path mappings in order (most specific first)
            sorted_mappings = sorted(
                self.path_mappings.items(), key=lambda x: len(x[0]), reverse=True
            )

            for old_path, new_path in sorted_mappings:
                if old_path in content:
                    # Count occurrences before replacement
                    count = content.count(old_path)
                    content = content.replace(old_path, new_path)
                    replacements_made += count
                    logger.info(
                        f"  Replaced {count} occurrences of '{old_path}' with '{new_path}'"
                    )

            if content != original_content:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                backup_path.write_text(original_content, encoding="utf-8")

                # Write updated content
                file_path.write_text(content, encoding="utf-8")
                logger.info(
                    f"✅ Updated {file_path} ({replacements_made} replacements)"
                )
                return True, replacements_made
            return False, 0

        except Exception as e:
            logger.error(f"❌ Failed to update {file_path}: {e}")
            return False, 0

    def update_all_files(self) -> dict[str, int]:
        """Update all files with outdated path references."""
        logger.info("Starting path update process...")

        files_to_update = self.find_files_with_old_paths()

        results = {"files_updated": 0, "total_replacements": 0, "files_failed": 0}

        for file_path in files_to_update:
            logger.info(f"Updating {file_path}...")
            success, replacements = self.update_file_paths(file_path)

            if success:
                results["files_updated"] += 1
                results["total_replacements"] += replacements
            else:
                results["files_failed"] += 1

        return results

    def validate_updates(self) -> bool:
        """Validate that no old paths remain."""
        logger.info("Validating path updates...")

        remaining_files = self.find_files_with_old_paths()

        if remaining_files:
            logger.warning(f"❌ {len(remaining_files)} files still contain old paths:")
            for file_path in remaining_files:
                logger.warning(f"  - {file_path}")
            return False
        logger.info("✅ All old paths have been successfully updated")
        return True


def main():
    """Main execution function."""
    updater = PathUpdater()

    # Update all files
    results = updater.update_all_files()

    # Print summary
    logger.info("=" * 50)
    logger.info("PATH UPDATE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Files updated: {results['files_updated']}")
    logger.info(f"Total replacements: {results['total_replacements']}")
    logger.info(f"Files failed: {results['files_failed']}")

    # Validate updates
    if updater.validate_updates():
        logger.info("✅ Path update process completed successfully!")
        return 0
    logger.error("❌ Some files still contain old paths")
    return 1


if __name__ == "__main__":
    exit(main())
