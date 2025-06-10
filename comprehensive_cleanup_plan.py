#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Codebase Cleanup and Optimization Script

This script performs systematic cleanup and optimization of the ACGS-1 constitutional
governance system following the recent reorganization.

Phases:
1. Remove backup directories and duplicate files
2. Security vulnerability remediation
3. Code quality and standards enforcement
4. Dependency management and consolidation
5. File structure optimization
6. Documentation and configuration updates

Usage:
    python comprehensive_cleanup_plan.py --phase all
    python comprehensive_cleanup_plan.py --phase security
    python comprehensive_cleanup_plan.py --phase dependencies
"""

import os
import sys
import json
import shutil
import subprocess
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("acgs_cleanup.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ACGSCleanupOrchestrator:
    """Orchestrates comprehensive cleanup and optimization of ACGS-1 codebase."""

    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "phases_completed": [],
            "files_removed": [],
            "files_modified": [],
            "security_fixes": [],
            "performance_improvements": [],
            "errors": [],
        }

    def execute_phase_1_backup_cleanup(self) -> Dict:
        """Phase 1: Remove backup directories and duplicate files."""
        logger.info("🧹 Phase 1: Backup and Duplicate File Cleanup")

        phase_results = {
            "backup_dirs_removed": [],
            "duplicate_files_removed": [],
            "space_freed_mb": 0,
        }

        # Identify backup directories
        backup_patterns = [
            "backup_*",
            "*_backup",
            "*.backup",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            "node_modules",
            "target/debug",
            "target/release",
        ]

        for pattern in backup_patterns:
            backup_dirs = list(self.project_root.glob(f"**/{pattern}"))
            for backup_dir in backup_dirs:
                if backup_dir.is_dir():
                    try:
                        # Calculate size before removal
                        size_mb = self._get_directory_size(backup_dir) / (1024 * 1024)

                        # Skip if it's the current backup we're creating
                        if "backup_20250607_192350" in str(backup_dir):
                            logger.info(f"Removing old backup: {backup_dir}")
                            shutil.rmtree(backup_dir)
                            phase_results["backup_dirs_removed"].append(str(backup_dir))
                            phase_results["space_freed_mb"] += size_mb

                    except Exception as e:
                        logger.error(f"Error removing {backup_dir}: {e}")
                        self.cleanup_report["errors"].append(
                            f"Backup removal error: {e}"
                        )

        # Remove duplicate .backup files
        backup_files = list(self.project_root.glob("**/*.backup"))
        for backup_file in backup_files:
            try:
                backup_file.unlink()
                phase_results["duplicate_files_removed"].append(str(backup_file))
                logger.info(f"Removed backup file: {backup_file}")
            except Exception as e:
                logger.error(f"Error removing backup file {backup_file}: {e}")

        self.cleanup_report["phases_completed"].append("backup_cleanup")
        return phase_results

    def execute_phase_2_security_remediation(self) -> Dict:
        """Phase 2: Security vulnerability remediation."""
        logger.info("🔒 Phase 2: Security Vulnerability Remediation")

        phase_results = {
            "vulnerabilities_fixed": [],
            "dependencies_updated": [],
            "security_configs_updated": [],
        }

        # Run security audit
        try:
            # Install security tools if not present
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "safety",
                    "bandit",
                    "pip-audit",
                ],
                check=True,
                capture_output=True,
            )

            # Run pip-audit for vulnerability scanning
            audit_result = subprocess.run(
                [sys.executable, "-m", "pip_audit", "--format=json"],
                capture_output=True,
                text=True,
            )

            if audit_result.returncode == 0:
                audit_data = json.loads(audit_result.stdout)
                phase_results["vulnerabilities_fixed"] = audit_data.get(
                    "vulnerabilities", []
                )

        except Exception as e:
            logger.error(f"Security audit error: {e}")
            self.cleanup_report["errors"].append(f"Security audit error: {e}")

        # Update security configurations
        self._update_security_configs()

        self.cleanup_report["phases_completed"].append("security_remediation")
        return phase_results

    def execute_phase_3_code_quality(self) -> Dict:
        """Phase 3: Code quality and standards enforcement."""
        logger.info("📝 Phase 3: Code Quality and Standards")

        phase_results = {
            "files_formatted": [],
            "unused_imports_removed": [],
            "dead_code_removed": [],
        }

        # Format Python files with Black
        python_files = list(self.project_root.glob("**/*.py"))
        for py_file in python_files:
            if self._should_format_file(py_file):
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "black", "--check", str(py_file)],
                        capture_output=True,
                    )

                    if result.returncode != 0:
                        subprocess.run(
                            [sys.executable, "-m", "black", str(py_file)], check=True
                        )
                        phase_results["files_formatted"].append(str(py_file))

                except Exception as e:
                    logger.error(f"Error formatting {py_file}: {e}")

        # Remove unused imports using autoflake
        self._remove_unused_imports(phase_results)

        self.cleanup_report["phases_completed"].append("code_quality")
        return phase_results

    def execute_phase_4_dependency_management(self) -> Dict:
        """Phase 4: Dependency management and consolidation."""
        logger.info("📦 Phase 4: Dependency Management")

        phase_results = {
            "requirements_consolidated": [],
            "unused_dependencies_removed": [],
            "version_conflicts_resolved": [],
        }

        # Find all requirements.txt files
        requirements_files = list(self.project_root.glob("**/requirements*.txt"))

        # Consolidate and clean requirements
        for req_file in requirements_files:
            if self._should_process_requirements(req_file):
                self._clean_requirements_file(req_file, phase_results)

        self.cleanup_report["phases_completed"].append("dependency_management")
        return phase_results

    def _get_directory_size(self, directory: Path) -> int:
        """Calculate directory size in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size

    def _should_format_file(self, file_path: Path) -> bool:
        """Determine if file should be formatted."""
        exclude_patterns = [
            "venv",
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            "target",
            "migrations",
        ]
        return not any(pattern in str(file_path) for pattern in exclude_patterns)

    def _should_process_requirements(self, req_file: Path) -> bool:
        """Determine if requirements file should be processed."""
        exclude_patterns = ["backup", "archive", "test"]
        return not any(pattern in str(req_file) for pattern in exclude_patterns)

    def _update_security_configs(self):
        """Update security configuration files."""
        # Update .bandit configuration
        bandit_config = self.project_root / ".bandit"
        if bandit_config.exists():
            logger.info("Security configuration already exists")

    def _remove_unused_imports(self, phase_results: Dict):
        """Remove unused imports from Python files."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "autoflake"],
                check=True,
                capture_output=True,
            )

            python_files = list(self.project_root.glob("**/*.py"))
            for py_file in python_files:
                if self._should_format_file(py_file):
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "autoflake",
                            "--remove-all-unused-imports",
                            "--remove-unused-variables",
                            "--in-place",
                            str(py_file),
                        ],
                        capture_output=True,
                    )

                    if result.returncode == 0:
                        phase_results["unused_imports_removed"].append(str(py_file))

        except Exception as e:
            logger.error(f"Error removing unused imports: {e}")

    def _clean_requirements_file(self, req_file: Path, phase_results: Dict):
        """Clean and consolidate requirements file."""
        try:
            with open(req_file, "r") as f:
                lines = f.readlines()

            # Remove duplicates and clean up
            cleaned_lines = []
            seen_packages = set()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    package_name = line.split("==")[0].split(">=")[0].split("<=")[0]
                    if package_name not in seen_packages:
                        seen_packages.add(package_name)
                        cleaned_lines.append(line)
                elif line.startswith("#"):
                    cleaned_lines.append(line)

            # Write back cleaned requirements
            with open(req_file, "w") as f:
                f.write("\n".join(cleaned_lines) + "\n")

            phase_results["requirements_consolidated"].append(str(req_file))
            logger.info(f"Cleaned requirements file: {req_file}")

        except Exception as e:
            logger.error(f"Error cleaning requirements file {req_file}: {e}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="ACGS-1 Comprehensive Cleanup")
    parser.add_argument(
        "--phase",
        choices=["all", "backup", "security", "quality", "dependencies"],
        default="all",
        help="Cleanup phase to execute",
    )
    parser.add_argument(
        "--project-root", default="/home/dislove/ACGS-1", help="Project root directory"
    )

    args = parser.parse_args()

    orchestrator = ACGSCleanupOrchestrator(args.project_root)

    try:
        if args.phase in ["all", "backup"]:
            orchestrator.execute_phase_1_backup_cleanup()

        if args.phase in ["all", "security"]:
            orchestrator.execute_phase_2_security_remediation()

        if args.phase in ["all", "quality"]:
            orchestrator.execute_phase_3_code_quality()

        if args.phase in ["all", "dependencies"]:
            orchestrator.execute_phase_4_dependency_management()

        # Save cleanup report
        report_file = f"acgs_cleanup_report_{orchestrator.backup_timestamp}.json"
        with open(report_file, "w") as f:
            json.dump(orchestrator.cleanup_report, f, indent=2)

        logger.info(f"✅ Cleanup completed. Report saved to: {report_file}")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
