# ACGS-1 Lite Operational Checklist

## Pre-Deployment Checklist

### Environment Preparation

- [ ] AWS credentials configured and tested
- [ ] kubectl configured for target EKS cluster
- [ ] Terraform v1.0+ installed and validated
- [ ] Docker installed and registry access verified
- [ ] Helm v3+ installed and repositories added
- [ ] Required AWS service quotas verified
- [ ] SSL/TLS certificates obtained and validated
- [ ] DNS records prepared for external endpoints

### Security Validation

- [ ] IAM roles and policies created and tested
- [ ] KMS keys created for encryption at rest
- [ ] Network security groups configured
- [ ] VPC and subnet configurations validated
- [ ] Container images scanned for vulnerabilities
- [ ] Secrets management strategy implemented
- [ ] Network policies reviewed and approved
- [ ] RBAC configurations validated

### Configuration Review

- [ ] Environment-specific variables configured
- [ ] Constitutional policies reviewed and approved
- [ ] Monitoring thresholds validated
- [ ] Alerting rules configured and tested
- [ ] Backup and retention policies defined
- [ ] Emergency contact information updated
- [ ] Runbook procedures reviewed by team

---

## Deployment Checklist

### Infrastructure Deployment

- [ ] Terraform plan reviewed and approved
- [ ] Infrastructure deployed successfully
- [ ] EKS cluster accessible via kubectl
- [ ] Node groups healthy and ready
- [ ] Storage classes available
- [ ] Load balancers configured
- [ ] DNS resolution working

### Operator Installation

- [ ] CloudNativePG operator installed
- [ ] RedPanda operator installed
- [ ] Prometheus operator installed
- [ ] All operators healthy and ready
- [ ] CRDs properly registered
- [ ] Operator permissions validated

### Service Deployment

- [ ] Namespaces created successfully
- [ ] RBAC configurations applied
- [ ] Security policies enforced
- [ ] Network policies active
- [ ] PostgreSQL HA cluster deployed
- [ ] Database schema initialized
- [ ] RedPanda cluster deployed
- [ ] Event topics created
- [ ] Policy Engine deployed
- [ ] OPA policies loaded
- [ ] Sandbox Controller deployed
- [ ] Monitoring stack deployed

### Post-Deployment Validation

- [ ] All deployments showing ready status
- [ ] Service endpoints accessible
- [ ] Health checks passing
- [ ] Database connectivity verified
- [ ] Event streaming functional
- [ ] Policy evaluation working
- [ ] Sandbox execution tested
- [ ] Monitoring data flowing
- [ ] Alerts configured and firing tests passed

---

## Daily Operations Checklist

### Morning Health Check (Start of Business)

- [ ] Run comprehensive health check script
- [ ] Review overnight alerts and incidents
- [ ] Check system resource utilization
- [ ] Verify constitutional compliance metrics
- [ ] Review audit logs for anomalies
- [ ] Check backup completion status
- [ ] Validate monitoring dashboard functionality
- [ ] Review policy evaluation performance

### System Monitoring

- [ ] Constitutional compliance rate >99%
- [ ] Policy evaluation latency <5ms P99
- [ ] No active sandbox escape attempts
- [ ] Database performance within thresholds
- [ ] Event streaming lag minimal
- [ ] No critical alerts firing
- [ ] Resource utilization normal
- [ ] All services healthy

### Security Validation

- [ ] No unauthorized access attempts
- [ ] Network policies enforcing correctly
- [ ] RBAC permissions working as expected
- [ ] Container security scans clean
- [ ] Audit trail integrity verified
- [ ] Encryption at rest functioning
- [ ] Certificate expiration dates checked

### End of Day Review

- [ ] Review day's constitutional violations
- [ ] Check human review queue status
- [ ] Verify backup completion
- [ ] Review performance trends
- [ ] Update incident log if applicable
- [ ] Prepare handoff notes for next shift

---

## Weekly Maintenance Checklist

### Performance Review

- [ ] Analyze policy evaluation latency trends
- [ ] Review constitutional compliance patterns
- [ ] Check resource utilization trends
- [ ] Identify performance optimization opportunities
- [ ] Review capacity planning metrics
- [ ] Update performance baselines

### Security Audit

- [ ] Review access logs and patterns
- [ ] Validate security policy effectiveness
- [ ] Check for new vulnerability reports
- [ ] Update security scanning rules
- [ ] Review incident response procedures
- [ ] Test emergency response procedures

### System Updates

- [ ] Review available security patches
- [ ] Plan container image updates
- [ ] Check for operator updates
- [ ] Review Kubernetes version compatibility
- [ ] Plan maintenance windows
- [ ] Prepare rollback procedures

### Documentation Updates

- [ ] Update operational procedures
- [ ] Review and update contact information
- [ ] Update troubleshooting guides
- [ ] Review emergency procedures
- [ ] Update configuration documentation

---

## Monthly Maintenance Checklist

### Comprehensive System Review

- [ ] Full security audit and penetration testing
- [ ] Performance optimization review
- [ ] Capacity planning assessment
- [ ] Disaster recovery testing
- [ ] Backup and restore testing
- [ ] Documentation review and updates

### Policy and Configuration Review

- [ ] Review constitutional policies for updates
- [ ] Validate monitoring thresholds
- [ ] Review alerting rules effectiveness
- [ ] Update emergency contact information
- [ ] Review and update SLAs/SLOs
- [ ] Validate compliance requirements

### Team and Process Review

- [ ] Conduct team training sessions
- [ ] Review incident response procedures
- [ ] Update on-call procedures
- [ ] Review escalation processes
- [ ] Conduct tabletop exercises
- [ ] Update knowledge base

---

## Incident Response Checklist

### Immediate Response (0-5 minutes)

- [ ] Acknowledge alert and assess severity
- [ ] Determine if emergency shutdown needed
- [ ] Notify appropriate team members
- [ ] Begin incident documentation
- [ ] Implement immediate containment if required

### Investigation (5-30 minutes)

- [ ] Collect system diagnostics
- [ ] Review recent changes and deployments
- [ ] Analyze logs and metrics
- [ ] Identify root cause
- [ ] Determine remediation steps

### Resolution (30+ minutes)

- [ ] Implement fix or workaround
- [ ] Verify system stability
- [ ] Update stakeholders on status
- [ ] Document resolution steps
- [ ] Plan follow-up actions

### Post-Incident (24-48 hours)

- [ ] Conduct post-incident review
- [ ] Document lessons learned
- [ ] Update procedures if needed
- [ ] Implement preventive measures
- [ ] Update monitoring and alerting

---

## Emergency Procedures Checklist

### Constitutional Violation Response

- [ ] Identify violation type and severity
- [ ] Implement immediate containment
- [ ] Capture forensic evidence
- [ ] Escalate to appropriate personnel
- [ ] Document incident details
- [ ] Implement corrective measures

### Sandbox Escape Response

- [ ] Immediately terminate affected agent
- [ ] Capture forensic snapshots
- [ ] Block agent from future execution
- [ ] Analyze escape vectors
- [ ] Update detection rules
- [ ] Report to security team

### System Emergency Response

- [ ] Assess system-wide impact
- [ ] Implement emergency procedures
- [ ] Scale resources if needed
- [ ] Activate disaster recovery if required
- [ ] Communicate with stakeholders
- [ ] Document emergency actions

---

## Rollback Procedures Checklist

### Pre-Rollback

- [ ] Create backup of current state
- [ ] Identify rollback target version
- [ ] Notify stakeholders of rollback
- [ ] Prepare rollback commands
- [ ] Verify rollback procedures

### During Rollback

- [ ] Execute rollback in correct order
- [ ] Monitor system during rollback
- [ ] Verify each step completion
- [ ] Check for any errors or issues
- [ ] Document rollback progress

### Post-Rollback

- [ ] Verify system functionality
- [ ] Run health checks
- [ ] Test critical workflows
- [ ] Update monitoring dashboards
- [ ] Document rollback completion
- [ ] Conduct post-rollback review

---

## Disaster Recovery Checklist

### Preparation

- [ ] Verify backup integrity
- [ ] Check DR site readiness
- [ ] Validate recovery procedures
- [ ] Confirm team availability
- [ ] Prepare communication plan

### Activation

- [ ] Declare disaster recovery
- [ ] Activate DR site
- [ ] Restore from backups
- [ ] Redirect traffic to DR site
- [ ] Verify system functionality

### Recovery

- [ ] Monitor DR site performance
- [ ] Coordinate with primary site recovery
- [ ] Plan failback procedures
- [ ] Document recovery process
- [ ] Conduct lessons learned session

---

## Compliance and Audit Checklist

### Regular Compliance Checks

- [ ] Verify constitutional compliance metrics
- [ ] Review audit trail integrity
- [ ] Check data retention compliance
- [ ] Validate access controls
- [ ] Review security configurations

### Audit Preparation

- [ ] Gather required documentation
- [ ] Prepare system access for auditors
- [ ] Review compliance evidence
- [ ] Prepare compliance reports
- [ ] Schedule audit meetings

### Post-Audit

- [ ] Address audit findings
- [ ] Implement recommended changes
- [ ] Update compliance procedures
- [ ] Schedule follow-up reviews
- [ ] Document compliance improvements

---

## Contact Information

### Emergency Contacts

- **On-Call Engineer**: +1-XXX-XXX-XXXX
- **Security Team**: security@company.com
- **Platform Team**: platform@company.com
- **Management**: management@company.com

### Escalation Procedures

1. **Level 1**: On-call engineer (0-15 minutes)
2. **Level 2**: Senior engineer + security team (15-30 minutes)
3. **Level 3**: Engineering manager + CISO (30+ minutes)

### External Contacts

- **AWS Support**: [Support Case URL]
- **Vendor Support**: [Vendor Contact Information]
- **Legal/Compliance**: legal@company.com

---

## Useful Commands Quick Reference

### Health Checks

```bash
# Run comprehensive health check
./scripts/health-check.sh

# Check specific service health
kubectl get pods -n governance
curl http://localhost:8001/health
```

### Emergency Response

```bash
# Emergency shutdown
./scripts/emergency-response.sh shutdown

# Handle sandbox escape
./scripts/emergency-response.sh sandbox-escape <agent_id>

# Collect diagnostics
./scripts/emergency-response.sh diagnostics <incident_id>
```

### Rollback Procedures

```bash
# Rollback all services
./scripts/rollback.sh all

# Rollback specific service
./scripts/rollback.sh service policy-engine

# Emergency rollback
./scripts/rollback.sh emergency
```

### Monitoring

```bash
# Port forward to monitoring services
kubectl port-forward svc/grafana 3000:3000 -n monitoring
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
kubectl port-forward svc/alertmanager 9093:9093 -n monitoring
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-01  
**Next Review**: 2024-02-01
