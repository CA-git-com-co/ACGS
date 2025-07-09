#!/bin/bash
# WAF Rules Testing Script
# Tests WAF rules against actual attack patterns discovered in Sprint 0

set -e

# Configuration
WAF_ENDPOINT="${WAF_ENDPOINT:-https://api.acgs-pgp.com}"
TEST_RESULTS_DIR="reports/waf-testing"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="${TEST_RESULTS_DIR}/waf_test_results_${TIMESTAMP}.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create results directory
mkdir -p "$TEST_RESULTS_DIR"

# Initialize results
echo "{" > "$RESULTS_FILE"
echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$RESULTS_FILE"
echo "  \"waf_endpoint\": \"$WAF_ENDPOINT\"," >> "$RESULTS_FILE"
echo "  \"test_results\": [" >> "$RESULTS_FILE"

test_count=0
passed_tests=0
failed_tests=0

log_test_result() {
    local test_name="$1"
    local expected_status="$2"
    local actual_status="$3"
    local rule_id="$4"
    local passed="$5"
    
    if [ $test_count -gt 0 ]; then
        echo "    ," >> "$RESULTS_FILE"
    fi
    
    cat >> "$RESULTS_FILE" << EOF
    {
      "test_name": "$test_name",
      "expected_status": $expected_status,
      "actual_status": $actual_status,
      "expected_rule": "$rule_id",
      "passed": $passed,
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }EOF
    
    test_count=$((test_count + 1))
    if [ "$passed" = "true" ]; then
        passed_tests=$((passed_tests + 1))
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
    else
        failed_tests=$((failed_tests + 1))
        echo -e "${RED}❌ FAIL${NC}: $test_name (Expected: $expected_status, Got: $actual_status)"
    fi
}

run_test() {
    local test_name="$1"
    local method="$2"
    local path="$3"
    local data="$4"
    local headers="$5"
    local expected_status="$6"
    local expected_rule="$7"
    
    echo -e "${BLUE}🧪 Testing${NC}: $test_name"
    
    # Build curl command
    local curl_cmd="curl -s -w '%{http_code}' -o /dev/null"
    curl_cmd="$curl_cmd -X $method"
    
    if [ -n "$headers" ]; then
        curl_cmd="$curl_cmd $headers"
    fi
    
    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -d '$data'"
    fi
    
    curl_cmd="$curl_cmd '$WAF_ENDPOINT$path'"
    
    # Execute test
    local actual_status
    actual_status=$(eval "$curl_cmd" 2>/dev/null || echo "000")
    
    # Check result
    local passed="false"
    if [ "$actual_status" = "$expected_status" ]; then
        passed="true"
    fi
    
    log_test_result "$test_name" "$expected_status" "$actual_status" "$expected_rule" "$passed"
}

echo -e "${BLUE}🛡️ WAF Security Rules Testing${NC}"
echo "=================================="
echo "Endpoint: $WAF_ENDPOINT"
echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Test Category 1: Injection Protection (Rule 101-102)
echo -e "${YELLOW}📋 Category 1: Injection Protection Tests${NC}"

run_test \
    "Datalog Injection - Drop Rules" \
    "POST" \
    "/api/v1/policy/evaluate" \
    '{"user_id": "admin'\'''; drop_all_rules; allow('\''admin", "action": "read", "resource": "document"}' \
    '-H "Content-Type: application/json"' \
    "403" \
    "101"

run_test \
    "Datalog Injection - Logic Operators" \
    "POST" \
    "/api/v1/policy/evaluate" \
    '{"user_id": "user and admin", "action": "read", "resource": "document"}' \
    '-H "Content-Type: application/json"' \
    "403" \
    "101"

run_test \
    "SQL Injection - Union Select" \
    "POST" \
    "/api/v1/search" \
    '{"query": "test'\'' UNION SELECT * FROM users--"}' \
    '-H "Content-Type: application/json"' \
    "403" \
    "102"

run_test \
    "SQL Injection - OR 1=1" \
    "GET" \
    "/api/v1/documents?search=test%27%20OR%201=1--" \
    "" \
    "" \
    "403" \
    "102"

# Test Category 2: API Endpoint Protection (Rule 201-202)
echo -e "${YELLOW}📋 Category 2: API Endpoint Protection Tests${NC}"

run_test \
    "Unauthorized Export Access" \
    "POST" \
    "/api/v1/audit/export" \
    '{"start_date": "2025-01-01", "end_date": "2025-01-29"}' \
    '-H "Content-Type: application/json" -H "Authorization: Bearer invalid-token"' \
    "403" \
    "201"

run_test \
    "Authorized Export Access" \
    "POST" \
    "/api/v1/audit/export" \
    '{"start_date": "2025-01-01", "end_date": "2025-01-29"}' \
    '-H "Content-Type: application/json" -H "Authorization: Bearer admin-token"' \
    "200" \
    "none"

# Test rate limiting (this will make multiple requests)
echo -e "${BLUE}🧪 Testing${NC}: Rate Limiting for Audit Endpoints"
rate_limit_passed="true"
for i in {1..15}; do
    status=$(curl -s -w '%{http_code}' -o /dev/null "$WAF_ENDPOINT/api/v1/audit/events" 2>/dev/null || echo "000")
    if [ $i -gt 10 ] && [ "$status" != "429" ]; then
        rate_limit_passed="false"
        break
    fi
done

log_test_result "Rate Limiting Audit Endpoints" "429" "$status" "202" "$rate_limit_passed"

# Test Category 3: Authentication Protection (Rule 301-302)
echo -e "${YELLOW}📋 Category 3: Authentication Protection Tests${NC}"

run_test \
    "Invalid JWT Format" \
    "GET" \
    "/api/v1/user/profile" \
    "" \
    '-H "Authorization: Bearer invalid.jwt.format.here"' \
    "401" \
    "301"

run_test \
    "Missing JWT Token" \
    "GET" \
    "/api/v1/user/profile" \
    "" \
    '-H "Authorization: Bearer"' \
    "401" \
    "301"

run_test \
    "Unauthorized Admin Access" \
    "GET" \
    "/admin/dashboard" \
    "" \
    '-H "Authorization: Bearer user-token"' \
    "403" \
    "302"

# Test Category 4: OWASP Protection (Rule 401-402)
echo -e "${YELLOW}📋 Category 4: OWASP Protection Tests${NC}"

run_test \
    "XSS Script Tag" \
    "POST" \
    "/api/v1/comments" \
    '{"comment": "<script>alert('\''xss'\'')</script>"}' \
    '-H "Content-Type: application/json"' \
    "403" \
    "401"

run_test \
    "XSS JavaScript URL" \
    "GET" \
    "/api/v1/redirect?url=javascript:alert('xss')" \
    "" \
    "" \
    "403" \
    "401"

# Test legitimate requests (should pass)
echo -e "${YELLOW}📋 Legitimate Request Tests (Should Pass)${NC}"

run_test \
    "Legitimate Policy Evaluation" \
    "POST" \
    "/api/v1/policy/evaluate" \
    '{"user_id": "alice123", "action": "read", "resource": "document-456"}' \
    '-H "Content-Type: application/json" -H "Authorization: Bearer valid-jwt-token"' \
    "200" \
    "none"

run_test \
    "Legitimate User Profile Access" \
    "GET" \
    "/api/v1/user/profile" \
    "" \
    '-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"' \
    "200" \
    "none"

# Finalize results file
echo "" >> "$RESULTS_FILE"
echo "  ]," >> "$RESULTS_FILE"
echo "  \"summary\": {" >> "$RESULTS_FILE"
echo "    \"total_tests\": $test_count," >> "$RESULTS_FILE"
echo "    \"passed_tests\": $passed_tests," >> "$RESULTS_FILE"
echo "    \"failed_tests\": $failed_tests," >> "$RESULTS_FILE"
echo "    \"success_rate\": $(echo "scale=2; $passed_tests * 100 / $test_count" | bc -l)%" >> "$RESULTS_FILE"
echo "  }" >> "$RESULTS_FILE"
echo "}" >> "$RESULTS_FILE"

# Print summary
echo ""
echo -e "${BLUE}📊 Test Summary${NC}"
echo "==============="
echo "Total Tests: $test_count"
echo -e "Passed: ${GREEN}$passed_tests${NC}"
echo -e "Failed: ${RED}$failed_tests${NC}"
echo "Success Rate: $(echo "scale=1; $passed_tests * 100 / $test_count" | bc -l)%"
echo ""
echo "Detailed results saved to: $RESULTS_FILE"

# Exit with appropriate code
if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}🎉 All WAF tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Some WAF tests failed. Please review the configuration.${NC}"
    exit 1
fi
