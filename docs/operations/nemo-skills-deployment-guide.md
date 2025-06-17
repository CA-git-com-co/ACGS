# NeMo-Skills Mathematical Reasoning Service Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the NeMo-Skills Mathematical Reasoning Service (MRS) as part of the ACGS-PGP v8 Semantic Fault Tolerance system.

## Prerequisites

### System Requirements

**Hardware:**
- GPU: NVIDIA A100/H100 (minimum 40GB VRAM) or 4x RTX 4090
- CPU: 32+ cores, 128GB+ RAM
- Storage: 1TB+ NVMe SSD
- Network: 10Gbps+ bandwidth

**Software:**
- Ubuntu 22.04 LTS or RHEL 8+
- Docker 24.0+ with NVIDIA Container Runtime
- CUDA 12.1+ drivers
- Python 3.11+
- PostgreSQL 15+
- Redis 7.0+

### Dependencies

```bash
# Install system dependencies
sudo apt update && sudo apt install -y \
    build-essential \
    git \
    curl \
    wget \
    python3.11 \
    python3.11-pip \
    python3.11-dev \
    postgresql-client \
    redis-tools

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## Installation

### 1. Clone and Setup Repository

```bash
# Navigate to ACGS-1 project root
cd /home/dislove/ACGS-1

# Verify NeMo-Skills is available
ls -la tools/NeMo-Skills/

# Install NeMo-Skills dependencies
cd tools/NeMo-Skills
pip install -e .

# Install additional mathematical reasoning dependencies
pip install -r requirements-mathematical.txt
```

### 2. Configure Mathematical Reasoning Service

```bash
# Create service configuration
mkdir -p services/core/mathematical-reasoning/mrs_service/config
cat > services/core/mathematical-reasoning/mrs_service/config/service_config.yaml << EOF
service:
  name: "mathematical_reasoning_service"
  host: "0.0.0.0"
  port: 8007
  workers: 4
  log_level: "INFO"
  timeout_seconds: 60

nemo_skills:
  tir_config:
    max_code_executions: 8
    timeout_ms: 30000
    sandbox_type: "local"
    enable_caching: true
  
  server_backends:
    primary: "vllm"
    fallback: ["trtllm", "sglang"]
    model_name: "meta/llama-3.3-70b-instruct"
  
  evaluation:
    benchmarks: ["gsm8k", "math", "aime24"]
    accuracy_threshold: 0.85
    performance_target_ms: 2000

database:
  url: "postgresql+asyncpg://acgs_user:acgs_password@localhost:5433/acgs_pgp_db"
  pool_size: 20
  max_overflow: 30

redis:
  url: "redis://localhost:6379/2"
  max_connections: 100
  socket_timeout: 30

security:
  enable_auth: true
  jwt_secret_key: "${JWT_SECRET_KEY}"
  cors_origins: ["http://localhost:3000", "http://localhost:3001"]

monitoring:
  prometheus_enabled: true
  metrics_port: 9007
  health_check_interval: 30
EOF
```

### 3. Database Schema Setup

```bash
# Create mathematical reasoning database tables
psql -h localhost -p 5433 -U acgs_user -d acgs_pgp_db << EOF
-- Mathematical reasoning results storage
CREATE TABLE IF NOT EXISTS mathematical_reasoning_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL,
    problem_type VARCHAR(100) NOT NULL,
    problem_content TEXT NOT NULL,
    solution_content TEXT NOT NULL,
    mathematical_validity BOOLEAN NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    execution_time_ms INTEGER NOT NULL,
    constitutional_compliance JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Mathematical policy rules
CREATE TABLE IF NOT EXISTS mathematical_policy_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID NOT NULL,
    rule_type VARCHAR(100) NOT NULL,
    mathematical_expression TEXT NOT NULL,
    constraints JSONB NOT NULL,
    optimization_objectives JSONB NOT NULL,
    validation_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quantitative compliance metrics
CREATE TABLE IF NOT EXISTS quantitative_compliance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    governance_action_id UUID NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    mathematical_model VARCHAR(200) NOT NULL,
    confidence_interval JSONB NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_math_results_problem_type ON mathematical_reasoning_results(problem_type);
CREATE INDEX IF NOT EXISTS idx_math_results_created_at ON mathematical_reasoning_results(created_at);
CREATE INDEX IF NOT EXISTS idx_policy_rules_policy_id ON mathematical_policy_rules(policy_id);
CREATE INDEX IF NOT EXISTS idx_compliance_metrics_action_id ON quantitative_compliance_metrics(governance_action_id);
EOF
```

## Deployment Options

### Option 1: Host-Based Deployment (Recommended)

```bash
# Create startup script
cat > start_mrs_service_host.py << 'EOF'
#!/usr/bin/env python3
"""
Mathematical Reasoning Service Host-Based Startup Script
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

def setup_environment():
    """Set up environment variables for MRS service."""
    print("🔧 Setting up environment variables...")
    
    # Core service URLs
    os.environ["AUTH_SERVICE_URL"] = "http://localhost:8000"
    os.environ["AC_SERVICE_URL"] = "http://localhost:8001"
    os.environ["INTEGRITY_SERVICE_URL"] = "http://localhost:8002"
    os.environ["FV_SERVICE_URL"] = "http://localhost:8003"
    os.environ["GS_SERVICE_URL"] = "http://localhost:8004"
    os.environ["PGC_SERVICE_URL"] = "http://localhost:8005"
    os.environ["EC_SERVICE_URL"] = "http://localhost:8006"
    
    # Database and Redis
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://acgs_user:acgs_password@localhost:5433/acgs_pgp_db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/2"
    
    # Security
    os.environ["JWT_SECRET_KEY"] = "acgs-mathematical-reasoning-secret-key-2024"
    os.environ["ENVIRONMENT"] = "development"
    
    # NeMo-Skills configuration
    os.environ["NEMO_SKILLS_PATH"] = "/home/dislove/ACGS-1/tools/NeMo-Skills"
    os.environ["PYTHONPATH"] = "/home/dislove/ACGS-1/services/shared:/home/dislove/ACGS-1/services/core/mathematical-reasoning/mrs_service"
    
    print("✅ Environment variables configured")

def start_mrs_service():
    """Start the Mathematical Reasoning Service."""
    print("🚀 Starting Mathematical Reasoning Service...")
    
    mrs_service_dir = Path("/home/dislove/ACGS-1/services/core/mathematical-reasoning/mrs_service")
    
    if not mrs_service_dir.exists():
        print(f"❌ MRS Service directory not found: {mrs_service_dir}")
        return None
    
    cmd = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007", "--reload"]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=mrs_service_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=os.environ.copy(),
        )
        
        print(f"✅ MRS Service started with PID: {process.pid}")
        
        # Save PID for management
        pid_file = Path("/home/dislove/ACGS-1/pids/mrs_service.pid")
        pid_file.parent.mkdir(exist_ok=True)
        pid_file.write_text(str(process.pid))
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start MRS service: {e}")
        return None

def main():
    """Main execution function."""
    print("🚀 Mathematical Reasoning Service Host-Based Startup")
    print("=" * 55)
    
    setup_environment()
    process = start_mrs_service()
    
    if process:
        print("\n✅ Mathematical Reasoning Service is running!")
        print(f"🔧 Service URL: http://localhost:8007")
        print(f"📊 Health Check: http://localhost:8007/health")
        print(f"📖 API Docs: http://localhost:8007/docs")
        return 0
    else:
        print("\n❌ Failed to start Mathematical Reasoning Service")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x start_mrs_service_host.py

# Start the service
python3 start_mrs_service_host.py
```

### Option 2: Docker Deployment

```bash
# Build Docker image
cd services/core/mathematical-reasoning/mrs_service
docker build -t acgs-mathematical-reasoning:latest .

# Run container
docker run -d \
    --name acgs-mrs \
    --gpus all \
    -p 8007:8007 \
    -p 9007:9007 \
    -e DATABASE_URL="postgresql+asyncpg://acgs_user:acgs_password@host.docker.internal:5433/acgs_pgp_db" \
    -e REDIS_URL="redis://host.docker.internal:6379/2" \
    -e JWT_SECRET_KEY="acgs-mathematical-reasoning-secret-key-2024" \
    -v /home/dislove/ACGS-1/tools/NeMo-Skills:/app/nemo-skills:ro \
    --restart unless-stopped \
    acgs-mathematical-reasoning:latest
```

## Configuration Management

### Environment Variables

```bash
# Core service configuration
export MRS_SERVICE_PORT=8007
export MRS_SERVICE_HOST="0.0.0.0"
export MRS_SERVICE_WORKERS=4

# NeMo-Skills configuration
export NEMO_SKILLS_MAX_CODE_EXECUTIONS=8
export NEMO_SKILLS_TIMEOUT_MS=30000
export NEMO_SKILLS_SANDBOX_TYPE="local"
export NEMO_SKILLS_ENABLE_CACHING=true

# Model configuration
export NEMO_SKILLS_PRIMARY_BACKEND="vllm"
export NEMO_SKILLS_MODEL_NAME="meta/llama-3.3-70b-instruct"
export NEMO_SKILLS_FALLBACK_BACKENDS="trtllm,sglang"

# Performance tuning
export NEMO_SKILLS_CONCURRENT_REQUESTS=1024
export NEMO_SKILLS_BATCH_SIZE=16
export NEMO_SKILLS_GPU_MEMORY_FRACTION=0.9
```

### Model Backend Configuration

```yaml
# vLLM backend configuration
vllm_config:
  model: "meta/llama-3.3-70b-instruct"
  tensor_parallel_size: 4
  max_model_len: 32768
  gpu_memory_utilization: 0.9
  enable_chunked_prefill: true
  max_num_batched_tokens: 8192

# TensorRT-LLM backend configuration
trtllm_config:
  model: "meta/llama-3.3-70b-instruct"
  max_batch_size: 16
  max_input_len: 16384
  max_output_len: 2048
  precision: "fp16"
  enable_kv_cache: true

# sglang backend configuration
sglang_config:
  model: "meta/llama-3.3-70b-instruct"
  mem_fraction_static: 0.85
  max_concurrent_requests: 1024
  enable_flashinfer: true
  chunked_prefill_size: 8192
```

## Monitoring and Observability

### Prometheus Metrics

```yaml
# Add to prometheus.yml
- job_name: 'acgs-mathematical-reasoning'
  static_configs:
    - targets: ['localhost:9007']
  metrics_path: '/metrics'
  scrape_interval: 15s
  scrape_timeout: 10s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "ACGS Mathematical Reasoning Service",
    "panels": [
      {
        "title": "Mathematical Problem Solving Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(acgs_mathematical_problems_solved_total[5m])",
            "legendFormat": "Problems/sec"
          }
        ]
      },
      {
        "title": "Response Time Distribution",
        "type": "histogram",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(acgs_mathematical_response_time_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Constitutional Compliance Rate",
        "type": "gauge",
        "targets": [
          {
            "expr": "acgs_constitutional_math_compliance",
            "legendFormat": "Compliance Rate"
          }
        ]
      }
    ]
  }
}
```

## Health Checks and Validation

### Service Health Validation

```bash
#!/bin/bash
# Health check script

echo "🔍 Mathematical Reasoning Service Health Check"
echo "============================================="

# Check service availability
if curl -f http://localhost:8007/health >/dev/null 2>&1; then
    echo "✅ Service is responding"
else
    echo "❌ Service is not responding"
    exit 1
fi

# Check mathematical capabilities
if curl -f http://localhost:8007/math/capabilities >/dev/null 2>&1; then
    echo "✅ Mathematical capabilities available"
else
    echo "❌ Mathematical capabilities not available"
    exit 1
fi

# Test mathematical problem solving
TEST_PROBLEM='{"content": "What is 2 + 2?", "problem_type": "arithmetic"}'
if curl -X POST -H "Content-Type: application/json" -d "$TEST_PROBLEM" http://localhost:8007/math/solve >/dev/null 2>&1; then
    echo "✅ Mathematical problem solving functional"
else
    echo "❌ Mathematical problem solving not functional"
    exit 1
fi

echo "✅ All health checks passed"
```

### Performance Validation

```bash
#!/bin/bash
# Performance validation script

echo "📊 Mathematical Reasoning Performance Validation"
echo "==============================================="

# Benchmark mathematical reasoning
python3 << EOF
import asyncio
import aiohttp
import time
import json

async def benchmark_mathematical_reasoning():
    problems = [
        {"content": "Solve: 3x + 5 = 14", "problem_type": "algebra"},
        {"content": "Find the derivative of x^2 + 3x + 2", "problem_type": "calculus"},
        {"content": "Calculate the mean of [1, 2, 3, 4, 5]", "problem_type": "statistics"}
    ]
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        tasks = []
        for problem in problems:
            task = session.post(
                "http://localhost:8007/math/solve",
                json=problem,
                headers={"Authorization": "Bearer test-token"}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        
        print(f"Total time: {(end_time - start_time) * 1000:.1f}ms")
        print(f"Successful responses: {len(successful_responses)}/{len(problems)}")
        print(f"Average response time: {((end_time - start_time) / len(problems)) * 1000:.1f}ms")

asyncio.run(benchmark_mathematical_reasoning())
EOF
```

## Troubleshooting

### Common Issues

**Issue: Service fails to start**
```bash
# Check logs
tail -f /home/dislove/ACGS-1/logs/mrs_service.log

# Check dependencies
pip list | grep -E "(nemo-skills|torch|transformers)"

# Verify GPU availability
nvidia-smi
```

**Issue: Mathematical reasoning timeout**
```bash
# Increase timeout in configuration
export NEMO_SKILLS_TIMEOUT_MS=60000

# Check GPU memory usage
nvidia-smi

# Monitor system resources
htop
```

**Issue: Constitutional compliance validation fails**
```bash
# Check AC service connectivity
curl http://localhost:8001/health

# Verify constitutional requirements
curl http://localhost:8007/math/capabilities
```

### Log Analysis

```bash
# View service logs
tail -f /home/dislove/ACGS-1/logs/mrs_service.log

# Filter for errors
grep -i error /home/dislove/ACGS-1/logs/mrs_service.log

# Monitor performance metrics
grep -i "response_time" /home/dislove/ACGS-1/logs/mrs_service.log
```

## Security Hardening

### Sandbox Security

```bash
# Configure secure sandbox environment
cat > /etc/security/limits.d/nemo-skills.conf << EOF
nemo-skills soft nproc 1024
nemo-skills hard nproc 2048
nemo-skills soft nofile 65536
nemo-skills hard nofile 65536
nemo-skills soft memlock unlimited
nemo-skills hard memlock unlimited
EOF

# Set up restricted execution environment
sudo useradd -r -s /bin/false nemo-skills
sudo mkdir -p /var/lib/nemo-skills/sandbox
sudo chown nemo-skills:nemo-skills /var/lib/nemo-skills/sandbox
sudo chmod 750 /var/lib/nemo-skills/sandbox
```

### Network Security

```bash
# Configure firewall rules
sudo ufw allow 8007/tcp comment "Mathematical Reasoning Service"
sudo ufw allow 9007/tcp comment "MRS Metrics"

# Restrict access to internal services only
sudo ufw deny from any to any port 8007 comment "Block external MRS access"
sudo ufw allow from 10.0.0.0/8 to any port 8007 comment "Allow internal MRS access"
```

This deployment guide provides comprehensive instructions for setting up and operating the NeMo-Skills Mathematical Reasoning Service as part of the ACGS-PGP v8 system.
