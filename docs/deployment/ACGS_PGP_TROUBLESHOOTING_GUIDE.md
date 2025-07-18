# ACGS-PGP Troubleshooting Guide

**Version**: 1.0.0
**Date**: 2025-06-27
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This guide provides comprehensive troubleshooting procedures for the ACGS-PGP system, organized by priority level and common scenarios.

## Priority System

### Critical (2 hours)

- Constitutional compliance failures
- Security vulnerabilities
- System-wide outages
- Emergency shutdown failures

### High (24-48 hours)

- Service startup failures
- Performance degradation
- AI model integration issues
- Database connectivity problems

### Moderate (1 week)

- Package manager issues
- Configuration inconsistencies
- Non-critical test failures
- Documentation gaps

### Low (2 weeks)

- Optimization opportunities
- Enhancement requests
- Minor UI issues
- Non-essential features

## Critical Issues (2h Response)

### Constitutional Compliance Failures

#### Symptoms

- Compliance score <95%
- Constitutional hash mismatches
- DGM safety pattern violations
- Policy validation failures

#### Diagnostic Commands

```bash
# Check constitutional compliance across all services
for port in 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010 8011 8012; do
  echo "Service on port $port:"
  curl -s http://localhost:$port/constitutional/compliance | jq .
done
```

#### Resolution Steps

1. **Immediate Actions**:

   ```bash
   # Stop non-compliant services
   curl -X POST http://localhost:<port>/emergency/shutdown

   # Verify constitutional hash
   grep -n "cdd01ef066bc6cf2" infrastructure/docker/docker-compose.acgs.yml
   ```

2. **Root Cause Analysis**:

   ```bash
   # Check service logs for compliance errors
   tail -f logs/ac_service.log | grep -i "constitutional\|compliance"

   # Validate OPA policies
   curl -s http://localhost:8181/health
   ```

3. **Remediation**:

   ```bash
   # Restart services with correct configuration
   ./scripts/start_all_services.sh

   # Validate compliance
   ./scripts/test_setup_scripts_comprehensive.sh
   ```

### Emergency Shutdown Failures

#### Symptoms

- Emergency endpoints not responding
- Shutdown time >30 minutes
- Services not stopping gracefully
- Constitutional violations during shutdown

#### Diagnostic Commands

```bash
# Test emergency shutdown endpoints
for port in {8000..8006}; do
  echo "Testing emergency shutdown for port $port:"
  curl -X POST -w "%{http_code}\n" http://localhost:$port/emergency/shutdown
done

# Check process status
ps aux | grep uvicorn
```

#### Resolution Steps

1. **Force Shutdown**:

   ```bash
   # Kill all uvicorn processes
   pkill -f "uvicorn.*:800[0-6]"

   # Verify all processes stopped
   ps aux | grep uvicorn
   ```

2. **Implement Emergency Endpoints**:

   ```bash
   # Add emergency endpoints to services missing them
   # Update service code to include /emergency/shutdown
   ```

3. **Test Recovery**:

   ```bash
   # Restart services
   ./scripts/start_all_services.sh

   # Test emergency shutdown capability
   ./scripts/test_emergency_shutdown.sh
   ```

## High Priority Issues (24-48h)

### Service Startup Failures

#### Symptoms

- Services fail to start
- Health checks return errors
- Port conflicts
- Dependency issues

#### Diagnostic Commands

```bash
# Check service status
./scripts/start_all_services.sh

# Check port availability
netstat -tulpn | grep :800[0-6]

# Check logs for errors
tail -f logs/*.log

# Verify dependencies
docker ps | grep -E "(postgres|redis|opa)"
```

#### Resolution Steps

1. **Check Dependencies**:

   ```bash
   # Start infrastructure services
   docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d postgres redis opa

   # Wait for services to be ready
   sleep 30
   ```

2. **Resolve Port Conflicts**:

   ```bash
   # Find processes using ports
   lsof -i :8000-8006

   # Kill conflicting processes
   kill -9 <PID>
   ```

3. **Fix Configuration Issues**:

   ```bash
   # Verify environment variables
   source config/env/config/environments/development.env
   echo $CONSTITUTIONAL_HASH

   # Check service configuration
   grep -n "8000\|8001\|8002\|8003\|8004\|8005\|8006" scripts/start_all_services.sh
   ```

### Performance Degradation

#### Symptoms

- Response time >2 seconds
- Throughput <1000 RPS
- High CPU/memory usage
- Database connection issues

#### Diagnostic Commands

```bash
# Test performance
./scripts/test_performance_validation.sh

# Check resource usage
docker stats
htop

# Test individual service response times
for port in {8000..8006}; do
  time curl -s http://localhost:$port/health
done
```

#### Resolution Steps

1. **Resource Optimization**:

   ```bash
   # Check resource limits
   grep -A 10 "resources:" infrastructure/docker/docker-compose.acgs.yml

   # Increase limits if needed (edit docker-compose.acgs.yml)
   # memory: 1Gi -> 2Gi
   # cpus: '500m' -> '1000m'
   ```

2. **Database Optimization**:

   ```bash
   # Check database connections
   docker exec acgs_postgres psql -U acgs_user -d acgs_db -c "SELECT count(*) FROM pg_stat_activity;"

   # Optimize queries (check slow query logs)
   ```

3. **Service Optimization**:
   ```bash
   # Restart services with optimized configuration
   docker-compose -f infrastructure/docker/docker-compose.acgs.yml restart
   ```

### AI Model Integration Issues

#### Symptoms

- AI model API errors
- Authentication failures
- Model response timeouts
- Constitutional reasoning failures

#### Diagnostic Commands

```bash
# Check API keys
echo $GOOGLE_GEMINI_API_KEY | cut -c1-10
echo $DEEPSEEK_R1_API_KEY | cut -c1-10
echo $NVIDIA_QWEN_API_KEY | cut -c1-10

# Test model endpoints
curl -H "Authorization: Bearer $GOOGLE_GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models

# Check model configuration
cat config/ai-models/model-config.yaml
```

#### Resolution Steps

1. **Verify API Keys**:

   ```bash
   # Test each API key
   # Google Gemini
   curl -H "Authorization: Bearer $GOOGLE_GEMINI_API_KEY" \
     "https://generativelanguage.googleapis.com/v1beta/models"

   # DeepSeek R1
   curl -H "Authorization: Bearer $DEEPSEEK_R1_API_KEY" \
     "https://api.deepseek.com/v1/models"

   # NVIDIA Qwen
   curl -H "Authorization: Bearer $NVIDIA_QWEN_API_KEY" \
     "https://integrate.api.nvidia.com/v1/models"
   ```

2. **Update Configuration**:

   ```bash
   # Update environment variables
   nano config/env/config/environments/development.env

   # Restart services to pick up new configuration
   ./scripts/start_all_services.sh
   ```

3. **Test Integration**:

   ```bash
   # Test constitutional AI service
   curl -s http://localhost:8002/constitutional/compliance

   # Verify AI model responses
   curl -X POST http://localhost:8002/ai/models/test
   ```

## Moderate Priority Issues (1 week)

### Package Manager Issues

#### Symptoms

- npm used instead of pnpm
- Cargo build failures
- Dependency conflicts
- Lock file inconsistencies

#### Resolution Steps

```bash
# Install pnpm if missing
npm install -g pnpm

# Update Node.js dependencies
cd applications/governance-dashboard
pnpm install

# Fix Rust dependencies
cd blockchain
cargo update
cargo build --release

# Verify package managers
which pnpm
which cargo
which uv
```

### Configuration Inconsistencies

#### Symptoms

- Environment variable mismatches
- Service configuration drift
- Resource limit inconsistencies

#### Resolution Steps

```bash
# Standardize configuration
./scripts/setup/project_setup.sh

# Verify constitutional hash consistency
grep -r "cdd01ef066bc6cf2" . --include="*.yml" --include="*.sh" --include="*.py"

# Update resource limits
# Edit infrastructure/docker/docker-compose.acgs.yml
# Ensure all services have: 200m/500m CPU, 512Mi/1Gi memory
```

## Diagnostic Tools

### Health Check Commands

```bash
# Basic health checks
for port in {8000..8006}; do
  curl -s http://localhost:$port/health
done

# Constitutional compliance checks
for port in {8000..8006}; do
  curl -s http://localhost:$port/constitutional/compliance
done

# DGM safety pattern checks
for port in {8000..8006}; do
  curl -s http://localhost:$port/dgm/sandbox/status
done
```

### Log Analysis

```bash
# View all service logs
tail -f logs/*.log

# Search for errors
grep -i error logs/*.log

# Search for constitutional violations
grep -i "constitutional\|compliance" logs/*.log

# Search for performance issues
grep -i "timeout\|slow\|performance" logs/*.log
```

### Performance Monitoring

```bash
# System resource usage
htop
docker stats

# Network connectivity
netstat -tulpn | grep :800[0-6]

# Database performance
docker exec acgs_postgres psql -U acgs_user -d acgs_db -c "SELECT * FROM pg_stat_activity;"
```

## Recovery Procedures

### Service Recovery

```bash
# Stop all services
pkill -f "uvicorn.*:800[0-6]"

# Clean up PIDs
rm -f pids/*.pid

# Restart infrastructure
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d postgres redis opa

# Restart services
./scripts/start_all_services.sh

# Validate recovery
./scripts/test_setup_scripts_comprehensive.sh
```

### Database Recovery

```bash
# Backup current state
docker exec acgs_postgres pg_dump -U acgs_user acgs_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restart database
docker-compose -f infrastructure/docker/docker-compose.acgs.yml restart postgres

# Run migrations
cd services/shared && alembic upgrade head
```

### Configuration Recovery

```bash
# Reset to known good configuration
git checkout HEAD -- config/ infrastructure/

# Regenerate configuration
./scripts/setup/project_setup.sh

# Validate configuration
./scripts/test_setup_scripts_comprehensive.sh
```

## Prevention Strategies

### Regular Maintenance

```bash
# Weekly health checks
./scripts/run_all_setup_tests.sh

# Monthly dependency updates
./scripts/setup/install_dependencies.sh

# Quarterly security audits
./scripts/security_audit.py
```

### Monitoring Setup

```bash
# Set up monitoring alerts for:
# - Constitutional compliance <95%
# - Response time >2000ms
# - Service availability <99%
# - Emergency shutdown events
```

### Documentation Maintenance

```bash
# Keep troubleshooting procedures updated
# Document new issues and resolutions
# Update runbooks based on incidents
```

## Escalation Procedures

### When to Escalate

- Constitutional compliance cannot be restored within 2 hours
- Emergency shutdown procedures fail
- Security vulnerabilities detected
- Data integrity compromised

### Escalation Contacts

- **Technical Lead**: For architectural decisions
- **Security Team**: For security incidents
- **Operations Team**: For infrastructure issues
- **AI Team**: For model integration problems

## Escalation Procedures

### When to Escalate

- Constitutional compliance cannot be restored within 2 hours
- Emergency shutdown procedures fail
- Security vulnerabilities detected
- Data integrity compromised

### Escalation Contacts

- **Technical Lead**: For architectural decisions
- **Security Team**: For security incidents
- **Operations Team**: For infrastructure issues
- **AI Team**: For model integration problems

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md.backup)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs_consolidated_archive_20250710_120000/deployment/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md.backup)
- [ACGE Testing and Validation Framework](../compliance/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs_consolidated_archive_20250710_120000/deployment/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md.backup)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md.backup)
- [ACGS Implementation Guide](ACGS_IMPLEMENTATION_GUIDE.md.backup)
- [Service Status Dashboard](../operations/SERVICE_STATUS.md.backup)



## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->
**Last Updated**: 2025-06-27
**Version**: 1.0.0
