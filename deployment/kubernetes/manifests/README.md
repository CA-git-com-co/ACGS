# ACGS-2 Kubernetes Manifests
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Complete Kubernetes manifests for deploying ACGS-2 (Advanced Constitutional Governance System) to production. These manifests provide comprehensive orchestration for all system components with constitutional compliance, security, and performance requirements.

## Constitutional Compliance

All manifests maintain constitutional hash `cdd01ef066bc6cf2` validation and enforce performance targets:
- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Availability**: 99.9% SLA compliance
- **Security**: High-level security controls and network policies

## Manifest Structure

### 1. Core Configuration
- **`namespace.yaml`**: Namespace definition with resource quotas and limits
- **`storage.yaml`**: Storage classes and persistent volume claims
- **`rbac.yaml`**: Role-based access control and service accounts
- **`secrets.yaml`**: Encrypted secrets for all services
- **`configmaps.yaml`**: Configuration data for all components
- **`security.yaml`**: Security policies and network controls

### 2. Infrastructure Services
- **`infrastructure.yaml`**: Core infrastructure (PostgreSQL, Redis, Nginx)
- **`monitoring.yaml`**: Monitoring stack (Prometheus, Grafana, AlertManager)

### 3. Orchestration
- **`kustomization.yaml`**: Kustomize configuration for deployment orchestration

## Components

### Infrastructure Layer
```yaml
# PostgreSQL Database
- Deployment: postgres (1 replica)
- Service: postgres (ClusterIP)
- Storage: 50Gi fast SSD
- Security: Read-only root filesystem, non-root user

# Redis Cache
- Deployment: redis (1 replica)
- Service: redis (ClusterIP)
- Storage: 10Gi fast SSD
- Security: Authentication, memory limits

# Nginx Ingress
- Deployment: nginx-ingress (2 replicas)
- Service: nginx-ingress (LoadBalancer)
- Security: TLS termination, rate limiting
```

### Monitoring Layer
```yaml
# Prometheus
- Deployment: prometheus (1 replica)
- Service: prometheus (ClusterIP)
- Storage: 100Gi monitoring data
- Configuration: Service discovery, alerting rules

# Grafana
- Deployment: grafana (1 replica)
- Service: grafana (ClusterIP)
- Configuration: Dashboards, data sources

# AlertManager
- Deployment: alertmanager (1 replica)
- Service: alertmanager (ClusterIP)
- Configuration: Alert routing, notifications
```

### Security Layer
```yaml
# Network Policies
- Default deny all traffic
- Service-specific ingress/egress rules
- Database isolation
- Monitoring access controls

# Pod Security Policies
- No privileged containers
- Read-only root filesystems
- Non-root user enforcement
- Capability dropping

# RBAC
- Service accounts for each component
- Least privilege access
- Cluster and namespace roles
```

## Deployment Instructions

### Prerequisites
1. **Kubernetes Cluster**: v1.25+ with RBAC enabled
2. **Storage**: Dynamic provisioning with SSD storage class
3. **Network**: CNI plugin with NetworkPolicy support
4. **Tools**: kubectl, kustomize (optional)

### Basic Deployment
```bash
# Create namespace and basic resources
kubectl apply -f namespace.yaml
kubectl apply -f storage.yaml
kubectl apply -f rbac.yaml
kubectl apply -f secrets.yaml
kubectl apply -f configmaps.yaml
kubectl apply -f security.yaml

# Deploy infrastructure
kubectl apply -f infrastructure.yaml

# Deploy monitoring
kubectl apply -f monitoring.yaml

# Verify deployment
kubectl get pods -n acgs-system
kubectl get services -n acgs-system
```

### Kustomize Deployment
```bash
# Deploy using Kustomize
kubectl apply -k .

# Verify deployment
kubectl get pods -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2
```

### Validation
```bash
# Check constitutional compliance
kubectl get all -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2

# Verify network policies
kubectl get networkpolicies -n acgs-system

# Check security policies
kubectl get podsecuritypolicies

# Test service connectivity
kubectl exec -it deployment/postgres -n acgs-system -- pg_isready
kubectl exec -it deployment/redis -n acgs-system -- redis-cli ping
```

## Configuration

### Environment Variables
```yaml
# Global configuration
CONSTITUTIONAL_HASH: "cdd01ef066bc6cf2"
ENVIRONMENT: "production"
LOG_LEVEL: "INFO"
PERFORMANCE_TARGET_P99_MS: "5"
PERFORMANCE_TARGET_RPS: "100"

# Database configuration
POSTGRES_HOST: "postgres"
POSTGRES_PORT: "5432"
POSTGRES_DB: "acgs_db"
POSTGRES_USER: "acgs_user"

# Cache configuration
REDIS_HOST: "redis"
REDIS_PORT: "6379"
```

### Resource Limits
```yaml
# Small services (agents, utilities)
requests:
  memory: "128Mi"
  cpu: "100m"
limits:
  memory: "512Mi"
  cpu: "500m"

# Medium services (core services)
requests:
  memory: "256Mi"
  cpu: "250m"
limits:
  memory: "1Gi"
  cpu: "1000m"

# Large services (database, monitoring)
requests:
  memory: "512Mi"
  cpu: "500m"
limits:
  memory: "4Gi"
  cpu: "2000m"
```

### Storage Configuration
```yaml
# Fast SSD storage class
StorageClass: acgs-fast-ssd
Provisioner: kubernetes.io/gce-pd
Parameters:
  type: pd-ssd
  replication-type: regional-pd
  
# Storage requirements
- PostgreSQL: 50Gi (fast SSD)
- Redis: 10Gi (fast SSD)
- Monitoring: 100Gi (fast SSD)
- Backups: 500Gi (standard)
- Logs: 200Gi (standard)
```

## Security Configuration

### Network Policies
```yaml
# Default deny all
- All pods: No ingress/egress by default

# Database access
- PostgreSQL: Only from core/agent/management components
- Redis: Only from core/agent/management components

# Service communication
- Core services: Inter-service communication allowed
- Agent services: Can communicate with core and each other
- Management services: Can communicate with all components

# External access
- Ingress: Only nginx-ingress can accept external traffic
- Monitoring: Only accessible via ingress
```

### Pod Security
```yaml
# Security context requirements
runAsNonRoot: true
readOnlyRootFilesystem: true
allowPrivilegeEscalation: false
capabilities:
  drop: ["ALL"]

# Resource constraints
memory: 4Gi max per container
cpu: 2000m max per container
storage: 100Gi max per PVC
```

### RBAC Configuration
```yaml
# Service accounts
- acgs-system-sa: Full namespace admin
- acgs-backup-sa: Backup operations
- acgs-monitoring-sa: Monitoring access
- acgs-security-sa: Security scanning
- acgs-deployment-sa: Deployment operations

# Permissions
- Least privilege principle
- Role-based access control
- Cluster-level and namespace-level roles
```

## Monitoring Configuration

### Prometheus
```yaml
# Scrape configuration
- Kubernetes API servers
- Kubernetes nodes
- All ACGS services
- System metrics

# Alerting rules
- Constitutional compliance violations
- Performance threshold breaches
- Service availability issues
- Resource utilization alerts
```

### Grafana
```yaml
# Data sources
- Prometheus metrics
- Kubernetes events
- Service logs

# Dashboards
- ACGS system overview
- Service performance
- Constitutional compliance
- Infrastructure health
```

### AlertManager
```yaml
# Alert routing
- Critical alerts: Immediate notification
- Warning alerts: Grouped notifications
- Constitutional alerts: Compliance team

# Notification channels
- Webhook to alerting service
- Email notifications
- Slack integration (optional)
```

## Troubleshooting

### Common Issues

1. **Pod Startup Issues**
```bash
# Check pod status
kubectl get pods -n acgs-system
kubectl describe pod <pod-name> -n acgs-system

# Check logs
kubectl logs <pod-name> -n acgs-system
kubectl logs <pod-name> -n acgs-system --previous
```

2. **Service Connection Issues**
```bash
# Check service endpoints
kubectl get endpoints -n acgs-system
kubectl describe service <service-name> -n acgs-system

# Test connectivity
kubectl exec -it <pod-name> -n acgs-system -- nslookup <service-name>
kubectl exec -it <pod-name> -n acgs-system -- curl http://<service-name>:<port>/health
```

3. **Storage Issues**
```bash
# Check PVC status
kubectl get pvc -n acgs-system
kubectl describe pvc <pvc-name> -n acgs-system

# Check storage class
kubectl get storageclass
kubectl describe storageclass acgs-fast-ssd
```

4. **Network Policy Issues**
```bash
# Check network policies
kubectl get networkpolicies -n acgs-system
kubectl describe networkpolicy <policy-name> -n acgs-system

# Test network connectivity
kubectl exec -it <pod-name> -n acgs-system -- nc -zv <service-name> <port>
```

### Debugging Commands
```bash
# Check all resources
kubectl get all -n acgs-system

# Check constitutional compliance
kubectl get all -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2

# Check resource usage
kubectl top pods -n acgs-system
kubectl top nodes

# Check events
kubectl get events -n acgs-system --sort-by=.metadata.creationTimestamp

# Check security
kubectl get podsecuritypolicies
kubectl get networkpolicies -n acgs-system
```

## Performance Tuning

### Resource Optimization
```yaml
# CPU optimization
- Use CPU requests/limits appropriately
- Monitor CPU throttling
- Adjust based on actual usage

# Memory optimization
- Set memory requests/limits
- Monitor memory usage patterns
- Use memory-efficient configurations

# Storage optimization
- Use appropriate storage classes
- Monitor I/O patterns
- Configure database parameters
```

### Network Optimization
```yaml
# Service mesh considerations
- Evaluate service mesh adoption
- Configure load balancing
- Implement circuit breakers

# DNS optimization
- Configure DNS caching
- Use headless services where appropriate
- Optimize service discovery
```

## Backup and Recovery

### Backup Strategy
```yaml
# Automated backups
- Database: Every 15 minutes
- Configurations: Every 6 hours
- Persistent volumes: Daily

# Backup validation
- Constitutional compliance checks
- Integrity verification
- Recovery testing
```

### Recovery Procedures
```yaml
# Service recovery
kubectl rollout restart deployment/<service-name> -n acgs-system
kubectl rollout status deployment/<service-name> -n acgs-system

# Database recovery
kubectl exec -it deployment/postgres -n acgs-system -- pg_restore

# Configuration recovery
kubectl apply -f configmaps.yaml
kubectl apply -f secrets.yaml
```

## Best Practices

### Development
- Always include constitutional hash in labels
- Use resource requests and limits
- Implement proper health checks
- Follow security best practices

### Operations
- Monitor constitutional compliance continuously
- Perform regular security scans
- Test disaster recovery procedures
- Maintain operational documentation

### Security
- Regularly update container images
- Scan for vulnerabilities
- Implement network segmentation
- Use least privilege access

---

**Navigation**: [Root](../../../CLAUDE.md) | [Deployment](../../README.md) | [Kubernetes](../README.md)

**Constitutional Compliance**: All manifests maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets (P99 <5ms, >100 RPS, 99.9% availability).

**Last Updated**: 2025-07-18 - Kubernetes manifests implementation