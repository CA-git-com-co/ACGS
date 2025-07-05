# ACGS Context Service

High-performance context management system providing sub-50ms context retrieval, multi-modal data support, and constitutional compliance validation for the AI Compliance and Governance System (ACGS).

## Features

### Core Capabilities

- **Sub-50ms Context Retrieval**: Optimized multi-tier storage architecture
- **Multi-Modal Support**: Text, structured data, and metadata context handling
- **Constitutional Compliance**: Real-time validation and audit trails
- **Hierarchical Management**: TTL-based context lifecycle management
- **Real-time Streaming**: Event-driven context updates via Kafka/NATS

### Architecture

- **Multi-Tier Storage**: Redis (L1) → Qdrant (L2) → PostgreSQL (L3)
- **Vector Search**: Qdrant with HNSW indexing for semantic retrieval
- **WINA Optimization**: 65% efficiency gains through intelligent neuron gating
- **Service Mesh Integration**: Seamless discovery and load balancing

## Quick Start

### Prerequisites

- Python 3.12+
- Redis Cluster (existing ACGS infrastructure)
- Qdrant Vector Database
- Kafka/NATS Streaming (existing ACGS infrastructure)

### Installation

```bash
cd /services/core/context/context_service
pip install -r requirements.txt
```

### Configuration

Set environment variables:

```bash
export CONTEXT_SERVICE_PORT=8012
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export REDIS_CLUSTER_NODES=localhost:7000,localhost:7001,localhost:7002
```

### Running the Service

```bash
python main.py
```

## API Endpoints

### Context Operations

- `POST /api/v1/context/store` - Store new context
- `GET /api/v1/context/retrieve` - Semantic search retrieval
- `PUT /api/v1/context/update` - Update existing context
- `GET /api/v1/context/history` - Get context evolution
- `DELETE /api/v1/context/expire` - Manual context expiration

### Health and Monitoring

- `GET /health` - Service health check
- `GET /metrics` - Performance and usage metrics
- `GET /api/v1/context/stats` - Context statistics

## Context Types

### Hierarchical TTL Structure

1. **ConversationContext** (TTL: 1-10 minutes) - Active dialogue context
2. **DomainContext** (TTL: 1-24 hours) - Domain-specific knowledge
3. **ConstitutionalContext** (TTL: weeks) - Constitutional principles and rules
4. **AgentContext** (TTL: per-agent lifecycle) - Agent-specific memory
5. **PolicyContext** (TTL: indefinite) - Policy definitions with versioning

## Performance Targets

- **Latency**: Sub-50ms context retrieval (P99)
- **Throughput**: 1000+ context operations/second
- **Accuracy**: 95%+ context relevance scoring
- **Compliance**: 100% constitutional validation
- **Availability**: 99.9% uptime

## Integration

### Service Registry

The context service automatically registers with the ACGS ServiceRegistry on port 8012:

```python
from services.shared.service_mesh.registry import ServiceType, get_service_registry

registry = get_service_registry()
context_url = registry.get_api_url(ServiceType.CONTEXT)
```

### Event Streaming

Context updates are published to Kafka/NATS topics:

```python
from services.shared.streaming.event_streaming_manager import EventType

# Context events
- CONTEXT_STORED
- CONTEXT_RETRIEVED
- CONTEXT_UPDATED
- CONTEXT_EXPIRED
```

## Development

### Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/
```

### Monitoring

Context service integrates with existing ACGS monitoring:

- Constitutional compliance validation
- Performance metrics collection
- Real-time alerting via existing AlertingSystem
- Audit logging via AuditLogger

## Security

- **Constitutional Compliance**: All context operations validated
- **Access Control**: Integration with ACGS authentication
- **Audit Trail**: Comprehensive logging of all operations
- **Encryption**: At-rest and in-transit data protection

## Contributing

Follow ACGS development standards:

1. Constitutional compliance validation required
2. Comprehensive testing (unit + integration)
3. Performance benchmarking
4. Security review for sensitive operations
