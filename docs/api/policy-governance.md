# Policy Governance API Documentation

## Service Overview

This service provides core functionality for the ACGS platform with constitutional compliance validation.

**Service**: Policy Governance
**Port**: 8XXX
**Constitutional Hash**: `cdd01ef066bc6cf2`


**Service**: Policy Governance Service
**Port**: 8005
**Base URL**: `http://localhost:8005/api/v1`
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This document provides comprehensive documentation for the Policy Governance Service (Port 8005) API, covering endpoints for policy evaluation, compliance validation, governance workflows, and more.

### Base URL

`http://localhost:8005`

### Health Check

`GET /health`

### Metrics

`GET /metrics`

## Key Endpoints

### Policy Evaluation

**Endpoint:** `POST /api/v1/policies/evaluate`

**Description:** Evaluate a policy against governance criteria

**Request Body:**
```json
{
  "policy_id": "string",
  "input_data": {,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
}
```

**Response:**
```json
{
  "evaluation_result": "approved",
  "compliance_score": 0.85,
  "reasons": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Example Request:**
```javascript
const evaluation = await fetch('http://localhost:8005/api/v1/policies/evaluate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <jwt_token>'
  },
  body: JSON.stringify({
    policy_id: 'POL001',
    input_data: { context: 'government' }
  })
});

const result = await evaluation.json();
console.log(result);
```

**Example Response:**
```json
{
  "evaluation_result": "approved",
  "compliance_score": 0.9,
  "reasons": ["Policy aligns with constitutional principles"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Compliance Validation

**Endpoint:** `POST /api/v1/compliance/validate`

**Description:** Validate policy compliance with constitutional standards

**Request Body:**
```json
{
  "policy_id": "string",
  "compliance_checks": ["string"]
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "compliance_status": "compliant",
  "violations": [],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Example Request:**
```javascript
const validation = await fetch('http://localhost:8005/api/v1/compliance/validate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <jwt_token>'
  },
  body: JSON.stringify({
    policy_id: 'POL001',
    compliance_checks: ["equality", "transparency"]
  })
});

const result = await validation.json();
console.log(result);
```

**Example Response:**
```json
{
  "compliance_status": "compliant",
  "violations": [],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Governance Workflow

**Endpoint:** `POST /api/v1/governance/workflow`

**Description:** Initiate a governance workflow for a policy

**Request Body:**
```json
{
  "policy_id": "string",
  "workflow_steps": ["string"]
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "workflow_id": "string",
  "status": "pending",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Example Request:**
```javascript
const workflow = await fetch('http://localhost:8005/api/v1/governance/workflow', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <jwt_token>'
  },
  body: JSON.stringify({
    policy_id: 'POL001',
    workflow_steps: ["evaluation", "compliance_check", "council_review"]
  })
});

const result = await workflow.json();
console.log(result);
```

**Example Response:**
```json
{
  "workflow_id": "WF001",
  "status": "pending",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Council Review

**Endpoint:** `POST /api/v1/council/review`

**Description:** Submit a policy for council review

**Request Body:**
```json
{
  "policy_id": "string",
  "council_members": ["string"]
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "review_id": "string",
  "status": "submitted",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Example Request:**
```javascript
const review = await fetch('http://localhost:8005/api/v1/council/review', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <jwt_token>'
  },
  body: JSON.stringify({
    policy_id: 'POL001',
    council_members: ["member1", "member2"]
  })
});

const result = await review.json();
console.log(result);
```

**Example Response:**
```json
{
  "review_id": "REV001",
  "status": "submitted",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## Additional Resources

- [API Documentation Index](index.md)
- [Governance Workflow Design](#Governance Workflow Design)
- [Council Review Process](#Council Review Process)

For system configuration details, deployment guides, and architecture diagrams, see the Policy Governance service documentation repository.
## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries (latency_p99: ≤5ms)
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Test Coverage**: ≥ 80%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## Error Handling

Standard HTTP status codes are used with detailed error messages:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

All errors include constitutional compliance validation status.


## Monitoring

Service health and performance metrics:

- Health check endpoint: `/health`
- Metrics endpoint: `/metrics`
- Constitutional compliance status: `/compliance`
- Performance dashboard integration available
