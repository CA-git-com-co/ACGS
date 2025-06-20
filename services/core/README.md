# ACGS-1 Core Services

This directory contains the core governance services that implement the fundamental constitutional AI governance capabilities of ACGS-1.

## Service Overview

### Constitutional AI Service (`constitutional-ai/`)
**Purpose**: Constitutional principle management and compliance checking
- Constitutional principle storage and validation
- Human-in-the-loop sampling for uncertainty
- Collective Constitutional AI integration
- Democratic participation mechanisms
- Constitutional Council operations

**Key Features**:
- Principle management APIs
- Meta-rule enforcement
- Conflict resolution mechanisms
- Democratic oversight workflows

**Port**: 8001
**API Base**: `/api/constitutional-ai/`

### Governance Synthesis Service (`governance-synthesis/`)
**Purpose**: LLM-powered policy synthesis from constitutional principles
- Policy generation with constitutional guidance
- Multi-model validation (99.92% reliability)
- QEC-inspired error correction
- Bias detection and mitigation

**Key Features**:
- Constitutional prompting
- Policy synthesis algorithms
- Multi-agent validation
- Quality assurance mechanisms

**Port**: 8002
**API Base**: `/api/governance-synthesis/`

### Policy Governance Service (`policy-governance/`)
**Purpose**: Real-time policy enforcement and governance
- Sub-5ms policy decisions with hardware acceleration
- OPA (Open Policy Agent) integration
- Incremental compilation and hot-swapping
- Constitutional amendment integration

**Key Features**:
- Real-time enforcement engine
- Policy decision APIs
- Constitutional compliance checking
- Performance optimization

**Port**: 8003
**API Base**: `/api/policy-governance/`

### Formal Verification Service (`formal-verification/`)
**Purpose**: Mathematical verification of policies against principles
- Z3 SMT solver integration
- Safety property checking
- Formal policy validation
- Mathematical proof generation

**Key Features**:
- SMT solver integration
- Property verification
- Formal validation APIs
- Proof generation and storage

**Port**: 8003
**API Base**: `/api/formal-verification/`

### Evolutionary Computation Service (`evolutionary-computation/`)
**Purpose**: WINA-optimized oversight and performance monitoring
- Constitutional compliance verification and optimization
- Evolutionary governance strategies and learning feedback
- Performance optimization alerts and constitutional updates
- WINA oversight coordination

**Key Features**:
- Performance monitoring and optimization
- Constitutional compliance tracking
- Evolutionary strategy implementation
- Alert and notification systems

**Port**: 8006
**API Base**: `/api/evolutionary-computation/`

### Darwin Gödel Machine Service (`dgm-service/`)
**Purpose**: Self-evolving AI governance with constitutional compliance
- Darwin Gödel Machine implementation for autonomous system evolution
- Event-driven architecture with NATS message broker integration
- LSU interface and SEE platform for self-evolving systems
- Conservative bandit algorithms for safe exploration

**Key Features**:
- Self-improving algorithms with constitutional constraints
- Archive-backed evolution loops with performance tracking
- Safe exploration with reward-hacking resilience
- Semantic validation as hard constraints

**Port**: 8007
**API Base**: `/api/dgm/`

## Service Architecture

### Communication Patterns
```
Constitutional AI ──→ Governance Synthesis
       │                      │
       │                      ▼
       │              Formal Verification
       │                      │
       │                      ▼
       └──────────────→ Policy Governance
```

### Data Flow
1. **Constitutional AI** manages principles and meta-rules
2. **Governance Synthesis** generates policies from principles
3. **Formal Verification** validates policies mathematically
4. **Policy Governance** enforces policies in real-time

### Integration Points
- **Blockchain Integration**: Via Quantumagi Bridge
- **Platform Services**: Authentication, Integrity, Workflow
- **Research Services**: Federated evaluation and research platform
- **Applications**: Governance dashboard, Constitutional Council interface

## Development

### Running All Core Services
```bash
# Start all core services
docker-compose -f infrastructure/docker/docker-compose.core.yml up -d

# Or start individually with UV (recommended)
cd services/core/constitutional-ai && uv sync && uv run uvicorn app.main:app --reload --port 8001
cd services/core/governance-synthesis && uv sync && uv run uvicorn app.main:app --reload --port 8004
cd services/core/policy-governance && uv sync && uv run uvicorn app.main:app --reload --port 8005
cd services/core/formal-verification && uv sync && uv run uvicorn app.main:app --reload --port 8003
cd services/core/evolutionary-computation && uv sync && uv run uvicorn app.main:app --reload --port 8006
cd services/core/dgm-service && uv sync && uv run python -m dgm_service.main

# Alternative: Traditional Python
cd services/core/constitutional-ai && python -m uvicorn app.main:app --reload --port 8001
cd services/core/governance-synthesis && python -m uvicorn app.main:app --reload --port 8004
cd services/core/policy-governance && python -m uvicorn app.main:app --reload --port 8005
cd services/core/formal-verification && python -m uvicorn app.main:app --reload --port 8003
cd services/core/evolutionary-computation && python -m uvicorn app.main:app --reload --port 8006
cd services/core/dgm-service && python -m dgm_service.main
```

### Testing Core Services
```bash
# Run core service tests
python -m pytest tests/unit/core/
python -m pytest tests/integration/core/

# Test service communication
python scripts/validation/test_core_service_integration.py
```

### Service Dependencies
- **Database**: PostgreSQL for persistent storage
- **Cache**: Redis for performance optimization
- **Message Queue**: NATS for inter-service communication
- **Monitoring**: Prometheus metrics collection

## Configuration

### Environment Variables
Each service uses environment variables for configuration:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `NATS_URL`: NATS message broker URL
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `SERVICE_PORT`: Service port number

### Service Registry
Services register with the shared service registry:
```python
# services/shared/config/service_registry.py
CORE_SERVICES = {
    "constitutional-ai": "http://localhost:8001",
    "governance-synthesis": "http://localhost:8002", 
    "policy-governance": "http://localhost:8003",
    "formal-verification": "http://localhost:8004"
}
```

## Monitoring & Health Checks

### Health Endpoints
Each service provides health check endpoints:
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health information
- `GET /metrics` - Prometheus metrics

### Service Monitoring
- **Metrics**: Prometheus metrics collection
- **Logging**: Structured logging with correlation IDs
- **Tracing**: Distributed tracing with Jaeger
- **Alerts**: Grafana alerting for service health

## Security

### Authentication
- JWT token validation for external requests
- Service-to-service authentication with internal tokens
- Role-based access control (RBAC)

### Data Protection
- Input validation and sanitization
- Rate limiting and request throttling
- Audit logging for all operations
- Encryption at rest and in transit

### Constitutional Compliance
- All operations logged for constitutional audit
- Principle-based access control
- Democratic governance through Constitutional Council
- Cryptographic integrity verification

## Documentation

- **[API Documentation](../../docs/api/README.md)**: Complete API reference
- **[Architecture Guide](../../docs/architecture/REORGANIZED_ARCHITECTURE.md)**: System architecture
- **[Development Guide](../../docs/development/developer_guide.md)**: Development workflows
- **[Deployment Guide](../../docs/deployment/deployment.md)**: Deployment instructions

---

**Core Services**: The foundation of constitutional AI governance in ACGS-1 🏛️
