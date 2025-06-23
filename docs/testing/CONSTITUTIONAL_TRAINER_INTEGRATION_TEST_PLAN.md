# Constitutional Trainer Service Integration Test Plan

## Overview

This document outlines the comprehensive integration test plan for the Constitutional Trainer Service, covering the full "train → evaluate → log" workflow through the ACGS-1 Lite stack.

## Scope

### Services Under Test

- **Constitutional Trainer Service** (Port 8000) - Core training orchestration
- **Policy Engine** (Port 8001) - OPA-based constitutional policy evaluation
- **Audit Engine** (Port 8003) - Immutable audit trail and logging
- **Redis** (Port 6379) - Caching and session management
- **Prometheus** (Port 9090) - Metrics collection
- **Grafana** (Port 3000) - Monitoring dashboards

### Integration Points

1. **API Endpoints** - REST API functionality and error handling
2. **Policy Evaluation** - OPA integration for constitutional compliance
3. **Audit Logging** - End-to-end audit trail creation and retrieval
4. **Caching Layer** - Redis performance and cache hit/miss behavior
5. **Metrics Emission** - Prometheus metrics collection and validation
6. **Dashboard Integration** - Grafana dashboard updates and visualization

## Test Scenarios

### 1. Happy Path Training Workflow

**Objective:** Validate successful constitutional training end-to-end

**Test Steps:**

1. Submit valid training request with constitutional data
2. Verify policy evaluation allows training
3. Monitor training progress through session management
4. Validate constitutional compliance scoring
5. Confirm audit log creation
6. Check metrics emission to Prometheus

**Success Criteria:**

- Training request accepted (HTTP 200)
- Response time < 2000ms
- Constitutional compliance score ≥ 0.95
- Audit log created with correct metadata
- Prometheus metrics updated

### 2. Policy Violation Detection

**Objective:** Ensure policy violations are properly detected and handled

**Test Steps:**

1. Submit training request with missing constitutional hash
2. Submit request with invalid constitutional data
3. Verify policy engine rejects requests
4. Confirm appropriate error responses
5. Validate audit logging of violations

**Success Criteria:**

- Policy violations detected (HTTP 400/403/422)
- Clear error messages returned
- Violation events logged to audit engine
- No training sessions created for invalid requests

### 3. Redis Caching Performance

**Objective:** Validate caching behavior and performance

**Test Steps:**

1. Execute cache write operations
2. Verify cache hit/miss behavior
3. Test cache expiration policies
4. Monitor cache performance metrics
5. Validate cache consistency

**Success Criteria:**

- Cache hit rate ≥ 80%
- Cache operations complete successfully
- TTL policies enforced correctly
- Performance metrics within targets

### 4. Audit Log Ingestion and Retrieval

**Objective:** Ensure complete audit trail functionality

**Test Steps:**

1. Generate training events
2. Verify audit log creation
3. Test audit log retrieval
4. Validate log integrity
5. Check audit chain consistency

**Success Criteria:**

- All events logged to audit engine
- Audit logs retrievable via API
- Log metadata complete and accurate
- Immutable audit chain maintained

### 5. Prometheus Metrics Validation

**Objective:** Confirm metrics collection and accuracy

**Test Steps:**

1. Execute training operations
2. Collect metrics from /metrics endpoint
3. Validate metric values and labels
4. Check metric cardinality
5. Verify dashboard integration

**Success Criteria:**

- All expected metrics present
- Metric values accurate and current
- P99 latency < 2ms for policy evaluation
- Dashboard graphs update correctly

### 6. Performance and Load Testing

**Objective:** Validate system performance under load

**Test Steps:**

1. Execute concurrent training requests
2. Monitor response times and throughput
3. Check resource utilization
4. Validate graceful degradation
5. Test circuit breaker behavior

**Success Criteria:**

- System handles concurrent load
- Response times remain within SLA
- No memory leaks or resource exhaustion
- Graceful error handling under stress

## Test Environment Setup

### Prerequisites

- Kubernetes cluster with kubectl access
- Python 3.11+ with required dependencies
- Docker for containerized services
- Access to container registry (if using custom images)

### Deployment Options

#### Option 1: Full Service Deployment

```bash
# Deploy complete ACGS-1 Lite stack
./scripts/testing/deploy-constitutional-trainer-test-env.sh --namespace acgs-test
```

#### Option 2: Mock Services (Faster Testing)

```bash
# Deploy with mock services for rapid testing
./scripts/testing/deploy-constitutional-trainer-test-env.sh --namespace acgs-test --mock-services
```

#### Option 3: Local Development

```bash
# Use existing local services
export CONSTITUTIONAL_TRAINER_URL="http://localhost:8000"
export POLICY_ENGINE_URL="http://localhost:8001"
export AUDIT_ENGINE_URL="http://localhost:8003"
export REDIS_URL="redis://localhost:6379/0"
```

## Test Execution

### Manual Execution

```bash
# Run all integration tests
pytest tests/integration/test_constitutional_trainer_integration.py -v

# Run specific test scenarios
pytest tests/integration/test_constitutional_trainer_integration.py::test_constitutional_trainer_integration -v

# Run with detailed output
pytest tests/integration/test_constitutional_trainer_integration.py -v --tb=long --capture=no
```

### Automated CI/CD Execution

```bash
# Add to GitHub Actions workflow
cp scripts/ci/constitutional-trainer-integration-tests.yml .github/workflows/

# Configure environment variables in CI
CONSTITUTIONAL_TRAINER_URL: "http://constitutional-trainer:8000"
POLICY_ENGINE_URL: "http://policy-engine:8001"
AUDIT_ENGINE_URL: "http://audit-engine:8003"
REDIS_URL: "redis://redis:6379/0"
```

### Standalone Test Runner

```bash
# Run comprehensive test suite with reporting
python tests/integration/test_constitutional_trainer_integration.py
```

## Performance Targets

| Metric                          | Target   | Measurement           |
| ------------------------------- | -------- | --------------------- |
| Training Request Response Time  | < 2000ms | 95th percentile       |
| Policy Evaluation Latency       | < 25ms   | Average               |
| Cache Hit Rate                  | ≥ 80%    | Over test duration    |
| Constitutional Compliance Score | ≥ 95%    | Minimum threshold     |
| Test Success Rate               | ≥ 90%    | Overall pass rate     |
| Service Availability            | 99.9%    | During test execution |

## Test Data

### Valid Training Data

- Constitutional AI principles and examples
- Privacy-preserving data handling scenarios
- Human oversight and governance examples
- Ethical AI decision-making cases

### Invalid Test Data (for violation testing)

- Missing constitutional hash
- Malformed training requests
- Potentially harmful content (for safety testing)
- Invalid configuration parameters

## Monitoring and Alerting

### Key Metrics to Monitor

- `constitutional_compliance_score` - Training compliance levels
- `training_request_duration_seconds` - Request processing time
- `policy_evaluation_duration_seconds` - Policy check latency
- `cache_hit_rate` - Redis cache performance
- `audit_log_creation_rate` - Audit system throughput

### Alert Conditions

- Constitutional compliance score < 0.95
- Response time > 2000ms for 5 consecutive requests
- Cache hit rate < 70% for 10 minutes
- Policy evaluation latency > 50ms average
- Any service health check failures

## Troubleshooting

### Common Issues

#### Service Connectivity

```bash
# Check service health
kubectl get pods -n acgs-test
kubectl logs -n acgs-test deployment/constitutional-trainer

# Test connectivity
curl http://constitutional-trainer:8000/health
```

#### Performance Issues

```bash
# Check resource usage
kubectl top pods -n acgs-test

# Review metrics
curl http://constitutional-trainer:8000/metrics
```

#### Test Failures

```bash
# Run with debug output
pytest tests/integration/test_constitutional_trainer_integration.py -v -s --tb=long

# Check test logs
tail -f constitutional_trainer_integration_report_*.json
```

## Cleanup

### Test Environment Cleanup

```bash
# Remove test namespace and all resources
kubectl delete namespace acgs-test

# Or use deployment script cleanup
./scripts/testing/deploy-constitutional-trainer-test-env.sh --cleanup --namespace acgs-test
```

### Local Cleanup

```bash
# Stop port forwards
pkill -f "kubectl port-forward"

# Clean up test artifacts
rm -f constitutional_trainer_integration_report_*.json
rm -rf reports/
```

## Deliverables

### 1. Automated Integration Test Scripts

- **Primary Test Suite:** `tests/integration/test_constitutional_trainer_integration.py`
- **Test Utilities:** `tests/integration/constitutional_trainer_test_utils.py`
- **Mock Services:** Kubernetes manifests for rapid testing

### 2. CI/CD Configuration

- **GitHub Actions Job:** `scripts/ci/constitutional-trainer-integration-tests.yml`
- **Multi-scenario testing matrix**
- **Automated artifact collection and reporting**

### 3. Deployment Scripts

- **Environment Setup:** `scripts/testing/deploy-constitutional-trainer-test-env.sh`
- **Service health verification**
- **Automated cleanup procedures**

### 4. Test Report Generation

- **Report Generator:** `scripts/testing/generate-integration-test-report.py`
- **Multiple output formats:** JSON, HTML, Markdown
- **Performance charts and metrics visualization**

### 5. Documentation

- **Integration Test Plan:** This document
- **Usage instructions and troubleshooting guides**
- **Performance benchmarks and SLA definitions**

## Success Criteria

The integration test plan is considered successful when:

✅ **All test scenarios pass** with ≥90% success rate  
✅ **Performance targets met** for all key metrics  
✅ **End-to-end workflows validated** through complete ACGS-1 Lite stack  
✅ **Policy violations properly detected** and handled  
✅ **Audit trail complete** with all events logged  
✅ **Caching behavior optimal** with ≥80% hit rate  
✅ **Metrics accurately collected** and dashboards updated  
✅ **CI/CD integration functional** with automated reporting  
✅ **Documentation complete** with clear usage instructions  
✅ **Zero unexpected failures** in production-like environment

## Next Steps

1. **Execute Initial Test Run** - Validate test suite functionality
2. **Performance Baseline** - Establish performance benchmarks
3. **CI/CD Integration** - Add to existing pipeline
4. **Monitoring Setup** - Configure alerts and dashboards
5. **Team Training** - Educate team on test execution and troubleshooting
6. **Continuous Improvement** - Regular review and enhancement of test coverage
