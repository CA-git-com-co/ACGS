# ACGS-1 Operational Runbook

## 🚀 System Overview

The ACGS-1 (Autonomous Constitutional Governance System) consists of 7 core services running on ports 8000-8006:

- **Authentication Service** (Port 8000): Enterprise-grade authentication with MFA, OAuth, and API key management
- **Constitutional AI Service** (Port 8001): Constitutional compliance validation and democratic participation checking
- **Integrity Service** (Port 8002): Cryptographic integrity verification and PGP assurance
- **Formal Verification Service** (Port 8003): Enhanced formal verification with Z3 SMT solver integration
- **Governance Synthesis Service** (Port 8004): Multi-model consensus and policy workflow management
- **Policy Governance Service** (Port 8005): Policy engine and compliance checking
- **Evolutionary Computation Service** (Port 8006): WINA optimization and constitutional oversight

## 📊 Monitoring Infrastructure

### Dashboard Access
- **Main Dashboard**: http://localhost:3000
- **Metrics API**: http://localhost:3000/api/metrics
- **Health Checks**: Individual service health at `http://localhost:800X/health`

### Key Metrics
- **Response Time Target**: < 500ms (Current: 2-3ms average)
- **Uptime Target**: > 99% (Current: 100%)
- **Service Availability**: All 7 services operational
- **Alert Thresholds**:
  - Response time > 500ms
  - 3 consecutive health check failures
  - Service downtime

## 🚨 Alert Management

### Alert Severity Levels
- **Critical**: Service down, multiple consecutive failures
- **Warning**: High response time, performance degradation
- **Info**: Service recovery, configuration changes

### Alert Response Procedures

#### Service Down Alert
1. **Immediate Actions** (0-5 minutes):
   - Check service status: `curl http://localhost:800X/health`
   - Review service logs: Check terminal output or log files
   - Verify network connectivity and port availability

2. **Investigation** (5-15 minutes):
   - Check system resources: CPU, memory, disk space
   - Review recent deployments or configuration changes
   - Check dependencies (database, Redis, external APIs)

3. **Recovery Actions** (15-30 minutes):
   - Restart service if needed
   - Scale resources if resource-constrained
   - Rollback recent changes if necessary
   - Escalate to development team if issue persists

#### High Response Time Alert
1. **Assessment**:
   - Monitor response time trends
   - Check system load and resource utilization
   - Identify potential bottlenecks

2. **Optimization**:
   - Review database query performance
   - Check cache hit rates
   - Optimize resource allocation
   - Consider horizontal scaling

## 🔧 Common Operations

### Service Management

#### Starting Services
```bash
# Start individual service
cd services/platform/authentication/auth_service && python3 simple_main.py

# Start all services (use separate terminals)
./scripts/start_all_services.sh
```

#### Stopping Services
```bash
# Find and kill service by port
lsof -ti:8000 | xargs kill -9

# Stop all services
pkill -f "python3.*main.py"
```

#### Service Health Checks
```bash
# Check all services
python3 scripts/validate_services.py

# Check individual service
curl http://localhost:8000/health
```

### Monitoring Operations

#### Start Monitoring Dashboard
```bash
python3 scripts/simple_monitoring_dashboard.py
```

#### Start Alerting System
```bash
python3 scripts/simple_alerting_system.py
```

#### View Alert Report
```bash
cat alert_report.json
```

## 🔍 Troubleshooting Guide

### Common Issues

#### Service Won't Start
- **Check port availability**: `netstat -tlnp | grep 800X`
- **Verify dependencies**: Ensure required Python packages are installed
- **Check configuration**: Verify environment variables and config files
- **Review logs**: Check for error messages in service output

#### High Response Times
- **System resources**: Check CPU and memory usage
- **Database performance**: Monitor database query times
- **Network latency**: Test network connectivity
- **Cache performance**: Verify cache hit rates

#### Authentication Issues
- **JWT tokens**: Check token expiration and validation
- **API keys**: Verify API key configuration and permissions
- **OAuth**: Check OAuth provider configuration

### Performance Optimization

#### Database Optimization
- Monitor query performance
- Optimize indexes
- Consider connection pooling
- Review query patterns

#### Caching Strategy
- Implement Redis caching where appropriate
- Monitor cache hit rates
- Optimize cache expiration policies

#### Resource Scaling
- Monitor resource utilization
- Scale horizontally when needed
- Optimize resource allocation

## 📋 Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- Review monitoring dashboard
- Check alert status
- Verify all services are healthy
- Monitor response times and uptime

#### Weekly
- Review performance trends
- Check system resource usage
- Update security patches
- Review and rotate logs

#### Monthly
- Performance optimization review
- Security audit
- Backup verification
- Capacity planning review

### Emergency Procedures

#### System-Wide Outage
1. **Immediate Response**:
   - Assess scope of outage
   - Check infrastructure status
   - Notify stakeholders

2. **Recovery**:
   - Restart services in dependency order
   - Verify data integrity
   - Restore from backup if necessary

3. **Post-Incident**:
   - Conduct root cause analysis
   - Update runbooks
   - Implement preventive measures

## 📞 Escalation Contacts

### Development Team
- **Primary**: Development team lead
- **Secondary**: System architect
- **Emergency**: On-call engineer

### Infrastructure Team
- **Primary**: DevOps engineer
- **Secondary**: Infrastructure manager
- **Emergency**: Infrastructure on-call

## 📚 Additional Resources

- **System Architecture**: docs/SYSTEM_ARCHITECTURE.md
- **API Documentation**: Individual service `/docs` endpoints
- **Security Guidelines**: docs/SECURITY_GUIDELINES.md
- **Deployment Guide**: docs/PRODUCTION_DEPLOYMENT_GUIDE.md

---

**Last Updated**: 2025-06-20
**Version**: 1.0.0
**Maintained By**: ACGS Operations Team
