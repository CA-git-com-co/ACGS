# ACGS-2 API Reference

## Authentication

All API endpoints require authentication using JWT tokens.

### Authentication Header
```
Authorization: Bearer <jwt_token>
```

### Token Endpoints

#### POST /auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 28800
}
```

## Constitutional AI Service (Port 8001)

### POST /api/v1/constitutional-ai/create-conversation
Create a new constitutional AI conversation.

**Request Body:**
```json
{
  "topic": "string",
  "participants": ["string"],
  "constitutional_principles": ["string"]
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "status": "active",
  "created_at": "datetime"
}
```

### POST /api/v1/constitutional-ai/synthesize-principle
Synthesize constitutional principles from input.

**Request Body:**
```json
{
  "input_text": "string",
  "context": "string",
  "synthesis_type": "democratic|expert|hybrid"
}
```

**Response:**
```json
{
  "principle": "string",
  "confidence_score": 0.95,
  "supporting_evidence": ["string"]
}
```

## Policy Governance Service (Port 8005)

### POST /api/v1/policy-governance/evaluate
Evaluate policy against constitutional principles.

**Request Body:**
```json
{
  "policy_text": "string",
  "constitutional_principles": ["string"],
  "evaluation_criteria": ["string"]
}
```

**Response:**
```json
{
  "compliance_score": 0.92,
  "violations": ["string"],
  "recommendations": ["string"],
  "evaluation_id": "uuid"
}
```

### POST /api/v1/governance-workflows/execute
Execute governance workflow.

**Request Body:**
```json
{
  "workflow_type": "policy_creation|review|approval",
  "input_data": {},
  "stakeholders": ["string"]
}
```

**Response:**
```json
{
  "workflow_id": "uuid",
  "status": "running",
  "next_steps": ["string"]
}
```

## Governance Synthesis Service (Port 8004)

### POST /api/v1/governance-synthesis/synthesize
Synthesize governance decisions from multiple inputs.

**Request Body:**
```json
{
  "inputs": ["string"],
  "synthesis_method": "consensus|optimization|hybrid",
  "constraints": {}
}
```

**Response:**
```json
{
  "synthesized_decision": "string",
  "confidence_score": 0.88,
  "contributing_factors": ["string"],
  "synthesis_id": "uuid"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid input parameters",
  "details": ["field_name: error_description"]
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred",
  "request_id": "uuid"
}
```

## Rate Limiting

- Default: 100 requests per minute per user
- Burst: 200 requests per minute
- Headers returned:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time (Unix timestamp)
