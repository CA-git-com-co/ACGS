# Constitutional AI API Documentation

## Overview

This document provides comprehensive documentation for the Constitutional AI Service (Port 8001) API, covering endpoints for constitutional compliance validation, principle evaluation, council operations, and more.

### Base URL

`http://localhost:8001`

### Health Check

`GET /health`

### Metrics

`GET /metrics`

## Key Endpoints

### Validate Constitutional Compliance

**Endpoint:** `POST /api/v1/validate`

**Description:** Verify constitutional compliance of a policy

**Request Body:**
```json
{
  "policy_content": "string",
  "input_data": {}
}
```

**Response:**
```json
{
  "constitutional_compliance": true,
  "compliance_rating": 0.9,
  "principles_evaluated": ["equality", "privacy"]
}
```

**Example Request:**
```javascript
const validation = await fetch('http://localhost:8001/api/v1/validate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <jwt_token>'
  },
  body: JSON.stringify({
    policy_content: 'Sample policy text.',
    input_data: { context: 'government' }
  })
});

const result = await validation.json();
console.log(result);
```

**Example Response:**
```json
{
  "constitutional_compliance": true,
  "compliance_rating": 0.95,
  "principles_evaluated": ["equality", "fairness", "transparency"]
}
```

### Evaluate Constitutional Principles

**Endpoint:** `POST /api/v1/principles/evaluate`

**Description:** Evaluate constitutional principles against input criteria

**Request Body:**
```json
{
  "principles": ["equality", "privacy"],
  "input_data": {}
}
```

**Response:**
```json
{
  "evaluation_results": [
    {
      "principle": "equality",
      "score": 0.85,
      "violations": []
    },
    {
      "principle": "privacy",
      "score": 0.9,
      "violations": ["data_leakage"]
    }
  ]
}
```

**Example Request:**
```javascript
const evaluation = await fetch('http://localhost:8001/api/v1/principles/evaluate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <jwt_token>'
  },
  body: JSON.stringify({
    principles: ["equality", "privacy"],
    input_data: { region: "US", parameters: { age: 25, budget: 1000000 } }
  })
});

const result = await evaluation.json();
console.log(result);
```

**Example Response:**
```json
{
  "evaluation_results": [
    {
      "principle": "equality",
      "score": 0.85,
      "violations": []
    },
    {
      "principle": "privacy",
      "score": 0.9,
      "violations": ["data_leakage"]
    }
  ]
}
```

### List Constitutional Principles

**Endpoint:** `GET /api/v1/principles`

**Description:** Retrieve a list of constitutional principles considered by the system

**Response:**
```json
[
  "equality",
  "privacy",
  "transparency",
  "fairness"
]
```

**Example Request:**
```javascript
const principles = await fetch('http://localhost:8001/api/v1/principles', {
  headers: {
    'Authorization': 'Bearer <jwt_token>'
  }
});

const result = await principles.json();
console.log(result);
```

**Example Response:**
```json
[
  "equality",
  "privacy",
  "transparency",
  "fairness"
]
```

### Get Council Decisions

**Endpoint:** `GET /api/v1/council/decisions`

**Description:** Retrieve a list of council decisions

**Response:**
```json
[
  {
    "decision_id": "string",
    "policy_id": "string",
    "outcome": "approved",
    "rationale": "string",
    "council_members": ["string"]
  }
]
```

**Example Request:**
```javascript
const decisions = await fetch('http://localhost:8001/api/v1/council/decisions', {
  headers: {
    'Authorization': 'Bearer <jwt_token>'
  }
});

const result = await decisions.json();
console.log(result);
```

**Example Response:**
```json
[
  {
    "decision_id": "DEC001",
    "policy_id": "POL001",
    "outcome": "approved",
    "rationale": "The policy aligns with constitutional principles of equality and privacy.",
    "council_members": ["member1", "member2"]
  }
]
```

## Additional Resources

- [API Documentation Index](index.md)
- [Principle Evaluation Model Paper](models/principle-eval.pdf)
- [Constitutional Compliance Checks RFC](rfcs/compliance-checks.md)

For system configuration details, deployment guides, and architecture diagrams, see the Constitutional AI service documentation repository.