# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# HAProxy Startup Script for ACGS-1 Load Balancer
# Handles graceful startup with configuration validation and monitoring

set -euo pipefail

# Configuration
HAPROXY_CONFIG="/usr/local/etc/haproxy/haproxy.cfg"
HAPROXY_PID_FILE="/var/run/haproxy/haproxy.pid"
LOG_FILE="/var/log/haproxy/startup.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Logging function
log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Validate HAProxy configuration
validate_config() {
    log "Validating HAProxy configuration..."
    
    if haproxy -f "$HAPROXY_CONFIG" -c; then
        log "✓ HAProxy configuration is valid"
        return 0
    else
        log "✗ HAProxy configuration validation failed"
        return 1
    fi
}

# Create necessary directories and files
setup_environment() {
    log "Setting up HAProxy environment..."
    
    # Ensure directories exist
    mkdir -p /var/run/haproxy /var/log/haproxy
    
    # Set proper permissions
    chown -R haproxy:haproxy /var/run/haproxy /var/log/haproxy
    
    # Create PID file
    touch "$HAPROXY_PID_FILE"
    chown haproxy:haproxy "$HAPROXY_PID_FILE"
    
    log "✓ Environment setup completed"
}

# Generate self-signed SSL certificate if not present
setup_ssl() {
    local ssl_cert="/etc/ssl/certs/acgs.pem"
    
    if [ ! -f "$ssl_cert" ]; then
        log "Generating self-signed SSL certificate..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /tmp/acgs.key \
            -out /tmp/acgs.crt \
            -subj "/C=US/ST=CA/L=San Francisco/O=ACGS/OU=Load Balancer/CN=acgs.local"
        
        # Combine certificate and key for HAProxy
        cat /tmp/acgs.crt /tmp/acgs.key > "$ssl_cert"
        chmod 600 "$ssl_cert"
        chown haproxy:haproxy "$ssl_cert"
        
        # Clean up temporary files
        rm -f /tmp/acgs.key /tmp/acgs.crt
        
        log "✓ SSL certificate generated"
    else
        log "✓ SSL certificate already exists"
    fi
}

# Wait for backend services to be available
wait_for_backends() {
    log "Waiting for backend services to be available..."
    
    local services=(
        "auth_service:8000"
        "ac_service:8001"
        "integrity_service:8002"
        "fv_service:8003"
        "gs_service:8004"
        "pgc_service:8005"
        "ec_service:8006"
    )
    
    local max_wait=300  # 5 minutes
    local wait_time=0
    local all_ready=false
    
    while [ $wait_time -lt $max_wait ] && [ "$all_ready" = false ]; do
        all_ready=true
        
        for service in "${services[@]}"; do
            host=$(echo "$service" | cut -d: -f1)
            port=$(echo "$service" | cut -d: -f2)
            
            if ! nc -z "$host" "$port" 2>/dev/null; then
                all_ready=false
                break
            fi
        done
        
        if [ "$all_ready" = false ]; then
            log "Waiting for backend services... ($wait_time/$max_wait seconds)"
            sleep 10
            wait_time=$((wait_time + 10))
        fi
    done
    
    if [ "$all_ready" = true ]; then
        log "✓ All backend services are available"
        return 0
    else
        log "⚠ Some backend services are not available, starting anyway"
        return 0  # Don't fail startup, HAProxy will handle unavailable backends
    fi
}

# Start monitoring in background
start_monitoring() {
    log "Starting background monitoring..."
    
    # Start monitoring script in background
    if [ -f "/usr/local/bin/monitor.sh" ]; then
        /usr/local/bin/monitor.sh &
        log "✓ Background monitoring started"
    else
        log "⚠ Monitoring script not found, skipping"
    fi
}

# Graceful shutdown handler
shutdown_handler() {
    log "Received shutdown signal, stopping HAProxy gracefully..."
    
    if [ -f "$HAPROXY_PID_FILE" ]; then
        local pid=$(cat "$HAPROXY_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid"
            
            # Wait for graceful shutdown
            local wait_time=0
            while kill -0 "$pid" 2>/dev/null && [ $wait_time -lt 30 ]; do
                sleep 1
                wait_time=$((wait_time + 1))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                log "Force killing HAProxy process"
                kill -KILL "$pid"
            fi
        fi
    fi
    
    log "HAProxy shutdown completed"
    exit 0
}

# Set up signal handlers
trap shutdown_handler SIGTERM SIGINT

# Main startup function
main() {
    log "Starting ACGS-1 HAProxy Load Balancer..."
    
    # Setup environment
    setup_environment
    
    # Validate configuration
    if ! validate_config; then
        log "✗ Configuration validation failed, exiting"
        exit 1
    fi
    
    # Setup SSL
    setup_ssl
    
    # Wait for backends (optional)
    wait_for_backends
    
    # Start monitoring
    start_monitoring
    
    # Start HAProxy
    log "Starting HAProxy with configuration: $HAPROXY_CONFIG"
    
    exec haproxy -f "$HAPROXY_CONFIG" -D -p "$HAPROXY_PID_FILE"
}

# Execute main function
main "$@"
