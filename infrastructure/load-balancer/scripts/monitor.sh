# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# HAProxy Monitoring Script for ACGS-1 Load Balancer
# Continuous monitoring of load balancer performance and backend health

set -euo pipefail

# Configuration
HAPROXY_STATS_URL="http://localhost:8080/stats"
HAPROXY_ADMIN_SOCKET="/var/run/haproxy/admin.sock"
LOG_FILE="/var/log/haproxy/monitor.log"
METRICS_FILE="/var/log/haproxy/metrics.json"
MONITOR_INTERVAL=30  # seconds
ALERT_THRESHOLD_ERROR_RATE=5.0  # percentage
ALERT_THRESHOLD_RESPONSE_TIME=500  # milliseconds

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Get HAProxy statistics
get_haproxy_stats() {
    curl -s "$HAPROXY_STATS_URL;csv" 2>/dev/null || echo ""
}

# Parse backend statistics
parse_backend_stats() {
    local stats="$1"
    local backend="$2"
    
    echo "$stats" | grep "^$backend," | head -1
}

# Calculate error rate
calculate_error_rate() {
    local total_requests="$1"
    local error_requests="$2"
    
    if [ "$total_requests" -gt 0 ]; then
        echo "scale=2; ($error_requests * 100) / $total_requests" | bc -l
    else
        echo "0"
    fi
}

# Check service health
check_service_health() {
    local backend="$1"
    local stats
    stats=$(get_haproxy_stats)
    
    if [ -z "$stats" ]; then
        log "⚠ Unable to retrieve HAProxy statistics"
        return 1
    fi
    
    local backend_stats
    backend_stats=$(parse_backend_stats "$stats" "$backend")
    
    if [ -z "$backend_stats" ]; then
        log "⚠ No statistics found for backend: $backend"
        return 1
    fi
    
    # Parse CSV fields (simplified)
    IFS=',' read -ra FIELDS <<< "$backend_stats"
    local status="${FIELDS[17]:-UNKNOWN}"
    local current_sessions="${FIELDS[4]:-0}"
    local total_requests="${FIELDS[7]:-0}"
    local error_requests="${FIELDS[13]:-0}"
    
    # Calculate metrics
    local error_rate
    error_rate=$(calculate_error_rate "$total_requests" "$error_requests")
    
    # Log status
    log "Backend $backend: Status=$status, Sessions=$current_sessions, Requests=$total_requests, Errors=$error_requests, Error Rate=$error_rate%"
    
    # Check for alerts
    if (( $(echo "$error_rate > $ALERT_THRESHOLD_ERROR_RATE" | bc -l) )); then
        log "🚨 ALERT: High error rate for $backend: $error_rate%"
    fi
    
    if [ "$status" != "UP" ]; then
        log "🚨 ALERT: Backend $backend is not UP: $status"
    fi
    
    return 0
}

# Generate metrics JSON
generate_metrics() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local stats
    stats=$(get_haproxy_stats)
    
    if [ -z "$stats" ]; then
        return 1
    fi
    
    # Initialize metrics object
    cat > "$METRICS_FILE" << EOF
{
  "timestamp": "$timestamp",
  "load_balancer": {
    "status": "healthy",
    "version": "2.8",
    "uptime_seconds": $(cat /proc/uptime | cut -d' ' -f1 | cut -d'.' -f1)
  },
  "backends": {
EOF
    
    local backends=("auth_backend" "ac_backend" "integrity_backend" "fv_backend" "gs_backend" "pgc_backend" "ec_backend")
    local first=true
    
    for backend in "${backends[@]}"; do
        local backend_stats
        backend_stats=$(parse_backend_stats "$stats" "$backend")
        
        if [ -n "$backend_stats" ]; then
            IFS=',' read -ra FIELDS <<< "$backend_stats"
            local status="${FIELDS[17]:-UNKNOWN}"
            local current_sessions="${FIELDS[4]:-0}"
            local total_requests="${FIELDS[7]:-0}"
            local error_requests="${FIELDS[13]:-0}"
            local response_time="${FIELDS[58]:-0}"
            
            local error_rate
            error_rate=$(calculate_error_rate "$total_requests" "$error_requests")
            
            if [ "$first" = true ]; then
                first=false
            else
                echo "," >> "$METRICS_FILE"
            fi
            
            cat >> "$METRICS_FILE" << EOF
    "$backend": {
      "status": "$status",
      "current_sessions": $current_sessions,
      "total_requests": $total_requests,
      "error_requests": $error_requests,
      "error_rate_percent": $error_rate,
      "avg_response_time_ms": $response_time,
      "healthy": $([ "$status" = "UP" ] && echo "true" || echo "false")
    }EOF
        fi
    done
    
    cat >> "$METRICS_FILE" << EOF

  },
  "performance": {
    "target_response_time_ms": 500,
    "target_availability_percent": 99.9,
    "target_concurrent_users": 1000
  }
}
EOF
}

# Check overall system health
check_system_health() {
    local healthy_backends=0
    local total_backends=7
    local backends=("auth_backend" "ac_backend" "integrity_backend" "fv_backend" "gs_backend" "pgc_backend" "ec_backend")
    
    for backend in "${backends[@]}"; do
        if check_service_health "$backend"; then
            ((healthy_backends++))
        fi
    done
    
    local health_percentage=$((healthy_backends * 100 / total_backends))
    
    log "System Health: $healthy_backends/$total_backends backends healthy ($health_percentage%)"
    
    if [ $health_percentage -lt 80 ]; then
        log "🚨 CRITICAL: System health below 80%"
    elif [ $health_percentage -lt 90 ]; then
        log "⚠ WARNING: System health below 90%"
    else
        log "✓ System health is good"
    fi
}

# Performance monitoring
monitor_performance() {
    local stats
    stats=$(get_haproxy_stats)
    
    if [ -z "$stats" ]; then
        return 1
    fi
    
    # Calculate total active sessions across all backends
    local total_sessions=0
    local backends=("auth_backend" "ac_backend" "integrity_backend" "fv_backend" "gs_backend" "pgc_backend" "ec_backend")
    
    for backend in "${backends[@]}"; do
        local backend_stats
        backend_stats=$(parse_backend_stats "$stats" "$backend")
        
        if [ -n "$backend_stats" ]; then
            IFS=',' read -ra FIELDS <<< "$backend_stats"
            local current_sessions="${FIELDS[4]:-0}"
            total_sessions=$((total_sessions + current_sessions))
        fi
    done
    
    log "Performance: Total active sessions: $total_sessions"
    
    # Check if approaching capacity
    if [ $total_sessions -gt 800 ]; then
        log "⚠ WARNING: High load detected - $total_sessions active sessions"
    fi
    
    if [ $total_sessions -gt 1000 ]; then
        log "🚨 CRITICAL: Very high load - $total_sessions active sessions (target: 1000)"
    fi
}

# Main monitoring loop
main() {
    log "Starting HAProxy monitoring (interval: ${MONITOR_INTERVAL}s)"
    
    while true; do
        log "--- Monitoring Cycle ---"
        
        # Generate metrics
        if generate_metrics; then
            log "✓ Metrics generated successfully"
        else
            log "✗ Failed to generate metrics"
        fi
        
        # Check system health
        check_system_health
        
        # Monitor performance
        monitor_performance
        
        log "--- End Monitoring Cycle ---"
        
        # Wait for next cycle
        sleep $MONITOR_INTERVAL
    done
}

# Handle shutdown gracefully
shutdown_handler() {
    log "Monitoring shutdown requested"
    exit 0
}

trap shutdown_handler SIGTERM SIGINT

# Execute main function
main "$@"
