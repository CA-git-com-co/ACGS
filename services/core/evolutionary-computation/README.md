# ACGS-1 Evolutionary Computation Service

## Overview

The Evolutionary Computation (EC) Service is an enterprise-grade WINA-optimized oversight and governance platform that provides advanced evolutionary computation algorithms, constitutional compliance verification, and intelligent performance optimization for the ACGS-PGP system.

**Service Port**: 8006
**Service Version**: 3.0.0 (Phase 3 Production)
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8006/health

## Core Features

### WINA-Optimized Oversight
- **Weighted Intelligence Network Architecture**: Advanced WINA optimization for resource allocation
- **Executive Council Oversight**: Comprehensive oversight coordination for governance systems
- **Constitutional Compliance**: Real-time constitutional principle verification for EC processes
- **Adaptive Learning**: Feedback mechanisms for continuous optimization improvement
- **Performance Monitoring**: Real-time monitoring with automated alerting

### Evolutionary Computation Algorithms
- **Genetic Algorithms**: Advanced genetic algorithm processing with constitutional constraints
- **Multi-Objective Optimization**: Pareto-optimal solutions for complex governance problems
- **Evolutionary Strategies**: Sophisticated evolution strategies for policy optimization
- **Constraint Handling**: Constitutional constraint satisfaction in optimization processes
- **Population Management**: Dynamic population sizing and diversity maintenance

### AlphaEvolve Integration
- **Constitutional Governance**: Integration with AlphaEvolve governance framework
- **Iterative Improvement**: Continuous optimization of governance processes
- **Strategy Selection**: WINA-informed strategy selection for optimal performance
- **Governance Recommendations**: AI-powered governance optimization recommendations
- **Performance Tuning**: Dynamic parameter adjustment for optimal system performance

### Enterprise Features
- **Advanced Analytics**: Comprehensive reporting and analytics capabilities
- **Real-Time Monitoring**: Performance dashboard with automated alerts
- **PGC Integration**: Seamless integration with Policy Governance Compiler
- **Scalability**: Enterprise-scale performance optimization
- **High Availability**: >99.9% availability with fault tolerance

## API Endpoints

### WINA Oversight Coordination
- `POST /api/v1/oversight/coordinate` - Coordinate WINA-optimized EC oversight operations
- `GET /api/v1/oversight/status/{oversight_id}` - Get oversight operation status
- `POST /api/v1/oversight/feedback` - Submit oversight feedback for learning
- `GET /api/v1/oversight/recommendations` - Get WINA-informed governance recommendations

### Advanced WINA Oversight (Task #4)
- `POST /api/v1/advanced-wina/optimization/run` - Run advanced optimization algorithms
- `GET /api/v1/advanced-wina/monitoring/real-time` - Real-time WINA monitoring
- `POST /api/v1/advanced-wina/alerts/configure` - Configure automated alerting
- `GET /api/v1/advanced-wina/analytics/performance` - Advanced performance analytics
- `GET /api/v1/advanced-wina/enterprise/configuration` - Enterprise configuration management

### AlphaEvolve Integration
- `POST /api/v1/alphaevolve/optimize` - Optimize EC algorithms with constitutional constraints
- `POST /api/v1/alphaevolve/governance` - AlphaEvolve governance optimization
- `GET /api/v1/alphaevolve/strategies` - Available optimization strategies
- `POST /api/v1/alphaevolve/constitutional` - Constitutional compliance optimization

### WINA Performance Monitoring
- `GET /api/v1/wina/performance/metrics` - WINA performance metrics and insights
- `GET /api/v1/wina/performance/optimization` - Performance optimization recommendations
- `POST /api/v1/wina/performance/tune` - Dynamic performance tuning
- `GET /api/v1/wina/performance/dashboard` - Real-time performance dashboard

### Evolutionary Computation
- `POST /api/v1/evolution/genetic-algorithm` - Run genetic algorithm optimization
- `POST /api/v1/evolution/multi-objective` - Multi-objective optimization
- `POST /api/v1/evolution/constraint-satisfaction` - Constitutional constraint satisfaction
- `GET /api/v1/evolution/population/status` - Population management status

### Reporting & Analytics
- `GET /api/v1/reporting/oversight` - Comprehensive oversight reports
- `GET /api/v1/reporting/performance` - Performance analysis reports
- `GET /api/v1/reporting/constitutional` - Constitutional compliance reports
- `POST /api/v1/reporting/custom` - Generate custom analytics reports

### Monitoring & Alerting
- `GET /api/v1/monitoring/system` - System performance monitoring
- `GET /api/v1/monitoring/alerts` - Active alerts and notifications
- `POST /api/v1/monitoring/configure` - Configure monitoring parameters
- `GET /api/v1/monitoring/dashboard` - Real-time monitoring dashboard

### System Management
- `GET /health` - Service health with component status
- `GET /api/v1/status` - Detailed service status and capabilities
- `GET /metrics` - Prometheus metrics for monitoring
- `GET /` - Service information and WINA capabilities

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_evolutionary_computation
REDIS_URL=redis://localhost:6379/6

# Service Configuration
SERVICE_NAME=ec-service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8006
APP_ENV=production
LOG_LEVEL=INFO

# WINA Configuration
ENABLE_WINA=true
WINA_OPTIMIZATION_LEVEL=advanced
WINA_MONITORING_LEVEL=comprehensive
WINA_PERFORMANCE_TARGET=high
WINA_LEARNING_RATE=0.01

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.8
ENABLE_CONSTITUTIONAL_VERIFICATION=true
STRICT_CONSTITUTIONAL_MODE=true

# Evolutionary Computation Configuration
POPULATION_SIZE=100
MUTATION_RATE=0.1
CROSSOVER_RATE=0.8
SELECTION_PRESSURE=2.0
MAX_GENERATIONS=1000
CONVERGENCE_THRESHOLD=0.001

# AlphaEvolve Configuration
ENABLE_ALPHAEVOLVE_OPTIMIZATION=true
ALPHAEVOLVE_STRATEGY=multi_objective
OPTIMIZATION_ALGORITHMS=genetic,evolutionary_strategy,particle_swarm
GOVERNANCE_OPTIMIZATION_ENABLED=true

# Performance Configuration
TARGET_RESPONSE_TIME_MS=300
AVAILABILITY_TARGET=0.999
MAX_CONCURRENT_OPTIMIZATIONS=50
OPTIMIZATION_TIMEOUT_SECONDS=3600

# Service Integration
AC_SERVICE_URL=http://localhost:8001
PGC_SERVICE_URL=http://localhost:8005
GS_SERVICE_URL=http://localhost:8004
INTEGRITY_SERVICE_URL=http://localhost:8002

# Advanced Features
ENABLE_REAL_TIME_MONITORING=true
ENABLE_AUTOMATED_ALERTING=true
ENABLE_PGC_INTEGRATION=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_ENTERPRISE_OPTIMIZATION=true
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
- NumPy, SciPy for mathematical computations
- WINA optimization libraries (if available)

### Local Development

```bash
# 1. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# Alternative: Traditional pip
pip install -r requirements.txt

# 2. Install scientific computing libraries
pip install numpy scipy matplotlib scikit-learn

# 3. Setup database
createdb acgs_evolutionary_computation
alembic upgrade head

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Start service
uv run uvicorn app.main:app --reload --port 8006
```

### Production Deployment

```bash
# Using Docker
docker build -t acgs-ec-service .
docker run -p 8006:8006 --env-file .env acgs-ec-service

# Using systemd
sudo cp ec-service.service /etc/systemd/system/
sudo systemctl enable ec-service
sudo systemctl start ec-service
```

## Testing

### Unit Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html
```

### Integration Tests
```bash
# Test WINA integration
uv run pytest tests/test_wina_integration.py -v

# Test evolutionary algorithms
uv run pytest tests/test_evolutionary_algorithms.py -v

# Test constitutional compliance
uv run pytest tests/test_constitutional_compliance.py -v
```

### Performance Tests
```bash
# Test optimization performance
python scripts/test_optimization_performance.py

# Test WINA oversight performance
python scripts/test_wina_oversight.py

# Load testing
python scripts/test_ec_load.py --concurrent 25
```

## Usage Examples

### WINA-Optimized Oversight Coordination

```python
import httpx

async def coordinate_wina_oversight():
    async with httpx.AsyncClient() as client:
        # Coordinate WINA-optimized EC oversight operation
        response = await client.post(
            "http://localhost:8006/api/v1/oversight/coordinate",
            json={
                "target_system": "governance_optimization",
                "oversight_type": "constitutional_compliance",
                "priority": "high",
                "context": {
                    "system_state": "active_optimization",
                    "performance_metrics": {
                        "throughput": 150.0,
                        "latency": 45.0,
                        "error_rate": 0.01
                    },
                    "constitutional_principles": [
                        "democratic_process",
                        "transparency",
                        "accountability"
                    ]
                },
                "strategy": "adaptive_wina_optimization",
                "enable_learning": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "oversight_id": result["oversight_id"],
            "wina_strategy": result["wina_strategy"],
            "constitutional_compliance": result["constitutional_compliance"],
            "optimization_recommendations": result["optimization_recommendations"]
        }
```

### Advanced WINA Optimization

```python
async def run_advanced_wina_optimization():
    async with httpx.AsyncClient() as client:
        # Run advanced optimization algorithms for resource allocation
        response = await client.post(
            "http://localhost:8006/api/v1/advanced-wina/optimization/run",
            json={
                "algorithm_type": "resource_allocation",
                "optimization_target": "governance_efficiency",
                "constraints": {
                    "constitutional_compliance": 0.95,
                    "performance_threshold": 0.90,
                    "resource_limits": {
                        "cpu_max": 0.8,
                        "memory_max": 0.7
                    }
                },
                "optimization_parameters": {
                    "population_size": 100,
                    "max_generations": 500,
                    "mutation_rate": 0.1,
                    "crossover_rate": 0.8
                },
                "enable_pgc_integration": True,
                "enable_real_time_monitoring": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "optimization_id": result["optimization_id"],
            "algorithm_performance": result["algorithm_performance"],
            "resource_allocation": result["resource_allocation"],
            "constitutional_compliance": result["constitutional_compliance"]
        }
```

### AlphaEvolve Constitutional Optimization

```python
async def alphaevolve_constitutional_optimization():
    async with httpx.AsyncClient() as client:
        # Optimize EC algorithms with constitutional constraints
        response = await client.post(
            "http://localhost:8006/api/v1/alphaevolve/optimize",
            json={
                "algorithm_type": "genetic_algorithm",
                "optimization_goal": "constitutional_compliance_maximization",
                "constitutional_constraints": [
                    {
                        "principle": "democratic_process",
                        "weight": 0.9,
                        "threshold": 0.85
                    },
                    {
                        "principle": "transparency",
                        "weight": 0.8,
                        "threshold": 0.80
                    }
                ],
                "wina_optimization": {
                    "enable_wina_insights": True,
                    "optimization_level": "advanced",
                    "learning_rate": 0.01
                },
                "performance_targets": {
                    "convergence_time": 300,
                    "solution_quality": 0.95,
                    "constitutional_compliance": 0.90
                }
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "optimization_id": result["optimization_id"],
            "optimized_parameters": result["optimized_parameters"],
            "constitutional_compliance": result["constitutional_compliance"],
            "wina_insights": result["wina_insights"]
        }
```

### Multi-Objective Evolutionary Optimization

```python
async def multi_objective_optimization():
    async with httpx.AsyncClient() as client:
        # Run multi-objective optimization for governance problems
        response = await client.post(
            "http://localhost:8006/api/v1/evolution/multi-objective",
            json={
                "objectives": [
                    {
                        "name": "constitutional_compliance",
                        "type": "maximize",
                        "weight": 0.4
                    },
                    {
                        "name": "system_efficiency",
                        "type": "maximize",
                        "weight": 0.3
                    },
                    {
                        "name": "resource_utilization",
                        "type": "minimize",
                        "weight": 0.3
                    }
                ],
                "constraints": [
                    {
                        "type": "constitutional_hash_validation",
                        "value": "cdd01ef066bc6cf2"
                    },
                    {
                        "type": "performance_threshold",
                        "value": 0.85
                    }
                ],
                "algorithm_parameters": {
                    "population_size": 200,
                    "max_generations": 1000,
                    "selection_method": "nsga2",
                    "mutation_rate": 0.1
                },
                "enable_constitutional_verification": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "optimization_id": result["optimization_id"],
            "pareto_solutions": result["pareto_solutions"],
            "best_solution": result["best_solution"],
            "convergence_metrics": result["convergence_metrics"]
        }
```

### Real-Time Performance Monitoring

```python
async def monitor_wina_performance():
    async with httpx.AsyncClient() as client:
        # Get real-time WINA performance metrics
        response = await client.get(
            "http://localhost:8006/api/v1/wina/performance/metrics",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "system_performance": result["system_performance"],
            "wina_optimization_status": result["wina_optimization_status"],
            "constitutional_compliance": result["constitutional_compliance"],
            "resource_utilization": result["resource_utilization"],
            "performance_trends": result["performance_trends"]
        }
```

## WINA Architecture Integration

### WINA Core Components
The service integrates advanced WINA (Weighted Intelligence Network Architecture) components:

```python
# WINA configuration example
WINA_CONFIG = {
    "optimization_level": "advanced",
    "monitoring_level": "comprehensive",
    "learning_rate": 0.01,
    "performance_targets": {
        "max_response_time_ms": 100,
        "min_throughput_ops_per_sec": 150,
        "max_error_rate_percent": 2.0,
        "min_compliance_score": 0.90
    }
}

# Constitutional WINA support
constitutional_wina = ConstitutionalWINASupport(
    wina_config=WINA_CONFIG,
    constitutional_hash="cdd01ef066bc6cf2"
)
```

### WINA Performance Optimization
```python
# WINA-optimized resource allocation
async def optimize_resource_allocation():
    optimization_result = await wina_coordinator.optimize_resource_allocation(
        target_efficiency=0.95,
        constitutional_constraints=constitutional_principles,
        performance_targets=performance_targets
    )

    return optimization_result
```

### Constitutional Hash Validation
```python
# Constitutional hash validation in EC processes
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def validate_constitutional_ec_process(ec_result):
    return (
        ec_result.get("constitutional_hash") == CONSTITUTIONAL_HASH and
        ec_result.get("constitutional_compliance", {}).get("compliant", False) and
        ec_result.get("constitutional_compliance", {}).get("score", 0) >= 0.8
    )
```

## Monitoring & Observability

### Health Checks
```bash
# Service health with component status
curl http://localhost:8006/health

# Expected response includes WINA status
{
  "status": "healthy",
  "service": "ec_service_production",
  "version": "3.0.0",
  "components": {
    "evolution_engine": "operational",
    "wina_coordinator": "operational",
    "constitutional_verifier": "operational",
    "performance_monitor": "operational"
  },
  "performance_metrics": {
    "target_response_time": "<300ms",
    "availability_target": ">99.9%"
  }
}
```

### Performance Metrics
```bash
# Get WINA performance metrics
curl http://localhost:8006/api/v1/wina/performance/metrics

# Advanced analytics
curl http://localhost:8006/api/v1/advanced-wina/analytics/performance

# Real-time monitoring
curl http://localhost:8006/api/v1/advanced-wina/monitoring/real-time
```

### Real-time Monitoring
```bash
# Monitor evolutionary computation operations
curl http://localhost:8006/api/v1/monitoring/system

# WINA oversight status
curl http://localhost:8006/api/v1/oversight/status

# Constitutional compliance monitoring
curl http://localhost:8006/api/v1/monitoring/constitutional
```

## Troubleshooting

### Common Issues

#### WINA Components Not Available
```bash
# Check WINA availability
python -c "
try:
    from app.core.wina_oversight_coordinator import WINAECOversightCoordinator
    print('WINA components: Available')
except ImportError:
    print('WINA components: Not available - using fallback mode')
"

# Enable WINA fallback mode
export ENABLE_WINA=false
```

#### Evolutionary Algorithm Convergence Issues
```bash
# Check algorithm parameters
curl http://localhost:8006/api/v1/evolution/population/status

# Adjust convergence parameters
export CONVERGENCE_THRESHOLD=0.01
export MAX_GENERATIONS=2000

# Monitor convergence progress
curl http://localhost:8006/api/v1/monitoring/convergence
```

#### Constitutional Hash Mismatch
```bash
# Verify constitutional hash
curl http://localhost:8006/api/v1/constitutional/status | jq '.constitutional_hash'

# Expected: "cdd01ef066bc6cf2"
# Reset if corrupted
python scripts/reset_constitutional_state.py --service ec
```

#### Performance Optimization Issues
```bash
# Check current performance metrics
curl http://localhost:8006/api/v1/wina/performance/metrics | jq '.system_performance'

# Enable performance tuning
curl -X POST http://localhost:8006/api/v1/wina/performance/tune \
  -H "Content-Type: application/json" \
  -d '{"optimization_level": "maximum"}'

# Monitor optimization progress
curl http://localhost:8006/api/v1/monitoring/optimization
```

#### PGC Integration Failures
```bash
# Check PGC service connectivity
curl http://localhost:8005/health

# Verify PGC integration status
curl http://localhost:8006/api/v1/advanced-wina/enterprise/configuration | jq '.monitoring_status.pgc_integration'

# Re-enable PGC integration
export ENABLE_PGC_INTEGRATION=true
```

### Performance Optimization

#### Evolutionary Algorithm Optimization
```python
# Optimize genetic algorithm parameters
optimal_params = {
    "population_size": 200,  # Larger population for better diversity
    "mutation_rate": 0.05,   # Lower mutation rate for fine-tuning
    "crossover_rate": 0.9,   # Higher crossover for better exploration
    "selection_pressure": 1.5,  # Moderate selection pressure
    "elitism_rate": 0.1      # Preserve best solutions
}
```

#### Database Optimization
```sql
-- Optimize EC queries
CREATE INDEX idx_ec_optimization_timestamp ON ec_optimizations(created_at);
CREATE INDEX idx_ec_optimization_status ON ec_optimizations(status);
CREATE INDEX idx_ec_optimization_type ON ec_optimizations(algorithm_type);
```

#### WINA Performance Tuning
```python
# WINA performance optimization
wina_config = {
    "optimization_level": "maximum",
    "cache_size": 1024,  # MB
    "parallel_processing": True,
    "gpu_acceleration": True,
    "memory_optimization": True
}
```

## Security Considerations

### Evolutionary Computation Security
- **Algorithm Integrity**: Cryptographic verification of algorithm parameters
- **Constitutional Validation**: Continuous constitutional hash verification
- **Access Control**: Role-based access for optimization operations
- **Audit Trail**: Comprehensive logging of all EC operations

### WINA Security
- **Secure Optimization**: Protected optimization parameter storage
- **Performance Monitoring**: Secure performance data collection
- **Constitutional Compliance**: Mandatory constitutional verification
- **Resource Protection**: Secure resource allocation and monitoring

## Contributing

1. Follow ACGS-1 coding standards with evolutionary computation best practices
2. Ensure >90% test coverage for optimization algorithms
3. Update API documentation for new EC endpoints
4. Test WINA integration thoroughly with edge cases
5. Validate constitutional compliance for all changes

## Support

- **Documentation**: [Evolutionary Computation API](../../../docs/api/evolutionary_computation_service_api.md)
- **Health Check**: http://localhost:8006/health
- **Interactive API Docs**: http://localhost:8006/docs
- **Logs**: `/logs/ec_service.log`
- **Configuration**: `services/core/evolutionary-computation/.env`
- **WINA Documentation**: [WINA Architecture Guide](../../../docs/architecture/wina_architecture.md)

### Running Service

```bash
uvicorn main:app --reload
```

### Running Tests

_No dedicated tests for this service_
