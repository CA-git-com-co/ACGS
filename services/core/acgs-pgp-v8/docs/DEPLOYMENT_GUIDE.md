# ACGS-PGP v8 Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying ACGS-PGP v8 in various environments, from local development to production Kubernetes clusters.

## Prerequisites

### System Requirements
- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Memory**: Minimum 2GB RAM, Recommended 4GB+ RAM
- **Storage**: Minimum 10GB available space
- **Network**: Access to ACGS-1 core services and external APIs

### Software Dependencies
- **Docker**: Version 20.10+
- **Python**: Version 3.11+ (for local development)
- **PostgreSQL**: Version 12+
- **Redis**: Version 6+
- **Kubernetes**: Version 1.20+ (for K8s deployment)

### ACGS-1 Dependencies
- Auth Service (port 8000)
- GS Service (port 8004)
- PGC Service (port 8005)
- PostgreSQL database
- Redis cache

## Local Development Deployment

### 1. Environment Setup

```bash
# Navigate to service directory
cd services/core/acgs-pgp-v8

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

Required environment variables:
```bash
DATABASE_URL=postgresql://acgs_user:acgs_password@localhost:5432/acgs_db
REDIS_URL=redis://localhost:6379/0
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
GS_SERVICE_URL=http://localhost:8004
PGC_SERVICE_URL=http://localhost:8005
AUTH_SERVICE_URL=http://localhost:8000
JWT_SECRET_KEY=acgs-pgp-v8-secret-key-2024
PORT=8010
```

### 3. Database Setup

```bash
# Ensure PostgreSQL is running
sudo systemctl start postgresql

# Create database (if not exists)
createdb -U acgs_user acgs_db

# Database tables will be created automatically on first run
```

### 4. Start Services

```bash
# Start Redis
redis-server

# Start ACGS-PGP v8
python main.py
```

### 5. Validation

```bash
# Health check
curl http://localhost:8010/health

# Metrics check
curl http://localhost:8010/metrics

# Run integration tests
python test_monitoring_integration.py
```

## Docker Deployment

### 1. Build Image

```bash
# Build Docker image
docker build -t acgs-pgp-v8:latest .

# Verify image
docker images | grep acgs-pgp-v8
```

### 2. Run Container

```bash
# Run with environment variables
docker run -d \
  --name acgs-pgp-v8 \
  -p 8010:8010 \
  -e DATABASE_URL=postgresql://acgs_user:acgs_password@host.docker.internal:5432/acgs_db \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e CONSTITUTIONAL_HASH=cdd01ef066bc6cf2 \
  -e GS_SERVICE_URL=http://host.docker.internal:8004 \
  -e PGC_SERVICE_URL=http://host.docker.internal:8005 \
  -e AUTH_SERVICE_URL=http://host.docker.internal:8000 \
  --restart unless-stopped \
  acgs-pgp-v8:latest
```

### 3. Using Docker Compose

```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f acgs-pgp-v8

# Stop services
docker-compose down
```

### 4. Automated Deployment

```bash
# Use deployment script
./scripts/deploy.sh

# Check deployment status
./scripts/deploy.sh health

# View logs
./scripts/deploy.sh logs

# Rollback if needed
./scripts/deploy.sh rollback
```

## Kubernetes Deployment

### 1. Prerequisites

```bash
# Ensure kubectl is configured
kubectl cluster-info

# Create namespace
kubectl create namespace acgs-system

# Label namespace for monitoring
kubectl label namespace acgs-system name=acgs-system
```

### 2. Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/deployment.yaml

# Verify deployment
kubectl get pods -n acgs-system -l app=acgs-pgp-v8

# Check service status
kubectl get svc -n acgs-system acgs-pgp-v8-service
```

### 3. Configuration Management

```bash
# Update ConfigMap
kubectl apply -f k8s/deployment.yaml

# Update Secrets (use kubectl create secret or external secret management)
kubectl create secret generic acgs-pgp-v8-secrets \
  --from-literal=database-url="postgresql://user:pass@host:5432/db" \
  --from-literal=redis-url="redis://host:6379/0" \
  --from-literal=jwt-secret-key="your-secret-key" \
  -n acgs-system
```

### 4. Scaling

```bash
# Manual scaling
kubectl scale deployment acgs-pgp-v8 --replicas=5 -n acgs-system

# Check HPA status
kubectl get hpa -n acgs-system

# View HPA details
kubectl describe hpa acgs-pgp-v8-hpa -n acgs-system
```

### 5. Monitoring

```bash
# Check pod logs
kubectl logs -f deployment/acgs-pgp-v8 -n acgs-system

# Port forward for local access
kubectl port-forward svc/acgs-pgp-v8-service 8010:8010 -n acgs-system

# Check metrics
curl http://localhost:8010/metrics
```

## Production Deployment

### 1. Security Hardening

```bash
# Use proper secrets management
# - Kubernetes Secrets
# - HashiCorp Vault
# - AWS Secrets Manager
# - Azure Key Vault

# Network security
# - Enable NetworkPolicies
# - Use TLS for all communications
# - Implement proper RBAC
```

### 2. High Availability

```bash
# Multi-zone deployment
kubectl apply -f k8s/deployment.yaml

# Database clustering
# - PostgreSQL with replication
# - Redis Cluster or Sentinel

# Load balancing
# - Kubernetes Ingress
# - External load balancer
```

### 3. Monitoring Setup

```bash
# Prometheus monitoring
kubectl apply -f monitoring/prometheus-rules.yaml

# Grafana dashboards
kubectl apply -f monitoring/grafana-dashboard.yaml

# Alerting
kubectl apply -f monitoring/alertmanager-rules.yaml
```

### 4. Backup Strategy

```bash
# Database backups
kubectl create cronjob acgs-pgp-v8-backup \
  --image=postgres:13 \
  --schedule="0 2 * * *" \
  -- pg_dump -h postgresql -U acgs_user acgs_db

# Configuration backups
kubectl get configmap acgs-pgp-v8-config -o yaml > backup/config.yaml
kubectl get secret acgs-pgp-v8-secrets -o yaml > backup/secrets.yaml
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
kubectl logs deployment/acgs-pgp-v8 -n acgs-system

# Check events
kubectl get events -n acgs-system --sort-by='.lastTimestamp'

# Check resource constraints
kubectl describe pod -l app=acgs-pgp-v8 -n acgs-system
```

#### 2. Database Connection Issues
```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:13 --restart=Never -- \
  psql postgresql://acgs_user:password@postgresql:5432/acgs_db -c "SELECT 1;"

# Check database service
kubectl get svc postgresql -n acgs-system
```

#### 3. Redis Connection Issues
```bash
# Test Redis connectivity
kubectl run -it --rm debug --image=redis:6 --restart=Never -- \
  redis-cli -h redis ping

# Check Redis service
kubectl get svc redis -n acgs-system
```

#### 4. Constitutional Compliance Failures
```bash
# Check PGC service health
curl http://pgc-service:8005/health

# Validate constitutional hash
kubectl logs deployment/acgs-pgp-v8 -n acgs-system | grep constitutional_hash
```

### Performance Tuning

#### 1. Resource Optimization
```yaml
# Adjust resource requests/limits
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

#### 2. Scaling Configuration
```yaml
# Adjust HPA settings
spec:
  minReplicas: 5
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

#### 3. Database Optimization
```bash
# Connection pooling
DATABASE_URL=postgresql://user:pass@host:5432/db?pool_size=20&max_overflow=30

# Query optimization
# - Add appropriate indexes
# - Optimize slow queries
# - Use connection pooling
```

## Rollback Procedures

### Docker Rollback
```bash
# Stop current container
docker stop acgs-pgp-v8

# Start previous version
docker run -d --name acgs-pgp-v8 acgs-pgp-v8:previous

# Or use deployment script
./scripts/deploy.sh rollback
```

### Kubernetes Rollback
```bash
# Check rollout history
kubectl rollout history deployment/acgs-pgp-v8 -n acgs-system

# Rollback to previous version
kubectl rollout undo deployment/acgs-pgp-v8 -n acgs-system

# Rollback to specific revision
kubectl rollout undo deployment/acgs-pgp-v8 --to-revision=2 -n acgs-system

# Check rollout status
kubectl rollout status deployment/acgs-pgp-v8 -n acgs-system
```

## Maintenance

### Regular Tasks
- Monitor service health and performance
- Review and rotate logs
- Update dependencies and security patches
- Backup configuration and data
- Performance optimization review

### Update Procedures
1. Test updates in staging environment
2. Create backup of current configuration
3. Deploy new version using rolling update
4. Validate deployment
5. Monitor for issues
6. Rollback if necessary

## Support

For deployment issues:
1. Check the operational runbook: `docs/OPERATIONAL_RUNBOOK.md`
2. Review API documentation: `docs/API_DOCUMENTATION.md`
3. Check service logs and metrics
4. Contact ACGS-1 operations team
