# ACGS Operational Runbooks
**Constitutional Hash:** `cdd01ef066bc6cf2`

## Overview
This document provides step-by-step procedures for common operational scenarios in the ACGS production environment.

## Runbook Index
1. [Service Restart Procedures](#service-restart-procedures)
2. [Performance Issue Investigation](#performance-issue-investigation)
3. [Constitutional Compliance Restoration](#constitutional-compliance-restoration)
4. [Monitoring System Recovery](#monitoring-system-recovery)
5. [Database Maintenance](#database-maintenance)
6. [Alert Investigation and Resolution](#alert-investigation-and-resolution)

---

## Service Restart Procedures

### PostgreSQL Service Restart
**Estimated Time:** 5 minutes  
**Risk Level:** Medium  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Prerequisites
- [ ] Verify no critical operations are running
- [ ] Notify team of planned restart
- [ ] Ensure backup is recent

#### Steps
1. **Check current status**
   ```bash
   docker exec acgs_postgres_production pg_isready -U acgs_user -d acgs
   ```

2. **Graceful restart**
   ```bash
   docker compose -f docker-compose.production-simple.yml restart postgres
   ```

3. **Verify restart**
   ```bash
   docker logs acgs_postgres_production --tail 20
   docker exec acgs_postgres_production pg_isready -U acgs_user -d acgs
   ```

4. **Validate constitutional compliance**
   ```bash
   # Verify service maintains constitutional requirements
   docker exec acgs_postgres_production psql -U acgs_user -d acgs -c "SELECT version();"
   ```

#### Rollback Procedure
If restart fails:
1. Check container logs for errors
2. Restore from backup if necessary
3. Escalate to database team

---

### Redis Service Restart
**Estimated Time:** 3 minutes  
**Risk Level:** Low  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Steps
1. **Check current status**
   ```bash
   docker exec acgs_redis_production redis-cli -a redis_production_password_2025 ping
   ```

2. **Restart service**
   ```bash
   docker compose -f docker-compose.production-simple.yml restart redis
   ```

3. **Verify functionality**
   ```bash
   docker exec acgs_redis_production redis-cli -a redis_production_password_2025 ping
   docker exec acgs_redis_production redis-cli -a redis_production_password_2025 info
   ```

---

### Prometheus Service Restart
**Estimated Time:** 2 minutes  
**Risk Level:** Low  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Steps
1. **Restart Prometheus**
   ```bash
   docker compose -f docker-compose.production-simple.yml restart prometheus
   ```

2. **Verify configuration loading**
   ```bash
   curl -s http://localhost:9091/api/v1/status/config | grep cdd01ef066bc6cf2
   ```

3. **Check alert rules**
   ```bash
   curl -s http://localhost:9091/api/v1/rules | jq '.data.groups | length'
   ```

---

## Performance Issue Investigation

### High Latency Investigation
**Estimated Time:** 30 minutes  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Investigation Steps
1. **Check current performance metrics**
   ```bash
   ./testing/performance/production-validation.sh
   ```

2. **Analyze Prometheus metrics**
   ```bash
   curl -s "http://localhost:9091/api/v1/query?query=up" | jq '.data.result'
   ```

3. **Check resource utilization**
   ```bash
   docker stats --no-stream
   ```

4. **Review recent changes**
   - Check deployment logs
   - Review configuration changes
   - Validate constitutional compliance

#### Resolution Actions
- Restart affected services if needed
- Scale resources if utilization is high
- Rollback recent changes if identified as cause
- Escalate to engineering team if unresolved

---

## Constitutional Compliance Restoration

### Compliance Violation Response
**Estimated Time:** 15 minutes  
**Risk Level:** Critical  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Immediate Actions
1. **Stop all affected operations**
   ```bash
   # Identify non-compliant services
   curl -s http://localhost:9091/api/v1/status/config | grep -c cdd01ef066bc6cf2
   ```

2. **Isolate affected systems**
   ```bash
   # Stop non-compliant containers if necessary
   docker compose -f docker-compose.production-simple.yml stop [service_name]
   ```

3. **Validate constitutional hash presence**
   ```bash
   # Check all configuration files
   grep -r "cdd01ef066bc6cf2" monitoring/ docker-compose*.yml
   ```

4. **Restore compliance**
   - Update configurations with correct constitutional hash
   - Restart services with compliant configurations
   - Verify compliance restoration

5. **Document incident**
   - Record violation details
   - Document remediation steps
   - Update compliance procedures if needed

---

## Monitoring System Recovery

### Prometheus Recovery
**Estimated Time:** 10 minutes  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Recovery Steps
1. **Check Prometheus status**
   ```bash
   curl -s http://localhost:9091/api/v1/status/config
   ```

2. **Restart if unresponsive**
   ```bash
   docker compose -f docker-compose.production-simple.yml restart prometheus
   ```

3. **Verify configuration**
   ```bash
   # Check constitutional compliance
   curl -s http://localhost:9091/api/v1/status/config | grep cdd01ef066bc6cf2
   
   # Verify alert rules
   curl -s http://localhost:9091/api/v1/rules
   ```

4. **Test metrics collection**
   ```bash
   curl -s "http://localhost:9091/api/v1/query?query=up"
   ```

---

### Grafana Recovery
**Estimated Time:** 5 minutes  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Recovery Steps
1. **Check Grafana health**
   ```bash
   curl -s http://localhost:3001/api/health
   ```

2. **Restart if needed**
   ```bash
   docker compose -f docker-compose.production-simple.yml restart grafana
   ```

3. **Verify dashboards**
   ```bash
   curl -s -u admin:acgs_admin_2025 http://localhost:3001/api/search?type=dash-db
   ```

4. **Test data source connectivity**
   - Access Grafana UI at http://localhost:3001
   - Verify Prometheus data source connection
   - Test dashboard functionality

---

## Database Maintenance

### PostgreSQL Maintenance
**Estimated Time:** 20 minutes  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Routine Maintenance
1. **Check database health**
   ```bash
   docker exec acgs_postgres_production psql -U acgs_user -d acgs -c "SELECT version();"
   ```

2. **Analyze database statistics**
   ```bash
   docker exec acgs_postgres_production psql -U acgs_user -d acgs -c "ANALYZE;"
   ```

3. **Check connection status**
   ```bash
   docker exec acgs_postgres_production psql -U acgs_user -d acgs -c "SELECT count(*) FROM pg_stat_activity;"
   ```

4. **Vacuum if needed**
   ```bash
   docker exec acgs_postgres_production psql -U acgs_user -d acgs -c "VACUUM ANALYZE;"
   ```

---

## Alert Investigation and Resolution

### Critical Alert Response
**Response Time:** 5 minutes  
**Constitutional Hash:** `cdd01ef066bc6cf2`

#### Investigation Process
1. **Identify alert details**
   ```bash
   curl -s http://localhost:9091/api/v1/alerts | jq '.data.alerts[] | select(.state=="firing")'
   ```

2. **Check affected services**
   ```bash
   # Check service health
   docker compose -f docker-compose.production-simple.yml ps
   ```

3. **Analyze root cause**
   - Review service logs
   - Check resource utilization
   - Validate constitutional compliance
   - Review recent changes

4. **Implement resolution**
   - Restart services if needed
   - Scale resources if required
   - Fix configuration issues
   - Restore constitutional compliance

5. **Verify resolution**
   ```bash
   # Check alert status
   curl -s http://localhost:9091/api/v1/alerts
   ```

6. **Document incident**
   - Record alert details and timeline
   - Document root cause analysis
   - Update procedures if needed

---

## Emergency Contacts

### Escalation Matrix
- **Level 1:** Operations Team (15 min response)
- **Level 2:** Senior Operations (30 min response)
- **Level 3:** Engineering Team (1 hour response)
- **Level 4:** Management (2 hour response)

### Constitutional Compliance Issues
- **Immediate:** compliance@acgs.example.com
- **Emergency:** +1-555-ACGS-COMP

---

## Validation Checklist

After any operational procedure:
- [ ] All services are running and healthy
- [ ] Constitutional compliance validated (hash: `cdd01ef066bc6cf2`)
- [ ] Monitoring systems operational
- [ ] Performance metrics within targets
- [ ] No active critical alerts
- [ ] Documentation updated if needed

---
**Document Version:** 1.0  
**Last Updated:** 2025-07-07  
**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Next Review:** 2025-08-07
