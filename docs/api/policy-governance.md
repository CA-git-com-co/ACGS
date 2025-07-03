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
**Description:** Evaluate a policy against a set of governance rules

**Request Body:**
```json
{
  "policy_id": "string",
  "context": {
    "region": "string",
    "parameters": {
      "year": 2025,
      "budget": 1000000
    }
  }
}
```

**Response:**
```json
{
  "evaluation_results": {
    "compliance": true,
    "scores": {
      "transparency": 0.9,
      "fairness": 0.85
    },
    "details": {
      "public_comment_period": true,
      "minority_impact_analysis": false,
      "algorithmic_bias_check": true
    }
  }
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
    policy_id: 'POL123',
    context: {
      region: 'US',
      parameters: {
        year: 2025,
        budget: 1500000
      }
    }
  })
});

const evalResults = await evaluation.json();
console.log(evalResults);
```

**Example Response:**
```json
{
  "evaluation_results": {
    "compliance": true,
    "scores": {
      "transparency": 0.92,
      "public_participation": 0.78
    },
    "details": {
      "citizen_engagement": true,
      "stakeholder_feedback": "Positive feedback received",
      "impact_assessment_approval": true
    }
  }
}
```

### List Policies

**Endpoint:** `GET /api/v1/policies`
**Description:** Retrieve a list of current policies and their metadata

**Response:**
```json
[
  {
    "id": "POL001",
    "title": "Public Health Directive",
    "governance_area": "Healthcare",
    "status": "active",
    "compliance_score": 0.85
  },
  {
    "id": "POL002",
    "title": "Tax Policy",
    "governance_area": "Finance",
    "status": "inactive",
    "compliance_score": 0.7
  },
  {
    "id": "POL123",
    "title": "Education Reform",
    "governance_area": "Education",
    "status": "pending",
    "compliance_score": 0.95
  }
]
```

**Example Request:**
```javascript
const policies = await fetch('http://localhost:8005/api/v1/policies', {
  headers: {
    'Authorization': 'Bearer <jwt_token>'
  }
});

const policyList = await policies.json();
console.log(policyList);
```

**Example Response:**
```json
[
  {
    "id": "POL456",
    "title": "Energy Efficiency Act 2025",
    "governance_area": "Environmental",
    "status": "draft",
    "compliance_score": null
  }
]
```


## Additional Resources

* [API Documentation Index](index.md)
* [Policy Evaluation Framework](frameworks/governance-evaluation.md)
* [Governance Workflow Automation](workflows/governance.md)

For implementation guidelines, data schema references, and service configuration details, see the Policy Governance service documentation repository.