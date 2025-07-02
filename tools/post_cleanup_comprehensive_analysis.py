#!/usr/bin/env python3
"""
ACGS-1 Post-Cleanup Comprehensive Analysis

This script performs a detailed analysis of the ACGS-1 project after the comprehensive cleanup
to identify any remaining issues, validate service integration, and ensure optimal performance.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class PostCleanupAnalyzer:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "Post-Cleanup Comprehensive Analysis",
            "remaining_duplicates": {"found": False, "items": []},
            "service_integration": {
                "status": "unknown",
                "services": {},
                "communication_tests": {},
            },
            "configuration_consistency": {
                "status": "unknown",
                "issues": [],
                "recommendations": [],
            },
            "documentation_updates": {
                "outdated_references": [],
                "missing_documentation": [],
                "update_recommendations": [],
            },
            "testing_validation": {
                "governance_workflows": "unknown",
                "quantumagi_deployment": "unknown",
                "enhancement_framework": "unknown",
                "import_dependencies": "unknown",
            },
            "performance_optimization": {"opportunities": [], "recommendations": []},
            "summary": {
                "total_issues_found": 0,
                "critical_issues": 0,
                "recommendations_count": 0,
                "overall_status": "unknown",
            },
        }

    def log_finding(self, category: str, finding: str, severity: str = "info"):
        """Log analysis findings."""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] {severity.upper()}: {category} - {finding}")

    def analyze_remaining_duplicates(self):
        """Analyze for any remaining duplicate files or directories."""
        print("🔍 Analyzing for remaining duplicates...")

        # Check for any remaining duplicate patterns
        duplicate_patterns = [
            ("services/core", ["_", "-"]),  # underscore vs hyphen variants
            ("blockchain", ["test", "tests"]),  # test directory variants
            ("docs", ["README", "readme"]),  # case variants
        ]

        remaining_duplicates = []

        for base_path, patterns in duplicate_patterns:
            full_path = self.project_root / base_path
            if full_path.exists():
                # Look for pattern-based duplicates
                for item in full_path.iterdir():
                    if item.is_dir():
                        item_name = item.name.lower()
                        # Check for similar named directories
                        for other_item in full_path.iterdir():
                            if other_item != item and other_item.is_dir():
                                other_name = other_item.name.lower()
                                # Check for underscore/hyphen variants
                                if item_name.replace("_", "-") == other_name.replace(
                                    "_", "-"
                                ):
                                    remaining_duplicates.append(
                                        {
                                            "type": "directory_variant",
                                            "items": [str(item), str(other_item)],
                                            "recommendation": f"Consider consolidating {item.name} and {other_item.name}",
                                        }
                                    )

        self.analysis_results["remaining_duplicates"]["found"] = (
            len(remaining_duplicates) > 0
        )
        self.analysis_results["remaining_duplicates"]["items"] = remaining_duplicates

        if remaining_duplicates:
            self.log_finding(
                "Remaining Duplicates",
                f"Found {len(remaining_duplicates)} potential duplicates",
                "warning",
            )
        else:
            self.log_finding(
                "Remaining Duplicates", "No additional duplicates found", "info"
            )

    def validate_service_integration(self):
        """Validate that all 7 core services are properly integrated."""
        print("🔗 Validating service integration...")

        core_services = {
            "constitutional-ai": {"port": 8001, "path": "ac_service"},
            "governance-synthesis": {"port": 8004, "path": "gs_service"},
            "formal-verification": {"port": 8003, "path": "fv_service"},
            "policy-governance": {"port": 8005, "path": "pgc_service"},
            "evolutionary-computation": {"port": 8006, "path": "app"},
            "self-evolving-ai": {"port": 8007, "path": "app"},
            "acgs-pgp-v8": {"port": 8010, "path": "src"},
        }

        service_status = {}

        for service_name, config in core_services.items():
            service_path = self.project_root / "services" / "core" / service_name

            status = {
                "exists": service_path.exists(),
                "has_main_app": False,
                "has_requirements": False,
                "has_config": False,
                "port_available": True,
                "integration_ready": False,
            }

            if status["exists"]:
                # Check for main application
                app_path = service_path / config["path"]
                status["has_main_app"] = app_path.exists()

                # Check for requirements
                req_files = ["requirements.txt", "pyproject.toml"]
                status["has_requirements"] = any(
                    (service_path / req).exists() for req in req_files
                )

                # Check for configuration
                config_paths = [service_path / "config", app_path / "config"]
                status["has_config"] = any(p.exists() for p in config_paths)

                # Determine integration readiness
                status["integration_ready"] = all(
                    [
                        status["exists"],
                        status["has_main_app"],
                        status["has_requirements"],
                    ]
                )

            service_status[service_name] = status

            status_icon = "✅" if status["integration_ready"] else "❌"
            self.log_finding(
                "Service Integration",
                f"{status_icon} {service_name}: {'Ready' if status['integration_ready'] else 'Issues found'}",
            )

        self.analysis_results["service_integration"]["services"] = service_status

        # Overall integration status
        ready_services = sum(
            1 for s in service_status.values() if s["integration_ready"]
        )
        total_services = len(service_status)

        if ready_services == total_services:
            self.analysis_results["service_integration"]["status"] = "excellent"
        elif ready_services >= total_services * 0.8:
            self.analysis_results["service_integration"]["status"] = "good"
        else:
            self.analysis_results["service_integration"]["status"] = "needs_attention"

    def check_configuration_consistency(self):
        """Check for configuration consistency across services."""
        print("⚙️ Checking configuration consistency...")

        config_issues = []

        # Check for consistent port configurations
        port_configs = {}
        services_core = self.project_root / "services" / "core"

        for service_dir in services_core.iterdir():
            if service_dir.is_dir():
                # Look for configuration files
                config_files = (
                    list(service_dir.rglob("*.yaml"))
                    + list(service_dir.rglob("*.yml"))
                    + list(service_dir.rglob("*.json"))
                )

                for config_file in config_files:
                    try:
                        with open(config_file) as f:
                            content = f.read()
                            # Look for port configurations
                            if "port" in content.lower():
                                port_configs[str(config_file)] = "contains_port_config"
                    except Exception:
                        continue

        # Check for environment variable consistency
        env_files = list(self.project_root.rglob(".env*"))
        docker_files = list(self.project_root.rglob("docker-compose*.yml"))

        if len(env_files) > 1:
            config_issues.append(
                {
                    "type": "multiple_env_files",
                    "description": f"Found {len(env_files)} environment files",
                    "files": [str(f) for f in env_files],
                    "recommendation": "Consolidate environment configurations",
                }
            )

        # Check for consistent database configurations
        db_configs = []
        for config_file in self.project_root.rglob("*config*.py"):
            try:
                with open(config_file) as f:
                    content = f.read()
                    if "database" in content.lower() or "db_" in content.lower():
                        db_configs.append(str(config_file))
            except Exception:
                continue

        self.analysis_results["configuration_consistency"]["issues"] = config_issues

        if config_issues:
            self.analysis_results["configuration_consistency"][
                "status"
            ] = "issues_found"
            self.log_finding(
                "Configuration",
                f"Found {len(config_issues)} configuration issues",
                "warning",
            )
        else:
            self.analysis_results["configuration_consistency"]["status"] = "consistent"
            self.log_finding(
                "Configuration", "Configuration appears consistent", "info"
            )

    def analyze_documentation_updates(self):
        """Analyze documentation for outdated references."""
        print("📚 Analyzing documentation updates needed...")

        outdated_references = []
        missing_docs = []

        # Check for references to removed services
        removed_services = [
            "constitutional_ai",
            "evolutionary_computation",
            "formal_verification",
            "governance_synthesis",
            "policy_governance",
            "self_evolving_ai",
            "ac",
            "ec",
            "gs",
            "pgc",
            "hitl_safety",
            "security_hardening",
        ]

        doc_files = []
        doc_extensions = [".md", ".rst", ".txt"]

        for ext in doc_extensions:
            doc_files.extend(self.project_root.rglob(f"*{ext}"))

        for doc_file in doc_files:
            try:
                with open(doc_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    for removed_service in removed_services:
                        if removed_service in content:
                            outdated_references.append(
                                {
                                    "file": str(doc_file),
                                    "reference": removed_service,
                                    "type": "removed_service_reference",
                                }
                            )
            except Exception:
                continue

        # Check for missing documentation for current services
        current_services = [
            "constitutional-ai",
            "governance-synthesis",
            "formal-verification",
            "policy-governance",
            "evolutionary-computation",
            "self-evolving-ai",
            "acgs-pgp-v8",
        ]

        for service in current_services:
            service_path = self.project_root / "services" / "core" / service
            if service_path.exists():
                readme_exists = (service_path / "README.md").exists()
                if not readme_exists:
                    missing_docs.append(
                        {
                            "service": service,
                            "missing": "README.md",
                            "recommendation": f"Create README.md for {service}",
                        }
                    )

        self.analysis_results["documentation_updates"][
            "outdated_references"
        ] = outdated_references
        self.analysis_results["documentation_updates"][
            "missing_documentation"
        ] = missing_docs

        total_doc_issues = len(outdated_references) + len(missing_docs)
        if total_doc_issues > 0:
            self.log_finding(
                "Documentation",
                f"Found {total_doc_issues} documentation issues",
                "warning",
            )
        else:
            self.log_finding(
                "Documentation", "Documentation appears up to date", "info"
            )

    def run_comprehensive_analysis(self):
        """Run the complete post-cleanup analysis."""
        print("🚀 Starting post-cleanup comprehensive analysis...")
        print("=" * 60)

        # Run all analysis components
        self.analyze_remaining_duplicates()
        self.validate_service_integration()
        self.check_configuration_consistency()
        self.analyze_documentation_updates()

        # Generate summary
        total_issues = (
            len(self.analysis_results["remaining_duplicates"]["items"])
            + len(self.analysis_results["configuration_consistency"]["issues"])
            + len(self.analysis_results["documentation_updates"]["outdated_references"])
            + len(
                self.analysis_results["documentation_updates"]["missing_documentation"]
            )
        )

        critical_issues = sum(
            1
            for item in self.analysis_results["remaining_duplicates"]["items"]
            if item.get("type") == "critical"
        )

        self.analysis_results["summary"] = {
            "total_issues_found": total_issues,
            "critical_issues": critical_issues,
            "recommendations_count": total_issues,
            "overall_status": (
                "excellent"
                if total_issues == 0
                else "good" if total_issues < 5 else "needs_attention"
            ),
        }

        print("\n📊 ANALYSIS SUMMARY")
        print("=" * 30)
        print(f"Total issues found: {total_issues}")
        print(f"Critical issues: {critical_issues}")
        print(f"Overall status: {self.analysis_results['summary']['overall_status']}")

        # Save results
        output_file = (
            f"post_cleanup_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_file, "w") as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"\n📄 Analysis results saved to: {output_file}")

        return self.analysis_results


if __name__ == "__main__":
    analyzer = PostCleanupAnalyzer()
    results = analyzer.run_comprehensive_analysis()

    # Exit with appropriate code
    total_issues = results["summary"]["total_issues_found"]
    critical_issues = results["summary"]["critical_issues"]

    if critical_issues > 0:
        sys.exit(2)  # Critical issues found
    elif total_issues > 0:
        sys.exit(1)  # Non-critical issues found
    else:
        sys.exit(0)  # No issues found
