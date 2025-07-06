# ACGS Kubernetes Production Deployment

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

Comprehensive Kubernetes manifests for deploying the Autonomous Coding Governance System (ACGS) in production environments with constitutional compliance, security hardening, and enterprise-scale operational capabilities.

## Quick Start

```bash
# Deploy in order
kubectl apply -f namespace.yaml
kubectl apply -f persistent-volumes.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml  # WARNING: Change defaults for production!
kubectl apply -f rbac.yaml
kubectl apply -f database.yaml
kubectl apply -f redis.yaml
kubectl apply -f core-services.yaml
kubectl apply -f api-gateway.yaml
kubectl apply -f monitoring.yaml
kubectl apply -f network-policies.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa-vpa.yaml
```

## File Descriptions

| File                      | Description                                      |
| ------------------------- | ------------------------------------------------ |
| `namespace.yaml`          | Kubernetes namespaces with constitutional labels |
| `configmap.yaml`          | Configuration data and Nginx config              |
| `secrets.yaml`            | Encrypted secrets (change for production!)       |
| `persistent-volumes.yaml` | Storage classes and persistent volumes           |
| `database.yaml`           | PostgreSQL StatefulSet with RLS                  |
| `redis.yaml`              | Redis deployment for caching                     |
| `api-gateway.yaml`        | API Gateway with HPA and PDB                     |
| `core-services.yaml`      | All ACGS microservices                           |
| `monitoring.yaml`         | Prometheus and Grafana stack                     |
| `ingress.yaml`            | Nginx ingress with TLS and security headers      |
| `rbac.yaml`               | Role-based access control policies               |
| `network-policies.yaml`   | Network micro-segmentation                       |
| `hpa-vpa.yaml`            | Horizontal and vertical pod autoscaling          |
| `deployment-scripts.yaml` | Automated deployment scripts                     |

## Key Features

- **Constitutional Compliance**: All components validate constitutional hash `cdd01ef066bc6cf2`
- **Security Hardening**: RBAC, network policies, pod security contexts
- **High Availability**: Multi-replica deployments with pod disruption budgets
- **Auto-scaling**: HPA and VPA for dynamic resource management
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Multi-tenant**: Row-level security and tenant isolation

## Production Requirements

⚠️ **MUST CHANGE FOR PRODUCTION**:

- Update secrets in `secrets.yaml` with strong passwords
- Configure real TLS certificates in ingress
- Update hostnames in `ingress.yaml`
- Review resource limits and storage sizes

**Constitutional Hash**: `cdd01ef066bc6cf2`
