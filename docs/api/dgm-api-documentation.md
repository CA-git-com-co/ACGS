# DGM Service API Documentation

## Overview

The Darwin Gödel Machine (DGM) service provides a comprehensive REST API for self-improvement operations, bandit algorithms, performance monitoring, and constitutional compliance. The API follows RESTful principles and includes comprehensive error handling, validation, and documentation.

## Base URL

```
http://localhost:8003/api/v1
```

## Authentication

The DGM API uses the ACGS authentication system. Include the authentication token in the Authorization header:

```
Authorization: Bearer <token>
```

## API Endpoints

### Core DGM Operations

#### GET /dgm/status

Get comprehensive DGM system status.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "active_improvements": 2,
  "total_improvements": 100,
  "success_rate": 85.0,
  "constitutional_compliance_score": 0.95,
  "performance_metrics": {
    "response_time_avg": 150.5,
    "throughput": 1000,
    "error_rate": 0.01
  },
  "system_health": {
    "status": "healthy"
  },
  "last_optimization": "2025-01-20T12:00:00Z"
}
```

#### POST /dgm/improve

Trigger a new improvement cycle.

**Request:**
```json
{
  "target_service": "dgm-service",
  "improvement_type": "code_optimization",
  "priority": "medium",
  "description": "Optimize query performance",
  "constraints": {
    "max_execution_time": 3600,
    "resource_limit": "high"
  },
  "safety_threshold": 0.8
}
```

**Response:**
```json
{
  "improvement_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "message": "Improvement cycle initiated successfully",
  "estimated_completion_time": "2025-01-20T13:00:00Z",
  "safety_score": 0.85,
  "constitutional_compliance_score": 0.92,
  "created_at": "2025-01-20T12:00:00Z"
}
```

### Bandit Algorithm Operations

#### POST /dgm/bandit/select-arm

Select an arm using bandit algorithm.

**Request:**
```json
{
  "context_key": "improvement_context",
  "algorithm_type": "conservative_bandit",
  "exploration_rate": 0.1,
  "safety_threshold": 0.8
}
```

**Response:**
```json
{
  "selected_arm": "code_optimization",
  "confidence": 0.85,
  "expected_reward": 0.75,
  "exploration_factor": 0.1,
  "safety_validated": true,
  "constitutional_compliance": true
}
```

#### POST /dgm/bandit/reward-feedback

Provide reward feedback for bandit algorithm learning.

**Request:**
```json
{
  "context_key": "improvement_context",
  "arm_id": "code_optimization",
  "reward": 0.9,
  "metadata": {
    "execution_time": 120,
    "resource_usage": "medium"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reward feedback processed successfully",
  "updated_stats": {
    "total_pulls": 11,
    "average_reward": 0.8
  }
}
```

### Performance Metrics

#### POST /dgm/metrics/query

Query performance metrics for a specific time range.

**Request:**
```json
{
  "metric_name": "response_time",
  "start_time": "2025-01-20T12:00:00Z",
  "end_time": "2025-01-20T13:00:00Z",
  "aggregation": "avg",
  "service_filter": "dgm-service"
}
```

**Response:**
```json
{
  "metric_name": "response_time",
  "time_range": {
    "start": "2025-01-20T12:00:00Z",
    "end": "2025-01-20T13:00:00Z"
  },
  "aggregation": "avg",
  "data_points": [
    {
      "timestamp": "2025-01-20T12:00:00Z",
      "value": 150.0
    },
    {
      "timestamp": "2025-01-20T12:01:00Z",
      "value": 155.0
    }
  ],
  "summary": {
    "avg": 152.5,
    "min": 150.0,
    "max": 155.0,
    "count": 2
  },
  "constitutional_compliance": true
}
```

#### GET /dgm/metrics/summary

Get performance metrics summary.

**Parameters:**
- `hours` (int): Hours to include in summary (1-168, default: 24)
- `service_name` (string, optional): Filter by service name

**Response:**
```json
{
  "time_period": {
    "start": "2025-01-19T12:00:00Z",
    "end": "2025-01-20T12:00:00Z",
    "hours": 24
  },
  "service_filter": null,
  "metrics": {
    "response_time": 150.5,
    "throughput": 1000,
    "error_rate": 0.01
  },
  "trends": {
    "response_time": "stable",
    "throughput": "increasing",
    "error_rate": "decreasing"
  },
  "alerts": [],
  "constitutional_compliance_score": 0.95
}
```

### Database Optimization

#### POST /dgm/optimize/database

Trigger database performance optimization.

**Response:**
```json
{
  "optimization_id": "456e7890-e89b-12d3-a456-426614174001",
  "status": "completed",
  "optimizations_applied": [
    "index_creation",
    "vacuum_tuning",
    "query_optimization"
  ],
  "performance_improvement": {
    "query_time_reduction": 25.0,
    "cache_hit_ratio_improvement": 5.0
  },
  "recommendations": [
    "Consider partitioning large tables",
    "Increase shared_buffers for better cache performance"
  ],
  "duration_seconds": 120.5,
  "constitutional_compliance": true
}
```

#### GET /dgm/optimize/database/report

Get database performance optimization report.

**Response:**
```json
{
  "generated_at": "2025-01-20T12:00:00Z",
  "performance_metrics": {
    "query_count": 1000,
    "slow_query_count": 5,
    "avg_query_time_ms": 150.0,
    "cache_hit_ratio": 0.85
  },
  "table_statistics": [
    {
      "tablename": "dgm_archive",
      "live_tuples": 10000,
      "dead_tuples": 500
    }
  ],
  "index_usage": [
    {
      "indexname": "idx_dgm_archive_status",
      "idx_scan": 1500,
      "idx_tup_read": 15000
    }
  ],
  "slow_queries": [
    {
      "query": "SELECT * FROM dgm.performance_metrics WHERE...",
      "mean_time": 250.0,
      "calls": 10
    }
  ],
  "recommendations": [
    "Add index on frequently queried columns",
    "Consider query optimization for slow queries"
  ]
}
```

### Cache Management

#### GET /dgm/cache/stats

Get cache performance statistics.

**Response:**
```json
{
  "memory_cache": {
    "size": 750,
    "max_size": 1000,
    "utilization": 75.0
  },
  "redis_cache": {
    "available": true,
    "memory_usage": "256MB",
    "connected_clients": 5
  },
  "metrics": {
    "hits": 8500,
    "misses": 1500,
    "hit_rate": 85.0,
    "sets": 2000,
    "deletes": 100
  },
  "constitutional_compliance": {
    "hash": "cdd01ef066bc6cf2",
    "validated": true
  }
}
```

#### POST /dgm/cache/clear

Clear cache entries.

**Parameters:**
- `pattern` (string, optional): Pattern to match cache keys

**Response:**
```json
{
  "success": true,
  "message": "Cleared 150 cache entries",
  "pattern": "dgm:metrics:*",
  "cleared_count": 150
}
```

### Constitutional Compliance

#### GET /constitutional/compliance/status

Get current constitutional compliance status.

**Response:**
```json
{
  "compliance_status": "validated",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "compliance_score": 0.95,
  "last_validation": "2025-01-20T12:00:00Z",
  "total_validations": 100,
  "violation_count": 2,
  "system_health": "healthy",
  "governance_active": true
}
```

#### POST /constitutional/compliance/validate

Validate content for constitutional compliance.

**Request:**
```json
{
  "content": "Proposed algorithm improvement",
  "context": {
    "service": "dgm",
    "type": "optimization"
  },
  "validation_type": "improvement",
  "strict_mode": true
}
```

**Response:**
```json
{
  "validation_id": "789e0123-e89b-12d3-a456-426614174002",
  "is_compliant": true,
  "compliance_score": 0.92,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "violations": [],
  "recommendations": [
    "Consider additional safety checks",
    "Add more comprehensive testing"
  ],
  "assessment_details": {
    "method": "automated",
    "confidence": 0.95,
    "principles_checked": 15
  },
  "validated_at": "2025-01-20T12:00:00Z"
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error information:

### Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-20T12:00:00Z",
  "path": "/api/v1/dgm/improve",
  "constitutional_compliance": false
}
```

### Common Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Standard endpoints**: 100 requests per minute
- **Optimization endpoints**: 10 requests per minute
- **Validation endpoints**: 50 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

## Versioning

The API uses URL versioning. The current version is `v1`. Future versions will be available at `/api/v2`, etc.

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8003/docs`
- **ReDoc**: `http://localhost:8003/redoc`
- **OpenAPI JSON**: `http://localhost:8003/openapi.json`
