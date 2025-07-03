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

const validateResult = await validation.json();
console.log(validateResult);
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
**Description:** Evaluate specific constitutional principles against input criteria

**Request Body:**
```json
{
  "principles": ["equality", "free_speech"],
  "input_data": {
    "context": "education",
    "parameters": { "age": 25, "region": "US" }
  }
}
```

**Response:**
```json
{
  "principle_results": [
    {
      "principle": "equality",
      "compliance": true,
      "metrics": {
        "discrimination_score": 0.05,
        "accessibility": 0.9
      }
    },
    {
      "principle": "free_speech",
      "compliance": false,
      "violation_type": "censorship",
      "details": {
        "censored_terms": ["democracy"],
        "affected_groups": ["journalists"]
      }
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
    principles: ["equality", "fairness"],
    input_data: {
      context: "government",
      parameters: { region: "US", policy_id: "POL123" }
    }
  })
});

const evalResults = await evaluation.json();
console.log(evalResults);
```

**Example Response:**
```json
{
  "principle_results": [
    {
      "principle": "equality",
      "compliance": true,
      "metrics": {
        "discrimination_index": 0.05,
        "representation": 0.8
      }
    },
    {
      "principle": "fairness",
      "compliance": false,
      "violation_type": "bias",
      "details": {
        "bias_factors": ["income", "race"],
        "severity": "medium"
      }
    }
  ]
}
```

### List Constitutional Principles

**Endpoint:** `GET /api/v1/principles`
**Description:** Retrieve a list of constitutional principles considered by the ACGS-2 system

**Response:**
```json
{
  "principles": [
    "equality",
    "fairness",
    "transparency",
    "privacy",
    "due_process"
  ]
}
```

**Example Request:**
```javascript
const principles = await fetch('http://localhost:8001/api/v1/principles', {
  headers: {
    'Authorization': 'Bearer <jwt_token>'
  }
});

const principleList = await principles.json();
console.log(principleList);
```

**Example Response:**
```json
{
  "principles": [
    "equality",
    "fairness",
    "transparency",
    "privacy",
    "due_process"
  ]
}
```


## Additional Resources

* [API Documentation Index](index.md)
* [Principle Evaluation Model Paper](models/principle-eval.pdf)
* [Constitutional Compliance Checks RFC](rfcs/compliance-checks.md)

For system configuration details, deployment guides, and architecture diagrams, see the Constitutional AI service documentation repository.