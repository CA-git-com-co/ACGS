# ACGS-1 Monitoring Setup

## Overview
This document describes the monitoring setup for the ACGS-1 system after reorganization.

## Services Monitored
- auth_service (port 8000)
- ac_service (port 8001)
- integrity_service (port 8002)
- fv_service (port 8003)
- gs_service (port 8004)
- pgc_service (port 8005)
- ec_service (port 8006)

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

Generated: 2025-06-24 00:43:50
