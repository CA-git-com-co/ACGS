# ACGS-PGP v8 Operational Runbook

## Overview

This runbook provides operational procedures for managing the ACGS-PGP v8 service in production environments. It covers deployment, monitoring, troubleshooting, and maintenance procedures.

## Service Information

- **Service Name**: ACGS-PGP v8
- **Port**: 8010
- **Constitutional Hash**: cdd01ef066bc6cf2
- **Dependencies**: PostgreSQL, Redis, ACGS-1 Core Services
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`

## Deployment Procedures

### Production Deployment

1. **Pre-deployment Checklist**
   ```bash
   # Verify dependencies
   curl http://localhost:8000/health  # Auth Service
   curl http://localhost:8004/health  # GS Service
   curl http://localhost:8005/health  # PGC Service
   
   # Check database connectivity
   psql -h localhost -U acgs_user -d acgs_db -c "SELECT 1;"
   
   # Verify Redis connectivity
   redis-cli ping
   ```

2. **Deploy Service**
   ```bash
   cd services/core/acgs-pgp-v8
   
   # Build and deploy
   docker build -t acgs-pgp-v8:latest .
   docker run -d \
     --name acgs-pgp-v8 \
     -p 8010:8010 \
     -e DATABASE_URL=postgresql://acgs_user:acgs_password@localhost:5432/acgs_db \
     -e REDIS_URL=redis://localhost:6379/0 \
     -e CONSTITUTIONAL_HASH=cdd01ef066bc6cf2 \
     acgs-pgp-v8:latest
   ```

3. **Post-deployment Validation**
   ```bash
   # Health check
   curl http://localhost:8010/health
   
   # Metrics validation
   curl http://localhost:8010/metrics | grep acgs_pgp_v8_system_uptime_seconds
   
   # Run monitoring integration test
   python test_monitoring_integration.py
   ```

### Rolling Updates

1. **Prepare New Version**
   ```bash
   docker build -t acgs-pgp-v8:v8.0.1 .
   ```

2. **Deploy with Zero Downtime**
   ```bash
   # Start new container
   docker run -d \
     --name acgs-pgp-v8-new \
     -p 8011:8010 \
     -e DATABASE_URL=postgresql://acgs_user:acgs_password@localhost:5432/acgs_db \
     -e REDIS_URL=redis://localhost:6379/0 \
     acgs-pgp-v8:v8.0.1
   
   # Validate new container
   curl http://localhost:8011/health
   
   # Update load balancer to point to new container
   # Stop old container
   docker stop acgs-pgp-v8
   docker rm acgs-pgp-v8
   
   # Rename new container
   docker stop acgs-pgp-v8-new
   docker run -d \
     --name acgs-pgp-v8 \
     -p 8010:8010 \
     acgs-pgp-v8:v8.0.1
   ```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Service Health**
   - `up{job="acgs-pgp-v8-service"}` - Service availability
   - `acgs_pgp_v8_component_health` - Component health status

2. **Performance Metrics**
   - `acgs_pgp_v8_policy_generation_duration_seconds` - Response times
   - `acgs_pgp_v8_policy_generation_requests_total` - Request rates
   - `acgs_pgp_v8_constitutional_compliance_score` - Compliance scores

3. **Error Metrics**
   - `acgs_pgp_v8_error_correction_events_total` - Error correction events
   - `acgs_pgp_v8_circuit_breaker_state` - Circuit breaker states

### Alert Thresholds

```yaml
# Prometheus alerting rules
groups:
  - name: acgs-pgp-v8
    rules:
      - alert: ACGSPGPv8ServiceDown
        expr: up{job="acgs-pgp-v8-service"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ACGS-PGP v8 service is down"
      
      - alert: ACGSPGPv8HighResponseTime
        expr: histogram_quantile(0.95, rate(acgs_pgp_v8_policy_generation_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ACGS-PGP v8 high response time"
      
      - alert: ACGSPGPv8LowCompliance
        expr: histogram_quantile(0.50, rate(acgs_pgp_v8_constitutional_compliance_score_bucket[5m])) < 0.8
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "ACGS-PGP v8 constitutional compliance below threshold"
```

## Troubleshooting Guide

### Common Issues

#### 1. Service Won't Start

**Symptoms**: Container exits immediately or health check fails

**Diagnosis**:
```bash
# Check container logs
docker logs acgs-pgp-v8

# Check dependencies
curl http://localhost:5432  # PostgreSQL
redis-cli ping              # Redis
```

**Resolution**:
- Verify database connection string
- Ensure Redis is accessible
- Check environment variables
- Validate constitutional hash configuration

#### 2. High Response Times

**Symptoms**: Policy generation taking >500ms

**Diagnosis**:
```bash
# Check metrics
curl http://localhost:8010/metrics | grep duration

# Check system resources
docker stats acgs-pgp-v8

# Check database performance
psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

**Resolution**:
- Scale horizontally if CPU bound
- Optimize database queries
- Increase cache TTL
- Check network latency to dependencies

#### 3. Constitutional Compliance Failures

**Symptoms**: Compliance scores below 0.8

**Diagnosis**:
```bash
# Check PGC service health
curl http://localhost:8005/health

# Validate constitutional hash
curl http://localhost:8010/api/v1/status | jq '.constitutional_hash'

# Check compliance endpoint
curl http://localhost:8005/api/v1/constitutional/validate
```

**Resolution**:
- Verify PGC service is healthy
- Validate constitutional hash matches expected value
- Check policy generation parameters
- Review constitutional principles in requests

#### 4. Circuit Breaker Open

**Symptoms**: Requests failing with circuit breaker errors

**Diagnosis**:
```bash
# Check circuit breaker states
curl http://localhost:8010/metrics | grep circuit_breaker_state

# Check error rates
curl http://localhost:8010/metrics | grep error_correction_events
```

**Resolution**:
- Wait for circuit breaker to reset (30 seconds)
- Fix underlying service issues
- Restart service if circuit breaker stuck
- Review error correction logs

### Emergency Procedures

#### Service Restart

```bash
# Graceful restart
docker restart acgs-pgp-v8

# Force restart if unresponsive
docker kill acgs-pgp-v8
docker start acgs-pgp-v8

# Verify restart
curl http://localhost:8010/health
```

#### Database Connection Issues

```bash
# Check database connectivity
psql -h localhost -U acgs_user -d acgs_db -c "SELECT 1;"

# Restart database connection pool
docker restart acgs-pgp-v8

# Check for connection leaks
psql -c "SELECT count(*) FROM pg_stat_activity WHERE application_name LIKE '%acgs-pgp-v8%';"
```

#### Cache Issues

```bash
# Clear Redis cache
redis-cli FLUSHDB

# Restart Redis if needed
sudo systemctl restart redis

# Verify cache connectivity
redis-cli ping
```

## Maintenance Procedures

### Regular Maintenance

#### Daily Tasks
- Monitor service health and performance metrics
- Review error logs for anomalies
- Validate constitutional compliance scores
- Check resource utilization

#### Weekly Tasks
- Review and rotate logs
- Update security patches
- Performance optimization review
- Backup validation

#### Monthly Tasks
- Capacity planning review
- Security audit
- Dependency updates
- Documentation updates

### Backup and Recovery

#### Database Backup
```bash
# Create backup
pg_dump -h localhost -U acgs_user acgs_db > acgs_pgp_v8_backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h localhost -U acgs_user -d acgs_db < acgs_pgp_v8_backup_20240616.sql
```

#### Configuration Backup
```bash
# Backup configuration
cp config/acgs_pgp_v8_config.yaml backups/config_$(date +%Y%m%d).yaml

# Backup environment variables
env | grep ACGS > backups/env_$(date +%Y%m%d).txt
```

### Performance Tuning

#### Database Optimization
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM policy_generations WHERE created_at > NOW() - INTERVAL '1 day';

-- Update statistics
ANALYZE;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes;
```

#### Cache Optimization
```bash
# Monitor cache hit rates
redis-cli INFO stats | grep keyspace_hits

# Optimize TTL settings based on usage patterns
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Security Procedures

### Security Monitoring
- Monitor authentication failures
- Track constitutional compliance violations
- Review access patterns
- Validate JWT token integrity

### Incident Response
1. Isolate affected components
2. Preserve logs and evidence
3. Notify security team
4. Implement containment measures
5. Document incident details

### Security Updates
```bash
# Update base image
docker pull python:3.11-slim

# Rebuild with security patches
docker build --no-cache -t acgs-pgp-v8:latest .

# Deploy with rolling update
# (Follow rolling update procedure above)
```

## Contact Information

- **Primary On-Call**: ACGS-1 Operations Team
- **Secondary**: ACGS-1 Development Team
- **Emergency Escalation**: Constitutional Governance Council
- **Documentation**: services/core/acgs-pgp-v8/docs/
