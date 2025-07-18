# ACGS-2 Operational Runbook

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This operational runbook provides comprehensive guidance for maintaining, monitoring, and troubleshooting the ACGS-2 (Advanced Constitutional Governance System) production environment.

## Quick Reference

### Emergency Contacts
- **System Administrator**: Primary contact for system issues
- **Security Team**: Constitutional compliance and security incidents
- **Development Team**: Application-level issues and bugs
- **Infrastructure Team**: Hardware and network issues

### Critical System Information
- **Constitutional Hash**: `cdd01ef066bc6cf2`
- **Primary Environment**: Production
- **Backup Environment**: Staging
- **Monitoring Dashboard**: http://localhost:3001 (Grafana)
- **Metrics Endpoint**: http://localhost:9090 (Prometheus)

## System Startup Procedures

### 1. Full System Startup

```bash
# Constitutional Hash: cdd01ef066bc6cf2
# Step 1: Start core infrastructure
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d postgres redis

# Step 2: Wait for health checks (30 seconds)
sleep 30

# Step 3: Start policy engine
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d opa

# Step 4: Start core services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d constitutional_core integrity_service

# Step 5: Start platform services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d api_gateway auth_service

# Step 6: Start advanced services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d governance_engine ec_service

# Step 7: Start monitoring
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d prometheus grafana

# Step 8: Start remaining services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d
```

### 2. Selective Service Startup

```bash
# Start specific service
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d <service_name>

# Scale specific service
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d --scale worker_agents=3
```

## Health Monitoring

### 1. Service Health Checks

```bash
# Check all service health
docker-compose -f infrastructure/docker/docker-compose.acgs.yml ps

# Check specific service health
curl -f http://localhost:8001/health  # Constitutional AI Service
curl -f http://localhost:8002/health  # Integrity Service
curl -f http://localhost:8004/health  # Governance Engine
curl -f http://localhost:8080/gateway/health  # API Gateway
```

### 2. Constitutional Compliance Monitoring

```bash
# Verify constitutional hash enforcement
grep -r "cdd01ef066bc6cf2" /app/logs/

# Check compliance metrics
curl http://localhost:9090/api/v1/query?query=acgs_constitutional_compliance_rate

# Monitor compliance violations
docker logs acgs_constitutional_core | grep -i "violation"
```

### 3. Performance Monitoring

```bash
# P99 Latency Check
curl http://localhost:9090/api/v1/query?query=histogram_quantile(0.99,acgs_response_time_seconds)

# Throughput Check
curl http://localhost:9090/api/v1/query?query=rate(acgs_requests_total[5m])

# Cache Hit Rate
curl http://localhost:9090/api/v1/query?query=acgs_cache_hit_rate

# Redis Performance
redis-cli -p 6389 info stats
```

## Troubleshooting Guide

### 1. Service Not Starting

**Symptoms**: Container exits immediately or fails to start

**Diagnosis**:
```bash
# Check container logs
docker logs acgs_<service_name>

# Check resource usage
docker stats acgs_<service_name>

# Check network connectivity
docker network ls
docker network inspect acgs_network
```

**Resolution**:
1. Verify environment variables are set
2. Check database connectivity
3. Ensure constitutional hash is properly configured
4. Verify service dependencies are running

### 2. Database Connection Issues

**Symptoms**: Services report database connection errors

**Diagnosis**:
```bash
# Check PostgreSQL health
docker exec acgs_postgres pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Check connection pool
docker logs acgs_postgres | grep -i "connection"

# Test database connectivity
psql -h localhost -p 5439 -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

**Resolution**:
1. Restart PostgreSQL container
2. Check database credentials
3. Verify network connectivity
4. Check available connections

### 3. Cache Performance Issues

**Symptoms**: High latency, low cache hit rates

**Diagnosis**:
```bash
# Check Redis status
redis-cli -p 6389 info replication

# Monitor cache metrics
redis-cli -p 6389 info stats | grep -E "(hit|miss|evicted)"

# Check memory usage
redis-cli -p 6389 info memory
```

**Resolution**:
1. Increase Redis memory allocation
2. Optimize cache key strategies
3. Implement cache warming
4. Review cache TTL settings

### 4. Constitutional Compliance Violations

**Symptoms**: Compliance rate below 100%

**Diagnosis**:
```bash
# Check compliance logs
docker logs acgs_constitutional_core | grep -i "compliance"

# Verify constitutional hash
grep -r "cdd01ef066bc6cf2" /app/

# Check OPA policy enforcement
curl http://localhost:8181/health
```

**Resolution**:
1. Verify constitutional hash in all services
2. Check OPA policy configurations
3. Review service authentication
4. Validate constitutional AI service

### 5. Performance Degradation

**Symptoms**: Response times exceed constitutional targets

**Diagnosis**:
```bash
# Check service metrics
curl http://localhost:9090/api/v1/query?query=acgs_response_time_seconds

# Monitor resource usage
docker stats

# Check for bottlenecks
docker logs acgs_api_gateway | grep -i "slow"
```

**Resolution**:
1. Scale up affected services
2. Optimize database queries
3. Increase cache capacity
4. Review load balancing configuration

## Maintenance Procedures

### 1. Regular Backup

```bash
# Database backup
docker exec acgs_postgres pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%Y%m%d).sql

# Redis backup
docker exec acgs_redis redis-cli -p 6379 BGSAVE

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz infrastructure/docker/
```

### 2. Log Rotation

```bash
# Rotate application logs
docker exec acgs_log_aggregator logrotate /etc/logrotate.conf

# Clean old logs
find /app/logs -name "*.log" -mtime +30 -delete

# Compress logs
gzip /app/logs/*.log
```

### 3. Security Updates

```bash
# Update base images
docker-compose -f infrastructure/docker/docker-compose.acgs.yml pull

# Rebuild with security patches
docker-compose -f infrastructure/docker/docker-compose.acgs.yml build --no-cache

# Rolling update
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d --force-recreate
```

### 4. Performance Optimization

```bash
# Analyze slow queries
docker exec acgs_postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Optimize Redis
redis-cli -p 6389 config set maxmemory-policy allkeys-lru

# Review cache hit rates
redis-cli -p 6389 info stats | grep keyspace_hits
```

## Emergency Response Procedures

### 1. Service Outage Response

**Immediate Actions**:
1. Check service health status
2. Verify infrastructure dependencies
3. Check resource availability
4. Review recent changes

**Recovery Steps**:
```bash
# Quick restart
docker-compose -f infrastructure/docker/docker-compose.acgs.yml restart <service_name>

# Full recovery
docker-compose -f infrastructure/docker/docker-compose.acgs.yml down <service_name>
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d <service_name>
```

### 2. Data Corruption Response

**Immediate Actions**:
1. Stop affected services
2. Identify corruption scope
3. Isolate affected data
4. Initiate backup recovery

**Recovery Steps**:
```bash
# Stop services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml stop

# Restore from backup
docker exec acgs_postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < backup_latest.sql

# Restart services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml start
```

### 3. Security Incident Response

**Immediate Actions**:
1. Isolate affected systems
2. Preserve evidence
3. Assess impact
4. Notify security team

**Recovery Steps**:
```bash
# Enable security validation
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d security_validation

# Review audit logs
docker logs acgs_integrity_service | grep -i "security"

# Verify constitutional compliance
curl http://localhost:8001/constitutional/validate
```

## Monitoring and Alerting

### 1. Critical Alerts

- **Service Down**: Any core service becomes unavailable
- **Constitutional Violation**: Compliance rate drops below 100%
- **Performance Degradation**: P99 latency exceeds 5ms
- **Database Issues**: Connection failures or corruption
- **Security Incidents**: Unauthorized access attempts

### 2. Dashboard Metrics

**Grafana Dashboards**:
- System Overview
- Service Performance
- Constitutional Compliance
- Database Metrics
- Cache Performance
- Security Monitoring

### 3. Alert Configuration

```yaml
# Prometheus alerting rules
groups:
- name: acgs_alerts
  rules:
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service {{ $labels.instance }} is down"
      
  - alert: ConstitutionalViolation
    expr: acgs_constitutional_compliance_rate < 1.0
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "Constitutional compliance violation detected"
```

## NEW_KNOWLEDGE_BLOCK for Blackboard Ingestion

```markdown
### NEW_KNOWLEDGE_BLOCK

ACGS-2 Emergency Recovery ::
1. `docker-compose -f infrastructure/docker/docker-compose.acgs.yml down`
2. `docker system prune -f`
3. `docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d postgres redis`
4. `sleep 30 && docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d`

### END_KNOWLEDGE_BLOCK
```

```markdown
### NEW_KNOWLEDGE_BLOCK

ACGS-2 Health Check Commands ::
- `curl http://localhost:8001/health` (Constitutional AI)
- `curl http://localhost:8002/health` (Integrity Service)
- `curl http://localhost:8080/gateway/health` (API Gateway)
- `docker-compose -f infrastructure/docker/docker-compose.acgs.yml ps`

### END_KNOWLEDGE_BLOCK
```

```markdown
### NEW_KNOWLEDGE_BLOCK

ACGS-2 Performance Monitoring ::
- `curl http://localhost:9090/api/v1/query?query=acgs_response_time_seconds`
- `redis-cli -p 6389 info stats`
- `docker stats acgs_*`
- `pg_stat_activity` query for database monitoring

### END_KNOWLEDGE_BLOCK
```

## Contact Information

### Escalation Matrix
1. **Level 1**: System Administrator
2. **Level 2**: Security Team + Development Team
3. **Level 3**: Infrastructure Team + Management

### Documentation Updates
- Update this runbook after any major system changes
- Review quarterly for accuracy
- Incorporate lessons learned from incidents

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Performance Targets**: P99 <5ms, >100 RPS, >85% cache hit rates  
**Compliance**: 100% Constitutional compliance enforced  
**Last Updated**: Generated for Step 12 Knowledge Transfer  
**Next Review**: Schedule quarterly review
