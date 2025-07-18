#!/usr/bin/env python3
"""
ACGS-PGP Resource Limits Validation Script
Validates that all services comply with standardized resource limits.

Standard Limits:
- CPU Request: 200m
- CPU Limit: 500m (1000m for PGC service)
- Memory Request: 512Mi
- Memory Limit: 1Gi (2Gi for AC, GS, PGC services)
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class ResourceLimits:
    """Standard resource limits for ACGS-PGP services."""

    cpu_request: str = "200m"
    cpu_limit: str = "500m"
    memory_request: str = "512Mi"
    memory_limit: str = "1Gi"

    # Service-specific overrides
    high_performance_services = ["ac_service", "gs_service", "pgc_service"]
    pgc_cpu_limit: str = "1000m"
    high_memory_limit: str = "2Gi"


@dataclass
class ValidationResult:
    """Resource validation result."""

    service_name: str
    file_path: str
    compliant: bool
    issues: list[str]
    current_limits: dict[str, str]
    expected_limits: dict[str, str]


class ResourceLimitsValidator:
    """Validates resource limits across ACGS-PGP services."""

    def __init__(self, project_root: str = "/home/ubuntu/ACGS"):
        self.project_root = Path(project_root)
        self.standard_limits = ResourceLimits()
        self.validation_results: list[ValidationResult] = []

    def get_expected_limits(self, service_name: str) -> dict[str, str]:
        """Get expected resource limits for a service."""
        limits = {
            "cpu_request": self.standard_limits.cpu_request,
            "memory_request": self.standard_limits.memory_request,
        }

        if service_name == "pgc_service":
            limits["cpu_limit"] = self.standard_limits.pgc_cpu_limit
            limits["memory_limit"] = self.standard_limits.high_memory_limit
        elif service_name in self.standard_limits.high_performance_services:
            limits["cpu_limit"] = self.standard_limits.cpu_limit
            limits["memory_limit"] = self.standard_limits.high_memory_limit
        else:
            limits["cpu_limit"] = self.standard_limits.cpu_limit
            limits["memory_limit"] = self.standard_limits.memory_limit

        return limits

    def validate_kubernetes_deployment(self, file_path: Path) -> list[ValidationResult]:
        """Validate Kubernetes deployment resource limits."""
        results = []

        try:
            with open(file_path) as f:
                docs = list(yaml.safe_load_all(f))

            for doc in docs:
                if not doc or doc.get("kind") != "Deployment":
                    continue

                service_name = doc.get("metadata", {}).get("name", "unknown")
                containers = (
                    doc.get("spec", {})
                    .get("template", {})
                    .get("spec", {})
                    .get("containers", [])
                )

                for container in containers:
                    resources = container.get("resources", {})
                    requests = resources.get("requests", {})
                    limits = resources.get("limits", {})

                    current_limits = {
                        "cpu_request": requests.get("cpu", "not_set"),
                        "cpu_limit": limits.get("cpu", "not_set"),
                        "memory_request": requests.get("memory", "not_set"),
                        "memory_limit": limits.get("memory", "not_set"),
                    }

                    expected_limits = self.get_expected_limits(service_name)
                    issues = []

                    for limit_type, expected_value in expected_limits.items():
                        current_value = current_limits.get(limit_type, "not_set")
                        if current_value != expected_value:
                            issues.append(
                                f"{limit_type}: expected {expected_value}, got {current_value}"
                            )

                    results.append(
                        ValidationResult(
                            service_name=service_name,
                            file_path=str(file_path),
                            compliant=len(issues) == 0,
                            issues=issues,
                            current_limits=current_limits,
                            expected_limits=expected_limits,
                        )
                    )

        except Exception as e:
            results.append(
                ValidationResult(
                    service_name="unknown",
                    file_path=str(file_path),
                    compliant=False,
                    issues=[f"Failed to parse file: {e!s}"],
                    current_limits={},
                    expected_limits={},
                )
            )

        return results

    def validate_docker_compose(self, file_path: Path) -> list[ValidationResult]:
        """Validate Docker Compose resource limits."""
        results = []

        try:
            with open(file_path) as f:
                compose_data = yaml.safe_load(f)

            services = compose_data.get("services", {})

            for service_name, service_config in services.items():
                deploy_config = service_config.get("deploy", {})
                resources = deploy_config.get("resources", {})
                limits = resources.get("limits", {})
                reservations = resources.get("reservations", {})

                current_limits = {
                    "cpu_limit": limits.get("cpus", "not_set"),
                    "memory_limit": limits.get("memory", "not_set"),
                    "cpu_request": reservations.get("cpus", "not_set"),
                    "memory_request": reservations.get("memory", "not_set"),
                }

                expected_limits = self.get_expected_limits(service_name)
                issues = []

                # Docker Compose uses different format, so we need to convert
                for limit_type, expected_value in expected_limits.items():
                    current_value = current_limits.get(limit_type, "not_set")
                    if current_value == "not_set":
                        issues.append(f"{limit_type}: not configured")

                results.append(
                    ValidationResult(
                        service_name=service_name,
                        file_path=str(file_path),
                        compliant=len(issues) == 0,
                        issues=issues,
                        current_limits=current_limits,
                        expected_limits=expected_limits,
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    service_name="unknown",
                    file_path=str(file_path),
                    compliant=False,
                    issues=[f"Failed to parse file: {e!s}"],
                    current_limits={},
                    expected_limits={},
                )
            )

        return results

    def validate_all_configurations(self) -> list[ValidationResult]:
        """Validate all resource configurations in the project."""
        all_results = []

        # Find all Kubernetes deployment files
        k8s_files = list(self.project_root.rglob("**/k8s/**/*.yaml"))
        k8s_files.extend(list(self.project_root.rglob("**/k8s/**/*.yml")))

        for k8s_file in k8s_files:
            if "deployment" in k8s_file.name.lower():
                results = self.validate_kubernetes_deployment(k8s_file)
                all_results.extend(results)

        # Find all Docker Compose files
        compose_files = list(self.project_root.rglob("**/docker-compose*.yml"))
        compose_files.extend(list(self.project_root.rglob("**/docker-compose*.yaml")))

        for compose_file in compose_files:
            results = self.validate_docker_compose(compose_file)
            all_results.extend(results)

        self.validation_results = all_results
        return all_results

    def generate_report(self) -> str:
        """Generate a validation report."""
        if not self.validation_results:
            self.validate_all_configurations()

        compliant_count = sum(1 for r in self.validation_results if r.compliant)
        total_count = len(self.validation_results)

        report = f"""
ACGS-PGP Resource Limits Validation Report
==========================================  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

Summary:
- Total configurations checked: {total_count}
- Compliant configurations: {compliant_count}
- Non-compliant configurations: {total_count - compliant_count}
- Compliance rate: {(compliant_count / total_count * 100):.1f}%

Standard Resource Limits:
- CPU Request: {self.standard_limits.cpu_request}
- CPU Limit: {self.standard_limits.cpu_limit} (1000m for PGC service)
- Memory Request: {self.standard_limits.memory_request}
- Memory Limit: {self.standard_limits.memory_limit} (2Gi for AC, GS, PGC services)

Detailed Results:
"""

        for result in self.validation_results:
            status = "✅ COMPLIANT" if result.compliant else "❌ NON-COMPLIANT"
            report += f"\n{status} - {result.service_name} ({result.file_path})\n"

            if result.issues:
                for issue in result.issues:
                    report += f"  - {issue}\n"

        return report


def main():
    """Main validation function."""
    validator = ResourceLimitsValidator()
    results = validator.validate_all_configurations()

    report = validator.generate_report()
    print(report)

    # Exit with error code if any configurations are non-compliant
    non_compliant = [r for r in results if not r.compliant]
    if non_compliant:
        print(f"\n❌ {len(non_compliant)} configurations are non-compliant!")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(results)} configurations are compliant!")
        sys.exit(0)


if __name__ == "__main__":
    main()
