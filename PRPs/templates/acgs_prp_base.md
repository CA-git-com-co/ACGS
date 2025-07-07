# ACGS PRP: {{feature_name}}

**Constitutional Hash**: `cdd01ef066bc6cf2`
**Status**: Ready for Implementation

---

## Goal

{{goal_description}}

**Constitutional Requirements**:
- [ ] All operations validate constitutional hash `cdd01ef066bc6cf2`
- [ ] {{compliance_rate}}% constitutional compliance rate
- [ ] Complete audit trail for all operations
- [ ] Real-time validation (no deferrals)

**Performance Targets**:
- [ ] P99 latency < {{p99_target_ms}}ms
- [ ] Throughput > {{throughput_target_rps}} RPS
- [ ] Cache hit rate > {{cache_hit_rate}}%
- [ ] Availability 99.99%

**Integration Points**:
- Constitutional AI Service (8001): {{constitutional_integration}}
- Multi-Agent Coordinator (8008): {{multi_agent_integration}}
- Blackboard Service (8010): {{blackboard_integration}}
- Integrity Service (8002): {{audit_integration}}

---

## Tasks

### 1. Core Service Implementation
**Location**: `services/core/{{service_name}}/`

```python
class {{ServiceClass}}:
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.cache = {{CacheClass}}()
        
    async def process_request(self, request: {{RequestClass}}) -> {{ResponseClass}}:
        # Validate constitutional compliance
        if not self._validate_constitutional_hash(request):
            raise ConstitutionalComplianceError()
        
        # Process with performance monitoring
        start_time = time.perf_counter()
        result = await self._process_request_internal(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Generate audit event
        await self._generate_audit_event(request, result, duration_ms)
        
        return result
```

### 2. Data Models
```python
class {{RequestClass}}(BaseModel):
    {{request_fields}}
    constitutional_hash: str = "cdd01ef066bc6cf2"

class {{ResponseClass}}(BaseModel):
    {{response_fields}}
    constitutional_hash: str = "cdd01ef066bc6cf2"
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
```

### 3. Multi-Agent Integration
```python
class {{CoordinatorClass}}:
    async def coordinate_{{operation}}(self, request: {{RequestClass}}) -> {{ResponseClass}}:
        # Register on blackboard
        task = await self.blackboard.create_task("{{operation}}", request)
        
        # Coordinate with agents
        responses = await self._coordinate_with_agents(request.participating_agents)
        
        # Validate constitutionally
        result = await self._validate_constitutional_compliance(responses)
        
        return {{ResponseClass}}(validated=result.compliant, details=result)
```

---

## Validation

### Level 1: Code Quality
```bash
ruff check services/core/{{service_name}}/ --fix
mypy services/core/{{service_name}}/
python tools/validation/constitutional_compliance_validator.py --service {{service_name}}
```

### Level 2: Unit Tests
```bash
pytest tests/unit/{{service_name}}/ -v --constitutional-compliance
pytest tests/unit/{{service_name}}/ -v --performance
```

**Test Pattern**:
```python
class Test{{ServiceClass}}(ConstitutionalTestCase):
    @pytest.mark.constitutional
    async def test_constitutional_compliance(self):
        service = {{ServiceClass}}()
        request = {{RequestClass}}(
            constitutional_hash="cdd01ef066bc6cf2",
            {{sample_request_data}}
        )
        result = await service.process_request(request)
        assert result.constitutional_hash == "cdd01ef066bc6cf2"
    
    @pytest.mark.performance
    async def test_performance_target(self):
        service = {{ServiceClass}}()
        latencies = []
        for i in range(100):
            start = time.perf_counter()
            await service.process_request(self.sample_request)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
        
        p99 = statistics.quantiles(latencies, n=100)[98]
        assert p99 < {{p99_target_ms}}, f"P99 latency {p99:.2f}ms exceeds {{p99_target_ms}}ms target"
```

### Level 3: Integration Tests
```bash
pytest tests/integration/{{service_name}}/ -v
python tests/integration/test_multi_agent_coordination.py --service {{service_name}}
```

### Level 4: Performance Tests
```bash
python tests/performance/test_performance_regression.py --service {{service_name}}
python tests/performance/validate_latency_targets.py --target-p99 {{p99_target_ms}}
```

---

## API

### POST /api/v1/{{endpoint}}
**Request**:
```json
{
  {{sample_request_json}}
  "constitutional_hash": "cdd01ef066bc6cf2"
}
```

**Response**:
```json
{
  {{sample_response_json}}
  "constitutional_hash": "cdd01ef066bc6cf2",
  "performance_metrics": {
    "duration_ms": {{sample_latency}}
  }
}
```

### GET /api/v1/{{endpoint}}/metrics
```json
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "requests_per_second": {{sample_rps}},
  "p99_latency_ms": {{sample_p99}},
  "cache_hit_rate": {{sample_cache_rate}},
  "constitutional_compliance_rate": {{compliance_rate_decimal}}
}
```

---

## Checklist

### Implementation
- [ ] ✅ **Constitutional Hash**: `cdd01ef066bc6cf2` validated in all operations
- [ ] ✅ **Performance**: P99 latency < {{p99_target_ms}}ms validated
- [ ] ✅ **Multi-Agent**: Blackboard integration functional
- [ ] ✅ **Audit**: Constitutional events generated
- [ ] ✅ **Testing**: ConstitutionalTestCase inheritance
- [ ] ✅ **Caching**: >{{cache_hit_rate}}% cache hit rate achieved

### Quality Gates
- [ ] ✅ **Syntax**: Ruff/mypy checks pass
- [ ] ✅ **Unit Tests**: Constitutional and performance tests pass
- [ ] ✅ **Integration**: Multi-service coordination works
- [ ] ✅ **Performance**: Latency targets met
- [ ] ✅ **Monitoring**: Metrics and alerts configured

### Production
- [ ] ✅ **Health**: `/health` includes constitutional status
- [ ] ✅ **Metrics**: `/metrics` includes compliance metrics
- [ ] ✅ **Logging**: Audit events flowing
- [ ] ✅ **Alerts**: Constitutional violation alerts configured

---

**Estimated Time**: {{estimated_hours}} hours
**Risk Level**: {{risk_level}}
**Constitutional Compliance**: ✅ All requirements validated

Ready for execution with `/execute-acgs-prp`