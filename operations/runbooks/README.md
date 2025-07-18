# ACGS-2 Operational Runbooks
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive operational runbooks for ACGS-2 (Advanced Constitutional Governance System). This collection provides detailed procedures for operating, maintaining, and troubleshooting the ACGS-2 system while maintaining constitutional compliance and performance requirements.

## Constitutional Requirements

All operational procedures must maintain constitutional hash `cdd01ef066bc6cf2` validation and adhere to:
- **Performance Targets**: P99 <5ms, >100 RPS maintained during all operations
- **Constitutional Compliance**: Hash validation and compliance verification
- **Zero-downtime Operations**: Critical services maintained during procedures
- **Audit Trail**: Complete logging of all operational activities

## Runbook Collection

### Core Operational Runbooks

#### 1. [Incident Response](./incident-response.md)
Comprehensive incident response procedures for handling system outages, performance degradation, and security incidents.

**Key Procedures:**
- Incident detection and classification (SEV-1 through SEV-4)
- Emergency response and containment
- Root cause analysis and investigation
- Recovery and validation procedures
- Post-incident review and documentation

**Constitutional Requirements:**
- SEV-1 incidents: <5 minute response time for constitutional violations
- Constitutional hash validation throughout incident response
- Performance targets maintained during recovery

#### 2. [Deployment Procedures](./deployment-procedures.md)
Step-by-step procedures for deploying, updating, and rolling back ACGS-2 services.

**Key Procedures:**
- New service deployment with constitutional compliance
- Rolling updates and blue-green deployments
- Canary deployments with performance validation
- Emergency hotfix procedures
- Rollback and recovery procedures

**Constitutional Requirements:**
- Zero-downtime deployments for constitutional services
- Constitutional hash validation pre/post deployment
- Performance validation (P99 <5ms, >100 RPS)

#### 3. [Monitoring and Maintenance](./monitoring-maintenance.md)
Daily, weekly, and monthly monitoring and maintenance procedures.

**Key Procedures:**
- Daily health checks and system monitoring
- Performance monitoring and optimization
- Resource management and capacity planning
- Log management and analysis
- Preventive maintenance procedures

**Constitutional Requirements:**
- Continuous constitutional compliance monitoring
- Performance target validation
- Audit trail maintenance

#### 4. [Security Operations](./security-operations.md)
Security monitoring, incident response, and compliance management procedures.

**Key Procedures:**
- Security health checks and monitoring
- Security incident response and threat management
- Compliance auditing and reporting
- Vulnerability management and patching
- Access control and authentication management

**Constitutional Requirements:**
- Constitutional hash security validation
- Zero-trust security model enforcement
- Immediate response to constitutional violations

## Quick Reference Guide

### Emergency Contacts
- **Critical Incidents**: +1-555-ACGS-911
- **Security Team**: security@acgs.local
- **Operations Team**: ops@acgs.local
- **Slack**: #acgs-incidents

### Emergency Procedures

#### Constitutional Violation Response
```bash
# Immediate response to constitutional hash violations
INCIDENT_ID="CONST-$(date +%Y%m%d%H%M%S)"

# 1. Isolate affected services
kubectl patch deployment constitutional-core -n acgs-system --patch '{"spec":{"replicas":1}}'

# 2. Validate constitutional hash
kubectl get pods -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2

# 3. Notify security team
curl -X POST "http://monitoring-service:8014/api/alerts" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d "{\"severity\": \"critical\", \"title\": \"Constitutional Violation\", \"incident_id\": \"$INCIDENT_ID\"}"
```

#### Service Restart Sequence
```bash
# Safe service restart sequence
services=("postgres" "redis" "constitutional-core" "groqcloud-policy" "auth-service" "api-gateway")

for service in "${services[@]}"; do
  kubectl rollout restart deployment/$service -n acgs-system
  kubectl rollout status deployment/$service -n acgs-system --timeout=300s
done
```

#### Performance Emergency Response
```bash
# Emergency performance optimization
kubectl scale deployment constitutional-core -n acgs-system --replicas=5
kubectl scale deployment groqcloud-policy -n acgs-system --replicas=3

# Verify performance recovery
LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/constitutional-core" | jq -r .p99)
echo "P99 Latency: $LATENCY ms"
```

### System Health Check
```bash
#!/bin/bash
# Quick system health check
echo "=== ACGS-2 System Health Check ==="

# 1. Service status
kubectl get pods -n acgs-system

# 2. Constitutional compliance
COMPLIANT=$(kubectl get pods -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2 --no-headers | wc -l)
TOTAL=$(kubectl get pods -n acgs-system --no-headers | wc -l)
echo "Constitutional compliance: $COMPLIANT/$TOTAL"

# 3. Performance metrics
curl -s "http://monitoring-service:8014/api/metrics/health" | jq .

# 4. Recent alerts
curl -s "http://monitoring-service:8014/api/alerts?count=5" | jq .
```

## Operational Procedures

### Daily Operations Checklist
- [ ] Run system health check
- [ ] Verify constitutional compliance
- [ ] Check performance metrics
- [ ] Review overnight alerts
- [ ] Validate backup completion
- [ ] Monitor resource usage
- [ ] Check security status

### Weekly Operations Checklist
- [ ] Perform system maintenance
- [ ] Review performance trends
- [ ] Conduct security audit
- [ ] Update documentation
- [ ] Capacity planning review
- [ ] Disaster recovery test
- [ ] Compliance reporting

### Monthly Operations Checklist
- [ ] Full system backup
- [ ] Security patches and updates
- [ ] Performance optimization
- [ ] Capacity planning
- [ ] Disaster recovery testing
- [ ] Documentation updates
- [ ] Compliance review

## Monitoring and Alerting

### Key Performance Indicators (KPIs)
- **Constitutional Compliance Rate**: >99%
- **System Availability**: >99.9%
- **P99 Latency**: <5ms
- **Throughput**: >100 RPS
- **Error Rate**: <1%
- **Security Incidents**: 0 critical/week

### Alert Categories

#### Critical Alerts (Immediate Response)
- Constitutional hash violations
- System-wide outages
- Security breaches
- Data corruption
- Performance degradation >50%

#### Warning Alerts (15-minute Response)
- Service degradation
- Performance issues
- Authentication failures
- Resource constraints
- Backup failures

#### Info Alerts (1-hour Response)
- Configuration drift
- Capacity warnings
- Non-critical errors
- Maintenance reminders

### Monitoring Dashboards

#### System Overview Dashboard
- Service health status
- Constitutional compliance metrics
- Performance metrics (latency, throughput)
- Resource utilization
- Active alerts

#### Security Dashboard
- Authentication metrics
- Authorization failures
- Security violations
- Threat detection
- Compliance status

#### Performance Dashboard
- Response time trends
- Throughput metrics
- Error rates
- Resource usage
- Bottleneck analysis

## Troubleshooting Guide

### Common Issues and Solutions

#### Pod Stuck in Pending
```bash
# Check resource constraints
kubectl describe pod <pod-name> -n acgs-system
kubectl top nodes

# Solution: Scale down or add nodes
kubectl scale deployment <deployment> -n acgs-system --replicas=1
```

#### Service Unavailable
```bash
# Check service endpoints
kubectl get endpoints -n acgs-system
kubectl get pods -n acgs-system -l app=<service>

# Solution: Restart service
kubectl rollout restart deployment/<service> -n acgs-system
```

#### High Latency
```bash
# Check performance metrics
curl -s "http://monitoring-service:8014/api/metrics/latency/<service>" | jq .

# Solution: Scale service or optimize
kubectl scale deployment <service> -n acgs-system --replicas=5
```

#### Constitutional Hash Violations
```bash
# Check compliance
kubectl get pods -n acgs-system -o jsonpath='{.items[*].metadata.labels.constitutional-hash}'

# Solution: Update pod labels
kubectl patch deployment <service> -n acgs-system --patch '{"spec":{"template":{"metadata":{"labels":{"constitutional-hash":"cdd01ef066bc6cf2"}}}}}'
```

### Escalation Procedures

#### Level 1: Operational Issues
- **Response Time**: 15 minutes
- **Scope**: Service degradation, minor performance issues
- **Actions**: Restart services, scale resources, check logs

#### Level 2: System Issues
- **Response Time**: 5 minutes
- **Scope**: Multiple service failures, major performance issues
- **Actions**: Emergency procedures, system recovery, stakeholder notification

#### Level 3: Critical Issues
- **Response Time**: Immediate
- **Scope**: Constitutional violations, security breaches, system outages
- **Actions**: Emergency response, executive notification, external support

## Documentation and Training

### Required Documentation
- Service architecture diagrams
- Network topology and security policies
- Data flow diagrams
- Backup and recovery procedures
- Disaster recovery plans

### Training Requirements
- **New Team Members**: Complete runbook training within 30 days
- **Existing Team**: Quarterly runbook reviews and updates
- **Emergency Procedures**: Monthly drills and simulations
- **Security Procedures**: Quarterly security training

### Documentation Updates
- **Frequency**: Monthly or after major changes
- **Process**: Technical review, stakeholder approval, team notification
- **Version Control**: Git-based documentation with change tracking
- **Distribution**: Automated notifications to operations team

## Tools and Resources

### Command Line Tools
- `kubectl`: Kubernetes cluster management
- `curl`: API testing and monitoring
- `jq`: JSON processing
- `bc`: Mathematical calculations
- `grep`: Log analysis

### Monitoring Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Jaeger**: Distributed tracing
- **Elasticsearch**: Log aggregation
- **Kibana**: Log analysis

### External Resources
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Istio Documentation**: https://istio.io/docs/
- **Prometheus Documentation**: https://prometheus.io/docs/
- **ACGS-2 Architecture**: [Architecture Documentation](../../docs/architecture/CLAUDE.md)

## Best Practices

### Operational Excellence
- **Automation**: Automate repetitive tasks and procedures
- **Documentation**: Keep runbooks current and comprehensive
- **Training**: Regular team training and knowledge sharing
- **Monitoring**: Proactive monitoring and alerting
- **Testing**: Regular disaster recovery and failover testing

### Constitutional Compliance
- **Validation**: Continuous constitutional hash validation
- **Monitoring**: Real-time compliance monitoring
- **Auditing**: Regular compliance audits and reporting
- **Remediation**: Immediate response to compliance violations

### Performance Management
- **Baselines**: Establish and maintain performance baselines
- **Optimization**: Regular performance tuning and optimization
- **Capacity Planning**: Proactive capacity planning and scaling
- **Testing**: Regular performance testing and validation

### Security Operations
- **Zero Trust**: Implement zero-trust security model
- **Monitoring**: Continuous security monitoring and threat detection
- **Response**: Rapid incident response and remediation
- **Compliance**: Regular security audits and compliance reporting

---

**Navigation**: [Root](../../CLAUDE.md) | [Operations](../README.md) | [Deployment](../../deployment/README.md)

**Constitutional Compliance**: All operational procedures maintain constitutional hash `cdd01ef066bc6cf2` validation and performance targets throughout system operations.

**Last Updated**: 2025-07-18 - Operational runbooks established