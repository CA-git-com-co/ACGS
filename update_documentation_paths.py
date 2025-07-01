#!/usr/bin/env python3
"""
ACGS-1 Documentation Path Update Script
======================================

This script finds and updates path references in documentation and configuration 
files to reflect the new directory structure after reorganization.

Key Features:
1. Scan documentation files for outdated path references
2. Update configuration files with new paths
3. Fix import statements and file references
4. Generate a report of all changes made
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("documentation_update.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DocumentationPathUpdater:
    """Updates path references in documentation and configuration files."""

    def __init__(self, project_root: str = "/home/ubuntu/ACGS"):
        self.project_root = Path(project_root)
        self.changes_made = []
        self.files_processed = 0
        self.errors_encountered = []

        # Path mappings for the reorganization
        self.path_mappings = {
            # Old paths -> New paths
            "scripts/maintenance/": "scripts/maintenance/",
            "docs/reports/": "docs/reports/",
            "docs/architecture/": "docs/architecture/",
            "services/core/constitutional-ai/": "services/core/constitutional-ai/",
            "services/core/formal-verification/": "services/core/formal-verification/",
            "services/core/governance-synthesis/": "services/core/governance-synthesis/",
            "services/core/policy-governance/": "services/core/policy-governance/",
            "services/core/evolutionary-computation/": "services/core/evolutionary-computation/",
            "services/platform/authentication/": "services/platform/authentication/",
            "services/platform/integrity/": "services/platform/integrity/",
            "config/environments/production.env": "config/environments/production.env",
            "config/environments/staging.env": "config/environments/staging.env",
            "config/environments/development.env": "config/environments/development.env",
        }

        # File patterns to scan
        self.file_patterns = [
            "*.md",
            "*.rst",
            "*.txt",  # Documentation
            "*.yml",
            "*.yaml",
            "*.json",
            "*.toml",
            "*.ini",  # Configuration
            "*.py",
            "*.js",
            "*.ts",  # Code files with potential path references
            "*.sh",
            "*.bat",  # Scripts
            "Dockerfile*",
            "docker-compose*",  # Docker files
            "README*",
            "CHANGELOG*",
            "CONTRIBUTING*",  # Project files
        ]

    def scan_and_update_all(self):
        """Scan and update all relevant files."""
        logger.info("🔍 Starting documentation path update scan...")
        logger.info("=" * 60)

        # Get all files to process
        files_to_process = self._get_files_to_process()
        logger.info(f"Found {len(files_to_process)} files to process")

        # Process each file
        for file_path in files_to_process:
            try:
                self._process_file(file_path)
                self.files_processed += 1
            except Exception as e:
                error_msg = f"Error processing {file_path}: {e}"
                self.errors_encountered.append(error_msg)
                logger.error(error_msg)

        # Generate report
        report = self._generate_report()
        return report

    def _get_files_to_process(self) -> List[Path]:
        """Get list of files that need to be processed."""
        files_to_process = []

        # Scan specific directories
        scan_dirs = [
            "docs",
            "config",
            "scripts",
            "services",
            "blockchain",
            "infrastructure",
        ]

        for dir_name in scan_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                files_to_process.extend(self._scan_directory(dir_path))

        # Also scan root level files
        for pattern in self.file_patterns:
            files_to_process.extend(self.project_root.glob(pattern))

        # Remove duplicates and filter out binary files
        unique_files = list(set(files_to_process))
        return [f for f in unique_files if self._is_text_file(f)]

    def _scan_directory(self, directory: Path) -> List[Path]:
        """Recursively scan directory for files matching patterns."""
        files = []
        for pattern in self.file_patterns:
            files.extend(directory.rglob(pattern))
        return files

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file that can be processed."""
        try:
            # Skip if file is too large (>10MB)
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False

            # Try to read first few bytes to check if it's text
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                if b"\x00" in chunk:  # Binary file indicator
                    return False

            return True
        except Exception:
            return False

    def _process_file(self, file_path: Path):
        """Process a single file for path updates."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
                return

        original_content = content
        changes_in_file = []

        # Apply path mappings
        for old_path, new_path in self.path_mappings.items():
            if old_path in content:
                # Count occurrences
                occurrences = content.count(old_path)
                content = content.replace(old_path, new_path)
                changes_in_file.append(
                    {
                        "old_path": old_path,
                        "new_path": new_path,
                        "occurrences": occurrences,
                    }
                )

        # Look for other potential path issues
        changes_in_file.extend(self._fix_common_path_issues(content, file_path))

        # Write back if changes were made
        if content != original_content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.changes_made.append(
                    {
                        "file": str(file_path.relative_to(self.project_root)),
                        "changes": changes_in_file,
                    }
                )

                logger.info(
                    f"✅ Updated {file_path.relative_to(self.project_root)} ({len(changes_in_file)} changes)"
                )

            except Exception as e:
                logger.error(f"Failed to write {file_path}: {e}")

    def _fix_common_path_issues(self, content: str, file_path: Path) -> List[Dict]:
        """Fix common path issues beyond simple mappings."""
        changes = []

        # Fix hardcoded paths like /home/dislove/ACGS-1/
        hardcoded_pattern = r"/home/dislove/ACGS-1/"
        if hardcoded_pattern in content:
            occurrences = len(re.findall(hardcoded_pattern, content))
            content = re.sub(hardcoded_pattern, "/home/ubuntu/ACGS/", content)
            changes.append(
                {
                    "old_path": hardcoded_pattern,
                    "new_path": "/home/ubuntu/ACGS/",
                    "occurrences": occurrences,
                    "type": "hardcoded_path_fix",
                }
            )

        # Fix relative import paths in Python files
        if file_path.suffix == ".py":
            # Look for sys.path.append patterns
            sys_path_pattern = r'sys\.path\.append\(["\']([^"\']+)["\']\)'
            matches = re.findall(sys_path_pattern, content)
            for match in matches:
                if "services/shared" in match:
                    old_pattern = f'sys.path.append("{match}")'
                    new_pattern = 'sys.path.append("/home/ubuntu/ACGS/services/shared")'
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        changes.append(
                            {
                                "old_path": old_pattern,
                                "new_path": new_pattern,
                                "occurrences": 1,
                                "type": "sys_path_fix",
                            }
                        )

        # Fix Docker volume mounts
        if "docker" in file_path.name.lower() or file_path.suffix in [".yml", ".yaml"]:
            docker_pattern = r"(/home/dislove/ACGS-1[^:\s]*)"
            matches = re.findall(docker_pattern, content)
            for match in matches:
                new_path = match.replace("/home/dislove/ACGS-1", "/home/ubuntu/ACGS")
                content = content.replace(match, new_path)
                changes.append(
                    {
                        "old_path": match,
                        "new_path": new_path,
                        "occurrences": 1,
                        "type": "docker_path_fix",
                    }
                )

        return changes

    def _generate_report(self) -> Dict:
        """Generate a comprehensive report of all changes made."""
        total_changes = sum(
            len(file_changes["changes"]) for file_changes in self.changes_made
        )

        report = {
            "timestamp": "2025-06-24T00:40:00Z",
            "summary": {
                "files_processed": self.files_processed,
                "files_modified": len(self.changes_made),
                "total_changes": total_changes,
                "errors_encountered": len(self.errors_encountered),
            },
            "path_mappings_applied": self.path_mappings,
            "files_modified": self.changes_made,
            "errors": self.errors_encountered,
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on the update process."""
        recommendations = []

        if self.errors_encountered:
            recommendations.append(
                f"Review {len(self.errors_encountered)} files that could not be processed"
            )

        if len(self.changes_made) > 0:
            recommendations.append(
                "Test all modified files to ensure functionality is preserved"
            )
            recommendations.append(
                "Update any remaining hardcoded paths found during testing"
            )

        recommendations.extend(
            [
                "Update IDE/editor configurations to use new paths",
                "Update CI/CD pipeline configurations if they reference old paths",
                "Update deployment scripts and documentation",
                "Verify all service imports and dependencies work correctly",
            ]
        )

        return recommendations


def main():
    """Main execution function."""
    updater = DocumentationPathUpdater()

    try:
        # Run the update process
        report = updater.scan_and_update_all()

        # Save report
        with open("documentation_update_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 DOCUMENTATION UPDATE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Files Processed: {report['summary']['files_processed']}")
        logger.info(f"Files Modified: {report['summary']['files_modified']}")
        logger.info(f"Total Changes: {report['summary']['total_changes']}")
        logger.info(f"Errors: {report['summary']['errors_encountered']}")

        if report["recommendations"]:
            logger.info("\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"], 1):
                logger.info(f"{i}. {rec}")

        logger.info(f"\n📄 Detailed report saved to: documentation_update_report.json")

        # Exit with appropriate code
        if report["summary"]["errors_encountered"] == 0:
            logger.info("✅ Documentation update completed successfully!")
            return 0
        else:
            logger.warning("⚠️ Documentation update completed with some errors")
            return 1

    except Exception as e:
        logger.error(f"Documentation update failed: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
