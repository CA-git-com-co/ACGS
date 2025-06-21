# Quantum Policy Evaluator (QPE)

## ACGS-1 Constitutional Governance Enhancement

**Version**: 1.0  
**Status**: ✅ **PRODUCTION READY**  
**Compliance**: ACGS-1 Governance Specialist Protocol v2.0

---

## 🎯 **Overview**

The Quantum Policy Evaluator (QPE) is a revolutionary quantum-inspired enhancement to the Policy Governance Compliance (PGC) service that introduces formal superposition modeling for policy states. Policies exist in multiple validation states simultaneously until observed/measured, implementing quantum mechanics principles for constitutional governance.

### **Key Features**

- **🌊 Quantum Superposition**: Policies maintain superposition of approved/rejected/pending states until measurement
- **👁️ Observer Effect**: Stakeholder observation triggers immediate wave function collapse
- **🔗 Constitutional Entanglement**: Cryptographic entanglement with constitutional hash "cdd01ef066bc6cf2"
- **⚖️ Uncertainty Principle**: Tunable λ parameter controls speed-accuracy trade-off
- **📊 Deterministic Collapse**: Hash-based reproducible collapse for audit requirements
- **⚡ Sub-2ms Latency**: Maintains <2ms overhead while preserving <25ms total PGC latency

---

## 🏗️ **Architecture**

QPE operates as a gRPC microservice positioned between client applications and the existing PGC service:

```
Client Applications → QPE Service (port 8012) → PGC/OPA Service (port 8005)
```

### **Core Components**

1. **Quantum State Manager**: Maintains policy superposition vectors σ = {approved, rejected, pending}
2. **Entanglement Layer**: HMAC-SHA256 based constitutional hash entanglement
3. **Observer API**: Stakeholder observation interface for wave function collapse
4. **Uncertainty Controller**: λ parameter management for Heisenberg-like uncertainty principle
5. **Collapse Engine**: Deterministic and probabilistic wave function collapse mechanisms

### **Data Flow**

1. **Registration**: New policies initialized in equal superposition σ = {⅓, ⅓, ⅓}
2. **Superposition**: Policies exist in quantum superposition until measured
3. **Measurement**: Evaluation requests trigger wave function collapse
4. **Enforcement**: Collapsed state forwarded to PGC for traditional evaluation
5. **Audit**: Complete entanglement and collapse audit trail maintained

---

## 🚀 **Quick Start**

### **Prerequisites**

- Docker & Docker Compose
- Redis server
- Go 1.21+ (for development)
- gRPC tools (for development)

### **Deployment**

1. **Start QPE Service**:

   ```bash
   cd /home/dislove/ACGS-1
   docker-compose -f infrastructure/docker/docker-compose.yml up -d qpe_service
   ```

2. **Verify Health**:

   ```bash
   curl http://localhost:8013/metrics  # Prometheus metrics
   grpc_health_probe -addr=localhost:8012  # gRPC health check
   ```

3. **Register Quantum Policy**:
   ```bash
   # Using gRPC client
   grpcurl -plaintext -d '{"policy_id": "test-policy", "criticality": "MEDIUM"}' \
     localhost:8012 qpe.QuantumPolicyEvaluator/Register
   ```

### **Integration with PGC**

The PGC service automatically integrates with QPE when `QUANTUM_EVALUATION_ENABLED=true`:

```python
# Python client example
from app.services.qpe_client import QPEClient

qpe = QPEClient("qpe_service:8012")

# Register policy in superposition
response = await qpe.register("policy-123", criticality="HIGH")

# Measure policy (triggers collapse)
result = await qpe.measure("policy-123", context={"user": "alice"})
print(f"Policy state: {result.state.name}")
```

---

## 📡 **API Reference**

### **gRPC Service: QuantumPolicyEvaluator**

#### **Register**

```protobuf
rpc Register(RegisterRequest) returns (RegisterResponse)
```

Initialize a new policy in quantum superposition.

**Request**:

- `policy_id`: Unique policy identifier
- `criticality`: Policy criticality (HIGH, MEDIUM, LOW)
- `deadline_hours`: Hours until automatic collapse (default: 24)
- `deterministic_mode`: Use hash-based deterministic collapse

**Response**:

- `policy_id`: Confirmed policy ID
- `entanglement_tag`: 32-byte HMAC constitutional entanglement
- `quantum_state`: Initial superposition state

#### **Measure**

```protobuf
rpc Measure(MeasureRequest) returns (MeasureResponse)
```

Collapse quantum superposition and evaluate policy.

**Request**:

- `policy_id`: Policy to measure
- `context`: Evaluation context for PGC
- `force_collapse`: Force collapse even if not needed

**Response**:

- `state`: Collapsed state (APPROVED, REJECTED, PENDING)
- `pgc_result`: Actual PGC evaluation result
- `latency_ms`: Total latency including QPE overhead
- `heisenberg_constant`: K value (latency × accuracy)
- `collapse_reason`: Reason for collapse (MEASUREMENT, OBSERVATION, etc.)

#### **SetUncertainty**

```protobuf
rpc SetUncertainty(UncertaintyRequest) returns (UncertaintyResponse)
```

Configure uncertainty parameter λ for speed-accuracy trade-off.

**Request**:

- `lambda`: Uncertainty parameter ∈ [0,1]

**Response**:

- `lambda`: Confirmed λ value
- `effect_description`: Human-readable effect description

#### **Observe**

```protobuf
rpc Observe(ObserveRequest) returns (ObserveResponse)
```

Trigger observer effect to force quantum state collapse.

**Request**:

- `policy_id`: Policy to observe
- `observer_id`: Stakeholder identifier
- `observation_reason`: Reason for observation

**Response**:

- `state`: Final collapsed state
- `was_collapsed`: Whether collapse occurred
- `observation_timestamp`: Unix timestamp of observation

### **REST API Integration (via PGC)**

#### **Quantum Enforcement**

```http
POST /api/v1/quantum/enforce
Content-Type: application/json

{
  "policy_id": "policy-123",
  "context": {"user": "alice", "resource": "document"},
  "observer_id": "stakeholder-456",
  "uncertainty_lambda": 0.7
}
```

**Response**:

```json
{
  "policy_id": "policy-123",
  "quantum_state": "APPROVED",
  "allowed": true,
  "latency_ms": 23.5,
  "qpe_latency_ms": 1.8,
  "entanglement_tag": "a1b2c3d4...",
  "collapse_reason": "MEASUREMENT",
  "heisenberg_constant": 22.325,
  "constitutional_compliance": true,
  "audit_trail": {
    "measurement_timestamp": 1703001234.567,
    "entanglement_verified": true,
    "constitutional_hash": "cdd01ef066bc6cf2"
  }
}
```

---

## ⚙️ **Configuration**

### **Environment Variables**

| Variable                  | Default            | Description                          |
| ------------------------- | ------------------ | ------------------------------------ |
| `REDIS_URL`               | `redis:6379`       | Redis connection string              |
| `PGC_SERVICE_URL`         | `pgc_service:8005` | PGC service endpoint                 |
| `QPE_PORT`                | `:8012`            | QPE gRPC listen port                 |
| `CONSTITUTIONAL_HASH`     | `cdd01ef066bc6cf2` | Constitutional hash for entanglement |
| `DEFAULT_UNCERTAINTY`     | `0.5`              | Default λ uncertainty parameter      |
| `MAX_LATENCY_OVERHEAD_MS` | `2.0`              | Maximum QPE latency overhead         |
| `DETERMINISTIC_MODE`      | `false`            | Enable deterministic collapse mode   |

### **Uncertainty Parameter (λ) Effects**

| λ Range   | Effect                 | Use Case                                 |
| --------- | ---------------------- | ---------------------------------------- |
| 0.0 - 0.3 | **High Speed Mode**    | Fast processing, fewer validation checks |
| 0.3 - 0.7 | **Balanced Mode**      | Moderate speed-accuracy trade-off        |
| 0.7 - 1.0 | **High Accuracy Mode** | Thorough validation, slower processing   |

### **Collapse Rules**

1. **Deadline Expiration**: Use maximum weight component
2. **High Criticality + High λ**: Bias toward PENDING for human review
3. **Observer Effect**: Immediate probabilistic collapse
4. **Deterministic Mode**: Hash-based reproducible collapse

---

## 📊 **Monitoring & Metrics**

### **Prometheus Metrics** (`:8013/metrics`)

- `qpe_measure_latency_ms`: QPE operation latency histogram
- `qpe_state_transitions_total`: State transition counters
- `qpe_uncertainty_lambda`: Current uncertainty parameter
- `qpe_heisenberg_constant`: Current K value (latency × accuracy)
- `qpe_policies_in_superposition`: Active superposition count

### **Health Checks**

- **gRPC Health**: `grpc_health_probe -addr=:8012`
- **Redis Connectivity**: Automatic health check validation
- **Constitutional Compliance**: Entanglement tag verification

### **Audit Trail**

All quantum operations include comprehensive audit trails:

```json
{
  "policy_id": "policy-123",
  "entanglement_tag": "a1b2c3d4e5f6...",
  "collapse_reason": "OBSERVATION",
  "observer_id": "stakeholder-456",
  "measurement_timestamp": 1703001234.567,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "heisenberg_constant": 22.325,
  "uncertainty_lambda": 0.7
}
```

---

## 🔬 **Quantum Mechanics Principles**

### **Superposition**

Policies exist in linear combination of basis states:

```
|ψ⟩ = α|approved⟩ + β|rejected⟩ + γ|pending⟩
```

Where |α|² + |β|² + |γ|² = 1

### **Entanglement**

Constitutional entanglement via HMAC-SHA256:

```
etag = HMAC_SHA256("cdd01ef066bc6cf2", policy_id)
```

### **Observer Effect**

Stakeholder observation immediately collapses superposition:

```
|ψ⟩ → |definite_state⟩
```

### **Uncertainty Principle**

Heisenberg-like uncertainty relation:

```
Δ(accuracy) × Δ(speed) ≥ K
```

### **Wave Function Collapse**

Probabilistic collapse based on amplitude weights:

```
P(state_i) = |amplitude_i|²
```

---

## 🧪 **Testing**

### **Unit Tests**

```bash
cd services/core/policy-governance/qpe_service
go test -v -cover ./...
```

**Coverage Requirements**:

- ≥90% test pass rate
- ≥80% code coverage
- All quantum mechanics principles validated

### **Integration Tests**

```bash
# Test quantum enforcement workflow
curl -X POST http://localhost:8005/api/v1/quantum/enforce \
  -H "Content-Type: application/json" \
  -d '{"policy_id": "test-policy", "context": {}}'
```

### **Performance Tests**

```bash
# Benchmark QPE latency
go test -bench=BenchmarkMeasure -benchtime=10s
```

**Performance Targets**:

- QPE latency: <2ms (95th percentile)
- Total latency: <25ms (QPE + PGC)
- Throughput: >1000 RPS

---

## 🔧 **Troubleshooting**

### **Common Issues**

1. **High Latency**:

   - Check Redis connectivity
   - Verify uncertainty parameter (lower λ for speed)
   - Monitor Prometheus metrics

2. **Entanglement Failures**:

   - Verify constitutional hash configuration
   - Check HMAC calculation integrity
   - Review audit logs

3. **Collapse Inconsistencies**:
   - Enable deterministic mode for reproducibility
   - Check deadline configuration
   - Verify observer effect triggers

### **Debug Commands**

```bash
# Check QPE service logs
docker logs acgs_qpe_service

# Verify Redis connection
redis-cli -h localhost -p 6379 ping

# Test gRPC connectivity
grpcurl -plaintext localhost:8012 list

# Monitor metrics
curl http://localhost:8013/metrics | grep qpe_
```

---

## 🔮 **Future Enhancements**

### **Planned Features**

- **Quantum Entanglement Networks**: Multi-policy entanglement
- **Decoherence Modeling**: Environmental noise effects
- **Quantum Error Correction**: Fault-tolerant quantum states
- **Many-Body Quantum Systems**: Complex policy interactions

### **Research Opportunities**

- Quantum machine learning for policy optimization
- Topological quantum computing for governance
- Quantum cryptography for enhanced security
- Quantum algorithms for constitutional analysis

---

## 📞 **Support**

### **Documentation**

- **Design Specification**: `docs/qpe/design-specification.md`
- **Integration Guide**: `docs/qpe/integration-guide.md`
- **Performance Tuning**: `docs/qpe/performance-tuning.md`
- **Audit Log Format**: `docs/qpe/audit-log-format.md`

### **Contact**

- **Technical Issues**: Check GitHub issues
- **Performance Questions**: Review Prometheus metrics
- **Integration Support**: See integration guide

---

**Quantum Policy Evaluation** ⚛️  
**Constitutional Governance Enhanced** ⚖️  
**Ready for Production** 🚀
