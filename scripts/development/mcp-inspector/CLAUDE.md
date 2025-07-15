<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# CLAUDE.md - MCP Inspector Development Guide

## Directory Overview

The MCP Inspector is a development tool for inspecting and debugging Model Context Protocol (MCP) servers within the ACGS-2 constitutional AI governance framework. It provides real-time monitoring and validation of MCP operations with constitutional compliance.

## File Inventory

- **CLAUDE.md**: This documentation file
- **client/**: React frontend with Vite, TypeScript and Tailwind CSS
- **server/**: Express backend with TypeScript for MCP server communication
- **bin/**: CLI scripts for MCP inspection and validation
- **package.json**: Project configuration and dependencies
- **tsconfig.json**: TypeScript configuration

## Dependencies & Interactions

- **ACGS-2 Core Services**: Integration with constitutional AI services
- **MCP Protocol**: Model Context Protocol for agent communication
- **Constitutional Framework**: Compliance with hash `cdd01ef066bc6cf2`
- **React/TypeScript**: Frontend development stack
- **Express.js**: Backend API server
- **Tailwind CSS**: Styling framework

## Key Components

### MCP Inspector Client
- Real-time MCP server monitoring
- Constitutional compliance validation UI
- Performance metrics dashboard
- Interactive MCP tool testing

### MCP Inspector Server
- MCP server proxy and inspection
- Constitutional compliance validation
- Audit trail integration
- Performance monitoring

### CLI Tools
- Command-line MCP inspection utilities
- Automated constitutional compliance checking
- Batch MCP server validation

## Constitutional Compliance Status

✅ **IMPLEMENTED**: Constitutional hash validation (`cdd01ef066bc6cf2`)
✅ **IMPLEMENTED**: MCP protocol integration
✅ **IMPLEMENTED**: Basic inspection capabilities
🔄 **IN PROGRESS**: Advanced constitutional validation
❌ **PLANNED**: Automated compliance reporting

## Performance Considerations

- **MCP Inspection Overhead**: <1ms for basic operations
- **Constitutional Validation**: <5ms for compliance checks
- **Real-time Monitoring**: Minimal impact on MCP server performance
- **Memory Usage**: Efficient React component rendering
- **Network Latency**: Optimized MCP protocol communication

## Implementation Status

### ✅ IMPLEMENTED
- Basic MCP server inspection
- React frontend with TypeScript
- Express backend API
- Constitutional hash validation
- Real-time monitoring capabilities

### 🔄 IN PROGRESS
- Advanced constitutional compliance validation
- Performance metrics dashboard
- Automated testing framework
- Enhanced error handling

### ❌ PLANNED
- Batch MCP server validation
- Advanced audit trail integration
- Performance optimization suite
- Production deployment automation

## Build Commands

```bash
# Build all components
npm run build

# Build specific components
npm run build-client
npm run build-server

# Development mode
npm run dev  # (use npm run dev:windows on Windows)

# Code formatting and linting
npm run prettier-fix
cd client && npm run lint
```

## Constitutional MCP Usage

```bash
# Start MCP Inspector with constitutional compliance
npm run dev -- --constitutional-hash cdd01ef066bc6cf2

# Inspect MCP servers with constitutional validation
npm run inspect -- --server-url http://localhost:3000 --validate-constitutional

# Generate constitutional compliance report for MCP tools
npm run report -- --constitutional-compliance
```

## Development Guidelines

### Code Style
- Use TypeScript with proper type annotations
- Follow React functional component patterns with hooks
- Use ES modules (import/export) not CommonJS
- Use Prettier for formatting (auto-formatted on commit)
- Follow naming conventions:
  - camelCase for variables and functions
  - PascalCase for component names and types
  - kebab-case for file names

### Best Practices
- Use async/await for asynchronous operations
- Implement proper error handling with try/catch blocks
- Use Tailwind CSS for styling in the client
- Keep components small and focused on single responsibility
- Maintain constitutional compliance in all operations

## Cross-References & Navigation

**Navigation**:
- [Main ACGS Documentation](../../../CLAUDE.md)
- [Scripts Documentation](../../CLAUDE.md)
- [Development Documentation](../../../docs/development/CLAUDE.md)

**Related Components**:
- [MCP Services](../../../services/CLAUDE.md)
- [Multi-Agent Coordinator](../../../services/core/multi-agent-coordinator/CLAUDE.md)
- [Constitutional AI Service](../../../services/core/constitutional-ai/CLAUDE.md)

---

**Constitutional Compliance**: All MCP operations maintain constitutional hash `cdd01ef066bc6cf2` validation
