#!/usr/bin/env python3
"""
ACGS-1 Security Policy Enforcement Script

This script enforces security policies across the ACGS-1 codebase and infrastructure.
It validates configurations, checks for security violations, and generates reports.
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityViolation:
    """Represents a security policy violation."""

    rule: str
    severity: str
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str


class SecurityPolicyEnforcer:
    """Main class for enforcing security policies."""

    def __init__(self, config_path: str = "config/security/security-config.yml"):
        """Initialize the security policy enforcer."""
        self.config_path = config_path
        self.config = self._load_config()
        self.violations: List[SecurityViolation] = []

    def _load_config(self) -> Dict[str, Any]:
        """Load security configuration from YAML file."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Security config file not found: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing security config: {e}")
            return {}

    def check_dockerfile_security(self) -> None:
        """Check Dockerfile security best practices."""
        logger.info("Checking Dockerfile security policies...")

        dockerfile_patterns = ["**/Dockerfile*", "**/dockerfile*"]
        dockerfiles = []

        for pattern in dockerfile_patterns:
            dockerfiles.extend(Path(".").glob(pattern))

        for dockerfile in dockerfiles:
            self._check_single_dockerfile(dockerfile)

    def _check_single_dockerfile(self, dockerfile_path: Path) -> None:
        """Check security policies for a single Dockerfile."""
        try:
            with open(dockerfile_path, "r") as f:
                content = f.read()
                lines = content.splitlines()

            # Check for USER instruction
            if not any("USER" in line for line in lines):
                self.violations.append(
                    SecurityViolation(
                        rule="docker_user_required",
                        severity="high",
                        file_path=str(dockerfile_path),
                        line_number=None,
                        description="Dockerfile does not specify USER instruction",
                        recommendation="Add USER instruction to avoid running as root",
                    )
                )

            # Check for latest tags
            for i, line in enumerate(lines, 1):
                if ":latest" in line and "FROM" in line:
                    self.violations.append(
                        SecurityViolation(
                            rule="docker_no_latest_tags",
                            severity="medium",
                            file_path=str(dockerfile_path),
                            line_number=i,
                            description="Using :latest tag in FROM instruction",
                            recommendation="Pin to specific version instead of :latest",
                        )
                    )

                # Check for ADD vs COPY
                if line.strip().startswith("ADD "):
                    self.violations.append(
                        SecurityViolation(
                            rule="docker_prefer_copy",
                            severity="low",
                            file_path=str(dockerfile_path),
                            line_number=i,
                            description="Using ADD instead of COPY",
                            recommendation="Use COPY instead of ADD unless you need ADD's features",
                        )
                    )

        except Exception as e:
            logger.error(f"Error checking {dockerfile_path}: {e}")

    def check_environment_files(self) -> None:
        """Check environment files for security issues."""
        logger.info("Checking environment files for security issues...")

        env_files = list(Path(".").glob("**/*.env")) + list(Path(".").glob("**/.*env*"))

        for env_file in env_files:
            self._check_single_env_file(env_file)

    def _check_single_env_file(self, env_file_path: Path) -> None:
        """Check security policies for a single environment file."""
        try:
            with open(env_file_path, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Check for hardcoded secrets
                if any(
                    keyword in line.lower()
                    for keyword in ["password", "secret", "key", "token"]
                ):
                    if (
                        "=" in line
                        and not line.endswith("${")
                        and not line.endswith("}")
                    ):
                        value = line.split("=", 1)[1].strip()
                        if value and not value.startswith("${") and len(value) > 5:
                            self.violations.append(
                                SecurityViolation(
                                    rule="no_hardcoded_secrets",
                                    severity="critical",
                                    file_path=str(env_file_path),
                                    line_number=i,
                                    description="Potential hardcoded secret in environment file",
                                    recommendation="Use environment variable substitution or secret management",
                                )
                            )

        except Exception as e:
            logger.error(f"Error checking {env_file_path}: {e}")

    def check_docker_compose_security(self) -> None:
        """Check Docker Compose files for security issues."""
        logger.info("Checking Docker Compose security policies...")

        compose_files = list(Path(".").glob("**/docker-compose*.yml")) + list(
            Path(".").glob("**/docker-compose*.yaml")
        )

        for compose_file in compose_files:
            self._check_single_compose_file(compose_file)

    def _check_single_compose_file(self, compose_file_path: Path) -> None:
        """Check security policies for a single Docker Compose file."""
        try:
            with open(compose_file_path, "r") as f:
                compose_data = yaml.safe_load(f)

            if "services" not in compose_data:
                return

            for service_name, service_config in compose_data["services"].items():
                # Check for privileged containers
                if service_config.get("privileged", False):
                    self.violations.append(
                        SecurityViolation(
                            rule="docker_no_privileged",
                            severity="high",
                            file_path=str(compose_file_path),
                            line_number=None,
                            description=f"Service '{service_name}' runs in privileged mode",
                            recommendation="Remove privileged: true unless absolutely necessary",
                        )
                    )

                # Check for host network mode
                if service_config.get("network_mode") == "host":
                    self.violations.append(
                        SecurityViolation(
                            rule="docker_no_host_network",
                            severity="medium",
                            file_path=str(compose_file_path),
                            line_number=None,
                            description=f"Service '{service_name}' uses host network mode",
                            recommendation="Use bridge network mode instead of host",
                        )
                    )

                # Check for missing health checks
                if "healthcheck" not in service_config:
                    self.violations.append(
                        SecurityViolation(
                            rule="docker_require_healthcheck",
                            severity="low",
                            file_path=str(compose_file_path),
                            line_number=None,
                            description=f"Service '{service_name}' missing health check",
                            recommendation="Add healthcheck configuration for better monitoring",
                        )
                    )

        except Exception as e:
            logger.error(f"Error checking {compose_file_path}: {e}")

    def check_kubernetes_security(self) -> None:
        """Check Kubernetes manifests for security issues."""
        logger.info("Checking Kubernetes security policies...")

        k8s_files = (
            list(Path(".").glob("**/kubernetes/**/*.yml"))
            + list(Path(".").glob("**/kubernetes/**/*.yaml"))
            + list(Path(".").glob("**/k8s/**/*.yml"))
            + list(Path(".").glob("**/k8s/**/*.yaml"))
        )

        for k8s_file in k8s_files:
            self._check_single_k8s_file(k8s_file)

    def _check_single_k8s_file(self, k8s_file_path: Path) -> None:
        """Check security policies for a single Kubernetes manifest."""
        try:
            with open(k8s_file_path, "r") as f:
                # Handle multiple YAML documents in one file
                documents = yaml.safe_load_all(f)

                for doc in documents:
                    if not doc or "kind" not in doc:
                        continue

                    if doc["kind"] in ["Deployment", "Pod", "DaemonSet", "StatefulSet"]:
                        self._check_k8s_pod_security(doc, k8s_file_path)

        except Exception as e:
            logger.error(f"Error checking {k8s_file_path}: {e}")

    def _check_k8s_pod_security(
        self, manifest: Dict[str, Any], file_path: Path
    ) -> None:
        """Check pod security policies."""
        spec = manifest.get("spec", {})

        # For Deployment, StatefulSet, DaemonSet, get the pod template
        if "template" in spec:
            pod_spec = spec["template"].get("spec", {})
        else:
            pod_spec = spec

        # Check for security context
        if "securityContext" not in pod_spec:
            self.violations.append(
                SecurityViolation(
                    rule="k8s_require_security_context",
                    severity="medium",
                    file_path=str(file_path),
                    line_number=None,
                    description="Pod missing security context",
                    recommendation="Add securityContext to pod specification",
                )
            )

        # Check containers
        containers = pod_spec.get("containers", [])
        for container in containers:
            # Check for privileged containers
            security_context = container.get("securityContext", {})
            if security_context.get("privileged", False):
                self.violations.append(
                    SecurityViolation(
                        rule="k8s_no_privileged_containers",
                        severity="high",
                        file_path=str(file_path),
                        line_number=None,
                        description=f"Container '{container.get('name', 'unknown')}' runs privileged",
                        recommendation="Remove privileged: true from container security context",
                    )
                )

            # Check for root user
            if security_context.get("runAsUser") == 0:
                self.violations.append(
                    SecurityViolation(
                        rule="k8s_no_root_user",
                        severity="medium",
                        file_path=str(file_path),
                        line_number=None,
                        description=f"Container '{container.get('name', 'unknown')}' runs as root",
                        recommendation="Set runAsUser to non-zero value",
                    )
                )

    def run_dependency_checks(self) -> None:
        """Run dependency vulnerability checks."""
        logger.info("Running dependency vulnerability checks...")

        # Check Python dependencies
        if Path("requirements.txt").exists() or Path("pyproject.toml").exists():
            self._run_python_dependency_check()

        # Check Node.js dependencies
        if Path("package.json").exists():
            self._run_nodejs_dependency_check()

        # Check Rust dependencies
        if Path("Cargo.toml").exists() or Path("blockchain/Cargo.toml").exists():
            self._run_rust_dependency_check()

    def _run_python_dependency_check(self) -> None:
        """Run Python dependency vulnerability check."""
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.violations.append(
                    SecurityViolation(
                        rule="python_vulnerable_dependencies",
                        severity="high",
                        file_path="requirements.txt",
                        line_number=None,
                        description="Vulnerable Python dependencies detected",
                        recommendation="Update vulnerable dependencies to secure versions",
                    )
                )

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Could not run Python dependency check")

    def _run_nodejs_dependency_check(self) -> None:
        """Run Node.js dependency vulnerability check."""
        try:
            result = subprocess.run(
                ["npm", "audit", "--audit-level=high"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.violations.append(
                    SecurityViolation(
                        rule="nodejs_vulnerable_dependencies",
                        severity="high",
                        file_path="package.json",
                        line_number=None,
                        description="Vulnerable Node.js dependencies detected",
                        recommendation="Run 'npm audit fix' to update vulnerable dependencies",
                    )
                )

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Could not run Node.js dependency check")

    def _run_rust_dependency_check(self) -> None:
        """Run Rust dependency vulnerability check."""
        try:
            # Check if we're in blockchain directory or if it exists
            cargo_dir = "blockchain" if Path("blockchain/Cargo.toml").exists() else "."

            result = subprocess.run(
                ["cargo", "audit"],
                cwd=cargo_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.violations.append(
                    SecurityViolation(
                        rule="rust_vulnerable_dependencies",
                        severity="high",
                        file_path=f"{cargo_dir}/Cargo.toml",
                        line_number=None,
                        description="Vulnerable Rust dependencies detected",
                        recommendation="Update vulnerable dependencies to secure versions",
                    )
                )

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Could not run Rust dependency check")

    def generate_report(self, output_format: str = "json") -> str:
        """Generate security policy enforcement report."""
        report_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_violations": len(self.violations),
            "violations_by_severity": {
                "critical": len(
                    [v for v in self.violations if v.severity == "critical"]
                ),
                "high": len([v for v in self.violations if v.severity == "high"]),
                "medium": len([v for v in self.violations if v.severity == "medium"]),
                "low": len([v for v in self.violations if v.severity == "low"]),
            },
            "violations": [
                {
                    "rule": v.rule,
                    "severity": v.severity,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "description": v.description,
                    "recommendation": v.recommendation,
                }
                for v in self.violations
            ],
        }

        if output_format == "json":
            return json.dumps(report_data, indent=2)
        elif output_format == "yaml":
            return yaml.dump(report_data, default_flow_style=False)
        else:
            # Text format
            lines = [
                "ACGS-1 Security Policy Enforcement Report",
                "=" * 45,
                f"Generated: {report_data['timestamp']}",
                f"Total Violations: {report_data['total_violations']}",
                "",
                "Violations by Severity:",
                f"  Critical: {report_data['violations_by_severity']['critical']}",
                f"  High: {report_data['violations_by_severity']['high']}",
                f"  Medium: {report_data['violations_by_severity']['medium']}",
                f"  Low: {report_data['violations_by_severity']['low']}",
                "",
                "Detailed Violations:",
                "-" * 20,
            ]

            for violation in self.violations:
                lines.extend(
                    [
                        f"Rule: {violation.rule}",
                        f"Severity: {violation.severity.upper()}",
                        f"File: {violation.file_path}",
                        f"Line: {violation.line_number or 'N/A'}",
                        f"Description: {violation.description}",
                        f"Recommendation: {violation.recommendation}",
                        "",
                    ]
                )

            return "\n".join(lines)

    def run_all_checks(self) -> None:
        """Run all security policy checks."""
        logger.info("Starting comprehensive security policy enforcement...")

        self.check_dockerfile_security()
        self.check_environment_files()
        self.check_docker_compose_security()
        self.check_kubernetes_security()
        self.run_dependency_checks()

        logger.info(
            f"Security policy enforcement completed. Found {len(self.violations)} violations."
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ACGS-1 Security Policy Enforcement")
    parser.add_argument(
        "--config",
        default="config/security/security-config.yml",
        help="Path to security configuration file",
    )
    parser.add_argument(
        "--output",
        choices=["json", "yaml", "text"],
        default="text",
        help="Output format for the report",
    )
    parser.add_argument("--output-file", help="Output file for the report")
    parser.add_argument(
        "--fail-on-violations",
        action="store_true",
        help="Exit with non-zero code if violations are found",
    )

    args = parser.parse_args()

    # Initialize enforcer
    enforcer = SecurityPolicyEnforcer(args.config)

    # Run all checks
    enforcer.run_all_checks()

    # Generate report
    report = enforcer.generate_report(args.output)

    # Output report
    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(report)
        logger.info(f"Report written to {args.output_file}")
    else:
        print(report)

    # Exit with appropriate code
    if args.fail_on_violations and enforcer.violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
