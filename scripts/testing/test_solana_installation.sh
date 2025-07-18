# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Test script for robust Solana CLI installation
# This script validates the installation methods used in GitHub Actions workflows

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOLANA_CLI_VERSION="1.18.22"
TEST_DIR="/tmp/solana_test_$$"

print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️ $message${NC}"
            ;;
        "info")
            echo -e "${BLUE}ℹ️ $message${NC}"
            ;;
    esac
}

# Test primary installation method
test_primary_installation() {
    print_status "info" "Testing primary Solana CLI installation method..."
    
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    # Test with timeout and retries (simulating GitHub Actions environment)
    if timeout 60 curl -sSfL --retry 3 --retry-delay 5 "https://release.solana.com/v$SOLANA_CLI_VERSION/install" -o install_script.sh; then
        print_status "success" "Primary installation script downloaded successfully"
        
        # Test script execution (dry run)
        if bash -n install_script.sh; then
            print_status "success" "Installation script syntax is valid"
        else
            print_status "error" "Installation script has syntax errors"
            cd - && rm -rf "$temp_dir"
            return 1
        fi
    else
        print_status "error" "Failed to download primary installation script"
        cd - && rm -rf "$temp_dir"
        return 1
    fi
    
    cd - && rm -rf "$temp_dir"
    return 0
}

# Test fallback installation method
test_fallback_installation() {
    print_status "info" "Testing fallback Solana CLI installation method..."
    
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    local url="https://github.com/solana-labs/solana/releases/download/v$SOLANA_CLI_VERSION/solana-release-x86_64-unknown-linux-gnu.tar.bz2"
    
    # Test download availability
    if timeout 30 wget --spider --retry-connrefused --waitretry=5 "$url"; then
        print_status "success" "Fallback installation archive is available"
        
        # Test actual download (first 1MB to verify it's a valid archive)
        if timeout 30 wget --retry-connrefused --waitretry=5 --read-timeout=20 --timeout=15 -t 3 -r 0-1048576 -O test_archive.tar.bz2 "$url"; then
            print_status "success" "Fallback archive download test successful"
            
            # Test if it's a valid bzip2 archive
            if file test_archive.tar.bz2 | grep -q "bzip2"; then
                print_status "success" "Downloaded file is a valid bzip2 archive"
            else
                print_status "warning" "Downloaded file may not be a valid bzip2 archive"
            fi
        else
            print_status "error" "Failed to download fallback archive"
            cd - && rm -rf "$temp_dir"
            return 1
        fi
    else
        print_status "error" "Fallback installation archive is not available"
        cd - && rm -rf "$temp_dir"
        return 1
    fi
    
    cd - && rm -rf "$temp_dir"
    return 0
}

# Test network connectivity to Solana endpoints
test_network_connectivity() {
    print_status "info" "Testing network connectivity to Solana endpoints..."
    
    # Test primary endpoint
    if curl -I --max-time 10 "https://release.solana.com/" 2>&1 | grep -q "HTTP"; then
        print_status "success" "Primary Solana release endpoint is accessible"
    else
        print_status "error" "Primary Solana release endpoint is not accessible"
        return 1
    fi
    
    # Test GitHub releases endpoint
    if curl -I --max-time 10 "https://github.com/solana-labs/solana/releases" 2>&1 | grep -q "HTTP"; then
        print_status "success" "GitHub Solana releases endpoint is accessible"
    else
        print_status "error" "GitHub Solana releases endpoint is not accessible"
        return 1
    fi
    
    return 0
}

# Test JSON minification alternatives
test_json_minification() {
    print_status "info" "Testing JSON minification methods..."
    
    local test_json='{"test": "value", "nested": {"key": "data", "array": [1, 2, 3]}}'
    
    # Test jq method (if available)
    if command -v jq >/dev/null 2>&1; then
        local jq_result=$(echo "$test_json" | jq -c .)
        print_status "success" "jq minification: $jq_result"
    else
        print_status "warning" "jq not available, testing alternative method"
    fi
    
    # Test alternative method (used in workflows)
    local alt_result=$(echo "$test_json" | tr -d '\n' | sed 's/[[:space:]]\+/ /g' | sed 's/{ /{/g' | sed 's/ }/}/g' | sed 's/, /,/g')
    print_status "success" "Alternative minification: $alt_result"
    
    # Verify the alternative method produces valid JSON
    if echo "$alt_result" | python3 -m json.tool >/dev/null 2>&1; then
        print_status "success" "Alternative minification produces valid JSON"
    else
        print_status "error" "Alternative minification produces invalid JSON"
        return 1
    fi
    
    return 0
}

# Test HTTP connectivity checks
test_http_connectivity() {
    print_status "info" "Testing HTTP connectivity checks..."
    
    # Test GitHub connectivity (used in workflows)
    if curl -I --max-time 10 https://github.com 2>&1 | grep -q "HTTP"; then
        print_status "success" "GitHub HTTP connectivity check passed"
    else
        print_status "error" "GitHub HTTP connectivity check failed"
        return 1
    fi
    
    # Test crates.io connectivity
    if curl -I --max-time 10 https://crates.io 2>&1 | grep -q "HTTP"; then
        print_status "success" "Crates.io HTTP connectivity check passed"
    else
        print_status "error" "Crates.io HTTP connectivity check failed"
        return 1
    fi
    
    return 0
}

# Main test execution
main() {
    print_status "info" "Starting comprehensive GitHub Actions fixes validation..."
    echo
    
    local tests_passed=0
    local tests_failed=0
    
    # Run all tests
    if test_network_connectivity; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    echo
    
    if test_primary_installation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    echo
    
    if test_fallback_installation; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    echo
    
    if test_json_minification; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    echo
    
    if test_http_connectivity; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    echo
    
    # Summary
    print_status "info" "Test Summary:"
    print_status "success" "Tests passed: $tests_passed"
    if [ $tests_failed -gt 0 ]; then
        print_status "error" "Tests failed: $tests_failed"
        print_status "error" "Some GitHub Actions fixes may not work properly"
        exit 1
    else
        print_status "success" "All tests passed! GitHub Actions fixes are ready for deployment"
        exit 0
    fi
}

# Run main function
main "$@"
