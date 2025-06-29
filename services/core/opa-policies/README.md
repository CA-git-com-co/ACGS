# ACGS-1 Lite Constitutional Policies

Comprehensive Open Policy Agent (OPA) policies encoding constitutional principles, safety rules, evolution controls, and data privacy protections for the ACGS-1 Lite governance system.

## 🎯 Overview

This policy bundle implements the constitutional framework for ACGS-1 Lite, providing automated decision-making capabilities for:

- **Constitutional Compliance**: Core principles of autonomy, beneficence, non-maleficence, transparency, fairness, privacy, and accountability
- **Safety Enforcement**: Critical safety patterns, behavioral analysis, and isolation requirements  
- **Evolution Control**: Multi-tier approval workflows with risk assessment and rollback requirements
- **Data Privacy**: Classification-based access control, consent management, and encryption requirements

**Constitutional Hash**: `cdd01ef066bc6cf2`
**Policy Version**: 1.0.0
**OPA Compatibility**: 0.50.0+

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main Entry    │    │  Constitutional │    │   Evolution     │
│     Point       │────┤    Policies     │    │   Policies      │
│                 │    │                 │    │                 │
│ • Route Request │    │ • Core Principles│    │ • Approval Rules│
│ • Hash Verify   │    │ • Safety Rules  │    │ • Risk Assessment│
│ • Allow/Deny    │    │ • Resource Limits│   │ • Rollback Req  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Privacy  │
                       │    Policies     │
                       │                 │
                       │ • Classification│
                       │ • Consent Mgmt  │
                       │ • Data Minimization│
                       │ • Encryption    │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- OPA 0.50.0 or later
- Basic familiarity with Rego policy language

### 1. Installation

```bash
# Install OPA
curl -L -o opa https://openpolicyagent.org/downloads/v0.50.0/opa_linux_amd64_static
chmod +x opa
sudo mv opa /usr/local/bin/

# Clone and build policies
git clone <repository>
cd services/core/opa-policies
```

### 2. Build and Test

```bash
# Run comprehensive test suite
./test.sh

# Build optimized policy bundle
./build.sh
```

### 3. Deploy

```bash
# Start OPA server with policies
opa run --server --bundle build/acgs-constitutional-policies-1.0.0.tar.gz

# Test deployment
curl http://localhost:8181/v1/data/acgs/main/health
```

## 📡 API Reference

### Main Decision Endpoint

**POST** `/v1/data/acgs/main/decision`

```json
{
  "input": {
    "type": "constitutional_evaluation",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "action": "data.read_public",
    "context": {
      "environment": {
        "sandbox_enabled": true,
        "audit_enabled": true
      },
      "agent": {
        "trust_level": 0.9,
        "requested_resources": {
          "cpu_cores": 1,
          "memory_gb": 2
        }
      },
      "responsible_party": "system_admin",
      "explanation": "Reading public data for dashboard display"
    }
  }
}
```

**Response:**
```json
{
  "result": {
    "allow": true,
    "compliance_score": 0.96,
    "constitutional_hash": "cdd01ef066bc6cf2",
    "reasons": [],
    "evaluation_details": {
      "safety": {"passed": true, "score": 1.0},
      "constitutional": {"passed": true, "score": 0.95},
      "resources": {"passed": true, "score": 1.0},
      "transparency": {"passed": true, "score": 0.9}
    }
  }
}
```

### Evolution Approval

**POST** `/v1/data/acgs/main/decision`

```json
{
  "input": {
    "type": "evolution_approval",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "evolution_request": {
      "type": "patch",
      "constitutional_hash": "cdd01ef066bc6cf2",
      "changes": {
        "code_changes": ["Minor bug fix"],
        "external_dependencies": [],
        "privilege_escalation": false,
        "experimental_features": false
      },
      "performance_analysis": {
        "complexity_delta": 0.02,
        "memory_delta": 0.01,
        "latency_delta": -0.05,
        "resource_delta": 0.0
      },
      "rollback_plan": {
        "procedure": "Automated rollback via git revert",
        "verification": "Unit tests + smoke tests",
        "timeline": "< 5 minutes",
        "dependencies": "None",
        "tested": true,
        "automated": true
      }
    }
  }
}
```

### Data Access Control

**POST** `/v1/data/acgs/main/decision`

```json
{
  "input": {
    "type": "data_access",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "data_request": {
      "data_fields": [
        {
          "name": "user_email",
          "classification_level": 2,
          "category": "personal_identifiable_information"
        }
      ],
      "requester_clearance_level": 3,
      "special_authorization": true,
      "data_subjects": ["user123"],
      "consent_records": [
        {
          "subject_id": "user123",
          "status": "granted",
          "allowed_purposes": ["user_communication"],
          "expiry_time": 1735689600
        }
      ],
      "purpose": "user_communication",
      "allowed_purposes": ["user_communication"],
      "justified_fields": ["user_email"],
      "timestamp": 1704067200,
      "retention_policy": {
        "personal_identifiable_information": 2592000
      },
      "encryption_config": {
        "user_email": {
          "encrypted": true,
          "algorithm": "AES",
          "key_length": 256
        },
        "key_management": {
          "rotation_enabled": true,
          "secure_storage": true,
          "access_controlled": true
        }
      }
    }
  }
}
```

### Health Check

**GET** `/v1/data/acgs/main/health`

```json
{
  "result": {
    "status": "healthy",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "policies_loaded": [
      "acgs.constitutional",
      "acgs.evolution",
      "acgs.data",
      "acgs.main"
    ]
  }
}
```

## 📋 Policy Details

### Constitutional Policies (`acgs.constitutional`)

**Core Principles:**
- **Autonomy**: Respect user choice and consent
- **Beneficence**: Aim to benefit users and society
- **Non-maleficence**: Do not cause harm
- **Transparency**: Provide explainable decisions
- **Fairness**: Avoid unfair discrimination
- **Privacy**: Protect user data
- **Accountability**: Maintain audit trails

**Safety Rules:**
- **Critical Violations**: 25+ dangerous actions blocked (shell execution, privilege escalation, etc.)
- **High-Risk Patterns**: Additional authorization required for sensitive operations
- **Behavioral Analysis**: Suspicious pattern detection and response
- **Isolation Requirements**: Sandbox, network, and filesystem isolation enforcement
- **Temporal Constraints**: Business hours and rate limiting

**Resource Limits:**
- CPU: 2 cores maximum
- Memory: 4GB maximum
- Disk: 10GB maximum
- Network: 10 Mbps maximum
- Execution time: 300 seconds maximum

### Evolution Policies (`acgs.evolution`)

**Approval Thresholds:**
- **Auto-approval**: ≥95% score
- **Fast-track review**: 90-95% score
- **Full human review**: <90% score

**Risk Assessment:**
- **Base risk** by evolution type (minor_update: 0.1, architecture_change: 0.9)
- **Risk factors**: External dependencies, privilege changes, experimental features
- **Mitigation factors**: Sandbox deployment, gradual rollout, enhanced monitoring

**Requirements:**
- **Human approval**: Required for major updates and architecture changes
- **Security review**: Required for security-sensitive changes
- **Peer review**: Required for significant feature additions
- **Rollback plan**: Must include procedure, verification, timeline, testing

### Data Privacy Policies (`acgs.data`)

**Classification Levels:**
- **Public (0)**: No restrictions
- **Internal (1)**: Organization access only
- **Confidential (2)**: Limited access with authorization
- **Restricted (3)**: High clearance required
- **Top Secret (4)**: Maximum security clearance

**Sensitive Categories:**
- Personal identifiable information
- Financial information
- Health records
- Biometric data
- Authentication credentials
- Cryptographic keys

**Privacy Controls:**
- **Consent verification**: User consent status, purpose limitation, expiration tracking
- **Data minimization**: Excessive data detection, necessity justification
- **Retention policies**: Regulatory compliance, disposal procedures
- **Encryption requirements**: Algorithm strength, key management

## 🧪 Testing

### Run All Tests

```bash
# Complete test suite
./test.sh

# Individual test suites
opa test tests/constitutional_test.rego constitutional/ main.rego -v
opa test tests/evolution_test.rego evolution/ main.rego -v
opa test tests/data_privacy_test.rego data/ main.rego -v
```

### Test Coverage

- **Constitutional tests**: 30+ test cases covering all principles and safety rules
- **Evolution tests**: 25+ test cases covering approval workflows and risk assessment
- **Data privacy tests**: 20+ test cases covering classification, consent, and encryption
- **Integration tests**: End-to-end policy evaluation scenarios
- **Performance tests**: Sub-10ms average latency verification

### Example Test Cases

```bash
# Test dangerous action blocking
opa eval -d . -i '{"type":"constitutional_evaluation","constitutional_hash":"cdd01ef066bc6cf2","action":"system.execute_shell","context":{"environment":{"sandbox_enabled":true},"agent":{"trust_level":0.9}}}' 'data.acgs.main.decision.allow'
# Expected: false

# Test safe action allowance
opa eval -d . -i '{"type":"constitutional_evaluation","constitutional_hash":"cdd01ef066bc6cf2","action":"data.read_public","context":{"environment":{"sandbox_enabled":true,"audit_enabled":true},"agent":{"trust_level":0.9,"requested_resources":{"cpu_cores":1}},"responsible_party":"test","explanation":"Safe data read operation"}}' 'data.acgs.main.decision.allow'
# Expected: true
```

## 📊 Performance

### Benchmarks

- **Average latency**: <5ms per evaluation
- **P99 latency**: <10ms per evaluation
- **Throughput**: 1000+ evaluations/second
- **Memory usage**: <50MB for policy bundle
- **Bundle size**: <1MB compressed

### Optimization

The policies are built with OPA optimization level 2, including:
- **Partial evaluation**: Pre-compute static policy elements
- **Indexing**: O(1) lookups for action classification
- **Caching**: Reduce redundant computations
- **Bundle compression**: Minimize network transfer

## 🔧 Development

### Adding New Policies

1. **Create policy file** in appropriate directory (`constitutional/`, `evolution/`, `data/`)
2. **Follow naming convention**: `snake_case.rego`
3. **Include constitutional hash**: `cdd01ef066bc6cf2`
4. **Add comprehensive tests** in `tests/` directory
5. **Update documentation** and examples

### Policy Structure

```rego
# Standard header
package acgs.module_name

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Constitutional hash
constitutional_hash := "cdd01ef066bc6cf2"

# Main evaluation function
evaluate = response {
    # Policy logic here
    response := {
        "allow": true,
        "score": 1.0,
        "constitutional_hash": constitutional_hash
    }
}
```

### Testing Guidelines

- **Test both positive and negative cases**
- **Include edge cases and boundary conditions**
- **Verify constitutional hash in all responses**
- **Test performance with realistic inputs**
- **Document expected behavior**

## 🔐 Security

### Policy Security

- **Constitutional hash verification**: All policies verify `cdd01ef066bc6cf2`
- **Input validation**: Comprehensive input sanitization and validation
- **Fail-safe defaults**: Deny by default, explicit allow required
- **Audit logging**: All decisions are traceable
- **Immutable policies**: Policies cannot be modified at runtime

### Deployment Security

- **Bundle signing**: Verify policy bundle integrity
- **HTTPS enforcement**: Secure communication with OPA server
- **Access control**: Restrict policy administration access
- **Monitoring**: Real-time policy evaluation monitoring
- **Backup**: Regular policy bundle backups

## 🚀 Production Deployment

### Scaling

```bash
# Multiple OPA instances behind load balancer
docker run -d --name opa-1 -p 8181:8181 -v $(pwd)/build:/policies openpolicyagent/opa:latest run --server --bundle /policies/acgs-constitutional-policies-1.0.0.tar.gz
docker run -d --name opa-2 -p 8182:8181 -v $(pwd)/build:/policies openpolicyagent/opa:latest run --server --bundle /policies/acgs-constitutional-policies-1.0.0.tar.gz
```

### Monitoring

```bash
# Health check
curl http://localhost:8181/health

# Policy metrics
curl http://localhost:8181/metrics

# Decision logging
curl http://localhost:8181/v1/logs
```

### Updates

```bash
# Build new bundle
./build.sh

# Deploy with zero downtime
curl -X PUT http://localhost:8181/v1/policies/acgs --data-binary @build/acgs-constitutional-policies-1.0.0.tar.gz
```

## 📚 Resources

- [OPA Documentation](https://www.openpolicyagent.org/docs/)
- [Rego Language Reference](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [OPA Best Practices](https://www.openpolicyagent.org/docs/latest/policy-performance/)
- [ACGS-1 Lite Specification](../../docs/acgs-1-lite-spec.md)

## 📄 License

Constitutional AI Governance System (ACGS-1 Lite)
Constitutional Hash: `cdd01ef066bc6cf2`