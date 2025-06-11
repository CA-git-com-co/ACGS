# ACGS-1 Reorganized Deployment Guide

This guide provides comprehensive instructions for deploying the reorganized ACGS-1 system with blockchain integration across different environments.

## Overview

ACGS-1 supports multiple deployment strategies with the new reorganized structure:
- **Local Development**: Docker Compose for development and testing
- **Staging Environment**: Kubernetes deployment for pre-production testing
- **Production Environment**: High-availability Kubernetes deployment with Solana integration

## Prerequisites

### System Requirements
- **CPU**: 8+ cores (16+ recommended for production)
- **Memory**: 16GB+ RAM (32GB+ recommended for production)
- **Storage**: 100GB+ available disk space (SSD recommended)
- **Network**: Stable internet connection for Solana RPC and external dependencies

### Software Dependencies
- **Solana CLI**: v1.18.22+
- **Anchor Framework**: v0.29.0+
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Kubernetes**: 1.24+ (for staging/production)
- **kubectl**: Kubernetes command-line tool
- **Helm**: 3.8+ (for Kubernetes deployments)
- **Node.js**: v18+ (for blockchain client)

## Directory Structure Overview

```
ACGS-1/
├── blockchain/                          # Solana/Anchor programs
├── services/                           # Backend microservices
│   ├── core/                           # Core governance services
│   ├── platform/                       # Platform services
│   ├── research/                       # Research services
│   └── shared/                         # Shared libraries
├── applications/                       # Frontend applications
├── integrations/                       # Integration layer
├── infrastructure/                     # Infrastructure configs
│   ├── docker/                        # Docker configurations
│   ├── kubernetes/                    # Kubernetes manifests
│   ├── monitoring/                    # Monitoring setup
│   └── deployment/                    # Deployment automation
└── tools/                             # Development tools
```

## Local Development Deployment

### Quick Start
```bash
# Clone the repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-1

# Install dependencies
./scripts/setup/install_dependencies.sh

# Start blockchain layer (local validator)
cd blockchain
solana-test-validator &
anchor build
anchor deploy
cd ..

# Start all services
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Verify deployment
./scripts/validation/validate_deployment.py
```

### Service Health Checks
```bash
# Core Services
curl http://localhost:8001/health  # Constitutional AI
curl http://localhost:8002/health  # Governance Synthesis
curl http://localhost:8003/health  # Policy Governance
curl http://localhost:8004/health  # Formal Verification

# Platform Services
curl http://localhost:8005/health  # Authentication
curl http://localhost:8006/health  # Integrity
curl http://localhost:8007/health  # Workflow

# Research Services
curl http://localhost:8008/health  # Federated Evaluation
curl http://localhost:8009/health  # Research Platform

# Integration Services
curl http://localhost:8010/health  # Data Flywheel
curl http://localhost:8011/health  # Quantumagi Bridge
curl http://localhost:8012/health  # AlphaEvolve Engine
```

### Integration Services
```bash
# Start Data Flywheel integration
cd integrations/data-flywheel
./scripts/setup.sh
python src/demo_app.py

# Start Quantumagi Bridge
cd integrations/quantumagi-bridge
npm install && npm start

# Start AlphaEvolve Engine
cd integrations/alphaevolve-engine
python -m alphaevolve_gs_engine.main
```

### Frontend Applications
```bash
# Start governance dashboard
cd applications/governance-dashboard
npm install && npm start

# Start constitutional council interface
cd applications/constitutional-council
npm install && npm start

# Start public consultation portal
cd applications/public-consultation
npm install && npm start

# Start admin panel
cd applications/admin-panel
npm install && npm start
```

## Staging Environment Deployment

### Kubernetes Setup
```bash
# Create namespace
kubectl create namespace acgs-staging

# Deploy infrastructure components
kubectl apply -f infrastructure/kubernetes/namespace.yml
kubectl apply -f infrastructure/kubernetes/configmaps/
kubectl apply -f infrastructure/kubernetes/secrets/

# Deploy core services
kubectl apply -f infrastructure/kubernetes/core-services/
kubectl apply -f infrastructure/kubernetes/platform-services/
kubectl apply -f infrastructure/kubernetes/research-services/
kubectl apply -f infrastructure/kubernetes/integration-services/

# Deploy applications
kubectl apply -f infrastructure/kubernetes/applications/

# Verify deployment
kubectl get pods -n acgs-staging
```

### Helm Deployment
```bash
# Add ACGS Helm repository
helm repo add acgs https://charts.acgs.ai
helm repo update

# Deploy with Helm
helm install acgs-staging acgs/acgs-1 \
  --namespace acgs-staging \
  --values infrastructure/kubernetes/values-staging.yml

# Verify deployment
helm status acgs-staging -n acgs-staging
```

## Production Environment Deployment

### High Availability Setup
```bash
# Create production namespace
kubectl create namespace acgs-production

# Deploy with production values
helm install acgs-production acgs/acgs-1 \
  --namespace acgs-production \
  --values infrastructure/kubernetes/values-production.yml \
  --set replicaCount=3 \
  --set autoscaling.enabled=true \
  --set monitoring.enabled=true

# Configure ingress
kubectl apply -f infrastructure/kubernetes/ingress-production.yml

# Verify deployment
kubectl get all -n acgs-production
```

### Solana Mainnet Integration
```bash
# Configure Solana mainnet
solana config set --url mainnet-beta

# Deploy programs to mainnet
cd blockchain
anchor deploy --provider.cluster mainnet-beta

# Update bridge configuration
kubectl patch configmap quantumagi-bridge-config \
  -n acgs-production \
  --patch '{"data":{"SOLANA_CLUSTER":"mainnet-beta"}}'

# Restart bridge service
kubectl rollout restart deployment/quantumagi-bridge -n acgs-production
```

## Monitoring and Observability

### Prometheus and Grafana
```bash
# Deploy monitoring stack
kubectl apply -f infrastructure/monitoring/prometheus/
kubectl apply -f infrastructure/monitoring/grafana/
kubectl apply -f infrastructure/monitoring/alertmanager/

# Access dashboards
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# Open http://localhost:3000
```

### Logging with ELK Stack
```bash
# Deploy logging infrastructure
kubectl apply -f infrastructure/monitoring/elasticsearch/
kubectl apply -f infrastructure/monitoring/logstash/
kubectl apply -f infrastructure/monitoring/kibana/

# Access Kibana
kubectl port-forward svc/kibana 5601:5601 -n monitoring
# Open http://localhost:5601
```

### Distributed Tracing
```bash
# Deploy Jaeger
kubectl apply -f infrastructure/monitoring/jaeger/

# Access Jaeger UI
kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring
# Open http://localhost:16686
```

## Security Configuration

### TLS/SSL Setup
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Create cluster issuer
kubectl apply -f infrastructure/kubernetes/cert-manager/cluster-issuer.yml

# Configure TLS ingress
kubectl apply -f infrastructure/kubernetes/ingress-tls.yml
```

### Secret Management
```bash
# Create secrets for services
kubectl create secret generic acgs-secrets \
  --from-env-file=config/environments/production.env \
  -n acgs-production

# Configure service accounts
kubectl apply -f infrastructure/kubernetes/rbac/
```

## Backup and Recovery

### Database Backup
```bash
# Automated backup script
./scripts/backup/backup_database_comprehensive.sh

# Restore from backup
./scripts/backup/restore_database.sh backup_20231207_120000.sql
```

### Blockchain State Backup
```bash
# Backup Solana account states
./scripts/backup/backup_solana_accounts.sh

# Monitor blockchain events
./scripts/monitoring/monitor_blockchain_events.sh
```

## Troubleshooting

### Common Issues

**Service Discovery Issues**:
```bash
# Check service registry
kubectl get endpoints -n acgs-production
kubectl describe service quantumagi-bridge -n acgs-production
```

**Database Connection Issues**:
```bash
# Check database connectivity
kubectl exec -it deployment/constitutional-ai -n acgs-production -- \
  python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"
```

**Blockchain Connection Issues**:
```bash
# Check Solana RPC connectivity
kubectl exec -it deployment/quantumagi-bridge -n acgs-production -- \
  solana cluster-version
```

### Performance Tuning
```bash
# Scale services based on load
kubectl scale deployment constitutional-ai --replicas=5 -n acgs-production

# Configure horizontal pod autoscaling
kubectl apply -f infrastructure/kubernetes/hpa/
```

## Maintenance

### Rolling Updates
```bash
# Update service image
kubectl set image deployment/constitutional-ai \
  constitutional-ai=acgs/constitutional-ai:v2.0.0 \
  -n acgs-production

# Monitor rollout
kubectl rollout status deployment/constitutional-ai -n acgs-production
```

### Health Monitoring
```bash
# Continuous health monitoring
./scripts/monitoring/continuous_health_check.sh

# Performance monitoring
./scripts/monitoring/performance_monitor.sh
```

## Documentation References

- **[Architecture Guide](../architecture/REORGANIZED_ARCHITECTURE.md)**: System architecture
- **[API Documentation](../api/README.md)**: API reference
- **[Security Guide](../security/README.md)**: Security configuration
- **[Monitoring Guide](../monitoring/README.md)**: Monitoring setup

---

**ACGS-1 Deployment**: Bringing constitutional governance to production 🚀🏛️
