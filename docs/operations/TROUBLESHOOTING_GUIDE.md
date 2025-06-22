# ACGS-1 API Versioning Troubleshooting Guide

**Version:** 1.0  
**Last Updated:** 2025-06-22  
**Owner:** API Operations Team

## 🔍 Overview

This guide provides systematic troubleshooting procedures for common issues with the ACGS-1 API versioning system.

## 🚀 Quick Diagnostic Commands

### System Health Check

```bash
# Overall system status
python3 tools/versioning/health_checker.py --comprehensive

# Version-specific health
python3 tools/versioning/health_checker.py --version=v2.0.0

# Check all active versions
kubectl get pods -n acgs-api -l component=api-server --show-labels
```

### Performance Quick Check

```bash
# Response time by version
curl -w "@curl-format.txt" -H "API-Version: v2.0.0" https://api.acgs.gov/api/v2/health

# Check transformation overhead
python3 tools/versioning/measure_performance.py --all-versions

# Monitor real-time metrics
watch -n 5 'curl -s https://api.acgs.gov/metrics | grep api_version_response_duration'
```

## 🔧 Common Issues and Solutions

### Issue 1: Version Detection Not Working

**Symptoms:**

- Clients receive wrong API version responses
- Version headers not being recognized
- Default version always returned

**Diagnostic Steps:**

```bash
# 1. Test version detection methods
curl -H "API-Version: v2.0.0" https://api.acgs.gov/api/v2/test
curl https://api.acgs.gov/api/v2/test?version=v2.0.0
curl https://api.acgs.gov/api/v1/test

# 2. Check middleware configuration
kubectl get configmap version-routing-config -o yaml

# 3. Verify middleware is running
kubectl logs -n acgs-api -l component=version-middleware --tail=50
```

**Common Causes & Solutions:**

1. **Middleware Not Loaded:**

   ```bash
   # Check if middleware is in the pipeline
   kubectl describe deployment acgs-api-gateway | grep -A 10 "Environment"

   # Restart with middleware enabled
   kubectl set env deployment/acgs-api-gateway ENABLE_VERSION_MIDDLEWARE=true
   kubectl rollout restart deployment/acgs-api-gateway
   ```

2. **Invalid Version Format:**

   ```bash
   # Check version validation rules
   python3 tools/versioning/validate_version_format.py --test-all

   # Update validation if needed
   kubectl patch configmap version-routing-config --patch '{"data":{"version_pattern":"v\\d+\\.\\d+\\.\\d+"}}'
   ```

3. **Header Case Sensitivity:**
   ```bash
   # Test different header formats
   curl -H "api-version: v2.0.0" https://api.acgs.gov/test
   curl -H "API-Version: v2.0.0" https://api.acgs.gov/test
   curl -H "X-API-Version: v2.0.0" https://api.acgs.gov/test
   ```

### Issue 2: Response Transformation Failures

**Symptoms:**

- Clients receive data in wrong format
- Transformation errors in logs
- Inconsistent response structures

**Diagnostic Steps:**

```bash
# 1. Test specific transformations
python3 tools/versioning/test_transformations.py --from=v1.5.0 --to=v2.0.0

# 2. Check transformer logs
kubectl logs -n acgs-api -l component=response-transformer --grep="ERROR"

# 3. Validate transformation rules
python3 tools/versioning/validate_transformation_rules.py
```

**Solutions:**

1. **Missing Transformation Rules:**

   ```bash
   # Check available transformers
   ls -la services/shared/versioning/transformers/

   # Add missing transformer
   python3 tools/versioning/generate_transformer.py --from=v1.5.0 --to=v2.1.0
   ```

2. **Schema Mismatch:**

   ```bash
   # Compare schemas
   python3 tools/versioning/compare_schemas.py --v1=v1.5.0 --v2=v2.0.0

   # Update transformation mapping
   vim services/shared/versioning/transformers/v1_to_v2_transformer.py
   ```

3. **Performance Issues:**

   ```bash
   # Profile transformation performance
   python3 tools/versioning/profile_transformations.py --version=v2.0.0

   # Enable transformation caching
   kubectl patch configmap api-versioning-config --patch '{"data":{"enable_transformation_cache":"true"}}'
   ```

### Issue 3: High Error Rates

**Symptoms:**

- Increased 4xx/5xx responses
- Client authentication failures
- Version compatibility errors

**Diagnostic Steps:**

```bash
# 1. Analyze error patterns
python3 tools/monitoring/analyze_errors.py --last=1h --by-version

# 2. Check error logs by version
kubectl logs -n acgs-api -l version=v2.0.0 --grep="ERROR\|WARN" --tail=100

# 3. Test endpoint functionality
python3 tests/integration/test_all_versions.py --verbose
```

**Solutions:**

1. **Authentication Issues:**

   ```bash
   # Check JWT validation
   python3 tools/auth/validate_jwt.py --version=v2.0.0

   # Update auth configuration
   kubectl patch secret api-auth-config --patch '{"data":{"jwt_secret":"<new-secret>"}}'
   ```

2. **Rate Limiting:**

   ```bash
   # Check rate limit configuration
   kubectl get configmap rate-limit-config -o yaml

   # Adjust limits if needed
   kubectl patch configmap rate-limit-config --patch '{"data":{"requests_per_minute":"1000"}}'
   ```

3. **Database Connection Issues:**

   ```bash
   # Check database connectivity
   python3 tools/database/test_connections.py --all-versions

   # Check connection pool status
   kubectl exec -it deployment/acgs-api-v2 -- python3 -c "from db import pool; print(pool.status())"
   ```

### Issue 4: Slow Response Times

**Symptoms:**

- Response times > 100ms (p95)
- Client timeouts
- Performance degradation alerts

**Diagnostic Steps:**

```bash
# 1. Measure response times by version
python3 tools/monitoring/measure_response_times.py --all-versions --duration=5m

# 2. Profile slow endpoints
python3 tools/profiling/profile_endpoints.py --version=v2.0.0 --slow-only

# 3. Check database query performance
python3 tools/database/analyze_slow_queries.py --version=v2.0.0
```

**Solutions:**

1. **Database Optimization:**

   ```bash
   # Analyze query performance
   python3 tools/database/query_analyzer.py --version=v2.0.0

   # Add missing indexes
   python3 tools/database/suggest_indexes.py --apply
   ```

2. **Caching Issues:**

   ```bash
   # Check cache hit rates
   python3 tools/caching/cache_stats.py --version=v2.0.0

   # Clear cache if needed
   python3 tools/caching/clear_cache.py --version=v2.0.0
   ```

3. **Resource Constraints:**

   ```bash
   # Check resource usage
   kubectl top pods -n acgs-api -l version=v2.0.0

   # Scale up if needed
   kubectl scale deployment acgs-api-v2 --replicas=5
   ```

### Issue 5: Deprecation Warnings Not Appearing

**Symptoms:**

- Clients not receiving deprecation headers
- Missing sunset information
- No migration guidance

**Diagnostic Steps:**

```bash
# 1. Test deprecation headers
curl -I -H "API-Version: v1.5.0" https://api.acgs.gov/api/v1/deprecated-endpoint

# 2. Check deprecation configuration
kubectl get configmap deprecation-config -o yaml

# 3. Verify deprecation middleware
kubectl logs -n acgs-api -l component=deprecation-middleware --tail=50
```

**Solutions:**

1. **Missing Deprecation Configuration:**

   ```bash
   # Add deprecation metadata
   python3 tools/versioning/configure_deprecation.py --version=v1.5.0 --sunset-date=2025-12-31

   # Restart services
   kubectl rollout restart deployment/acgs-api-v1
   ```

2. **Header Configuration:**

   ```bash
   # Check header configuration
   python3 tools/versioning/validate_deprecation_headers.py

   # Update header templates
   vim config/deprecation/header_templates.json
   ```

## 🔍 Advanced Diagnostics

### Memory and Resource Analysis

```bash
# Check memory usage by version
kubectl top pods -n acgs-api --sort-by=memory

# Analyze memory leaks
python3 tools/diagnostics/memory_profiler.py --version=v2.0.0 --duration=10m

# Check for resource limits
kubectl describe pods -n acgs-api -l version=v2.0.0 | grep -A 5 "Limits\|Requests"
```

### Network Connectivity

```bash
# Test inter-service communication
python3 tools/network/test_service_connectivity.py --all-versions

# Check DNS resolution
nslookup acgs-api-v2.acgs-api.svc.cluster.local

# Verify load balancer configuration
kubectl get services -n acgs-api -o wide
```

### Configuration Validation

```bash
# Validate all configuration files
python3 tools/config/validate_all_configs.py

# Check for configuration drift
python3 tools/config/compare_configs.py --env1=staging --env2=production

# Verify environment variables
kubectl exec deployment/acgs-api-v2 -- env | grep -i version
```

## 📊 Monitoring and Metrics

### Key Metrics to Monitor

```bash
# Response time percentiles
curl -s https://api.acgs.gov/metrics | grep api_version_response_duration

# Error rates by version
curl -s https://api.acgs.gov/metrics | grep api_version_requests_total

# Transformation success rates
curl -s https://api.acgs.gov/metrics | grep api_version_transformation_success

# Deprecation usage
curl -s https://api.acgs.gov/metrics | grep api_deprecated_endpoint_usage
```

### Log Analysis

```bash
# Search for specific error patterns
kubectl logs -n acgs-api --all-containers=true | grep -E "(ERROR|FATAL|version.*fail)"

# Analyze request patterns
python3 tools/logs/analyze_request_patterns.py --last=1h --group-by=version

# Generate log summary
python3 tools/logs/log_summary.py --version=v2.0.0 --last=24h
```

## 🛠️ Maintenance Commands

### Regular Health Checks

```bash
# Daily health check
python3 tools/maintenance/daily_health_check.py

# Weekly performance review
python3 tools/maintenance/weekly_performance_review.py

# Monthly compatibility audit
python3 tools/maintenance/monthly_compatibility_audit.py
```

### Cache Management

```bash
# Clear all version caches
python3 tools/caching/clear_all_caches.py

# Warm up caches
python3 tools/caching/warm_up_caches.py --all-versions

# Cache statistics
python3 tools/caching/cache_report.py
```

### Database Maintenance

```bash
# Update statistics
python3 tools/database/update_statistics.py --all-versions

# Cleanup old data
python3 tools/database/cleanup_old_data.py --older-than=90d

# Backup critical data
python3 tools/database/backup_version_data.py
```

## 📞 When to Escalate

### Immediate Escalation (Call On-Call)

- Complete API unavailability
- Data corruption detected
- Security breach suspected
- Error rates > 10%

### Standard Escalation (Create Ticket)

- Performance degradation > 50%
- Version compatibility issues affecting multiple clients
- Monitoring alerts not resolving within SLA

### Information Only

- Minor performance variations
- Single client issues
- Documentation requests

---

## 📚 Additional Resources

- [Emergency Procedures](EMERGENCY_PROCEDURES.md)
- [Version Lifecycle Management](VERSION_LIFECYCLE_MANAGEMENT.md)
- [Monitoring Guide](MONITORING_GUIDE.md)
- [API Documentation](../api/)

**Support:** api-team@acgs.gov  
**Emergency:** +1-555-ACGS-911  
**Status:** https://status.acgs.gov
