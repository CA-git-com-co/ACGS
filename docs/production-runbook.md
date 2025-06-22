# ACGS-1 Lite Production Deployment Runbook

## Overview

This runbook provides comprehensive step-by-step procedures for deploying, operating, and maintaining the ACGS-1 Lite Constitutional Governance System in production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Validation](#environment-validation)
3. [Infrastructure Deployment](#infrastructure-deployment)
4. [Service Deployment](#service-deployment)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Monitoring Setup](#monitoring-setup)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Emergency Response](#emergency-response)
9. [Rollback Procedures](#rollback-procedures)
10. [Disaster Recovery](#disaster-recovery)

---

## Pre-Deployment Checklist

### Prerequisites Verification

- [ ] AWS CLI configured with appropriate permissions
- [ ] kubectl configured for target EKS cluster
- [ ] Terraform v1.0+ installed and configured
- [ ] Docker installed for container operations
- [ ] Helm v3+ installed for chart deployments
- [ ] Access to required AWS services (EKS, RDS, S3, VPC)

### Security Requirements

- [ ] IAM roles and policies created for ACGS-1 Lite services
- [ ] KMS keys created for encryption at rest
- [ ] SSL/TLS certificates obtained for external endpoints
- [ ] Network security groups configured
- [ ] VPC and subnet configurations validated

### Resource Requirements

- [ ] AWS resource quotas sufficient for deployment
- [ ] EKS cluster capacity planned (minimum 3 nodes)
- [ ] Storage requirements calculated (PostgreSQL, monitoring data)
- [ ] Network bandwidth requirements validated
- [ ] Cost estimates approved

### Configuration Validation

- [ ] Environment-specific variables configured
- [ ] Constitutional policies reviewed and approved
- [ ] Monitoring thresholds and alerting rules validated
- [ ] Backup and retention policies defined
- [ ] Emergency contact information updated

---

## Environment Validation

### Step 1: Validate AWS Environment

```bash
# Verify AWS credentials and permissions
aws sts get-caller-identity

# Check AWS service availability in target region
aws ec2 describe-availability-zones --region us-east-1

# Validate EKS service availability
aws eks list-clusters --region us-east-1
```

### Step 2: Validate Terraform State

```bash
# Initialize Terraform backend
cd infrastructure/terraform
terraform init

# Validate Terraform configuration
terraform validate

# Plan infrastructure changes
terraform plan -var-file=environments/production.tfvars
```

### Step 3: Validate Kubernetes Access

```bash
# Test kubectl connectivity
kubectl cluster-info

# Verify node readiness
kubectl get nodes

# Check available storage classes
kubectl get storageclass
```

### Step 4: Validate Container Registry Access

```bash
# Login to ECR (or your container registry)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Verify image availability
docker pull <account-id>.dkr.ecr.us-east-1.amazonaws.com/acgs-lite/policy-engine:latest
docker pull <account-id>.dkr.ecr.us-east-1.amazonaws.com/acgs-lite/sandbox-controller:latest
```

---

## Infrastructure Deployment

### Step 1: Deploy Core Infrastructure

```bash
cd infrastructure/terraform

# Apply Terraform configuration
terraform apply -var-file=environments/production.tfvars -auto-approve

# Verify infrastructure deployment
terraform output
```

**Expected Outputs:**

- EKS cluster endpoint
- RDS endpoint
- Redis endpoint
- S3 bucket names
- VPC and subnet IDs

### Step 2: Configure kubectl for EKS

```bash
# Update kubeconfig for new EKS cluster
aws eks update-kubeconfig --region us-east-1 --name acgs-lite-production

# Verify cluster access
kubectl get nodes
kubectl get namespaces
```

### Step 3: Install Required Operators

```bash
# Install CloudNativePG operator for PostgreSQL
kubectl apply -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.20/releases/cnpg-1.20.0.yaml

# Install RedPanda operator
kubectl apply -f https://github.com/redpanda-data/redpanda/releases/latest/download/redpanda-operator-crd.yaml
kubectl apply -f https://github.com/redpanda-data/redpanda/releases/latest/download/redpanda-operator.yaml

# Install Prometheus operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus-operator prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

### Step 4: Verify Infrastructure Health

```bash
# Check all pods are running
kubectl get pods --all-namespaces

# Verify persistent volumes
kubectl get pv,pvc --all-namespaces

# Check service endpoints
kubectl get svc --all-namespaces
```

---

## Service Deployment

### Step 1: Create Namespaces and RBAC

```bash
# Apply namespace configuration
kubectl apply -f infrastructure/kubernetes/acgs-lite/namespaces.yaml

# Apply RBAC configuration
kubectl apply -f infrastructure/kubernetes/acgs-lite/rbac.yaml

# Apply security policies
kubectl apply -f infrastructure/kubernetes/acgs-lite/security-policies.yaml

# Apply network policies
kubectl apply -f infrastructure/kubernetes/acgs-lite/network-policies.yaml
```

### Step 2: Deploy Database Infrastructure

```bash
# Deploy PostgreSQL HA cluster
kubectl apply -f infrastructure/kubernetes/acgs-lite/postgresql-ha.yaml

# Wait for PostgreSQL cluster to be ready
kubectl wait --for=condition=Ready cluster/constitutional-postgres -n shared --timeout=600s

# Initialize database schema
kubectl apply -f infrastructure/kubernetes/acgs-lite/database-init.yaml

# Verify database initialization
kubectl logs job/acgs-lite-db-init -n shared
```

### Step 3: Deploy Event Streaming

```bash
# Deploy RedPanda cluster
kubectl apply -f infrastructure/kubernetes/acgs-lite/redpanda-cluster.yaml

# Wait for RedPanda to be ready
kubectl wait --for=condition=Ready redpanda/constitutional-events -n shared --timeout=600s

# Apply event streaming configuration
kubectl apply -f infrastructure/kubernetes/acgs-lite/event-streaming-config.yaml

# Verify topic creation
kubectl logs job/redpanda-topic-setup -n shared
```

### Step 4: Deploy Core Services

```bash
# Deploy Policy Engine with OPA
kubectl apply -f infrastructure/kubernetes/acgs-lite/policy-engine.yaml

# Wait for Policy Engine to be ready
kubectl wait --for=condition=Available deployment/policy-engine -n governance --timeout=300s
kubectl wait --for=condition=Available deployment/opa -n governance --timeout=300s

# Deploy Sandbox Controller
kubectl apply -f infrastructure/kubernetes/acgs-lite/sandbox-controller.yaml

# Wait for Sandbox Controller to be ready
kubectl wait --for=condition=Available deployment/sandbox-controller -n workload --timeout=300s
```

### Step 5: Deploy Monitoring Stack

```bash
# Deploy Prometheus configuration
kubectl apply -f infrastructure/kubernetes/acgs-lite/monitoring.yaml

# Deploy Grafana
kubectl apply -f infrastructure/kubernetes/acgs-lite/grafana.yaml

# Deploy AlertManager
kubectl apply -f infrastructure/kubernetes/acgs-lite/alertmanager.yaml

# Wait for monitoring stack to be ready
kubectl wait --for=condition=Available deployment/prometheus -n monitoring --timeout=300s
kubectl wait --for=condition=Available deployment/grafana -n monitoring --timeout=300s
kubectl wait --for=condition=Available deployment/alertmanager -n monitoring --timeout=300s
```

---

## Post-Deployment Verification

### Step 1: Service Health Checks

```bash
# Check all deployments are ready
kubectl get deployments --all-namespaces

# Verify service endpoints
kubectl get services --all-namespaces

# Check pod status and logs
kubectl get pods --all-namespaces
kubectl logs -l app=policy-engine -n governance --tail=50
kubectl logs -l app=sandbox-controller -n workload --tail=50
```

### Step 2: Database Connectivity

```bash
# Test PostgreSQL connectivity
kubectl exec -it constitutional-postgres-1 -n shared -- psql -U postgres -d acgs_lite -c "SELECT COUNT(*) FROM constitutional_policies;"

# Verify database schema
kubectl exec -it constitutional-postgres-1 -n shared -- psql -U postgres -d acgs_lite -c "\dt"
```

### Step 3: Event Streaming Verification

```bash
# Check RedPanda cluster status
kubectl exec -it constitutional-events-0 -n shared -- rpk cluster info

# List topics
kubectl exec -it constitutional-events-0 -n shared -- rpk topic list

# Test topic connectivity
kubectl exec -it constitutional-events-0 -n shared -- rpk topic produce constitutional.events --key test --value "test message"
```

### Step 4: Policy Engine Testing

```bash
# Test Policy Engine health endpoint
kubectl port-forward svc/policy-engine 8001:8001 -n governance &
curl http://localhost:8001/health

# Test policy evaluation
curl -X POST http://localhost:8001/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "action": "evolve_agent",
    "agent_id": "test-agent",
    "input_data": {
      "fitness_improvement": 0.06,
      "safety_score": 0.96,
      "constitutional_compliance": 0.995
    }
  }'
```

### Step 5: Monitoring Verification

```bash
# Access Grafana dashboard
kubectl port-forward svc/grafana 3000:3000 -n monitoring &
# Open http://localhost:3000 (admin/acgs-lite-admin)

# Check Prometheus targets
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
# Open http://localhost:9090/targets

# Verify AlertManager
kubectl port-forward svc/alertmanager 9093:9093 -n monitoring &
# Open http://localhost:9093
```

---

## Monitoring Setup

### Step 1: Configure Dashboards

1. **Access Grafana**: http://localhost:3000
2. **Login**: admin / acgs-lite-admin
3. **Import Dashboards**:
   - ACGS-1 Lite Constitutional Health Overview
   - Constitutional Violations Dashboard
   - System Performance Dashboard

### Step 2: Validate Metrics Collection

```bash
# Check Prometheus metrics
curl http://localhost:9090/api/v1/query?query=policy_evaluations_total

# Verify constitutional compliance metrics
curl http://localhost:9090/api/v1/query?query=constitutional_compliance_rate

# Check sandbox metrics
curl http://localhost:9090/api/v1/query?query=sandbox_executions_total
```

### Step 3: Test Alerting

```bash
# Trigger test alert (simulate high latency)
kubectl exec -it deployment/policy-engine -n governance -- curl -X POST http://localhost:8001/test/high-latency

# Check AlertManager for fired alerts
curl http://localhost:9093/api/v1/alerts
```

### Step 4: Configure Notification Channels

1. **Slack Integration**: Update AlertManager config with Slack webhook
2. **PagerDuty Integration**: Configure PagerDuty service keys
3. **Email Notifications**: Set up SMTP configuration

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Policy Engine Not Starting

**Symptoms**: Policy Engine pods in CrashLoopBackOff
**Diagnosis**:

```bash
kubectl logs deployment/policy-engine -n governance
kubectl describe pod -l app=policy-engine -n governance
```

**Solutions**:

1. Check OPA connectivity: `kubectl logs deployment/opa -n governance`
2. Verify Redis connectivity: `kubectl get svc redis -n shared`
3. Check resource limits: `kubectl describe deployment/policy-engine -n governance`

#### Issue: Database Connection Failures

**Symptoms**: Services cannot connect to PostgreSQL
**Diagnosis**:

```bash
kubectl logs constitutional-postgres-1 -n shared
kubectl get cluster constitutional-postgres -n shared -o yaml
```

**Solutions**:

1. Check PostgreSQL cluster status: `kubectl get cluster -n shared`
2. Verify network policies: `kubectl get networkpolicy -n shared`
3. Check secrets: `kubectl get secret constitutional-postgres-app -n shared`

#### Issue: High Policy Evaluation Latency

**Symptoms**: Policy evaluations taking >5ms
**Diagnosis**:

```bash
# Check Prometheus metrics
curl http://localhost:9090/api/v1/query?query=histogram_quantile(0.99,rate(policy_evaluation_duration_seconds_bucket[5m]))
```

**Solutions**:

1. Scale Policy Engine: `kubectl scale deployment/policy-engine --replicas=5 -n governance`
2. Check Redis cache hit rate: Monitor cache_hit_rate metric
3. Optimize OPA policies: Review Rego policy complexity

#### Issue: Sandbox Escape Detection False Positives

**Symptoms**: Legitimate operations flagged as violations
**Diagnosis**:

```bash
kubectl logs deployment/sandbox-controller -n workload | grep "violation"
```

**Solutions**:

1. Review violation patterns in sandbox controller configuration
2. Adjust detection thresholds
3. Update whitelist for legitimate operations

---

## Emergency Response

### Constitutional Violation Response

#### Critical Alert: Sandbox Escape Attempt

**Immediate Actions (0-5 minutes)**:

1. **Verify Alert**: Check AlertManager and Grafana dashboards
2. **Isolate Affected Agent**:
   ```bash
   kubectl delete pod -l agent-id=<affected-agent> -n workload
   ```
3. **Capture Forensics**:
   ```bash
   kubectl logs -l agent-id=<affected-agent> -n workload > forensics-$(date +%Y%m%d-%H%M%S).log
   ```

**Investigation Actions (5-30 minutes)**:

1. **Review Audit Trail**:
   ```bash
   kubectl exec -it constitutional-postgres-1 -n shared -- psql -U postgres -d acgs_lite -c "SELECT * FROM sandbox_violations WHERE agent_id='<affected-agent>' ORDER BY created_at DESC LIMIT 10;"
   ```
2. **Analyze Violation Patterns**:
   ```bash
   kubectl logs deployment/sandbox-controller -n workload | grep -A 10 -B 10 "<affected-agent>"
   ```

#### Critical Alert: Constitutional Compliance Rate Drop

**Immediate Actions**:

1. **Check Policy Engine Health**:
   ```bash
   kubectl get pods -l app=policy-engine -n governance
   curl http://localhost:8001/health
   ```
2. **Review Recent Policy Changes**:
   ```bash
   kubectl exec -it constitutional-postgres-1 -n shared -- psql -U postgres -d acgs_lite -c "SELECT * FROM constitutional_policies WHERE updated_at > NOW() - INTERVAL '1 hour';"
   ```

### System-Wide Emergency Procedures

#### Emergency Shutdown

```bash
# Scale down all ACGS services
kubectl scale deployment/policy-engine --replicas=0 -n governance
kubectl scale deployment/sandbox-controller --replicas=0 -n workload

# Prevent new agent executions
kubectl patch networkpolicy default-deny-all -n workload -p '{"spec":{"policyTypes":["Ingress","Egress"],"podSelector":{},"ingress":[],"egress":[]}}'
```

#### Emergency Recovery

```bash
# Restore from last known good configuration
kubectl apply -f infrastructure/kubernetes/acgs-lite/

# Verify system health
kubectl get pods --all-namespaces
curl http://localhost:8001/health
```

---

## Rollback Procedures

### Service Rollback

```bash
# Rollback Policy Engine deployment
kubectl rollout undo deployment/policy-engine -n governance

# Rollback Sandbox Controller deployment
kubectl rollout undo deployment/sandbox-controller -n workload

# Verify rollback status
kubectl rollout status deployment/policy-engine -n governance
kubectl rollout status deployment/sandbox-controller -n workload
```

### Database Rollback

```bash
# Restore from point-in-time backup
kubectl apply -f - <<EOF
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: constitutional-postgres-restore
  namespace: shared
spec:
  instances: 3
  bootstrap:
    recovery:
      source: constitutional-postgres
      recoveryTargetTime: "2024-01-01 12:00:00"
EOF
```

### Infrastructure Rollback

```bash
cd infrastructure/terraform

# Revert to previous Terraform state
terraform state pull > current-state.json
terraform state push previous-state.json

# Apply previous configuration
terraform apply -var-file=environments/production.tfvars
```

---

## Disaster Recovery

### Backup Verification

```bash
# Check PostgreSQL backups
kubectl get backup -n shared

# Verify S3 backup integrity
aws s3 ls s3://acgs-lite-production-backups/ --recursive

# Test backup restoration
kubectl apply -f infrastructure/kubernetes/acgs-lite/backup-test.yaml
```

### Recovery Time Objectives (RTO)

- **Policy Engine**: 5 minutes
- **Sandbox Controller**: 5 minutes
- **Database**: 15 minutes
- **Full System**: 30 minutes

### Recovery Point Objectives (RPO)

- **Configuration Data**: 0 (stored in Git)
- **Audit Data**: 5 minutes (continuous backup)
- **Metrics Data**: 15 minutes (acceptable loss)

### Cross-Region Disaster Recovery

```bash
# Replicate to DR region
aws s3 sync s3://acgs-lite-production-backups/ s3://acgs-lite-dr-backups/ --region us-west-2

# Deploy to DR region
cd infrastructure/terraform
terraform workspace select dr
terraform apply -var-file=environments/dr.tfvars
```

---

## Maintenance Procedures

### Regular Maintenance Tasks

#### Weekly Tasks

- [ ] Review system performance metrics
- [ ] Check backup integrity
- [ ] Update security patches
- [ ] Review audit logs for anomalies

#### Monthly Tasks

- [ ] Update container images
- [ ] Review and update constitutional policies
- [ ] Capacity planning review
- [ ] Disaster recovery testing

#### Quarterly Tasks

- [ ] Security audit and penetration testing
- [ ] Performance optimization review
- [ ] Documentation updates
- [ ] Team training and runbook updates

---

## Contact Information

### Emergency Contacts

- **On-Call Engineer**: +1-XXX-XXX-XXXX
- **Security Team**: security@company.com
- **Platform Team**: platform@company.com

### Escalation Matrix

1. **Level 1**: On-call engineer (0-15 minutes)
2. **Level 2**: Senior engineer + security team (15-30 minutes)
3. **Level 3**: Engineering manager + CISO (30+ minutes)

---

## Appendix

### Useful Commands Reference

```bash
# Quick health check
kubectl get pods --all-namespaces | grep -v Running

# View recent events
kubectl get events --sort-by=.metadata.creationTimestamp

# Check resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Emergency logs collection
kubectl logs --all-containers=true --since=1h -l app.kubernetes.io/name=acgs-lite > emergency-logs.txt
```

### Configuration Files Location

- **Terraform**: `infrastructure/terraform/`
- **Kubernetes**: `infrastructure/kubernetes/acgs-lite/`
- **Monitoring**: `infrastructure/kubernetes/acgs-lite/monitoring.yaml`
- **Policies**: `infrastructure/kubernetes/acgs-lite/policy-engine.yaml`

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-01  
**Next Review**: 2024-04-01
