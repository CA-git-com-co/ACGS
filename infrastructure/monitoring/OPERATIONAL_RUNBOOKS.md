<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# ACGS-1 Monitoring Infrastructure Operational Runbooks

## Overview

This document provides comprehensive operational runbooks for managing the ACGS-1 monitoring infrastructure in production environments. These runbooks cover incident response, maintenance procedures, and troubleshooting guides for enterprise-grade monitoring operations.

## Table of Contents

1. [Incident Response Procedures](#incident-response)
2. [Service Management](#service-management)
3. [Performance Troubleshooting](#performance-troubleshooting)
4. [Alert Management](#alert-management)
5. [Backup and Recovery Operations](#backup-recovery)
6. [Maintenance Procedures](#maintenance)
7. [Emergency Procedures](#emergency)

## Incident Response Procedures {#incident-response}

### Critical Alert Response (Response Time: <5 minutes)

**Severity: Critical**

- Service Down alerts
- Constitutional compliance failures
- Security breaches
- System resource exhaustion

**Response Procedure**:

```bash
# Step 1: Acknowledge alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{"status": "acknowledged", "alertname": "ALERT_NAME"}'

# Step 2: Check service status
docker-compose -f docker-compose.monitoring.yml ps
systemctl status acgs-*

# Step 3: Review logs
docker logs acgs_prometheus --tail 100
docker logs acgs_grafana --tail 100
docker logs acgs_alertmanager --tail 100

# Step 4: Check system resources
htop
df -h
free -m

# Step 5: Escalate if needed
./scripts/escalate-incident.sh --severity critical --alert ALERT_NAME
```

### High Priority Alert Response (Response Time: <15 minutes)

**Severity: High**

- High error rates
- Performance degradation
- Load balancer issues
- Database connection problems

**Response Procedure**:

```bash
# Step 1: Assess impact
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result'

# Step 2: Check service health
./infrastructure/monitoring/health-check.sh

# Step 3: Review performance metrics
curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total[5m])" | jq

# Step 4: Implement temporary mitigation
./scripts/temporary-mitigation.sh --issue ISSUE_TYPE

# Step 5: Document findings
echo "$(date): High priority alert - ALERT_NAME" >> /var/log/acgs/incident.log
```

### Warning Alert Response (Response Time: <1 hour)

**Severity: Warning**

- Resource usage warnings
- Minor performance issues
- Configuration drift
- Capacity planning alerts

**Response Procedure**:

```bash
# Step 1: Analyze trends
./scripts/analyze-trends.sh --metric METRIC_NAME --timeframe 24h

# Step 2: Check capacity
./scripts/capacity-check.sh

# Step 3: Plan remediation
./scripts/plan-remediation.sh --alert ALERT_NAME

# Step 4: Schedule maintenance if needed
./scripts/schedule-maintenance.sh --type preventive
```

## Service Management {#service-management}

### Starting Monitoring Services

```bash
# Start all monitoring services
cd /opt/acgs-1
docker-compose -f docker-compose.monitoring.yml up -d

# Verify startup
./infrastructure/monitoring/verify-startup.sh

# Check service health
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana
curl http://localhost:9093/-/healthy  # Alertmanager
```

### Stopping Monitoring Services

```bash
# Graceful shutdown
docker-compose -f docker-compose.monitoring.yml down

# Force stop if needed
docker-compose -f docker-compose.monitoring.yml kill
docker-compose -f docker-compose.monitoring.yml rm -f
```

### Restarting Individual Services

```bash
# Restart Prometheus
docker-compose -f docker-compose.monitoring.yml restart prometheus

# Restart Grafana
docker-compose -f docker-compose.monitoring.yml restart grafana

# Restart Alertmanager
docker-compose -f docker-compose.monitoring.yml restart alertmanager
```

### Service Configuration Reload

```bash
# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload

# Reload Alertmanager configuration
curl -X POST http://localhost:9093/-/reload

# Restart Grafana for configuration changes
docker-compose -f docker-compose.monitoring.yml restart grafana
```

## Performance Troubleshooting {#performance-troubleshooting}

### High CPU Usage

**Symptoms**: CPU usage >80% sustained
**Investigation**:

```bash
# Check process CPU usage
top -p $(pgrep -d',' prometheus)
top -p $(pgrep -d',' grafana)

# Check Prometheus query load
curl -s "http://localhost:9090/api/v1/status/tsdb" | jq '.data'

# Analyze slow queries
curl -s "http://localhost:9090/api/v1/label/__name__/values" | jq '.data | length'
```

**Resolution**:

```bash
# Optimize Prometheus configuration
# Edit prometheus.yml:
# --query.max-concurrency=20
# --query.timeout=30s

# Restart Prometheus
docker-compose -f docker-compose.monitoring.yml restart prometheus
```

### High Memory Usage

**Symptoms**: Memory usage >90%
**Investigation**:

```bash
# Check memory usage by service
docker stats --no-stream

# Check Prometheus memory usage
curl -s "http://localhost:9090/api/v1/status/tsdb" | jq '.data.headStats'

# Check for memory leaks
./scripts/memory-leak-detection.sh
```

**Resolution**:

```bash
# Optimize retention settings
# Edit prometheus.yml:
# --storage.tsdb.retention.time=15d
# --storage.tsdb.max-block-duration=2h

# Restart services
docker-compose -f docker-compose.monitoring.yml restart
```

### Slow Dashboard Loading

**Symptoms**: Dashboard load times >5 seconds
**Investigation**:

```bash
# Check Grafana performance
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:3000/api/health

# Check database connections
docker exec acgs_grafana grafana-cli admin stats

# Analyze slow queries
tail -f /var/log/grafana/grafana.log | grep "slow"
```

**Resolution**:

```bash
# Optimize dashboard queries
# - Use appropriate time ranges
# - Limit data points in visualizations
# - Use efficient PromQL queries

# Enable query caching
# Edit grafana.ini:
# [caching]
# enabled = true
```

### Alert Storm Prevention

**Symptoms**: >100 alerts firing simultaneously
**Investigation**:

```bash
# Check current alerts
curl -s "http://localhost:9093/api/v1/alerts" | jq '.data | length'

# Analyze alert patterns
curl -s "http://localhost:9093/api/v1/alerts" | jq '.data[] | .labels.alertname' | sort | uniq -c
```

**Resolution**:

```bash
# Implement alert inhibition
# Edit alertmanager.yml:
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['service', 'instance']

# Reload Alertmanager
curl -X POST http://localhost:9093/-/reload
```

## Alert Management {#alert-management}

### Adding New Alert Rules

```bash
# Create new alert rule file
cat > /etc/prometheus/rules/new_alerts.yml << EOF
groups:
  - name: new_service_alerts
    rules:
      - alert: NewServiceDown
        expr: up{job="new-service"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "New service is down"
          description: "Service has been down for more than 30 seconds"
EOF

# Validate alert rules
promtool check rules /etc/prometheus/rules/new_alerts.yml

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

### Modifying Alert Thresholds

```bash
# Edit existing alert rule
vim /etc/prometheus/rules/acgs_alert_rules.yml

# Example: Change response time threshold
# FROM: expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
# TO:   expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1

# Validate changes
promtool check rules /etc/prometheus/rules/acgs_alert_rules.yml

# Reload configuration
curl -X POST http://localhost:9090/-/reload
```

### Silencing Alerts

```bash
# Silence specific alert
curl -X POST http://localhost:9093/api/v1/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [
      {
        "name": "alertname",
        "value": "ServiceDown",
        "isRegex": false
      }
    ],
    "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "endsAt": "'$(date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "createdBy": "operator",
    "comment": "Planned maintenance"
  }'

# List active silences
curl -s "http://localhost:9093/api/v1/silences" | jq '.data'
```

## Backup and Recovery Operations {#backup-recovery}

### Creating Backups

```bash
# Run automated backup
./infrastructure/monitoring/backup-monitoring-data.sh

# Manual backup procedure
BACKUP_DIR="/var/backups/acgs-monitoring/manual_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup Prometheus data
docker exec acgs_prometheus promtool tsdb snapshot /prometheus
cp -r /var/lib/docker/volumes/prometheus_data/_data/snapshots/latest "$BACKUP_DIR/prometheus"

# Backup Grafana data
docker exec acgs_grafana grafana-cli admin export-dashboard > "$BACKUP_DIR/grafana-dashboards.json"

# Backup configurations
cp -r /etc/prometheus "$BACKUP_DIR/"
cp -r /etc/alertmanager "$BACKUP_DIR/"
```

### Restoring from Backup

```bash
# Stop monitoring services
docker-compose -f docker-compose.monitoring.yml down

# Restore Prometheus data
rm -rf /var/lib/docker/volumes/prometheus_data/_data/*
cp -r "$BACKUP_DIR/prometheus/*" /var/lib/docker/volumes/prometheus_data/_data/

# Restore Grafana data
rm -rf /var/lib/docker/volumes/grafana_data/_data/*
cp -r "$BACKUP_DIR/grafana/*" /var/lib/docker/volumes/grafana_data/_data/

# Restore configurations
cp -r "$BACKUP_DIR/prometheus/*" /etc/prometheus/
cp -r "$BACKUP_DIR/alertmanager/*" /etc/alertmanager/

# Start services
docker-compose -f docker-compose.monitoring.yml up -d

# Verify restoration
./infrastructure/monitoring/verify-restoration.sh
```

## Maintenance Procedures {#maintenance}

### Weekly Maintenance

```bash
# Check system health
./infrastructure/monitoring/weekly-health-check.sh

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

# Performance optimization
./scripts/performance-optimization.sh
```

### Quarterly Maintenance

```bash
# Comprehensive system review
./scripts/quarterly-system-review.sh

# Update security certificates
./scripts/update-certificates.sh

# Review access controls
./scripts/review-access-controls.sh

# Disaster recovery testing
./scripts/test-disaster-recovery.sh

# Documentation updates
./scripts/update-documentation.sh
```

## Emergency Procedures {#emergency}

### Complete System Failure

**Symptoms**: All monitoring services down
**Response**:

```bash
# Step 1: Check system status
systemctl status docker
df -h
free -m

# Step 2: Restart Docker if needed
sudo systemctl restart docker

# Step 3: Start monitoring services
cd /opt/acgs-1
docker-compose -f docker-compose.monitoring.yml up -d

# Step 4: Verify recovery
./infrastructure/monitoring/emergency-recovery-check.sh

# Step 5: Escalate if needed
./scripts/emergency-escalation.sh
```

### Data Corruption

**Symptoms**: Metrics data inconsistencies
**Response**:

```bash
# Step 1: Stop affected services
docker-compose -f docker-compose.monitoring.yml stop prometheus

# Step 2: Check data integrity
promtool tsdb analyze /var/lib/docker/volumes/prometheus_data/_data

# Step 3: Restore from backup if needed
./infrastructure/monitoring/restore-from-backup.sh --latest

# Step 4: Restart services
docker-compose -f docker-compose.monitoring.yml start prometheus
```

### Security Incident

**Symptoms**: Unauthorized access detected
**Response**:

```bash
# Step 1: Isolate affected systems
./scripts/isolate-systems.sh

# Step 2: Change all passwords
./scripts/rotate-passwords.sh

# Step 3: Review access logs
./scripts/review-access-logs.sh

# Step 4: Implement additional security measures
./scripts/enhance-security.sh

# Step 5: Document incident
./scripts/document-security-incident.sh
```



## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---

**Contact Information**:

- **Emergency Escalation**: +1-XXX-XXX-XXXX
- **Security Team**: security@acgs.ai
- **Operations Team**: ops@acgs.ai

**Additional Resources**:

- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Training Guide](TRAINING_GUIDE.md)
- [Security Configuration Guide](SECURITY_GUIDE.md)
