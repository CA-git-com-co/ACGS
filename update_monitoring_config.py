#!/usr/bin/env python3
"""
ACGS-1 Monitoring and Observability Configuration Updates
Updates monitoring configurations for new blockchain-focused directory structure
"""

import json
import logging
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MonitoringConfigUpdater:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.monitoring_dir = self.project_root / "infrastructure/monitoring"

        # Service configuration for monitoring
        self.services = {
            "authentication": {
                "port": 8000,
                "path": "services/platform/authentication",
            },
            "constitutional-ai": {
                "port": 8001,
                "path": "services/core/constitutional-ai",
            },
            "governance-synthesis": {
                "port": 8002,
                "path": "services/core/governance-synthesis",
            },
            "policy-governance": {
                "port": 8003,
                "path": "services/core/policy-governance",
            },
            "formal-verification": {
                "port": 8004,
                "path": "services/core/formal-verification",
            },
            "integrity": {"port": 8005, "path": "services/platform/integrity"},
            "evolutionary-computation": {
                "port": 8006,
                "path": "services/core/evolutionary-computation",
            },
        }

    def update_prometheus_config(self):
        """Update Prometheus configuration for new service structure"""
        logger.info("Updating Prometheus configuration...")

        prometheus_config = {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "rule_files": ["rules/*.yml"],
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

        # Add ACGS-1 core services
        for service_name, config in self.services.items():
            prometheus_config["scrape_configs"].append(
                {
                    "job_name": f"acgs-{service_name}",
                    "static_configs": [{"targets": [f"localhost:{config['port']}"]}],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s",
                    "scrape_timeout": "5s",
                    "honor_labels": True,
                    "params": {"format": ["prometheus"]},
                }
            )

        # Add blockchain monitoring
        prometheus_config["scrape_configs"].extend(
            [
                {
                    "job_name": "solana-validator",
                    "static_configs": [{"targets": ["api.devnet.solana.com:443"]}],
                    "metrics_path": "/",
                    "scheme": "https",
                    "scrape_interval": "30s",
                },
                {
                    "job_name": "quantumagi-programs",
                    "static_configs": [
                        {"targets": ["localhost:8080"]}  # Custom metrics endpoint
                    ],
                    "metrics_path": "/blockchain/metrics",
                    "scrape_interval": "15s",
                },
            ]
        )

        # Add infrastructure monitoring
        prometheus_config["scrape_configs"].extend(
            [
                {
                    "job_name": "node-exporter",
                    "static_configs": [{"targets": ["localhost:9100"]}],
                },
                {
                    "job_name": "docker",
                    "static_configs": [{"targets": ["localhost:9323"]}],
                },
            ]
        )

        # Create monitoring directory
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)

        # Save Prometheus configuration
        prometheus_file = self.monitoring_dir / "prometheus.yml"
        with open(prometheus_file, "w") as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

        logger.info("✅ Updated Prometheus configuration")
        return True

    def create_grafana_dashboards(self):
        """Create Grafana dashboards for ACGS-1 services"""
        logger.info("Creating Grafana dashboards...")

        # ACGS-1 Overview Dashboard
        overview_dashboard = {
            "dashboard": {
                "id": None,
                "title": "ACGS-1 System Overview",
                "tags": ["acgs", "overview"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Service Health Status",
                        "type": "stat",
                        "targets": [
                            {"expr": f'up{{job=~"acgs-.*"}}', "legendFormat": "{{job}}"}
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "thresholds"},
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "green", "value": 1},
                                    ]
                                },
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    },
                    {
                        "id": 2,
                        "title": "Response Times",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=~"acgs-.*"}[5m]))',
                                "legendFormat": "95th percentile - {{job}}",
                            }
                        ],
                        "yAxes": [{"label": "Seconds", "max": 2.0}],  # 2s target
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    },
                    {
                        "id": 3,
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": 'rate(http_requests_total{job=~"acgs-.*"}[5m])',
                                "legendFormat": "{{job}} - {{method}}",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                    },
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "10s",
            }
        }

        # Constitutional Governance Dashboard
        governance_dashboard = {
            "dashboard": {
                "id": None,
                "title": "Constitutional Governance Metrics",
                "tags": ["acgs", "governance"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Policy Creation Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(acgs_policies_created_total[5m])",
                                "legendFormat": "Policies per second",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    },
                    {
                        "id": 2,
                        "title": "Constitutional Compliance Rate",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "acgs_constitutional_compliance_rate",
                                "legendFormat": "Compliance %",
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "min": 0,
                                "max": 100,
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 90},
                                        {"color": "green", "value": 95},
                                    ]
                                },
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    },
                    {
                        "id": 3,
                        "title": "Governance Action Costs (SOL)",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "acgs_governance_action_cost_sol",
                                "legendFormat": "Cost per action",
                            }
                        ],
                        "yAxes": [{"label": "SOL", "max": 0.01}],  # Target <0.01 SOL
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                    },
                ],
            }
        }

        # Blockchain Dashboard
        blockchain_dashboard = {
            "dashboard": {
                "id": None,
                "title": "Blockchain & Quantumagi Metrics",
                "tags": ["acgs", "blockchain", "solana"],
                "panels": [
                    {
                        "id": 1,
                        "title": "Solana Network Health",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "solana_network_health",
                                "legendFormat": "Network Status",
                            }
                        ],
                        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
                    },
                    {
                        "id": 2,
                        "title": "Program Invocations",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(quantumagi_program_invocations_total[5m])",
                                "legendFormat": "{{program}} invocations/sec",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 18, "x": 6, "y": 0},
                    },
                ],
            }
        }

        # Save dashboards
        dashboards_dir = self.monitoring_dir / "grafana/dashboards"
        dashboards_dir.mkdir(parents=True, exist_ok=True)

        with open(dashboards_dir / "acgs_overview.json", "w") as f:
            json.dump(overview_dashboard, f, indent=2)

        with open(dashboards_dir / "constitutional_governance.json", "w") as f:
            json.dump(governance_dashboard, f, indent=2)

        with open(dashboards_dir / "blockchain_metrics.json", "w") as f:
            json.dump(blockchain_dashboard, f, indent=2)

        logger.info("✅ Created Grafana dashboards")
        return True

    def create_alerting_rules(self):
        """Create alerting rules for ACGS-1 services"""
        logger.info("Creating alerting rules...")

        alerting_rules = {
            "groups": [
                {
                    "name": "acgs_service_health",
                    "rules": [
                        {
                            "alert": "ServiceDown",
                            "expr": 'up{job=~"acgs-.*"} == 0',
                            "for": "1m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "ACGS service {{ $labels.job }} is down",
                                "description": "Service {{ $labels.job }} has been down for more than 1 minute.",
                            },
                        },
                        {
                            "alert": "HighResponseTime",
                            "expr": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=~"acgs-.*"}[5m])) > 2',
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High response time for {{ $labels.job }}",
                                "description": "95th percentile response time is {{ $value }}s, exceeding 2s target.",
                            },
                        },
                    ],
                },
                {
                    "name": "acgs_governance",
                    "rules": [
                        {
                            "alert": "LowConstitutionalCompliance",
                            "expr": "acgs_constitutional_compliance_rate < 95",
                            "for": "2m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "Constitutional compliance below threshold",
                                "description": "Constitutional compliance rate is {{ $value }}%, below 95% threshold.",
                            },
                        },
                        {
                            "alert": "HighGovernanceCosts",
                            "expr": "acgs_governance_action_cost_sol > 0.01",
                            "for": "1m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "Governance action costs too high",
                                "description": "Governance action cost is {{ $value }} SOL, exceeding 0.01 SOL target.",
                            },
                        },
                    ],
                },
                {
                    "name": "acgs_blockchain",
                    "rules": [
                        {
                            "alert": "QuantumagiProgramError",
                            "expr": "rate(quantumagi_program_errors_total[5m]) > 0.1",
                            "for": "2m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "High error rate in Quantumagi programs",
                                "description": "Error rate is {{ $value }} errors/sec in {{ $labels.program }}.",
                            },
                        }
                    ],
                },
            ]
        }

        rules_dir = self.monitoring_dir / "prometheus/rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        with open(rules_dir / "acgs_alerts.yml", "w") as f:
            yaml.dump(alerting_rules, f, default_flow_style=False)

        logger.info("✅ Created alerting rules")
        return True

    def create_health_check_script(self):
        """Create comprehensive health check script"""
        logger.info("Creating health check script...")

        health_check_script = """#!/bin/bash
# ACGS-1 Comprehensive Health Check Script
# Validates all services and blockchain components

set -e

echo "🏥 ACGS-1 System Health Check"
echo "============================="

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Health check results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to check service health
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $service_name (port $port)... "
    
    if curl -s -f "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Function to check response time
check_response_time() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    local max_time=${4:-2}
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $service_name response time... "
    
    response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:$port$endpoint" 2>/dev/null || echo "999")
    
    if (( $(echo "$response_time < $max_time" | bc -l) )); then
        echo -e "${GREEN}✅ ${response_time}s (< ${max_time}s)${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ ${response_time}s (> ${max_time}s)${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Function to check Solana connection
check_solana() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking Solana devnet connection... "
    
    if solana cluster-version --url devnet > /dev/null 2>&1; then
        echo -e "${GREEN}✅ CONNECTED${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ DISCONNECTED${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Function to check Quantumagi programs
check_quantumagi_programs() {
    local programs=(
        "8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4:Quantumagi Core"
        "CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ:Appeals Program"
    )
    
    for program_info in "${programs[@]}"; do
        IFS=':' read -r program_id program_name <<< "$program_info"
        
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        
        echo -n "Checking $program_name... "
        
        if solana account "$program_id" --url devnet > /dev/null 2>&1; then
            echo -e "${GREEN}✅ DEPLOYED${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "${RED}❌ NOT FOUND${NC}"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    done
}

echo "🔍 Checking Core Services..."
echo "----------------------------"

# Check all ACGS-1 services
check_service "Authentication" 8000
check_service "Constitutional AI" 8001
check_service "Governance Synthesis" 8002
check_service "Policy Governance" 8003
check_service "Formal Verification" 8004
check_service "Integrity" 8005
check_service "Evolutionary Computation" 8006

echo ""
echo "⏱️  Checking Response Times..."
echo "------------------------------"

# Check response times (target <2s)
check_response_time "Authentication" 8000 "/health" 2
check_response_time "Constitutional AI" 8001 "/health" 2
check_response_time "Governance Synthesis" 8002 "/health" 2
check_response_time "Policy Governance" 8003 "/health" 2
check_response_time "Formal Verification" 8004 "/health" 2
check_response_time "Integrity" 8005 "/health" 2

echo ""
echo "🔗 Checking Blockchain Components..."
echo "------------------------------------"

# Check Solana connection
check_solana

# Check Quantumagi programs
check_quantumagi_programs

echo ""
echo "📊 Health Check Summary"
echo "======================"
echo "Total Checks: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"

# Calculate success rate
success_rate=$(echo "scale=1; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc)
echo "Success Rate: $success_rate%"

# Determine overall health
if [ "$FAILED_CHECKS" -eq 0 ]; then
    echo -e "\\n${GREEN}🎉 System Status: HEALTHY${NC}"
    exit 0
elif [ "$success_rate" -ge 90 ]; then
    echo -e "\\n${YELLOW}⚠️  System Status: DEGRADED${NC}"
    exit 1
else
    echo -e "\\n${RED}🚨 System Status: CRITICAL${NC}"
    exit 2
fi
"""

        health_check_file = self.project_root / "scripts/comprehensive_health_check.sh"
        health_check_file.parent.mkdir(parents=True, exist_ok=True)

        with open(health_check_file, "w") as f:
            f.write(health_check_script)

        # Make script executable
        health_check_file.chmod(0o755)

        logger.info("✅ Created health check script")
        return True

    def create_docker_monitoring_compose(self):
        """Create Docker Compose for monitoring stack"""
        logger.info("Creating monitoring Docker Compose...")

        monitoring_compose = {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "acgs_prometheus",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./prometheus.yml:/etc/prometheus/prometheus.yml",
                        "./prometheus/rules:/etc/prometheus/rules",
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
                    "networks": ["acgs_monitoring"],
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "acgs_grafana",
                    "ports": ["3000:3000"],
                    "volumes": [
                        "grafana_data:/var/lib/grafana",
                        "./grafana/dashboards:/etc/grafana/provisioning/dashboards",
                        "./grafana/datasources:/etc/grafana/provisioning/datasources",
                    ],
                    "environment": {"GF_SECURITY_ADMIN_PASSWORD": "acgs_admin_2024"},
                    "networks": ["acgs_monitoring"],
                },
                "alertmanager": {
                    "image": "prom/alertmanager:latest",
                    "container_name": "acgs_alertmanager",
                    "ports": ["9093:9093"],
                    "volumes": [
                        "./alertmanager.yml:/etc/alertmanager/alertmanager.yml"
                    ],
                    "networks": ["acgs_monitoring"],
                },
                "node-exporter": {
                    "image": "prom/node-exporter:latest",
                    "container_name": "acgs_node_exporter",
                    "ports": ["9100:9100"],
                    "volumes": [
                        "/proc:/host/proc:ro",
                        "/sys:/host/sys:ro",
                        "/:/rootfs:ro",
                    ],
                    "command": [
                        "--path.procfs=/host/proc",
                        "--path.rootfs=/rootfs",
                        "--path.sysfs=/host/sys",
                        "--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)",
                    ],
                    "networks": ["acgs_monitoring"],
                },
            },
            "networks": {"acgs_monitoring": {"driver": "bridge"}},
            "volumes": {"prometheus_data": {}, "grafana_data": {}},
        }

        compose_file = self.monitoring_dir / "docker-compose.monitoring.yml"
        with open(compose_file, "w") as f:
            yaml.dump(monitoring_compose, f, default_flow_style=False)

        logger.info("✅ Created monitoring Docker Compose")
        return True

    def run_monitoring_updates(self):
        """Execute all monitoring configuration updates"""
        logger.info("Starting monitoring and observability configuration updates...")

        try:
            results = {
                "prometheus_config": self.update_prometheus_config(),
                "grafana_dashboards": self.create_grafana_dashboards(),
                "alerting_rules": self.create_alerting_rules(),
                "health_check_script": self.create_health_check_script(),
                "monitoring_compose": self.create_docker_monitoring_compose(),
            }

            success_count = sum(results.values())
            total_count = len(results)

            if success_count == total_count:
                logger.info(
                    "✅ All monitoring configuration updates completed successfully!"
                )
            else:
                logger.warning(
                    f"⚠️ {success_count}/{total_count} monitoring updates completed"
                )

            return success_count == total_count

        except Exception as e:
            logger.error(f"Monitoring configuration update failed: {e}")
            return False


if __name__ == "__main__":
    updater = MonitoringConfigUpdater()
    success = updater.run_monitoring_updates()
    exit(0 if success else 1)
