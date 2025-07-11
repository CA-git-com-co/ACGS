# API Gateway Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **API Gateway Service (Port 8010)** API. This service provides production routing with constitutional middleware.

- **Service Name**: API Gateway Service
- **Port**: 8010
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Gateway Health and Configuration

- **GET /gateway/health**: Returns the health status of the gateway.
- **GET /gateway/health/detailed**: Returns a detailed health status of the gateway and its components.
- **GET /gateway/config**: Returns the gateway configuration.
- **GET /gateway/metrics**: Returns gateway metrics.

### 2.2. Authentication

- **POST /auth/login**: Authenticates a user and returns an access token.
- **POST /auth/logout**: Logs out a user by invalidating their token.
- **GET /auth/me**: Retrieves the current user's information.
- **POST /auth/validate**: Validates a token.
- **GET /auth/health**: Returns the health status of the authentication module.

### 2.3. Administration

- **POST /auth/admin/users**: Creates a new user (admin only).
- **POST /gateway/admin/reload-policies**: Reloads security policies (admin only).
- **POST /gateway/admin/refresh-services**: Refreshes the service registry (admin only).

### 2.4. Service Proxy

- **ANY /api/{service_name:path}**: Proxies requests to the appropriate backend service.

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
