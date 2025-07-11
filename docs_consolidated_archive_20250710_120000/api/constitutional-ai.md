# Constitutional AI Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Constitutional AI Service (Port 8001)** API. This service is the core of the ACGS platform's governance model, responsible for validating actions against the system's constitution.

- **Service Name**: Constitutional AI Service
- **Port**: 8001
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Health and Metrics

- **GET /health/constitutional**: Returns the constitutional health status of the service.
- **GET /metrics**: Provides Prometheus-compatible performance metrics.

### 2.2. Constitutional Validation

#### POST /validate

Verifies the constitutional compliance of a given policy or action.

**Request Body**:

```json
{
  "policy_content": "string",
  "input_data": {},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "constitutional_compliance": boolean,
  "compliance_rating": float,
  "principles_evaluated": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.3. Principle Evaluation

#### POST /principles/evaluate

Evaluates a set of constitutional principles against the provided input data.

**Request Body**:

```json
{
  "principles": ["string"],
  "input_data": {},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "evaluation_results": [
    {
      "principle": "string",
      "score": float,
      "violations": ["string"]
    }
  ],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### GET /principles

Retrieves a list of all constitutional principles supported by the system.

**Response (200 OK)**:

```json
[
  "string"
]
```

### 2.4. Governance Council

#### GET /council/decisions

Retrieves a list of historical decisions made by the governance council.

**Response (200 OK)**:

```json
[
  {
    "decision_id": "string",
    "policy_id": "string",
    "outcome": "string",
    "rationale": "string",
    "council_members": ["string"]
  }
]
```

## 3. Performance Targets

- **P99 Latency**: <5ms
- **Throughput**: >100 RPS
- **Cache Hit Rate**: >85%
- **Availability**: 99.99%
- **Constitutional Compliance**: 97% (Verified, working towards 100%)

## 4. Error Handling

Standard HTTP status codes are used. All error responses include a constitutional compliance validation status.

- `400 Bad Request`: Invalid request parameters.
- `401 Unauthorized`: Authentication required.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource not found.
- `500 Internal Server Error`: Server error.

## 5. Related Information

- **Governance Synthesis Service**: For information on how governance policies are synthesized from constitutional principles, see the [Governance Synthesis Service API](governance_synthesis.md).
- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
- [ACGS System Overview](../../SYSTEM_OVERVIEW.md)
- [Constitutional Compliance Validation Framework](../constitutional_compliance_validation_framework.md)