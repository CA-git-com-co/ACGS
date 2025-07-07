# ACGS-2 Production Deployment Guide - 2025 Edition

**Last Updated**: July 2, 2025
**Version**: 2.0.0
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->
**Performance Targets**: P99 ≤5ms, 100+ RPS, 85% cache hit rate

This comprehensive guide provides step-by-step instructions for deploying the ACGS-2 system with current performance optimizations and infrastructure specifications.

## Current Infrastructure Status

### Performance Achievements
- **P99 Latency**: 0.97ms (Target: ≤5ms) ✅
- **Throughput**: 306.9 RPS (Target: ≥100 RPS) ✅
- **Constitutional Compliance**: 98.0% (Target: ≥95%) ✅
- **WINA Optimization**: 65% efficiency gain ✅
- **Cache Hit Rate**: 25% (Target: 85% - optimization in progress)

### Infrastructure Ports
- **PostgreSQL**: Port 5439 (Production database)
- **Redis**: Port 6389 (Caching and session management)
- **Auth Service**: Port 8016 (JWT authentication)
- **Core Services**: Ports 8001-8006 (Microservices)

## 1. Prerequisites

- Kubernetes cluster (v1.28+) with GPU node pools
- `kubectl` configured to connect to your cluster
- Docker and Docker Compose installed (for local development/testing)
- `uv` package manager (recommended) or `pip`

## 2. Deployment Order

The deployment must follow a specific dependency order to ensure proper system functionality and constitutional hash consistency.

1.  **Infrastructure Services**: Core databases and caching layers.
2.  **Monitoring Services**: Prometheus and Grafana for observability.
3.  **Core Microservices**: The seven ACGS-PGP services.

## 3. Deployment Steps

### Phase 1: Deploy Infrastructure Services

These services are foundational and must be deployed first.

```bash
# Apply Kubernetes secrets
kubectl apply -f infrastructure/kubernetes/acgs-secrets.yaml

# Deploy CockroachDB
kubectl apply -f infrastructure/kubernetes/cockroachdb.yaml

# Deploy DragonflyDB
kubectl apply -f infrastructure/kubernetes/dragonflydb.yaml
```

### Phase 2: Deploy Monitoring Services

Deploy Prometheus and Grafana for system observability with constitutional compliance monitoring.

```bash
# Deploy Prometheus with constitutional configuration
kubectl apply -f infrastructure/kubernetes/prometheus.yaml

# Deploy Grafana
kubectl apply -f infrastructure/kubernetes/grafana.yaml

# Deploy monitoring rules and dashboards
kubectl apply -f infrastructure/kubernetes/monitoring/prometheus-rules.yaml
kubectl apply -f config/monitoring/acgs_alert_rules.yml
kubectl apply -f config/monitoring/constitutional_compliance_rules.yml

# Configure Prometheus with constitutional configuration
kubectl create configmap prometheus-config \
  --from-file=config/monitoring/prometheus-constitutional.yml

# Configure constitutional alerting rules
kubectl create configmap prometheus-rules \
  --from-file=config/monitoring/constitutional_rules.yml

# Configure Grafana dashboards
# Access Grafana UI and import dashboards from:
# - config/monitoring/grafana-constitutional-dashboard.json (Primary constitutional dashboard)
# - config/grafana/dashboards/nano-vllm-constitutional-ai.json
# - config/monitoring/acgs_constitutional_dashboard.json
# - config/monitoring/acgs_production_dashboard.json
```

#### Alternative: Docker Compose Monitoring Stack

For non-Kubernetes deployments, use the Docker Compose monitoring stack:

```bash
# Deploy monitoring infrastructure with Docker Compose
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Verify monitoring services are running
docker-compose -f docker-compose.monitoring.yml ps
```

### Phase 3: Deploy Core Microservices

Deploy the seven ACGS-PGP microservices. Ensure your Docker images are built and pushed to a registry accessible by your Kubernetes cluster.

```bash
# Deploy Authentication Service
kubectl apply -f services/platform/authentication/kubernetes/deployment.yaml

# Deploy Constitutional AI Service
kubectl apply -f services/core/constitutional-ai/kubernetes/deployment.yaml

# Deploy Integrity Service
kubectl apply -f services/core/integrity/kubernetes/deployment.yaml

# Deploy Formal Verification Service
kubectl apply -f services/core/formal-verification/kubernetes/deployment.yaml

# Deploy Governance Synthesis Service
kubectl apply -f services/core/governance-synthesis/kubernetes/deployment.yaml

# Deploy Policy Governance Service
kubectl apply -f services/core/policy-governance/kubernetes/deployment.yaml

# Deploy Evolutionary Computation Service
kubectl apply -f services/core/evolutionary-computation/kubernetes/deployment.yaml

# Deploy Model Orchestrator Service (if applicable)
# kubectl apply -f services/core/model-orchestrator/kubernetes/deployment.yaml
```

## 4. Health Validation Commands

After each deployment phase, validate the health of the deployed components.

### Infrastructure Validation

```bash
kubectl get pods -l app=cockroachdb
kubectl get pods -l app=dragonflydb
kubectl logs -l app=cockroachdb # Check CockroachDB logs for readiness
kubectl logs -l app=dragonflydb # Check DragonflyDB logs for readiness
```

### Monitoring Validation

```bash
kubectl get pods -l app=prometheus
kubectl get pods -l app=grafana

# Verify Prometheus is collecting constitutional metrics
kubectl port-forward svc/prometheus 9090:9090 &
curl -s "http://localhost:9090/api/v1/query?query=up{constitutional_hash=\"cdd01ef066bc6cf2\"}"

# Verify constitutional alerting rules are loaded
curl -s "http://localhost:9090/api/v1/rules" | grep "cdd01ef066bc6cf2"

# Access Grafana dashboard and verify:
# 1. Prometheus data source is connected
# 2. Constitutional dashboard is imported and functional
# 3. Constitutional hash template is properly configured
kubectl port-forward svc/grafana 3000:3000 &
# Navigate to http://localhost:3000 and import config/monitoring/grafana-constitutional-dashboard.json
```

### Service Validation

```bash
kubectl get pods -l app=auth-service
kubectl get pods -l app=constitutional-ai-service
kubectl get pods -l app=integrity-service
kubectl get pods -l app=formal-verification-service
kubectl get pods -l app=governance-synthesis-service
kubectl get pods -l app=policy-governance-service
kubectl get pods -l app=evolutionary-computation-service

# Check service health endpoints (replace with actual service IPs/ports)
curl http://<auth-service-ip>:8000/health
curl http://<constitutional-ai-service-ip>:8001/health
curl http://<integrity-service-ip>:8002/health
# ... and so on for all services
```

## 5. Emergency Procedures

### Emergency Shutdown

In case of a critical emergency, follow these steps for rapid shutdown. The RTO (Recovery Time Objective) for emergency shutdown is targeted at <30 minutes.

```bash
# Scale down all ACGS-PGP deployments
kubectl scale --replicas=0 deployment -l app=acgs-service

# Optionally, delete all ACGS-PGP related resources (use with extreme caution)
# kubectl delete all -l app=acgs-service
# kubectl delete all -l app=cockroachdb
# kubectl delete all -l app=dragonflydb
# kubectl delete all -l app=prometheus
# kubectl delete all -l app=grafana
```

### Rollback

Refer to `PRODUCTION_READINESS_CHECKLIST.md` for detailed rollback criteria and procedures.

## 6. Troubleshooting Guidance

- **Unified Architecture Guide**: For a comprehensive overview of the ACGS architecture, see the [ACGS Unified Architecture Guide](../architecture/ACGS_UNIFIED_ARCHITECTURE_GUIDE.md).
- **GEMINI.md**: For a comprehensive overview of the entire ACGS project, including development environment setup, testing commands, and service architecture, see the [GEMINI.md](../../GEMINI.md) file.

- **Pod stuck in Pending**: Check `kubectl describe pod <pod-name>` for events related to scheduling, resource limits, or persistent volume claims.
- **Pod in CrashLoopBackOff**: Check `kubectl logs <pod-name>` for application errors.
- **Service Unreachable**: Verify service and ingress/route configurations. Check `kubectl get svc` and `kubectl get ing` (or `kubectl get route` for OpenShift).
- **Constitutional Hash Mismatch**: Verify `CONSTITUTIONAL_HASH` environment variable in service deployments. Ensure all services are using `cdd01ef066bc6cf2`.
- **Performance Degradation**: Use Grafana dashboards to identify bottlenecks (CPU, memory, network, database). Run load tests to simulate and diagnose.
