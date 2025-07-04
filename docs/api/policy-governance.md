# Policy Governance API Documentation

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
  "input_data": {}
}
```

**Response:**
```json
{
  "evaluation_result": "approved",
  "compliance_score": 0.85,
  "reasons": ["string"]
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
  "reasons": ["Policy aligns with constitutional principles"]
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
}
```

**Response:**
```json
{
  "compliance_status": "compliant",
  "violations": []
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
  "violations": []
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
}
```

**Response:**
```json
{
  "workflow_id": "string",
  "status": "pending"
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
  "status": "pending"
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
}
```

**Response:**
```json
{
  "review_id": "string",
  "status": "submitted"
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
  "status": "submitted"
}
```

## Additional Resources

- [API Documentation Index](index.md)
- [Governance Workflow Design](workflow/design.md)
- [Council Review Process](council/process.md)

For system configuration details, deployment guides, and architecture diagrams, see the Policy Governance service documentation repository.