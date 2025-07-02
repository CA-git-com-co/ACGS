#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Codebase Cleanup and Reorganization Executor

This script orchestrates the execution of the comprehensive cleanup and reorganization process
for the ACGS-1 codebase. It runs the process in phases, with validation between each phase
to ensure system functionality is maintained.

Phases:
1. Analysis: Scan the codebase and generate a cleanup plan
2. Backup: Create a full backup of the codebase
3. Test Before: Run tests to establish baseline functionality
4. Cleanup: Execute the cleanup plan
5. Test After: Verify system functionality after cleanup
6. Format: Apply code formatting and style standards
7. Final Validation: Comprehensive validation of system functionality

Usage:
    python execute_comprehensive_cleanup.py
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("comprehensive_cleanup_execution.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Timestamp for this execution
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Backup directory
BACKUP_DIR = os.path.join(ROOT_DIR, "backups", f"full_backup_{TIMESTAMP}")

# Core services to validate
CORE_SERVICES = [
    "ac_service",  # Constitutional AI
    "auth_service",  # Authentication
    "fv_service",  # Formal Verification
    "gs_service",  # Governance Synthesis
    "pgc_service",  # Policy Governance
    "integrity_service",  # Integrity
    "ec_service",  # Evolutionary Computation
]


class CleanupExecutor:
    """Orchestrates the execution of the comprehensive cleanup process"""

    def __init__(self):
        self.results = {
            "timestamp": TIMESTAMP,
            "phases": {},
            "success": False,
            "errors": [],
        }

    def run_command(
        self, cmd: list[str], cwd: str | None = None, capture_output: bool = True
    ) -> dict[str, Any]:
        """Run a command and return the result"""
        try:
            if cwd is None:
                cwd = ROOT_DIR

            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=capture_output, text=True, check=False
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
            }
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {"success": False, "error": str(e)}

    def phase_1_analysis(self) -> dict[str, Any]:
        """Phase 1: Analyze the codebase and generate cleanup plan"""
        logger.info("=== Phase 1: Analysis ===")

        phase_results = {"success": False, "actions": 0, "plan_file": "", "details": {}}

        try:
            # Run the cleanup script in dry-run mode
            cmd = [
                sys.executable,
                "comprehensive_cleanup_and_reorganization.py",
                "--output",
                f"cleanup_plan_{TIMESTAMP}.json",
            ]

            result = self.run_command(cmd)

            if result["success"]:
                # Parse the plan file
                plan_file = os.path.join(ROOT_DIR, f"cleanup_plan_{TIMESTAMP}.json")
                if os.path.exists(plan_file):
                    with open(plan_file) as f:
                        plan_data = json.load(f)

                    phase_results["success"] = True
                    phase_results["actions"] = len(plan_data.get("actions", []))
                    phase_results["plan_file"] = plan_file
                    phase_results["details"] = plan_data.get("summary", {})
                else:
                    phase_results["error"] = "Plan file not generated"
            else:
                phase_results["error"] = f"Analysis failed: {result.get('stderr', '')}"

        except Exception as e:
            logger.error(f"Error in analysis phase: {e}")
            phase_results["error"] = str(e)

        self.results["phases"]["analysis"] = phase_results
        return phase_results

    def phase_2_backup(self) -> dict[str, Any]:
        """Phase 2: Create a full backup of the codebase"""
        logger.info("=== Phase 2: Backup ===")

        phase_results = {
            "success": False,
            "backup_dir": BACKUP_DIR,
            "backup_size_mb": 0,
        }

        try:
            # Create backup directory
            os.makedirs(BACKUP_DIR, exist_ok=True)

            # Get list of files to backup (exclude some large directories)
            exclude_dirs = [".git", "node_modules", "venv", "__pycache__", "target"]

            for root, dirs, files in os.walk(ROOT_DIR):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, ROOT_DIR)
                    dst_path = os.path.join(BACKUP_DIR, rel_path)

                    # Create destination directory if it doesn't exist
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                    # Copy file
                    try:
                        shutil.copy2(src_path, dst_path)
                    except OSError as e:
                        logger.warning(f"Error copying {rel_path}: {e}")

            # Calculate backup size
            backup_size = 0
            for root, _, files in os.walk(BACKUP_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    backup_size += os.path.getsize(file_path)

            phase_results["backup_size_mb"] = backup_size / (1024 * 1024)
            phase_results["success"] = True

        except Exception as e:
            logger.error(f"Error in backup phase: {e}")
            phase_results["error"] = str(e)

        self.results["phases"]["backup"] = phase_results
        return phase_results

    def phase_3_test_before(self) -> dict[str, Any]:
        """Phase 3: Run tests to establish baseline functionality"""
        logger.info("=== Phase 3: Test Before ===")

        phase_results = {
            "success": False,
            "tests_run": 0,
            "tests_passed": 0,
            "services_checked": 0,
            "services_ok": 0,
        }

        try:
            # Run tests
            cmd = ["pytest", "-xvs", "--collect-only"]

            result = self.run_command(cmd)

            if result["success"]:
                # Count tests
                tests_output = result["stdout"]
                phase_results["tests_run"] = tests_output.count("collected")
                phase_results["success"] = True

            # Check core services
            for service_name in CORE_SERVICES:
                phase_results["services_checked"] += 1

                # Find service directory
                service_found = False
                for root, dirs, _ in os.walk(ROOT_DIR):
                    if service_name in dirs:
                        service_path = os.path.join(root, service_name)

                        # Check if service has entry point
                        if (
                            os.path.exists(os.path.join(service_path, "main.py"))
                            or os.path.exists(os.path.join(service_path, "app.py"))
                            or os.path.exists(
                                os.path.join(service_path, "app", "main.py")
                            )
                        ):
                            service_found = True
                            phase_results["services_ok"] += 1
                            break

                if not service_found:
                    logger.warning(
                        f"Service {service_name} not found or missing entry point"
                    )

            # Set overall success
            phase_results["success"] = (
                phase_results["services_ok"] == phase_results["services_checked"]
            )

        except Exception as e:
            logger.error(f"Error in test-before phase: {e}")
            phase_results["error"] = str(e)

        self.results["phases"]["test_before"] = phase_results
        return phase_results

    def phase_4_cleanup(self) -> dict[str, Any]:
        """Phase 4: Execute the cleanup plan"""
        logger.info("=== Phase 4: Cleanup ===")

        phase_results = {"success": False, "actions_executed": 0, "details": {}}

        try:
            # Get plan file from phase 1
            plan_file = self.results["phases"]["analysis"].get("plan_file")

            if not plan_file or not os.path.exists(plan_file):
                raise ValueError("Plan file not found from analysis phase")

            # Execute the cleanup plan
            cmd = [
                sys.executable,
                "comprehensive_cleanup_and_reorganization.py",
                "--execute",
                "--output",
                plan_file,
                "--skip-scan",
            ]

            result = self.run_command(cmd)

            if result["success"]:
                phase_results["success"] = True
                phase_results["actions_executed"] = self.results["phases"][
                    "analysis"
                ].get("actions", 0)

                # Parse output for details
                output = result["stdout"]
                phase_results["details"] = {
                    "move_actions": output.count("MOVE:"),
                    "remove_actions": output.count("REMOVE:"),
                    "standardize_actions": output.count("STANDARDIZE:"),
                }
            else:
                phase_results["error"] = (
                    f"Cleanup execution failed: {result.get('stderr', '')}"
                )

        except Exception as e:
            logger.error(f"Error in cleanup phase: {e}")
            phase_results["error"] = str(e)

        self.results["phases"]["cleanup"] = phase_results
        return phase_results

    def phase_5_test_after(self) -> dict[str, Any]:
        """Phase 5: Verify system functionality after cleanup"""
        logger.info("=== Phase 5: Test After ===")

        phase_results = {
            "success": False,
            "tests_run": 0,
            "tests_passed": 0,
            "services_checked": 0,
            "services_ok": 0,
        }

        try:
            # Run tests
            cmd = ["pytest", "-xvs", "--collect-only"]

            result = self.run_command(cmd)

            if result["success"]:
                # Count tests
                tests_output = result["stdout"]
                phase_results["tests_run"] = tests_output.count("collected")
                phase_results["success"] = True

            # Check core services
            for service_name in CORE_SERVICES:
                phase_results["services_checked"] += 1

                # Find service directory
                service_found = False
                for root, dirs, _ in os.walk(ROOT_DIR):
                    if service_name in dirs:
                        service_path = os.path.join(root, service_name)

                        # Check if service has entry point
                        if (
                            os.path.exists(os.path.join(service_path, "main.py"))
                            or os.path.exists(os.path.join(service_path, "app.py"))
                            or os.path.exists(
                                os.path.join(service_path, "app", "main.py")
                            )
                        ):
                            service_found = True
                            phase_results["services_ok"] += 1
                            break

                if not service_found:
                    logger.warning(
                        f"Service {service_name} not found or missing entry point"
                    )

            # Set overall success
            phase_results["success"] = (
                phase_results["services_ok"] == phase_results["services_checked"]
            )

            # Compare with before results
            before_results = self.results["phases"].get("test_before", {})
            if before_results:
                phase_results["tests_diff"] = phase_results[
                    "tests_run"
                ] - before_results.get("tests_run", 0)
                phase_results["services_diff"] = phase_results[
                    "services_ok"
                ] - before_results.get("services_ok", 0)

        except Exception as e:
            logger.error(f"Error in test-after phase: {e}")
            phase_results["error"] = str(e)

        self.results["phases"]["test_after"] = phase_results
        return phase_results

    def phase_6_format(self) -> dict[str, Any]:
        """Phase 6: Apply code formatting and style standards"""
        logger.info("=== Phase 6: Format ===")

        phase_results = {
            "success": False,
            "python_files_formatted": 0,
            "js_files_formatted": 0,
            "rust_files_formatted": 0,
        }

        try:
            # Apply code formatting
            cmd = [
                sys.executable,
                "comprehensive_cleanup_and_reorganization.py",
                "--format",
            ]

            result = self.run_command(cmd)

            if result["success"]:
                phase_results["success"] = True

                # Parse output for details
                output = result["stdout"]
                if "Successfully formatted Python files" in output:
                    phase_results["python_files_formatted"] = 1
                if "Successfully formatted JS/TS files" in output:
                    phase_results["js_files_formatted"] = 1
                if "Successfully formatted Rust files" in output:
                    phase_results["rust_files_formatted"] = 1
            else:
                phase_results["error"] = (
                    f"Formatting failed: {result.get('stderr', '')}"
                )

        except Exception as e:
            logger.error(f"Error in format phase: {e}")
            phase_results["error"] = str(e)

        self.results["phases"]["format"] = phase_results
        return phase_results

    def phase_7_final_validation(self) -> dict[str, Any]:
        """Phase 7: Comprehensive validation of system functionality"""
        logger.info("=== Phase 7: Final Validation ===")

        phase_results = {
            "success": False,
            "blockchain_ok": False,
            "services_ok": False,
            "tests_ok": False,
            "details": {},
        }

        try:
            # Check blockchain
            blockchain_dir = os.path.join(ROOT_DIR, "blockchain")
            if os.path.exists(blockchain_dir) and os.path.isdir(blockchain_dir):
                # Check for key blockchain files
                key_files = ["Cargo.toml", "Anchor.toml", "programs"]

                blockchain_ok = True
                for key_file in key_files:
                    if not os.path.exists(os.path.join(blockchain_dir, key_file)):
                        blockchain_ok = False
                        logger.warning(f"Missing key blockchain file: {key_file}")

                phase_results["blockchain_ok"] = blockchain_ok

            # Check core services
            services_ok = True
            services_details = {}

            for service_name in CORE_SERVICES:
                service_details = {"found": False, "has_entry_point": False}

                # Find service directory
                for root, dirs, _ in os.walk(ROOT_DIR):
                    if service_name in dirs:
                        service_path = os.path.join(root, service_name)
                        service_details["found"] = True

                        # Check if service has entry point
                        if (
                            os.path.exists(os.path.join(service_path, "main.py"))
                            or os.path.exists(os.path.join(service_path, "app.py"))
                            or os.path.exists(
                                os.path.join(service_path, "app", "main.py")
                            )
                        ):
                            service_details["has_entry_point"] = True
                        else:
                            services_ok = False

                        break

                if not service_details["found"]:
                    services_ok = False

                services_details[service_name] = service_details

            phase_results["services_ok"] = services_ok
            phase_results["services_details"] = services_details

            # Check tests
            tests_dir = os.path.join(ROOT_DIR, "tests")
            if os.path.exists(tests_dir) and os.path.isdir(tests_dir):
                # Count test files
                test_files = 0
                for root, _, files in os.walk(tests_dir):
                    for file in files:
                        if file.startswith("test_") and file.endswith(".py"):
                            test_files += 1

                phase_results["tests_ok"] = test_files > 0
                phase_results["test_files"] = test_files
            else:
                phase_results["tests_ok"] = False

            # Set overall success
            phase_results["success"] = (
                phase_results["blockchain_ok"]
                and phase_results["services_ok"]
                and phase_results["tests_ok"]
            )

        except Exception as e:
            logger.error(f"Error in final validation phase: {e}")
            phase_results["error"] = str(e)

        self.results["phases"]["final_validation"] = phase_results
        return phase_results

    def generate_report(self) -> None:
        """Generate a comprehensive report of the cleanup process"""
        logger.info("Generating comprehensive cleanup report...")

        # Set overall success
        all_phases = [
            "analysis",
            "backup",
            "test_before",
            "cleanup",
            "test_after",
            "format",
            "final_validation",
        ]

        # Check if all required phases succeeded
        required_phases = ["backup", "cleanup", "test_after", "final_validation"]
        self.results["success"] = all(
            self.results["phases"].get(phase, {}).get("success", False)
            for phase in required_phases
        )

        # Calculate statistics
        stats = {
            "total_phases": len(all_phases),
            "successful_phases": sum(
                1
                for phase in all_phases
                if self.results["phases"].get(phase, {}).get("success", False)
            ),
            "actions_executed": self.results["phases"]
            .get("cleanup", {})
            .get("actions_executed", 0),
            "backup_size_mb": self.results["phases"]
            .get("backup", {})
            .get("backup_size_mb", 0),
        }

        self.results["statistics"] = stats

        # Save report to file
        report_file = os.path.join(
            ROOT_DIR, f"cleanup_execution_report_{TIMESTAMP}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Report saved to: {report_file}")

        # Generate human-readable summary
        summary_file = os.path.join(ROOT_DIR, f"CLEANUP_SUMMARY_{TIMESTAMP}.md")

        with open(summary_file, "w") as f:
            f.write("# ACGS-1 Codebase Cleanup and Reorganization Summary\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Overall Status\n\n")
            if self.results["success"]:
                f.write(
                    "✅ **Success:** The cleanup and reorganization completed successfully\n\n"
                )
            else:
                f.write(
                    "❌ **Failed:** The cleanup and reorganization encountered issues\n\n"
                )

            f.write("## Phase Results\n\n")
            for phase in all_phases:
                phase_data = self.results["phases"].get(phase, {})
                if phase_data:
                    if phase_data.get("success", False):
                        f.write(
                            f"- ✅ **{phase.replace('_', ' ').title()}:** Successful\n"
                        )
                    else:
                        f.write(
                            f"- ❌ **{phase.replace('_', ' ').title()}:** Failed - {phase_data.get('error', 'Unknown error')}\n"
                        )

            f.write("\n## Key Statistics\n\n")
            f.write(
                f"- **Phases Completed:** {stats['successful_phases']}/{stats['total_phases']}\n"
            )
            f.write(f"- **Actions Executed:** {stats['actions_executed']}\n")
            f.write(f"- **Backup Size:** {stats['backup_size_mb']:.2f} MB\n")

            # Add service status
            f.write("\n## Core Services Status\n\n")
            services_details = (
                self.results["phases"]
                .get("final_validation", {})
                .get("services_details", {})
            )
            for service_name, details in services_details.items():
                if details.get("found", False) and details.get(
                    "has_entry_point", False
                ):
                    f.write(f"- ✅ **{service_name}:** Found and has entry point\n")
                elif details.get("found", False):
                    f.write(f"- ⚠️ **{service_name}:** Found but missing entry point\n")
                else:
                    f.write(f"- ❌ **{service_name}:** Not found\n")

            # Add next steps
            f.write("\n## Next Steps\n\n")
            if self.results["success"]:
                f.write("1. Verify system functionality with comprehensive tests\n")
                f.write("2. Deploy the cleaned and reorganized codebase\n")
                f.write("3. Update documentation to reflect the new structure\n")
            else:
                f.write("1. Review the error logs and fix the issues\n")
                f.write("2. Restore from backup if needed\n")
                f.write("3. Retry the cleanup process\n")

            f.write("\n## Backup Location\n\n")
            f.write(f"A full backup was created at: `{BACKUP_DIR}`\n")

        logger.info(f"Summary saved to: {summary_file}")

    def execute_all_phases(self) -> bool:
        """Execute all phases of the cleanup process"""
        logger.info("Starting comprehensive cleanup and reorganization process...")

        # Phase 1: Analysis
        phase_1_results = self.phase_1_analysis()
        if not phase_1_results["success"]:
            logger.error("Analysis phase failed - aborting")
            self.results["errors"].append("Analysis phase failed")
            self.generate_report()
            return False

        # Phase 2: Backup
        phase_2_results = self.phase_2_backup()
        if not phase_2_results["success"]:
            logger.error("Backup phase failed - aborting")
            self.results["errors"].append("Backup phase failed")
            self.generate_report()
            return False

        # Phase 3: Test Before
        phase_3_results = self.phase_3_test_before()
        if not phase_3_results["success"]:
            logger.warning("Test Before phase had issues - proceeding with caution")
            self.results["errors"].append("Test Before phase had issues")

        # Phase 4: Cleanup
        phase_4_results = self.phase_4_cleanup()
        if not phase_4_results["success"]:
            logger.error("Cleanup phase failed - aborting")
            self.results["errors"].append("Cleanup phase failed")
            self.generate_report()
            return False

        # Phase 5: Test After
        phase_5_results = self.phase_5_test_after()
        if not phase_5_results["success"]:
            logger.error("Test After phase failed - system may be broken")
            self.results["errors"].append("Test After phase failed")
            # Continue to generate report

        # Phase 6: Format
        phase_6_results = self.phase_6_format()
        if not phase_6_results["success"]:
            logger.warning("Format phase had issues - continuing")
            self.results["errors"].append("Format phase had issues")

        # Phase 7: Final Validation
        phase_7_results = self.phase_7_final_validation()
        if not phase_7_results["success"]:
            logger.error("Final Validation phase failed - system may be broken")
            self.results["errors"].append("Final Validation phase failed")

        # Generate report
        self.generate_report()

        return self.results["success"]


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="ACGS-1 Comprehensive Cleanup Executor"
    )
    parser.add_argument(
        "--skip-backup", action="store_true", help="Skip backup phase (not recommended)"
    )
    parser.add_argument(
        "--skip-format", action="store_true", help="Skip code formatting phase"
    )
    args = parser.parse_args()

    executor = CleanupExecutor()

    try:
        success = executor.execute_all_phases()

        if success:
            logger.info(
                "✅ Comprehensive cleanup and reorganization completed successfully!"
            )
            return 0
        logger.error("❌ Comprehensive cleanup and reorganization failed!")
        return 1

    except KeyboardInterrupt:
        logger.error("\nOperation cancelled by user")
        return 2
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return 3


if __name__ == "__main__":
    sys.exit(main())
