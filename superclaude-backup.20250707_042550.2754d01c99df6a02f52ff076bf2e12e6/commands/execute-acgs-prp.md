# Execute ACGS PRP Command

This command executes a Product Requirements Prompt (PRP) for ACGS features with constitutional compliance validation, performance monitoring, and comprehensive testing.

## Usage

Use this command to implement an ACGS feature based on a generated PRP:

```
/execute-acgs-prp PRPs/feature_name.md
```

## What this command does

This command implements ACGS features using a systematic approach with built-in constitutional compliance, performance validation, and multi-agent coordination:

1. **Load and validate PRP** with constitutional compliance checking
2. **ULTRATHINK planning** with ACGS-specific considerations
3. **Systematic implementation** following ACGS patterns
4. **Constitutional validation** at each step
5. **Performance validation** against ACGS targets
6. **Multi-agent integration** testing
7. **Comprehensive audit logging** for all operations

## ACGS Implementation Workflow

### Phase 1: Load PRP and Constitutional Validation

#### Load PRP Context
- Read the specified PRP file from the PRPs directory
- Parse constitutional compliance requirements
- Extract performance targets and validation criteria
- Identify multi-agent coordination requirements
- Load ACGS integration specifications

#### Constitutional Compliance Validation
- Verify constitutional hash `cdd01ef066bc6cf2` requirements
- Validate constitutional AI service integration needs
- Check constitutional policy compliance specifications
- Verify audit logging requirements for constitutional events

#### Performance Requirements Validation
- Confirm P99 latency targets (typically < 5ms for coordination operations)
- Validate throughput requirements (typically > 100 RPS)
- Check cache hit rate requirements (typically > 85%)
- Verify performance monitoring and alerting specifications

### Phase 2: ULTRATHINK Planning

Think comprehensively about the implementation before starting. Create a detailed plan that addresses:

#### Constitutional Compliance Planning
- Constitutional hash validation strategy throughout implementation
- Constitutional AI service integration approach
- Constitutional policy compliance validation points
- Constitutional error handling and escalation procedures
- Audit event generation for all constitutional operations

#### Performance Optimization Planning
- Sub-5ms latency optimization strategies
- Caching implementation with constitutional compliance
- Async/await patterns for optimal performance
- Performance monitoring integration with Prometheus
- Performance regression testing approach

#### Multi-Agent Coordination Planning
- Blackboard service integration strategy
- Multi-agent coordinator service registration approach
- Worker agent communication protocol implementation
- Consensus engine integration (if applicable)
- Agent lifecycle management and monitoring

#### ACGS Service Integration Planning
- Service discovery and registration approach
- API Gateway integration and routing configuration
- Authentication and multi-tenant isolation implementation
- Database integration with PostgreSQL Row-Level Security
- Redis caching with tenant isolation and constitutional compliance

### Phase 3: Implementation Execution

Execute the implementation plan systematically:

#### Step 1: Constitutional Service Foundation
```python
# Always start with constitutional compliance foundation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ACGSFeatureService:
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.constitutional_validator = ConstitutionalSafetyValidator()
        
    async def initialize(self):
        if not await self.validate_constitutional_compliance():
            raise ConstitutionalComplianceError("Service initialization failed constitutional validation")
```

#### Step 2: Performance Monitoring Integration
```python
# Add performance monitoring for all operations
from services.shared.performance.metrics import track_latency, track_constitutional_compliance

@track_latency("feature_operation")
@track_constitutional_compliance
async def feature_operation(self, request: ACGSRequest) -> ACGSResponse:
    start_time = time.perf_counter()
    # Implementation with performance tracking
    pass
```

#### Step 3: Multi-Agent Coordination Integration
```python
# Integrate with blackboard and coordinator services
from services.shared.blackboard.coordination_service import BlackboardCoordinator

async def coordinate_with_agents(self, coordination_request: CoordinationMessage):
    coordinator = BlackboardCoordinator(self.agent_id, self.agent_type)
    await coordinator.initialize()
    return await coordinator.send_coordination_message(coordination_request)
```

#### Step 4: Data Models and API Endpoints
- Implement Pydantic models inheriting from ACGS base classes
- Create FastAPI endpoints with constitutional compliance middleware
- Add constitutional hash validation to all request/response models
- Implement performance monitoring for all endpoints

#### Step 5: Database Integration
- Implement PostgreSQL integration with Row-Level Security
- Add constitutional compliance to all database operations
- Implement audit logging for all database changes
- Add multi-tenant isolation with constitutional validation

#### Step 6: Testing Implementation
- Inherit from ConstitutionalTestCase for all test classes
- Implement constitutional compliance tests
- Add performance validation tests with latency targets
- Create multi-agent coordination integration tests

### Phase 4: Validation and Quality Assurance

#### Constitutional Compliance Validation
Run comprehensive constitutional compliance validation:
```bash
# Constitutional hash validation
python tools/validation/constitutional_compliance_validator.py --service feature_name

# Constitutional AI service integration validation
curl http://localhost:8001/api/v1/validate --data '{"constitutional_hash": "cdd01ef066bc6cf2"}'

# Constitutional policy compliance check
python tools/validation/constitutional_policy_validator.py --feature feature_name
```

#### Performance Validation
Validate performance against ACGS targets:
```bash
# Performance regression testing
python tests/performance/test_performance_regression.py --service feature_name

# Latency validation (P99 < 5ms target)
python tests/performance/validate_latency_targets.py --service feature_name --target-p99 5.0

# Throughput validation (> 100 RPS target)
python tests/performance/validate_throughput_targets.py --service feature_name --min-rps 100
```

#### Multi-Agent Coordination Validation
Test multi-agent coordination functionality:
```bash
# Blackboard integration testing
python tests/integration/test_blackboard_integration.py --feature feature_name

# Multi-agent coordinator integration
python tests/integration/test_multi_agent_coordination.py --feature feature_name

# Consensus engine integration (if applicable)
python tests/integration/test_consensus_engine_integration.py --feature feature_name
```

### Phase 5: Integration Testing

#### Service Integration Validation
```bash
# Full ACGS service integration test
python tests/integration/test_acgs_service_integration.py --feature feature_name

# API Gateway integration test
curl http://localhost:8010/api/v1/feature_name/health

# Authentication service integration test
python tests/integration/test_authentication_integration.py --feature feature_name
```

#### End-to-End Constitutional Compliance Testing
```bash
# End-to-end constitutional compliance validation
python tests/integration/test_end_to_end_constitutional_compliance.py --feature feature_name

# Multi-service constitutional compliance chain test
python tests/integration/test_multi_service_constitutional_chain.py --feature feature_name
```

### Phase 6: Production Readiness Validation

#### Health Check Implementation
Ensure `/health` endpoint includes constitutional compliance status:
```json
{
  "service": "feature_name",
  "status": "healthy",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "constitutional_compliant": true,
  "performance_metrics": {
    "p99_latency_ms": 2.3,
    "throughput_rps": 150,
    "cache_hit_rate": 0.92
  }
}
```

#### Metrics Implementation
Ensure `/metrics` endpoint includes ACGS-specific metrics:
```
# Constitutional compliance metrics
acgs_constitutional_compliance_score{service="feature_name"} 1.0
acgs_constitutional_hash_validations_total{service="feature_name"} 1000

# Performance metrics
acgs_request_duration_seconds{service="feature_name",percentile="0.99"} 0.0023
acgs_requests_per_second{service="feature_name"} 150

# Multi-agent coordination metrics
acgs_coordination_messages_total{service="feature_name"} 500
acgs_blackboard_operations_total{service="feature_name"} 200
```

## Validation Loops

### Level 1: Syntax and Constitutional Compliance
```bash
# Code quality and constitutional compliance
ruff check services/core/feature_name/ --fix
mypy services/core/feature_name/
python tools/validation/constitutional_compliance_validator.py --service feature_name
```

If any validation fails, fix the issues and re-run until all checks pass.

### Level 2: Unit Tests with Constitutional Validation
```bash
# Constitutional compliance unit tests
pytest tests/unit/feature_name/ -v --constitutional-compliance

# Performance unit tests  
pytest tests/unit/feature_name/ -v --performance

# Multi-agent coordination unit tests
pytest tests/unit/feature_name/ -v --multi-agent-coordination
```

If any tests fail, analyze the failure, fix the implementation, and re-run until all tests pass.

### Level 3: Integration Tests
```bash
# ACGS service integration tests
pytest tests/integration/feature_name/ -v

# Multi-service integration tests
python tests/integration/test_multi_service_integration.py --feature feature_name

# End-to-end workflow tests
python tests/integration/test_end_to_end_workflows.py --feature feature_name
```

If integration tests fail, investigate service communication issues, fix integration problems, and re-run until all tests pass.

### Level 4: Performance and Load Testing
```bash
# Performance regression validation
python tests/performance/test_performance_regression.py --service feature_name

# Load testing with constitutional validation
python tests/load_testing/test_constitutional_load.py --service feature_name --rps 100 --duration 60

# Constitutional compliance under load
python tests/load_testing/test_constitutional_compliance_load.py --service feature_name
```

If performance tests fail, optimize the implementation and re-run until performance targets are met.

## Error Handling and Recovery

### Constitutional Compliance Failures
If constitutional compliance validation fails:
1. **Stop implementation immediately**
2. **Review constitutional hash validation logic**
3. **Check constitutional AI service integration**
4. **Verify constitutional policy compliance**
5. **Fix compliance issues before proceeding**

### Performance Target Failures
If performance targets are not met:
1. **Analyze performance metrics and bottlenecks**
2. **Optimize database queries and caching**
3. **Review async/await patterns**
4. **Optimize constitutional validation performance**
5. **Re-test until targets are met**

### Multi-Agent Coordination Failures
If multi-agent coordination fails:
1. **Check blackboard service connectivity**
2. **Verify agent registration and discovery**
3. **Test coordination message routing**
4. **Validate consensus integration (if applicable)**
5. **Fix coordination issues and re-test**

## Completion Criteria

The implementation is complete when:
- [ ] ✅ **Constitutional Compliance**: All operations validate constitutional hash `cdd01ef066bc6cf2`
- [ ] ✅ **Performance Targets**: P99 latency < 5ms, throughput > 100 RPS, cache hit rate > 85%
- [ ] ✅ **Multi-Agent Integration**: Blackboard and coordinator integration functional
- [ ] ✅ **Testing**: All constitutional, performance, and integration tests pass
- [ ] ✅ **Monitoring**: Prometheus metrics and Grafana dashboards functional
- [ ] ✅ **Audit Logging**: Constitutional compliance events generated for all operations
- [ ] ✅ **Production Ready**: Health checks, metrics, and monitoring fully operational

## Success Validation

Run final validation to confirm successful implementation:
```bash
# Complete ACGS validation suite
python tools/validation/complete_acgs_validation.py --feature feature_name

# Constitutional compliance certification
python tools/validation/constitutional_compliance_certification.py --service feature_name

# Performance certification
python tests/performance/performance_certification.py --service feature_name

# Multi-agent coordination certification
python tests/integration/multi_agent_coordination_certification.py --feature feature_name
```

---

**Constitutional Hash**: `cdd01ef066bc6cf2` - All implementations must maintain constitutional compliance throughout the execution process