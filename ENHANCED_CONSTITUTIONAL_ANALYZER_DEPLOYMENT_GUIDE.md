# Enhanced Constitutional Analyzer Deployment Guide

This guide provides detailed instructions for deploying the Enhanced Constitutional Analyzer with Qwen3 Embedding Integration for the ACGS-1 system.

## Overview

The Enhanced Constitutional Analyzer provides semantic similarity analysis using Qwen3 embeddings integrated with the existing MultiModelManager for comprehensive constitutional compliance analysis in the ACGS-1 governance system.

### Key Features

- **Semantic similarity analysis** using Qwen3 embeddings
- **Integration with existing multi-model LLM coordination**
- **Constitutional compliance scoring** with >95% accuracy target
- **Real-time analysis capabilities** for PGC service integration
- **Constitution Hash validation** logic

## Prerequisites

- Python 3.10+
- Redis server (for caching)
- OpenRouter API key (for Qwen3 embeddings)
- Groq API key (for Qwen3-32B model)
- Access to ACGS-1 services infrastructure

## Installation

1. Ensure the Enhanced Constitutional Analyzer components are available in the `services/shared` directory:
   - `qwen3_embedding_client.py`
   - `enhanced_constitutional_analyzer.py`
   - `multi_model_manager.py`

2. Set up the required environment variables:
   ```bash
   export OPENROUTER_API_KEY="your_openrouter_api_key"
   export GROQ_API_KEY="your_groq_api_key"
   export REDIS_URL="redis://localhost:6379"
   export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
   ```

3. Install required dependencies:
   ```bash
   pip install httpx numpy redis fastapi pydantic
   ```

## Integration with PGC Service

The Enhanced Constitutional Analyzer is integrated with the PGC service through the following endpoints:

1. **Enhanced Constitutional Analysis**: `/api/v1/governance/enhanced-constitutional-analysis`
2. **PGC Enforcement Integration**: `/api/v1/governance/pgc-enforcement-integration`
3. **Constitutional Compliance**: `/api/v1/governance/constitutional-compliance` (enhanced)

## Deployment Steps

### 1. Validate Installation

Run the test suite to validate the Enhanced Constitutional Analyzer installation:

```bash
python test_enhanced_constitutional_analyzer.py
```

This will generate a test report with detailed validation results.

### 2. Validate PGC Service Integration

Run the PGC integration test to validate the integration with the PGC service:

```bash
python test_pgc_enhanced_integration.py
```

### 3. Deploy to Production Environment

1. **Update PGC Service**:
   - Ensure the PGC service has access to the Enhanced Constitutional Analyzer components
   - Restart the PGC service to load the new integration

   ```bash
   cd services/core/policy-governance/policy-governance_service
   docker-compose -f infrastructure/docker/docker-compose.yml build
   docker-compose -f infrastructure/docker/docker-compose.yml up -d
   ```

2. **Configure Environment Variables**:
   - Add the required environment variables to your production environment
   - Ensure Redis is properly configured for caching

3. **Monitor Deployment**:
   - Check the PGC service logs for successful initialization
   - Verify the Enhanced Constitutional Analyzer health status

   ```bash
   curl http://localhost:8005/api/v1/governance/status
   ```

## Performance Optimization

To achieve the target performance of <500ms response times and >95% accuracy:

1. **Redis Caching**:
   - Ensure Redis is properly configured for caching
   - Monitor cache hit rates and adjust TTL as needed

2. **Embedding Optimization**:
   - Use batch processing for multiple embedding requests
   - Consider pre-computing embeddings for common constitutional principles

3. **Multi-Model Coordination**:
   - Adjust model weights in `multi_model_manager.py` based on performance
   - Consider using the `EMBEDDING_PRIORITY` consensus strategy for faster responses

## Integration with Quantumagi Solana Deployment

The Enhanced Constitutional Analyzer maintains compatibility with the existing Quantumagi Solana deployment through:

1. **Constitution Hash Validation**:
   - Ensures all analyses use the correct constitution hash (`cdd01ef066bc6cf2`)
   - Validates policy compliance against on-chain constitutional principles

2. **PGC Service Integration**:
   - Provides real-time enforcement recommendations for on-chain governance
   - Maintains compatibility with existing Quantumagi smart contracts

## Governance Workflow Integration

The Enhanced Constitutional Analyzer integrates with all 5 governance workflows:

1. **Policy Creation**:
   - Validates new policies against constitutional principles
   - Provides compliance scoring and recommendations

2. **Constitutional Compliance**:
   - Performs comprehensive compliance analysis
   - Uses semantic similarity for principle alignment

3. **Policy Enforcement**:
   - Provides real-time enforcement recommendations
   - Integrates with PGC service for enforcement actions

4. **WINA Oversight**:
   - Monitors constitutional compliance over time
   - Provides oversight recommendations

5. **Audit/Transparency**:
   - Generates audit trails for constitutional compliance
   - Provides transparency reports

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure the `services/shared` directory is in the Python path
   - Check for missing dependencies

2. **API Key Issues**:
   - Verify OpenRouter and Groq API keys are correctly set
   - Check API rate limits and quotas

3. **Performance Issues**:
   - Monitor Redis cache hit rates
   - Check for network latency to OpenRouter API
   - Consider using mock implementations for testing

### Health Check

Use the health check endpoint to diagnose issues:

```bash
curl http://localhost:8005/api/v1/governance/status
```

## Conclusion

The Enhanced Constitutional Analyzer with Qwen3 Embedding Integration provides a powerful semantic analysis capability for the ACGS-1 governance system. By following this deployment guide, you can successfully integrate this enhancement with the existing Quantumagi Solana deployment while maintaining all performance targets.

For additional support, refer to the test reports and logs generated during the validation process.
