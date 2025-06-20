# Constitutional Cache System API Documentation

**Version**: v3.0.0  
**Last Updated**: 2025-06-20  
**Service**: Shared Constitutional Cache System  
**Base URL**: Integrated across all services  

## Overview

The Constitutional Cache System provides enterprise-grade Redis-based caching for constitutional validation results across all ACGS-1 services. It implements multi-layer caching with automatic TTL management, constitutional compliance validation, and ultra-low latency performance targets.

## Architecture

### Multi-Layer Caching
- **L1 Memory Cache**: In-memory LRU cache for ultra-fast access
- **L2 Redis Cache**: Distributed Redis cache for persistence and sharing
- **Constitutional Validation**: Automatic constitutional hash validation for all cached data

### Performance Targets
- **Cache Hit Rate**: >80%
- **Lookup Latency**: <2ms for 95% of requests
- **Constitutional Validation**: <5ms for 95% of validations
- **Cache Invalidation**: <100ms

## Core Components

### ConstitutionalCache Class

#### Initialization
```python
from shared.constitutional_cache import ConstitutionalCache

cache = ConstitutionalCache(
    redis_url="redis://localhost:6379",
    constitutional_hash="cdd01ef066bc6cf2",
    cache_ttl=300
)
await cache.initialize()
```

#### Cache Operations

##### Set Validation Result
```python
await cache.set_validation_result(
    cache_key="policy_validation_123",
    result={
        "is_valid": True,
        "compliance_score": 0.94,
        "validation_timestamp": "2025-06-20T10:30:00Z"
    },
    ttl=600
)
```

##### Get Validation Result
```python
result = await cache.get_validation_result("policy_validation_123")
if result:
    print(f"Compliance Score: {result['compliance_score']}")
```

##### Cache Key Generation
```python
cache_key = cache.generate_cache_key(
    operation_type="policy_validation",
    data={"policy_id": "pol_123", "version": "v1.0"}
)
```

## Cache Strategies

### Policy Fragment Caching
```json
{
  "ttl_seconds": 300,
  "max_size_mb": 100,
  "compression": true,
  "strategy": "policy_fragments"
}
```

### Constitutional Validation Caching
```json
{
  "ttl_seconds": 3600,
  "max_size_mb": 50,
  "compression": false,
  "strategy": "constitutional_validations"
}
```

### LLM Response Caching
```json
{
  "ttl_seconds": 1800,
  "max_size_mb": 200,
  "compression": true,
  "strategy": "llm_responses"
}
```

### Governance Decision Caching
```json
{
  "ttl_seconds": 600,
  "max_size_mb": 75,
  "compression": true,
  "strategy": "governance_decisions"
}
```

## Configuration

### Environment Variables
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379)
- `CONSTITUTIONAL_HASH`: Reference constitutional hash (default: cdd01ef066bc6cf2)
- `CACHE_TTL_DEFAULT`: Default TTL in seconds (default: 300)
- `CACHE_MAX_MEMORY_SIZE`: Maximum memory cache size (default: 1000)

### Redis Configuration
```json
{
  "host": "localhost",
  "port": 6379,
  "db": 0,
  "max_connections": 100,
  "socket_keepalive": true,
  "health_check_interval": 30
}
```

## API Endpoints

### Cache Health Check
```http
GET /api/v1/cache/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "redis_connected": true,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "cache_stats": {
    "hit_rate": 0.87,
    "total_keys": 1234,
    "memory_usage_mb": 45.2
  }
}
```

### Cache Statistics
```http
GET /api/v1/cache/stats
```

**Response (200 OK):**
```json
{
  "performance_metrics": {
    "cache_hits": 8765,
    "cache_misses": 1234,
    "hit_rate": 0.876,
    "avg_lookup_time_ms": 1.2
  },
  "constitutional_metrics": {
    "validations_cached": 5432,
    "validation_hit_rate": 0.92,
    "avg_validation_time_ms": 3.4
  },
  "memory_usage": {
    "l1_cache_size": 567,
    "l1_cache_usage_mb": 23.4,
    "redis_memory_mb": 128.7
  }
}
```

### Cache Invalidation
```http
POST /api/v1/cache/invalidate
```

**Request Body:**
```json
{
  "pattern": "policy_validation_*",
  "reason": "constitutional_hash_update",
  "force": false
}
```

**Response (200 OK):**
```json
{
  "invalidated_keys": 45,
  "invalidation_time_ms": 67,
  "status": "completed"
}
```

## Security Features

### HMAC Integrity Protection
- All cached data includes HMAC signatures for integrity verification
- Automatic detection and handling of corrupted cache entries
- Secure key derivation for HMAC generation

### Constitutional Compliance
- Automatic constitutional hash validation for all cache operations
- Cache invalidation on constitutional hash changes
- Compliance scoring and monitoring

### Circuit Breaker Pattern
- Automatic failure detection and isolation
- Graceful degradation to memory-only caching
- Configurable failure thresholds and recovery

## Monitoring and Observability

### Metrics
- **Cache Hit Rate**: Percentage of successful cache lookups
- **Lookup Latency**: Time taken for cache operations
- **Constitutional Validation Rate**: Success rate of constitutional validations
- **Memory Usage**: L1 and L2 cache memory consumption

### Logging
- Cache operation events with correlation IDs
- Constitutional validation results
- Performance warnings for slow operations
- Circuit breaker state changes

### Health Checks
- Redis connectivity status
- Constitutional hash validation status
- Cache performance metrics
- Memory usage monitoring

## Usage Examples

### Basic Cache Usage
```python
from shared.constitutional_cache import get_constitutional_cache

# Get cache instance
cache = await get_constitutional_cache()

# Cache a validation result
await cache.set_validation_result(
    "policy_123_validation",
    {"valid": True, "score": 0.95},
    ttl=600
)

# Retrieve cached result
result = await cache.get_validation_result("policy_123_validation")
```

### Batch Operations
```python
# Cache multiple validation results
batch_data = {
    "policy_123": {"valid": True, "score": 0.95},
    "policy_124": {"valid": False, "score": 0.45},
    "policy_125": {"valid": True, "score": 0.88}
}

for policy_id, result in batch_data.items():
    await cache.set_validation_result(f"{policy_id}_validation", result)
```

### Cache Warming
```python
# Pre-populate cache with common validations
common_policies = await get_common_policies()
for policy in common_policies:
    validation_result = await validate_policy(policy)
    cache_key = cache.generate_cache_key("policy_validation", policy)
    await cache.set_validation_result(cache_key, validation_result)
```

## Troubleshooting

### Common Issues

#### High Cache Miss Rate
```bash
# Check cache configuration
curl http://localhost:8005/api/v1/cache/stats

# Monitor cache patterns
redis-cli monitor | grep "acgs:constitutional"
```

#### Redis Connection Issues
```bash
# Test Redis connectivity
redis-cli ping

# Check Redis memory usage
redis-cli info memory
```

#### Constitutional Validation Failures
```bash
# Check constitutional hash
curl http://localhost:8005/api/v1/cache/health

# Verify cache invalidation
curl -X POST http://localhost:8005/api/v1/cache/invalidate \
  -H "Content-Type: application/json" \
  -d '{"pattern": "*", "reason": "debug"}'
```

## Performance Optimization

### Cache Tuning
- Adjust TTL values based on data volatility
- Configure appropriate cache sizes for workload
- Enable compression for large cached objects
- Use cache warming for frequently accessed data

### Redis Optimization
- Configure Redis memory policies
- Enable Redis persistence for durability
- Use Redis clustering for high availability
- Monitor Redis performance metrics

## Integration

The Constitutional Cache System is automatically integrated into all ACGS-1 services:

- **Authentication Service**: User session and permission caching
- **Constitutional AI Service**: Principle and rule caching
- **Integrity Service**: Audit log and verification caching
- **Formal Verification Service**: Proof and validation caching
- **Governance Synthesis Service**: Policy generation caching
- **Policy Governance Service**: Enforcement and compliance caching
- **Evolutionary Computation Service**: Optimization result caching
