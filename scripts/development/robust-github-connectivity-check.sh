# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Robust GitHub Connectivity Check Script
# Replaces fragile ping-based checks with HTTP-based verification

set -e

# Configuration
MAX_RETRIES=3
RETRY_DELAY=5
TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${2:-$NC}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Test DNS resolution
test_dns() {
    log "🔍 Testing DNS resolution for github.com..." "$YELLOW"
    
    if command -v nslookup >/dev/null 2>&1; then
        if nslookup github.com >/dev/null 2>&1; then
            log "✅ DNS resolution successful" "$GREEN"
            return 0
        else
            log "❌ DNS resolution failed" "$RED"
            return 1
        fi
    elif command -v dig >/dev/null 2>&1; then
        if dig github.com +short >/dev/null 2>&1; then
            log "✅ DNS resolution successful" "$GREEN"
            return 0
        else
            log "❌ DNS resolution failed" "$RED"
            return 1
        fi
    else
        log "⚠️  Neither nslookup nor dig available, skipping DNS test" "$YELLOW"
        return 0
    fi
}

# Test HTTP connectivity
test_http_connectivity() {
    local url="$1"
    local description="$2"
    
    log "🌐 Testing HTTP connectivity to $description..." "$YELLOW"
    
    if command -v curl >/dev/null 2>&1; then
        if curl -s --max-time "$TIMEOUT" --head "$url" >/dev/null 2>&1; then
            log "✅ HTTP connectivity to $description successful" "$GREEN"
            return 0
        else
            log "❌ HTTP connectivity to $description failed" "$RED"
            return 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget --timeout="$TIMEOUT" --spider --quiet "$url" 2>/dev/null; then
            log "✅ HTTP connectivity to $description successful" "$GREEN"
            return 0
        else
            log "❌ HTTP connectivity to $description failed" "$RED"
            return 1
        fi
    else
        log "❌ Neither curl nor wget available for HTTP testing" "$RED"
        return 1
    fi
}

# Test GitHub API connectivity
test_github_api() {
    log "🔌 Testing GitHub API connectivity..." "$YELLOW"
    
    if command -v curl >/dev/null 2>&1; then
        local response
        response=$(curl -s --max-time "$TIMEOUT" -w "%{http_code}" "https://api.github.com/zen" 2>/dev/null)
        local http_code="${response: -3}"
        
        if [[ "$http_code" == "200" ]]; then
            log "✅ GitHub API connectivity successful" "$GREEN"
            return 0
        else
            log "❌ GitHub API returned HTTP $http_code" "$RED"
            return 1
        fi
    else
        return 1
    fi
}

# Main connectivity check with retries
check_connectivity() {
    local attempt=1
    
    while [[ $attempt -le $MAX_RETRIES ]]; do
        log "🔄 Connectivity check attempt $attempt/$MAX_RETRIES" "$YELLOW"
        
        # Test DNS first
        if ! test_dns; then
            log "⚠️  DNS test failed on attempt $attempt" "$YELLOW"
        fi
        
        # Test basic HTTP connectivity
        local tests_passed=0
        local total_tests=3
        
        # Test 1: GitHub main site
        if test_http_connectivity "https://github.com" "GitHub main site"; then
            ((tests_passed++))
        fi
        
        # Test 2: GitHub API
        if test_github_api; then
            ((tests_passed++))
        fi
        
        # Test 3: Alternative endpoint
        if test_http_connectivity "https://api.github.com" "GitHub API endpoint"; then
            ((tests_passed++))
        fi
        
        # Check if enough tests passed
        if [[ $tests_passed -ge 2 ]]; then
            log "🎉 GitHub connectivity verified successfully!" "$GREEN"
            log "📊 Passed $tests_passed/$total_tests connectivity tests" "$GREEN"
            return 0
        fi
        
        if [[ $attempt -lt $MAX_RETRIES ]]; then
            log "⏳ Waiting $RETRY_DELAY seconds before retry..." "$YELLOW"
            sleep "$RETRY_DELAY"
        fi
        
        ((attempt++))
    done
    
    log "💥 GitHub connectivity check failed after $MAX_RETRIES attempts" "$RED"
    log "🔧 Please check network configuration and firewall settings" "$RED"
    return 1
}

# Network diagnostics
run_diagnostics() {
    log "🔍 Running network diagnostics..." "$YELLOW"
    
    # Check if we can resolve any domain
    if command -v nslookup >/dev/null 2>&1; then
        log "📋 DNS servers in use:" "$YELLOW"
        cat /etc/resolv.conf 2>/dev/null || log "Could not read /etc/resolv.conf" "$RED"
    fi
    
    # Check routing
    if command -v ip >/dev/null 2>&1; then
        log "🛣️  Default route:" "$YELLOW"
        ip route show default 2>/dev/null || log "Could not show routes" "$RED"
    fi
    
    # Test alternative connectivity
    log "🌍 Testing alternative connectivity..." "$YELLOW"
    if test_http_connectivity "https://httpbin.org/status/200" "httpbin.org"; then
        log "✅ General internet connectivity appears to work" "$GREEN"
    else
        log "❌ General internet connectivity issues detected" "$RED"
    fi
}

# Main execution
main() {
    log "🚀 Starting robust GitHub connectivity check..." "$GREEN"
    
    if check_connectivity; then
        log "✅ All connectivity checks passed!" "$GREEN"
        exit 0
    else
        log "❌ Connectivity checks failed, running diagnostics..." "$RED"
        run_diagnostics
        exit 1
    fi
}

# Run main function
main "$@"
