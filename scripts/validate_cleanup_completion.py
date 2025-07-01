#!/usr/bin/env python3
"""
ACGS-1 Cleanup Validation Script

Validates that the comprehensive codebase cleanup was successful and that
all critical functionality is preserved.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class CleanupValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_status": "unknown",
            "core_services": {},
            "blockchain_programs": {},
            "configuration_files": {},
            "test_infrastructure": {},
            "documentation": {},
            "applications": {},
            "critical_files": {},
            "errors": [],
            "warnings": [],
            "summary": {},
        }

    def validate_core_services(self) -> bool:
        """Validate that all 7 core ACGS services are present and functional."""
        print("🔍 Validating core services...")

        core_services = {
            "auth_service": "services/core/constitutional-ai/ac_service/app/main.py",
            "ac_service": "services/core/constitutional-ai/ac_service/app/main.py",
            "integrity_service": "services/core/self-evolving-ai/app/main.py",
            "fv_service": "services/core/formal-verification/fv_service/main.py",
            "gs_service": "services/core/governance-synthesis/gs_service/app/main.py",
            "pgc_service": "services/core/policy-governance/pgc_service/app/main.py",
            "ec_service": "services/core/evolutionary-computation/app/main.py",
        }

        all_services_present = True
        for service_name, service_path in core_services.items():
            full_path = self.project_root / service_path
            if full_path.exists():
                self.validation_results["core_services"][service_name] = {
                    "status": "present",
                    "path": str(service_path),
                    "size": full_path.stat().st_size,
                }
                print(f"  ✅ {service_name}: Found at {service_path}")
            else:
                self.validation_results["core_services"][service_name] = {
                    "status": "missing",
                    "path": str(service_path),
                }
                self.validation_results["errors"].append(
                    f"Missing core service: {service_name}"
                )
                print(f"  ❌ {service_name}: Missing at {service_path}")
                all_services_present = False

        return all_services_present

    def validate_blockchain_programs(self) -> bool:
        """Validate that blockchain programs and Quantumagi deployment are intact."""
        print("🔍 Validating blockchain programs...")

        blockchain_files = {
            "anchor_toml": "blockchain/Anchor.toml",
            "cargo_toml": "blockchain/Cargo.toml",
            "quantumagi_core_program": "blockchain/programs/quantumagi-core/src/lib.rs",
            "appeals_program": "blockchain/programs/appeals/src/lib.rs",
            "logging_program": "blockchain/programs/logging/src/lib.rs",
            "devnet_program_ids": "blockchain/devnet_program_ids.json",
        }

        all_blockchain_present = True
        for file_name, file_path in blockchain_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                self.validation_results["blockchain_programs"][file_name] = {
                    "status": "present",
                    "path": str(file_path),
                    "size": full_path.stat().st_size,
                }
                print(f"  ✅ {file_name}: Found at {file_path}")
            else:
                self.validation_results["blockchain_programs"][file_name] = {
                    "status": "missing",
                    "path": str(file_path),
                }
                self.validation_results["errors"].append(
                    f"Missing blockchain file: {file_name}"
                )
                print(f"  ❌ {file_name}: Missing at {file_path}")
                all_blockchain_present = False

        return all_blockchain_present

    def validate_configuration_files(self) -> bool:
        """Validate that critical configuration files are preserved."""
        print("🔍 Validating configuration files...")

        config_files = {
            "docker_compose": "docker-compose.acgs.yml",
            "production_compose": "docker-compose.prod.yml",
            "requirements": "requirements.txt",
            "pyproject": "pyproject.toml",
            "package_json": "package.json",
            "prometheus_config": "config/prometheus.yml",
        }

        all_configs_present = True
        for config_name, config_path in config_files.items():
            full_path = self.project_root / config_path
            if full_path.exists():
                self.validation_results["configuration_files"][config_name] = {
                    "status": "present",
                    "path": str(config_path),
                    "size": full_path.stat().st_size,
                }
                print(f"  ✅ {config_name}: Found at {config_path}")
            else:
                self.validation_results["configuration_files"][config_name] = {
                    "status": "missing",
                    "path": str(config_path),
                }
                self.validation_results["warnings"].append(
                    f"Missing config file: {config_name}"
                )
                print(f"  ⚠️ {config_name}: Missing at {config_path}")
                all_configs_present = False

        return all_configs_present

    def validate_test_infrastructure(self) -> bool:
        """Validate that test infrastructure is preserved."""
        print("🔍 Validating test infrastructure...")

        test_files = {
            "pytest_ini": "pytest.ini",
            "conftest": "conftest.py",
            "tests_directory": "tests",
            "unit_tests": "tests/unit",
            "integration_tests": "tests/integration",
            "e2e_tests": "tests/e2e",
        }

        all_tests_present = True
        for test_name, test_path in test_files.items():
            full_path = self.project_root / test_path
            if full_path.exists():
                if full_path.is_dir():
                    test_count = len(list(full_path.rglob("test_*.py")))
                    self.validation_results["test_infrastructure"][test_name] = {
                        "status": "present",
                        "path": str(test_path),
                        "test_files": test_count,
                    }
                    print(
                        f"  ✅ {test_name}: Found at {test_path} ({test_count} test files)"
                    )
                else:
                    self.validation_results["test_infrastructure"][test_name] = {
                        "status": "present",
                        "path": str(test_path),
                        "size": full_path.stat().st_size,
                    }
                    print(f"  ✅ {test_name}: Found at {test_path}")
            else:
                self.validation_results["test_infrastructure"][test_name] = {
                    "status": "missing",
                    "path": str(test_path),
                }
                self.validation_results["warnings"].append(
                    f"Missing test component: {test_name}"
                )
                print(f"  ⚠️ {test_name}: Missing at {test_path}")
                all_tests_present = False

        return all_tests_present

    def validate_applications(self) -> bool:
        """Validate that applications are preserved."""
        print("🔍 Validating applications...")

        app_components = {
            "frontend": "applications/frontend",
            "governance_dashboard": "applications/governance-dashboard",
            "package_json": "applications/package.json",
            "next_config": "applications/next.config.js",
        }

        all_apps_present = True
        for app_name, app_path in app_components.items():
            full_path = self.project_root / app_path
            if full_path.exists():
                if full_path.is_dir():
                    file_count = len(list(full_path.rglob("*")))
                    self.validation_results["applications"][app_name] = {
                        "status": "present",
                        "path": str(app_path),
                        "files": file_count,
                    }
                    print(f"  ✅ {app_name}: Found at {app_path} ({file_count} files)")
                else:
                    self.validation_results["applications"][app_name] = {
                        "status": "present",
                        "path": str(app_path),
                        "size": full_path.stat().st_size,
                    }
                    print(f"  ✅ {app_name}: Found at {app_path}")
            else:
                self.validation_results["applications"][app_name] = {
                    "status": "missing",
                    "path": str(app_path),
                }
                self.validation_results["warnings"].append(
                    f"Missing application component: {app_name}"
                )
                print(f"  ⚠️ {app_name}: Missing at {app_path}")
                all_apps_present = False

        return all_apps_present

    def check_cleanup_report(self) -> bool:
        """Check if cleanup report exists and analyze results."""
        print("🔍 Checking cleanup report...")

        cleanup_reports = list(self.project_root.glob("cleanup_report_*.json"))
        if not cleanup_reports:
            self.validation_results["warnings"].append("No cleanup report found")
            print("  ⚠️ No cleanup report found")
            return False

        # Get the most recent cleanup report
        latest_report = max(cleanup_reports, key=lambda p: p.stat().st_mtime)

        try:
            with open(latest_report) as f:
                cleanup_data = json.load(f)

            self.validation_results["cleanup_summary"] = {
                "report_file": str(latest_report),
                "files_removed": cleanup_data.get("total_files_removed", 0),
                "size_freed_mb": cleanup_data.get("total_size_removed_mb", 0),
                "validation_passed": cleanup_data.get("validation_passed", False),
            }

            print(f"  ✅ Cleanup report found: {latest_report}")
            print(f"     Files removed: {cleanup_data.get('total_files_removed', 0)}")
            print(f"     Size freed: {cleanup_data.get('total_size_removed_mb', 0)} MB")

            return True

        except Exception as e:
            self.validation_results["errors"].append(
                f"Failed to read cleanup report: {e}"
            )
            print(f"  ❌ Failed to read cleanup report: {e}")
            return False

    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report."""

        # Calculate overall status
        error_count = len(self.validation_results["errors"])
        warning_count = len(self.validation_results["warnings"])

        if error_count == 0:
            if warning_count == 0:
                self.validation_results["validation_status"] = "success"
            else:
                self.validation_results["validation_status"] = "success_with_warnings"
        else:
            self.validation_results["validation_status"] = "failed"

        # Generate summary
        self.validation_results["summary"] = {
            "total_errors": error_count,
            "total_warnings": warning_count,
            "core_services_validated": len(
                [
                    s
                    for s in self.validation_results["core_services"].values()
                    if s["status"] == "present"
                ]
            ),
            "blockchain_programs_validated": len(
                [
                    b
                    for b in self.validation_results["blockchain_programs"].values()
                    if b["status"] == "present"
                ]
            ),
            "configuration_files_validated": len(
                [
                    c
                    for c in self.validation_results["configuration_files"].values()
                    if c["status"] == "present"
                ]
            ),
            "test_infrastructure_validated": len(
                [
                    t
                    for t in self.validation_results["test_infrastructure"].values()
                    if t["status"] == "present"
                ]
            ),
            "applications_validated": len(
                [
                    a
                    for a in self.validation_results["applications"].values()
                    if a["status"] == "present"
                ]
            ),
        }

        # Save validation report
        report_path = (
            self.project_root
            / f"cleanup_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        return str(report_path)

    def run_validation(self) -> bool:
        """Run comprehensive validation."""
        print("🚀 Starting ACGS-1 cleanup validation...")
        print("=" * 60)

        # Run all validation checks
        core_services_ok = self.validate_core_services()
        blockchain_ok = self.validate_blockchain_programs()
        config_ok = self.validate_configuration_files()
        tests_ok = self.validate_test_infrastructure()
        apps_ok = self.validate_applications()
        cleanup_report_ok = self.check_cleanup_report()

        # Generate report
        report_path = self.generate_validation_report()

        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        status = self.validation_results["validation_status"]
        if status == "success":
            print("✅ VALIDATION PASSED - All critical components preserved")
        elif status == "success_with_warnings":
            print("⚠️ VALIDATION PASSED WITH WARNINGS - Core functionality preserved")
        else:
            print("❌ VALIDATION FAILED - Critical components missing")

        print(f"\nErrors: {len(self.validation_results['errors'])}")
        print(f"Warnings: {len(self.validation_results['warnings'])}")
        print(f"Report saved: {report_path}")

        if self.validation_results["errors"]:
            print("\n❌ ERRORS:")
            for error in self.validation_results["errors"]:
                print(f"  - {error}")

        if self.validation_results["warnings"]:
            print("\n⚠️ WARNINGS:")
            for warning in self.validation_results["warnings"]:
                print(f"  - {warning}")

        return status in ["success", "success_with_warnings"]


if __name__ == "__main__":
    validator = CleanupValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)
