# NVIDIA LLM Router Service

## Overview

The NVIDIA LLM Router Service provides intelligent routing of LLM requests to optimal models based on task complexity, content type, and performance requirements. This service integrates with the ACGS-PGP platform to enhance constitutional governance operations through efficient model selection and load balancing.

## Architecture

The service consists of two main components:

### Router Controller

- **Purpose**: Manages routing policies, model configurations, and health monitoring
- **Port**: 8080 (internal)
- **Features**:
  - Task-based routing policies
  - Complexity-based model selection
  - Real-time model health monitoring
  - Performance metrics collection
  - Configuration management

### Router Server

- **Purpose**: Handles incoming LLM requests and routes them to appropriate models
- **Port**: 8081 (internal), exposed via Nginx at `/api/llm-router/`
- **Features**:
  - Request preprocessing and analysis
  - Dynamic model selection
  - Load balancing across model instances
  - Response aggregation and optimization
  - Fallback handling

## Key Features

### 1. Intelligent Routing

- **Task-Based Routing**: Routes requests based on task type (constitutional analysis, policy synthesis, etc.)
- **Complexity-Based Routing**: Analyzes request complexity and routes to appropriate model tiers
- **Performance Optimization**: Considers model latency, throughput, and availability

### 2. ACGS-PGP Integration

- **Constitutional Compliance**: Ensures routed models meet constitutional governance requirements
- **Policy Synthesis Support**: Optimized routing for governance synthesis workflows
- **Audit Trail**: Comprehensive logging for governance audit requirements

### 3. Security & Compliance

- **API Key Management**: Secure storage and rotation of NVIDIA API keys
- **Request Validation**: Input sanitization and validation
- **Access Control**: Integration with ACGS authentication system
- **Audit Logging**: Detailed request/response logging for compliance

### 4. Performance Monitoring

- **Real-time Metrics**: Model performance, latency, and availability tracking
- **Health Checks**: Continuous monitoring of model endpoints
- **Alerting**: Automated alerts for performance degradation or failures
- **Prometheus Integration**: Metrics export for monitoring dashboards

## Configuration

### Environment Variables

```bash
# NVIDIA API Configuration
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1

# Router Configuration
LLM_ROUTER_CONTROLLER_PORT=8080
LLM_ROUTER_SERVER_PORT=8081
LLM_ROUTER_LOG_LEVEL=INFO

# Model Configuration
DEFAULT_MODEL_TIER=standard
FALLBACK_MODEL=nvidia/llama-3.1-nemotron-70b-instruct
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT_SECONDS=30

# ACGS Integration
ENABLE_CONSTITUTIONAL_ROUTING=true
CONSTITUTIONAL_MODEL_TIER=premium
POLICY_SYNTHESIS_MODEL=nvidia/llama-3.1-nemotron-70b-instruct
```

### Routing Policies

The service supports multiple routing strategies:

1. **Task-Based Routing**: Routes based on request metadata and task type
2. **Complexity-Based Routing**: Analyzes request content to determine optimal model
3. **Performance-Based Routing**: Considers current model load and performance metrics
4. **Constitutional Routing**: Special handling for constitutional governance tasks

## API Endpoints

### Router Server (Port 8081)

- `POST /v1/chat/completions` - Main LLM routing endpoint
- `GET /health` - Health check endpoint
- `GET /metrics` - Prometheus metrics endpoint

### Router Controller (Port 8080)

- `GET /config` - Current routing configuration
- `POST /config/reload` - Reload routing policies
- `GET /models/status` - Model health and availability
- `GET /metrics` - Controller metrics

## Usage Examples

### Basic Request

```python
import asyncio
from services.shared.llm_router_client import LLMRouterClient

async def example_request():
    client = LLMRouterClient()

    response = await client.chat_completion(
        messages=[
            {"role": "user", "content": "Analyze this policy for constitutional compliance..."}
        ],
        task_type="constitutional_analysis",
        complexity="high"
    )

    return response
```

### Constitutional Governance Request

```python
async def constitutional_analysis():
    client = LLMRouterClient()

    response = await client.constitutional_request(
        content="Policy text to analyze...",
        analysis_type="compliance_check",
        constitutional_principles=["fairness", "transparency", "accountability"]
    )

    return response
```

## Integration with ACGS Services

### Constitutional AI Service

- Routes constitutional analysis requests to specialized models
- Provides enhanced accuracy for constitutional compliance checks

### Governance Synthesis Service

- Optimizes model selection for policy synthesis workflows
- Supports multi-model consensus for critical governance decisions

### Policy Governance Compliance Service

- Ensures compliance-focused routing for enforcement decisions
- Provides audit trails for governance accountability

## Monitoring and Observability

### Metrics

- Request latency and throughput
- Model selection accuracy
- Error rates and failure modes
- Resource utilization

### Logging

- Request/response audit trails
- Model selection decisions
- Performance metrics
- Error and exception tracking

### Alerting

- Model availability issues
- Performance degradation
- Configuration errors
- Security incidents

## Development and Testing

### Local Development

```bash
# Start the router services
docker-compose -f infrastructure/docker/docker-compose.nvidia-router.yml up

# Run tests
python -m pytest services/platform/nvidia-llm-router/tests/
```

### Configuration Testing

```bash
# Validate routing configuration
python services/platform/nvidia-llm-router/validate_config.py

# Test model connectivity
python services/platform/nvidia-llm-router/test_models.py
```

## Security Considerations

1. **API Key Security**: Keys are encrypted at rest and rotated regularly
2. **Request Validation**: All inputs are sanitized and validated
3. **Access Control**: Integration with ACGS authentication system
4. **Audit Logging**: Comprehensive logging for security monitoring
5. **Network Security**: Internal communication over secure channels

## Performance Optimization

1. **Connection Pooling**: Efficient connection management to NVIDIA APIs
2. **Caching**: Response caching for frequently requested content
3. **Load Balancing**: Intelligent distribution across available models
4. **Fallback Strategies**: Graceful degradation when primary models are unavailable

## Troubleshooting

### Common Issues

1. **Model Unavailability**: Check NVIDIA API status and model health endpoints
2. **High Latency**: Review routing policies and model selection logic
3. **Authentication Errors**: Verify API key configuration and rotation
4. **Configuration Issues**: Validate routing policy syntax and model mappings

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
LLM_ROUTER_LOG_LEVEL=DEBUG
LLM_ROUTER_DEBUG_MODE=true
```

## Contributing

1. Follow ACGS-PGP coding standards
2. Include comprehensive tests for new features
3. Update documentation for configuration changes
4. Ensure security review for API modifications

## License

This service is part of the ACGS-PGP platform and follows the project's licensing terms.
