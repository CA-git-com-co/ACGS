# ACGS-1 Monitoring Infrastructure Production Deployment Guide

## Subtask 13.8: Documentation and Production Deployment

This comprehensive guide provides step-by-step procedures for deploying the ACGS-1 monitoring infrastructure to production environments with enterprise-grade reliability and security.

## Table of Contents

1. [Prerequisites and Environment Requirements](#prerequisites)
2. [Security Configuration](#security-configuration)
3. [Production Deployment Procedures](#deployment-procedures)
4. [Integration with ACGS Services](#integration)
5. [Performance Validation](#performance-validation)
6. [Backup and Disaster Recovery](#backup-recovery)
7. [Operational Procedures](#operational-procedures)
8. [Troubleshooting Guide](#troubleshooting)

## Prerequisites and Environment Requirements {#prerequisites}

### System Requirements

**Minimum Hardware Specifications**:
- **CPU**: 8 cores (16 vCPUs recommended)
- **Memory**: 32GB RAM (64GB recommended for >1000 concurrent users)
- **Storage**: 500GB SSD (1TB recommended for 15-day retention)
- **Network**: 1Gbps bandwidth with low latency (<10ms)

**Operating System**:
- Ubuntu 20.04 LTS or later
- CentOS 8 or later
- RHEL 8 or later
- Docker 20.10+ and Docker Compose 2.0+

### Software Dependencies

```bash
# Required packages
sudo apt-get update
sudo apt-get install -y \
    docker.io \
    docker-compose \
    curl \
    wget \
    jq \
    python3 \
    python3-pip \
    git \
    htop \
    iotop \
    netstat-nat

# Python dependencies for monitoring tools
pip3 install aiohttp psutil prometheus_client
```

### Network Configuration

**Required Ports**:
- **Prometheus**: 9090 (metrics collection)
- **Grafana**: 3000 (dashboard access)
- **Alertmanager**: 9093 (alert management)
- **HAProxy Exporter**: 9101 (load balancer metrics)
- **Node Exporter**: 9100 (system metrics)

**Firewall Configuration**:
```bash
# Allow monitoring ports
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9093/tcp  # Alertmanager
sudo ufw allow 9101/tcp  # HAProxy Exporter
sudo ufw allow 9100/tcp  # Node Exporter

# Allow ACGS service ports
sudo ufw allow 8000:8006/tcp  # ACGS services
sudo ufw allow 8080/tcp       # HAProxy
```

## Security Configuration {#security-configuration}

### Authentication and Access Control

**Grafana Security Configuration**:
```yaml
# grafana.ini security settings
[security]
admin_user = acgs_admin
admin_password = ${GRAFANA_ADMIN_PASSWORD}
secret_key = ${GRAFANA_SECRET_KEY}
disable_gravatar = true
cookie_secure = true
cookie_samesite = strict

[auth]
disable_login_form = false
disable_signout_menu = false

[auth.anonymous]
enabled = false

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer
```

**Prometheus Security Configuration**:
```yaml
# prometheus.yml security settings
global:
  external_labels:
    cluster: 'acgs-1-production'
    environment: 'production'
    system: 'constitutional-governance'

# Enable basic authentication
basic_auth_users:
  acgs_monitor: ${PROMETHEUS_PASSWORD_HASH}

# TLS configuration
tls_server_config:
  cert_file: /etc/prometheus/certs/prometheus.crt
  key_file: /etc/prometheus/certs/prometheus.key
```

**Environment Variables Setup**:
```bash
# Create secure environment file
cat > /etc/acgs/monitoring.env << EOF
# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 32)
GRAFANA_SECRET_KEY=$(openssl rand -base64 32)

# Prometheus Configuration
PROMETHEUS_PASSWORD_HASH=$(htpasswd -nbB acgs_monitor $(openssl rand -base64 16))

# Alertmanager Configuration
SMTP_USERNAME=acgs-alerts@acgs.ai
SMTP_PASSWORD=${SMTP_PASSWORD}
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
PAGERDUTY_INTEGRATION_KEY=${PAGERDUTY_KEY}

# Security Settings
TLS_CERT_PATH=/etc/acgs/certs
BACKUP_ENCRYPTION_KEY=$(openssl rand -base64 32)
EOF

# Secure the environment file
chmod 600 /etc/acgs/monitoring.env
chown root:root /etc/acgs/monitoring.env
```

### SSL/TLS Configuration

**Generate SSL Certificates**:
```bash
# Create certificate directory
sudo mkdir -p /etc/acgs/certs

# Generate self-signed certificates (replace with CA-signed in production)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/acgs/certs/monitoring.key \
    -out /etc/acgs/certs/monitoring.crt \
    -subj "/C=US/ST=State/L=City/O=ACGS/CN=monitoring.acgs.ai"

# Set proper permissions
sudo chmod 600 /etc/acgs/certs/monitoring.key
sudo chmod 644 /etc/acgs/certs/monitoring.crt
```

## Production Deployment Procedures {#deployment-procedures}

### Step 1: Environment Preparation

```bash
# Clone ACGS-1 repository
git clone https://github.com/CA-git-com-co/ACGS.git /opt/acgs-1
cd /opt/acgs-1

# Create necessary directories
sudo mkdir -p /var/log/acgs
sudo mkdir -p /var/lib/acgs/monitoring
sudo mkdir -p /etc/acgs

# Set proper ownership
sudo chown -R acgs:acgs /var/log/acgs
sudo chown -R acgs:acgs /var/lib/acgs
```

### Step 2: Configuration Deployment

```bash
# Deploy monitoring configurations
sudo cp infrastructure/monitoring/prometheus.yml /etc/prometheus/
sudo cp infrastructure/monitoring/alertmanager.yml /etc/alertmanager/
sudo cp -r infrastructure/monitoring/rules /etc/prometheus/
sudo cp -r infrastructure/monitoring/grafana /etc/grafana/

# Deploy Docker Compose configuration
cp infrastructure/monitoring/docker-compose.monitoring.yml /opt/acgs-1/
```

### Step 3: Service Deployment

```bash
# Deploy monitoring stack
cd /opt/acgs-1
docker-compose -f docker-compose.monitoring.yml up -d

# Verify service startup
docker-compose -f docker-compose.monitoring.yml ps
```

### Step 4: Health Validation

```bash
# Run comprehensive health check
./infrastructure/monitoring/validate-deployment.sh

# Verify service endpoints
curl -f http://localhost:9090/-/healthy  # Prometheus
curl -f http://localhost:3000/api/health # Grafana
curl -f http://localhost:9093/-/healthy  # Alertmanager
```

### Step 5: Performance Validation

```bash
# Run performance validation suite
./infrastructure/monitoring/run-performance-validation.sh

# Verify performance targets
python3 infrastructure/monitoring/performance-validation.py \
    --users 1000 \
    --duration 600
```

## Integration with ACGS Services {#integration}

### Service Discovery Configuration

**Prometheus Service Discovery**:
```yaml
scrape_configs:
  # ACGS Core Services
  - job_name: 'acgs-auth-service'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'acgs-ac-service'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'acgs-integrity-service'
    static_configs:
      - targets: ['localhost:8002']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'acgs-fv-service'
    static_configs:
      - targets: ['localhost:8003']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'acgs-gs-service'
    static_configs:
      - targets: ['localhost:8004']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'acgs-pgc-service'
    static_configs:
      - targets: ['localhost:8005']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'acgs-ec-service'
    static_configs:
      - targets: ['localhost:8006']
    metrics_path: '/metrics'
    scrape_interval: 15s

  # Infrastructure Services
  - job_name: 'haproxy-exporter'
    static_configs:
      - targets: ['localhost:9101']
    scrape_interval: 15s

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['localhost:9121']
    scrape_interval: 30s

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['localhost:9187']
    scrape_interval: 30s
```

### Custom ACGS Metrics Integration

**Constitutional Governance Metrics**:
```python
# Example metrics integration in ACGS services
from prometheus_client import Counter, Histogram, Gauge

# Constitutional compliance metrics
constitutional_compliance_score = Gauge(
    'acgs_constitutional_compliance_score',
    'Constitutional compliance score (0-1)',
    ['service', 'principle_id']
)

# Policy synthesis metrics
policy_synthesis_duration = Histogram(
    'acgs_policy_synthesis_duration_seconds',
    'Time spent on policy synthesis',
    ['service', 'synthesis_type']
)

# Governance action costs
governance_action_cost = Gauge(
    'acgs_governance_action_cost_sol',
    'Cost of governance actions in SOL',
    ['action_type', 'service']
)
```

## Performance Validation {#performance-validation}

### Performance Targets

**Response Time Targets**:
- Prometheus queries: <500ms (95th percentile)
- Grafana dashboards: <2000ms loading time
- Alert detection: <30 seconds
- Metrics collection: <100ms scraping latency

**Availability Targets**:
- Overall system: >99.9% availability
- Individual services: >99.5% availability
- Load test success rate: >95%

**Resource Utilization Targets**:
- CPU overhead: <1% of total system resources
- Memory overhead: <2% of total system resources
- Network overhead: <5% of total bandwidth

### Performance Testing Procedures

```bash
# Run comprehensive performance validation
./infrastructure/monitoring/run-performance-validation.sh

# Run individual test components
python3 infrastructure/monitoring/load-test-monitoring.py --users 1000
python3 infrastructure/monitoring/test-alert-system.py
python3 infrastructure/monitoring/test-dashboard-performance.py

# Monitor performance during testing
./scripts/monitor-system-resources.sh
```

## Backup and Disaster Recovery {#backup-recovery}

### Backup Procedures

**Automated Backup Script**:
```bash
#!/bin/bash
# backup-monitoring-data.sh

BACKUP_DIR="/var/backups/acgs-monitoring/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup Prometheus data
docker exec acgs_prometheus promtool tsdb snapshot /prometheus
cp -r /var/lib/docker/volumes/prometheus_data/_data/snapshots/latest "$BACKUP_DIR/prometheus"

# Backup Grafana data
docker exec acgs_grafana grafana-cli admin export-dashboard > "$BACKUP_DIR/grafana-dashboards.json"
cp -r /var/lib/docker/volumes/grafana_data/_data "$BACKUP_DIR/grafana"

# Backup configurations
cp -r /etc/prometheus "$BACKUP_DIR/"
cp -r /etc/alertmanager "$BACKUP_DIR/"
cp -r /etc/grafana "$BACKUP_DIR/"

# Encrypt and compress backup
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
openssl enc -aes-256-cbc -salt -in "$BACKUP_DIR.tar.gz" -out "$BACKUP_DIR.tar.gz.enc" -k "$BACKUP_ENCRYPTION_KEY"

# Clean up unencrypted files
rm -rf "$BACKUP_DIR" "$BACKUP_DIR.tar.gz"
```

### Disaster Recovery Procedures

**Recovery Steps**:
1. **Stop monitoring services**
2. **Restore configurations from backup**
3. **Restore data volumes**
4. **Restart services**
5. **Validate functionality**

```bash
# Disaster recovery script
./infrastructure/monitoring/disaster-recovery.sh --backup-file /path/to/backup.tar.gz.enc
```

## Operational Procedures {#operational-procedures}

### Daily Operations

**Health Check Routine**:
```bash
# Daily health check script
./infrastructure/monitoring/daily-health-check.sh

# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# Verify metrics collection
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result | length'

# Check alert status
curl -s "http://localhost:9093/api/v1/alerts" | jq '.data | length'
```

**Performance Monitoring**:
```bash
# Monitor system resources
./scripts/monitor-system-resources.sh

# Check monitoring overhead
./infrastructure/monitoring/check-monitoring-overhead.sh

# Validate performance targets
python3 infrastructure/monitoring/validate-performance-targets.py
```

### Maintenance Procedures

**Weekly Maintenance**:
- Review alert configurations and thresholds
- Analyze performance trends and capacity planning
- Update dashboard configurations based on usage patterns
- Validate backup integrity and recovery procedures

**Monthly Maintenance**:
- Update monitoring software versions
- Review and optimize alert rules
- Capacity planning and resource scaling
- Security audit and access review

## Troubleshooting Guide {#troubleshooting}

### Common Issues and Solutions

**High Memory Usage**:
```bash
# Check Prometheus memory usage
docker stats acgs_prometheus

# Optimize retention settings
# Edit prometheus.yml:
# --storage.tsdb.retention.time=15d
# --storage.tsdb.max-block-duration=2h
```

**Slow Dashboard Loading**:
```bash
# Check Grafana performance
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:3000/api/health

# Optimize dashboard queries
# Use appropriate time ranges
# Limit data points in visualizations
# Enable query caching
```

**Alert Fatigue**:
```bash
# Review alert frequency
curl -s "http://localhost:9093/api/v1/alerts" | jq '.data[] | .labels.alertname' | sort | uniq -c

# Adjust alert thresholds
# Edit alert rules in /etc/prometheus/rules/
# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload
```

For detailed troubleshooting procedures, refer to the [Operational Runbooks](OPERATIONAL_RUNBOOKS.md).

---

**Next Steps**: After successful deployment, proceed with [Training and Knowledge Transfer](TRAINING_GUIDE.md) and [Operational Runbooks](OPERATIONAL_RUNBOOKS.md) setup.
