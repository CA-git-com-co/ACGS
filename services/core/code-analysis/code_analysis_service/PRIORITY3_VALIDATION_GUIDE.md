# ACGS Code Analysis Engine - Priority 3 Validation Guide

## Overview

This guide provides comprehensive instructions for executing Priority 3: Integration and Testing Validation for the ACGS Code Analysis Engine. The validation suite ensures production readiness through systematic testing of infrastructure integration, performance benchmarks, monitoring setup, and constitutional compliance.

**Constitutional Hash:** `cdd01ef066bc6cf2`

## Success Criteria

✅ **All ACGS infrastructure services integrate successfully**
✅ **Performance targets met: P99 <10ms, >100 RPS, >85% cache hit rate**
✅ **Constitutional compliance hash cdd01ef066bc6cf2 maintained across all operations**
✅ **Zero critical integration failures**
✅ **Production monitoring fully operational**
✅ **Service ready for Phase 1 production deployment**

## Prerequisites

### 1. ACGS Infrastructure Services Running

Ensure the following ACGS services are running:

```bash
# PostgreSQL (Port 5439)
sudo systemctl status postgresql
# Should be accessible on localhost:5439

# Redis (Port 6389)  
sudo systemctl status redis
# Should be accessible on localhost:6389

# Auth Service (Port 8016)
curl http://localhost:8016/health

# Context Service (Port 8012) - Optional but recommended
curl http://localhost:8012/health

# Service Registry (Port 8001) - Optional but recommended
curl http://localhost:8001/registry/health
```

### 2. Environment Setup

```bash
# Navigate to service directory
cd /home/dislove/ACGS-2/services/core/code-analysis/code_analysis_service

# Set required environment variables
export POSTGRESQL_PASSWORD="test_password"
export JWT_SECRET_KEY="test_jwt_secret_key_for_development_only"
export REDIS_PASSWORD=""
export ENVIRONMENT="testing"

# Install Python dependencies
pip install -r requirements.txt

# Install additional testing dependencies
pip install matplotlib numpy pytest-cov requests asyncpg redis
```

### 3. Service Startup

Start the ACGS Code Analysis Engine:

```bash
# Option 1: Direct Python execution
python main.py

# Option 2: Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8007 --reload

# Verify service is running
curl http://localhost:8007/health
```

## Validation Test Suite

### Phase 1: Integration Testing

Tests ACGS infrastructure connectivity and service integration:

```bash
# Run comprehensive integration tests
python test_priority3_integration.py

# Expected output:
# ✓ PostgreSQL connectivity (port 5439): OK
# ✓ Redis connectivity (port 6389): OK  
# ✓ Auth Service connectivity (port 8016): OK
# ✓ Constitutional hash validation: PASS
# ✓ All integration tests passed!
```

**Key Integration Tests:**
- PostgreSQL database connectivity and queries
- Redis cache operations and performance
- Auth Service JWT token validation
- Context Service bidirectional communication
- Service Registry integration
- Constitutional compliance validation
- API endpoint functionality
- Middleware integration (auth, performance, constitutional)
- Error handling and graceful degradation

### Phase 2: Performance Benchmarking

Tests performance targets and scalability:

```bash
# Run comprehensive performance benchmarks
python test_performance_benchmarks.py

# Expected output:
# ✓ P99 latency: 8.45ms (target: <10ms) - PASS
# ✓ Throughput: 125.3 RPS (target: >100 RPS) - PASS
# ✓ Cache hit rate: 87.2% (target: >85%) - PASS
# ✓ Performance score: 92.5/100
# ✓ All performance targets met!
```

**Performance Tests:**
- **Latency Testing:** P99 <10ms for cached queries
- **Throughput Testing:** >100 RPS sustained load
- **Cache Performance:** >85% hit rate for repeated queries
- **Stress Testing:** Service stability under high load
- **O(1) Lookup Validation:** WINA optimization patterns
- **Constitutional Compliance Overhead:** Performance impact measurement

### Phase 3: Monitoring & Observability

Validates production monitoring setup:

```bash
# Run monitoring and observability validation
python test_monitoring_setup.py

# Expected output:
# ✓ Prometheus metrics: Found (7/7 required metrics)
# ✓ Health monitoring: 100% success rate
# ✓ Constitutional compliance tracking: PASS
# ✓ Structured logging: Valid JSON format
# ✓ Alerting configuration: All critical alerts configured
# ✓ Monitoring ready for production!
```

**Monitoring Tests:**
- **Prometheus Metrics:** Essential ACGS metrics collection
- **Health Check Monitoring:** Constitutional compliance validation
- **Structured Logging:** JSON format with constitutional hash
- **Alerting Configuration:** Critical performance and compliance alerts
- **Dashboard Setup:** Essential monitoring panels
- **Real-time Metrics:** Service performance tracking

### Phase 4: Constitutional Compliance

Validates constitutional compliance across all components:

```bash
# Constitutional compliance is validated in all phases
# Hash: cdd01ef066bc6cf2 must be present in:
# - Health endpoint responses
# - Metrics endpoint data
# - Error responses
# - Log entries
# - Database operations
```

## Comprehensive Validation Execution

### Option 1: Run All Tests Individually

```bash
# Run each test suite separately
python test_priority3_integration.py
python test_performance_benchmarks.py  
python test_monitoring_setup.py
```

### Option 2: Run Comprehensive Validation Suite

```bash
# Run all Priority 3 validation phases
python run_priority3_validation.py

# This executes:
# Phase 1: Integration Testing
# Phase 2: Performance Benchmarking  
# Phase 3: Monitoring & Observability Validation
# Phase 4: Constitutional Compliance Validation
# Final Report Generation
```

## Expected Results

### Success Output

```
================================================================================
PRIORITY 3 VALIDATION FINAL REPORT
================================================================================
Overall Score: 95.2/100
Production Ready: YES
Success Criteria Met: YES
Total Execution Time: 245.67 seconds

Phase Results:
✅ Integration: PASS
✅ Performance: PASS
⚠️ Monitoring: PARTIAL
✅ Constitutional: PASS

Success Criteria:
✅ ACGS Infrastructure Integration: MET
✅ Performance Targets Met: MET
✅ Constitutional Compliance Maintained: MET
✅ Zero Critical Failures: MET
✅ Monitoring Operational: MET

🎉 RECOMMENDATION: Service is READY for Phase 1 production deployment!
```

### Results Files Generated

- `priority3_comprehensive_validation_results.json` - Complete validation results
- `priority3_integration_test_results.json` - Integration test details
- `performance_benchmark_results.json` - Performance benchmark data
- `monitoring_validation_results.json` - Monitoring validation results

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL is running on port 5439
   sudo netstat -tlnp | grep 5439
   # Verify credentials
   psql -h localhost -p 5439 -U acgs_user -d acgs
   ```

2. **Redis Connection Failed**
   ```bash
   # Check Redis is running on port 6389
   sudo netstat -tlnp | grep 6389
   # Test connection
   redis-cli -p 6389 ping
   ```

3. **Auth Service Unavailable**
   ```bash
   # Check Auth Service status
   curl -v http://localhost:8016/health
   # Start Auth Service if needed
   ```

4. **Performance Targets Not Met**
   - Check system resources (CPU, memory)
   - Verify database connection pooling
   - Review cache configuration
   - Check for competing processes

5. **Constitutional Compliance Failures**
   - Verify constitutional hash: `cdd01ef066bc6cf2`
   - Check environment variables
   - Review service configuration
   - Validate middleware integration

### Debug Mode

Run tests with debug output:

```bash
export LOG_LEVEL="DEBUG"
python run_priority3_validation.py
```

## Production Deployment Readiness

Upon successful validation:

1. **✅ Infrastructure Integration Verified**
2. **✅ Performance Targets Achieved**
3. **✅ Constitutional Compliance Maintained**
4. **✅ Monitoring and Observability Operational**
5. **✅ Zero Critical Failures**

The service is ready for Phase 1 production deployment with:
- Sub-5ms P99 latency for critical paths
- >100 RPS sustained throughput
- >85% cache hit rate
- Constitutional compliance hash validation
- Comprehensive monitoring and alerting

## Next Steps

After successful Priority 3 validation:

1. **Deploy to staging environment**
2. **Run 24-hour stability monitoring**
3. **Conduct load testing at production scale**
4. **Validate backup and recovery procedures**
5. **Execute production deployment**

---

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Service Port:** `8007`  
**Validation Suite Version:** `1.0.0`  
**Last Updated:** `2024-07-05`
