# Ec Service API Documentation

**Service:** Ec Service  
**Port:** 8006  
**Base URL:** `http://localhost:8006`  
**Status:** ✅ Operational  
**Last Updated:** 2025-06-15

// requires: Complete API documentation with examples and error handling
// ensures: Comprehensive API guidance for developers
// sha256: ec593fdf614f95ab

## 🎯 Service Overview

Evolutionary computation service for governance optimization.

## 📋 API Endpoints

### Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "ec_service",
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
  "timestamp": "2025-06-15T11:09:03.406201"
}
```

### WINA Optimization Endpoints

#### WINA Performance Monitoring
```http
GET /api/v1/wina/performance
```

**Description:** Get current WINA optimization performance metrics

**Response (200 OK):**
```json
{
  "wina_metrics": {
    "optimization_score": 0.87,
    "performance_improvement": 0.23,
    "constitutional_compliance": 0.94,
    "last_optimization": "2025-06-20T10:30:00Z"
  },
  "system_health": {
    "cpu_usage": 0.45,
    "memory_usage": 0.62,
    "active_optimizations": 3
  }
}
```

#### WINA Configuration Management
```http
POST /api/v1/wina/configure
```

**Description:** Configure WINA optimization parameters

**Request Body:**
```json
{
  "optimization_level": "high",
  "constitutional_weight": 0.8,
  "performance_weight": 0.2,
  "max_iterations": 100,
  "convergence_threshold": 0.01
}
```

**Response (200 OK):**
```json
{
  "status": "configured",
  "configuration_id": "wina_config_123",
  "applied_at": "2025-06-20T10:30:00Z"
}
```

#### Evolutionary Computation Endpoints

#### Start Optimization Process
```http
POST /api/v1/oversight/start
```

**Description:** Initiate evolutionary oversight for governance optimization

**Request Body:**
```json
{
  "target_policy": "policy_id_123",
  "optimization_goals": ["performance", "compliance", "efficiency"],
  "constraints": {
    "max_duration": 3600,
    "constitutional_compliance_min": 0.8
  }
}
```

#### AlphaEvolve Integration
```http
POST /api/v1/alphaevolve/execute
```

**Description:** Execute AlphaEvolve iterative improvement process

**Request Body:**
```json
{
  "model_id": "governance_model_v2",
  "evolution_parameters": {
    "population_size": 50,
    "mutation_rate": 0.1,
    "crossover_rate": 0.8,
    "selection_method": "tournament"
  }
}
```

#### Monitoring and Reporting
```http
GET /api/v1/reporting/execution/{execution_id}
```

**Description:** Get detailed execution report for optimization process

**Response (200 OK):**
```json
{
  "execution_id": "exec_123",
  "status": "completed",
  "results": {
    "optimization_improvement": 0.15,
    "constitutional_compliance": 0.92,
    "performance_metrics": {
      "response_time_improvement": 0.08,
      "throughput_increase": 0.12
    }
  },
  "duration": 1847,
  "iterations_completed": 87
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
    "timestamp": "2025-06-15T11:09:03.406202",
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
**Interactive Docs:** `http://localhost:8006/docs`
