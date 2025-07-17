# Agent Identity Management System
**Constitutional Hash: cdd01ef066bc6cf2**


## Overview

The Agent Identity Management System extends the ACGS authentication service to support autonomous agents as first-class entities with distinct identities, credentials, and lifecycle management. This system implements the **Agent Directory & Profiles** component of the ACGS blueprint (Task ACGS.3.1).

## Key Features

### 🤖 Agent Identity Management
- **Unique Agent Identities**: Each agent has a stable, unique identifier and profile
- **Lifecycle Management**: Complete agent lifecycle from creation to retirement
- **Owner Assignment**: Every agent is owned by a human user for accountability
- **Role-Based Permissions**: Granular permission system integrated with existing RBAC

### 🔐 Security & Authentication
- **API Key Authentication**: Secure API keys for agent authentication
- **Constitutional Compliance**: All agents operate under constitutional constraints
- **IP Whitelisting**: Optional IP-based access control
- **Resource Limits**: Configurable rate limits and resource quotas

### 📊 Monitoring & Auditing
- **Comprehensive Audit Logs**: Complete audit trail of all agent operations
- **Activity Tracking**: Real-time monitoring of agent activity
- **Performance Metrics**: Operation success/failure tracking
- **Session Management**: Active session tracking and management

## Architecture

### Database Schema

#### Agents Table
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    agent_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    owner_user_id INTEGER NOT NULL REFERENCES auth_users(id),
    capabilities JSONB NOT NULL DEFAULT '[]',
    permissions JSONB NOT NULL DEFAULT '[]',
    allowed_services JSONB NOT NULL DEFAULT '[]',
    allowed_operations JSONB NOT NULL DEFAULT '[]',
    constitutional_hash VARCHAR(64) NOT NULL,
    compliance_level VARCHAR(20) NOT NULL DEFAULT 'standard',
    -- ... additional fields
);
```

#### Agent Sessions Table
```sql
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY,
    agent_id UUID NOT NULL REFERENCES agents(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    -- ... additional fields
);
```

#### Agent Audit Logs Table
```sql
CREATE TABLE agent_audit_logs (
    id UUID PRIMARY KEY,
    agent_id UUID NOT NULL REFERENCES agents(id),
    event_type VARCHAR(50) NOT NULL,
    event_description TEXT NOT NULL,
    performed_by_user_id INTEGER REFERENCES auth_users(id),
    timestamp TIMESTAMPTZ NOT NULL,
    constitutional_hash VARCHAR(64) NOT NULL,
    -- ... additional fields
);
```

### API Endpoints

#### Agent Management
- `POST /api/v1/agents` - Create new agent
- `GET /api/v1/agents` - List/search agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `PUT /api/v1/agents/{agent_id}` - Update agent
- `PATCH /api/v1/agents/{agent_id}/status` - Update agent status
- `GET /api/v1/agents/{agent_id}/audit-logs` - Get audit logs

#### Authentication
- Agent authentication via API keys in `Authorization: Bearer <api_key>` header
- Integration with existing user authentication system
- Constitutional compliance validation on all operations

## Agent Types

The system supports multiple agent types:

- **`coding_agent`**: Code generation and modification
- **`policy_agent`**: Policy enforcement and governance
- **`monitoring_agent`**: System monitoring and alerting
- **`analysis_agent`**: Data analysis and reporting
- **`integration_agent`**: External system integration
- **`custom_agent`**: Custom agent types

## Agent Lifecycle

### Status Flow
```
PENDING → ACTIVE → SUSPENDED → ACTIVE
    ↓        ↓         ↓
  RETIRED  RETIRED  RETIRED
    ↓        ↓         ↓
COMPROMISED → RETIRED
```

### Status Descriptions
- **`PENDING`**: Agent created but not yet activated
- **`ACTIVE`**: Agent is operational and can perform actions
- **`SUSPENDED`**: Agent temporarily disabled
- **`RETIRED`**: Agent permanently deactivated
- **`COMPROMISED`**: Agent credentials potentially compromised

## Permissions System

### Agent-Specific Permissions
- `agent:create` - Create new agents
- `agent:create_any` - Create agents for any user (admin)
- `agent:read` - Read own agents
- `agent:read_all` - Read all agents (admin)
- `agent:update` - Update own agents
- `agent:update_any` - Update any agent (admin)
- `agent:manage_status` - Manage status of own agents
- `agent:manage_status_any` - Manage status of any agent (admin)
- `agent:audit` - View audit logs for own agents
- `agent:audit_all` - View all agent audit logs (admin)

### Predefined Roles
- **`agent_manager`**: Can manage own agents
- **`agent_admin`**: Full administrative access to agent management

## Constitutional Compliance

All agents operate under constitutional constraints:

- **Constitutional Hash**: `cdd01ef066bc6cf2`
- **Compliance Levels**: `standard`, `high`, `critical`
- **Human Approval**: Configurable requirement for human approval
- **Audit Requirements**: All operations logged for compliance

## Usage Examples

### Creating an Agent

```python
from app.schemas.agent import AgentCreate, AgentType

agent_data = AgentCreate(
    agent_id="my-coding-agent-001",
    name="My Coding Assistant",
    description="AI agent for code generation and review",
    agent_type=AgentType.CODING_AGENT,
    owner_user_id=123,
    capabilities=["code_generation", "code_review", "testing"],
    permissions=["read:code", "write:code"],
    allowed_services=["github", "gitlab"],
    allowed_operations=["create_pr", "review_code"],
    compliance_level="high",
    requires_human_approval=True
)

# POST /api/v1/agents
response = await client.post("/api/v1/agents", json=agent_data.dict())
credentials = response.json()
api_key = credentials["api_key"]  # Store securely!
```

### Authenticating as an Agent

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "X-Agent-ID": "my-coding-agent-001"
}

response = await client.get("/api/v1/some-service", headers=headers)
```

### Updating Agent Status

```python
from app.schemas.agent import AgentStatusUpdate, AgentStatus

status_update = AgentStatusUpdate(
    status=AgentStatus.ACTIVE,
    reason="Activating agent for production use"
)

# PATCH /api/v1/agents/{agent_id}/status
response = await client.patch(
    f"/api/v1/agents/{agent_id}/status",
    json=status_update.dict()
)
```

## Security Considerations

### API Key Management
- API keys are generated using cryptographically secure random generation
- Keys are hashed before storage (never stored in plaintext)
- Keys are only shown once during agent creation
- Implement key rotation policies for production use

### Access Control
- Agents can only be managed by their owners or admin users
- All operations require appropriate permissions
- IP whitelisting available for additional security
- Rate limiting and resource quotas prevent abuse

### Audit Trail
- Complete audit log of all agent operations
- Constitutional compliance verification on all actions
- Immutable audit records with cryptographic integrity
- Integration with existing security monitoring systems

## Deployment

### Database Migration
```bash
# Run the migration script
psql -d your_database -f migrations/add_agent_tables.sql
```

### Environment Variables
```bash
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
ACGE_ENABLED=true
```

### Testing
```bash
# Run the test suite
python test_agent_system.py
```

## Integration with ACGS Services

The Agent Identity Management system integrates with:

- **Authentication Service**: User authentication and authorization
- **Constitutional AI Service**: Constitutional compliance validation
- **Policy Governance Service**: Policy enforcement for agent actions
- **Audit Service**: Comprehensive audit logging
- **HITL System**: Human oversight for agent operations

## Future Enhancements

- **Multi-tenancy**: Support for multiple organizations
- **Agent-to-Agent Delegation**: Agents acting on behalf of other agents
- **Advanced Analytics**: ML-powered agent behavior analysis
- **Federation**: Cross-organization agent identity management
- **Zero-Trust Architecture**: Enhanced security with continuous verification

## Support

For questions or issues with the Agent Identity Management system:

1. Check the audit logs for detailed error information
2. Verify agent permissions and status
3. Review constitutional compliance requirements
4. Contact the ACGS development team



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

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**System Version**: 1.0.0  
**Last Updated**: 2025-06-30
