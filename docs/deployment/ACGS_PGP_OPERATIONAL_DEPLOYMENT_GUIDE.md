# ACGS-PGP Operational Deployment Guide

**Version**: 1.0.0
**Date**: 2025-06-27
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This guide provides comprehensive procedures for deploying, operating, and maintaining the ACGS-PGP system in production environments with constitutional governance requirements.

## Pre-Deployment Checklist

### Infrastructure Requirements

#### Hardware Specifications

- **CPU**: 16 cores minimum, 32 cores recommended
- **Memory**: 32GB RAM minimum, 64GB recommended
- **Storage**: 500GB SSD minimum, 1TB recommended
- **Network**: 1Gbps minimum, 10Gbps recommended
- **Redundancy**: Multi-zone deployment for high availability

#### Software Requirements

- **OS**: Ubuntu 22.04 LTS or RHEL 9+
- **Container Runtime**: Docker 24.0+ with containerd
- **Orchestration**: Kubernetes 1.28+ (optional but recommended)
- **Load Balancer**: NGINX or HAProxy
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or similar

### Security Requirements

#### Network Security

- **Firewall**: Only required ports open (8000-8006, 8181)
- **TLS**: SSL/TLS certificates for all external endpoints
- **VPN**: Secure access for administrative functions
- **Network Segmentation**: Isolated network for ACGS services

#### Access Control

- **Authentication**: Multi-factor authentication required
- **Authorization**: Role-based access control (RBAC)
- **Audit Logging**: All administrative actions logged
- **Key Management**: Secure storage for API keys and secrets

### Constitutional Governance Requirements

#### Compliance Validation

- [ ] Constitutional hash verified: `cdd01ef066bc6cf2`
- [ ] Compliance threshold configured: >95%
- [ ] DGM safety patterns implemented
- [ ] Emergency shutdown procedures tested
- [ ] OPA policies deployed and validated

#### AI Model Integration

- [ ] Google Gemini API key configured and tested
- [ ] DeepSeek R1 API key configured and tested
- [ ] NVIDIA Qwen API key configured and tested
- [ ] Nano-vLLM local deployment configured
- [ ] Constitutional reasoning capabilities validated

## Deployment Procedures

### Phase 1: Infrastructure Deployment

#### 1.1 Environment Setup

```bash
# Create deployment directory
mkdir -p /opt/acgs-pgp
cd /opt/acgs-pgp

# Clone repository
git clone https://github.com/CA-git-com-co/ACGS.git .

# Set up environment
cp config/env/config/environments/developmentconfig/environments/production.env.backup.example config/env/config/environments/development.env
```

#### 1.2 Database Setup

```bash
# Deploy PostgreSQL with high availability
docker-compose -f infrastructure/docker/config/docker/docker-compose.production.yml up -d postgres

# Wait for database to be ready
sleep 30

# Run migrations
cd services/shared
alembic upgrade head
```

#### 1.3 Infrastructure Services

```bash
# Deploy Redis cluster
docker-compose -f infrastructure/docker/config/docker/docker-compose.production.yml up -d redis

# Deploy OPA with policies
docker-compose -f infrastructure/docker/config/docker/docker-compose.production.yml up -d opa

# Verify infrastructure health
curl http://localhost:5432  # PostgreSQL
curl http://localhost:6379  # Redis
curl http://localhost:8181/health  # OPA
```

### Phase 2: Service Deployment

#### 2.1 Constitutional Governance Services

```bash
# Deploy core constitutional services first
docker-compose -f infrastructure/docker/config/docker/docker-compose.production.yml up -d \
  auth_service ac_service integrity_service fv_service gs_service pgc_service ec_service \
  consensus_engine multi_agent_coordinator worker_agents blackboard_service code_analysis_service context_service

# Wait for services to stabilize
sleep 60

# Validate constitutional compliance
for port in 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010 8011 8012; do
  curl -s http://localhost:$port/constitutional/compliance
done
```

#### 2.2 Policy and Governance Services

```bash
# Deploy policy services
# (No separate deployment needed as all services are started in 2.1)
```

#### 2.3 Evolution and Computation Services

```bash
# Deploy evolution service
# (No separate deployment needed as all services are started in 2.1)
```


### Phase 3: Validation and Testing

#### 3.1 Health Validation

```bash
# Comprehensive health check
./scripts/run_all_setup_tests.sh

# Performance validation
./scripts/test_performance_validation.sh

# Emergency procedures validation
./scripts/test_emergency_shutdown.sh
```

#### 3.2 Load Testing

```bash
# Install load testing tools
npm install -g artillery

# Run load tests
artillery run tests/load/constitutional-compliance-load-test.yml
artillery run tests/load/performance-load-test.yml

# Validate results
# - Response time: ≤2000ms
# - Throughput: ≥1000 RPS
# - Error rate: <1%
# - Constitutional compliance: >95%
```

#### 3.3 Security Validation

```bash
# Run security scans
docker run --rm -v $(pwd):/app \
  aquasec/trivy fs /app

# Validate TLS configuration
openssl s_client -connect localhost:8000 -servername acgs-pgp.domain.com

# Test authentication and authorization
curl -H "Authorization: Bearer invalid_token" http://localhost:8000/protected
```

## Operational Procedures

### Daily Operations

#### Morning Health Check

```bash
#!/bin/bash
# Daily health check script

echo "ACGS-PGP Daily Health Check - $(date)"
echo "=================================="

# Service health
for port in {8000..8006}; do
  if curl -f -s http://localhost:$port/health > /dev/null; then
    echo "✅ Service on port $port: HEALTHY"
  else
    echo "❌ Service on port $port: UNHEALTHY"
  fi
done

# Constitutional compliance
echo ""
echo "Constitutional Compliance:"
for port in {8000..8006}; do
  compliance=$(curl -s http://localhost:$port/constitutional/compliance | jq -r '.compliance_score // "N/A"')
  if [[ "$compliance" != "N/A" ]] && (( $(echo "$compliance >= 0.95" | bc -l) )); then
    echo "✅ Port $port: $compliance (≥0.95)"
  else
    echo "❌ Port $port: $compliance (<0.95)"
  fi
done

# Performance metrics
echo ""
echo "Performance Metrics:"
for port in {8000..8006}; do
  start_time=$(date +%s%3N)
  if curl -f -s http://localhost:$port/health > /dev/null; then
    end_time=$(date +%s%3N)
    response_time=$((end_time - start_time))
    if [ $response_time -le 2000 ]; then
      echo "✅ Port $port: ${response_time}ms (≤2000ms)"
    else
      echo "❌ Port $port: ${response_time}ms (>2000ms)"
    fi
  fi
done
```

#### Resource Monitoring

```bash
# Check resource usage
docker stats --no-stream

# Check disk usage
df -h

# Check memory usage
free -h

# Check CPU usage
top -bn1 | grep "Cpu(s)"
```

### Weekly Operations

#### Dependency Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose -f infrastructure/docker/config/docker/docker-compose.production.yml pull

# Update Node.js dependencies
cd applications/governance-dashboard
pnpm update

# Update Python dependencies
cd services/shared
uv pip install --upgrade -r requirements.txt
```

#### Security Scans

```bash
# Scan for vulnerabilities
docker run --rm -v $(pwd):/app aquasec/trivy fs /app

# Update security policies
curl -X PUT http://localhost:8181/v1/policies/security \
  -H "Content-Type: application/json" \
  -d @policies/security-policy.json

# Rotate secrets (if needed)
# Update API keys, database passwords, etc.
```

### Monthly Operations

#### Performance Review

```bash
# Generate performance report
./scripts/generate_performance_report.sh

# Review constitutional compliance trends
./scripts/analyze_compliance_trends.sh

# Capacity planning review
./scripts/capacity_planning_analysis.sh
```

#### Backup and Recovery Testing

```bash
# Test database backup
docker exec acgs_postgres pg_dump -U acgs_user acgs_db > backup_test.sql

# Test service recovery
./scripts/test_emergency_shutdown.sh
./scripts/start_all_services.sh

# Validate recovery
./scripts/run_all_setup_tests.sh
```

## Monitoring and Alerting

### Key Performance Indicators (KPIs)

#### Constitutional Governance KPIs

- **Constitutional Compliance Score**: >95%
- **DGM Safety Pattern Availability**: >99%
- **Policy Validation Success Rate**: >98%
- **Emergency Shutdown RTO**: <30 minutes

#### Technical KPIs

- **Service Availability**: >99.9%
- **Response Time P95**: <2000ms
- **Throughput**: >1000 RPS
- **Error Rate**: <1%

#### Business KPIs

- **Governance Actions per Hour**: Baseline + growth
- **Policy Synthesis Success Rate**: >95%
- **Constitutional Reasoning Accuracy**: >98%
- **System Evolution Effectiveness**: Measured quarterly

### Alert Configuration

#### Critical Alerts (Immediate Response)

```yaml
# Prometheus alert rules
groups:
  - name: acgs-pgp-critical
    rules:
      - alert: ConstitutionalComplianceFailure
        expr: constitutional_compliance_score < 0.95
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: 'Constitutional compliance below threshold'

      - alert: ServiceDown
        expr: up{job="acgs-pgp"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: 'ACGS-PGP service is down'

      - alert: EmergencyShutdownTriggered
        expr: emergency_shutdown_active == 1
        for: 0s
        labels:
          severity: critical
        annotations:
          summary: 'Emergency shutdown has been triggered'
```

#### Warning Alerts (24h Response)

```yaml
- name: acgs-pgp-warning
  rules:
    - alert: HighResponseTime
      expr: http_request_duration_seconds{quantile="0.95"} > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: 'High response time detected'

    - alert: LowThroughput
      expr: rate(http_requests_total[5m]) < 1000
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: 'Throughput below target'
```

### Dashboard Configuration

#### Grafana Dashboards

1. **Constitutional Governance Dashboard**

   - Constitutional compliance scores
   - DGM safety pattern status
   - Policy validation metrics
   - Emergency shutdown status

2. **Performance Dashboard**

   - Response time percentiles
   - Throughput metrics
   - Error rates
   - Resource utilization

3. **AI Model Integration Dashboard**
   - Model response times
   - Model availability
   - Constitutional reasoning accuracy
   - API usage metrics

## Maintenance Procedures

### Planned Maintenance

#### Service Updates

```bash
# 1. Notify stakeholders
# 2. Enable maintenance mode
curl -X POST http://localhost:8000/admin/maintenance/enable

# 3. Perform rolling updates
docker-compose -f infrastructure/docker/config/docker/docker-compose.production.yml \
  up -d --no-deps auth_service

# 4. Validate service health
curl http://localhost:8000/health

# 5. Continue with other services
# 6. Disable maintenance mode
curl -X POST http://localhost:8000/admin/maintenance/disable
```

#### Database Maintenance

```bash
# 1. Create backup
docker exec acgs_postgres pg_dump -U acgs_user acgs_db > backup_$(date +%Y%m%d).sql

# 2. Run maintenance
docker exec acgs_postgres psql -U acgs_user -d acgs_db -c "VACUUM ANALYZE;"

# 3. Update statistics
docker exec acgs_postgres psql -U acgs_user -d acgs_db -c "ANALYZE;"
```

### Emergency Maintenance

#### Emergency Response Procedures

1. **Assess Situation**

   - Determine severity level
   - Identify affected services
   - Estimate impact

2. **Immediate Actions**

   - Trigger emergency shutdown if necessary
   - Isolate affected components
   - Notify stakeholders

3. **Resolution**

   - Apply emergency fixes
   - Validate constitutional compliance
   - Restore service gradually

4. **Post-Incident**
   - Conduct root cause analysis
   - Update procedures
   - Implement preventive measures

## Disaster Recovery

### Backup Strategy

- **Database**: Daily full backups, hourly incremental
- **Configuration**: Version controlled in Git
- **Logs**: Centralized logging with retention
- **Secrets**: Secure backup of encryption keys

### Recovery Procedures

1. **Infrastructure Recovery**

   - Restore from infrastructure as code
   - Deploy base services
   - Validate network connectivity

2. **Data Recovery**

   - Restore database from backup
   - Validate data integrity
   - Apply any missing transactions

3. **Service Recovery**
   - Deploy services in dependency order
   - Validate constitutional compliance
   - Perform comprehensive testing

### Recovery Time Objectives (RTO)

- **Critical Services**: 4 hours
- **Full System**: 8 hours
- **Emergency Shutdown**: 30 minutes
- **Constitutional Compliance**: 2 hours

## Disaster Recovery

### Backup Strategy

- **Database**: Daily full backups, hourly incremental
- **Configuration**: Version controlled in Git
- **Logs**: Centralized logging with retention
- **Secrets**: Secure backup of encryption keys

### Recovery Procedures

1. **Infrastructure Recovery**

   - Restore from infrastructure as code
   - Deploy base services
   - Validate network connectivity

2. **Data Recovery**

   - Restore database from backup
   - Validate data integrity
   - Apply any missing transactions

3. **Service Recovery**
   - Deploy services in dependency order
   - Validate constitutional compliance
   - Perform comprehensive testing

### Recovery Time Objectives (RTO)

- **Critical Services**: 4 hours
- **Full System**: 8 hours
- **Emergency Shutdown**: 30 minutes
- **Constitutional Compliance**: 2 hours

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)
- [ACGS Implementation Guide](ACGS_IMPLEMENTATION_GUIDE.md)
- [ACGS-PGP Troubleshooting Guide](ACGS_PGP_TROUBLESHOOTING_GUIDE.md)
- [Service Status Dashboard](../operations/SERVICE_STATUS.md)

---

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->
**Last Updated**: 2025-06-27
**Version**: 1.0.0
