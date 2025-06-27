# ACGS API Reference - Consolidated Guide

**Version**: 3.0  
**Last Updated**: 2025-06-27  
**Base URL**: `http://localhost:8000` (development)

## 🎯 Overview

This consolidated guide provides complete API reference for all ACGS services with consistent documentation format, authentication requirements, and examples.

## 🔐 Authentication

All API endpoints require JWT authentication unless otherwise specified.

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure_password"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer <JWT_TOKEN>" \
  http://localhost:8001/api/constitutional-ai/principles
```

## 🏗️ Service Architecture

| Service                  | Port | Base URL                         | Implementation Status   | Interactive Docs |
| ------------------------ | ---- | -------------------------------- | ----------------------- | ---------------- |
| Authentication           | 8000 | `/api/auth/`                     | ✅ **Production Ready** | `/docs`          |
| Constitutional AI        | 8001 | `/api/constitutional-ai/`        | ✅ **Production Ready** | `/docs`          |
| Integrity                | 8002 | `/api/integrity/`                | ✅ **Production Ready** | `/docs`          |
| Formal Verification      | 8003 | `/api/formal-verification/`      | 🧪 **Prototype**        | `/docs`          |
| Governance Synthesis     | 8004 | `/api/governance-synthesis/`     | 🧪 **Prototype**        | `/docs`          |
| Policy Governance        | 8005 | `/api/policy-governance/`        | 🧪 **Prototype**        | `/docs`          |
| Evolutionary Computation | 8006 | `/api/evolutionary-computation/` | 🧪 **Prototype**        | `/docs`          |
| Darwin Gödel Machine     | 8007 | `/api/dgm/`                      | 🧪 **Prototype**        | `/docs`          |

### Implementation Status Notes

- **✅ Production Ready**: Fully implemented with comprehensive features and production-grade security
- **🧪 Prototype**: Functional implementation with limitations (mock components, debug modes, disabled features)

## 📊 Monitoring & Health Endpoints

All services expose standard monitoring and health endpoints:

### Health Check
```bash
GET /health
# Returns service health status
{
  "status": "healthy",
  "service": "authentication-service",
  "version": "3.0.0",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-06-27T12:00:00Z"
}
```

### Prometheus Metrics
```bash
GET /metrics
# Returns Prometheus-formatted metrics
# TYPE http_requests_total counter
# HELP http_requests_total Total number of HTTP requests
http_requests_total{method="GET",status="200"} 1234
```

### Service Info
```bash
GET /info
# Returns detailed service information
{
  "service": "constitutional-ai-service",
  "version": "3.0.0",
  "environment": "production",
  "features": ["compliance_validation", "multi_model_consensus"],
  "dependencies": ["auth-service", "integrity-service"]
}
```

## 📋 Common Response Formats

### Success Response

```json
{
  "success": true,
  "data": {
    /* response data */
  },
  "timestamp": "2025-06-23T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      /* error details */
    }
  },
  "timestamp": "2025-06-23T10:30:00Z",
  "request_id": "req_123456789"
}
```

## 🔑 Authentication Service (Port 8000)

### Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### Refresh Token

```bash
POST /api/auth/refresh
Authorization: Bearer <JWT_TOKEN>
```

### User Profile

```bash
GET /api/auth/profile
Authorization: Bearer <JWT_TOKEN>
```

## 🏛️ Constitutional AI Service (Port 8001)

### Get Constitutional Principles

```bash
GET /api/constitutional-ai/principles
Authorization: Bearer <JWT_TOKEN>

# Response
{
  "success": true,
  "data": {
    "principles": [
      {
        "id": "principle_001",
        "title": "Transparency Principle",
        "description": "All governance actions must be transparent",
        "priority": 1,
        "status": "active"
      }
    ]
  }
}
```

### Create Constitutional Principle

```bash
POST /api/constitutional-ai/principles
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "priority": 1,
  "category": "governance|ethics|transparency"
}
```

### Validate Policy Against Constitution

```bash
POST /api/constitutional-ai/validate
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "policy_text": "string",
  "policy_category": "string",
  "validation_level": "basic|comprehensive|strict"
}

# Response
{
  "success": true,
  "data": {
    "is_constitutional": true,
    "confidence_score": 0.95,
    "violations": [],
    "recommendations": [
      "Consider adding transparency requirements"
    ]
  }
}
```

## 🔍 Integrity Service (Port 8002)

### Check System Integrity

```bash
GET /api/integrity/check
Authorization: Bearer <JWT_TOKEN>

# Response
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "components": {
      "database": "healthy",
      "blockchain": "healthy",
      "services": "healthy"
    },
    "last_check": "2025-06-23T10:30:00Z"
  }
}
```

### Verify Data Integrity

```bash
POST /api/integrity/verify
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "data_type": "policy|vote|proposal",
  "data_id": "string",
  "hash": "string"
}
```

## ✅ Formal Verification Service (Port 8003)

### Verify Policy Formally

```bash
POST /api/formal-verification/verify
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "policy_specification": "string",
  "verification_type": "safety|liveness|correctness",
  "timeout_seconds": 300
}

# Response
{
  "success": true,
  "data": {
    "verification_result": "verified|failed|timeout",
    "proof": "string",
    "counterexample": null,
    "execution_time_ms": 1250
  }
}
```

### Get Verification History

```bash
GET /api/formal-verification/history?policy_id=<ID>
Authorization: Bearer <JWT_TOKEN>
```

## 🧠 Governance Synthesis Service (Port 8004)

### Synthesize Policy

```bash
POST /api/governance-synthesis/synthesize
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "requirements": ["string"],
  "constraints": ["string"],
  "stakeholder_input": ["string"],
  "synthesis_model": "gpt-4|claude|gemini"
}

# Response
{
  "success": true,
  "data": {
    "synthesized_policy": "string",
    "confidence_score": 0.87,
    "alternative_options": ["string"],
    "reasoning": "string"
  }
}
```

### Multi-Model Validation

```bash
POST /api/governance-synthesis/validate-multi-model
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "policy_text": "string",
  "models": ["gpt-4", "claude", "gemini"],
  "validation_criteria": ["consistency", "feasibility", "ethics"]
}
```

## 📋 Policy Governance Service (Port 8005)

### Create Policy Proposal

```bash
POST /api/policy-governance/proposals
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "title": "string",
  "description": "string",
  "policy_text": "string",
  "category": "string",
  "impact_assessment": "string"
}
```

### Vote on Proposal

```bash
POST /api/policy-governance/proposals/{proposal_id}/vote
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "vote": "approve|reject|abstain",
  "reasoning": "string",
  "weight": 1.0
}
```

### Get Policy Status

```bash
GET /api/policy-governance/policies/{policy_id}/status
Authorization: Bearer <JWT_TOKEN>

# Response
{
  "success": true,
  "data": {
    "policy_id": "string",
    "status": "draft|review|approved|rejected|active|deprecated",
    "approval_score": 0.85,
    "votes": {
      "approve": 15,
      "reject": 3,
      "abstain": 2
    },
    "next_review_date": "2025-07-23T00:00:00Z"
  }
}
```

## 🧬 Evolutionary Computation Service (Port 8006)

### Evolve Policy

```bash
POST /api/evolutionary-computation/evolve
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "base_policy": "string",
  "fitness_criteria": ["effectiveness", "fairness", "efficiency"],
  "generations": 10,
  "population_size": 50
}
```

### Get Evolution History

```bash
GET /api/evolutionary-computation/evolution/{evolution_id}/history
Authorization: Bearer <JWT_TOKEN>
```

## 🤖 Darwin Gödel Machine Service (Port 8007)

### Submit Learning Task

```bash
POST /api/dgm/learn
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "task_type": "policy_optimization|governance_improvement",
  "input_data": "string",
  "learning_parameters": {
    "iterations": 1000,
    "learning_rate": 0.01
  }
}
```

### Get Learning Progress

```bash
GET /api/dgm/tasks/{task_id}/progress
Authorization: Bearer <JWT_TOKEN>

# Response
{
  "success": true,
  "data": {
    "task_id": "string",
    "status": "running|completed|failed",
    "progress": 0.75,
    "current_iteration": 750,
    "estimated_completion": "2025-06-23T11:00:00Z"
  }
}
```

## 📊 Common Query Parameters

### Pagination

```bash
GET /api/service/endpoint?page=1&limit=20&sort=created_at&order=desc
```

### Filtering

```bash
GET /api/service/endpoint?status=active&category=governance&created_after=2025-01-01
```

### Response Format

```bash
GET /api/service/endpoint?format=json&include=metadata&fields=id,title,status
```

## 🚨 Error Codes

| Code                       | Description                     | HTTP Status |
| -------------------------- | ------------------------------- | ----------- |
| `AUTH_REQUIRED`            | Authentication required         | 401         |
| `INSUFFICIENT_PERMISSIONS` | Insufficient permissions        | 403         |
| `RESOURCE_NOT_FOUND`       | Resource not found              | 404         |
| `VALIDATION_ERROR`         | Input validation failed         | 400         |
| `RATE_LIMIT_EXCEEDED`      | Rate limit exceeded             | 429         |
| `INTERNAL_ERROR`           | Internal server error           | 500         |
| `SERVICE_UNAVAILABLE`      | Service temporarily unavailable | 503         |

## 📞 Support and Resources

- **Interactive Documentation**: Visit `http://localhost:800X/docs` for each service
- **Health Checks**: `GET /health` endpoint available on all services
- **Rate Limits**: 1000 requests/hour per authenticated user
- **Support**: [GitHub Issues](https://github.com/CA-git-com-co/ACGS/issues)

---

**API Version**: 2.0  
**Last Updated**: 2025-06-23  
**Compatibility**: All ACGS services v2.0+
