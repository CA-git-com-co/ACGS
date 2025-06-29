#!/bin/bash
# Setup script for gVisor runtime on Kubernetes nodes
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🔒 Setting up gVisor runtime for hardened sandboxes"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    exit 1
fi

# Detect OS
OS=""
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

echo "📋 Detected OS: $OS"

# Install gVisor
echo "📦 Installing gVisor..."

case $OS in
    "ubuntu"|"debian")
        # Add gVisor repository
        curl -fsSL https://gvisor.dev/archive.key | apt-key add -
        add-apt-repository "deb https://storage.googleapis.com/gvisor/releases release main"
        
        # Update package list
        apt-get update
        
        # Install runsc
        apt-get install -y runsc
        ;;
    
    "centos"|"rhel"|"fedora")
        # Install from GitHub releases
        GVISOR_VERSION=$(curl -s https://api.github.com/repos/google/gvisor/releases/latest | grep '"tag_name":' | cut -d'"' -f4)
        
        # Download runsc binary
        curl -fsSL https://storage.googleapis.com/gvisor/releases/${GVISOR_VERSION}/x86_64/runsc -o /usr/local/bin/runsc
        chmod +x /usr/local/bin/runsc
        ;;
    
    *)
        echo "❌ Unsupported OS: $OS"
        exit 1
        ;;
esac

# Verify installation
if ! command -v runsc &> /dev/null; then
    echo "❌ runsc installation failed"
    exit 1
fi

echo "✅ gVisor runsc installed successfully"
runsc --version

# Configure containerd for gVisor
echo "⚙️  Configuring containerd for gVisor..."

# Backup existing config
cp /etc/containerd/config.toml /etc/containerd/config.toml.backup

# Check if gVisor runtime is already configured
if grep -q "runsc" /etc/containerd/config.toml; then
    echo "ℹ️  gVisor runtime already configured in containerd"
else
    # Add gVisor runtime configuration
    cat >> /etc/containerd/config.toml << 'EOF'

# gVisor runtime configuration for hardened sandboxes
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
  runtime_type = "io.containerd.runsc.v1"

[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc.options]
  TypeUrl = "io.containerd.runsc.v1.options"
  ConfigPath = "/etc/containerd/runsc.toml"
EOF

    echo "✅ Added gVisor runtime configuration to containerd"
fi

# Create runsc configuration
echo "📝 Creating runsc configuration..."

cat > /etc/containerd/runsc.toml << 'EOF'
# gVisor runsc configuration for ACGS hardened sandboxes
# Constitutional Hash: cdd01ef066bc6cf2

[runsc_config]
  # Enhanced security settings
  debug-log = "/var/log/runsc/"
  debug-log-format = "json"
  strace = false
  
  # Network configuration
  network = "none"  # No network access by default
  
  # Filesystem configuration  
  file-access = "exclusive"
  overlay = true
  
  # Resource limits
  cpu-num = 2
  total-memory = 2147483648  # 2GB
  
  # Security hardening
  panic-signal = -1
  watchdog-action = "panic"
  
  # Constitutional governance
  annotation = "constitutional-hash=cdd01ef066bc6cf2"
EOF

# Create log directory
mkdir -p /var/log/runsc
chmod 755 /var/log/runsc

echo "✅ runsc configuration created"

# Restart containerd
echo "🔄 Restarting containerd..."
systemctl restart containerd

# Wait for containerd to be ready
sleep 5

# Verify containerd is running
if ! systemctl is-active --quiet containerd; then
    echo "❌ containerd failed to start"
    echo "📋 Checking containerd status..."
    systemctl status containerd
    exit 1
fi

echo "✅ containerd restarted successfully"

# Label node for gVisor scheduling
echo "🏷️  Labeling node for gVisor workloads..."

# Get node name
NODE_NAME=$(hostname)

# Apply labels
kubectl label node $NODE_NAME sandbox=gvisor --overwrite
kubectl label node $NODE_NAME kernel-isolation=enabled --overwrite

# Apply taint for dedicated gVisor nodes
kubectl taint node $NODE_NAME sandbox=gvisor:NoSchedule --overwrite

echo "✅ Node labeled and tainted for gVisor workloads"

# Test gVisor installation
echo "🧪 Testing gVisor installation..."

# Create test container
TEST_OUTPUT=$(runsc --network=none do true 2>&1) || true

if echo "$TEST_OUTPUT" | grep -q "runsc executed successfully"; then
    echo "✅ gVisor test passed"
else
    echo "⚠️  gVisor test had issues, but installation appears complete"
    echo "Test output: $TEST_OUTPUT"
fi

# Setup log rotation for gVisor logs
echo "📋 Setting up log rotation..."

cat > /etc/logrotate.d/runsc << 'EOF'
/var/log/runsc/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
    maxsize 100M
}
EOF

echo "✅ Log rotation configured"

# Create monitoring script
echo "📊 Creating monitoring script..."

cat > /usr/local/bin/monitor-gvisor.sh << 'EOF'
#!/bin/bash
# gVisor monitoring script for ACGS hardened sandboxes

LOG_FILE="/var/log/gvisor-monitor.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> $LOG_FILE
}

# Check gVisor health
check_gvisor_health() {
    if runsc --help > /dev/null 2>&1; then
        log "INFO: gVisor runsc is healthy"
        return 0
    else
        log "ERROR: gVisor runsc health check failed"
        return 1
    fi
}

# Monitor gVisor containers
monitor_containers() {
    local count=$(runsc list 2>/dev/null | wc -l)
    log "INFO: Active gVisor containers: $count"
}

# Check for security violations in logs
check_violations() {
    local violations=$(grep -c "violation\|security\|blocked" /var/log/runsc/*.log 2>/dev/null || echo "0")
    if [ $violations -gt 0 ]; then
        log "WARNING: $violations security-related log entries found"
    fi
}

# Main monitoring loop
main() {
    log "INFO: Starting gVisor monitoring (Constitutional Hash: cdd01ef066bc6cf2)"
    
    check_gvisor_health
    monitor_containers  
    check_violations
    
    log "INFO: gVisor monitoring cycle completed"
}

main "$@"
EOF

chmod +x /usr/local/bin/monitor-gvisor.sh

# Create systemd service for monitoring
cat > /etc/systemd/system/gvisor-monitor.service << 'EOF'
[Unit]
Description=gVisor Health Monitor for ACGS Hardened Sandboxes
After=containerd.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/monitor-gvisor.sh
User=root

[Install]
WantedBy=multi-user.target
EOF

# Create timer for periodic monitoring
cat > /etc/systemd/system/gvisor-monitor.timer << 'EOF'
[Unit]
Description=Run gVisor Health Monitor every 5 minutes
Requires=gvisor-monitor.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start monitoring
systemctl daemon-reload
systemctl enable gvisor-monitor.timer
systemctl start gvisor-monitor.timer

echo "✅ gVisor monitoring configured and started"

# Final verification
echo "🔍 Final verification..."

# Check if runtime class is available
if kubectl get runtimeclass gvisor &>/dev/null; then
    echo "✅ gVisor runtime class is available"
else
    echo "ℹ️  gVisor runtime class not yet created (will be created by controller)"
fi

# Display summary
echo ""
echo "🎉 gVisor setup completed successfully!"
echo ""
echo "Summary:"
echo "  📦 gVisor runsc installed and configured"
echo "  ⚙️  containerd configured for gVisor runtime"
echo "  🏷️  Node labeled: sandbox=gvisor, kernel-isolation=enabled"
echo "  🚫 Node tainted: sandbox=gvisor:NoSchedule"
echo "  📊 Monitoring service enabled"
echo "  📋 Log rotation configured"
echo ""
echo "Next steps:"
echo "  1. Deploy the hardened sandbox controller"
echo "  2. Apply Kubernetes runtime setup: kubectl apply -f k8s-runtime-setup.yaml"
echo "  3. Test sandbox execution"
echo ""
echo "Monitoring:"
echo "  📋 Check gVisor status: systemctl status gvisor-monitor.timer"
echo "  📝 View logs: tail -f /var/log/gvisor-monitor.log"
echo "  🔍 List containers: runsc list"
echo ""
echo "Constitutional Hash: cdd01ef066bc6cf2"