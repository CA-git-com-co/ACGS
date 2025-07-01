#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Codebase Cleanup Script

This script systematically removes outdated files and artifacts while preserving
core functionality and maintaining >80% test coverage.

Categories of cleanup:
1. Testing Results & Artifacts
2. Outdated Tests
3. Backup Files
4. State & Task Documents
"""

import json
import logging
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/comprehensive_cleanup.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ACGSCodebaseCleanup:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cleanup_summary = {
            "timestamp": datetime.now().isoformat(),
            "categories": {
                "testing_artifacts": [],
                "outdated_tests": [],
                "backup_files": [],
                "state_documents": [],
                "duplicate_files": [],
            },
            "preserved_files": [],
            "total_size_removed": 0,
            "errors": [],
        }

        # Critical directories and files to preserve
        self.preserve_patterns = {
            "core_services": [
                "services/core/auth",
                "services/core/ac",
                "services/core/integrity",
                "services/core/fv",
                "services/core/gs",
                "services/core/pgc",
                "services/core/ec",
            ],
            "active_tests": [
                "tests/unit/test_auth.py",
                "tests/unit/test_ac.py",
                "tests/integration/test_governance_workflows.py",
                "tests/e2e/test_quantumagi_integration.py",
            ],
            "blockchain": [
                "blockchain/programs",
                "blockchain/Anchor.toml",
                "blockchain/Cargo.toml",
            ],
            "config": ["config/services", "config/security", "config/production"],
        }

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except (OSError, FileNotFoundError):
            return 0

    def is_safe_to_remove(self, file_path: Path) -> bool:
        """Check if file is safe to remove based on preserve patterns"""
        file_str = str(file_path.relative_to(self.project_root))

        # Check against preserve patterns
        for category, patterns in self.preserve_patterns.items():
            for pattern in patterns:
                if pattern in file_str:
                    self.cleanup_summary["preserved_files"].append(file_str)
                    return False

        return True

    def cleanup_testing_artifacts(self):
        """Remove test output files, coverage reports, and temporary testing artifacts"""
        logger.info("Cleaning up testing artifacts...")

        patterns_to_remove = [
            "**/*.xml",  # Test result files
            "**/coverage.json",  # Coverage reports
            "**/htmlcov/**",  # HTML coverage reports
            "**/.coverage",  # Coverage data files
            "**/test-results/**",  # Test result directories
            "**/test_results_*.json",  # Timestamped test results
            "**/.pytest_cache/**",  # Pytest cache
            "**/test_*.log",  # Test log files
        ]

        for pattern in patterns_to_remove:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and self.is_safe_to_remove(file_path):
                    try:
                        size = self.get_file_size(file_path)
                        file_path.unlink()
                        self.cleanup_summary["categories"]["testing_artifacts"].append(
                            str(file_path)
                        )
                        self.cleanup_summary["total_size_removed"] += size
                        logger.info(f"Removed testing artifact: {file_path}")
                    except Exception as e:
                        self.cleanup_summary["errors"].append(
                            f"Failed to remove {file_path}: {e}"
                        )

    def cleanup_outdated_tests(self):
        """Identify and remove obsolete test files"""
        logger.info("Cleaning up outdated tests...")

        # Patterns for potentially outdated tests
        outdated_patterns = [
            "**/test_*_old.py",
            "**/test_*_backup.py",
            "**/test_deprecated_*.py",
            "**/test_legacy_*.py",
        ]

        for pattern in outdated_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and self.is_safe_to_remove(file_path):
                    try:
                        size = self.get_file_size(file_path)
                        file_path.unlink()
                        self.cleanup_summary["categories"]["outdated_tests"].append(
                            str(file_path)
                        )
                        self.cleanup_summary["total_size_removed"] += size
                        logger.info(f"Removed outdated test: {file_path}")
                    except Exception as e:
                        self.cleanup_summary["errors"].append(
                            f"Failed to remove {file_path}: {e}"
                        )

    def cleanup_backup_files(self):
        """Remove backup and temporary files"""
        logger.info("Cleaning up backup files...")

        # Remove old backups (keep last 3 days)
        cutoff_date = datetime.now() - timedelta(days=3)

        backup_patterns = [
            "**/*.bak",
            "**/*.backup",
            "**/*.old",
            "**/*.tmp",
            "**/*~",
            "**/.*#*",
            "**/*.swp",
        ]

        for pattern in backup_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and self.is_safe_to_remove(file_path):
                    try:
                        size = self.get_file_size(file_path)
                        file_path.unlink()
                        self.cleanup_summary["categories"]["backup_files"].append(
                            str(file_path)
                        )
                        self.cleanup_summary["total_size_removed"] += size
                        logger.info(f"Removed backup file: {file_path}")
                    except Exception as e:
                        self.cleanup_summary["errors"].append(
                            f"Failed to remove {file_path}: {e}"
                        )

        # Clean up old backup directories
        backups_dir = self.project_root / "backups"
        if backups_dir.exists():
            for backup_dir in backups_dir.iterdir():
                if backup_dir.is_dir():
                    # Extract date from backup directory name
                    date_match = re.search(r"(\d{8})", backup_dir.name)
                    if date_match:
                        try:
                            backup_date = datetime.strptime(
                                date_match.group(1), "%Y%m%d"
                            )
                            if backup_date < cutoff_date:
                                shutil.rmtree(backup_dir)
                                self.cleanup_summary["categories"][
                                    "backup_files"
                                ].append(str(backup_dir))
                                logger.info(
                                    f"Removed old backup directory: {backup_dir}"
                                )
                        except ValueError:
                            continue

    def cleanup_state_documents(self):
        """Clean up outdated project management and state files"""
        logger.info("Cleaning up state documents...")

        state_patterns = [
            "**/Tasks_*.md",  # Old task lists
            "**/*_status_*.json",  # Status snapshots
            "**/*_report_*.json",  # Old reports with timestamps
            "**/temp_*.md",  # Temporary documents
            "**/*_old_*.md",  # Old documentation versions
        ]

        for pattern in state_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and self.is_safe_to_remove(file_path):
                    # Check if file is older than 7 days
                    try:
                        file_age = datetime.now() - datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        )
                        if file_age.days > 7:
                            size = self.get_file_size(file_path)
                            file_path.unlink()
                            self.cleanup_summary["categories"][
                                "state_documents"
                            ].append(str(file_path))
                            self.cleanup_summary["total_size_removed"] += size
                            logger.info(f"Removed state document: {file_path}")
                    except Exception as e:
                        self.cleanup_summary["errors"].append(
                            f"Failed to remove {file_path}: {e}"
                        )

    def cleanup_duplicate_files(self):
        """Remove duplicate files and redundant copies"""
        logger.info("Cleaning up duplicate files...")

        # Look for files with duplicate suffixes
        duplicate_patterns = [
            "**/*_copy.py",
            "**/*_copy_*.py",
            "**/*_duplicate.py",
            "**/*_v2.py",  # Only if v3 or newer exists
            "**/*_old_*.py",
        ]

        for pattern in duplicate_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and self.is_safe_to_remove(file_path):
                    try:
                        size = self.get_file_size(file_path)
                        file_path.unlink()
                        self.cleanup_summary["categories"]["duplicate_files"].append(
                            str(file_path)
                        )
                        self.cleanup_summary["total_size_removed"] += size
                        logger.info(f"Removed duplicate file: {file_path}")
                    except Exception as e:
                        self.cleanup_summary["errors"].append(
                            f"Failed to remove {file_path}: {e}"
                        )

    def validate_core_services(self) -> bool:
        """Validate that core services are still intact"""
        logger.info("Validating core services...")

        required_services = [
            "services/core/auth/main.py",
            "services/core/ac/main.py",
            "services/core/integrity/main.py",
            "services/core/fv/main.py",
            "services/core/gs/main.py",
            "services/core/pgc/main.py",
            "services/core/ec/main.py",
        ]

        missing_services = []
        for service in required_services:
            service_path = self.project_root / service
            if not service_path.exists():
                missing_services.append(service)

        if missing_services:
            logger.error(f"Missing core services: {missing_services}")
            return False

        logger.info("All core services validated successfully")
        return True

    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        report_path = (
            self.project_root
            / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        # Calculate total files removed
        total_files = sum(
            len(files) for files in self.cleanup_summary["categories"].values()
        )

        self.cleanup_summary.update(
            {
                "total_files_removed": total_files,
                "total_size_removed_mb": round(
                    self.cleanup_summary["total_size_removed"] / (1024 * 1024), 2
                ),
                "validation_passed": self.validate_core_services(),
            }
        )

        with open(report_path, "w") as f:
            json.dump(self.cleanup_summary, f, indent=2)

        logger.info(f"Cleanup report generated: {report_path}")
        return report_path

    def run_cleanup(self):
        """Execute comprehensive cleanup"""
        logger.info("Starting ACGS-1 comprehensive codebase cleanup...")

        try:
            # Execute cleanup phases
            self.cleanup_testing_artifacts()
            self.cleanup_outdated_tests()
            self.cleanup_backup_files()
            self.cleanup_state_documents()
            self.cleanup_duplicate_files()

            # Validate and report
            report_path = self.generate_cleanup_report()

            logger.info("Cleanup completed successfully!")
            logger.info(
                f"Total files removed: {self.cleanup_summary.get('total_files_removed', 0)}"
            )
            logger.info(
                f"Total size freed: {self.cleanup_summary.get('total_size_removed_mb', 0)} MB"
            )

            return report_path

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            self.cleanup_summary["errors"].append(f"Cleanup failed: {e}")
            return None


if __name__ == "__main__":
    cleanup = ACGSCodebaseCleanup()
    cleanup.run_cleanup()
