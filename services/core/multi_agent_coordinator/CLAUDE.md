
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# CLAUDE.md - Multi-Agent Coordinator Service

## Directory Overview

The Multi-Agent Coordinator service orchestrates collaboration between multiple AI agents within the ACGS-2 constitutional AI governance framework. It implements a hybrid hierarchical-blackboard coordination model for complex governance requests.

## File Inventory

- **CLAUDE.md**: This documentation file
- **app/**: FastAPI application and API endpoints
- **coordinator_agent.py**: Core coordination logic and agent management
- **performance_integration.py**: Performance monitoring and optimization
- **__init__.py**: Package initialization
- **tests/**: Unit and integration tests

## Dependencies & Interactions

- **Constitutional AI Service**: Constitutional compliance validation
- **Worker Agents Service**: Specialized agent coordination
- **Blackboard Service**: Shared knowledge and task management
- **Integrity Service**: Audit trail for coordination decisions
- **Constitutional Framework**: Compliance with hash `cdd01ef066bc6cf2`

## Key Components

### Coordination Engine
- **Hierarchical Agent Structure**: Three-tier hierarchy (Orchestrator, Domain Specialist, Worker)
- **Blackboard System**: Shared knowledge space for agent communication
- **Task Decomposition**: Breaking complex requests into manageable tasks
- **Conflict Resolution**: Detecting and resolving agent conflicts
- **Constitutional Safety**: Ensuring all coordination adheres to constitutional principles

### Agent Management
- **Dynamic Hierarchy Creation**: Adaptive agent structures based on request complexity
- **Agent Lifecycle Management**: Creation, coordination, and cleanup of agent instances
- **Performance Monitoring**: Tracking agent performance and coordination efficiency
- **Load Balancing**: Distributing tasks across available agents
- **Fault Tolerance**: Graceful handling of agent failures

### Coordination Protocols
- **Request Processing**: Intake and analysis of governance requests
- **Task Assignment**: Intelligent distribution of tasks to appropriate agents
- **Progress Tracking**: Monitoring task completion and agent status
- **Result Aggregation**: Combining agent outputs into coherent responses
- **Quality Assurance**: Validating coordination outcomes

## Constitutional Compliance Status

✅ **IMPLEMENTED**: Constitutional hash validation (`cdd01ef066bc6cf2`)
✅ **IMPLEMENTED**: Hierarchical coordination model
✅ **IMPLEMENTED**: Blackboard integration
✅ **IMPLEMENTED**: Basic agent management
🔄 **IN PROGRESS**: Advanced conflict resolution
🔄 **IN PROGRESS**: Performance optimization
❌ **PLANNED**: AI-driven coordination strategies
❌ **PLANNED**: Advanced agent learning

## Performance Considerations

- **Coordination Latency**: <10ms for task assignment and management
- **Agent Response Time**: <100ms for typical coordination requests
- **Throughput**: >500 RPS for coordination operations
- **Memory Usage**: Efficient agent instance management
- **Scalability**: Horizontal scaling with multiple coordinator instances

## Implementation Status

### ✅ IMPLEMENTED
- Core coordination engine and agent management
- Hierarchical coordination model
- Blackboard service integration
- Constitutional compliance validation
- Basic performance monitoring

### 🔄 IN PROGRESS
- Advanced conflict resolution mechanisms
- Performance optimization and caching
- Enhanced agent lifecycle management
- Real-time coordination analytics
- Cross-service coordination protocols

### ❌ PLANNED
- AI-driven coordination strategy optimization
- Advanced agent learning and adaptation
- Predictive coordination planning
- Multi-tenant coordination isolation
- Advanced coordination pattern recognition

## API Endpoints

### Coordination Management
- **POST /coordinate**: Initiate multi-agent coordination for governance request
- **GET /coordination/{id}**: Get coordination status and progress
- **POST /coordination/{id}/cancel**: Cancel ongoing coordination
- **GET /agents**: List active agents and their status
- **POST /agents/create**: Create new agent instance

### Monitoring and Health
- **GET /health**: Service health check
- **GET /metrics**: Prometheus metrics endpoint
- **GET /coordination/stats**: Coordination performance statistics

## Configuration

```yaml
# Multi-Agent Coordinator Configuration
coordinator:
  max_agents: 50
  coordination_timeout: 300s
  task_queue_size: 1000
  constitutional_hash: cdd01ef066bc6cf2

agent_management:
  default_agent_timeout: 60s
  max_concurrent_tasks: 10
  agent_pool_size: 20

blackboard:
  connection_url: redis://localhost:6389
  knowledge_ttl: 3600s
  max_knowledge_size: 10MB

performance:
  coordination_latency_target: 10ms
  throughput_target: 500rps
  memory_limit: 2GB
```

## Usage Examples

```python
# Coordinate governance request
coordination_request = {
    "request_id": "gov-req-123",
    "governance_query": {
        "type": "policy_evaluation",
        "context": "healthcare_data_access",
        "stakeholders": ["clinician", "researcher"]
    },
    "constitutional_hash": "cdd01ef066bc6cf2"
}

response = await coordinator.coordinate(coordination_request)
```

## Cross-References & Navigation

**Navigation**:
- [Core Services](../CLAUDE.md)
- [Worker Agents](../worker_agents/CLAUDE.md)
- [Constitutional AI](../constitutional-ai/CLAUDE.md)
- [Governance Synthesis](../governance-synthesis/CLAUDE.md)

**Related Components**:
- [Blackboard Service](../../platform_services/blackboard/CLAUDE.md)
- [Integrity Service](../../platform_services/integrity/CLAUDE.md)
- [API Gateway](../../platform_services/api_gateway/CLAUDE.md)

**External References**:
- [Multi-Agent Systems Documentation](https://en.wikipedia.org/wiki/Multi-agent_system)
- [Blackboard System Pattern](https://en.wikipedia.org/wiki/Blackboard_system)

---

**Constitutional Compliance**: All coordination operations maintain constitutional hash `cdd01ef066bc6cf2` validation
