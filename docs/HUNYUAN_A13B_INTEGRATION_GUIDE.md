# Hunyuan-A13B-Instruct Integration Guide for ACGS

## Overview

This guide covers the integration of Tencent's Hunyuan-A13B-Instruct model into the ACGS (Autonomous Constitutional Governance System) framework. Hunyuan-A13B is a high-performance Chinese language model with multilingual capabilities, ideal for constitutional governance analysis in cross-cultural contexts.

## Model Specifications

- **Model**: Tencent Hunyuan-A13B-Instruct
- **Parameters**: 13 billion
- **Context Length**: 4,096 tokens
- **Languages**: Chinese (Simplified/Traditional), English, Japanese, Korean
- **Architecture**: Transformer-based instruction-tuned model
- **Deployment**: vLLM with Docker containers

## System Requirements

### Hardware Requirements

- **GPU**: NVIDIA GPU with 24GB+ VRAM (A100 80GB recommended)
- **CPU**: 16+ cores
- **Memory**: 64GB+ system RAM
- **Storage**: 100GB+ free space
- **CUDA**: Version 12.8 or higher

### Software Requirements

- Docker with GPU support
- Docker Compose v2
- NVIDIA Container Toolkit
- Python 3.10+

## Quick Start

### 1. Deploy with Docker Compose

```bash
# Start with HuggingFace download (default)
docker-compose -f docker-compose.hunyuan.yml up -d hunyuan-a13b

# Start with ModelScope download (alternative)
docker-compose -f docker-compose.hunyuan.yml --profile modelscope up -d hunyuan-a13b-modelscope
```

### 2. Deploy with Management Script

```bash
# Make script executable
chmod +x scripts/hunyuan_management.sh

# Start the service
./scripts/hunyuan_management.sh start

# Check status
./scripts/hunyuan_management.sh status

# Test inference
./scripts/hunyuan_management.sh test
```

### 3. Deploy with Python Script

```bash
# Make script executable
chmod +x scripts/deploy_hunyuan_a13b.py

# Deploy with all checks
python scripts/deploy_hunyuan_a13b.py deploy

# Deploy with ModelScope source
python scripts/deploy_hunyuan_a13b.py deploy --source modelscope

# Test the deployment
python scripts/deploy_hunyuan_a13b.py test
```

## Configuration Files

### Model Configuration

- **Location**: `config/models/hunyuan-a13b.yaml`
- **Purpose**: Model specifications, performance settings, and ACGS integration parameters

### Docker Configuration

- **Location**: `docker-compose.hunyuan.yml`
- **Purpose**: Container orchestration with GPU support and health monitoring

## API Usage

### Basic Inference

```python
import httpx

# OpenAI-compatible API call
response = httpx.post("http://localhost:8000/v1/chat/completions", json={
    "model": "tencent/Hunyuan-A13B-Instruct",
    "messages": [
        {
            "role": "user",
            "content": "请分析这个政策的宪政含义。Please analyze the constitutional implications of this policy."
        }
    ],
    "max_tokens": 2048,
    "temperature": 0.1
})

print(response.json()["choices"][0]["message"]["content"])
```

### ACGS Integration

```python
from services.shared.ai_model_service import AIModelService

# Initialize AI service
ai_service = AIModelService()

# Use Hunyuan for Chinese governance analysis
response = await ai_service.generate_text(
    prompt="分析中国治理体系中的透明度机制",
    model="hunyuan_a13b",
    use_constitutional_prompt=True,
    constitutional_role="chinese_governance_specialist"
)

print(response.content)
```

## Constitutional Prompt Framework Integration

The Hunyuan model integrates with ACGS's constitutional prompt framework through specialized roles:

### Chinese Governance Specialist

- **Role**: `chinese_governance_specialist`
- **Purpose**: Analyze Chinese policies and governance structures
- **Language**: Bilingual (Chinese/English)
- **Focus**: Constitutional compliance, transparency, accountability

### Multilingual Translator

- **Role**: `multilingual_translator`
- **Purpose**: Accurate translation with constitutional context
- **Languages**: Chinese, English, Japanese, Korean
- **Focus**: Cultural and legal adaptation

### Cross-Cultural Analyst

- **Role**: `cross_cultural_analyst`
- **Purpose**: Analyze policies across cultural contexts
- **Focus**: Cultural sensitivity, legal traditions, social norms

## Management Commands

### Service Management

```bash
# Start service
./scripts/hunyuan_management.sh start [huggingface|modelscope]

# Stop service
./scripts/hunyuan_management.sh stop

# Restart service
./scripts/hunyuan_management.sh restart

# Check status
./scripts/hunyuan_management.sh status

# View logs
./scripts/hunyuan_management.sh logs [lines]
```

### Monitoring and Testing

```bash
# Test inference
./scripts/hunyuan_management.sh test

# Monitor resources
./scripts/hunyuan_management.sh monitor

# Health check
./scripts/hunyuan_management.sh health
```

### Maintenance

```bash
# Pull latest images
./scripts/hunyuan_management.sh pull

# Clean up resources
./scripts/hunyuan_management.sh cleanup
```

## Performance Optimization

### GPU Utilization

- **Tensor Parallel Size**: 4 (recommended for multi-GPU setups)
- **GPU Memory Utilization**: 90% (configurable)
- **Batch Size**: Adaptive based on available memory

### Memory Management

- **Model Caching**: Local cache directories for model weights
- **Context Management**: 4K token context with efficient attention
- **Memory Mapping**: Optimized for 24GB+ GPU memory

### Network Configuration

- **Host Networking**: Direct host network access for minimal latency
- **Health Checks**: Automated health monitoring with 30s intervals
- **Load Balancing**: Ready for multi-instance deployments

## Integration with ACGS Services

### Constitutional AI Service

```python
# Enhanced constitutional analysis endpoint
@app.post("/api/v1/constitutional/chinese-analysis")
async def analyze_chinese_governance(request: GovernanceAnalysisRequest):
    return await ai_service.generate_text(
        prompt=request.policy_text,
        model="hunyuan_a13b",
        constitutional_role="chinese_governance_specialist"
    )
```

### Multilingual Support

```python
# Translation with constitutional context
@app.post("/api/v1/translate/constitutional")
async def translate_constitutional_text(request: TranslationRequest):
    return await ai_service.generate_text(
        prompt=f"Translate: {request.text}",
        model="hunyuan_a13b",
        constitutional_role="multilingual_translator"
    )
```

## Monitoring and Observability

### Health Endpoints

- **Health Check**: `http://localhost:8000/health`
- **Metrics**: `http://localhost:8000/metrics`
- **Model Info**: `http://localhost:8000/v1/models`

### Prometheus Monitoring

- **Configuration**: `config/monitoring/prometheus-hunyuan.yml`
- **Metrics Port**: 9090
- **Scrape Interval**: 10 seconds

### Log Management

- **Location**: `logs/hunyuan/`
- **Format**: JSON structured logs
- **Rotation**: 100MB max size, 3 files retained

## Troubleshooting

### Common Issues

1. **GPU Memory Insufficient**

   ```bash
   # Check GPU memory usage
   nvidia-smi

   # Reduce tensor parallel size or GPU memory utilization
   # Edit docker-compose.hunyuan.yml
   ```

2. **Model Download Failures**

   ```bash
   # Try alternative image
   ./scripts/hunyuan_management.sh start modelscope

   # Check network connectivity
   docker logs acgs-hunyuan-a13b
   ```

3. **API Not Responding**

   ```bash
   # Check container status
   ./scripts/hunyuan_management.sh status

   # View recent logs
   ./scripts/hunyuan_management.sh logs 50

   # Test health endpoint
   curl http://localhost:8000/health
   ```

### Performance Issues

1. **Slow Inference**

   - Increase GPU memory utilization
   - Optimize tensor parallel configuration
   - Check for memory swapping

2. **High Memory Usage**

   - Reduce batch size
   - Enable memory optimization flags
   - Monitor container resource limits

3. **Network Latency**
   - Use host networking mode
   - Optimize Docker network configuration
   - Consider local model deployment

## Security Considerations

### Model Security

- **Access Control**: Restrict API access to authorized services
- **Input Validation**: Validate all inputs for safety and compliance
- **Output Filtering**: Apply constitutional safety filters

### Container Security

- **Privileged Mode**: Required for GPU access (security trade-off)
- **Network Isolation**: Use Docker networks for service isolation
- **Secret Management**: Secure API keys and configuration

### Constitutional Compliance

- **Safety Filters**: Integrated constitutional safety framework
- **Audit Logging**: All interactions logged for compliance
- **Bias Detection**: Monitor for cultural and linguistic biases

## Support and Maintenance

### Regular Maintenance

- Update Docker images monthly
- Monitor GPU driver compatibility
- Review performance metrics weekly

### Backup and Recovery

- **Model Weights**: Cached in persistent volumes
- **Configuration**: Version controlled in git
- **Logs**: Regular log rotation and archival

### Updates and Upgrades

- Monitor Hunyuan model updates
- Test compatibility with ACGS framework
- Plan maintenance windows for updates

## Conclusion

The Hunyuan-A13B-Instruct integration provides ACGS with powerful Chinese language capabilities and cross-cultural governance analysis. The deployment is designed for high availability, constitutional compliance, and optimal performance in production environments.

For additional support or questions, refer to the ACGS documentation or contact the development team.
