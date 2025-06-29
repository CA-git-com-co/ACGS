# ACGS-1 Lite Evolution Oversight Service

Comprehensive evolution evaluation, approval workflows, and rollback mechanisms for AI agent governance in constitutional AI systems.

## 🎯 Overview

The Evolution Oversight Service provides automated evaluation criteria, human review integration, and fast rollback capabilities to ensure safe and constitutional evolution of AI agents. It implements a multi-tier approval workflow that balances automation with human oversight.

**Service Port**: 8004
**Metrics Port**: 9004
**Service Version**: 1.0.0
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8004/health

## 🔒 Key Features

- **Automated Evaluation Pipeline**: Constitutional compliance, performance regression, anomaly detection, and risk assessment
- **Intelligent Approval Workflows**: Auto-approval for low-risk changes, fast-track review for medium risk, full human review for high risk
- **Human Review Integration**: Structured review tasks with priority scheduling and approval/rejection workflows
- **Fast Rollback Mechanism**: <30 second rollback to previous safe versions with validation
- **Constitutional Verification**: Built-in hash validation (`cdd01ef066bc6cf2`)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Evolution     │    │   Evaluation    │    │   Approval      │
│   Requests      │    │   Criteria      │    │   Workflow      │
│                 │────┤                 │────┤                 │
│ Agent Changes   │    │ • Constitutional │    │ • Auto-approve  │
│ Version Updates │    │ • Performance   │    │ • Fast-track    │
│ Risk Assessment │    │ • Anomaly Score │    │ • Human Review  │
└─────────────────┘    │ • Risk Factors  │    └─────────────────┘
                       └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Human Review  │    │   Rollback      │    │   Audit &       │
│   Interface     │    │   Manager       │    │   Monitoring    │
│                 │    │                 │    │                 │
│ • Review Tasks  │    │ • Version Mgmt  │    │ • Decision Log  │
│ • Priority Queue│    │ • Safety Check  │    │ • Metrics       │
│ • Approval UI   │    │ • Fast Recovery │    │ • Compliance    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (for evolution tracking)
- Redis (for caching)
- Docker (for containerized deployment)

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://acgs_user:acgs_password@localhost:5432/acgs_evolution"
export REDIS_URL="redis://localhost:6379/3"
export AUDIT_ENGINE_URL="http://localhost:8003"
export POLICY_ENGINE_URL="http://localhost:8001"

# Run the service
python main.py
```

### 2. Docker Deployment

```bash
# Deploy using the provided script
./deploy.sh
```

### 3. Verify Deployment

```bash
# Check service health
curl http://localhost:8004/health

# Submit test evolution
curl -X POST http://localhost:8004/api/v1/evolution/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": "test_agent",
    "new_version": {
      "version": "1.0.1",
      "changes": {"code_changes": ["Minor bug fix"]},
      "complexity_delta": 0.01
    },
    "change_description": "Test evolution",
    "requester_id": "developer"
  }'
```

## 📡 API Reference

### Submit Evolution Request

**POST** `/api/v1/evolution/submit`

### Get Evolution Status

**GET** `/api/v1/evolution/{evolution_id}`

### Get Pending Reviews

**GET** `/api/v1/reviews/pending`

### Approve/Reject Review

**POST** `/api/v1/reviews/{task_id}/approve`
**POST** `/api/v1/reviews/{task_id}/reject`

### Rollback Agent

**POST** `/api/v1/evolution/{evolution_id}/rollback`

### Get Agent History

**GET** `/api/v1/agents/{agent_id}/history`

## 📊 Monitoring

### Prometheus Metrics

- `evolution_requests_total`: Total evolution requests by agent and decision
- `evaluation_duration_seconds`: Time spent evaluating agents
- `active_human_reviews`: Number of active human reviews
- `rollback_operations_total`: Total rollback operations by reason
- `auto_approval_rate`: Rate of auto-approved evolutions

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "service": "evolution-oversight-service",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "active_reviews": 3
}
```

## 🧪 Testing

```bash
# Run test suite
pytest tests/test_evolution_oversight.py -v

# Performance tests
pytest tests/test_evolution_oversight.py::TestEvolutionOversightPerformance -v
```

## 🔐 Security

- Database security with connection pooling and SSL
- API rate limiting and authentication
- Audit logging for all decisions
- Constitutional compliance validation

## 📄 License

Constitutional AI Governance System (ACGS-1 Lite)
Constitutional Hash: `cdd01ef066bc6cf2`