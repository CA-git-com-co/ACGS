# Formal Verification Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Formal Verification Service (Port 8003)** API. This service provides mathematical proof validation, logical consistency checking, and formal verification of policies and governance decisions within the ACGS system, utilizing a Z3 SMT solver for rigorous analysis.

- **Service Name**: Formal Verification Service
- **Port**: 8003
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Health and Metrics

- **GET /health**: Returns the health status of the service.
- **GET /metrics**: Provides Prometheus-compatible performance metrics.

### 2.2. Proof Validation

#### POST /proof/validate

Validates a mathematical proof using the Z3 SMT solver.

**Request Body**:

```json
{
  "proof_content": "string",
  "assumptions": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "is_valid": boolean,
  "errors": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.3. Consistency Checking

#### POST /consistency/check

Checks the logical consistency of a set of statements or a policy.

**Request Body**:

```json
{
  "statements": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "is_consistent": boolean,
  "conflicts": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.4. Policy Verification

#### POST /policy/verify

Formally verifies a policy against a set of properties or constraints.

**Request Body**:

```json
{
  "policy_content": "string",
  "properties": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "is_verified": boolean,
  "violations": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## 3. Performance Targets

- **Latency**: P99 ≤ 10ms for complex queries
- **Throughput**: ≥ 50 RPS sustained
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
- [Constitutional AI Service API](constitutional-ai.md)