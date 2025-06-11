# ACGS-1 Monitoring Infrastructure Training Guide

## Overview

This comprehensive training guide provides administrators, operators, and developers with the knowledge and skills needed to effectively manage the ACGS-1 monitoring infrastructure in production environments.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Navigation](#dashboard-navigation)
3. [Alert Management](#alert-management)
4. [Performance Monitoring](#performance-monitoring)
5. [Troubleshooting Procedures](#troubleshooting)
6. [Maintenance Tasks](#maintenance)
7. [Best Practices](#best-practices)
8. [Advanced Topics](#advanced-topics)

## Getting Started {#getting-started}

### Accessing the Monitoring Infrastructure

**Grafana Dashboard Access**:
- URL: `http://localhost:3000`
- Default Username: `acgs_admin`
- Password: Located in `/etc/acgs/admin-credentials.txt`

**Prometheus Metrics Access**:
- URL: `http://localhost:9090`
- Username: `acgs_monitor`
- Password: Located in `/etc/acgs/admin-credentials.txt`

**Alertmanager Access**:
- URL: `http://localhost:9093`
- No authentication required (internal access only)

### Initial Setup Verification

```bash
# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# Verify health endpoints
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana
curl http://localhost:9093/-/healthy  # Alertmanager

# Check metrics collection
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result | length'
```

## Dashboard Navigation {#dashboard-navigation}

### Main Dashboards Overview

**1. ACGS Services Overview Dashboard**
- **Purpose**: High-level view of all 7 ACGS services
- **Key Metrics**: Service uptime, response times, error rates
- **Use Cases**: Daily health checks, incident overview

**2. Constitutional Governance Workflows Dashboard**
- **Purpose**: Monitor governance-specific operations
- **Key Metrics**: Policy creation rates, compliance scores, governance costs
- **Use Cases**: Governance performance analysis, compliance monitoring

**3. Infrastructure Monitoring Dashboard**
- **Purpose**: System-level monitoring (HAProxy, Redis, PostgreSQL)
- **Key Metrics**: Load balancer performance, cache hit rates, database connections
- **Use Cases**: Infrastructure health, capacity planning

**4. Performance Metrics Dashboard**
- **Purpose**: Detailed performance analysis
- **Key Metrics**: Response time distributions, throughput, resource utilization
- **Use Cases**: Performance optimization, SLA monitoring

**5. Security Dashboard**
- **Purpose**: Security event monitoring and threat detection
- **Key Metrics**: Authentication failures, suspicious activities, security alerts
- **Use Cases**: Security incident response, threat analysis

### Dashboard Navigation Tips

**Time Range Selection**:
- Use appropriate time ranges for analysis
- Default: Last 1 hour for real-time monitoring
- Extended ranges: Last 24 hours for trend analysis

**Panel Interactions**:
- Click on legend items to toggle series visibility
- Drag to zoom into specific time periods
- Right-click for context menu options

**Variable Usage**:
- Use dashboard variables to filter by service, environment, or instance
- Variables are located at the top of each dashboard

### Creating Custom Dashboards

```json
{
  "dashboard": {
    "title": "Custom ACGS Dashboard",
    "panels": [
      {
        "title": "Service Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=~\"acgs-.*\"}[5m]))",
            "legendFormat": "95th percentile - {{job}}"
          }
        ]
      }
    ]
  }
}
```

## Alert Management {#alert-management}

### Understanding Alert Severity Levels

**Critical Alerts** (Response: <5 minutes):
- Service down
- Constitutional compliance failures
- Security breaches
- System resource exhaustion

**High Priority Alerts** (Response: <15 minutes):
- High error rates
- Performance degradation
- Load balancer issues
- Database connection problems

**Warning Alerts** (Response: <1 hour):
- Resource usage warnings
- Minor performance issues
- Configuration drift
- Capacity planning alerts

### Alert Response Procedures

**Step 1: Alert Acknowledgment**
```bash
# Acknowledge alert in Alertmanager
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{"status": "acknowledged", "alertname": "ALERT_NAME"}'
```

**Step 2: Initial Assessment**
```bash
# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# Review recent logs
docker logs acgs_prometheus --tail 50
docker logs acgs_grafana --tail 50
```

**Step 3: Impact Analysis**
```bash
# Check affected services
curl -s "http://localhost:9090/api/v1/query?query=up{job=~'acgs-.*'}" | jq '.data.result'

# Analyze error rates
curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{status=~'5..'}[5m])" | jq
```

### Silencing Alerts

**Temporary Silence (Maintenance)**:
```bash
curl -X POST http://localhost:9093/api/v1/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "alertname", "value": "ServiceDown", "isRegex": false}],
    "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "endsAt": "'$(date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "createdBy": "operator",
    "comment": "Planned maintenance"
  }'
```

## Performance Monitoring {#performance-monitoring}

### Key Performance Indicators (KPIs)

**Response Time Metrics**:
- Average response time: <200ms
- 95th percentile: <500ms
- 99th percentile: <1000ms

**Availability Metrics**:
- Service uptime: >99.5%
- System availability: >99.9%
- Error rate: <1%

**Resource Utilization**:
- CPU usage: <80%
- Memory usage: <85%
- Disk usage: <90%

### Performance Analysis Queries

**Service Response Times**:
```promql
# Average response time by service
rate(http_request_duration_seconds_sum{job=~"acgs-.*"}[5m]) / 
rate(http_request_duration_seconds_count{job=~"acgs-.*"}[5m])

# 95th percentile response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=~"acgs-.*"}[5m]))
```

**Error Rate Analysis**:
```promql
# Error rate by service
rate(http_requests_total{status=~"5.."}[5m]) / 
rate(http_requests_total[5m])

# Total error count
sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
```

**Resource Utilization**:
```promql
# CPU usage
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
100 - ((node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes)
```

### Constitutional Governance Metrics

**Compliance Monitoring**:
```promql
# Constitutional compliance score
acgs_constitutional_compliance_score

# Policy synthesis success rate
rate(acgs_policy_synthesis_success_total[5m]) / 
rate(acgs_policy_synthesis_total[5m])

# Governance action costs
acgs_governance_action_cost_sol
```

## Troubleshooting Procedures {#troubleshooting}

### Common Issues and Solutions

**Issue: High Memory Usage**
```bash
# Check memory usage by container
docker stats --no-stream

# Check Prometheus memory usage
curl -s "http://localhost:9090/api/v1/status/tsdb" | jq '.data.headStats'

# Solution: Optimize retention settings
# Edit prometheus.yml: --storage.tsdb.retention.time=15d
```

**Issue: Slow Dashboard Loading**
```bash
# Check Grafana performance
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:3000/api/health

# Solution: Optimize dashboard queries
# - Use appropriate time ranges
# - Limit data points in visualizations
# - Use efficient PromQL queries
```

**Issue: Alert Storm**
```bash
# Check current alerts
curl -s "http://localhost:9093/api/v1/alerts" | jq '.data | length'

# Solution: Implement alert inhibition
# Edit alertmanager.yml with inhibit_rules
```

### Diagnostic Commands

**Service Health Check**:
```bash
# Comprehensive health check
./infrastructure/monitoring/health-check.sh

# Individual service checks
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health
curl http://localhost:9093/-/healthy
```

**Log Analysis**:
```bash
# View service logs
docker logs acgs_prometheus --tail 100
docker logs acgs_grafana --tail 100
docker logs acgs_alertmanager --tail 100

# Search for errors
docker logs acgs_prometheus 2>&1 | grep -i error
```

## Maintenance Tasks {#maintenance}

### Daily Maintenance

```bash
# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# Verify metrics collection
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result | length'

# Check disk usage
df -h /var/lib/docker/volumes/prometheus_data
df -h /var/lib/docker/volumes/grafana_data
```

### Weekly Maintenance

```bash
# Review alert configurations
./scripts/review-alert-configs.sh

# Analyze performance trends
./scripts/analyze-performance-trends.sh --period week

# Update dashboard configurations
./scripts/update-dashboards.sh

# Validate backup integrity
./scripts/validate-backup-integrity.sh
```

### Monthly Maintenance

```bash
# Update monitoring software
./scripts/update-monitoring-software.sh

# Review and optimize alert rules
./scripts/optimize-alert-rules.sh

# Capacity planning analysis
./scripts/capacity-planning.sh

# Security audit
./scripts/security-audit.sh
```

## Best Practices {#best-practices}

### Dashboard Design

1. **Use Consistent Time Ranges**: Align all panels to the same time range
2. **Logical Grouping**: Group related metrics in the same dashboard
3. **Clear Naming**: Use descriptive titles and labels
4. **Appropriate Visualizations**: Choose the right chart type for each metric
5. **Performance Optimization**: Limit the number of queries per dashboard

### Alert Configuration

1. **Meaningful Thresholds**: Set thresholds based on business impact
2. **Appropriate Timing**: Use suitable `for` durations to avoid flapping
3. **Clear Descriptions**: Provide actionable alert descriptions
4. **Escalation Policies**: Implement proper escalation chains
5. **Regular Review**: Periodically review and adjust alert rules

### Query Optimization

1. **Use Recording Rules**: Pre-calculate expensive queries
2. **Appropriate Time Ranges**: Use suitable time ranges for aggregations
3. **Efficient Selectors**: Use specific label selectors
4. **Avoid High Cardinality**: Be careful with label combinations
5. **Rate vs Increase**: Use `rate()` for per-second rates

### Security Practices

1. **Access Control**: Implement proper user authentication and authorization
2. **Network Security**: Use firewalls and network segmentation
3. **Data Encryption**: Encrypt data in transit and at rest
4. **Regular Updates**: Keep monitoring software up to date
5. **Audit Logging**: Enable and monitor access logs

## Advanced Topics {#advanced-topics}

### Custom Metrics Development

```python
# Example: Adding custom ACGS metrics
from prometheus_client import Counter, Histogram, Gauge

# Constitutional governance metrics
constitutional_compliance = Gauge(
    'acgs_constitutional_compliance_score',
    'Constitutional compliance score',
    ['service', 'principle']
)

policy_synthesis_duration = Histogram(
    'acgs_policy_synthesis_duration_seconds',
    'Policy synthesis duration',
    ['synthesis_type']
)

governance_actions = Counter(
    'acgs_governance_actions_total',
    'Total governance actions',
    ['action_type', 'status']
)
```

### Advanced PromQL Queries

```promql
# Complex aggregations
sum(rate(http_requests_total[5m])) by (job, status) / 
sum(rate(http_requests_total[5m])) by (job)

# Prediction queries
predict_linear(node_filesystem_free_bytes[1h], 4*3600) < 0

# Anomaly detection
abs(rate(http_requests_total[5m]) - 
    avg_over_time(rate(http_requests_total[5m])[1h:5m])) > 
    2 * stddev_over_time(rate(http_requests_total[5m])[1h:5m])
```

### Integration with External Systems

**Webhook Integration**:
```yaml
# alertmanager.yml
webhook_configs:
  - url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    send_resolved: true
    title: 'ACGS Alert: {{ .GroupLabels.alertname }}'
```

**API Integration**:
```bash
# Custom notification script
curl -X POST https://api.external-system.com/alerts \
  -H "Content-Type: application/json" \
  -d '{"alert": "'$ALERT_NAME'", "severity": "'$SEVERITY'"}'
```

---

**Additional Resources**:
- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Operational Runbooks](OPERATIONAL_RUNBOOKS.md)
- [Security Configuration Guide](SECURITY_GUIDE.md)
- [Performance Validation Guide](PERFORMANCE_VALIDATION_GUIDE.md)

**Support Contacts**:
- **Training Questions**: training@acgs.ai
- **Technical Support**: support@acgs.ai
- **Emergency Escalation**: +1-XXX-XXX-XXXX
