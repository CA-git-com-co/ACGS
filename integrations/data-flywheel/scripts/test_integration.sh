#!/bin/bash

# ACGS-1 Data Flywheel Integration Test Script
# Comprehensive testing of the constitutional governance integration

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test configuration
API_BASE_URL="http://localhost:8010"
ACGS_BASE_URL="http://localhost"
TEST_TIMEOUT=30

echo "🧪 ACGS-1 Data Flywheel Integration Test Suite"
echo "=============================================="
echo "API Base URL: $API_BASE_URL"
echo "ACGS Base URL: $ACGS_BASE_URL"
echo "Test Timeout: ${TEST_TIMEOUT}s"
echo ""

# Test counters
tests_passed=0
tests_failed=0
tests_total=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="${3:-200}"
    
    tests_total=$((tests_total + 1))
    print_status "Test $tests_total: $test_name"
    
    if eval "$test_command"; then
        tests_passed=$((tests_passed + 1))
        print_success "✅ $test_name passed"
    else
        tests_failed=$((tests_failed + 1))
        print_error "❌ $test_name failed"
    fi
    echo ""
}

# Function to test HTTP endpoint
test_endpoint() {
    local url="$1"
    local expected_status="${2:-200}"
    local method="${3:-GET}"
    local data="${4:-}"
    
    local curl_cmd="curl -s -w '%{http_code}' -o /tmp/test_response.json --connect-timeout $TEST_TIMEOUT"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        curl_cmd="$curl_cmd -X POST -H 'Content-Type: application/json' -d '$data'"
    fi
    
    local response_code=$(eval "$curl_cmd '$url'" | tail -n1)
    
    if [ "$response_code" = "$expected_status" ]; then
        return 0
    else
        print_error "Expected status $expected_status, got $response_code"
        return 1
    fi
}

# Test 1: Basic API Health Check
run_test "Basic API Health Check" "test_endpoint '$API_BASE_URL/health'"

# Test 2: Constitutional Health Check
run_test "Constitutional Health Check" "test_endpoint '$API_BASE_URL/constitutional/health'"

# Test 3: ACGS-1 Services Health Check
print_status "Test 3: ACGS-1 Services Health Check"
acgs_services_healthy=0
acgs_services_total=7

for port in 8000 8001 8002 8003 8004 8005 8006; do
    if curl -f -s --connect-timeout 5 "$ACGS_BASE_URL:$port/health" > /dev/null 2>&1; then
        acgs_services_healthy=$((acgs_services_healthy + 1))
    fi
done

if [ $acgs_services_healthy -ge 5 ]; then
    tests_passed=$((tests_passed + 1))
    print_success "✅ ACGS-1 Services Health Check passed ($acgs_services_healthy/7 healthy)"
else
    tests_failed=$((tests_failed + 1))
    print_error "❌ ACGS-1 Services Health Check failed ($acgs_services_healthy/7 healthy)"
fi
tests_total=$((tests_total + 1))
echo ""

# Test 4: Governance Workloads Endpoint
run_test "Governance Workloads Endpoint" "test_endpoint '$API_BASE_URL/constitutional/workloads'"

# Test 5: Infrastructure Services
print_status "Test 5: Infrastructure Services Check"
infra_healthy=0
infra_total=3

# Elasticsearch
if curl -f -s --connect-timeout 5 "http://localhost:9200/_cluster/health" > /dev/null 2>&1; then
    infra_healthy=$((infra_healthy + 1))
fi

# MongoDB
if echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet > /dev/null 2>&1; then
    infra_healthy=$((infra_healthy + 1))
fi

# Redis
if redis-cli ping > /dev/null 2>&1; then
    infra_healthy=$((infra_healthy + 1))
fi

if [ $infra_healthy -eq $infra_total ]; then
    tests_passed=$((tests_passed + 1))
    print_success "✅ Infrastructure Services Check passed ($infra_healthy/$infra_total healthy)"
else
    tests_failed=$((tests_failed + 1))
    print_error "❌ Infrastructure Services Check failed ($infra_healthy/$infra_total healthy)"
fi
tests_total=$((tests_total + 1))
echo ""

# Test 6: Constitutional Compliance Validation
print_status "Test 6: Constitutional Compliance Validation"
compliance_test_data='{
    "model_output": "This policy promotes democratic participation and transparency in governance decisions.",
    "expected_output": "This policy should ensure democratic participation and transparency.",
    "governance_context": {
        "policy_type": "democratic_governance",
        "constitutional_principles": ["democratic_participation", "transparency"]
    },
    "workload_id": "test_policy_synthesis"
}'

if test_endpoint "$API_BASE_URL/constitutional/validate" "200" "POST" "$compliance_test_data"; then
    tests_passed=$((tests_passed + 1))
    print_success "✅ Constitutional Compliance Validation passed"
else
    tests_failed=$((tests_failed + 1))
    print_error "❌ Constitutional Compliance Validation failed"
fi
tests_total=$((tests_total + 1))
echo ""

# Test 7: Constitutional Job Creation
print_status "Test 7: Constitutional Job Creation"
job_test_data='{
    "workload_id": "test_governance_optimization",
    "client_id": "acgs_test_client",
    "constitutional_requirements": {
        "compliance_threshold": 0.95,
        "validation_required": true
    },
    "governance_context": {
        "policy_domain": "environmental_protection",
        "stakeholders": ["citizens", "government", "environmental_groups"]
    }
}'

if test_endpoint "$API_BASE_URL/constitutional/jobs" "200" "POST" "$job_test_data"; then
    tests_passed=$((tests_passed + 1))
    print_success "✅ Constitutional Job Creation passed"
    
    # Extract job ID for follow-up tests
    job_id=$(cat /tmp/test_response.json | jq -r '.id' 2>/dev/null || echo "")
    if [ -n "$job_id" ] && [ "$job_id" != "null" ]; then
        print_status "Created test job with ID: $job_id"
        
        # Test 8: Job Status Check
        sleep 5  # Wait a bit for job to process
        run_test "Job Status Check" "test_endpoint '$API_BASE_URL/jobs/$job_id'"
        
    else
        print_warning "Could not extract job ID for follow-up tests"
    fi
else
    tests_failed=$((tests_failed + 1))
    print_error "❌ Constitutional Job Creation failed"
fi
tests_total=$((tests_total + 1))
echo ""

# Test 9: Traffic Collection
run_test "Governance Traffic Collection" "test_endpoint '$API_BASE_URL/constitutional/traffic/collect?hours=1' '200' 'POST'"

# Test 10: Performance Test
print_status "Test 10: Performance Test"
start_time=$(date +%s.%N)
if curl -f -s --connect-timeout 10 "$API_BASE_URL/health" > /dev/null 2>&1; then
    end_time=$(date +%s.%N)
    response_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    if (( $(echo "$response_time < 2.0" | bc -l 2>/dev/null || echo "0") )); then
        tests_passed=$((tests_passed + 1))
        print_success "✅ Performance Test passed (${response_time}s)"
    else
        tests_failed=$((tests_failed + 1))
        print_error "❌ Performance Test failed (${response_time}s > 2.0s)"
    fi
else
    tests_failed=$((tests_failed + 1))
    print_error "❌ Performance Test failed (no response)"
fi
tests_total=$((tests_total + 1))
echo ""

# Test 11: Docker Services Test
if command -v docker-compose > /dev/null 2>&1; then
    print_status "Test 11: Docker Services Test"
    cd "$(dirname "$0")/.."
    
    if [ -f "deploy/docker-compose.acgs.yaml" ]; then
        docker_services=$(docker-compose -f deploy/docker-compose.acgs.yaml ps --services 2>/dev/null || echo "")
        
        if [ -n "$docker_services" ]; then
            running_services=0
            total_docker_services=0
            
            for service in $docker_services; do
                total_docker_services=$((total_docker_services + 1))
                if docker-compose -f deploy/docker-compose.acgs.yaml ps "$service" | grep -q "Up\|healthy"; then
                    running_services=$((running_services + 1))
                fi
            done
            
            if [ $running_services -ge $((total_docker_services * 3 / 4)) ]; then
                tests_passed=$((tests_passed + 1))
                print_success "✅ Docker Services Test passed ($running_services/$total_docker_services running)"
            else
                tests_failed=$((tests_failed + 1))
                print_error "❌ Docker Services Test failed ($running_services/$total_docker_services running)"
            fi
        else
            tests_failed=$((tests_failed + 1))
            print_error "❌ Docker Services Test failed (no services found)"
        fi
    else
        tests_failed=$((tests_failed + 1))
        print_error "❌ Docker Services Test failed (no compose file)"
    fi
    tests_total=$((tests_total + 1))
    echo ""
fi

# Test 12: Integration Stress Test
print_status "Test 12: Integration Stress Test"
stress_test_passed=true

for i in {1..5}; do
    if ! curl -f -s --connect-timeout 5 "$API_BASE_URL/health" > /dev/null 2>&1; then
        stress_test_passed=false
        break
    fi
    sleep 1
done

if [ "$stress_test_passed" = true ]; then
    tests_passed=$((tests_passed + 1))
    print_success "✅ Integration Stress Test passed"
else
    tests_failed=$((tests_failed + 1))
    print_error "❌ Integration Stress Test failed"
fi
tests_total=$((tests_total + 1))
echo ""

# Cleanup
rm -f /tmp/test_response.json

# Test Summary
echo "📊 Test Summary"
echo "==============="
echo "Total Tests: $tests_total"
echo "Passed: $tests_passed"
echo "Failed: $tests_failed"
echo "Success Rate: $(( tests_passed * 100 / tests_total ))%"
echo ""

# Overall result
if [ $tests_failed -eq 0 ]; then
    print_success "🎉 All tests passed! ACGS-1 Data Flywheel integration is fully operational."
    echo ""
    echo "✅ Ready for:"
    echo "   - Constitutional governance optimization"
    echo "   - Policy synthesis enhancement"
    echo "   - Formal verification acceleration"
    echo "   - Governance workflow automation"
    exit 0
elif [ $tests_passed -ge $((tests_total * 3 / 4)) ]; then
    print_warning "⚠️ Most tests passed, but some issues detected. System is partially operational."
    echo ""
    echo "🔧 Recommended actions:"
    echo "   - Check failed test details above"
    echo "   - Verify service configurations"
    echo "   - Review logs for error details"
    exit 1
else
    print_error "❌ Multiple tests failed. System is not ready for production use."
    echo ""
    echo "🚨 Required actions:"
    echo "   - Fix critical service failures"
    echo "   - Verify ACGS-1 service health"
    echo "   - Check infrastructure dependencies"
    echo "   - Review configuration settings"
    exit 2
fi
