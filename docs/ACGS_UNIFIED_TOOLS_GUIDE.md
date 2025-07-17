# ACGS Unified Tools Implementation Guide
**Constitutional Hash: cdd01ef066bc6cf2**


**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Last Updated**: 2025-01-07 UTC  
**Version**: 1.0.0  

## Quick Start

### Prerequisites
- Python 3.11+
- Docker 20.10+
- PostgreSQL 15+ (port 5439)
- Redis 7+ (port 6389)

### Installation
```bash
# Clone repository
git clone https://github.com/acgs/acgs.git
cd acgs

# Install dependencies
pip install -r requirements.txt

# Verify constitutional hash
echo $CONSTITUTIONAL_HASH  # Should equal: cdd01ef066bc6cf2
```

### Basic Usage
```bash
# Run comprehensive suite
python tools/acgs_unified_orchestrator.py --comprehensive

# Run specific tool
python tools/acgs_unified_orchestrator.py --tool performance

# List available tools
python tools/acgs_unified_orchestrator.py --list-tools
```

## Unified Tools Overview

### 1. Performance Testing
```bash
# Comprehensive performance suite
python tools/acgs_performance_suite.py

# Performance monitoring
python tools/acgs_performance_suite.py --monitor

# Specific performance test
python tools/acgs_unified_orchestrator.py --tool performance
```

**Expected Output**:
- P99 Latency: <5ms ✅
- Throughput: >100 RPS ✅
- Cache Hit Rate: >85% ✅
- Constitutional Compliance: 100% ✅

### 2. Cache Optimization
```bash
# Cache optimization
python tools/acgs_cache_optimizer.py

# Cache monitoring
python tools/acgs_cache_optimizer.py --monitor

# Via unified orchestrator
python tools/acgs_unified_orchestrator.py --tool cache
```

**Key Features**:
- Automated cache warming
- TTL policy optimization
- Memory usage optimization
- Real-time monitoring

### 3. Constitutional Compliance
```bash
# Compliance validation
python tools/acgs_constitutional_compliance_framework.py

# Generate compliance report
python tools/acgs_constitutional_compliance_framework.py --report

# Via unified orchestrator
python tools/acgs_unified_orchestrator.py --tool compliance
```

**Validation Checks**:
- Constitutional hash verification
- Service connectivity validation
- Audit trail compliance
- Performance compliance

### 4. Testing Infrastructure
```bash
# Run all tests
python tools/acgs_test_orchestrator.py

# Specific test suite
python tools/acgs_test_orchestrator.py --suite unit

# Via unified orchestrator
python tools/acgs_unified_orchestrator.py --tool testing
```

**Test Coverage**:
- Unit tests
- Integration tests
- Performance tests
- Security tests
- Constitutional compliance tests

### 5. Security Assessment
```bash
# Comprehensive security scan
python tools/acgs_security_orchestrator.py

# Vulnerability scan only
python tools/acgs_security_orchestrator.py --scan-vulnerabilities

# Via unified orchestrator
python tools/acgs_unified_orchestrator.py --tool security
```

**Security Tools**:
- Bandit (Python security)
- Safety (dependency vulnerabilities)
- Trivy (filesystem scanning)
- Semgrep (static analysis)

### 6. Deployment Management
```bash
# Deploy full stack
python tools/acgs_deployment_orchestrator.py --deploy-all

# Deploy specific service
python tools/acgs_deployment_orchestrator.py --service auth

# Via unified orchestrator
python tools/acgs_unified_orchestrator.py --tool deployment
```

**Deployment Strategies**:
- Rolling deployment
- Blue-green deployment
- Canary deployment

### 7. Monitoring & Observability
```bash
# Start monitoring
python tools/acgs_monitoring_orchestrator.py

# Health check all services
python tools/acgs_monitoring_orchestrator.py --health-check

# Via unified orchestrator
python tools/acgs_unified_orchestrator.py --tool monitoring
```

**Monitoring Features**:
- Real-time health monitoring
- Performance metrics collection
- Alert management
- Constitutional compliance tracking

### 8. Documentation Generation
```bash
# Generate all documentation
python tools/acgs_documentation_orchestrator.py

# Generate API docs only
python tools/acgs_documentation_orchestrator.py --api-only

# Via unified orchestrator
python tools/acgs_unified_orchestrator.py --tool documentation
```

**Documentation Types**:
- API documentation (OpenAPI)
- System architecture
- Deployment guides
- Compliance documentation

## Configuration

### Environment Variables
```bash
# Required
export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
export DATABASE_URL="postgresql://acgs_user:acgs_secure_password@localhost:5439/acgs_db"
export REDIS_URL="redis://localhost:6389/0"

# Optional
export ENVIRONMENT="development"
export LOG_LEVEL="INFO"
export PERFORMANCE_TARGETS_P99_MS="5.0"
export PERFORMANCE_TARGETS_RPS="100.0"
export CACHE_HIT_RATE_TARGET="0.85"
```

### Service Configuration
```yaml
# config/services.yml
services:
  auth:
    port: 8016
    critical: true
  constitutional_ai:
    port: 8001
    critical: true
  # ... other services
```

## Best Practices

### 1. Constitutional Compliance
- Always validate constitutional hash before operations
- Include constitutional hash in all responses
- Maintain audit trail with constitutional context
- Validate compliance in CI/CD pipeline

### 2. Performance Optimization
- Use async/await patterns throughout
- Implement connection pooling for databases
- Optimize cache usage for >85% hit rate
- Monitor P99 latency <5ms target

### 3. Security
- Run security scans regularly
- Address critical vulnerabilities immediately
- Maintain compliance with security frameworks
- Validate constitutional security requirements

### 4. Testing
- Maintain >80% test coverage
- Run comprehensive test suite in CI/CD
- Include constitutional compliance tests
- Validate performance targets in tests

### 5. Monitoring
- Monitor all services continuously
- Set up alerts for critical issues
- Track constitutional compliance metrics
- Monitor performance targets

## Troubleshooting

### Common Issues

#### Constitutional Hash Mismatch
```bash
# Check current hash
echo $CONSTITUTIONAL_HASH

# Should equal: cdd01ef066bc6cf2
# If not, update environment variable
export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
```

#### Service Connection Issues
```bash
# Check service health
python tools/acgs_monitoring_orchestrator.py --health-check

# Check specific service
curl http://localhost:8016/health
```

#### Performance Issues
```bash
# Run performance diagnostics
python tools/acgs_performance_suite.py --diagnose

# Check cache performance
python tools/acgs_cache_optimizer.py --analyze
```

#### Test Failures
```bash
# Run specific test suite
python tools/acgs_test_orchestrator.py --suite unit --verbose

# Check test coverage
python tools/acgs_test_orchestrator.py --coverage-report
```

### Getting Help

1. **Check logs**: All tools provide detailed logging
2. **Run diagnostics**: Use `--verbose` flag for detailed output
3. **Validate configuration**: Ensure all environment variables are set
4. **Check constitutional compliance**: Verify hash is correct
5. **Review documentation**: Check tool-specific documentation

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: ACGS Comprehensive Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Validate Constitutional Compliance
        env:
          CONSTITUTIONAL_HASH: cdd01ef066bc6cf2
        run: python tools/acgs_unified_orchestrator.py --tool compliance
      
      - name: Run Security Assessment
        run: python tools/acgs_unified_orchestrator.py --tool security
      
      - name: Run Performance Tests
        run: python tools/acgs_unified_orchestrator.py --tool performance
      
      - name: Run Test Suite
        run: python tools/acgs_unified_orchestrator.py --tool testing
```

## Migration from Legacy Tools

### Step 1: Identify Legacy Tools
```bash
# Find old tools
find tools/ -name "*.py" | grep -E "(old|legacy|deprecated)"
```

### Step 2: Map to New Tools
- Performance tools → `acgs_performance_suite.py`
- Cache tools → `acgs_cache_optimizer.py`
- Compliance tools → `acgs_constitutional_compliance_framework.py`
- Test tools → `acgs_test_orchestrator.py`
- Security tools → `acgs_security_orchestrator.py`
- Deployment tools → `acgs_deployment_orchestrator.py`
- Monitoring tools → `acgs_monitoring_orchestrator.py`
- Documentation tools → `acgs_documentation_orchestrator.py`

### Step 3: Update Scripts
Replace legacy tool calls with unified orchestrator:
```bash
# Old way
python tools/old_performance_test.py
python tools/legacy_security_scan.py

# New way
python tools/acgs_unified_orchestrator.py --tool performance
python tools/acgs_unified_orchestrator.py --tool security
```

### Step 4: Validate Migration
```bash
# Run comprehensive validation
python tools/acgs_unified_orchestrator.py --comprehensive
```

## Support and Maintenance

### Regular Maintenance Tasks
1. **Weekly**: Run comprehensive suite validation
2. **Monthly**: Review performance metrics and optimize
3. **Quarterly**: Security assessment and compliance review
4. **Annually**: Full system audit and documentation update

### Monitoring and Alerts
- Set up continuous monitoring for all services
- Configure alerts for constitutional compliance violations
- Monitor performance targets continuously
- Track security vulnerabilities and address promptly



## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Documentation Status**: Complete  
**Next Review**: 2025-04-07  

For additional support, refer to the comprehensive documentation in the `docs/` directory or contact the ACGS development team.
