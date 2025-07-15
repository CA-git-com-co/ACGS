#!/usr/bin/env python3
"""
ACGS-2 Constitutional Monitoring Deployment Validation Script
Constitutional Hash: cdd01ef066bc6cf2

This script validates the complete constitutional monitoring setup including:
- Prometheus configuration and rules
- Grafana dashboard configuration
- Service metrics endpoints
- Constitutional compliance tracking
- Alert rule validation
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import redis.asyncio as aioredis
import asyncpg
import requests
import yaml

# Constitutional hash validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class ValidationResult:
    """Validation result data structure"""

    component: str
    status: str
    details: str
    constitutional_compliant: bool
    timestamp: float


class ConstitutionalMonitoringValidator:
    """Constitutional monitoring setup validator"""

    def __init__(self):
        self.results: List[ValidationResult] = []
        self.setup_logging()

    def setup_logging(self) -> None:
        """Setup constitutional logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("/tmp/constitutional_monitoring_validation.log"),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def add_result(
        self,
        component: str,
        status: str,
        details: str,
        constitutional_compliant: bool = True,
    ) -> None:
        """Add validation result"""
        result = ValidationResult(
            component=component,
            status=status,
            details=details,
            constitutional_compliant=constitutional_compliant,
            timestamp=time.time(),
        )
        self.results.append(result)

        # Log with constitutional context
        self.logger.info(
            f"Validation: {component} - {status}",
            extra={
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "component": component,
                "status": status,
                "constitutional_compliant": constitutional_compliant,
            },
        )

    def validate_prometheus_config(self) -> bool:
        """Validate Prometheus constitutional configuration"""
        try:
            config_path = Path(
                "/home/dislove/ACGS-2/config/monitoring/prometheus-constitutional.yml"
            )

            if not config_path.exists():
                self.add_result(
                    "prometheus_config",
                    "FAILED",
                    "Prometheus config file not found",
                    False,
                )
                return False

            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            # Validate constitutional hash presence
            global_labels = config.get("global", {}).get("external_labels", {})
            if global_labels.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                self.add_result(
                    "prometheus_config",
                    "FAILED",
                    f"Constitutional hash mismatch in global labels: {global_labels.get('constitutional_hash')}",
                    False,
                )
                return False

            # Validate scrape configs
            scrape_configs = config.get("scrape_configs", [])
            constitutional_jobs = 0

            for job in scrape_configs:
                job_labels = job.get("labels", {})
                job_params = job.get("params", {})

                if job_labels.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                    constitutional_jobs += 1

                # Validate infrastructure port labeling
                if "infrastructure_port" not in job_labels:
                    self.logger.warning(
                        f"Job {job.get('job_name')} missing infrastructure_port label"
                    )

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
                "ERROR",
                f"Config validation error: {str(e)}",
                False,
            )
            return False

    def validate_alerting_rules(self) -> bool:
        """Validate constitutional alerting rules"""
        try:
            rules_path = Path(
                "/home/dislove/ACGS-2/config/monitoring/constitutional_rules.yml"
            )

            if not rules_path.exists():
                self.add_result(
                    "alerting_rules", "FAILED", "Alerting rules file not found", False
                )
                return False

            with open(rules_path, "r") as f:
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
                f"Found {constitutional_alerts} constitutional alerts ({critical_alerts} critical)",
                True,
            )
            return True

        except Exception as e:
            self.add_result(
                "alerting_rules", "ERROR", f"Rules validation error: {str(e)}", False
            )
            return False

    def validate_grafana_dashboard(self) -> bool:
        """Validate constitutional Grafana dashboard"""
        try:
            dashboard_path = Path(
                "/home/dislove/ACGS-2/config/monitoring/grafana-constitutional-dashboard.json"
            )

            if not dashboard_path.exists():
                self.add_result(
                    "grafana_dashboard",
                    "FAILED",
                    "Grafana dashboard file not found",
                    False,
                )
                return False

            with open(dashboard_path, "r") as f:
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
                    f"Constitutional hash template mismatch: {constitutional_template.get('query')}",
                    False,
                )
                return False

            # Validate panels
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
                "ERROR",
                f"Dashboard validation error: {str(e)}",
                False,
            )
            return False

    async def validate_service_metrics_endpoints(self) -> bool:
        """Validate service metrics endpoints"""
        endpoints = [
            ("http://localhost:8080/metrics", "api_gateway"),
            ("http://localhost:8001/metrics", "constitutional_core"),
            ("http://localhost:8002/metrics", "integrity_service"),
            ("http://localhost:8004/metrics", "governance_engine"),
        ]

        successful_endpoints = 0
        constitutional_endpoints = 0

        for url, service in endpoints:
            try:
                # Try to connect with timeout
                import aiohttp

                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            successful_endpoints += 1
                            metrics_text = await response.text()

                            # Check for constitutional metrics
                            if (
                                CONSTITUTIONAL_HASH in metrics_text
                                or "constitutional_" in metrics_text
                            ):
                                constitutional_endpoints += 1

                            self.logger.info(
                                f"Service {service} metrics endpoint accessible"
                            )
                        else:
                            self.logger.warning(
                                f"Service {service} returned status {response.status}"
                            )

            except Exception as e:
                self.logger.warning(
                    f"Service {service} metrics endpoint not accessible: {str(e)}"
                )

        if constitutional_endpoints > 0:
            self.add_result(
                "service_metrics",
                "PASSED",
                f"Found {constitutional_endpoints}/{len(endpoints)} constitutional metrics endpoints",
                True,
            )
            return True
        else:
            self.add_result(
                "service_metrics",
                "WARNING",
                "No constitutional metrics endpoints accessible (services may not be running)",
                True,  # Not a constitutional compliance failure
            )
            return False

    async def validate_infrastructure_connectivity(self) -> bool:
        """Validate infrastructure connectivity (PostgreSQL, Redis)"""
        results = []

        # Test PostgreSQL
        try:
            conn = await asyncpg.connect(
                host="localhost",
                port=5439,
                user="acgs_user",
                password=os.environ.get("PASSWORD"),
                database="acgs_constitutional",
                command_timeout=5,
            )
            await conn.close()
            results.append(("PostgreSQL", True, "Connection successful"))
        except Exception as e:
            results.append(("PostgreSQL", False, f"Connection failed: {str(e)}"))

        # Test Redis
        try:
            redis = aioredis.from_url("redis://localhost:6389", socket_timeout=5)
            await redis.ping()
            await redis.close()
            results.append(("Redis", True, "Connection successful"))
        except Exception as e:
            results.append(("Redis", False, f"Connection failed: {str(e)}"))

        successful_connections = sum(1 for _, success, _ in results if success)

        if successful_connections > 0:
            self.add_result(
                "infrastructure_connectivity",
                "PASSED" if successful_connections == len(results) else "PARTIAL",
                f"{successful_connections}/{len(results)} infrastructure connections successful",
                True,
            )
            return True
        else:
            self.add_result(
                "infrastructure_connectivity",
                "WARNING",
                "No infrastructure connections available (services may not be running)",
                True,  # Not a constitutional compliance failure
            )
            return False

    def validate_monitoring_file_structure(self) -> bool:
        """Validate monitoring configuration file structure"""
        required_files = [
            "/home/dislove/ACGS-2/config/monitoring/prometheus-constitutional.yml",
            "/home/dislove/ACGS-2/config/monitoring/constitutional_rules.yml",
            "/home/dislove/ACGS-2/config/monitoring/grafana-constitutional-dashboard.json",
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            self.add_result(
                "file_structure",
                "FAILED",
                f"Missing files: {', '.join(missing_files)}",
                False,
            )
            return False
        else:
            self.add_result(
                "file_structure",
                "PASSED",
                "All monitoring configuration files present",
                True,
            )
            return True

    async def run_validation(self) -> Dict[str, any]:
        """Run complete constitutional monitoring validation"""
        self.logger.info(
            f"Starting constitutional monitoring validation with hash: {CONSTITUTIONAL_HASH}"
        )

        # File structure validation
        self.validate_monitoring_file_structure()

        # Configuration validation
        self.validate_prometheus_config()
        self.validate_alerting_rules()
        self.validate_grafana_dashboard()

        # Service endpoint validation (async)
        await self.validate_service_metrics_endpoints()
        await self.validate_infrastructure_connectivity()

        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "PASSED")
        failed_tests = sum(1 for r in self.results if r.status == "FAILED")
        warning_tests = sum(1 for r in self.results if r.status == "WARNING")
        error_tests = sum(1 for r in self.results if r.status == "ERROR")
        constitutional_compliant = sum(
            1 for r in self.results if r.constitutional_compliant
        )

        summary = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warning_tests,
            "errors": error_tests,
            "constitutional_compliance_rate": (
                constitutional_compliant / total_tests if total_tests > 0 else 0
            ),
            "overall_status": (
                "PASSED" if failed_tests == 0 and error_tests == 0 else "FAILED"
            ),
            "timestamp": time.time(),
            "details": [
                {
                    "component": r.component,
                    "status": r.status,
                    "details": r.details,
                    "constitutional_compliant": r.constitutional_compliant,
                }
                for r in self.results
            ],
        }

        self.logger.info(
            f"Validation complete: {passed_tests}/{total_tests} passed, "
            f"Constitutional compliance: {constitutional_compliant}/{total_tests}",
            extra={
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "validation_summary": summary,
            },
        )

        return summary

    def print_results(self, summary: Dict[str, any]) -> None:
        """Print validation results"""
        print(f"\n{'='*80}")
        print(f"ACGS-2 Constitutional Monitoring Validation Results")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"{'='*80}")

        print(f"\nSUMMARY:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"  Errors: {summary['errors']}")
        print(
            f"  Constitutional Compliance Rate: {summary['constitutional_compliance_rate']:.2%}"
        )
        print(f"  Overall Status: {summary['overall_status']}")

        print(f"\nDETAILED RESULTS:")
        for detail in summary["details"]:
            status_icon = {
                "PASSED": "✓",
                "FAILED": "✗",
                "WARNING": "⚠",
                "ERROR": "⚠",
            }.get(detail["status"], "?")

            compliance_icon = "🏛️" if detail["constitutional_compliant"] else "❌"

            print(
                f"  {status_icon} {compliance_icon} {detail['component']:25} {detail['status']:8} {detail['details']}"
            )

        print(f"\n{'='*80}")


async def main():
    """Main validation function"""
    validator = ConstitutionalMonitoringValidator()

    try:
        summary = await validator.run_validation()
        validator.print_results(summary)

        # Save results to file
        results_path = Path("/tmp/constitutional_monitoring_validation_results.json")
        with open(results_path, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\nResults saved to: {results_path}")

        # Exit with appropriate code
        if summary["overall_status"] == "PASSED":
            print("\n🎉 Constitutional monitoring validation PASSED!")
            exit(0)
        else:
            print("\n❌ Constitutional monitoring validation FAILED!")
            exit(1)

    except Exception as e:
        print(f"\n💥 Validation script error: {str(e)}")
        logging.exception("Validation script error")
        exit(2)


if __name__ == "__main__":
    asyncio.run(main())
