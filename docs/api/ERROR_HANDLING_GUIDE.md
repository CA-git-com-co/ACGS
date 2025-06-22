# ACGS-1 Error Handling Guide

**Version:** 1.0  
**Date:** 2025-06-22  
**Status:** Implementation Complete

## Overview

This guide provides comprehensive documentation for the standardized error handling system implemented across all ACGS-1 microservices. The system ensures consistent error responses, proper HTTP status code usage, and actionable debugging information.

## 🎯 Standardized Error Response Format

### Error Response Structure

```json
{
  "success": false,
  "error": {
    "code": "SERVICE_CATEGORY_NUMBER",
    "message": "Human-readable error message",
    "details": {},
    "timestamp": "2025-06-22T10:30:00Z",
    "request_id": "uuid-here",
    "service": "service-name",
    "category": "ERROR_CATEGORY",
    "severity": "error|warning|critical|info",
    "retryable": boolean,
    "resolution_guidance": "How to fix this error"
  },
  "data": null,
  "metadata": {
    "timestamp": "2025-06-22T10:30:00Z",
    "request_id": "uuid-here",
    "version": "1.0.0",
    "service": "service-name"
  }
}
```

### Multiple Error Response Structure

```json
{
  "success": false,
  "errors": [
    {
      "code": "SERVICE_CATEGORY_001",
      "message": "First error message",
      "details": {},
      "timestamp": "2025-06-22T10:30:00Z",
      "request_id": "uuid-here",
      "service": "service-name",
      "category": "VALIDATION",
      "severity": "error",
      "retryable": false,
      "resolution_guidance": "Fix the validation error"
    }
  ],
  "data": null,
  "metadata": {
    "timestamp": "2025-06-22T10:30:00Z",
    "request_id": "uuid-here",
    "version": "1.0.0",
    "service": "service-name"
  }
}
```

## 📋 Error Code Catalog

### Hierarchical Error Code Format

Error codes follow the format: `{SERVICE}_{CATEGORY}_{NUMBER}`

**Services:**

- `AUTH`: Authentication Service
- `AC`: Constitutional AI Service
- `INTEGRITY`: Integrity Service
- `FV`: Formal Verification Service
- `GS`: Governance Synthesis Service
- `PGC`: Policy Governance Service
- `EC`: Evolutionary Computation Service
- `DGM`: Darwin Gödel Machine Service
- `SHARED`: Shared/Common Errors

**Categories:**

- `VALIDATION`: Input validation and data format errors
- `AUTHENTICATION`: Authentication and token-related errors
- `AUTHORIZATION`: Permission and access control errors
- `BUSINESS_LOGIC`: Domain-specific business rule violations
- `EXTERNAL_SERVICE`: External API and service integration errors
- `SYSTEM_ERROR`: Internal system and infrastructure errors

### Common Error Codes

#### Shared Errors

| Code                      | Message                         | HTTP Status | Description                              |
| ------------------------- | ------------------------------- | ----------- | ---------------------------------------- |
| `SHARED_VALIDATION_001`   | Invalid request format          | 400         | Request body or parameters are malformed |
| `SHARED_VALIDATION_002`   | Request validation failed       | 422         | One or more parameters failed validation |
| `SHARED_SYSTEM_ERROR_001` | Internal server error           | 500         | Unexpected error occurred                |
| `SHARED_SYSTEM_ERROR_002` | Service temporarily unavailable | 503         | Service unavailable due to maintenance   |

#### Authentication Service Errors

| Code                      | Message                    | HTTP Status | Description                           |
| ------------------------- | -------------------------- | ----------- | ------------------------------------- |
| `AUTH_VALIDATION_001`     | Invalid credentials format | 400         | Username or password format invalid   |
| `AUTH_AUTHENTICATION_001` | Invalid credentials        | 401         | Username or password incorrect        |
| `AUTH_AUTHENTICATION_002` | Account locked             | 401         | Account locked due to failed attempts |
| `AUTH_AUTHENTICATION_003` | Token expired              | 401         | Authentication token expired          |
| `AUTH_AUTHENTICATION_004` | Invalid token              | 401         | Authentication token malformed        |
| `AUTH_AUTHORIZATION_001`  | Insufficient permissions   | 403         | User lacks required permissions       |
| `AUTH_BUSINESS_LOGIC_001` | User already exists        | 409         | Username or email already taken       |

#### Constitutional AI Service Errors

| Code                    | Message                             | HTTP Status | Description                                    |
| ----------------------- | ----------------------------------- | ----------- | ---------------------------------------------- |
| `AC_VALIDATION_001`     | Invalid principle format            | 400         | Constitutional principle format invalid        |
| `AC_BUSINESS_LOGIC_001` | Principle conflict detected         | 409         | Principle conflicts with existing rules        |
| `AC_BUSINESS_LOGIC_002` | Constitutional compliance violation | 422         | Operation violates constitutional requirements |

#### Formal Verification Service Errors

| Code                      | Message                    | HTTP Status | Description                          |
| ------------------------- | -------------------------- | ----------- | ------------------------------------ |
| `FV_VALIDATION_001`       | Invalid verification query | 400         | Verification query malformed         |
| `FV_EXTERNAL_SERVICE_001` | Z3 solver timeout          | 408         | Z3 SMT solver timed out              |
| `FV_BUSINESS_LOGIC_001`   | Verification failed        | 422         | Property cannot be formally verified |

## 🔧 HTTP Status Code Mapping

### Standard HTTP Status Codes

| Status Code | Usage                 | Description                                  |
| ----------- | --------------------- | -------------------------------------------- |
| **400**     | Bad Request           | Client error in request format or parameters |
| **401**     | Unauthorized          | Authentication required or failed            |
| **403**     | Forbidden             | Authenticated but insufficient permissions   |
| **404**     | Not Found             | Requested resource does not exist            |
| **408**     | Request Timeout       | Request processing timeout                   |
| **409**     | Conflict              | Resource conflict (e.g., duplicate creation) |
| **422**     | Unprocessable Entity  | Valid format but business logic error        |
| **429**     | Too Many Requests     | Rate limiting exceeded                       |
| **500**     | Internal Server Error | Unexpected server error                      |
| **503**     | Service Unavailable   | Service temporarily unavailable              |

### Status Code Decision Matrix

| Error Category   | Default Status | Override Conditions                  |
| ---------------- | -------------- | ------------------------------------ |
| VALIDATION       | 400            | -                                    |
| AUTHENTICATION   | 401            | -                                    |
| AUTHORIZATION    | 403            | -                                    |
| BUSINESS_LOGIC   | 422            | 409 for conflicts, 404 for not found |
| EXTERNAL_SERVICE | 503            | 408 for timeouts                     |
| SYSTEM_ERROR     | 500            | 503 for service unavailable          |

## 🛠️ Implementation Guide

### Using Error Response Builder

```python
from services.shared.response.error_response import ErrorResponseBuilder

# Create builder for your service
builder = ErrorResponseBuilder("your-service-name", "1.0.0")

# Set request context for correlation
builder.set_request_context(request)

# Create error response from catalog
error_response = builder.from_error_code(
    "AUTH_AUTHENTICATION_002",
    details={"username": "user123", "attempt_count": 3},
    context={"ip_address": "192.168.1.1"}
)

# Return as JSON response
return ErrorJSONResponse(error_response)
```

### Validation Error Example

```python
# Handle validation errors
validation_errors = [
    {"field": "username", "message": "Required field missing", "type": "missing"},
    {"field": "password", "message": "Too short", "type": "value_error"}
]

error_response = builder.validation_error(
    validation_errors=validation_errors,
    message="Request validation failed"
)

return ErrorJSONResponse(error_response, status_code=422)
```

### Using Error Middleware

```python
from fastapi import FastAPI
from services.shared.middleware.error_middleware import ErrorHandlingMiddleware

app = FastAPI()

# Add error handling middleware
app.add_middleware(
    ErrorHandlingMiddleware,
    service_name="your-service-name",
    service_version="1.0.0",
    debug_mode=False
)
```

## 🔍 Troubleshooting Guide

### Common Error Scenarios

#### 1. Authentication Failures

**Symptoms:**

- HTTP 401 responses
- Error codes starting with `AUTH_AUTHENTICATION_`

**Troubleshooting Steps:**

1. Check if token is present in request headers or cookies
2. Verify token format and expiration
3. Confirm user account is active and not locked
4. Check authentication service logs for details

**Resolution:**

- Refresh expired tokens
- Unlock locked accounts
- Verify credentials are correct

#### 2. Validation Errors

**Symptoms:**

- HTTP 400 or 422 responses
- Error codes with `VALIDATION` category
- Multiple validation errors in response

**Troubleshooting Steps:**

1. Review request payload format
2. Check required fields are present
3. Validate data types and formats
4. Confirm field constraints are met

**Resolution:**

- Fix request format according to API documentation
- Provide all required fields
- Ensure data meets validation rules

#### 3. Service Unavailable Errors

**Symptoms:**

- HTTP 503 responses
- Error codes with `EXTERNAL_SERVICE` or `SYSTEM_ERROR` categories
- Retryable errors

**Troubleshooting Steps:**

1. Check service health endpoints
2. Verify external service connectivity
3. Review service logs for errors
4. Check circuit breaker status

**Resolution:**

- Wait for service recovery
- Retry request after delay
- Contact system administrator if persistent

#### 4. Permission Denied Errors

**Symptoms:**

- HTTP 403 responses
- Error codes with `AUTHORIZATION` category

**Troubleshooting Steps:**

1. Verify user has required role/permissions
2. Check resource ownership
3. Confirm operation is allowed for user type
4. Review authorization policies

**Resolution:**

- Request appropriate permissions
- Contact administrator for role assignment
- Use authorized account

### Error Monitoring and Alerting

#### Key Metrics to Monitor

1. **Error Rate by Service**

   - Track 4xx and 5xx error rates
   - Alert on error rate spikes

2. **Error Distribution by Category**

   - Monitor validation vs system errors
   - Track authentication failure patterns

3. **Response Time for Errors**

   - Ensure error responses are fast
   - Monitor error handling performance

4. **Circuit Breaker Status**
   - Track circuit breaker state changes
   - Alert on service degradation

#### Log Analysis

Error logs include structured context:

```json
{
  "timestamp": "2025-06-22T10:30:00Z",
  "service": "authentication-service",
  "request_id": "uuid-here",
  "method": "POST",
  "url": "/auth/login",
  "client_ip": "192.168.1.1",
  "exception_type": "HTTPException",
  "status_code": 401,
  "error_code": "AUTH_AUTHENTICATION_002"
}
```

## 📈 Best Practices

### For Developers

1. **Always use error catalog codes** instead of creating ad-hoc errors
2. **Provide actionable error messages** that help users resolve issues
3. **Include relevant context** in error details for debugging
4. **Use appropriate HTTP status codes** based on error category
5. **Log errors with structured context** for monitoring and debugging

### For Operations

1. **Monitor error rates and patterns** to identify system issues
2. **Set up alerts for critical errors** and service degradation
3. **Use request IDs for correlation** across distributed services
4. **Implement proper retry logic** for retryable errors
5. **Maintain error documentation** and troubleshooting guides

### Anti-Patterns to Avoid

❌ **Don't expose sensitive information** in error messages  
❌ **Don't use generic error messages** without context  
❌ **Don't ignore error correlation** across services  
❌ **Don't skip error logging** for debugging  
❌ **Don't use inconsistent status codes** across endpoints

## 🚀 Migration Guide

### Updating Existing Services

1. **Install shared error handling modules**
2. **Add error handling middleware** to FastAPI app
3. **Replace existing error responses** with standardized format
4. **Update error codes** to use catalog format
5. **Test error scenarios** to ensure consistency

### Backward Compatibility

During migration, services can support both old and new error formats:

- Use `X-Accept-Error-Format` header to determine response format
- Gradually migrate clients to new format
- Remove legacy format support after migration complete

---

**Next Steps:**

- ✅ Error Handling Standardization: **COMPLETE**
- 🔄 OpenAPI Documentation Generation: **NEXT**
- 🔄 API Versioning Strategy Implementation: **PENDING**
