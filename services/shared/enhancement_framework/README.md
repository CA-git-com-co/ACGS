# ACGS-1 Enhancement Framework

The ACGS-1 Enhancement Framework provides a lightweight, standardized approach to enhancing all ACGS-1 services with constitutional compliance, performance optimization, monitoring, and caching capabilities.

## Overview

This framework ensures consistent enhancement patterns across all 7 core ACGS services while maintaining:

- **Constitutional Compliance**: Validation against hash `cdd01ef066bc6cf2`
- **Performance Targets**: <500ms response times, >99.5% availability
- **Monitoring Integration**: Prometheus metrics and health checks
- **Caching Optimization**: Redis integration with fallback
- **Circuit Breaker Protection**: Automatic failover and recovery

## Quick Start

### Basic Usage

```python
from services.shared.enhancement_framework import ACGSServiceEnhancer

# Create service enhancer
enhancer = ACGSServiceEnhancer("my_service", port=8001)

# Create enhanced FastAPI application
app = await enhancer.create_enhanced_service()
```

### Advanced Configuration

```python
# Configure constitutional compliance
enhancer.configure_constitutional_compliance(
    enabled=True,
    strict_mode=True,
    performance_target_ms=5.0
)

# Configure performance optimization
enhancer.configure_performance_optimization(
    enabled=True,
    response_time_target=0.5,  # 500ms
    availability_target=0.995,  # 99.5%
    circuit_breaker_threshold=5
)

# Configure monitoring
enhancer.configure_monitoring(
    enabled=True,
    prometheus_enabled=True,
    health_check_enabled=True
)

# Configure caching
enhancer.configure_caching(
    enabled=True,
    redis_url="redis://localhost:6379/0",
    default_ttl=300
)
```

## Framework Components

### 1. Service Template (`service_template.py`)

- Standardized FastAPI application creation
- Consistent middleware stack
- Lifespan management
- Standard endpoints

### 2. Constitutional Validator (`constitutional_validator.py`)

- Fast constitutional compliance validation (<5ms target)
- Hash verification against `cdd01ef066bc6cf2`
- Bypass paths for health/metrics endpoints
- Performance monitoring

### 3. Performance Optimizer (`performance_optimizer.py`)

- Response time optimization (<500ms target)
- Circuit breaker patterns
- Availability tracking (>99.5% target)
- Performance monitoring

### 4. Monitoring Integrator (`monitoring_integrator.py`)

- Prometheus metrics collection
- Health check endpoints
- Service performance tracking
- Constitutional compliance metrics

### 5. Cache Enhancer (`cache_enhancer.py`)

- Redis caching integration
- Constitutional validation caching
- Policy decision caching
- Fallback to in-memory cache

### 6. Service Enhancer (`service_enhancer.py`)

- Main orchestration class
- Configuration management
- Service creation and validation

## Standard Endpoints

All enhanced services automatically include:

- `GET /` - Service information and capabilities
- `GET /health` - Health check with metrics
- `GET /status` - Enhanced status with performance data
- `GET /metrics` - Prometheus metrics (if enabled)
- `GET /docs` - OpenAPI documentation

## Performance Targets

The framework enforces these performance targets:

| Metric                    | Target | Monitoring   |
| ------------------------- | ------ | ------------ |
| Response Time (P95)       | <500ms | ✅ Automatic |
| Availability              | >99.5% | ✅ Automatic |
| Constitutional Compliance | >95%   | ✅ Automatic |
| Cache Hit Rate            | >80%   | ✅ Automatic |

## Constitutional Compliance

All enhanced services validate constitutional compliance:

- **Reference Hash**: `cdd01ef066bc6cf2`
- **Validation Target**: <5ms per request
- **Bypass Paths**: `/health`, `/metrics`, `/docs`, `/redoc`
- **Headers**: `X-Constitutional-Hash` required for strict mode

### Example Request

```bash
curl -H "X-Constitutional-Hash: cdd01ef066bc6cf2" \
     http://localhost:8005/api/v1/some-endpoint
```

## Monitoring and Metrics

### Prometheus Metrics

The framework automatically collects:

- `acgs_requests_total` - Total requests by service/endpoint/status
- `acgs_request_duration_seconds` - Request duration histogram
- `acgs_constitutional_compliance_checks_total` - Compliance check counters
- `acgs_service_health` - Service health gauge
- `acgs_response_time_p95_seconds` - 95th percentile response time

### Health Checks

Enhanced health endpoints provide:

```json
{
  "status": "healthy",
  "service": "pgc_service",
  "timestamp": 1703123456.789,
  "metrics": {
    "prometheus_enabled": true,
    "service_health": "healthy"
  }
}
```

## Caching Strategy

### Constitutional Validation Caching

```python
# Cache constitutional validation results
cache_key = await cache_enhancer.cache_constitutional_validation(
    request_hash="cdd01ef066bc6cf2",
    validation_result={"valid": True, "score": 0.95},
    ttl=300
)

# Retrieve cached validation
result = await cache_enhancer.get_cached_constitutional_validation(
    request_hash="cdd01ef066bc6cf2"
)
```

### Policy Decision Caching

```python
# Cache policy decisions
cache_key = await cache_enhancer.cache_policy_decision(
    policy_content="policy text",
    input_data={"user": "test"},
    result={"decision": "allow"},
    ttl=300
)
```

## Integration with Existing Services

### Refactoring Existing Services

1. **Import the framework**:

   ```python
   from services.shared.enhancement_framework import ACGSServiceEnhancer
   ```

2. **Create enhancer**:

   ```python
   enhancer = ACGSServiceEnhancer("service_name", port=8XXX)
   ```

3. **Create enhanced app**:

   ```python
   app = await enhancer.create_enhanced_service()
   ```

4. **Include existing routers**:
   ```python
   app.include_router(existing_router, prefix="/api/v1", tags=["API"])
   ```

### Preserving Existing Functionality

The framework is designed to preserve all existing functionality:

- ✅ All existing API endpoints remain functional
- ✅ Existing middleware is compatible
- ✅ Database connections are preserved
- ✅ Service-to-service communication continues working
- ✅ Quantumagi Solana integration is maintained

## Validation

Use the validation script to test enhanced services:

```bash
cd services/shared/enhancement_framework
python validate_framework.py http://localhost:8005
```

The validator checks:

- Service health and availability
- Constitutional compliance validation
- Performance optimization
- Monitoring integration
- Cache functionality
- API endpoint preservation
- Error handling

## Example: Enhanced PGC Service

See `services/core/policy-governance/pgc_service/app/main_enhanced.py` for a complete example of applying the framework to the PGC service while preserving all existing functionality.

## Deployment

### Host-based Deployment

The framework is compatible with host-based deployment:

```bash
cd services/core/policy-governance/pgc_service
python -m app.main_enhanced
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-m", "app.main_enhanced"]
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `services/shared` is in Python path
2. **Redis Connection**: Check Redis is running on `localhost:6379`
3. **Constitutional Validation**: Verify hash `cdd01ef066bc6cf2` in headers
4. **Performance**: Monitor response times with `/metrics` endpoint

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. Apply framework to remaining 6 core services
2. Validate each enhanced service maintains functionality
3. Monitor performance improvements
4. Integrate with production monitoring systems

## Support

For issues or questions about the enhancement framework:

1. Check the validation results: `framework_validation_results.json`
2. Review service logs for enhancement-related messages
3. Verify constitutional compliance with test requests
