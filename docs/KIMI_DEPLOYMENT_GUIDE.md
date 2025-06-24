# ACGS Kimi-Dev-72B Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Kimi-Dev-72B model using vLLM within the ACGS (Autonomous Constitutional Governance System) infrastructure. Kimi-Dev-72B is a state-of-the-art coding LLM that achieves 60.4% performance on SWE-bench Verified, setting new standards for open-source software engineering models.

### Key Features

- **SWE-bench Excellence**: 60.4% performance on SWE-bench Verified
- **Reinforcement Learning Optimized**: Trained via large-scale RL with real repository patching
- **Two-Stage Framework**: File localization + precise code editing
- **Extended Context**: Support for 131K token sequences
- **ACGS Integration**: Full constitutional compliance and governance workflow integration

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [SWE-bench Setup](#swe-bench-setup)
4. [Configuration](#configuration)
5. [Deployment Options](#deployment-options)
6. [Monitoring](#monitoring)
7. [Testing](#testing)
8. [SWE-bench Usage](#swe-bench-usage)
9. [Troubleshooting](#troubleshooting)
10. [Integration with ACGS](#integration-with-acgs)

## Prerequisites

### System Requirements

- **GPU**: NVIDIA GPU with at least 48GB VRAM (recommended: A100 80GB or H100)
- **RAM**: Minimum 64GB system RAM
- **Storage**: 200GB+ free space for model cache
- **OS**: Ubuntu 20.04+ or compatible Linux distribution

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Container Toolkit
- CUDA 11.8+ or 12.0+
- Python 3.9+ (for testing scripts)

### Environment Setup

1. **Install NVIDIA Container Toolkit**:
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

2. **Verify GPU Access**:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
   ```

## Quick Start

### 1. Environment Configuration

Ensure your `.env` file contains the required configuration:

```bash
# Verify HuggingFace token is set
grep HUGGINGFACE_API_KEY .env

# Verify Kimi service URL is configured
grep KIMI_SERVICE_URL .env
```

### 2. Deploy the Service

```bash
# Deploy Kimi service
./scripts/deploy_kimi_service.sh

# Check deployment status
./scripts/manage_kimi_service.sh status
```

### 3. Verify Deployment

```bash
# Run health check
./scripts/manage_kimi_service.sh health

# Run comprehensive tests
python3 scripts/test_kimi_integration.py
```

### 4. Test API

```bash
# Simple test
curl -X POST "http://localhost:8007/v1/chat/completions" \
  -H "Content-Type: application/json" \
  --data '{
    "model": "kimi-dev",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 50
  }'
```

## SWE-bench Setup

For software engineering tasks and SWE-bench evaluation:

### 1. Automated Setup

```bash
# Run the automated SWE-bench setup
./scripts/swe_bench/setup_swe_environment.sh
```

This script will:
- Create a conda environment with Python 3.12
- Clone the Kimi-Dev repository
- Download SWE-bench repository structure (~10GB)
- Install all dependencies
- Configure environment variables

### 2. Manual Setup (Alternative)

```bash
# Create conda environment
conda create -n kimidev python=3.12
conda activate kimidev

# Install vLLM with CUDA support
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu128

# Clone Kimi-Dev repository
git clone https://github.com/MoonshotAI/Kimi-Dev.git integrations/kimi-dev
cd integrations/kimi-dev
pip install -e .

# Download SWE-bench data (manual)
# Download from: https://drive.google.com/file/d/15-4XjTmY48ystrsc_xcvtOkMs3Fx8RoW/view
# Extract to: data/swe_repos/
```

### 3. Enable SWE-bench Mode

```bash
# Set environment variables
export ENABLE_SWE_BENCH=true
export PROJECT_FILE_LOC=/home/ubuntu/ACGS/data/swe_repos

# Deploy SWE-bench optimized service
docker-compose -f infrastructure/docker/docker-compose.kimi-swe.yml up -d
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Model Configuration
KIMI_MODEL_NAME=moonshotai/Kimi-Dev-72B
KIMI_MAX_MODEL_LEN=32768
KIMI_MAX_NUM_SEQS=256
KIMI_GPU_MEMORY_UTILIZATION=0.9

# Service Configuration
KIMI_SERVICE_URL=http://localhost:8007
ENVIRONMENT=development
LOG_LEVEL=INFO

# ACGS Integration
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.95
GOVERNANCE_WORKFLOW_VALIDATION=true

# Authentication
HUGGINGFACE_API_KEY=your_hf_token_here
```

### Service Configuration

Edit `config/kimi/service-config.yaml` for advanced configuration:

- Model parameters
- API settings
- ACGS integration
- Monitoring options
- Security settings

## Deployment Options

### Option 1: Standalone Deployment

Deploy only the Kimi service:

```bash
docker-compose -f infrastructure/docker/docker-compose.kimi.yml up -d
```

### Option 2: ACGS-Integrated Deployment

Deploy with full ACGS integration:

```bash
# Start ACGS core services first
docker-compose -f docker-compose.production.yml up -d

# Then deploy Kimi service
./scripts/deploy_kimi_service.sh
```

### Option 3: Development Deployment

For development with hot-reloading:

```bash
# Set development environment
export ENVIRONMENT=development
export DEBUG=true

# Deploy with development settings
./scripts/deploy_kimi_service.sh
```

## Monitoring

### Prometheus Metrics

The service exposes metrics at `http://localhost:9007/metrics`:

- Request latency and throughput
- GPU utilization and memory
- Model performance metrics
- Constitutional compliance scores

### Grafana Dashboard

Import the Kimi dashboard:

1. Open Grafana at `http://localhost:3000`
2. Import dashboard from `config/monitoring/kimi-dashboard.json`
3. Configure data source to point to Prometheus

### Health Checks

Monitor service health:

```bash
# Basic health check
curl http://localhost:8007/health

# Detailed health information
curl http://localhost:8007/health/detailed

# Continuous monitoring
./scripts/manage_kimi_service.sh monitor
```

## Testing

### Automated Testing

Run the comprehensive test suite:

```bash
# Full test suite
python3 scripts/test_kimi_integration.py

# Save results to file
python3 scripts/test_kimi_integration.py --output test-results.json

# Test specific URL
python3 scripts/test_kimi_integration.py --url http://your-server:8007
```

### Manual Testing

Test different scenarios:

```bash
# Simple completion
./scripts/manage_kimi_service.sh test

# Performance testing
curl -X POST "http://localhost:8007/v1/chat/completions" \
  -H "Content-Type: application/json" \
  --data '{
    "model": "kimi-dev-72b",
    "messages": [{"role": "user", "content": "Write a detailed explanation of quantum computing"}],
    "max_tokens": 500,
    "temperature": 0.7
  }'

# Streaming test
curl -X POST "http://localhost:8007/v1/chat/completions" \
  -H "Content-Type: application/json" \
  --data '{
    "model": "kimi-dev-72b",
    "messages": [{"role": "user", "content": "Count from 1 to 10"}],
    "max_tokens": 100,
    "stream": true
  }'
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Symptoms**: Container exits immediately or fails to start

**Solutions**:
```bash
# Check logs
./scripts/manage_kimi_service.sh logs

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Check disk space
df -h ~/.cache/huggingface

# Verify environment variables
docker-compose -f infrastructure/docker/docker-compose.kimi.yml config
```

#### 2. Model Loading Fails

**Symptoms**: Service starts but model doesn't load

**Solutions**:
```bash
# Check HuggingFace token
echo $HUGGINGFACE_API_KEY

# Verify model access
huggingface-cli login --token $HUGGINGFACE_API_KEY
huggingface-cli download moonshotai/Kimi-Dev-72B --cache-dir ~/.cache/huggingface

# Check available GPU memory
nvidia-smi
```

#### 3. High Memory Usage

**Symptoms**: Out of memory errors or slow performance

**Solutions**:
```bash
# Reduce GPU memory utilization
export KIMI_GPU_MEMORY_UTILIZATION=0.8

# Reduce max sequence length
export KIMI_MAX_MODEL_LEN=16384

# Enable CPU offloading
export KIMI_CPU_OFFLOAD_GB=8

# Restart service
./scripts/manage_kimi_service.sh restart
```

#### 4. API Timeouts

**Symptoms**: Requests timeout or take too long

**Solutions**:
```bash
# Check service load
./scripts/manage_kimi_service.sh status

# Reduce concurrent requests
export KIMI_MAX_NUM_SEQS=128

# Check GPU utilization
nvidia-smi -l 1

# Scale horizontally if needed
docker-compose -f infrastructure/docker/docker-compose.kimi.yml up -d --scale kimi_service=2
```

### Log Analysis

Check different log sources:

```bash
# Service logs
./scripts/manage_kimi_service.sh logs --follow

# Container logs
docker logs acgs_kimi_service --follow

# System logs
journalctl -u docker --follow

# GPU logs
nvidia-smi dmon -s pucvmet -d 1
```

### Performance Tuning

Optimize performance:

```bash
# GPU memory optimization
export KIMI_GPU_MEMORY_UTILIZATION=0.95

# Batch size optimization
export KIMI_MAX_NUM_SEQS=512

# Enable tensor parallelism (multi-GPU)
export TENSOR_PARALLEL_SIZE=2

# Enable pipeline parallelism
export PIPELINE_PARALLEL_SIZE=2
```

## Integration with ACGS

### Constitutional Compliance

The Kimi service integrates with ACGS constitutional compliance:

- All requests are validated against constitutional principles
- Responses are checked for compliance violations
- Compliance scores are tracked and monitored
- Violations trigger alerts and can block responses

### Governance Workflow

Integration with ACGS governance:

- Policy synthesis requests are routed through governance workflows
- Formal verification is applied to critical responses
- Evolutionary computation optimizes response quality
- Audit trails are maintained for all interactions

### Authentication

ACGS authentication integration:

- JWT tokens from ACGS auth service are validated
- Role-based access control is enforced
- API usage is tracked per user
- Rate limiting is applied based on user roles

### Monitoring Integration

Seamless monitoring integration:

- Metrics are collected by ACGS Prometheus
- Alerts are routed through ACGS Alertmanager
- Dashboards are integrated with ACGS Grafana
- Logs are aggregated with ACGS logging stack

## Next Steps

After successful deployment:

1. **Configure monitoring dashboards**
2. **Set up automated backups**
3. **Implement load balancing** (for production)
4. **Configure SSL/TLS** (for production)
5. **Set up log aggregation**
6. **Implement disaster recovery**

For advanced configuration and production deployment, see:
- [ACGS Production Deployment Guide](ACGS_PRODUCTION_DEPLOYMENT.md)
- [Monitoring and Alerting Guide](MONITORING_GUIDE.md)
- [Security Configuration Guide](SECURITY_GUIDE.md)
