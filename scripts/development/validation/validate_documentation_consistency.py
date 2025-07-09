#!/usr/bin/env python3
"""
ACGS Documentation Consistency Validation Tool

This script validates consistency across all ACGS documentation files including:
- Port number consistency
- Performance target alignment
- Constitutional hash validation
- Test coverage target consistency
- Service endpoint validation

Usage:
    python tools/validation/validate_documentation_consistency.py
    python tools/validation/validate_documentation_consistency.py --fix
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Represents the result of a validation check"""

    check_name: str
    passed: bool
    message: str
    files_checked: list[str]
    issues_found: list[str]


class ACGSDocumentationValidator:
    """Main validation class for ACGS documentation consistency"""

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.production_ports = {
            "postgresql": 5439,
            "redis": 6389,
            "auth_service": 8016,
            "constitutional_ai": 8001,
            "integrity_service": 8002,
            "formal_verification": 8003,
            "governance_synthesis": 8004,
            "policy_governance": 8005,
            "evolutionary_computation": 8006,
        }
        self.performance_targets = {
            "throughput": "≥100 RPS",
            "latency": "≤5ms",
            "cache_hit_rate": "≥85%",
            "test_coverage": "≥80%",
            "availability": "≥99.9%",
        }

    def validate_constitutional_hash(self) -> ValidationResult:
        """Validate constitutional hash consistency across all files"""
        print("🔍 Validating constitutional hash consistency...")

        files_with_hash = []
        files_missing_hash = []
        files_checked = []

        # Documentation files to check
        doc_patterns = [
            "docs/**/*.md",
            "README.md",
            "infrastructure/docker/docker-compose.acgs.yml",
            "services/**/config/*.yml",
            "services/**/config/*.yaml",
        ]

        for pattern in doc_patterns:
            for file_path in self.repo_root.glob(pattern):
                if file_path.is_file():
                    files_checked.append(str(file_path.relative_to(self.repo_root)))
                    content = file_path.read_text(encoding="utf-8", errors="ignore")

                    if self.constitutional_hash in content:
                        files_with_hash.append(
                            str(file_path.relative_to(self.repo_root))
                        )
                    elif (
                        "constitutional" in content.lower()
                        and "hash" in content.lower()
                    ):
                        files_missing_hash.append(
                            str(file_path.relative_to(self.repo_root))
                        )

        # Check critical files specifically
        critical_files = [
            "docs/configuration/README.md",
            "docs/api/index.md",
            "infrastructure/docker/docker-compose.acgs.yml",
        ]

        missing_critical = []
        for critical_file in critical_files:
            file_path = self.repo_root / critical_file
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if self.constitutional_hash not in content:
                    missing_critical.append(critical_file)

        passed = len(missing_critical) == 0 and len(files_missing_hash) == 0
        message = f"Constitutional hash found in {len(files_with_hash)} files"

        issues = []
        if missing_critical:
            issues.extend(
                [f"Critical file missing hash: {f}" for f in missing_critical]
            )
        if files_missing_hash:
            issues.extend(
                [
                    f"File mentions constitutional hash but missing value: {f}"
                    for f in files_missing_hash
                ]
            )

        return ValidationResult(
            check_name="Constitutional Hash Consistency",
            passed=passed,
            message=message,
            files_checked=files_checked,
            issues_found=issues,
        )

    def validate_port_consistency(self) -> ValidationResult:
        """Validate port consistency across documentation and configuration"""
        print("🔍 Validating port consistency...")

        files_checked = []
        issues = []

        # Check docker-compose file
        compose_file = self.repo_root / "infrastructure/docker/docker-compose.acgs.yml"
        if compose_file.exists():
            files_checked.append(str(compose_file.relative_to(self.repo_root)))
            content = compose_file.read_text()

            # Check port mappings
            expected_mappings = [
                ("PostgreSQL", "5439:5432"),
                ("Redis", "6389:6379"),
                ("Auth Service", "8016:8016"),
            ]

            for service, mapping in expected_mappings:
                if mapping not in content:
                    issues.append(
                        f"{service} port mapping incorrect (should be {mapping})"
                    )
        else:
            issues.append(
                "Docker compose file not found:"
                " infrastructure/docker/docker-compose.acgs.yml"
            )

        # Check documentation consistency
        doc_files = [
            "README.md",
            "docs/configuration/README.md",
            "docs/operations/SERVICE_STATUS.md",
        ]

        for doc_file in doc_files:
            file_path = self.repo_root / doc_file
            if file_path.exists():
                files_checked.append(doc_file)
                content = file_path.read_text()

                # Check for production ports
                for service, port in self.production_ports.items():
                    if service in ["postgresql", "redis", "auth_service"]:
                        if str(port) not in content:
                            issues.append(
                                f"Port {port} for {service} not found in {doc_file}"
                            )

        passed = len(issues) == 0
        message = f"Checked {len(files_checked)} files for port consistency"

        return ValidationResult(
            check_name="Port Consistency",
            passed=passed,
            message=message,
            files_checked=files_checked,
            issues_found=issues,
        )

    def validate_performance_targets(self) -> ValidationResult:
        """Validate performance targets consistency"""
        print("🔍 Validating performance targets consistency...")

        files_checked = []
        issues = []

        # Files that should contain performance targets
        target_files = [
            "README.md",
            "docs/configuration/README.md",
            "docs/operations/SERVICE_STATUS.md",
        ]

        for file_name in target_files:
            file_path = self.repo_root / file_name
            if file_path.exists():
                files_checked.append(file_name)
                content = file_path.read_text()

                # Check for specific performance targets
                target_checks = [
                    ("Throughput", ["≥100", "RPS", "requests"]),
                    ("Latency", ["≤5ms", "P99", "5ms"]),
                    ("Cache Hit Rate", ["≥85%", "cache", "hit"]),
                    ("Test Coverage", ["≥80%", "80%", "coverage"]),
                ]

                for target_name, keywords in target_checks:
                    if not any(keyword in content for keyword in keywords):
                        issues.append(
                            f"Performance target '{target_name}' not found in"
                            f" {file_name}"
                        )

        passed = len(issues) == 0
        message = f"Checked {len(files_checked)} files for performance targets"

        return ValidationResult(
            check_name="Performance Targets Consistency",
            passed=passed,
            message=message,
            files_checked=files_checked,
            issues_found=issues,
        )

    def validate_test_coverage_targets(self) -> ValidationResult:
        """Validate test coverage targets consistency"""
        print("🔍 Validating test coverage targets...")

        files_checked = []
        issues = []

        # Files that should have 80% coverage target
        coverage_files = [
            ("pytest.ini", ["--cov-fail-under=80", "80"]),
            ("pyproject.toml", ["fail_under = 80", "80"]),
            ("docs/configuration/README.md", ["80%", "coverage"]),
        ]

        for file_name, patterns in coverage_files:
            file_path = self.repo_root / file_name
            if file_path.exists():
                files_checked.append(file_name)
                content = file_path.read_text()

                if not any(pattern in content for pattern in patterns):
                    issues.append(f"80% test coverage target not found in {file_name}")

        passed = len(issues) == 0
        message = f"Checked {len(files_checked)} files for test coverage targets"

        return ValidationResult(
            check_name="Test Coverage Targets",
            passed=passed,
            message=message,
            files_checked=files_checked,
            issues_found=issues,
        )

    def validate_service_endpoints(self) -> ValidationResult:
        """Validate service endpoint documentation consistency"""
        print("🔍 Validating service endpoint consistency...")

        files_checked = []
        issues = []

        # Check API documentation
        api_files = list((self.repo_root / "docs/api").glob("*.md"))

        for api_file in api_files:
            files_checked.append(str(api_file.relative_to(self.repo_root)))
            content = api_file.read_text()

            # Check for constitutional hash in API responses
            if (
                "constitutional" in content.lower()
                and self.constitutional_hash not in content
            ):
                issues.append(
                    f"API file {api_file.name} missing constitutional hash in examples"
                )

            # Check for proper port references
            for service, port in self.production_ports.items():
                if f":{port}" in content and f"localhost:{port}" not in content:
                    # This might be okay, but flag for review
                    pass

        passed = len(issues) == 0
        message = f"Checked {len(files_checked)} API documentation files"

        return ValidationResult(
            check_name="Service Endpoints Consistency",
            passed=passed,
            message=message,
            files_checked=files_checked,
            issues_found=issues,
        )

    def run_all_validations(self) -> list[ValidationResult]:
        """Run all validation checks"""
        print("🚀 Starting ACGS documentation consistency validation...")
        print(f"Repository root: {self.repo_root}")
        print(f"Constitutional hash: {self.constitutional_hash}")
        print("=" * 60)

        validations = [
            self.validate_constitutional_hash(),
            self.validate_port_consistency(),
            self.validate_performance_targets(),
            self.validate_test_coverage_targets(),
            self.validate_service_endpoints(),
        ]

        return validations

    def generate_report(self, results: list[ValidationResult]) -> str:
        """Generate a comprehensive validation report"""
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)

        report = f"""
# ACGS Documentation Consistency Validation Report

**Date**: {self._get_timestamp()}
**Repository**: {self.repo_root}
**Constitutional Hash**: {self.constitutional_hash}

## Summary

**Overall Status**: {'✅ PASSED' if passed_count == total_count else '❌ FAILED'}
**Checks Passed**: {passed_count}/{total_count}

## Detailed Results

"""

        for result in results:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            report += f"### {result.check_name}\n\n"
            report += f"**Status**: {status}\n"
            report += f"**Message**: {result.message}\n"
            report += f"**Files Checked**: {len(result.files_checked)}\n"

            if result.issues_found:
                report += f"**Issues Found**: {len(result.issues_found)}\n"
                for issue in result.issues_found:
                    report += f"- {issue}\n"

            report += "\n"

        if passed_count == total_count:
            report += (
                "## ✅ Conclusion\n\nAll documentation consistency checks passed"
                " successfully. The documentation is ready for production deployment.\n"
            )
        else:
            report += (
                "## ❌ Action Required\n\nSome validation checks failed. Please review"
                " and fix the issues listed above before proceeding with deployment.\n"
            )

        return report

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="ACGS Documentation Consistency Validator"
    )
    parser.add_argument("--repo-root", type=Path, help="Repository root directory")
    parser.add_argument("--output", type=Path, help="Output file for validation report")
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    args = parser.parse_args()

    # Initialize validator
    validator = ACGSDocumentationValidator(args.repo_root)

    # Run validations
    results = validator.run_all_validations()

    # Generate report
    if args.json:
        # JSON output for CI/CD integration
        json_results = {
            "timestamp": validator._get_timestamp(),
            "constitutional_hash": validator.constitutional_hash,
            "summary": {
                "total_checks": len(results),
                "passed_checks": sum(1 for r in results if r.passed),
                "overall_status": (
                    "PASSED" if all(r.passed for r in results) else "FAILED"
                ),
            },
            "results": [
                {
                    "check_name": r.check_name,
                    "passed": r.passed,
                    "message": r.message,
                    "files_checked": r.files_checked,
                    "issues_found": r.issues_found,
                }
                for r in results
            ],
        }

        if args.output:
            args.output.write_text(json.dumps(json_results, indent=2))
        else:
            print(json.dumps(json_results, indent=2))
    else:
        # Markdown report
        report = validator.generate_report(results)

        if args.output:
            args.output.write_text(report)
            print(f"📋 Validation report saved to: {args.output}")
        else:
            print(report)

    # Print summary to console
    print("\n" + "=" * 60)
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)

    if passed_count == total_count:
        print("✅ All documentation consistency checks PASSED!")
        return 0
    else:
        print(
            "❌ Documentation consistency validation FAILED!"
            f" ({passed_count}/{total_count} checks passed)"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
