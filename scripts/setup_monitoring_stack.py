#!/usr/bin/env python3
"""
ACGS-PGP Monitoring Stack Setup Script

Configures Prometheus metrics collection, Grafana dashboards for constitutional
compliance monitoring, and alert rules for 0.75 threshold violations.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MonitoringStackSetup:
    """Setup comprehensive monitoring stack for ACGS-PGP."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.compliance_threshold = 0.75
        self.services = {
            "auth_service": 8000,
            "ac_service": 8001,
            "integrity_service": 8002,
            "fv_service": 8003,
            "gs_service": 8004,
            "pgc_service": 8005,
            "ec_service": 8006,
        }

    def create_prometheus_config(self) -> dict[str, Any]:
        """Create Prometheus configuration."""
        logger.info("📊 Creating Prometheus configuration...")

        config = {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "rule_files": [
                "rules/acgs_constitutional_compliance.yml",
                "rules/acgs_performance_alerts.yml",
                "rules/acgs_security_alerts.yml",
            ],
            "alerting": {
                "alertmanagers": [
                    {"static_configs": [{"targets": ["alertmanager:9093"]}]}
                ]
            },
            "scrape_configs": [
                {
                    "job_name": "prometheus",
                    "static_configs": [{"targets": ["localhost:9090"]}],
                }
            ],
        }

        # Add ACGS service targets
        for service_name, port in self.services.items():
            config["scrape_configs"].append(
                {
                    "job_name": f"acgs_{service_name}",
                    "static_configs": [{"targets": [f"localhost:{port}"]}],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s",
                    "params": {"constitutional_hash": [self.constitutional_hash]},
                }
            )

        return config

    def create_constitutional_compliance_rules(self) -> dict[str, Any]:
        """Create constitutional compliance alert rules."""
        logger.info("🏛️ Creating constitutional compliance alert rules...")

        rules = {
            "groups": [
                {
                    "name": "acgs_constitutional_compliance",
                    "interval": "30s",
                    "rules": [
                        {
                            "alert": "ConstitutionalComplianceBelow75Percent",
                            "expr": "acgs_constitutional_compliance_score < 0.75",
                            "for": "1m",
                            "labels": {
                                "severity": "critical",
                                "constitutional_hash": self.constitutional_hash,
                            },
                            "annotations": {
                                "summary": "Constitutional compliance below 75% threshold",
                                "description": "Service {{ $labels.service }} has constitutional compliance score of {{ $value }} which is below the required 0.75 threshold",
                            },
                        },
                        {
                            "alert": "ConstitutionalHashMismatch",
                            "expr": "acgs_constitutional_hash_valid == 0",
                            "for": "0s",
                            "labels": {
                                "severity": "critical",
                                "constitutional_hash": self.constitutional_hash,
                            },
                            "annotations": {
                                "summary": "Constitutional hash validation failed",
                                "description": "Service {{ $labels.service }} has invalid constitutional hash",
                            },
                        },
                        {
                            "alert": "DGMSafetyPatternViolation",
                            "expr": "acgs_dgm_safety_score < 0.95",
                            "for": "2m",
                            "labels": {
                                "severity": "warning",
                                "constitutional_hash": self.constitutional_hash,
                            },
                            "annotations": {
                                "summary": "DGM safety pattern violation detected",
                                "description": "Service {{ $labels.service }} DGM safety score is {{ $value }}",
                            },
                        },
                        {
                            "alert": "EmergencyShutdownRequired",
                            "expr": "acgs_constitutional_compliance_score < 0.5",
                            "for": "30s",
                            "labels": {
                                "severity": "critical",
                                "constitutional_hash": self.constitutional_hash,
                            },
                            "annotations": {
                                "summary": "Emergency shutdown required - critical compliance failure",
                                "description": "Service {{ $labels.service }} compliance score {{ $value }} requires immediate emergency shutdown",
                            },
                        },
                    ],
                }
            ]
        }

        return rules

    def create_performance_alert_rules(self) -> dict[str, Any]:
        """Create performance alert rules."""
        logger.info("⚡ Creating performance alert rules...")

        rules = {
            "groups": [
                {
                    "name": "acgs_performance_alerts",
                    "interval": "15s",
                    "rules": [
                        {
                            "alert": "ResponseTimeExceeds2Seconds",
                            "expr": 'acgs_http_request_duration_seconds{quantile="0.95"} > 2',
                            "for": "1m",
                            "labels": {
                                "severity": "warning",
                                "constitutional_hash": self.constitutional_hash,
                            },
                            "annotations": {
                                "summary": "Response time exceeds 2 second target",
                                "description": "Service {{ $labels.service }} 95th percentile response time is {{ $value }}s",
                            },
                        },
                        {
                            "alert": "HighErrorRate",
                            "expr": 'rate(acgs_http_requests_total{status=~"5.."}[5m]) > 0.05',
                            "for": "2m",
                            "labels": {
                                "severity": "critical",
                                "constitutional_hash": self.constitutional_hash,
                            },
                            "annotations": {
                                "summary": "High error rate detected",
                                "description": "Service {{ $labels.service }} error rate is {{ $value }}",
                            },
                        },
                        {
                            "alert": "ServiceDown",
                            "expr": 'up{job=~"acgs_.*"} == 0',
                            "for": "1m",
                            "labels": {
                                "severity": "critical",
                                "constitutional_hash": self.constitutional_hash,
                            },
                            "annotations": {
                                "summary": "ACGS service is down",
                                "description": "Service {{ $labels.job }} is not responding",
                            },
                        },
                    ],
                }
            ]
        }

        return rules

    def create_grafana_dashboard(self) -> dict[str, Any]:
        """Create Grafana dashboard for constitutional compliance."""
        logger.info("📈 Creating Grafana constitutional compliance dashboard...")

        dashboard = {
            "dashboard": {
                "id": None,
                "title": "ACGS-PGP Constitutional Compliance Dashboard",
                "tags": ["acgs", "constitutional", "compliance"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Constitutional Compliance Score",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "acgs_constitutional_compliance_score",
                                "legendFormat": "{{ service }}",
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 0.75},
                                        {"color": "green", "value": 0.95},
                                    ]
                                },
                                "min": 0,
                                "max": 1,
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    },
                    {
                        "id": 2,
                        "title": "Service Response Times",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": 'acgs_http_request_duration_seconds{quantile="0.95"}',
                                "legendFormat": "{{ service }} - 95th percentile",
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 1},
                                        {"color": "red", "value": 2},
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    },
                    {
                        "id": 3,
                        "title": "DGM Safety Patterns",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "acgs_dgm_safety_score",
                                "legendFormat": "{{ service }}",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                    },
                    {
                        "id": 4,
                        "title": "Constitutional Hash Validation",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "acgs_constitutional_hash_valid",
                                "legendFormat": "{{ service }}",
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "green", "value": 1},
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                    },
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "10s",
            }
        }

        return dashboard

    def create_docker_compose_monitoring(self) -> dict[str, Any]:
        """Create Docker Compose for monitoring stack."""
        logger.info("🐳 Creating Docker Compose monitoring configuration...")

        compose = {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "acgs-prometheus",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro",
                        "./config/rules:/etc/prometheus/rules:ro",
                        "prometheus_data:/prometheus",
                    ],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--storage.tsdb.retention.time=200h",
                        "--web.enable-lifecycle",
                    ],
                    "environment": {"CONSTITUTIONAL_HASH": self.constitutional_hash},
                    "networks": ["acgs-monitoring"],
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "acgs-grafana",
                    "ports": ["3000:3000"],
                    "volumes": [
                        "grafana_data:/var/lib/grafana",
                        "./config/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro",
                        "./config/grafana/datasources:/etc/grafana/provisioning/datasources:ro",
                    ],
                    "environment": {
                        "GF_SECURITY_ADMIN_PASSWORD": "acgs_admin_2025",
                        "GF_USERS_ALLOW_SIGN_UP": "false",
                        "CONSTITUTIONAL_HASH": self.constitutional_hash,
                    },
                    "networks": ["acgs-monitoring"],
                    "depends_on": ["prometheus"],
                },
                "alertmanager": {
                    "image": "prom/alertmanager:latest",
                    "container_name": "acgs-alertmanager",
                    "ports": ["9093:9093"],
                    "volumes": [
                        "./config/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro"
                    ],
                    "networks": ["acgs-monitoring"],
                },
            },
            "volumes": {"prometheus_data": {}, "grafana_data": {}},
            "networks": {
                "acgs-monitoring": {
                    "driver": "bridge",
                    "name": "acgs-monitoring-network",
                }
            },
        }

        return compose

    def setup_monitoring_stack(self) -> dict[str, Any]:
        """Setup complete monitoring stack."""
        logger.info("🚀 Setting up ACGS-PGP monitoring stack...")

        # Create monitoring directories
        monitoring_dir = self.project_root / "infrastructure/monitoring"
        config_dir = monitoring_dir / "config"
        rules_dir = config_dir / "rules"
        grafana_dir = config_dir / "grafana"

        for directory in [monitoring_dir, config_dir, rules_dir, grafana_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Create configurations
        prometheus_config = self.create_prometheus_config()
        compliance_rules = self.create_constitutional_compliance_rules()
        performance_rules = self.create_performance_alert_rules()
        grafana_dashboard = self.create_grafana_dashboard()
        docker_compose = self.create_docker_compose_monitoring()

        # Save configurations
        with open(config_dir / "prometheus.yml", "w") as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

        with open(rules_dir / "acgs_constitutional_compliance.yml", "w") as f:
            yaml.dump(compliance_rules, f, default_flow_style=False)

        with open(rules_dir / "acgs_performance_alerts.yml", "w") as f:
            yaml.dump(performance_rules, f, default_flow_style=False)

        with open(grafana_dir / "constitutional_dashboard.json", "w") as f:
            json.dump(grafana_dashboard, f, indent=2)

        with open(monitoring_dir / "docker-compose.monitoring.yml", "w") as f:
            yaml.dump(docker_compose, f, default_flow_style=False)

        # Create setup report
        setup_report = {
            "timestamp": "2025-01-25T12:00:00Z",
            "constitutional_hash": self.constitutional_hash,
            "monitoring_stack": "CONFIGURED",
            "prometheus_config": "CREATED",
            "grafana_dashboard": "CREATED",
            "alert_rules": "CREATED",
            "compliance_threshold": self.compliance_threshold,
            "services_monitored": len(self.services),
            "alert_rules_count": len(compliance_rules["groups"][0]["rules"])
            + len(performance_rules["groups"][0]["rules"]),
        }

        with open(monitoring_dir / "monitoring_setup_report.json", "w") as f:
            json.dump(setup_report, f, indent=2)

        logger.info(
            f"✅ Monitoring stack setup completed. Configuration saved to: {monitoring_dir}"
        )

        return setup_report


def main():
    """Main execution function."""
    setup = MonitoringStackSetup()
    report = setup.setup_monitoring_stack()

    print("\n" + "=" * 80)
    print("📊 ACGS-PGP MONITORING STACK SETUP COMPLETED")
    print("=" * 80)
    print(f"🏛️ Constitutional Hash: {report['constitutional_hash']}")
    print(f"📈 Prometheus Config: {report['prometheus_config']}")
    print(f"📊 Grafana Dashboard: {report['grafana_dashboard']}")
    print(f"🚨 Alert Rules: {report['alert_rules_count']} rules created")
    print(f"🎯 Compliance Threshold: {report['compliance_threshold']}")
    print(f"🔧 Services Monitored: {report['services_monitored']}")
    print(f"✅ Status: {report['monitoring_stack']}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
