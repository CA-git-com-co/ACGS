#!/bin/bash

# Comprehensive Network Diagnostics Script
# Use this to debug connectivity issues

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${2:-$NC}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

section() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# System Information
check_system_info() {
    section "SYSTEM INFORMATION"
    
    log "🖥️  Operating System:" "$YELLOW"
    uname -a
    
    if [ -f /etc/os-release ]; then
        log "📋 OS Release:" "$YELLOW"
        cat /etc/os-release
    fi
    
    log "🌐 Hostname:" "$YELLOW"
    hostname
    
    log "👤 Current User:" "$YELLOW"
    whoami
}

# Network Configuration
check_network_config() {
    section "NETWORK CONFIGURATION"
    
    log "🔌 Network Interfaces:" "$YELLOW"
    if command -v ip >/dev/null 2>&1; then
        ip addr show
    elif command -v ifconfig >/dev/null 2>&1; then
        ifconfig
    else
        log "❌ Neither ip nor ifconfig available" "$RED"
    fi
    
    log "🛣️  Routing Table:" "$YELLOW"
    if command -v ip >/dev/null 2>&1; then
        ip route show
    elif command -v route >/dev/null 2>&1; then
        route -n
    else
        log "❌ No routing command available" "$RED"
    fi
    
    log "📋 DNS Configuration:" "$YELLOW"
    if [ -f /etc/resolv.conf ]; then
        cat /etc/resolv.conf
    else
        log "❌ /etc/resolv.conf not found" "$RED"
    fi
}

# DNS Testing
test_dns() {
    section "DNS RESOLUTION TESTING"
    
    local domains=("github.com" "api.github.com" "google.com" "cloudflare.com")
    local dns_servers=("default" "8.8.8.8" "1.1.1.1" "208.67.222.222")
    
    for domain in "${domains[@]}"; do
        log "🔍 Testing DNS resolution for $domain:" "$YELLOW"
        
        for dns in "${dns_servers[@]}"; do
            if [ "$dns" = "default" ]; then
                if command -v nslookup >/dev/null 2>&1; then
                    if nslookup "$domain" >/dev/null 2>&1; then
                        log "  ✅ $domain resolved with default DNS" "$GREEN"
                    else
                        log "  ❌ $domain failed with default DNS" "$RED"
                    fi
                fi
            else
                if command -v nslookup >/dev/null 2>&1; then
                    if nslookup "$domain" "$dns" >/dev/null 2>&1; then
                        log "  ✅ $domain resolved with DNS $dns" "$GREEN"
                    else
                        log "  ❌ $domain failed with DNS $dns" "$RED"
                    fi
                fi
            fi
        done
        echo
    done
}

# Connectivity Testing
test_connectivity() {
    section "CONNECTIVITY TESTING"
    
    local endpoints=(
        "https://github.com|GitHub Main"
        "https://api.github.com|GitHub API"
        "https://raw.githubusercontent.com|GitHub Raw"
        "https://google.com|Google"
        "https://httpbin.org/status/200|HTTPBin"
    )
    
    for endpoint in "${endpoints[@]}"; do
        IFS='|' read -r url name <<< "$endpoint"
        log "🌐 Testing connectivity to $name ($url):" "$YELLOW"
        
        # Test with curl
        if command -v curl >/dev/null 2>&1; then
            if curl -s --max-time 10 --head "$url" >/dev/null 2>&1; then
                log "  ✅ curl: SUCCESS" "$GREEN"
            else
                log "  ❌ curl: FAILED" "$RED"
            fi
        else
            log "  ⚠️  curl not available" "$YELLOW"
        fi
        
        # Test with wget
        if command -v wget >/dev/null 2>&1; then
            if wget --timeout=10 --spider --quiet "$url" 2>/dev/null; then
                log "  ✅ wget: SUCCESS" "$GREEN"
            else
                log "  ❌ wget: FAILED" "$RED"
            fi
        else
            log "  ⚠️  wget not available" "$YELLOW"
        fi
        
        echo
    done
}

# Port Testing
test_ports() {
    section "PORT CONNECTIVITY TESTING"
    
    local hosts_ports=(
        "github.com:443|GitHub HTTPS"
        "github.com:22|GitHub SSH"
        "api.github.com:443|GitHub API HTTPS"
        "8.8.8.8:53|Google DNS"
    )
    
    for host_port in "${hosts_ports[@]}"; do
        IFS='|' read -r hp name <<< "$host_port"
        IFS=':' read -r host port <<< "$hp"
        
        log "🔌 Testing port connectivity to $name ($host:$port):" "$YELLOW"
        
        if command -v nc >/dev/null 2>&1; then
            if nc -z -w5 "$host" "$port" 2>/dev/null; then
                log "  ✅ netcat: Port $port is open" "$GREEN"
            else
                log "  ❌ netcat: Port $port is closed or filtered" "$RED"
            fi
        elif command -v telnet >/dev/null 2>&1; then
            if timeout 5 telnet "$host" "$port" </dev/null >/dev/null 2>&1; then
                log "  ✅ telnet: Port $port is open" "$GREEN"
            else
                log "  ❌ telnet: Port $port is closed or filtered" "$RED"
            fi
        else
            log "  ⚠️  Neither nc nor telnet available" "$YELLOW"
        fi
        
        echo
    done
}

# Environment Variables
check_environment() {
    section "ENVIRONMENT VARIABLES"
    
    local env_vars=("HTTP_PROXY" "HTTPS_PROXY" "NO_PROXY" "http_proxy" "https_proxy" "no_proxy")
    
    for var in "${env_vars[@]}"; do
        if [ -n "${!var}" ]; then
            log "🔧 $var=${!var}" "$YELLOW"
        else
            log "📝 $var is not set" "$NC"
        fi
    done
}

# Firewall Status
check_firewall() {
    section "FIREWALL STATUS"
    
    # Check iptables
    if command -v iptables >/dev/null 2>&1; then
        log "🔥 iptables status:" "$YELLOW"
        if iptables -L >/dev/null 2>&1; then
            log "  ✅ iptables accessible" "$GREEN"
            # Show only if not too verbose
            local rule_count
            rule_count=$(iptables -L | wc -l)
            log "  📊 Total iptables rules: $rule_count" "$NC"
        else
            log "  ❌ iptables not accessible (may require sudo)" "$RED"
        fi
    else
        log "⚠️  iptables not available" "$YELLOW"
    fi
    
    # Check ufw
    if command -v ufw >/dev/null 2>&1; then
        log "🔥 ufw status:" "$YELLOW"
        ufw status 2>/dev/null || log "  ❌ ufw status not accessible" "$RED"
    fi
}

# Main execution
main() {
    log "🚀 Starting comprehensive network diagnostics..." "$GREEN"
    
    check_system_info
    check_network_config
    check_environment
    test_dns
    test_connectivity
    test_ports
    check_firewall
    
    section "DIAGNOSTICS COMPLETE"
    log "📋 Network diagnostics completed!" "$GREEN"
    log "💡 Review the output above to identify connectivity issues" "$YELLOW"
}

main "$@"
