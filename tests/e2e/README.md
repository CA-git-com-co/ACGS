# ACGS-1 Comprehensive End-to-End Test Suite

**Enterprise-grade end-to-end testing for the complete ACGS-1 Constitutional Governance System**

This test suite provides comprehensive validation of the entire ACGS-1 system, from blockchain programs to frontend applications, ensuring production readiness and constitutional compliance.

## 🎯 Overview

The comprehensive E2E test suite validates:

- **All 8 Core Services**: Auth, AC, Integrity, FV, GS, PGC, EC, DGM
- **Solana Blockchain Programs**: Quantumagi core, Appeals, Logging
- **Frontend Applications**: Governance dashboard, Constitutional council
- **Complete Governance Workflows**: Policy creation, Enforcement, Appeals
- **Performance Validation**: <500ms response, <0.01 SOL cost
- **Security & Compliance**: Authentication, Authorization, Constitutional compliance

## 🏗️ Architecture

```
tests/e2e/
├── test_comprehensive_end_to_end.py    # Main test orchestrator
├── modules/
│   ├── blockchain_integration.py       # Solana blockchain testing
│   ├── service_integration.py          # Service communication testing
│   ├── frontend_automation.py          # UI automation (Playwright)
│   ├── performance_validation.py       # Performance benchmarking
│   └── security_validation.py          # Security compliance testing
├── scenarios/
│   ├── democratic_policy_creation.py   # Policy creation workflow
│   ├── emergency_governance.py         # Emergency procedures
│   └── appeals_resolution.py           # Appeals and disputes
├── fixtures/
│   ├── test_data.py                    # Test data and configurations
│   └── mock_services.py               # Service mocking utilities
├── run_comprehensive_e2e_test.py       # Standalone test runner
└── README.md                           # This file
```

## 🚀 Quick Start

### Prerequisites

1. **System Requirements**:
   ```bash
   # Rust 1.81.0+ (for blockchain)
   rustc --version

   # Python 3.11+ with UV package manager
   python --version
   uv --version

   # Node.js 18+ (for frontend)
   node --version

   # Solana CLI (for blockchain testing)
   solana --version
   ```

2. **Optional: Multimodal VL Model** (for integration tests):
   ```bash
   # Deploy NVIDIA Llama-3.1-Nemotron-Nano-VL-8B-V1 on localhost:8002
   # Required only for @pytest.mark.integration tests
   curl http://localhost:8002/health  # Verify deployment
   ```

2. **ACGS-1 System Running**:
   ```bash
   # Start all 8 core services
   ./scripts/start_all_services.sh
   
   # Deploy blockchain programs to devnet
   cd blockchain && anchor deploy --provider.cluster devnet
   
   # Start frontend applications
   cd applications && npm start
   ```

### Running the Tests

#### Option 1: Pytest Integration

```bash
# Run comprehensive E2E test via pytest
pytest tests/e2e/test_comprehensive_end_to_end.py -v -s

# Run with specific markers
pytest tests/e2e/ -m "e2e" -v
pytest tests/e2e/ -m "performance" -v
pytest tests/e2e/ -m "security" -v

# Run multimodal VL integration tests
pytest tests/e2e/test_multimodal_vl_integration.py -v

# Run only integration tests (requires deployed services)
pytest tests/e2e/ -m "integration" -v

# Skip integration tests (mock tests only)
pytest tests/e2e/ -m "not integration" -v
```

#### Option 2: Standalone Execution

```bash
# Run complete test suite
python tests/e2e/test_comprehensive_end_to_end.py

# Run with comprehensive runner
python tests/e2e/run_comprehensive_e2e_test.py
```

#### Option 3: Targeted Testing

```bash
# Test only services
python tests/e2e/run_comprehensive_e2e_test.py --services-only

# Test only blockchain
python tests/e2e/run_comprehensive_e2e_test.py --blockchain-only

# Test with performance benchmarking
python tests/e2e/run_comprehensive_e2e_test.py --performance

# Test with security validation
python tests/e2e/run_comprehensive_e2e_test.py --security

# Generate HTML report
python tests/e2e/run_comprehensive_e2e_test.py --report-format html
```

## 📊 Test Scenarios

### 1. Democratic Policy Creation Workflow

**Scenario**: Multi-stakeholder policy creation with constitutional validation

```python
# Test Flow:
1. User authentication and role assignment
2. Constitutional principle creation and validation
3. Policy synthesis using GS service
4. Multi-model validation (GPT-4, Claude, Gemini)
5. Stakeholder consensus building
6. Policy deployment to blockchain
7. Enforcement setup via PGC service
```

**Validation Criteria**:
- ✅ All services respond within 500ms
- ✅ Blockchain operations cost <0.01 SOL
- ✅ Constitutional compliance score >0.8
- ✅ Multi-model consensus achieved

### 2. Emergency Governance Procedures

**Scenario**: Rapid response to security incidents

```python
# Test Flow:
1. Emergency situation detection
2. Authority validation and escalation
3. Rapid policy creation and deployment
4. Audit trail generation
5. Recovery and normalization
```

**Validation Criteria**:
- ✅ Emergency response time <2s
- ✅ Authority validation successful
- ✅ Complete audit trail maintained
- ✅ System recovery within 30s

### 3. Appeals and Dispute Resolution

**Scenario**: Policy violation appeal processing

```python
# Test Flow:
1. Policy violation detection
2. Appeal submission with evidence
3. Human-in-the-loop review process
4. Resolution and enforcement update
5. Transparency reporting
```

**Validation Criteria**:
- ✅ Appeal processing workflow complete
- ✅ Evidence integrity maintained
- ✅ Resolution properly documented
- ✅ Transparency requirements met

## 🔧 Configuration

### Test Configuration

```python
# tests/e2e/test_comprehensive_end_to_end.py
test_config = {
    "max_response_time_ms": 500,
    "max_blockchain_cost_sol": 0.01,
    "min_success_rate": 0.9,
    "constitutional_hash": "cdd01ef066bc6cf2",
    "test_timeout_seconds": 300
}
```

### Service Endpoints

```python
services = {
    "auth": "http://localhost:8000",      # Authentication
    "ac": "http://localhost:8001",        # Constitutional AI
    "integrity": "http://localhost:8002", # Integrity Service
    "fv": "http://localhost:8003",        # Formal Verification
    "gs": "http://localhost:8004",        # Governance Synthesis
    "pgc": "http://localhost:8005",       # Policy Governance
    "ec": "http://localhost:8006",        # Evolutionary Computation
    "dgm": "http://localhost:8007"        # Darwin Gödel Machine
}
```

## 📈 Performance Targets

| **Metric** | **Target** | **Validation** |
|------------|------------|----------------|
| **Service Response Time** | <500ms | ✅ All endpoints |
| **Blockchain Cost** | <0.01 SOL | ✅ Per operation |
| **Test Success Rate** | >90% | ✅ Overall suite |
| **Constitutional Compliance** | >0.8 | ✅ All policies |
| **Frontend Load Time** | <2s | ✅ All pages |

## 🔒 Security Validation

### Authentication & Authorization
- ✅ JWT token validation
- ✅ Role-based access control
- ✅ Session management
- ✅ Multi-factor authentication

### Cryptographic Security
- ✅ Encryption strength (AES-256)
- ✅ Digital signature validation
- ✅ Key management security
- ✅ Data integrity verification

### Constitutional Compliance
- ✅ Principle adherence validation
- ✅ Bias detection and mitigation
- ✅ Transparency requirements
- ✅ Accountability mechanisms

## 📋 Test Reports

### JSON Report Structure

```json
{
  "execution_metadata": {
    "start_time": "2025-06-20T10:00:00Z",
    "total_duration_seconds": 120.5,
    "test_runner_version": "3.0"
  },
  "service_integration": {
    "total_tests": 24,
    "successful_tests": 22,
    "success_rate": 0.92
  },
  "blockchain_integration": {
    "deployments": [...],
    "test_results": [...],
    "total_cost_sol": 0.028
  },
  "end_to_end_workflows": {
    "success": true,
    "constitutional_compliance": 0.95,
    "failed_tests": []
  },
  "summary": {
    "overall_success": true,
    "key_metrics": {...}
  }
}
```

### Report Locations

```bash
# Test reports saved to:
tests/results/
├── comprehensive_e2e_report_20250620_100000.json
├── service_integration_details.json
├── blockchain_test_results.json
├── performance_benchmarks.json
└── security_validation_report.json

# Logs saved to:
tests/logs/
├── e2e_test_execution.log
├── service_integration.log
└── blockchain_integration.log
```

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Services not responding
```bash
# Solution: Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health
# ... check all 8 services
```

**Issue**: Blockchain deployment fails
```bash
# Solution: Check Solana configuration
solana config get
solana balance
anchor build && anchor deploy
```

**Issue**: Frontend automation fails
```bash
# Solution: Check frontend server
curl http://localhost:3000
# Ensure React/Next.js dev server is running
```

### Debug Mode

```bash
# Run tests with debug logging
PYTHONPATH=. python tests/e2e/test_comprehensive_end_to_end.py --log-level DEBUG

# Run with verbose output
pytest tests/e2e/ -v -s --tb=long
```

## 🤝 Contributing

1. **Adding New Test Scenarios**:
   ```python
   # Create new scenario in tests/e2e/scenarios/
   async def test_new_governance_scenario(self):
       # Implement test logic
       pass
   ```

2. **Extending Service Integration**:
   ```python
   # Add new service endpoints in modules/service_integration.py
   "new_service": {
       "port": 8008,
       "endpoints": {...}
   }
   ```

3. **Performance Benchmarks**:
   ```python
   # Add new performance tests in modules/performance_validation.py
   async def test_new_performance_scenario(self):
       # Implement performance validation
       pass
   ```

## 📞 Support

- **Documentation**: [docs/TESTING_GUIDE.md](../../docs/TESTING_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/CA-git-com-co/ACGS/issues)
- **Discord**: [ACGS Community](https://discord.gg/acgs)

---

**ACGS-1 E2E Testing**: Ensuring Constitutional AI Governance Excellence 🏛️✨
