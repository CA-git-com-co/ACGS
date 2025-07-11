# Autonomous Coding Governance System (ACGS) Implementation Guide

## Overview

The Autonomous Coding Governance System (ACGS) is a comprehensive governance framework for autonomous AI agents that ensures constitutional compliance, human oversight, secure execution, and complete auditability.

## Architecture

### Core Components

1. **Agent Identity Management (ACGS.2)** - Port 8006
   - Agent registration, authentication, and lifecycle management
   - Role-based access control and permissions
   - API key-based authentication for agents

2. **Human-in-the-Loop (HITL) Service (ACGS.1)** - Port 8008
   - Multi-factor confidence scoring and risk assessment
   - 4-level escalation system (Auto → Team Lead → Domain Expert → Constitutional Council)
   - Agent-specific learning and adaptation

3. **Sandbox Execution Service (ACGS.3)** - Port 8009
   - Docker-based secure code execution
   - Resource limits and network isolation
   - Policy enforcement and security scanning

4. **Formal Verification Service (ACGS.4)** - Port 8010
   - Z3 SMT solver integration for policy verification
   - Constitutional compliance checking
   - Policy consistency analysis

5. **Audit Integrity Service (ACGS.5)** - Port 8011
   - Cryptographic audit logging with Merkle trees
   - Digital signatures and blockchain anchoring
   - Tamper-evident audit trails

6. **ACGS Coordinator** - Port 8000
   - Central orchestration of all governance components
   - End-to-end operation management
   - Unified API for agent operations

7. **Consensus Engine** - Port 8007
   - Enables agreement between different AI agents
   - Implements various consensus algorithms

8. **Multi-Agent Coordinator** - Port 8008
   - Coordinates the actions of multiple AI agents
   - Dynamic hierarchy creation

9. **Worker Agents** - Port 8009
   - Specialized agents for ethical, legal, and operational analysis
   - Perform core analysis and assessment tasks

10. **Blackboard Service** - Port 8010
    - Redis-based shared knowledge system
    - Facilitates knowledge sharing between agents

11. **Code Analysis Service** - Port 8011
    - Static analysis with tenant routing
    - Semantic code search and dependency mapping

12. **Context Service** - Port 8012
    - Governance workflow integration
    - Bidirectional context enrichment

### Supporting Infrastructure

- **PostgreSQL Database** - Centralized data storage
- **Redis** - Caching and session management
- **Prometheus + Grafana** - Monitoring and metrics
- **Elasticsearch + Kibana** - Log aggregation and analysis

## Constitutional Framework

### Constitutional Hash: `cdd01ef066bc6cf2`

All services operate under constitutional principles:

1. **Non-Maleficence** - Agents must not cause harm
2. **Human Autonomy** - Respect human decision-making authority
3. **Transparency** - All actions must be auditable and explainable
4. **Least Privilege** - Minimum necessary permissions
5. **Data Protection** - Protect sensitive data and privacy

## Quick Start

### Prerequisites

- Docker and Docker Compose
- 8GB+ RAM (recommended for full deployment)
- 20GB+ disk space

### Deployment

1. **Clone and prepare the environment:**
   ```bash
   cd /home/dislove/ACGS-2
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Deploy the full ACGS stack:**
   ```bash
   docker-compose -f docker-compose.acgs.yml up -d
   ```

3. **Verify deployment:**
   ```bash
   # Check all services are healthy
   docker-compose -f docker-compose.acgs.yml ps

   # Test coordinator endpoint
   curl http://localhost:8000/
   ```

4. **Initialize the system:**
   ```bash
   # Run database migrations
   docker-compose -f docker-compose.acgs.yml exec acgs-database psql -U acgs_user -d acgs_db -f /docker-entrypoint-initdb.d/01-auth/add_agent_tables.sql

   # Create first agent
   curl -X POST http://localhost:8006/api/v1/agents \
     -H "Content-Type: application/json" \
     -d '{
       "agent_id": "demo-agent-001",
       "name": "Demo Coding Agent",
       "description": "Demo agent for testing ACGS",
       "agent_type": "coding_agent",
       "owner_user_id": 1,
       "capabilities": ["code_generation", "code_review"],
       "permissions": ["read:code", "write:code"],
       "compliance_level": "high"
     }'
   ```

## Usage Examples

### 1. Execute Code with Full ACGS Governance

```bash
curl -X POST http://localhost:8000/api/v1/operations \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "demo-agent-001",
    "agent_type": "coding_agent",
    "operation_type": "code_execution",
    "operation_description": "Execute Python script to analyze data",
    "code": "print(\"Hello from ACGS!\")\nresult = sum([1, 2, 3, 4, 5])\nprint(f\"Sum: {result}\")",
    "execution_environment": "python",
    "operation_context": {
      "safe_operation": true,
      "data_access": false
    }
  }'
```

### 2. Request Human Review for High-Risk Operation

```bash
curl -X POST http://localhost:8000/api/v1/operations \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "demo-agent-001",
    "agent_type": "coding_agent",
    "operation_type": "system_command",
    "operation_description": "Update system configuration file",
    "requires_human_approval": true,
    "operation_context": {
      "affects_production": true,
      "irreversible": true
    }
  }'
```

### 3. Check Operation Status

```bash
curl http://localhost:8000/api/v1/operations/{operation_id}
```

## Service Endpoints

### ACGS Coordinator (Port 8000)
- `POST /api/v1/operations` - Execute governed operation
- `GET /api/v1/operations/{id}` - Get operation status
- `GET /api/v1/agents/{id}/operations` - List agent operations

### Agent Identity Management (Port 8006)
- `POST /api/v1/agents` - Create agent
- `GET /api/v1/agents` - List agents
- `GET /api/v1/agents/{id}` - Get agent details
- `PUT /api/v1/agents/{id}` - Update agent
- `PATCH /api/v1/agents/{id}/status` - Update agent status

### HITL Service (Port 8008)
- `POST /api/v1/reviews/evaluate` - Request operation review
- `GET /api/v1/reviews` - List reviews
- `POST /api/v1/reviews/{id}/decide` - Make review decision
- `POST /api/v1/reviews/{id}/feedback` - Provide feedback

### Sandbox Execution (Port 8009)
- `POST /api/v1/executions` - Execute code in sandbox
- `GET /api/v1/executions` - List executions
- `GET /api/v1/executions/{id}` - Get execution details
- `POST /api/v1/executions/{id}/kill` - Kill running execution

### Formal Verification (Port 8010)
- Policy verification endpoints (to be implemented)

### Audit Integrity (Port 8011)
- Audit logging and integrity verification endpoints (to be implemented)

## Monitoring and Operations

### Health Checks

Check service health:
```bash
curl http://localhost:8000/health  # Coordinator
curl http://localhost:8006/health  # Auth Service
curl http://localhost:8008/health  # HITL Service
curl http://localhost:8009/health  # Sandbox Service
```

### Monitoring Dashboards

- **Grafana**: http://localhost:3000 (admin/acgs_admin_password)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601

### Logs

View service logs:
```bash
docker-compose -f docker-compose.acgs.yml logs -f acgs-coordinator
docker-compose -f docker-compose.acgs.yml logs -f acgs-agent-hitl
docker-compose -f docker-compose.acgs.yml logs -f acgs-sandbox-execution
```

## Security Configuration

### Agent Authentication

Agents authenticate using API keys:
```bash
# Example API call with agent authentication
curl -X POST http://localhost:8009/api/v1/executions \
  -H "Authorization: Bearer acgs_agent_YOUR_API_KEY" \
  -H "X-Agent-ID: demo-agent-001" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

### Constitutional Compliance

All operations are validated against constitutional principles:
- Operations violating principles are automatically blocked
- Human oversight required for ambiguous cases
- Complete audit trail maintained for compliance

### Sandbox Security

Code execution is isolated using Docker containers with:
- No network access by default
- Read-only filesystem (except designated areas)
- Memory and CPU limits
- Dropped capabilities and seccomp filtering

## Performance Targets

- **HITL Auto-Decision**: <5ms P99 latency
- **Sandbox Startup**: <500ms
- **Policy Verification**: <100ms for simple policies
- **Audit Integrity**: <1s batch processing

## Compliance Features

- **SOC2 Type II** controls implementation
- **ISO 27001** security frameworks
- **GDPR** data protection compliance
- **Constitutional AI** governance principles
- **Immutable audit trails** with cryptographic integrity
- **Blockchain anchoring** for external verification

## Development and Testing

### Running Tests

```bash
# Run unit tests for each service
docker-compose -f docker-compose.acgs.yml exec acgs-auth-service python -m pytest
docker-compose -f docker-compose.acgs.yml exec acgs-agent-hitl python -m pytest
docker-compose -f docker-compose.acgs.yml exec acgs-sandbox-execution python -m pytest
```

### Local Development

For development, you can run individual services:
```bash
cd services/core/agent-hitl
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   docker-compose -f docker-compose.acgs.yml restart acgs-database
   # Wait for health check to pass
   ```

2. **Sandbox Execution Fails**
   ```bash
   # Check Docker socket access
   docker ps
   # Restart sandbox service
   docker-compose -f docker-compose.acgs.yml restart acgs-sandbox-execution
   ```

3. **Service Discovery Issues**
   ```bash
   # Check network connectivity
   docker-compose -f docker-compose.acgs.yml exec acgs-coordinator curl http://acgs-auth-service:8006/health
   ```

### Debug Mode

Enable debug logging:
```bash
# Set DEBUG=true in environment
docker-compose -f docker-compose.acgs.yml -f docker-compose.debug.yml up -d
```

## Contributing

### Adding New Services

1. Create service in `services/core/your-service/`
2. Add Docker configuration
3. Update `docker-compose.acgs.yml`
4. Add integration to ACGS Coordinator
5. Update documentation

### Security Guidelines

- All agent operations must go through HITL evaluation
- Code execution must use sandbox isolation
- Audit logging is mandatory for all operations
- Constitutional compliance must be verified

## License and Support

This implementation is part of the ACGS research project. For support and questions:

- Check service logs for error details
- Review monitoring dashboards for performance issues
- Consult the architecture documentation for design decisions

## Implementation Status

### ✅ Completed Components

- **Agent Identity Management**: Full CRUD operations, authentication, audit logging
- **HITL Service**: Decision engine, confidence scoring, escalation system
- **Sandbox Execution**: Docker-based isolation, resource limits, security policies
- **Agent Authentication Middleware**: Cross-service agent authentication
- **ACGS Coordinator**: End-to-end operation orchestration
- **Docker Deployment**: Complete containerized deployment stack

### 🚧 In Progress

- **Formal Verification Service**: Z3 integration (partial implementation)
- **Audit Integrity Service**: Cryptographic integrity (partial implementation)
- **Human Review Interface**: Web dashboard for HITL reviews

### 📋 Future Enhancements

- Advanced policy language for formal verification
- Real blockchain integration (Solana/Ethereum)
- Machine learning for confidence score optimization
- Multi-tenancy support
- Advanced analytics and reporting

## License and Support

This implementation is part of the ACGS research project. For support and questions:

- Check service logs for error details
- Review monitoring dashboards for performance issues
- Consult the architecture documentation for design decisions

## Implementation Status

### ✅ Completed Components

- **Agent Identity Management**: Full CRUD operations, authentication, audit logging
- **HITL Service**: Decision engine, confidence scoring, escalation system
- **Sandbox Execution**: Docker-based isolation, resource limits, security policies
- **Agent Authentication Middleware**: Cross-service agent authentication
- **ACGS Coordinator**: End-to-end operation orchestration
- **Docker Deployment**: Complete containerized deployment stack

### 🚧 In Progress

- **Formal Verification Service**: Z3 integration (partial implementation)
- **Audit Integrity Service**: Cryptographic integrity (partial implementation)
- **Human Review Interface**: Web dashboard for HITL reviews

### 📋 Future Enhancements

- Advanced policy language for formal verification
- Real blockchain integration (Solana/Ethereum)
- Machine learning for confidence score optimization
- Multi-tenancy support
- Advanced analytics and reporting

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)

---

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->
**Implementation Version**: 1.0.0
**Last Updated**: 2025-06-30
