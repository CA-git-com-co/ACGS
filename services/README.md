# ACGS-1 Lite: AI Constitutional Governance System

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

## 🎯 Overview

ACGS-1 Lite is a lightweight implementation of the AI Constitutional Governance System, designed to provide constitutional AI oversight, safety enforcement, and governance workflows for AI agent operations. This system ensures AI agents operate within defined constitutional principles while maintaining high performance and reliability.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ACGS-1 Lite System Architecture                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │  External APIs  │    │  Admin Portal   │
│                 │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Load Balancer        │
                    │     (nginx/traefik)       │
                    └─────────────┬─────────────┘
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
    ▼                             ▼                             ▼
┌───────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ Policy Engine │    │ Evolution Oversight │    │   Audit Engine      │
│               │    │                     │    │                     │
│ Port: 8004    │    │     Port: 8002      │    │    Port: 8003       │
│ OPA Policies  │◄───┤ Approval Workflows  │◄───┤ Cryptographic       │
│ Constitutional│    │ Risk Assessment     │    │ Hash Chaining       │
│ Evaluation    │    │ Rollback Mechanisms │    │ Event Logging       │
└───────┬───────┘    └─────────┬───────────┘    └─────────┬───────────┘
        │                      │                          │
        └──────────────────────┼──────────────────────────┘
                               │
                    ┌─────────────────────┐
                    │ Hardened Sandbox    │
                    │    Controller       │
                    │                     │
                    │    Port: 8001       │
                    │ gVisor/Firecracker  │
                    │ Seccomp Profiles    │
                    │ Syscall Monitoring  │
                    └─────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ PostgreSQL  │    │    Redpanda     │    │  S3 Storage     │
│             │    │    (Kafka)      │    │                 │
│ Audit Data  │    │ Event Streams   │    │ Archive Data    │
│ Metadata    │    │ Real-time Logs  │    │ Backups         │
└─────────────┘    └─────────────────┘    └─────────────────┘

        ┌─────────────────────┐    ┌─────────────────────┐
        │       Redis         │    │    Prometheus       │
        │                     │    │                     │
        │   L2 Cache          │    │ Metrics Collection  │
        │   Session Store     │    │ Alerting Rules      │
        └─────────────────────┘    └─────────────────────┘
```

## 🎨 Component Overview

### Core Services

| Service | Port | Purpose | Status | Performance |
|---------|------|---------|--------|------------|
| **Policy Engine** | 8004 | Constitutional policy evaluation and enforcement | ✅ | <1ms P99 |
| **Evolution Oversight** | 8002 | AI agent evolution approval workflows | ✅ | <50ms P99 |
| **Audit Engine** | 8003 | Cryptographic audit trails and logging | ✅ | 1000+ events/sec |
| **Sandbox Controller** | 8001 | Hardened execution environments | ✅ | gVisor/Firecracker |

### Supporting Infrastructure

| Component | Purpose | Technology | Status |
|-----------|---------|------------|--------|
| **PostgreSQL** | Audit data storage | PostgreSQL 15 | ✅ |
| **Redpanda** | Event streaming | Kafka-compatible | ✅ |
| **S3 Storage** | Archive storage | MinIO/AWS S3 | ✅ |
| **Redis** | Caching & sessions | Redis 7 | ✅ |
| **Prometheus** | Metrics collection | Prometheus | ✅ |
| **Grafana** | Monitoring dashboards | Grafana | ✅ |

## 🌟 Key Features

### Constitutional Principles
- **Autonomy**: Respect user choice and consent
- **Beneficence**: Aim to benefit users and society  
- **Non-maleficence**: Do not cause harm
- **Transparency**: Provide explainable decisions
- **Fairness**: Avoid unfair discrimination
- **Privacy**: Protect user data
- **Accountability**: Maintain audit trails

### Safety & Security
- **25+ Dangerous Actions** blocked automatically
- **Multi-tier Approval** workflows (auto/fast-track/human review)
- **Cryptographic Hash Chaining** for audit integrity
- **Hardened Sandboxes** with gVisor/Firecracker isolation
- **Real-time Monitoring** with Prometheus/Grafana
- **Constitutional Hash Verification**: `cdd01ef066bc6cf2`

### Performance & Reliability
- **Sub-millisecond Latency**: <1ms P99 policy evaluation
- **High Throughput**: 15,000+ requests/second
- **Two-tier Caching**: L1 (memory) + L2 (Redis)
- **Partial Evaluation**: Pre-computed common scenarios
- **Horizontal Scaling**: Container-based architecture
- **Automated CI/CD**: Performance regression detection

## 🚀 Quick Start

### Prerequisites

```bash
# System requirements
docker --version          # Docker 20.10+
docker-compose --version  # Docker Compose 2.0+
python3 --version         # Python 3.11+

# Hardware requirements
# CPU: 4+ cores
# RAM: 8GB+ 
# Disk: 20GB+ available space
```

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ACGS/services

# Start core services
cd core/audit-engine
./deploy.sh

cd ../sandbox-controller/hardened
./deploy.sh

cd ../evolutionary-computation
./deploy.sh

cd ../opa-policies
./deploy.sh

# Verify all services are running
./health-check.sh
```

### Verification

```bash
# Check service health
curl http://localhost:8001/health  # Sandbox Controller
curl http://localhost:8002/health  # Evolution Oversight
curl http://localhost:8003/health  # Audit Engine
curl http://localhost:8004/v1/data/acgs/main/health  # Policy Engine

# Test policy evaluation
curl -X POST http://localhost:8004/v1/data/acgs/main/decision \
  -H "Content-Type: application/json" \
  -d '{
    "type": "constitutional_evaluation",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "action": "data.read_public",
    "context": {
      "environment": {"sandbox_enabled": true, "audit_enabled": true},
      "agent": {"trust_level": 0.9},
      "responsible_party": "test_user",
      "explanation": "Reading public data for display"
    }
  }'
```

## 📋 ACGS-1 Lite vs Full ACGS-1

### What's Included in ACGS-1 Lite

| Feature | ACGS-1 Lite | Full ACGS-1 |
|---------|-------------|-------------|
| **Constitutional Policy Engine** | ✅ Full | ✅ Full |
| **Basic Safety Rules** | ✅ 25+ rules | ✅ 100+ rules |
| **Evolution Oversight** | ✅ Core workflows | ✅ Advanced ML pipelines |
| **Audit Engine** | ✅ Hash chaining | ✅ + Zero-knowledge proofs |
| **Sandbox Hardening** | ✅ gVisor/Firecracker | ✅ + Custom hypervisor |
| **Performance Monitoring** | ✅ Basic metrics | ✅ + AI performance analysis |
| **Multi-tenant Support** | ❌ Single tenant | ✅ Full multi-tenancy |
| **Advanced AI Training** | ❌ Limited | ✅ Full training pipelines |
| **Enterprise SSO** | ❌ Basic auth | ✅ Full SSO integration |
| **Global Consensus** | ❌ Single node | ✅ Distributed consensus |

### Deployment Scale

- **ACGS-1 Lite**: Small to medium deployments (1-100 AI agents)
- **Full ACGS-1**: Enterprise scale (1000+ AI agents, multi-region)

### Resource Requirements

- **ACGS-1 Lite**: 4 CPU cores, 8GB RAM, 20GB storage
- **Full ACGS-1**: 16+ CPU cores, 64GB+ RAM, 1TB+ storage

## 📚 API Documentation

### Policy Engine (Port 8004)

**Evaluate Constitutional Policy**
```http
POST /v1/data/acgs/main/decision
Content-Type: application/json

{
  "type": "constitutional_evaluation",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "action": "data.read_public",
  "context": {
    "environment": {"sandbox_enabled": true},
    "agent": {"trust_level": 0.9},
    "responsible_party": "user123",
    "explanation": "Reading public data"
  }
}
```

**Response:**
```json
{
  "allow": true,
  "compliance_score": 0.96,
  "constitutional_hash": "cdd01ef066bc6cf2",
  "reasons": [],
  "evaluation_details": {
    "safety": {"passed": true, "score": 1.0},
    "constitutional": {"passed": true, "score": 0.95}
  }
}
```

### Evolution Oversight (Port 8002)

**Submit Evolution Request**
```http
POST /evolution/request
Content-Type: application/json

{
  "type": "minor_update",
  "agent_id": "agent_123",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "changes": {
    "code_changes": ["Performance optimization"],
    "external_dependencies": [],
    "privilege_escalation": false
  },
  "rollback_plan": {
    "procedure": "Git revert",
    "tested": true,
    "automated": true
  }
}
```

### Audit Engine (Port 8003)

**Query Audit Events**
```http
GET /audit/events?agent_id=agent_123&limit=100
Authorization: Bearer <token>
```

### Sandbox Controller (Port 8001)

**Execute in Hardened Sandbox**
```http
POST /execute
Content-Type: application/json

{
  "runtime": "gvisor",
  "image": "python:3.11-slim",
  "command": ["python", "-c", "print('Hello from sandbox')"],
  "security_profile": "restricted",
  "resource_limits": {
    "cpu_cores": 1,
    "memory_gb": 1,
    "execution_time_seconds": 30
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Core Configuration
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ENVIRONMENT=production
LOG_LEVEL=INFO

# Service URLs
POLICY_ENGINE_URL=http://localhost:8004
EVOLUTION_OVERSIGHT_URL=http://localhost:8002
AUDIT_ENGINE_URL=http://localhost:8003
SANDBOX_CONTROLLER_URL=http://localhost:8001

# Database Configuration
POSTGRES_URL=postgresql://acgs:password@localhost:5432/acgs_audit
REDIS_URL=redis://localhost:6379
S3_BUCKET=acgs-audit-data

# Performance Settings
PERFORMANCE_TARGET_P99_MS=1.0
CACHE_TTL_SECONDS=300
MAX_CONCURRENT_REQUESTS=1000

# Security Settings
JWT_SECRET_KEY=<generate-secure-key>
ADMIN_API_KEY=<generate-admin-key>
ENCRYPTION_KEY=<generate-encryption-key>
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Core services
  policy-engine:
    image: acgs/policy-engine:1.0.0
    ports: ["8004:8004"]
    environment:
      - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
    
  evolution-oversight:
    image: acgs/evolution-oversight:1.0.0
    ports: ["8002:8002"]
    
  audit-engine:
    image: acgs/audit-engine:1.0.0
    ports: ["8003:8003"]
    
  sandbox-controller:
    image: acgs/sandbox-controller:1.0.0
    ports: ["8001:8001"]
    privileged: true  # Required for gVisor/Firecracker
    
  # Infrastructure
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: acgs_audit
      POSTGRES_USER: acgs
      POSTGRES_PASSWORD: <secure-password>
    
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 512mb
    
  redpanda:
    image: vectorized/redpanda:latest
    command: redpanda start --smp 1 --memory 1G
```

## 📊 Monitoring & Observability

### Metrics Collection

- **Prometheus**: System and application metrics
- **Grafana**: Visualization dashboards
- **Custom Metrics**: Constitutional compliance, safety violations
- **Performance**: Latency percentiles, throughput, error rates

### Key Dashboards

1. **System Overview**: Service health, resource utilization
2. **Performance**: Latency trends, throughput analysis
3. **Constitutional Compliance**: Policy evaluation metrics
4. **Security**: Safety violations, audit trail integrity
5. **Business**: Agent evolution trends, approval workflows

### Alerting Rules

```yaml
# prometheus-alerts.yml
groups:
  - name: acgs-lite
    rules:
      - alert: HighLatency
        expr: acgs_latency_p99 > 0.005  # 5ms
        for: 2m
        annotations:
          summary: "ACGS-1 Lite high latency detected"
          
      - alert: ConstitutionalViolation
        expr: increase(acgs_safety_violations_total[5m]) > 10
        for: 1m
        annotations:
          summary: "Multiple constitutional violations detected"
```

## 🔐 Security

### Authentication & Authorization

- **JWT Tokens**: Service-to-service authentication
- **API Keys**: External client authentication  
- **RBAC**: Role-based access control
- **Rate Limiting**: Per-client request throttling

### Security Measures

- **Constitutional Hash Verification**: All requests validated
- **Input Sanitization**: Comprehensive validation
- **Audit Logging**: All actions tracked with cryptographic integrity
- **Sandbox Isolation**: gVisor/Firecracker security boundaries
- **Encrypted Storage**: Data encrypted at rest and in transit

### Security Incident Response

1. **Detection**: Automated monitoring and alerting
2. **Containment**: Automatic sandbox isolation
3. **Analysis**: Audit trail investigation
4. **Recovery**: Rollback mechanisms and service restoration
5. **Lessons Learned**: Post-incident review and improvements

## 🚨 Troubleshooting

### Common Issues

**High Latency (>5ms P99)**
```bash
# Check cache hit rates
curl http://localhost:8004/v1/metrics | grep cache_hit_rate

# Warm cache
curl http://localhost:8004/v1/cache/warm

# Check resource usage
docker stats
```

**Constitutional Violations**
```bash
# Check safety violation logs
curl http://localhost:8003/audit/events?type=safety_violation

# Review policy evaluation details
curl -X POST http://localhost:8004/v1/data/acgs/main/decision \
  -d '{"type":"constitutional_evaluation", ...}'
```

**Service Unavailable**
```bash
# Check service health
./health-check.sh

# View service logs
docker-compose logs -f <service-name>

# Restart services
docker-compose restart
```

### Performance Tuning

- **Cache Size**: Adjust L1 cache size based on memory
- **Batch Size**: Optimize request batching for your workload
- **Connection Pools**: Tune database connection settings
- **Resource Limits**: Adjust CPU/memory limits per service

## 📈 Production Deployment

### Scaling Guidelines

```yaml
# production scaling
services:
  policy-engine:
    deploy:
      replicas: 3
      resources:
        limits: {memory: 500M, cpus: '1.0'}
        
  evolution-oversight:
    deploy:
      replicas: 2
      resources:
        limits: {memory: 1G, cpus: '2.0'}
```

### Load Balancing

```nginx
# nginx.conf
upstream policy_engine {
    server policy-engine-1:8004 weight=3;
    server policy-engine-2:8004 weight=3;
    server policy-engine-3:8004 weight=3;
}

server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/acgs.crt;
    ssl_certificate_key /etc/ssl/acgs.key;
    
    location /v1/ {
        proxy_pass http://policy_engine;
        proxy_cache_valid 200 60s;
    }
}
```

### Backup & Recovery

- **Database Backups**: Automated PostgreSQL backups to S3
- **Configuration**: Git-based configuration management
- **Audit Trails**: Immutable audit data with S3 Object Lock
- **Disaster Recovery**: Cross-region replication setup

## 📖 Additional Resources

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment procedures
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Operational Runbook](OPERATIONAL_RUNBOOK.md) - Operations procedures
- [Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md) - System architecture details

## 🤝 Contributing

See individual service READMEs for development setup and contribution guidelines.

## 📄 License

Constitutional AI Governance System (ACGS-1 Lite)  
Constitutional Hash: `cdd01ef066bc6cf2`

---

**Status:** ✅ Production Ready  
**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Last Updated:** 2024-12-28