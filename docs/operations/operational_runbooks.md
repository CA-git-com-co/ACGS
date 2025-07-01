# ACGS Operational Runbooks

**Version:** 3.0.0  
**Date:** July 1, 2025  
**Constitutional Hash:** cdd01ef066bc6cf2  

## Overview

This document provides detailed operational procedures for ACGS production support, including incident response, maintenance procedures, and troubleshooting guides.

## Incident Response Procedures

### Incident Classification

**P0 - Critical (Response: <15 minutes)**
- Complete system outage
- Security breach or data compromise
- Constitutional compliance system failure
- Database corruption or data loss

**P1 - High (Response: <1 hour)**
- Partial service degradation affecting >50% of users
- Performance degradation >500% of baseline
- Authentication system issues
- Critical service failures

**P2 - Medium (Response: <4 hours)**
- Single service degradation
- Performance issues affecting <50% of users
- Non-critical feature failures
- Monitoring alert failures

**P3 - Low (Response: <24 hours)**
- Minor bugs or cosmetic issues
- Documentation updates
- Enhancement requests
- Non-urgent maintenance

### Incident Response Workflow

#### 1. Incident Detection and Acknowledgment

```bash
# Check service status
./scripts/health_check_all.sh

# View recent alerts
tail -f /var/log/acgs/alerts.log

# Check system resources
htop
df -h
free -m
```

#### 2. Initial Assessment

```bash
# Service health check
curl -f http://localhost:8016/health  # Auth Service
curl -f http://localhost:8002/health  # Constitutional AI
curl -f http://localhost:8003/health  # Policy Governance
curl -f http://localhost:8004/health  # Governance Synthesis
curl -f http://localhost:8005/health  # Formal Verification
curl -f http://localhost:8010/health  # Evolutionary Computation

# Database connectivity
psql -h localhost -U acgs -d acgs_production -c "SELECT 1;"

# Redis connectivity
redis-cli ping

# Check constitutional compliance
grep "cdd01ef066bc6cf2" /var/log/acgs/*.log | tail -10
```

#### 3. Escalation Procedures

**Level 1 (0-15 minutes):** On-call engineer
**Level 2 (15-60 minutes):** Technical lead + Engineering manager
**Level 3 (60+ minutes):** CTO + Security team (if security-related)

### Common Incident Scenarios

#### Service Outage

**Symptoms:**
- Health check endpoints returning 5xx errors
- Service not responding to requests
- High error rates in logs

**Immediate Actions:**
```bash
# Check if service is running
ps aux | grep uvicorn

# Check port availability
netstat -tlnp | grep :8016

# Restart service
sudo systemctl restart acgs-auth-service

# Check logs for errors
tail -f /var/log/acgs/auth_service.log
```

**Root Cause Investigation:**
```bash
# Check system resources
top
iostat -x 1 5
vmstat 1 5

# Check disk space
df -h

# Check memory usage
free -m
cat /proc/meminfo

# Check for OOM kills
dmesg | grep -i "killed process"
```

#### Database Issues

**Symptoms:**
- Connection timeouts
- Slow query performance
- Lock contention

**Immediate Actions:**
```bash
# Check database status
sudo systemctl status postgresql

# Check active connections
psql -U acgs -d acgs_production -c "SELECT count(*) FROM pg_stat_activity;"

# Check for long-running queries
psql -U acgs -d acgs_production -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"

# Check for locks
psql -U acgs -d acgs_production -c "
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement,
       blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;"
```

#### High Latency

**Symptoms:**
- P99 latency >100ms
- Slow response times
- User complaints about performance

**Investigation Steps:**
```bash
# Check current latency
python scripts/latency_check.py

# Check database performance
psql -U acgs -d acgs_production -c "
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;"

# Check Redis performance
redis-cli --latency-history

# Check system load
uptime
cat /proc/loadavg

# Check network latency
ping -c 10 localhost
```

#### Constitutional Compliance Failure

**Symptoms:**
- Constitutional hash validation failures
- Policy enforcement errors
- Compliance rate <95%

**Immediate Actions:**
```bash
# Verify constitutional hash
grep "cdd01ef066bc6cf2" /var/log/acgs/*.log

# Check policy validation service
curl -f http://localhost:8003/health

# Validate policy files
python scripts/validate_constitutional_policies.py

# Check formal verification service
curl -f http://localhost:8005/health

# Review compliance metrics
python scripts/compliance_report.py
```

## Maintenance Procedures

### Planned Maintenance

#### Pre-Maintenance Checklist

```bash
# 1. Notify stakeholders
echo "Maintenance window starting at $(date)" | mail -s "ACGS Maintenance" stakeholders@company.com

# 2. Create backup
./scripts/backup_full_system.sh

# 3. Verify backup integrity
./scripts/verify_backup.sh

# 4. Check system health
./scripts/health_check_comprehensive.sh

# 5. Document current state
./scripts/system_state_snapshot.sh > /var/log/acgs/pre_maintenance_$(date +%Y%m%d_%H%M%S).log
```

#### Service Updates

```bash
# 1. Stop services gracefully
./scripts/stop_acgs_services.sh

# 2. Update application code
cd /home/acgs/ACGS
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Run database migrations
python scripts/migrate_database.py

# 5. Update configuration if needed
cp config/production.env.new config/production.env

# 6. Start services
./scripts/start_acgs_services.sh

# 7. Verify deployment
./scripts/health_check_all.sh
./scripts/smoke_test.sh
```

#### Database Maintenance

```bash
# Weekly maintenance
psql -U acgs -d acgs_production << EOF
-- Update table statistics
ANALYZE;

-- Reindex if needed
REINDEX DATABASE acgs_production;

-- Clean up old data (if applicable)
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days';

-- Vacuum to reclaim space
VACUUM ANALYZE;
EOF
```

### Emergency Procedures

#### Emergency Rollback

```bash
# 1. Stop current services
./scripts/stop_acgs_services.sh

# 2. Restore from backup
./scripts/restore_from_backup.sh /var/backups/acgs/latest/

# 3. Restore database
psql -U acgs -d acgs_production < /var/backups/acgs/latest/database.sql

# 4. Start services
./scripts/start_acgs_services.sh

# 5. Verify rollback
./scripts/health_check_all.sh
```

#### Security Incident Response

```bash
# 1. Isolate affected systems
sudo ufw deny from suspicious_ip

# 2. Preserve evidence
cp -r /var/log/acgs/ /var/log/acgs_incident_$(date +%Y%m%d_%H%M%S)/

# 3. Check for unauthorized access
grep -i "failed\|unauthorized\|breach" /var/log/acgs/*.log

# 4. Verify constitutional compliance
python scripts/security_audit.py

# 5. Reset credentials if compromised
python scripts/rotate_all_keys.py

# 6. Notify security team
echo "Security incident detected at $(date)" | mail -s "ACGS Security Alert" security@company.com
```

## Monitoring and Alerting

### Key Metrics to Monitor

**Service Health:**
- Service availability (target: >99.9%)
- Response time P99 (target: <5ms)
- Error rate (target: <0.1%)
- Constitutional compliance rate (target: >99%)

**System Resources:**
- CPU utilization (alert: >80%)
- Memory usage (alert: >85%)
- Disk usage (alert: >90%)
- Network throughput

**Database Metrics:**
- Connection count (alert: >80% of max)
- Query performance (alert: >100ms average)
- Lock contention
- Replication lag (if applicable)

### Alert Configuration

```bash
# CPU usage alert
if [ $(cat /proc/loadavg | cut -d' ' -f1 | cut -d'.' -f1) -gt 8 ]; then
    echo "High CPU load detected" | mail -s "ACGS CPU Alert" ops@company.com
fi

# Memory usage alert
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEMORY_USAGE -gt 85 ]; then
    echo "High memory usage: ${MEMORY_USAGE}%" | mail -s "ACGS Memory Alert" ops@company.com
fi

# Disk usage alert
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "High disk usage: ${DISK_USAGE}%" | mail -s "ACGS Disk Alert" ops@company.com
fi
```

## Backup and Recovery

### Backup Procedures

#### Daily Automated Backup

```bash
#!/bin/bash
# /home/acgs/scripts/daily_backup.sh

BACKUP_DIR="/var/backups/acgs/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U acgs acgs_production | gzip > $BACKUP_DIR/database.sql.gz

# Configuration backup
tar -czf $BACKUP_DIR/config.tar.gz /home/acgs/ACGS/config/

# Application backup
tar -czf $BACKUP_DIR/application.tar.gz /home/acgs/ACGS/ --exclude=venv --exclude=.git

# Log backup
tar -czf $BACKUP_DIR/logs.tar.gz /var/log/acgs/

# Verify backup integrity
if [ -f $BACKUP_DIR/database.sql.gz ] && [ -f $BACKUP_DIR/config.tar.gz ]; then
    echo "Backup completed successfully: $BACKUP_DIR"
else
    echo "Backup failed!" | mail -s "ACGS Backup Failure" ops@company.com
fi

# Clean up old backups (keep 30 days)
find /var/backups/acgs/ -type d -mtime +30 -exec rm -rf {} \;
```

#### Recovery Procedures

```bash
# Full system recovery
./scripts/stop_acgs_services.sh

# Restore database
gunzip -c /var/backups/acgs/20250701/database.sql.gz | psql -U acgs -d acgs_production

# Restore configuration
tar -xzf /var/backups/acgs/20250701/config.tar.gz -C /

# Restore application
tar -xzf /var/backups/acgs/20250701/application.tar.gz -C /

# Start services
./scripts/start_acgs_services.sh

# Verify recovery
./scripts/health_check_all.sh
```

## Performance Optimization

### Database Optimization

```sql
-- Identify slow queries
SELECT query, mean_time, calls, total_time, rows, 100.0 * shared_blks_hit /
       nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Analyze table bloat
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
       pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Application Optimization

```bash
# Check memory usage by service
ps aux | grep uvicorn | awk '{print $2, $4, $11}' | sort -k2 -nr

# Monitor connection pools
python scripts/connection_pool_stats.py

# Check cache hit rates
redis-cli info stats | grep keyspace_hits
```

## Security Procedures

### Regular Security Tasks

```bash
# Weekly security scan
python scripts/security_scan.py

# Check for unauthorized access
grep -i "failed login\|unauthorized" /var/log/acgs/*.log

# Verify SSL certificates
openssl x509 -in /etc/ssl/acgs/cert.pem -text -noout | grep "Not After"

# Check file permissions
find /home/acgs/ACGS -type f -perm /o+w -ls

# Audit user accounts
cut -d: -f1 /etc/passwd | sort
```

### Key Rotation

```bash
# Rotate application keys (monthly)
python scripts/rotate_application_keys.py

# Rotate database passwords (quarterly)
python scripts/rotate_database_credentials.py

# Update SSL certificates (as needed)
sudo certbot renew --nginx
```

## Contact Information

### Escalation Matrix

**Level 1 - On-call Engineer**
- Response Time: 15 minutes
- Contact: +1-555-0123
- Email: oncall@company.com

**Level 2 - Technical Lead**
- Response Time: 1 hour
- Contact: +1-555-0124
- Email: tech-lead@company.com

**Level 3 - Engineering Manager**
- Response Time: 4 hours
- Contact: +1-555-0125
- Email: eng-manager@company.com

**Security Team**
- 24/7 Hotline: +1-555-0199
- Email: security-incident@company.com

---

**Document Version:** 3.0.0  
**Last Updated:** July 1, 2025  
**Constitutional Hash:** cdd01ef066bc6cf2  
**Next Review:** August 1, 2025
