# ACGS-2 API Guidelines

**Constitutional Hash:** `cdd01ef066bc6cf2`

## Overview

This document defines the API design guidelines for ACGS-2 services to ensure consistency, constitutional compliance, and optimal performance across all endpoints.

## API Design Principles

### Constitutional Compliance
- All API responses must include `constitutional_hash: cdd01ef066bc6cf2`
- Authentication endpoints must validate constitutional compliance
- Error responses must maintain constitutional hash validation

### Performance Requirements
- Target P99 latency <5ms for all endpoints
- Support >100 RPS throughput
- Implement proper caching strategies
- Use async/await for all I/O operations

## Standard Response Format

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-12T20:00:00Z",
  "service": "service-name"
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-12T20:00:00Z",
  "service": "service-name"
}
```

## Endpoint Standards

### Health Check Endpoint
All services must implement `/health`:
```json
GET /health
{
  "status": "healthy",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-12T20:00:00Z",
  "service": "service-name",
  "version": "1.0.0"
}
```

### Authentication Endpoints
```json
POST /auth/login
{
  "username": "string",
  "password": "string"
}

Response:
{
  "status": "success",
  "data": {
    "access_token": "jwt-token",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## Request/Response Guidelines

### Input Validation
- Validate all input parameters
- Use Pydantic models for request validation
- Include constitutional compliance in validation

### Rate Limiting
- Implement rate limiting for all public endpoints
- Use constitutional hash in rate limiting keys
- Provide clear rate limit headers

### Caching
- Implement appropriate caching strategies
- Include constitutional hash in cache keys
- Set appropriate TTL values

## Error Handling

### HTTP Status Codes
- 200: Success
- 400: Bad Request (validation errors)
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

### Error Response Details
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "username",
      "issue": "Required field missing"
    }
  },
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## Security Guidelines

### Authentication
- Use JWT tokens with constitutional hash validation
- Implement proper token expiration
- Include constitutional compliance in auth flows

### Authorization
- Implement role-based access control
- Validate constitutional compliance for all operations
- Log security events with constitutional hash

### Input Sanitization
- Sanitize all user inputs
- Validate against constitutional compliance requirements
- Prevent injection attacks

## Performance Optimization

### Async Operations
```python
@app.post("/api/v1/process")
async def process_data(request: ProcessRequest) -> ProcessResponse:
    """Process data with constitutional compliance."""
    try:
        # Async processing
        result = await process_async(request.data)
        
        return ProcessResponse(
            status="success",
            data=result,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
    except Exception as e:
        return ProcessResponse(
            status="error",
            error=str(e),
            constitutional_hash=CONSTITUTIONAL_HASH
        )
```

### Caching Strategy
- Use Redis for session and request caching
- Implement multi-tier caching (L1: memory, L2: Redis)
- Include constitutional hash in cache validation

## Documentation Requirements

### OpenAPI/Swagger
- All endpoints must be documented with OpenAPI specs
- Include constitutional compliance requirements
- Provide example requests and responses

### API Versioning
- Use URL path versioning: `/api/v1/endpoint`
- Maintain backward compatibility
- Include constitutional hash in all versions

## Testing Guidelines

### API Testing
- Test all endpoints for constitutional compliance
- Validate performance requirements
- Include integration tests for service interactions

### Example Test
```python
async def test_api_constitutional_compliance():
    """Test API maintains constitutional compliance."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
    assert "timestamp" in data
```

## Conclusion

Following these API guidelines ensures consistent, secure, and performant APIs across all ACGS-2 services while maintaining constitutional compliance with hash `cdd01ef066bc6cf2`.

---

**Document Maintained By:** ACGS-2 API Team  
**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Last Updated:** July 12, 2025
