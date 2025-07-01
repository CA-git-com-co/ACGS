#!/usr/bin/env python3
"""
ACGS-1 Monitoring Setup and Validation
======================================

This script sets up and validates monitoring systems (Prometheus, Grafana, alerting)
for the reorganized ACGS-1 structure.

Key Features:
1. Validate existing monitoring configurations
2. Update monitoring targets for new service structure
3. Create monitoring dashboards for all 7 services
4. Set up alerting rules for critical metrics
5. Test monitoring endpoints and data collection
"""

import json
import time
import logging
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("monitoring_setup.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ACGSMonitoringSetup:
    """ACGS-1 Monitoring Setup and Validation."""

    def __init__(self, project_root: str = "/home/ubuntu/ACGS"):
        self.project_root = Path(project_root)
        self.services = [
            {"name": "auth_service", "port": 8000, "url": "http://localhost:8000"},
            {"name": "ac_service", "port": 8001, "url": "http://localhost:8001"},
            {"name": "integrity_service", "port": 8002, "url": "http://localhost:8002"},
            {"name": "fv_service", "port": 8003, "url": "http://localhost:8003"},
            {"name": "gs_service", "port": 8004, "url": "http://localhost:8004"},
            {"name": "pgc_service", "port": 8005, "url": "http://localhost:8005"},
            {"name": "ec_service", "port": 8006, "url": "http://localhost:8006"},
        ]
        self.monitoring_results = []
        self.monitoring_dir = self.project_root / "infrastructure" / "monitoring"

    def setup_and_validate_all(self):
        """Set up and validate all monitoring components."""
        logger.info("🔧 Starting ACGS-1 Monitoring Setup and Validation")
        logger.info("=" * 60)

        # Setup tasks
        setup_tasks = [
            ("Create Monitoring Directory Structure", self.create_monitoring_structure),
            ("Generate Prometheus Configuration", self.generate_prometheus_config),
            ("Create Grafana Dashboard", self.create_grafana_dashboard),
            ("Setup Alerting Rules", self.setup_alerting_rules),
            ("Validate Service Metrics", self.validate_service_metrics),
            ("Test Monitoring Endpoints", self.test_monitoring_endpoints),
            ("Generate Monitoring Documentation", self.generate_monitoring_docs),
        ]

        for task_name, task_func in setup_tasks:
            logger.info(f"\n📋 {task_name}...")
            try:
                task_func()
                self.monitoring_results.append(
                    {"task": task_name, "success": True, "timestamp": time.time()}
                )
                logger.info(f"✅ {task_name} completed successfully")
            except Exception as e:
                logger.error(f"❌ {task_name} failed: {e}")
                self.monitoring_results.append(
                    {
                        "task": task_name,
                        "success": False,
                        "error": str(e),
                        "timestamp": time.time(),
                    }
                )

        return self.monitoring_results

    def create_monitoring_structure(self):
        """Create the monitoring directory structure."""
        directories = [
            self.monitoring_dir,
            self.monitoring_dir / "prometheus",
            self.monitoring_dir / "grafana",
            self.monitoring_dir / "alertmanager",
            self.monitoring_dir / "dashboards",
            self.monitoring_dir / "rules",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"Created directory: {directory.relative_to(self.project_root)}"
            )

    def generate_prometheus_config(self):
        """Generate Prometheus configuration for all services."""
        prometheus_config = {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "rule_files": ["rules/*.yml"],
            "alerting": {
                "alertmanagers": [{"static_configs": [{"targets": ["localhost:9093"]}]}]
            },
            "scrape_configs": [
                {
                    "job_name": "prometheus",
                    "static_configs": [{"targets": ["localhost:9090"]}],
                }
            ],
        }

        # Add scrape configs for all ACGS services
        for service in self.services:
            scrape_config = {
                "job_name": service["name"],
                "static_configs": [{"targets": [f"localhost:{service['port']}"]}],
                "metrics_path": "/metrics",
                "scrape_interval": "10s",
                "scrape_timeout": "5s",
            }
            prometheus_config["scrape_configs"].append(scrape_config)

        # Save Prometheus configuration
        config_file = self.monitoring_dir / "prometheus" / "prometheus.yml"
        with open(config_file, "w") as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

        logger.info(
            f"Generated Prometheus config: {config_file.relative_to(self.project_root)}"
        )

    def create_grafana_dashboard(self):
        """Create Grafana dashboard for ACGS services."""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "ACGS-1 Services Dashboard",
                "tags": ["acgs", "services", "monitoring"],
                "timezone": "browser",
                "panels": [],
                "time": {"from": "now-1h", "to": "now"},
                "timepicker": {},
                "templating": {"list": []},
                "annotations": {"list": []},
                "refresh": "30s",
                "schemaVersion": 16,
                "version": 1,
            }
        }

        # Add panels for each service
        panel_id = 1
        for i, service in enumerate(self.services):
            # Response time panel
            response_time_panel = {
                "id": panel_id,
                "title": f"{service['name']} Response Time",
                "type": "graph",
                "targets": [
                    {
                        "expr": f"histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{job=\"{service['name']}\"}}[5m]))",
                        "legendFormat": "95th percentile",
                        "refId": "A",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": (i % 2) * 12, "y": (i // 2) * 8},
                "yAxes": [{"label": "seconds", "min": 0}, {}],
            }
            dashboard["dashboard"]["panels"].append(response_time_panel)
            panel_id += 1

        # Save Grafana dashboard
        dashboard_file = (
            self.monitoring_dir / "dashboards" / "acgs_services_dashboard.json"
        )
        with open(dashboard_file, "w") as f:
            json.dump(dashboard, f, indent=2)

        logger.info(
            f"Generated Grafana dashboard: {dashboard_file.relative_to(self.project_root)}"
        )

    def setup_alerting_rules(self):
        """Set up alerting rules for critical metrics."""
        alerting_rules = {
            "groups": [
                {
                    "name": "acgs_services",
                    "rules": [
                        {
                            "alert": "ServiceDown",
                            "expr": "up == 0",
                            "for": "1m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "Service {{ $labels.job }} is down",
                                "description": "Service {{ $labels.job }} has been down for more than 1 minute.",
                            },
                        },
                        {
                            "alert": "HighResponseTime",
                            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High response time for {{ $labels.job }}",
                                "description": "95th percentile response time is above 500ms for {{ $labels.job }}.",
                            },
                        },
                        {
                            "alert": "ConstitutionalHashMismatch",
                            "expr": "constitutional_hash_valid == 0",
                            "for": "1m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "Constitutional hash validation failed",
                                "description": "Constitutional hash validation failed for {{ $labels.service }}.",
                            },
                        },
                    ],
                }
            ]
        }

        # Save alerting rules
        rules_file = self.monitoring_dir / "rules" / "acgs_alerts.yml"
        with open(rules_file, "w") as f:
            yaml.dump(alerting_rules, f, default_flow_style=False)

        logger.info(
            f"Generated alerting rules: {rules_file.relative_to(self.project_root)}"
        )

    def validate_service_metrics(self):
        """Validate that services expose metrics endpoints."""
        metrics_status = {}

        for service in self.services:
            try:
                # Check if service has metrics endpoint
                metrics_url = f"{service['url']}/metrics"
                response = requests.get(metrics_url, timeout=5)

                if response.status_code == 200:
                    metrics_content = response.text
                    # Check for basic Prometheus metrics
                    has_basic_metrics = any(
                        metric in metrics_content
                        for metric in [
                            "http_requests_total",
                            "http_request_duration",
                            "process_cpu_seconds",
                            "process_resident_memory",
                        ]
                    )

                    metrics_status[service["name"]] = {
                        "endpoint_available": True,
                        "has_basic_metrics": has_basic_metrics,
                        "metrics_count": len(metrics_content.split("\n")),
                    }

                    if has_basic_metrics:
                        logger.info(f"✅ {service['name']} metrics endpoint validated")
                    else:
                        logger.warning(
                            f"⚠️ {service['name']} metrics endpoint available but limited metrics"
                        )
                else:
                    metrics_status[service["name"]] = {
                        "endpoint_available": False,
                        "status_code": response.status_code,
                    }
                    logger.warning(
                        f"⚠️ {service['name']} metrics endpoint returned {response.status_code}"
                    )

            except Exception as e:
                metrics_status[service["name"]] = {
                    "endpoint_available": False,
                    "error": str(e),
                }
                logger.warning(
                    f"⚠️ {service['name']} metrics endpoint not available: {e}"
                )

        # Save metrics validation report
        metrics_report = {
            "timestamp": time.time(),
            "services_with_metrics": len(
                [
                    s
                    for s in metrics_status.values()
                    if s.get("endpoint_available", False)
                ]
            ),
            "total_services": len(self.services),
            "metrics_status": metrics_status,
        }

        report_file = self.monitoring_dir / "metrics_validation_report.json"
        with open(report_file, "w") as f:
            json.dump(metrics_report, f, indent=2)

        logger.info(
            f"Metrics validation report: {report_file.relative_to(self.project_root)}"
        )

    def test_monitoring_endpoints(self):
        """Test monitoring endpoints and data collection."""
        monitoring_tests = []

        # Test service health endpoints
        for service in self.services:
            try:
                health_url = f"{service['url']}/health"
                response = requests.get(health_url, timeout=5)

                test_result = {
                    "service": service["name"],
                    "endpoint": "health",
                    "success": response.status_code == 200,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "status_code": response.status_code,
                }

                if response.status_code == 200:
                    health_data = response.json()
                    test_result["service_version"] = health_data.get(
                        "version", "unknown"
                    )
                    test_result["service_status"] = health_data.get("status", "unknown")

                monitoring_tests.append(test_result)

            except Exception as e:
                monitoring_tests.append(
                    {
                        "service": service["name"],
                        "endpoint": "health",
                        "success": False,
                        "error": str(e),
                    }
                )

        # Save monitoring test results
        test_report = {
            "timestamp": time.time(),
            "tests_passed": len(
                [t for t in monitoring_tests if t.get("success", False)]
            ),
            "total_tests": len(monitoring_tests),
            "test_results": monitoring_tests,
        }

        test_file = self.monitoring_dir / "monitoring_test_report.json"
        with open(test_file, "w") as f:
            json.dump(test_report, f, indent=2)

        logger.info(
            f"Monitoring test report: {test_file.relative_to(self.project_root)}"
        )

    def generate_monitoring_docs(self):
        """Generate monitoring documentation."""
        docs_content = f"""# ACGS-1 Monitoring Setup

## Overview
This document describes the monitoring setup for the ACGS-1 system after reorganization.

## Services Monitored
{chr(10).join(f"- {service['name']} (port {service['port']})" for service in self.services)}

## Monitoring Components

### Prometheus
- Configuration: `infrastructure/monitoring/prometheus/prometheus.yml`
- Scrapes metrics from all ACGS services every 10 seconds
- Stores metrics for alerting and visualization

### Grafana
- Dashboard: `infrastructure/monitoring/dashboards/acgs_services_dashboard.json`
- Visualizes service metrics, response times, and health status
- Access: http://localhost:3000 (default Grafana port)

### Alerting
- Rules: `infrastructure/monitoring/rules/acgs_alerts.yml`
- Alerts on service downtime, high response times, and constitutional hash issues
- Integrates with Alertmanager for notifications

## Key Metrics

### Service Health
- `up`: Service availability (1 = up, 0 = down)
- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request response times

### Constitutional Governance
- `constitutional_hash_valid`: Constitutional hash validation status
- Custom metrics for governance workflows

### Performance
- Response time percentiles (50th, 95th, 99th)
- Request rate and error rate
- Resource utilization (CPU, memory)

## Setup Instructions

1. **Start Prometheus**:
   ```bash
   cd infrastructure/monitoring/prometheus
   prometheus --config.file=prometheus.yml
   ```

2. **Start Grafana**:
   ```bash
   grafana-server --config=/etc/grafana/grafana.ini
   ```

3. **Import Dashboard**:
   - Access Grafana at http://localhost:3000
   - Import `dashboards/acgs_services_dashboard.json`

4. **Configure Alerting**:
   - Ensure Alertmanager is running
   - Alerts will be sent based on rules in `rules/acgs_alerts.yml`

## Troubleshooting

### Service Metrics Not Available
- Check if service `/metrics` endpoint is accessible
- Verify Prometheus configuration includes the service
- Check service logs for metric export issues

### Dashboard Not Showing Data
- Verify Prometheus is scraping the services
- Check Grafana data source configuration
- Ensure time range is appropriate

## Maintenance

- Monitor disk usage for Prometheus data storage
- Regularly update alerting rules based on operational experience
- Review and optimize dashboard queries for performance

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

        docs_file = self.monitoring_dir / "README.md"
        with open(docs_file, "w") as f:
            f.write(docs_content)

        logger.info(
            f"Generated monitoring documentation: {docs_file.relative_to(self.project_root)}"
        )

    def generate_report(self):
        """Generate comprehensive monitoring setup report."""
        successful_tasks = [
            t for t in self.monitoring_results if t.get("success", False)
        ]
        failed_tasks = [
            t for t in self.monitoring_results if not t.get("success", False)
        ]

        report = {
            "timestamp": time.time(),
            "summary": {
                "total_tasks": len(self.monitoring_results),
                "successful_tasks": len(successful_tasks),
                "failed_tasks": len(failed_tasks),
                "success_rate": (
                    (len(successful_tasks) / len(self.monitoring_results)) * 100
                    if self.monitoring_results
                    else 0
                ),
            },
            "monitoring_structure": {
                "prometheus_config": str(
                    self.monitoring_dir / "prometheus" / "prometheus.yml"
                ),
                "grafana_dashboard": str(
                    self.monitoring_dir / "dashboards" / "acgs_services_dashboard.json"
                ),
                "alerting_rules": str(
                    self.monitoring_dir / "rules" / "acgs_alerts.yml"
                ),
                "documentation": str(self.monitoring_dir / "README.md"),
            },
            "services_configured": len(self.services),
            "task_results": self.monitoring_results,
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self):
        """Generate recommendations based on monitoring setup."""
        recommendations = []

        failed_tasks = [
            t for t in self.monitoring_results if not t.get("success", False)
        ]
        if failed_tasks:
            recommendations.append(
                f"Address {len(failed_tasks)} failed monitoring setup tasks"
            )

        recommendations.extend(
            [
                "Install and configure Prometheus server",
                "Install and configure Grafana server",
                "Set up Alertmanager for alert notifications",
                "Configure notification channels (email, Slack, etc.)",
                "Test all monitoring components end-to-end",
                "Set up log aggregation (ELK stack or similar)",
                "Configure backup for monitoring data",
                "Establish monitoring runbooks and procedures",
            ]
        )

        return recommendations


def main():
    """Main execution function."""
    monitor_setup = ACGSMonitoringSetup()

    try:
        # Run monitoring setup
        results = monitor_setup.setup_and_validate_all()

        # Generate and save report
        report = monitor_setup.generate_report()

        with open("monitoring_setup_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 MONITORING SETUP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tasks: {report['summary']['total_tasks']}")
        logger.info(f"Successful: {report['summary']['successful_tasks']}")
        logger.info(f"Failed: {report['summary']['failed_tasks']}")
        logger.info(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        logger.info(f"Services Configured: {report['services_configured']}")

        if report["recommendations"]:
            logger.info("\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"], 1):
                logger.info(f"{i}. {rec}")

        logger.info(f"\n📄 Detailed report saved to: monitoring_setup_report.json")

        # Exit with appropriate code
        if report["summary"]["success_rate"] >= 80:
            logger.info("✅ Monitoring setup completed successfully!")
            return 0
        else:
            logger.error("❌ Monitoring setup completed with issues")
            return 1

    except Exception as e:
        logger.error(f"Monitoring setup failed: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
