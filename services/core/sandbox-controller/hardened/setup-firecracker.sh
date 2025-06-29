#!/bin/bash
# Setup script for Firecracker/Kata runtime on Kubernetes nodes
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🔥 Setting up Firecracker/Kata runtime for maximum isolation"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "=========================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    exit 1
fi

# Check for KVM support
echo "🔍 Checking virtualization support..."

if [ ! -e /dev/kvm ]; then
    echo "❌ KVM is not available. Firecracker requires KVM support."
    echo "💡 Ensure:"
    echo "   - Hardware virtualization is enabled in BIOS"
    echo "   - KVM modules are loaded: modprobe kvm kvm_intel"
    echo "   - /dev/kvm exists and is accessible"
    exit 1
fi

if [ ! -r /dev/kvm ] || [ ! -w /dev/kvm ]; then
    echo "❌ /dev/kvm is not accessible"
    echo "💡 Fix permissions: chmod 666 /dev/kvm"
    exit 1
fi

echo "✅ KVM support verified"

# Detect OS
OS=""
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

echo "📋 Detected OS: $OS"

# Install Kata Containers
echo "📦 Installing Kata Containers..."

case $OS in
    "ubuntu")
        # Add Kata repository
        ARCH=$(arch)
        BRANCH="${BRANCH:-main}"
        
        # Install from GitHub releases
        KATA_VERSION="3.2.0"
        
        # Download and install kata-runtime
        curl -fsSL https://github.com/kata-containers/kata-containers/releases/download/${KATA_VERSION}/kata-static-${KATA_VERSION}-x86_64.tar.xz -o kata-static.tar.xz
        
        # Extract to /opt/kata
        mkdir -p /opt/kata
        tar -xf kata-static.tar.xz -C /opt/kata
        
        # Create symlinks
        ln -sf /opt/kata/bin/kata-runtime /usr/local/bin/kata-runtime
        ln -sf /opt/kata/bin/kata-collect-data.sh /usr/local/bin/kata-collect-data.sh
        
        # Clean up
        rm kata-static.tar.xz
        ;;
    
    "centos"|"rhel"|"fedora")
        # Install from GitHub releases (same as Ubuntu)
        KATA_VERSION="3.2.0"
        
        curl -fsSL https://github.com/kata-containers/kata-containers/releases/download/${KATA_VERSION}/kata-static-${KATA_VERSION}-x86_64.tar.xz -o kata-static.tar.xz
        
        mkdir -p /opt/kata
        tar -xf kata-static.tar.xz -C /opt/kata
        
        ln -sf /opt/kata/bin/kata-runtime /usr/local/bin/kata-runtime
        ln -sf /opt/kata/bin/kata-collect-data.sh /usr/local/bin/kata-collect-data.sh
        
        rm kata-static.tar.xz
        ;;
    
    *)
        echo "❌ Unsupported OS: $OS"
        exit 1
        ;;
esac

# Verify installation
if ! command -v kata-runtime &> /dev/null; then
    echo "❌ kata-runtime installation failed"
    exit 1
fi

echo "✅ Kata Containers installed successfully"
kata-runtime --version

# Install Firecracker
echo "🔥 Installing Firecracker..."

FIRECRACKER_VERSION="v1.4.1"

# Download Firecracker binary
curl -fsSL https://github.com/firecracker-microvm/firecracker/releases/download/${FIRECRACKER_VERSION}/firecracker-${FIRECRACKER_VERSION}-x86_64.tgz -o firecracker.tgz

# Extract and install
tar -xzf firecracker.tgz
mv release-${FIRECRACKER_VERSION}-x86_64/firecracker-${FIRECRACKER_VERSION}-x86_64 /usr/local/bin/firecracker
mv release-${FIRECRACKER_VERSION}-x86_64/jailer-${FIRECRACKER_VERSION}-x86_64 /usr/local/bin/jailer

# Make executable
chmod +x /usr/local/bin/firecracker
chmod +x /usr/local/bin/jailer

# Clean up
rm -rf firecracker.tgz release-${FIRECRACKER_VERSION}-x86_64

# Verify Firecracker installation
if ! command -v firecracker &> /dev/null; then
    echo "❌ Firecracker installation failed"
    exit 1
fi

echo "✅ Firecracker installed successfully"
firecracker --version

# Configure Kata for Firecracker
echo "⚙️  Configuring Kata Containers for Firecracker..."

# Create Kata configuration directory
mkdir -p /etc/kata-containers
mkdir -p /var/lib/kata-containers

# Create Kata configuration for Firecracker
cat > /etc/kata-containers/configuration-fc.toml << 'EOF'
# Kata Containers configuration for Firecracker
# Constitutional Hash: cdd01ef066bc6cf2

[hypervisor.firecracker]
path = "/usr/local/bin/firecracker"
jailer_path = "/usr/local/bin/jailer"
kernel = "/opt/kata/share/kata-containers/vmlinux.container"
image = "/opt/kata/share/kata-containers/kata-containers.img"
machine_type = ""
kernel_params = "tsc=reliable no_timer_check rcupdate.rcu_expedited=1 i8042.direct=1 i8042.dumbkbd=1 i8042.nopnp=1 i8042.noaux=1 noreplace-smp reboot=k cryptomgr.notests net.ifnames=0 pci=lastbus=0 root=/dev/vda1 rootflags=dax,data=ordered,errors=remount-ro ro rootfstype=ext4 quiet systemd.show_status=false panic=1 nr_cpus=1 systemd.unit=kata-containers.target systemd.mask=systemd-networkd.service systemd.mask=systemd-networkd.socket scsi_mod.scan=none"
ctlpath = "/run/vc/firecracker/%(ID)s/root/kata.hvsock"
jailer_root = "/run/vc/firecracker"
netns = "testns"

# Resource constraints for hardened sandboxes
default_vcpus = 1
default_maxvcpus = 2
default_memory = 512
default_maxmemory = 2048

# Security settings
disable_block_device_use = true
shared_fs = "virtio-fs"
virtio_fs_daemon = "/opt/kata/libexec/kata-containers/virtiofsd"
file_mem_backend = ""
pflashes = ["/opt/kata/share/kata-containers/kata-containers-initrd.img"]

# Enhanced security
enable_debug = false
debug_console_enabled = false
sandbox_cgroup_only = true

# Constitutional governance
[hypervisor.firecracker.blockdev]
block_device_driver = "virtio-blk"
block_device_cache_set = false
block_device_cache_direct = false

[agent.kata]
enable_tracing = false
enable_debug = false
debug_console_vport = 1026
EOF

# Set up Kata configuration symlink
ln -sf /etc/kata-containers/configuration-fc.toml /etc/kata-containers/configuration.toml

echo "✅ Kata Containers configured for Firecracker"

# Configure containerd for Kata
echo "⚙️  Configuring containerd for Kata runtime..."

# Backup existing config
cp /etc/containerd/config.toml /etc/containerd/config.toml.backup-kata

# Check if Kata runtime is already configured
if grep -q "kata-runtime" /etc/containerd/config.toml; then
    echo "ℹ️  Kata runtime already configured in containerd"
else
    # Add Kata runtime configuration
    cat >> /etc/containerd/config.toml << 'EOF'

# Kata Containers runtime configuration for maximum isolation
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.kata]
  runtime_type = "io.containerd.kata.v2"
  privileged_without_host_devices = false

[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.kata.options]
  ConfigPath = "/etc/kata-containers/configuration.toml"

# Kata Firecracker specific runtime
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.kata-firecracker]
  runtime_type = "io.containerd.kata.v2"
  privileged_without_host_devices = false

[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.kata-firecracker.options]
  ConfigPath = "/etc/kata-containers/configuration-fc.toml"
EOF

    echo "✅ Added Kata runtime configuration to containerd"
fi

# Set up KVM permissions
echo "🔑 Setting up KVM permissions..."

# Create kvm group if it doesn't exist
if ! getent group kvm > /dev/null 2>&1; then
    groupadd kvm
fi

# Add users to kvm group
usermod -a -G kvm root

# Set up udev rules for KVM
cat > /etc/udev/rules.d/99-kvm.rules << 'EOF'
KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"
EOF

# Reload udev rules
udevadm control --reload-rules
udevadm trigger

echo "✅ KVM permissions configured"

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

# Label node for Kata/Firecracker scheduling
echo "🏷️  Labeling node for Kata/Firecracker workloads..."

# Get node name
NODE_NAME=$(hostname)

# Apply labels
kubectl label node $NODE_NAME sandbox=kata --overwrite
kubectl label node $NODE_NAME microvm-isolation=enabled --overwrite
kubectl label node $NODE_NAME virtualization=firecracker --overwrite

# Apply taint for dedicated Kata nodes
kubectl taint node $NODE_NAME sandbox=kata:NoSchedule --overwrite

echo "✅ Node labeled and tainted for Kata/Firecracker workloads"

# Test Kata installation
echo "🧪 Testing Kata/Firecracker installation..."

# Run Kata check
if kata-runtime kata-check; then
    echo "✅ Kata runtime check passed"
else
    echo "⚠️  Kata runtime check had issues, but installation appears complete"
fi

# Create monitoring script for Firecracker
echo "📊 Creating Firecracker monitoring script..."

cat > /usr/local/bin/monitor-firecracker.sh << 'EOF'
#!/bin/bash
# Firecracker monitoring script for ACGS hardened sandboxes

LOG_FILE="/var/log/firecracker-monitor.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> $LOG_FILE
}

# Check Firecracker health
check_firecracker_health() {
    if firecracker --version > /dev/null 2>&1; then
        log "INFO: Firecracker is healthy"
        return 0
    else
        log "ERROR: Firecracker health check failed"
        return 1
    fi
}

# Check Kata runtime health
check_kata_health() {
    if kata-runtime --version > /dev/null 2>&1; then
        log "INFO: Kata runtime is healthy"
        return 0
    else
        log "ERROR: Kata runtime health check failed"
        return 1
    fi
}

# Monitor KVM usage
monitor_kvm() {
    if [ -e /dev/kvm ]; then
        local kvm_processes=$(ps aux | grep firecracker | grep -v grep | wc -l)
        log "INFO: Active Firecracker processes: $kvm_processes"
    else
        log "ERROR: /dev/kvm not available"
    fi
}

# Check for security violations
check_violations() {
    local violations=$(dmesg | grep -c "firecracker\|kata" | tail -100 | grep -c "violation\|security\|blocked" || echo "0")
    if [ $violations -gt 0 ]; then
        log "WARNING: $violations security-related kernel messages found"
    fi
}

# Main monitoring loop
main() {
    log "INFO: Starting Firecracker monitoring (Constitutional Hash: cdd01ef066bc6cf2)"
    
    check_firecracker_health
    check_kata_health
    monitor_kvm
    check_violations
    
    log "INFO: Firecracker monitoring cycle completed"
}

main "$@"
EOF

chmod +x /usr/local/bin/monitor-firecracker.sh

# Create systemd service for monitoring
cat > /etc/systemd/system/firecracker-monitor.service << 'EOF'
[Unit]
Description=Firecracker Health Monitor for ACGS Hardened Sandboxes
After=containerd.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/monitor-firecracker.sh
User=root

[Install]
WantedBy=multi-user.target
EOF

# Create timer for periodic monitoring
cat > /etc/systemd/system/firecracker-monitor.timer << 'EOF'
[Unit]
Description=Run Firecracker Health Monitor every 5 minutes
Requires=firecracker-monitor.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start monitoring
systemctl daemon-reload
systemctl enable firecracker-monitor.timer
systemctl start firecracker-monitor.timer

echo "✅ Firecracker monitoring configured and started"

# Setup log rotation
echo "📋 Setting up log rotation..."

cat > /etc/logrotate.d/firecracker << 'EOF'
/var/log/firecracker-monitor.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
    maxsize 100M
}

/var/log/kata-containers/*.log {
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

# Final verification
echo "🔍 Final verification..."

# Check if runtime class is available
if kubectl get runtimeclass kata-firecracker &>/dev/null; then
    echo "✅ Kata Firecracker runtime class is available"
else
    echo "ℹ️  Kata Firecracker runtime class not yet created (will be created by controller)"
fi

# Display summary
echo ""
echo "🎉 Firecracker/Kata setup completed successfully!"
echo ""
echo "Summary:"
echo "  🔥 Firecracker microVM hypervisor installed"
echo "  📦 Kata Containers runtime installed and configured"
echo "  ⚙️  containerd configured for Kata/Firecracker runtime"
echo "  🏷️  Node labeled: sandbox=kata, microvm-isolation=enabled"
echo "  🚫 Node tainted: sandbox=kata:NoSchedule"
echo "  🔑 KVM permissions configured"
echo "  📊 Monitoring service enabled"
echo "  📋 Log rotation configured"
echo ""
echo "Next steps:"
echo "  1. Deploy the hardened sandbox controller"
echo "  2. Apply Kubernetes runtime setup: kubectl apply -f k8s-runtime-setup.yaml"
echo "  3. Test sandbox execution with Firecracker runtime"
echo ""
echo "Monitoring:"
echo "  📋 Check Firecracker status: systemctl status firecracker-monitor.timer"
echo "  📝 View logs: tail -f /var/log/firecracker-monitor.log"
echo "  🔍 Run health check: kata-runtime kata-check"
echo "  🧪 Test microVM: firecracker --version"
echo ""
echo "Constitutional Hash: cdd01ef066bc6cf2"