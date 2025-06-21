# MCP Inspector Integration for ACGS-1

## Overview

The MCP Inspector has been integrated into ACGS-1 to provide comprehensive testing and debugging capabilities for our Model Context Protocol (MCP) servers. This integration enables rapid development, testing, and validation of constitutional governance MCP implementations.

## Integration Benefits

### 🎯 **Constitutional Governance Testing**

- **Interactive Policy Testing**: Test policy synthesis and compliance checking workflows
- **Constitutional Validation**: Validate constitutional governance MCP server implementations
- **Real-time Debugging**: Debug policy enforcement and governance decision flows
- **Compliance Verification**: Verify PGC (Policy-Governance-Compliance) operations

### 🔧 **Development Acceleration**

- **Rapid Prototyping**: Quick iteration on MCP server features
- **Visual Debugging**: Browser-based interface for complex governance workflows
- **Automated Testing**: CLI mode integration for CI/CD pipelines
- **Configuration Export**: Generate `mcp.json` files for client integration

### 🔒 **Security & Authentication**

- **Bearer Token Support**: Secure authentication for production MCP servers
- **Transport Flexibility**: Support for stdio, SSE, and streamable-http protocols
- **Environment Isolation**: Safe testing environment for governance operations

## Usage Scenarios for ACGS-1

### 1. **Constitutional Governance Server Testing**

```bash
# Test ACGS-1 constitutional governance MCP server
cd blockchain/quantumagi-deployment
npx @modelcontextprotocol/inspector node build/governance-server.js

# With environment variables for Solana configuration
npx @modelcontextprotocol/inspector \
  -e SOLANA_RPC_URL=https://api.devnet.solana.com \
  -e ANCHOR_WALLET=/path/to/wallet.json \
  node build/governance-server.js
```

### 2. **Policy Synthesis Engine Testing**

```bash
# Test policy synthesis with research capabilities
npx @modelcontextprotocol/inspector \
  -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
  -e PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY \
  node build/policy-synthesis-server.js
```

### 3. **CLI Mode for CI/CD Integration**

```bash
# Automated testing in CI/CD pipelines
npx @modelcontextprotocol/inspector --cli \
  node build/governance-server.js \
  --method tools/list

# Test specific governance tools
npx @modelcontextprotocol/inspector --cli \
  node build/governance-server.js \
  --method tools/call \
  --tool-name validate_constitution \
  --tool-arg constitution_hash=cdd01ef066bc6cf2
```

### 4. **Configuration File Usage**

Create `tools/mcp-inspector/acgs-config.json`:

```json
{
  "mcpServers": {
    "governance-server": {
      "command": "node",
      "args": ["build/governance-server.js"],
      "env": {
        "SOLANA_RPC_URL": "https://api.devnet.solana.com",
        "ANCHOR_WALLET": "/path/to/wallet.json"
      }
    },
    "policy-synthesis": {
      "command": "node",
      "args": ["build/policy-synthesis-server.js"],
      "env": {
        "OPENROUTER_API_KEY": "your-key",
        "PERPLEXITY_API_KEY": "your-key"
      }
    }
  }
}
```

```bash
# Use configuration file
npx @modelcontextprotocol/inspector \
  --config tools/mcp-inspector/acgs-config.json \
  --server governance-server
```

## ACGS-1 Specific Features

### **Constitutional Governance Workflows**

1. **Constitution Validation**

   - Test constitution hash verification
   - Validate constitutional compliance checks
   - Debug policy-constitution alignment

2. **Policy Synthesis Testing**

   - Test multi-model consensus mechanisms
   - Validate policy generation workflows
   - Debug risk assessment algorithms

3. **Compliance Checking**
   - Test PGC validation functions
   - Verify governance decision flows
   - Debug constitutional enforcement

### **Integration with ACGS-1 Services**

- **Auth Service (Port 8000)**: Test authentication workflows
- **AC Service (Port 8001)**: Test access control mechanisms
- **Integrity Service (Port 8002)**: Test data integrity validation
- **FV Service (Port 8003)**: Test formal verification processes
- **GS Service (Port 8004)**: Test governance synthesis operations
- **PGC Service (Port 8005)**: Test policy-governance-compliance
- **EC Service (Port 8006)**: Test enforcement and compliance

## Performance Targets

- **Response Time**: < 2s for 95% of governance operations
- **Throughput**: Support > 1000 concurrent governance actions
- **Availability**: > 99.5% uptime for testing infrastructure
- **Cost Efficiency**: < 0.01 SOL per governance validation

## Security Considerations

### **Development Environment**

- Use devnet Solana endpoints for testing
- Isolate test wallets from production funds
- Validate all governance operations in sandbox

### **Production Testing**

- Use bearer token authentication for production servers
- Implement rate limiting for governance operations
- Monitor and log all constitutional compliance checks

## CI/CD Integration

Add to `.github/workflows/mcp-testing.yml`:

```yaml
name: MCP Server Testing
on: [push, pull_request]

jobs:
  test-mcp-servers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"

      - name: Test Governance Server
        run: |
          npx @modelcontextprotocol/inspector --cli \
            node build/governance-server.js \
            --method tools/list

      - name: Test Policy Synthesis
        run: |
          npx @modelcontextprotocol/inspector --cli \
            node build/policy-synthesis-server.js \
            --method tools/call \
            --tool-name synthesize_policy \
            --tool-arg context="test governance scenario"
```

## Next Steps

1. **Implement ACGS-1 MCP Servers**: Develop constitutional governance MCP servers
2. **Create Test Configurations**: Set up comprehensive test scenarios
3. **Integrate with CI/CD**: Add automated MCP testing to pipelines
4. **Document Workflows**: Create detailed testing procedures
5. **Performance Optimization**: Tune for ACGS-1 performance targets

## Support

For ACGS-1 specific MCP Inspector usage:

- Review `tools/mcp-inspector/README.md` for general usage
- Check ACGS-1 documentation for governance workflows
- Use CLI mode for automated testing and CI/CD integration
- Leverage UI mode for interactive development and debugging

---

**Integration Status**: ✅ Complete - Ready for ACGS-1 MCP server development and testing
