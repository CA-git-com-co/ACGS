# ACGS-1 Governance Synthesis Service

## Overview

The Governance Synthesis (GS) Service is a **prototype implementation** of an AI-powered policy generation platform. This service provides basic policy synthesis capabilities with plans for advanced multi-model LLM integration and sophisticated consensus mechanisms.

**Implementation Status**: 🧪 **Prototype**
**Service Port**: 8004
**Service Version**: 3.0.0
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8004/health

## ⚠️ Prototype Limitations

**Current Implementation Status**:
- ✅ Basic policy synthesis endpoints implemented
- ✅ Health check and status monitoring functional
- ✅ Constitutional compliance integration framework
- ⚠️ **Many API routers temporarily disabled due to import issues**
- ⚠️ **Running in "minimal mode" with reduced functionality**
- ⚠️ **Multi-model consensus not fully implemented**
- ⚠️ **Advanced synthesis workflows incomplete**

**Production Readiness**: This service requires router stabilization and feature completion before production deployment.

## Core Features

### AI-Powered Policy Synthesis
- **Multi-Model LLM Ensemble**: Google Gemini (2.0 Flash, 2.5 Pro), DeepSeek-R1, NVIDIA Qwen integration
- **Constitutional Prompting**: AI models trained on constitutional principles and governance frameworks
- **Policy Generation**: Automated generation of enforceable governance policies
- **Multi-Model Consensus**: Weighted voting and consensus mechanisms across AI models
- **Constitutional Compliance**: Real-time validation against constitutional principles

### Advanced Synthesis Capabilities
- **Enhanced Validation**: Comprehensive policy validation with formal verification integration
- **Human Review Integration**: Human-in-the-loop validation for critical policies
- **Proactive Error Prediction**: AI-powered error detection and prevention
- **Batch Processing**: Parallel synthesis of multiple policies
- **Template Management**: Reusable policy templates and frameworks

### Enterprise Features
- **Performance Optimization**: <2s response times with >95% accuracy targets
- **Reliability Enhancement**: >99.9% availability with circuit breaker patterns
- **AlphaEvolve Integration**: Advanced governance optimization algorithms
- **WINA Oversight**: Weighted Intelligence Network Architecture monitoring
- **Real-time Monitoring**: Comprehensive performance and quality metrics

### Constitutional Governance
- **Constitutional Fidelity**: Continuous validation against constitutional hash
- **Compliance Scoring**: Multi-dimensional constitutional compliance assessment
- **Impact Analysis**: Assessment of policy changes on constitutional framework
- **Audit Trail**: Complete audit trail for all policy synthesis activities
- **Transparency Reporting**: Public reporting and governance transparency

## API Endpoints

### Core Policy Synthesis
- `POST /api/v1/synthesize` - Generate policies from constitutional principles
- `POST /api/v1/enhanced-synthesis/synthesize` - Enhanced synthesis with OPA validation
- `POST /api/v1/enhanced-synthesis/multi-model-consensus` - Multi-model consensus synthesis
- `POST /api/v1/enhanced-synthesis/batch` - Batch policy synthesis
- `POST /api/v1/multi-model/synthesize` - LangGraph workflow orchestration

### Constitutional Synthesis
- `POST /api/v1/constitutional/synthesize` - Constitutional policy synthesis
- `GET /api/v1/constitutional/validate` - Constitutional hash validation
- `POST /api/v1/constitutional/compliance` - Constitutional compliance validation
- `GET /api/v1/constitutional/principles` - Available constitutional principles

### Policy Management
- `GET /api/v1/policy-management/policies` - List managed policies
- `POST /api/v1/policy-management/policies` - Create new policy
- `PUT /api/v1/policy-management/policies/{id}` - Update existing policy
- `DELETE /api/v1/policy-management/policies/{id}` - Delete policy
- `GET /api/v1/policy-management/templates` - Policy templates

### Advanced Optimization
- `POST /api/v1/alphaevolve/optimize` - AlphaEvolve governance optimization
- `GET /api/v1/alphaevolve/strategies` - Available optimization strategies
- `POST /api/v1/mab/synthesize` - Multi-Armed Bandit optimized synthesis
- `GET /api/v1/mab/performance` - MAB performance metrics

### Performance & Monitoring
- `GET /api/v1/performance/metrics` - Performance optimization metrics
- `GET /api/v1/performance/targets` - Performance target status
- `GET /api/v1/monitoring/synthesis` - Synthesis monitoring data
- `GET /api/v1/monitoring/constitutional` - Constitutional compliance monitoring

### Phase A3 Production Features
- `POST /api/v1/phase-a3/synthesize` - Phase A3 enhanced synthesis
- `POST /api/v1/phase-a3/consensus` - Phase A3 consensus mechanisms
- `GET /api/v1/phase-a3/strategies` - Available synthesis strategies
- `GET /api/v1/phase-a3/performance` - Phase A3 performance metrics

### System Management
- `GET /health` - Service health with component status
- `GET /api/v1/status` - Detailed API status and capabilities
- `GET /metrics` - Prometheus metrics for monitoring
- `GET /` - Service information and governance workflows

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_governance_synthesis
REDIS_URL=redis://localhost:6379/4

# Service Configuration
SERVICE_NAME=gs-service
SERVICE_VERSION=3.0.0
SERVICE_PORT=8004
APP_ENV=production
LOG_LEVEL=INFO

# AI Model Configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL_FLASH=gemini-2.0-flash-exp
GEMINI_MODEL_PRO=gemini-2.5-pro
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat-v3
NVIDIA_API_KEY=your-nvidia-api-key
NVIDIA_MODEL=nvidia/qwen3-235b
OPENAI_API_KEY=your-openai-fallback-key

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.8
ENABLE_CONSTITUTIONAL_VALIDATION=true

# Synthesis Configuration
MAX_POLICY_LENGTH=5000
MIN_CONSTITUTIONAL_COMPLIANCE=0.8
CONSENSUS_THRESHOLD=0.7
MAX_CONCURRENT_GENERATIONS=10
GENERATION_TIMEOUT_SECONDS=300
RESPONSE_TIME_TARGET_MS=500

# Performance Targets
TARGET_RESPONSE_TIME_MS=2000
TARGET_ACCURACY=0.95
TARGET_AVAILABILITY=0.999
ERROR_REDUCTION_TARGET=0.5

# Service Integration
AC_SERVICE_URL=http://localhost:8001
FV_SERVICE_URL=http://localhost:8003
INTEGRITY_SERVICE_URL=http://localhost:8002
AUTH_SERVICE_URL=http://localhost:8000

# Advanced Features
ENABLE_MULTI_MODEL_CONSENSUS=true
ENABLE_ALPHAEVOLVE_OPTIMIZATION=true
ENABLE_HUMAN_REVIEW_INTEGRATION=true
ENABLE_PROACTIVE_ERROR_PREDICTION=true
ENABLE_BATCH_PROCESSING=true
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
- AI Model API Access (Gemini, DeepSeek, NVIDIA, OpenAI)
- LangGraph and LangChain libraries

### Local Development

```bash
# 1. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv sync

# Alternative: Traditional pip
pip install -r requirements.txt

# 2. Install AI/ML dependencies
pip install langchain langgraph google-generativeai openai

# 3. Setup database
createdb acgs_governance_synthesis
alembic upgrade head

# 4. Configure environment
cp .env.example .env
# Edit .env with your AI model API keys and configuration

# 5. Start service
uv run uvicorn app.main:app --reload --port 8004
```

### Production Deployment

```bash
# Using Docker
docker build -t acgs-gs-service .
docker run -p 8004:8004 --env-file .env acgs-gs-service

# Using systemd
sudo cp gs-service.service /etc/systemd/system/
sudo systemctl enable gs-service
sudo systemctl start gs-service
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
# Test AI model integration
uv run pytest tests/test_ai_models.py -v

# Test multi-model consensus
uv run pytest tests/test_consensus.py -v

# Test constitutional compliance
uv run pytest tests/test_constitutional_synthesis.py -v
```

### Synthesis Tests
```bash
# Test policy synthesis
python scripts/test_policy_synthesis.py

# Test multi-model consensus
python scripts/test_multi_model_consensus.py

# Performance testing
python scripts/test_synthesis_performance.py --concurrent 20
```

## Usage Examples

### Basic Policy Synthesis

```python
import httpx

async def synthesize_governance_policy():
    async with httpx.AsyncClient() as client:
        # Synthesize policy from constitutional principles
        response = await client.post(
            "http://localhost:8004/api/v1/synthesize",
            json={
                "synthesis_goal": "Create privacy protection policy for citizen data",
                "constitutional_principles": [
                    {
                        "type": "privacy_rights",
                        "description": "Citizens have fundamental right to data privacy",
                        "priority": 9
                    },
                    {
                        "type": "transparency",
                        "description": "Government operations must be transparent",
                        "priority": 8
                    }
                ],
                "constraints": [
                    "Must comply with existing data protection laws",
                    "Should not impede legitimate government functions"
                ],
                "target_format": "opa_policy",
                "validation_level": "comprehensive"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "policy_content": result["policy_content"],
            "constitutional_compliance": result["constitutional_compliance"],
            "synthesis_quality": result["synthesis_quality"]
        }
```

### Multi-Model Consensus Synthesis

```python
async def multi_model_consensus_synthesis():
    async with httpx.AsyncClient() as client:
        # Use multiple AI models for consensus-based synthesis
        response = await client.post(
            "http://localhost:8004/api/v1/enhanced-synthesis/multi-model-consensus",
            json={
                "synthesis_goal": "Develop fair hiring policy for government positions",
                "constitutional_principles": [
                    {
                        "type": "equality",
                        "description": "Equal opportunity for all citizens",
                        "priority": 10
                    },
                    {
                        "type": "merit_based",
                        "description": "Selection based on qualifications and merit",
                        "priority": 9
                    }
                ],
                "ai_models": ["gemini-2.5-pro", "deepseek-r1", "nvidia-qwen"],
                "consensus_threshold": 0.95,
                "enable_red_teaming": True,
                "enable_constitutional_fidelity": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "consensus_policy": result["consensus_result"]["policy_content"],
            "model_agreement": result["consensus_result"]["consensus_score"],
            "constitutional_compliance": result["constitutional_compliance"],
            "red_team_analysis": result["red_team_results"]
        }
```

### Batch Policy Synthesis

```python
async def batch_policy_synthesis():
    async with httpx.AsyncClient() as client:
        # Synthesize multiple policies in parallel
        response = await client.post(
            "http://localhost:8004/api/v1/enhanced-synthesis/batch",
            json={
                "requests": [
                    {
                        "synthesis_goal": "Environmental protection policy",
                        "constitutional_principles": [
                            {"type": "environmental_stewardship", "description": "Protect environment for future generations", "priority": 9}
                        ]
                    },
                    {
                        "synthesis_goal": "Education access policy",
                        "constitutional_principles": [
                            {"type": "education_rights", "description": "Universal access to quality education", "priority": 10}
                        ]
                    },
                    {
                        "synthesis_goal": "Healthcare equity policy",
                        "constitutional_principles": [
                            {"type": "healthcare_rights", "description": "Equal access to healthcare services", "priority": 10}
                        ]
                    }
                ],
                "enable_parallel_processing": True,
                "max_concurrent": 5
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "batch_id": result["batch_id"],
            "policies_synthesized": len(result["results"]),
            "overall_quality": result["overall_quality"],
            "synthesis_results": result["results"]
        }
```

### AlphaEvolve Optimization

```python
async def alphaevolve_policy_optimization():
    async with httpx.AsyncClient() as client:
        # Optimize policy using AlphaEvolve algorithms
        response = await client.post(
            "http://localhost:8004/api/v1/alphaevolve/optimize",
            json={
                "policy_content": "Current policy text to optimize",
                "optimization_goals": [
                    "maximize_constitutional_compliance",
                    "minimize_implementation_complexity",
                    "enhance_citizen_satisfaction"
                ],
                "optimization_strategy": "multi_objective",
                "max_iterations": 100,
                "convergence_threshold": 0.95
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        result = response.json()
        return {
            "optimized_policy": result["optimized_policy"],
            "optimization_score": result["optimization_metrics"]["overall_score"],
            "improvements": result["optimization_metrics"]["improvements"],
            "iterations_used": result["optimization_metrics"]["iterations"]
        }
```

## AI Model Integration

### Google Gemini Integration
The service integrates multiple Gemini models for specialized tasks:

```python
# Gemini model configuration
GEMINI_MODELS = {
    "flash": "gemini-2.0-flash-exp",  # Fast synthesis
    "pro": "gemini-2.5-pro",         # Complex reasoning
}

# Constitutional prompting example
constitutional_prompt = f"""
You are a constitutional AI assistant specialized in governance policy synthesis.

CONSTITUTIONAL PRINCIPLES:
{constitutional_principles}

SYNTHESIS GOAL:
{synthesis_goal}

Generate a governance policy that:
1. Fully complies with all constitutional principles
2. Is enforceable and implementable
3. Balances competing interests fairly
4. Includes clear implementation guidelines

Constitutional Hash: {CONSTITUTIONAL_HASH}
"""
```

### Multi-Model Consensus
```python
# Multi-model consensus mechanism
async def get_multi_model_consensus(prompt, context):
    models = ["gemini-2.5-pro", "deepseek-r1", "nvidia-qwen"]
    responses = []

    for model in models:
        response = await generate_policy(model, prompt, context)
        responses.append(response)

    # Weighted consensus based on constitutional compliance
    consensus = calculate_weighted_consensus(responses)
    return consensus
```

### Constitutional Compliance Validation
```python
# Constitutional hash validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def validate_constitutional_compliance(policy_content):
    compliance_score = calculate_compliance_score(policy_content)
    hash_validation = validate_constitutional_hash(policy_content)

    return {
        "compliant": compliance_score >= 0.8,
        "score": compliance_score,
        "hash_valid": hash_validation,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }
```

## Monitoring & Observability

### Health Checks
```bash
# Service health with component status
curl http://localhost:8004/health

# Expected response includes AI model status
{
  "status": "healthy",
  "service": "gs_service_production",
  "version": "3.0.0",
  "synthesis_capabilities": {
    "standard_synthesis": true,
    "enhanced_validation": true,
    "multi_model_consensus": true,
    "human_review_integration": true
  }
}
```

### Performance Metrics
```bash
# Get performance metrics
curl http://localhost:8004/api/v1/performance/metrics

# Synthesis performance targets
curl http://localhost:8004/api/v1/performance/targets

# Constitutional compliance monitoring
curl http://localhost:8004/api/v1/monitoring/constitutional
```

### Real-time Monitoring
```bash
# Monitor synthesis operations
curl http://localhost:8004/api/v1/monitoring/synthesis

# AI model performance
curl http://localhost:8004/api/v1/monitoring/ai-models

# Constitutional validation status
curl http://localhost:8004/api/v1/constitutional/validate
```

## Troubleshooting

### Common Issues

#### AI Model API Failures
```bash
# Test AI model connectivity
python -c "
import google.generativeai as genai
genai.configure(api_key='your-api-key')
model = genai.GenerativeModel('gemini-2.5-pro')
print('Gemini API: OK')
"

# Check API quotas
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models

# Enable fallback models if primary fails
export ENABLE_FALLBACK_MODELS=true
```

#### Constitutional Hash Mismatch
```bash
# Verify constitutional hash
curl http://localhost:8004/api/v1/constitutional/validate | jq '.constitutional_hash'

# Expected: "cdd01ef066bc6cf2"
# Reset if corrupted
python scripts/reset_constitutional_state.py --service gs
```

#### Synthesis Performance Issues
```bash
# Check synthesis performance
curl http://localhost:8004/api/v1/performance/metrics | jq '.current_metrics'

# Monitor response times
curl http://localhost:8004/api/v1/performance/targets | jq '.response_time'

# Optimize synthesis configuration
export RESPONSE_TIME_TARGET_MS=1500
export MAX_CONCURRENT_GENERATIONS=5
```

#### Multi-Model Consensus Failures
```bash
# Check model availability
curl http://localhost:8004/api/v1/monitoring/ai-models

# Reduce consensus threshold if needed
export CONSENSUS_THRESHOLD=0.6

# Enable single-model fallback
export ENABLE_SINGLE_MODEL_FALLBACK=true
```

#### Memory Issues with Large Policies
```bash
# Monitor memory usage
free -h
docker stats acgs-gs-service

# Increase memory limits
# In docker-compose.yml or Kubernetes deployment
memory: 2Gi

# Reduce policy length limits
export MAX_POLICY_LENGTH=3000
```

### Performance Optimization

#### Database Optimization
```sql
-- Optimize synthesis queries
CREATE INDEX idx_synthesis_timestamp ON synthesis_requests(created_at);
CREATE INDEX idx_synthesis_status ON synthesis_requests(status);
CREATE INDEX idx_synthesis_user ON synthesis_requests(user_id);
```

#### Cache Optimization
```bash
# Monitor cache performance
redis-cli info stats | grep hit_rate

# Optimize synthesis caching
redis-cli config set maxmemory 2gb
redis-cli config set maxmemory-policy allkeys-lru
```

#### AI Model Optimization
```python
# Optimize AI model calls
async def optimize_model_calls():
    # Use caching for similar requests
    cache_key = hashlib.md5(prompt.encode()).hexdigest()
    cached_result = await redis.get(cache_key)

    if cached_result:
        return json.loads(cached_result)

    # Batch similar requests
    result = await model.generate_content(prompt)
    await redis.setex(cache_key, 3600, json.dumps(result))

    return result
```

## Security Considerations

### AI Model Security
- **API Key Protection**: Secure storage and rotation of AI model API keys
- **Input Validation**: Comprehensive validation of synthesis requests
- **Output Sanitization**: Sanitization of AI-generated policy content
- **Rate Limiting**: Protection against API abuse and DoS attacks

### Constitutional Security
- **Hash Validation**: Continuous validation of constitutional hash
- **Compliance Monitoring**: Real-time constitutional violation detection
- **Audit Trail**: Complete audit trail for all synthesis activities
- **Access Control**: Role-based access for synthesis operations

## Contributing

1. Follow ACGS-1 coding standards with AI/ML best practices
2. Ensure >90% test coverage for synthesis algorithms
3. Update API documentation for new synthesis endpoints
4. Test AI model integration thoroughly with edge cases
5. Validate constitutional compliance for all changes

## Support

- **Documentation**: [Governance Synthesis API](../../../docs/api/governance_synthesis_service_api.md)
- **Health Check**: http://localhost:8004/health
- **Interactive API Docs**: http://localhost:8004/docs
- **Logs**: `/logs/gs_service.log`
- **Configuration**: `services/core/governance-synthesis/gs_service/.env`
- **AI Model Documentation**:
  - [Google Gemini API](https://ai.google.dev/docs)
  - [DeepSeek API](https://platform.deepseek.com/docs)
  - [NVIDIA API](https://docs.nvidia.com/ai-enterprise/)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set:
   - `AC_SERVICE_URL` - URL of the AC service
   - `INTEGRITY_SERVICE_URL` - URL of the Integrity service

### Running Service

```bash
uvicorn main:app --reload
```

### Running Tests

```bash
pytest tests
```
