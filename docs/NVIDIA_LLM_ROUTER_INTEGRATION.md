# NVIDIA LLM Router Integration Guide

## Overview

The NVIDIA LLM Router provides intelligent routing of LLM requests to optimal models based on task complexity, content type, and performance requirements. This integration enhances the ACGS-PGP platform's constitutional governance capabilities through efficient model selection and load balancing.

## Architecture

### Service Components

1. **Router Controller** (Port 8080)

   - Manages routing policies and model configurations
   - Monitors model health and performance
   - Handles configuration updates and policy management

2. **Router Server** (Port 8081)

   - Processes incoming LLM requests
   - Performs intelligent model selection
   - Routes requests to appropriate NVIDIA models

3. **Client Library** (`services/shared/llm_router_client.py`)
   - Async-compatible Python client
   - High-level interfaces for common tasks
   - Session management and error handling

## Integration Methods

### 1. Client Library Integration (Recommended)

The client library provides the easiest integration method for ACGS services.

#### Basic Usage

```python
from services.shared.llm_router_client import LLMRouterClient, TaskType, ComplexityLevel

async def example_usage():
    async with LLMRouterClient() as client:
        response = await client.chat_completion(
            messages=[
                {"role": "user", "content": "Analyze this policy for constitutional compliance..."}
            ],
            task_type=TaskType.CONSTITUTIONAL_ANALYSIS,
            complexity=ComplexityLevel.HIGH
        )
        return response.content
```

#### Constitutional Analysis

```python
async def constitutional_analysis_example():
    async with LLMRouterClient() as client:
        response = await client.constitutional_request(
            content="Policy text to analyze...",
            analysis_type="compliance_check",
            constitutional_principles=["fairness", "transparency", "accountability"]
        )
        return response.content
```

#### Policy Synthesis

```python
async def policy_synthesis_example():
    async with LLMRouterClient() as client:
        response = await client.policy_synthesis_request(
            requirements="Create a policy for data privacy protection",
            context="Healthcare data processing",
            stakeholders=["patients", "healthcare_providers", "regulators"]
        )
        return response.content
```

### 2. Direct API Integration

For services that need direct HTTP API access.

#### Chat Completions Endpoint

```python
import aiohttp

async def direct_api_example():
    async with aiohttp.ClientSession() as session:
        payload = {
            "messages": [
                {"role": "user", "content": "Your request here"}
            ],
            "task_type": "constitutional_analysis",
            "complexity": "high",
            "max_tokens": 2048,
            "temperature": 0.1
        }

        async with session.post(
            "http://nvidia_llm_router_server:8081/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            result = await response.json()
            return result["choices"][0]["message"]["content"]
```

#### Model Selection Endpoint

```python
async def get_available_models():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://nvidia_llm_router_server:8081/v1/models"
        ) as response:
            models = await response.json()
            return models
```

### 3. External Access via Nginx

For external applications or frontend integration.

#### External API Endpoints

- **Base URL**: `http://localhost:8000/api/llm-router/`
- **Chat Completions**: `POST /api/llm-router/v1/chat/completions`
- **Models**: `GET /api/llm-router/v1/models`
- **Health Check**: `GET /api/llm-router-health`

#### JavaScript/Frontend Example

```javascript
async function callLLMRouter(messages, taskType = null) {
  const payload = {
    messages: messages,
    task_type: taskType,
    max_tokens: 2048,
    temperature: 0.2,
  };

  const response = await fetch('/api/llm-router/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify(payload),
  });

  const result = await response.json();
  return result.choices[0].message.content;
}
```

## Routing Policies

### Task-Based Routing

The router automatically selects optimal models based on task type:

#### Constitutional AI Tasks

- **constitutional_analysis**: Routes to premium models (Nemotron-70B, Llama-405B)
- **constitutional_compliance**: Uses high-accuracy models with audit trails
- **policy_synthesis**: Employs multi-model consensus for critical decisions

#### Governance Synthesis Tasks

- **policy_synthesis**: Premium models with multi-model validation
- **policy_review**: Balanced models with good accuracy/speed ratio
- **compliance_enforcement**: High-accuracy models with audit logging

#### General Tasks

- **content_generation**: Standard models for balanced performance
- **summarization**: Efficient models for speed
- **classification**: Fast models with good accuracy

### Complexity-Based Routing

The router analyzes request complexity and routes accordingly:

#### High Complexity

- **Indicators**: "constitutional", "multi-step", "reasoning", "analysis"
- **Models**: Premium tier (Nemotron-70B, Llama-405B)
- **Use Cases**: Constitutional analysis, complex policy synthesis

#### Medium Complexity

- **Indicators**: "review", "evaluate", "compare", "assess"
- **Models**: Standard tier (Llama-70B, Llama-8B)
- **Use Cases**: Policy review, content analysis

#### Low Complexity

- **Indicators**: "summarize", "classify", "extract", "list"
- **Models**: Efficient tier (Llama-8B, Mistral-7B)
- **Use Cases**: Summarization, simple classification

## Configuration

### Environment Variables

```bash
# Required
NVIDIA_API_KEY=your_nvidia_api_key_here

# Optional - Router Configuration
LLM_ROUTER_LOG_LEVEL=INFO
DEFAULT_MODEL_TIER=standard
FALLBACK_MODEL=nvidia/llama-3.1-8b-instruct
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT_SECONDS=30

# ACGS Integration
ENABLE_CONSTITUTIONAL_ROUTING=true
CONSTITUTIONAL_MODEL_TIER=premium
POLICY_SYNTHESIS_MODEL=nvidia/llama-3.1-nemotron-70b-instruct
```

### Routing Configuration

The routing policies are defined in `services/platform/nvidia-llm-router/router-controller/config.yml`:

```yaml
# Task-based routing example
task_routing:
  constitutional_analysis:
    preferred_models: ['nvidia/llama-3.1-nemotron-70b-instruct']
    fallback_models: ['nvidia/llama-3.1-70b-instruct']
    min_confidence_threshold: 0.95
    require_audit_trail: true
```

## Service Integration Examples

### Constitutional AI Service Integration

```python
# In services/core/constitutional-ai/ac_service/app/main.py
from services.shared.llm_router_client import LLMRouterClient, TaskType

class ConstitutionalAnalyzer:
    def __init__(self):
        self.llm_client = LLMRouterClient()

    async def analyze_constitutional_compliance(self, content: str) -> dict:
        response = await self.llm_client.constitutional_request(
            content=content,
            analysis_type="compliance_check",
            constitutional_principles=["fairness", "transparency", "accountability"]
        )

        return {
            "analysis": response.content,
            "model_used": response.model_used,
            "confidence": response.confidence_score,
            "latency_ms": response.latency_ms
        }
```

### Governance Synthesis Service Integration

```python
# In services/core/governance-synthesis/gs_service/app/main.py
from services.shared.llm_router_client import LLMRouterClient, TaskType

class PolicySynthesizer:
    def __init__(self):
        self.llm_client = LLMRouterClient()

    async def synthesize_policy(self, requirements: str, context: str) -> dict:
        response = await self.llm_client.policy_synthesis_request(
            requirements=requirements,
            context=context,
            stakeholders=["citizens", "government", "experts"]
        )

        return {
            "policy": response.content,
            "model_used": response.model_used,
            "synthesis_metadata": response.metadata
        }
```

### Policy Governance Compliance Integration

```python
# In services/core/policy-governance/pgc_service/app/main.py
from services.shared.llm_router_client import LLMRouterClient, TaskType

class ComplianceEnforcer:
    def __init__(self):
        self.llm_client = LLMRouterClient()

    async def detect_violations(self, content: str, policies: list) -> dict:
        messages = [
            {"role": "system", "content": "You are a compliance enforcement AI."},
            {"role": "user", "content": f"Check this content against policies: {content}"}
        ]

        response = await self.llm_client.chat_completion(
            messages=messages,
            task_type=TaskType.VIOLATION_DETECTION,
            metadata={"policies": policies}
        )

        return {
            "violations": response.content,
            "model_used": response.model_used,
            "enforcement_metadata": response.metadata
        }
```

## Monitoring and Observability

### Health Checks

```python
async def check_router_health():
    async with LLMRouterClient() as client:
        health = await client.health_check()
        return health["status"] == "healthy"
```

### Metrics Collection

```python
async def get_router_metrics():
    async with LLMRouterClient() as client:
        metrics = await client.get_metrics()
        return {
            "request_count": metrics.get("request_count", 0),
            "average_latency": metrics.get("average_latency_ms", 0),
            "error_rate": metrics.get("error_rate", 0)
        }
```

### Prometheus Metrics

The router exposes Prometheus metrics at:

- Controller: `http://nvidia_llm_router_controller:9092/metrics`
- Server: `http://nvidia_llm_router_server:9093/metrics`
- Via Nginx: `http://localhost:8000/metrics/llm-router`

## Deployment

### Docker Compose

```bash
# Start the NVIDIA LLM Router services
docker-compose -f infrastructure/docker/docker-compose.nvidia-router.yml up -d

# Verify services are running
docker-compose -f infrastructure/docker/docker-compose.nvidia-router.yml ps
```

### Integration with Main Stack

Add to your main `infrastructure/docker/docker-compose.yml`:

```yaml
services:
  # ... existing services ...

  nvidia_llm_router_controller:
    extends:
      file: infrastructure/docker/docker-compose.nvidia-router.yml
      service: nvidia_llm_router_controller

  nvidia_llm_router_server:
    extends:
      file: infrastructure/docker/docker-compose.nvidia-router.yml
      service: nvidia_llm_router_server
```

## Security Considerations

### API Key Management

- API keys are encrypted using AES-256 encryption
- Keys are stored securely in the database with rotation support
- Environment variable fallbacks for development

### Request Validation

- All requests are validated and sanitized
- Rate limiting prevents abuse
- Authentication integration with ACGS auth system

### Audit Logging

- All constitutional governance requests are logged
- Audit trails maintained for compliance
- Request/response metadata tracked

## Troubleshooting

### Common Issues

1. **Model Unavailable**

   ```bash
   # Check model status
   curl http://localhost:8081/v1/models
   ```

2. **High Latency**

   ```bash
   # Check router metrics
   curl http://localhost:8081/metrics
   ```

3. **Authentication Errors**
   ```bash
   # Verify API key
   docker logs acgs_nvidia_llm_router_server
   ```

### Debug Mode

Enable debug logging:

```bash
LLM_ROUTER_DEBUG_MODE=true
LLM_ROUTER_LOG_LEVEL=DEBUG
```

## Performance Optimization

### Connection Pooling

The client library uses connection pooling for optimal performance:

```python
# Reuse client instance for multiple requests
client = LLMRouterClient()
# ... make multiple requests ...
await client.close()
```

### Caching

Response caching is enabled for non-sensitive requests:

- Cache TTL: 5 minutes
- Excluded tasks: constitutional_analysis, compliance_enforcement

### Load Balancing

Multiple router instances can be deployed for high availability:

```yaml
# In infrastructure/docker/docker-compose.yml
nvidia_llm_router_server_2:
  # ... same configuration as nvidia_llm_router_server ...
  container_name: acgs_nvidia_llm_router_server_2
```

## Best Practices

1. **Use Task Types**: Always specify task_type for optimal routing
2. **Set Appropriate Complexity**: Help the router select the right model tier
3. **Handle Errors Gracefully**: Implement retry logic and fallbacks
4. **Monitor Performance**: Track latency and error rates
5. **Secure API Keys**: Use the encrypted key management system
6. **Cache Responses**: Cache non-sensitive responses when possible

## Support

For issues and questions:

1. Check the service logs: `docker logs acgs_nvidia_llm_router_server`
2. Verify configuration: Review `router-controller/config.yml`
3. Test connectivity: Use health check endpoints
4. Monitor metrics: Check Prometheus metrics for performance issues
