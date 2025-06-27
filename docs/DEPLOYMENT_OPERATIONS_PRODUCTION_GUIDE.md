# ACGS Production Deployment and Operations Guide

**Version**: 3.0.0  
**Last Updated**: 2025-06-24  
**Target Audience**: DevOps Engineers, System Administrators, Production Teams

## Overview

This guide provides comprehensive deployment and operations procedures for ACGS services, with specific guidance for production-ready and prototype services.

## Deployment Strategy by Implementation Status

### ✅ Production Ready Services

**Services**: Auth (8000), AC (8001), Integrity (8002)  
**Deployment Status**: ✅ **Approved for Production**  
**Monitoring**: Full production monitoring required  
**SLA**: Production-grade service level agreements apply

### 🧪 Prototype Services

**Services**: FV (8003), GS (8004), PGC (8005), EC (8006)  
**Deployment Status**: 🧪 **Development/Testing Only**  
**Monitoring**: Development monitoring sufficient  
**SLA**: No production SLA guarantees

---

## Production Deployment Architecture

### Infrastructure Requirements

#### Production Services (Auth, AC, Integrity)

```yaml
# Minimum production requirements
resources:
  cpu:
    request: 500m
    limit: 1000m
  memory:
    request: 1Gi
    limit: 2Gi
  storage: 10Gi

replicas:
  min: 3
  max: 10
  target_cpu: 70%

availability:
  target: 99.9%
  max_downtime: 8.76h/year
```

#### Prototype Services (FV, GS, PGC, EC)

```yaml
# Development/testing requirements
resources:
  cpu:
    request: 200m
    limit: 500m
  memory:
    request: 512Mi
    limit: 1Gi
  storage: 5Gi

replicas:
  min: 1
  max: 3
  target_cpu: 80%

availability:
  target: 95%
  max_downtime: 18.25d/year
```

### Network Architecture

#### Production Network Segmentation

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │  Production DMZ │    │ Internal Network│
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Auth Service │ │◄──►│ │   Gateway   │ │◄──►│ │AC Service   │ │
│ │   (8000)    │ │    │ │             │ │    │ │   (8001)    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │                 │    │ ┌─────────────┐ │
│ │Integrity    │ │    │                 │    │ │Database     │ │
│ │Service(8002)│ │    │                 │    │ │Cluster      │ │
│ └─────────────┘ │    │                 │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Service-Specific Deployment Procedures

### ✅ Auth Service (Port 8000) - Production Deployment

#### Pre-deployment Checklist

- [ ] Database migrations completed
- [ ] Redis cluster configured
- [ ] SSL certificates installed
- [ ] Environment variables configured
- [ ] Health checks validated
- [ ] Load balancer configured
- [ ] Monitoring alerts configured

#### Deployment Commands

```bash
# Production deployment
kubectl apply -f k8s/production/auth-service/

# Verify deployment
kubectl get pods -l app=auth-service
kubectl logs -l app=auth-service --tail=100

# Health check validation
curl -f https://auth.acgs.prod/health

# Performance validation
./scripts/validate_auth_performance.sh
```

#### Post-deployment Validation

```bash
# Functional testing
./tests/production/auth_service_smoke_test.sh

# Performance baseline
./scripts/auth_performance_baseline.sh

# Security validation
./scripts/auth_security_validation.sh

# Integration testing
./tests/integration/auth_integration_test.sh
```

### ✅ AC Service (Port 8001) - Production Deployment

#### Constitutional Compliance Setup

```bash
# Initialize constitutional state
./scripts/initialize_constitutional_state.sh --hash cdd01ef066bc6cf2

# Validate constitutional principles
./scripts/validate_constitutional_principles.sh

# Test compliance engine
./tests/constitutional/compliance_engine_test.sh
```

#### Deployment and Validation

```bash
# Deploy AC service
kubectl apply -f k8s/production/ac-service/

# Validate constitutional compliance
curl -X POST https://ac.acgs.prod/api/v1/constitutional/validate \
  -H "Content-Type: application/json" \
  -d '{"policy": "test_policy", "principles": ["transparency"]}'

# Performance validation
./scripts/validate_ac_performance.sh
```

### ✅ Integrity Service (Port 8002) - Production Deployment

#### Cryptographic Setup

```bash
# Initialize PGP keys
./scripts/initialize_pgp_keys.sh

# Configure audit trail
./scripts/configure_audit_trail.sh

# Test cryptographic functions
./tests/crypto/integrity_crypto_test.sh
```

---

## Prototype Service Deployment

### 🧪 Development/Testing Deployment

#### Prototype Service Warnings

```bash
# Display prototype warnings before deployment
echo "⚠️  WARNING: Deploying prototype services"
echo "   - Not suitable for production workloads"
echo "   - May contain mock implementations"
echo "   - Limited error handling and recovery"
echo "   - Performance not optimized"
echo "   - Use for development and testing only"
```

#### FV Service (Port 8003) - Prototype Deployment

```bash
# Deploy with prototype configuration
kubectl apply -f k8s/development/fv-service/

# Validate mock Z3 integration
curl http://fv.acgs.dev/api/v1/enterprise/status

# Check prototype limitations
./scripts/check_fv_prototype_status.sh
```

#### GS Service (Port 8004) - Prototype Deployment

```bash
# Deploy in minimal mode
kubectl apply -f k8s/development/gs-service/

# Check router availability
curl http://gs.acgs.dev/api/v1/status

# Validate minimal mode operation
./scripts/check_gs_minimal_mode.sh
```

---

## Configuration Management

### Production Configuration

#### Environment Variables (Production Services)

```bash
# Auth Service
export AUTH_DATABASE_URL="postgresql://auth:***@db.prod:5432/auth"
export AUTH_REDIS_URL="redis://redis.prod:6379/0"
export AUTH_JWT_SECRET="***"
export AUTH_ENVIRONMENT="production"

# AC Service
export AC_DATABASE_URL="postgresql://ac:***@db.prod:5432/ac"
export AC_CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
export AC_ENVIRONMENT="production"

# Integrity Service
export INTEGRITY_DATABASE_URL="postgresql://integrity:***@db.prod:5432/integrity"
export INTEGRITY_PGP_KEY_PATH="/etc/pgp/keys"
export INTEGRITY_ENVIRONMENT="production"
```

#### Development Configuration (Prototype Services)

```bash
# FV Service
export FV_Z3_MOCK_MODE="true"
export FV_ENVIRONMENT="development"
export FV_PROTOTYPE_MODE="true"

# GS Service
export GS_MINIMAL_MODE="true"
export GS_ROUTER_FALLBACK="true"
export GS_ENVIRONMENT="development"
```

### Configuration Validation

```bash
# Validate production configuration
./scripts/validate_production_config.sh

# Validate prototype configuration
./scripts/validate_prototype_config.sh
```

---

## Monitoring and Observability

### Production Monitoring (Auth, AC, Integrity)

#### Metrics Collection

```yaml
# Prometheus metrics
metrics:
  - request_duration_seconds
  - request_total
  - error_rate
  - active_connections
  - constitutional_compliance_rate
  - cryptographic_operations_total

# Custom dashboards
dashboards:
  - auth_service_dashboard.json
  - ac_service_dashboard.json
  - integrity_service_dashboard.json
```

#### Alerting Rules

```yaml
# Critical alerts
alerts:
  - name: ServiceDown
    condition: up == 0
    severity: critical

  - name: HighErrorRate
    condition: error_rate > 0.05
    severity: warning

  - name: ConstitutionalViolation
    condition: constitutional_violations > 0
    severity: critical
```

### Development Monitoring (Prototype Services)

#### Basic Monitoring

```yaml
# Development metrics
metrics:
  - basic_health_check
  - prototype_status
  - mock_component_status
  - development_performance

# Development alerts
alerts:
  - name: PrototypeServiceDown
    condition: up == 0
    severity: warning
```

---

## Operational Procedures

### Production Operations

#### Daily Operations Checklist

- [ ] Check service health status
- [ ] Review error logs and alerts
- [ ] Validate constitutional compliance metrics
- [ ] Check performance baselines
- [ ] Review security audit logs
- [ ] Validate backup completion
- [ ] Check resource utilization

#### Weekly Operations

- [ ] Performance trend analysis
- [ ] Security vulnerability assessment
- [ ] Capacity planning review
- [ ] Disaster recovery testing
- [ ] Documentation updates

### Prototype Operations

#### Development Operations

- [ ] Check prototype service status
- [ ] Review mock component functionality
- [ ] Assess production readiness progress
- [ ] Update prototype limitations documentation
- [ ] Plan production readiness improvements

---

## Disaster Recovery

### Production Services Recovery

#### Recovery Time Objectives (RTO)

- **Auth Service**: 15 minutes
- **AC Service**: 30 minutes (constitutional state critical)
- **Integrity Service**: 15 minutes (data integrity critical)

#### Recovery Point Objectives (RPO)

- **Database**: 5 minutes (continuous replication)
- **Configuration**: 1 hour (version controlled)
- **Audit Logs**: 0 minutes (real-time replication)

#### Recovery Procedures

```bash
# Emergency recovery
./scripts/emergency_recovery.sh --service auth

# Constitutional state recovery
./scripts/recover_constitutional_state.sh --hash cdd01ef066bc6cf2

# Integrity validation post-recovery
./scripts/validate_integrity_post_recovery.sh
```

### Prototype Services Recovery

#### Development Recovery

- **RTO**: Best effort (no SLA)
- **RPO**: Development data acceptable loss
- **Procedure**: Redeploy from latest development branch

---

## Troubleshooting Guide

### Production Service Issues

#### Common Issues and Solutions

1. **Service Unavailable**:

   ```bash
   kubectl get pods -l app=auth-service
   kubectl describe pod <pod-name>
   kubectl logs <pod-name> --tail=100
   ```

2. **Constitutional Compliance Failures**:

   ```bash
   ./scripts/diagnose_constitutional_issues.sh
   ./scripts/reset_constitutional_state.sh
   ```

3. **Performance Degradation**:
   ```bash
   ./scripts/performance_diagnostics.sh
   ./scripts/scale_service.sh --replicas 5
   ```

### Prototype Service Issues

#### Common Prototype Issues

1. **Mock Component Failures**: Expected behavior, check prototype status
2. **Router Import Issues**: Known limitation, use minimal mode
3. **Debug Mode Active**: Expected for development, not for production

---

**Note**: This guide will be updated as prototype services mature to production status and operational experience is gained.
