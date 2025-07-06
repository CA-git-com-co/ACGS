# Authentication API Documentation

## Service Overview

This service provides core functionality for the ACGS platform with constitutional compliance validation.

**Service**: Authentication
**Port**: 8XXX
**Constitutional Hash**: `cdd01ef066bc6cf2`


**Service**: Authentication Service
**Port**: 8016
**Base URL**: `http://localhost:8016/api/v1`
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This document provides comprehensive documentation for the Authentication Service (Port 8016) API, including endpoints for user authentication, token management, and profile retrieval.

### Base URL

`http://localhost:8001`

### Health Check

`GET /health`

### Metrics

`GET /metrics`

## Key Endpoints

### User Authentication

**Endpoint:** `POST /auth/login`

**Description:** User login and token issuance

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "token": "string",
  "expires_in": 3600,
  "user": {
    "id": "string",
    "username": "string",
    "roles": ["string"]
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Example Request:**
```javascript
const auth = await fetch('http://localhost:8001/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'user123',
    password: 'password123'
  })
});

const result = await auth.json();
console.log(result);
```

**Example Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "expires_in": 3600,
  "user": {
    "id": "1234567890",
    "username": "user123",
    "roles": ["user", "admin"]
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### Token Refresh

**Endpoint:** `POST /auth/refresh`

**Description:** Refresh a stale access token

**Request Body:**
```json
{
  "refresh_token": "string"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "access_token": "string",
  "expires_in": 3600,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Example Request:**
```javascript
const refresh = await fetch('http://localhost:8001/auth/refresh', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <refresh_token>'
  },
  body: JSON.stringify({
    refresh_token: 'refresh_token_here'
  })
});

const result = await refresh.json();
console.log(result);
```

**Example Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "expires_in": 3600,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

### User Logout

**Endpoint:** `POST /auth/logout`

**Description:** Invalidate existing access tokens

**Request Headers:**
```http
Authorization: Bearer <access_token>
```

**Response Status:**
`204 No Content`

### Get User Profile

**Endpoint:** `GET /auth/profile`

**Description:** Retrieve current user profile data

**Request Headers:**
```http
Authorization: Bearer <access_token>
```

**Response:**
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

**Example Request:**
```javascript
const profile = await fetch('http://localhost:8001/auth/profile', {
  headers: {
    'Authorization': 'Bearer <access_token>'
  }
});

const result = await profile.json();
console.log(result);
```

**Example Response:**
```json
{
  "id": "1234567890",
  "username": "user123",
  "email": "user@example.com",
  "roles": ["user", "admin"],
  "mfa_enabled": false,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## Additional Resources

- [API Documentation Index](index.md)
- [JWT Token Reference](#JWT Token Reference)
- [Role-based Access Control (RBAC) Design](#Role-based Access Control (RBAC) Design)

For detailed specifications and implementation guidelines, see the Auth Service documentation repository.
## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries (latency_p99: ≤5ms)
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
