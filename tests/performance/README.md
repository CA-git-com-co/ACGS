# ACGS-2 Constitutional Performance Testing Suite
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive performance testing and monitoring suite for ACGS-2 to ensure constitutional compliance with performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

## Components

### 1. Constitutional Performance Suite (`constitutional_performance_suite.py`)

Main performance testing engine that validates all ACGS-2 services against constitutional performance targets.

**Features:**
- ⚡ **Load Testing**: Configurable RPS and duration
- 📊 **Metrics Collection**: P95/P99 latency, throughput, success rates
- ⚖️ **Constitutional Validation**: Hash compliance verification
- 📈 **Detailed Reporting**: Text and JSON output formats
- 🔄 **Multi-Service Testing**: Tests all core ACGS-2 services

**Usage:**
```bash
# Quick test (30s per service, 120 RPS)
python constitutional_performance_suite.py --duration 30 --rps 120

# Comprehensive test (60s per service, 150 RPS)
python constitutional_performance_suite.py --duration 60 --rps 150

# Stress test (30s per service, 300 RPS)
python constitutional_performance_suite.py --duration 30 --rps 300 --output stress_test.txt
```

**Parameters:**
- `--duration`: Test duration per service in seconds (default: 60)
- `--rps`: Target requests per second (default: 150)
- `--output`: Output report file (default: performance_report.txt)
- `--json`: Also generate JSON report

### 2. Performance Test Runner (`run_performance_tests.py`)

Automated test runner for CI/CD integration that executes a complete performance validation suite.

**Features:**
- 🔍 **Service Health Check**: Validates services are running
- 🏃 **Multi-Test Execution**: Quick, comprehensive, and stress tests
- 📊 **Summary Reporting**: Aggregated results across all tests
- ✅ **CI/CD Integration**: Exit codes for automated validation

**Test Types:**
1. **Quick Test** (30s, 120 RPS): Fast validation for development
2. **Comprehensive Test** (60s, 150 RPS): Full performance validation
3. **Stress Test** (30s, 300 RPS): High-load behavior analysis

**Usage:**
```bash
# Run complete test suite
python run_performance_tests.py

# The runner automatically:
# 1. Checks if services are running
# 2. Installs requirements if needed
# 3. Runs all three test types
# 4. Generates summary report
# 5. Exits with status code (0=pass, 1=fail)
```

### 3. Continuous Performance Monitor (`continuous_performance_monitor.py`)

Real-time performance monitoring for production environments with constitutional compliance tracking.

**Features:**
- 📡 **Continuous Monitoring**: Regular performance measurements
- 🚨 **Real-time Alerting**: Threshold-based alerts
- ⚖️ **Constitutional Tracking**: Continuous hash validation
- 📊 **Health Reporting**: Periodic system health assessments
- 💾 **Data Persistence**: JSON data export for analysis

**Usage:**
```bash
# Start continuous monitoring (default: 30s intervals, 5m reports)
python continuous_performance_monitor.py

# Custom intervals
python continuous_performance_monitor.py --interval 60 --report-interval 10 --threshold 3.0
```

**Parameters:**
- `--interval`: Measurement interval in seconds (default: 30)
- `--report-interval`: Report interval in minutes (default: 5)
- `--threshold`: Alert threshold in milliseconds (default: 5.0)

## Service Coverage

The performance testing suite covers all core ACGS-2 services:

| Service | Port | Endpoints Tested | Critical | Constitutional |
|---------|------|------------------|----------|----------------|
| auth-service | 8013 | `/health`, `/api/v1/auth/health` | ✅ | ✅ |
| monitoring-service | 8014 | `/health`, `/api/v1/services/health` | ✅ | ✅ |
| audit-service | 8015 | `/health` | ✅ | ✅ |
| gdpr-compliance | 8016 | `/health` | - | ✅ |
| alerting-service | 8017 | `/health` | ✅ | ✅ |
| api-gateway | 8080 | `/health`, `/gateway/metrics` | ✅ | ✅ |
| constitutional-core | 8001 | `/health`, `/api/v1/constitutional/validate` | ✅ | ✅ |
| groqcloud-policy | 8023 | `/health` | ✅ | ✅ |
| multi-agent-coordination | 8008 | `/health` | ✅ | ✅ |
| worker-agents | 8009 | `/health` | ✅ | ✅ |
| blackboard-coordination | 8010 | `/health` | ✅ | ✅ |
| consensus-engine | 8011 | `/health` | ✅ | ✅ |
| human-in-the-loop | 8012 | `/health` | ✅ | ✅ |

## Constitutional Performance Requirements

### Latency Requirements
- **P99 Response Time**: <5ms (constitutional mandate)
- **P95 Response Time**: <3ms (operational target)
- **Average Response Time**: <2ms (efficiency target)

### Throughput Requirements
- **Minimum RPS**: >100 RPS per service
- **Target RPS**: >150 RPS per service
- **Peak Capacity**: >300 RPS per service (stress test)

### Reliability Requirements
- **Success Rate**: >99.5%
- **Availability**: >99.9%
- **Constitutional Compliance**: 100% (no tolerance for hash mismatches)

### Constitutional Compliance Validation
Every response from constitutional services must include:
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "status": "healthy",
  // ... other fields
}
```

## Report Formats

### Text Reports
Detailed human-readable reports with:
- System-wide performance summary
- Per-service performance breakdown
- Constitutional compliance status
- Performance optimization recommendations
- Failure analysis and troubleshooting

### JSON Reports
Machine-readable data for integration:
```json
{
  "timestamp": "2025-07-18T10:30:00Z",
  "overall_system_pass": true,
  "system_p99_response_time_ms": 3.2,
  "system_throughput_rps": 156.7,
  "constitutional_compliance_rate": 100.0,
  "services": [
    {
      "name": "auth-service",
      "p99_response_time_ms": 2.8,
      "throughput_rps": 145.2,
      "constitutional_compliance_rate": 100.0,
      "overall_pass": true
    }
  ]
}
```

## Integration with CI/CD

### GitHub Actions Integration
```yaml
- name: Run Constitutional Performance Tests
  run: |
    cd tests/performance
    python run_performance_tests.py
  
- name: Upload Performance Reports
  uses: actions/upload-artifact@v3
  with:
    name: performance-reports
    path: tests/performance/*_report.*
```

### Exit Codes
- `0`: All tests passed, system meets constitutional requirements
- `1`: Performance failures detected, optimization required

## Monitoring and Alerting

### Performance Degradation Detection
- **Latency Alerts**: P99 >5ms triggers critical alert
- **Throughput Alerts**: RPS <100 triggers warning
- **Constitutional Alerts**: Hash mismatch triggers immediate escalation

### Integration with Alerting Service
The performance monitor integrates with the ACGS-2 alerting service:
```bash
# Alerts are sent to:
# - Constitutional oversight team (hash violations)
# - DevOps team (performance degradation)
# - Security team (availability issues)
```

## Installation and Setup

### Requirements
```bash
# Install performance testing dependencies
pip install -r config/environments/requirements.txt
```

### Prerequisites
1. **ACGS-2 Services Running**: Start services with `python scripts/run_services_local.py`
2. **Python 3.9+**: Required for async/await performance features
3. **Network Access**: Services must be accessible on localhost

### Quick Start
```bash
# 1. Navigate to performance testing directory
cd tests/performance

# 2. Install dependencies
pip install -r config/environments/requirements.txt

# 3. Run quick validation
python run_performance_tests.py

# 4. Check results
cat performance_summary_report.txt
```

## Constitutional Compliance Verification

### Hash Validation Process
1. **Request Execution**: Send HTTP request to service endpoint
2. **Response Parsing**: Extract JSON response body
3. **Hash Verification**: Validate `constitutional_hash` field
4. **Compliance Recording**: Track compliance rate per service
5. **Alert Generation**: Trigger alerts for non-compliance

### Compliance Thresholds
- **100% Compliance**: Required for constitutional services
- **Immediate Escalation**: Any hash mismatch triggers alerts
- **Retention Period**: Compliance data retained for audit

## Troubleshooting

### Common Issues

#### Services Not Running
```bash
# Check service status
curl http://localhost:8013/health
curl http://localhost:8014/health

# Start services if needed
python scripts/run_services_local.py
```

#### High Latency Results
- Check system resources (CPU, memory)
- Verify database connections
- Review service logs for errors
- Consider scaling service instances

#### Constitutional Hash Mismatches
- Verify `CONSTITUTIONAL_HASH` environment variable
- Check service configuration files
- Review recent code changes
- Validate hash propagation across services

#### Authentication Failures
- Verify auth service is running
- Check JWT token generation
- Review authentication configuration

### Performance Optimization

#### Latency Optimization
1. **Caching**: Implement response caching
2. **Connection Pooling**: Optimize database connections
3. **Async Processing**: Use async/await patterns
4. **Resource Optimization**: Scale CPU/memory as needed

#### Throughput Optimization
1. **Load Balancing**: Distribute requests across instances
2. **Horizontal Scaling**: Add service replicas
3. **Database Optimization**: Index optimization and query tuning
4. **Network Optimization**: Reduce network latency

## Development Guidelines

### Adding New Services to Testing
1. Add service configuration to `services` list
2. Define critical endpoints for testing
3. Specify constitutional compliance requirements
4. Update service coverage documentation

### Creating Custom Performance Tests
```python
from constitutional_performance_suite import ConstitutionalPerformanceTester

# Create custom tester
tester = ConstitutionalPerformanceTester()

# Run custom test
report = await tester.run_comprehensive_test(
    duration_seconds=120,
    target_rps=200
)
```

### Extending Monitoring Capabilities
```python
from continuous_performance_monitor import ContinuousPerformanceMonitor

# Create custom monitor
monitor = ContinuousPerformanceMonitor(
    measurement_interval_seconds=15,
    alert_threshold_ms=3.0
)

# Add custom alerting logic
monitor.add_custom_alert_handler(my_alert_handler)
```

---

**Constitutional Compliance**: All performance testing maintains constitutional hash `cdd01ef066bc6cf2` validation and enforces the P99 <5ms, >100 RPS performance requirements mandated by the ACGS-2 constitutional framework.

**Last Updated**: 2025-07-18 - Constitutional Performance Testing Suite Implementation