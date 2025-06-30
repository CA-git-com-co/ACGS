# ACGS-2 Operational Runbook

## Daily Operations

### Morning Health Check (9:00 AM UTC)
1. **Service Health Verification**
   ```bash
   # Check all service health endpoints
   curl -f http://localhost:8000/health  # Auth Service
   curl -f http://localhost:8001/health  # Constitutional AI
   curl -f http://localhost:8005/health  # Policy Governance
   curl -f http://localhost:8004/health  # Governance Synthesis
   ```

2. **Database Health Check**
   ```bash
   # Check database connectivity and performance
   python3 scripts/health/check_database_health.py

   # Check for long-running queries
   psql -h localhost -U acgs_user -d acgs_production -c "
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query
   FROM pg_stat_activity
   WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
   ```

3. **Cache Performance Check**
   ```bash
   # Check Redis health and performance
   redis-cli info stats | grep hit_rate
   redis-cli info memory | grep used_memory_human
   ```

4. **Monitor Key Metrics**
   - Response times (P95 < 2s, P99 < 5s)
   - Error rates (< 1%)
   - Cache hit rates (> 85%)
   - Database connection pool usage (< 80%)

### Weekly Operations

#### Monday: Security Review
- Review security alerts and logs
- Check for failed authentication attempts
- Verify SSL certificate expiration dates
- Review access logs for anomalies

#### Wednesday: Performance Review
- Analyze performance trends
- Review slow query logs
- Check resource utilization trends
- Plan capacity adjustments if needed

#### Friday: Backup Verification
- Verify backup completion
- Test backup restoration process
- Review backup retention policies
- Update disaster recovery documentation

## Incident Response Procedures

### Severity Levels

#### Critical (P0) - Service Down
- **Response Time**: 15 minutes
- **Escalation**: Immediate to on-call engineer
- **Communication**: Status page update within 30 minutes

#### High (P1) - Degraded Performance
- **Response Time**: 1 hour
- **Escalation**: Within 2 hours if not resolved
- **Communication**: Internal notification within 1 hour

#### Medium (P2) - Minor Issues
- **Response Time**: 4 hours
- **Escalation**: Next business day if not resolved
- **Communication**: Internal tracking only

#### Low (P3) - Enhancement Requests
- **Response Time**: Next business day
- **Escalation**: Weekly review
- **Communication**: Planned maintenance window

### Incident Response Steps

1. **Acknowledge and Assess**
   - Acknowledge alert within SLA
   - Assess impact and severity
   - Gather initial information

2. **Investigate and Diagnose**
   - Check service health endpoints
   - Review logs and metrics
   - Identify root cause

3. **Implement Fix**
   - Apply immediate mitigation
   - Implement permanent fix
   - Verify resolution

4. **Communicate and Document**
   - Update stakeholders
   - Document incident details
   - Schedule post-mortem if needed

## Common Maintenance Tasks

### Service Restart
```bash
# Graceful service restart
docker-compose -f docker-compose.production.yml restart <service_name>

# Rolling restart for zero downtime
./scripts/operations/rolling_restart.sh
```

### Database Maintenance
```bash
# Vacuum and analyze database
psql -h localhost -U acgs_user -d acgs_production -c "VACUUM ANALYZE;"

# Reindex database
psql -h localhost -U acgs_user -d acgs_production -c "REINDEX DATABASE acgs_production;"

# Update table statistics
psql -h localhost -U acgs_user -d acgs_production -c "ANALYZE;"
```

### Cache Maintenance
```bash
# Clear specific cache keys
redis-cli DEL "cache_key_pattern*"

# Flush all cache (use with caution)
redis-cli FLUSHALL

# Check cache memory usage
redis-cli INFO memory
```

### Log Rotation
```bash
# Manual log rotation
logrotate -f /etc/logrotate.d/acgs

# Check log sizes
du -sh /var/log/acgs/*
```

## Monitoring and Alerting

### Key Metrics to Monitor

#### Application Metrics
- Request rate (requests/second)
- Response time (P50, P95, P99)
- Error rate (4xx, 5xx responses)
- Active connections

#### Infrastructure Metrics
- CPU utilization (< 80%)
- Memory utilization (< 85%)
- Disk utilization (< 90%)
- Network I/O

#### Business Metrics
- Constitutional compliance score (> 95%)
- Policy evaluation success rate (> 99%)
- User satisfaction metrics

### Alert Thresholds

#### Critical Alerts
- Service down (any core service)
- Error rate > 5%
- Response time P99 > 10s
- Database connection failures
- Disk usage > 95%

#### Warning Alerts
- Error rate > 1%
- Response time P95 > 2s
- Cache hit rate < 85%
- Memory usage > 85%
- CPU usage > 80%

## Escalation Procedures

### On-Call Rotation
- Primary: Senior Engineer (24/7)
- Secondary: Team Lead (business hours)
- Tertiary: Engineering Manager (escalation only)

### Contact Information
- On-call phone: +1-XXX-XXX-XXXX
- Slack channel: #acgs-incidents
- Email: acgs-oncall@company.com

### Escalation Timeline
- P0: Immediate escalation to secondary if no response in 15 minutes
- P1: Escalate to secondary after 2 hours
- P2: Escalate to secondary next business day
- P3: Weekly review with team lead
