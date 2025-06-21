# ACGS-1 Operational Runbooks & Troubleshooting Guide

**Version**: 3.0.0  
**Date**: 2025-06-16  
**Status**: Production Ready

## Table of Contents

1. [Emergency Procedures](#emergency-procedures)
2. [Service Management](#service-management)
3. [Common Issues & Solutions](#common-issues--solutions)
4. [Performance Troubleshooting](#performance-troubleshooting)
5. [Constitutional Governance Issues](#constitutional-governance-issues)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Maintenance Procedures](#maintenance-procedures)
8. [Escalation Procedures](#escalation-procedures)

## Emergency Procedures

### 🚨 System-Wide Outage

**Symptoms**: All services unresponsive, health checks failing

**Immediate Actions**:

1. **Assess Scope**:

   ```bash
   python3 scripts/emergency_rollback_procedures.py health
   ```

2. **Emergency Stop All Services**:

   ```bash
   python3 scripts/emergency_rollback_procedures.py stop
   ```

3. **Create Incident Report**:

   ```bash
   python3 scripts/emergency_rollback_procedures.py incident \
     --type "system_wide_outage" \
     --description "All services unresponsive" \
     --severity "critical"
   ```

4. **Check System Resources**:

   ```bash
   htop
   df -h
   free -h
   iostat -x 1 5
   ```

5. **Restart Services**:

   ```bash
   python3 scripts/emergency_rollback_procedures.py restart
   ```

6. **Verify Recovery**:
   ```bash
   python3 scripts/comprehensive_health_check.py
   ```

### 🔥 Constitutional Compliance Failure

**Symptoms**: Constitution hash validation failing, PGC service errors

**Immediate Actions**:

1. **Verify Constitution Hash**:

   ```bash
   curl -s http://localhost:8005/api/v1/constitutional/validate | grep "cdd01ef066bc6cf2"
   ```

2. **Check PGC Service Status**:

   ```bash
   curl -s http://localhost:8005/health
   ```

3. **Validate Blockchain Connectivity**:

   ```bash
   # Check Quantumagi deployment status
   cd blockchain && anchor test --skip-build
   ```

4. **Restart Governance Services**:
   ```bash
   pkill -f 'uvicorn.*:8005'
   cd services/core/policy-governance/pgc_service
   uvicorn app.main:app --host 0.0.0.0 --port 8005 &
   ```

## Service Management

### Starting Services

**Individual Service Start**:

```bash
# Auth Service
cd services/core/auth/auth_service
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# PGC Service
cd services/core/policy-governance/pgc_service
uvicorn app.main:app --host 0.0.0.0 --port 8005 &
```

**All Services Start**:

```bash
bash scripts/start_missing_services.sh
```

### Stopping Services

**Individual Service Stop**:

```bash
# Stop specific service by port
pkill -f 'uvicorn.*:8005'  # PGC Service
```

**All Services Stop**:

```bash
python3 scripts/emergency_rollback_procedures.py stop
```

### Service Health Checks

**Quick Health Check**:

```bash
python3 scripts/emergency_rollback_procedures.py health
```

**Comprehensive Health Check**:

```bash
python3 scripts/comprehensive_health_check.py
```

**Individual Service Health**:

```bash
curl -s http://localhost:8005/health | jq
```

## Common Issues & Solutions

### Issue: Service Won't Start

**Symptoms**: Service fails to start, port binding errors

**Diagnosis**:

```bash
# Check if port is in use
netstat -tulpn | grep :8005

# Check service logs
tail -f logs/pgc_service.log

# Check system resources
free -h
df -h
```

**Solutions**:

1. **Kill existing process**:

   ```bash
   pkill -f 'uvicorn.*:8005'
   fuser -k 8005/tcp
   ```

2. **Check dependencies**:

   ```bash
   # Verify database connection
   pg_isready -h localhost -p 5432

   # Verify Redis connection
   redis-cli ping
   ```

3. **Restart with debug logging**:
   ```bash
   cd services/core/policy-governance/pgc_service
   uvicorn app.main:app --host 0.0.0.0 --port 8005 --log-level debug
   ```

### Issue: Database Connection Errors

**Symptoms**: "Connection refused", "Database unavailable"

**Diagnosis**:

```bash
# Check PostgreSQL status
sudo systemctl status postgresql
pg_isready -h localhost -p 5432

# Check connections
psql -h localhost -p 5432 -U acgs_user -d acgs_pgp_db -c "SELECT 1;"
```

**Solutions**:

1. **Restart PostgreSQL**:

   ```bash
   sudo systemctl restart postgresql
   ```

2. **Check connection limits**:

   ```sql
   SELECT count(*) FROM pg_stat_activity;
   SHOW max_connections;
   ```

3. **Reset connections**:
   ```sql
   SELECT pg_terminate_backend(pid) FROM pg_stat_activity
   WHERE datname = 'acgs_pgp_db' AND pid <> pg_backend_pid();
   ```

### Issue: High Memory Usage

**Symptoms**: Services crashing, OOM errors

**Diagnosis**:

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -20

# Check service memory usage
ps aux | grep uvicorn
```

**Solutions**:

1. **Restart memory-intensive services**:

   ```bash
   # Restart GS service (typically highest memory usage)
   pkill -f 'uvicorn.*:8004'
   cd services/core/governance-synthesis/gs_service
   uvicorn app.main:app --host 0.0.0.0 --port 8004 &
   ```

2. **Clear Redis cache**:

   ```bash
   redis-cli FLUSHALL
   ```

3. **Optimize service configuration**:
   ```bash
   # Reduce worker processes in production
   export WORKERS=1
   ```

### Issue: Slow Response Times

**Symptoms**: API timeouts, >500ms response times

**Diagnosis**:

```bash
# Check service response times
time curl -s http://localhost:8005/health

# Check database performance
psql -h localhost -p 5432 -U acgs_user -d acgs_pgp_db -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;"

# Check Redis performance
redis-cli --latency-history
```

**Solutions**:

1. **Restart slow services**:

   ```bash
   python3 scripts/emergency_rollback_procedures.py restart
   ```

2. **Clear caches**:

   ```bash
   redis-cli FLUSHALL
   ```

3. **Check resource utilization**:
   ```bash
   iostat -x 1 5
   top -p $(pgrep -d',' uvicorn)
   ```

## Performance Troubleshooting

### Database Performance

**Slow Queries**:

```sql
-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;

-- Check active queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

**Index Optimization**:

```sql
-- Check missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Analyze table statistics
ANALYZE;
```

### Redis Performance

**Memory Usage**:

```bash
# Check Redis memory usage
redis-cli INFO memory

# Check key distribution
redis-cli --bigkeys

# Monitor commands
redis-cli MONITOR
```

**Cache Hit Rates**:

```bash
# Check cache statistics
redis-cli INFO stats | grep hit
```

### Service Performance

**Response Time Monitoring**:

```bash
# Monitor service response times
while true; do
  echo "$(date): $(time curl -s http://localhost:8005/health > /dev/null)"
  sleep 5
done
```

**Resource Monitoring**:

```bash
# Monitor service resources
watch -n 1 'ps aux | grep uvicorn | grep -v grep'
```

## Constitutional Governance Issues

### Constitution Hash Validation Failures

**Symptoms**: Constitutional validation returning false, hash mismatches

**Diagnosis**:

```bash
# Check current constitution hash
curl -s http://localhost:8005/api/v1/constitutional/validate | jq '.constitutional_hash'

# Verify expected hash
echo "Expected: cdd01ef066bc6cf2"

# Check blockchain state
cd blockchain && anchor test --skip-build
```

**Solutions**:

1. **Verify blockchain connectivity**:

   ```bash
   solana config get
   solana balance
   ```

2. **Restart PGC service**:

   ```bash
   pkill -f 'uvicorn.*:8005'
   cd services/core/policy-governance/pgc_service
   uvicorn app.main:app --host 0.0.0.0 --port 8005 &
   ```

3. **Check constitution program**:
   ```bash
   cd blockchain
   anchor test tests/constitution.ts
   ```

### Policy Synthesis Failures

**Symptoms**: GS service errors, policy generation timeouts

**Diagnosis**:

```bash
# Check GS service health
curl -s http://localhost:8004/health

# Check model availability
curl -s http://localhost:8004/api/v1/models/status

# Check service logs
tail -f logs/gs_service.log
```

**Solutions**:

1. **Restart GS service**:

   ```bash
   pkill -f 'uvicorn.*:8004'
   cd services/core/governance-synthesis/gs_service
   uvicorn app.main:app --host 0.0.0.0 --port 8004 &
   ```

2. **Clear model cache**:

   ```bash
   redis-cli DEL "model:*"
   ```

3. **Check model endpoints**:
   ```bash
   # Test model connectivity
   curl -s "https://api.groq.com/openai/v1/models" -H "Authorization: Bearer $GROQ_API_KEY"
   ```

## Monitoring & Alerting

### Prometheus Metrics

**Key Metrics to Monitor**:

- `acgs_service_response_time_seconds`
- `acgs_constitutional_compliance_score`
- `acgs_governance_workflow_completion_rate`
- `acgs_service_error_rate`

**Prometheus Queries**:

```promql
# Average response time by service
avg(rate(acgs_service_response_time_seconds_sum[5m])) by (service)

# Error rate by service
rate(acgs_service_errors_total[5m])

# Constitutional compliance score
acgs_constitutional_compliance_score
```

### Grafana Dashboards

**Access**: http://localhost:3000
**Default Login**: admin/admin

**Key Dashboards**:

- ACGS System Overview
- Service Performance
- Constitutional Governance
- Infrastructure Metrics

### Log Analysis

**Service Logs Location**: `/home/dislove/ACGS-1/logs/`

**Common Log Patterns**:

```bash
# Error patterns
grep -i "error\|exception\|failed" logs/*.log

# Constitutional validation logs
grep "constitutional" logs/pgc_service.log

# Performance issues
grep "timeout\|slow" logs/*.log
```

## Maintenance Procedures

### Daily Maintenance

**Health Check**:

```bash
# Run automated health check
python3 scripts/automated_health_check.sh
```

**Backup Verification**:

```bash
# Check recent backups
python3 scripts/simple_backup_recovery.py list

# Monitor backup health
bash scripts/monitor_backups.sh
```

### Weekly Maintenance

**Log Rotation**:

```bash
# Compress old logs
find logs/ -name "*.log" -size +100M -exec gzip {} \;
```

**Backup Cleanup**:

```bash
# Clean old backups
bash scripts/cleanup_old_backups.sh
```

**Performance Review**:

```bash
# Generate performance report
python3 scripts/comprehensive_health_check.py > reports/weekly_health_$(date +%Y%m%d).json
```

### Monthly Maintenance

**Disaster Recovery Test**:

```bash
# Run DR test
bash scripts/test_disaster_recovery.sh
```

**Security Review**:

```bash
# Check for security updates
apt list --upgradable | grep -i security

# Review access logs
grep "401\|403" logs/auth_service.log
```

## Escalation Procedures

### Severity Levels

**Critical (P1)**:

- System-wide outage
- Constitutional compliance failure
- Data corruption
- Security breach

**High (P2)**:

- Single service failure
- Performance degradation >50%
- Governance workflow failures

**Medium (P3)**:

- Minor service issues
- Performance degradation <50%
- Non-critical feature failures

**Low (P4)**:

- Documentation issues
- Enhancement requests
- Minor bugs

### Contact Information

**Primary On-Call**: ACGS-1 Operations Team
**Secondary**: Infrastructure Team  
**Escalation**: System Architecture Team

### Escalation Matrix

| Severity | Initial Response | Escalation Time | Contact             |
| -------- | ---------------- | --------------- | ------------------- |
| P1       | Immediate        | 15 minutes      | All teams           |
| P2       | 15 minutes       | 1 hour          | Primary + Secondary |
| P3       | 1 hour           | 4 hours         | Primary             |
| P4       | 4 hours          | 24 hours        | Primary             |

---

**Document Maintained By**: ACGS-1 Operations Team  
**Last Updated**: 2025-06-16  
**Next Review**: 2025-07-16
