# Database Issues Runbook - ACGS-1 Constitutional Governance System

## Alert: DatabaseConnectionIssues / ACGSPostgreSQLDown

**Severity:** Critical  
**Component:** Database Infrastructure  
**SLA Impact:** High - All constitutional governance operations affected

## Overview

This runbook addresses PostgreSQL database connectivity and performance issues in the ACGS-1 Constitutional Governance System. Database issues can completely halt constitutional governance operations and require immediate attention.

## Database Configuration

- **Database:** PostgreSQL 13+
- **Host:** localhost
- **Port:** 5432
- **Database Name:** acgs_db
- **User:** acgs_user
- **Connection Pool:** 10-20 connections per service

## Immediate Response (0-5 minutes)

### 1. Alert Acknowledgment

```bash
# Acknowledge the alert
curl -X POST http://localhost:8080/alerts/{alert_id}/acknowledge \
  -H "Authorization: Bearer acgs-webhook-secret-2024"
```

### 2. Quick Database Status Check

```bash
# Check PostgreSQL service status
sudo systemctl status postgresql

# Check if PostgreSQL is listening
netstat -tlnp | grep :5432

# Quick connection test
psql -h localhost -U acgs_user -d acgs_db -c "SELECT 1;" 2>/dev/null && echo "DB Connected" || echo "DB Connection Failed"
```

### 3. Check Database Processes

```bash
# Check PostgreSQL processes
ps aux | grep postgres

# Check database connections
sudo -u postgres psql -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"
```

## Investigation (5-15 minutes)

### 4. Database Service Analysis

```bash
# Check PostgreSQL logs
sudo tail -n 100 /var/log/postgresql/postgresql-*.log

# Check for recent errors
sudo grep -i "error\|fatal\|panic" /var/log/postgresql/postgresql-*.log | tail -20

# Check disk space for database
df -h /var/lib/postgresql/
```

### 5. Connection Pool Analysis

```bash
# Check active connections by database
sudo -u postgres psql -c "
SELECT datname, count(*) as connections
FROM pg_stat_activity
GROUP BY datname
ORDER BY connections DESC;"

# Check connection states
sudo -u postgres psql -c "
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;"

# Check for long-running transactions
sudo -u postgres psql -c "
SELECT pid, now() - xact_start as duration, query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY duration DESC
LIMIT 10;"
```

### 6. Database Performance Metrics

```bash
# Check database size
sudo -u postgres psql -c "
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;"

# Check table sizes
sudo -u postgres psql acgs_db -c "
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;"

# Check index usage
sudo -u postgres psql acgs_db -c "
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_tup_read DESC
LIMIT 10;"
```

## Automated Remediation

### 7. Intelligent Alerting Response

The system will automatically attempt:

1. **Database Connection Test**
2. **Connection Pool Reset**
3. **Service Restart** (if connection pool exhausted)
4. **Database Restart** (requires approval for critical impact)

## Manual Database Recovery

### 8. Connection Issues Resolution

#### Connection Pool Exhaustion

```bash
# Kill idle connections
sudo -u postgres psql -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < now() - interval '1 hour';"

# Restart services to reset connection pools
python3 /home/dislove/ACGS-1/scripts/emergency_rollback_procedures.py restart
```

#### Database Service Issues

```bash
# Restart PostgreSQL service
sudo systemctl restart postgresql

# Check restart status
sudo systemctl status postgresql

# Verify database is accepting connections
psql -h localhost -U acgs_user -d acgs_db -c "SELECT version();"
```

### 9. Database Corruption Issues

#### Check Database Integrity

```bash
# Check for database corruption
sudo -u postgres psql acgs_db -c "
SELECT datname, pg_database_size(datname)
FROM pg_database
WHERE datname = 'acgs_db';"

# Run database consistency checks
sudo -u postgres psql acgs_db -c "
SELECT schemaname, tablename,
       pg_relation_size(schemaname||'.'||tablename) as size
FROM pg_tables
WHERE schemaname = 'public';"
```

#### Repair Procedures

```bash
# Reindex database (if corruption suspected)
sudo -u postgres psql acgs_db -c "REINDEX DATABASE acgs_db;"

# Vacuum and analyze
sudo -u postgres psql acgs_db -c "VACUUM FULL ANALYZE;"

# Check for orphaned files
sudo find /var/lib/postgresql/ -name "*.tmp" -o -name "*.old"
```

### 10. Performance Optimization

#### Query Performance

```bash
# Enable query logging temporarily
sudo -u postgres psql -c "ALTER SYSTEM SET log_statement = 'all';"
sudo -u postgres psql -c "SELECT pg_reload_conf();"

# Check slow queries
sudo -u postgres psql -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;"

# Disable query logging
sudo -u postgres psql -c "ALTER SYSTEM SET log_statement = 'none';"
sudo -u postgres psql -c "SELECT pg_reload_conf();"
```

#### Index Optimization

```bash
# Find missing indexes
sudo -u postgres psql acgs_db -c "
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
AND n_distinct > 100
ORDER BY n_distinct DESC;"

# Check unused indexes
sudo -u postgres psql acgs_db -c "
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;"
```

## Database Backup and Recovery

### 11. Emergency Backup

```bash
# Create emergency backup
sudo -u postgres pg_dump acgs_db > /tmp/acgs_emergency_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
head -20 /tmp/acgs_emergency_backup_*.sql

# Compress backup
gzip /tmp/acgs_emergency_backup_*.sql
```

### 12. Point-in-Time Recovery

```bash
# Check WAL files
sudo ls -la /var/lib/postgresql/*/pg_wal/

# Check backup status
sudo -u postgres psql -c "SELECT pg_is_in_recovery();"

# If recovery needed, stop services first
python3 /home/dislove/ACGS-1/scripts/emergency_rollback_procedures.py stop
```

## Service-Specific Database Issues

### Auth Service Database Issues

```bash
# Check user authentication tables
sudo -u postgres psql acgs_db -c "
SELECT count(*) FROM users;
SELECT count(*) FROM user_sessions WHERE expires_at > now();"

# Reset authentication cache
redis-cli DEL "auth:*"
```

### AC Service Database Issues

```bash
# Check constitutional amendment tables
sudo -u postgres psql acgs_db -c "
SELECT count(*) FROM constitutional_amendments;
SELECT status, count(*) FROM constitutional_amendments GROUP BY status;"

# Verify amendment integrity
sudo -u postgres psql acgs_db -c "
SELECT id, title, hash_value
FROM constitutional_amendments
WHERE hash_value IS NULL OR hash_value = '';"
```

### PGC Service Database Issues

```bash
# Check governance compliance tables
sudo -u postgres psql acgs_db -c "
SELECT count(*) FROM governance_policies;
SELECT count(*) FROM compliance_validations WHERE created_at > now() - interval '1 day';"

# Verify constitutional hash consistency
sudo -u postgres psql acgs_db -c "
SELECT DISTINCT constitutional_hash
FROM governance_policies
WHERE constitutional_hash != 'cdd01ef066bc6cf2';"
```

## Database Monitoring Setup

### 13. Enhanced Monitoring

```bash
# Install pg_stat_statements extension
sudo -u postgres psql acgs_db -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# Configure monitoring user
sudo -u postgres psql -c "
CREATE USER acgs_monitor WITH PASSWORD 'monitor_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO acgs_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO acgs_monitor;"
```

### 14. Automated Health Checks

```bash
# Create database health check script
cat > /home/dislove/ACGS-1/scripts/db_health_check.sh << 'EOF'
#!/bin/bash
DB_STATUS=$(psql -h localhost -U acgs_user -d acgs_db -c "SELECT 1;" 2>/dev/null && echo "OK" || echo "FAIL")
CONNECTIONS=$(sudo -u postgres psql -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null || echo "0")
echo "Database Status: $DB_STATUS, Active Connections: $CONNECTIONS"
EOF

chmod +x /home/dislove/ACGS-1/scripts/db_health_check.sh
```

## Escalation Procedures

### Level 1 Escalation (5 minutes)

- **Trigger:** Database connection failures
- **Action:** Contact Database Administrator
- **Channels:** #acgs-database-alerts

### Level 2 Escalation (15 minutes)

- **Trigger:** Database service down
- **Action:** Engage Infrastructure Team
- **Channels:** #acgs-critical-alerts, Emergency on-call

### Level 3 Escalation (30 minutes)

- **Trigger:** Data corruption suspected
- **Action:** Activate disaster recovery
- **Channels:** Emergency response team, Management notification

## Post-Incident Actions

### 15. Database Analysis

```bash
# Generate database performance report
sudo -u postgres psql acgs_db -c "
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_stat_get_tuples_inserted(c.oid) as inserts,
    pg_stat_get_tuples_updated(c.oid) as updates,
    pg_stat_get_tuples_deleted(c.oid) as deletes
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### 16. Preventive Measures

- Review database configuration
- Update connection pool settings
- Implement database monitoring
- Schedule regular maintenance
- Update backup procedures

## Database Maintenance Checklist

- [ ] Database service running
- [ ] Connection pools within limits
- [ ] No long-running transactions
- [ ] Disk space adequate (>20% free)
- [ ] Backup completed successfully
- [ ] Query performance acceptable
- [ ] No corruption detected
- [ ] Monitoring alerts configured

## Emergency Contacts

- **Database Administrator:** DBA Team
- **Infrastructure Team:** Infrastructure on-call
- **Application Teams:** Service owners
- **Escalation:** System Architecture Team

## Related Runbooks

- [Service Down Runbook](service_down_runbook.md)
- [High Response Time Runbook](high_response_time_runbook.md)
- [Backup and Recovery Runbook](backup_recovery_runbook.md)
- [Performance Issues Runbook](performance_issues_runbook.md)

---

**Last Updated:** 2024-01-01  
**Version:** 1.0  
**Owner:** ACGS Database Administration Team
