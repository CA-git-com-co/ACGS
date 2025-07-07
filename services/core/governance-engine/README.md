# Unified Governance Engine Service

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

The Unified Governance Engine combines the functionality of:
- **Governance Synthesis Service** (formerly gs_service, port 8004)
- **Policy Governance & Compliance Service** (formerly pgc_service, port 8005)

This consolidation reduces service sprawl while maintaining all core functionality.

## Features

### Governance Synthesis (from gs_service)
- Policy synthesis using OPA engine
- Multi-model coordination and consensus
- Constitutional compliance validation
- Performance optimization and caching
- LLM integration for policy generation

### Policy Governance & Compliance (from pgc_service)
- Policy enforcement and compliance checking
- Real-time compliance monitoring
- Incremental policy compilation
- Quantum-enhanced policy enforcement
- Ultra-low latency optimization

## Architecture

```
governance-engine/
├── app/
│   ├── api/v1/                    # Unified API endpoints
│   │   ├── synthesis/             # Policy synthesis endpoints
│   │   ├── enforcement/           # Policy enforcement endpoints
│   │   ├── compliance/            # Compliance monitoring
│   │   └── workflows/             # Governance workflows
│   ├── core/                      # Core business logic
│   │   ├── synthesis/             # Synthesis engine
│   │   ├── enforcement/           # Enforcement engine
│   │   ├── compliance/            # Compliance engine
│   │   └── shared/                # Shared utilities
│   ├── services/                  # Service layer
│   ├── models/                    # Data models
│   └── main.py                    # Application entry point
├── config/                        # Configuration
├── tests/                         # Test suite
└── Dockerfile                     # Container definition
```

## Port Assignment

- **Port 8004**: Unified Governance Engine (replaces both 8004 and 8005)

## Migration

This service replaces:
- `services/core/governance-synthesis/` (port 8004)
- `services/core/policy-governance/` (port 8005)

All existing APIs are preserved with backward compatibility.