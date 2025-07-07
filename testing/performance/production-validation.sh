#!/bin/bash
# ACGS Production Infrastructure Validation
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "=== ACGS Production Infrastructure Validation ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo ""

# Validation results
VALIDATION_RESULTS=()
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to add test result
add_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$result" = "PASS" ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "✓ $test_name: $details"
    else
        echo "✗ $test_name: $details"
    fi
    
    VALIDATION_RESULTS+=("$test_name:$result:$details")
}

echo "1. Infrastructure Health Validation"
echo "-----------------------------------"

# Test PostgreSQL availability and basic performance
echo "Testing PostgreSQL..."
if docker exec acgs_postgres_production pg_isready -U acgs_user -d acgs > /dev/null 2>&1; then
    # Test basic query performance
    PG_START=$(date +%s%N)
    docker exec acgs_postgres_production psql -U acgs_user -d acgs -c "SELECT version();" > /dev/null 2>&1
    PG_END=$(date +%s%N)
    PG_LATENCY=$(( (PG_END - PG_START) / 1000000 ))
    
    if [ $PG_LATENCY -lt 100 ]; then  # Adjusted for containerized environment
        add_result "PostgreSQL Health" "PASS" "Available, query latency: ${PG_LATENCY}ms"
    else
        add_result "PostgreSQL Health" "FAIL" "High latency: ${PG_LATENCY}ms"
    fi
else
    add_result "PostgreSQL Health" "FAIL" "Database not accessible"
fi

# Test Redis availability and performance
echo "Testing Redis..."
if docker exec acgs_redis_production redis-cli -a redis_production_password_2025 ping > /dev/null 2>&1; then
    REDIS_START=$(date +%s%N)
    docker exec acgs_redis_production redis-cli -a redis_production_password_2025 set test_key test_value > /dev/null 2>&1
    docker exec acgs_redis_production redis-cli -a redis_production_password_2025 get test_key > /dev/null 2>&1
    docker exec acgs_redis_production redis-cli -a redis_production_password_2025 del test_key > /dev/null 2>&1
    REDIS_END=$(date +%s%N)
    REDIS_LATENCY=$(( (REDIS_END - REDIS_START) / 1000000 ))
    
    if [ $REDIS_LATENCY -lt 50 ]; then  # Adjusted for containerized environment
        add_result "Redis Health" "PASS" "Available, operation latency: ${REDIS_LATENCY}ms"
    else
        add_result "Redis Health" "FAIL" "High latency: ${REDIS_LATENCY}ms"
    fi
else
    add_result "Redis Health" "FAIL" "Redis not accessible"
fi

echo ""
echo "2. Monitoring System Validation"
echo "-------------------------------"

# Test Prometheus
echo "Testing Prometheus..."
if curl -s http://localhost:9091/api/v1/status/config > /dev/null; then
    # Test query performance
    PROM_START=$(date +%s%N)
    PROM_RESPONSE=$(curl -s "http://localhost:9091/api/v1/query?query=up")
    PROM_END=$(date +%s%N)
    PROM_LATENCY=$(( (PROM_END - PROM_START) / 1000000 ))
    
    if echo "$PROM_RESPONSE" | grep -q '"status":"success"'; then
        add_result "Prometheus Health" "PASS" "Available, query latency: ${PROM_LATENCY}ms"
    else
        add_result "Prometheus Health" "FAIL" "Query failed"
    fi
else
    add_result "Prometheus Health" "FAIL" "Prometheus not accessible"
fi

# Test Grafana
echo "Testing Grafana..."
if curl -s http://localhost:3001/api/health > /dev/null; then
    GRAFANA_RESPONSE=$(curl -s http://localhost:3001/api/health)
    if echo "$GRAFANA_RESPONSE" | grep -q '"database":"ok"'; then
        add_result "Grafana Health" "PASS" "Available and healthy"
    else
        add_result "Grafana Health" "FAIL" "Health check failed"
    fi
else
    add_result "Grafana Health" "FAIL" "Grafana not accessible"
fi

echo ""
echo "3. Alert System Validation"
echo "--------------------------"

# Test Alert Rules
echo "Testing Alert Rules..."
ALERT_RULES=$(curl -s http://localhost:9091/api/v1/rules | jq -r '.data.groups | length' 2>/dev/null || echo "0")
if [ "$ALERT_RULES" -ge 4 ]; then
    add_result "Alert Rules" "PASS" "$ALERT_RULES rule groups loaded"
else
    add_result "Alert Rules" "FAIL" "Expected 4+ rule groups, found $ALERT_RULES"
fi

# Test Active Alerts (should have some due to services being down)
echo "Testing Active Alerts..."
ACTIVE_ALERTS=$(curl -s http://localhost:9091/api/v1/alerts | jq -r '.data.alerts | length' 2>/dev/null || echo "0")
if [ "$ACTIVE_ALERTS" -gt 0 ]; then
    add_result "Alert System" "PASS" "$ACTIVE_ALERTS active alerts (expected)"
else
    add_result "Alert System" "FAIL" "No alerts active (unexpected)"
fi

echo ""
echo "4. Dashboard Validation"
echo "-----------------------"

# Test Grafana Dashboards
echo "Testing Grafana Dashboards..."
DASHBOARD_COUNT=$(curl -s -u admin:acgs_admin_2025 http://localhost:3001/api/search?type=dash-db | jq '. | length' 2>/dev/null || echo "0")
if [ "$DASHBOARD_COUNT" -ge 3 ]; then
    add_result "Grafana Dashboards" "PASS" "$DASHBOARD_COUNT dashboards imported"
else
    add_result "Grafana Dashboards" "FAIL" "Expected 3+ dashboards, found $DASHBOARD_COUNT"
fi

echo ""
echo "5. Constitutional Compliance Validation"
echo "---------------------------------------"

# Test Constitutional Hash in Prometheus Config
echo "Testing Constitutional Hash..."
HASH_COUNT=$(curl -s http://localhost:9091/api/v1/status/config | grep -c "cdd01ef066bc6cf2" 2>/dev/null || echo "0")
if [ "$HASH_COUNT" -gt 0 ]; then
    add_result "Constitutional Compliance" "PASS" "Hash found $HASH_COUNT times in config"
else
    add_result "Constitutional Compliance" "FAIL" "Constitutional hash not found"
fi

# Test Alert Rules contain Constitutional Hash
ALERT_HASH_COUNT=$(curl -s http://localhost:9091/api/v1/rules | grep -c "cdd01ef066bc6cf2" 2>/dev/null || echo "0")
if [ "$ALERT_HASH_COUNT" -gt 0 ]; then
    add_result "Alert Rule Compliance" "PASS" "Hash found $ALERT_HASH_COUNT times in alert rules"
else
    add_result "Alert Rule Compliance" "FAIL" "Constitutional hash not found in alert rules"
fi

echo ""
echo "6. Performance Baseline Validation"
echo "----------------------------------"

# Test sustained monitoring load
echo "Testing sustained monitoring load..."
LOAD_START=$(date +%s)
REQUEST_COUNT=0
FAILED_REQUESTS=0

# Run for 30 seconds with moderate load
while [ $(($(date +%s) - LOAD_START)) -lt 30 ]; do
    if curl -s "http://localhost:9091/api/v1/query?query=up" > /dev/null 2>&1; then
        REQUEST_COUNT=$((REQUEST_COUNT + 1))
    else
        FAILED_REQUESTS=$((FAILED_REQUESTS + 1))
    fi
    sleep 0.5  # 2 RPS sustained load
done

SUCCESS_RATE=$(( (REQUEST_COUNT * 100) / (REQUEST_COUNT + FAILED_REQUESTS) ))
if [ $SUCCESS_RATE -ge 95 ]; then
    add_result "Sustained Load" "PASS" "$REQUEST_COUNT requests, $SUCCESS_RATE% success rate"
else
    add_result "Sustained Load" "FAIL" "$REQUEST_COUNT requests, $SUCCESS_RATE% success rate"
fi

echo ""
echo "=== VALIDATION SUMMARY ==="
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "Tests Passed: $PASSED_TESTS/$TOTAL_TESTS ($(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%)"
echo ""

# Save detailed results
RESULTS_FILE="testing/performance/production-validation-results.json"
mkdir -p testing/performance

cat > "$RESULTS_FILE" << EOF
{
  "constitutional_hash": "cdd01ef066bc6cf2",
  "timestamp": $(date +%s),
  "validation_type": "production_infrastructure",
  "summary": {
    "total_tests": $TOTAL_TESTS,
    "passed_tests": $PASSED_TESTS,
    "success_rate": $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
  },
  "results": [
EOF

# Add individual results
for i in "${!VALIDATION_RESULTS[@]}"; do
    IFS=':' read -r test_name result details <<< "${VALIDATION_RESULTS[$i]}"
    echo "    {" >> "$RESULTS_FILE"
    echo "      \"test_name\": \"$test_name\"," >> "$RESULTS_FILE"
    echo "      \"result\": \"$result\"," >> "$RESULTS_FILE"
    echo "      \"details\": \"$details\"," >> "$RESULTS_FILE"
    echo "      \"constitutional_hash\": \"cdd01ef066bc6cf2\"" >> "$RESULTS_FILE"
    if [ $i -eq $((${#VALIDATION_RESULTS[@]} - 1)) ]; then
        echo "    }" >> "$RESULTS_FILE"
    else
        echo "    }," >> "$RESULTS_FILE"
    fi
done

cat >> "$RESULTS_FILE" << EOF
  ]
}
EOF

echo "Detailed results saved to: $RESULTS_FILE"
echo "Constitutional Hash: cdd01ef066bc6cf2"

# Exit with appropriate code
if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo ""
    echo "✓ ALL PRODUCTION VALIDATION TESTS PASSED"
    exit 0
else
    echo ""
    echo "✗ SOME VALIDATION TESTS FAILED"
    exit 1
fi
