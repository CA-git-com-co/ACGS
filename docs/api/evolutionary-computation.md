# Evolutionary Computation Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Evolutionary Computation Service (Port 8006)** API. This service provides WINA (Weight Informed Neuron Activation) optimization, genetic algorithms, and evolutionary policy optimization for the ACGS system, enabling the system to adapt and improve over time.

- **Service Name**: Evolutionary Computation Service
- **Port**: 8006
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Health and Metrics

- **GET /health**: Returns the health status of the service.
- **GET /metrics**: Provides Prometheus-compatible performance metrics.

### 2.2. WINA Optimization

#### POST /wina/optimize

Optimizes a model using the Weight Informed Neuron Activation (WINA) algorithm.

**Request Body**:

```json
{
  "model_id": "string",
  "optimization_parameters": {},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "optimization_id": "string",
  "status": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.3. Genetic Algorithms

#### POST /ga/run

Runs a genetic algorithm to solve an optimization problem.

**Request Body**:

```json
{
  "problem_definition": {},
  "ga_parameters": {},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "run_id": "string",
  "status": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.4. Policy Optimization

#### POST /policy/evolve

Evolves a policy using evolutionary algorithms.

**Request Body**:

```json
{
  "policy_id": "string",
  "evolution_parameters": {},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "evolution_id": "string",
  "status": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## 3. Performance Targets

- **Latency**: P99 ≤ 20ms for complex optimizations
- **Throughput**: ≥ 20 RPS sustained
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
- [Policy Governance Service API](policy-governance.md)