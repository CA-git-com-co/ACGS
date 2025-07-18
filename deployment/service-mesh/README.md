# ACGS-2 Service Mesh Implementation
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive Istio service mesh implementation for ACGS-2 (Advanced Constitutional Governance System). This service mesh provides advanced traffic management, security, and observability capabilities while maintaining constitutional compliance throughout all inter-service communications.

## Constitutional Compliance

All service mesh components maintain constitutional hash `cdd01ef066bc6cf2` validation and enforce performance targets:
- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Mutual TLS**: Strict mode for all communications
- **Observability**: 100% tracing and metrics collection

## Architecture

### Service Mesh Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Istio Control Plane                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Istiod    │  │   Ingress   │  │   Egress    │        │
│  │  (Pilot)    │  │   Gateway   │  │   Gateway   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Data Plane (Envoy Sidecars)              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Constitutional│  │   Agent     │  │ Management  │        │
│  │    Core     │  │  Services   │  │  Services   │        │
│  │   + Proxy   │  │  + Proxy    │  │  + Proxy    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Observability Stack                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Jaeger    │  │    Kiali    │  │   Grafana   │        │
│  │  (Tracing)  │  │  (Topology) │  │ (Metrics)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## System Components

### 1. Istio Installation (`istio-installation.yaml`)
- **Automated Istio setup** with constitutional compliance
- **Control plane configuration** optimized for ACGS-2
- **Gateway configuration** for ingress/egress traffic
- **Namespace preparation** with sidecar injection

### 2. Traffic Management (`traffic-management.yaml`)
- **Gateway configuration** for external traffic
- **VirtualService routing** with constitutional headers
- **DestinationRule policies** for load balancing and circuit breaking
- **ServiceEntry** for external API access (GroqCloud, OpenAI)
- **EnvoyFilter** for constitutional compliance validation

### 3. Security Policies (`security-policies.yaml`)
- **PeerAuthentication** with strict mTLS
- **AuthorizationPolicy** for service-to-service access
- **RequestAuthentication** with JWT validation
- **Sidecar configuration** for traffic isolation

### 4. Observability (`observability.yaml`)
- **Telemetry configuration** for metrics and tracing
- **Jaeger tracing** with constitutional compliance tags
- **Kiali service mesh visualization**
- **OpenTelemetry collector** for comprehensive observability

### 5. Deployment Manager (`service-mesh-deploy.py`)
- **Automated deployment** orchestration
- **Validation and health checks**
- **Constitutional compliance verification**
- **Performance monitoring setup**

## Installation

### Prerequisites
```bash
# Kubernetes cluster v1.25+
kubectl version --short

# Sufficient resources (minimum 4 CPUs, 8GB RAM)
kubectl get nodes

# ACGS-2 namespace exists
kubectl get namespace acgs-system
```

### Automated Installation
```bash
# Make installation script executable
chmod +x istio-installation.yaml

# Run installation
./istio-installation.yaml

# Verify installation
kubectl get pods -n istio-system
kubectl get pods -n acgs-system
```

### Manual Installation
```bash
# 1. Install Istio control plane
kubectl apply -f istio-installation.yaml

# 2. Configure namespace
kubectl label namespace acgs-system istio-injection=enabled
kubectl label namespace acgs-system constitutional-hash=cdd01ef066bc6cf2

# 3. Apply traffic management
kubectl apply -f traffic-management.yaml

# 4. Apply security policies
kubectl apply -f security-policies.yaml

# 5. Configure observability
kubectl apply -f observability.yaml
```

### Python Deployment Manager
```bash
# Install dependencies
pip install asyncio aiohttp pyyaml

# Run deployment
python3 service-mesh-deploy.py

# Check deployment status
kubectl get pods -n istio-system
kubectl get pods -n acgs-system
```

## Configuration

### Traffic Management
```yaml
# Gateway configuration
gateway:
  hosts: ["acgs.local", "api.acgs.local"]
  tls_mode: "SIMPLE"
  
# VirtualService routing
routing:
  constitutional_core:
    timeout: 5s
    retries: 3
    headers:
      constitutional-hash: "cdd01ef066bc6cf2"
      
# DestinationRule policies
policies:
  load_balancer: "LEAST_CONN"
  circuit_breaker:
    consecutive_errors: 5
    interval: 30s
```

### Security Configuration
```yaml
# Mutual TLS
mutual_tls:
  mode: "STRICT"
  
# Authorization policies
authorization:
  constitutional_core:
    principals: ["cluster.local/ns/acgs-system/sa/acgs-system-sa"]
    operations: ["GET", "POST", "PUT"]
    conditions:
      - key: "request.headers[constitutional-hash]"
        values: ["cdd01ef066bc6cf2"]
        
# JWT authentication
jwt:
  issuer: "https://acgs.local/auth"
  audience: "acgs-api"
  jwks_uri: "https://acgs.local/auth/.well-known/jwks.json"
```

### Observability Configuration
```yaml
# Tracing
tracing:
  provider: "jaeger"
  sampling_rate: 1.0
  custom_tags:
    constitutional_hash: "cdd01ef066bc6cf2"
    environment: "production"
    
# Metrics
metrics:
  provider: "prometheus"
  constitutional_labels:
    constitutional_hash: "cdd01ef066bc6cf2"
    compliance_status: "validated"
    
# Access logging
access_logging:
  format: "CONSTITUTIONAL_HASH:cdd01ef066bc6cf2 [%START_TIME%] ..."
  providers: ["otel"]
```

## Traffic Management Features

### Intelligent Routing
- **Constitutional header validation** on all requests
- **Performance-based routing** with P99 latency monitoring
- **Circuit breaker patterns** for fault tolerance
- **Retry policies** with exponential backoff

### Load Balancing
- **LEAST_CONN algorithm** for optimal distribution
- **Health-based routing** with automatic failover
- **Weighted routing** for canary deployments
- **Session affinity** for stateful services

### External Integration
- **GroqCloud API** access with constitutional validation
- **OpenAI API** integration with compliance headers
- **Rate limiting** and timeout configuration
- **TLS termination** for external connections

## Security Features

### Mutual TLS (mTLS)
- **Strict mode** enforcement for all communications
- **Automatic certificate management** via Istio
- **Certificate rotation** and renewal
- **Constitutional compliance** validation in certificates

### Authorization Policies
- **Service-to-service** access control
- **Operation-level** permissions (GET, POST, PUT, DELETE)
- **Conditional access** based on constitutional headers
- **Namespace isolation** and cross-namespace policies

### JWT Authentication
- **Token validation** for external requests
- **Audience verification** for API access
- **Token forwarding** for service chains
- **Custom claims** for constitutional compliance

## Observability Features

### Distributed Tracing
- **Jaeger integration** with constitutional tags
- **100% sampling** for complete visibility
- **Custom span attributes** for compliance tracking
- **Performance analysis** with P99 latency monitoring

### Metrics Collection
- **Prometheus integration** with constitutional labels
- **Custom metrics** for compliance validation
- **Performance metrics** for SLA monitoring
- **Resource utilization** tracking

### Service Topology
- **Kiali visualization** of service mesh
- **Real-time traffic flow** analysis
- **Security policy** visualization
- **Performance bottleneck** identification

## Performance Optimization

### Latency Optimization
```yaml
# Connection pooling
connection_pool:
  tcp:
    max_connections: 100
    connect_timeout: 10s
  http:
    http1_max_pending_requests: 50
    max_requests_per_connection: 10
    
# Timeout configuration
timeouts:
  constitutional_core: 5s
  database_services: 3s
  external_apis: 10s
```

### Throughput Optimization
```yaml
# Load balancing
load_balancer:
  algorithm: "LEAST_CONN"
  health_check:
    interval: 10s
    timeout: 3s
    
# Circuit breaker
circuit_breaker:
  consecutive_errors: 5
  interval: 30s
  max_ejection_percent: 50
```

## Monitoring and Alerting

### Constitutional Compliance Monitoring
```yaml
# Envoy filter for compliance
envoy_filter:
  lua_script: |
    function envoy_on_request(request_handle)
      local hash = request_handle:headers():get("constitutional-hash")
      if hash ~= "cdd01ef066bc6cf2" then
        request_handle:respond({[":status"] = "403"}, "Constitutional hash required")
      end
    end
```

### Performance Monitoring
```yaml
# Performance alerts
alerts:
  - name: "HighLatency"
    condition: "p99_latency > 5ms"
    severity: "warning"
    
  - name: "LowThroughput"
    condition: "requests_per_second < 100"
    severity: "warning"
    
  - name: "ConstitutionalViolation"
    condition: "constitutional_hash_mismatch > 0"
    severity: "critical"
```

## Troubleshooting

### Common Issues

1. **Sidecar Injection Not Working**
```bash
# Check namespace labels
kubectl get namespace acgs-system --show-labels

# Verify injection configuration
kubectl get mutatingwebhookconfiguration istio-sidecar-injector -o yaml

# Check webhook status
kubectl get pods -n istio-system -l app=istiod
```

2. **mTLS Connection Issues**
```bash
# Check peer authentication
kubectl get peerauthentication -n acgs-system

# Verify certificates
kubectl exec -it <pod-name> -c istio-proxy -- openssl s_client -connect <service>:<port>

# Check Istio configuration
istioctl proxy-config cluster <pod-name> -n acgs-system
```

3. **Traffic Routing Problems**
```bash
# Check virtual services
kubectl get virtualservice -n acgs-system

# Verify destination rules
kubectl get destinationrule -n acgs-system

# Debug Envoy configuration
istioctl proxy-config route <pod-name> -n acgs-system
```

### Debugging Commands
```bash
# Check Istio installation
istioctl verify-install

# Analyze configuration
istioctl analyze -n acgs-system

# Check proxy configuration
istioctl proxy-config all <pod-name> -n acgs-system

# View access logs
kubectl logs <pod-name> -c istio-proxy -n acgs-system

# Check metrics
kubectl port-forward -n istio-system svc/prometheus 9090:9090
```

## Best Practices

### Configuration Management
- Use **constitutional hash labels** on all resources
- Implement **gradual rollout** for policy changes
- Maintain **configuration versioning** and rollback capabilities
- Regular **security policy audits** and updates

### Performance Optimization
- Monitor **P99 latency** and throughput metrics
- Implement **circuit breakers** for fault tolerance
- Use **connection pooling** for database services
- Regular **performance testing** and optimization

### Security Hardening
- Enforce **strict mTLS** for all communications
- Implement **least privilege** authorization policies
- Regular **certificate rotation** and validation
- Monitor **security violations** and anomalies

### Observability
- Enable **comprehensive tracing** for all services
- Implement **custom metrics** for business logic
- Set up **alerting** for constitutional violations
- Regular **observability stack** maintenance

---

**Navigation**: [Root](../../CLAUDE.md) | [Deployment](../README.md) | [Kubernetes](../kubernetes/README.md)

**Constitutional Compliance**: All service mesh components maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets (P99 <5ms, >100 RPS, strict mTLS).

**Last Updated**: 2025-07-18 - Service mesh implementation complete