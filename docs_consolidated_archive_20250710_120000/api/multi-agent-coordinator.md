# Multi-Agent Coordinator Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Multi-Agent Coordinator Service (Port 8008)** API. This service orchestrates constitutional agent workflows.

- **Service Name**: Multi-Agent Coordinator Service
- **Port**: 8008
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Health and Status

- **GET /health**: Returns the health status of the service.
- **GET /**: Returns basic information about the service.
- **GET /api/v1/status**: Returns detailed status of the service.

### 2.2. Coordination Requests

- **GET /api/v1/requests**: Retrieves all coordination requests.
- **POST /api/v1/requests**: Creates a new coordination request.

### 2.3. Agent Assignments

- **GET /api/v1/assignments**: Retrieves all agent assignments.
- **POST /api/v1/assignments**: Creates a new agent assignment.

### 2.4. Performance and Validation

- **GET /api/v1/performance**: Retrieves performance metrics for the service.
- **POST /api/v1/coordinate**: Coordinates multiple agents for a complex task.
- **GET /constitutional/validate**: Validates the constitutional hash compliance.

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
