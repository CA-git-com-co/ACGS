# OpenCode CLI with ACGS Integration
**Constitutional Hash: cdd01ef066bc6cf2**


This is the ACGS-integrated version of OpenCode CLI, providing constitutional compliance and governance for AI coding operations.

## Features

- **Constitutional Compliance**: All operations validated against constitutional principles (hash: cdd01ef066bc6cf2)
- **Performance Monitoring**: Sub-5ms P99 latency targets with comprehensive metrics
- **Audit Trail**: Complete operation logging for transparency and accountability
- **ACGS Service Integration**: Connected to all 7 ACGS core services
- **Human-in-the-Loop**: High-risk operations require human approval

## Quick Start

```bash
# Start with ACGS compliance
npm run start

# Check ACGS services health
npm run acgs-health

# Development mode
npm run dev
```

## ACGS Services Integration

The CLI integrates with these ACGS services:

- **Auth Service** (port 8016): Authentication and authorization
- **Constitutional AI** (port 8001): Constitutional validation
- **Integrity Service** (port 8002): Audit trail and data integrity
- **Formal Verification** (port 8003): Mathematical proof validation
- **Governance Synthesis** (port 8004): Policy synthesis and enforcement
- **Policy Governance** (port 8005): Governance decision making
- **Evolutionary Computation** (port 8006): Adaptive optimization

## Commands

### Core Commands

- `opencode run [message]` - Run OpenCode with constitutional compliance
- `opencode generate` - Generate OpenAPI specs with ACGS validation
- `opencode tui` - Terminal UI mode with compliance monitoring
- `opencode --acgs-health` - Check ACGS services status

### ACGS-Specific Options

- `--acgs-health` - Display health status of all ACGS services
- `--print-logs` - Print detailed logs including ACGS operations

## Configuration

The CLI uses `acgs-config.json` for ACGS integration:

```json
{
  "acgs": {
    "constitutional_hash": "cdd01ef066bc6cf2",
    "services": {
      "auth_service_url": "http://localhost:8016",
      "constitutional_ai_url": "http://localhost:8001",
      ...
    },
    "performance_targets": {
      "p99_latency_ms": 5,
      "cache_hit_rate": 0.85,
      "throughput_rps": 1000
    }
  }
}
```

## Constitutional Principles

All operations are validated against these principles:

- **Safety First**: High-risk operations blocked by default
- **Operational Transparency**: All actions logged and auditable
- **User Consent**: Explicit approval for sensitive operations
- **Data Privacy**: Privacy-preserving operation handling
- **Resource Constraints**: Efficient resource utilization
- **Operation Reversibility**: Support for operation rollback
- **Least Privilege**: Minimal permission sets


## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

- **P99 Latency**: Sub-5ms response time
- **Cache Hit Rate**: >85% for frequently accessed data
- **Throughput**: 1000+ requests per second capacity

## Architecture

```
OpenCode CLI
├── ACGS Middleware Layer
│   ├── Constitutional Compliance
│   ├── Performance Monitoring
│   └── Audit Logging
├── Core Commands (run, generate, tui, etc.)
└── ACGS Service Integration
    ├── Constitutional AI Validation
    ├── Formal Verification
    ├── Governance Policy Checks
    └── Integrity Audit Trail
```

## Security

- All operations validated against constitutional hash `cdd01ef066bc6cf2`
- Comprehensive audit trail for all CLI actions
- Integration with ACGS security framework
- Human approval required for high-risk operations

## Development

```bash
# Type checking
npm run typecheck

# Development with hot reload
npm run dev

# Health check during development
npm run acgs-health
```

## Integration with ACGS

This CLI is fully integrated with the Automated Constitutional Governance System (ACGS-2), providing:

1. **Real-time Constitutional Validation**: Every command validated against constitutional principles
2. **Performance Compliance**: Continuous monitoring against ACGS performance targets
3. **Governance Integration**: Policy enforcement through ACGS governance services
4. **Audit Compliance**: Complete operation history for regulatory compliance

For more information about ACGS-2, see the main project documentation.
