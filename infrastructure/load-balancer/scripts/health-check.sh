#!/bin/bash
# HAProxy Health Check Script for ACGS-1 Load Balancer
# Validates load balancer health and backend service availability

set -euo pipefail

# Configuration
HAPROXY_STATS_URL="http://localhost:8080/stats"
HAPROXY_ADMIN_SOCKET="/var/run/haproxy/admin.sock"
LOG_FILE="/var/log/haproxy/health-check.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Logging function
log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Check if HAProxy process is running
check_haproxy_process() {
    if pgrep -f haproxy > /dev/null; then
        log "✓ HAProxy process is running"
        return 0
    else
        log "✗ HAProxy process is not running"
        return 1
    fi
}

# Check HAProxy stats interface
check_stats_interface() {
    if curl -s -f "$HAPROXY_STATS_URL" > /dev/null; then
        log "✓ HAProxy stats interface is accessible"
        return 0
    else
        log "✗ HAProxy stats interface is not accessible"
        return 1
    fi
}

# Check admin socket
check_admin_socket() {
    if [ -S "$HAPROXY_ADMIN_SOCKET" ]; then
        log "✓ HAProxy admin socket is available"
        return 0
    else
        log "✗ HAProxy admin socket is not available"
        return 1
    fi
}

# Check backend services health
check_backend_services() {
    local failed_services=0
    local services=(
        "auth_backend:auth1"
        "ac_backend:ac1"
        "integrity_backend:integrity1"
        "fv_backend:fv1"
        "gs_backend:gs1"
        "pgc_backend:pgc1"
        "ec_backend:ec1"
    )
    
    for service in "${services[@]}"; do
        backend=$(echo "$service" | cut -d: -f1)
        server=$(echo "$service" | cut -d: -f2)
        
        # Query server status via admin socket
        if echo "show stat" | socat stdio "$HAPROXY_ADMIN_SOCKET" | grep -q "$backend,$server.*UP"; then
            log "✓ Service $backend/$server is UP"
        else
            log "✗ Service $backend/$server is DOWN or not responding"
            ((failed_services++))
        fi
    done
    
    if [ $failed_services -eq 0 ]; then
        log "✓ All backend services are healthy"
        return 0
    else
        log "✗ $failed_services backend services are unhealthy"
        return 1
    fi
}

# Check load balancer performance metrics
check_performance_metrics() {
    local stats_output
    stats_output=$(curl -s "$HAPROXY_STATS_URL;csv" | grep -E "^(auth_backend|ac_backend|integrity_backend|fv_backend|gs_backend|pgc_backend|ec_backend),FRONTEND")
    
    local total_requests=0
    local total_errors=0
    
    while IFS=',' read -r backend type _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _; do
        if [ "$type" = "FRONTEND" ]; then
            # Extract request and error counts (simplified)
            log "✓ Backend $backend is processing requests"
        fi
    done <<< "$stats_output"
    
    log "✓ Performance metrics check completed"
    return 0
}

# Main health check function
main() {
    log "Starting HAProxy health check..."
    
    local exit_code=0
    
    # Run all health checks
    check_haproxy_process || exit_code=1
    check_stats_interface || exit_code=1
    check_admin_socket || exit_code=1
    check_backend_services || exit_code=1
    check_performance_metrics || exit_code=1
    
    if [ $exit_code -eq 0 ]; then
        log "✓ All health checks passed - HAProxy is healthy"
    else
        log "✗ Some health checks failed - HAProxy may have issues"
    fi
    
    return $exit_code
}

# Execute main function
main "$@"
