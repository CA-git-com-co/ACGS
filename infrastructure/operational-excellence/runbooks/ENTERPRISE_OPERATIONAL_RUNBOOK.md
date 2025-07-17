# ACGS Enterprise Operational Runbook
**Constitutional Hash: cdd01ef066bc6cf2**


## Overview

This runbook provides comprehensive operational procedures for the ACGS (Autonomous Code Generation System) platform, designed to achieve and maintain 98+/100 production readiness score with enterprise-grade operational excellence.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Service Management](#service-management)
3. [Monitoring and Alerting](#monitoring-and-alerting)
4. [Deployment Procedures](#deployment-procedures)
5. [Disaster Recovery](#disaster-recovery)
6. [Security Operations](#security-operations)
7. [Performance Management](#performance-management)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Emergency Procedures](#emergency-procedures)
10. [Maintenance Procedures](#maintenance-procedures)

## System Architecture

### Core Services

| Service | Port | Purpose | Criticality | Dependencies |
|---------|------|---------|-------------|--------------|
| auth-service | 8000 | Authentication & Authorization | Critical | PostgreSQL, Redis |
| ac-service | 8001 | Constitutional Compliance | Critical | PostgreSQL, OPA |
| integrity-service | 8002 | Data Integrity Validation | Critical | PostgreSQL |
| fv-service | 8003 | Formal Verification | Medium | PostgreSQL |
| gs-service | 8004 | Governance System | Medium | PostgreSQL, NATS |
| pgc-service | 8005 | Policy Generation & Compliance | Medium | PostgreSQL, Redis |
| ec-service | 8006 | Evolutionary Computation | Critical | PostgreSQL, Redis |

### Infrastructure Components

- **Database**: PostgreSQL 15+ with read replicas
- **Cache**: Redis 7+ cluster
- **Message Broker**: NATS Streaming
- **Load Balancer**: HAProxy with SSL termination
- **Monitoring**: Prometheus + Grafana + AlertManager
- **Service Mesh**: Istio (optional)
- **Container Runtime**: Docker 24.0+
- **Orchestration**: Kubernetes 1.24+

## Service Management

### Starting Services

#### Development Environment
```bash
# Start all services with Docker Compose
cd /home/ubuntu/ACGS
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Verify services are running
./scripts/comprehensive_health_check.sh
```

#### Production Environment
```bash
# Deploy using enterprise pipeline
python3 infrastructure/operational-excellence/scripts/enterprise_deployment_pipeline.py

# Verify deployment
kubectl get pods -n acgs-production
kubectl get services -n acgs-production
```

### Stopping Services

#### Graceful Shutdown
```bash
# Graceful shutdown with 30-second timeout
./scripts/emergency_shutdown_all_services.sh graceful

# Verify all services stopped
docker ps | grep acgs
```

#### Emergency Shutdown
```bash
# Immediate shutdown (< 30 seconds)
./scripts/emergency_shutdown_all_services.sh emergency
```

### Service Health Checks

#### Manual Health Check
```bash
# Check all services
for port in 8000 8001 8002 8003 8004 8005 8006; do
  echo "Port $port: $(curl -s http://localhost:$port/health | jq -r '.status // "ERROR"')"
done

# Constitutional compliance verification
curl -s http://localhost:8001/api/v1/compliance/status | jq '.data.constitutional_hash'
# Expected: "cdd01ef066bc6cf2"
```

#### Automated Health Monitoring
```bash
# Start enterprise monitoring system
python3 infrastructure/operational-excellence/scripts/enterprise_monitoring_system.py &

# View metrics
curl http://localhost:8080/metrics
```

## Monitoring and Alerting

### Key Metrics

#### SLA Targets
- **Uptime**: >99.9%
- **Response Time P95**: <500ms
- **Error Rate**: <1%
- **Constitutional Compliance**: 100%

#### Critical Alerts
1. **Service Down**: Any critical service unavailable
2. **Response Time SLA Breach**: P95 > 500ms
3. **Error Rate SLA Breach**: Error rate > 1%
4. **Constitutional Compliance Violation**: Hash mismatch
5. **Database Connection Failure**: PostgreSQL/Redis unavailable

### Alert Escalation

#### Level 1 (0-15 minutes)
- **Contacts**: ops-team@acgs.local
- **Response**: Automated remediation + notification
- **Actions**: Service restart, cache clear, connection reset

#### Level 2 (15-30 minutes)
- **Contacts**: senior-ops@acgs.local, engineering-lead@acgs.local
- **Response**: Manual investigation required
- **Actions**: Deep dive analysis, manual intervention

#### Level 3 (30+ minutes)
- **Contacts**: cto@acgs.local, emergency-response@acgs.local
- **Response**: Executive escalation
- **Actions**: Disaster recovery, external support

### Monitoring Dashboards

#### Grafana Dashboards
- **System Overview**: http://localhost:3000/d/acgs-overview
- **Service Health**: http://localhost:3000/d/acgs-services
- **SLA Compliance**: http://localhost:3000/d/acgs-sla
- **Constitutional Compliance**: http://localhost:3000/d/acgs-constitutional

#### Prometheus Queries
```promql
# Service availability
acgs_service_up

# Response time P95
histogram_quantile(0.95, acgs_response_time_seconds_bucket)

# Error rate
rate(acgs_errors_total[5m]) / rate(acgs_requests_total[5m]) * 100

# Constitutional compliance
acgs_constitutional_compliance
```

## Deployment Procedures

### Blue-Green Deployment

#### Pre-Deployment Checklist
- [ ] All tests passing in CI/CD
- [ ] Security scan completed
- [ ] Performance benchmarks validated
- [ ] Constitutional compliance verified
- [ ] Database migrations tested
- [ ] Rollback plan prepared

#### Deployment Steps
```bash
# 1. Execute enterprise deployment pipeline
python3 infrastructure/operational-excellence/scripts/enterprise_deployment_pipeline.py \
  --version v1.2.3 \
  --environment production

# 2. Monitor deployment progress
tail -f /tmp/deployment_results/deploy-*.json

# 3. Validate deployment
./scripts/validate_production_deployment.sh

# 4. Switch traffic (automated in pipeline)
# Traffic gradually switched from blue to green environment
```

#### Rollback Procedure
```bash
# Automated rollback (triggered by pipeline on failure)
# Manual rollback if needed:
python3 infrastructure/operational-excellence/scripts/enterprise_deployment_pipeline.py \
  --rollback \
  --deployment-id deploy-1234567890
```

### Canary Deployment

#### Configuration
- **Initial Traffic**: 10%
- **Increment**: 25%
- **Interval**: 5 minutes
- **Success Threshold**: 95%

#### Monitoring During Canary
```bash
# Monitor canary metrics
kubectl get canary acgs-canary -n acgs-production

# Check error rates
curl "http://prometheus:9090/api/v1/query?query=rate(acgs_errors_total[5m])"
```

## Disaster Recovery

### Backup Procedures

#### Automated Backup
```bash
# Execute comprehensive backup
python3 infrastructure/operational-excellence/scripts/disaster_recovery_automation.py backup

# Verify backup integrity
ls -la /backups/
cat /tmp/backup_metadata/backup-*.json
```

#### Manual Backup
```bash
# Database backup
./scripts/backup_database_comprehensive.sh

# Configuration backup
tar -czf /backups/config_$(date +%Y%m%d_%H%M%S).tar.gz config/

# Application data backup
tar -czf /backups/app_data_$(date +%Y%m%d_%H%M%S).tar.gz logs/ data/
```

### Recovery Procedures

#### Full System Recovery
```bash
# Execute disaster recovery
python3 infrastructure/operational-excellence/scripts/disaster_recovery_automation.py recover \
  --backup-id backup-1234567890 \
  --recovery-type full

# Monitor recovery progress
tail -f /tmp/recovery_results/recovery-*.json
```

#### Partial Recovery
```bash
# Database only
./scripts/restore_database.sh backup-1234567890

# Configuration only
tar -xzf /backups/config_20240101_120000.tar.gz -C /
```

### RTO/RPO Targets
- **RTO (Recovery Time Objective)**: 30 minutes
- **RPO (Recovery Point Objective)**: 5 minutes

## Security Operations

### Security Monitoring

#### Vulnerability Scanning
```bash
# Daily automated scan
./scripts/comprehensive_security_scan.py

# Manual security assessment
./scripts/quick_security_assessment.py
```

#### Constitutional Compliance
```bash
# Verify constitutional hash
curl -s http://localhost:8001/api/v1/compliance/status | jq '.data.constitutional_hash'

# Expected: "cdd01ef066bc6cf2"
# If mismatch detected, investigate immediately
```

#### Security Incident Response
```bash
# Activate security incident response
./scripts/security_incident_response.sh

# Isolate affected services
kubectl scale deployment suspicious-service --replicas=0

# Collect forensic data
./scripts/collect_security_forensics.sh
```

## Performance Management

### Performance Monitoring

#### Key Performance Indicators
- **Response Time P95**: <500ms
- **Throughput**: >1000 RPS
- **CPU Utilization**: <70%
- **Memory Utilization**: <80%
- **Database Connection Pool**: <80% utilization

#### Performance Testing
```bash
# Load testing
./scripts/comprehensive_load_test.py

# Performance benchmarking
./scripts/run_performance_validation.py

# Stress testing
./scripts/phase3_load_testing.py
```

### Performance Optimization

#### Database Optimization
```bash
# Analyze slow queries
./scripts/database_performance_analysis.py

# Optimize database configuration
./scripts/database_performance_optimization.py
```

#### Cache Optimization
```bash
# Redis cache analysis
./scripts/cache_monitor.py

# Cache performance enhancement
./scripts/enhance_cache_performance.py
```

## Troubleshooting Guide

### Common Issues

#### Service Won't Start
1. Check logs: `docker logs <container_name>`
2. Verify dependencies: Database, Redis connectivity
3. Check resource limits: CPU, memory, disk space
4. Validate configuration: Environment variables, secrets

#### High Response Times
1. Check database performance: Slow queries, connection pool
2. Analyze cache hit rates: Redis performance
3. Monitor resource utilization: CPU, memory, I/O
4. Review load balancer configuration

#### Constitutional Compliance Failures
1. Verify hash: Expected "cdd01ef066bc6cf2"
2. Check AC service logs: `/var/log/acgs/ac-service.log`
3. Validate OPA policies: `curl http://localhost:8181/v1/policies`
4. Restart AC service if needed

### Log Analysis

#### Log Locations
- **Application Logs**: `/var/log/acgs/`
- **System Logs**: `/var/log/syslog`
- **Container Logs**: `docker logs <container>`
- **Kubernetes Logs**: `kubectl logs <pod>`

#### Log Analysis Commands
```bash
# Search for errors
grep -i error /var/log/acgs/*.log

# Monitor real-time logs
tail -f /var/log/acgs/ac-service.log

# Analyze performance issues
grep "slow query" /var/log/acgs/database.log
```

## Emergency Procedures

### Emergency Contacts

#### Primary On-Call
- **Phone**: +1-555-0123
- **Email**: oncall@acgs.local
- **Slack**: #acgs-emergency

#### Secondary Escalation
- **Engineering Lead**: engineering-lead@acgs.local
- **CTO**: cto@acgs.local
- **Emergency Response**: emergency-response@acgs.local

### Emergency Response

#### Severity 1 (Critical)
- **Definition**: System down, data loss, security breach
- **Response Time**: 15 minutes
- **Actions**: Immediate escalation, emergency procedures

#### Severity 2 (High)
- **Definition**: Degraded performance, partial outage
- **Response Time**: 30 minutes
- **Actions**: Investigation, remediation planning

#### Severity 3 (Medium)
- **Definition**: Minor issues, non-critical alerts
- **Response Time**: 2 hours
- **Actions**: Standard troubleshooting

### Emergency Shutdown
```bash
# Emergency shutdown (< 30 seconds)
./scripts/emergency-response.sh shutdown

# Emergency restart
./scripts/emergency-response.sh restart

# Emergency rollback
./scripts/emergency_rollback_procedures.py
```

## Maintenance Procedures

### Scheduled Maintenance

#### Weekly Maintenance (Sundays 2:00-4:00 UTC)
- [ ] Security updates
- [ ] Database maintenance
- [ ] Log rotation
- [ ] Backup verification
- [ ] Performance optimization

#### Monthly Maintenance
- [ ] Dependency updates
- [ ] Security audit
- [ ] Disaster recovery testing
- [ ] Documentation updates
- [ ] Capacity planning review

### Maintenance Commands
```bash
# Start maintenance mode
./scripts/maintenance/start_maintenance_mode.sh

# Apply updates
./scripts/maintenance/apply_updates.sh

# End maintenance mode
./scripts/maintenance/end_maintenance_mode.sh
```

---

## Appendix

### Useful Commands Reference

```bash
# Health checks
./scripts/comprehensive_health_check.sh

# Performance validation
./scripts/run_performance_validation.py

# Security scan
./scripts/comprehensive_security_scan.py

# Backup
python3 infrastructure/operational-excellence/scripts/disaster_recovery_automation.py backup

# Deployment
python3 infrastructure/operational-excellence/scripts/enterprise_deployment_pipeline.py

# Monitoring
python3 infrastructure/operational-excellence/scripts/enterprise_monitoring_system.py
```

### Configuration Files

- **Operational Config**: `infrastructure/operational-excellence/config/operational-config.yaml`
- **Docker Compose**: `infrastructure/docker/docker-compose.yml`
- **Kubernetes Manifests**: `infrastructure/kubernetes/`
- **Monitoring Config**: `infrastructure/monitoring/`

### Documentation Links

- **Technical Overview**: `docs/ACGS-1-LITE-TECHNICAL-OVERVIEW.md`
- **Deployment Guide**: `ACGS_GITOPS_DEPLOYMENT_GUIDE.md`
- **Security Guide**: `infrastructure/monitoring/SECURITY_GUIDE.md`
- **Performance Guide**: `infrastructure/monitoring/PERFORMANCE_VALIDATION_GUIDE.md`



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

**Document Version**: 1.0  
**Last Updated**: 2024-01-01  
**Next Review**: 2024-02-01  
**Owner**: ACGS Operations Team
