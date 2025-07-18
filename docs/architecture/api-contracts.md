# ACGS-2 API Contract Documentation
**Constitutional Hash: cdd01ef066bc6cf2**
**Generated: 2025-07-18T13:13:22Z**

## Overview

This document defines the API contracts for inter-service communication within the ACGS-2 system, ensuring consistent and reliable integration between all service layers.

## Global Standards

### Constitutional Compliance
All API responses must include the constitutional hash validation:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "hash_validated": true,
  "compliance_status": "COMPLIANT"
}
```

### Authentication Headers
All authenticated requests must include:
```
Authorization: Bearer <jwt_token>
X-Constitutional-Hash: cdd01ef066bc6cf2
X-Service-Name: <calling_service>
X-Request-ID: <unique_request_id>
```

### Response Format
Standardized response structure:
```json
{
  "status": "success|error",
  "data": {},
  "metadata": {
    "timestamp": "2025-07-18T13:13:22Z",
    "service": "service_name",
    "version": "1.0.0",
    "constitutional_hash": "cdd01ef066bc6cf2"
  },
  "errors": []
}
```

## Core Services API Contracts

### 1. Constitutional AI Service (Port 8001)

#### Base URL: `http://constitutional-ai:8001`

#### Health Check
```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "service": "constitutional-ai",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-18T13:13:22Z",
  "version": "1.0.0"
}
```

#### Constitutional Validation
```
POST /validation
Content-Type: application/json

Request:
{
  "content": "Policy text to validate",
  "policy_type": "general|specific",
  "context": {}
}

Response: 200 OK
{
  "valid": true,
  "compliance_score": 0.95,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-18T13:13:22Z",
  "details": {
    "violations": [],
    "recommendations": [],
    "confidence": 0.98
  }
}
```

#### Compliance Scoring
```
POST /compliance/score
Content-Type: application/json

Request:
{
  "policies": ["policy1", "policy2"],
  "context": {},
  "evaluation_criteria": []
}

Response: 200 OK
{
  "overall_score": 0.92,
  "individual_scores": {
    "policy1": 0.95,
    "policy2": 0.89
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "details": {}
}
```

### 2. Policy Governance Service (Port 8003)

#### Base URL: `http://policy-governance:8003`

#### Policy Creation
```
POST /policies
Content-Type: application/json

Request:
{
  "name": "Policy Name",
  "description": "Policy description",
  "rules": [],
  "priority": 1,
  "category": "governance|compliance|security"
}

Response: 201 Created
{
  "policy_id": "pol_123456",
  "status": "created",
  "constitutional_validation": {
    "valid": true,
    "hash": "cdd01ef066bc6cf2"
  }
}
```

#### Policy Evaluation
```
POST /policies/evaluate
Content-Type: application/json

Request:
{
  "policy_id": "pol_123456",
  "context": {},
  "data": {}
}

Response: 200 OK
{
  "evaluation_result": "compliant|non_compliant|partial",
  "score": 0.95,
  "violations": [],
  "recommendations": []
}
```

### 3. Evolutionary Computation Service (Port 8004)

#### Base URL: `http://evolutionary-computation:8004`

#### Evolution Execution
```
POST /evolution/execute
Content-Type: application/json

Request:
{
  "population_size": 100,
  "generations": 50,
  "fitness_function": "constitutional_compliance",
  "constraints": {},
  "constitutional_hash": "cdd01ef066bc6cf2"
}

Response: 200 OK
{
  "evolution_id": "evo_123456",
  "status": "running",
  "estimated_completion": "2025-07-18T13:30:00Z"
}
```

#### Evolution Results
```
GET /evolution/{evolution_id}/results
Response: 200 OK
{
  "evolution_id": "evo_123456",
  "status": "completed",
  "best_solution": {},
  "fitness_score": 0.96,
  "constitutional_compliance": true,
  "generations_completed": 50
}
```

### 4. Formal Verification Service (Port 8005)

#### Base URL: `http://formal-verification:8005`

#### Verification Request
```
POST /verification/verify
Content-Type: application/json

Request:
{
  "system_specification": {},
  "properties_to_verify": [],
  "verification_method": "model_checking|theorem_proving",
  "constitutional_constraints": []
}

Response: 200 OK
{
  "verification_id": "ver_123456",
  "status": "verified|failed|pending",
  "properties_verified": [],
  "counterexamples": [],
  "constitutional_compliance": true
}
```

## Platform Services API Contracts

### 1. Authentication Service (Port 8006)

#### Base URL: `http://authentication:8006`

#### User Authentication
```
POST /auth/login
Content-Type: application/json

Request:
{
  "username": "user@example.com",
  "password": "secure_password",
  "constitutional_hash": "cdd01ef066bc6cf2"
}

Response: 200 OK
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "expires_in": 3600,
  "token_type": "Bearer",
  "constitutional_compliance": true
}
```

#### Token Validation
```
POST /auth/validate
Content-Type: application/json

Request:
{
  "token": "jwt_token",
  "constitutional_hash": "cdd01ef066bc6cf2"
}

Response: 200 OK
{
  "valid": true,
  "user_id": "user_123",
  "permissions": [],
  "expires_at": "2025-07-18T14:13:22Z"
}
```

### 2. Integrity Service (Port 8002)

#### Base URL: `http://integrity:8002`

#### Audit Log Creation
```
POST /audit/log
Content-Type: application/json

Request:
{
  "event_type": "policy_change|access_granted|validation_performed",
  "user_id": "user_123",
  "service": "constitutional-ai",
  "action": "policy_validation",
  "details": {},
  "constitutional_hash": "cdd01ef066bc6cf2"
}

Response: 201 Created
{
  "audit_id": "audit_123456",
  "timestamp": "2025-07-18T13:13:22Z",
  "integrity_verified": true
}
```

#### Integrity Verification
```
GET /integrity/verify/{resource_id}
Response: 200 OK
{
  "resource_id": "resource_123",
  "integrity_status": "verified|compromised|unknown",
  "hash_chain_valid": true,
  "constitutional_compliance": true,
  "last_verified": "2025-07-18T13:13:22Z"
}
```

### 3. API Gateway Service (Port 8000)

#### Base URL: `http://api-gateway:8000`

#### Service Registration
```
POST /gateway/register
Content-Type: application/json

Request:
{
  "service_name": "new-service",
  "service_url": "http://new-service:8080",
  "health_check_url": "/health",
  "constitutional_hash": "cdd01ef066bc6cf2"
}

Response: 201 Created
{
  "registration_id": "reg_123456",
  "status": "registered",
  "load_balancer_weight": 1.0
}
```

#### Route Configuration
```
POST /gateway/routes
Content-Type: application/json

Request:
{
  "path": "/api/v1/policies",
  "target_service": "policy-governance",
  "methods": ["GET", "POST"],
  "authentication_required": true,
  "rate_limit": 100
}

Response: 201 Created
{
  "route_id": "route_123456",
  "status": "active"
}
```

## Protocol Services API Contracts

### 1. MCP Aggregator Service (Port 8010)

#### Base URL: `http://mcp-aggregator:8010`

#### MCP Service Registration
```
POST /mcp/register
Content-Type: application/json

Request:
{
  "service_name": "mcp-filesystem",
  "service_url": "http://mcp-filesystem:8012",
  "capabilities": ["file_operations", "directory_listing"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}

Response: 201 Created
{
  "registration_id": "mcp_reg_123456",
  "status": "registered"
}
```

#### MCP Operation Execution
```
POST /mcp/execute
Content-Type: application/json

Request:
{
  "service": "mcp-filesystem",
  "operation": "list_files",
  "parameters": {
    "path": "/project/src"
  }
}

Response: 200 OK
{
  "operation_id": "op_123456",
  "result": {},
  "constitutional_compliance": true
}
```

## Security and Compliance

### Constitutional Hash Validation
All services must validate the constitutional hash in requests:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "hash_validation": {
    "valid": true,
    "validated_at": "2025-07-18T13:13:22Z",
    "validator_service": "constitutional-ai"
  }
}
```

### Rate Limiting
Standard rate limits apply to all endpoints:
- **Authentication**: 10 requests/minute
- **Core Services**: 1000 requests/minute
- **Platform Services**: 500 requests/minute
- **Protocol Services**: 100 requests/minute

### Error Handling
Standardized error responses:
```json
{
  "error": {
    "code": "CONSTITUTIONAL_VIOLATION",
    "message": "Constitutional hash validation failed",
    "details": {
      "expected_hash": "cdd01ef066bc6cf2",
      "received_hash": "invalid_hash"
    },
    "timestamp": "2025-07-18T13:13:22Z"
  }
}
```

## Monitoring and Observability

### Health Check Standards
All services must implement:
```
GET /health
Response: 200 OK
{
  "status": "healthy|unhealthy|degraded",
  "service": "service_name",
  "version": "1.0.0",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-18T13:13:22Z",
  "dependencies": {
    "database": "healthy",
    "cache": "healthy",
    "constitutional_ai": "healthy"
  }
}
```

### Metrics Endpoints
```
GET /metrics
Response: 200 OK
# Prometheus format metrics
constitutional_compliance_score{service="constitutional-ai"} 0.95
request_duration_seconds{service="constitutional-ai",endpoint="/validation"} 0.002
```

## Service Discovery

### Service Registration
Services register with the service discovery system:
```
POST /discovery/register
Content-Type: application/json

Request:
{
  "service_name": "constitutional-ai",
  "service_url": "http://constitutional-ai:8001",
  "capabilities": ["validation", "compliance_scoring"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Service Lookup
```
GET /discovery/services/{service_name}
Response: 200 OK
{
  "service_name": "constitutional-ai",
  "instances": [
    {
      "url": "http://constitutional-ai:8001",
      "status": "healthy",
      "last_heartbeat": "2025-07-18T13:13:22Z"
    }
  ]
}
```

## Deployment and Scaling

### Container Health Checks
Docker compose health check configuration:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

### Load Balancing
Services support multiple instances with load balancing:
```yaml
deploy:
  replicas: 3
  update_config:
    parallelism: 1
    delay: 10s
  restart_policy:
    condition: on-failure
```

---

**HASH-OK:cdd01ef066bc6cf2**

This API contract documentation ensures consistent, secure, and compliant communication between all ACGS-2 services while maintaining constitutional governance principles.
