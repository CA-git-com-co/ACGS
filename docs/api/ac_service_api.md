# Constitutional AI Service API Documentation

**Service:** Constitutional AI Service
**Port:** 8001
**Base URL:** `http://localhost:8001`
**Status:** ✅ Operational
**Last Updated:** 2025-06-20

// requires: Complete API documentation with examples and error handling
// ensures: Comprehensive API guidance for developers
// sha256: 7f718a49de960c98

## 🎯 Service Overview

Advanced constitutional compliance validation with formal verification and real-time monitoring. Provides sophisticated constitutional compliance algorithms, formal verification integration, and comprehensive audit logging.

## 📋 API Endpoints

### Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "ac_service",
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
  "timestamp": "2025-06-15T11:09:03.405677"
}
```

### Core Endpoints

#### GET /api/v1/status
Get detailed service status and capabilities.

**Response (200 OK):**
```json
{
  "api_version": "v1",
  "service": "ac_service_production",
  "status": "active",
  "phase": "Phase 3 - Production Implementation",
  "constitutional_rules_loaded": true,
  "compliance_engine_status": "operational",
  "endpoints": {
    "core": ["/", "/health", "/api/v1/status"],
    "validation": [
      "/api/v1/constitutional/validate",
      "/api/v1/constitutional/validate-advanced",
      "/api/v1/constitutional/validate-formal"
    ],
    "analysis": [
      "/api/v1/constitutional/analyze",
      "/api/v1/constitutional/impact-analysis",
      "/api/v1/constitutional/compliance-score"
    ]
  }
}
```

### Constitutional Validation

#### POST /api/v1/constitutional/validate
Enhanced constitutional compliance validation.

**Request:**
```json
{
  "policy": {
    "title": "Data Privacy Policy",
    "content": "Policy content here...",
    "category": "privacy"
  },
  "rules": ["CONST-001", "CONST-002", "CONST-003"],
  "validation_level": "comprehensive"
}
```

**Response (200 OK):**
```json
{
  "validation_id": "VAL-1234567890",
  "overall_compliance": true,
  "compliance_score": 0.92,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "rule_evaluations": [
    {
      "rule_id": "CONST-001",
      "title": "Democratic Participation",
      "compliant": true,
      "score": 0.95,
      "details": "Policy includes stakeholder consultation mechanisms"
    }
  ],
  "recommendations": [
    "Consider additional transparency measures",
    "Add more comprehensive audit trail"
  ]
}
```

#### GET /api/v1/constitutional/rules
Get constitutional rules for governance validation.

**Response (200 OK):**
```json
{
  "rules": [
    {
      "id": "CONST-001",
      "title": "Democratic Participation",
      "description": "All governance decisions must allow democratic participation",
      "category": "democratic_process",
      "priority": "high",
      "enforcement": "mandatory",
      "criteria": [
        "stakeholder_input_required",
        "voting_mechanism_present",
        "transparency_maintained"
      ]
    }
  ]
}
```

#### POST /api/v1/constitutional/analyze
Analyze constitutional impact of proposed policy changes.

**Request:**
```json
{
  "changes": [
    {
      "description": "Update privacy policy requirements",
      "type": "policy_modification",
      "scope": "data_protection"
    }
  ],
  "scope": "comprehensive"
}
```

**Response (200 OK):**
```json
{
  "analysis_id": "IMPACT-1234567890",
  "scope": "comprehensive",
  "changes_analyzed": 1,
  "constitutional_impacts": [
    {
      "change_id": "CHANGE-1",
      "description": "Update privacy policy requirements",
      "constitutional_domains_affected": ["democratic_process", "transparency"],
      "impact_severity": "medium",
      "compliance_risk": "low"
    }
  ],
  "risk_assessment": {
    "overall_risk": "low",
    "risk_factors": [],
    "mitigation_strategies": []
  }
}
```

### Collective Constitutional AI

#### POST /api/v1/ccai/conversations
Create a new Polis conversation for democratic deliberation.

#### POST /api/v1/ccai/bias-evaluation
Evaluate bias in constitutional principles.

#### Service-Specific Features
- Advanced constitutional compliance algorithms
- Formal verification integration with FV service
- Real-time constitutional violation detection
- Sophisticated compliance scoring and ranking
- Comprehensive audit logging and reporting
- Collective Constitutional AI (CCAI) methodology
- Democratic principle sourcing via Polis integration
- Multi-dimensional bias evaluation


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
    "timestamp": "2025-06-15T11:09:03.405679",
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

**API Version:** 3.0
**Documentation Status:** ✅ Current
**Interactive Docs:** `http://localhost:8001/docs`
