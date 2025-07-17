# OpenCode Agent Guidelines - ACGS-2 Constitutional Compliance
**Constitutional Hash: cdd01ef066bc6cf2**


## Constitutional Compliance (CRITICAL)

### Core Requirements
- **Constitutional Hash**: `cdd01ef066bc6cf2` - REQUIRED for all operations
- **Integration**: OpenCode tools must maintain constitutional compliance
- **Audit Trail**: All actions logged through Integrity Service
- **Performance**: OpenCode operations must meet P99 c5ms

## Build/Test Commands

### Development Commands
```bash
# Setup environment with constitutional compliance
bun install --check-constitutional

# Run and validate constitutional compliance
bun run index.ts --constitutional-hash cdd01ef066bc6cf2

# Typecheck and validate constitutional compliance
bun run typecheck --validate-constitutional

# Full test suite with constitutional validation
bun test --constitutional
bun test test/tool/tool.test.ts --validate-hash
```

## Code Style

### Constitutional Code Requirements
- **TypeScript**: ESM modules with strict types
- **Zod**: Comprehensive schemas for validation with constitutional hash check
- **Naming**: camelCase variables, PascalCase classes; MANDATORY constitutional hash in docstrings
- **Error Handling**: Use Result patterns with `constitutional_error`, avoid exceptions where possible

### Code Quality Standards
- **Imports**: Relative imports for local modules, named imports preferred
- **File Structure**: Namespace-based organization
- **Environment**: Bun with TypeScript ESM modules

## Architecture

### Constitutional Integration
- **Tools**: `Tool.Info` interface with `execute()` + constitutional compliance
- **Context**: Pass `sessionID` in tool context, utilize `App.provide()` for DI
- **Storage**: `Storage` namespace with constitutional metadata

### API Client:: Constitutional Compliance
- **Communication**: OpenCode TUI interfaces with TypeScript server via constitutional SDK
- **Client Changes**: Server changes require new constitutional client SDK generation for compliance


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
