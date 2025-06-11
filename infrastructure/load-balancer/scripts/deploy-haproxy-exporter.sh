#!/bin/bash
# HAProxy Prometheus Exporter Deployment Script for ACGS-1
# Subtask 13.6: Integrate with Load Balancing Infrastructure
# Target: >99.9% availability, <500ms response times, >1000 concurrent users

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HAPROXY_EXPORTER_VERSION="v0.15.0"
EXPORTER_USER="prometheus"
EXPORTER_GROUP="prometheus"
EXPORTER_PORT="9101"
HAPROXY_STATS_URL="http://localhost:8080/stats;csv"
HAPROXY_USERNAME="admin"
HAPROXY_PASSWORD="acgs_haproxy_admin_2024"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "/var/log/acgs/haproxy-exporter-deploy.log"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites for HAProxy exporter deployment..."
    
    # Check if HAProxy is running
    if ! systemctl is-active --quiet haproxy; then
        error_exit "HAProxy service is not running. Please start HAProxy first."
    fi
    
    # Check if HAProxy stats endpoint is accessible
    if ! curl -s --user "$HAPROXY_USERNAME:$HAPROXY_PASSWORD" "$HAPROXY_STATS_URL" > /dev/null; then
        error_exit "HAProxy stats endpoint is not accessible"
    fi
    
    # Check if port 9101 is available
    if netstat -tuln | grep -q ":$EXPORTER_PORT "; then
        log "WARNING: Port $EXPORTER_PORT is already in use"
    fi
    
    # Check if prometheus user exists
    if ! id "$EXPORTER_USER" &>/dev/null; then
        log "Creating prometheus user..."
        sudo useradd --system --no-create-home --shell /bin/false "$EXPORTER_USER" || true
    fi
    
    log "✓ Prerequisites check completed"
}

# Download and install HAProxy exporter
install_haproxy_exporter() {
    log "Installing HAProxy Prometheus Exporter $HAPROXY_EXPORTER_VERSION..."
    
    local temp_dir="/tmp/haproxy-exporter-install"
    mkdir -p "$temp_dir"
    cd "$temp_dir"
    
    # Download HAProxy exporter
    local download_url="https://github.com/prometheus/haproxy_exporter/releases/download/$HAPROXY_EXPORTER_VERSION/haproxy_exporter-${HAPROXY_EXPORTER_VERSION#v}.linux-amd64.tar.gz"
    
    log "Downloading from: $download_url"
    wget -q "$download_url" -O haproxy_exporter.tar.gz || error_exit "Failed to download HAProxy exporter"
    
    # Extract and install
    tar -xzf haproxy_exporter.tar.gz
    local extracted_dir="haproxy_exporter-${HAPROXY_EXPORTER_VERSION#v}.linux-amd64"
    
    if [ ! -f "$extracted_dir/haproxy_exporter" ]; then
        error_exit "HAProxy exporter binary not found in extracted archive"
    fi
    
    # Install binary
    sudo cp "$extracted_dir/haproxy_exporter" /usr/local/bin/
    sudo chown root:root /usr/local/bin/haproxy_exporter
    sudo chmod 755 /usr/local/bin/haproxy_exporter
    
    # Cleanup
    cd /
    rm -rf "$temp_dir"
    
    log "✓ HAProxy exporter installed successfully"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service for HAProxy exporter..."
    
    sudo tee /etc/systemd/system/acgs-haproxy-exporter.service > /dev/null << EOF
[Unit]
Description=HAProxy Prometheus Exporter for ACGS-1
Documentation=https://github.com/prometheus/haproxy_exporter
After=network.target haproxy.service
Requires=haproxy.service

[Service]
Type=simple
User=$EXPORTER_USER
Group=$EXPORTER_GROUP
ExecStart=/usr/local/bin/haproxy_exporter \\
    --haproxy.scrape-uri=$HAPROXY_STATS_URL \\
    --haproxy.ssl-verify=false \\
    --haproxy.timeout=5s \\
    --web.listen-address=:$EXPORTER_PORT \\
    --web.telemetry-path=/metrics \\
    --log.level=info
Environment=HAPROXY_USERNAME=$HAPROXY_USERNAME
Environment=HAPROXY_PASSWORD=$HAPROXY_PASSWORD
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=acgs-haproxy-exporter

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=/var/log/acgs

# Resource limits
MemoryLimit=128M
CPUQuota=10%

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable acgs-haproxy-exporter.service
    
    log "✓ Systemd service created and enabled"
}

# Start HAProxy exporter service
start_exporter_service() {
    log "Starting HAProxy exporter service..."
    
    sudo systemctl start acgs-haproxy-exporter.service
    
    # Wait for service to start
    sleep 5
    
    # Check service status
    if systemctl is-active --quiet acgs-haproxy-exporter.service; then
        log "✓ HAProxy exporter service started successfully"
    else
        error_exit "Failed to start HAProxy exporter service"
    fi
    
    # Check if metrics endpoint is accessible
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$EXPORTER_PORT/metrics" > /dev/null; then
            log "✓ HAProxy exporter metrics endpoint is accessible"
            break
        fi
        
        log "Waiting for metrics endpoint... (attempt $attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error_exit "HAProxy exporter metrics endpoint is not accessible after $max_attempts attempts"
    fi
}

# Update Prometheus configuration
update_prometheus_config() {
    log "Updating Prometheus configuration..."
    
    local prometheus_config="$PROJECT_ROOT/infrastructure/monitoring/prometheus.yml"
    
    # Check if HAProxy exporter job already exists
    if grep -q "job_name: 'haproxy-exporter'" "$prometheus_config"; then
        log "HAProxy exporter job already exists in Prometheus configuration"
        return 0
    fi
    
    # Add HAProxy exporter job to Prometheus configuration
    local temp_config="/tmp/prometheus-updated.yml"
    
    # Insert the new job configuration after the existing haproxy-stats job
    awk '
    /job_name: .haproxy-stats./ {
        print
        # Print the existing haproxy-stats job
        while (getline && !/^  - job_name:/ && !/^scrape_configs:/ && !/^$/) {
            print
        }
        # Add the new haproxy-exporter job
        print ""
        print "  # HAProxy Prometheus Exporter (Subtask 13.6)"
        print "  - job_name: '\''haproxy-exporter'\''"
        print "    static_configs:"
        print "      - targets: ['\''localhost:9101'\'']"
        print "    scrape_interval: 15s"
        print "    scrape_timeout: 10s"
        print "    metric_relabel_configs:"
        print "      - source_labels: [__name__]"
        print "        regex: '\''haproxy_.*'\''"
        print "        target_label: '\''component'\''"
        print "        replacement: '\''load_balancer'\''"
        print "      - source_labels: [proxy]"
        print "        regex: '\''(.*)_backend'\''"
        print "        target_label: '\''acgs_service'\''"
        print "        replacement: '\''${1}'\''"
        print ""
        # Print the current line (which should be the next job or section)
        if (!/^$/) print
    }
    !/job_name: .haproxy-stats./ { print }
    ' "$prometheus_config" > "$temp_config"
    
    # Validate the updated configuration
    if prometheus --config.file="$temp_config" --dry-run 2>/dev/null; then
        sudo cp "$temp_config" "$prometheus_config"
        log "✓ Prometheus configuration updated successfully"
        
        # Reload Prometheus configuration
        if systemctl is-active --quiet prometheus; then
            sudo systemctl reload prometheus || log "WARNING: Failed to reload Prometheus"
        fi
    else
        error_exit "Invalid Prometheus configuration generated"
    fi
    
    rm -f "$temp_config"
}

# Validate deployment
validate_deployment() {
    log "Validating HAProxy exporter deployment..."
    
    # Check service status
    if ! systemctl is-active --quiet acgs-haproxy-exporter.service; then
        error_exit "HAProxy exporter service is not running"
    fi
    
    # Check metrics endpoint
    local metrics_response
    metrics_response=$(curl -s "http://localhost:$EXPORTER_PORT/metrics" | head -20)
    
    if [[ "$metrics_response" == *"haproxy_"* ]]; then
        log "✓ HAProxy metrics are being exported correctly"
    else
        error_exit "HAProxy metrics are not being exported"
    fi
    
    # Check specific ACGS metrics
    local expected_metrics=(
        "haproxy_server_status"
        "haproxy_server_current_sessions"
        "haproxy_server_response_time_average_seconds"
        "haproxy_backend_current_sessions"
        "haproxy_backend_response_time_average_seconds"
    )
    
    for metric in "${expected_metrics[@]}"; do
        if curl -s "http://localhost:$EXPORTER_PORT/metrics" | grep -q "$metric"; then
            log "✓ Metric $metric is available"
        else
            log "WARNING: Metric $metric is not available"
        fi
    done
    
    # Check backend health metrics
    local backends=("auth_backend" "ac_backend" "integrity_backend" "fv_backend" "gs_backend" "pgc_backend" "ec_backend")
    
    for backend in "${backends[@]}"; do
        if curl -s "http://localhost:$EXPORTER_PORT/metrics" | grep -q "proxy=\"$backend\""; then
            log "✓ Backend $backend metrics are available"
        else
            log "WARNING: Backend $backend metrics are not available"
        fi
    done
    
    log "✓ Deployment validation completed"
}

# Generate deployment report
generate_deployment_report() {
    log "Generating deployment report..."
    
    local report_file="/var/log/acgs/haproxy-exporter-deployment-report.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$report_file" << EOF
{
  "deployment": {
    "timestamp": "$timestamp",
    "component": "haproxy-prometheus-exporter",
    "version": "$HAPROXY_EXPORTER_VERSION",
    "status": "completed",
    "subtask": "13.6"
  },
  "configuration": {
    "exporter_port": $EXPORTER_PORT,
    "haproxy_stats_url": "$HAPROXY_STATS_URL",
    "metrics_endpoint": "http://localhost:$EXPORTER_PORT/metrics",
    "systemd_service": "acgs-haproxy-exporter.service"
  },
  "integration": {
    "prometheus_job": "haproxy-exporter",
    "grafana_dashboard": "load-balancing-dashboard",
    "alert_rules": "infrastructure_alerts.yml"
  },
  "validation": {
    "service_running": $(systemctl is-active --quiet acgs-haproxy-exporter.service && echo "true" || echo "false"),
    "metrics_accessible": $(curl -s "http://localhost:$EXPORTER_PORT/metrics" > /dev/null && echo "true" || echo "false"),
    "haproxy_integration": $(curl -s "http://localhost:$EXPORTER_PORT/metrics" | grep -q "haproxy_" && echo "true" || echo "false")
  },
  "performance_targets": {
    "response_time_target": "<500ms",
    "availability_target": ">99.9%",
    "concurrent_users_target": ">1000"
  }
}
EOF
    
    log "✓ Deployment report generated: $report_file"
}

# Main deployment function
main() {
    log "Starting HAProxy Prometheus Exporter deployment for ACGS-1 Subtask 13.6"
    
    # Create log directory
    sudo mkdir -p /var/log/acgs
    sudo chown "$USER:$USER" /var/log/acgs
    
    # Execute deployment steps
    check_prerequisites
    install_haproxy_exporter
    create_systemd_service
    start_exporter_service
    update_prometheus_config
    validate_deployment
    generate_deployment_report
    
    log "✅ HAProxy Prometheus Exporter deployment completed successfully"
    log "📊 Metrics endpoint: http://localhost:$EXPORTER_PORT/metrics"
    log "🔧 Service status: sudo systemctl status acgs-haproxy-exporter.service"
    log "📋 Logs: sudo journalctl -u acgs-haproxy-exporter.service -f"
}

# Handle script termination
cleanup() {
    log "Deployment script interrupted"
    exit 1
}

trap cleanup SIGINT SIGTERM

# Execute main function
main "$@"
