# Evolutionary Computation Service API

## Service Overview

This service provides core functionality for the ACGS platform with constitutional compliance validation.

**Service**: Evolutionary Computation
**Port**: 8XXX
**Constitutional Hash**: `cdd01ef066bc6cf2`


**Service**: Evolutionary Computation Service
**Port**: 8006
**Base URL**: `http://localhost:8006/api/v1`
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

The Evolutionary Computation Service provides WINA (Weight Informed Neuron Activation) optimization, genetic algorithms, and evolutionary policy optimization for the ACGS system.

## Authentication

All endpoints require JWT authentication:

```http
Authorization: Bearer <jwt_token>
X-Constitutional-Hash: cdd01ef066bc6cf2
```

## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Test Coverage**: ≥ 80%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation

## Service Status

⚠️ **Current Status**: Service experiencing connection issues
**Last Known State**: Cannot connect to port 8006
**Impact**: WINA optimization and evolutionary algorithms unavailable

## Endpoints

### Health Check

```http
GET /health
```

**Expected Response** (when service is operational):
```json
{
  "status": "healthy",
  "service": "ec_service",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "wina_enabled": true,
  "optimization_engine": "active",
  "timestamp": "2025-07-05T12:00:00Z"
}
```

### WINA Optimization

```http
POST /wina/optimize
```

**Request**:
```json
{
  "neural_network": {
    "architecture": "transformer",
    "layers": 12,
    "parameters": 1000000
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "optimization_target": "governance_efficiency",
  "constraints": {
    "max_iterations": 1000,
    "convergence_threshold": 0.001
  }
}
```

**Expected Response**:
```json
{
  "success": true,
  "optimization_complete": true,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "results": {
    "efficiency_gain": 0.65,
    "gflops_reduction": 0.55,
    "latency_improvement": "2.3ms",
    "iterations": 847,
    "convergence_achieved": true
  }
}
```

### Genetic Algorithm Execution

```http
POST /genetic/evolve
```

**Request**:
```json
{
  "population_size": 100,
  "generations": 500,
  "fitness_function": "policy_effectiveness",
  "mutation_rate": 0.01,
  "crossover_rate": 0.8,
  "selection_method": "tournament"
,
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Expected Response**:
```json
{
  "success": true,
  "evolution_complete": true,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "results": {
    "best_fitness": 0.94,
    "generations_completed": 500,
    "convergence_generation": 387,
    "population_diversity": 0.72,
    "best_individual": "optimized_policy_genome"
  }
}
```

### Policy Evolution

```http
POST /evolution/policy
```

**Request**:
```json
{
  "base_policy": {
    "id": "policy_123",
    "parameters": {"param1": 0.5, "param2": 0.8,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
    "effectiveness_score": 0.75
  },
  "evolution_strategy": "differential_evolution",
  "target_improvement": 0.1
}
```

**Expected Response**:
```json
{
  "success": true,
  "policy_evolved": true,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "evolved_policy": {
    "id": "policy_123_evolved",
    "parameters": {"param1": 0.62, "param2": 0.85},
    "effectiveness_score": 0.87,
    "improvement": 0.12
  }
}
```

### Performance Optimization

```http
POST /optimization/performance
```

**Request**:
```json
{
  "system_metrics": {
    "current_latency": "5.2ms",
    "current_throughput": "95 RPS",
    "resource_usage": 0.78
  ,
  "constitutional_hash": "cdd01ef066bc6cf2"
},
  "optimization_goals": {
    "target_latency": "3.0ms",
    "target_throughput": "120 RPS",
    "max_resource_usage": 0.85
  }
}
```

**Expected Response**:
```json
{
  "success": true,
  "optimization_successful": true,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "optimized_configuration": {
    "predicted_latency": "2.8ms",
    "predicted_throughput": "125 RPS",
    "resource_efficiency": 0.82,
    "optimization_strategy": "wina_neural_pruning"
  }
}
```

## Performance Specifications

| Metric | Target | Status |
|--------|--------|--------|
| **Response Time** | P99 ≤5ms | ❌ Service Down |
| **Throughput** | ≥50 RPS | ❌ Service Down |
| **Availability** | ≥99.9% | ❌ Connection Failed |
| **WINA Efficiency** | ≥50% | 65% (when operational) |
| **Optimization Speed** | ≤10s | Fast (when operational) |

## WINA Algorithm Features

### Optimization Capabilities

- **Neural Network Pruning**: Remove redundant connections
- **Weight Quantization**: Reduce precision while maintaining accuracy
- **Activation Optimization**: Optimize neuron activation patterns
- **Architecture Search**: Find optimal network structures
- **Constitutional Compliance**: Ensure all optimizations maintain constitutional hash

### Supported Algorithms

- **Genetic Algorithms**: Population-based optimization
- **Differential Evolution**: Real-parameter optimization
- **Particle Swarm Optimization**: Swarm intelligence
- **Simulated Annealing**: Probabilistic optimization
- **Multi-Objective Optimization**: Pareto-optimal solutions

## Troubleshooting

### Current Issue: Service Connection Failed

**Symptoms**:
- Cannot connect to port 8006
- Connection refused errors
- Service appears to be down

**Troubleshooting Steps**:

1. **Check Service Status**:
   ```bash
   docker ps | grep ec_service
   netstat -tulpn | grep :8006
   ```

2. **Restart Service**:
   ```bash
   docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d ec_service
   ```

3. **Check Logs**:
   ```bash
   docker logs acgs_ec_service --tail 50
   ```

4. **Verify Dependencies**:
   ```bash
   # Check if other services are running
   curl http://localhost:8016/health  # Auth
   curl http://localhost:8001/health  # Constitutional AI
   ```

### Common Issues (when operational)

1. **Optimization Timeout**: Increase iteration limits
2. **Memory Issues**: Reduce population size or network complexity
3. **Convergence Problems**: Adjust mutation/crossover rates

## Integration Examples

### Python Client (when service is restored)

```python
import requests

# WINA optimization example
response = requests.post(
    "http://localhost:8006/api/v1/wina/optimize",
    headers={
        "Authorization": f"Bearer {jwt_token}",
        "X-Constitutional-Hash": "cdd01ef066bc6cf2"
    },
    json={
        "neural_network": {
            "architecture": "transformer",
            "layers": 12,
            "parameters": 1000000
        },
        "optimization_target": "governance_efficiency"
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Efficiency gain: {result['results']['efficiency_gain']}")
else:
    print("Service unavailable - check connection")
```

### Recovery Procedure

```bash
#!/bin/bash
# ec_service_recovery.sh

echo "Attempting to recover Evolutionary Computation Service..."

# Stop any existing instances
docker stop acgs_ec_service 2>/dev/null || true
docker rm acgs_ec_service 2>/dev/null || true

# Start fresh instance
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d ec_service

# Wait for startup
sleep 30

# Test connectivity
if curl -f -s "http://localhost:8006/health" > /dev/null; then
    echo "✅ EC Service recovered successfully"
else
    echo "❌ EC Service recovery failed - check logs"
    docker logs acgs_ec_service --tail 20
fi
```

## Related Documentation

- [API Documentation Index](index.md)
- [Policy Governance API](policy-governance.md)
- [Service Status](../operations/SERVICE_STATUS.md)
- [Performance Optimization Guide](../performance_benchmarking_plan.md)

---

**Status**: ❌ Service Down - Recovery in progress
**Priority**: HIGH - WINA optimization unavailable
<!-- Constitutional Hash: cdd01ef066bc6cf2 --> ✅

## Error Handling

Standard HTTP status codes are used with detailed error messages:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

All errors include constitutional compliance validation status.


## Monitoring

Service health and performance metrics:

- Health check endpoint: `/health`
- Metrics endpoint: `/metrics`
- Constitutional compliance status: `/compliance`
- Performance dashboard integration available
