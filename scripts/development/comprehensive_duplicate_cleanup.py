#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Duplicate and Outdated File Cleanup

This script systematically identifies and removes:
1. Duplicate timestamped files (health reports, test results, etc.)
2. Outdated backup directories (older than 30 days)
3. Redundant configuration files
4. Temporary build artifacts
5. Multiple docker-compose variations
6. Old log files and reports

PRESERVATION REQUIREMENTS:
- Quantumagi Solana deployment files
- Constitutional governance files (hash: cdd01ef066bc6cf2)
- All 7 core services and dependencies
- Current configuration files
- Recent backups (within 30 days)
"""

import hashlib
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


class ComprehensiveDuplicateCleanup:
    """Comprehensive cleanup tool for ACGS-1 project"""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "duplicates_removed": [],
            "outdated_files_removed": [],
            "backup_files_cleaned": [],
            "temp_files_removed": [],
            "docker_compose_consolidated": [],
            "total_space_saved_mb": 0,
            "files_preserved": [],
            "errors": [],
        }

        # Critical files to preserve
        self.preserve_patterns = [
            "blockchain/",
            "services/core/",
            "services/platform/",
            "applications/",
            "integrations/",
            "infrastructure/",
            "config/",
            "migrations/",
            "requirements*.txt",
            "package*.json",
            "Cargo.toml",
            "config/environments/pyproject.toml",
            "docker-compose.prod.yml",  # Keep production compose
            "docker-compose.acgs.yml",  # Keep main ACGS compose
            "README.md",
            "LICENSE",
            "SECURITY.md",
            "CHANGELOG.md",
            "constitution_data.json",
            "devnet_program_ids.json",
            "governance_accounts.json",
        ]

        # Patterns for files safe to remove
        self.cleanup_patterns = {
            "timestamped_health_reports": r"acgs_health_report_\d+\.json",
            "timestamped_test_results": r".*_test_results_\d+\.json",
            "timestamped_service_restart": r"service_restart_results_\d+\.json",
            "old_security_scans": r"security_scan_\d{8}_\d{6}_.*\.json",
            "phase3_validation_old": r"phase3_24point_validation_\d+\.json",
            "old_final_validation": r"final_validation_\d{8}_\d{6}\.json",
            "old_constitutional_reports": r"constitutional_security_report_\d+\.json",
            "temp_logs": r".*\.log$",
            "build_artifacts": [
                "__pycache__/",
                "*.pyc",
                "*.pyo",
                ".pytest_cache/",
                "node_modules/",
                "target/debug/",
                ".coverage",
                "reports/coverage/htmlcov/",
            ],
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return "error"

    def is_preserved_file(self, file_path: Path) -> bool:
        """Check if file should be preserved"""
        file_str = str(file_path.relative_to(self.project_root))

        for pattern in self.preserve_patterns:
            if pattern in file_str:
                return True

        # Preserve recent files (within 7 days)
        try:
            if (
                file_path.stat().st_mtime
                > (datetime.now() - timedelta(days=7)).timestamp()
            ):
                if any(
                    keyword in file_str
                    for keyword in ["constitution", "quantumagi", "devnet"]
                ):
                    return True
        except:
            pass

        return False

    def find_timestamped_duplicates(self) -> list[tuple[str, list[Path]]]:
        """Find timestamped duplicate files"""
        duplicates = []

        for pattern_name, pattern in self.cleanup_patterns.items():
            if pattern_name.startswith("timestamped") or pattern_name.startswith("old"):
                matching_files = []

                # Search in root directory
                for file_path in self.project_root.glob("*"):
                    if file_path.is_file() and re.match(pattern, file_path.name):
                        matching_files.append(file_path)

                # Search in logs and reports directories
                for subdir in ["logs", "reports", "root_reports"]:
                    subdir_path = self.project_root / subdir
                    if subdir_path.exists():
                        for file_path in subdir_path.glob("*"):
                            if file_path.is_file() and re.match(
                                pattern, file_path.name
                            ):
                                matching_files.append(file_path)

                if len(matching_files) > 1:
                    # Sort by modification time, keep the newest
                    matching_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    duplicates.append(
                        (pattern_name, matching_files[1:])
                    )  # Remove all but newest

        return duplicates

    def find_old_backups(self) -> list[Path]:
        """Find backup directories older than 30 days"""
        old_backups = []
        backup_dir = self.project_root / "backups"

        if backup_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=30)

            for backup_path in backup_dir.iterdir():
                if backup_path.is_dir():
                    try:
                        # Check if backup is older than 30 days
                        backup_time = datetime.fromtimestamp(
                            backup_path.stat().st_mtime
                        )
                        if backup_time < cutoff_date:
                            old_backups.append(backup_path)
                    except Exception as e:
                        logger.warning(
                            f"Could not check backup date for {backup_path}: {e}"
                        )

        return old_backups

    def find_redundant_docker_compose(self) -> list[Path]:
        """Find redundant docker-compose files"""
        redundant_files = []

        # Keep only production and main ACGS compose files
        keep_files = {"docker-compose.prod.yml", "docker-compose.acgs.yml"}

        for file_path in self.project_root.glob("docker-compose*.yml"):
            if file_path.name not in keep_files:
                redundant_files.append(file_path)

        return redundant_files

    def cleanup_build_artifacts(self) -> list[Path]:
        """Remove build artifacts and temporary files"""
        removed_files = []

        for pattern in self.cleanup_patterns["build_artifacts"]:
            if pattern.endswith("/"):
                # Directory pattern
                for dir_path in self.project_root.rglob(pattern.rstrip("/")):
                    if dir_path.is_dir() and not self.is_preserved_file(dir_path):
                        try:
                            shutil.rmtree(dir_path)
                            removed_files.append(dir_path)
                            logger.info(f"Removed build artifact directory: {dir_path}")
                        except Exception as e:
                            logger.error(f"Failed to remove {dir_path}: {e}")
            else:
                # File pattern
                for file_path in self.project_root.rglob(pattern):
                    if file_path.is_file() and not self.is_preserved_file(file_path):
                        try:
                            file_path.unlink()
                            removed_files.append(file_path)
                            logger.info(f"Removed build artifact: {file_path}")
                        except Exception as e:
                            logger.error(f"Failed to remove {file_path}: {e}")

        return removed_files

    def cleanup_specific_root_files(self) -> list[Path]:
        """Remove specific files identified in root directory"""
        removed_files = []

        # Specific files to remove from root
        root_files_to_remove = [
            "acgs_health_report_1750361353.json",
            "acgs_health_report_1750361567.json",
            "acgs_health_report_1750361653.json",
            "governance_workflows_test_results_1750347130.json",
            "service_restart_results_1750336553.json",
            "service_restart_results_1750336722.json",
            "root_cleanup_report_20250618_100428.json",
            "root_directory_analysis_20250618_100240.json",
            "cryptographic_upgrade.log",
            "cryptographic_upgrade_report.json",
            "security_middleware_deployment.log",
            "security_middleware_deployment_report.json",
            "comprehensive_root_cleanup.py",  # Old cleanup script
            "bfg.jar",  # Git BFG tool, not needed in repo
        ]

        # Remove temp directories
        temp_dirs_to_remove = [
            "temp_cleanup",
            "coverage_demo_html",
            "dgm_output",
            "security_scans",
            "__pycache__",
        ]

        for filename in root_files_to_remove:
            file_path = self.project_root / filename
            if file_path.exists() and file_path.is_file():
                try:
                    file_path.unlink()
                    removed_files.append(file_path)
                    logger.info(f"Removed root file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}: {e}")

        for dirname in temp_dirs_to_remove:
            dir_path = self.project_root / dirname
            if dir_path.exists() and dir_path.is_dir():
                try:
                    shutil.rmtree(dir_path)
                    removed_files.append(dir_path)
                    logger.info(f"Removed temp directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {dir_path}: {e}")

        return removed_files

    def consolidate_logs_directory(self) -> list[Path]:
        """Clean up and organize logs directory"""
        removed_files = []
        logs_dir = self.project_root / "logs"

        if not logs_dir.exists():
            return removed_files

        # Remove old security scan files (keep only latest)
        security_scan_files = {}
        for file_path in logs_dir.glob("security_scan_*"):
            # Extract date from filename
            match = re.search(r"security_scan_(\d{8})_(\d{6})_", file_path.name)
            if match:
                date_str = match.group(1)
                scan_type = file_path.name.split("_")[
                    -1
                ]  # Get the scan type (bandit.json, etc.)

                if scan_type not in security_scan_files:
                    security_scan_files[scan_type] = []
                security_scan_files[scan_type].append((date_str, file_path))

        # Keep only the latest scan for each type
        for scan_type, files in security_scan_files.items():
            if len(files) > 1:
                files.sort(
                    key=lambda x: x[0], reverse=True
                )  # Sort by date, newest first
                for _, file_path in files[1:]:  # Remove all but the newest
                    try:
                        file_path.unlink()
                        removed_files.append(file_path)
                        logger.info(f"Removed old security scan: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove {file_path}: {e}")

        # Remove old phase3 validation files (keep only latest)
        phase3_files = list(logs_dir.glob("phase3_24point_validation_*.json"))
        if len(phase3_files) > 1:
            phase3_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for file_path in phase3_files[1:]:  # Keep only the newest
                try:
                    file_path.unlink()
                    removed_files.append(file_path)
                    logger.info(f"Removed old phase3 validation: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}: {e}")

        return removed_files

    def create_backup(self) -> Path:
        """Create backup before cleanup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / "backups" / f"cleanup_backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created cleanup backup directory: {backup_dir}")
        return backup_dir

    def execute_cleanup(self) -> dict:
        """Execute the comprehensive cleanup"""
        logger.info("Starting comprehensive duplicate and outdated file cleanup")

        # Create backup
        backup_dir = self.create_backup()

        total_space_saved = 0

        try:
            # 1. Remove timestamped duplicates
            logger.info("Removing timestamped duplicate files...")
            duplicates = self.find_timestamped_duplicates()

            for pattern_name, duplicate_files in duplicates:
                for file_path in duplicate_files:
                    if not self.is_preserved_file(file_path):
                        try:
                            file_size = file_path.stat().st_size
                            # Backup file before removal
                            backup_file = backup_dir / file_path.name
                            shutil.copy2(file_path, backup_file)

                            file_path.unlink()
                            total_space_saved += file_size

                            self.cleanup_report["duplicates_removed"].append(
                                {
                                    "file": str(file_path),
                                    "pattern": pattern_name,
                                    "size_mb": round(file_size / (1024 * 1024), 2),
                                }
                            )
                            logger.info(f"Removed duplicate: {file_path}")
                        except Exception as e:
                            error_msg = f"Failed to remove duplicate {file_path}: {e}"
                            logger.error(error_msg)
                            self.cleanup_report["errors"].append(error_msg)

            # 2. Remove old backups
            logger.info("Removing old backup directories...")
            old_backups = self.find_old_backups()

            for backup_path in old_backups:
                try:
                    backup_size = sum(
                        f.stat().st_size for f in backup_path.rglob("*") if f.is_file()
                    )
                    shutil.rmtree(backup_path)
                    total_space_saved += backup_size

                    self.cleanup_report["backup_files_cleaned"].append(
                        {
                            "path": str(backup_path),
                            "size_mb": round(backup_size / (1024 * 1024), 2),
                        }
                    )
                    logger.info(f"Removed old backup: {backup_path}")
                except Exception as e:
                    error_msg = f"Failed to remove old backup {backup_path}: {e}"
                    logger.error(error_msg)
                    self.cleanup_report["errors"].append(error_msg)

            # 3. Consolidate docker-compose files
            logger.info("Consolidating docker-compose files...")
            redundant_compose = self.find_redundant_docker_compose()

            for file_path in redundant_compose:
                try:
                    file_size = file_path.stat().st_size
                    # Backup before removal
                    backup_file = backup_dir / file_path.name
                    shutil.copy2(file_path, backup_file)

                    file_path.unlink()
                    total_space_saved += file_size

                    self.cleanup_report["docker_compose_consolidated"].append(
                        {
                            "file": str(file_path),
                            "size_mb": round(file_size / (1024 * 1024), 2),
                        }
                    )
                    logger.info(f"Removed redundant docker-compose: {file_path}")
                except Exception as e:
                    error_msg = f"Failed to remove docker-compose {file_path}: {e}"
                    logger.error(error_msg)
                    self.cleanup_report["errors"].append(error_msg)

            # 4. Clean build artifacts
            logger.info("Cleaning build artifacts...")
            removed_artifacts = self.cleanup_build_artifacts()

            for artifact_path in removed_artifacts:
                self.cleanup_report["temp_files_removed"].append(str(artifact_path))

            # 5. Clean specific root files
            logger.info("Cleaning specific root files...")
            removed_root_files = self.cleanup_specific_root_files()

            for file_path in removed_root_files:
                self.cleanup_report["temp_files_removed"].append(str(file_path))

            # 6. Consolidate logs directory
            logger.info("Consolidating logs directory...")
            removed_log_files = self.consolidate_logs_directory()

            for file_path in removed_log_files:
                self.cleanup_report["outdated_files_removed"].append(str(file_path))

        except Exception as e:
            error_msg = f"Critical error during cleanup: {e}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

        # Update final report
        self.cleanup_report["total_space_saved_mb"] = round(
            total_space_saved / (1024 * 1024), 2
        )
        self.cleanup_report["backup_location"] = str(backup_dir)

        # Save cleanup report
        report_file = (
            self.project_root
            / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.cleanup_report, f, indent=2)

        logger.info(f"Cleanup completed. Report saved to: {report_file}")
        logger.info(
            f"Total space saved: {self.cleanup_report['total_space_saved_mb']} MB"
        )
        logger.info(f"Backup created at: {backup_dir}")

        return self.cleanup_report


def main():
    """Main execution function"""
    cleanup_tool = ComprehensiveDuplicateCleanup()
    report = cleanup_tool.execute_cleanup()

    print("\n" + "=" * 60)
    print("ACGS-1 COMPREHENSIVE CLEANUP COMPLETED")
    print("=" * 60)
    print(f"Duplicates removed: {len(report['duplicates_removed'])}")
    print(f"Old backups cleaned: {len(report['backup_files_cleaned'])}")
    print(f"Docker-compose consolidated: {len(report['docker_compose_consolidated'])}")
    print(f"Build artifacts removed: {len(report['temp_files_removed'])}")
    print(f"Total space saved: {report['total_space_saved_mb']} MB")
    print(f"Errors encountered: {len(report['errors'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
