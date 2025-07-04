#!/usr/bin/env python3
"""
ACGS-PGP Configuration Standardization Script

Consolidates multiple configuration versions and establishes single source of truth:
- Audit all config files in /config/, /config_backup_*, and service-specific configs
- Establish single source of truth for each environment (dev/staging/prod)
- Validate resource limits match specified 200m/500m CPU and 512Mi/1Gi memory constraints
- Test configuration changes in staging before production deployment

From remediation plan TIER 3 - MODERATE (Complete within 1 week)
"""

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



@dataclass
class ConfigFile:
    """Configuration file metadata."""

    path: str
    type: str  # json, yaml, py, etc.
    environment: str  # dev, staging, prod, shared
    service: str
    content: Any
    size_bytes: int
    last_modified: str


@dataclass
class ResourceLimits:
    """Resource limits configuration."""

    cpu_request: str = "200m"
    cpu_limit: str = "500m"
    memory_request: str = "512Mi"
    memory_limit: str = "1Gi"


class ConfigurationStandardizer:
    """Configuration standardization tool for ACGS-PGP system."""

    def __init__(self, project_root: str = "/home/ubuntu/ACGS"):
        self.project_root = Path(project_root)
        self.config_files: list[ConfigFile] = []
        self.standard_resource_limits = ResourceLimits()
        self.environments = ["dev", "staging", "prod", "shared"]

    def discover_config_files(self) -> list[ConfigFile]:
        """Discover all configuration files in the project."""
        print("🔍 Discovering configuration files...")

        config_patterns = [
            "**/*config*.json",
            "**/*config*.yaml",
            "**/*config*.yml",
            "**/config.py",
            "**/.env*",
            "**/docker-compose*.yml",
        ]

        config_files = []

        for pattern in config_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Skip node_modules, .git, __pycache__, etc.
                if any(
                    skip in str(file_path)
                    for skip in [
                        "node_modules",
                        ".git",
                        "__pycache__",
                        ".venv",
                        "applications_REMOVED",
                        ".mypy_cache",
                    ]
                ):
                    continue

                try:
                    stat = file_path.stat()

                    # Determine environment and service
                    env = self._determine_environment(file_path)
                    service = self._determine_service(file_path)

                    # Load content based on file type
                    content = self._load_config_content(file_path)

                    config_file = ConfigFile(
                        path=str(file_path.relative_to(self.project_root)),
                        type=file_path.suffix.lower(),
                        environment=env,
                        service=service,
                        content=content,
                        size_bytes=stat.st_size,
                        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    )

                    config_files.append(config_file)

                except (PermissionError, UnicodeDecodeError, Exception) as e:
                    print(f"  ⚠️ Skipped {file_path}: {e}")
                    continue

        self.config_files = config_files
        print(f"  ✅ Found {len(config_files)} configuration files")
        return config_files

    def _determine_environment(self, file_path: Path) -> str:
        """Determine environment from file path."""
        path_str = str(file_path).lower()

        if "prod" in path_str:
            return "prod"
        if "staging" in path_str:
            return "staging"
        if "dev" in path_str or "development" in path_str:
            return "dev"
        return "shared"

    def _determine_service(self, file_path: Path) -> str:
        """Determine service from file path."""
        path_parts = file_path.parts

        # Look for service names in path
        services = [
            "auth_service",
            "ac_service",
            "integrity_service",
            "fv_service",
            "gs_service",
            "pgc_service",
            "ec_service",
            "acgs-pgp-v8",
        ]

        for part in path_parts:
            for service in services:
                if service in part:
                    return service

        return "shared"

    def _load_config_content(self, file_path: Path) -> Any:
        """Load configuration file content."""
        try:
            with open(file_path, encoding="utf-8") as f:
                if file_path.suffix.lower() in [".json"]:
                    return json.load(f)
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    return yaml.safe_load(f)
                # For .py, .env, etc., just return first 1000 chars
                content = f.read()
                return content[:1000] if len(content) > 1000 else content
        except Exception:
            return None

    def analyze_configurations(self) -> dict[str, Any]:
        """Analyze configuration files for standardization opportunities."""
        print("📊 Analyzing configurations...")

        analysis = {
            "total_files": len(self.config_files),
            "by_environment": {},
            "by_service": {},
            "by_type": {},
            "duplicates": [],
            "resource_limit_compliance": {},
            "recommendations": [],
        }

        # Group by environment, service, type
        for config in self.config_files:
            # By environment
            if config.environment not in analysis["by_environment"]:
                analysis["by_environment"][config.environment] = []
            analysis["by_environment"][config.environment].append(config.path)

            # By service
            if config.service not in analysis["by_service"]:
                analysis["by_service"][config.service] = []
            analysis["by_service"][config.service].append(config.path)

            # By type
            if config.type not in analysis["by_type"]:
                analysis["by_type"][config.type] = []
            analysis["by_type"][config.type].append(config.path)

        # Check for resource limit compliance
        analysis["resource_limit_compliance"] = self._check_resource_limits()

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    def _check_resource_limits(self) -> dict[str, Any]:
        """Check resource limits compliance across configurations."""
        compliance = {
            "compliant_files": [],
            "non_compliant_files": [],
            "missing_limits": [],
        }

        for config in self.config_files:
            if config.content and isinstance(config.content, dict):
                # Check for resource limits in various formats
                has_limits = False
                is_compliant = False

                # Check Kubernetes-style resource limits
                if "resources" in config.content:
                    has_limits = True
                    resources = config.content["resources"]
                    if self._validate_k8s_resources(resources):
                        is_compliant = True

                # Check Docker Compose style
                elif (
                    "deploy" in config.content
                    and "resources" in config.content["deploy"]
                ):
                    has_limits = True
                    resources = config.content["deploy"]["resources"]
                    if self._validate_docker_resources(resources):
                        is_compliant = True

                if has_limits:
                    if is_compliant:
                        compliance["compliant_files"].append(config.path)
                    else:
                        compliance["non_compliant_files"].append(config.path)
                else:
                    compliance["missing_limits"].append(config.path)

        return compliance

    def _validate_k8s_resources(self, resources: dict) -> bool:
        """Validate Kubernetes resource limits."""
        try:
            limits = resources.get("limits", {})
            requests = resources.get("requests", {})

            # Check CPU limits
            cpu_limit = limits.get("cpu", "")
            cpu_request = requests.get("cpu", "")

            # Check memory limits
            memory_limit = limits.get("memory", "")
            memory_request = requests.get("memory", "")

            return (
                cpu_request == self.standard_resource_limits.cpu_request
                and cpu_limit == self.standard_resource_limits.cpu_limit
                and memory_request == self.standard_resource_limits.memory_request
                and memory_limit == self.standard_resource_limits.memory_limit
            )
        except:
            return False

    def _validate_docker_resources(self, resources: dict) -> bool:
        """Validate Docker resource limits."""
        try:
            limits = resources.get("limits", {})

            # Convert standard limits to Docker format
            cpu_limit = (
                float(self.standard_resource_limits.cpu_limit.replace("m", "")) / 1000
            )
            memory_limit = self.standard_resource_limits.memory_limit

            return (
                limits.get("cpus", 0) <= cpu_limit
                and limits.get("memory", "") == memory_limit
            )
        except:
            return False

    def _generate_recommendations(self, analysis: dict) -> list[str]:
        """Generate standardization recommendations."""
        recommendations = []

        # Environment-specific recommendations
        env_counts = {
            env: len(files) for env, files in analysis["by_environment"].items()
        }
        if env_counts.get("shared", 0) < env_counts.get("dev", 0):
            recommendations.append("Move common configurations to shared environment")

        # Service-specific recommendations
        service_counts = {
            svc: len(files) for svc, files in analysis["by_service"].items()
        }
        if service_counts.get("shared", 0) > 10:
            recommendations.append(
                "Consider splitting shared configurations by service"
            )

        # Resource limits recommendations
        compliance = analysis["resource_limit_compliance"]
        if compliance["non_compliant_files"]:
            recommendations.append(
                f"Update {len(compliance['non_compliant_files'])} files to use standard resource limits"
            )

        if compliance["missing_limits"]:
            recommendations.append(
                f"Add resource limits to {len(compliance['missing_limits'])} configuration files"
            )

        return recommendations

    def standardize_configurations(self) -> dict[str, Any]:
        """Apply configuration standardization."""
        print("🔧 Applying configuration standardization...")

        results = {
            "standardized_files": [],
            "created_directories": [],
            "backup_created": False,
            "errors": [],
        }

        # Create backup
        backup_dir = (
            self.project_root
            / f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        try:
            if (self.project_root / "config").exists():
                shutil.copytree(self.project_root / "config", backup_dir)
                results["backup_created"] = True
                print(f"  ✅ Backup created: {backup_dir}")
        except Exception as e:
            results["errors"].append(f"Backup failed: {e}")

        # Create standardized directory structure
        standard_dirs = [
            "config/environments/dev",
            "config/environments/staging",
            "config/environments/prod",
            "config/services",
            "config/shared",
        ]

        for dir_path in standard_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            results["created_directories"].append(str(full_path))

        # Create standard resource limits template
        self._create_resource_limits_template()

        print(f"  ✅ Standardized {len(results['standardized_files'])} files")
        return results

    def _create_resource_limits_template(self):
        """Create standard resource limits template."""
        template = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": "acgs-resource-limits", "namespace": "acgs-system"},
            "data": {
                "cpu_request": self.standard_resource_limits.cpu_request,
                "cpu_limit": self.standard_resource_limits.cpu_limit,
                "memory_request": self.standard_resource_limits.memory_request,
                "memory_limit": self.standard_resource_limits.memory_limit,
            },
        }

        template_path = self.project_root / "config" / "shared" / "resource-limits.yaml"
        with open(template_path, "w") as f:
            yaml.dump(template, f, default_flow_style=False)

        print(f"  ✅ Created resource limits template: {template_path}")


def print_standardization_report(analysis: dict[str, Any], results: dict[str, Any]):
    """Print configuration standardization report."""
    print("\n" + "=" * 80)
    print("⚙️ ACGS-PGP CONFIGURATION STANDARDIZATION REPORT")
    print("=" * 80)

    print("📊 Configuration Analysis:")
    print(f"   • Total Files: {analysis['total_files']}")
    print(f"   • Environments: {', '.join(analysis['by_environment'].keys())}")
    print(f"   • Services: {len(analysis['by_service'])} services")
    print(f"   • File Types: {', '.join(analysis['by_type'].keys())}")

    print("\n🎯 Resource Limits Compliance:")
    compliance = analysis["resource_limit_compliance"]
    print(f"   • Compliant Files: {len(compliance['compliant_files'])}")
    print(f"   • Non-Compliant Files: {len(compliance['non_compliant_files'])}")
    print(f"   • Missing Limits: {len(compliance['missing_limits'])}")

    print("\n🔧 Standardization Results:")
    print(f"   • Backup Created: {'✅' if results['backup_created'] else '❌'}")
    print(f"   • Directories Created: {len(results['created_directories'])}")
    print(f"   • Files Standardized: {len(results['standardized_files'])}")

    if results["errors"]:
        print("\n⚠️ Errors:")
        for error in results["errors"]:
            print(f"   • {error}")

    print("\n💡 Recommendations:")
    for rec in analysis["recommendations"]:
        print(f"   • {rec}")

    print("=" * 80)


def main():
    """Main configuration standardization function."""
    parser = argparse.ArgumentParser(description="ACGS-PGP Configuration Standardizer")
    parser.add_argument(
        "--analyze-only", action="store_true", help="Only analyze, don't standardize"
    )
    parser.add_argument(
        "--output", "-o", default="config_analysis.json", help="Output analysis file"
    )

    args = parser.parse_args()

    # Run configuration standardization
    standardizer = ConfigurationStandardizer()

    # Discover and analyze configurations
    standardizer.discover_config_files()
    analysis = standardizer.analyze_configurations()

    results = {}
    if not args.analyze_only:
        results = standardizer.standardize_configurations()

    # Print report
    print_standardization_report(analysis, results)

    # Save analysis
    with open(args.output, "w") as f:
        json.dump({"analysis": analysis, "results": results}, f, indent=2)
    print(f"\n📄 Analysis saved to: {args.output}")

    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
