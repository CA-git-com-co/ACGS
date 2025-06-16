# ACGS-1 Comprehensive API Documentation

**Version:** 2.0  
**Date:** 2025-06-16  
**Status:** Production Ready  
**Base URL**: `https://api.acgs-1.com`  

## 🎯 API Overview

The ACGS-1 Constitutional Governance System provides a comprehensive REST API across 8 core services, enabling constitutional AI governance, policy enforcement, and democratic oversight. All APIs follow OpenAPI 3.0 specifications with comprehensive authentication and rate limiting.

### Service Endpoints Overview

| Service | Port | Base Path | Purpose |
|---------|------|-----------|---------|
| Auth Service | 8000 | `/api/auth/` | Authentication & Authorization |
| AC Service | 8001 | `/api/constitutional-ai/` | Constitutional AI Management |
| Integrity Service | 8002 | `/api/integrity/` | Cryptographic Integrity |
| FV Service | 8003 | `/api/formal-verification/` | Formal Verification |
| GS Service | 8004 | `/api/governance-synthesis/` | Governance Synthesis |
| PGC Service | 8005 | `/api/policy-governance/` | Policy Enforcement |
| EC Service | 8006 | `/api/evolutionary-computation/` | Evolutionary Computation |
| Self-Evolving AI | 8007 | `/api/self-evolving-ai/` | AI Evolution Management |

## 🔐 Authentication

### JWT Authentication
All API endpoints require JWT authentication except for public health checks and authentication endpoints.

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Authentication Flow
```http
POST /api/auth/login
{
  "username": "user@example.com",
  "password": "secure_password",
  "mfa_code": "123456"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 🏛️ Core Service APIs

### 1. Authentication Service (Port 8000)

#### User Management
```http
# Register new user
POST /api/auth/register
{
  "username": "user@example.com",
  "password": "secure_password",
  "role": "user",
  "profile": {
    "first_name": "John",
    "last_name": "Doe"
  }
}

# User login
POST /api/auth/login
{
  "username": "user@example.com",
  "password": "secure_password",
  "mfa_code": "123456"
}

# Refresh token
POST /api/auth/refresh
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# User logout
POST /api/auth/logout
Authorization: Bearer <token>
```

#### Role-Based Access Control
```http
# Get user permissions
GET /api/auth/permissions
Authorization: Bearer <token>

# Update user role
PUT /api/auth/users/{user_id}/role
Authorization: Bearer <token>
{
  "role": "admin",
  "permissions": ["read", "write", "admin"]
}
```

### 2. Constitutional AI Service (Port 8001)

#### Constitutional Principles Management
```http
# Get all principles
GET /api/constitutional-ai/principles
Authorization: Bearer <token>

# Create new principle
POST /api/constitutional-ai/principles
Authorization: Bearer <token>
{
  "title": "Democratic Participation",
  "description": "All governance decisions must include democratic participation",
  "category": "governance",
  "priority": 1,
  "validation_criteria": {
    "requires_voting": true,
    "minimum_participation": 0.6
  }
}

# Update principle
PUT /api/constitutional-ai/principles/{principle_id}
Authorization: Bearer <token>
{
  "title": "Updated Democratic Participation",
  "description": "Enhanced democratic participation requirements"
}
```

#### Constitutional Compliance
```http
# Validate constitutional compliance
POST /api/constitutional-ai/validate-compliance
Authorization: Bearer <token>
{
  "policy_content": "Policy text to validate",
  "context": {
    "policy_type": "governance",
    "stakeholders": ["citizens", "administrators"]
  }
}

Response:
{
  "compliance_score": 0.95,
  "violations": [],
  "recommendations": [
    "Consider adding democratic oversight mechanism"
  ],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 3. Integrity Service (Port 8002)

#### Data Integrity Verification
```http
# Verify data integrity
POST /api/integrity/verify
Authorization: Bearer <token>
{
  "data": "Data to verify",
  "hash": "sha256_hash_value",
  "signature": "digital_signature"
}

# Create integrity record
POST /api/integrity/records
Authorization: Bearer <token>
{
  "data_type": "policy",
  "data_id": "policy_123",
  "hash": "sha256_hash",
  "metadata": {
    "created_by": "user_id",
    "timestamp": "2025-06-16T10:00:00Z"
  }
}
```

#### Audit Logging
```http
# Get audit logs
GET /api/integrity/audit-logs?start_date=2025-06-01&end_date=2025-06-16
Authorization: Bearer <token>

# Create audit entry
POST /api/integrity/audit-logs
Authorization: Bearer <token>
{
  "action": "policy_update",
  "resource": "policy_123",
  "user_id": "user_456",
  "details": {
    "changes": ["title", "description"],
    "previous_hash": "old_hash",
    "new_hash": "new_hash"
  }
}
```

### 4. Formal Verification Service (Port 8003)

#### Policy Verification
```http
# Verify policy against principles
POST /api/formal-verification/verify-policy
Authorization: Bearer <token>
{
  "policy_content": "Policy in Rego format",
  "principles": ["principle_1", "principle_2"],
  "verification_level": "comprehensive"
}

Response:
{
  "verification_result": "passed",
  "confidence_score": 0.92,
  "violations": [],
  "formal_proof": "Z3 proof output",
  "verification_time_ms": 450
}
```

#### Safety Property Checking
```http
# Check safety properties
POST /api/formal-verification/safety-check
Authorization: Bearer <token>
{
  "code": "Policy or rule code",
  "safety_properties": [
    "no_infinite_loops",
    "bounded_resources",
    "termination_guaranteed"
  ]
}
```

### 5. Governance Synthesis Service (Port 8004)

#### Policy Synthesis
```http
# Synthesize policy from principle
POST /api/governance-synthesis/synthesize
Authorization: Bearer <token>
{
  "principle": {
    "title": "Democratic Participation",
    "description": "Ensure democratic participation in governance"
  },
  "context": {
    "domain": "voting",
    "stakeholders": ["citizens", "officials"]
  },
  "synthesis_options": {
    "format": "rego",
    "validation_level": "comprehensive"
  }
}

Response:
{
  "synthesis_id": "synth_123",
  "policy_code": "package governance.voting...",
  "explanation": "This policy ensures democratic participation...",
  "confidence_score": 0.88,
  "validation_results": {
    "syntactic": "passed",
    "semantic": "passed",
    "formal": "passed"
  }
}
```

#### Multi-Model Validation
```http
# Validate with multiple models
POST /api/governance-synthesis/multi-model-validate
Authorization: Bearer <token>
{
  "policy_content": "Policy to validate",
  "models": ["gpt-4", "claude", "gemini-pro"],
  "consensus_threshold": 0.8
}
```

### 6. Policy Governance Compiler Service (Port 8005)

#### Real-time Policy Enforcement
```http
# Evaluate action against policies
POST /api/policy-governance/evaluate
Authorization: Bearer <token>
{
  "action": {
    "type": "vote",
    "user_id": "user_123",
    "proposal_id": "prop_456",
    "vote": "approve"
  },
  "context": {
    "timestamp": "2025-06-16T10:00:00Z",
    "session_id": "session_789"
  }
}

Response:
{
  "decision": "allow",
  "confidence": 0.95,
  "applied_policies": ["voting_policy", "participation_policy"],
  "evaluation_time_ms": 15,
  "constitutional_compliance": true
}
```

#### Constitutional Validation
```http
# Validate constitutional compliance
POST /api/policy-governance/constitutional-validate
Authorization: Bearer <token>
{
  "policy_hash": "policy_hash_value",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validation_context": {
    "strict_mode": true,
    "require_consensus": true
  }
}
```

### 7. Evolutionary Computation Service (Port 8006)

#### WINA Oversight
```http
# Execute WINA oversight
POST /api/evolutionary-computation/wina-oversight
Authorization: Bearer <token>
{
  "oversight_type": "performance_optimization",
  "governance_requirements": [
    "maintain_constitutional_compliance",
    "ensure_democratic_participation"
  ],
  "optimization_hints": {
    "focus_area": "efficiency",
    "constraints": ["safety", "fairness"]
  }
}
```

#### Performance Monitoring
```http
# Get performance metrics
GET /api/evolutionary-computation/performance-metrics
Authorization: Bearer <token>

# Record performance data
POST /api/evolutionary-computation/performance-data
Authorization: Bearer <token>
{
  "metric_type": "latency",
  "value": 25.5,
  "unit": "milliseconds",
  "context": {
    "service": "pgc",
    "operation": "policy_evaluation"
  }
}
```

### 8. Self-Evolving AI Service (Port 8007)

#### Evolution Management
```http
# Initiate evolution cycle
POST /api/self-evolving-ai/evolution/initiate
Authorization: Bearer <token>
{
  "evolution_type": "policy_optimization",
  "target_policies": ["voting_policy"],
  "proposed_changes": {
    "optimization_goal": "reduce_latency",
    "constraints": ["maintain_accuracy"]
  },
  "approval_required": true
}

# Get evolution status
GET /api/self-evolving-ai/evolution/{evolution_id}/status
Authorization: Bearer <token>

# Approve evolution
POST /api/self-evolving-ai/evolution/{evolution_id}/approve
Authorization: Bearer <token>
{
  "approval_decision": "approved",
  "approver_comments": "Changes look good for production"
}
```

#### Security Management
```http
# Get security status
GET /api/self-evolving-ai/security/status
Authorization: Bearer <token>

# Execute security assessment
POST /api/self-evolving-ai/security/assess
Authorization: Bearer <token>
{
  "assessment_type": "comprehensive",
  "target_components": ["evolution_engine", "policy_orchestrator"]
}
```

## 📊 Common Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "metadata": {
    "timestamp": "2025-06-16T10:00:00Z",
    "request_id": "req_123456",
    "processing_time_ms": 45
  }
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "policy_content",
      "reason": "Required field missing"
    }
  },
  "metadata": {
    "timestamp": "2025-06-16T10:00:00Z",
    "request_id": "req_123456",
    "trace_id": "trace_789"
  }
}
```

## 🚀 Performance Specifications

### Response Time Targets
- **Authentication**: <50ms
- **Constitutional Validation**: <100ms
- **Policy Enforcement**: <25ms
- **Formal Verification**: <500ms
- **Policy Synthesis**: <2000ms
- **Evolution Operations**: <10000ms

### Rate Limiting
- **Standard Users**: 1000 requests/hour
- **Premium Users**: 10000 requests/hour
- **Admin Users**: Unlimited
- **Burst Limit**: 100 requests/minute

### Pagination
```http
GET /api/service/endpoint?page=1&limit=50&sort=created_at&order=desc

Response:
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1250,
    "pages": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🔍 Health Checks & Monitoring

### Health Check Endpoints
```http
# Service health check
GET /health
Response: {"status": "healthy", "timestamp": "2025-06-16T10:00:00Z"}

# Detailed health check
GET /health/detailed
Response: {
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "external_apis": "healthy"
  },
  "metrics": {
    "response_time_ms": 25,
    "memory_usage": "45%",
    "cpu_usage": "12%"
  }
}
```

### Metrics Endpoints
```http
# Prometheus metrics
GET /metrics
Content-Type: text/plain

# Custom ACGS metrics
GET /api/metrics/acgs
Authorization: Bearer <token>
```

## 📚 SDK and Integration

### Python SDK Example
```python
from acgs_client import ACGSClient

# Initialize client
client = ACGSClient(
    base_url="https://api.acgs-1.com",
    api_key="your_api_key"
)

# Authenticate
token = client.auth.login("user@example.com", "password")

# Validate constitutional compliance
result = client.constitutional_ai.validate_compliance(
    policy_content="Policy text",
    context={"type": "governance"}
)

print(f"Compliance Score: {result.compliance_score}")
```

### JavaScript SDK Example
```javascript
import { ACGSClient } from '@acgs/client';

const client = new ACGSClient({
  baseURL: 'https://api.acgs-1.com',
  apiKey: 'your_api_key'
});

// Authenticate
const token = await client.auth.login('user@example.com', 'password');

// Synthesize policy
const synthesis = await client.governanceSynthesis.synthesize({
  principle: {
    title: 'Democratic Participation',
    description: 'Ensure democratic participation'
  },
  context: { domain: 'voting' }
});

console.log('Generated Policy:', synthesis.policy_code);
```

## 🎯 Best Practices

### API Usage Guidelines
1. **Always use HTTPS** for all API communications
2. **Implement proper error handling** for all API calls
3. **Use appropriate HTTP methods** (GET, POST, PUT, DELETE)
4. **Include request IDs** for debugging and tracing
5. **Implement exponential backoff** for retry logic
6. **Cache responses** where appropriate to reduce API calls

### Security Best Practices
1. **Store JWT tokens securely** (never in localStorage)
2. **Implement token refresh logic** before expiration
3. **Validate all inputs** before sending to API
4. **Use CSRF protection** for web applications
5. **Implement rate limiting** on client side
6. **Log security events** for audit purposes

## 🏆 API Conclusion

The ACGS-1 API provides comprehensive access to constitutional AI governance capabilities with enterprise-grade security, performance, and reliability. The API design follows REST principles with comprehensive documentation, SDKs, and monitoring capabilities to ensure successful integration and operation.

**Key API Features:**
- Comprehensive REST API across 8 core services
- JWT-based authentication with RBAC
- Real-time policy enforcement and validation
- Multi-model AI validation capabilities
- Constitutional compliance verification
- Comprehensive monitoring and health checks
- Production-ready performance and reliability
