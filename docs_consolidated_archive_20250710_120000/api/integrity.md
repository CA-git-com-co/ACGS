# Integrity Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Integrity Service (Port 8002)** API. This service is responsible for cryptographic verification, data integrity validation, and secure hash operations, ensuring the immutability and trustworthiness of data within the ACGS system.

- **Service Name**: Integrity Service
- **Port**: 8002
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Health and Metrics

- **GET /health**: Returns the health status of the service.
- **GET /metrics**: Provides Prometheus-compatible performance metrics.

### 2.2. Cryptographic Verification

#### POST /verify/signature

Verifies the cryptographic signature of a piece of data.

**Request Body**:

```json
{
  "data": "string",
  "signature": "string",
  "public_key": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "is_valid": boolean,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.3. Data Integrity

#### POST /data/validate

Validates the integrity of a piece of data using a checksum or hash.

**Request Body**:

```json
{
  "data": "string",
  "hash": "string",
  "algorithm": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "is_valid": boolean,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.4. Secure Hashing

#### POST /hash/generate

Generates a secure hash of a piece of data.

**Request Body**:

```json
{
  "data": "string",
  "algorithm": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "hash": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
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

- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
- [ACGS System Overview](../../SYSTEM_OVERVIEW.md)
- [Constitutional AI Service API](constitutional-ai.md)