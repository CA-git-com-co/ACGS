# ACGS Specialized Compose Stacks
# Constitutional Hash: cdd01ef066bc6cf2

This directory contains specialized Docker Compose stacks for specific use cases beyond the main ACGS services.

## Available Stacks

### MCP (Model Context Protocol) Stack
- **File**: `docker-compose.mcp.yml`
- **Purpose**: Model Context Protocol services for enhanced multi-agent coordination
- **Usage**: `docker-compose -f compose-stacks/docker-compose.mcp.yml up`
- **Services**:
  - MCP Aggregator (port 3000)
  - Filesystem MCP (port 3001)
  - GitHub MCP (port 3002)
  - Browser MCP (port 3003)

### Blockchain Integration Stack
- **File**: `docker-compose.blockchain.yml`
- **Purpose**: Blockchain services for constitutional compliance verification
- **Usage**: `docker-compose -f compose-stacks/docker-compose.blockchain.yml up`

### Enterprise Security Stack
- **File**: `docker-compose.enterprise-security.yml`
- **Purpose**: Enhanced security services for enterprise deployments
- **Usage**: `docker-compose -f compose-stacks/docker-compose.enterprise-security.yml up`

### Machine Learning Stack
- **File**: `docker-compose.ml.yml`
- **Purpose**: ML/AI services for advanced governance analytics
- **Usage**: `docker-compose -f compose-stacks/docker-compose.ml.yml up`

## Integration with Main ACGS

These stacks are designed to work alongside the main ACGS services:

```bash
# Start core ACGS services
docker-compose -f docker-compose.base.yml -f docker-compose.services.yml up -d

# Add monitoring
docker-compose -f docker-compose.base.yml -f docker-compose.services.yml -f docker-compose.monitoring.yml up -d

# Add specialized stack (e.g., MCP)
docker-compose -f compose-stacks/docker-compose.mcp.yml up -d
```

## Constitutional Compliance

All specialized stacks maintain constitutional compliance with hash `cdd01ef066bc6cf2` and integrate with the main ACGS Constitutional AI service for validation.
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
