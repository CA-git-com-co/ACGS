# Authentication Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Authentication Service (Port 8016)** API. This service is responsible for user authentication, token management, and profile retrieval, ensuring all operations are compliant with the constitutional hash `cdd01ef066bc6cf2`.

- **Service Name**: Authentication Service
- **Port**: 8016
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Health and Metrics

- **GET /health**: Returns the health status of the service.
- **GET /metrics**: Provides Prometheus-compatible performance metrics.

### 2.2. User Authentication

#### POST /auth/login

Authenticates a user and returns a JWT token upon success.

**Request Body**:

```json
{
  "username": "string",
  "password": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "token": "string",
  "expires_in": 3600,
  "user": {
    "id": "string",
    "username": "string",
    "roles": ["string"]
  },
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### 2.3. Token Management

#### POST /auth/refresh

Refreshes an expired access token using a valid refresh token.

**Request Body**:

```json
{
  "refresh_token": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "access_token": "string",
  "expires_in": 3600,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### POST /auth/logout

Invalidates the user's current access token.

**Request Headers**:

- `Authorization`: `Bearer <access_token>`

**Response (204 No Content)**

### 2.4. User Profile

#### GET /auth/profile

Retrieves the profile of the currently authenticated user.

**Request Headers**:

- `Authorization`: `Bearer <access_token>`

**Response (200 OK)**:

```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "roles": ["string"],
  "mfa_enabled": boolean,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## 3. Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## 4. Error Handling

Standard HTTP status codes are used to indicate the success or failure of a request. All error responses include a constitutional compliance validation status.

- `400 Bad Request`: Invalid request parameters.
- `401 Unauthorized`: Authentication required or token is invalid.
- `403 Forbidden`: Insufficient permissions for the requested operation.
- `404 Not Found`: The requested resource does not exist.
- `500 Internal Server Error`: An unexpected server-side error occurred.

## 5. Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- **JWT Token Reference**: For detailed information on the structure and claims of the JWT tokens used in the ACGS platform, see the [JWT Token Reference](jwt.md).
- **Role-Based Access Control (RBAC)**: For information on the roles and permissions used to control access to resources, see the [RBAC Design](rbac.md).
- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
- [ACGS System Overview](../architecture/SYSTEM_OVERVIEW.md)

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation
