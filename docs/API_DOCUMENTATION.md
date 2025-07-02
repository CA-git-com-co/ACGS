# ACGS-2 API Documentation

This document provides comprehensive API documentation for all ACGS-2 services.

**Current Status**: Phase 1 Complete - All services operational with constitutional compliance hash `cdd01ef066bc6cf2`

## Base URLs

### Development Environment (Current Deployment)

- **Constitutional AI**: `http://localhost:8002`
- **Policy Governance**: `http://localhost:8005`
- **Policy Generation (ACGS-PGP v8)**: `http://localhost:8010`
- **Governance Synthesis**: `http://localhost:8004`
- **Formal Verification**: `http://localhost:8003`
- **Evolutionary Computation**: `http://localhost:8006`
- **Authentication**: `http://localhost:8016`
- **Integrity**: `http://localhost:8002`

### Infrastructure Services

- **PostgreSQL Database**: Port 5439 (production configuration)
- **Redis Cache**: Port 6389 (>85% cache hit rate achieved)
- **OPA Policy Engine**: Port 8181

### Production Environment

- Base URL: `https://api.acgs.ai`
- Service routing via path prefix: `/api/v1/{service}/`
- Constitutional compliance validation on all endpoints

## Authentication

All API endpoints require authentication unless otherwise specified.

### JWT Token Authentication

```http
Authorization: Bearer <jwt_token>
```

### Obtaining Tokens

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Constitutional Compliance

All API endpoints validate constitutional compliance using hash `cdd01ef066bc6cf2`.

### Compliance Headers

```http
X-Constitutional-Hash: cdd01ef066bc6cf2
X-Compliance-Threshold: 0.8
```

### Compliance Response

All responses include constitutional compliance information:

```json
{
  "data": { ... },
  "constitutional_compliance": {
    "hash": "cdd01ef066bc6cf2",
    "compliance_score": 0.95,
    "is_compliant": true,
    "validation_timestamp": "2025-01-01T12:00:00Z"
  }
}
```

## Constitutional AI Service (Port 8002)

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "constitutional_ai",
  "version": "2.0.0",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Constitutional Validation
```http
POST /api/v1/constitutional/validate
Content-Type: application/json
Authorization: Bearer <token>

{
  "policy": {
    "action": "data_access",
    "resource": "user_data",
    "context": {
      "user_role": "admin",
      "purpose": "analysis"
    }
  },
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "is_compliant": true,
  "compliance_score": 0.95,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validation_details": {
    "principles_checked": ["privacy", "fairness", "transparency"],
    "violations": [],
    "recommendations": []
  },
  "processing_time_ms": 2.5
}
```

### Constitutional Analysis
```http
POST /api/v1/constitutional/analyze
Content-Type: application/json
Authorization: Bearer <token>

{
  "policies": [
    {
      "id": "policy_001",
      "content": "Allow data access for authorized users",
      "context": {"domain": "healthcare"}
    }
  ],
  "analysis_type": "comprehensive"
}
```

## Policy Governance Service (Port 8010)

### Policy Query
```http
POST /api/v1/policy/query
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": {
    "action": "read",
    "resource": "sensitive_data",
    "subject": {
      "role": "analyst",
      "clearance": "secret"
    }
  },
  "context": {
    "timestamp": "2024-01-01T12:00:00Z",
    "location": "secure_facility"
  }
}
```

**Response:**
```json
{
  "decision": "allow",
  "confidence": 0.98,
  "applied_rules": [
    {
      "rule_id": "access_control_001",
      "description": "Analyst access to classified data",
      "weight": 0.8
    }
  ],
  "processing_time_ms": 1.2,
  "cache_hit": true
}
```

### Policy Management
```http
POST /api/v1/policy/manage
Content-Type: application/json
Authorization: Bearer <token>

{
  "operation": "create",
  "policy": {
    "name": "Data Access Policy",
    "rules": [
      {
        "condition": "role == 'admin'",
        "action": "allow",
        "resource": "all_data"
      }
    ],
    "priority": 100
  }
}
```

## Governance Synthesis Service (Port 8005)

### Multi-Model Synthesis
```http
POST /api/v1/synthesis/multi-model
Content-Type: application/json
Authorization: Bearer <token>

{
  "request": {
    "policies": ["policy_001", "policy_002"],
    "context": {
      "domain": "healthcare",
      "urgency": "high"
    },
    "synthesis_strategy": "consensus"
  }
}
```

**Response:**
```json
{
  "synthesized_policy": {
    "id": "synthesized_001",
    "content": "Synthesized policy content",
    "confidence": 0.92,
    "consensus_score": 0.88
  },
  "model_contributions": [
    {
      "model": "constitutional_ai",
      "weight": 0.4,
      "confidence": 0.95
    },
    {
      "model": "policy_governance",
      "weight": 0.6,
      "confidence": 0.89
    }
  ],
  "processing_time_ms": 45.2
}
```

## Formal Verification Service (Port 8004)

### Verify Policy
```http
POST /api/v1/verification/verify
Content-Type: application/json
Authorization: Bearer <token>

{
  "policy": {
    "id": "policy_001",
    "formal_specification": "∀x. authorized(x) → access_granted(x)",
    "properties": ["safety", "liveness"]
  },
  "verification_level": "comprehensive"
}
```

**Response:**
```json
{
  "verification_result": "verified",
  "properties_verified": ["safety", "liveness"],
  "proof_summary": "Policy satisfies all specified properties",
  "verification_time_ms": 150.5,
  "confidence": 0.99
}
```

## Authentication Service (Port 8016)

### Token Validation
```http
POST /api/v1/auth/validate
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "valid": true,
  "user_id": "user_123",
  "roles": ["admin", "analyst"],
  "expires_at": "2024-01-01T13:00:00Z"
}
```

### User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "newuser@example.com",
  "password": "secure_password",
  "roles": ["user"]
}
```

## Error Responses

All services follow a consistent error response format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "policy.action",
      "reason": "Required field missing"
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_123456"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `VALIDATION_ERROR`: Invalid input data
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

## Rate Limiting

All endpoints are subject to rate limiting:

- **Default**: 100 requests per minute per user
- **Authentication**: 10 requests per minute per IP
- **Heavy operations**: 10 requests per minute per user

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks

ACGS-2 supports webhooks for real-time notifications:

### Webhook Events
- `policy.validated`: Policy validation completed
- `constitutional.violation`: Constitutional violation detected
- `synthesis.completed`: Policy synthesis completed
- `verification.failed`: Formal verification failed

### Webhook Payload
```json
{
  "event": "policy.validated",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "policy_id": "policy_001",
    "validation_result": "compliant",
    "compliance_score": 0.95
  },
  "service": "constitutional_ai"
}
```

## SDK and Client Libraries

Official SDKs are available for:
- **Python**: `pip install acgs-python-sdk`
- **JavaScript/Node.js**: `npm install acgs-js-sdk`
- **Go**: `go get github.com/acgs/go-sdk`

### Python SDK Example
```python
from acgs_sdk import ACGSClient

client = ACGSClient(
    base_url="https://api.acgs.ai",
    api_key="your_api_key"
)

result = await client.constitutional.validate(policy_data)
print(f"Compliance: {result.is_compliant}")
```

For more detailed examples and advanced usage, see the SDK documentation.
