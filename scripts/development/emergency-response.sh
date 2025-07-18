# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
set -euo pipefail

# ACGS-1 Lite Emergency Response Script
# Handles critical incidents and constitutional violations

# Configuration
NAMESPACE_GOVERNANCE="governance"
NAMESPACE_WORKLOAD="workload"
NAMESPACE_MONITORING="monitoring"
NAMESPACE_SHARED="shared"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_critical() {
    echo -e "${RED}[CRITICAL]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# Emergency procedures
emergency_shutdown() {
    log_critical "INITIATING EMERGENCY SHUTDOWN"
    
    # Scale down all ACGS services
    log_info "Scaling down Policy Engine..."
    kubectl scale deployment/policy-engine --replicas=0 -n $NAMESPACE_GOVERNANCE || log_error "Failed to scale down Policy Engine"
    
    log_info "Scaling down Sandbox Controller..."
    kubectl scale deployment/sandbox-controller --replicas=0 -n $NAMESPACE_WORKLOAD || log_error "Failed to scale down Sandbox Controller"
    
    # Block all network traffic to workload namespace
    log_info "Implementing network isolation..."
    kubectl patch networkpolicy default-deny-all -n $NAMESPACE_WORKLOAD -p '{"spec":{"policyTypes":["Ingress","Egress"],"podSelector":{},"ingress":[],"egress":[]}}' || log_error "Failed to implement network isolation"
    
    # Kill all running sandbox pods
    log_info "Terminating all sandbox pods..."
    kubectl delete pods -l acgs-lite.io/service-type=sandbox -n $NAMESPACE_WORKLOAD --grace-period=0 --force || log_warning "Some sandbox pods may still be running"
    
    log_critical "EMERGENCY SHUTDOWN COMPLETED"
}

# Sandbox escape response
handle_sandbox_escape() {
    local agent_id="$1"
    local incident_id="$(date +%Y%m%d-%H%M%S)-escape-${agent_id}"
    
    log_critical "SANDBOX ESCAPE DETECTED - Agent: $agent_id, Incident: $incident_id"
    
    # Immediate containment
    log_info "Implementing immediate containment for agent $agent_id..."
    
    # Kill specific agent pods
    kubectl delete pods -l agent-id="$agent_id" -n $NAMESPACE_WORKLOAD --grace-period=0 --force || log_error "Failed to terminate agent pods"
    
    # Capture forensic data
    log_info "Capturing forensic data..."
    mkdir -p "forensics/$incident_id"
    
    # Collect logs
    kubectl logs -l agent-id="$agent_id" -n $NAMESPACE_WORKLOAD --previous > "forensics/$incident_id/agent-logs.txt" 2>/dev/null || log_warning "Could not collect previous logs"
    kubectl logs -l app=sandbox-controller -n $NAMESPACE_WORKLOAD --since=10m > "forensics/$incident_id/sandbox-controller-logs.txt" || log_warning "Could not collect sandbox controller logs"
    
    # Collect system state
    kubectl get pods -l agent-id="$agent_id" -n $NAMESPACE_WORKLOAD -o yaml > "forensics/$incident_id/pod-state.yaml" 2>/dev/null || log_warning "Could not collect pod state"
    kubectl get events -n $NAMESPACE_WORKLOAD --field-selector involvedObject.name="$agent_id" > "forensics/$incident_id/events.txt" || log_warning "Could not collect events"
    
    # Query audit database
    log_info "Querying audit database for agent $agent_id..."
    kubectl exec -it constitutional-postgres-1 -n $NAMESPACE_SHARED -- psql -U postgres -d acgs_lite -c "
        SELECT * FROM sandbox_violations 
        WHERE agent_id='$agent_id' 
        ORDER BY created_at DESC 
        LIMIT 20;
    " > "forensics/$incident_id/audit-violations.txt" 2>/dev/null || log_warning "Could not query audit database"
    
    # Block agent from future execution
    log_info "Blacklisting agent $agent_id..."
    kubectl create configmap agent-blacklist-$agent_id -n $NAMESPACE_WORKLOAD --from-literal=agent_id="$agent_id" --from-literal=reason="sandbox_escape" --from-literal=timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)" || log_warning "Could not create blacklist entry"
    
    # Send alert
    send_critical_alert "SANDBOX ESCAPE" "Agent $agent_id attempted sandbox escape. Incident ID: $incident_id. Immediate containment implemented."
    
    log_success "Sandbox escape response completed for agent $agent_id"
    log_info "Forensic data saved to: forensics/$incident_id/"
}

# Constitutional violation response
handle_constitutional_violation() {
    local violation_type="$1"
    local agent_id="$2"
    local severity="$3"
    local incident_id="$(date +%Y%m%d-%H%M%S)-violation-${agent_id}"
    
    log_critical "CONSTITUTIONAL VIOLATION - Type: $violation_type, Agent: $agent_id, Severity: $severity"
    
    case "$severity" in
        "critical")
            # Immediate shutdown for critical violations
            log_info "Critical violation detected - implementing emergency containment..."
            kubectl delete pods -l agent-id="$agent_id" -n $NAMESPACE_WORKLOAD --grace-period=0 --force
            
            # Escalate to human review immediately
            create_human_review_request "$agent_id" "$violation_type" "critical" "immediate"
            ;;
        "high")
            # Pause agent execution
            log_info "High severity violation - pausing agent execution..."
            kubectl patch deployment -l agent-id="$agent_id" -n $NAMESPACE_WORKLOAD -p '{"spec":{"replicas":0}}'
            
            # Escalate to human review
            create_human_review_request "$agent_id" "$violation_type" "high" "urgent"
            ;;
        "medium")
            # Enhanced monitoring
            log_info "Medium severity violation - implementing enhanced monitoring..."
            kubectl label pods -l agent-id="$agent_id" -n $NAMESPACE_WORKLOAD enhanced-monitoring=true
            ;;
    esac
    
    # Log violation to audit trail
    log_info "Recording violation in audit trail..."
    kubectl exec -it constitutional-postgres-1 -n $NAMESPACE_SHARED -- psql -U postgres -d acgs_lite -c "
        INSERT INTO sandbox_violations (sandbox_id, agent_id, violation_type, severity, description, detection_layer, created_at)
        VALUES ('$incident_id', '$agent_id', '$violation_type', '$severity', 'Emergency response triggered', 'emergency_system', NOW());
    " || log_warning "Could not record violation in audit trail"
    
    send_critical_alert "CONSTITUTIONAL VIOLATION" "Violation: $violation_type, Agent: $agent_id, Severity: $severity, Incident: $incident_id"
    
    log_success "Constitutional violation response completed"
}

# System health emergency
handle_system_emergency() {
    local emergency_type="$1"
    local incident_id="$(date +%Y%m%d-%H%M%S)-system-${emergency_type}"
    
    log_critical "SYSTEM EMERGENCY - Type: $emergency_type, Incident: $incident_id"
    
    case "$emergency_type" in
        "policy_engine_failure")
            log_info "Policy Engine failure detected - implementing failsafe mode..."
            
            # Scale up Policy Engine
            kubectl scale deployment/policy-engine --replicas=5 -n $NAMESPACE_GOVERNANCE
            
            # Enable emergency policy mode (deny all by default)
            kubectl patch configmap opa-policies -n $NAMESPACE_GOVERNANCE -p '{"data":{"emergency.rego":"package emergency\ndefault allow = false"}}'
            
            # Restart OPA to load emergency policies
            kubectl rollout restart deployment/opa -n $NAMESPACE_GOVERNANCE
            ;;
            
        "database_failure")
            log_info "Database failure detected - implementing emergency procedures..."
            
            # Switch to read-only mode
            kubectl patch cluster constitutional-postgres -n $NAMESPACE_SHARED --type='merge' -p='{"spec":{"postgresql":{"parameters":{"default_transaction_read_only":"on"}}}}'
            
            # Scale down write-heavy services
            kubectl scale deployment/audit-trail-archiver --replicas=0 -n $NAMESPACE_SHARED
            ;;
            
        "monitoring_failure")
            log_info "Monitoring failure detected - implementing backup monitoring..."
            
            # Restart monitoring stack
            kubectl rollout restart deployment/prometheus -n $NAMESPACE_MONITORING
            kubectl rollout restart deployment/grafana -n $NAMESPACE_MONITORING
            kubectl rollout restart deployment/alertmanager -n $NAMESPACE_MONITORING
            ;;
    esac
    
    send_critical_alert "SYSTEM EMERGENCY" "Emergency type: $emergency_type, Incident: $incident_id, Response initiated"
    
    log_success "System emergency response completed"
}

# Create human review request
create_human_review_request() {
    local agent_id="$1"
    local violation_type="$2"
    local priority="$3"
    local urgency="$4"
    local request_id="$(uuidgen)"
    
    log_info "Creating human review request for agent $agent_id..."
    
    kubectl exec -it constitutional-postgres-1 -n $NAMESPACE_SHARED -- psql -U postgres -d acgs_lite -c "
        INSERT INTO human_review_requests (request_id, agent_id, action, risk_score, priority, context, requested_at, auto_timeout_at)
        VALUES (
            '$request_id',
            '$agent_id',
            'emergency_review',
            1.0,
            '$priority',
            '{\"violation_type\": \"$violation_type\", \"urgency\": \"$urgency\", \"emergency_response\": true}',
            NOW(),
            NOW() + INTERVAL '2 hours'
        );
    " || log_warning "Could not create human review request"
    
    log_success "Human review request created: $request_id"
}

# Send critical alert
send_critical_alert() {
    local alert_type="$1"
    local message="$2"
    local timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    log_info "Sending critical alert: $alert_type"
    
    # Create alert annotation for Prometheus
    kubectl annotate pod -l app=alertmanager -n $NAMESPACE_MONITORING \
        "acgs-lite.io/critical-alert-$(date +%s)"="$alert_type: $message" || log_warning "Could not create alert annotation"
    
    # Log to system
    echo "[$timestamp] CRITICAL ALERT - $alert_type: $message" >> /var/log/acgs-lite-emergency.log
    
    log_success "Critical alert sent"
}

# Collect emergency diagnostics
collect_diagnostics() {
    local incident_id="$1"
    local diag_dir="diagnostics/$incident_id"
    
    log_info "Collecting emergency diagnostics..."
    mkdir -p "$diag_dir"
    
    # System state
    kubectl get pods --all-namespaces -o wide > "$diag_dir/pods.txt"
    kubectl get services --all-namespaces > "$diag_dir/services.txt"
    kubectl get deployments --all-namespaces > "$diag_dir/deployments.txt"
    kubectl get events --all-namespaces --sort-by=.metadata.creationTimestamp > "$diag_dir/events.txt"
    
    # Resource usage
    kubectl top nodes > "$diag_dir/node-usage.txt" 2>/dev/null || echo "Metrics server not available" > "$diag_dir/node-usage.txt"
    kubectl top pods --all-namespaces > "$diag_dir/pod-usage.txt" 2>/dev/null || echo "Metrics server not available" > "$diag_dir/pod-usage.txt"
    
    # Logs from critical services
    kubectl logs -l app=policy-engine -n $NAMESPACE_GOVERNANCE --tail=1000 > "$diag_dir/policy-engine-logs.txt" 2>/dev/null || echo "No logs available" > "$diag_dir/policy-engine-logs.txt"
    kubectl logs -l app=sandbox-controller -n $NAMESPACE_WORKLOAD --tail=1000 > "$diag_dir/sandbox-controller-logs.txt" 2>/dev/null || echo "No logs available" > "$diag_dir/sandbox-controller-logs.txt"
    
    # Database status
    kubectl exec -it constitutional-postgres-1 -n $NAMESPACE_SHARED -- psql -U postgres -d acgs_lite -c "
        SELECT 
            'violations' as table_name, COUNT(*) as count 
        FROM sandbox_violations 
        WHERE created_at > NOW() - INTERVAL '1 hour'
        UNION ALL
        SELECT 
            'evaluations' as table_name, COUNT(*) as count 
        FROM policy_evaluations 
        WHERE created_at > NOW() - INTERVAL '1 hour';
    " > "$diag_dir/database-status.txt" 2>/dev/null || echo "Database not accessible" > "$diag_dir/database-status.txt"
    
    log_success "Emergency diagnostics collected in: $diag_dir"
}

# Recovery procedures
initiate_recovery() {
    local recovery_type="$1"
    
    log_info "Initiating recovery procedure: $recovery_type"
    
    case "$recovery_type" in
        "service_restart")
            log_info "Restarting core services..."
            kubectl rollout restart deployment/policy-engine -n $NAMESPACE_GOVERNANCE
            kubectl rollout restart deployment/sandbox-controller -n $NAMESPACE_WORKLOAD
            kubectl rollout restart deployment/opa -n $NAMESPACE_GOVERNANCE
            ;;
            
        "network_reset")
            log_info "Resetting network policies..."
            kubectl delete networkpolicy --all -n $NAMESPACE_WORKLOAD
            kubectl apply -f infrastructure/kubernetes/acgs-lite/network-policies.yaml
            ;;
            
        "full_restart")
            log_info "Performing full system restart..."
            kubectl delete pods --all -n $NAMESPACE_GOVERNANCE
            kubectl delete pods --all -n $NAMESPACE_WORKLOAD
            kubectl delete pods --all -n $NAMESPACE_MONITORING
            ;;
    esac
    
    log_success "Recovery procedure completed: $recovery_type"
}

# Main emergency response function
main() {
    local action="$1"
    shift
    
    case "$action" in
        "shutdown")
            emergency_shutdown
            ;;
        "sandbox-escape")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 sandbox-escape <agent_id>"
                exit 1
            fi
            handle_sandbox_escape "$1"
            ;;
        "constitutional-violation")
            if [[ $# -lt 3 ]]; then
                log_error "Usage: $0 constitutional-violation <violation_type> <agent_id> <severity>"
                exit 1
            fi
            handle_constitutional_violation "$1" "$2" "$3"
            ;;
        "system-emergency")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 system-emergency <emergency_type>"
                exit 1
            fi
            handle_system_emergency "$1"
            ;;
        "diagnostics")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 diagnostics <incident_id>"
                exit 1
            fi
            collect_diagnostics "$1"
            ;;
        "recovery")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 recovery <recovery_type>"
                exit 1
            fi
            initiate_recovery "$1"
            ;;
        *)
            echo "ACGS-1 Lite Emergency Response Script"
            echo "Usage: $0 <action> [arguments]"
            echo ""
            echo "Actions:"
            echo "  shutdown                                    - Emergency shutdown of all services"
            echo "  sandbox-escape <agent_id>                  - Handle sandbox escape attempt"
            echo "  constitutional-violation <type> <agent> <severity> - Handle constitutional violation"
            echo "  system-emergency <type>                    - Handle system emergency"
            echo "  diagnostics <incident_id>                  - Collect emergency diagnostics"
            echo "  recovery <type>                            - Initiate recovery procedures"
            echo ""
            echo "Examples:"
            echo "  $0 sandbox-escape agent-001"
            echo "  $0 constitutional-violation privilege_escalation agent-002 critical"
            echo "  $0 system-emergency policy_engine_failure"
            echo "  $0 diagnostics incident-20240101-120000"
            echo "  $0 recovery service_restart"
            exit 1
            ;;
    esac
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
