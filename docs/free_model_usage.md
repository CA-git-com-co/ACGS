# Free Model Usage Guide for ACGS OpenRouter Integration

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->


This guide shows how to use the free OpenRouter model (`openrouter/cypher-alpha:free`) for constitutional AI validation in ACGS.

## Quick Start

### 1. Get Your Free API Key

1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Sign up for a free account
3. Generate your API key
4. Set the environment variable:

```bash
export OPENROUTER_API_KEY="your_free_api_key_here"
```

### 2. Basic Usage

```python
from services.shared.ai_model_service import AIModelService, ModelProvider

# Initialize with free model
ai_service = AIModelService(default_provider=ModelProvider.OPENROUTER)

# Constitutional validation (free)
response = await ai_service.validate_constitutional_compliance(
    content="Agent decision to process user data",
    context={"agent_id": "test-agent"}
)

print(f"Validation: {response.content}")
```

## Free Model Capabilities

The `openrouter/cypher-alpha:free` model provides:

✅ **Constitutional Compliance Validation**
- Analyze agent decisions for constitutional violations
- Check human oversight requirements
- Validate data privacy compliance

✅ **Governance Decision Analysis**
- Multi-stakeholder impact assessment
- Policy change evaluation
- Risk assessment for governance updates

✅ **Agent Behavior Evaluation**
- Monitor agent actions for compliance
- Detect concerning behavioral patterns
- Generate improvement recommendations

✅ **General AI Tasks**
- Chat completions
- Text analysis
- Content generation

## Example Use Cases

### 1. Agent Decision Validation

```python
async def validate_agent_decision():
    ai_service = AIModelService()

    decision = """
    EthicsAgent_001 wants to access user personal data
    for bias analysis without explicit consent.
    """

    response = await ai_service.validate_constitutional_compliance(
        content=decision,
        context={
            "agent_id": "EthicsAgent_001",
            "action_type": "data_access",
            "risk_level": "high"
        }
    )

    # Response will include:
    # - Compliance status
    # - Specific violations found
    # - Recommendations
    # - Risk assessment

    return response
```

### 2. Policy Change Analysis

```python
async def analyze_policy_change():
    ai_service = AIModelService()

    policy_change = {
        "type": "data_retention_update",
        "current": "30 days retention",
        "proposed": "90 days retention",
        "justification": "Better model training"
    }

    stakeholders = ["users", "agents", "administrators"]

    response = await ai_service.analyze_governance_decision(
        decision=policy_change,
        stakeholders=stakeholders
    )

    return response
```

### 3. Continuous Agent Monitoring

```python
async def monitor_agent_behavior():
    ai_service = AIModelService()

    behavior_log = [
        {
            "timestamp": "2024-01-15T10:00:00Z",
            "action": "critical_decision",
            "human_oversight": False,  # Potential issue
            "risk_level": "high"
        }
    ]

    response = await ai_service.evaluate_agent_behavior(
        agent_id="EthicsAgent_001",
        behavior_log=behavior_log
    )

    return response
```

## Integration with ACGS Components

### Worker Agents

```python
class EthicsAgent:
    def __init__(self):
        self.ai_service = AIModelService()

    async def validate_decision(self, decision_context):
        # Use free model for validation
        response = await self.ai_service.validate_constitutional_compliance(
            content=str(decision_context),
            context={"agent_type": "ethics"}
        )

        # Parse response for compliance status
        is_compliant = "compliant" in response.content.lower()
        return is_compliant, response.content
```

### Governance Service

```python
class GovernanceService:
    def __init__(self):
        self.ai_service = AIModelService()

    async def evaluate_policy(self, policy_proposal):
        # Analyze with free model
        analysis = await self.ai_service.analyze_governance_decision(
            decision=policy_proposal,
            stakeholders=policy_proposal.get("affected_parties", [])
        )

        return analysis
```

## Performance Considerations

### Free Model Limitations

- **Rate Limits**: Free tier has usage limits
- **Response Time**: May be slower than paid models
- **Capability**: Good for most ACGS tasks but not as sophisticated as premium models

### Optimization Tips

1. **Batch Requests**: Group multiple validations when possible
2. **Cache Results**: Cache validation results for similar decisions
3. **Async Processing**: Use async/await for better performance
4. **Error Handling**: Implement retry logic for rate limits

```python
import asyncio
from functools import wraps

def retry_on_rate_limit(max_retries=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise
            return wrapper
    return decorator

@retry_on_rate_limit()
async def validate_with_retry(ai_service, content):
    return await ai_service.validate_constitutional_compliance(content)
```

## Cost Benefits

### Free Tier Advantages

- **$0 Cost**: No API charges for development or production
- **No Credit Card**: No payment method required
- **Unlimited Development**: Test and iterate without cost concerns
- **Production Ready**: Suitable for production ACGS deployments

### When to Consider Paid Models

- **High Volume**: Very high request volumes
- **Low Latency**: Sub-second response requirements
- **Advanced Analysis**: Complex legal or ethical analysis
- **Custom Models**: Specialized constitutional AI models

## Monitoring and Metrics

```python
# Get performance metrics
metrics = ai_service.get_performance_metrics()

print(f"Total Requests: {metrics['total_requests']}")
print(f"Average Response Time: {metrics['average_response_time_ms']}ms")
print(f"Success Rate: {calculate_success_rate(metrics)}")

def calculate_success_rate(metrics):
    if metrics['total_requests'] == 0:
        return 0.0

    # Calculate based on error responses
    error_responses = sum(1 for response in ai_service.response_history
                         if response.metadata.get('error', False))

    success_rate = (metrics['total_requests'] - error_responses) / metrics['total_requests']
    return success_rate * 100
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Error: OpenRouter client not initialized. Check API key.
   ```
   **Solution**: Set `OPENROUTER_API_KEY` environment variable

2. **Rate Limit Exceeded**
   ```
   Error: Rate limit exceeded for free tier
   ```
   **Solution**: Implement retry logic with exponential backoff

3. **Model Not Available**
   ```
   Error: Model not available
   ```
   **Solution**: Verify you're using `openrouter/cypher-alpha:free`

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed API calls and responses
ai_service = AIModelService()
```

## Next Steps

1. **Set up your free API key** from OpenRouter
2. **Run the example script** to test the integration
3. **Integrate with your ACGS agents** for constitutional validation
4. **Monitor performance** and adjust as needed
5. **Scale up** to paid models if needed for high-volume use

## Support

- **OpenRouter Documentation**: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- **ACGS Documentation**: [../README.md](../README.md)
- **Example Code**: [../examples/openrouter_constitutional_validation.py](../examples/openrouter_constitutional_validation.py)

## Support

- **OpenRouter Documentation**: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- **ACGS Documentation**: [../README.md](../README.md)
- **Example Code**: [../examples/openrouter_constitutional_validation.py](../examples/openrouter_constitutional_validation.py)

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)
- [ACGS Implementation Guide](../deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [ACGS-PGP Operational Deployment Guide](../deployment/ACGS_PGP_OPERATIONAL_DEPLOYMENT_GUIDE.md)
- [ACGS-PGP Troubleshooting Guide](../deployment/ACGS_PGP_TROUBLESHOOTING_GUIDE.md)
- [ACGS-PGP Setup Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status Dashboard](../operations/SERVICE_STATUS.md)
- [ACGS Configuration Guide](../configuration/README.md)
- [ACGS-2 Technical Specifications - 2025 Edition](../TECHNICAL_SPECIFICATIONS_2025.md)
- [ACGS GitOps Task Completion Report](../architecture/ACGS_GITOPS_TASK_COMPLETION_REPORT.md)
- [ACGS GitOps Comprehensive Validation Report](../architecture/ACGS_GITOPS_COMPREHENSIVE_VALIDATION_REPORT.md)
- [ACGS-PGP Setup Scripts Architecture Analysis Report](../architecture/ACGS_PGP_SETUP_SCRIPTS_ANALYSIS_REPORT.md)
- [ACGS Documentation Quality Metrics and Continuous Improvement](DOCUMENTATION_QUALITY_METRICS.md)
- [Quarterly Documentation Audit Procedures](QUARTERLY_DOCUMENTATION_AUDIT_PROCEDURES.md)
- [ACGE Security Assessment and Compliance Validation](../security/ACGE_SECURITY_ASSESSMENT_COMPLIANCE.md)
- [ACGE Phase 3: Edge Infrastructure & Deployment](../architecture/ACGE_PHASE3_EDGE_INFRASTRUCTURE.md)
- [ACGE Phase 4: Cross-Domain Modules & Production Validation](../architecture/ACGE_PHASE4_CROSS_DOMAIN_PRODUCTION.md)
- [ACGS Next Phase Development Roadmap](../architecture/NEXT_PHASE_DEVELOPMENT_ROADMAP.md)
- [ACGS Remaining Tasks Completion Summary](REMAINING_TASKS_COMPLETION_SUMMARY.md)
- [GitHub Actions Systematic Fixes - Final Report](workflow_systematic_fixes_final_report.md)
- [GitHub Actions Workflow Systematic Fixes Summary](workflow_fixes_summary.md)
- [Security Input Validation Integration - Completion Report](security_validation_completion_report.md)
- [Phase 2: Enhanced Production Readiness - COMPLETION REPORT](phase2_completion_report.md)
- [Phase 1: Critical Path to Basic Production Readiness - COMPLETION REPORT](phase1_completion_report.md)
- [OpenRouter Integration for ACGS Constitutional AI](openrouter_integration.md)

The free model provides excellent value for ACGS constitutional AI validation without any cost barriers!


## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.
