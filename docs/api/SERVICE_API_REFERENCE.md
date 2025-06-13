# ACGS-1 Service API Reference

This document provides comprehensive API documentation for all 7 core services in the ACGS-1 constitutional AI governance system.

## Service Architecture Overview

ACGS-1 operates with 7 core services running on dedicated ports:

| Service | Port | Purpose | Authentication |
|---------|------|---------|----------------|
| Authentication Service | 8000 | User auth, MFA, RBAC | OAuth 2.0, JWT |
| Constitutional AI Service | 8001 | Constitutional validation | API Key + JWT |
| Integrity Service | 8002 | Cryptographic integrity | PGP + API Key |
| Formal Verification Service | 8003 | Mathematical verification | API Key |
| Governance Synthesis Service | 8004 | Policy synthesis | API Key + JWT |
| Policy Governance Service | 8005 | Policy enforcement | API Key + JWT |
| Evolutionary Computation Service | 8006 | WINA oversight | API Key |

## Authentication Service (Port 8000)

**Base URL**: `http://localhost:8000`
**Implementation**: `services/platform/authentication/auth_service/`

### Core Endpoints

#### POST /auth/login
Authenticate user with credentials
```json
{
  "username": "string",
  "password": "string",
  "mfa_token": "string (optional)"
}
```

#### POST /auth/register
Register new user account
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "string"
}
```

#### GET /auth/profile
Get current user profile (requires JWT)

#### POST /auth/refresh
Refresh JWT token

### Dependencies
- PostgreSQL database for user storage
- Redis for session management
- OAuth 2.0 providers (optional)

## Constitutional AI Service (Port 8001)

**Base URL**: `http://localhost:8001`
**Implementation**: `services/core/constitutional-ai/ac_service/`

### Core Endpoints

#### POST /constitutional/validate
Validate content against constitutional principles
```json
{
  "content": "string",
  "context": "string",
  "principles": ["principle1", "principle2"]
}
```

#### GET /constitutional/principles
List all constitutional principles

#### POST /constitutional/human-in-loop
Submit content for human review
```json
{
  "content": "string",
  "uncertainty_score": "float",
  "review_type": "string"
}
```

#### GET /constitutional/compliance/{policy_id}
Check policy compliance status

### Dependencies
- OpenAI API for LLM processing
- Gemini API for multi-model validation
- PostgreSQL for principle storage

## Integrity Service (Port 8002)

**Base URL**: `http://localhost:8002`
**Implementation**: `services/platform/integrity/integrity_service/`

### Core Endpoints

#### POST /integrity/verify
Verify cryptographic integrity
```json
{
  "data": "string",
  "signature": "string",
  "public_key": "string"
}
```

#### POST /integrity/sign
Create digital signature
```json
{
  "data": "string",
  "private_key": "string"
}
```

#### POST /integrity/appeals
Submit governance appeal
```json
{
  "case_id": "string",
  "appeal_reason": "string",
  "evidence": "string"
}
```

#### GET /integrity/appeals/{appeal_id}
Get appeal status

### Dependencies
- PGP cryptographic libraries
- PostgreSQL for appeal storage
- Research data pipeline integration

## Formal Verification Service (Port 8003)

**Base URL**: `http://localhost:8003`
**Implementation**: `services/core/formal-verification/fv_service/`

### Core Endpoints

#### POST /verification/verify
Formally verify policy or contract
```json
{
  "code": "string",
  "properties": ["safety", "liveness"],
  "solver": "z3"
}
```

#### POST /verification/batch
Batch verification of multiple items
```json
{
  "items": [
    {
      "id": "string",
      "code": "string",
      "properties": ["string"]
    }
  ]
}
```

#### GET /verification/status/{verification_id}
Get verification status

#### POST /verification/adversarial
Run adversarial robustness testing
```json
{
  "target": "string",
  "test_suite": "string",
  "iterations": "integer"
}
```

### Dependencies
- Z3 SMT solver
- Parallel processing infrastructure
- Mathematical verification libraries

## Governance Synthesis Service (Port 8004)

**Base URL**: `http://localhost:8004`
**Implementation**: `services/core/governance-synthesis/gs_service/`

### Core Endpoints

#### POST /synthesis/generate
Generate policy from principles
```json
{
  "principles": ["string"],
  "context": "string",
  "stakeholders": ["string"],
  "constraints": {}
}
```

#### POST /synthesis/validate
Validate synthesized policy
```json
{
  "policy": "string",
  "validation_type": "multi_model",
  "models": ["gpt-4", "gemini-pro"]
}
```

#### GET /synthesis/history/{synthesis_id}
Get synthesis history

#### POST /synthesis/alphaevolve
Enhanced synthesis with AlphaEvolve
```json
{
  "base_policy": "string",
  "optimization_target": "string",
  "iterations": "integer"
}
```

### Dependencies
- Multiple LLM APIs (OpenAI, Gemini)
- AlphaEvolve integration
- QEC error correction algorithms

## Policy Governance Service (Port 8005)

**Base URL**: `http://localhost:8005`
**Implementation**: `services/core/policy-governance/pgc_service/`

### Core Endpoints

#### POST /governance/enforce
Enforce policy decision
```json
{
  "policy_id": "string",
  "context": {},
  "decision_required": "boolean"
}
```

#### GET /governance/workflows
List all governance workflows

#### POST /governance/workflows/{workflow_type}
Execute specific governance workflow
```json
{
  "workflow_type": "policy_creation|compliance|enforcement|audit",
  "parameters": {},
  "stakeholders": ["string"]
}
```

#### GET /governance/policies
List all active policies

#### POST /governance/amendment
Submit constitutional amendment
```json
{
  "amendment_text": "string",
  "justification": "string",
  "impact_analysis": "string"
}
```

### Dependencies
- Open Policy Agent (OPA)
- Constitutional AI Service
- Multi-stakeholder coordination system

## Evolutionary Computation Service (Port 8006)

**Base URL**: `http://localhost:8006`
**Implementation**: `services/core/evolutionary-computation/ec_service/`

### Core Endpoints

#### GET /wina/oversight
Get WINA oversight status
```json
{
  "metrics": {
    "performance_score": "float",
    "compliance_rate": "float",
    "optimization_suggestions": ["string"]
  }
}
```

#### POST /wina/optimize
Run governance optimization
```json
{
  "target_metrics": ["performance", "compliance"],
  "constraints": {},
  "evolution_parameters": {}
}
```

#### GET /wina/performance
Get performance monitoring data

#### POST /wina/feedback
Submit learning feedback
```json
{
  "feedback_type": "performance|compliance|optimization",
  "data": {},
  "recommendations": ["string"]
}
```

### Dependencies
- WINA optimization algorithms
- Performance monitoring infrastructure
- Constitutional compliance verification

## Inter-Service Communication

Services communicate through:
- **HTTP REST APIs** for synchronous operations
- **Message queues** for asynchronous workflows
- **Shared database** for persistent state
- **Event streaming** for real-time updates

## Error Handling

All services follow consistent error response format:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "timestamp": "ISO8601"
  }
}
```

## Rate Limiting

- **Authentication Service**: 100 requests/minute per IP
- **Other Services**: 1000 requests/minute per API key
- **Governance Operations**: 10 requests/minute per user

## Health Checks

All services expose health check endpoints:
- `GET /health` - Basic health status
- `GET /health/detailed` - Comprehensive health metrics
- `GET /metrics` - Prometheus-compatible metrics
