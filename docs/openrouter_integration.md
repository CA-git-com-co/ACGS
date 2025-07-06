# OpenRouter Integration for ACGS Constitutional AI

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->


This document describes the OpenRouter integration in the ACGS AI Model Service, enabling external model access for constitutional AI validation and governance decisions.

## Overview

The enhanced AI Model Service now supports OpenRouter as a provider, giving access to multiple state-of-the-art AI models for constitutional compliance validation, governance decision analysis, and agent behavior evaluation.

## Features

### 🔧 **External Model Access**
- Access to free AI models via `openrouter/cypher-alpha:free`
- No API costs for development and testing
- Unified interface across all model providers

### 🛡️ **Constitutional AI Validation**
- Automated compliance checking against ACGS constitutional principles
- Structured analysis with violations, recommendations, and confidence scores
- Support for human oversight requirements validation

### 🏛️ **Governance Decision Analysis**
- Multi-stakeholder impact assessment
- Ethical and legal implications analysis
- Risk assessment for governance policies

### 🤖 **Agent Behavior Evaluation**
- Continuous monitoring of agent actions
- Pattern detection for constitutional violations
- Behavioral recommendations and corrections

## Setup

### 1. Install Dependencies

```bash
pip install openai>=1.0.0
```

### 2. Set Environment Variables

```bash
export OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

Get your API key from [OpenRouter](https://openrouter.ai/keys).

### 3. Initialize the Service

```python
from services.shared.ai_model_service import AIModelService, ModelProvider

# Initialize with OpenRouter as default provider
ai_service = AIModelService(default_provider=ModelProvider.OPENROUTER)
```

## Usage Examples

### Constitutional Compliance Validation

```python
import asyncio
from services.shared.ai_model_service import AIModelService

async def validate_agent_decision():
    ai_service = AIModelService()
    
    # Validate an agent's decision
    decision = "Agent wants to process user data without explicit consent"
    
    response = await ai_service.validate_constitutional_compliance(
        content=decision,
        context={
            "agent_id": "EthicsAgent_001",
            "action_type": "data_processing",
            "urgency": "high"
        }
    )
    
    print(f"Compliance Status: {response.content}")
    print(f"Confidence: {response.confidence_score}")
    return response

# Run the validation
asyncio.run(validate_agent_decision())
```

### Governance Decision Analysis

```python
async def analyze_policy_change():
    ai_service = AIModelService()
    
    decision = {
        "type": "policy_update",
        "title": "Enhanced Data Retention Policy", 
        "description": "Extend retention from 30 to 90 days",
        "justification": "Improved model training accuracy"
    }
    
    stakeholders = ["users", "agents", "administrators"]
    
    response = await ai_service.analyze_governance_decision(
        decision=decision,
        stakeholders=stakeholders
    )
    
    print(f"Analysis: {response.content}")
    return response
```

### Agent Behavior Evaluation

```python
async def evaluate_agent_behavior():
    ai_service = AIModelService()
    
    behavior_log = [
        {
            "timestamp": "2024-01-15T10:00:00Z",
            "action": "data_access_request",
            "result": "approved",
            "human_oversight": False
        },
        {
            "timestamp": "2024-01-15T10:05:00Z",
            "action": "critical_decision",
            "risk_level": "high",
            "human_oversight": False  # Potential violation
        }
    ]
    
    response = await ai_service.evaluate_agent_behavior(
        agent_id="EthicsAgent_001",
        behavior_log=behavior_log
    )
    
    print(f"Behavior Assessment: {response.content}")
    return response
```

## Available Models

### Free Tier Model
- `openrouter/cypher-alpha:free` - Free model for all ACGS operations
  - Constitutional validation
  - Governance decision analysis
  - Agent behavior evaluation
  - General chat and completion tasks

## Constitutional Principles

The system validates against these core ACGS principles:

1. **Human Oversight Requirements** - Critical decisions must have human oversight
2. **Data Privacy Protection** - Personal data must be protected
3. **Transparent Decision Making** - Decisions must be explainable
4. **Resource Usage Limits** - Resource usage within defined limits
5. **Security Compliance** - All operations meet security standards

## Integration with ACGS Components

### Worker Agents
```python
# In your worker agent implementation
from services.shared.ai_model_service import AIModelService

class EthicsAgent:
    def __init__(self):
        self.ai_service = AIModelService()
    
    async def validate_decision(self, decision_context):
        # Use OpenRouter for constitutional validation
        response = await self.ai_service.validate_constitutional_compliance(
            content=str(decision_context),
            context={"agent_type": "ethics", "decision_id": decision_context.get("id")}
        )
        return response
```

### Governance Service
```python
# In governance service
async def evaluate_policy_proposal(self, proposal):
    ai_service = AIModelService()
    
    analysis = await ai_service.analyze_governance_decision(
        decision=proposal,
        stakeholders=proposal.get("affected_parties", [])
    )
    
    # Use analysis for policy approval workflow
    return analysis
```

## Performance Monitoring

```python
# Get performance metrics
metrics = ai_service.get_performance_metrics()

print(f"Total Requests: {metrics['total_requests']}")
print(f"Average Response Time: {metrics['average_response_time_ms']}ms")
print(f"Providers Used: {metrics['providers_used']}")
print(f"Models Used: {metrics['models_used']}")
```

## Error Handling

The service includes comprehensive error handling:

```python
try:
    response = await ai_service.validate_constitutional_compliance(content)
    if response.metadata.get("error"):
        print(f"Validation failed: {response.content}")
    else:
        print(f"Validation successful: {response.content}")
except Exception as e:
    print(f"Service error: {e}")
```

## Best Practices

### 1. Model Selection
- Use `openrouter/cypher-alpha:free` for all ACGS operations
- Free tier provides sufficient capability for constitutional validation
- No API costs for development, testing, and production use

### 2. Context Provision
Always provide relevant context for better analysis:
```python
context = {
    "agent_id": "specific_agent",
    "action_type": "data_processing",
    "urgency": "high",
    "stakeholders": ["users", "admins"]
}
```

### 3. Response Validation
Check response metadata for errors and confidence scores:
```python
if response.confidence_score < 0.7:
    # Request human review
    await request_human_oversight(response)
```

### 4. Rate Limiting
Implement appropriate rate limiting for API calls:
```python
import asyncio

# Add delays between requests if needed
await asyncio.sleep(0.1)
```

## Security Considerations

1. **API Key Management** - Store API keys securely in environment variables
2. **Data Privacy** - Ensure sensitive data is not sent to external models
3. **Response Validation** - Always validate AI responses before acting
4. **Audit Logging** - Log all constitutional validation requests

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Error: OpenRouter client not initialized. Check API key.
   ```
   Solution: Set `OPENROUTER_API_KEY` environment variable

2. **Model Not Available**
   ```
   Error: Model not available for provider/type
   ```
   Solution: Check available models with `get_available_models()`

3. **Rate Limiting**
   ```
   Error: Rate limit exceeded
   ```
   Solution: Implement exponential backoff and retry logic

## Next Steps

1. **Integration Testing** - Test with real ACGS agents
2. **Performance Optimization** - Optimize for sub-5ms P99 latency targets
3. **Advanced Features** - Add custom constitutional rules
4. **Monitoring Dashboard** - Create real-time monitoring interface

For more information, see the [ACGS Documentation](../README.md) and [API Reference](api/index.md).
