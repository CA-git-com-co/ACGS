# ACGS-1 Constitutional AI Service

## Overview

The Constitutional AI (AC) Service is the core constitutional compliance engine for the ACGS-PGP system. It provides advanced constitutional analysis, compliance validation, formal verification integration, and real-time constitutional violation detection with sophisticated governance capabilities.

**Service Port**: 8001
**Service Version**: 3.0.0
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8001/health

## Core Features

### Constitutional Management
- **Principles Management**: CRUD operations for constitutional principles and guidelines
- **Constitutional Council**: Democratic governance with voting mechanisms and amendments
- **Compliance Validation**: Real-time constitutional compliance checking and scoring
- **Conflict Resolution**: Automated and manual conflict resolution mechanisms
- **Constitutional Impact Analysis**: Assessment of policy changes on constitutional framework

### Advanced Capabilities
- **Formal Verification Integration**: Integration with FV service for mathematical proof validation
- **Real-time Violation Detection**: Continuous monitoring for constitutional violations
- **Sophisticated Compliance Scoring**: Multi-dimensional compliance assessment and ranking
- **Audit Logging**: Comprehensive constitutional event logging and reporting
- **AI Model Integration**: Google Gemini, DeepSeek-R1 for constitutional analysis

## API Endpoints

### Constitutional Principles
- `GET /api/v1/principles` - List all constitutional principles
- `POST /api/v1/principles` - Create new constitutional principle
- `PUT /api/v1/principles/{id}` - Update existing principle
- `DELETE /api/v1/principles/{id}` - Remove principle (requires council approval)
- `GET /api/v1/principles/{id}/compliance` - Get principle compliance metrics

### Constitutional Council
- `GET /api/v1/constitutional-council/members` - List council members
- `POST /api/v1/constitutional-council/proposals` - Submit constitutional proposal
- `POST /api/v1/constitutional-council/vote` - Cast vote on proposal
- `GET /api/v1/constitutional-council/voting-history` - View voting history
- `GET /api/v1/voting/mechanisms` - Available voting mechanisms

### Compliance & Validation
- `POST /api/v1/constitutional/validate` - Validate constitutional compliance
- `GET /api/v1/compliance/status` - Overall compliance status
- `POST /api/v1/compliance/analyze` - Analyze constitutional impact
- `GET /api/v1/compliance/violations` - Recent constitutional violations
- `POST /api/v1/compliance/remediate` - Remediate compliance issues

### Conflict Resolution
- `POST /api/v1/conflict-resolution/submit` - Submit conflict for resolution
- `GET /api/v1/conflict-resolution/cases` - List active conflict cases
- `POST /api/v1/conflict-resolution/resolve` - Resolve conflict case
- `GET /api/v1/conflict-resolution/history` - Conflict resolution history

### Monitoring & Analytics
- `GET /api/v1/fidelity/metrics` - Constitutional fidelity metrics
- `GET /api/v1/dashboard/status` - Real-time dashboard data
- `WS /api/v1/dashboard/ws` - WebSocket dashboard updates
- `GET /api/v1/analytics/trends` - Constitutional compliance trends

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_constitutional
REDIS_URL=redis://localhost:6379/1

# Service Configuration
SERVICE_NAME=ac-service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8001
APP_ENV=production
LOG_LEVEL=INFO

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.8
CONSTITUTIONAL_VALIDATION_ENABLED=true

# AI Model Integration
GEMINI_API_KEY=your-gemini-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
NVIDIA_API_KEY=your-nvidia-api-key

# Service Integration
AUTH_SERVICE_URL=http://localhost:8000
FV_SERVICE_URL=http://localhost:8003
GS_SERVICE_URL=http://localhost:8004
INTEGRITY_SERVICE_URL=http://localhost:8002

# Security Configuration
AUTH_SERVICE_TOKEN=your-internal-service-token
RATE_LIMIT_REQUESTS_PER_MINUTE=100
ENABLE_AUDIT_LOGGING=true
```

### Resource Limits

```yaml
resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 1Gi
```

## Installation & Deployment

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Access to AI model APIs (Gemini, DeepSeek, NVIDIA)

### Local Development

```bash
# 1. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# 2. Setup database
createdb acgs_constitutional
alembic upgrade head

# 3. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 4. Start service
uv run uvicorn main:app --reload --port 8001
```

### Production Deployment

```bash
# Using Docker
docker build -t acgs-ac-service .
docker run -p 8001:8001 --env-file .env acgs-ac-service

# Using systemd
sudo cp ac-service.service /etc/systemd/system/
sudo systemctl enable ac-service
sudo systemctl start ac-service
```

## Testing

### Unit Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html
```

### Integration Tests
```bash
# Test constitutional validation
uv run pytest tests/test_constitutional_validation.py -v

# Test council workflows
uv run pytest tests/test_council_workflows.py -v
```

### Constitutional Compliance Tests
```bash
# Test compliance validation
python scripts/test_constitutional_compliance.py

# Test AI model integration
python scripts/test_enhanced_constitutional_analyzer.py
```

## Usage Examples

### Constitutional Validation

```python
import httpx

async def validate_constitutional_compliance():
    async with httpx.AsyncClient() as client:
        # Validate action against constitution
        response = await client.post(
            "http://localhost:8001/api/v1/constitutional/validate",
            json={
                "action": "policy_creation",
                "context": {
                    "policy_id": "pol_123",
                    "user_id": "user_456",
                    "metadata": {
                        "category": "privacy",
                        "impact_level": "high"
                    }
                },
                "validation_level": "comprehensive"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "compliant": result["data"]["validation_result"]["compliant"],
            "confidence": result["data"]["validation_result"]["confidence"],
            "constitutional_hash": result["data"]["constitutional_hash"]
        }
```

### Constitutional Council Voting

```python
async def submit_constitutional_proposal():
    async with httpx.AsyncClient() as client:
        # Submit proposal to constitutional council
        proposal_response = await client.post(
            "http://localhost:8001/api/v1/constitutional-council/proposals",
            json={
                "title": "Privacy Rights Amendment",
                "description": "Enhance privacy protections for citizens",
                "proposed_changes": [
                    {
                        "section": "privacy_rights",
                        "change_type": "amendment",
                        "new_text": "Citizens have absolute right to data privacy"
                    }
                ],
                "justification": "Strengthening constitutional privacy protections"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        proposal_id = proposal_response.json()["data"]["proposal_id"]

        # Cast vote on proposal
        vote_response = await client.post(
            "http://localhost:8001/api/v1/constitutional-council/vote",
            json={
                "proposal_id": proposal_id,
                "vote": "approve",
                "reasoning": "Necessary for constitutional compliance"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        return vote_response.json()
```

## AI Model Integration

### Google Gemini Integration
- **Model**: Gemini 2.5 Pro for constitutional analysis
- **Use Cases**: Complex constitutional reasoning, impact analysis
- **Configuration**: Set `GEMINI_API_KEY` in environment

### DeepSeek-R1 Integration
- **Model**: DeepSeek-R1 for formal reasoning
- **Use Cases**: Logical validation, proof generation
- **Configuration**: Set `DEEPSEEK_API_KEY` in environment

### NVIDIA Qwen Integration
- **Model**: NVIDIA Qwen for multi-model consensus
- **Use Cases**: Constitutional compliance scoring, conflict resolution
- **Configuration**: Set `NVIDIA_API_KEY` in environment

## Monitoring & Observability

### Health Checks
```bash
# Service health
curl http://localhost:8001/health

# Constitutional compliance status
curl http://localhost:8001/api/v1/compliance/status
```

### Metrics
```bash
# Prometheus metrics
curl http://localhost:8001/metrics

# Constitutional fidelity metrics
curl http://localhost:8001/api/v1/fidelity/metrics
```

### Real-time Dashboard
```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8001/api/v1/dashboard/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Constitutional update:', data);
};
```

## Troubleshooting

### Common Issues

#### Constitutional Hash Mismatch
```bash
# Verify constitutional hash
curl http://localhost:8001/api/v1/constitutional/validate | jq -r '.constitutional_hash'

# Expected: cdd01ef066bc6cf2
# If different, reset constitutional state
python scripts/fix_constitutional_compliance_auth.py
```

#### AI Model API Errors
```bash
# Test Gemini API connectivity
python -c "
import os
from google.generativeai import configure, GenerativeModel
configure(api_key=os.getenv('GEMINI_API_KEY'))
model = GenerativeModel('gemini-pro')
print('Gemini API: OK')
"
```

#### Compliance Validation Failures
```bash
# Check compliance threshold
grep "CONSTITUTIONAL_COMPLIANCE_THRESHOLD" .env

# Review recent violations
curl http://localhost:8001/api/v1/compliance/violations
```

## Security Considerations

### Constitutional Integrity
- Constitutional hash validation on every request
- Immutable constitutional principles with versioning
- Audit trail for all constitutional changes
- Multi-signature requirements for amendments

### Access Control
- Role-based access for constitutional council members
- Graduated permissions for different compliance levels
- Service-to-service authentication for internal calls
- Rate limiting for constitutional validation endpoints

## Support

- **Documentation**: [Constitutional AI API](../../../docs/api/constitutional_ai_service_api.md)
- **Health Check**: http://localhost:8001/health
- **Interactive API Docs**: http://localhost:8001/docs
- **Logs**: `/logs/ac_service.log`
- **Configuration**: `services/core/constitutional-ai/ac_service/.env`
