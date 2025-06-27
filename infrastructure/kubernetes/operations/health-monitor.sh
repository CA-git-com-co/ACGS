#!/bin/bash

# ACGS-PGP Health Monitoring Utility
# Continuous monitoring of system health, constitutional compliance, and performance

set -e

NAMESPACE="acgs-system"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
COMPLIANCE_THRESHOLD=0.95
RESPONSE_TIME_THRESHOLD=2.0
CHECK_INTERVAL=30

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }
log_health() { echo -e "${BLUE}[HEALTH]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }

# Expected services and their ports
declare -A SERVICES=(
    ["auth-service"]="8000"
    ["constitutional-ai-service"]="8001"
    ["integrity-service"]="8002"
    ["formal-verification-service"]="8003"
    ["governance-synthesis-service"]="8004"
    ["policy-governance-service"]="8005"
    ["evolutionary-computation-service"]="8006"
    ["model-orchestrator-service"]="8007"
)

# Check service health endpoints
check_service_health() {
    log_health "Checking service health endpoints..."
    
    local failed_services=()
    local total_services=${#SERVICES[@]}
    local healthy_services=0
    
    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"
        
        # Check if service is running
        local pod_status=$(kubectl get pods -n $NAMESPACE -l app=$service -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")
        
        if [[ "$pod_status" == "Running" ]]; then
            # Test health endpoint
            local health_check=$(kubectl exec -n $NAMESPACE deployment/$service -- curl -s -f http://localhost:$port/health 2>/dev/null || echo "FAIL")
            
            if [[ "$health_check" != "FAIL" ]]; then
                log_info "✓ $service healthy (port $port)"
                ((healthy_services++))
            else
                log_error "✗ $service health check failed"
                failed_services+=("$service")
            fi
        else
            log_error "✗ $service not running (status: $pod_status)"
            failed_services+=("$service")
        fi
    done
    
    local health_percentage=$(( healthy_services * 100 / total_services ))
    log_health "Service health: $healthy_services/$total_services ($health_percentage%)"
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_warn "Failed services: ${failed_services[*]}"
        return 1
    fi
    
    return 0
}

# Check constitutional compliance
check_constitutional_compliance() {
    log_health "Checking constitutional compliance..."
    
    # Check if constitutional AI service is responding
    local ac_pod=$(kubectl get pods -n $NAMESPACE -l app=constitutional-ai-service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -z "$ac_pod" ]]; then
        log_error "Constitutional AI service pod not found"
        return 1
    fi
    
    # Check constitutional hash
    local hash_check=$(kubectl exec -n $NAMESPACE $ac_pod -- env | grep CONSTITUTIONAL_HASH | cut -d= -f2 || echo "")
    
    if [[ "$hash_check" == "$CONSTITUTIONAL_HASH" ]]; then
        log_info "✓ Constitutional hash validated: $CONSTITUTIONAL_HASH"
    else
        log_error "✗ Constitutional hash mismatch - Expected: $CONSTITUTIONAL_HASH, Found: $hash_check"
        return 1
    fi
    
    # Test constitutional compliance endpoint
    local compliance_test=$(kubectl exec -n $NAMESPACE $ac_pod -- curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"query": "test compliance", "context": "health_check"}' \
        http://localhost:8001/validate 2>/dev/null || echo '{"compliance_score": 0}')
    
    # Extract compliance score (simplified - would need jq in production)
    local compliance_score=$(echo "$compliance_test" | grep -o '"compliance_score":[0-9.]*' | cut -d: -f2 || echo "0")
    
    if (( $(echo "$compliance_score >= $COMPLIANCE_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
        log_info "✓ Constitutional compliance: $compliance_score (>= $COMPLIANCE_THRESHOLD)"
        return 0
    else
        log_error "✗ Constitutional compliance below threshold: $compliance_score < $COMPLIANCE_THRESHOLD"
        return 1
    fi
}

# Check resource utilization
check_resource_utilization() {
    log_health "Checking resource utilization..."
    
    local high_cpu_pods=()
    local high_memory_pods=()
    
    # Get resource usage for all pods
    local pod_metrics=$(kubectl top pods -n $NAMESPACE --no-headers 2>/dev/null || echo "")
    
    if [[ -z "$pod_metrics" ]]; then
        log_warn "Unable to retrieve pod metrics (metrics-server may not be available)"
        return 0
    fi
    
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            local pod_name=$(echo "$line" | awk '{print $1}')
            local cpu_usage=$(echo "$line" | awk '{print $2}' | sed 's/m//')
            local memory_usage=$(echo "$line" | awk '{print $3}' | sed 's/Mi//')
            
            # Check CPU usage (threshold: 400m = 80% of 500m limit)
            if [[ "$cpu_usage" -gt 400 ]]; then
                high_cpu_pods+=("$pod_name:${cpu_usage}m")
            fi
            
            # Check memory usage (threshold: 800Mi = 80% of 1Gi limit)
            if [[ "$memory_usage" -gt 800 ]]; then
                high_memory_pods+=("$pod_name:${memory_usage}Mi")
            fi
        fi
    done <<< "$pod_metrics"
    
    if [[ ${#high_cpu_pods[@]} -gt 0 ]]; then
        log_warn "High CPU usage detected: ${high_cpu_pods[*]}"
    fi
    
    if [[ ${#high_memory_pods[@]} -gt 0 ]]; then
        log_warn "High memory usage detected: ${high_memory_pods[*]}"
    fi
    
    if [[ ${#high_cpu_pods[@]} -eq 0 ]] && [[ ${#high_memory_pods[@]} -eq 0 ]]; then
        log_info "✓ Resource utilization within normal limits"
        return 0
    fi
    
    return 1
}

# Check database connectivity
check_database_connectivity() {
    log_health "Checking database connectivity..."
    
    # Check CockroachDB
    local db_pod=$(kubectl get pods -n $NAMESPACE -l app=cockroachdb -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -z "$db_pod" ]]; then
        log_error "CockroachDB pod not found"
        return 1
    fi
    
    # Test database connection
    local db_test=$(kubectl exec -n $NAMESPACE $db_pod -- cockroach sql --insecure -e "SELECT 1;" 2>/dev/null || echo "FAIL")
    
    if [[ "$db_test" != "FAIL" ]]; then
        log_info "✓ CockroachDB connectivity verified"
    else
        log_error "✗ CockroachDB connectivity failed"
        return 1
    fi
    
    # Check DragonflyDB (Redis)
    local redis_pod=$(kubectl get pods -n $NAMESPACE -l app=dragonflydb -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -z "$redis_pod" ]]; then
        log_error "DragonflyDB pod not found"
        return 1
    fi
    
    # Test Redis connection
    local redis_test=$(kubectl exec -n $NAMESPACE $redis_pod -- redis-cli ping 2>/dev/null || echo "FAIL")
    
    if [[ "$redis_test" == "PONG" ]]; then
        log_info "✓ DragonflyDB connectivity verified"
        return 0
    else
        log_error "✗ DragonflyDB connectivity failed"
        return 1
    fi
}

# Check monitoring systems
check_monitoring_systems() {
    log_health "Checking monitoring systems..."
    
    local monitoring_issues=()
    
    # Check Prometheus
    local prometheus_pod=$(kubectl get pods -n $NAMESPACE -l app=prometheus -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$prometheus_pod" ]]; then
        local prometheus_status=$(kubectl get pod -n $NAMESPACE $prometheus_pod -o jsonpath='{.status.phase}')
        if [[ "$prometheus_status" == "Running" ]]; then
            log_info "✓ Prometheus is running"
        else
            log_error "✗ Prometheus not running (status: $prometheus_status)"
            monitoring_issues+=("prometheus")
        fi
    else
        log_warn "⚠ Prometheus pod not found"
        monitoring_issues+=("prometheus")
    fi
    
    # Check Grafana
    local grafana_pod=$(kubectl get pods -n $NAMESPACE -l app=grafana -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$grafana_pod" ]]; then
        local grafana_status=$(kubectl get pod -n $NAMESPACE $grafana_pod -o jsonpath='{.status.phase}')
        if [[ "$grafana_status" == "Running" ]]; then
            log_info "✓ Grafana is running"
        else
            log_error "✗ Grafana not running (status: $grafana_status)"
            monitoring_issues+=("grafana")
        fi
    else
        log_warn "⚠ Grafana pod not found"
        monitoring_issues+=("grafana")
    fi
    
    # Check OPA
    local opa_pod=$(kubectl get pods -n $NAMESPACE -l app=opa -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [[ -n "$opa_pod" ]]; then
        local opa_status=$(kubectl get pod -n $NAMESPACE $opa_pod -o jsonpath='{.status.phase}')
        if [[ "$opa_status" == "Running" ]]; then
            log_info "✓ OPA is running"
        else
            log_error "✗ OPA not running (status: $opa_status)"
            monitoring_issues+=("opa")
        fi
    else
        log_warn "⚠ OPA pod not found"
        monitoring_issues+=("opa")
    fi
    
    if [[ ${#monitoring_issues[@]} -eq 0 ]]; then
        return 0
    else
        log_warn "Monitoring issues detected: ${monitoring_issues[*]}"
        return 1
    fi
}

# Generate health report
generate_health_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="/tmp/acgs_health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS-PGP Health Report"
        echo "Generated: $timestamp"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "Namespace: $NAMESPACE"
        echo "=========================="
        echo
        
        echo "Service Status:"
        for service in "${!SERVICES[@]}"; do
            local port="${SERVICES[$service]}"
            local pod_status=$(kubectl get pods -n $NAMESPACE -l app=$service -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")
            echo "  $service:$port - $pod_status"
        done
        echo
        
        echo "Resource Usage:"
        kubectl top pods -n $NAMESPACE 2>/dev/null || echo "  Metrics not available"
        echo
        
        echo "Recent Events:"
        kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
        
    } > "$report_file"
    
    log_health "Health report generated: $report_file"
    echo "$report_file"
}

# Continuous monitoring mode
continuous_monitor() {
    log_health "Starting continuous monitoring (interval: ${CHECK_INTERVAL}s)..."
    log_health "Press Ctrl+C to stop monitoring"
    
    while true; do
        echo
        log_health "=== Health Check Cycle ==="
        
        local check_results=()
        
        check_service_health && check_results+=("services:OK") || check_results+=("services:FAIL")
        check_constitutional_compliance && check_results+=("compliance:OK") || check_results+=("compliance:FAIL")
        check_resource_utilization && check_results+=("resources:OK") || check_results+=("resources:WARN")
        check_database_connectivity && check_results+=("database:OK") || check_results+=("database:FAIL")
        check_monitoring_systems && check_results+=("monitoring:OK") || check_results+=("monitoring:WARN")
        
        # Summary
        local failed_checks=$(printf '%s\n' "${check_results[@]}" | grep -c "FAIL" || echo "0")
        local warning_checks=$(printf '%s\n' "${check_results[@]}" | grep -c "WARN" || echo "0")
        
        if [[ $failed_checks -eq 0 ]] && [[ $warning_checks -eq 0 ]]; then
            log_health "✅ All systems healthy"
        elif [[ $failed_checks -eq 0 ]]; then
            log_health "⚠️ Systems operational with warnings ($warning_checks warnings)"
        else
            log_health "❌ System issues detected ($failed_checks failures, $warning_checks warnings)"
        fi
        
        sleep $CHECK_INTERVAL
    done
}

# Main function
main() {
    local action=${1:-"check"}
    
    case $action in
        "check")
            log_health "Running single health check..."
            check_service_health
            check_constitutional_compliance
            check_resource_utilization
            check_database_connectivity
            check_monitoring_systems
            log_health "Health check completed"
            ;;
        "monitor")
            continuous_monitor
            ;;
        "report")
            generate_health_report
            ;;
        "services")
            check_service_health
            ;;
        "compliance")
            check_constitutional_compliance
            ;;
        "resources")
            check_resource_utilization
            ;;
        "database")
            check_database_connectivity
            ;;
        *)
            echo "Usage: $0 {check|monitor|report|services|compliance|resources|database}"
            echo "  check       - Run single comprehensive health check"
            echo "  monitor     - Continuous monitoring mode"
            echo "  report      - Generate detailed health report"
            echo "  services    - Check service health only"
            echo "  compliance  - Check constitutional compliance only"
            echo "  resources   - Check resource utilization only"
            echo "  database    - Check database connectivity only"
            exit 1
            ;;
    esac
}

main "$@"
