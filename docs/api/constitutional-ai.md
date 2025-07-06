# Constitutional AI API Documentation

## Service Overview

This service provides core functionality for the ACGS platform with constitutional compliance validation.

**Service**: Constitutional Ai
**Port**: 8XXX
**Constitutional Hash**: `cdd01ef066bc6cf2`


**Service**: Constitutional AI Service
**Port**: 8001
**Base URL**: `http://localhost:8001/api/v1`
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This document provides comprehensive documentation for the Constitutional AI Service (Port 8001) API, covering endpoints for constitutional compliance validation, principle evaluation, council operations, and more.

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
  "input_data": {,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
}
```

**Response:**
```json
{
  "constitutional_compliance": true,
  "compliance_rating": 0.9,
  "principles_evaluated": ["equality", "privacy"]
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Example Request:**
```javascript
const validation = await fetch('http://localhost:8001/api/v1/validate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <jwt_token>',
    'X-Constitutional-Hash': 'cdd01ef066bc6cf2'
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
  "principles_evaluated": ["equality", "fairness", "transparency"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Evaluate Constitutional Principles

**Endpoint:** `POST /api/v1/principles/evaluate`

**Description:** Evaluate constitutional principles against input criteria

**Request Body:**
```json
{
  "principles": ["equality", "privacy"],
  "input_data": {,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
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
    ,
  "constitutional_hash": "cdd01ef066bc6cf2"
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
    ,
  "constitutional_hash": "cdd01ef066bc6cf2"
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
- [Constitutional Compliance Checks RFC](#Constitutional Compliance Checks RFC)

For system configuration details, deployment guides, and architecture diagrams, see the Constitutional AI service documentation repository.
## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
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

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)
- [ACGS Implementation Guide](../deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [ACGS-PGP Operational Deployment Guide](../deployment/ACGS_PGP_OPERATIONAL_DEPLOYMENT_GUIDE.md)
- [ACGS-PGP Troubleshooting Guide](../deployment/ACGS_PGP_TROUBLESHOOTING_GUIDE.md)
- [ACGS-PGP Setup Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status Dashboard](../operations/SERVICE_STATUS.md)
- [ACGS Configuration Guide](../configuration/README.md)
- [ACGS-2 Technical Specifications - 2025 Edition](../TECHNICAL_SPECIFICATIONS_2025.md)
