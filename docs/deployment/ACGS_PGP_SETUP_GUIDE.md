# ACGS-PGP System Setup Guide

**Version**: 1.0.0  
**Date**: 2025-06-27  
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This guide provides comprehensive instructions for setting up the ACGS-PGP (Autonomous Constitutional Governance System - Policy Governance Platform) with 7-service architecture, constitutional governance, and real AI model integrations.

## Architecture Overview

### 7-Service Architecture

| Service           | Port | Description                                 | Constitutional Role            |
| ----------------- | ---- | ------------------------------------------- | ------------------------------ |
| auth_service      | 8000 | Authentication & Authorization              | Identity governance            |
| ac_service        | 8001 | Constitutional AI                           | Core constitutional compliance |
| integrity_service | 8002 | Data Integrity & Cryptographic Verification | Data governance                |
| fv_service        | 8003 | Formal Verification                         | Policy verification            |
| gs_service        | 8004 | Governance Synthesis                        | Policy synthesis               |
| pgc_service       | 8005 | Policy Governance Compliance                | Compliance monitoring          |
| ec_service        | 8006 | Evolutionary Computation                    | System evolution               |

### Constitutional Governance Features

- <!-- Constitutional Hash: cdd01ef066bc6cf2 -->
- **Compliance Threshold**: >95%
- **DGM Safety Patterns**: Sandbox + Human Review + Rollback
- **Emergency Shutdown**: <30min RTO
- **Performance Targets**: ≤2s response time, 1000 RPS

### Real AI Model Integrations

- **Google Gemini**: gemini-1.5-pro for constitutional reasoning
- **DeepSeek R1**: deepseek-r1 for advanced reasoning
- **NVIDIA Qwen**: qwen2.5-72b-instruct for policy analysis
- **Nano-vLLM**: Local deployment for privacy-sensitive operations

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ or compatible Linux distribution
- **Memory**: 16GB RAM minimum, 32GB recommended
- **Storage**: 100GB available space
- **CPU**: 8 cores minimum, 16 cores recommended
- **Network**: Stable internet connection for AI model APIs

### Required Software

- **Git**: Version control
- **Python**: 3.9+ with pip
- **Node.js**: 18+ with npm
- **Rust**: Latest stable with cargo
- **Docker**: 20.10+ with docker-compose
- **PostgreSQL**: 15+ (or use Docker)
- **Redis**: 7+ (or use Docker)

### Package Managers

- **Python**: UV (preferred) or pip
- **Node.js**: pnpm (preferred) or yarn
- **Rust**: cargo (standard)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS
```

### 2. Run Automated Setup

```bash
# Complete project setup
./scripts/setup/project_setup.sh

# Install dependencies with proper package managers
./scripts/setup/install_dependencies.sh
```

### 3. Configure Environment

```bash
# Copy environment template
cp config/env/.env.example config/env/.env

# Edit configuration (add API keys)
nano config/env/.env
```

### 4. Start Services

```bash
# Start all 7 services with constitutional governance
./scripts/start_all_services.sh
```

### 5. Validate Deployment

```bash
# Run comprehensive test suite
./scripts/run_all_setup_tests.sh
```

## Detailed Setup Instructions

### Step 1: Environment Configuration

#### Required Environment Variables

```bash
# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.95
OPA_SERVER_URL=http://localhost:8181

# Real AI Model API Keys
GOOGLE_GEMINI_API_KEY=your_gemini_api_key
DEEPSEEK_R1_API_KEY=your_deepseek_api_key
NVIDIA_QWEN_API_KEY=your_nvidia_api_key

# DGM Safety Patterns
DGM_SANDBOX_ENABLED=true
DGM_HUMAN_REVIEW_ENABLED=true
DGM_ROLLBACK_ENABLED=true
EMERGENCY_SHUTDOWN_RTO_MINUTES=30

# Database Configuration
DATABASE_URL=postgresql+asyncpg://acgs_user:secure_password@localhost:5432/acgs_db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=generate_secure_secret_key
JWT_SECRET_KEY=generate_secure_jwt_key
```

#### AI Model Configuration

Create `config/ai-models/model-config.yaml`:

```yaml
ai_models:
  google_gemini:
    enabled: true
    model_name: 'gemini-1.5-pro'
    constitutional_compliance: true

  deepseek_r1:
    enabled: true
    model_name: 'deepseek-r1'
    reasoning_mode: true

  nvidia_qwen:
    enabled: true
    model_name: 'qwen2.5-72b-instruct'
    gpu_acceleration: true

  nano_vllm:
    enabled: true
    local_deployment: true
    endpoint: 'http://localhost:8080/v1'

constitutional_governance:
  hash: 'cdd01ef066bc6cf2'
  compliance_threshold: 0.95
  dgm_safety_patterns:
    sandbox_enabled: true
    human_review_required: true
    rollback_capability: true
```

### Step 2: Service Configuration

#### Docker Compose Deployment

```bash
# Start infrastructure services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d postgres redis opa

# Start ACGS services
docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d
```

#### Host-Based Deployment

```bash
# Start individual services
./scripts/start_all_services.sh

# Or start services individually
cd services/platform/authentication/auth_service && uvicorn app.main:app --host 0.0.0.0 --port 8000
cd services/core/constitutional-ai/ac_service && uvicorn app.main:app --host 0.0.0.0 --port 8001
# ... continue for all services
```

### Step 3: Validation and Testing

#### Health Checks

```bash
# Check all services
for port in {8000..8006}; do
  curl -s http://localhost:$port/health
done

# Check constitutional compliance
for port in {8000..8006}; do
  curl -s http://localhost:$port/constitutional/compliance
done
```

#### Performance Validation

```bash
# Run performance tests
./scripts/test_performance_validation.sh

# Expected results:
# - Response time: ≤2000ms
# - Throughput: ≥1000 RPS
# - Constitutional compliance: ≥95%
```

#### Emergency Shutdown Testing

```bash
# Test emergency shutdown capability
./scripts/test_emergency_shutdown.sh

# Expected results:
# - Shutdown time: <30 minutes
# - All services respond to emergency endpoints
# - Constitutional compliance maintained during shutdown
```

## Troubleshooting

### Common Issues

#### 1. Service Startup Failures

**Symptoms**: Services fail to start or health checks fail

**Solutions**:

```bash
# Check logs
tail -f logs/<service_name>.log

# Verify dependencies
docker ps  # Check if postgres/redis are running
curl http://localhost:8181/health  # Check OPA

# Restart services
./scripts/start_all_services.sh
```

#### 2. Constitutional Compliance Issues

**Symptoms**: Compliance score <95%

**Solutions**:

```bash
# Verify constitutional hash
grep -r "cdd01ef066bc6cf2" config/

# Check OPA policies
curl http://localhost:8181/v1/policies

# Validate AI model integrations
curl http://localhost:8001/constitutional/compliance
```

#### 3. Performance Issues

**Symptoms**: Response time >2s or low throughput

**Solutions**:

```bash
# Check resource usage
docker stats
htop

# Verify resource limits
grep -A 5 "resources:" infrastructure/docker/docker-compose.acgs.yml

# Optimize configuration
# Increase memory limits if needed
# Check database connection pooling
```

#### 4. AI Model Integration Issues

**Symptoms**: AI model endpoints returning errors

**Solutions**:

```bash
# Verify API keys
echo $GOOGLE_GEMINI_API_KEY
echo $DEEPSEEK_R1_API_KEY
echo $NVIDIA_QWEN_API_KEY

# Test model endpoints
curl -H "Authorization: Bearer $GOOGLE_GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models

# Check model configuration
cat config/ai-models/model-config.yaml
```

### Emergency Procedures

#### Emergency Shutdown

```bash
# System-wide emergency shutdown
for port in {8000..8006}; do
  curl -X POST http://localhost:$port/emergency/shutdown
done

# Or use individual service shutdown
curl -X POST http://localhost:8001/emergency/shutdown
```

#### Rollback Procedures

```bash
# Stop all services
pkill -f "uvicorn.*:800[0-6]"

# Restore from backup
# (Backup procedures should be implemented)

# Restart with previous configuration
git checkout previous_working_commit
./scripts/start_all_services.sh
```

## Operational Deployment

### Production Deployment Checklist

- [ ] All environment variables configured
- [ ] AI model API keys valid and tested
- [ ] Constitutional hash verified: `cdd01ef066bc6cf2`
- [ ] Resource limits configured (200m/500m CPU, 512Mi/1Gi memory)
- [ ] OPA policies deployed and validated
- [ ] Database migrations applied
- [ ] SSL certificates configured
- [ ] Monitoring and alerting setup
- [ ] Backup procedures implemented
- [ ] Emergency procedures documented and tested
- [ ] Performance targets validated (≤2s, 1000 RPS, >95% compliance)

### Monitoring and Alerting

#### Key Metrics

- **Constitutional Compliance**: >95% threshold
- **Response Time**: ≤2000ms
- **Throughput**: ≥1000 RPS
- **Error Rate**: <1%
- **Service Availability**: >99.9%

#### Alert Conditions

- Constitutional compliance <95%
- Response time >2000ms
- Service unavailable >5 minutes
- Emergency shutdown triggered
- DGM safety pattern violation

### Maintenance Procedures

#### Regular Maintenance

```bash
# Weekly health check
./scripts/run_all_setup_tests.sh

# Monthly dependency updates
./scripts/setup/install_dependencies.sh

# Quarterly security audit
./scripts/security_audit.py
```

#### Emergency Maintenance

```bash
# Emergency shutdown
./scripts/test_emergency_shutdown.sh

# System recovery
./scripts/start_all_services.sh

# Validation
./scripts/test_performance_validation.sh
```

## Next Steps

1. **Configure AI Model API Keys**: Obtain and configure API keys for all AI models
2. **Deploy to Staging**: Test full deployment in staging environment
3. **Performance Tuning**: Optimize for production workloads
4. **Security Hardening**: Implement additional security measures
5. **Monitoring Setup**: Deploy comprehensive monitoring stack
6. **Documentation Review**: Ensure all procedures are documented
7. **Team Training**: Train operations team on procedures
8. **Production Deployment**: Deploy to production with monitoring

## Support

For technical support and questions:

- **Documentation**: This guide and service-specific READMEs
- **Test Suite**: `./scripts/run_all_setup_tests.sh`
- **Health Checks**: Individual service `/health` endpoints
- **Logs**: `logs/` directory for service logs
- **Configuration**: `config/` directory for all configuration files

## Additional Resources

- **[ACGS-PGP Troubleshooting Guide](ACGS_PGP_TROUBLESHOOTING_GUIDE.md)**: Detailed troubleshooting procedures
- **[Service-Specific Documentation](services/)**: Individual service READMEs and API documentation
- **[Test Suite Documentation](scripts/test_setup_scripts_comprehensive.sh)**: Comprehensive testing procedures
- **[AI Model Integration Guide](config/ai-models/)**: AI model configuration and troubleshooting

---

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->
**Last Updated**: 2025-06-27
**Version**: 1.0.0
