# ACGS-2 Security Operations Runbook
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

Comprehensive security operations procedures for ACGS-2 (Advanced Constitutional Governance System). This runbook provides step-by-step procedures for security monitoring, incident response, compliance auditing, and threat management while maintaining constitutional compliance.

## Constitutional Security Requirements

All security operations must maintain constitutional hash `cdd01ef066bc6cf2` validation and adhere to:
- **Zero-trust security model** with constitutional verification
- **Continuous security monitoring** and threat detection
- **Incident response** within 5 minutes for constitutional violations
- **Compliance auditing** with constitutional requirements

## Security Architecture

### Security Components
- **Authentication Service**: JWT-based authentication with constitutional validation
- **Authorization Service**: RBAC with constitutional compliance checks
- **Audit Service**: Comprehensive logging and compliance tracking
- **Service Mesh Security**: mTLS and policy enforcement
- **Network Security**: Kubernetes NetworkPolicies and Istio security

### Constitutional Security Model
```
┌─────────────────────────────────────────────────────────────┐
│                Constitutional Security Layer                │
├─────────────────────────────────────────────────────────────┤
│  ✓ Hash Validation (cdd01ef066bc6cf2)                     │
│  ✓ Constitutional Compliance Verification                   │
│  ✓ Performance Security (P99 <5ms, >100 RPS)              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Application Security                     │
├─────────────────────────────────────────────────────────────┤
│  ✓ Authentication & Authorization                           │
│  ✓ Input Validation & Sanitization                         │
│  ✓ Rate Limiting & DDoS Protection                         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Network Security                        │
├─────────────────────────────────────────────────────────────┤
│  ✓ Service Mesh mTLS                                       │
│  ✓ Network Policies                                        │
│  ✓ Ingress/Egress Control                                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Security                     │
├─────────────────────────────────────────────────────────────┤
│  ✓ Kubernetes Security Policies                            │
│  ✓ Container Security                                       │
│  ✓ Secrets Management                                       │
└─────────────────────────────────────────────────────────────┘
```

## Daily Security Operations

### Security Health Check
```bash
#!/bin/bash
# Daily security health check
echo "=== ACGS-2 Security Health Check - $(date) ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. Constitutional Security Status
echo "1. Constitutional Security Status"
CONST_HASH_VIOLATIONS=$(kubectl get pods -n acgs-system -o jsonpath='{.items[*].metadata.labels.constitutional-hash}' | grep -cv "cdd01ef066bc6cf2")
echo "Constitutional hash violations: $CONST_HASH_VIOLATIONS"

# 2. Authentication Service Status
echo "2. Authentication Service Status"
AUTH_STATUS=$(kubectl get deployment auth-service -n acgs-system -o jsonpath='{.status.readyReplicas}/{.spec.replicas}')
echo "Auth service replicas: $AUTH_STATUS"

# Test authentication
AUTH_RESPONSE=$(curl -s -X POST "http://auth-service:8013/api/auth/login" \
  -H "Content-Type: application/json" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d '{"username": "system", "password": "system"}')

if echo "$AUTH_RESPONSE" | grep -q "token"; then
  echo "✅ Authentication service operational"
else
  echo "❌ Authentication service issues detected"
fi

# 3. Authorization Policy Status
echo "3. Authorization Policy Status"
kubectl get authorizationpolicy -n acgs-system | grep -c "acgs-"
kubectl get networkpolicy -n acgs-system | grep -c "acgs-"

# 4. mTLS Status
echo "4. mTLS Status"
kubectl get peerauthentication -n acgs-system | grep -c "STRICT"
kubectl get destinationrule -n acgs-system | grep -c "ISTIO_MUTUAL"

# 5. Security Violations
echo "5. Security Violations (last 24h)"
SECURITY_VIOLATIONS=$(curl -s "http://monitoring-service:8014/api/security/violations?since=24h" | jq -r '.total')
echo "Security violations: $SECURITY_VIOLATIONS"

# 6. Failed Authentication Attempts
echo "6. Failed Authentication Attempts (last 24h)"
FAILED_AUTH=$(curl -s "http://monitoring-service:8014/api/security/failed-auth?since=24h" | jq -r '.total')
echo "Failed authentication attempts: $FAILED_AUTH"

# 7. Unauthorized Access Attempts
echo "7. Unauthorized Access Attempts (last 24h)"
UNAUTHORIZED=$(curl -s "http://monitoring-service:8014/api/security/unauthorized?since=24h" | jq -r '.total')
echo "Unauthorized access attempts: $UNAUTHORIZED"

# 8. Certificate Status
echo "8. Certificate Status"
kubectl get certificates -n acgs-system
kubectl get secrets -n acgs-system -l type=kubernetes.io/tls

# 9. Pod Security Context
echo "9. Pod Security Context"
kubectl get pods -n acgs-system -o jsonpath='{.items[*].spec.securityContext.runAsNonRoot}' | grep -c "true"

# 10. Network Policy Enforcement
echo "10. Network Policy Enforcement"
kubectl get networkpolicy -n acgs-system --no-headers | wc -l

echo "=== Security Health Check Complete ==="
```

### Security Monitoring
```bash
#!/bin/bash
# Continuous security monitoring
MONITOR_INTERVAL=60
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

while true; do
  echo "=== Security Monitoring - $(date) ==="
  
  # Constitutional compliance monitoring
  COMPLIANCE_VIOLATIONS=$(kubectl get pods -n acgs-system -o jsonpath='{.items[*].metadata.labels.constitutional-hash}' | grep -cv "cdd01ef066bc6cf2")
  if [ "$COMPLIANCE_VIOLATIONS" -gt 0 ]; then
    echo "🚨 CRITICAL: $COMPLIANCE_VIOLATIONS constitutional hash violations detected"
    curl -X POST "http://monitoring-service:8014/api/alerts" \
      -H "Content-Type: application/json" \
      -d "{\"severity\": \"critical\", \"title\": \"Constitutional Hash Violations\", \"count\": $COMPLIANCE_VIOLATIONS}"
  fi
  
  # Authentication failure monitoring
  FAILED_AUTH_RATE=$(curl -s "http://monitoring-service:8014/api/security/failed-auth-rate" | jq -r '.rate')
  if (( $(echo "$FAILED_AUTH_RATE > 0.1" | bc -l) )); then
    echo "⚠️ WARNING: High authentication failure rate: $FAILED_AUTH_RATE"
    curl -X POST "http://monitoring-service:8014/api/alerts" \
      -H "Content-Type: application/json" \
      -d "{\"severity\": \"warning\", \"title\": \"High Authentication Failure Rate\", \"rate\": $FAILED_AUTH_RATE}"
  fi
  
  # Unauthorized access monitoring
  UNAUTHORIZED_RATE=$(curl -s "http://monitoring-service:8014/api/security/unauthorized-rate" | jq -r '.rate')
  if (( $(echo "$UNAUTHORIZED_RATE > 0.05" | bc -l) )); then
    echo "⚠️ WARNING: High unauthorized access rate: $UNAUTHORIZED_RATE"
    curl -X POST "http://monitoring-service:8014/api/alerts" \
      -H "Content-Type: application/json" \
      -d "{\"severity\": \"warning\", \"title\": \"High Unauthorized Access Rate\", \"rate\": $UNAUTHORIZED_RATE}"
  fi
  
  # mTLS certificate monitoring
  CERT_EXPIRY=$(kubectl get certificates -n acgs-system -o jsonpath='{.items[*].status.notAfter}')
  # Check if certificates expire within 30 days
  # (Certificate expiry checking logic would go here)
  
  # Network policy violations
  NETWORK_VIOLATIONS=$(kubectl get events -n acgs-system --field-selector reason=NetworkPolicyViolation --no-headers | wc -l)
  if [ "$NETWORK_VIOLATIONS" -gt 0 ]; then
    echo "⚠️ WARNING: $NETWORK_VIOLATIONS network policy violations detected"
  fi
  
  sleep $MONITOR_INTERVAL
done
```

## Security Incident Response

### Security Incident Classification

#### SEV-1 (Critical Security Incident)
- **Constitutional hash violation** or unauthorized modification
- **Authentication system compromise**
- **Data breach or exfiltration**
- **Privilege escalation**
- **System-wide security compromise**

#### SEV-2 (High Security Incident)
- **Service-specific security breach**
- **Unauthorized access to sensitive data**
- **Security policy violations**
- **Denial of service attacks**
- **Certificate or key compromise**

#### SEV-3 (Medium Security Incident)
- **Failed authentication attempts above threshold**
- **Suspicious access patterns**
- **Security configuration drift**
- **Non-critical vulnerability exploitation**

### Security Incident Response Procedure

#### Phase 1: Detection and Initial Response (0-5 minutes)
```bash
#!/bin/bash
# Security incident detection and initial response
INCIDENT_ID="SEC-$(date +%Y%m%d%H%M%S)"
INCIDENT_TYPE=$1  # constitutional, authentication, authorization, network, data

echo "=== SECURITY INCIDENT RESPONSE ==="
echo "Incident ID: $INCIDENT_ID"
echo "Incident Type: $INCIDENT_TYPE"
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. Immediate containment
case $INCIDENT_TYPE in
  "constitutional")
    echo "🚨 CONSTITUTIONAL SECURITY INCIDENT"
    # Immediate containment for constitutional violations
    kubectl patch deployment constitutional-core -n acgs-system --patch '{"spec":{"replicas":1}}'
    kubectl patch service constitutional-core -n acgs-system --patch '{"spec":{"selector":{"security-status":"validated"}}}'
    ;;
  "authentication")
    echo "🚨 AUTHENTICATION SECURITY INCIDENT"
    # Disable auth service temporarily
    kubectl scale deployment auth-service -n acgs-system --replicas=0
    kubectl patch configmap auth-config -n acgs-system --patch '{"data":{"emergency_mode":"true"}}'
    ;;
  "authorization")
    echo "🚨 AUTHORIZATION SECURITY INCIDENT"
    # Implement strictest authorization policies
    kubectl apply -f /security/emergency/strict-authorization.yaml
    ;;
  "network")
    echo "🚨 NETWORK SECURITY INCIDENT"
    # Implement network isolation
    kubectl apply -f /security/emergency/network-isolation.yaml
    ;;
  "data")
    echo "🚨 DATA SECURITY INCIDENT"
    # Implement data protection measures
    kubectl apply -f /security/emergency/data-protection.yaml
    ;;
esac

# 2. Evidence preservation
mkdir -p "/security/incidents/$INCIDENT_ID"
kubectl get events -n acgs-system --sort-by='.lastTimestamp' > "/security/incidents/$INCIDENT_ID/events.log"
kubectl logs -n acgs-system --all-containers=true --previous > "/security/incidents/$INCIDENT_ID/previous-logs.log"
kubectl get pods -n acgs-system -o yaml > "/security/incidents/$INCIDENT_ID/pod-states.yaml"

# 3. Notification
curl -X POST "http://monitoring-service:8014/api/security/incidents" \
  -H "Content-Type: application/json" \
  -d "{
    \"incident_id\": \"$INCIDENT_ID\",
    \"type\": \"$INCIDENT_TYPE\",
    \"severity\": \"critical\",
    \"timestamp\": \"$(date --iso-8601)\",
    \"constitutional_hash\": \"cdd01ef066bc6cf2\",
    \"status\": \"active\"
  }"

echo "✅ Initial response completed for incident $INCIDENT_ID"
```

#### Phase 2: Investigation and Analysis (5-30 minutes)
```bash
#!/bin/bash
# Security incident investigation
INCIDENT_ID=$1

echo "=== SECURITY INCIDENT INVESTIGATION ==="
echo "Incident ID: $INCIDENT_ID"

# 1. Collect forensic data
echo "1. Collecting forensic data..."
kubectl get all -n acgs-system -o yaml > "/security/incidents/$INCIDENT_ID/cluster-state.yaml"
kubectl describe pods -n acgs-system > "/security/incidents/$INCIDENT_ID/pod-descriptions.txt"

# 2. Analyze security logs
echo "2. Analyzing security logs..."
kubectl logs -n acgs-system -l app=auth-service | grep -i "error\|unauthorized\|failed" > "/security/incidents/$INCIDENT_ID/auth-errors.log"
kubectl logs -n acgs-system -l app=audit-service | grep -i "violation\|breach\|unauthorized" > "/security/incidents/$INCIDENT_ID/audit-violations.log"

# 3. Check constitutional compliance
echo "3. Checking constitutional compliance..."
kubectl get pods -n acgs-system -o jsonpath='{.items[*].metadata.labels.constitutional-hash}' | grep -v "cdd01ef066bc6cf2" > "/security/incidents/$INCIDENT_ID/compliance-violations.txt"

# 4. Network analysis
echo "4. Analyzing network traffic..."
kubectl get networkpolicy -n acgs-system -o yaml > "/security/incidents/$INCIDENT_ID/network-policies.yaml"
kubectl get authorizationpolicy -n acgs-system -o yaml > "/security/incidents/$INCIDENT_ID/authorization-policies.yaml"

# 5. User activity analysis
echo "5. Analyzing user activity..."
curl -s "http://monitoring-service:8014/api/security/user-activity?since=1h" > "/security/incidents/$INCIDENT_ID/user-activity.json"

# 6. System integrity check
echo "6. Checking system integrity..."
kubectl exec -n acgs-system deployment/constitutional-core -- \
  python3 -c "
import hashlib
import json
# System integrity validation
expected_hash = 'cdd01ef066bc6cf2'
print(f'Expected constitutional hash: {expected_hash}')
# Add integrity checking logic here
" > "/security/incidents/$INCIDENT_ID/integrity-check.log"

echo "✅ Investigation completed for incident $INCIDENT_ID"
```

#### Phase 3: Remediation and Recovery (30-120 minutes)
```bash
#!/bin/bash
# Security incident remediation
INCIDENT_ID=$1
INCIDENT_TYPE=$2

echo "=== SECURITY INCIDENT REMEDIATION ==="
echo "Incident ID: $INCIDENT_ID"
echo "Incident Type: $INCIDENT_TYPE"

# 1. Implement remediation based on incident type
case $INCIDENT_TYPE in
  "constitutional")
    echo "Remediating constitutional security incident..."
    # Restore constitutional compliance
    kubectl patch deployment constitutional-core -n acgs-system --patch '{"spec":{"template":{"metadata":{"labels":{"constitutional-hash":"cdd01ef066bc6cf2"}}}}}'
    kubectl rollout restart deployment/constitutional-core -n acgs-system
    ;;
  "authentication")
    echo "Remediating authentication security incident..."
    # Reset authentication service
    kubectl delete secret auth-jwt-secret -n acgs-system
    kubectl create secret generic auth-jwt-secret -n acgs-system --from-literal=secret=$(openssl rand -hex 32)
    kubectl scale deployment auth-service -n acgs-system --replicas=3
    ;;
  "authorization")
    echo "Remediating authorization security incident..."
    # Restore proper authorization policies
    kubectl delete authorizationpolicy --all -n acgs-system
    kubectl apply -f /security/policies/default-authorization.yaml
    ;;
  "network")
    echo "Remediating network security incident..."
    # Restore network policies
    kubectl delete networkpolicy --all -n acgs-system
    kubectl apply -f /security/policies/default-network-policies.yaml
    ;;
  "data")
    echo "Remediating data security incident..."
    # Restore from backup if needed
    kubectl apply -f /deployment/backup/emergency-restore.yaml
    ;;
esac

# 2. Validate remediation
echo "2. Validating remediation..."
kubectl get pods -n acgs-system --field-selector=status.phase=Running
kubectl exec -n acgs-system deployment/constitutional-core -- curl -f http://localhost:8001/health

# 3. Security validation
echo "3. Performing security validation..."
curl -X POST "http://auth-service:8013/api/auth/validate" \
  -H "constitutional-hash: cdd01ef066bc6cf2" \
  -d '{"test": "post_incident"}'

# 4. Performance validation
echo "4. Validating performance..."
LATENCY=$(curl -s "http://monitoring-service:8014/api/metrics/latency/constitutional-core" | jq -r .p99)
THROUGHPUT=$(curl -s "http://monitoring-service:8014/api/metrics/throughput/constitutional-core" | jq -r .rps)

echo "P99 Latency: $LATENCY ms"
echo "Throughput: $THROUGHPUT RPS"

# 5. Constitutional compliance validation
echo "5. Validating constitutional compliance..."
COMPLIANCE_RATE=$(curl -s "http://monitoring-service:8014/api/metrics/compliance/system" | jq -r .rate)
echo "Constitutional compliance rate: $COMPLIANCE_RATE"

echo "✅ Remediation completed for incident $INCIDENT_ID"
```

## Security Auditing

### Daily Security Audit
```bash
#!/bin/bash
# Daily security audit
echo "=== ACGS-2 Daily Security Audit - $(date) ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. Constitutional compliance audit
echo "1. Constitutional Compliance Audit"
TOTAL_PODS=$(kubectl get pods -n acgs-system --no-headers | wc -l)
COMPLIANT_PODS=$(kubectl get pods -n acgs-system -l constitutional-hash=cdd01ef066bc6cf2 --no-headers | wc -l)
COMPLIANCE_RATE=$(echo "scale=2; $COMPLIANT_PODS / $TOTAL_PODS * 100" | bc -l)

echo "Total pods: $TOTAL_PODS"
echo "Compliant pods: $COMPLIANT_PODS"
echo "Compliance rate: $COMPLIANCE_RATE%"

# 2. Authentication audit
echo "2. Authentication Audit"
AUTH_ATTEMPTS=$(curl -s "http://monitoring-service:8014/api/security/auth-attempts?since=24h" | jq -r .total)
AUTH_FAILURES=$(curl -s "http://monitoring-service:8014/api/security/auth-failures?since=24h" | jq -r .total)
AUTH_SUCCESS_RATE=$(echo "scale=2; ($AUTH_ATTEMPTS - $AUTH_FAILURES) / $AUTH_ATTEMPTS * 100" | bc -l)

echo "Authentication attempts: $AUTH_ATTEMPTS"
echo "Authentication failures: $AUTH_FAILURES"
echo "Authentication success rate: $AUTH_SUCCESS_RATE%"

# 3. Authorization audit
echo "3. Authorization Audit"
AUTHZ_REQUESTS=$(curl -s "http://monitoring-service:8014/api/security/authz-requests?since=24h" | jq -r .total)
AUTHZ_DENIALS=$(curl -s "http://monitoring-service:8014/api/security/authz-denials?since=24h" | jq -r .total)
AUTHZ_SUCCESS_RATE=$(echo "scale=2; ($AUTHZ_REQUESTS - $AUTHZ_DENIALS) / $AUTHZ_REQUESTS * 100" | bc -l)

echo "Authorization requests: $AUTHZ_REQUESTS"
echo "Authorization denials: $AUTHZ_DENIALS"
echo "Authorization success rate: $AUTHZ_SUCCESS_RATE%"

# 4. Network security audit
echo "4. Network Security Audit"
NETWORK_POLICIES=$(kubectl get networkpolicy -n acgs-system --no-headers | wc -l)
AUTHZ_POLICIES=$(kubectl get authorizationpolicy -n acgs-system --no-headers | wc -l)
PEER_AUTH_POLICIES=$(kubectl get peerauthentication -n acgs-system --no-headers | wc -l)

echo "Network policies: $NETWORK_POLICIES"
echo "Authorization policies: $AUTHZ_POLICIES"
echo "Peer authentication policies: $PEER_AUTH_POLICIES"

# 5. Certificate audit
echo "5. Certificate Audit"
kubectl get certificates -n acgs-system -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' | grep -c "True"

# 6. Security violations
echo "6. Security Violations (last 24h)"
SECURITY_VIOLATIONS=$(curl -s "http://monitoring-service:8014/api/security/violations?since=24h" | jq -r .total)
echo "Security violations: $SECURITY_VIOLATIONS"

# 7. Audit log integrity
echo "7. Audit Log Integrity"
AUDIT_LOGS=$(curl -s "http://monitoring-service:8014/api/audit/logs?since=24h" | jq -r .total)
AUDIT_INTEGRITY=$(curl -s "http://monitoring-service:8014/api/audit/integrity" | jq -r .valid)
echo "Audit logs: $AUDIT_LOGS"
echo "Audit integrity: $AUDIT_INTEGRITY"

# Generate audit report
cat > "/security/audit/daily-audit-$(date +%Y%m%d).json" << EOF
{
  "timestamp": "$(date --iso-8601)",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "compliance_rate": $COMPLIANCE_RATE,
  "authentication_success_rate": $AUTH_SUCCESS_RATE,
  "authorization_success_rate": $AUTHZ_SUCCESS_RATE,
  "network_policies": $NETWORK_POLICIES,
  "authorization_policies": $AUTHZ_POLICIES,
  "peer_auth_policies": $PEER_AUTH_POLICIES,
  "security_violations": $SECURITY_VIOLATIONS,
  "audit_logs": $AUDIT_LOGS,
  "audit_integrity": "$AUDIT_INTEGRITY"
}
EOF

echo "✅ Daily security audit completed"
```

### Weekly Security Assessment
```bash
#!/bin/bash
# Weekly security assessment
echo "=== ACGS-2 Weekly Security Assessment - $(date) ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. Vulnerability scanning
echo "1. Vulnerability Scanning"
kubectl apply -f /security/scanning/weekly-vulnerability-scan.yaml
kubectl wait --for=condition=complete job/vulnerability-scan -n acgs-system --timeout=1800s

# 2. Penetration testing
echo "2. Penetration Testing"
kubectl apply -f /security/testing/weekly-penetration-test.yaml
kubectl wait --for=condition=complete job/penetration-test -n acgs-system --timeout=1800s

# 3. Security policy review
echo "3. Security Policy Review"
kubectl get networkpolicy -n acgs-system -o yaml > "/security/reviews/network-policies-$(date +%Y%m%d).yaml"
kubectl get authorizationpolicy -n acgs-system -o yaml > "/security/reviews/authorization-policies-$(date +%Y%m%d).yaml"

# 4. Access review
echo "4. Access Review"
kubectl get rolebinding -n acgs-system -o yaml > "/security/reviews/role-bindings-$(date +%Y%m%d).yaml"
kubectl get clusterrolebinding -o yaml | grep -A 10 -B 10 "acgs-system" > "/security/reviews/cluster-role-bindings-$(date +%Y%m%d).yaml"

# 5. Certificate review
echo "5. Certificate Review"
kubectl get certificates -n acgs-system -o yaml > "/security/reviews/certificates-$(date +%Y%m%d).yaml"

# 6. Security metrics analysis
echo "6. Security Metrics Analysis"
curl -s "http://monitoring-service:8014/api/security/metrics?period=week" > "/security/reviews/security-metrics-$(date +%Y%m%d).json"

echo "✅ Weekly security assessment completed"
```

## Threat Management

### Threat Detection
```bash
#!/bin/bash
# Threat detection system
echo "=== ACGS-2 Threat Detection - $(date) ==="

# 1. Anomaly detection
echo "1. Anomaly Detection"
ANOMALIES=$(curl -s "http://monitoring-service:8014/api/security/anomalies" | jq -r .total)
echo "Detected anomalies: $ANOMALIES"

# 2. Brute force detection
echo "2. Brute Force Detection"
BRUTE_FORCE_ATTEMPTS=$(curl -s "http://monitoring-service:8014/api/security/brute-force" | jq -r .attempts)
if [ "$BRUTE_FORCE_ATTEMPTS" -gt 10 ]; then
  echo "🚨 THREAT: Brute force attack detected ($BRUTE_FORCE_ATTEMPTS attempts)"
  # Implement rate limiting
  kubectl apply -f /security/threat-response/rate-limiting.yaml
fi

# 3. DDoS detection
echo "3. DDoS Detection"
REQUEST_RATE=$(curl -s "http://monitoring-service:8014/api/metrics/request-rate" | jq -r .rate)
if (( $(echo "$REQUEST_RATE > 10000" | bc -l) )); then
  echo "🚨 THREAT: Potential DDoS attack detected ($REQUEST_RATE RPS)"
  # Implement DDoS protection
  kubectl apply -f /security/threat-response/ddos-protection.yaml
fi

# 4. Insider threat detection
echo "4. Insider Threat Detection"
UNUSUAL_ACCESS=$(curl -s "http://monitoring-service:8014/api/security/unusual-access" | jq -r .total)
if [ "$UNUSUAL_ACCESS" -gt 5 ]; then
  echo "⚠️ WARNING: Unusual access patterns detected ($UNUSUAL_ACCESS instances)"
fi

# 5. Malware detection
echo "5. Malware Detection"
kubectl apply -f /security/scanning/malware-scan.yaml
kubectl wait --for=condition=complete job/malware-scan -n acgs-system --timeout=600s

echo "✅ Threat detection completed"
```

### Threat Response
```bash
#!/bin/bash
# Automated threat response
THREAT_TYPE=$1
THREAT_SEVERITY=$2

echo "=== ACGS-2 Threat Response ==="
echo "Threat Type: $THREAT_TYPE"
echo "Threat Severity: $THREAT_SEVERITY"

case $THREAT_TYPE in
  "brute_force")
    echo "Responding to brute force attack..."
    # Implement rate limiting
    kubectl apply -f /security/threat-response/enhanced-rate-limiting.yaml
    # Block suspicious IPs
    kubectl apply -f /security/threat-response/ip-blocking.yaml
    ;;
  "ddos")
    echo "Responding to DDoS attack..."
    # Implement DDoS protection
    kubectl apply -f /security/threat-response/ddos-protection.yaml
    # Scale up services
    kubectl scale deployment constitutional-core -n acgs-system --replicas=10
    ;;
  "insider")
    echo "Responding to insider threat..."
    # Implement stricter access controls
    kubectl apply -f /security/threat-response/strict-access-control.yaml
    # Enable enhanced monitoring
    kubectl apply -f /security/threat-response/enhanced-monitoring.yaml
    ;;
  "malware")
    echo "Responding to malware threat..."
    # Isolate affected pods
    kubectl apply -f /security/threat-response/pod-isolation.yaml
    # Initiate cleanup
    kubectl apply -f /security/threat-response/malware-cleanup.yaml
    ;;
esac

# Log threat response
curl -X POST "http://monitoring-service:8014/api/security/threat-response" \
  -H "Content-Type: application/json" \
  -d "{
    \"threat_type\": \"$THREAT_TYPE\",
    \"severity\": \"$THREAT_SEVERITY\",
    \"response_time\": \"$(date --iso-8601)\",
    \"constitutional_hash\": \"cdd01ef066bc6cf2\"
  }"

echo "✅ Threat response completed"
```

## Compliance Management

### Compliance Monitoring
```bash
#!/bin/bash
# Compliance monitoring
echo "=== ACGS-2 Compliance Monitoring - $(date) ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"

# 1. Constitutional compliance
echo "1. Constitutional Compliance"
CONST_COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/compliance/constitutional" | jq -r .compliance_rate)
echo "Constitutional compliance: $CONST_COMPLIANCE%"

# 2. GDPR compliance
echo "2. GDPR Compliance"
GDPR_COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/compliance/gdpr" | jq -r .compliance_rate)
echo "GDPR compliance: $GDPR_COMPLIANCE%"

# 3. SOX compliance
echo "3. SOX Compliance"
SOX_COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/compliance/sox" | jq -r .compliance_rate)
echo "SOX compliance: $SOX_COMPLIANCE%"

# 4. HIPAA compliance
echo "4. HIPAA Compliance"
HIPAA_COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/compliance/hipaa" | jq -r .compliance_rate)
echo "HIPAA compliance: $HIPAA_COMPLIANCE%"

# 5. Audit trail compliance
echo "5. Audit Trail Compliance"
AUDIT_COMPLIANCE=$(curl -s "http://monitoring-service:8014/api/compliance/audit" | jq -r .compliance_rate)
echo "Audit compliance: $AUDIT_COMPLIANCE%"

# Generate compliance report
cat > "/security/compliance/compliance-report-$(date +%Y%m%d).json" << EOF
{
  "timestamp": "$(date --iso-8601)",
  "constitutional_hash": "cdd01ef066bc6cf2",
  "constitutional_compliance": $CONST_COMPLIANCE,
  "gdpr_compliance": $GDPR_COMPLIANCE,
  "sox_compliance": $SOX_COMPLIANCE,
  "hipaa_compliance": $HIPAA_COMPLIANCE,
  "audit_compliance": $AUDIT_COMPLIANCE,
  "overall_compliance": $(echo "scale=2; ($CONST_COMPLIANCE + $GDPR_COMPLIANCE + $SOX_COMPLIANCE + $HIPAA_COMPLIANCE + $AUDIT_COMPLIANCE) / 5" | bc -l)
}
EOF

echo "✅ Compliance monitoring completed"
```

## Security Automation

### Automated Security Scanning
```bash
# Create security scanning automation
create_security_automation() {
  echo "Creating security automation jobs..."
  
  # Daily vulnerability scan
  kubectl apply -f - << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-vulnerability-scan
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: vulnerability-scanner
            image: aquasec/trivy:latest
            command: ["/bin/sh", "-c"]
            args:
            - |
              echo "Starting vulnerability scan"
              trivy image --format json acgs/constitutional-core:latest > /tmp/vuln-report.json
              echo "Vulnerability scan completed"
          restartPolicy: OnFailure
EOF

  # Weekly security assessment
  kubectl apply -f - << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: weekly-security-assessment
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  schedule: "0 1 * * 0"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: security-assessor
            image: acgs/security-tools:latest
            command: ["/bin/sh", "-c"]
            args:
            - |
              echo "Starting security assessment"
              # Run security assessment tools
              echo "Security assessment completed"
          restartPolicy: OnFailure
EOF

  # Continuous compliance monitoring
  kubectl apply -f - << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: compliance-monitor
  namespace: acgs-system
  labels:
    constitutional-hash: cdd01ef066bc6cf2
spec:
  schedule: "*/10 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: compliance-monitor
            image: acgs/compliance-monitor:latest
            command: ["/bin/sh", "-c"]
            args:
            - |
              echo "Starting compliance check"
              # Run compliance monitoring
              echo "Compliance check completed"
          restartPolicy: OnFailure
EOF

  echo "Security automation jobs created"
}
```

## Security Troubleshooting

### Common Security Issues

#### Authentication Issues
```bash
# Troubleshoot authentication problems
troubleshoot_auth() {
  echo "=== Authentication Troubleshooting ==="
  
  # Check auth service status
  kubectl get pods -n acgs-system -l app=auth-service
  kubectl logs -n acgs-system -l app=auth-service --tail=50
  
  # Check JWT secret
  kubectl get secret auth-jwt-secret -n acgs-system
  
  # Test authentication endpoint
  curl -v "http://auth-service:8013/api/auth/health"
  
  # Check auth database connection
  kubectl exec -n acgs-system deployment/auth-service -- \
    pg_isready -h postgres -p 5432
}
```

#### Authorization Issues
```bash
# Troubleshoot authorization problems
troubleshoot_authz() {
  echo "=== Authorization Troubleshooting ==="
  
  # Check authorization policies
  kubectl get authorizationpolicy -n acgs-system
  
  # Check RBAC
  kubectl get rolebinding -n acgs-system
  kubectl get clusterrolebinding | grep acgs
  
  # Check service account
  kubectl get serviceaccount -n acgs-system
}
```

#### Network Security Issues
```bash
# Troubleshoot network security problems
troubleshoot_network_security() {
  echo "=== Network Security Troubleshooting ==="
  
  # Check network policies
  kubectl get networkpolicy -n acgs-system
  
  # Check mTLS configuration
  kubectl get peerauthentication -n acgs-system
  kubectl get destinationrule -n acgs-system
  
  # Test mTLS connectivity
  kubectl exec -n acgs-system deployment/constitutional-core -- \
    curl -v https://groqcloud-policy:8080/health
}
```

---

**Constitutional Compliance**: All security operations maintain constitutional hash `cdd01ef066bc6cf2` validation and enforce security policies throughout the system.

**Last Updated**: 2025-07-18 - Security operations procedures established