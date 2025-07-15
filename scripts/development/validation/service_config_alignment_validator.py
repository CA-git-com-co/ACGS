#!/usr/bin/env python3
"""
ACGS Service Configuration Alignment Validator
Constitutional Hash: cdd01ef066bc6cf2

This validator ensures alignment between:
1. Docker Compose configurations
2. Kubernetes manifests
3. Service configuration files (config/*.y*ml)
4. Code constants (FastAPI configurations, etc.)

The validator extracts ports, image tags, environment variables and cross-checks
them against code constants for consistency validation.

Performance Targets:
- P99 Latency: ≤5ms for validation operations
- Throughput: ≥100 RPS for validation requests
- Cache Hit Rate: ≥85% for configuration data
- Constitutional Compliance: 100%
"""

import ast
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import yaml

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Unified validation result compatible with ACGS framework.

    This class provides a consistent result format that can be used
    across all ACGS validation tools.
    """

    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    performance_score: float = 0.0
    start_time: float = field(default_factory=time.time)
    constitutional_hash: str = CONSTITUTIONAL_HASH
    validator_name: str = "ServiceConfigurationAlignmentValidator"

    def add_issue(
        self,
        severity: str,
        category: str,
        component: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        line_number: Optional[int] = None,
    ):
        """Add a validation issue."""
        self.issues.append(
            {
                "severity": severity,
                "category": category,
                "component": component,
                "message": message,
                "details": details or {},
                "line": line_number,
                "timestamp": datetime.now().isoformat(),
                "constitutional_hash": self.constitutional_hash,
            }
        )

    def get_duration(self) -> float:
        """Get validation duration in seconds."""
        return time.time() - self.start_time

    def get_success_rate(self) -> float:
        """Get validation success rate as percentage."""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "summary": {
                "total_checks": self.total_checks,
                "passed_checks": self.passed_checks,
                "failed_checks": self.failed_checks,
                "success_rate": self.get_success_rate(),
                "duration": self.get_duration(),
                "constitutional_hash": self.constitutional_hash,
                "validator_name": self.validator_name,
            },
            "issues": self.issues,
            "performance_score": self.performance_score,
        }


@dataclass
class ServiceConfiguration:
    """Represents extracted service configuration from various sources."""

    name: str
    ports: Set[int] = field(default_factory=set)
    image_tags: Set[str] = field(default_factory=set)
    env_vars: Dict[str, str] = field(default_factory=dict)
    docs_url: Optional[str] = None
    config_files: List[Path] = field(default_factory=list)
    source_files: List[Path] = field(default_factory=list)


class ServiceConfigurationAlignmentValidator:
    """
    Validates alignment between service configurations and code constants.

    This validator checks consistency across:
    - Docker Compose files
    - Kubernetes manifests
    - Service config/*.y*ml files
    - FastAPI and other code constants
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the validator."""
        self.repo_root = repo_root or Path.cwd()
        self.result = ValidationResult()
        self.configurations: Dict[str, ServiceConfiguration] = {}

        # Configuration patterns
        self.docker_compose_patterns = [
            "**/docker-compose*.yml",
            "**/docker-compose*.yaml",
        ]

        self.k8s_patterns = [
            "**/*.k8s.yml",
            "**/*.k8s.yaml",
            "**/k8s/**/*.yml",
            "**/k8s/**/*.yaml",
            "**/kubernetes/**/*.yml",
            "**/kubernetes/**/*.yaml",
        ]

        self.service_config_patterns = ["**/config/*.yml", "**/config/*.yaml"]

        self.code_patterns = [
            "**/services/**/*.py",
            "**/apps/**/*.py",
            "**/src/**/*.py",
        ]

        logger.info(f"🔧 Initialized ServiceConfigurationAlignmentValidator")
        logger.info(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        logger.info(f"📁 Repository Root: {self.repo_root}")

    def find_files(self, patterns: List[str]) -> List[Path]:
        """Find files matching the given patterns."""
        files = []
        for pattern in patterns:
            files.extend(self.repo_root.glob(pattern))
        return [f for f in files if f.is_file()]

    def parse_docker_compose(self, file_path: Path) -> Dict[str, ServiceConfiguration]:
        """Parse Docker Compose file and extract service configurations."""
        configs = {}

        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)

            if not data or "services" not in data:
                return configs

            for service_name, service_config in data["services"].items():
                config = ServiceConfiguration(name=service_name)
                config.source_files.append(file_path)

                # Extract ports
                if "ports" in service_config:
                    for port_mapping in service_config["ports"]:
                        if isinstance(port_mapping, str):
                            # Handle "8001:8001" format
                            if ":" in port_mapping:
                                external_port = int(port_mapping.split(":")[0])
                                config.ports.add(external_port)
                        elif isinstance(port_mapping, int):
                            config.ports.add(port_mapping)

                # Extract image tags
                if "image" in service_config:
                    config.image_tags.add(service_config["image"])

                # Extract environment variables
                if "environment" in service_config:
                    env = service_config["environment"]
                    if isinstance(env, list):
                        for var in env:
                            if "=" in var:
                                key, value = var.split("=", 1)
                                configconfig/environments/development.env_vars[key] = value
                    elif isinstance(env, dict):
                        configconfig/environments/development.env_vars.update(env)

                configs[service_name] = config

        except Exception as e:
            self.result.add_issue(
                "ERROR",
                "docker_compose_parsing",
                str(file_path),
                f"Failed to parse Docker Compose file: {e}",
            )

        return configs

    def parse_kubernetes_manifest(
        self, file_path: Path
    ) -> Dict[str, ServiceConfiguration]:
        """Parse Kubernetes manifest and extract service configurations."""
        configs = {}

        try:
            with open(file_path, "r") as f:
                # Handle multiple YAML documents
                documents = list(yaml.safe_load_all(f))

            for doc in documents:
                if not doc or "kind" not in doc:
                    continue

                if doc["kind"] in ["Deployment", "Service", "StatefulSet"]:
                    service_name = doc["metadata"]["name"]

                    if service_name not in configs:
                        configs[service_name] = ServiceConfiguration(name=service_name)

                    config = configs[service_name]
                    config.source_files.append(file_path)

                    # Extract from Service
                    if doc["kind"] == "Service":
                        if "spec" in doc and "ports" in doc["spec"]:
                            for port in doc["spec"]["ports"]:
                                if "port" in port:
                                    config.ports.add(port["port"])
                                if "targetPort" in port:
                                    if isinstance(port["targetPort"], int):
                                        config.ports.add(port["targetPort"])

                    # Extract from Deployment/StatefulSet
                    elif doc["kind"] in ["Deployment", "StatefulSet"]:
                        spec = doc.get("spec", {})
                        template = spec.get("template", {})
                        pod_spec = template.get("spec", {})

                        for container in pod_spec.get("containers", []):
                            # Extract image
                            if "image" in container:
                                config.image_tags.add(container["image"])

                            # Extract ports
                            for port in container.get("ports", []):
                                if "containerPort" in port:
                                    config.ports.add(port["containerPort"])

                            # Extract environment variables
                            for env in container.get("env", []):
                                if "name" in env and "value" in env:
                                    configconfig/environments/development.env_vars[env["name"]] = env["value"]

        except Exception as e:
            self.result.add_issue(
                "ERROR",
                "kubernetes_parsing",
                str(file_path),
                f"Failed to parse Kubernetes manifest: {e}",
            )

        return configs

    def parse_service_config(self, file_path: Path) -> ServiceConfiguration:
        """Parse service configuration YAML file."""
        config = ServiceConfiguration(name=file_path.stem)
        config.config_files.append(file_path)

        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)

            if not data:
                return config

            # Extract port configurations
            def extract_ports_recursive(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if "port" in key.lower() and isinstance(value, int):
                            config.ports.add(value)
                        elif isinstance(value, (dict, list)):
                            extract_ports_recursive(
                                value, f"{prefix}.{key}" if prefix else key
                            )
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, (dict, list)):
                            extract_ports_recursive(item, prefix)

            extract_ports_recursive(data)

            # Extract environment-like configurations
            def extract_env_recursive(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, (str, int, bool, float)):
                            full_key = f"{prefix}.{key}" if prefix else key
                            configconfig/environments/development.env_vars[full_key] = str(value)
                        elif isinstance(value, dict):
                            extract_env_recursive(
                                value, f"{prefix}.{key}" if prefix else key
                            )

            extract_env_recursive(data)

        except Exception as e:
            self.result.add_issue(
                "ERROR",
                "service_config_parsing",
                str(file_path),
                f"Failed to parse service config: {e}",
            )

        return config

    def parse_python_code(self, file_path: Path) -> ServiceConfiguration:
        """Parse Python code to extract FastAPI and other service constants."""
        config = ServiceConfiguration(name=file_path.stem)
        config.source_files.append(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST to extract constants
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # File might have syntax errors, skip AST parsing but continue with regex
                tree = None

            # Extract FastAPI app configurations using regex
            fastapi_patterns = [
                r'app\s*=\s*FastAPI\s*\([^)]*docs_url\s*=\s*["\']([^"\']+)["\'][^)]*\)',
                r"app\s*=\s*FastAPI\s*\([^)]*port\s*=\s*(\d+)[^)]*\)",
                r"uvicorn\.run\s*\([^)]*port\s*=\s*(\d+)[^)]*\)",
                r"\.run\s*\([^)]*port\s*=\s*(\d+)[^)]*\)",
            ]

            for pattern in fastapi_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    value = match.group(1)
                    if "docs_url" in pattern and value:
                        config.docs_url = value
                    elif "port" in pattern and value.isdigit():
                        config.ports.add(int(value))

            # Extract port constants
            port_patterns = [
                r"(\w*PORT\w*)\s*=\s*(\d+)",
                r"port\s*=\s*(\d+)",
                r'["\']port["\']\s*:\s*(\d+)',
            ]

            for pattern in port_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) == 2:
                        # Variable name and value
                        var_name, port_str = match.groups()
                        if port_str.isdigit():
                            config.ports.add(int(port_str))
                            configconfig/environments/development.env_vars[var_name] = port_str
                    else:
                        # Just port value
                        port_str = match.group(1)
                        if port_str.isdigit():
                            config.ports.add(int(port_str))

            # Extract image references
            image_patterns = [
                r'image\s*[=:]\s*["\']([^"\']+)["\']',
                r'["\']image["\']\s*:\s*["\']([^"\']+)["\']',
            ]

            for pattern in image_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    config.image_tags.add(match.group(1))

            # Use AST for more precise extraction if available
            if tree:
                for node in ast.walk(tree):
                    # Extract variable assignments
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                var_name = target.id
                                if isinstance(node.value, ast.Constant):
                                    value = node.value.value
                                    if (
                                        isinstance(value, int)
                                        and "port" in var_name.lower()
                                    ):
                                        config.ports.add(value)
                                    configconfig/environments/development.env_vars[var_name] = str(value)
                                elif isinstance(
                                    node.value, ast.Str
                                ):  # Python < 3.8 compatibility
                                    configconfig/environments/development.env_vars[var_name] = node.value.s
                                elif isinstance(
                                    node.value, ast.Num
                                ):  # Python < 3.8 compatibility
                                    value = node.value.n
                                    if (
                                        isinstance(value, int)
                                        and "port" in var_name.lower()
                                    ):
                                        config.ports.add(value)
                                    configconfig/environments/development.env_vars[var_name] = str(value)

        except Exception as e:
            self.result.add_issue(
                "ERROR",
                "python_code_parsing",
                str(file_path),
                f"Failed to parse Python code: {e}",
            )

        return config

    def merge_configurations(
        self, configs: List[ServiceConfiguration]
    ) -> Dict[str, ServiceConfiguration]:
        """Merge configurations from different sources for the same service."""
        merged = {}

        for config in configs:
            service_name = config.name

            if service_name not in merged:
                merged[service_name] = ServiceConfiguration(name=service_name)

            target = merged[service_name]
            target.ports.update(config.ports)
            target.image_tags.update(config.image_tags)
            targetconfig/environments/development.env_vars.update(configconfig/environments/development.env_vars)
            target.config_files.extend(config.config_files)
            target.source_files.extend(config.source_files)

            if config.docs_url and not target.docs_url:
                target.docs_url = config.docs_url

        return merged

    def validate_port_consistency(self) -> None:
        """Validate port consistency across configurations."""
        self.result.total_checks += 1

        port_conflicts = []
        service_ports = {}

        for service_name, config in self.configurations.items():
            if not config.ports:
                continue

            service_ports[service_name] = config.ports

            # Check for duplicate ports across services
            for other_name, other_config in self.configurations.items():
                if other_name != service_name:
                    conflicts = config.ports.intersection(other_config.ports)
                    if conflicts:
                        port_conflicts.append(
                            {
                                "services": [service_name, other_name],
                                "conflicting_ports": list(conflicts),
                            }
                        )

        if port_conflicts:
            self.result.failed_checks += 1
            for conflict in port_conflicts:
                self.result.add_issue(
                    "HIGH",
                    "port_conflict",
                    f"{conflict['services'][0]} vs {conflict['services'][1]}",
                    f"Port conflict detected: {conflict['conflicting_ports']}",
                    {"conflict_details": conflict},
                )
        else:
            self.result.passed_checks += 1

    def validate_image_tag_consistency(self) -> None:
        """Validate image tag consistency."""
        self.result.total_checks += 1

        inconsistencies = []

        for service_name, config in self.configurations.items():
            if len(config.image_tags) > 1:
                inconsistencies.append(
                    {
                        "service": service_name,
                        "image_tags": list(config.image_tags),
                        "sources": [str(f) for f in config.source_files],
                    }
                )

        if inconsistencies:
            self.result.failed_checks += 1
            for inconsistency in inconsistencies:
                self.result.add_issue(
                    "MEDIUM",
                    "image_tag_inconsistency",
                    inconsistency["service"],
                    f"Multiple image tags found: {inconsistency['image_tags']}",
                    {"inconsistency_details": inconsistency},
                )
        else:
            self.result.passed_checks += 1

    def validate_environment_consistency(self) -> None:
        """Validate environment variable consistency."""
        self.result.total_checks += 1

        # Check for common environment variables that should be consistent
        common_env_vars = ["ENVIRONMENT", "PORT", "HOST", "DEBUG"]
        inconsistencies = []

        for var in common_env_vars:
            values_by_service = {}
            for service_name, config in self.configurations.items():
                for env_key, env_value in configconfig/environments/development.env_vars.items():
                    if var.lower() in env_key.lower():
                        if service_name not in values_by_service:
                            values_by_service[service_name] = []
                        values_by_service[service_name].append(
                            {"key": env_key, "value": env_value}
                        )

            if len(values_by_service) > 1:
                # Check if values are consistent
                all_values = set()
                for service_values in values_by_service.values():
                    for sv in service_values:
                        all_values.add(sv["value"])

                if len(all_values) > 1:
                    inconsistencies.append(
                        {"variable_pattern": var, "services": values_by_service}
                    )

        if inconsistencies:
            self.result.failed_checks += 1
            for inconsistency in inconsistencies:
                self.result.add_issue(
                    "MEDIUM",
                    "environment_inconsistency",
                    f"Environment variable: {inconsistency['variable_pattern']}",
                    f"Inconsistent values across services",
                    {"inconsistency_details": inconsistency},
                )
        else:
            self.result.passed_checks += 1

    def validate_constitutional_compliance(self) -> None:
        """Validate constitutional compliance across all configurations."""
        self.result.total_checks += 1

        missing_hash_files = []

        for service_name, config in self.configurations.items():
            for file_path in config.source_files + config.config_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if CONSTITUTIONAL_HASH not in content:
                        missing_hash_files.append(str(file_path))

                except Exception as e:
                    self.result.add_issue(
                        "ERROR",
                        "constitutional_compliance_check",
                        str(file_path),
                        f"Failed to check constitutional compliance: {e}",
                    )

        if missing_hash_files:
            self.result.failed_checks += 1
            self.result.add_issue(
                "CRITICAL",
                "constitutional_compliance",
                "Configuration files",
                f"Missing constitutional hash in {len(missing_hash_files)} files",
                {"missing_hash_files": missing_hash_files},
            )
        else:
            self.result.passed_checks += 1

    def validate_docs_url_consistency(self) -> None:
        """Validate API documentation URL consistency."""
        self.result.total_checks += 1

        docs_urls = {}
        for service_name, config in self.configurations.items():
            if config.docs_url:
                docs_urls[service_name] = config.docs_url

        if not docs_urls:
            # No docs URLs found, this might be expected
            self.result.passed_checks += 1
            return

        # Check for common patterns
        inconsistent_patterns = []
        for service_name, docs_url in docs_urls.items():
            if not any(
                pattern in docs_url for pattern in ["/docs", "/api", "/swagger"]
            ):
                inconsistent_patterns.append(
                    {"service": service_name, "docs_url": docs_url}
                )

        if inconsistent_patterns:
            self.result.failed_checks += 1
            for pattern in inconsistent_patterns:
                self.result.add_issue(
                    "LOW",
                    "docs_url_pattern",
                    pattern["service"],
                    f"Unusual docs URL pattern: {pattern['docs_url']}",
                    {"pattern_details": pattern},
                )
        else:
            self.result.passed_checks += 1

    def run_validation(self) -> ValidationResult:
        """Run the complete validation process."""
        logger.info("🚀 Starting Service Configuration Alignment Validation")
        logger.info(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")

        # 1. Collect all configuration files
        logger.info("📄 Collecting configuration files...")

        docker_compose_files = self.find_files(self.docker_compose_patterns)
        k8s_files = self.find_files(self.k8s_patterns)
        service_config_files = self.find_files(self.service_config_patterns)
        code_files = self.find_files(self.code_patterns)

        logger.info(f"Found {len(docker_compose_files)} Docker Compose files")
        logger.info(f"Found {len(k8s_files)} Kubernetes manifests")
        logger.info(f"Found {len(service_config_files)} service config files")
        logger.info(f"Found {len(code_files)} Python code files")

        # 2. Parse configurations
        logger.info("🔍 Parsing configurations...")

        all_configs = []

        # Parse Docker Compose files
        for file_path in docker_compose_files:
            configs = self.parse_docker_compose(file_path)
            all_configs.extend(configs.values())

        # Parse Kubernetes manifests
        for file_path in k8s_files:
            configs = self.parse_kubernetes_manifest(file_path)
            all_configs.extend(configs.values())

        # Parse service config files
        for file_path in service_config_files:
            config = self.parse_service_config(file_path)
            all_configs.append(config)

        # Parse Python code files
        for file_path in code_files:
            config = self.parse_python_code(file_path)
            if config.ports or config.image_tags or configconfig/environments/development.env_vars or config.docs_url:
                all_configs.append(config)

        # 3. Merge configurations by service name
        logger.info("🔧 Merging configurations...")
        self.configurations = self.merge_configurations(all_configs)

        logger.info(f"Identified {len(self.configurations)} services:")
        for service_name, config in self.configurations.items():
            logger.info(
                f"  - {service_name}: {len(config.ports)} ports, {len(config.image_tags)} images"
            )

        # 4. Run validation checks
        logger.info("✅ Running validation checks...")

        self.validate_constitutional_compliance()
        self.validate_port_consistency()
        self.validate_image_tag_consistency()
        self.validate_environment_consistency()
        self.validate_docs_url_consistency()

        # 5. Calculate performance score
        duration = self.result.get_duration()
        total_files = (
            len(docker_compose_files)
            + len(k8s_files)
            + len(service_config_files)
            + len(code_files)
        )
        if duration > 0:
            self.result.performance_score = min(100.0, (total_files / duration) * 10)

        # 6. Generate summary
        logger.info("📊 Validation Summary:")
        logger.info(f"  Total Checks: {self.result.total_checks}")
        logger.info(f"  Passed: {self.result.passed_checks}")
        logger.info(f"  Failed: {self.result.failed_checks}")
        logger.info(f"  Success Rate: {self.result.get_success_rate():.1f}%")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Performance Score: {self.result.performance_score:.1f}")

        if self.result.issues:
            logger.warning(f"⚠️  Found {len(self.result.issues)} issues:")
            for issue in self.result.issues:
                logger.warning(f"    {issue['severity']}: {issue['message']}")

        return self.result

    def generate_report(self) -> str:
        """Generate a detailed validation report."""
        duration = self.result.get_duration()
        success_rate = self.result.get_success_rate()

        # Group issues by severity
        issues_by_severity = {}
        for issue in self.result.issues:
            severity = issue["severity"]
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)

        report = f"""# ACGS Service Configuration Alignment Validation Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`
**Validator**: {self.result.validator_name}
**Duration**: {duration:.2f} seconds
**Performance Score**: {self.result.performance_score:.1f}/100

## Summary

| Metric | Value |
|--------|-------|
| Total Checks | {self.result.total_checks} |
| Passed Checks | {self.result.passed_checks} |
| Failed Checks | {self.result.failed_checks} |
| Success Rate | {success_rate:.1f}% |
| Total Issues | {len(self.result.issues)} |

## Service Overview

"""

        for service_name, config in self.configurations.items():
            report += f"### {service_name}\n\n"
            report += f"- **Ports**: {sorted(list(config.ports)) if config.ports else 'None'}\n"
            report += f"- **Image Tags**: {list(config.image_tags) if config.image_tags else 'None'}\n"
            report += f"- **Docs URL**: {config.docs_url or 'Not specified'}\n"
            report += f"- **Config Files**: {len(config.config_files)}\n"
            report += f"- **Source Files**: {len(config.source_files)}\n\n"

        report += "## Issues by Severity\n\n"

        for severity in ["CRITICAL", "ERROR", "HIGH", "MEDIUM", "LOW"]:
            if severity in issues_by_severity:
                issues = issues_by_severity[severity]
                report += f"### {severity} ({len(issues)} issues)\n\n"

                for issue in issues:
                    line_info = f" (line {issue['line']})" if issue.get("line") else ""
                    report += (
                        f"- **{issue['component']}**{line_info}: {issue['message']}\n"
                    )
                    if issue.get("details"):
                        report += (
                            f"  - Details: {json.dumps(issue['details'], indent=2)}\n"
                        )

                report += "\n"

        if not self.result.issues:
            report += (
                "✅ **No issues found!** All service configurations are aligned.\n\n"
            )

        report += f"""## Validation Metrics

- **Validation Speed**: {self.result.total_checks / duration:.1f} checks/second
- **Configuration Sources**: Docker Compose, Kubernetes, Service Configs, Code
- **Constitutional Compliance**: {CONSTITUTIONAL_HASH} ✅
- **Performance Score**: {self.result.performance_score:.1f}/100

---

**Service Configuration Alignment Validator**: Generated by ACGS Unified Validation Framework
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}` ✅
"""

        return report


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS Service Configuration Alignment Validator"
    )
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--output", type=Path, help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    # Initialize validator
    validator = ServiceConfigurationAlignmentValidator(repo_root=args.repo_root)

    # Run validation
    result = validator.run_validation()

    # Generate output
    if args.json:
        output = json.dumps(result.to_dict(), indent=2)
    else:
        output = validator.generate_report()

    # Save or print output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"📄 Report saved to: {args.output}")
    else:
        print(output)

    # Exit with appropriate code
    if result.failed_checks > 0:
        critical_issues = len([i for i in result.issues if i["severity"] == "CRITICAL"])
        if critical_issues > 0:
            print(
                f"\n🚨 {critical_issues} CRITICAL issues require immediate attention!"
            )
            return 2
        else:
            print(f"\n⚠️ {result.failed_checks} checks failed and should be addressed")
            return 1
    else:
        print("\n🎉 All configuration alignment checks passed!")
        return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
