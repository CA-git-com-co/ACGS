# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# ACGS-1 PGC Service Restart Script
# Automated remediation for PGC service failures

set -euo pipefail

LOG_FILE="/var/log/acgs/pgc_service_restart.log"
PID_FILE="/var/run/acgs/pgc_service.pid"
SERVICE_PORT=8005

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if service is running
check_service() {
    if curl -s -f "http://localhost:$SERVICE_PORT/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Kill existing process
kill_service() {
    log "Stopping PGC service..."
    
    # Kill by PID file if exists
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid"
            sleep 5
            if kill -0 "$pid" 2>/dev/null; then
                kill -KILL "$pid"
            fi
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill by process name
    pkill -f "pgc_service" || true
    pkill -f "start_with_tracing.py" || true
    
    sleep 3
}

# Start service
start_service() {
    log "Starting PGC service..."
    
    cd /home/dislove/ACGS-1/services/core/policy-governance/pgc_service
    
    # Activate virtual environment and start service
    source /home/dislove/ACGS-1/.venv/bin/activate
    nohup python3 start_with_tracing.py > "$LOG_FILE" 2>&1 &
    
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    log "PGC service started with PID: $pid"
}

# Wait for service to be ready
wait_for_service() {
    log "Waiting for PGC service to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if check_service; then
            log "PGC service is ready and responding"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts - service not ready yet"
        sleep 2
        ((attempt++))
    done
    
    log "ERROR: PGC service failed to start within timeout"
    return 1
}

# Main execution
main() {
    log "=== PGC Service Restart Script Started ==="
    
    # Create necessary directories
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$PID_FILE")"
    
    # Check if service is already running
    if check_service; then
        log "PGC service is already running and healthy"
        exit 0
    fi
    
    # Kill existing process
    kill_service
    
    # Start service
    start_service
    
    # Wait for service to be ready
    if wait_for_service; then
        log "=== PGC Service Restart Completed Successfully ==="
        exit 0
    else
        log "=== PGC Service Restart Failed ==="
        exit 1
    fi
}

# Execute main function
main "$@"
