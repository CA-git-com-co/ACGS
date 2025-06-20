# Constitutional AI Service API Documentation

## Overview

The Constitutional AI Service provides advanced constitutional analysis, policy validation, and compliance checking capabilities for the ACGS-1 system. It uses state-of-the-art AI models to ensure all policies and decisions align with constitutional principles.

**Base URL**: `http://localhost:8001`
**Interactive Docs**: `http://localhost:8001/docs`
**Service Version**: 2.1.0
**Last Updated**: 2024-06-20

## Authentication

All endpoints (except `/health` and `/metrics`) require JWT authentication:

```http
Authorization: Bearer <jwt_token>
```

## Core Endpoints

### Health Check

#### GET /health

Returns the current health status of the Constitutional AI Service.

**Authentication**: Not required

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "constitutional-ai",
  "version": "2.1.0",
  "uptime": 3600,
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "ai_model": "loaded"
  },
  "model_info": {
    "name": "constitutional-ai-v2.1",
    "status": "ready",
    "last_updated": "2024-06-20T10:00:00Z"
  }
}
```

### Constitutional Analysis

#### POST /api/v1/analyze

Performs comprehensive constitutional analysis on provided text or policy content.

**Authentication**: Required

**Request Body**:
```json
{
  "text": "Policy or document text to analyze",
  "principles": ["transparency", "fairness", "accountability"],
  "analysis_type": "comprehensive",
  "context": {
    "document_type": "policy",
    "stakeholders": ["citizens", "government"],
    "jurisdiction": "federal"
  }
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "analysis_id": "analysis_123456",
    "overall_score": 0.85,
    "principle_scores": {
      "transparency": 0.90,
      "fairness": 0.80,
      "accountability": 0.85
    },
    "detailed_analysis": {
      "strengths": [
        "Clear language and accessible terminology",
        "Well-defined accountability mechanisms"
      ],
      "concerns": [
        "Limited transparency in decision-making process"
      ],
      "recommendations": [
        "Add public consultation requirements",
        "Include appeal process details"
      ]
    },
    "compliance_status": "compliant_with_recommendations",
    "confidence_score": 0.92
  },
  "timestamp": "2024-06-20T10:30:00Z",
  "request_id": "req_123456"
}
```

### Policy Validation

#### POST /api/v1/validate

Validates a policy against constitutional principles and legal requirements.

**Authentication**: Required

**Request Body**:
```json
{
  "policy": {
    "title": "Data Privacy Protection Policy",
    "content": "Policy content text...",
    "category": "privacy",
    "scope": "national"
  },
  "validation_rules": ["constitutional_compliance", "legal_consistency", "stakeholder_impact"],
  "strict_mode": true
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "validation_id": "val_789012",
    "is_valid": true,
    "validation_score": 0.88,
    "rule_results": {
      "constitutional_compliance": {
        "passed": true,
        "score": 0.90,
        "details": "Policy aligns with constitutional privacy rights"
      },
      "legal_consistency": {
        "passed": true,
        "score": 0.85,
        "details": "Consistent with existing privacy legislation"
      },
      "stakeholder_impact": {
        "passed": true,
        "score": 0.89,
        "details": "Positive impact on citizen privacy rights"
      }
    },
    "issues": [],
    "recommendations": [
      "Consider adding enforcement mechanisms",
      "Clarify data retention policies"
    ]
  },
  "timestamp": "2024-06-20T10:30:00Z",
  "request_id": "req_789012"
}
```

### Constitutional Principles

#### GET /api/v1/principles

Retrieves the list of constitutional principles used for analysis.

**Authentication**: Required

**Query Parameters**:
- `category` (optional): Filter by principle category
- `active_only` (optional): Return only active principles (default: true)

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "principles": [
      {
        "id": "transparency",
        "name": "Transparency",
        "description": "Openness and accessibility in governance processes",
        "category": "governance",
        "weight": 0.9,
        "active": true,
        "criteria": [
          "Public access to information",
          "Clear decision-making processes",
          "Accessible language and format"
        ]
      },
      {
        "id": "fairness",
        "name": "Fairness",
        "description": "Equal treatment and non-discrimination",
        "category": "rights",
        "weight": 0.95,
        "active": true,
        "criteria": [
          "Equal application of rules",
          "Non-discriminatory practices",
          "Proportionate responses"
        ]
      }
    ],
    "total_count": 12,
    "active_count": 10
  },
  "timestamp": "2024-06-20T10:30:00Z",
  "request_id": "req_345678"
}
```

### Compliance Check

#### POST /api/v1/compliance-check

Performs a quick compliance check against specific constitutional requirements.

**Authentication**: Required

**Request Body**:
```json
{
  "content": "Content to check for compliance",
  "requirements": [
    "due_process",
    "equal_protection",
    "freedom_of_speech"
  ],
  "check_type": "quick"
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "check_id": "check_456789",
    "overall_compliance": true,
    "compliance_score": 0.87,
    "requirement_results": {
      "due_process": {
        "compliant": true,
        "score": 0.90,
        "evidence": ["Clear procedural steps outlined", "Appeal process defined"]
      },
      "equal_protection": {
        "compliant": true,
        "score": 0.85,
        "evidence": ["Non-discriminatory language used", "Equal access provisions"]
      },
      "freedom_of_speech": {
        "compliant": true,
        "score": 0.86,
        "evidence": ["No speech restrictions imposed", "Expression rights protected"]
      }
    },
    "warnings": [],
    "processing_time_ms": 1250
  },
  "timestamp": "2024-06-20T10:30:00Z",
  "request_id": "req_456789"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "text",
      "issue": "Text content is required"
    }
  },
  "timestamp": "2024-06-20T10:30:00Z",
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
  "timestamp": "2024-06-20T10:30:00Z",
  "request_id": "req_error_456"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An internal server error occurred",
    "details": "AI model temporarily unavailable"
  },
  "timestamp": "2024-06-20T10:30:00Z",
  "request_id": "req_error_789"
}
```

## Rate Limits

- **Standard requests**: 100 requests per minute per user
- **Analysis requests**: 20 requests per minute per user
- **Bulk operations**: 5 requests per minute per user

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Examples

### Python Client Example
```python
import httpx
import asyncio

class ConstitutionalAIClient:
    def __init__(self, base_url="http://localhost:8001", token=None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async def analyze_text(self, text, principles=None):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/analyze",
                json={
                    "text": text,
                    "principles": principles or ["transparency", "fairness"],
                    "analysis_type": "comprehensive"
                },
                headers=self.headers
            )
            return response.json()
    
    async def validate_policy(self, policy_content):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/validate",
                json={
                    "policy": {"content": policy_content},
                    "validation_rules": ["constitutional_compliance"]
                },
                headers=self.headers
            )
            return response.json()

# Usage
async def main():
    client = ConstitutionalAIClient(token="your_jwt_token")
    result = await client.analyze_text("Policy text to analyze")
    print(result)

asyncio.run(main())
```

### cURL Examples
```bash
# Health check
curl http://localhost:8001/health

# Analyze constitutional compliance
curl -X POST http://localhost:8001/api/v1/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This policy ensures transparent decision-making processes",
    "principles": ["transparency", "accountability"],
    "analysis_type": "comprehensive"
  }'

# Get constitutional principles
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8001/api/v1/principles

# Quick compliance check
curl -X POST http://localhost:8001/api/v1/compliance-check \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Policy content to check",
    "requirements": ["due_process", "equal_protection"],
    "check_type": "quick"
  }'
```

## Monitoring

### Metrics Endpoint

#### GET /metrics

Returns Prometheus-formatted metrics for monitoring.

**Authentication**: Not required

Key metrics include:
- `constitutional_ai_requests_total`: Total number of requests
- `constitutional_ai_analysis_duration_seconds`: Analysis processing time
- `constitutional_ai_model_health`: AI model health status
- `constitutional_ai_compliance_scores`: Distribution of compliance scores

---

**For additional support or questions, please refer to the [ACGS-1 Documentation](../README.md) or contact the development team.**
