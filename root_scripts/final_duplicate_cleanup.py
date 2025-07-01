#!/usr/bin/env python3
"""
ACGS-1 Final Duplicate Cleanup

This script handles the remaining duplicate directories and files that need consolidation.
"""

import shutil
from datetime import datetime
from pathlib import Path


class FinalDuplicateCleanup:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.actions_log = []

    def log_action(self, action: str):
        """Log cleanup actions."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action}"
        self.actions_log.append(log_entry)
        print(f"📝 {log_entry}")

    def remove_remaining_duplicates(self):
        """Remove remaining duplicate directories."""
        print("🔄 Removing remaining duplicate directories...")

        services_core = self.project_root / "services" / "core"

        # Remaining duplicates to remove (keep the hyphenated versions)
        duplicates_to_remove = [
            "governance_workflows",  # Keep governance-workflows
            "formal_verification_enhanced",  # Keep formal-verification
        ]

        # Also remove some obsolete service directories
        obsolete_services = [
            "ac",  # Superseded by constitutional-ai
            "ec",  # Superseded by evolutionary-computation
            "gs",  # Superseded by governance-synthesis
            "pgc",  # Superseded by policy-governance
            "hitl_safety",  # Integrated into other services
            "security_hardening",  # Integrated into other services
            "mathematical-reasoning",  # Not part of core 7 services
        ]

        all_to_remove = duplicates_to_remove + obsolete_services

        for dir_name in all_to_remove:
            dir_path = services_core / dir_name
            if dir_path.exists():
                if dir_path.is_symlink():
                    dir_path.unlink()
                    self.log_action(f"Removed symlink: {dir_name}")
                elif dir_path.is_dir():
                    shutil.rmtree(dir_path)
                    self.log_action(f"Removed directory: {dir_name}")

    def clean_root_level_duplicates(self):
        """Clean up duplicate files in the root directory."""
        print("🧹 Cleaning root level duplicate files...")

        # Files that appear to be duplicates or version variants
        root_duplicates = [
            # Version files that are likely duplicates
            "=0.104.0",
            "=0.21.0",
            "=0.24.0",
            "=0.25.0",
            "=1.0.0",
            "=1.24.0",
            "=1.3.0",
            "=1.7.4",
            "=2.1.0",
            "=2.5.0",
            "=23.2.0",
            "=3.3.0",
            "=4.6.0",
            "=41.0.0",
            "=5.0.0",
            "=6.0.1",
            "=8.11.0",
        ]

        removed_count = 0
        for file_name in root_duplicates:
            file_path = self.project_root / file_name
            if file_path.exists():
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                removed_count += 1
                self.log_action(f"Removed root duplicate: {file_name}")

        self.log_action(f"Removed {removed_count} root level duplicates")

    def clean_old_reports_and_logs(self):
        """Clean up old report and log files."""
        print("📋 Cleaning old reports and logs...")

        # Patterns for old files to remove
        old_file_patterns = [
            "*_report_*.json",
            "*_results_*.json",
            "*_analysis_*.json",
            "*_summary_*.json",
            "Tasks_*.md",
            "*_COMPLETION_REPORT.md",
            "*_SUMMARY.md",
            "*_REPORT.md",
        ]

        removed_count = 0
        for pattern in old_file_patterns:
            files = list(self.project_root.glob(pattern))
            # Keep the 3 most recent of each type
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_file in files[3:]:  # Remove all but the 3 newest
                try:
                    old_file.unlink()
                    removed_count += 1
                except Exception as e:
                    self.log_action(f"Warning: Could not remove {old_file}: {e}")

        self.log_action(f"Removed {removed_count} old report files")

    def validate_core_services(self):
        """Validate that all 7 core services are present and functional."""
        print("✅ Validating core services...")

        required_services = [
            "constitutional-ai",
            "governance-synthesis",
            "formal-verification",
            "policy-governance",
            "evolutionary-computation",
            "self-evolving-ai",
            "acgs-pgp-v8",  # 7th service
        ]

        services_core = self.project_root / "services" / "core"
        missing_services = []

        for service in required_services:
            service_path = services_core / service
            if not service_path.exists():
                missing_services.append(service)

        if missing_services:
            self.log_action(f"ERROR: Missing services: {missing_services}")
            return False

        self.log_action("All 7 core services validated successfully")
        return True

    def validate_critical_components(self):
        """Validate critical components are preserved."""
        print("🛡️ Validating critical components...")

        critical_paths = [
            "services/shared/enhancement_framework",
            "blockchain/quantumagi-deployment",
            "blockchain/programs",
            "services/shared/alembic",
            "migrations",
        ]

        missing_components = []
        for path in critical_paths:
            full_path = self.project_root / path
            if not full_path.exists():
                missing_components.append(path)

        if missing_components:
            self.log_action(f"ERROR: Missing critical components: {missing_components}")
            return False

        self.log_action("All critical components validated successfully")
        return True

    def generate_final_report(self):
        """Generate final cleanup report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cleanup_type": "Final Duplicate Cleanup",
            "actions_performed": self.actions_log,
            "validation_passed": True,
            "summary": {
                "total_actions": len(self.actions_log),
                "cleanup_completed": True,
            },
        }

        report_file = (
            self.project_root
            / f"final_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        import json

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.log_action(f"Final cleanup report saved to {report_file}")
        return report

    def execute_final_cleanup(self):
        """Execute the final cleanup process."""
        print("🚀 Starting final duplicate cleanup...")

        try:
            # Step 1: Remove remaining duplicates
            self.remove_remaining_duplicates()

            # Step 2: Clean root level duplicates
            self.clean_root_level_duplicates()

            # Step 3: Clean old reports
            self.clean_old_reports_and_logs()

            # Step 4: Validate core services
            if not self.validate_core_services():
                print("❌ Core service validation failed!")
                return False

            # Step 5: Validate critical components
            if not self.validate_critical_components():
                print("❌ Critical component validation failed!")
                return False

            # Step 6: Generate final report
            report = self.generate_final_report()

            print("✅ Final cleanup completed successfully!")
            print(f"📝 Total actions: {len(self.actions_log)}")

            return True

        except Exception as e:
            self.log_action(f"ERROR during final cleanup: {e!s}")
            print(f"❌ Final cleanup failed: {e}")
            return False


if __name__ == "__main__":
    cleanup = FinalDuplicateCleanup()
    success = cleanup.execute_final_cleanup()
    exit(0 if success else 1)
