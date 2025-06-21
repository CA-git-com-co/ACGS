# Auth Service API Documentation

**Service:** Auth Service  
**Port:** 8000  
**Base URL:** `http://localhost:8000`  
**Status:** ✅ Operational  
**Last Updated:** 2025-06-15

// requires: Complete API documentation with examples and error handling
// ensures: Comprehensive API guidance for developers
// sha256: 6b5bf93b70f8ba26

## 🎯 Service Overview

Handles authentication, authorization, and user management with JWT tokens and RBAC.

## 📋 API Endpoints

### Health Check

```http
GET /health
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "auth_service",
  "version": "2.1.0",
  "uptime": "1234567",
  "dependencies": {
    "database": "connected",
    "redis": "connected"
  }
}
```

**Error Response (503 Service Unavailable):**

```json
{
  "status": "unhealthy",
  "error": "Database connection failed",
  "timestamp": "2025-06-15T11:09:03.405528"
}
```

### Authentication Endpoints

#### POST /auth/register

Register a new user account.

**Request:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string (optional)",
  "last_name": "string (optional)"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "is_active": true,
  "is_superuser": false
}
```

#### POST /auth/token (Login)

Authenticate user and receive JWT tokens.

**Request:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "refresh_token": null
}
```

#### POST /auth/token/refresh

Refresh JWT access token using refresh token cookie.

**Response (200 OK):**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "refresh_token": null
}
```

#### POST /auth/logout

Logout user and revoke tokens.

**Response (200 OK):**

```json
{
  "message": "Logout successful"
}
```

#### GET /auth/me

Get current user profile (requires authentication).

**Response (200 OK):**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "is_active": true,
  "is_superuser": false
}
```

#### Service-Specific Features

- JWT token authentication with refresh tokens
- HttpOnly cookie-based token storage
- CSRF protection
- Role-based access control (RBAC)
- Multi-factor authentication (MFA) support
- OAuth 2.0 and OpenID Connect integration
- API key management

## 🔧 Error Handling

### Standard Error Codes

- **400 Bad Request:** Invalid input parameters
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **429 Too Many Requests:** Rate limit exceeded
- **500 Internal Server Error:** Server error
- **503 Service Unavailable:** Service temporarily unavailable

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "policy_content",
      "reason": "Content cannot be empty"
    },
    "timestamp": "2025-06-15T11:09:03.405530",
    "request_id": "req_123456789"
  }
}
```

## 📊 Performance Metrics

- **Average Response Time:** <500ms
- **Rate Limit:** 1000 requests/hour
- **Timeout:** 30 seconds
- **Availability:** >99.5%

## 🔐 Authentication

### JWT Token Authentication

```http
Authorization: Bearer <jwt_token>
```

### API Key Authentication (Optional)

```http
X-API-Key: <api_key>
```

---

**API Version:** 2.1  
**Documentation Status:** ✅ Current  
**Interactive Docs:** `http://localhost:8000/docs`
