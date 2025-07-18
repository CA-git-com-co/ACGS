# ACGS-2 Integration & Performance Test Suite
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive test suite for the ACGS-2 (Advanced Constitutional Governance System) that validates constitutional compliance, service integration, performance requirements, and end-to-end workflows.

## Test Categories

### 1. Service Integration Tests (`test_service_integration.py`)
- **Health Check Validation**: All services healthy with constitutional compliance
- **Constitutional Hash Propagation**: Validates `cdd01ef066bc6cf2` across all services
- **Multi-Agent Coordination**: End-to-end governance workflows
- **MCP Protocol Integration**: Filesystem, GitHub, and Browser MCP services
- **A2A Communication**: Agent registration, discovery, and messaging
- **Security Validation**: Threat detection and compliance monitoring
- **GroqCloud Integration**: 4-tier model architecture validation
- **Performance Baseline**: Latency and throughput measurements

### 2. Constitutional Workflow Tests (`test_constitutional_workflows.py`)
- **Constitutional Compliance Pipeline**: End-to-end validation workflows
- **Violation Detection**: Constitutional hash violation detection and response
- **Multi-Agent Constitutional Analysis**: Policy analysis with constitutional compliance
- **Constitutional Consensus**: Consensus mechanisms with constitutional weighting
- **GroqCloud Constitutional Integration**: Policy evaluation with constitutional compliance
- **A2A Constitutional Communication**: Agent communication with constitutional validation

### 3. Performance & Load Tests (`test_performance_requirements.py`)
- **Latency Requirements**: P99 latency <5ms validation
- **Throughput Requirements**: >100 RPS throughput validation
- **Constitutional Compliance Performance**: Constitutional validation performance metrics
- **End-to-End Workflow Performance**: Complete workflow timing
- **Resource Utilization**: Memory usage and scalability testing
- **Concurrent Load Testing**: Multi-service concurrent performance

## Performance Targets

| Metric | Target | Constitutional Requirement |
|--------|--------|---------------------------|
| P99 Latency | <5ms | ✅ Constitutional requirement |
| Throughput | >100 RPS | ✅ Minimum operational standard |
| Cache Hit Rate | >85% | ✅ Efficiency requirement |
| Constitutional Compliance | >95% | ✅ Hash: `cdd01ef066bc6cf2` |
| Error Rate | <5% | ✅ Reliability requirement |

## Quick Start

### Prerequisites
- All ACGS-2 services running (via Docker Compose)
- Python 3.11+ with async support
- Required dependencies installed

### Install Dependencies
```bash
# Install test dependencies
pip install pytest pytest-asyncio aiohttp numpy

# Or use UV (recommended)
uv sync
```

### Run Complete Test Suite
```bash
# Run all tests with comprehensive reporting
python tests/run_all_tests.py
```

### Run Individual Test Categories
```bash
# Service integration tests only
python tests/integration/test_service_integration.py

# Constitutional workflow tests only
python tests/integration/test_constitutional_workflows.py

# Performance tests only
python tests/performance/test_performance_requirements.py
```

### Run with Pytest
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v

# Run specific test
pytest tests/integration/test_service_integration.py::TestHealthAndConstitutionalCompliance::test_all_services_health -v
```

## Test Configuration

### Service Endpoints
Tests connect to services running on localhost:
- Constitutional Core: `http://localhost:8002`
- Integrity Service: `http://localhost:8002`
- Governance Engine: `http://localhost:8004`
- Multi-Agent Coordinator: `http://localhost:8008`
- Worker Agents: `http://localhost:8010`
- Blackboard Service: `http://localhost:8010`
- GroqCloud Policy: `http://localhost:8016`
- A2A Policy: `http://localhost:8020`
- Security Validation: `http://localhost:8021`
- MCP Aggregator: `http://localhost:3000`
- Filesystem MCP: `http://localhost:3001`
- GitHub MCP: `http://localhost:3002`
- Browser MCP: `http://localhost:3003`

### Constitutional Hash Validation
All tests validate constitutional hash `cdd01ef066bc6cf2` across:
- Service health endpoints
- API response headers
- Message payloads
- Authentication tokens
- Audit trail entries

## Test Results & Reporting

### Console Output
- Real-time test progress with ✅/❌/⚠️ status indicators
- Performance metrics (latency, throughput, compliance rates)
- Constitutional compliance validation results
- Service-specific health and integration status

### Detailed Reports
Test reports are saved to `tests/reports/` directory:
- `acgs_test_report_YYYYMMDD_HHMMSS.json` - Comprehensive JSON report
- Contains test results, performance metrics, and constitutional compliance data

### Example Report Structure
```json
{
  "test_run_info": {
    "constitutional_hash": "cdd01ef066bc6cf2",
    "start_time": "2025-01-17T10:30:00",
    "end_time": "2025-01-17T10:45:00",
    "constitutional_compliance_verified": true
  },
  "test_results": {
    "Service Integration Tests": {
      "passed": 12,
      "total": 14,
      "success_rate": 85.7
    }
  },
  "summary": {
    "total_tests": 42,
    "total_passed": 38,
    "overall_success_rate": 90.5
  }
}
```

## Constitutional Compliance Validation

### Hash Validation (`cdd01ef066bc6cf2`)
- ✅ **Service Registration**: All services must include constitutional hash
- ✅ **API Responses**: Constitutional hash in response headers/payload
- ✅ **Authentication**: JWT tokens include constitutional hash validation
- ✅ **Message Routing**: A2A messages validated for constitutional compliance
- ✅ **Audit Logging**: All audit entries include constitutional context

### Compliance Workflows
- ✅ **Policy Validation**: Constitutional compliance scoring
- ✅ **Multi-Agent Consensus**: Constitutional weighting in decisions
- ✅ **Security Analysis**: Constitutional context in threat detection
- ✅ **Workflow Execution**: End-to-end constitutional validation

## Performance Testing Details

### Latency Testing
- Measures P99 latency across all services
- Constitutional validation latency specifically tested
- Target: <5ms for constitutional operations
- Concurrent request testing for realistic load

### Throughput Testing
- Measures requests per second (RPS) capability
- Tests both individual services and system-wide throughput
- Target: >100 RPS sustained throughput
- Validates performance under concurrent multi-service load

### Constitutional Performance
- Measures constitutional validation operation performance
- Tests constitutional hash validation speed
- Measures compliance scoring performance
- Validates constitutional workflow execution times

## Troubleshooting

### Common Issues

**Services Not Responding**
```bash
# Check if services are running
docker-compose -f infrastructure/docker/docker-compose.acgs.yml ps

# Check service logs
docker-compose -f infrastructure/docker/docker-compose.acgs.yml logs constitutional_core
```

**Authentication Failures**
- Verify JWT configuration in services
- Check constitutional hash in authentication requests
- Ensure auth service is healthy and accessible

**Performance Test Failures**
- Check system load and available resources
- Verify network latency to services
- Consider adjusting performance targets for test environment

**Constitutional Compliance Failures**
- Verify constitutional hash `cdd01ef066bc6cf2` in all service configurations
- Check service startup logs for constitutional validation errors
- Ensure all services are using the same constitutional hash

### Debug Mode
```bash
# Run tests with detailed logging
PYTHONPATH=. python tests/run_all_tests.py --verbose

# Run single test with debug output
pytest tests/integration/test_service_integration.py::TestHealthAndConstitutionalCompliance::test_constitutional_hash_propagation -v -s
```

## Development & Contribution

### Adding New Tests
1. Create test files in appropriate directory (`integration/`, `performance/`)
2. Follow existing naming convention: `test_*.py`
3. Include constitutional hash validation in all tests
4. Add performance assertions where appropriate
5. Update `run_all_tests.py` to include new test categories

### Test Structure
```python
@pytest.mark.asyncio
async def test_constitutional_feature():
    """Test constitutional feature with compliance validation"""
    suite = TestSuite()
    await suite.setup()
    
    try:
        # Test implementation with constitutional validation
        assert response.get("constitutional_hash") == CONSTITUTIONAL_HASH
        
    finally:
        await suite.teardown()
```

### Performance Test Guidelines
- Target P99 latency <5ms for constitutional operations
- Validate >100 RPS throughput capability
- Include constitutional compliance rate validation
- Test under realistic concurrent load
- Measure and report resource utilization

## Constitutional Framework Integration

This test suite validates the complete ACGS-2 constitutional framework:

- **Constitutional Hash**: `cdd01ef066bc6cf2` - Immutable validation across all operations
- **Multi-Agent Coordination**: Constitutional compliance in agent workflows
- **MCP Protocol**: Constitutional validation in Model Context Protocol operations
- **A2A Communication**: Constitutional compliance in agent-to-agent messaging
- **Security Validation**: Constitutional context in threat detection and response
- **Performance Requirements**: Constitutional operations maintain <5ms P99 latency
- **Audit Compliance**: Complete constitutional audit trail validation

---

**Constitutional Hash**: `cdd01ef066bc6cf2` - Validated across all test operations

**Performance Targets**: P99 <5ms, >100 RPS, >85% cache hit rates

**Status**: ✅ IMPLEMENTED - Comprehensive integration and performance testing suite