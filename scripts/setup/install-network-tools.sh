# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Install network tools for CI/CD environments
# This script detects the OS and installs ping and other network utilities

set -e

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

install_network_tools() {
    log "🔧 Installing network tools..."
    
    # Detect OS and package manager
    if command -v apt-get >/dev/null 2>&1; then
        log "📦 Detected Debian/Ubuntu - using apt-get"
        apt-get update -qq
        apt-get install -y iputils-ping dnsutils netcat-openbsd
        log "✅ Installed: ping, nslookup, dig, nc"
        
    elif command -v yum >/dev/null 2>&1; then
        log "📦 Detected RHEL/CentOS - using yum"
        yum install -y iputils bind-utils nc
        log "✅ Installed: ping, nslookup, dig, nc"
        
    elif command -v apk >/dev/null 2>&1; then
        log "📦 Detected Alpine Linux - using apk"
        apk add --no-cache iputils bind-tools netcat-openbsd
        log "✅ Installed: ping, nslookup, dig, nc"
        
    elif command -v dnf >/dev/null 2>&1; then
        log "📦 Detected Fedora - using dnf"
        dnf install -y iputils bind-utils nc
        log "✅ Installed: ping, nslookup, dig, nc"
        
    else
        log "❌ Unknown package manager - cannot install network tools"
        log "💡 Consider using HTTP-based connectivity checks instead"
        return 1
    fi
    
    # Verify installation
    log "🔍 Verifying installation..."
    if command -v ping >/dev/null 2>&1; then
        log "✅ ping is now available"
        ping -c 1 github.com >/dev/null 2>&1 && log "✅ ping test to github.com successful"
    else
        log "❌ ping installation failed"
        return 1
    fi
}

# Main execution
main() {
    log "🚀 Starting network tools installation..."
    
    # Check if running as root (required for package installation)
    if [[ $EUID -ne 0 ]]; then
        log "⚠️  This script requires root privileges to install packages"
        log "💡 Run with: sudo $0"
        exit 1
    fi
    
    install_network_tools
    log "🎉 Network tools installation completed!"
}

main "$@"
