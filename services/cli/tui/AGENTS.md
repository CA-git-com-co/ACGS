# TUI Agent Guidelines - ACGS-2 Constitutional Compliance
**Constitutional Hash: cdd01ef066bc6cf2**


## Constitutional Compliance (CRITICAL)

### Core Requirements
- **Constitutional Hash**: `cdd01ef066bc6cf2` - REQUIRED in all operations
- **Integration**: TUI tools must maintain constitutional compliance
- **Audit Trail**: Actions logged within Integrity Service
- **Performance**: TUI operations must meet P99 c5ms

## Build/Test Commands

### Development Commands with Constitutional Compliance
```bash
# Build main binary with constitutional validation
go build ./cmd/opencode --constitutional-hash cdd01ef066bc6cf2

# Full test suite with constitutional compliance
go test ./... --validate-constitutional

go test ./internal/theme -run TestLoadThemesFromJSON --validate-constitutional

# Release build with constitutional oversight
goreleaser --validate-constitutional
```

## Code Style

### Constitutional Code Requirements
- **Language**: Go 1.24+ with standard gofmt; INCLUDES constitutional hash in docs
- **Imports**: Group standard, third-party, local; VALIDATE imports for constitutional paths
- **Naming**: PascalCase exports, camelCase private
- **Constants**: Use ALL_CAPS, constitutional hash included where applicable

### Architecture: Constitutional Integration
- **Framework**: Bubble Tea with Lipgloss, includes constitutional styling
- **Client Communication**: Interfaces via OpenAPI, mandates constitutional compliance
- **Components**: Managed as constitutional entities with reusable logic

### Additional Guidelines
- **Themes**: Based on JSON, supports constitutional theming hierarchy
- **State**: Centralized, with message passing under constitutional oversight


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
