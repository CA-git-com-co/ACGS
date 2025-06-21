# Governance Synthesis Service API Documentation

**Service:** Governance Synthesis Service
**Port:** 8004
**Base URL:** `http://localhost:8004`
**Status:** ✅ Operational
**Last Updated:** 2025-06-20

// requires: Complete API documentation with examples and error handling
// ensures: Comprehensive API guidance for developers
// sha256: 36631576d79cecc1

## 🎯 Service Overview

Enterprise-grade policy synthesis engine with four-tier risk strategy, multi-model consensus, and constitutional compliance validation. Provides AI-powered policy generation and synthesis capabilities with advanced orchestration and monitoring.

### Key Features

- **Multi-Model Consensus**: Ensemble of AI models for robust policy generation
- **Constitutional Compliance**: Real-time validation against constitutional principles
- **Policy Synthesis**: Advanced NLP for policy content generation and optimization
- **Performance Optimization**: Sub-500ms response times with caching and parallel processing

### Integration Points

- **Authentication Service**: JWT token validation and RBAC
- **Constitutional AI Service**: Constitutional principle validation and compliance scoring
- **Integrity Service**: Audit logging and policy versioning
- **Policy Governance Service**: Real-time policy enforcement integration

## 📋 API Endpoints

### Health Check

```http
GET /health
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "gs_service",
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
  "timestamp": "2025-06-15T11:09:03.406011"
}
```

### Core Endpoints

#### GET /api/v1/status

Get detailed service status and capabilities.

**Response (200 OK):**

```json
{
  "api_version": "v1",
  "service": "gs_service_production",
  "status": "active",
  "phase": "Phase 3 - Production Implementation",
  "endpoints": {
    "core": ["/", "/health", "/api/v1/status"],
    "phase_a3_synthesis": [
      "/api/v1/phase-a3/synthesize",
      "/api/v1/phase-a3/consensus",
      "/api/v1/phase-a3/strategies"
    ],
    "governance_workflows": [
      "/api/v1/governance/workflows",
      "/api/v1/governance/workflows/{workflow_id}",
      "/api/v1/governance/workflows/{workflow_id}/start"
    ],
    "synthesis": [
      "/api/v1/synthesize",
      "/api/v1/multi-model/synthesize",
      "/api/v1/enhanced/synthesize"
    ]
  },
  "capabilities": {
    "advanced_synthesis": true,
    "multi_model_consensus": true,
    "constitutional_compliance": true,
    "real_time_monitoring": true
  }
}
```

### Policy Synthesis Endpoints

#### POST /api/v1/synthesize

Core governance synthesis from constitutional principles.

**Request Body:**

```json
{
  "policy_id": 123,
  "principles": [
    {
      "title": "Democratic Participation",
      "description": "Ensure democratic participation in governance"
    }
  ],
  "synthesis_options": {
    "format": "rego",
    "validation_level": "comprehensive"
  }
}
```

**Response (200 OK):**

```json
{
  "policy": {
    "id": "pol_dp_2025_001",
    "title": "Data Privacy Protection Policy",
    "content": "Generated policy content...",
    "version": "1.0",
    "status": "draft"
  },
  "synthesis_metadata": {
    "models_used": ["qwen3-32b", "deepseek-chat", "qwen3-235b"],
    "consensus_score": 0.87,
    "constitutional_compliance": 0.94,
    "generation_time_ms": 1247
  },
  "validation_results": {
    "constitutional_score": 0.94,
    "stakeholder_alignment": 0.89,
    "policy_coherence": 0.92
  }
}
```

#### Multi-Model Consensus

```http
POST /api/v1/synthesis/consensus
```

**Description:** Run multi-model consensus validation on existing policy

**Request Body:**

```json
{
  "policy_content": "Policy text to validate...",
  "models": ["qwen3-32b", "deepseek-chat", "qwen3-235b"],
  "consensus_threshold": 0.8,
  "validation_criteria": ["constitutional_compliance", "stakeholder_alignment", "policy_coherence"]
}
```

**Response (200 OK):**

```json
{
  "consensus_result": {
    "overall_score": 0.87,
    "consensus_achieved": true,
    "model_scores": {
      "qwen3-32b": 0.89,
      "deepseek-chat": 0.85,
      "qwen3-235b": 0.87
    }
  },
  "validation_details": {
    "constitutional_compliance": 0.94,
    "stakeholder_alignment": 0.82,
    "policy_coherence": 0.85
  },
  "recommendations": ["Enhance stakeholder engagement section", "Clarify enforcement mechanisms"]
}
```

#### Policy Optimization

```http
POST /api/v1/synthesis/optimize
```

**Description:** Optimize existing policy for better constitutional compliance

**Request Body:**

```json
{
  "policy_id": "pol_dp_2025_001",
  "optimization_goals": [
    "constitutional_compliance",
    "stakeholder_satisfaction",
    "implementation_feasibility"
  ],
  "constraints": {
    "max_length": 5000,
    "preserve_core_principles": true
  }
}
```

### Advanced Features

#### POST /api/v1/multi-model/synthesize

Multi-model policy synthesis with consensus validation.

#### POST /api/v1/enhanced/synthesize

Enhanced governance synthesis with OPA integration.

#### POST /api/v1/phase-a3/synthesize

Phase A3 production policy synthesis with four-tier risk strategy.

#### POST /api/v1/alphaevolve/synthesize

AlphaEvolve integration for governance tuning.

#### POST /api/v1/mab/optimize

Multi-Armed Bandit optimization for synthesis strategies.

#### POST /api/v1/wina/synthesize

WINA-optimized Rego policy synthesis.

### Governance Workflows

#### GET /api/v1/governance/workflows

List all available governance workflows.

#### POST /api/v1/governance/workflows/{workflow_id}/start

Start a specific governance workflow.

#### GET /api/v1/governance/workflows/types

Get available workflow types.

### Configuration and Management

#### Service Status

```http
GET /api/v1/status
```

**Description:** Comprehensive service status and capabilities

**Response (200 OK):**

```json
{
  "api_version": "v1",
  "service": "gs_service_production",
  "status": "active",
  "phase": "Phase 3 - Production Implementation",
  "capabilities": {
    "advanced_synthesis": true,
    "multi_model_consensus": true,
    "constitutional_compliance": true,
    "real_time_monitoring": true
  },
  "performance_targets": {
    "response_time": "<2s for 95% operations",
    "accuracy": ">95%",
    "error_reduction": ">50%",
    "availability": ">99.9%"
  }
}
```

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
    "timestamp": "2025-06-15T11:09:03.406013",
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
**Interactive Docs:** `http://localhost:8004/docs`
