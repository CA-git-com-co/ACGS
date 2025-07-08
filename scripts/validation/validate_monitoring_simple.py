#!/usr/bin/env python3
"""
ACGS-2 Simple Monitoring Validation Script
Constitutional Hash: cdd01ef066bc6cf2

This script validates the monitoring infrastructure configuration files
and documentation without requiring external dependencies.
"""

import json
import time
from pathlib import Path

import yaml

# Constitutional hash validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class SimpleMonitoringValidator:
    """Simple monitoring validation without external dependencies"""

    def __init__(self):
        self.results = []
        self.project_root = Path("/home/dislove/ACGS-2")

    def add_result(
        self,
        component: str,
        status: str,
        details: str,
        constitutional_compliant: bool = True,
    ) -> None:
        """Add validation result"""
        result = {
            "component": component,
            "status": status,
            "details": details,
            "constitutional_compliant": constitutional_compliant,
            "timestamp": time.time(),
        }
        self.results.append(result)

        status_icon = {"PASSED": "✅", "FAILED": "❌", "WARNING": "⚠️"}.get(status, "?")
        compliance_icon = "🏛️" if constitutional_compliant else "❌"
        print(f"{status_icon} {compliance_icon} {component}: {details}")

    def validate_file_structure(self) -> bool:
        """Validate monitoring configuration file structure"""
        required_files = [
            "config/monitoring/prometheus-constitutional.yml",
            "config/monitoring/constitutional_rules.yml",
            "config/monitoring/grafana-constitutional-dashboard.json",
            "scripts/validate_constitutional_monitoring.py",
        ]

        all_present = True
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.add_result(
                    "file_structure", "PASSED", f"File exists: {file_path}", True
                )
            else:
                self.add_result(
                    "file_structure", "FAILED", f"Missing file: {file_path}", False
                )
                all_present = False

        return all_present

    def validate_prometheus_config(self) -> bool:
        """Validate Prometheus constitutional configuration"""
        config_path = (
            self.project_root / "config/monitoring/prometheus-constitutional.yml"
        )

        if not config_path.exists():
            self.add_result(
                "prometheus_config", "FAILED", "Prometheus config file not found", False
            )
            return False

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)

            # Validate constitutional hash in global labels
            global_labels = config.get("global", {}).get("external_labels", {})
            if global_labels.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                self.add_result(
                    "prometheus_config",
                    "PASSED",
                    "Constitutional hash found in global labels:"
                    f" {CONSTITUTIONAL_HASH}",
                    True,
                )
            else:
                self.add_result(
                    "prometheus_config",
                    "FAILED",
                    "Constitutional hash missing or incorrect in global labels",
                    False,
                )
                return False

            # Count scrape configs with constitutional hash
            scrape_configs = config.get("scrape_configs", [])
            constitutional_jobs = 0

            for job in scrape_configs:
                job_labels = job.get("labels", {})
                if job_labels.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                    constitutional_jobs += 1

            self.add_result(
                "prometheus_config",
                "PASSED",
                f"Found {constitutional_jobs} constitutional scrape jobs",
                True,
            )
            return True

        except Exception as e:
            self.add_result(
                "prometheus_config",
                "FAILED",
                f"Error parsing Prometheus config: {e!s}",
                False,
            )
            return False

    def validate_alerting_rules(self) -> bool:
        """Validate constitutional alerting rules"""
        rules_path = self.project_root / "config/monitoring/constitutional_rules.yml"

        if not rules_path.exists():
            self.add_result(
                "alerting_rules", "FAILED", "Alerting rules file not found", False
            )
            return False

        try:
            with open(rules_path) as f:
                rules = yaml.safe_load(f)

            groups = rules.get("groups", [])
            constitutional_alerts = 0
            critical_alerts = 0

            for group in groups:
                for rule in group.get("rules", []):
                    if "alert" in rule:
                        labels = rule.get("labels", {})
                        annotations = rule.get("annotations", {})

                        # Check constitutional hash in labels and annotations
                        if (
                            labels.get("constitutional_hash") == CONSTITUTIONAL_HASH
                            and annotations.get("constitutional_hash")
                            == CONSTITUTIONAL_HASH
                        ):
                            constitutional_alerts += 1

                            if labels.get("severity") == "critical":
                                critical_alerts += 1

            self.add_result(
                "alerting_rules",
                "PASSED",
                f"Found {constitutional_alerts} constitutional alerts"
                f" ({critical_alerts} critical)",
                True,
            )
            return True

        except Exception as e:
            self.add_result(
                "alerting_rules",
                "FAILED",
                f"Error parsing alerting rules: {e!s}",
                False,
            )
            return False

    def validate_grafana_dashboard(self) -> bool:
        """Validate constitutional Grafana dashboard"""
        dashboard_path = (
            self.project_root
            / "config/monitoring/grafana-constitutional-dashboard.json"
        )

        if not dashboard_path.exists():
            self.add_result(
                "grafana_dashboard", "FAILED", "Grafana dashboard file not found", False
            )
            return False

        try:
            with open(dashboard_path) as f:
                dashboard = json.load(f)

            dashboard_config = dashboard.get("dashboard", {})

            # Validate constitutional templating
            templating = dashboard_config.get("templating", {}).get("list", [])
            constitutional_template = None

            for template in templating:
                if template.get("name") == "constitutional_hash":
                    constitutional_template = template
                    break

            if not constitutional_template:
                self.add_result(
                    "grafana_dashboard",
                    "FAILED",
                    "Constitutional hash template not found",
                    False,
                )
                return False

            if constitutional_template.get("query") != CONSTITUTIONAL_HASH:
                self.add_result(
                    "grafana_dashboard",
                    "FAILED",
                    "Constitutional hash template mismatch:"
                    f" {constitutional_template.get('query')}",
                    False,
                )
                return False

            # Count panels with constitutional context
            panels = dashboard_config.get("panels", [])
            constitutional_panels = 0

            for panel in panels:
                targets = panel.get("targets", [])
                for target in targets:
                    expr = target.get("expr", "")
                    if CONSTITUTIONAL_HASH in expr:
                        constitutional_panels += 1
                        break

            self.add_result(
                "grafana_dashboard",
                "PASSED",
                f"Found {constitutional_panels} constitutional panels",
                True,
            )
            return True

        except Exception as e:
            self.add_result(
                "grafana_dashboard",
                "FAILED",
                f"Error parsing Grafana dashboard: {e!s}",
                False,
            )
            return False

    def validate_documentation(self) -> bool:
        """Validate documentation has been updated"""
        docs_to_check = [
            ("README.md", ["comprehensive constitutional monitoring infrastructure"]),
            (
                "docs/ACGS_SERVICE_OVERVIEW.md",
                ["comprehensive monitoring infrastructure"],
            ),
            (
                "docs/operations/ACGS_PRODUCTION_OPERATIONS.md",
                ["comprehensive monitoring and alerting system"],
            ),
            (
                "docs/operations/runbooks.md",
                ["Constitutional Monitoring Dashboard Recovery"],
            ),
            (
                "docs/deployment/DEPLOYMENT_GUIDE.md",
                ["constitutional compliance monitoring"],
            ),
        ]

        all_docs_valid = True

        for doc_path, patterns in docs_to_check:
            full_path = self.project_root / doc_path

            if not full_path.exists():
                self.add_result(
                    "documentation",
                    "FAILED",
                    f"Documentation file not found: {doc_path}",
                    False,
                )
                all_docs_valid = False
                continue

            try:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()

                missing_patterns = []
                for pattern in patterns:
                    if pattern not in content:
                        missing_patterns.append(pattern)

                if missing_patterns:
                    self.add_result(
                        "documentation",
                        "FAILED",
                        f"Missing patterns in {doc_path}: {missing_patterns}",
                        False,
                    )
                    all_docs_valid = False
                else:
                    self.add_result(
                        "documentation",
                        "PASSED",
                        f"Documentation updated: {doc_path}",
                        True,
                    )

            except Exception as e:
                self.add_result(
                    "documentation",
                    "FAILED",
                    f"Error reading {doc_path}: {e!s}",
                    False,
                )
                all_docs_valid = False

        return all_docs_valid

    def run_validation(self) -> dict:
        """Run complete monitoring validation"""
        print("🏛️ ACGS-2 Simple Monitoring Validation")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("=" * 60)

        # Run all validations
        file_structure_valid = self.validate_file_structure()
        prometheus_valid = self.validate_prometheus_config()
        alerting_valid = self.validate_alerting_rules()
        grafana_valid = self.validate_grafana_dashboard()
        docs_valid = self.validate_documentation()

        # Generate summary
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r["status"] == "PASSED")
        failed_checks = sum(1 for r in self.results if r["status"] == "FAILED")
        warning_checks = sum(1 for r in self.results if r["status"] == "WARNING")
        constitutional_compliant = sum(
            1 for r in self.results if r["constitutional_compliant"]
        )

        summary = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "warnings": warning_checks,
            "constitutional_compliance_rate": (
                constitutional_compliant / total_checks if total_checks > 0 else 0
            ),
            "overall_status": "PASSED" if failed_checks == 0 else "FAILED",
            "timestamp": time.time(),
            "validation_components": {
                "file_structure": file_structure_valid,
                "prometheus_config": prometheus_valid,
                "alerting_rules": alerting_valid,
                "grafana_dashboard": grafana_valid,
                "documentation": docs_valid,
            },
        }

        print("=" * 60)
        print("📊 VALIDATION SUMMARY")
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        print(f"Warnings: {warning_checks}")
        print(
            "Constitutional Compliance Rate:"
            f" {summary['constitutional_compliance_rate']:.1%}"
        )
        print(f"Overall Status: {summary['overall_status']}")
        print("=" * 60)

        return summary


def main():
    """Main validation function"""
    validator = SimpleMonitoringValidator()

    try:
        summary = validator.run_validation()

        if summary["overall_status"] == "PASSED":
            print("\n🎉 Constitutional monitoring validation PASSED!")
            exit(0)
        else:
            print("\n❌ Constitutional monitoring validation FAILED!")
            exit(1)

    except Exception as e:
        print(f"\n💥 Validation script error: {e!s}")
        exit(2)


if __name__ == "__main__":
    main()
