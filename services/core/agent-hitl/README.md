# Agent HITL Service - Human Oversight Integration

## Overview

The Agent HITL (Human-in-the-Loop) Service provides real-time oversight for autonomous agent operations, implementing confidence-based escalation and human review workflows. This service extends the existing ACGS HITL infrastructure with agent-specific capabilities.

## Key Features

### 🤖 Agent-Specific Oversight
- **Confidence-Based Decisions**: Dynamic confidence scoring based on agent history and operation risk
- **Tiered Escalation**: Four-level escalation system from automated approval to Constitutional Council review
- **Agent Profile Integration**: Leverages agent capabilities, permissions, and compliance levels
- **Operation Risk Assessment**: Real-time risk evaluation based on operation type and context

### ⚡ High-Performance Decision Engine
- **Sub-5ms P99 Latency**: Automated decisions with Redis caching and pre-compiled patterns
- **O(1) Lookups**: Optimized data structures for agent confidence and operation patterns
- **Request-Scoped Caching**: Efficient caching strategy with appropriate TTLs
- **Async Processing**: Non-blocking human review workflows

### 👥 Human Review System
- **Real-Time Dashboard**: Web interface for human reviewers with live updates
- **Smart Task Assignment**: Intelligent routing based on reviewer expertise and availability
- **Contextual Information**: Complete operation context and agent history for informed decisions
- **Feedback Collection**: Structured feedback mechanisms for continuous improvement

### 📈 Learning and Adaptation
- **Confidence Score Adaptation**: Machine learning from human decisions to improve accuracy
- **Historical Performance Tracking**: Long-term agent behavior analysis
- **Threshold Optimization**: Dynamic adjustment of escalation thresholds
- **Constitutional Compliance Learning**: Enhanced understanding of constitutional requirements

## Architecture

### Service Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent HITL Service                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Decision      │  │   Human Review  │  │  Feedback   │ │
│  │   Engine        │  │   Interface     │  │  System     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Redis Cache   │  │   PostgreSQL    │  │  Metrics    │ │
│  │   (Confidence)  │  │   (Audit/Tasks) │  │  (Monitor)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

- **Agent Identity Management**: Agent profiles, permissions, and capabilities
- **Constitutional AI Service**: Constitutional compliance validation
- **Policy Governance Service**: Operation policy enforcement
- **Audit Service**: Comprehensive audit logging
- **Constitutional Council**: High-level governance decisions

## Escalation Levels

### Level 1: Automated Approval (Target: <5ms)
- **Criteria**: High confidence (>0.9), low risk operations
- **Examples**: Code formatting, documentation updates, routine monitoring
- **Processing**: Cached decision patterns, O(1) lookups
- **Audit**: Automated logging with operation details

### Level 2: Automated Review with Notification (<100ms)
- **Criteria**: Medium confidence (0.7-0.9), standard risk operations
- **Examples**: Code changes, configuration updates, data analysis
- **Processing**: Real-time risk assessment with human notification
- **Audit**: Enhanced logging with confidence scores

### Level 3: Human Approval Required (<30 seconds)
- **Criteria**: Low confidence (<0.7) or high-risk operations
- **Examples**: Production deployments, security changes, policy modifications
- **Processing**: Human reviewer assignment with context
- **Audit**: Complete human decision trail

### Level 4: Constitutional Council Review (<24 hours)
- **Criteria**: Critical operations affecting constitutional principles
- **Examples**: Agent capability expansion, constitutional policy changes
- **Processing**: Formal governance workflow
- **Audit**: Constitutional compliance documentation

## Performance Targets

- **Automated Decisions**: <5ms P99 latency
- **Escalation Decisions**: <100ms P95 latency
- **Human Task Assignment**: <1 second
- **System Availability**: 99.9% uptime
- **False Positive Rate**: <1% for escalations
- **Human Reviewer Satisfaction**: >95%

## API Endpoints

### Decision Engine
- `POST /api/v1/hitl/evaluate` - Evaluate agent operation for HITL decision
- `GET /api/v1/hitl/decision/{decision_id}` - Get decision details
- `POST /api/v1/hitl/feedback` - Submit human feedback on decision

### Human Review
- `GET /api/v1/hitl/tasks` - Get pending review tasks
- `POST /api/v1/hitl/tasks/{task_id}/review` - Submit human review
- `GET /api/v1/hitl/dashboard` - Get dashboard data

### Agent Management
- `GET /api/v1/hitl/agents/{agent_id}/confidence` - Get agent confidence profile
- `POST /api/v1/hitl/agents/{agent_id}/confidence` - Update confidence scores
- `GET /api/v1/hitl/agents/{agent_id}/history` - Get decision history

## Configuration

### Environment Variables
```bash
# Service Configuration
AGENT_HITL_SERVICE_PORT=8008
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL_CONFIDENCE=3600  # 1 hour
REDIS_CACHE_TTL_PATTERNS=86400   # 24 hours

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/agent_hitl

# Performance Tuning
DECISION_CACHE_SIZE=10000
MAX_CONCURRENT_REVIEWS=100
CONFIDENCE_LEARNING_RATE=0.1

# Integration Endpoints
AGENT_IDENTITY_SERVICE_URL=http://auth-service:8000
CONSTITUTIONAL_AI_SERVICE_URL=http://ac-service:8001
POLICY_GOVERNANCE_SERVICE_URL=http://pgc-service:8005
```

### Decision Thresholds
```yaml
escalation_thresholds:
  level_1_confidence: 0.9    # Automated approval
  level_2_confidence: 0.7    # Automated with notification
  level_3_confidence: 0.5    # Human approval required
  level_4_operations:        # Constitutional Council review
    - "constitutional_policy_change"
    - "agent_capability_expansion"
    - "critical_security_modification"

risk_factors:
  operation_types:
    code_generation: 0.3
    code_modification: 0.5
    deployment: 0.8
    security_change: 0.9
    policy_change: 1.0
  
  agent_compliance_levels:
    standard: 1.0
    high: 0.8
    critical: 0.6
```

## Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  agent-hitl:
    build: .
    ports:
      - "8008:8008"
    environment:
      - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/agent_hitl
    depends_on:
      - redis
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-hitl-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-hitl
  template:
    metadata:
      labels:
        app: agent-hitl
    spec:
      containers:
      - name: agent-hitl
        image: acgs/agent-hitl:latest
        ports:
        - containerPort: 8008
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"
```

## Monitoring and Metrics

### Key Metrics
- Decision latency (P50, P95, P99)
- Escalation rates by level
- Human reviewer response times
- Confidence score accuracy
- Constitutional compliance rates

### Alerts
- Decision latency > 10ms (P99)
- Escalation rate > 5%
- Human review backlog > 50 tasks
- Confidence score drift > 10%
- Service availability < 99.9%

## Security

### Authentication
- Integration with existing ACGS authentication
- API key authentication for service-to-service calls
- Role-based access control for human reviewers

### Data Protection
- Encryption at rest for sensitive operation data
- Audit logging for all decisions and reviews
- Constitutional compliance validation
- PII protection in logs and metrics

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Service Version**: 1.0.0  
**Port**: 8008
