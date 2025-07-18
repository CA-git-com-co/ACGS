# ACGS-2 Production Deployment Guide
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive production deployment infrastructure for ACGS-2 (Advanced Constitutional Governance System) with constitutional compliance validation, automated testing, and enterprise-grade security.

## 🏛️ Constitutional Requirements

All deployments must maintain constitutional compliance:
- **Constitutional Hash**: `cdd01ef066bc6cf2` (validated in all services)
- **Performance Targets**: P99 <5ms, >100 RPS minimum
- **Security Standards**: Zero-trust architecture with audit trails
- **Compliance Monitoring**: 100% constitutional hash validation

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (v1.24+)
- Docker (v20.10+)
- kubectl configured
- Helm (v3.8+)
- Container registry access

### One-Command Deployment

```bash
# Production deployment
./deployment/scripts/deploy.sh -e production -t v1.0.0

# Staging deployment
./deployment/scripts/deploy.sh -e staging -t latest

# Development deployment with Docker Compose
cd deployment/docker
docker-compose -f docker-compose.production.yml up -d
```

## 📋 Deployment Components

### Core Infrastructure
- **PostgreSQL**: Primary database with constitutional audit logging
- **Redis**: Distributed cache and session storage
- **Nginx**: Reverse proxy with security headers
- **Traefik**: Load balancer with automatic HTTPS

### ACGS-2 Services
1. **Constitutional Core** (Port 8001): Constitutional validation engine
2. **Auth Service** (Port 8013): JWT authentication with RBAC
3. **Monitoring Service** (Port 8014): System health and metrics
4. **Audit Service** (Port 8015): Immutable audit trails
5. **GDPR Compliance** (Port 8016): Data subject rights management
6. **Alerting Service** (Port 8017): Constitutional alert management
7. **API Gateway** (Port 8080): Unified API endpoint

### Observability Stack
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Dashboards and visualization
- **Jaeger**: Distributed tracing
- **Alert Manager**: Constitutional alert routing

## 🐳 Container Deployment

### Docker Compose Production

```bash
cd deployment/docker

# Set environment variables
export POSTGRES_PASSWORD=secure_password
export JWT_SECRET=jwt_secret_key
export GRAFANA_PASSWORD=grafana_password
export DOMAIN=acgs.example.com
export ACME_EMAIL=admin@acgs.example.com

# Deploy full stack
docker-compose -f docker-compose.production.yml up -d

# Monitor deployment
docker-compose logs -f
```

### Individual Service Build

```bash
# Build specific service
docker build \
  -f deployment/docker/Dockerfile.production \
  -t acgs/auth-service:v1.0.0 \
  --build-arg SERVICE_NAME=auth-service \
  --build-arg SERVICE_PATH=auth-service \
  .

# Run with constitutional validation
docker run -d \
  -p 8013:8013 \
  -e CONSTITUTIONAL_HASH=cdd01ef066bc6cf2 \
  -e JWT_SECRET=secret_key \
  acgs/auth-service:v1.0.0
```

## ☸️ Kubernetes Deployment

### Namespace Setup

```bash
# Create namespace and RBAC
kubectl apply -f deployment/kubernetes/namespace.yaml

# Configure secrets (update with real values)
kubectl apply -f deployment/kubernetes/secrets.yaml

# Apply configuration
kubectl apply -f deployment/kubernetes/configmap.yaml
```

### Service Deployment

```bash
# Deploy infrastructure
kubectl apply -f deployment/kubernetes/infrastructure/

# Deploy ACGS-2 services
kubectl apply -f deployment/kubernetes/deployments/

# Configure ingress
kubectl apply -f deployment/kubernetes/ingress.yaml

# Verify deployment
kubectl get pods -n acgs-system
```

### Helm Deployment

```bash
# Add ACGS-2 Helm repository
helm repo add acgs-2 https://charts.acgs.example.com
helm repo update

# Deploy with constitutional validation
helm install acgs-2 acgs-2/acgs-system \
  --namespace acgs-system \
  --create-namespace \
  --set constitutional.hash=cdd01ef066bc6cf2 \
  --set image.tag=v1.0.0 \
  --set domain=acgs.example.com

# Upgrade deployment
helm upgrade acgs-2 acgs-2/acgs-system \
  --set image.tag=v1.1.0
```

## 🔧 Configuration Management

### Environment Variables

```bash
# Core configuration
export CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
export DATABASE_URL=postgresql://user:pass@localhost/acgs_db
export REDIS_URL=redis://localhost:6379/0
export JWT_SECRET=secure_jwt_secret

# Performance targets
export PERFORMANCE_TARGETS_P99_MS=5
export PERFORMANCE_TARGETS_THROUGHPUT_RPS=100

# Security configuration
export SECURITY_POLICY=strict
export CONSTITUTIONAL_COMPLIANCE_REQUIRED=true
export AUDIT_LOGGING_ENABLED=true
```

### ConfigMap Customization

```yaml
# deployment/kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: acgs-config
data:
  CONSTITUTIONAL_HASH: "cdd01ef066bc6cf2"
  LOG_LEVEL: "INFO"
  PERFORMANCE_TARGETS_P99_MS: "5"
  PERFORMANCE_TARGETS_THROUGHPUT_RPS: "100"
  CONSTITUTIONAL_COMPLIANCE_REQUIRED: "true"
```

### Secrets Management

```bash
# Create secrets from files
kubectl create secret generic acgs-secrets \
  --from-file=postgres-password=postgres.txt \
  --from-file=jwt-secret=jwt.txt \
  --from-file=redis-password=redis.txt \
  -n acgs-system

# Create TLS secrets
kubectl create secret tls tls-certificates \
  --cert=tls.crt \
  --key=tls.key \
  -n acgs-system
```

## 🔍 Monitoring & Observability

### Metrics Collection

```bash
# Access Prometheus
kubectl port-forward service/prometheus 9090:9090 -n acgs-system

# Access Grafana
kubectl port-forward service/grafana 3000:3000 -n acgs-system

# View metrics
curl http://localhost:9090/api/v1/query?query=constitutional_compliance_rate
```

### Constitutional Compliance Monitoring

```bash
# Monitor constitutional hash validation
kubectl logs -l constitutional.hash=cdd01ef066bc6cf2 -n acgs-system

# Check compliance metrics
curl -s http://localhost:8014/api/v1/metrics | grep constitutional

# Verify all services report correct hash
for service in auth-service monitoring-service audit-service; do
  kubectl port-forward service/$service 8080:8080 -n acgs-system &
  HASH=$(curl -s http://localhost:8080/health | jq -r '.constitutional_hash')
  echo "$service: $HASH"
  pkill -f "kubectl port-forward"
done
```

### Health Checks

```bash
# Check all service health
kubectl get pods -n acgs-system
kubectl get services -n acgs-system

# Service-specific health checks
curl http://localhost:8013/health  # auth-service
curl http://localhost:8014/health  # monitoring-service
curl http://localhost:8015/health  # audit-service
curl http://localhost:8017/health  # alerting-service

# Constitutional compliance verification
curl -s http://localhost:8013/health | jq '.constitutional_hash'
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Constitutional Hash Mismatch
```bash
# Symptom: Services failing constitutional validation
# Solution: Verify environment variable is set correctly
kubectl get configmap acgs-config -n acgs-system -o yaml
kubectl set env deployment/auth-service CONSTITUTIONAL_HASH=cdd01ef066bc6cf2 -n acgs-system
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
kubectl get pods -l app=postgres -n acgs-system
kubectl logs deployment/postgres -n acgs-system

# Test database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql postgresql://acgs_user:password@postgres:5432/acgs_db
```

#### 3. Service Discovery Problems
```bash
# Check service endpoints
kubectl get endpoints -n acgs-system

# Verify DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup auth-service.acgs-system.svc.cluster.local
```

#### 4. Performance Issues
```bash
# Check resource usage
kubectl top pods -n acgs-system
kubectl top nodes

# Scale services if needed
kubectl scale deployment auth-service --replicas=5 -n acgs-system

# Check performance metrics
curl http://localhost:8014/api/v1/metrics
```

### Log Collection

```bash
# Collect all service logs
kubectl logs -l app.kubernetes.io/part-of=acgs-2 -n acgs-system --tail=100

# Specific service logs
kubectl logs deployment/auth-service -n acgs-system -f

# Save logs for analysis
kubectl logs deployment/auth-service -n acgs-system > auth-service.log
```

### Emergency Rollback

```bash
# Rollback specific service
kubectl rollout undo deployment/auth-service -n acgs-system

# Rollback all services
for service in auth-service monitoring-service audit-service; do
  kubectl rollout undo deployment/$service -n acgs-system
done

# Check rollback status
kubectl rollout status deployment/auth-service -n acgs-system
```

## 🔐 Security Considerations

### Container Security

- **Non-root user**: All containers run as UID 1001
- **Read-only filesystem**: Root filesystem is read-only
- **Security contexts**: Drop all capabilities, no privilege escalation
- **Resource limits**: CPU and memory limits enforced
- **Image scanning**: Automated vulnerability scanning

### Network Security

- **Network policies**: Restrict inter-pod communication
- **TLS encryption**: All traffic encrypted in transit
- **Security headers**: Comprehensive HTTP security headers
- **Rate limiting**: API endpoint rate limiting
- **Firewall rules**: Ingress/egress traffic control

### Secrets Management

- **Kubernetes secrets**: Encrypted at rest
- **Least privilege**: Minimal RBAC permissions
- **Rotation**: Regular secret rotation
- **External secrets**: Integration with external secret managers
- **Audit logging**: All secret access logged

## 📊 Performance Optimization

### Resource Scaling

```bash
# Horizontal Pod Autoscaler
kubectl autoscale deployment auth-service --cpu-percent=70 --min=3 --max=10 -n acgs-system

# Vertical Pod Autoscaler
kubectl apply -f deployment/kubernetes/vpa/

# Check scaling events
kubectl get hpa -n acgs-system
kubectl describe hpa auth-service-hpa -n acgs-system
```

### Database Optimization

```bash
# Connection pooling configuration
export DATABASE_POOL_SIZE=20
export DATABASE_MAX_OVERFLOW=10

# Query optimization
export DATABASE_QUERY_TIMEOUT=30
export DATABASE_SLOW_QUERY_LOG=true
```

### Cache Configuration

```bash
# Redis optimization
export REDIS_MAXMEMORY=2gb
export REDIS_MAXMEMORY_POLICY=allkeys-lru
export REDIS_CLUSTER_ENABLED=true
```

## 🔄 CI/CD Integration

### GitHub Actions

The deployment includes automated CI/CD with:
- Constitutional compliance validation
- Security audit scanning
- Performance testing
- Automated deployments
- Rollback capabilities

```bash
# Trigger deployment
git tag v1.1.0
git push origin v1.1.0

# Monitor deployment
gh run list --workflow=deploy-production.yml
gh run watch
```

### GitOps Deployment

```bash
# ArgoCD deployment
kubectl apply -f deployment/gitops/argocd/

# Flux deployment
kubectl apply -f deployment/gitops/flux/
```

## 📈 Capacity Planning

### Resource Requirements

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| Auth Service | 100m-500m | 128Mi-512Mi | - |
| Constitutional Core | 200m-1000m | 256Mi-1Gi | - |
| Monitoring Service | 100m-500m | 256Mi-1Gi | - |
| PostgreSQL | 500m-2000m | 1Gi-4Gi | 100Gi |
| Redis | 100m-500m | 512Mi-2Gi | 10Gi |

### Scaling Guidelines

- **Development**: 1 replica per service
- **Staging**: 2 replicas per service
- **Production**: 3+ replicas per critical service
- **High Availability**: Multi-zone deployment

## 🆘 Support & Documentation

### Resources

- **Architecture Documentation**: `docs/architecture/`
- **API Documentation**: `docs/api/`
- **Operations Runbook**: `docs/operations/`
- **Security Policies**: `docs/security/`

### Getting Help

1. Check troubleshooting guide above
2. Review service logs and metrics
3. Validate constitutional compliance
4. Check GitHub issues and discussions
5. Contact ACGS-2 support team

---

**Constitutional Compliance**: All deployments maintain constitutional hash `cdd01ef066bc6cf2` validation and enforce performance targets (P99 <5ms, >100 RPS) as mandated by the ACGS-2 constitutional framework.

**Last Updated**: 2025-07-18 - Production Deployment Infrastructure Complete