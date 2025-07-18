# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
set -euo pipefail

# ACGS-1 Lite Health Check Script
# Comprehensive system health monitoring and validation

# Configuration
NAMESPACE_GOVERNANCE="governance"
NAMESPACE_WORKLOAD="workload"
NAMESPACE_MONITORING="monitoring"
NAMESPACE_SHARED="shared"

# Health check thresholds
POLICY_LATENCY_THRESHOLD_MS=5
COMPLIANCE_RATE_THRESHOLD=0.99
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Health status tracking
HEALTH_SCORE=0
MAX_HEALTH_SCORE=0
FAILED_CHECKS=()

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((HEALTH_SCORE++))
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    FAILED_CHECKS+=("$1")
}

# Increment max score for each check
check_start() {
    ((MAX_HEALTH_SCORE++))
}

# Check Kubernetes cluster health
check_cluster_health() {
    log_info "Checking Kubernetes cluster health..."
    check_start
    
    # Check node status
    local ready_nodes=$(kubectl get nodes --no-headers | grep -c " Ready ")
    local total_nodes=$(kubectl get nodes --no-headers | wc -l)
    
    if [[ $ready_nodes -eq $total_nodes ]] && [[ $total_nodes -gt 0 ]]; then
        log_success "Cluster health: $ready_nodes/$total_nodes nodes ready"
    else
        log_error "Cluster health: Only $ready_nodes/$total_nodes nodes ready"
        return 1
    fi
}

# Check namespace health
check_namespace_health() {
    log_info "Checking namespace health..."
    
    local namespaces=("$NAMESPACE_GOVERNANCE" "$NAMESPACE_WORKLOAD" "$NAMESPACE_MONITORING" "$NAMESPACE_SHARED")
    
    for ns in "${namespaces[@]}"; do
        check_start
        if kubectl get namespace "$ns" >/dev/null 2>&1; then
            log_success "Namespace $ns exists and is active"
        else
            log_error "Namespace $ns is missing or not active"
        fi
    done
}

# Check deployment health
check_deployment_health() {
    log_info "Checking deployment health..."
    
    local deployments=(
        "$NAMESPACE_GOVERNANCE:policy-engine"
        "$NAMESPACE_GOVERNANCE:opa"
        "$NAMESPACE_WORKLOAD:sandbox-controller"
        "$NAMESPACE_MONITORING:prometheus"
        "$NAMESPACE_MONITORING:grafana"
        "$NAMESPACE_MONITORING:alertmanager"
    )
    
    for deployment in "${deployments[@]}"; do
        check_start
        local ns=$(echo "$deployment" | cut -d: -f1)
        local name=$(echo "$deployment" | cut -d: -f2)
        
        local ready=$(kubectl get deployment "$name" -n "$ns" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        local desired=$(kubectl get deployment "$name" -n "$ns" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
        
        if [[ "$ready" == "$desired" ]] && [[ "$ready" -gt 0 ]]; then
            log_success "Deployment $ns/$name: $ready/$desired replicas ready"
        else
            log_error "Deployment $ns/$name: Only $ready/$desired replicas ready"
        fi
    done
}

# Check service endpoints
check_service_endpoints() {
    log_info "Checking service endpoints..."
    
    local services=(
        "$NAMESPACE_GOVERNANCE:policy-engine:8001"
        "$NAMESPACE_GOVERNANCE:opa:8181"
        "$NAMESPACE_WORKLOAD:sandbox-controller:8004"
        "$NAMESPACE_SHARED:constitutional-postgres-rw:5432"
        "$NAMESPACE_SHARED:constitutional-events-kafka:9092"
    )
    
    for service in "${services[@]}"; do
        check_start
        local ns=$(echo "$service" | cut -d: -f1)
        local name=$(echo "$service" | cut -d: -f2)
        local port=$(echo "$service" | cut -d: -f3)
        
        if kubectl get service "$name" -n "$ns" >/dev/null 2>&1; then
            local endpoints=$(kubectl get endpoints "$name" -n "$ns" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null | wc -w)
            if [[ $endpoints -gt 0 ]]; then
                log_success "Service $ns/$name: $endpoints endpoints available"
            else
                log_error "Service $ns/$name: No endpoints available"
            fi
        else
            log_error "Service $ns/$name: Service not found"
        fi
    done
}

# Check Policy Engine health
check_policy_engine_health() {
    log_info "Checking Policy Engine health..."
    check_start
    
    # Port forward to Policy Engine
    kubectl port-forward svc/policy-engine 8001:8001 -n $NAMESPACE_GOVERNANCE >/dev/null 2>&1 &
    local port_forward_pid=$!
    sleep 3
    
    # Test health endpoint
    if curl -f -s http://localhost:8001/health >/dev/null 2>&1; then
        log_success "Policy Engine health endpoint responding"
        
        # Test policy evaluation
        check_start
        local start_time=$(date +%s%3N)
        local response=$(curl -s -X POST http://localhost:8001/v1/evaluate \
            -H "Content-Type: application/json" \
            -d '{
                "action": "evolve_agent",
                "agent_id": "health-check-agent",
                "input_data": {
                    "fitness_improvement": 0.06,
                    "safety_score": 0.96,
                    "constitutional_compliance": 0.995
                }
            }' 2>/dev/null || echo "")
        local end_time=$(date +%s%3N)
        local latency=$((end_time - start_time))
        
        if [[ -n "$response" ]] && echo "$response" | jq -e '.allow' >/dev/null 2>&1; then
            if [[ $latency -le $POLICY_LATENCY_THRESHOLD_MS ]]; then
                log_success "Policy evaluation: ${latency}ms (threshold: ${POLICY_LATENCY_THRESHOLD_MS}ms)"
            else
                log_warning "Policy evaluation: ${latency}ms exceeds threshold of ${POLICY_LATENCY_THRESHOLD_MS}ms"
            fi
        else
            log_error "Policy evaluation failed or returned invalid response"
        fi
    else
        log_error "Policy Engine health endpoint not responding"
    fi
    
    # Clean up port forward
    kill $port_forward_pid 2>/dev/null || true
}

# Check database health
check_database_health() {
    log_info "Checking database health..."
    check_start
    
    # Check PostgreSQL cluster status
    local cluster_status=$(kubectl get cluster constitutional-postgres -n $NAMESPACE_SHARED -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
    
    if [[ "$cluster_status" == "Cluster in healthy state" ]] || [[ "$cluster_status" == "Ready" ]]; then
        log_success "PostgreSQL cluster status: $cluster_status"
        
        # Test database connectivity
        check_start
        if kubectl exec -it constitutional-postgres-1 -n $NAMESPACE_SHARED -- psql -U postgres -d acgs_lite -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "Database connectivity test passed"
            
            # Check table counts
            check_start
            local policy_count=$(kubectl exec -it constitutional-postgres-1 -n $NAMESPACE_SHARED -- psql -U postgres -d acgs_lite -t -c "SELECT COUNT(*) FROM constitutional_policies;" 2>/dev/null | tr -d ' \n\r' || echo "0")
            if [[ $policy_count -gt 0 ]]; then
                log_success "Database contains $policy_count constitutional policies"
            else
                log_warning "Database contains no constitutional policies"
            fi
        else
            log_error "Database connectivity test failed"
        fi
    else
        log_error "PostgreSQL cluster status: $cluster_status"
    fi
}

# Check event streaming health
check_event_streaming_health() {
    log_info "Checking event streaming health..."
    check_start
    
    # Check RedPanda cluster status
    if kubectl get redpanda constitutional-events -n $NAMESPACE_SHARED >/dev/null 2>&1; then
        log_success "RedPanda cluster exists"
        
        # Check topics
        check_start
        local topics=$(kubectl exec -it constitutional-events-0 -n $NAMESPACE_SHARED -- rpk topic list 2>/dev/null | grep -c "constitutional\|audit\|policy\|sandbox" || echo "0")
        if [[ $topics -ge 4 ]]; then
            log_success "Event streaming: $topics topics configured"
        else
            log_warning "Event streaming: Only $topics topics found (expected 6+)"
        fi
    else
        log_error "RedPanda cluster not found"
    fi
}

# Check monitoring health
check_monitoring_health() {
    log_info "Checking monitoring health..."
    
    # Check Prometheus
    check_start
    kubectl port-forward svc/prometheus 9090:9090 -n $NAMESPACE_MONITORING >/dev/null 2>&1 &
    local prom_pid=$!
    sleep 3
    
    if curl -f -s http://localhost:9090/-/healthy >/dev/null 2>&1; then
        log_success "Prometheus is healthy"
        
        # Check targets
        check_start
        local targets=$(curl -s http://localhost:9090/api/v1/targets 2>/dev/null | jq -r '.data.activeTargets | length' 2>/dev/null || echo "0")
        if [[ $targets -gt 0 ]]; then
            log_success "Prometheus monitoring $targets targets"
        else
            log_warning "Prometheus has no active targets"
        fi
    else
        log_error "Prometheus health check failed"
    fi
    
    kill $prom_pid 2>/dev/null || true
    
    # Check Grafana
    check_start
    kubectl port-forward svc/grafana 3000:3000 -n $NAMESPACE_MONITORING >/dev/null 2>&1 &
    local grafana_pid=$!
    sleep 3
    
    if curl -f -s http://localhost:3000/api/health >/dev/null 2>&1; then
        log_success "Grafana is healthy"
    else
        log_error "Grafana health check failed"
    fi
    
    kill $grafana_pid 2>/dev/null || true
}

# Check resource usage
check_resource_usage() {
    log_info "Checking resource usage..."
    
    # Check node resource usage
    check_start
    local high_cpu_nodes=$(kubectl top nodes --no-headers 2>/dev/null | awk -v threshold=$CPU_THRESHOLD '$3 > threshold {count++} END {print count+0}' || echo "0")
    local high_memory_nodes=$(kubectl top nodes --no-headers 2>/dev/null | awk -v threshold=$MEMORY_THRESHOLD '$5 > threshold {count++} END {print count+0}' || echo "0")
    
    if [[ $high_cpu_nodes -eq 0 ]] && [[ $high_memory_nodes -eq 0 ]]; then
        log_success "Node resource usage within thresholds"
    else
        log_warning "Resource usage: $high_cpu_nodes nodes >$CPU_THRESHOLD% CPU, $high_memory_nodes nodes >$MEMORY_THRESHOLD% memory"
    fi
    
    # Check pod resource usage
    check_start
    local high_usage_pods=$(kubectl top pods --all-namespaces --no-headers 2>/dev/null | awk '$3 ~ /[0-9]+m/ && $3+0 > 1000 {count++} END {print count+0}' || echo "0")
    
    if [[ $high_usage_pods -eq 0 ]]; then
        log_success "Pod resource usage normal"
    else
        log_warning "$high_usage_pods pods using >1000m CPU"
    fi
}

# Check constitutional compliance metrics
check_constitutional_compliance() {
    log_info "Checking constitutional compliance metrics..."
    check_start
    
    # This would typically query Prometheus for actual metrics
    # For now, we'll simulate the check
    kubectl port-forward svc/prometheus 9090:9090 -n $NAMESPACE_MONITORING >/dev/null 2>&1 &
    local prom_pid=$!
    sleep 3
    
    # Query constitutional compliance rate
    local compliance_rate=$(curl -s "http://localhost:9090/api/v1/query?query=constitutional_compliance_rate" 2>/dev/null | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "0")
    
    if [[ $(echo "$compliance_rate >= $COMPLIANCE_RATE_THRESHOLD" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        log_success "Constitutional compliance rate: $(printf "%.3f" "$compliance_rate") (threshold: $COMPLIANCE_RATE_THRESHOLD)"
    else
        log_error "Constitutional compliance rate: $(printf "%.3f" "$compliance_rate") below threshold of $COMPLIANCE_RATE_THRESHOLD"
    fi
    
    kill $prom_pid 2>/dev/null || true
}

# Check security policies
check_security_policies() {
    log_info "Checking security policies..."
    
    # Check network policies
    check_start
    local network_policies=$(kubectl get networkpolicy --all-namespaces --no-headers | wc -l)
    if [[ $network_policies -ge 8 ]]; then
        log_success "Network policies: $network_policies policies active"
    else
        log_warning "Network policies: Only $network_policies policies found (expected 8+)"
    fi
    
    # Check RBAC
    check_start
    local service_accounts=$(kubectl get serviceaccount --all-namespaces --no-headers | grep acgs-lite | wc -l)
    if [[ $service_accounts -ge 4 ]]; then
        log_success "RBAC: $service_accounts ACGS-Lite service accounts configured"
    else
        log_warning "RBAC: Only $service_accounts ACGS-Lite service accounts found"
    fi
}

# Generate health report
generate_health_report() {
    local health_percentage=$((HEALTH_SCORE * 100 / MAX_HEALTH_SCORE))
    
    echo ""
    echo "=================================="
    echo "ACGS-1 Lite Health Check Report"
    echo "=================================="
    echo "Timestamp: $(date)"
    echo "Health Score: $HEALTH_SCORE/$MAX_HEALTH_SCORE ($health_percentage%)"
    echo ""
    
    if [[ $health_percentage -ge 90 ]]; then
        echo -e "${GREEN}System Status: HEALTHY${NC}"
    elif [[ $health_percentage -ge 70 ]]; then
        echo -e "${YELLOW}System Status: WARNING${NC}"
    else
        echo -e "${RED}System Status: CRITICAL${NC}"
    fi
    
    if [[ ${#FAILED_CHECKS[@]} -gt 0 ]]; then
        echo ""
        echo "Failed Checks:"
        for check in "${FAILED_CHECKS[@]}"; do
            echo "  - $check"
        done
    fi
    
    echo ""
    echo "Recommendations:"
    if [[ $health_percentage -lt 100 ]]; then
        echo "  - Review failed checks and take corrective action"
        echo "  - Check system logs for detailed error information"
        echo "  - Consider scaling up resources if performance issues detected"
    else
        echo "  - System is operating normally"
        echo "  - Continue regular monitoring"
    fi
    
    echo ""
    echo "Next Steps:"
    echo "  - Schedule next health check in 1 hour"
    echo "  - Monitor constitutional compliance metrics"
    echo "  - Review audit logs for any violations"
}

# Main health check function
main() {
    log_info "Starting ACGS-1 Lite comprehensive health check..."
    echo ""
    
    # Run all health checks
    check_cluster_health
    check_namespace_health
    check_deployment_health
    check_service_endpoints
    check_policy_engine_health
    check_database_health
    check_event_streaming_health
    check_monitoring_health
    check_resource_usage
    check_constitutional_compliance
    check_security_policies
    
    # Generate report
    generate_health_report
    
    # Exit with appropriate code
    local health_percentage=$((HEALTH_SCORE * 100 / MAX_HEALTH_SCORE))
    if [[ $health_percentage -ge 90 ]]; then
        exit 0
    elif [[ $health_percentage -ge 70 ]]; then
        exit 1
    else
        exit 2
    fi
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
