# MCP Inspector Development Guide - ACGS-2 Constitutional Compliance

## Constitutional Compliance for MCP Inspector

### Core Requirements
- **Constitutional Hash**: `cdd01ef066bc6cf2` - REQUIRED for all MCP operations
- **MCP Integration**: All MCP tools must validate constitutional compliance
- **Audit Trail**: MCP operations logged through ACGS Integrity Service
- **Performance**: MCP operations must meet P99 <5ms requirement

## Build Commands

- Build all: `npm run build`
- Build client: `npm run build-client`
- Build server: `npm run build-server`
- Development mode: `npm run dev` (use `npm run dev:windows` on Windows)
- Format code: `npm run prettier-fix`
- Client lint: `cd client && npm run lint`

## Constitutional MCP Usage

```bash
# Start MCP Inspector with constitutional compliance
npm run dev -- --constitutional-hash cdd01ef066bc6cf2

# Inspect MCP servers with constitutional validation
npm run inspect -- --server-url http://localhost:3000 --validate-constitutional

# Generate constitutional compliance report for MCP tools
npm run report -- --constitutional-compliance
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
