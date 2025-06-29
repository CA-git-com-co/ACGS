# ACGS-1 Lite API Documentation

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Version:** 1.0.0  
**API Standard:** OpenAPI 3.0.3

## 🎯 Overview

This document provides comprehensive API documentation for all ACGS-1 Lite services. Each service exposes RESTful APIs for constitutional governance, audit trails, evolution oversight, and secure sandbox execution.

## 🔗 Service Endpoints

| Service | Base URL | Port | Purpose |
|---------|----------|------|---------|
| **Policy Engine** | `http://localhost:8004` | 8004 | Constitutional policy evaluation |
| **Evolution Oversight** | `http://localhost:8002` | 8002 | AI agent evolution management |
| **Audit Engine** | `http://localhost:8003` | 8003 | Cryptographic audit trails |
| **Sandbox Controller** | `http://localhost:8001` | 8001 | Hardened execution environments |

## 🔐 Authentication

### API Key Authentication
```http
Authorization: Bearer <api_key>
```

### Constitutional Hash Verification
All requests must include the constitutional hash for verification:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

## 📊 Policy Engine API (Port 8004)

The Policy Engine evaluates constitutional policies and enforces safety rules for AI agent actions.

### Base URL
```
http://localhost:8004
```

### Endpoints

#### 1. Evaluate Constitutional Policy

**Endpoint:** `POST /v1/data/acgs/main/decision`

Evaluates whether an action complies with constitutional principles and safety rules.

**Request:**
```json
{
  "type": "constitutional_evaluation",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "action": "data.read_public",
  "context": {
    "environment": {
      "sandbox_enabled": true,
      "audit_enabled": true,
      "isolation_level": "strict"
    },
    "agent": {
      "trust_level": 0.9,
      "requested_resources": {
        "cpu_cores": 2,
        "memory_gb": 4,
        "disk_gb": 10,
        "network_mbps": 100
      },
      "capabilities": ["data_read", "compute_analysis"]
    },
    "responsible_party": "user@example.com",
    "explanation": "Reading public dataset for analysis",
    "urgency": "normal",
    "session_id": "sess_123456"
  }
}
```

**Response:**
```json
{
  "allow": true,
  "compliance_score": 0.96,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "reasons": [],
  "evaluation_details": {
    "safety": {
      "passed": true,
      "score": 1.0,
      "violations": [],
      "risk_level": "low"
    },
    "constitutional": {
      "passed": true,
      "score": 0.95,
      "principles": {
        "autonomy": 0.98,
        "beneficence": 0.94,
        "non_maleficence": 1.0,
        "transparency": 0.92,
        "fairness": 0.96,
        "privacy": 0.94,
        "accountability": 0.95
      }
    },
    "resources": {
      "passed": true,
      "score": 1.0,
      "within_limits": true
    },
    "transparency": {
      "passed": true,
      "score": 0.9,
      "explanation_quality": "good"
    }
  },
  "conditions": [],
  "monitoring_requirements": [
    "log_all_data_access",
    "track_resource_usage"
  ],
  "expires_at": "2024-12-28T15:30:00Z",
  "session_id": "sess_123456",
  "evaluation_time_ms": 0.8,
  "cache_hit": false
}
```

#### 2. Simple Allow/Deny Check

**Endpoint:** `GET /v1/data/acgs/main/allow`

Quick boolean check for basic policy compliance.

**Parameters:**
- `type`: Request type (constitutional_evaluation, evolution_approval, data_access)
- `constitutional_hash`: Required constitutional hash
- `action`: Action to evaluate

**Example:**
```http
GET /v1/data/acgs/main/allow?type=constitutional_evaluation&constitutional_hash=cdd01ef066bc6cf2&action=data.read_public
```

**Response:**
```json
{
  "allow": true
}
```

#### 3. Evolution Approval

**Endpoint:** `POST /v1/data/acgs/main/decision`

Evaluates evolution requests for AI agent updates.

**Request:**
```json
{
  "type": "evolution_approval",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "evolution_request": {
    "type": "minor_update",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "agent_id": "agent_123",
    "version": "1.2.1",
    "changes": {
      "code_changes": ["Performance optimization in data processing"],
      "external_dependencies": [],
      "privilege_escalation": false,
      "experimental_features": false,
      "breaking_changes": false
    },
    "performance_analysis": {
      "complexity_delta": 0.02,
      "memory_delta": -0.05,
      "latency_delta": -0.10,
      "resource_delta": 0.01
    },
    "security_analysis": {
      "new_attack_vectors": [],
      "security_improvements": ["Enhanced input validation"],
      "risk_assessment": "low"
    },
    "rollback_plan": {
      "procedure": "Automated rollback via git revert and container restart",
      "verification": "Unit tests, integration tests, and smoke tests",
      "timeline": "< 5 minutes",
      "dependencies": "None",
      "tested": true,
      "automated": true,
      "contact": "devops@example.com"
    }
  }
}
```

**Response:**
```json
{
  "allow": true,
  "approval_type": "auto_approved",
  "compliance_score": 0.94,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "reasons": [],
  "evaluation_details": {
    "risk_assessment": {
      "overall_risk": 0.15,
      "risk_factors": {
        "code_complexity": 0.02,
        "dependency_changes": 0.0,
        "privilege_changes": 0.0,
        "experimental_features": 0.0
      },
      "mitigation_score": 0.95
    },
    "rollback_readiness": {
      "score": 1.0,
      "automated": true,
      "tested": true,
      "timeline_acceptable": true
    },
    "performance_impact": {
      "acceptable": true,
      "improvements": ["latency", "memory"],
      "regressions": []
    }
  },
  "conditions": [
    "Monitor performance metrics for 24 hours",
    "Automated rollback if error rate > 1%"
  ],
  "approval_id": "approval_789",
  "valid_until": "2024-12-29T12:00:00Z"
}
```

#### 4. Data Access Control

**Endpoint:** `POST /v1/data/acgs/main/decision`

Evaluates data access requests with privacy and consent validation.

**Request:**
```json
{
  "type": "data_access",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "data_request": {
    "data_fields": [
      {
        "name": "user_preferences",
        "classification_level": 2,
        "category": "personal_identifiable_information",
        "sensitivity": "medium"
      },
      {
        "name": "usage_analytics",
        "classification_level": 1,
        "category": "analytics",
        "sensitivity": "low"
      }
    ],
    "requester_clearance_level": 3,
    "special_authorization": true,
    "data_subjects": ["user_123", "user_456"],
    "consent_records": [
      {
        "subject_id": "user_123",
        "status": "granted",
        "allowed_purposes": ["service_improvement", "analytics"],
        "granted_at": "2024-12-01T10:00:00Z",
        "expiry_time": 1735689600,
        "consent_type": "explicit"
      },
      {
        "subject_id": "user_456",
        "status": "granted",
        "allowed_purposes": ["service_improvement"],
        "granted_at": "2024-12-15T14:30:00Z",
        "expiry_time": 1738281600,
        "consent_type": "explicit"
      }
    ],
    "purpose": "service_improvement",
    "allowed_purposes": ["service_improvement", "analytics"],
    "justified_fields": ["user_preferences", "usage_analytics"],
    "timestamp": 1704067200,
    "retention_policy": {
      "personal_identifiable_information": 2592000,
      "analytics": 7776000
    },
    "encryption_config": {
      "user_preferences": {
        "encrypted": true,
        "algorithm": "AES",
        "key_length": 256,
        "mode": "GCM"
      },
      "usage_analytics": {
        "encrypted": false
      },
      "key_management": {
        "rotation_enabled": true,
        "rotation_frequency_days": 90,
        "secure_storage": true,
        "access_controlled": true,
        "hsm_protected": false
      }
    }
  }
}
```

#### 5. Health Check

**Endpoint:** `GET /v1/data/acgs/main/health`

Returns service health status and system information.

**Response:**
```json
{
  "status": "healthy",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "performance": {
    "request_count": 15420,
    "avg_latency_ms": 0.8,
    "p99_latency_ms": 0.95,
    "targets_met": {
      "p99_under_1ms": true
    }
  },
  "cache_stats": {
    "l1_size": 8450,
    "l1_max_size": 10000,
    "l1_utilization": 0.845,
    "hit_rate": 0.96
  },
  "dependencies": {
    "redis": "connected",
    "opa_engine": "loaded",
    "prometheus": "collecting"
  },
  "timestamp": "2024-12-28T12:00:00Z"
}
```

#### 6. Performance Metrics

**Endpoint:** `GET /v1/metrics`

Returns detailed performance metrics in Prometheus format.

**Response:**
```json
{
  "request_count": 15420,
  "avg_latency_ms": 0.8,
  "percentiles": {
    "p50": 0.6,
    "p95": 0.9,
    "p99": 0.95
  },
  "cache_hit_rate": 0.96,
  "l1_hit_rate": 0.85,
  "l2_hit_rate": 0.11,
  "partial_eval_rate": 0.42,
  "batch_stats": {
    "batch_count": 1542,
    "avg_batch_size": 8.5,
    "total_batched_requests": 13107
  },
  "targets_met": {
    "p50_under_0_5ms": false,
    "p95_under_0_8ms": false,
    "p99_under_1ms": true,
    "cache_hit_rate_over_95": true
  }
}
```

#### 7. Cache Warming

**Endpoint:** `GET /v1/cache/warm`

Warms up the cache with common policy scenarios.

**Response:**
```json
{
  "warmed_scenarios": 5,
  "total_scenarios": 5,
  "cache_entries_added": 5,
  "warm_up_time_ms": 125
}
```

### Error Responses

**400 Bad Request:**
```json
{
  "error": "invalid_request",
  "message": "Constitutional hash is required",
  "details": {
    "field": "constitutional_hash",
    "expected": "cdd01ef066bc6cf2"
  }
}
```

**403 Forbidden:**
```json
{
  "error": "constitutional_violation",
  "message": "Action violates constitutional principles",
  "details": {
    "violations": ["non_maleficence"],
    "risk_level": "high"
  }
}
```

**429 Too Many Requests:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "retry_after_seconds": 60
}
```

## 🔄 Evolution Oversight API (Port 8002)

The Evolution Oversight service manages AI agent evolution requests and approval workflows.

### Base URL
```
http://localhost:8002
```

### Endpoints

#### 1. Submit Evolution Request

**Endpoint:** `POST /evolution/request`

Submits an evolution request for approval.

**Request:**
```json
{
  "agent_id": "agent_123",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "evolution_type": "minor_update",
  "version": "1.2.1",
  "changes": {
    "code_changes": ["Performance optimization"],
    "external_dependencies": ["numpy>=1.21.0"],
    "privilege_escalation": false,
    "experimental_features": false
  },
  "performance_analysis": {
    "complexity_delta": 0.05,
    "memory_delta": 0.02,
    "latency_delta": -0.1,
    "resource_delta": 0.01
  },
  "rollback_plan": {
    "procedure": "Automated rollback",
    "tested": true,
    "automated": true
  },
  "submitter": "dev@example.com",
  "justification": "Performance improvements for data processing workloads"
}
```

**Response:**
```json
{
  "request_id": "req_789123",
  "status": "submitted",
  "estimated_review_time": "15m",
  "approval_required": false,
  "auto_approval_eligible": true,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "created_at": "2024-12-28T12:00:00Z"
}
```

#### 2. Get Evolution Request Status

**Endpoint:** `GET /evolution/request/{request_id}`

Retrieves the status of an evolution request.

**Response:**
```json
{
  "request_id": "req_789123",
  "agent_id": "agent_123",
  "status": "approved",
  "approval_type": "auto_approved",
  "approved_by": "system",
  "approved_at": "2024-12-28T12:15:00Z",
  "compliance_score": 0.94,
  "conditions": [
    "Monitor for 24 hours",
    "Rollback if error rate > 1%"
  ],
  "valid_until": "2024-12-29T12:00:00Z",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

#### 3. List Evolution Requests

**Endpoint:** `GET /evolution/requests`

Lists evolution requests with filtering options.

**Parameters:**
- `agent_id`: Filter by agent ID
- `status`: Filter by status (pending, approved, rejected)
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "requests": [
    {
      "request_id": "req_789123",
      "agent_id": "agent_123",
      "status": "approved",
      "created_at": "2024-12-28T12:00:00Z",
      "approved_at": "2024-12-28T12:15:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### 4. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "dependencies": {
    "postgres": "connected",
    "policy_engine": "available"
  }
}
```

## 📊 Audit Engine API (Port 8003)

The Audit Engine provides cryptographic audit trails and event logging.

### Base URL
```
http://localhost:8003
```

### Endpoints

#### 1. Log Audit Event

**Endpoint:** `POST /audit/event`

Logs an audit event with cryptographic integrity.

**Request:**
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "event_type": "policy_evaluation",
  "agent_id": "agent_123",
  "action": "data.read_public",
  "result": "allowed",
  "metadata": {
    "compliance_score": 0.96,
    "evaluation_time_ms": 0.8,
    "cache_hit": false
  },
  "responsible_party": "user@example.com",
  "session_id": "sess_123456"
}
```

**Response:**
```json
{
  "event_id": "evt_abc123def456",
  "hash": "sha256:a1b2c3d4e5f6...",
  "previous_hash": "sha256:f6e5d4c3b2a1...",
  "timestamp": "2024-12-28T12:00:00.123Z",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "ingested": true
}
```

#### 2. Query Audit Events

**Endpoint:** `GET /audit/events`

Queries audit events with filtering and pagination.

**Parameters:**
- `agent_id`: Filter by agent ID
- `event_type`: Filter by event type
- `start_time`: Start timestamp (ISO 8601)
- `end_time`: End timestamp (ISO 8601)
- `limit`: Number of results (default: 100)
- `offset`: Pagination offset

**Response:**
```json
{
  "events": [
    {
      "event_id": "evt_abc123def456",
      "event_type": "policy_evaluation",
      "agent_id": "agent_123",
      "action": "data.read_public",
      "result": "allowed",
      "timestamp": "2024-12-28T12:00:00.123Z",
      "hash": "sha256:a1b2c3d4e5f6...",
      "metadata": {
        "compliance_score": 0.96
      }
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0,
  "integrity_verified": true
}
```

#### 3. Verify Audit Trail

**Endpoint:** `POST /audit/verify`

Verifies the cryptographic integrity of audit trail.

**Request:**
```json
{
  "start_event_id": "evt_abc123def456",
  "end_event_id": "evt_def456ghi789",
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response:**
```json
{
  "verified": true,
  "event_count": 1000,
  "hash_chain_intact": true,
  "constitutional_hash_verified": true,
  "verification_time_ms": 45,
  "details": {
    "first_event": {
      "event_id": "evt_abc123def456",
      "timestamp": "2024-12-28T10:00:00.000Z"
    },
    "last_event": {
      "event_id": "evt_def456ghi789",
      "timestamp": "2024-12-28T12:00:00.000Z"
    }
  }
}
```

#### 4. Get Event by ID

**Endpoint:** `GET /audit/event/{event_id}`

Retrieves a specific audit event by ID.

**Response:**
```json
{
  "event_id": "evt_abc123def456",
  "event_type": "policy_evaluation",
  "agent_id": "agent_123",
  "action": "data.read_public",
  "result": "allowed",
  "timestamp": "2024-12-28T12:00:00.123Z",
  "hash": "sha256:a1b2c3d4e5f6...",
  "previous_hash": "sha256:f6e5d4c3b2a1...",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "metadata": {
    "compliance_score": 0.96,
    "evaluation_time_ms": 0.8
  },
  "responsible_party": "user@example.com",
  "session_id": "sess_123456"
}
```

#### 5. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "version": "1.0.0",
  "event_count": 15420,
  "last_event_timestamp": "2024-12-28T12:00:00.123Z",
  "dependencies": {
    "postgres": "connected",
    "redpanda": "connected",
    "s3": "available"
  }
}
```

## 🛡️ Sandbox Controller API (Port 8001)

The Sandbox Controller provides hardened execution environments for AI agents.

### Base URL
```
http://localhost:8001
```

### Endpoints

#### 1. Execute in Sandbox

**Endpoint:** `POST /execute`

Executes code in a hardened sandbox environment.

**Request:**
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "runtime": "gvisor",
  "image": "python:3.11-slim",
  "command": ["python", "-c", "print('Hello from sandbox')"],
  "security_profile": "restricted",
  "resource_limits": {
    "cpu_cores": 1,
    "memory_gb": 2,
    "disk_gb": 5,
    "execution_time_seconds": 300,
    "network_enabled": false
  },
  "environment_variables": {
    "PYTHONPATH": "/app"
  },
  "volumes": [
    {
      "host_path": "/tmp/sandbox-data",
      "container_path": "/app/data",
      "read_only": true
    }
  ],
  "agent_id": "agent_123",
  "session_id": "sess_123456"
}
```

**Response:**
```json
{
  "execution_id": "exec_789abc123",
  "status": "completed",
  "exit_code": 0,
  "stdout": "Hello from sandbox\n",
  "stderr": "",
  "execution_time_ms": 1250,
  "resource_usage": {
    "cpu_time_ms": 45,
    "memory_peak_mb": 12,
    "disk_read_mb": 0.1,
    "disk_write_mb": 0.0
  },
  "security_events": [],
  "constitutional_hash": "cdd01ef066bc6cf2",
  "started_at": "2024-12-28T12:00:00.000Z",
  "completed_at": "2024-12-28T12:00:01.250Z"
}
```

#### 2. Get Execution Status

**Endpoint:** `GET /execute/{execution_id}`

Retrieves the status of a sandbox execution.

**Response:**
```json
{
  "execution_id": "exec_789abc123",
  "status": "running",
  "runtime": "gvisor",
  "started_at": "2024-12-28T12:00:00.000Z",
  "execution_time_ms": 5000,
  "resource_usage": {
    "cpu_time_ms": 145,
    "memory_current_mb": 8,
    "memory_peak_mb": 12
  },
  "security_events": []
}
```

#### 3. Stop Execution

**Endpoint:** `DELETE /execute/{execution_id}`

Stops a running sandbox execution.

**Response:**
```json
{
  "execution_id": "exec_789abc123",
  "status": "stopped",
  "stopped_at": "2024-12-28T12:00:05.500Z",
  "reason": "user_requested"
}
```

#### 4. List Executions

**Endpoint:** `GET /executions`

Lists sandbox executions with filtering options.

**Parameters:**
- `agent_id`: Filter by agent ID
- `status`: Filter by status (running, completed, failed, stopped)
- `limit`: Number of results (default: 50)

**Response:**
```json
{
  "executions": [
    {
      "execution_id": "exec_789abc123",
      "agent_id": "agent_123",
      "status": "completed",
      "runtime": "gvisor",
      "started_at": "2024-12-28T12:00:00.000Z",
      "completed_at": "2024-12-28T12:00:01.250Z"
    }
  ],
  "total": 1
}
```

#### 5. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "version": "1.0.0",
  "runtimes": {
    "gvisor": "available",
    "firecracker": "available",
    "docker": "available"
  },
  "active_executions": 3,
  "total_executions": 1542,
  "resource_usage": {
    "cpu_utilization": 0.15,
    "memory_utilization": 0.25
  }
}
```

## 🔧 Rate Limiting

All APIs implement rate limiting to prevent abuse:

| Service | Endpoint | Rate Limit |
|---------|----------|------------|
| Policy Engine | `/v1/data/acgs/main/decision` | 100 requests/minute |
| Policy Engine | `/v1/data/acgs/main/allow` | 1000 requests/minute |
| Evolution Oversight | `/evolution/request` | 10 requests/minute |
| Audit Engine | `/audit/event` | 1000 requests/minute |
| Sandbox Controller | `/execute` | 20 requests/minute |

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 📈 Response Times

Target response times for API endpoints:

| Endpoint | Target | P99 Target |
|----------|--------|------------|
| Policy evaluation | <1ms | <5ms |
| Simple allow/deny | <0.5ms | <2ms |
| Evolution request | <50ms | <200ms |
| Audit event logging | <10ms | <50ms |
| Sandbox execution | <2s | <10s |

## 🚨 Error Handling

All APIs follow consistent error response format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "field_name",
    "value": "invalid_value"
  },
  "timestamp": "2024-12-28T12:00:00Z",
  "request_id": "req_123456"
}
```

Common error codes:
- `invalid_request`: Malformed request
- `unauthorized`: Authentication failed
- `forbidden`: Access denied
- `not_found`: Resource not found
- `rate_limit_exceeded`: Rate limit exceeded
- `internal_error`: Server error
- `constitutional_violation`: Policy violation

## 📋 OpenAPI Specifications

Complete OpenAPI 3.0.3 specifications are available for each service:

- [Policy Engine OpenAPI](./openapi/policy-engine.yaml)
- [Evolution Oversight OpenAPI](./openapi/evolution-oversight.yaml)
- [Audit Engine OpenAPI](./openapi/audit-engine.yaml)
- [Sandbox Controller OpenAPI](./openapi/sandbox-controller.yaml)

## 🧪 Testing APIs

### Using curl

```bash
# Test policy evaluation
curl -X POST http://localhost:8004/v1/data/acgs/main/decision \
  -H "Content-Type: application/json" \
  -d '{
    "type": "constitutional_evaluation",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "action": "data.read_public",
    "context": {
      "environment": {"sandbox_enabled": true},
      "agent": {"trust_level": 0.9}
    }
  }'

# Test evolution request
curl -X POST http://localhost:8002/evolution/request \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "agent_id": "agent_123",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "evolution_type": "minor_update"
  }'
```

### Using Python

```python
import requests

# Policy evaluation
response = requests.post('http://localhost:8004/v1/data/acgs/main/decision', 
  json={
    "type": "constitutional_evaluation",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "action": "data.read_public",
    "context": {
      "environment": {"sandbox_enabled": True},
      "agent": {"trust_level": 0.9}
    }
  })

print(response.json())
```

---

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**API Documentation Version:** 1.0.0  
**Last Updated:** 2024-12-28