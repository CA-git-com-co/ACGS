# ACGS-PGP MLOps Operational Handover Guide

## Overview

This document provides comprehensive operational guidance for the ACGS-PGP MLOps system. It covers system architecture, monitoring procedures, troubleshooting guides, maintenance schedules, and emergency procedures for operations teams.

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**System Version**: Production v1.0  
**Last Updated**: 2025-06-27

## System Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACGS-PGP Production System                   │
├─────────────────────────────────────────────────────────────────┤
│  Core ACGS Services                                             │
│  ├── Authentication Service (port 8000)                        │
│  ├── Constitutional AI Service (port 8001)                     │
│  ├── Integrity Service (port 8002)                             │
│  ├── Feature Validation Service (port 8003)                    │
│  ├── Governance Service (port 8004)                            │
│  ├── Policy Generation Service (port 8005)                     │
│  └── Evolution Control Service (port 8006)                     │
├─────────────────────────────────────────────────────────────────┤
│  MLOps System (NEW)                                            │
│  ├── MLOps Manager (orchestration)                             │
│  ├── Model Versioning Service                                  │
│  ├── Git Integration Service                                   │
│  ├── Artifact Storage Service                                  │
│  ├── Deployment Pipeline Service                               │
│  ├── Monitoring Dashboard                                      │
│  └── Production Integration Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Data & Storage Layer                                          │
│  ├── PostgreSQL Database (primary)                             │
│  ├── Redis Cache Cluster                                       │
│  ├── Artifact Storage (S3/MinIO)                              │
│  └── Monitoring Database (InfluxDB)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Key Performance Targets

| Metric                    | Target  | Current Performance |
| ------------------------- | ------- | ------------------- |
| Response Time             | <2000ms | ~450ms              |
| Constitutional Compliance | >95%    | ~97%                |
| Cost Savings              | >74%    | ~76%                |
| Model Accuracy            | >90%    | ~92%                |
| System Availability       | >99.9%  | ~99.95%             |

## Daily Operations

### Morning Health Check (9:00 AM)

```bash
# Run daily health check
./scripts/daily_mlops_health_check.sh

# Expected output:
# ✅ All services operational
# ✅ Constitutional compliance: 97%
# ✅ Performance targets met
# ✅ No critical alerts
```

### Key Metrics to Monitor

1. **System Health**

   - Service availability (all services should be "Running")
   - Response times (<2000ms)
   - Error rates (<1%)
   - Resource utilization (CPU <80%, Memory <85%)

2. **Constitutional Compliance**

   - Compliance score (>95%)
   - Hash integrity verification
   - DGM safety pattern status
   - Audit trail completeness

3. **Business Metrics**
   - Model accuracy trends
   - Cost efficiency
   - User satisfaction scores
   - Prediction quality metrics

### Daily Monitoring Commands

```bash
# Check service status
kubectl get pods -n acgs-production

# Check resource usage
kubectl top nodes
kubectl top pods -n acgs-production

# Check constitutional compliance
./scripts/run_constitutional_compliance_validation.py --quick

# Check performance metrics
./scripts/monitor_mlops_performance.sh --daily

# Review alerts
tail -f /var/log/acgs/alerts_$(date +%Y%m%d).log
```

## Weekly Operations

### Weekly Performance Review (Mondays 10:00 AM)

```bash
# Generate weekly performance report
./scripts/weekly_mlops_report.sh

# Analyze model performance trends
./scripts/analyze_model_performance.sh --weekly

# Review and clean up old artifacts
./scripts/cleanup_old_artifacts.sh --retention-days 90

# Update performance baselines if needed
./scripts/update_performance_baselines.sh
```

### Weekly Maintenance Tasks

1. **Artifact Cleanup**

   - Remove artifacts older than 90 days
   - Verify backup integrity
   - Update retention policies if needed

2. **Performance Analysis**

   - Review response time trends
   - Analyze constitutional compliance patterns
   - Check for performance degradation

3. **Security Review**
   - Review access logs
   - Check for security alerts
   - Verify certificate expiration dates

## Monitoring and Alerting

### Alert Levels

| Level         | Response Time      | Description                                |
| ------------- | ------------------ | ------------------------------------------ |
| **INFO**      | No action required | Normal operational events                  |
| **WARNING**   | 30 minutes         | Performance degradation, investigate       |
| **CRITICAL**  | 15 minutes         | Service failure, immediate action required |
| **EMERGENCY** | 5 minutes          | System-wide failure, all hands on deck     |

### Key Alerts to Watch

1. **Critical Alerts**

   - Service down (any core service)
   - Constitutional compliance <90%
   - Response time >2500ms
   - Error rate >2%
   - Database connection failures

2. **Warning Alerts**
   - Response time >1500ms
   - Constitutional compliance <93%
   - High resource usage (CPU >80%, Memory >85%)
   - Model accuracy degradation

### Alert Response Procedures

#### Service Down Alert

```bash
# 1. Check service status
kubectl get pods -n acgs-production | grep <service-name>

# 2. Check service logs
kubectl logs deployment/<service-name> -n acgs-production --tail=100

# 3. Restart service if needed
kubectl rollout restart deployment/<service-name> -n acgs-production

# 4. Verify service recovery
kubectl rollout status deployment/<service-name> -n acgs-production

# 5. Run health check
./scripts/verify_service_health.sh <service-name>
```

#### Constitutional Compliance Alert

```bash
# 1. Run immediate compliance check
./scripts/run_constitutional_compliance_validation.py --emergency

# 2. Check constitutional hash integrity
./scripts/verify_constitutional_hash.sh

# 3. Review compliance logs
tail -f /var/log/acgs/compliance_$(date +%Y%m%d).log

# 4. If hash integrity compromised, initiate emergency procedures
./scripts/emergency_compliance_recovery.sh
```

#### Performance Degradation Alert

```bash
# 1. Check current performance metrics
./scripts/check_current_performance.sh

# 2. Identify bottlenecks
./scripts/identify_performance_bottlenecks.sh

# 3. Check resource usage
kubectl top nodes
kubectl top pods -n acgs-production

# 4. Scale services if needed
kubectl scale deployment/<service-name> --replicas=<new-count> -n acgs-production
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. High Response Times

**Symptoms**: Response times >1500ms consistently

**Investigation Steps**:

```bash
# Check database performance
./scripts/check_database_performance.sh

# Check cache hit rates
./scripts/check_cache_performance.sh

# Check network latency
./scripts/check_network_latency.sh

# Check service resource usage
kubectl top pods -n acgs-production
```

**Common Solutions**:

- Scale up services: `kubectl scale deployment/<service> --replicas=<count>`
- Clear cache: `./scripts/clear_redis_cache.sh`
- Restart database connections: `./scripts/restart_db_connections.sh`

#### 2. Constitutional Compliance Violations

**Symptoms**: Compliance score <95%

**Investigation Steps**:

```bash
# Check hash integrity
./scripts/verify_constitutional_hash.sh

# Review compliance logs
grep "compliance_violation" /var/log/acgs/compliance_*.log

# Check DGM safety patterns
./scripts/check_dgm_safety_patterns.sh
```

**Common Solutions**:

- Verify hash integrity across all components
- Restart constitutional AI service
- Review and update compliance policies

#### 3. Model Performance Degradation

**Symptoms**: Model accuracy <90%

**Investigation Steps**:

```bash
# Check model version status
./scripts/check_model_versions.sh

# Analyze recent predictions
./scripts/analyze_recent_predictions.sh

# Check training data quality
./scripts/check_training_data_quality.sh
```

**Common Solutions**:

- Retrain model with recent data
- Rollback to previous model version
- Update feature engineering pipeline

### Emergency Procedures

#### Emergency Shutdown

```bash
# If system must be shut down immediately
./scripts/emergency_shutdown.sh

# This will:
# 1. Stop all traffic routing
# 2. Gracefully shutdown services
# 3. Backup critical data
# 4. Notify stakeholders
```

#### Emergency Rollback

```bash
# If deployment needs immediate rollback
./scripts/emergency_rollback.sh

# This will:
# 1. Revert to previous stable version
# 2. Restore previous configurations
# 3. Verify system stability
# 4. Generate rollback report
```

#### Constitutional Compliance Emergency

```bash
# If constitutional compliance is compromised
./scripts/emergency_compliance_recovery.sh

# This will:
# 1. Immediately halt non-compliant operations
# 2. Verify hash integrity
# 3. Restore compliant configurations
# 4. Generate compliance incident report
```

## Backup and Recovery

### Backup Schedule

| Component      | Frequency | Retention | Location                  |
| -------------- | --------- | --------- | ------------------------- |
| Database       | Daily     | 30 days   | `/opt/backups/db/`        |
| Artifacts      | Daily     | 90 days   | `/opt/backups/artifacts/` |
| Configurations | Weekly    | 12 weeks  | `/opt/backups/config/`    |
| Logs           | Daily     | 7 days    | `/opt/backups/logs/`      |

### Backup Commands

```bash
# Manual database backup
./scripts/backup_database.sh

# Manual artifact backup
./scripts/backup_artifacts.sh

# Manual configuration backup
./scripts/backup_configurations.sh

# Verify backup integrity
./scripts/verify_backup_integrity.sh
```

### Recovery Procedures

#### Database Recovery

```bash
# Restore from latest backup
./scripts/restore_database.sh --backup-date YYYY-MM-DD

# Verify database integrity
./scripts/verify_database_integrity.sh

# Restart dependent services
./scripts/restart_dependent_services.sh
```

#### Service Recovery

```bash
# Restore service configuration
./scripts/restore_service_config.sh <service-name>

# Restart service
kubectl rollout restart deployment/<service-name> -n acgs-production

# Verify service health
./scripts/verify_service_health.sh <service-name>
```

## Maintenance Schedules

### Monthly Maintenance (First Saturday of each month, 2:00 AM)

1. **System Updates**

   - Apply security patches
   - Update dependencies
   - Review and update configurations

2. **Performance Optimization**

   - Analyze performance trends
   - Optimize database queries
   - Update caching strategies

3. **Security Review**
   - Review access controls
   - Update certificates
   - Audit user permissions

### Quarterly Maintenance (First Saturday of quarter, 2:00 AM)

1. **Major Updates**

   - Kubernetes cluster updates
   - Database version updates
   - Major dependency updates

2. **Capacity Planning**

   - Review resource usage trends
   - Plan for capacity expansion
   - Update resource limits

3. **Disaster Recovery Testing**
   - Test backup and recovery procedures
   - Validate emergency procedures
   - Update disaster recovery plans

## Contact Information

### Primary Contacts

| Role                                  | Name   | Phone   | Email   | Escalation        |
| ------------------------------------- | ------ | ------- | ------- | ----------------- |
| **Operations Lead**                   | [Name] | [Phone] | [Email] | Primary           |
| **MLOps Engineer**                    | [Name] | [Phone] | [Email] | Technical         |
| **Database Admin**                    | [Name] | [Phone] | [Email] | Database Issues   |
| **Security Officer**                  | [Name] | [Phone] | [Email] | Security Issues   |
| **Constitutional Compliance Officer** | [Name] | [Phone] | [Email] | Compliance Issues |

### Escalation Matrix

| Severity          | Response Time | Escalation Path                       |
| ----------------- | ------------- | ------------------------------------- |
| **P1 (Critical)** | 15 minutes    | Operations Lead → CTO → CEO           |
| **P2 (High)**     | 1 hour        | Operations Lead → Engineering Manager |
| **P3 (Medium)**   | 4 hours       | Assigned Engineer → Operations Lead   |
| **P4 (Low)**      | 24 hours      | Assigned Engineer                     |

### Emergency Contacts

- **24/7 Operations Hotline**: [Phone Number]
- **Security Emergency**: [Phone Number]
- **Constitutional Compliance Emergency**: [Phone Number]

## Documentation and Resources

### Key Documentation

- [System Architecture Documentation](./SYSTEM_ARCHITECTURE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Security Procedures](./SECURITY_PROCEDURES.md)
- [Disaster Recovery Plan](./DISASTER_RECOVERY_PLAN.md)
- [Constitutional Compliance Guide](./CONSTITUTIONAL_COMPLIANCE_GUIDE.md)

### Useful Commands Reference

```bash
# Quick system status
kubectl get pods -n acgs-production

# Check all services health
./scripts/check_all_services_health.sh

# View recent alerts
tail -f /var/log/acgs/alerts_$(date +%Y%m%d).log

# Constitutional compliance check
./scripts/run_constitutional_compliance_validation.py --quick

# Performance metrics
./scripts/get_current_performance_metrics.sh

# Emergency procedures
./scripts/emergency_procedures.sh --help
```

### Log Locations

- **Application Logs**: `/var/log/acgs/`
- **System Logs**: `/var/log/syslog`
- **Kubernetes Logs**: `kubectl logs <pod-name> -n acgs-production`
- **Database Logs**: `/var/log/postgresql/`
- **Web Server Logs**: `/var/log/nginx/`

---

**Document Version**: 1.0  
**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Last Updated**: 2025-06-27  
**Next Review**: 2025-07-27  
**Approved By**: Operations Team Lead
