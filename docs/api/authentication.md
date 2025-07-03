# Authentication API Documentation

## Overview

This document provides comprehensive documentation for the Authentication Service (Port 8016) API, including endpoints for user authentication, token management, and profile retrieval.

### Base URL

`http://localhost:8016`

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
  }
}
```

**Example Request:**
```javascript
const auth = await fetch('http://localhost:8016/auth/login', {
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
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi...c13Mtg",
  "expires_in": 3600,
  "user": {
    "id": "123",
    "username": "user123",
    "roles": ["user", "admin"]
  }
}
```

### Token Refresh

**Endpoint:** `POST /auth/refresh`
**Description:** Refresh a stale access token

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "expires_in": 3600
}
```

**Example Request:**
```javascript
const refresh = await fetch('http://localhost:8016/auth/refresh', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <refresh_token>'
  },
  body: JSON.stringify({
    refresh_token: 'refresh_token_here'
  })
});

const refreshResult = await refresh.json();
console.log(refreshResult);
```

**Example Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi...c13Mtg"
  "expires_in": 3600
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
  "mfa_enabled": boolean
}
```

**Example Request:**
```javascript
const profile = await fetch('http://localhost:8016/auth/profile', {
  headers: {
    'Authorization': 'Bearer <access_token>'
  }
});

const profileData = await profile.json();
console.log(profileData);
```

**Example Response:**
```json
{
  "id": "123",
  "username": "user123",
  "email": "user@example.com",
  "roles": ["user", "admin"],
  "mfa_enabled": false
}
```


## Additional Resources

* [API Documentation Index](index.md)
* [JWT Token Reference](jwt.md)
* [Role-based Access Control (RBAC) Design](rbac.md)

For detailed specifications and implementation guidelines, see the ACGS-2 API documentation repository.