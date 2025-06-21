#!/bin/bash
# GitHub Actions Workflow Testing Script
# Tests critical workflow components locally where possible

set -e

echo "🧪 Testing GitHub Actions Workflow Fixes"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n🔍 Testing: $test_name"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to test connectivity
test_connectivity() {
    echo -e "\n📡 Testing Network Connectivity"
    echo "--------------------------------"
    
    run_test "GitHub API connectivity" "timeout 10 curl -sSf https://api.github.com/zen"
    run_test "Crates.io API connectivity" "timeout 10 curl -sSf https://crates.io/api/v1/crates"
    run_test "NPM registry connectivity" "timeout 10 curl -sSf https://registry.npmjs.org/"
    run_test "Docker Hub connectivity" "timeout 10 curl -sSf https://hub.docker.com/v2/"
}

# Function to test dependency files
test_dependency_files() {
    echo -e "\n📦 Testing Dependency Files"
    echo "----------------------------"
    
    run_test "Root requirements.txt exists" "test -f requirements.txt"
    run_test "Root package-lock.json exists" "test -f package-lock.json"
    run_test "Blockchain package-lock.json exists" "test -f blockchain/package-lock.json"
    run_test "Applications package-lock.json exists" "test -f applications/package-lock.json"
    
    # Test dependency file validity
    if command -v python3 >/dev/null 2>&1; then
        run_test "Requirements.txt is valid" "python3 -m pip install --dry-run -r requirements.txt"
    fi
    
    if command -v npm >/dev/null 2>&1; then
        run_test "Package.json is valid" "npm ls --depth=0"
    fi
}

# Function to test workflow syntax
test_workflow_syntax() {
    echo -e "\n📝 Testing Workflow Syntax"
    echo "---------------------------"
    
    local workflow_count=0
    local valid_workflows=0
    
    for workflow in .github/workflows/*.yml .github/workflows/*.yaml; do
        if [[ -f "$workflow" ]]; then
            workflow_count=$((workflow_count + 1))
            if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
                valid_workflows=$((valid_workflows + 1))
            fi
        fi
    done
    
    run_test "All workflows have valid YAML syntax" "test $valid_workflows -eq $workflow_count"
    echo "   📊 Valid workflows: $valid_workflows/$workflow_count"
}

# Function to test deprecated actions
test_deprecated_actions() {
    echo -e "\n🔄 Testing for Deprecated Actions"
    echo "----------------------------------"
    
    local deprecated_found=0
    
    # Check for deprecated actions
    if grep -r "actions/upload-artifact@v[123]" .github/workflows/ >/dev/null 2>&1; then
        deprecated_found=$((deprecated_found + 1))
    fi
    
    if grep -r "actions/checkout@v[123]" .github/workflows/ >/dev/null 2>&1; then
        deprecated_found=$((deprecated_found + 1))
    fi
    
    if grep -r "codecov/codecov-action@v[1234]" .github/workflows/ >/dev/null 2>&1; then
        deprecated_found=$((deprecated_found + 1))
    fi
    
    run_test "No deprecated actions found" "test $deprecated_found -eq 0"
    
    if [[ $deprecated_found -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  Found $deprecated_found deprecated action(s)${NC}"
    fi
}

# Function to test configuration conflicts
test_configuration_conflicts() {
    echo -e "\n⚙️  Testing Configuration Conflicts"
    echo "-----------------------------------"
    
    local conflicts=0
    
    # Check for CARGO_INCREMENTAL conflicts with sccache
    if grep -r "CARGO_INCREMENTAL.*1" .github/workflows/ | grep -q "sccache"; then
        conflicts=$((conflicts + 1))
    fi
    
    run_test "No CARGO_INCREMENTAL conflicts with sccache" "test $conflicts -eq 0"
}

# Function to test timeout protections
test_timeout_protections() {
    echo -e "\n⏱️  Testing Timeout Protections"
    echo "-------------------------------"
    
    local curl_without_timeout=0
    local wget_without_timeout=0
    
    # Check for curl commands without timeout
    if grep -r "curl.*github.com" .github/workflows/ | grep -v "timeout" >/dev/null 2>&1; then
        curl_without_timeout=$((curl_without_timeout + 1))
    fi
    
    # Check for wget commands without timeout
    if grep -r "wget.*https://" .github/workflows/ | grep -v "timeout" >/dev/null 2>&1; then
        wget_without_timeout=$((wget_without_timeout + 1))
    fi
    
    run_test "Critical curl commands have timeout protection" "test $curl_without_timeout -eq 0"
    run_test "Critical wget commands have timeout protection" "test $wget_without_timeout -eq 0"
}

# Function to test tools availability
test_tools_availability() {
    echo -e "\n🛠️  Testing Required Tools"
    echo "--------------------------"
    
    run_test "curl is available" "command -v curl"
    run_test "wget is available" "command -v wget"
    run_test "timeout is available" "command -v timeout"
    run_test "jq is available" "command -v jq"
    
    # Optional tools
    if command -v python3 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ INFO${NC}: Python3 is available"
    else
        echo -e "${YELLOW}⚠️  INFO${NC}: Python3 not available (optional)"
    fi
    
    if command -v npm >/dev/null 2>&1; then
        echo -e "${GREEN}✅ INFO${NC}: npm is available"
    else
        echo -e "${YELLOW}⚠️  INFO${NC}: npm not available (optional)"
    fi
}

# Function to generate test report
generate_test_report() {
    echo -e "\n📊 Test Results Summary"
    echo "========================"
    echo "Total Tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    local success_rate=$((TESTS_PASSED * 100 / TESTS_TOTAL))
    echo "Success Rate: $success_rate%"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}🎉 All tests passed! Workflows are ready for production.${NC}"
        return 0
    else
        echo -e "\n${RED}⚠️  Some tests failed. Please review and fix the issues above.${NC}"
        return 1
    fi
}

# Main execution
main() {
    echo "Starting comprehensive workflow testing..."
    echo "Timestamp: $(date -u)"
    echo ""
    
    # Run all test suites
    test_tools_availability
    test_connectivity
    test_dependency_files
    test_workflow_syntax
    test_deprecated_actions
    test_configuration_conflicts
    test_timeout_protections
    
    # Generate final report
    generate_test_report
}

# Execute main function
main "$@"
