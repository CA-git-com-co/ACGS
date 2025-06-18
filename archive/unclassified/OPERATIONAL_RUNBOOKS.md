# ACGS-1 Operational Runbooks

**Version**: 1.0  
**Date**: 2025-06-15  
**Status**: Production Ready  

## 🚨 Emergency Contacts

- **Primary On-Call**: ACGS-1 Operations Team
- **Secondary**: Infrastructure Team  
- **Escalation**: System Architecture Team

## 📋 Quick Reference

### Service Ports
- Auth Service: 8000
- AC Service: 8001  
- Integrity Service: 8002
- FV Service: 8003
- GS Service: 8004
- PGC Service: 8005
- EC Service: 8006

### Key URLs
- **Grafana Dashboard**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **HAProxy Stats**: http://localhost:8080/stats

## 🔧 Service Management

### Start All Services
```bash
cd /home/dislove/ACGS-1
./scripts/start_missing_services.sh
```

### Check Service Health
```bash
python3 scripts/comprehensive_health_check.py
```

### Individual Service Management
```bash
# Start specific service
cd services/[service-path]
uvicorn app.main:app --host 0.0.0.0 --port [PORT]

# Stop service
pkill -f 'uvicorn.*:[PORT]'

# Check service logs
tail -f logs/[service_name].log
```

## 🚨 Incident Response

### Severity Levels

#### CRITICAL (P1) - Immediate Response
- **Definition**: Complete system outage, security breach
- **Response Time**: 15 minutes
- **Actions**:
  1. Acknowledge incident
  2. Assess impact and scope
  3. Implement immediate mitigation
  4. Escalate to architecture team
  5. Communicate to stakeholders

#### HIGH (P2) - 1 Hour Response  
- **Definition**: Service degradation, partial outage
- **Response Time**: 1 hour
- **Actions**:
  1. Investigate root cause
  2. Implement workaround if possible
  3. Plan permanent fix
  4. Monitor system stability

#### MEDIUM (P3) - 4 Hour Response
- **Definition**: Performance issues, non-critical failures
- **Response Time**: 4 hours
- **Actions**:
  1. Schedule investigation
  2. Implement fix during maintenance window
  3. Update monitoring if needed

### Common Issues & Solutions

#### Service Not Responding
```bash
# 1. Check if service is running
ps aux | grep uvicorn

# 2. Check port availability  
netstat -tlnp | grep [PORT]

# 3. Check logs for errors
tail -f logs/[service_name].log

# 4. Restart service
cd services/[service-path]
uvicorn app.main:app --host 0.0.0.0 --port [PORT]
```

#### High Response Times
```bash
# 1. Check system resources
htop
df -h

# 2. Check Redis cache
redis-cli ping

# 3. Check database connections
docker exec acgs_postgres pg_isready

# 4. Review Grafana dashboards for bottlenecks
```

#### Database Connection Issues
```bash
# 1. Check PostgreSQL status
docker ps | grep postgres

# 2. Check database logs
docker logs acgs_postgres

# 3. Test connection
docker exec acgs_postgres pg_isready -U acgs_user

# 4. Restart if needed
docker restart acgs_postgres
```

## 📊 Monitoring & Alerting

### Key Metrics to Monitor
- **Service Health**: All services responding to /health
- **Response Times**: <500ms for 95% of requests
- **Error Rates**: <1% error rate
- **Resource Usage**: CPU <80%, Memory <85%
- **Database Performance**: Connection pool, query times

### Alert Response Procedures

#### Service Down Alert
1. **Immediate**: Check service status via health endpoint
2. **Investigate**: Review service logs for errors
3. **Action**: Restart service if needed
4. **Validate**: Confirm service recovery
5. **Document**: Log incident and resolution

#### High Response Time Alert  
1. **Check**: System resource utilization
2. **Investigate**: Database and cache performance
3. **Action**: Scale resources or optimize queries
4. **Monitor**: Track improvement in metrics
5. **Follow-up**: Implement permanent optimizations

#### Security Alert
1. **Immediate**: Isolate affected systems
2. **Assess**: Determine scope and impact
3. **Contain**: Implement security measures
4. **Investigate**: Analyze attack vectors
5. **Recover**: Restore services securely
6. **Report**: Document security incident

## 💾 Backup & Recovery

### Daily Backup Procedure
```bash
# Manual backup
sudo -u postgres pg_dump acgs_pgp_db > /var/backups/acgs-pgp/backup_$(date +%Y%m%d).sql

# Automated backup (cron)
0 2 * * * /home/dislove/ACGS-1/scripts/backup_database_comprehensive.sh
```

### Recovery Procedure
```bash
# 1. Stop all services
pkill -f 'uvicorn.*:800[0-6]'

# 2. Restore database
sudo -u postgres psql -d acgs_pgp_db < /var/backups/acgs-pgp/backup_YYYYMMDD.sql

# 3. Restart services
./scripts/start_missing_services.sh

# 4. Validate recovery
python3 scripts/comprehensive_health_check.py
```

## 🔄 Maintenance Procedures

### Planned Maintenance Window
1. **Pre-maintenance**:
   - Notify stakeholders
   - Create backup
   - Prepare rollback plan
   
2. **During maintenance**:
   - Stop services gracefully
   - Apply updates/changes
   - Test functionality
   
3. **Post-maintenance**:
   - Start services
   - Validate health checks
   - Monitor for issues
   - Confirm completion

### Rolling Updates
```bash
# 1. Update one service at a time
cd services/[service-path]
git pull origin main

# 2. Restart service
pkill -f 'uvicorn.*:[PORT]'
uvicorn app.main:app --host 0.0.0.0 --port [PORT] &

# 3. Validate health
curl http://localhost:[PORT]/health

# 4. Proceed to next service
```

## 🔍 Troubleshooting Guide

### Performance Issues
1. **Check system resources**: CPU, memory, disk I/O
2. **Review database performance**: Slow queries, connections
3. **Analyze cache hit rates**: Redis performance metrics
4. **Check network latency**: Service-to-service communication
5. **Review application logs**: Error patterns and bottlenecks

### Service Startup Issues
1. **Check dependencies**: Database, Redis, OPA availability
2. **Verify configuration**: Environment variables, ports
3. **Review logs**: Startup errors and stack traces
4. **Check permissions**: File and directory access
5. **Validate imports**: Python module dependencies

### Integration Issues
1. **Test service connectivity**: Health endpoints
2. **Check API compatibility**: Request/response formats
3. **Verify authentication**: JWT tokens and permissions
4. **Review policy enforcement**: OPA rule evaluation
5. **Validate data flow**: End-to-end request tracing

## 📈 Performance Optimization

### Regular Maintenance Tasks
- **Weekly**: Review performance metrics and trends
- **Monthly**: Analyze slow queries and optimize
- **Quarterly**: Capacity planning and scaling review
- **Annually**: Architecture review and modernization

### Optimization Checklist
- [ ] Database query optimization
- [ ] Cache hit rate improvement  
- [ ] Resource allocation tuning
- [ ] Load balancer configuration
- [ ] Service dependency optimization

## 📞 Escalation Matrix

### Level 1: Operations Team
- **Scope**: Routine issues, service restarts, monitoring
- **Response**: 15 minutes for critical, 1 hour for high

### Level 2: Engineering Team  
- **Scope**: Code issues, complex troubleshooting
- **Response**: 1 hour for critical, 4 hours for high

### Level 3: Architecture Team
- **Scope**: System design issues, major outages
- **Response**: 30 minutes for critical, 2 hours for high

### Level 4: Executive Team
- **Scope**: Business impact, security incidents
- **Response**: Immediate for critical business impact

---

**Document Owner**: ACGS-1 Operations Team  
**Last Updated**: 2025-06-15  
**Next Review**: 2025-07-15

## 🔄 Automated Backup System

### Backup Schedule
- **Daily Backups**: 2:00 AM (configurations, service states, blockchain)
- **Backup Monitoring**: Every hour
- **Health Checks**: Every 15 minutes
- **Cleanup**: Weekly (Sundays at 3:00 AM)

### Backup Commands
```bash
# Manual backup
python3 scripts/simple_backup_recovery.py backup

# List backups
python3 scripts/simple_backup_recovery.py list

# Monitor backup health
./scripts/monitor_backups.sh

# Test disaster recovery
./scripts/test_disaster_recovery.sh
```

### Emergency Procedures
```bash
# Quick health check
python3 scripts/emergency_rollback_procedures.py health

# Emergency stop all services
python3 scripts/emergency_rollback_procedures.py stop

# Emergency restart all services
python3 scripts/emergency_rollback_procedures.py restart

# Isolate specific service
python3 scripts/emergency_rollback_procedures.py isolate --service pgc_service

# Create incident report
python3 scripts/emergency_rollback_procedures.py incident \
  --type "service_failure" \
  --description "PGC service unresponsive" \
  --severity "high"

# Get emergency procedures
python3 scripts/emergency_rollback_procedures.py procedures
```

### Recovery Time Objectives
- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 15 minutes
- **Service Restart Time**: < 5 minutes
- **Health Check Response**: < 30 seconds

### Escalation Matrix
- **Low**: Log incident, monitor
- **Medium**: Contact primary on-call
- **High**: Contact primary + secondary
- **Critical**: Contact all teams + escalation

