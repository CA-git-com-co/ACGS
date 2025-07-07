# Constitutional Core Service

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

The Constitutional Core Service unifies constitutional AI and formal verification capabilities into a single, powerful service. This consolidation reduces service sprawl while providing comprehensive constitutional compliance and formal verification.

## Features

### Constitutional AI (from ac_service)
- Constitutional principle validation and enforcement
- AI-based constitutional reasoning and interpretation
- Constitutional amendment lifecycle management
- Stakeholder engagement and democratic governance
- Human-in-the-loop constitutional decision making
- Multi-model constitutional consensus
- Constitutional reward modeling

### Formal Verification (from fv_service)
- Z3 SMT solver integration for mathematical proofs
- Formal specification validation
- Policy compliance verification
- Cryptographic signature validation
- Proof obligation generation and verification
- Cross-domain testing and validation
- Adversarial robustness testing

### Unified Capabilities
- Constitutional compliance scoring with formal mathematical backing
- Formal verification of constitutional principles
- Mathematically proven constitutional compliance
- Integrated audit trails with cryptographic integrity
- Constitutional-aware formal specifications

## Architecture

```
constitutional-core/
├── app/
│   ├── api/v1/                    # Unified API endpoints
│   │   ├── constitutional/        # Constitutional AI endpoints
│   │   ├── verification/          # Formal verification endpoints
│   │   ├── principles/            # Constitutional principles
│   │   ├── proofs/               # Mathematical proofs
│   │   └── compliance/           # Unified compliance
│   ├── core/                      # Core business logic
│   │   ├── constitutional/        # Constitutional reasoning
│   │   ├── verification/          # Formal verification
│   │   ├── solvers/              # Z3 and SMT solvers
│   │   └── unified/              # Unified constitutional-formal logic
│   ├── services/                  # Service layer
│   ├── models/                    # Data models
│   └── main.py                    # Application entry point
├── config/                        # Configuration
├── tests/                         # Test suite
└── Dockerfile                     # Container definition
```

## Port Assignment

- **Port 8001**: Constitutional Core Service (replaces both 8001 and 8003)

## Migration

This service replaces:
- `services/core/constitutional-ai/` (port 8001)
- `services/core/formal-verification/` (port 8003)

All existing APIs are preserved with backward compatibility.

## Key Benefits

1. **Unified Constitutional Reasoning**: Combines AI reasoning with mathematical proofs
2. **Formal Constitutional Verification**: Mathematical proof of constitutional compliance
3. **Reduced Complexity**: Single service for all constitutional and verification needs
4. **Enhanced Accuracy**: Cross-validation between AI and formal methods
5. **Better Performance**: Direct integration eliminates network overhead