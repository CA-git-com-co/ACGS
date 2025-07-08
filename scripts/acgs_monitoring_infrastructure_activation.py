#!/usr/bin/env python3
"""
ACGS Monitoring Infrastructure Activation
Constitutional Hash: cdd01ef066bc6cf2

Activate Prometheus metrics collection and Grafana dashboards for all ACGS services
with constitutional compliance tracking and performance monitoring.
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

import requests

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# Monitoring service configurations
MONITORING_SERVICES = {
    "prometheus": {
        "port": 9091,
        "health_endpoint": "/-/healthy",
        "container_name": "acgs_prometheus_production",
    },
    "grafana": {
        "port": 3001,
        "health_endpoint": "/api/health",
        "container_name": "acgs_grafana_production",
    },
}

# ACGS services to monitor
ACGS_SERVICES_TO_MONITOR = {
    "rules-engine": {"port": 8020, "metrics_endpoint": "/metrics"},
    "code-analysis": {"port": 8107, "metrics_endpoint": "/metrics"},
    "auth-service-mock": {"port": 8116, "metrics_endpoint": "/metrics"},
    "context-service-mock": {"port": 8112, "metrics_endpoint": "/metrics"},
}


class ACGSMonitoringActivator:
    """ACGS monitoring infrastructure activation and validation."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.activation_results = {
            "monitoring_services": {},
            "dashboard_deployment": {},
            "metrics_collection": {},
            "constitutional_compliance": {},
            "alerting_setup": {},
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for monitoring activation."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    def _run_command(
        self, command: str, cwd: Path = None, timeout: int = 60
    ) -> tuple[bool, str, str]:
        """Run shell command safely."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd or REPO_ROOT,
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def check_monitoring_services_status(self) -> dict[str, bool]:
        """Check status of monitoring services."""
        self.logger.info("🔍 Checking monitoring services status...")

        status_results = {}

        for service_name, config in MONITORING_SERVICES.items():
            port = config["port"]
            endpoint = config["health_endpoint"]
            url = f"http://localhost:{port}{endpoint}"

            try:
                response = requests.get(url, timeout=10)
                is_healthy = response.status_code == 200
                status_results[service_name] = is_healthy

                if is_healthy:
                    self.logger.info(f"  ✅ {service_name} is healthy on port {port}")
                else:
                    self.logger.warning(
                        f"  ⚠️ {service_name} responded with status"
                        f" {response.status_code}"
                    )

            except Exception as e:
                status_results[service_name] = False
                self.logger.warning(f"  ❌ {service_name} is not accessible: {e}")

        self.activation_results["monitoring_services"] = status_results
        return status_results

    def validate_prometheus_configuration(self) -> dict[str, bool]:
        """Validate Prometheus configuration and targets."""
        self.logger.info("📊 Validating Prometheus configuration...")

        prometheus_results = {
            "config_valid": False,
            "targets_discovered": False,
            "constitutional_metrics": False,
        }

        try:
            # Check Prometheus config
            config_url = "http://localhost:9091/api/v1/status/config"
            response = requests.get(config_url, timeout=10)

            if response.status_code == 200:
                prometheus_results["config_valid"] = True
                self.logger.info("  ✅ Prometheus configuration is valid")

                # Check for constitutional compliance in config
                config_data = response.json()
                config_yaml = config_data.get("data", {}).get("yaml", "")
                if CONSTITUTIONAL_HASH in config_yaml:
                    prometheus_results["constitutional_metrics"] = True
                    self.logger.info("  ✅ Constitutional compliance tracking enabled")
                else:
                    self.logger.warning(
                        "  ⚠️ Constitutional compliance tracking not found in config"
                    )

            # Check targets
            targets_url = "http://localhost:9091/api/v1/targets"
            response = requests.get(targets_url, timeout=10)

            if response.status_code == 200:
                targets_data = response.json()
                active_targets = targets_data.get("data", {}).get("activeTargets", [])

                if active_targets:
                    prometheus_results["targets_discovered"] = True
                    self.logger.info(f"  ✅ {len(active_targets)} targets discovered")

                    # Log some target details
                    for target in active_targets[:5]:  # Show first 5
                        job = target.get("labels", {}).get("job", "unknown")
                        health = target.get("health", "unknown")
                        self.logger.info(f"    Target: {job} - Health: {health}")
                else:
                    self.logger.warning("  ⚠️ No active targets found")

        except Exception as e:
            self.logger.error(f"  ❌ Failed to validate Prometheus: {e}")

        return prometheus_results

    def deploy_constitutional_compliance_dashboard(self) -> bool:
        """Deploy constitutional compliance dashboard to Grafana."""
        self.logger.info("📈 Deploying constitutional compliance dashboard...")

        # Check if constitutional compliance dashboard exists
        dashboard_path = (
            REPO_ROOT
            / "infrastructure/monitoring/grafana_dashboards/acgs_constitutional_compliance_dashboard.json"
        )

        if not dashboard_path.exists():
            self.logger.warning(f"  ⚠️ Dashboard file not found: {dashboard_path}")
            return False

        try:
            # Read dashboard JSON
            with open(dashboard_path) as f:
                dashboard_json = json.load(f)

            # Ensure constitutional hash is in dashboard
            dashboard_str = json.dumps(dashboard_json)
            if CONSTITUTIONAL_HASH not in dashboard_str:
                # Add constitutional hash to dashboard metadata
                if "tags" not in dashboard_json.get("dashboard", {}):
                    dashboard_json["dashboard"]["tags"] = []
                dashboard_json["dashboard"]["tags"].append(
                    f"constitutional-{CONSTITUTIONAL_HASH}"
                )

            # Deploy to Grafana
            grafana_url = "http://localhost:3001/api/dashboards/db"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer admin",  # Default admin token
            }

            # Try with admin:admin credentials
            import base64

            auth_string = base64.b64encode(b"admin:admin").decode("ascii")
            headers["Authorization"] = f"Basic {auth_string}"

            response = requests.post(
                grafana_url, json=dashboard_json, headers=headers, timeout=30
            )

            if response.status_code in [200, 201]:
                self.logger.info("  ✅ Constitutional compliance dashboard deployed")
                return True
            else:
                self.logger.warning(
                    f"  ⚠️ Dashboard deployment failed: {response.status_code}"
                )
                self.logger.warning(f"    Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"  ❌ Failed to deploy dashboard: {e}")
            return False

    def setup_constitutional_compliance_alerts(self) -> bool:
        """Setup constitutional compliance alerting rules."""
        self.logger.info("🚨 Setting up constitutional compliance alerts...")

        # Check if alert rules exist
        alert_rules_path = (
            REPO_ROOT / "infrastructure/monitoring/constitutional_compliance_alerts.yml"
        )

        if not alert_rules_path.exists():
            self.logger.warning(f"  ⚠️ Alert rules file not found: {alert_rules_path}")
            return False

        try:
            # Validate alert rules contain constitutional hash
            with open(alert_rules_path) as f:
                alert_content = f.read()

            if CONSTITUTIONAL_HASH not in alert_content:
                self.logger.warning("  ⚠️ Constitutional hash not found in alert rules")
                return False

            # Check if Prometheus can reload rules
            reload_url = "http://localhost:9091/-/reload"
            response = requests.post(reload_url, timeout=10)

            if response.status_code == 200:
                self.logger.info("  ✅ Constitutional compliance alerts configured")
                return True
            else:
                self.logger.warning(
                    f"  ⚠️ Failed to reload Prometheus rules: {response.status_code}"
                )
                return False

        except Exception as e:
            self.logger.error(f"  ❌ Failed to setup alerts: {e}")
            return False

    def validate_metrics_collection(self) -> dict[str, bool]:
        """Validate metrics collection from ACGS services."""
        self.logger.info("📊 Validating metrics collection...")

        metrics_results = {}

        for service_name, config in ACGS_SERVICES_TO_MONITOR.items():
            port = config["port"]
            endpoint = config["metrics_endpoint"]
            url = f"http://localhost:{port}{endpoint}"

            try:
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    metrics_content = response.text

                    # Check for basic Prometheus metrics
                    has_metrics = (
                        "# HELP" in metrics_content or "# TYPE" in metrics_content
                    )

                    # Check for constitutional compliance metrics
                    has_constitutional = CONSTITUTIONAL_HASH in metrics_content

                    metrics_results[service_name] = {
                        "metrics_available": has_metrics,
                        "constitutional_compliance": has_constitutional,
                    }

                    if has_metrics:
                        self.logger.info(f"  ✅ {service_name} metrics available")
                        if has_constitutional:
                            self.logger.info(
                                "    ✅ Constitutional compliance metrics found"
                            )
                        else:
                            self.logger.warning(
                                "    ⚠️ Constitutional compliance metrics missing"
                            )
                    else:
                        self.logger.warning(
                            f"  ⚠️ {service_name} metrics not in Prometheus format"
                        )
                else:
                    metrics_results[service_name] = {
                        "metrics_available": False,
                        "constitutional_compliance": False,
                    }
                    self.logger.warning(
                        f"  ❌ {service_name} metrics endpoint returned"
                        f" {response.status_code}"
                    )

            except Exception as e:
                metrics_results[service_name] = {
                    "metrics_available": False,
                    "constitutional_compliance": False,
                }
                self.logger.warning(f"  ❌ {service_name} metrics not accessible: {e}")

        self.activation_results["metrics_collection"] = metrics_results
        return metrics_results

    def test_performance_monitoring(self) -> dict[str, bool]:
        """Test performance monitoring capabilities."""
        self.logger.info("⚡ Testing performance monitoring...")

        performance_results = {
            "latency_metrics": False,
            "throughput_metrics": False,
            "error_rate_metrics": False,
        }

        try:
            # Query Prometheus for performance metrics
            queries = {
                "latency_metrics": (
                    "histogram_quantile(0.99,"
                    " rate(http_request_duration_seconds_bucket[5m]))"
                ),
                "throughput_metrics": "rate(http_requests_total[5m])",
                "error_rate_metrics": 'rate(http_requests_total{status=~"5.."}[5m])',
            }

            for metric_type, query in queries.items():
                query_url = "http://localhost:9091/api/v1/query"
                params = {"query": query}

                response = requests.get(query_url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    result = data.get("data", {}).get("result", [])

                    if result:
                        performance_results[metric_type] = True
                        self.logger.info(f"  ✅ {metric_type} available")
                    else:
                        self.logger.warning(f"  ⚠️ {metric_type} no data")
                else:
                    self.logger.warning(f"  ❌ {metric_type} query failed")

        except Exception as e:
            self.logger.error(f"  ❌ Performance monitoring test failed: {e}")

        return performance_results

    def generate_monitoring_activation_report(self) -> str:
        """Generate monitoring activation report."""
        self.logger.info("📄 Generating monitoring activation report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "activation_results": self.activation_results,
            "summary": {
                "monitoring_services_active": len([
                    s
                    for s in self.activation_results["monitoring_services"].values()
                    if s
                ]),
                "dashboards_deployed": len([
                    d
                    for d in self.activation_results["dashboard_deployment"].values()
                    if d
                ]),
                "services_monitored": len([
                    m
                    for m in self.activation_results["metrics_collection"].values()
                    if m.get("metrics_available", False)
                ]),
                "constitutional_compliance_enabled": any(
                    m.get("constitutional_compliance", False)
                    for m in self.activation_results["metrics_collection"].values()
                ),
                "overall_success": self._calculate_overall_success(),
            },
        }

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPO_ROOT / f"acgs_monitoring_activation_report_{timestamp}.json"

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"  📄 Report saved: {report_path.relative_to(REPO_ROOT)}")
        return str(report_path.relative_to(REPO_ROOT))

    def _calculate_overall_success(self) -> bool:
        """Calculate overall monitoring activation success."""
        # Check if core monitoring services are running
        prometheus_ok = self.activation_results["monitoring_services"].get(
            "prometheus", False
        )
        grafana_ok = self.activation_results["monitoring_services"].get(
            "grafana", False
        )

        # Check if at least some metrics are being collected
        any_metrics = any(
            m.get("metrics_available", False)
            for m in self.activation_results["metrics_collection"].values()
        )

        return prometheus_ok and grafana_ok and any_metrics

    def run_monitoring_activation(self) -> dict:
        """Run complete monitoring infrastructure activation."""
        self.logger.info("🚀 Starting ACGS Monitoring Infrastructure Activation...")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

        # Check monitoring services status
        self.check_monitoring_services_status()

        # Validate Prometheus
        prometheus_results = self.validate_prometheus_configuration()
        self.activation_results["prometheus_validation"] = prometheus_results

        # Deploy dashboards
        dashboard_deployed = self.deploy_constitutional_compliance_dashboard()
        self.activation_results["dashboard_deployment"][
            "constitutional_compliance"
        ] = dashboard_deployed

        # Setup alerts
        alerts_setup = self.setup_constitutional_compliance_alerts()
        self.activation_results["alerting_setup"][
            "constitutional_compliance"
        ] = alerts_setup

        # Validate metrics collection
        self.validate_metrics_collection()

        # Test performance monitoring
        performance_results = self.test_performance_monitoring()
        self.activation_results["performance_monitoring"] = performance_results

        # Generate report
        report_path = self.generate_monitoring_activation_report()

        # Summary
        overall_success = self._calculate_overall_success()

        self.logger.info("📊 Monitoring Activation Summary:")
        self.logger.info(
            "  Prometheus:"
            f" {'✅ Active' if self.activation_results['monitoring_services'].get('prometheus') else '❌ Inactive'}"
        )
        self.logger.info(
            "  Grafana:"
            f" {'✅ Active' if self.activation_results['monitoring_services'].get('grafana') else '❌ Inactive'}"
        )
        self.logger.info(
            "  Services Monitored:"
            f" {len([m for m in self.activation_results['metrics_collection'].values() if m.get('metrics_available', False)])}"
        )
        self.logger.info(
            "  Constitutional Compliance:"
            f" {'✅ Enabled' if any(m.get('constitutional_compliance', False) for m in self.activation_results['metrics_collection'].values()) else '⚠️ Limited'}"
        )
        self.logger.info(
            f"  Overall Success: {'✅ PASS' if overall_success else '❌ FAIL'}"
        )
        self.logger.info(f"  Report: {report_path}")

        return self.activation_results


def main():
    """Main monitoring activation function."""
    print("🚀 ACGS Monitoring Infrastructure Activation")
    print("=" * 50)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    activator = ACGSMonitoringActivator()
    results = activator.run_monitoring_activation()

    overall_success = activator._calculate_overall_success()
    if overall_success:
        print("\n✅ Monitoring infrastructure activation completed successfully!")
    else:
        print("\n⚠️ Monitoring infrastructure activation completed with issues")

    return results


if __name__ == "__main__":
    main()
