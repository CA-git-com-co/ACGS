# MCP Inspector Development Guide - ACGS-2 Constitutional Compliance (Gemini)
**Constitutional Hash: cdd01ef066bc6cf2**


## Constitutional Compliance for MCP Inspector with Gemini

### Core Requirements
- **Constitutional Hash**: `cdd01ef066bc6cf2` - REQUIRED for all MCP operations
- **Gemini-MCP Integration**: All MCP tools must validate constitutional compliance for Gemini agents
- **Audit Trail**: Gemini MCP operations logged through ACGS Integrity Service
- **Performance**: Gemini MCP operations must meet P99 <5ms requirement

## Build Commands

- Build all: `npm run build`
- Build client: `npm run build-client`
- Build server: `npm run build-server`
- Development mode: `npm run dev` (use `npm run dev:windows` on Windows)
- Format code: `npm run prettier-fix`
- Client lint: `cd client && npm run lint`

## Gemini-Specific MCP Usage

```bash
# Start MCP Inspector with constitutional compliance for Gemini agents
npm run dev -- --agent-type gemini --constitutional-hash cdd01ef066bc6cf2

# Inspect Gemini-MCP integration with constitutional validation
npm run inspect -- --gemini-integration --validate-constitutional

# Generate constitutional compliance report for Gemini MCP usage
npm run report -- --gemini-report --constitutional-compliance
```

## Code Style Guidelines

- Use TypeScript with proper type annotations
- Follow React functional component patterns with hooks
- Use ES modules (import/export) not CommonJS
- Use Prettier for formatting (auto-formatted on commit)
- Follow existing naming conventions:
  - camelCase for variables and functions
  - PascalCase for component names and types
  - kebab-case for file names
- Use async/await for asynchronous operations
- Implement proper error handling with try/catch blocks
- Use Tailwind CSS for styling in the client
- Keep components small and focused on a single responsibility

## Project Organization

The project is organized as a monorepo with workspaces:

- `client/`: React frontend with Vite, TypeScript and Tailwind
- `server/`: Express backend with TypeScript
- `bin/`: CLI scripts


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
