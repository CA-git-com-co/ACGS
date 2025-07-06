# ACGS Service Integration Guide

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

This guide provides comprehensive instructions for integrating with ACGS (Autonomous Constitutional Governance System) services. ACGS implements constitutional AI governance with performance targets of sub-5ms P99 latency, >100 RPS throughput, and >85% cache hit rates.

## Quick Start

### 1. Authentication Setup

All ACGS services require JWT-based authentication. First, obtain an authentication token:

```bash
curl -X POST http://localhost:8016/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password",
    "constitutional_hash": "cdd01ef066bc6cf2"
  }'
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-07-07T12:00:00Z",
  "user_id": "user_123",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2. Constitutional Compliance Validation

Validate content for constitutional compliance:

```bash
curl -X POST http://localhost:8001/api/v1/validate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your content to validate",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "validation_level": "comprehensive"
  }'
```

Response:
```json
{
  "is_compliant": true,
  "compliance_score": 0.95,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validation_id": "val_123",
  "violations": [],
  "processing_time_ms": 2.5
}
```

## Service Endpoints

### Authentication Service (Port 8016)

**Base URL**: `http://localhost:8016`

#### Key Endpoints:
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/validate-token` - Token validation
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/user/{user_id}` - User information

#### Example Integration:

```python
import httpx
import asyncio

class ACGSAuthClient:
    def __init__(self, base_url: str = "http://localhost:8016"):
        self.base_url = base_url
        self.token = None
        
    async def authenticate(self, username: str, password: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "username": username,
                    "password": password,
                    "constitutional_hash": "cdd01ef066bc6cf2"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["token"]
            return self.token
    
    def get_auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}
```

### Constitutional AI Service (Port 8001)

**Base URL**: `http://localhost:8001`

#### Key Endpoints:
- `POST /api/v1/validate` - Constitutional compliance validation
- `POST /api/v1/analyze` - Detailed constitutional analysis
- `GET /api/v1/principles` - Get constitutional principles
- `POST /api/v1/batch-validate` - Batch validation for multiple items

#### Example Integration:

```python
class ACGSConstitutionalClient:
    def __init__(self, auth_client: ACGSAuthClient):
        self.auth_client = auth_client
        self.base_url = "http://localhost:8001"
    
    async def validate_compliance(self, content: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/validate",
                headers=self.auth_client.get_auth_headers(),
                json={
                    "content": content,
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "validation_level": "comprehensive"
                }
            )
            response.raise_for_status()
            return response.json()
```

### Evolutionary Computation Service (Port 8006)

**Base URL**: `http://localhost:8006`

#### Key Endpoints:
- `POST /api/v1/evolve` - Submit evolution request
- `GET /api/v1/status/{evolution_id}` - Get evolution status
- `GET /api/v1/results/{evolution_id}` - Get evolution results
- `POST /api/v1/fitness/evaluate` - Evaluate individual fitness

#### Example Integration:

```python
class ACGSEvolutionClient:
    def __init__(self, auth_client: ACGSAuthClient):
        self.auth_client = auth_client
        self.base_url = "http://localhost:8006"
    
    async def submit_evolution(self, evolution_params: dict) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/evolve",
                headers=self.auth_client.get_auth_headers(),
                json={
                    **evolution_params,
                    "constitutional_hash": "cdd01ef066bc6cf2"
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["evolution_id"]
    
    async def get_evolution_status(self, evolution_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/status/{evolution_id}",
                headers=self.auth_client.get_auth_headers()
            )
            response.raise_for_status()
            return response.json()
```

## Performance Optimization

### 1. Caching Strategy

ACGS services implement aggressive caching for >85% hit rates:

```python
import aioredis

class ACGSCacheClient:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = aioredis.from_url(redis_url)
    
    async def get_cached_validation(self, content_hash: str) -> dict:
        """Get cached constitutional validation result."""
        cache_key = f"constitutional_validation:{content_hash}"
        cached_result = await self.redis.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        return None
    
    async def cache_validation_result(self, content_hash: str, result: dict):
        """Cache validation result with TTL."""
        cache_key = f"constitutional_validation:{content_hash}"
        await self.redis.setex(
            cache_key, 
            3600,  # 1 hour TTL
            json.dumps(result)
        )
```

### 2. Connection Pooling

Use connection pooling for optimal performance:

```python
import httpx

class ACGSClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100
            ),
            timeout=httpx.Timeout(5.0)  # 5s timeout for sub-5ms P99 target
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
```

### 3. Batch Operations

Use batch operations for improved throughput:

```python
async def batch_validate_compliance(
    client: ACGSConstitutionalClient, 
    contents: List[str]
) -> List[dict]:
    """Batch validate multiple contents for constitutional compliance."""
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            f"{client.base_url}/api/v1/batch-validate",
            headers=client.auth_client.get_auth_headers(),
            json={
                "contents": contents,
                "constitutional_hash": "cdd01ef066bc6cf2",
                "validation_level": "comprehensive"
            }
        )
        response.raise_for_status()
        return response.json()["results"]
```

## Error Handling

### Standard Error Response Format

All ACGS services return errors in a consistent format:

```json
{
  "error": "validation_failed",
  "message": "Content violates constitutional principle: safety_first",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-06T12:00:00Z",
  "details": {
    "violation_type": "safety",
    "severity": "high",
    "suggested_action": "Review content for safety compliance"
  }
}
```

### Error Handling Best Practices

```python
async def handle_acgs_request(client_func, *args, **kwargs):
    """Generic error handler for ACGS service requests."""
    try:
        return await client_func(*args, **kwargs)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            # Token expired, refresh and retry
            await auth_client.refresh_token()
            return await client_func(*args, **kwargs)
        elif e.response.status_code == 429:
            # Rate limited, implement exponential backoff
            await asyncio.sleep(2 ** retry_count)
            return await client_func(*args, **kwargs)
        elif e.response.status_code >= 500:
            # Server error, implement circuit breaker
            raise ACGSServiceUnavailableError(f"Service error: {e}")
        else:
            # Client error, parse and handle
            error_data = e.response.json()
            raise ACGSValidationError(error_data["message"])
    except httpx.TimeoutException:
        raise ACGSTimeoutError("Request timeout exceeded")
```

## Monitoring and Observability

### Health Checks

Monitor service health with regular health checks:

```python
async def check_service_health(service_url: str) -> dict:
    """Check health of ACGS service."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{service_url}/health")
        response.raise_for_status()
        return response.json()

# Example health check response
{
  "status": "healthy",
  "service": "constitutional_ai",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-06T12:00:00Z",
  "version": "3.0.0",
  "uptime_seconds": 86400,
  "performance_metrics": {
    "p99_latency_ms": 2.5,
    "throughput_rps": 150,
    "cache_hit_rate": 0.87
  }
}
```

### Metrics Collection

Collect performance metrics for monitoring:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
acgs_requests_total = Counter(
    'acgs_requests_total',
    'Total ACGS requests',
    ['service', 'endpoint', 'status']
)

acgs_request_duration = Histogram(
    'acgs_request_duration_seconds',
    'ACGS request duration',
    ['service', 'endpoint']
)

acgs_constitutional_compliance_score = Gauge(
    'acgs_constitutional_compliance_score',
    'Constitutional compliance score',
    ['service']
)
```

## Constitutional Compliance Requirements

### Mandatory Fields

All requests to ACGS services must include:

1. **Constitutional Hash**: `cdd01ef066bc6cf2`
2. **Authentication Token**: Valid JWT token
3. **Request ID**: Unique identifier for tracing

### Compliance Validation

Every operation undergoes constitutional compliance validation:

- **Safety First**: Operations must not pose safety risks
- **Operational Transparency**: All operations must be auditable
- **User Consent**: User consent required for data processing
- **Data Privacy**: Personal data protection compliance
- **Resource Constraints**: Operations within resource limits
- **Operation Reversibility**: Operations must be reversible
- **Least Privilege**: Minimum required permissions

## Next Steps

1. **Set up authentication** with the Authentication Service
2. **Implement constitutional compliance validation** in your workflows
3. **Configure caching** for optimal performance
4. **Set up monitoring** and health checks
5. **Test integration** with provided examples
6. **Review performance metrics** to ensure targets are met

## Next Steps

1. **Set up authentication** with the Authentication Service
2. **Implement constitutional compliance validation** in your workflows
3. **Configure caching** for optimal performance
4. **Set up monitoring** and health checks
5. **Test integration** with provided examples
6. **Review performance metrics** to ensure targets are met

For additional support and advanced integration patterns, refer to the [ACGS Advanced Integration Guide](./ACGS_ADVANCED_INTEGRATION.md).

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)
- [ACGS Implementation Guide](../deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [ACGS-PGP Operational Deployment Guide](../deployment/ACGS_PGP_OPERATIONAL_DEPLOYMENT_GUIDE.md)
- [ACGS-PGP Troubleshooting Guide](../deployment/ACGS_PGP_TROUBLESHOOTING_GUIDE.md)
- [ACGS-PGP Setup Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status Dashboard](../operations/SERVICE_STATUS.md)
- [ACGS Configuration Guide](../configuration/README.md)
- [ACGS-2 Technical Specifications - 2025 Edition](../TECHNICAL_SPECIFICATIONS_2025.md)
