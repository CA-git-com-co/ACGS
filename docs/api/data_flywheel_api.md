# Data Flywheel Integration API Documentation

## Overview

The Data Flywheel Integration provides NVIDIA AI Blueprints Data Flywheel capabilities for autonomous optimization of AI models used in governance processes while maintaining strict constitutional compliance.

**Base URL:** `http://localhost:8010/api/data-flywheel/`
**Interactive Docs:** `http://localhost:8010/docs`

## Authentication

All endpoints require JWT authentication with appropriate role permissions:

- **Admin:** Full access to all operations
- **Policy Manager:** Access to governance optimization jobs
- **Auditor:** Read-only access to compliance data
- **Constitutional Council:** Access to constitutional validation operations

## Core Endpoints

### Health Check

#### GET `/health`

Enhanced health check with ACGS-1 integration status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-06-11T15:51:43.132995",
  "service": "acgs_data_flywheel_demo",
  "acgs_integration": {
    "services": {
      "auth_service": true,
      "ac_service": true,
      "integrity_service": true,
      "fv_service": true,
      "gs_service": true,
      "pgc_service": true,
      "ec_service": true
    },
    "integration_status": "operational"
  }
}
```

### Constitutional Governance

#### GET `/constitutional/health`

Check health of ACGS-1 services integration.

**Response:**

```json
{
  "overall_status": "healthy",
  "services": {
    "auth_service": true,
    "ac_service": true,
    "integrity_service": true,
    "fv_service": true,
    "gs_service": true,
    "pgc_service": true,
    "ec_service": true
  },
  "constitutional_validation_available": true,
  "governance_workflows_operational": true
}
```

#### GET `/constitutional/workloads`

Get available governance workloads for optimization.

**Response:**

```json
{
  "workload_mapping": {
    "policy_synthesis": "gs_service",
    "formal_verification": "fv_service",
    "constitutional_analysis": "ac_service",
    "integrity_validation": "integrity_service",
    "policy_governance": "pgc_service",
    "evolutionary_computation": "ec_service"
  },
  "optimization_targets": {
    "cost_reduction": 0.8,
    "response_time": 500,
    "accuracy_threshold": 0.95,
    "constitutional_compliance": 0.98
  },
  "available_workloads": [
    "policy_synthesis",
    "formal_verification",
    "constitutional_analysis",
    "integrity_validation",
    "policy_governance",
    "evolutionary_computation"
  ]
}
```

#### POST `/constitutional/jobs`

Create a new constitutional governance optimization job.

**Request Body:**

```json
{
  "workload_id": "policy_synthesis_demo_001",
  "workload_type": "policy_synthesis",
  "optimization_target": "cost_reduction",
  "constitutional_requirements": {
    "democratic_participation": true,
    "transparency": true,
    "accountability": true,
    "rule_of_law": true,
    "human_rights": true
  }
}
```

**Response:**

```json
{
  "id": "demo_job_20250611_155206",
  "status": "queued",
  "message": "Constitutional governance optimization workflow started (demo mode)"
}
```

#### GET `/constitutional/compliance/{job_id}`

Get compliance validation results for a specific job.

**Response:**

```json
{
  "job_id": "demo_job_20250611_155206",
  "compliance_status": "validated",
  "constitutional_score": 0.96,
  "principle_scores": {
    "democratic_participation": 0.98,
    "transparency": 0.95,
    "accountability": 0.97,
    "rule_of_law": 0.94,
    "human_rights": 0.96
  },
  "recommendations": ["Enhance transparency mechanisms", "Strengthen accountability measures"]
}
```

#### POST `/constitutional/validate`

Manual constitutional compliance validation.

**Request Body:**

```json
{
  "model_output": "This policy promotes democratic participation through transparent voting mechanisms.",
  "constitutional_principles": ["democratic_participation", "transparency"]
}
```

**Response:**

```json
{
  "validation_id": "val_20250611_155300",
  "compliance_score": 0.94,
  "principle_analysis": {
    "democratic_participation": {
      "score": 0.96,
      "confidence": 0.92,
      "reasoning": "Strong democratic elements identified"
    },
    "transparency": {
      "score": 0.92,
      "confidence": 0.89,
      "reasoning": "Clear transparency mechanisms present"
    }
  },
  "overall_assessment": "compliant",
  "recommendations": []
}
```

#### POST `/constitutional/traffic/collect`

Collect governance traffic for analysis and optimization.

**Request Body:**

```json
{
  "service_name": "gs_service",
  "endpoint": "/api/v1/synthesis",
  "request_data": {
    "principles": ["democratic_participation", "transparency"],
    "context": "Policy synthesis request"
  },
  "response_data": {
    "synthesized_policy": "Generated policy text",
    "confidence": 0.94
  },
  "metadata": {
    "timestamp": "2025-06-11T15:53:00Z",
    "user_id": "user_123",
    "session_id": "session_456"
  }
}
```

**Response:**

```json
{
  "collection_id": "traffic_20250611_155300",
  "status": "collected",
  "analysis_queued": true
}
```

### Monitoring and Metrics

#### GET `/constitutional/metrics/{job_id}`

Get detailed governance metrics for a specific job.

**Response:**

```json
{
  "job_id": "demo_job_20250611_155206",
  "performance_metrics": {
    "response_time_ms": 45,
    "cost_reduction": 0.82,
    "accuracy": 0.96,
    "constitutional_compliance": 0.98
  },
  "optimization_progress": {
    "iterations": 5,
    "best_model": "model_v3",
    "improvement": 0.15
  },
  "resource_usage": {
    "cpu_utilization": 0.65,
    "memory_usage": "2.1GB",
    "gpu_utilization": 0.78
  }
}
```

## Constitutional Principles Supported

The Data Flywheel integration validates AI outputs against these constitutional principles:

1. **Democratic Participation** - Ensure inclusive governance processes
2. **Transparency** - Maintain open and clear decision-making
3. **Accountability** - Enable responsibility tracking
4. **Rule of Law** - Uphold legal and constitutional frameworks
5. **Human Rights** - Protect fundamental rights and dignity
6. **Sustainability** - Consider long-term environmental impact
7. **Public Welfare** - Prioritize collective well-being
8. **Equity** - Ensure fair treatment and opportunities
9. **Privacy Protection** - Safeguard personal information
10. **Due Process** - Maintain fair procedural standards

## Error Handling

All endpoints return standard HTTP status codes:

- **200 OK**: Successful operation
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

Error responses include detailed information:

```json
{
  "error": "ValidationError",
  "message": "Constitutional requirements validation failed",
  "details": {
    "missing_principles": ["transparency"],
    "invalid_format": "constitutional_requirements must be object"
  },
  "timestamp": "2025-06-11T15:55:00Z"
}
```

## Rate Limiting

API endpoints are rate-limited to ensure system stability:

- **Standard endpoints**: 100 requests per minute
- **Job creation**: 10 requests per minute
- **Traffic collection**: 1000 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1623456789
```

## Integration Examples

### Python Client Example

```python
import requests
import json

# Create a governance optimization job
job_data = {
    "workload_id": "policy_optimization_001",
    "workload_type": "policy_synthesis",
    "optimization_target": "cost_reduction",
    "constitutional_requirements": {
        "democratic_participation": True,
        "transparency": True,
        "accountability": True
    }
}

response = requests.post(
    "http://localhost:8010/constitutional/jobs",
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"},
    json=job_data
)

job_result = response.json()
print(f"Job created: {job_result['id']}")
```

### JavaScript Client Example

```javascript
const createGovernanceJob = async () => {
  const jobData = {
    workload_id: 'policy_optimization_001',
    workload_type: 'policy_synthesis',
    optimization_target: 'cost_reduction',
    constitutional_requirements: {
      democratic_participation: true,
      transparency: true,
      accountability: true,
    },
  };

  const response = await fetch('http://localhost:8010/constitutional/jobs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer YOUR_JWT_TOKEN',
    },
    body: JSON.stringify(jobData),
  });

  const result = await response.json();
  console.log(`Job created: ${result.id}`);
};
```

For more examples and detailed integration guides, see the [Data Flywheel Integration Documentation](../integrations/data-flywheel/README.md).
