# Policy Governance Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Policy Governance Service (Port 8005)** API. This service is responsible for policy evaluation, compliance validation, and governance workflows within the ACGS system.

- **Service Name**: Policy Governance Service
- **Port**: 8005
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Health and Metrics

- **GET /health**: Returns the health status of the service.
- **GET /metrics**: Provides Prometheus-compatible performance metrics.

### 2.2. Policy Evaluation

#### POST /policies/evaluate

Evaluates a policy against predefined governance criteria.

**Request Body**:

```json
{
  "policy_id": "string",
  "input_data": {},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "evaluation_result": "string",
  "compliance_score": float,
  "reasons": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.3. Compliance Validation

#### POST /compliance/validate

Validates a policy's compliance with constitutional standards and other regulatory frameworks.

**Request Body**:

```json
{
  "policy_id": "string",
  "compliance_checks": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "compliance_status": "string",
  "violations": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.4. Governance Workflow

#### POST /governance/workflow

Initiates a predefined governance workflow for a specific policy.

**Request Body**:

```json
{
  "policy_id": "string",
  "workflow_steps": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (201 Created)**:

```json
{
  "workflow_id": "string",
  "status": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.5. Council Review

#### POST /council/review

Submits a policy for review by the governance council.

**Request Body**:

```json
{
  "policy_id": "string",
  "council_members": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (201 Created)**:

```json
{
  "review_id": "string",
  "status": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## 3. Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## 4. Error Handling

Standard HTTP status codes are used. All error responses include a constitutional compliance validation status.

- `400 Bad Request`: Invalid request parameters.
- `401 Unauthorized`: Authentication required.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource not found.
- `500 Internal Server Error`: Server error.

## 5. Related Information

- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
- [ACGS System Overview](../../SYSTEM_OVERVIEW.md)
## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation
