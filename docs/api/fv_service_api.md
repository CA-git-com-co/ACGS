# Formal Verification Service API Documentation

**Service:** Formal Verification Service
**Port:** 8003
**Base URL:** `http://localhost:8003`
**Status:** ✅ Operational
**Last Updated:** 2025-06-20

// requires: Complete API documentation with examples and error handling
// ensures: Comprehensive API guidance for developers
// sha256: f31930c0870f47b3

## 🎯 Service Overview

Enterprise-grade formal verification with advanced algorithms, cryptographic validation, and blockchain audit trails. Provides Z3 SMT solver integration for mathematical proof generation and constitutional compliance verification.

## 📋 API Endpoints

### Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "fv_service",
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
  "timestamp": "2025-06-15T11:09:03.405905"
}
```

### Core Endpoints

#### GET /api/v1/enterprise/status
Get enterprise formal verification status and capabilities.

**Response (200 OK):**
```json
{
  "enterprise_verification_enabled": true,
  "advanced_features": {
    "mathematical_proof_algorithms": {
      "enabled": true,
      "algorithms": ["z3_smt", "datalog_reasoning", "temporal_logic"],
      "performance": "optimized"
    },
    "cryptographic_validation": {
      "enabled": true,
      "methods": ["digital_signatures", "hash_verification", "merkle_proofs"],
      "algorithms": ["RSA", "ECDSA", "SHA-256"]
    }
  }
}
```

### Verification Endpoints

#### POST /api/v1/validate
Validate content for security threats and constitutional compliance.

**Request:**
```json
{
  "content": "Policy content to validate",
  "policy_content": "Detailed policy text",
  "constitutional_principles": ["principle1", "principle2"],
  "validation_level": "comprehensive"
}
```

**Response (200 OK):**
```json
{
  "validation_id": "VAL-1234567890",
  "is_valid": true,
  "security_score": 0.95,
  "constitutional_compliance": true,
  "threat_analysis": {
    "threats_detected": 0,
    "security_level": "high",
    "risk_factors": []
  },
  "formal_verification": {
    "status": "verified",
    "mathematical_proof": "Z3 proof output",
    "verification_time_ms": 45
  }
}
```

#### POST /api/v1/verify/constitutional-compliance
Verify constitutional compliance with formal verification.

**Request:**
```json
{
  "content": "Policy content",
  "policy_content": "Detailed policy",
  "constitutional_principles": ["democratic_participation", "transparency"]
}
```

**Response (200 OK):**
```json
{
  "verification_status": "verified",
  "mathematical_proof": "Formal proof output",
  "compliance_score": 0.92,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "verification_details": {
    "z3_solver_result": "satisfiable",
    "proof_steps": ["step1", "step2", "step3"],
    "verification_time_ms": 120
  }
}
```

#### POST /api/v1/verify
Orchestrate formal verification of Datalog policy rules against AC principles.

**Request:**
```json
{
  "policy_rule_refs": [
    {
      "id": 1,
      "name": "voting_policy"
    }
  ],
  "verification_level": "comprehensive"
}
```

#### POST /api/v1/verify/tiered-verification
Phase 3 tiered formal verification with Automated, HITL, and Rigorous validation levels.

#### POST /api/v1/verify/generate-formal-proof
Generate formal mathematical proof for constitutional property verification.

**Request:**
```json
{
  "property_specification": "Property to prove",
  "policy_constraints": ["constraint1", "constraint2"],
  "proof_type": "constitutional_compliance"
}
```

### Performance & Monitoring

#### GET /api/v1/performance/metrics
Get performance metrics and optimization status.

**Response (200 OK):**
```json
{
  "performance_optimization_enabled": true,
  "current_metrics": {
    "average_response_time_ms": 45,
    "concurrent_verifications": 25,
    "cache_hit_ratio": 0.85,
    "throughput_per_hour": 1250
  },
  "optimization_features": {
    "parallel_processing": {
      "enabled": true,
      "max_concurrent_tasks": 100,
      "current_utilization": "25%"
    },
    "caching": {
      "enabled": true,
      "cache_size": "1GB",
      "hit_ratio": "85%"
    }
  }
}
```

#### GET /api/v1/validation/error-reports
Get comprehensive error handling and validation reports.

#### Service-Specific Features
- Z3 SMT solver integration for mathematical proofs
- Tiered validation pipeline (Automated, HITL, Rigorous)
- Parallel processing and caching optimization
- Cryptographic validation and digital signatures
- Blockchain audit trail verification
- Constitutional compliance integration
- Advanced security threat detection
- Performance optimization with load balancing


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
    "timestamp": "2025-06-15T11:09:03.405907",
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

**API Version:** 2.0
**Documentation Status:** ✅ Current
**Interactive Docs:** `http://localhost:8003/docs`
