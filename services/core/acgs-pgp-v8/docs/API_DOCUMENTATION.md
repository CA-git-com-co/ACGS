# ACGS-PGP v8 API Documentation

## Overview

The ACGS-PGP v8 API provides quantum-inspired semantic fault tolerance for policy generation within the ACGS-1 Constitutional Governance System. All endpoints require proper authentication and constitutional compliance validation.

**Base URL**: `http://localhost:8010`  
**Constitutional Hash**: `cdd01ef066bc6cf2`  
**API Version**: v8.0.0

## Authentication

All API endpoints (except `/health` and `/metrics`) require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

Tokens are validated against the ACGS-1 Auth Service (port 8000).

## Core Endpoints

### Health Check

#### GET /health

Returns the current health status of all ACGS-PGP v8 components.

**Response Example:**
```json
{
  "status": "healthy",
  "service": "acgs-pgp-v8",
  "version": "8.0.0",
  "timestamp": "2024-06-16T15:30:45.123456",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "components": {
    "generation_engine": {
      "status": "healthy",
      "last_check": "2024-06-16T15:30:44.123456",
      "response_time_ms": 45.2
    },
    "stabilizer_environment": {
      "status": "healthy",
      "active_executions": 3,
      "circuit_breaker_state": "closed"
    },
    "diagnostic_engine": {
      "status": "healthy",
      "diagnostics_completed": 1247,
      "error_detection_rate": 0.943
    },
    "cache_manager": {
      "status": "healthy",
      "hit_rate": 0.87,
      "active_connections": 12
    }
  }
}
```

### System Status

#### GET /api/v1/status

Returns comprehensive system status including performance metrics.

**Authentication**: Required

**Response Example:**
```json
{
  "overall_status": "operational",
  "generation_engine": {
    "status": "healthy",
    "policies_generated": 1523,
    "average_response_time_ms": 287.5,
    "constitutional_compliance_rate": 0.952
  },
  "stabilizer_environment": {
    "status": "healthy",
    "executions_completed": 8934,
    "error_correction_events": 23,
    "fault_tolerance_level": 2
  },
  "diagnostic_engine": {
    "status": "healthy",
    "diagnostics_performed": 2341,
    "recovery_recommendations": 45,
    "accuracy_rate": 0.934
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2024-06-16T15:30:45.123456"
}
```

## Policy Generation

### Generate Policy

#### POST /api/v1/generate-policy

Generates a new policy using quantum-inspired semantic fault tolerance.

**Authentication**: Required  
**Content-Type**: `application/json`

**Request Body:**
```json
{
  "title": "Data Privacy Protection Policy",
  "description": "Comprehensive policy for protecting citizen data privacy",
  "stakeholders": ["citizens", "government", "businesses"],
  "constitutional_principles": ["privacy", "transparency", "accountability"],
  "priority": "high",
  "context": {
    "domain": "data_protection",
    "jurisdiction": "federal",
    "effective_date": "2024-07-01"
  },
  "requirements": {
    "compliance_threshold": 0.9,
    "consensus_required": true,
    "multi_model_validation": true
  }
}
```

**Response Example:**
```json
{
  "generation_id": "pgp_gen_20240616_153045_abc123",
  "status": "completed",
  "policy": {
    "title": "Data Privacy Protection Policy",
    "content": "...",
    "sections": [
      {
        "title": "Purpose and Scope",
        "content": "...",
        "constitutional_basis": ["privacy", "transparency"]
      }
    ]
  },
  "constitutional_compliance_score": 0.952,
  "confidence_score": 0.887,
  "semantic_hash": "sha256:abc123def456...",
  "generation_metadata": {
    "models_used": ["qwen3-32b", "deepseek-chat"],
    "consensus_method": "weighted_average",
    "fault_tolerance_applied": true,
    "error_corrections": 2
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2024-06-16T15:30:45.123456",
  "processing_time_ms": 287
}
```

**Error Responses:**
- `400 Bad Request`: Invalid request format or missing required fields
- `401 Unauthorized`: Invalid or missing authentication token
- `422 Unprocessable Entity`: Constitutional compliance validation failed
- `500 Internal Server Error`: Policy generation failed

## Diagnostics

### System Diagnosis

#### POST /api/v1/diagnose

Performs comprehensive system diagnosis with ML-powered error analysis.

**Authentication**: Required  
**Content-Type**: `application/json`

**Request Body:**
```json
{
  "target_system": "acgs-pgp-v8",
  "include_recommendations": true,
  "diagnostic_depth": "comprehensive"
}
```

**Response Example:**
```json
{
  "diagnostic_id": "diag_20240616_153045_xyz789",
  "target_system": "acgs-pgp-v8",
  "overall_health_score": 0.934,
  "constitutional_compliance_score": 0.952,
  "error_count": 3,
  "critical_error_count": 0,
  "recommendations_count": 2,
  "auto_executable_recommendations": 1,
  "timestamp": "2024-06-16T15:30:45.123456",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "is_system_healthy": true,
  "requires_immediate_attention": false
}
```

## Monitoring

### Prometheus Metrics

#### GET /metrics

Returns Prometheus-formatted metrics for monitoring and alerting.

**Authentication**: Not required  
**Content-Type**: `text/plain; version=0.0.4; charset=utf-8`

**Key Metrics:**
- `acgs_pgp_v8_system_uptime_seconds`: System uptime
- `acgs_pgp_v8_policy_generation_requests_total`: Total policy generation requests
- `acgs_pgp_v8_constitutional_compliance_score`: Constitutional compliance scores
- `acgs_pgp_v8_component_health`: Component health status (1=healthy, 0=unhealthy)
- `acgs_pgp_v8_error_correction_events_total`: Error correction events

### Metrics Summary

#### GET /api/v1/metrics/summary

Returns a JSON summary of key metrics for dashboard consumption.

**Authentication**: Not required

**Response Example:**
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "system_uptime_seconds": 86400,
  "metrics_collected": true,
  "registry_collectors": 15,
  "timestamp": "2024-06-16T15:30:45.123456"
}
```

## Error Handling

All API endpoints follow consistent error response format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Constitutional compliance validation failed",
    "details": {
      "compliance_score": 0.65,
      "required_threshold": 0.8,
      "constitutional_hash": "cdd01ef066bc6cf2"
    },
    "timestamp": "2024-06-16T15:30:45.123456",
    "trace_id": "trace_abc123def456"
  }
}
```

## Rate Limiting

- **Default Limit**: 100 requests per minute per IP
- **Policy Generation**: 10 requests per minute per authenticated user
- **Diagnostics**: 5 requests per minute per authenticated user

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Security Headers

All responses include security headers:
- `X-Constitutional-Hash`: cdd01ef066bc6cf2
- `X-ACGS-Service`: acgs-pgp-v8
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY
- `Strict-Transport-Security`: max-age=31536000; includeSubDomains

## Integration Examples

### Python Client
```python
import httpx
import asyncio

class ACGSPGPClient:
    def __init__(self, base_url="http://localhost:8010", token=None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async def generate_policy(self, policy_request):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/generate-policy",
                json=policy_request,
                headers=self.headers
            )
            return response.json()
    
    async def health_check(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            return response.json()
```

### cURL Examples
```bash
# Health check
curl http://localhost:8010/health

# Generate policy (with authentication)
curl -X POST http://localhost:8010/api/v1/generate-policy \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Policy",
    "description": "Test policy description",
    "stakeholders": ["citizens"],
    "constitutional_principles": ["transparency"],
    "priority": "medium"
  }'

# Get metrics
curl http://localhost:8010/metrics
```
