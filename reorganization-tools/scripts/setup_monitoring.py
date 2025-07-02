#!/usr/bin/env python3
"""
Setup Repository-Specific Monitoring for ACGS

This script creates monitoring configurations for each ACGS repository.
"""

import json
import yaml
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonitoringSetup:
    def __init__(self, workspace_path: Path):
        self.workspace_path = Path(workspace_path)
        self.repositories = self._load_workspace_config()
    
    def _load_workspace_config(self) -> dict:
        """Load workspace configuration"""
        config_file = self.workspace_path / "acgs-workspace.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config["repositories"]
    
    def create_prometheus_config(self, repo_path: Path, repo_name: str, port: int) -> str:
        """Create Prometheus monitoring configuration"""
        return f"""# Prometheus configuration for {repo_name}

global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/{repo_name}_rules.yml"

scrape_configs:
  - job_name: '{repo_name}'
    static_configs:
      - targets: ['localhost:{port}']
    metrics_path: '/metrics'
    scrape_interval: 5s
    scrape_timeout: 3s
    
  - job_name: '{repo_name}-health'
    static_configs:
      - targets: ['localhost:{port}']
    metrics_path: '/health'
    scrape_interval: 10s
    
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

# Repository-specific service discovery
  - job_name: '{repo_name}-discovery'
    consul_sd_configs:
      - server: 'consul:8500'
        services: ['{repo_name}']
"""
    
    def create_grafana_dashboard(self, repo_name: str, port: int) -> dict:
        """Create Grafana dashboard configuration"""
        return {
            "dashboard": {
                "id": None,
                "title": f"ACGS {repo_name.title()} Dashboard",
                "tags": ["acgs", repo_name],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Request Rate",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": f"rate(http_requests_total{{service=\"{repo_name}\"}}[5m])",
                                "legendFormat": "{{method}} {{endpoint}}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": f"histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service=\"{repo_name}\"}}[5m]))",
                                "legendFormat": "95th percentile"
                            },
                            {
                                "expr": f"histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{{service=\"{repo_name}\"}}[5m]))",
                                "legendFormat": "50th percentile"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Error Rate",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": f"rate(http_requests_total{{service=\"{repo_name}\",status=~\"5..\"|status=~\"4..\"}}[5m])",
                                "legendFormat": "Error Rate"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Service Health",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": f"up{{service=\"{repo_name}\"}}",
                                "legendFormat": "Service Status"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    },
                    {
                        "id": 5,
                        "title": "Memory Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": f"process_resident_memory_bytes{{service=\"{repo_name}\"}}",
                                "legendFormat": "RSS Memory"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
                    },
                    {
                        "id": 6,
                        "title": "CPU Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": f"rate(process_cpu_seconds_total{{service=\"{repo_name}\"}}[5m])",
                                "legendFormat": "CPU Usage"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "5s"
            }
        }
    
    def create_alerting_rules(self, repo_name: str) -> dict:
        """Create Prometheus alerting rules"""
        return {
            "groups": [
                {
                    "name": f"{repo_name}_alerts",
                    "rules": [
                        {
                            "alert": f"{repo_name.title()}ServiceDown",
                            "expr": f"up{{service=\"{repo_name}\"}} == 0",
                            "for": "30s",
                            "labels": {
                                "severity": "critical",
                                "service": repo_name
                            },
                            "annotations": {
                                "summary": f"{repo_name.title()} service is down",
                                "description": f"The {repo_name} service has been down for more than 30 seconds."
                            }
                        },
                        {
                            "alert": f"{repo_name.title()}HighErrorRate",
                            "expr": f"rate(http_requests_total{{service=\"{repo_name}\",status=~\"5..\"}}[5m]) > 0.1",
                            "for": "2m",
                            "labels": {
                                "severity": "warning",
                                "service": repo_name
                            },
                            "annotations": {
                                "summary": f"High error rate in {repo_name}",
                                "description": f"Error rate is above 10% for {repo_name} service."
                            }
                        },
                        {
                            "alert": f"{repo_name.title()}HighResponseTime",
                            "expr": f"histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service=\"{repo_name}\"}}[5m])) > 0.5",
                            "for": "5m",
                            "labels": {
                                "severity": "warning",
                                "service": repo_name
                            },
                            "annotations": {
                                "summary": f"High response time in {repo_name}",
                                "description": f"95th percentile response time is above 500ms for {repo_name}."
                            }
                        },
                        {
                            "alert": f"{repo_name.title()}HighMemoryUsage",
                            "expr": f"process_resident_memory_bytes{{service=\"{repo_name}\"}} > 1073741824",
                            "for": "5m",
                            "labels": {
                                "severity": "warning",
                                "service": repo_name
                            },
                            "annotations": {
                                "summary": f"High memory usage in {repo_name}",
                                "description": f"Memory usage is above 1GB for {repo_name} service."
                            }
                        }
                    ]
                }
            ]
        }
    
    def create_docker_compose_monitoring(self, repo_name: str, port: int) -> dict:
        """Create Docker Compose configuration for monitoring stack"""
        return {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": f"{repo_name}-prometheus",
                    "ports": ["9090:9090"],
                    "volumes": [
                        f"./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml",
                        f"./monitoring/rules:/etc/prometheus/rules"
                    ],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--storage.tsdb.retention.time=200h",
                        "--web.enable-lifecycle"
                    ]
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": f"{repo_name}-grafana",
                    "ports": ["3000:3000"],
                    "environment": [
                        "GF_SECURITY_ADMIN_PASSWORD=admin"
                    ],
                    "volumes": [
                        f"./monitoring/grafana/dashboards:/var/lib/grafana/dashboards",
                        f"./monitoring/grafana/provisioning:/etc/grafana/provisioning"
                    ]
                },
                "alertmanager": {
                    "image": "prom/alertmanager:latest",
                    "container_name": f"{repo_name}-alertmanager",
                    "ports": ["9093:9093"],
                    "volumes": [
                        f"./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml"
                    ]
                }
            }
        }
    
    def create_alertmanager_config(self, repo_name: str) -> dict:
        """Create Alertmanager configuration"""
        return {
            "global": {
                "smtp_smarthost": "localhost:587",
                "smtp_from": f"alerts@acgs.ai"
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
                    "slack_configs": [
                        {
                            "api_url": "YOUR_SLACK_WEBHOOK_URL",
                            "channel": f"#acgs-{repo_name}-alerts",
                            "title": f"ACGS {repo_name.title()} Alert",
                            "text": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                        }
                    ],
                    "email_configs": [
                        {
                            "to": "team@acgs.ai",
                            "subject": f"ACGS {repo_name.title()} Alert",
                            "body": "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
                        }
                    ]
                }
            ]
        }
    
    def create_health_check_endpoint(self, repo_name: str) -> str:
        """Create health check endpoint code"""
        return f'''"""
Health check endpoint for {repo_name}
"""
from fastapi import FastAPI, Response
from datetime import datetime
import psutil
import asyncio

app = FastAPI()

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {{
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "{repo_name}",
        "version": "1.0.0"
    }}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {{
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "{repo_name}",
        "version": "1.0.0",
        "metrics": {{
            "cpu_percent": cpu_usage,
            "memory_percent": memory.percent,
            "memory_available": memory.available,
            "disk_percent": (disk.used / disk.total) * 100,
            "disk_free": disk.free
        }}
    }}

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    metrics = f"""# HELP {repo_name}_cpu_percent CPU usage percentage
# TYPE {repo_name}_cpu_percent gauge
{repo_name}_cpu_percent{{service="{repo_name}"}} {{cpu_usage}}

# HELP {repo_name}_memory_percent Memory usage percentage  
# TYPE {repo_name}_memory_percent gauge
{repo_name}_memory_percent{{service="{repo_name}"}} {{memory.percent}}

# HELP {repo_name}_memory_available Available memory in bytes
# TYPE {repo_name}_memory_available gauge
{repo_name}_memory_available{{service="{repo_name}"}} {{memory.available}}
"""
    
    return Response(content=metrics, media_type="text/plain")
'''
    
    def setup_repository_monitoring(self, repo_name: str) -> bool:
        """Setup monitoring for a specific repository"""
        try:
            repo_path = self.workspace_path / repo_name
            if not repo_path.exists():
                logger.error(f"Repository path does not exist: {repo_path}")
                return False
            
            # Create monitoring directory
            monitoring_dir = repo_path / "monitoring"
            monitoring_dir.mkdir(exist_ok=True)
            
            # Assign ports based on repository
            port_mapping = {
                "acgs-core": 8001,
                "acgs-platform": 8002,
                "acgs-blockchain": 8003,
                "acgs-models": 8004,
                "acgs-applications": 8005,
                "acgs-infrastructure": 8006,
                "acgs-tools": 8007
            }
            port = port_mapping.get(repo_name, 8000)
            
            # Create Prometheus configuration
            prometheus_config = self.create_prometheus_config(repo_path, repo_name, port)
            with open(monitoring_dir / "prometheus.yml", 'w') as f:
                f.write(prometheus_config)
            
            # Create Grafana dashboard
            grafana_dir = monitoring_dir / "grafana" / "dashboards"
            grafana_dir.mkdir(parents=True, exist_ok=True)
            
            dashboard = self.create_grafana_dashboard(repo_name, port)
            with open(grafana_dir / f"{repo_name}_dashboard.json", 'w') as f:
                json.dump(dashboard, f, indent=2)
            
            # Create alerting rules
            rules_dir = monitoring_dir / "rules"
            rules_dir.mkdir(exist_ok=True)
            
            rules = self.create_alerting_rules(repo_name)
            with open(rules_dir / f"{repo_name}_rules.yml", 'w') as f:
                yaml.dump(rules, f, default_flow_style=False)
            
            # Create Docker Compose for monitoring
            docker_compose = self.create_docker_compose_monitoring(repo_name, port)
            with open(monitoring_dir / "docker-compose.monitoring.yml", 'w') as f:
                yaml.dump(docker_compose, f, default_flow_style=False)
            
            # Create Alertmanager configuration
            alertmanager_config = self.create_alertmanager_config(repo_name)
            with open(monitoring_dir / "alertmanager.yml", 'w') as f:
                yaml.dump(alertmanager_config, f, default_flow_style=False)
            
            # Create health check endpoint
            health_check_code = self.create_health_check_endpoint(repo_name)
            with open(repo_path / "health_check.py", 'w') as f:
                f.write(health_check_code)
            
            logger.info(f"✅ Monitoring setup complete for {repo_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup monitoring for {repo_name}: {e}")
            return False
    
    def create_monitoring_overview(self) -> str:
        """Create monitoring overview documentation"""
        return """# ACGS Monitoring Overview

## Monitoring Stack

Each ACGS repository includes a comprehensive monitoring setup:

### Components
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards  
- **Alertmanager**: Alert routing and notification
- **Health Checks**: Service health monitoring

### Repository-Specific Monitoring

| Repository | Port | Prometheus | Grafana | Alerts |
|------------|------|------------|---------|--------|
| acgs-core | 8001 | ✅ | ✅ | ✅ |
| acgs-platform | 8002 | ✅ | ✅ | ✅ |
| acgs-blockchain | 8003 | ✅ | ✅ | ✅ |
| acgs-models | 8004 | ✅ | ✅ | ✅ |
| acgs-applications | 8005 | ✅ | ✅ | ✅ |
| acgs-infrastructure | 8006 | ✅ | ✅ | ✅ |
| acgs-tools | 8007 | ✅ | ✅ | ✅ |

## Getting Started

### Start Monitoring Stack
```bash
cd [repository]/monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### Access Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### Health Check Endpoints
```bash
# Basic health check
curl http://localhost:800[X]/health

# Detailed health check
curl http://localhost:800[X]/health/detailed

# Prometheus metrics
curl http://localhost:800[X]/metrics
```

## Key Metrics

### Service Health
- Service uptime and availability
- Response time percentiles (50th, 95th, 99th)
- Error rates and HTTP status codes
- Request throughput

### System Resources
- CPU usage percentage
- Memory consumption
- Disk usage
- Network I/O

### Application Metrics
- Database connection pool status
- Cache hit rates
- Queue lengths
- Custom business metrics

## Alerting

### Alert Levels
- **Critical**: Service down, data loss risk
- **Warning**: Performance degradation, high resource usage
- **Info**: Deployment notifications, capacity planning

### Notification Channels
- Slack: #acgs-[repository]-alerts
- Email: team@acgs.ai
- PagerDuty: For critical alerts

### Common Alerts
- Service downtime (>30s)
- High error rate (>10%)
- High response time (>500ms 95th percentile)
- High memory usage (>1GB)
- High CPU usage (>80%)

## Dashboard Features

### Overview Dashboard
- Service status grid
- Key performance indicators
- Error rate trends
- Resource utilization

### Detailed Dashboards
- Request rate and patterns
- Response time distributions
- Error analysis
- Resource consumption trends
- Database performance
- Cache effectiveness

## Configuration

### Custom Metrics
Add custom metrics to your application:

```python
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('app_active_users', 'Active users')
```

### Custom Alerts
Add repository-specific alerts in `monitoring/rules/[repo]_rules.yml`:

```yaml
- alert: CustomBusinessMetric
  expr: business_metric > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: Custom business metric exceeded threshold
```

## Troubleshooting

### Common Issues

#### Metrics Not Appearing
1. Check service health: `curl http://localhost:800X/health`
2. Verify Prometheus targets: http://localhost:9090/targets
3. Check application logs for errors

#### Alerts Not Firing
1. Verify alert rules syntax in Prometheus UI
2. Check Alertmanager configuration
3. Test notification channels

#### Dashboard Issues
1. Check Prometheus data source in Grafana
2. Verify metric names and labels
3. Check time range settings

### Performance Optimization

#### High Cardinality Metrics
- Limit label values to prevent metric explosion
- Use histogram buckets appropriately
- Consider sampling for high-volume metrics

#### Storage Management
- Configure retention policies
- Monitor disk usage
- Consider remote storage for long-term data

## Best Practices

### Metrics Design
- Use consistent naming conventions
- Include meaningful labels
- Avoid high-cardinality labels
- Document custom metrics

### Alert Design
- Set appropriate thresholds
- Use multiple severity levels
- Include actionable information
- Test alert conditions

### Dashboard Design
- Focus on business value
- Use appropriate visualizations
- Include context and documentation
- Regular review and updates

## Integration

### CI/CD Integration
Monitoring configurations are automatically deployed with each repository through the CI/CD pipeline.

### Log Aggregation
Integrate with ELK stack or similar for comprehensive observability.

### Distributed Tracing
Use Jaeger or Zipkin for request tracing across services.

## Support

- **Documentation**: See repository-specific monitoring docs
- **Issues**: Create issues in respective repositories
- **Emergency**: Page on-call team through PagerDuty
"""
    
    def setup_all_monitoring(self) -> dict:
        """Setup monitoring for all repositories"""
        results = {}
        
        for repo_name in self.repositories.keys():
            logger.info(f"\n=== Setting up monitoring for {repo_name} ===")
            
            if self.setup_repository_monitoring(repo_name):
                results[repo_name] = "success"
            else:
                results[repo_name] = "failed"
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup monitoring for ACGS repositories")
    parser.add_argument("workspace_path", help="Path to ACGS workspace")
    parser.add_argument("--repo", help="Setup monitoring for specific repository only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    setup = MonitoringSetup(args.workspace_path)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - Would create monitoring for:")
        repos = [args.repo] if args.repo else setup.repositories.keys()
        for repo_name in repos:
            logger.info(f"  {repo_name}: Prometheus + Grafana + Alertmanager")
        return
    
    # Execute setup
    if args.repo:
        result = setup.setup_repository_monitoring(args.repo)
        logger.info(f"Monitoring setup for {args.repo}: {'SUCCESS' if result else 'FAILED'}")
    else:
        results = setup.setup_all_monitoring()
        
        # Create monitoring overview
        overview = setup.create_monitoring_overview()
        overview_file = Path(args.workspace_path) / "MONITORING_OVERVIEW.md"
        with open(overview_file, 'w') as f:
            f.write(overview)
        
        # Summary
        successful = [repo for repo, status in results.items() if status == "success"]
        failed = [repo for repo, status in results.items() if status == "failed"]
        
        logger.info(f"\nMonitoring setup complete!")
        logger.info(f"Successful: {len(successful)}/{len(results)}")
        if failed:
            logger.warning(f"Failed: {', '.join(failed)}")
        logger.info(f"Overview saved to: {overview_file}")

if __name__ == "__main__":
    main()