# ACGS-1 Evolutionary Computation Service

**Status**: 🧪 **Prototype**  
**Last Updated**: 2025-06-27

## Overview

The Evolutionary Computation (EC) Service is an enterprise-grade WINA-optimized oversight and governance platform that provides advanced evolutionary computation algorithms, constitutional compliance verification, and intelligent performance optimization for the ACGS-PGP system. It implements the WINA (Weighted Intelligence Network Architecture) framework for autonomous governance evolution.

**Service Port**: 8006
**Service Version**: 3.0.0 (Phase 3 Production)
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8006/health

## Core Features

### WINA Framework Integration

- **WINA-Optimized Oversight**: Advanced WINA optimization for resource allocation and governance
- **Weighted Intelligence Networks**: Multi-agent coordination with weighted decision making
- **SVD Transformation**: Singular Value Decomposition for governance optimization
- **Autonomous Evolution**: Self-improving governance algorithms
- **Performance Optimization**: Intelligent resource allocation and system optimization

### Evolutionary Algorithms

- **Genetic Algorithms**: Policy evolution through genetic programming
- **Multi-Objective Optimization**: Pareto-optimal governance solutions
- **Swarm Intelligence**: Collective intelligence for governance decisions
- **Neural Evolution**: Evolutionary neural networks for policy adaptation
- **Hybrid Algorithms**: Combined evolutionary and traditional optimization

### AlphaEvolve Integration

- **AlphaEvolve Framework**: Integration with advanced governance evolution
- **Continuous Optimization**: Real-time governance parameter tuning
- **Performance Monitoring**: Advanced analytics and monitoring
- **Adaptive Learning**: Machine learning-driven governance improvement
- **Constitutional Evolution**: Constitutional principle evolution within bounds

### DGM Safety Patterns

- **Sandbox Execution**: Isolated evolutionary computation environment
- **Human Review Interface**: Critical evolution decision review workflows
- **Gradual Rollout**: Phased evolution deployment with validation gates
- **Emergency Shutdown**: <30min RTO emergency procedures
- **Constitutional Compliance Monitoring**: Real-time compliance tracking

## API Endpoints

### WINA Oversight

- `POST /api/v1/wina/optimize` - Trigger WINA optimization
- `GET /api/v1/wina/status` - WINA system status
- `POST /api/v1/wina/configure` - Configure WINA parameters
- `GET /api/v1/wina/performance` - WINA performance metrics

### Evolutionary Computation

- `POST /api/v1/evolution/genetic` - Run genetic algorithm
- `POST /api/v1/evolution/multi-objective` - Multi-objective optimization
- `POST /api/v1/evolution/swarm` - Swarm intelligence optimization
- `GET /api/v1/evolution/history` - Evolution history

### AlphaEvolve Integration

- `POST /api/v1/alphaevolve/evolve` - Trigger AlphaEvolve process
- `GET /api/v1/alphaevolve/status` - AlphaEvolve status
- `POST /api/v1/alphaevolve/configure` - Configure evolution parameters
- `GET /api/v1/alphaevolve/results` - Evolution results

### Performance Monitoring

- `GET /api/v1/performance/metrics` - Performance metrics
- `GET /api/v1/performance/analytics` - Advanced analytics
- `POST /api/v1/performance/optimize` - Trigger optimization
- `GET /api/v1/performance/reports` - Performance reports

### Constitutional Compliance

- `POST /api/v1/constitutional/validate` - Validate constitutional compliance
- `GET /api/v1/constitutional/violations` - List constitutional violations
- `POST /api/v1/constitutional/emergency-shutdown` - Emergency shutdown
- `GET /api/v1/constitutional/audit-log` - Constitutional audit trail

### System Management

- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics
- `GET /api/v1/status` - Detailed service status
- `POST /api/v1/system/restart` - Restart system components

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_ec
REDIS_URL=redis://localhost:6379/6

# Service Configuration
SERVICE_NAME=evolutionary-computation-service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8006
APP_ENV=production
LOG_LEVEL=INFO

# WINA Configuration
WINA_ENABLED=true
WINA_OPTIMIZATION_INTERVAL=3600
WINA_SVD_THRESHOLD=0.95
WINA_WEIGHT_DECAY=0.01
WINA_LEARNING_RATE=0.001

# Evolutionary Algorithm Configuration
GENETIC_POPULATION_SIZE=100
GENETIC_MUTATION_RATE=0.1
GENETIC_CROSSOVER_RATE=0.8
GENETIC_GENERATIONS=1000
MULTI_OBJECTIVE_ALGORITHMS=NSGA2,SPEA2

# AlphaEvolve Configuration
ALPHAEVOLVE_ENABLED=true
ALPHAEVOLVE_LEARNING_RATE=0.01
ALPHAEVOLVE_EXPLORATION_RATE=0.1
ALPHAEVOLVE_MEMORY_SIZE=10000

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
AC_SERVICE_URL=http://localhost:8001
GS_SERVICE_URL=http://localhost:8004
PGC_SERVICE_URL=http://localhost:8005

# Performance Configuration
MAX_CONCURRENT_EVOLUTIONS=3
EVOLUTION_TIMEOUT_SECONDS=1800
CACHE_TTL_SECONDS=7200
ENABLE_PARALLEL_PROCESSING=true

# DGM Safety Configuration
SANDBOX_ENABLED=true
HUMAN_REVIEW_REQUIRED=true
EMERGENCY_SHUTDOWN_ENABLED=true
RTO_TARGET_MINUTES=30
```

### Resource Limits

```yaml
resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 1Gi
```

## Installation & Deployment

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- NumPy/SciPy for numerical computations
- TensorFlow/PyTorch for neural evolution

### Local Development

```bash
# 1. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# 2. Install scientific computing libraries
pip install numpy scipy scikit-learn tensorflow

# 3. Setup database
createdb acgs_ec
alembic upgrade head

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Start service
uv run uvicorn main:app --reload --port 8006
```

### Production Deployment

````bash
# Using Docker
docker build -t acgs-ec-service .
docker run -p 8006:8006 --env-file .env acgs-ec-service

# Using Docker Compose
docker-compose up -d ec-service

# Health check
curl http://localhost:8006/health

## Usage Examples

### WINA Optimization

```python
import httpx

# Trigger WINA optimization
async def optimize_wina():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8006/api/v1/wina/optimize",
            json={
                "optimization_target": "governance_efficiency",
                "constraints": {
                    "constitutional_compliance": 0.95,
                    "resource_utilization": 0.8
                },
                "svd_threshold": 0.95
            }
        )
        return response.json()
````

### Genetic Algorithm Evolution

```bash
# Run genetic algorithm for policy evolution
curl -X POST http://localhost:8006/api/v1/evolution/genetic \
  -H "Content-Type: application/json" \
  -d '{
    "population_size": 100,
    "generations": 500,
    "mutation_rate": 0.1,
    "crossover_rate": 0.8,
    "fitness_function": "constitutional_compliance"
  }'
```

### AlphaEvolve Process

```python
# Trigger AlphaEvolve governance evolution
alphaevolve_config = {
    "learning_rate": 0.01,
    "exploration_rate": 0.1,
    "evolution_target": "policy_optimization",
    "constitutional_constraints": True
}

response = await client.post(
    "http://localhost:8006/api/v1/alphaevolve/evolve",
    json=alphaevolve_config
)
```

### Multi-Objective Optimization

```bash
# Multi-objective optimization for governance
curl -X POST http://localhost:8006/api/v1/evolution/multi-objective \
  -H "Content-Type: application/json" \
  -d '{
    "objectives": ["efficiency", "fairness", "transparency"],
    "algorithm": "NSGA2",
    "population_size": 200,
    "generations": 1000
  }'
```

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8006/health

# Detailed status with WINA metrics
curl http://localhost:8006/api/v1/status

# WINA performance metrics
curl http://localhost:8006/api/v1/wina/performance
```

### Prometheus Metrics

Key metrics exposed:

- `ec_evolution_requests_total` - Total evolution requests
- `ec_evolution_duration_seconds` - Evolution processing time
- `ec_wina_optimization_score` - WINA optimization scores
- `ec_constitutional_compliance_score` - Constitutional compliance scores
- `ec_active_evolutions` - Currently active evolutions
- `ec_alphaevolve_performance` - AlphaEvolve performance metrics

### Grafana Dashboard

Import the EC Service dashboard:

```bash
# Dashboard location
infrastructure/monitoring/grafana/dashboards/services/ec-service-dashboard.json
```

### Alerting Rules

```yaml
# Critical alerts
- alert: ECServiceDown
  expr: up{job="ec-service"} == 0
  for: 1m

- alert: HighEvolutionLatency
  expr: ec_evolution_duration_seconds > 300
  for: 5m

- alert: WINAOptimizationFailure
  expr: ec_wina_optimization_score < 0.8
  for: 3m

- alert: ConstitutionalComplianceBelow95
  expr: ec_constitutional_compliance_score < 0.95
  for: 2m
```

## Troubleshooting

### Common Issues

#### WINA Optimization Failures

```bash
# Check WINA status
curl http://localhost:8006/api/v1/wina/status

# Check SVD computation
curl http://localhost:8006/api/v1/wina/performance | jq '.svd_metrics'

# Reset WINA state
python scripts/reset_wina_state.py

# Restart with fresh WINA configuration
sudo systemctl restart ec-service
```

#### High Evolution Latency

```bash
# Check current evolution performance
curl http://localhost:8006/api/v1/performance/metrics | jq '.evolution_metrics'

# Reduce population size temporarily
export GENETIC_POPULATION_SIZE=50

# Enable parallel processing
export ENABLE_PARALLEL_PROCESSING=true

# Restart service
sudo systemctl restart ec-service
```

#### AlphaEvolve Integration Issues

```bash
# Check AlphaEvolve status
curl http://localhost:8006/api/v1/alphaevolve/status

# Test AlphaEvolve configuration
python scripts/test_alphaevolve.py

# Reset AlphaEvolve memory
curl -X POST http://localhost:8006/api/v1/alphaevolve/reset
```

#### Constitutional Hash Mismatch

```bash
# Verify constitutional hash
curl http://localhost:8006/api/v1/constitutional/validate | jq '.constitutional_hash'

# Expected: "cdd01ef066bc6cf2"
# Reset if corrupted
python scripts/reset_constitutional_state.py --service ec
```

### Emergency Procedures

#### Emergency Shutdown

```bash
# Immediate shutdown (< 30min RTO)
curl -X POST http://localhost:8006/api/v1/constitutional/emergency-shutdown \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Verify shutdown
curl http://localhost:8006/health
```

#### Rollback Procedure

```bash
# Rollback to previous version
kubectl rollout undo deployment/ec-service

# Verify rollback
kubectl get pods -l app=ec-service
```

## Testing

### Unit Tests

```bash
# Run unit tests
pytest tests/unit/ -v --cov=app

# Test WINA integration
pytest tests/unit/test_wina.py -v

# Test evolutionary algorithms
pytest tests/unit/test_evolution.py -v
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/ -v

# Test AlphaEvolve integration
pytest tests/integration/test_alphaevolve.py -v

# Test multi-service integration
pytest tests/integration/test_service_integration.py -v
```

### Performance Tests

```bash
# Load testing
pytest tests/performance/test_evolution_load.py -v

# Stress testing with multiple evolutions
python tests/performance/stress_test_evolution.py --concurrent=5
```

## Security

### Authentication

- **JWT Integration**: Seamless integration with ACGS-1 auth service
- **Service-to-Service**: Mutual TLS authentication
- **Evolution Security**: Secure evolutionary computation sandboxing

### Data Protection

- **Encryption at Rest**: AES-256 encryption for evolution data
- **Encryption in Transit**: TLS 1.3 for all communications
- **Key Management**: Secure key rotation and storage

### Evolution Security

- **Sandbox Execution**: Isolated evolutionary computation
- **Constitutional Bounds**: Evolution within constitutional limits
- **Human Oversight**: Critical evolution decision review

## Contributing

1. Follow ACGS-1 coding standards
2. Ensure >90% test coverage for new features
3. Update API documentation for endpoint changes
4. Test WINA integration thoroughly
5. Validate constitutional compliance integration
6. Test evolutionary algorithms extensively

## Support

- **Documentation**: [EC Service API](../../../docs/api/evolutionary_computation_service_api.md)
- **Health Check**: http://localhost:8006/health
- **Interactive API Docs**: http://localhost:8006/docs
- **Logs**: `/logs/ec_service.log`
- **Configuration**: `services/core/evolutionary-computation/.env`

```

```
