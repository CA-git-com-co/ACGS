# ACGS-1 Backend Services

This directory contains the backend service organization structure for the ACGS-1 Constitutional Governance System.

## Directory Structure

```
services/
├── core/                   # Core governance services
│   ├── auth/              # Authentication Service
│   ├── ac/                # Audit & Compliance Service
│   ├── integrity/         # Integrity Service
│   ├── fv/                # Formal Verification Service
│   ├── gs/                # Governance Synthesis Service
│   ├── pgc/               # Prompt Governance Compiler Service
│   └── ec/                # Evolutionary Computation Service
├── platform/              # Platform services
│   ├── monitoring/        # Monitoring & Observability
│   ├── logging/           # Centralized Logging
│   ├── backup/            # Backup & Recovery
│   └── analytics/         # Analytics & Reporting
├── shared/                # Shared libraries and utilities
│   ├── models/            # Data models
│   ├── utils/             # Utility functions
│   ├── middleware/        # Common middleware
│   └── config/            # Configuration management
└── tests/                 # Backend-specific tests
    ├── unit/              # Unit tests
    ├── integration/       # Integration tests
    └── fixtures/          # Test fixtures
```

## Service Architecture

### Core Services (7 ACGS-1 Services)

1. **Authentication Service (auth)** - Port 8000
   - User authentication and authorization
   - JWT token management
   - Role-based access control (RBAC)

2. **Audit & Compliance Service (ac)** - Port 8001
   - Constitutional principle management
   - Compliance validation
   - Audit trail generation

3. **Integrity Service (integrity)** - Port 8002
   - Data integrity validation
   - Cryptographic verification
   - System health monitoring

4. **Formal Verification Service (fv)** - Port 8003
   - Z3 SMT solver integration
   - Policy verification against principles
   - Safety property checking

5. **Governance Synthesis Service (gs)** - Port 8004
   - LLM-powered policy generation
   - Multi-model consensus engine
   - Policy synthesis workflows

6. **Prompt Governance Compiler Service (pgc)** - Port 8005
   - Real-time governance enforcement
   - Constitutional compliance checking
   - Policy compilation and execution

7. **Evolutionary Computation Service (ec)** - Port 8006
   - Adaptive governance algorithms
   - Policy optimization
   - System evolution management

### Platform Services

- **Monitoring** - System observability and metrics
- **Logging** - Centralized log aggregation
- **Backup** - Data backup and recovery
- **Analytics** - Performance and usage analytics

## Integration with Quantumagi

This backend structure integrates seamlessly with the Quantumagi Solana deployment:

- **Constitution Hash**: cdd01ef066bc6cf2
- **On-chain Programs**: quantumagi_core, appeals, logging
- **Off-chain Services**: All 7 core services provide governance support
- **Real-time Sync**: Event-driven synchronization with blockchain state

## Performance Targets

- **Response Times**: <500ms for 95% of requests
- **Availability**: >99.5% uptime
- **Throughput**: >1000 concurrent governance actions
- **Latency**: <50ms for PGC compliance checks

## Development Guidelines

1. Follow ACGS-1 enterprise standards
2. Implement proper error handling and logging
3. Use structured configuration management
4. Maintain >80% test coverage
5. Follow constitutional governance principles

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
python -m pytest services/tests/ -v

# Start services (development)
./scripts/start_services_simple.sh

# Health check
./scripts/comprehensive_health_check.sh
```

## Related Documentation

- [ACGS-1 Architecture](../../docs/architecture/)
- [Quantumagi Integration](../../blockchain/quantumagi-deployment/)
- [Service Deployment](../../infrastructure/)
- [Testing Guide](../../docs/testing/)
