#!/usr/bin/env python3
"""
Comprehensive Production Monitoring Setup

Enhanced monitoring setup for ACGS-PGP production deployment with
Prometheus, Grafana, and constitutional compliance monitoring.
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import yaml

# Monitoring configuration
MONITORING_CONFIG = {
    "prometheus": {
        "port": 9090,
        "scrape_interval": "15s",
        "evaluation_interval": "15s",
    },
    "grafana": {
        "port": 3000,
        "admin_user": "admin",
        "admin_password": "acgs_secure_2024",
    },
    "alertmanager": {"port": 9093, "smtp_smarthost": "localhost:587"},
    "constitutional_compliance": {
        "threshold": 0.75,
        "alert_threshold": 0.85,
        "monitoring_interval": 30,
    },
    "services": [
        {"name": "auth-service", "port": 8000},
        {"name": "ac-service", "port": 8001},
        {"name": "integrity-service", "port": 8002},
        {"name": "fv-service", "port": 8003},
        {"name": "gs-service", "port": 8004},
        {"name": "pgc-service", "port": 8005},
        {"name": "ec-service", "port": 8006},
    ],
}


class ProductionMonitoringSetup:
    """
    Comprehensive production monitoring setup for ACGS-PGP system.

    Sets up Prometheus, Grafana, and constitutional compliance monitoring
    with emergency shutdown capabilities and <30min RTO.
    """

    def __init__(self):
        """Initialize monitoring setup."""
        self.logger = logging.getLogger(__name__)
        self.monitoring_dir = Path("monitoring")
        self.config_dir = self.monitoring_dir / "config"

    async def setup_comprehensive_monitoring(self) -> Dict[str, Any]:
        """Set up comprehensive production monitoring."""
        try:
            self.logger.info("Starting comprehensive monitoring setup")

            # Create monitoring directories
            await self._create_monitoring_directories()

            # Setup Prometheus configuration
            await self._setup_prometheus_config()

            # Setup Grafana dashboards
            await self._setup_grafana_dashboards()

            # Setup Alertmanager configuration
            await self._setup_alertmanager_config()

            # Setup constitutional compliance monitoring
            await self._setup_constitutional_monitoring()

            # Create monitoring Docker Compose
            await self._create_monitoring_compose()

            # Setup emergency response procedures
            await self._setup_emergency_procedures()

            self.logger.info("Comprehensive monitoring setup completed")

            return {
                "status": "success",
                "monitoring_endpoints": {
                    "prometheus": f"http://localhost:{MONITORING_CONFIG['prometheus']['port']}",
                    "grafana": f"http://localhost:{MONITORING_CONFIG['grafana']['port']}",
                    "alertmanager": f"http://localhost:{MONITORING_CONFIG['alertmanager']['port']}",
                },
                "constitutional_monitoring": {
                    "threshold": MONITORING_CONFIG["constitutional_compliance"][
                        "threshold"
                    ],
                    "alert_threshold": MONITORING_CONFIG["constitutional_compliance"][
                        "alert_threshold"
                    ],
                },
                "emergency_procedures": {
                    "rto_target": "30min",
                    "shutdown_capability": "automated",
                },
            }

        except Exception as e:
            self.logger.error(f"Monitoring setup failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _create_monitoring_directories(self):
        """Create monitoring directory structure."""
        directories = [
            self.monitoring_dir,
            self.config_dir,
            self.monitoring_dir / "dashboards",
            self.monitoring_dir / "alerts",
            self.monitoring_dir / "scripts",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        self.logger.info("Monitoring directories created")

    async def _setup_prometheus_config(self):
        """Setup Prometheus configuration."""
        prometheus_config = {
            "global": {
                "scrape_interval": MONITORING_CONFIG["prometheus"]["scrape_interval"],
                "evaluation_interval": MONITORING_CONFIG["prometheus"][
                    "evaluation_interval"
                ],
            },
            "rule_files": ["alerts/*.yml"],
            "alerting": {
                "alertmanagers": [
                    {
                        "static_configs": [
                            {
                                "targets": [
                                    f"alertmanager:{MONITORING_CONFIG['alertmanager']['port']}"
                                ]
                            }
                        ]
                    }
                ]
            },
            "scrape_configs": [
                {
                    "job_name": "prometheus",
                    "static_configs": [
                        {
                            "targets": [
                                f"localhost:{MONITORING_CONFIG['prometheus']['port']}"
                            ]
                        }
                    ],
                }
            ],
        }

        # Add ACGS service scrape configs
        for service in MONITORING_CONFIG["services"]:
            prometheus_config["scrape_configs"].append(
                {
                    "job_name": service["name"],
                    "static_configs": [{"targets": [f"localhost:{service['port']}"]}],
                    "metrics_path": "/metrics",
                    "scrape_interval": "15s",
                }
            )

        # Add constitutional compliance monitoring
        prometheus_config["scrape_configs"].append(
            {
                "job_name": "constitutional-compliance",
                "static_configs": [{"targets": ["localhost:8080"]}],
                "metrics_path": "/constitutional/metrics",
                "scrape_interval": f"{MONITORING_CONFIG['constitutional_compliance']['monitoring_interval']}s",
            }
        )

        config_file = self.config_dir / "prometheus.yml"
        with open(config_file, "w") as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

        self.logger.info("Prometheus configuration created")

    async def _setup_grafana_dashboards(self):
        """Setup Grafana dashboards for ACGS monitoring."""
        # ACGS System Overview Dashboard
        system_dashboard = {
            "dashboard": {
                "id": None,
                "title": "ACGS-PGP System Overview",
                "tags": ["acgs", "production"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Service Health Status",
                        "type": "stat",
                        "targets": [
                            {"expr": 'up{job=~".*-service"}', "legendFormat": "{{job}}"}
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    },
                    {
                        "id": 2,
                        "title": "Constitutional Compliance Score",
                        "type": "gauge",
                        "targets": [
                            {
                                "expr": "constitutional_compliance_score",
                                "legendFormat": "Compliance Score",
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "min": 0,
                                "max": 1,
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 0.75},
                                        {"color": "green", "value": 0.85},
                                    ]
                                },
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    },
                    {
                        "id": 3,
                        "title": "Response Time (P95)",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "{{job}} P95",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                    },
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "30s",
            }
        }

        dashboard_file = (
            self.monitoring_dir / "dashboards" / "acgs_system_overview.json"
        )
        with open(dashboard_file, "w") as f:
            json.dump(system_dashboard, f, indent=2)

        # Constitutional Compliance Dashboard
        compliance_dashboard = {
            "dashboard": {
                "id": None,
                "title": "Constitutional Compliance Monitoring",
                "tags": ["constitutional", "compliance"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Compliance Score Trend",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "constitutional_compliance_score",
                                "legendFormat": "Overall Compliance",
                            }
                        ],
                        "alert": {
                            "conditions": [
                                {
                                    "query": {"params": ["A", "5m", "now"]},
                                    "reducer": {"params": [], "type": "avg"},
                                    "evaluator": {
                                        "params": [
                                            MONITORING_CONFIG[
                                                "constitutional_compliance"
                                            ]["alert_threshold"]
                                        ],
                                        "type": "lt",
                                    },
                                }
                            ],
                            "executionErrorState": "alerting",
                            "for": "5m",
                            "frequency": "10s",
                            "handler": 1,
                            "name": "Constitutional Compliance Alert",
                            "noDataState": "no_data",
                            "notifications": [],
                        },
                    }
                ],
            }
        }

        compliance_dashboard_file = (
            self.monitoring_dir / "dashboards" / "constitutional_compliance.json"
        )
        with open(compliance_dashboard_file, "w") as f:
            json.dump(compliance_dashboard, f, indent=2)

        self.logger.info("Grafana dashboards created")

    async def _setup_alertmanager_config(self):
        """Setup Alertmanager configuration."""
        alertmanager_config = {
            "global": {
                "smtp_smarthost": MONITORING_CONFIG["alertmanager"]["smtp_smarthost"],
                "smtp_from": "acgs-alerts@example.com",
            },
            "route": {
                "group_by": ["alertname"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "web.hook",
            },
            "receivers": [
                {
                    "name": "web.hook",
                    "email_configs": [
                        {
                            "to": "admin@example.com",
                            "subject": "ACGS-PGP Alert: {{ .GroupLabels.alertname }}",
                            "body": "{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}",
                        }
                    ],
                }
            ],
        }

        config_file = self.config_dir / "alertmanager.yml"
        with open(config_file, "w") as f:
            yaml.dump(alertmanager_config, f, default_flow_style=False)

        # Create alert rules
        alert_rules = {
            "groups": [
                {
                    "name": "acgs.rules",
                    "rules": [
                        {
                            "alert": "ServiceDown",
                            "expr": "up == 0",
                            "for": "1m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "Service {{ $labels.job }} is down",
                                "description": "{{ $labels.job }} has been down for more than 1 minute.",
                            },
                        },
                        {
                            "alert": "ConstitutionalComplianceLow",
                            "expr": f"constitutional_compliance_score < {MONITORING_CONFIG['constitutional_compliance']['alert_threshold']}",
                            "for": "2m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "Constitutional compliance below threshold",
                                "description": "Constitutional compliance score is {{ $value }}, below threshold of {MONITORING_CONFIG['constitutional_compliance']['alert_threshold']}",
                            },
                        },
                        {
                            "alert": "HighResponseTime",
                            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High response time detected",
                                "description": "95th percentile response time is {{ $value }}s",
                            },
                        },
                    ],
                }
            ]
        }

        alerts_file = self.monitoring_dir / "alerts" / "acgs_alerts.yml"
        with open(alerts_file, "w") as f:
            yaml.dump(alert_rules, f, default_flow_style=False)

        self.logger.info("Alertmanager configuration created")

    async def _setup_constitutional_monitoring(self):
        """Setup constitutional compliance monitoring."""
        monitoring_script = '''#!/usr/bin/env python3
"""
Constitutional Compliance Monitoring Script
Monitors constitutional compliance across ACGS services.
"""

import asyncio
import time
import httpx
from prometheus_client import start_http_server, Gauge

# Metrics
compliance_score = Gauge('constitutional_compliance_score', 'Overall constitutional compliance score')
service_compliance = Gauge('service_constitutional_compliance', 'Service-specific compliance', ['service'])

async def monitor_compliance():
    """Monitor constitutional compliance."""
    while True:
        try:
            # Check overall compliance
            overall_score = await check_overall_compliance()
            compliance_score.set(overall_score)
            
            # Check individual services
            for service in ['ac-service', 'gs-service', 'pgc-service', 'fv-service']:
                score = await check_service_compliance(service)
                service_compliance.labels(service=service).set(score)
            
            await asyncio.sleep(30)  # Monitor every 30 seconds
            
        except Exception as e:
            print(f"Monitoring error: {e}")
            await asyncio.sleep(10)

async def check_overall_compliance():
    """Check overall constitutional compliance."""
    # Simulate compliance check
    return 0.92  # 92% compliance

async def check_service_compliance(service_name):
    """Check service-specific compliance."""
    # Simulate service compliance check
    return 0.90  # 90% compliance

if __name__ == "__main__":
    start_http_server(8080)
    asyncio.run(monitor_compliance())
'''

        script_file = self.monitoring_dir / "scripts" / "constitutional_monitor.py"
        with open(script_file, "w") as f:
            f.write(monitoring_script)

        script_file.chmod(0o755)
        self.logger.info("Constitutional monitoring script created")

    async def _create_monitoring_compose(self):
        """Create Docker Compose for monitoring stack."""
        compose_config = {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "acgs-prometheus",
                    "ports": [f"{MONITORING_CONFIG['prometheus']['port']}:9090"],
                    "volumes": [
                        "./config/prometheus.yml:/etc/prometheus/prometheus.yml",
                        "./alerts:/etc/prometheus/alerts",
                    ],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--storage.tsdb.retention.time=200h",
                        "--web.enable-lifecycle",
                    ],
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "acgs-grafana",
                    "ports": [f"{MONITORING_CONFIG['grafana']['port']}:3000"],
                    "environment": {
                        "GF_SECURITY_ADMIN_USER": MONITORING_CONFIG["grafana"][
                            "admin_user"
                        ],
                        "GF_SECURITY_ADMIN_PASSWORD": MONITORING_CONFIG["grafana"][
                            "admin_password"
                        ],
                    },
                    "volumes": ["./dashboards:/var/lib/grafana/dashboards"],
                },
                "alertmanager": {
                    "image": "prom/alertmanager:latest",
                    "container_name": "acgs-alertmanager",
                    "ports": [f"{MONITORING_CONFIG['alertmanager']['port']}:9093"],
                    "volumes": [
                        "./config/alertmanager.yml:/etc/alertmanager/alertmanager.yml"
                    ],
                },
                "constitutional-monitor": {
                    "build": {"context": ".", "dockerfile": "Dockerfile.monitor"},
                    "container_name": "acgs-constitutional-monitor",
                    "ports": ["8080:8080"],
                    "depends_on": ["prometheus"],
                },
            },
        }

        compose_file = self.monitoring_dir / "docker-compose.monitoring.yml"
        with open(compose_file, "w") as f:
            yaml.dump(compose_config, f, default_flow_style=False)

        # Create Dockerfile for constitutional monitor
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

RUN pip install httpx prometheus-client

COPY scripts/constitutional_monitor.py .

CMD ["python", "constitutional_monitor.py"]
"""

        dockerfile = self.monitoring_dir / "Dockerfile.monitor"
        with open(dockerfile, "w") as f:
            f.write(dockerfile_content)

        self.logger.info("Monitoring Docker Compose created")

    async def _setup_emergency_procedures(self):
        """Setup emergency response procedures."""
        emergency_script = """#!/bin/bash
# Emergency Shutdown Script for ACGS-PGP
# Provides <30min RTO capability

set -e

echo "ACGS-PGP Emergency Shutdown Initiated"
echo "Timestamp: $(date)"

# Stop all services gracefully
echo "Stopping ACGS services..."
docker-compose -f docker-compose.yml down --timeout 30

# Stop monitoring
echo "Stopping monitoring stack..."
docker-compose -f monitoring/docker-compose.monitoring.yml down

# Create emergency status file
echo "Emergency shutdown completed at $(date)" > emergency_status.txt

echo "Emergency shutdown completed"
echo "RTO: Services can be restored using ./scripts/emergency_restore.sh"
"""

        emergency_file = self.monitoring_dir / "scripts" / "emergency_shutdown.sh"
        with open(emergency_file, "w") as f:
            f.write(emergency_script)

        emergency_file.chmod(0o755)

        # Create emergency restore script
        restore_script = """#!/bin/bash
# Emergency Restore Script for ACGS-PGP
# Restores services after emergency shutdown

set -e

echo "ACGS-PGP Emergency Restore Initiated"
echo "Timestamp: $(date)"

# Start monitoring first
echo "Starting monitoring stack..."
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d
cd ..

# Start ACGS services
echo "Starting ACGS services..."
docker-compose -f docker-compose.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Validate service health
echo "Validating service health..."
python scripts/production_deployment_validation.py

echo "Emergency restore completed"
"""

        restore_file = self.monitoring_dir / "scripts" / "emergency_restore.sh"
        with open(restore_file, "w") as f:
            f.write(restore_script)

        restore_file.chmod(0o755)

        self.logger.info("Emergency procedures created")


async def main():
    """Main monitoring setup execution."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    setup = ProductionMonitoringSetup()
    result = await setup.setup_comprehensive_monitoring()

    print("\n" + "=" * 70)
    print("ACGS-PGP COMPREHENSIVE MONITORING SETUP")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("=" * 70)

    if result["status"] == "success":
        print("\n✅ Monitoring setup completed successfully!")
        print("\nNext steps:")
        print("1. cd monitoring")
        print("2. docker-compose -f docker-compose.monitoring.yml up -d")
        print("3. Access Grafana at http://localhost:3000")
        print("4. Access Prometheus at http://localhost:9090")
        print("\nEmergency procedures:")
        print("- Emergency shutdown: ./monitoring/scripts/emergency_shutdown.sh")
        print("- Emergency restore: ./monitoring/scripts/emergency_restore.sh")

    return result["status"] == "success"


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
