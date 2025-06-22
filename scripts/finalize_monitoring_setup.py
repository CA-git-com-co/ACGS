#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Monitoring Setup Script

Finalizes Prometheus metrics collection, configures alerting for deprecation violations,
and establishes SLA monitoring for version-specific performance targets.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveMonitoringSetup:
    """
    Sets up comprehensive monitoring for API versioning system.
    
    Features:
    - Prometheus metrics configuration
    - Grafana dashboard definitions
    - Alerting rules for deprecation violations
    - SLA monitoring for version-specific targets
    - Automated reporting configuration
    """
    
    def __init__(self):
        self.setup_results = []
        
    def setup_comprehensive_monitoring(self) -> Dict[str, Any]:
        """Set up comprehensive monitoring infrastructure."""
        logger.info("📊 Setting up comprehensive monitoring infrastructure...")
        
        start_time = datetime.now(timezone.utc)
        
        # Setup monitoring components
        self._setup_prometheus_metrics()
        self._configure_grafana_dashboards()
        self._setup_alerting_rules()
        self._configure_sla_monitoring()
        self._setup_automated_reporting()
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        # Generate setup report
        report = self._generate_setup_report(start_time, end_time, duration)
        
        logger.info(f"✅ Monitoring setup completed in {duration:.2f}s")
        return report
    
    def _setup_prometheus_metrics(self):
        """Configure Prometheus metrics collection."""
        logger.info("📈 Setting up Prometheus metrics collection...")
        
        try:
            # Define comprehensive metrics configuration
            prometheus_config = {
                "global": {
                    "scrape_interval": "15s",
                    "evaluation_interval": "15s"
                },
                "rule_files": [
                    "rules/api_versioning_rules.yml",
                    "rules/deprecation_rules.yml",
                    "rules/sla_rules.yml"
                ],
                "scrape_configs": [
                    {
                        "job_name": "acgs-api-versioning",
                        "static_configs": [
                            {"targets": ["localhost:8000", "localhost:8001", "localhost:8002"]}
                        ],
                        "metrics_path": "/metrics",
                        "scrape_interval": "10s"
                    },
                    {
                        "job_name": "acgs-version-metrics",
                        "static_configs": [
                            {"targets": ["localhost:9090"]}
                        ],
                        "metrics_path": "/api/v2/metrics/versioning",
                        "scrape_interval": "30s"
                    }
                ],
                "alerting": {
                    "alertmanagers": [
                        {
                            "static_configs": [
                                {"targets": ["localhost:9093"]}
                            ]
                        }
                    ]
                }
            }
            
            # Save Prometheus configuration
            config_path = Path("monitoring/prometheus/prometheus.yml")
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                yaml.dump(prometheus_config, f, default_flow_style=False)
            
            # Define custom metrics
            custom_metrics = {
                "api_version_requests_total": {
                    "type": "counter",
                    "description": "Total number of API requests by version",
                    "labels": ["version", "endpoint", "method", "status_code"]
                },
                "api_version_response_duration_seconds": {
                    "type": "histogram",
                    "description": "Response duration by API version",
                    "labels": ["version", "endpoint", "method"],
                    "buckets": [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
                },
                "api_deprecated_endpoint_usage_total": {
                    "type": "counter",
                    "description": "Usage of deprecated API endpoints",
                    "labels": ["version", "endpoint", "client_id", "sunset_date"]
                },
                "api_version_compatibility_errors_total": {
                    "type": "counter",
                    "description": "Version compatibility transformation errors",
                    "labels": ["source_version", "target_version", "error_type"]
                },
                "api_version_adoption_percentage": {
                    "type": "gauge",
                    "description": "Percentage adoption of each API version",
                    "labels": ["version"]
                }
            }
            
            metrics_path = Path("monitoring/prometheus/custom_metrics.json")
            with open(metrics_path, 'w') as f:
                json.dump(custom_metrics, f, indent=2)
            
            self.setup_results.append({
                "component": "prometheus_metrics",
                "status": "success",
                "details": {
                    "config_file": str(config_path),
                    "metrics_defined": len(custom_metrics),
                    "scrape_jobs": len(prometheus_config["scrape_configs"])
                }
            })
            
        except Exception as e:
            self.setup_results.append({
                "component": "prometheus_metrics",
                "status": "failed",
                "error": str(e)
            })
    
    def _configure_grafana_dashboards(self):
        """Configure Grafana dashboards for API versioning."""
        logger.info("📊 Configuring Grafana dashboards...")
        
        try:
            # API Versioning Overview Dashboard
            overview_dashboard = {
                "dashboard": {
                    "id": None,
                    "title": "ACGS API Versioning Overview",
                    "tags": ["acgs", "api", "versioning"],
                    "timezone": "UTC",
                    "panels": [
                        {
                            "id": 1,
                            "title": "API Version Distribution",
                            "type": "piechart",
                            "targets": [
                                {
                                    "expr": "sum by (version) (rate(api_version_requests_total[5m]))",
                                    "legendFormat": "{{version}}"
                                }
                            ],
                            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                        },
                        {
                            "id": 2,
                            "title": "Response Time by Version",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": "histogram_quantile(0.95, sum(rate(api_version_response_duration_seconds_bucket[5m])) by (version, le))",
                                    "legendFormat": "{{version}} p95"
                                }
                            ],
                            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                        },
                        {
                            "id": 3,
                            "title": "Deprecated Endpoint Usage",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": "sum by (endpoint, version) (rate(api_deprecated_endpoint_usage_total[5m]))",
                                    "legendFormat": "{{version}}/{{endpoint}}"
                                }
                            ],
                            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                        },
                        {
                            "id": 4,
                            "title": "Version Compatibility Errors",
                            "type": "stat",
                            "targets": [
                                {
                                    "expr": "sum(rate(api_version_compatibility_errors_total[5m]))",
                                    "legendFormat": "Errors/sec"
                                }
                            ],
                            "gridPos": {"h": 4, "w": 6, "x": 0, "y": 16}
                        },
                        {
                            "id": 5,
                            "title": "Version Adoption Rate",
                            "type": "gauge",
                            "targets": [
                                {
                                    "expr": "api_version_adoption_percentage{version=\"v2.0.0\"}",
                                    "legendFormat": "v2.0.0 Adoption"
                                }
                            ],
                            "gridPos": {"h": 4, "w": 6, "x": 6, "y": 16}
                        }
                    ],
                    "time": {"from": "now-1h", "to": "now"},
                    "refresh": "30s"
                }
            }
            
            # Save dashboard configuration
            dashboard_path = Path("monitoring/grafana/dashboards/api_versioning_overview.json")
            dashboard_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(dashboard_path, 'w') as f:
                json.dump(overview_dashboard, f, indent=2)
            
            # SLA Monitoring Dashboard
            sla_dashboard = {
                "dashboard": {
                    "id": None,
                    "title": "ACGS API Versioning SLA Monitoring",
                    "tags": ["acgs", "sla", "versioning"],
                    "panels": [
                        {
                            "id": 1,
                            "title": "SLA Compliance by Version",
                            "type": "stat",
                            "targets": [
                                {
                                    "expr": "(sum(rate(api_version_requests_total{status_code!~\"5..\"}[5m])) by (version) / sum(rate(api_version_requests_total[5m])) by (version)) * 100",
                                    "legendFormat": "{{version}} Availability %"
                                }
                            ]
                        },
                        {
                            "id": 2,
                            "title": "Response Time SLA Compliance",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": "histogram_quantile(0.95, sum(rate(api_version_response_duration_seconds_bucket[5m])) by (version, le)) < 0.1",
                                    "legendFormat": "{{version}} < 100ms SLA"
                                }
                            ]
                        }
                    ]
                }
            }
            
            sla_dashboard_path = Path("monitoring/grafana/dashboards/sla_monitoring.json")
            with open(sla_dashboard_path, 'w') as f:
                json.dump(sla_dashboard, f, indent=2)
            
            self.setup_results.append({
                "component": "grafana_dashboards",
                "status": "success",
                "details": {
                    "dashboards_created": 2,
                    "overview_dashboard": str(dashboard_path),
                    "sla_dashboard": str(sla_dashboard_path)
                }
            })
            
        except Exception as e:
            self.setup_results.append({
                "component": "grafana_dashboards",
                "status": "failed",
                "error": str(e)
            })
    
    def _setup_alerting_rules(self):
        """Set up alerting rules for deprecation violations and SLA breaches."""
        logger.info("🚨 Setting up alerting rules...")
        
        try:
            # Deprecation alerting rules
            deprecation_rules = {
                "groups": [
                    {
                        "name": "api_deprecation_alerts",
                        "rules": [
                            {
                                "alert": "DeprecatedEndpointHighUsage",
                                "expr": "sum by (endpoint, version) (rate(api_deprecated_endpoint_usage_total[5m])) > 10",
                                "for": "5m",
                                "labels": {
                                    "severity": "warning",
                                    "team": "api"
                                },
                                "annotations": {
                                    "summary": "High usage of deprecated endpoint {{$labels.endpoint}} in version {{$labels.version}}",
                                    "description": "Deprecated endpoint {{$labels.endpoint}} in version {{$labels.version}} is receiving {{$value}} requests/second"
                                }
                            },
                            {
                                "alert": "SunsetDateApproaching",
                                "expr": "time() > on() (api_deprecated_endpoint_sunset_timestamp - 86400 * 30)",
                                "for": "1h",
                                "labels": {
                                    "severity": "critical",
                                    "team": "api"
                                },
                                "annotations": {
                                    "summary": "API endpoint sunset date approaching in 30 days",
                                    "description": "Deprecated endpoint will be sunset in less than 30 days"
                                }
                            }
                        ]
                    },
                    {
                        "name": "api_sla_alerts",
                        "rules": [
                            {
                                "alert": "APIResponseTimeSLABreach",
                                "expr": "histogram_quantile(0.95, sum(rate(api_version_response_duration_seconds_bucket[5m])) by (version, le)) > 0.1",
                                "for": "2m",
                                "labels": {
                                    "severity": "warning",
                                    "team": "api"
                                },
                                "annotations": {
                                    "summary": "API response time SLA breach for version {{$labels.version}}",
                                    "description": "95th percentile response time for version {{$labels.version}} is {{$value}}s, exceeding 100ms SLA"
                                }
                            },
                            {
                                "alert": "APIErrorRateHigh",
                                "expr": "sum by (version) (rate(api_version_requests_total{status_code=~\"5..\"}[5m])) / sum by (version) (rate(api_version_requests_total[5m])) > 0.01",
                                "for": "1m",
                                "labels": {
                                    "severity": "critical",
                                    "team": "api"
                                },
                                "annotations": {
                                    "summary": "High error rate for API version {{$labels.version}}",
                                    "description": "Error rate for version {{$labels.version}} is {{$value | humanizePercentage}}"
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Save alerting rules
            rules_path = Path("monitoring/prometheus/rules/api_versioning_rules.yml")
            rules_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(rules_path, 'w') as f:
                yaml.dump(deprecation_rules, f, default_flow_style=False)
            
            # Alertmanager configuration
            alertmanager_config = {
                "global": {
                    "smtp_smarthost": "localhost:587",
                    "smtp_from": "alerts@acgs.gov"
                },
                "route": {
                    "group_by": ["alertname"],
                    "group_wait": "10s",
                    "group_interval": "10s",
                    "repeat_interval": "1h",
                    "receiver": "web.hook"
                },
                "receivers": [
                    {
                        "name": "web.hook",
                        "webhook_configs": [
                            {
                                "url": "http://localhost:5001/webhook",
                                "send_resolved": True
                            }
                        ],
                        "email_configs": [
                            {
                                "to": "api-team@acgs.gov",
                                "subject": "ACGS API Alert: {{ .GroupLabels.alertname }}",
                                "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                            }
                        ]
                    }
                ]
            }
            
            alertmanager_path = Path("monitoring/alertmanager/alertmanager.yml")
            alertmanager_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(alertmanager_path, 'w') as f:
                yaml.dump(alertmanager_config, f, default_flow_style=False)
            
            self.setup_results.append({
                "component": "alerting_rules",
                "status": "success",
                "details": {
                    "rules_file": str(rules_path),
                    "alertmanager_config": str(alertmanager_path),
                    "alert_rules_count": sum(len(group["rules"]) for group in deprecation_rules["groups"])
                }
            })
            
        except Exception as e:
            self.setup_results.append({
                "component": "alerting_rules",
                "status": "failed",
                "error": str(e)
            })
    
    def _configure_sla_monitoring(self):
        """Configure SLA monitoring for version-specific performance targets."""
        logger.info("🎯 Configuring SLA monitoring...")
        
        try:
            # Define SLA targets
            sla_targets = {
                "availability": {
                    "target": 99.9,
                    "measurement_window": "30d",
                    "error_budget": 0.1
                },
                "response_time": {
                    "p95_target_ms": 100,
                    "p99_target_ms": 250,
                    "measurement_window": "5m"
                },
                "version_compatibility": {
                    "transformation_success_rate": 99.95,
                    "measurement_window": "1h"
                },
                "deprecation_compliance": {
                    "advance_notice_days": 30,
                    "sunset_enforcement": True,
                    "migration_support_period_days": 180
                }
            }
            
            # Save SLA configuration
            sla_path = Path("monitoring/sla/sla_targets.json")
            sla_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(sla_path, 'w') as f:
                json.dump(sla_targets, f, indent=2)
            
            self.setup_results.append({
                "component": "sla_monitoring",
                "status": "success",
                "details": {
                    "sla_config": str(sla_path),
                    "availability_target": sla_targets["availability"]["target"],
                    "response_time_target": sla_targets["response_time"]["p95_target_ms"]
                }
            })
            
        except Exception as e:
            self.setup_results.append({
                "component": "sla_monitoring",
                "status": "failed",
                "error": str(e)
            })
    
    def _setup_automated_reporting(self):
        """Set up automated reporting for version metrics."""
        logger.info("📋 Setting up automated reporting...")
        
        try:
            # Define reporting configuration
            reporting_config = {
                "reports": [
                    {
                        "name": "weekly_version_adoption",
                        "schedule": "0 9 * * 1",  # Every Monday at 9 AM
                        "recipients": ["api-team@acgs.gov", "product-team@acgs.gov"],
                        "metrics": [
                            "version_adoption_percentage",
                            "deprecated_endpoint_usage",
                            "migration_progress"
                        ]
                    },
                    {
                        "name": "monthly_sla_report",
                        "schedule": "0 9 1 * *",  # First day of month at 9 AM
                        "recipients": ["leadership@acgs.gov", "api-team@acgs.gov"],
                        "metrics": [
                            "availability_sla_compliance",
                            "response_time_sla_compliance",
                            "error_budget_consumption"
                        ]
                    }
                ],
                "notification_channels": {
                    "email": {
                        "smtp_server": "localhost:587",
                        "from_address": "reports@acgs.gov"
                    },
                    "slack": {
                        "webhook_url": "https://hooks.slack.com/services/...",
                        "channel": "#api-monitoring"
                    }
                }
            }
            
            # Save reporting configuration
            reporting_path = Path("monitoring/reporting/config.json")
            reporting_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(reporting_path, 'w') as f:
                json.dump(reporting_config, f, indent=2)
            
            self.setup_results.append({
                "component": "automated_reporting",
                "status": "success",
                "details": {
                    "config_file": str(reporting_path),
                    "reports_configured": len(reporting_config["reports"]),
                    "notification_channels": len(reporting_config["notification_channels"])
                }
            })
            
        except Exception as e:
            self.setup_results.append({
                "component": "automated_reporting",
                "status": "failed",
                "error": str(e)
            })
    
    def _generate_setup_report(self, start_time: datetime, end_time: datetime, duration: float) -> Dict[str, Any]:
        """Generate comprehensive setup report."""
        successful_components = len([r for r in self.setup_results if r["status"] == "success"])
        total_components = len(self.setup_results)
        
        return {
            "setup_summary": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": round(duration, 2),
                "total_components": total_components,
                "successful_components": successful_components,
                "failed_components": total_components - successful_components,
                "success_rate": round((successful_components / total_components) * 100, 1) if total_components > 0 else 0
            },
            "component_results": self.setup_results,
            "success_criteria": {
                "prometheus_configured": any(r["component"] == "prometheus_metrics" and r["status"] == "success" for r in self.setup_results),
                "grafana_dashboards_created": any(r["component"] == "grafana_dashboards" and r["status"] == "success" for r in self.setup_results),
                "alerting_rules_configured": any(r["component"] == "alerting_rules" and r["status"] == "success" for r in self.setup_results),
                "sla_monitoring_enabled": any(r["component"] == "sla_monitoring" and r["status"] == "success" for r in self.setup_results),
                "automated_reporting_setup": any(r["component"] == "automated_reporting" and r["status"] == "success" for r in self.setup_results),
                "all_components_successful": successful_components == total_components
            }
        }

def main():
    """Main function to set up comprehensive monitoring."""
    monitoring_setup = ComprehensiveMonitoringSetup()
    
    # Set up monitoring infrastructure
    report = monitoring_setup.setup_comprehensive_monitoring()
    
    # Save report
    output_path = Path("docs/implementation/reports/monitoring_setup_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("ACGS-1 COMPREHENSIVE MONITORING SETUP SUMMARY")
    print("="*80)
    
    summary = report["setup_summary"]
    print(f"⏱️  Duration: {summary['duration_seconds']}s")
    print(f"📊 Components: {summary['successful_components']}/{summary['total_components']} successful")
    print(f"📈 Success Rate: {summary['success_rate']}%")
    
    print(f"\n🎯 SUCCESS CRITERIA:")
    criteria = report["success_criteria"]
    for criterion, passed in criteria.items():
        status = "PASS" if passed else "FAIL"
        print(f"   {criterion}: {status}")
    
    if summary["failed_components"] > 0:
        print(f"\n❌ FAILED COMPONENTS:")
        for result in report["component_results"]:
            if result["status"] == "failed":
                print(f"   - {result['component']}: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*80)
    print(f"📄 Full report saved to: {output_path}")
    
    # Return exit code based on success criteria
    return 0 if criteria['all_components_successful'] else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
