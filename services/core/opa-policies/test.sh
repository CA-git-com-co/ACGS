#!/bin/bash
# OPA Policy Test Runner for ACGS-1 Lite
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🧪 ACGS-1 Lite Constitutional Policy Test Suite"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "=============================================="

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v opa &> /dev/null; then
    echo "❌ OPA is not installed or not in PATH"
    echo "💡 Install OPA: https://www.openpolicyagent.org/docs/latest/get-started/"
    exit 1
fi

echo "✅ OPA found: $(opa version)"

# Test configuration
FAILED_TESTS=0
TOTAL_TESTS=0

# Function to run test suite
run_test_suite() {
    local test_file=$1
    local policy_dir=$2
    local description=$3
    
    echo ""
    echo "🔬 Running ${description}..."
    echo "   Test file: ${test_file}"
    echo "   Policy dir: ${policy_dir}"
    
    if opa test ${test_file} ${policy_dir} main.rego -v; then
        echo "✅ ${description} - PASSED"
        local test_count=$(opa test ${test_file} ${policy_dir} main.rego --count 2>/dev/null | grep -o '[0-9]* tests' | grep -o '[0-9]*' || echo "0")
        TOTAL_TESTS=$((TOTAL_TESTS + test_count))
    else
        echo "❌ ${description} - FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Run all test suites
run_test_suite "tests/constitutional_test.rego" "constitutional/" "Constitutional Policy Tests"
run_test_suite "tests/evolution_test.rego" "evolution/" "Evolution Approval Tests"
run_test_suite "tests/data_privacy_test.rego" "data/" "Data Privacy Tests"

# Run comprehensive integration test
echo ""
echo "🔗 Running integration tests..."

# Test main policy integration
echo "   Testing main policy integration..."
if opa eval -d . -i <(echo '{"type":"constitutional_evaluation","constitutional_hash":"cdd01ef066bc6cf2","action":"data.read_public","context":{"environment":{"sandbox_enabled":true,"audit_enabled":true},"agent":{"trust_level":0.9,"requested_resources":{"cpu_cores":1}},"responsible_party":"test","explanation":"Integration test"}}') 'data.acgs.main.decision.allow' > /dev/null; then
    echo "✅ Main policy integration - PASSED"
else
    echo "❌ Main policy integration - FAILED"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test policy performance
echo ""
echo "⚡ Running performance tests..."

# Performance benchmark
echo "   Running performance benchmark..."
BENCHMARK_START=$(date +%s%N)

for i in {1..100}; do
    opa eval -d . -i <(echo '{"type":"constitutional_evaluation","constitutional_hash":"cdd01ef066bc6cf2","action":"data.read_public","context":{"environment":{"sandbox_enabled":true,"audit_enabled":true},"agent":{"trust_level":0.9,"requested_resources":{"cpu_cores":1}},"responsible_party":"test","explanation":"Performance test"}}') 'data.acgs.main.decision.allow' > /dev/null
done

BENCHMARK_END=$(date +%s%N)
BENCHMARK_DURATION=$(( (BENCHMARK_END - BENCHMARK_START) / 1000000 ))  # Convert to milliseconds
AVG_LATENCY=$(( BENCHMARK_DURATION / 100 ))

echo "   Performance results:"
echo "     Total time: ${BENCHMARK_DURATION}ms for 100 evaluations"
echo "     Average latency: ${AVG_LATENCY}ms per evaluation"

if [ ${AVG_LATENCY} -lt 10 ]; then
    echo "✅ Performance test - PASSED (target: <10ms avg)"
else
    echo "⚠️  Performance test - WARNING (avg latency: ${AVG_LATENCY}ms > 10ms target)"
fi

# Test different policy scenarios
echo ""
echo "📋 Running scenario tests..."

# Scenario 1: Safe action should be allowed
echo "   Scenario 1: Safe action with proper context..."
RESULT1=$(opa eval -d . -i <(echo '{"type":"constitutional_evaluation","constitutional_hash":"cdd01ef066bc6cf2","action":"data.read_public","context":{"environment":{"sandbox_enabled":true,"audit_enabled":true},"agent":{"trust_level":0.9,"requested_resources":{"cpu_cores":1}},"responsible_party":"test","explanation":"Safe public data read for dashboard display"}}') 'data.acgs.main.decision.allow' --format raw)

if [ "$RESULT1" = "true" ]; then
    echo "✅ Scenario 1 - PASSED (safe action allowed)"
else
    echo "❌ Scenario 1 - FAILED (safe action blocked)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Scenario 2: Dangerous action should be blocked
echo "   Scenario 2: Dangerous action should be blocked..."
RESULT2=$(opa eval -d . -i <(echo '{"type":"constitutional_evaluation","constitutional_hash":"cdd01ef066bc6cf2","action":"system.execute_shell","context":{"environment":{"sandbox_enabled":true},"agent":{"trust_level":0.9}}}') 'data.acgs.main.decision.allow' --format raw)

if [ "$RESULT2" = "false" ]; then
    echo "✅ Scenario 2 - PASSED (dangerous action blocked)"
else
    echo "❌ Scenario 2 - FAILED (dangerous action allowed)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Scenario 3: Evolution approval
echo "   Scenario 3: Evolution approval workflow..."
RESULT3=$(opa eval -d . -i <(echo '{"type":"evolution_approval","constitutional_hash":"cdd01ef066bc6cf2","evolution_request":{"type":"patch","constitutional_hash":"cdd01ef066bc6cf2","changes":{"code_changes":["Bug fix"],"external_dependencies":[],"privilege_escalation":false},"performance_analysis":{"complexity_delta":0.01,"memory_delta":0.005,"latency_delta":0.0,"resource_delta":0.0},"rollback_plan":{"procedure":"Git revert","verification":"Tests","timeline":"5 min","dependencies":"None","tested":true,"automated":true}}}') 'data.acgs.main.decision.allow' --format raw)

if [ "$RESULT3" = "true" ]; then
    echo "✅ Scenario 3 - PASSED (low-risk evolution auto-approved)"
else
    echo "❌ Scenario 3 - FAILED (low-risk evolution blocked)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Scenario 4: Data access with consent
echo "   Scenario 4: Data access with proper consent..."
RESULT4=$(opa eval -d . -i <(echo '{"type":"data_access","constitutional_hash":"cdd01ef066bc6cf2","data_request":{"data_fields":[{"name":"public_metrics","classification_level":0,"category":"analytics"}],"requester_clearance_level":0,"purpose":"dashboard_display","allowed_purposes":["dashboard_display","reporting"],"justified_fields":["public_metrics"],"timestamp":1704067200,"retention_policy":{"analytics":2592000},"encryption_config":{"public_metrics":{"encrypted":false}}}}') 'data.acgs.main.decision.allow' --format raw)

if [ "$RESULT4" = "true" ]; then
    echo "✅ Scenario 4 - PASSED (public data access allowed)"
else
    echo "❌ Scenario 4 - FAILED (public data access blocked)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test health endpoint
echo ""
echo "🏥 Testing health endpoint..."
HEALTH_RESULT=$(opa eval -d . 'data.acgs.main.health.status' --format raw)

if [ "$HEALTH_RESULT" = '"healthy"' ]; then
    echo "✅ Health check - PASSED"
else
    echo "❌ Health check - FAILED"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test constitutional hash verification
echo ""
echo "🔒 Testing constitutional hash verification..."
HASH_RESULT=$(opa eval -d . 'data.acgs.main.constitutional_hash' --format raw)

if [ "$HASH_RESULT" = '"cdd01ef066bc6cf2"' ]; then
    echo "✅ Constitutional hash verification - PASSED"
else
    echo "❌ Constitutional hash verification - FAILED"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test unknown request type handling
echo ""
echo "🤷 Testing unknown request type handling..."
UNKNOWN_RESULT=$(opa eval -d . -i <(echo '{"type":"unknown_type","constitutional_hash":"cdd01ef066bc6cf2"}') 'data.acgs.main.decision.allow' --format raw)

if [ "$UNKNOWN_RESULT" = "false" ]; then
    echo "✅ Unknown request type handling - PASSED (properly denied)"
else
    echo "❌ Unknown request type handling - FAILED (incorrectly allowed)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="
echo "Total policy evaluations: ${TOTAL_TESTS}"
echo "Performance: ${AVG_LATENCY}ms average latency"
echo "Failed test suites: ${FAILED_TESTS}"

if [ ${FAILED_TESTS} -eq 0 ]; then
    echo ""
    echo "🎉 All tests PASSED!"
    echo "✅ Policy bundle is ready for deployment"
    echo ""
    echo "Constitutional Hash: cdd01ef066bc6cf2"
    exit 0
else
    echo ""
    echo "❌ ${FAILED_TESTS} test suite(s) FAILED!"
    echo "🔧 Please fix failing tests before deployment"
    echo ""
    echo "Constitutional Hash: cdd01ef066bc6cf2"
    exit 1
fi