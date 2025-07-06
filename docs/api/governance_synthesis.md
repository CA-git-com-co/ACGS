# Governance Synthesis API Documentation

## Service Overview

This service provides core functionality for the ACGS platform with constitutional compliance validation.

**Service**: Governance_Synthesis
**Port**: 8XXX
**Constitutional Hash**: `cdd01ef066bc6cf2`


<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

**Service**: Governance Synthesis Service
**Port**: 8004
**Base URL**: `http://localhost:8004/api/v1`
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Version**: 3.0.0

## Overview

The Governance Synthesis Service is a core component of the ACGS system, responsible for synthesizing governance policies from constitutional principles using advanced AI model integration. It employs a multi-model LLM consensus mechanism with Google Gemini, DeepSeek-R1, NVIDIA Qwen, and Nano-vLLM to ensure robust and reliable policy generation.

### Key Features

- **Multi-Model AI Integration**: Google Gemini, DeepSeek-R1, NVIDIA Qwen, Nano-vLLM
- **Constitutional Policy Generation**: Synthesis from constitutional principles
- **Multi-Stakeholder Coordination**: Stakeholder interest representation
- **Democratic Process Management**: Voting and deliberation tools
- **Policy Validation**: Constitutional compliance verification
- **Conflict Resolution**: Automated policy conflict detection and resolution

### Base URL

`http://localhost:8004`

### Health Check

`GET /health`

### Metrics

`GET /metrics`

## Authentication

All API endpoints require proper authentication. Include the authentication token in the request headers:

```
Authorization: Bearer <your-token>
```

## API Endpoints

### Policy Synthesis

#### Generate Governance Policy

**Endpoint:** `POST /api/v1/synthesis/generate`

**Description:** Generate governance policy from constitutional principles

**Request Body:**
```json
{
  "constitutional_principles": [
    "transparency",
    "accountability",
    "democratic_legitimacy"
  ],
  "policy_domain": "data_governance",
  "stakeholder_requirements": [
    "privacy_protection",
    "data_accessibility"
  ],
  "use_consensus": true,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "policy_id": "pol_12345",
  "generated_policy": {
    "title": "Data Governance Policy",
    "content": "Policy content here...",
    "principles_applied": ["transparency", "accountability"],
    "compliance_score": 0.95
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "synthesis_metadata": {
    "models_used": ["gemini-2.5-pro", "deepseek-r1"],
    "consensus_score": 0.87,
    "generation_time_ms": 1250
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-05T10:30:00Z"
}
```

#### Validate Policy

**Endpoint:** `POST /api/v1/synthesis/validate`

**Description:** Validate policy against constitutional principles

**Request Body:**
```json
{
  "policy_text": "Policy content to validate",
  "constitutional_principles": ["transparency", "accountability"],
  "validation_level": "comprehensive",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "validation_result": {
    "is_compliant": true,
    "compliance_score": 0.92,
    "violations": [],
    "recommendations": [
      "Consider adding explicit privacy protections"
    ]
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validated_at": "2025-07-05T10:30:00Z"
}
```

#### Multi-Model Consensus

**Endpoint:** `POST /api/v1/synthesis/consensus`

**Description:** Generate policy using multi-model consensus

**Request Body:**
```json
{
  "policy_text": "Proposed governance policy",
  "models": ["gemini-2.5-pro", "deepseek-r1", "nvidia-qwen"],
  "consensus_threshold": 0.8,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "consensus_result": {
    "consensus_achieved": true,
    "consensus_score": 0.85,
    "model_agreements": {
      "gemini-2.5-pro": 0.87,
      "deepseek-r1": 0.83,
      "nvidia-qwen": 0.85
    ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
    "final_policy": "Consensus policy text..."
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "processed_at": "2025-07-05T10:30:00Z"
}
```

### Constitutional Analysis

#### Analyze Constitutional Compliance

**Endpoint:** `POST /api/v1/constitutional/analyze`

**Description:** Analyze constitutional compliance of policies

**Request Body:**
```json
{
  "policy_content": "Policy text to analyze",
  "analysis_depth": "comprehensive",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "analysis_result": {
    "compliance_score": 0.94,
    "constitutional_alignment": "high",
    "principle_coverage": {
      "transparency": 0.95,
      "accountability": 0.93,
      "democratic_legitimacy": 0.94
    ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
    "recommendations": []
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "analyzed_at": "2025-07-05T10:30:00Z"
}
```

### Stakeholder Management

#### Register Stakeholder

**Endpoint:** `POST /api/v1/stakeholders/register`

**Description:** Register a new stakeholder in the governance process

**Request Body:**
```json
{
  "name": "Privacy Advocacy Group",
  "type": "civil_society",
  "interests": ["privacy", "transparency"],
  "contact": "privacy@example.org",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "stakeholder_id": "stake_12345",
  "registration_status": "active",
  "assigned_roles": ["policy_reviewer"],
  "constitutional_hash": "cdd01ef066bc6cf2",
  "registered_at": "2025-07-05T10:30:00Z"
}
```

### Democratic Processes

#### Create Democratic Vote

**Endpoint:** `POST /api/v1/democracy/create-vote`

**Description:** Create a democratic voting process

**Request Body:**
```json
{
  "title": "Data Governance Policy Vote",
  "description": "Vote on proposed data governance policy",
  "policy_id": "pol_12345",
  "voting_period_hours": 168,
  "eligible_stakeholders": ["stake_12345", "stake_67890"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "vote_id": "vote_12345",
  "status": "active",
  "voting_deadline": "2025-07-12T10:30:00Z",
  "participation_url": "http://localhost:8004/vote/vote_12345",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "created_at": "2025-07-05T10:30:00Z"
}
```

### AI Model Management

#### Get Model Status

**Endpoint:** `GET /api/v1/models/status`

**Description:** Get status and health of AI models

**Response:**
```json
{
  "models": {
    "gemini-2.5-pro": {
      "status": "healthy",
      "response_time_ms": 245,
      "availability": 0.99
    ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
    "deepseek-r1": {
      "status": "healthy",
      "response_time_ms": 312,
      "availability": 0.98
    },
    "nvidia-qwen": {
      "status": "healthy",
      "response_time_ms": 189,
      "availability": 0.99
    }
  },
  "overall_health": "healthy",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "checked_at": "2025-07-05T10:30:00Z"
}
```

## Error Handling

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Constitutional hash validation failed",
    "details": {
      "expected_hash": "cdd01ef066bc6cf2",
      "provided_hash": "invalid_hash"
    }
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "2025-07-05T10:30:00Z"
}
```

## Performance Targets

- **Test Coverage**: ≥ 80%


- **Latency**: P99 ≤ 5ms for cached queries (latency_p99: ≤5ms)
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## Rate Limiting

- **Standard endpoints**: 1000 requests/hour per API key
- **Synthesis endpoints**: 100 requests/hour per API key
- **Consensus endpoints**: 50 requests/hour per API key

## Monitoring

### Health Endpoints

- `GET /health` - Basic health check
- `GET /api/v1/status` - Detailed service status
- `GET /metrics` - Prometheus metrics

### Key Metrics

- `gs_synthesis_requests_total` - Total policy synthesis requests
- `gs_synthesis_duration_seconds` - Policy synthesis processing time
- `gs_constitutional_compliance_score` - Constitutional compliance scores
- `gs_consensus_accuracy` - Multi-model consensus accuracy
- `gs_active_stakeholders` - Currently active stakeholders

## Examples

### Python Client Example

```python
import httpx

async def synthesize_policy():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8004/api/v1/synthesis/generate",
            json={
                "constitutional_principles": ["transparency", "accountability"],
                "policy_domain": "data_governance",
                "use_consensus": True,
                "constitutional_hash": "cdd01ef066bc6cf2"
            },
            headers={"Authorization": "Bearer your-token"}
        )
        return response.json()
```

### cURL Example

```bash
curl -X POST http://localhost:8004/api/v1/synthesis/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "constitutional_principles": ["transparency", "accountability"],
    "policy_domain": "data_governance",
    "constitutional_hash": "cdd01ef066bc6cf2"
  }'
```

---

**Last Updated**: 2025-07-05
**API Version**: 3.0.0
**Constitutional Hash**: `cdd01ef066bc6cf2` ✅
