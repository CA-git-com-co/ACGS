# Integrity Service API Documentation

**Service:** Integrity Service  
**Port:** 8002  
**Base URL:** `http://localhost:8002`  
**Status:** ✅ Operational  
**Last Updated:** 2025-06-15

// requires: Complete API documentation with examples and error handling
// ensures: Comprehensive API guidance for developers
// sha256: fa9deea8686f4a25

## 🎯 Service Overview

Provides cryptographic integrity, audit trails, and data verification.

## 📋 API Endpoints

### Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "integrity_service",
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
  "timestamp": "2025-06-15T11:09:03.405792"
}
```

### Service-Specific Endpoints


#### Main Endpoints
- `GET /api/v1/status` - Service status and capabilities
- `POST /api/v1/process` - Main processing endpoint
- `GET /api/v1/metrics` - Performance metrics

#### Service-Specific Features
- Constitutional governance integration
- Real-time processing capabilities
- Enterprise security compliance


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
    "timestamp": "2025-06-15T11:09:03.405793",
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
**Interactive Docs:** `http://localhost:8002/docs`
