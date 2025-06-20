# Authentication Service API Documentation

## Overview

Provides user authentication, authorization, and session management for the ACGS-1 system.

**Base URL**: `http://localhost:8000`
**Interactive Docs**: `http://localhost:8000/docs`
**Service Version**: 2.1.0
**Last Updated**: 2025-06-20

## Authentication

All endpoints (except `/health` and `/metrics`) require JWT authentication:

```http
Authorization: Bearer <jwt_token>
```

## Core Endpoints

### Health Check

#### GET /health

Returns the current health status of the Authentication Service.

**Authentication**: Not required

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "authentication_service",
  "version": "2.1.0",
  "uptime": 3600,
  "dependencies": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### User Login

#### POST /auth/login

Authenticate user and return JWT token.

**Authentication**: Not required

**Request Body**:
```json
{"username": "user", "password": "password"}
```

**Response (200 OK)**:
```json
{"access_token": "jwt_token", "token_type": "bearer", "expires_in": 3600}
```

### Token Refresh

#### POST /auth/refresh

Refresh an existing JWT token.

**Authentication**: Required

**Request Body**:
```json
{"refresh_token": "refresh_token"}
```

**Response (200 OK)**:
```json
{"access_token": "new_jwt_token", "expires_in": 3600}
```

### User Profile

#### GET /auth/profile

Get current user profile information.

**Authentication**: Required

**Response (200 OK)**:
```json
{"user_id": "123", "username": "user", "roles": ["citizen"], "permissions": ["read", "write"]}
```

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters"
  },
  "timestamp": "2025-06-20T22:30:45.548056Z",
  "request_id": "req_error_123"
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing authentication token"
  },
  "timestamp": "2025-06-20T22:30:45.548064Z",
  "request_id": "req_error_456"
}
```

## Rate Limits

- **Standard requests**: 100 requests per minute per user
- **Heavy operations**: 20 requests per minute per user

## Examples

### cURL Examples
```bash
# Health check
curl http://localhost:8000/health

# Example API call (replace with actual endpoint)
curl -X POST http://localhost:8000/api/v1/example \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"example": "data"}'
```

### Python Client Example
```python
import httpx
import asyncio

class AuthenticationServiceClient:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async def health_check(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            return response.json()

# Usage
async def main():
    client = AuthenticationServiceClient(token="your_jwt_token")
    result = await client.health_check()
    print(result)

asyncio.run(main())
```

## Monitoring

### Metrics Endpoint

#### GET /metrics

Returns Prometheus-formatted metrics for monitoring.

**Authentication**: Not required

---

**For additional support or questions, please refer to the [ACGS-1 Documentation](../README.md) or contact the development team.**
