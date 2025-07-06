# ACGS-2 API Documentation

## Overview

This directory contains comprehensive API documentation for all ACGS-2 services, including authentication, constitutional AI, policy governance, and performance monitoring endpoints.

**Base URL**: `https://api.acgs.example.com`
**API Version**: v1
**Authentication**: JWT Bearer tokens
**Rate Limiting**: 1000 requests/minute per user

## Service Endpoints

### Core Services

#### Authentication Service (Port 8016)
- **Base URL**: `http://localhost:8016`
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **Documentation**: [Authentication API](authentication.md)

**Key Endpoints**:
```markdown
POST /auth/login          - User authentication
POST /auth/refresh        - Token refresh
POST /auth/logout         - User logout
GET  /auth/profile        - User profile
POST /auth/mfa/setup      - MFA configuration
POST /auth/agents         - Agent management
POST /auth/api-keys       - API key management
```

**Example Request and Response**:
```javascript
// User authentication
const auth = await fetch('http://localhost:8016/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'user123',
    password: 'password123'
  })
});

const result = await auth.json();
console.log(result);
```
```json
// Successful response
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi...c13Mtg",
  "expiresIn": 3600,
  "user": {
    "id": 123,
    "username": "user123",
    "roles": ["user", "admin"]
  }
}
```

**Usage Notes**:
- Request parameters include username and password.
- Response format includes a JWT token, expiration time, user ID, username, and roles.

#### Constitutional AI Service (Port 8001)
- **Base URL**: `http://localhost:8001`
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **Documentation**: [Constitutional AI API](constitutional-ai.md)

**Key Endpoints**:
```markdown
POST /api/v1/validate                    - Validate constitutional compliance
POST /api/v1/principles/evaluate         - Evaluate constitutional principles
GET  /api/v1/principles                  - List constitutional principles
POST /api/v1/constitutional-council      - Council operations
GET  /api/v1/performance/metrics         - Performance metrics
POST /api/v1/wina/validate               - WINA model validation
```

**Example Request and Response**:
```javascript
// Validate constitutional compliance
const validation = await fetch('http://localhost:8001/api/v1/validate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <jwt_token>',
  },
  body: JSON.stringify({
    policyContent: '...',
    inputData: {...}
  })
});

const validateResult = await validation.json();
console.log(validateResult);
```
```json
// Successful response
{
  "constitutionalCompliance": true,
  "complianceRating": 0.95,
  "principlesEvaluated": ["equality", "fairness", "transparency"]
}
```

**Usage Notes**:
- Request parameters include policy content and input data.
- Response format includes constitutional compliance, compliance rating, and principles evaluated.

#### Policy Governance Service (Port 8005)
- **Base URL**: `http://localhost:8005`
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **Documentation**: [Policy Governance API](policy-governance.md)

**Key Endpoints**:
```markdown
POST /api/v1/policies/evaluate           - Policy evaluation
GET  /api/v1/policies                    - List policies
POST /api/v1/compliance/validate         - Compliance validation
GET  /api/v1/governance/workflows        - Governance workflows
POST /api/v1/constitutional-compliance   - Constitutional compliance
POST /api/v1/synthetic/governance        - Synthetic governance
```

### Platform Services

#### Integrity Service (Port 8002)
- **Base URL**: `http://localhost:8002`
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **Documentation**: [Integrity API](integrity.md)

#### Formal Verification Service (Port 8003)
- **Base URL**: `http://localhost:8003`
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **Documentation**: [Formal Verification API](formal-verification.md)

#### Evolutionary Computation Service (Port 8006)
- **Base URL**: `http://localhost:8006`
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **Documentation**: [Evolutionary Computation API](evolutionary-computation.md)

## Authentication

### JWT Token Format
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "payload": {
    "sub": "user_id",
    "iat": 1625097600,
    "exp": 1625101200,
    "roles": ["user", "admin"],
    "constitutional_clearance": "high",
    "permissions": ["read:policies", "write:governance"]
  }
}
```

### Authentication Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Constitutional-Hash: cdd01ef066bc6cf2
X-Request-ID: <unique_request_id>
```

## Performance Specifications

### Response Time Targets
- **P99 Latency**: ≤5ms for core operations
- **Average Response**: ≤2ms for cached operations
- **Constitutional Validation**: ≤3ms per request
- **Policy Evaluation**: ≤5ms per policy

### Throughput Capacity
- **Sustained Load**: 100+ RPS per service
- **Peak Capacity**: 500+ RPS with auto-scaling
- **Concurrent Users**: 1000+ simultaneous connections
- **Cache Hit Rate**: Target 85% (current 25%)

### Error Handling
```json
{
  "error": {
    "code": "CONSTITUTIONAL_VIOLATION",
    "message": "Policy violates constitutional principle",
    "details": {
      "principle_id": "equality",
      "violation_type": "discriminatory_clause",
      "confidence": 0.95
    ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
    "request_id": "req_123456789",
    "timestamp": "2025-07-02T16:00:00Z"
  }
}
```

## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Test Coverage**: ≥ 80%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## Rate Limiting

### Default Limits
- **Authenticated Users**: 1000 requests/minute
- **Anonymous Users**: 100 requests/minute
- **Admin Users**: 5000 requests/minute
- **Service-to-Service**: 10000 requests/minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1625097660
X-RateLimit-Window: 60
```

## Monitoring and Metrics

### Health Check Response
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-07-02T16:00:00Z",
  "uptime": 86400,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "performance": {
    "response_time_p99": 0.97,
    "cache_hit_rate": 0.25,
    "throughput_rps": 306.9,
    "error_rate": 0.001
  },
  "dependencies": {
    "database": "healthy",
    "redis": "healthy",
    "external_apis": "healthy"
  }
}
```

### Metrics Endpoint
All services expose Prometheus metrics at `/metrics`:

```
# HELP acgs_request_duration_seconds Request duration in seconds
# TYPE acgs_request_duration_seconds histogram
acgs_request_duration_seconds_bucket{endpoint="/api/v1/validate",method="POST",le="0.001"} 245
acgs_request_duration_seconds_bucket{endpoint="/api/v1/validate",method="POST",le="0.005"} 892
acgs_request_duration_seconds_bucket{endpoint="/api/v1/validate",method="POST",le="0.01"} 987

# HELP acgs_constitutional_compliance_rate Constitutional compliance rate
# TYPE acgs_constitutional_compliance_rate gauge
acgs_constitutional_compliance_rate 0.98

# HELP acgs_cache_hit_rate Cache hit rate percentage
# TYPE acgs_cache_hit_rate gauge
acgs_cache_hit_rate{cache_type="l1"} 0.35
acgs_cache_hit_rate{cache_type="l2"} 0.25
```

## WebSocket Connections

### Real-time Governance Events
```javascript
const ws = new WebSocket('ws://localhost:8005/api/v1/governance/events');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Governance event:', data);
};

// Example event
{
  "type": "policy_violation",
  "timestamp": "2025-07-02T16:00:00Z",
  "policy_id": "pol_123",
  "violation_type": "constitutional",
  "severity": "high",
  "details": {
    "principle_violated": "equality",
    "confidence": 0.95
  }
}
```

## SDK and Client Libraries

### Python SDK
```python
from acgs_client import ACGSClient

client = ACGSClient(
    base_url="http://localhost:8001",
    api_key="your_api_key",
    constitutional_hash="cdd01ef066bc6cf2"
)

# Constitutional validation
result = await client.constitutional_ai.validate(
    policy_content="...",
    input_data={...}
)

# Policy evaluation
evaluation = await client.policy_governance.evaluate(
    policy_id="pol_123",
    context={...}
)
```

### JavaScript SDK
```javascript
import { ACGSClient } from '@acgs/client';

const client = new ACGSClient({
  baseUrl: 'http://localhost:8001',
  apiKey: 'your_api_key',
  constitutionalHash: 'cdd01ef066bc6cf2'
});

// Constitutional validation
const result = await client.constitutionalAI.validate({
  policyContent: '...',
  inputData: {...}
});
```

## Testing and Development

### Test Environment
- **Base URL**: `http://localhost:8000-8006`
- **Test Database**: PostgreSQL on port 5439
- **Test Cache**: Redis on port 6389
- **Mock Services**: Available for integration testing

### API Testing Tools
```bash
# Health check all services
curl http://localhost:8001/health
curl http://localhost:8005/health

# Constitutional validation test
curl -X POST http://localhost:8001/api/v1/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"policy_content": "test policy", "input_data": {}}'

# Performance metrics
curl http://localhost:8001/metrics
```

## Support and Resources

- **API Documentation**: Complete OpenAPI specifications in each service directory
- **SDK Documentation**: Language-specific client library documentation
- **Performance Monitoring**: Grafana dashboards for real-time metrics
- **Error Tracking**: Centralized error logging and alerting
- **Support**: Technical support through GitHub issues and documentation

For detailed endpoint specifications, see the individual service documentation files in this directory.
