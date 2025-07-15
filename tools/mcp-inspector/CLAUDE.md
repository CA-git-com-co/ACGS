<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# CLAUDE.md - MCP Inspector Development Tool

## Directory Overview

The MCP Inspector is a comprehensive development tool for inspecting, debugging, and validating Model Context Protocol (MCP) servers within the ACGS-2 constitutional AI governance framework. It provides real-time monitoring, constitutional compliance validation, and performance analysis.

## File Inventory

- **CLAUDE.md**: This documentation file
- **client/**: React frontend with Vite, TypeScript and Tailwind CSS
- **server/**: Express backend with TypeScript for MCP server communication
- **bin/**: CLI scripts for MCP inspection and validation
- **package.json**: Project configuration and dependencies
- **tsconfig.json**: TypeScript configuration
- **README.md**: Project overview and setup instructions

## Dependencies & Interactions

- **ACGS-2 Core Services**: Integration with constitutional AI services
- **MCP Protocol**: Model Context Protocol for agent communication
- **Constitutional Framework**: Compliance with hash `cdd01ef066bc6cf2`
- **React/TypeScript**: Frontend development stack
- **Express.js**: Backend API server
- **Tailwind CSS**: Styling framework
- **Vite**: Build tool and development server

## Key Components

### MCP Inspector Client
- Real-time MCP server monitoring dashboard
- Constitutional compliance validation interface
- Performance metrics visualization
- Interactive MCP tool testing environment
- Error tracking and debugging tools

### MCP Inspector Server
- MCP server proxy and inspection engine
- Constitutional compliance validation middleware
- Audit trail integration with ACGS services
- Performance monitoring and metrics collection
- WebSocket communication for real-time updates

### CLI Tools
- Command-line MCP inspection utilities
- Automated constitutional compliance checking
- Batch MCP server validation
- Performance benchmarking tools

## Constitutional Compliance Status

✅ **IMPLEMENTED**: Constitutional hash validation (`cdd01ef066bc6cf2`)
✅ **IMPLEMENTED**: MCP protocol integration
✅ **IMPLEMENTED**: Basic inspection capabilities
✅ **IMPLEMENTED**: Real-time monitoring dashboard
🔄 **IN PROGRESS**: Advanced constitutional validation
🔄 **IN PROGRESS**: Performance optimization
❌ **PLANNED**: Automated compliance reporting
❌ **PLANNED**: Advanced audit trail integration

## Performance Considerations

- **MCP Inspection Overhead**: <1ms for basic operations
- **Constitutional Validation**: <5ms for compliance checks
- **Real-time Monitoring**: Minimal impact on MCP server performance
- **Memory Usage**: Efficient React component rendering with virtual scrolling
- **Network Latency**: Optimized MCP protocol communication
- **WebSocket Performance**: Sub-100ms update latency for real-time monitoring

## Implementation Status

### ✅ IMPLEMENTED
- Basic MCP server inspection and monitoring
- React frontend with TypeScript and Tailwind CSS
- Express backend API with MCP integration
- Constitutional hash validation throughout
- Real-time monitoring capabilities
- CLI tools for basic inspection

### 🔄 IN PROGRESS
- Advanced constitutional compliance validation
- Performance metrics dashboard enhancement
- Automated testing framework
- Enhanced error handling and debugging
- WebSocket optimization for real-time updates

### ❌ PLANNED
- Batch MCP server validation tools
- Advanced audit trail integration with ACGS
- Performance optimization suite
- Production deployment automation
- Advanced security scanning capabilities

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

# Testing
npm run test
npm run test:coverage
```

## Constitutional MCP Usage

```bash
# Start MCP Inspector with constitutional compliance
npm run dev -- --constitutional-hash cdd01ef066bc6cf2

# Inspect MCP servers with constitutional validation
npm run inspect -- --server-url http://localhost:3000 --validate-constitutional

# Generate constitutional compliance report for MCP tools
npm run report -- --constitutional-compliance

# Batch validation of multiple MCP servers
npm run validate-batch -- --config mcp-servers.json --constitutional
```

## Development Guidelines

### Code Style Standards
- Use TypeScript with strict type annotations
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
- Include comprehensive TypeScript types
- Write unit tests for all critical functionality

### Project Organization
The project is organized as a monorepo with workspaces:
- `client/`: React frontend with Vite, TypeScript and Tailwind
- `server/`: Express backend with TypeScript
- `bin/`: CLI scripts and utilities

## Cross-References & Navigation

**Navigation**:
- [Main ACGS Documentation](../../CLAUDE.md)
- [Tools Documentation](../CLAUDE.md)
- [Development Documentation](../../docs/development/CLAUDE.md)

**Related Components**:
- [MCP Services](../../services/CLAUDE.md)
- [Multi-Agent Coordinator](../../services/core/multi-agent-coordinator/CLAUDE.md)
- [Constitutional AI Service](../../services/core/constitutional-ai/CLAUDE.md)
- [Scripts Development](../../scripts/development/CLAUDE.md)

**External References**:
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Constitutional Compliance**: All MCP operations maintain constitutional hash `cdd01ef066bc6cf2` validation
