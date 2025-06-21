# ACGS-1 API Specifications

**Version**: 3.0.0  
**Date**: 2025-06-16  
**Base URL**: `http://localhost`  
**Constitution Hash**: cdd01ef066bc6cf2

## Authentication

All API endpoints require JWT authentication except health endpoints.

### Headers

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Request-ID: <uuid> (optional)
```

### Authentication Endpoints

#### POST /auth/login

Authenticate user and receive JWT tokens.

**Request**:

```json
{
  "username": "string",
  "password": "string",
  "mfa_code": "string" (optional)
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "jwt_token",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "username": "string",
      "roles": ["admin", "user"]
    }
  }
}
```

## Core Service APIs

### Auth Service (Port 8000)

#### GET /health

Service health check.

**Response**:

```json
{
  "status": "healthy",
  "service": "auth_service",
  "version": "3.0.0",
  "timestamp": "2025-06-16T15:00:00Z"
}
```

#### POST /auth/refresh

Refresh JWT access token.

**Request**:

```json
{
  "refresh_token": "jwt_token"
}
```

### AC Service (Port 8001)

#### GET /api/v1/constitutional-council/members

Get constitutional council members.

**Response**:

```json
{
  "status": "success",
  "data": {
    "members": [
      {
        "id": "council_001",
        "name": "Constitutional Council Member 1",
        "active": true
      }
    ],
    "required_signatures": 5,
    "total_members": 7,
    "constitutional_hash": "cdd01ef066bc6cf2"
  }
}
```

#### GET /api/v1/voting/mechanisms

Get available voting mechanisms.

**Response**:

```json
{
  "status": "success",
  "data": {
    "mechanisms": [
      {
        "id": "supermajority",
        "name": "Supermajority Voting",
        "threshold": 0.67,
        "description": "Requires 2/3 majority for constitutional changes"
      }
    ],
    "default_mechanism": "supermajority",
    "constitutional_hash": "cdd01ef066bc6cf2"
  }
}
```

#### POST /api/v1/constitutional/validate

Validate constitutional compliance.

**Request**:

```json
{
  "action": "string",
  "context": {
    "policy_id": "string",
    "user_id": "string",
    "metadata": {}
  },
  "validation_level": "basic|comprehensive"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "validation_result": {
      "compliant": true,
      "confidence": 0.95,
      "hash_valid": true,
      "principles_checked": 15,
      "violations": []
    },
    "constitutional_hash": "cdd01ef066bc6cf2",
    "timestamp": "2025-06-16T15:00:00Z"
  }
}
```

### Integrity Service (Port 8002)

#### POST /api/v1/verify/signature

Verify digital signature.

**Request**:

```json
{
  "data": "string",
  "signature": "string",
  "public_key": "string",
  "algorithm": "RSA|ECDSA"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "valid": true,
    "algorithm": "RSA",
    "key_size": 2048,
    "timestamp": "2025-06-16T15:00:00Z"
  }
}
```

#### POST /api/v1/verify/hash

Verify hash integrity.

**Request**:

```json
{
  "data": "string",
  "expected_hash": "string",
  "algorithm": "SHA256|SHA512"
}
```

### FV Service (Port 8003)

#### POST /api/v1/verify/policy

Formally verify policy.

**Request**:

```json
{
  "policy": {
    "id": "string",
    "rules": [],
    "constraints": []
  },
  "verification_type": "satisfiability|consistency|completeness"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "verified": true,
    "proof": "string",
    "constraints_satisfied": 15,
    "verification_time_ms": 250,
    "timestamp": "2025-06-16T15:00:00Z"
  }
}
```

### GS Service (Port 8004)

#### POST /api/v1/synthesize/policy

Synthesize new policy using AI.

**Request**:

```json
{
  "requirements": "string",
  "context": {},
  "risk_level": "standard|enhanced_validation|multi_model_consensus|human_review",
  "target_domain": "string"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "policy": {
      "id": "generated_uuid",
      "title": "string",
      "content": "string",
      "rules": [],
      "metadata": {}
    },
    "synthesis_confidence": 0.92,
    "risk_assessment": "low",
    "models_used": ["qwen3-32b", "deepseek-chat-v3"],
    "generation_time_ms": 1500
  }
}
```

### PGC Service (Port 8005)

#### POST /api/v1/governance-workflows/policy-creation

Initiate policy creation workflow.

**Request**:

```json
{
  "policy_data": {
    "title": "string",
    "description": "string",
    "category": "string",
    "priority": "high|medium|low"
  },
  "workflow_options": {
    "require_formal_verification": true,
    "require_constitutional_review": true,
    "auto_approve": false
  }
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "workflow_id": "uuid",
    "status": "initiated",
    "constitutional_compliance": {
      "compliant": true,
      "confidence": 0.95
    },
    "next_steps": ["review", "approval", "implementation"],
    "estimated_completion": "2025-06-16T16:00:00Z",
    "constitutional_hash": "cdd01ef066bc6cf2"
  }
}
```

#### GET /api/v1/compliance/status

Get compliance status overview.

**Response**:

```json
{
  "status": "success",
  "data": {
    "overall_compliance": 0.98,
    "active_policies": 45,
    "violations_last_24h": 2,
    "constitutional_hash": "cdd01ef066bc6cf2",
    "last_validation": "2025-06-16T15:00:00Z"
  }
}
```

### EC Service (Port 8006)

#### POST /api/v1/oversight/decision

Record executive decision.

**Request**:

```json
{
  "decision": {
    "title": "string",
    "description": "string",
    "category": "policy|operational|strategic",
    "impact_level": "high|medium|low"
  },
  "justification": "string",
  "stakeholders": ["string"]
}
```

#### GET /api/v1/audit/trail

Get audit trail.

**Query Parameters**:

- `start_date`: ISO 8601 date
- `end_date`: ISO 8601 date
- `category`: Filter by category
- `limit`: Number of results (default: 100)

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "username",
      "reason": "Required field missing"
    },
    "trace_id": "uuid"
  },
  "timestamp": "2025-06-16T15:00:00Z"
}
```

### Common Error Codes

- `AUTHENTICATION_FAILED` - Invalid credentials
- `AUTHORIZATION_DENIED` - Insufficient permissions
- `VALIDATION_ERROR` - Input validation failed
- `CONSTITUTIONAL_VIOLATION` - Action violates constitution
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `SERVICE_UNAVAILABLE` - Dependent service down
- `INTERNAL_ERROR` - Unexpected server error

## Rate Limiting

### Limits

- **Authentication**: 10 requests/minute
- **General APIs**: 100 requests/minute
- **Health Checks**: 1000 requests/minute
- **Constitutional Validation**: 50 requests/minute

### Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Governance Workflow APIs

### Policy Lifecycle States

1. `draft` - Initial creation
2. `review` - Under constitutional review
3. `verification` - Formal verification in progress
4. `approved` - Ready for implementation
5. `active` - Currently enforced
6. `deprecated` - No longer active
7. `rejected` - Failed review process

### Workflow Status Endpoints

#### GET /api/v1/workflows/{workflow_id}/status

Get workflow status.

#### POST /api/v1/workflows/{workflow_id}/advance

Advance workflow to next stage.

#### GET /api/v1/workflows/active

List active workflows.

## WebSocket APIs

### Real-time Updates

Connect to `ws://localhost:8005/ws/governance` for real-time governance updates.

**Message Format**:

```json
{
  "type": "policy_update|compliance_alert|workflow_status",
  "data": {},
  "timestamp": "2025-06-16T15:00:00Z"
}
```

---

**Document Maintained By**: ACGS-1 API Team  
**Last Updated**: 2025-06-16  
**Next Review**: 2025-07-16
