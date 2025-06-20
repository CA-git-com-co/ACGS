# Service-Specific Troubleshooting Guide

This guide provides detailed troubleshooting procedures for each of the 7 core ACGS-1 services, including common error scenarios, diagnostic commands, and step-by-step resolution procedures.

## 🔐 Authentication Service (Port 8000)

### Common Issues

#### Issue: JWT Token Validation Failures
**Symptoms:**
- 401 Unauthorized responses across services
- "Invalid token" errors in logs
- Users unable to authenticate

**Diagnosis:**
```bash
# Check auth service health
curl http://localhost:8000/health

# Verify JWT secret configuration
grep JWT_SECRET .env

# Check token expiration
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/validate
```

**Resolution:**
```bash
# 1. Restart auth service
pkill -f "uvicorn.*8000"
cd services/platform/authentication/auth_service
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. Regenerate JWT secret if compromised
export JWT_SECRET=$(openssl rand -base64 32)

# 3. Clear token cache
redis-cli FLUSHDB
```

#### Issue: Database Connection Failures
**Symptoms:**
- Service fails to start
- "Database connection refused" errors
- User data not persisting

**Diagnosis:**
```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Check database logs
docker logs acgs_postgres_db

# Verify connection pool
curl http://localhost:8000/api/v1/status | jq '.database'
```

**Resolution:**
```bash
# 1. Restart PostgreSQL
docker restart acgs_postgres_db

# 2. Check database configuration
grep DATABASE_URL .env

# 3. Run database migrations
cd services/platform/authentication/auth_service
alembic upgrade head
```

## 🏛️ Constitutional AI Service (Port 8001)

### Common Issues

#### Issue: Constitutional Validation Failures
**Symptoms:**
- Policies failing constitutional compliance checks
- Low compliance scores (<0.8)
- Constitutional hash mismatches

**Diagnosis:**
```bash
# Check constitutional hash
curl http://localhost:8001/api/v1/constitutional/hash

# Verify compliance scoring
curl -X POST http://localhost:8001/api/v1/constitutional/validate \
  -H "Content-Type: application/json" \
  -d '{"policy": "test policy content"}'

# Check constitutional cache
redis-cli KEYS "acgs:constitutional:*"
```

**Resolution:**
```bash
# 1. Clear constitutional cache
redis-cli DEL $(redis-cli KEYS "acgs:constitutional:*")

# 2. Restart constitutional AI service
pkill -f "uvicorn.*8001"
cd services/core/constitutional-ai/ac_service
uvicorn app.main:app --host 0.0.0.0 --port 8001 &

# 3. Verify constitutional hash
export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
```

#### Issue: High Response Times (>500ms)
**Symptoms:**
- Slow constitutional validation
- Timeout errors
- Performance degradation

**Diagnosis:**
```bash
# Monitor response times
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8001/health

# Check resource usage
docker stats ac_service

# Monitor database queries
tail -f services/core/constitutional-ai/ac_service/logs/ac_service.log
```

**Resolution:**
```bash
# 1. Optimize database queries
psql $DATABASE_URL -c "REINDEX DATABASE acgs_pgp_db;"

# 2. Increase cache TTL
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 3. Scale service instances
docker-compose up --scale ac_service=3
```

## 🔒 Integrity Service (Port 8002)

### Common Issues

#### Issue: Audit Log Corruption
**Symptoms:**
- Missing audit entries
- Integrity verification failures
- Cryptographic signature mismatches

**Diagnosis:**
```bash
# Check audit log integrity
curl http://localhost:8002/api/v1/audit/verify

# Verify cryptographic signatures
curl http://localhost:8002/api/v1/integrity/check

# Check log file permissions
ls -la services/platform/integrity/integrity_service/logs/
```

**Resolution:**
```bash
# 1. Backup current logs
cp -r services/platform/integrity/integrity_service/logs/ logs_backup_$(date +%Y%m%d)

# 2. Regenerate integrity signatures
curl -X POST http://localhost:8002/api/v1/integrity/regenerate

# 3. Restart integrity service
pkill -f "uvicorn.*8002"
cd services/platform/integrity/integrity_service
uvicorn app.main:app --host 0.0.0.0 --port 8002 &
```

## ⚖️ Formal Verification Service (Port 8003)

### Common Issues

#### Issue: Z3 SMT Solver Failures
**Symptoms:**
- Verification timeouts
- "Z3 solver error" messages
- Proof generation failures

**Diagnosis:**
```bash
# Test Z3 solver
python -c "import z3; print(z3.get_version_string())"

# Check verification logs
tail -f services/core/formal-verification/fv_service/logs/fv_service.log

# Test verification endpoint
curl -X POST http://localhost:8003/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"policy": "test policy", "properties": ["safety"]}'
```

**Resolution:**
```bash
# 1. Reinstall Z3 solver
pip uninstall z3-solver
pip install z3-solver==4.12.2.0

# 2. Increase solver timeout
export Z3_TIMEOUT=60000

# 3. Restart verification service
pkill -f "uvicorn.*8003"
cd services/core/formal-verification/fv_service
uvicorn app.main:app --host 0.0.0.0 --port 8003 &
```

## 🤖 Governance Synthesis Service (Port 8004)

### Common Issues

#### Issue: LLM Model Failures
**Symptoms:**
- Policy generation failures
- "Model unavailable" errors
- Low consensus scores

**Diagnosis:**
```bash
# Check model status
curl http://localhost:8004/api/v1/models/status

# Test model connectivity
curl -X POST http://localhost:8004/api/v1/synthesis/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test prompt"}'

# Check model configuration
grep -E "(QWEN|DEEPSEEK)" .env
```

**Resolution:**
```bash
# 1. Restart model connections
curl -X POST http://localhost:8004/api/v1/models/restart

# 2. Switch to fallback models
export ENABLE_FALLBACK_MODELS=true

# 3. Clear model cache
redis-cli DEL $(redis-cli KEYS "*llm_cache*")
```

## 📋 Policy Governance Service (Port 8005)

### Common Issues

#### Issue: OPA Policy Compilation Failures
**Symptoms:**
- Policy enforcement errors
- "OPA compilation failed" messages
- Inconsistent policy application

**Diagnosis:**
```bash
# Check OPA status
curl http://localhost:8181/health

# Test policy compilation
curl -X POST http://localhost:8005/api/v1/policies/compile \
  -H "Content-Type: application/json" \
  -d '{"policy": "test policy content"}'

# Check OPA logs
docker logs opa_server
```

**Resolution:**
```bash
# 1. Restart OPA server
docker restart opa_server

# 2. Reload policy bundles
curl -X POST http://localhost:8181/v1/bundles/reload

# 3. Clear policy cache
curl -X DELETE http://localhost:8181/v1/data
```

## 🧬 Evolutionary Computation Service (Port 8006)

### Common Issues

#### Issue: WINA Optimization Failures
**Symptoms:**
- Optimization processes not converging
- High resource usage
- Performance degradation

**Diagnosis:**
```bash
# Check WINA performance metrics
curl http://localhost:8006/api/v1/wina/performance

# Monitor optimization processes
curl http://localhost:8006/api/v1/oversight/status

# Check resource usage
top -p $(pgrep -f "uvicorn.*8006")
```

**Resolution:**
```bash
# 1. Adjust optimization parameters
curl -X POST http://localhost:8006/api/v1/wina/configure \
  -H "Content-Type: application/json" \
  -d '{"optimization_level": "medium", "max_iterations": 50}'

# 2. Restart optimization processes
curl -X POST http://localhost:8006/api/v1/oversight/restart

# 3. Clear optimization cache
redis-cli DEL $(redis-cli KEYS "*wina*")
```

## 🔧 Cross-Service Issues

### Issue: Service Communication Failures
**Symptoms:**
- Services unable to communicate
- Timeout errors between services
- Inconsistent data across services

**Diagnosis:**
```bash
# Test service connectivity
for port in 8000 8001 8002 8003 8004 8005 8006; do
  echo "Testing port $port:"
  curl -s http://localhost:$port/health | jq '.status'
done

# Check network configuration
docker network ls
docker network inspect acgs_default
```

**Resolution:**
```bash
# 1. Restart all services in order
./scripts/stop_all_services.sh
./scripts/start_all_services.sh

# 2. Check service discovery
# Ensure services use correct hostnames in configuration

# 3. Verify firewall rules
sudo ufw status
```

### Issue: Database Performance Problems
**Symptoms:**
- Slow query responses
- High database CPU usage
- Connection pool exhaustion

**Diagnosis:**
```bash
# Check database performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"

# Monitor slow queries
psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check connection pool
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
```

**Resolution:**
```bash
# 1. Optimize database
psql $DATABASE_URL -c "VACUUM ANALYZE;"
psql $DATABASE_URL -c "REINDEX DATABASE acgs_pgp_db;"

# 2. Increase connection pool
export DATABASE_POOL_SIZE=30
export DATABASE_MAX_OVERFLOW=50

# 3. Restart database
docker restart acgs_postgres_db
```

## 📊 Performance Monitoring

### Real-time Monitoring Commands
```bash
# Monitor all service health
watch -n 5 'for port in 8000 8001 8002 8003 8004 8005 8006; do echo "Port $port: $(curl -s http://localhost:$port/health | jq -r .status)"; done'

# Monitor resource usage
watch -n 2 'docker stats --no-stream'

# Monitor database connections
watch -n 5 'psql $DATABASE_URL -c "SELECT count(*) as connections FROM pg_stat_activity;"'
```

### Log Analysis
```bash
# Aggregate service logs
tail -f services/*/logs/*.log | grep ERROR

# Monitor constitutional compliance
grep "constitutional" services/*/logs/*.log | tail -20

# Track performance metrics
grep "response_time" services/*/logs/*.log | tail -20
```
