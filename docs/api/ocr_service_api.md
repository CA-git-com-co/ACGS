# OCR Service API Documentation

## Overview

Provides optical character recognition for document processing and analysis.

**Base URL**: `http://localhost:8020`
**Interactive Docs**: `http://localhost:8020/docs`
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

Returns the current health status of the OCR Service.

**Authentication**: Not required

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "ocr_service",
  "version": "2.1.0",
  "uptime": 3600,
  "dependencies": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### Extract Text

#### POST /api/v1/ocr/extract

Extract text from image or document.

**Authentication**: Required

**Request Body**:
```json
{"image_data": "base64_encoded_image", "format": "pdf"}
```

**Response (200 OK)**:
```json
{"extracted_text": "Document text content", "confidence": 0.95, "processing_time_ms": 1200}
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
  "timestamp": "2025-06-20T22:30:45.548424Z",
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
  "timestamp": "2025-06-20T22:30:45.548425Z",
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
curl http://localhost:8020/health

# Example API call (replace with actual endpoint)
curl -X POST http://localhost:8020/api/v1/example \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"example": "data"}'
```

### Python Client Example
```python
import httpx
import asyncio

class OCRServiceClient:
    def __init__(self, base_url="http://localhost:8020", token=None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async def health_check(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            return response.json()

# Usage
async def main():
    client = OCRServiceClient(token="your_jwt_token")
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
