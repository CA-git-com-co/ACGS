# DGM Service Monitoring & Alerting System

## Overview

This directory contains a comprehensive monitoring and alerting system for the DGM (Darwin Gödel Machine) Service. The system provides real-time monitoring, alerting, and observability for all DGM operations including constitutional compliance, performance metrics, and system health.

## Architecture

### Components

1. **Prometheus** - Metrics collection and storage
2. **Alertmanager** - Alert routing and notifications
3. **Grafana** - Visualization and dashboards
4. **Blackbox Exporter** - Endpoint monitoring
5. **Node Exporter** - System metrics
6. **cAdvisor** - Container metrics
7. **Redis Exporter** - Cache metrics
8. **PostgreSQL Exporter** - Database metrics

### Monitoring Stack Ports

- **Prometheus**: 9091 (DGM-specific instance)
- **Alertmanager**: 9093
- **Grafana**: 3000
- **Node Exporter**: 9100
- **cAdvisor**: 8080
- **Redis Exporter**: 9121
- **PostgreSQL Exporter**: 9187
- **Blackbox Exporter**: 9115

## Quick Start

### Prerequisites

- Docker 24.0+
- Docker Compose 2.0+
- 4GB+ available RAM
- 10GB+ available disk space

### Starting the Monitoring Stack

```bash
# Navigate to monitoring directory
cd services/core/dgm-service/monitoring

# Start all monitoring services
./start-monitoring.sh start

# Check service status
./start-monitoring.sh status

# View logs
./start-monitoring.sh logs [service_name]

# Stop services
./start-monitoring.sh stop
```

### Environment Configuration

The monitoring stack uses environment variables defined in `.env` file:

```bash
# Database Configuration
POSTGRES_DB=dgm_db
POSTGRES_USER=dgm_user
POSTGRES_PASSWORD=your_secure_password

# Redis Configuration
REDIS_PASSWORD=your_redis_password

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=your_grafana_password

# Alerting Configuration
SMTP_PASSWORD=your_smtp_password
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
PAGERDUTY_ROUTING_KEY=your_pagerduty_routing_key
```

## Alert Categories

### Critical Alerts

- **DGMServiceDown**: Service unavailable
- **DGMHighErrorRate**: Error rate > 5%
- **DGMConstitutionalViolation**: Constitutional compliance violations

### Warning Alerts

- **DGMHighResponseTime**: Response time > 2s
- **DGMImprovementFailureRate**: Improvement failure rate > 20%
- **DGMLowComplianceScore**: Compliance score < 95%
- **DGMPerformanceDegradation**: Performance score < 0.8

### Info Alerts

- **DGMBanditHighExploration**: High exploration rate (informational)
- **DGMArchiveGrowthRate**: High archive growth rate

## Notification Channels

### Slack Integration

Alerts are routed to different Slack channels based on severity and component:

- `#dgm-critical` - Critical alerts requiring immediate attention
- `#dgm-alerts` - General DGM service alerts
- `#constitutional-compliance` - Constitutional compliance issues
- `#dgm-performance` - Performance-related alerts
- `#dgm-security` - Security alerts
- `#dgm-database` - Database alerts
- `#dgm-models` - AI model alerts

### Email Notifications

- **Critical alerts**: dgm-oncall@acgs.ai, sre-team@acgs.ai
- **Constitutional alerts**: constitutional-team@acgs.ai, compliance@acgs.ai
- **Security alerts**: security-team@acgs.ai
- **General alerts**: dgm-team@acgs.ai

### PagerDuty Integration

Critical alerts are automatically escalated to PagerDuty for 24/7 on-call response.

## Metrics Categories

### Service Health Metrics

- `dgm_service_up` - Service availability
- `dgm_http_requests_total` - HTTP request counts
- `dgm_http_request_duration_seconds` - Request latency

### Improvement Metrics

- `dgm_improvements_total` - Total improvements by status
- `dgm_improvement_duration_seconds` - Improvement execution time
- `dgm_active_improvements` - Currently active improvements
- `dgm_improvement_success_rate` - Success rate (0-1)

### Constitutional Compliance Metrics

- `dgm_constitutional_validations_total` - Validation counts
- `dgm_constitutional_compliance_score` - Compliance scores
- `dgm_constitutional_violations_total` - Violation counts
- `dgm_average_compliance_score` - Average compliance

### Performance Metrics

- `dgm_performance_score` - System performance scores
- `dgm_performance_improvement_percent` - Performance improvements

### Bandit Algorithm Metrics

- `dgm_bandit_arm_pulls_total` - Bandit arm selections
- `dgm_bandit_arm_reward` - Reward distributions
- `dgm_bandit_exploration_rate` - Exploration rates

### Foundation Model Metrics

- `dgm_model_requests_total` - Model API requests
- `dgm_model_request_duration_seconds` - Model request latency
- `dgm_model_tokens_total` - Token usage
- `dgm_model_cost_total` - API costs

## Configuration Files

### Core Configuration

- `prometheus-dgm.yml` - Prometheus configuration
- `alert_rules.yml` - Alert rule definitions
- `alertmanager.yml` - Alert routing configuration
- `blackbox.yml` - Endpoint monitoring configuration

### Templates

- `templates/dgm-alerts.tmpl` - Alert notification templates

### Docker Configuration

- `docker-compose.monitoring.yml` - Complete monitoring stack
- `.env` - Environment variables

## Runbooks

Alert notifications include runbook URLs for troubleshooting:

- **Service Down**: https://docs.acgs.ai/runbooks/dgm-service-down
- **High Error Rate**: https://docs.acgs.ai/runbooks/dgm-high-error-rate
- **Constitutional Violations**: https://docs.acgs.ai/runbooks/dgm-constitutional-violation
- **Performance Issues**: https://docs.acgs.ai/runbooks/dgm-performance-degradation

## Troubleshooting

### Common Issues

1. **Services not starting**

   ```bash
   # Check Docker daemon
   docker info

   # Check logs
   ./start-monitoring.sh logs
   ```

2. **Metrics not appearing**

   ```bash
   # Verify DGM service is exposing metrics
   curl http://localhost:8007/metrics

   # Check Prometheus targets
   curl http://localhost:9091/api/v1/targets
   ```

3. **Alerts not firing**

   ```bash
   # Check alert rules
   curl http://localhost:9091/api/v1/rules

   # Verify Alertmanager config
   curl http://localhost:9093/api/v1/status
   ```

### Log Locations

- Prometheus: `docker logs dgm-prometheus`
- Alertmanager: `docker logs dgm-alertmanager`
- Grafana: `docker logs dgm-grafana`

## Maintenance

### Data Retention

- **Prometheus**: 30 days (configurable)
- **Alertmanager**: 120 hours
- **Grafana**: Persistent dashboards and settings

### Backup

```bash
# Backup Grafana dashboards
docker exec dgm-grafana grafana-cli admin export-dashboard

# Backup Prometheus data
docker run --rm -v dgm-prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data
```

### Updates

```bash
# Update monitoring stack
docker-compose -f docker-compose.monitoring.yml pull
./start-monitoring.sh restart
```

## Security Considerations

- All services run in isolated Docker networks
- Sensitive credentials stored in environment variables
- TLS encryption for external communications
- Role-based access control in Grafana
- Alert notification authentication

## Performance Tuning

### Prometheus

- Adjust scrape intervals based on requirements
- Configure retention policies for storage optimization
- Use recording rules for complex queries

### Alertmanager

- Configure appropriate grouping and throttling
- Set up inhibition rules to prevent alert storms
- Optimize notification delivery

## Integration with ACGS Platform

The DGM monitoring system integrates with the broader ACGS monitoring infrastructure:

- Shares the `acgs-network` Docker network
- Collects metrics from other ACGS services
- Forwards critical alerts to central monitoring
- Participates in platform-wide observability

## Support

For issues with the DGM monitoring system:

1. Check this documentation
2. Review logs and metrics
3. Consult runbooks for specific alerts
4. Contact the DGM team: dgm-team@acgs.ai
