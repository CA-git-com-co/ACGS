# ACGS End-to-End Test Framework

A comprehensive end-to-end testing framework for the Autonomous Coding Governance System (ACGS) that validates production readiness and maintains established performance targets.

## 🎯 Overview

This framework provides comprehensive testing capabilities for the ACGS system, including:

- **Constitutional AI policy validation** (hash: `cdd01ef066bc6cf2`)
- **HITL decision processing** with sub-5ms P99 latency validation
- **Multi-agent coordination** with blackboard architecture
- **Policy governance** with WINA optimization (O(1) lookups)
- **Cache performance validation** (>85% hit rate target)
- **Infrastructure component validation**
- **Security compliance testing**
- **Performance benchmarking and regression detection**

## 🏗️ Architecture

### Framework Components

```
tests/e2e/
├── framework/           # Core framework components
│   ├── core.py         # Main framework orchestration
│   ├── config.py       # Configuration management
│   ├── base.py         # Base test classes
│   ├── runner.py       # Test execution engine
│   ├── reporter.py     # Reporting and analysis
│   ├── mocks.py        # Mock service implementations
│   └── utils.py        # Utilities and helpers
├── tests/              # Test implementations
│   ├── health.py       # Health and connectivity tests
│   ├── constitutional.py # Constitutional compliance tests
│   ├── hitl.py         # Human-in-the-loop tests
│   ├── governance.py   # Multi-agent governance tests
│   ├── performance.py  # Performance and load tests
│   ├── infrastructure.py # Infrastructure tests
│   └── security.py     # Security and compliance tests
├── docker/             # Docker configuration
│   ├── docker-compose.e2e.yml
│   ├── Dockerfile.mock-services
│   ├── Dockerfile.test-runner
│   └── init-scripts/
└── suites/             # Test suite definitions
```

### Testing Modes

1. **Online Mode**: Tests against live infrastructure (PostgreSQL/Redis/Auth services)
2. **Offline Mode**: Uses mocked services and in-memory databases for CI/CD
3. **Hybrid Mode**: Mix of live and mocked components for specific test scenarios

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+ (for online mode)
- Redis 7+ (for online mode)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov
   ```

2. **Set environment variables:**
   ```bash
   export E2E_TEST_MODE=offline
   export CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
   export E2E_PARALLEL_WORKERS=4
   ```

### Running Tests

#### Quick Smoke Tests
```bash
# Run basic validation tests
python -m pytest tests/e2e/tests/health.py -m smoke -v
```

#### Full Test Suite (Docker)
```bash
# Run complete E2E test suite in Docker
cd tests/e2e/docker
docker-compose -f docker-compose.e2e.yml up --build
```

#### Specific Test Categories
```bash
# Constitutional compliance tests
python -m pytest tests/e2e/tests/constitutional.py -v

# Performance tests
python -m pytest tests/e2e/tests/performance.py -v

# Security tests
python -m pytest tests/e2e/tests/security.py -v
```

#### Using the Framework API
```python
import asyncio
from tests.e2e.framework.runner import run_quick_validation

# Quick validation
async def main():
    success = await run_quick_validation()
    print(f"Validation {'PASSED' if success else 'FAILED'}")

asyncio.run(main())
```

## 📊 Performance Targets

The framework validates against these established performance targets:

| Metric | Target | Validation |
|--------|--------|------------|
| P99 Latency | <5ms | All service endpoints |
| Cache Hit Rate | >85% | Policy governance service |
| Throughput | >100 RPS | Load testing scenarios |
| Success Rate | >95% | All test operations |
| Test Coverage | >80% | Framework and tests |
| Constitutional Compliance | 100% | All governance operations |

## 🔧 Configuration

### Environment Variables

```bash
# Core configuration
E2E_TEST_MODE=offline|online|hybrid
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
E2E_PARALLEL_WORKERS=4
E2E_TEST_TIMEOUT=1800

# Infrastructure (online/hybrid mode)
POSTGRES_HOST=localhost
POSTGRES_PORT=5439
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password
POSTGRES_DB=acgs_e2e_test

REDIS_HOST=localhost
REDIS_PORT=6389

# Service endpoints
AUTH_SERVICE_URL=http://localhost:8016
CONSTITUTIONAL_AI_URL=http://localhost:8001
POLICY_GOVERNANCE_URL=http://localhost:8005
GOVERNANCE_SYNTHESIS_URL=http://localhost:8004
```

### Test Configuration File

Create `tests/e2e/config/test_config.yaml`:

```yaml
test_mode: offline
constitutional_hash: cdd01ef066bc6cf2
performance_targets:
  p99_latency_ms: 5.0
  cache_hit_rate: 0.85
  throughput_rps: 100.0
  success_rate: 0.95
services:
  auth:
    url: http://localhost:8016
    enabled: true
  constitutional_ai:
    url: http://localhost:8001
    enabled: true
  policy_governance:
    url: http://localhost:8005
    enabled: true
```

## 🐳 Docker Usage

### Infrastructure Only
```bash
# Start just PostgreSQL and Redis
docker-compose -f docker-compose.e2e.yml up postgres-e2e redis-e2e
```

### Mock Services
```bash
# Start mock ACGS services
docker-compose -f docker-compose.e2e.yml up --build \
  postgres-e2e redis-e2e \
  mock-auth-service mock-constitutional-ai mock-policy-governance
```

### Full Test Suite
```bash
# Run complete test suite with reporting
docker-compose -f docker-compose.e2e.yml up --build
```

### With Monitoring
```bash
# Include Prometheus and Grafana
docker-compose -f docker-compose.e2e.yml --profile monitoring up --build
```

## 📈 CI/CD Integration

### GitHub Actions

The framework integrates with GitHub Actions for automated testing:

```yaml
# .github/workflows/e2e-tests.yml
name: ACGS E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run E2E Tests
        run: |
          cd tests/e2e/docker
          docker-compose -f docker-compose.e2e.yml up --build --abort-on-container-exit
```

### Test Reports

The framework generates multiple report formats:

- **JUnit XML**: For CI/CD integration
- **HTML Reports**: For human-readable results
- **JSON Reports**: For programmatic analysis
- **Coverage Reports**: For test coverage analysis
- **Performance Reports**: For regression detection

## 🔍 Test Categories

### Health Tests (`tests/health.py`)
- Service connectivity validation
- Infrastructure health checks
- Basic endpoint responsiveness

### Constitutional Tests (`tests/constitutional.py`)
- Constitutional hash consistency
- Policy validation compliance
- Constitutional AI service testing

### HITL Tests (`tests/hitl.py`)
- Sub-5ms P99 latency validation
- Uncertainty assessment accuracy
- Human escalation triggers

### Governance Tests (`tests/governance.py`)
- Multi-agent coordination
- Blackboard architecture validation
- Consensus mechanisms

### Performance Tests (`tests/performance.py`)
- Latency benchmarking
- Throughput validation
- Cache performance testing

### Infrastructure Tests (`tests/infrastructure.py`)
- Database connectivity
- Redis operations
- Service port configuration

### Security Tests (`tests/security.py`)
- Authentication requirements
- Input validation
- Audit trail verification

## 📋 Test Execution Patterns

### Smoke Tests
```bash
# Quick validation (< 5 minutes)
python -m pytest -m smoke --maxfail=5 --timeout=300
```

### Regression Tests
```bash
# Full regression suite (< 30 minutes)
python -m pytest --cov=tests/e2e --cov-fail-under=80
```

### Performance Tests
```bash
# Performance validation (< 60 minutes)
python -m pytest -m performance --benchmark-json=reports/benchmark.json
```

### Security Tests
```bash
# Security compliance (< 15 minutes)
python -m pytest -m security --tb=short
```

## 🚨 Deployment Gates

The framework implements deployment gates that block deployments if:

- Critical tests fail (smoke, constitutional, security)
- Performance regressions exceed thresholds
- Constitutional compliance rate < 95%
- Test coverage drops below 80%

## 🛠️ Development

### Adding New Tests

1. **Create test class:**
   ```python
   from tests.e2e.framework.base import BaseE2ETest
   
   class MyNewTest(BaseE2ETest):
       test_type = "my_category"
       tags = ["my_tag", "category"]
       
       async def run_test(self):
           # Test implementation
           pass
   ```

2. **Register test:**
   ```python
   from tests.e2e.framework.runner import E2ETestRunner
   
   runner = E2ETestRunner()
   runner.register_test(MyNewTest, "my_new_test")
   ```

### Extending Mock Services

1. **Add endpoints to mock service:**
   ```python
   @mock_service.app.post("/api/v1/my/endpoint")
   async def my_endpoint():
       await mock_service.simulate_latency()
       return {"result": "success"}
   ```

2. **Update Docker configuration:**
   ```dockerfile
   # Add new service to docker-compose.e2e.yml
   ```

## 📚 API Reference

### Core Classes

- `E2ETestFramework`: Main framework orchestration
- `E2ETestConfig`: Configuration management
- `E2ETestRunner`: Test execution engine
- `E2ETestReporter`: Reporting and analysis
- `BaseE2ETest`: Base class for all tests

### Test Types

- `ConstitutionalComplianceTest`: Constitutional validation
- `PerformanceTest`: Performance benchmarking
- `SecurityTest`: Security validation

## 🤝 Contributing

1. Follow existing test patterns
2. Maintain >80% test coverage
3. Validate performance targets
4. Update documentation
5. Test in all modes (offline/online/hybrid)

## 📞 Support

For issues or questions:

1. Check existing test logs and reports
2. Verify configuration and environment
3. Run diagnostic tests: `python -m pytest tests/e2e/tests/health.py`
4. Review framework documentation

## 📄 License

This E2E test framework is part of the ACGS project and follows the same licensing terms.
