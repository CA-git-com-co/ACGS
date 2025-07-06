# ACGS Service Issue Resolution Guide

**Date**: 2025-07-05  
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->  
**Status**: Production Ready

## 🎯 Quick Reference

### Critical Issues Identified

| Service | Issue | Priority | Status |
|---------|-------|----------|--------|
| **Integrity Service** | HTTP 500 errors | HIGH | 🔧 Resolution Available |
| **Evolutionary Computation** | Connection Failed | HIGH | 🔧 Resolution Available |

## 🚨 Issue 1: Integrity Service HTTP 500 Errors

### Root Cause Analysis

**Primary Causes**:
1. **Database Connection Issues**: PostgreSQL connection pool exhaustion
2. **Cryptographic Library Errors**: Missing or corrupted crypto dependencies
3. **Configuration Mismatch**: Incorrect environment variables
4. **Resource Constraints**: Memory/CPU limitations

### Resolution Procedures

#### Step 1: Immediate Diagnostics

```bash
# Check service status
curl -v http://localhost:8002/health

# Check detailed logs
docker logs acgs_integrity_service --tail 100 --follow

# Check resource usage
docker stats acgs_integrity_service

# Verify database connectivity
docker exec acgs_integrity_service pg_isready -h postgres -p 5432 -U acgs_user
```

#### Step 2: Configuration Validation

```bash
# Verify environment variables
docker exec acgs_integrity_service env | grep -E "(DATABASE_URL|REDIS_URL|CONSTITUTIONAL_HASH)"

# Expected values:
# DATABASE_URL=postgresql+asyncpg://acgs_user:acgs_password@postgres:5432/acgs_db
# REDIS_URL=redis://redis:6379/2
# CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
```

#### Step 3: Service Recovery

```bash
# Option 1: Restart service
docker restart acgs_integrity_service

# Option 2: Rebuild and restart
docker-compose -f infrastructure/docker/docker-compose.acgs.yml down integrity_service
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d integrity_service

# Option 3: Full reset (if needed)
docker-compose -f infrastructure/docker/docker-compose.acgs.yml down
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d postgres redis
sleep 30
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d integrity_service
```

#### Step 4: Verification

```bash
# Test health endpoint
curl http://localhost:8002/health

# Test integrity validation endpoint
curl -X POST http://localhost:8002/api/v1/integrity/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -H "X-Constitutional-Hash: cdd01ef066bc6cf2" \
  -d '{"data": "test_data", "hash": "test_hash"}'
```

## 🚨 Issue 2: Evolutionary Computation Service Connection Failed

### Root Cause Analysis

**Primary Causes**:
1. **Service Not Started**: Container not running
2. **Port Conflicts**: Port 8006 already in use
3. **Dependency Issues**: Missing required services
4. **Build Failures**: Docker image build problems

### Resolution Procedures

#### Step 1: Service Status Check

```bash
# Check if container is running
docker ps | grep ec_service

# Check if container exists but stopped
docker ps -a | grep ec_service

# Check port availability
netstat -tulpn | grep :8006
lsof -i :8006
```

#### Step 2: Start Service

```bash
# Start EC service specifically
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d ec_service

# If service fails to start, check logs
docker logs acgs_ec_service --tail 50

# Check dependencies are running
docker ps | grep -E "(postgres|redis|auth_service)"
```

#### Step 3: Troubleshoot Build Issues

```bash
# Rebuild service if needed
docker-compose -f infrastructure/docker/docker-compose.acgs.yml build ec_service

# Force rebuild without cache
docker-compose -f infrastructure/docker/docker-compose.acgs.yml build --no-cache ec_service

# Check Dockerfile and build context
ls -la infrastructure/docker/Dockerfile.acgs
```

#### Step 4: Configuration Verification

```bash
# Verify service configuration
docker exec acgs_ec_service env | grep -E "(SERVICE_PORT|DATABASE_URL|REDIS_URL)"

# Expected values:
# SERVICE_PORT=8006
# DATABASE_URL=postgresql+asyncpg://acgs_user:acgs_password@postgres:5432/acgs_db
# REDIS_URL=redis://redis:6379/6
```

#### Step 5: Service Verification

```bash
# Test health endpoint
curl http://localhost:8006/health

# Test WINA optimization endpoint
curl -X POST http://localhost:8006/api/v1/wina/optimize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -H "X-Constitutional-Hash: cdd01ef066bc6cf2" \
  -d '{"algorithm": "genetic", "parameters": {}}'
```

## 🔧 General Service Recovery Procedures

### Complete System Recovery

```bash
#!/bin/bash
# Complete ACGS system recovery script

echo "Starting ACGS system recovery..."

# Stop all services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml down

# Start infrastructure first
docker-compose -f docker-compose.postgresql.yml up -d
docker-compose -f docker-compose.redis.yml up -d

# Wait for infrastructure
echo "Waiting for infrastructure to be ready..."
sleep 30

# Verify infrastructure
pg_isready -h localhost -p 5439 -U acgs_user
redis-cli -h localhost -p 6389 ping

# Start all services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d

# Wait for services to start
sleep 60

# Verify all services
echo "Verifying service health..."
curl http://localhost:8016/health  # Auth
curl http://localhost:8001/health  # Constitutional AI
curl http://localhost:8002/health  # Integrity
curl http://localhost:8003/health  # Formal Verification
curl http://localhost:8004/health  # Governance Synthesis
curl http://localhost:8005/health  # Policy Governance
curl http://localhost:8006/health  # Evolutionary Computation

echo "Recovery complete!"
```

### Health Check Script

```bash
#!/bin/bash
# ACGS health check script

services=(
    "8016:Auth Service"
    "8001:Constitutional AI"
    "8002:Integrity Service"
    "8003:Formal Verification"
    "8004:Governance Synthesis"
    "8005:Policy Governance"
    "8006:Evolutionary Computation"
)

echo "ACGS Health Check Report - $(date)"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "=================================="

for service in "${services[@]}"; do
    port="${service%%:*}"
    name="${service##*:}"
    
    if curl -f -s "http://localhost:$port/health" > /dev/null; then
        echo "✅ $name (Port $port) - Healthy"
    else
        echo "❌ $name (Port $port) - Unhealthy"
    fi
done

echo "=================================="
echo "Infrastructure Status:"
pg_isready -h localhost -p 5439 -U acgs_user && echo "✅ PostgreSQL - Healthy" || echo "❌ PostgreSQL - Unhealthy"
redis-cli -h localhost -p 6389 ping > /dev/null && echo "✅ Redis - Healthy" || echo "❌ Redis - Unhealthy"
```

## 📋 Prevention Measures

### Monitoring Setup

1. **Automated Health Checks**: Run health check script every 5 minutes
2. **Log Monitoring**: Set up alerts for ERROR/CRITICAL log levels
3. **Resource Monitoring**: Monitor CPU/Memory usage
4. **Constitutional Compliance**: Verify hash in all responses

### Maintenance Schedule

- **Daily**: Run health checks, review error logs
- **Weekly**: Restart services, clear logs, update dependencies
- **Monthly**: Full system health audit, performance optimization

## 📞 Escalation Procedures

### Severity Levels

1. **P1 - Critical**: Multiple services down, constitutional compliance failing
2. **P2 - High**: Single service down, performance degraded
3. **P3 - Medium**: Service errors, intermittent issues
4. **P4 - Low**: Minor issues, optimization opportunities

### Contact Matrix

- **P1/P2**: Immediate restart procedures, escalate if not resolved in 15 minutes
- **P3**: Standard troubleshooting, escalate if not resolved in 1 hour
- **P4**: Schedule during maintenance window

---

**Success Criteria**: All services healthy, constitutional hash validated, P99 latency <5ms
