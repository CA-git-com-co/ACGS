# OpenCode Adapter for ACGS

A governance-compliant adapter service that integrates OpenCode AI coding assistant with the ACGS (AI Constitutional Governance System) framework, ensuring all AI operations adhere to constitutional principles and performance requirements.

## Overview

The OpenCode Adapter wraps the OpenCode CLI tool with ACGS governance layers, providing:

- **Constitutional Compliance**: All operations validated against ACGS principles
- **Policy Enforcement**: Real-time policy checking through ACGS services
- **Performance Monitoring**: Sub-5ms P99 latency with >85% cache hit rates
- **Audit Trail**: Cryptographic audit logging for all operations
- **Human-in-the-Loop**: Automatic escalation for high-risk operations

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Client App    │────▶│ OpenCode Adapter │────▶│  OpenCode   │
└─────────────────┘     └──────────────────┘     └─────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   ACGS Services     │
                    ├─────────────────────┤
                    │ • Auth (port 8016)  │
                    │ • Policy (port 8002)│
                    │ • Audit (port 8004) │
                    │ • HITL (port 8006)  │
                    └─────────────────────┘
```

## Features

### 🛡️ Security & Governance
- **Constitutional Wrapper**: 7 core principles ensuring safe AI operations
- **Policy Verification**: Every command checked against ACGS policies
- **Audit Logging**: Blockchain-anchored audit trail for compliance
- **Data Privacy**: Automatic detection and protection of sensitive data

### 📊 Performance
- **O(1) Lookups**: Optimized data structures for instant access
- **Sub-5ms P99 Latency**: Meeting strict performance requirements
- **Cache Optimization**: >85% cache hit rate for repeated operations
- **Real-time Monitoring**: Continuous performance metrics tracking

### 🔄 Integration
- **REST API**: Simple HTTP endpoints for command execution
- **Async Operations**: Non-blocking command execution
- **Health Checks**: Built-in monitoring endpoints
- **Graceful Shutdown**: Clean resource cleanup

## Installation

### Prerequisites
- Node.js 20+
- ACGS services running (Auth, Policy, Audit, HITL)
- OpenCode CLI installed globally

### Setup

1. Install dependencies:
```bash
cd services/cli/opencode_adapter
npm install --legacy-peer-deps
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your ACGS service URLs and credentials
```

3. Build the service:
```bash
npm run build
```

4. Run tests:
```bash
npm test
```

5. Start the service:
```bash
npm start
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ACGS_AUTH_SERVICE_URL` | Auth service endpoint | `http://localhost:8016` |
| `ACGS_POLICY_SERVICE_URL` | Policy service endpoint | `http://localhost:8002` |
| `ACGS_AUDIT_SERVICE_URL` | Audit service endpoint | `http://localhost:8004` |
| `ACGS_HITL_SERVICE_URL` | HITL service endpoint | `http://localhost:8006` |
| `ACGS_AGENT_ID` | Adapter agent ID | `opencode-adapter` |
| `ACGS_AGENT_SECRET` | Agent authentication secret | Required |
| `ACGS_CONSTITUTIONAL_HASH` | Constitutional compliance hash | `cdd01ef066bc6cf2` |
| `PORT` | Service port | `8020` |
| `LOG_LEVEL` | Logging level | `info` |

## API Reference

### Execute Command
```http
POST /execute
Content-Type: application/json

{
  "command": "run",
  "args": ["script.js"],
  "context": {
    "requestId": "req-123",
    "userId": "user-456"
  }
}
```

Response:
```json
{
  "success": true,
  "output": "Script executed successfully",
  "performanceMetrics": {
    "latency": 3.2,
    "memoryUsage": 1024
  }
}
```

### Check Permission
```http
POST /check-permission
Content-Type: application/json

{
  "action": "deploy",
  "context": {
    "environment": "production"
  }
}
```

Response:
```json
{
  "allowed": false,
  "reason": "Production deployments require approval"
}
```

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "acgsCompliant": true,
  "metrics": {
    "command_latency": {
      "p99": 4.8,
      "p95": 3.2,
      "p50": 1.5
    },
    "cache_hit_rate": {
      "p50": 0.87
    }
  }
}
```

### Metrics
```http
GET /metrics
```

## Constitutional Principles

The adapter enforces these core principles:

1. **Safety First**: No harmful operations on systems or data
2. **Operational Transparency**: All operations must be auditable
3. **User Consent**: High-risk operations require explicit approval
4. **Data Privacy**: Protection of sensitive information
5. **Resource Constraints**: Respect system resource limits
6. **Operation Reversibility**: Destructive operations must be reversible
7. **Least Privilege**: Use minimum required permissions

## Docker Deployment

Build the image:
```bash
docker build -t acgs/opencode-adapter .
```

Run with Docker Compose:
```yaml
version: '3.8'
services:
  opencode-adapter:
    image: acgs/opencode-adapter
    ports:
      - "8020:8020"
    environment:
      - ACGS_AUTH_SERVICE_URL=http://auth-service:8016
      - ACGS_POLICY_SERVICE_URL=http://policy-service:8002
      - ACGS_AUDIT_SERVICE_URL=http://audit-service:8004
      - ACGS_HITL_SERVICE_URL=http://hitl-service:8006
      - ACGS_AGENT_SECRET=${ACGS_AGENT_SECRET}
    depends_on:
      - auth-service
      - policy-service
      - audit-service
      - hitl-service
```

## Development

### Running Tests
```bash
# Unit tests
npm test

# With coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Type Checking
```bash
npm run typecheck
```

### Development Mode
```bash
npm run dev
```

## Performance Benchmarks

The adapter maintains these performance targets:

- **P99 Latency**: < 5ms
- **Cache Hit Rate**: > 85%
- **Memory Usage**: < 512MB
- **Startup Time**: < 2s
- **Request Throughput**: > 1000 req/s

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify ACGS_AGENT_SECRET is set correctly
   - Check Auth Service is running on port 8016
   - Ensure agent is registered in ACGS

2. **Policy Denials**
   - Review policy logs for specific violations
   - Check constitutional compliance requirements
   - Verify user permissions in ACGS

3. **Performance Issues**
   - Monitor /metrics endpoint for bottlenecks
   - Check cache hit rates
   - Review operation complexity

## License

MIT License - See LICENSE file for details