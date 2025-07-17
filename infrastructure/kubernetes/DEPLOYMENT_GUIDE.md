# ACGS-PGP Kubernetes Deployment Guide
**Constitutional Hash: cdd01ef066bc6cf2**


## Overview

This guide provides step-by-step instructions for deploying the ACGS-PGP system to Kubernetes, following the ACGS-1 Lite architecture with constitutional AI constraints and DGM safety patterns.

## Prerequisites

- Kubernetes cluster (v1.24+) with kubectl configured
- Minimum 8 CPU cores and 16GB RAM available
- Persistent storage support (for CockroachDB and monitoring)
- Network policies support (recommended)

## Architecture Validation

The deployment includes:

- **7 Core Services**: auth:8000, ac:8001, integrity:8002, fv:8003, gs:8004, pgc:8005, ec:8006
- **Constitutional Hash**: `cdd01ef066bc6cf2`
- **Resource Limits**: 200m/500m CPU, 512Mi/1Gi memory per service
- **Performance Targets**: ≤2s response time, >95% constitutional compliance
- **Emergency Shutdown**: <30min RTO capability

## Deployment Order

### Phase 1: Infrastructure Foundation

```bash
# 1. Apply Linkerd CRDs (if using service mesh)
kubectl apply -f infrastructure/linkerd/linkerd-crds.yaml

# 2. Create namespace and secrets
kubectl create namespace acgs-system
kubectl apply -f infrastructure/kubernetes/acgs-secrets.yaml

# 3. Deploy databases and caching
kubectl apply -f infrastructure/kubernetes/cockroachdb.yaml
kubectl apply -f infrastructure/kubernetes/dragonflydb.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=cockroachdb -n acgs-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dragonflydb -n acgs-system --timeout=300s
```

### Phase 2: Policy and Monitoring

```bash
# 4. Deploy OPA for policy enforcement
kubectl apply -f infrastructure/kubernetes/opa.yaml

# 5. Deploy monitoring stack
kubectl apply -f infrastructure/kubernetes/prometheus.yaml
kubectl apply -f infrastructure/kubernetes/grafana.yaml

# Wait for monitoring to be ready
kubectl wait --for=condition=ready pod -l app=opa -n acgs-system --timeout=180s
kubectl wait --for=condition=ready pod -l app=prometheus -n acgs-system --timeout=180s
```

### Phase 3: Core Services Deployment

```bash
# 6. Deploy services in dependency order
kubectl apply -f infrastructure/kubernetes/services/auth-service.yaml
kubectl apply -f infrastructure/kubernetes/services/integrity-service.yaml
kubectl apply -f infrastructure/kubernetes/services/constitutional-ai-service.yaml
kubectl apply -f infrastructure/kubernetes/services/formal-verification-service.yaml
kubectl apply -f infrastructure/kubernetes/services/governance-synthesis-service.yaml
kubectl apply -f infrastructure/kubernetes/services/policy-governance-service.yaml
kubectl apply -f infrastructure/kubernetes/services/evolutionary-computation-service.yaml
kubectl apply -f infrastructure/kubernetes/services/model-orchestrator-service.yaml

# Wait for all services to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=acgs-system -n acgs-system --timeout=600s
```

## Health Validation

### Service Health Checks

```bash
# Check all pods are running
kubectl get pods -n acgs-system

# Check service endpoints
kubectl get svc -n acgs-system

# Verify constitutional compliance
kubectl logs -l app=constitutional-ai-service -n acgs-system --tail=50
```

### Performance Validation

```bash
# Test response times (requires cluster access)
kubectl run test-pod --image=curlimages/curl --rm -it --restart=Never -- \
  curl -w "@curl-format.txt" -o /dev/null -s http://auth-service.acgs-system:8000/health

# Check constitutional compliance metrics
kubectl port-forward svc/prometheus 9090:9090 -n acgs-system &
# Access http://localhost:9090 and query: constitutional_compliance_score
```

## Monitoring Setup

### Prometheus Queries

- Constitutional compliance: `constitutional_compliance_score > 0.95`
- Response time: `http_request_duration_seconds{quantile="0.95"} < 2.0`
- Service availability: `up{job=~"acgs-.*"} == 1`

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (admin/admin) after port-forwarding:

```bash
kubectl port-forward svc/grafana 3000:3000 -n acgs-system
```

## Emergency Procedures

### Emergency Shutdown (<30min RTO)

```bash
# Scale down all services immediately
kubectl scale deployment --all --replicas=0 -n acgs-system

# Verify shutdown
kubectl get pods -n acgs-system
```

### Rollback Procedure

```bash
# Rollback specific service
kubectl rollout undo deployment/constitutional-ai-service -n acgs-system

# Check rollback status
kubectl rollout status deployment/constitutional-ai-service -n acgs-system
```

## Troubleshooting

### Common Issues

1. **Pod CrashLoopBackOff**: Check logs with `kubectl logs <pod-name> -n acgs-system`
2. **Service Unreachable**: Verify service and endpoint with `kubectl describe svc <service-name> -n acgs-system`
3. **Constitutional Compliance Low**: Check OPA policies and model responses
4. **High Response Times**: Check resource limits and scaling

### Debug Commands

```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n acgs-system

# Check resource usage
kubectl top pods -n acgs-system

# View events
kubectl get events -n acgs-system --sort-by='.lastTimestamp'
```

## Next Steps

1. Configure external access (Ingress/LoadBalancer)
2. Set up automated backups for CockroachDB
3. Configure log aggregation
4. Implement blue-green deployment pipeline
5. Set up disaster recovery procedures

## Security Considerations

- All services run as non-root users
- Network policies restrict inter-service communication
- Secrets are encrypted at rest
- Regular security scanning recommended

For additional support, refer to individual service documentation in their respective directories.

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation


## Performance Requirements

### ACGS-2 Performance Targets
- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)  
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

### Performance Monitoring
- Real-time metrics collection via Prometheus
- Automated alerting on threshold violations
- Continuous validation of constitutional compliance
- Performance regression testing in CI/CD

### Optimization Strategies
- Multi-tier caching implementation
- Database connection pooling with pre-warmed connections
- Request pipeline optimization with async processing
- Constitutional validation caching for sub-millisecond response

These targets are validated continuously and must be maintained across all operations.
