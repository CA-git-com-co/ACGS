# Governance Synthesis Service API

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Governance Synthesis Service (Port 8004)** API. This service is a core component of the ACGS system, responsible for synthesizing governance policies from constitutional principles using advanced AI model integration.

- **Service Name**: Governance Synthesis Service
- **Port**: 8004
- **Base URL**: `/api/v1`

## 2. Service Endpoints

### 2.1. Health and Metrics

- **GET /health**: Returns the health status of the service.
- **GET /metrics**: Provides Prometheus-compatible performance metrics.

### 2.2. Policy Synthesis

#### POST /synthesis/generate

Generates a governance policy from a set of constitutional principles and stakeholder requirements.

**Request Body**:

```json
{
  "constitutional_principles": ["string"],
  "policy_domain": "string",
  "stakeholder_requirements": ["string"],
  "use_consensus": boolean,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "policy_id": "string",
  "generated_policy": {
    "title": "string",
    "content": "string",
    "principles_applied": ["string"],
    "compliance_score": float
  },
  "synthesis_metadata": {
    "models_used": ["string"],
    "consensus_score": float,
    "generation_time_ms": int
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": "string"
}
```

#### POST /synthesis/validate

Validates a given policy against a set of constitutional principles.

**Request Body**:

```json
{
  "policy_text": "string",
  "constitutional_principles": ["string"],
  "validation_level": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "validation_result": {
    "is_compliant": boolean,
    "compliance_score": float,
    "violations": ["string"],
    "recommendations": ["string"]
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "validated_at": "string"
}
```

#### POST /synthesis/consensus

Generates a policy using a multi-model consensus approach.

**Request Body**:

```json
{
  "policy_text": "string",
  "models": ["string"],
  "consensus_threshold": float,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "consensus_result": {
    "consensus_achieved": boolean,
    "consensus_score": float,
    "model_agreements": {},
    "final_policy": "string"
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "processed_at": "string"
}
```

### 2.3. Constitutional Analysis

#### POST /constitutional/analyze

Analyzes the constitutional compliance of a given policy.

**Request Body**:

```json
{
  "policy_content": "string",
  "analysis_depth": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (200 OK)**:

```json
{
  "analysis_result": {
    "compliance_score": float,
    "constitutional_alignment": "string",
    "principle_coverage": {},
    "recommendations": ["string"]
  },
  "constitutional_hash": "cdd01ef066bc6cf2",
  "analyzed_at": "string"
}
```

### 2.4. Stakeholder Management

#### POST /stakeholders/register

Registers a new stakeholder in the governance process.

**Request Body**:

```json
{
  "name": "string",
  "type": "string",
  "interests": ["string"],
  "contact": "string",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (201 Created)**:

```json
{
  "stakeholder_id": "string",
  "registration_status": "string",
  "assigned_roles": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2",
  "registered_at": "string"
}
```

### 2.5. Democratic Processes

#### POST /democracy/create-vote

Creates a democratic voting process for a given policy.

**Request Body**:

```json
{
  "title": "string",
  "description": "string",
  "policy_id": "string",
  "voting_period_hours": int,
  "eligible_stakeholders": ["string"],
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response (201 Created)**:

```json
{
  "vote_id": "string",
  "status": "string",
  "voting_deadline": "string",
  "participation_url": "string",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "created_at": "string"
}
```

### 2.6. AI Model Management

#### GET /models/status

Gets the status and health of the AI models used by the service.

**Response (200 OK)**:

```json
{
  "models": {},
  "overall_health": "string",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "checked_at": "string"
}
```

## 3. Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## 4. Error Handling

Standard HTTP status codes are used. All error responses include a constitutional compliance validation status.

- `400 Bad Request`: Invalid request parameters.
- `401 Unauthorized`: Authentication required.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource not found.
- `500 Internal Server Error`: Server error.

## 5. Related Information

- **Constitutional AI Service**: For information on how constitutional principles are validated, see the [Constitutional AI Service API](constitutional-ai.md).
- **Policy Governance Service**: For information on how policies are evaluated and governed, see the [Policy Governance Service API](policy-governance.md).
- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
- [ACGS System Overview](../../SYSTEM_OVERVIEW.md)
## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation
