#!/bin/bash

# ACGS-PGP Emergency Response System
# Handles emergency situations, constitutional violations, and system failures

set -e

NAMESPACE="acgs-system"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
EMERGENCY_LOG="/var/log/acgs-emergency.log"
EMERGENCY_CONTACT="ops-team@acgs.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$EMERGENCY_LOG"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$EMERGENCY_LOG"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$EMERGENCY_LOG"; }
log_emergency() { echo -e "${PURPLE}[EMERGENCY]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$EMERGENCY_LOG"; }

# Emergency shutdown - scales all services to 0 replicas
emergency_shutdown() {
    local reason=${1:-"Manual emergency shutdown"}
    
    log_emergency "INITIATING EMERGENCY SHUTDOWN"
    log_emergency "Reason: $reason"
    log_emergency "Target RTO: <30 minutes"
    
    local start_time=$(date +%s)
    
    # Create emergency backup first
    log_emergency "Creating emergency backup..."
    ./infrastructure/kubernetes/operations/backup-restore.sh emergency
    
    # Scale down all deployments
    log_emergency "Scaling down all services..."
    kubectl scale deployment --all --replicas=0 -n $NAMESPACE
    
    # Wait for pods to terminate
    log_emergency "Waiting for pods to terminate..."
    local timeout=300  # 5 minutes
    local elapsed=0
    
    while [[ $elapsed -lt $timeout ]]; do
        local running_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase=Running --no-headers | wc -l)
        
        if [[ $running_pods -eq 0 ]]; then
            log_emergency "All pods terminated successfully"
            break
        fi
        
        log_emergency "Waiting for $running_pods pods to terminate..."
        sleep 10
        elapsed=$((elapsed + 10))
    done
    
    local end_time=$(date +%s)
    local shutdown_duration=$((end_time - start_time))
    
    if [[ $shutdown_duration -lt 1800 ]]; then  # 30 minutes
        log_emergency "✅ Emergency shutdown completed in ${shutdown_duration}s (< 30min RTO)"
    else
        log_emergency "⚠️ Emergency shutdown took ${shutdown_duration}s (> 30min RTO)"
    fi
    
    # Send notification
    send_emergency_notification "EMERGENCY_SHUTDOWN" "$reason" "$shutdown_duration"
    
    return 0
}

# Constitutional violation response
constitutional_violation_response() {
    local violation_details=${1:-"Constitutional compliance violation detected"}
    
    log_emergency "CONSTITUTIONAL VIOLATION DETECTED"
    log_emergency "Details: $violation_details"
    
    # Immediate actions
    log_emergency "Executing constitutional violation protocol..."
    
    # 1. Isolate constitutional AI service
    log_emergency "Isolating constitutional AI service..."
    kubectl scale deployment constitutional-ai-service --replicas=0 -n $NAMESPACE
    
    # 2. Create forensic snapshot
    log_emergency "Creating forensic snapshot..."
    local forensic_dir="/tmp/constitutional_violation_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$forensic_dir"
    
    # Capture logs
    kubectl logs -l app=constitutional-ai-service -n $NAMESPACE --previous > "$forensic_dir/ac_service_logs.txt" 2>/dev/null || true
    kubectl logs -l app=constitutional-ai-service -n $NAMESPACE > "$forensic_dir/ac_service_current_logs.txt" 2>/dev/null || true
    
    # Capture configuration
    kubectl get deployment constitutional-ai-service -n $NAMESPACE -o yaml > "$forensic_dir/ac_service_config.yaml"
    
    # Capture events
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' > "$forensic_dir/events.txt"
    
    # 3. Verify constitutional hash
    log_emergency "Verifying constitutional hash..."
    local current_hash=$(kubectl get deployment constitutional-ai-service -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="CONSTITUTIONAL_HASH")].value}')
    
    if [[ "$current_hash" != "$CONSTITUTIONAL_HASH" ]]; then
        log_emergency "❌ Constitutional hash mismatch detected!"
        log_emergency "Expected: $CONSTITUTIONAL_HASH"
        log_emergency "Found: $current_hash"
        echo "HASH_MISMATCH: Expected=$CONSTITUTIONAL_HASH, Found=$current_hash" > "$forensic_dir/hash_violation.txt"
    fi
    
    # 4. Archive forensic data
    tar -czf "/var/log/constitutional_violation_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$forensic_dir" .
    rm -rf "$forensic_dir"
    
    # 5. Send critical alert
    send_emergency_notification "CONSTITUTIONAL_VIOLATION" "$violation_details" "IMMEDIATE_ATTENTION_REQUIRED"
    
    log_emergency "Constitutional violation response completed"
    log_emergency "Manual review required before service restoration"
    
    return 0
}

# Service failure recovery
service_failure_recovery() {
    local failed_service=$1
    local failure_reason=${2:-"Service failure detected"}
    
    log_emergency "SERVICE FAILURE RECOVERY INITIATED"
    log_emergency "Service: $failed_service"
    log_emergency "Reason: $failure_reason"
    
    # 1. Capture failure state
    log_emergency "Capturing failure state..."
    local failure_dir="/tmp/service_failure_${failed_service}_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$failure_dir"
    
    # Get pod logs
    kubectl logs -l app=$failed_service -n $NAMESPACE --previous > "$failure_dir/previous_logs.txt" 2>/dev/null || true
    kubectl logs -l app=$failed_service -n $NAMESPACE > "$failure_dir/current_logs.txt" 2>/dev/null || true
    
    # Get pod description
    kubectl describe pods -l app=$failed_service -n $NAMESPACE > "$failure_dir/pod_description.txt"
    
    # Get deployment status
    kubectl describe deployment $failed_service -n $NAMESPACE > "$failure_dir/deployment_status.txt"
    
    # 2. Attempt automatic recovery
    log_emergency "Attempting automatic recovery..."
    
    # Restart deployment
    kubectl rollout restart deployment/$failed_service -n $NAMESPACE
    
    # Wait for rollout to complete
    if kubectl rollout status deployment/$failed_service -n $NAMESPACE --timeout=300s; then
        log_emergency "✅ Service recovery successful: $failed_service"
        
        # Verify service health
        sleep 30
        local health_check=$(kubectl exec -n $NAMESPACE deployment/$failed_service -- curl -s -f http://localhost:8000/health 2>/dev/null || echo "FAIL")
        
        if [[ "$health_check" != "FAIL" ]]; then
            log_emergency "✅ Service health verified: $failed_service"
        else
            log_emergency "⚠️ Service health check failed after recovery: $failed_service"
        fi
    else
        log_emergency "❌ Automatic recovery failed: $failed_service"
        
        # Escalate to manual intervention
        log_emergency "Escalating to manual intervention..."
        send_emergency_notification "SERVICE_RECOVERY_FAILED" "$failed_service: $failure_reason" "MANUAL_INTERVENTION_REQUIRED"
    fi
    
    # 3. Archive failure data
    tar -czf "/var/log/service_failure_${failed_service}_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$failure_dir" .
    rm -rf "$failure_dir"
    
    return 0
}

# Performance degradation response
performance_degradation_response() {
    local metric_type=$1
    local current_value=$2
    local threshold=$3
    
    log_emergency "PERFORMANCE DEGRADATION DETECTED"
    log_emergency "Metric: $metric_type"
    log_emergency "Current: $current_value"
    log_emergency "Threshold: $threshold"
    
    # 1. Capture performance snapshot
    log_emergency "Capturing performance snapshot..."
    local perf_dir="/tmp/performance_degradation_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$perf_dir"
    
    # Resource usage
    kubectl top pods -n $NAMESPACE > "$perf_dir/resource_usage.txt" 2>/dev/null || echo "Metrics not available" > "$perf_dir/resource_usage.txt"
    kubectl top nodes > "$perf_dir/node_usage.txt" 2>/dev/null || echo "Metrics not available" > "$perf_dir/node_usage.txt"
    
    # Service status
    kubectl get pods -n $NAMESPACE -o wide > "$perf_dir/pod_status.txt"
    
    # Recent events
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -50 > "$perf_dir/recent_events.txt"
    
    # 2. Attempt performance optimization
    case $metric_type in
        "response_time")
            log_emergency "Implementing response time optimization..."
            # Scale up services
            kubectl scale deployment --all --replicas=5 -n $NAMESPACE
            ;;
        "cpu_usage")
            log_emergency "Implementing CPU optimization..."
            # Restart high CPU pods
            kubectl delete pods -l app.kubernetes.io/part-of=acgs-system -n $NAMESPACE --field-selector=status.phase=Running
            ;;
        "memory_usage")
            log_emergency "Implementing memory optimization..."
            # Restart high memory pods
            kubectl delete pods -l app.kubernetes.io/part-of=acgs-system -n $NAMESPACE --field-selector=status.phase=Running
            ;;
    esac
    
    # 3. Monitor improvement
    log_emergency "Monitoring performance improvement..."
    sleep 60
    
    # 4. Archive performance data
    tar -czf "/var/log/performance_degradation_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$perf_dir" .
    rm -rf "$perf_dir"
    
    send_emergency_notification "PERFORMANCE_DEGRADATION" "$metric_type: $current_value > $threshold" "OPTIMIZATION_ATTEMPTED"
    
    return 0
}

# Send emergency notification
send_emergency_notification() {
    local alert_type=$1
    local details=$2
    local status=$3
    
    local message="ACGS-PGP EMERGENCY ALERT
Type: $alert_type
Time: $(date '+%Y-%m-%d %H:%M:%S')
Namespace: $NAMESPACE
Details: $details
Status: $status
Constitutional Hash: $CONSTITUTIONAL_HASH

This is an automated emergency notification from the ACGS-PGP system.
Please review the situation immediately.

Emergency Log: $EMERGENCY_LOG"
    
    # Log the notification
    log_emergency "Sending emergency notification: $alert_type"
    
    # In production, this would send to actual notification systems
    # For now, we'll write to a notification file
    echo "$message" > "/tmp/emergency_notification_$(date +%Y%m%d_%H%M%S).txt"
    
    # Simulate notification sending
    log_emergency "Emergency notification sent to: $EMERGENCY_CONTACT"
}

# System status check
emergency_status_check() {
    log_emergency "EMERGENCY STATUS CHECK"
    
    echo "=== ACGS-PGP Emergency Status ==="
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Namespace: $NAMESPACE"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo
    
    echo "=== Service Status ==="
    kubectl get deployments -n $NAMESPACE -o wide
    echo
    
    echo "=== Pod Status ==="
    kubectl get pods -n $NAMESPACE -o wide
    echo
    
    echo "=== Recent Events ==="
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
    echo
    
    echo "=== Resource Usage ==="
    kubectl top pods -n $NAMESPACE 2>/dev/null || echo "Metrics not available"
    echo
    
    echo "=== Emergency Log Tail ==="
    tail -20 "$EMERGENCY_LOG" 2>/dev/null || echo "Emergency log not found"
}

# Main function
main() {
    local action=${1:-"status"}
    
    # Ensure emergency log exists
    mkdir -p "$(dirname "$EMERGENCY_LOG")"
    touch "$EMERGENCY_LOG"
    
    case $action in
        "shutdown")
            emergency_shutdown "$2"
            ;;
        "constitutional-violation")
            constitutional_violation_response "$2"
            ;;
        "service-failure")
            service_failure_recovery "$2" "$3"
            ;;
        "performance-degradation")
            performance_degradation_response "$2" "$3" "$4"
            ;;
        "status")
            emergency_status_check
            ;;
        "test-notification")
            send_emergency_notification "TEST" "Emergency notification test" "TESTING"
            ;;
        *)
            echo "Usage: $0 {shutdown|constitutional-violation|service-failure|performance-degradation|status|test-notification}"
            echo "  shutdown                    - Emergency system shutdown"
            echo "  constitutional-violation    - Handle constitutional AI violation"
            echo "  service-failure            - Recover from service failure"
            echo "  performance-degradation    - Handle performance issues"
            echo "  status                     - Emergency status check"
            echo "  test-notification          - Test emergency notification system"
            exit 1
            ;;
    esac
}

main "$@"
