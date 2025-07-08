#!/usr/bin/env python3
"""
ACGS-2 Monitoring Documentation Validation Script
Constitutional Hash: cdd01ef066bc6cf2

This script validates that the monitoring infrastructure documentation
has been properly updated across all relevant files.
"""

from pathlib import Path
from typing import Union

# Constitutional hash validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class DocumentationValidator:
    """Validates monitoring documentation updates"""

    def __init__(self) -> None:
        self.project_root = Path("/home/dislove/ACGS-2")
        self.results: list[dict[str, str]] = []

    def validate_file_exists(self, file_path: str) -> bool:
        """Check if a file exists"""
        full_path = self.project_root / file_path
        exists = full_path.exists()
        self.results.append({
            "check": f"File exists: {file_path}",
            "status": "PASS" if exists else "FAIL",
            "details": f"File {'found' if exists else 'not found'} at {full_path}",
        })
        return exists

    def validate_content_contains(self, file_path: str, patterns: list[str]) -> bool:
        """Check if file contains specific patterns"""
        full_path = self.project_root / file_path

        if not full_path.exists():
            self.results.append({
                "check": f"Content validation: {file_path}",
                "status": "FAIL",
                "details": f"File not found: {full_path}",
            })
            return False

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            all_found = True
            missing_patterns = []

            for pattern in patterns:
                if pattern not in content:
                    all_found = False
                    missing_patterns.append(pattern)

            self.results.append({
                "check": f"Content patterns in {file_path}",
                "status": "PASS" if all_found else "FAIL",
                "details": (
                    f"Missing patterns: {missing_patterns}"
                    if missing_patterns
                    else "All patterns found"
                ),
            })

            return all_found

        except Exception as e:
            self.results.append({
                "check": f"Content validation: {file_path}",
                "status": "ERROR",
                "details": f"Error reading file: {e!s}",
            })
            return False

    def validate_constitutional_hash(self, file_path: str) -> bool:
        """Validate constitutional hash presence"""
        return self.validate_content_contains(file_path, [CONSTITUTIONAL_HASH])

    def run_validation(self) -> dict[str, Union[int, float, str, list[dict[str, str]]]]:
        """Run complete documentation validation"""
        print("🏛️ Validating monitoring documentation updates...")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("=" * 60)

        # 1. Validate monitoring configuration files exist
        config_files = [
            "config/monitoring/prometheus-constitutional.yml",
            "config/monitoring/constitutional_rules.yml",
            "config/monitoring/grafana-constitutional-dashboard.json",
            "scripts/validate_constitutional_monitoring.py",
        ]

        for config_file in config_files:
            self.validate_file_exists(config_file)
            self.validate_constitutional_hash(config_file)

        # 2. Validate README.md updates
        readme_patterns = [
            "comprehensive constitutional monitoring infrastructure",
            "docs/ACGS_SERVICE_OVERVIEW.md",
            "Prometheus, Grafana, and a set of custom alert rules",
        ]
        self.validate_content_contains("README.md", readme_patterns)

        # 3. Validate ACGS_SERVICE_OVERVIEW.md updates
        service_overview_patterns = [
            "comprehensive monitoring infrastructure",
            "Prometheus and Grafana",
            "grafana-constitutional-dashboard.json",
            "docs/operations/ACGS_PRODUCTION_OPERATIONS.md",
        ]
        self.validate_content_contains(
            "docs/ACGS_SERVICE_OVERVIEW.md", service_overview_patterns
        )

        # 4. Validate operations documentation updates
        operations_patterns = [
            "comprehensive monitoring and alerting system",
            "prometheus-constitutional.yml",
            "grafana-constitutional-dashboard.json",
        ]
        self.validate_content_contains(
            "docs/operations/ACGS_PRODUCTION_OPERATIONS.md", operations_patterns
        )

        # 5. Validate runbooks updates
        runbooks_patterns = [
            "Constitutional Monitoring Dashboard Recovery",
            "Grafana Dashboard Restoration",
            "config/monitoring/grafana-constitutional-dashboard.json",
        ]
        self.validate_content_contains("docs/operations/runbooks.md", runbooks_patterns)

        # 6. Validate deployment guide updates
        deployment_patterns = [
            "constitutional compliance monitoring",
            "prometheus-constitutional.yml",
            "constitutional_rules.yml",
            "grafana-constitutional-dashboard.json",
        ]
        self.validate_content_contains(
            "docs/deployment/DEPLOYMENT_GUIDE.md", deployment_patterns
        )

        # Generate summary
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r["status"] == "PASS")
        failed_checks = sum(1 for r in self.results if r["status"] == "FAIL")
        error_checks = sum(1 for r in self.results if r["status"] == "ERROR")

        summary: dict[str, Union[int, float, str, list[dict[str, str]]]] = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "errors": error_checks,
            "success_rate": passed_checks / total_checks if total_checks > 0 else 0,
            "overall_status": (
                "PASS" if failed_checks == 0 and error_checks == 0 else "FAIL"
            ),
            "results": self.results,
        }

        return summary

    def print_results(
        self, summary: dict[str, Union[int, float, str, list[dict[str, str]]]]
    ) -> None:
        """Print validation results"""
        print("\n📊 VALIDATION RESULTS")
        print("=" * 60)
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Overall Status: {summary['overall_status']}")

        print("\n📋 DETAILED RESULTS")
        print("=" * 60)

        results = summary.get("results", [])
        if isinstance(results, list):
            for result in results:
                status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️"}.get(
                    result["status"], "?"
                )

                print(f"{status_icon} {result['check']}")
                if result["status"] != "PASS":
                    print(f"   {result['details']}")

        print("=" * 60)


def main() -> None:
    """Main validation function"""
    validator = DocumentationValidator()

    try:
        summary = validator.run_validation()
        validator.print_results(summary)

        if summary["overall_status"] == "PASS":
            print("\n🎉 All monitoring documentation validations PASSED!")
            print(
                "✅ Monitoring infrastructure documentation is complete and consistent."
            )
            exit(0)
        else:
            print("\n❌ Some monitoring documentation validations FAILED!")
            print(
                "Please review the failed checks and update documentation accordingly."
            )
            exit(1)

    except Exception as e:
        print(f"\n💥 Validation script error: {e!s}")
        exit(2)


if __name__ == "__main__":
    main()
