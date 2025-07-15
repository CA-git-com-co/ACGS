#!/bin/bash

# ACGS-PGP Comprehensive Load Testing Suite
# Validates performance targets, constitutional compliance, and system stability

set -e

NAMESPACE="acgs-staging"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TARGET_RPS=1000
TARGET_RESPONSE_TIME=2.0
CONSTITUTIONAL_THRESHOLD=0.95
TEST_DURATION=300  # 5 minutes

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $(date '+%H:%M:%S') $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $1"; }
log_test() { echo -e "${BLUE}[TEST]${NC} $(date '+%H:%M:%S') $1"; }
log_perf() { echo -e "${PURPLE}[PERF]${NC} $(date '+%H:%M:%S') $1"; }

# Test configuration
declare -A SERVICES=(
    ["auth-service"]="8000"
    ["constitutional-ai-service"]="8001"
    ["integrity-service"]="8002"
    ["formal-verification-service"]="8003"
    ["governance-synthesis-service"]="8004"
    ["policy-governance-service"]="8005"
    ["evolutionary-computation-service"]="8006"
    ["model-orchestrator-service"]="8007"
)

# Create load testing pod
create_load_test_pod() {
    log_test "Creating advanced load testing pod..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: acgs-load-tester
  namespace: $NAMESPACE
  labels:
    app: load-tester
spec:
  restartPolicy: Never
  containers:
  - name: load-tester
    image: curlimages/curl:latest
    command: ["sleep", "7200"]  # 2 hours
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1000m
        memory: 2Gi
    env:
    - name: CONSTITUTIONAL_HASH
      value: "$CONSTITUTIONAL_HASH"
    - name: TARGET_RPS
      value: "$TARGET_RPS"
    - name: TEST_DURATION
      value: "$TEST_DURATION"
EOF
    
    # Wait for pod to be ready
    kubectl wait --for=condition=ready pod/acgs-load-tester -n $NAMESPACE --timeout=60s
    log_info "✓ Load testing pod ready"
}

# Baseline performance test
baseline_performance_test() {
    log_test "Running baseline performance test..."
    
    local results_file="/tmp/baseline_results.txt"
    
    # Test each service individually
    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"
        
        log_test "Testing $service baseline performance..."
        
        # Single request test
        local response_time=$(kubectl exec acgs-load-tester -n $NAMESPACE -- \
            curl -w "%{time_total}" -o /dev/null -s \
            http://$service:$port/health 2>/dev/null || echo "999")
        
        if (( $(echo "$response_time < $TARGET_RESPONSE_TIME" | bc -l 2>/dev/null || echo "0") )); then
            log_info "✓ $service baseline: ${response_time}s (<${TARGET_RESPONSE_TIME}s)"
        else
            log_warn "⚠ $service baseline: ${response_time}s (>${TARGET_RESPONSE_TIME}s)"
        fi
        
        echo "$service:$response_time" >> "$results_file"
    done
    
    log_info "✓ Baseline performance test completed"
}

# Constitutional compliance load test
constitutional_compliance_test() {
    log_test "Running constitutional compliance load test..."
    
    local compliance_results="/tmp/compliance_results.txt"
    local test_queries=(
        '{"query": "test constitutional compliance", "context": "load_test_1"}'
        '{"query": "validate safety protocols", "context": "load_test_2"}'
        '{"query": "check governance rules", "context": "load_test_3"}'
        '{"query": "verify policy adherence", "context": "load_test_4"}'
        '{"query": "assess constitutional alignment", "context": "load_test_5"}'
    )
    
    local total_tests=0
    local passed_tests=0
    
    # Run multiple constitutional compliance tests
    for i in {1..20}; do
        local query_index=$((i % ${#test_queries[@]}))
        local test_query="${test_queries[$query_index]}"
        
        log_test "Constitutional test $i/20..."
        
        local response=$(kubectl exec acgs-load-tester -n $NAMESPACE -- \
            curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$test_query" \
            http://constitutional-ai-service:8001/validate 2>/dev/null || echo '{"compliance_score": 0}')
        
        # Extract compliance score (simplified)
        local compliance_score=$(echo "$response" | grep -o '"compliance_score":[0-9.]*' | cut -d: -f2 || echo "0")
        
        ((total_tests++))
        
        if (( $(echo "$compliance_score >= $CONSTITUTIONAL_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
            ((passed_tests++))
            log_info "✓ Test $i: compliance score $compliance_score"
        else
            log_warn "⚠ Test $i: compliance score $compliance_score (below threshold)"
        fi
        
        echo "test_$i:$compliance_score" >> "$compliance_results"
        
        # Small delay between tests
        sleep 0.5
    done
    
    local compliance_rate=$(echo "scale=2; $passed_tests * 100 / $total_tests" | bc -l)
    
    if (( $(echo "$compliance_rate >= 95" | bc -l) )); then
        log_info "✓ Constitutional compliance rate: $compliance_rate% (>95%)"
    else
        log_error "✗ Constitutional compliance rate: $compliance_rate% (<95%)"
    fi
    
    echo "overall_compliance_rate:$compliance_rate" >> "$compliance_results"
}

# Concurrent load test
concurrent_load_test() {
    log_test "Running concurrent load test..."
    
    local concurrent_users=20
    local requests_per_user=50
    local results_dir="/tmp/concurrent_results"
    
    # Create concurrent test script
    kubectl exec acgs-load-tester -n $NAMESPACE -- sh -c "
cat > /tmp/concurrent_test.sh << 'SCRIPT'
#!/bin/sh
SERVICE=\$1
PORT=\$2
USER_ID=\$3
REQUESTS=\$4

echo \"User \$USER_ID starting \$REQUESTS requests to \$SERVICE:\$PORT\"

for i in \$(seq 1 \$REQUESTS); do
    START_TIME=\$(date +%s.%N)
    
    RESPONSE=\$(curl -w '%{http_code}:%{time_total}' -o /dev/null -s http://\$SERVICE:\$PORT/health 2>/dev/null || echo '000:999')
    
    HTTP_CODE=\$(echo \$RESPONSE | cut -d: -f1)
    RESPONSE_TIME=\$(echo \$RESPONSE | cut -d: -f2)
    
    echo \"User\$USER_ID,Request\$i,\$HTTP_CODE,\$RESPONSE_TIME\"
    
    # Small delay to simulate realistic usage
    sleep 0.1
done
SCRIPT
chmod +x /tmp/concurrent_test.sh
"
    
    # Test each critical service
    local critical_services=("auth-service:8000" "constitutional-ai-service:8001")
    
    for service_port in "${critical_services[@]}"; do
        local service=$(echo $service_port | cut -d: -f1)
        local port=$(echo $service_port | cut -d: -f2)
        
        log_test "Running concurrent test for $service..."
        
        # Launch concurrent users
        local pids=()
        for user_id in $(seq 1 $concurrent_users); do
            kubectl exec acgs-load-tester -n $NAMESPACE -- \
                /tmp/concurrent_test.sh "$service" "$port" "$user_id" "$requests_per_user" > "/tmp/${service}_user_${user_id}.log" &
            pids+=($!)
        done
        
        # Wait for all users to complete
        for pid in "${pids[@]}"; do
            wait $pid 2>/dev/null || true
        done
        
        # Analyze results
        kubectl exec acgs-load-tester -n $NAMESPACE -- sh -c "
            cat /tmp/${service}_user_*.log > /tmp/${service}_all_results.log
            
            TOTAL_REQUESTS=\$(wc -l < /tmp/${service}_all_results.log)
            SUCCESS_REQUESTS=\$(grep ',200,' /tmp/${service}_all_results.log | wc -l)
            
            if [ \$TOTAL_REQUESTS -gt 0 ]; then
                SUCCESS_RATE=\$(echo \"scale=2; \$SUCCESS_REQUESTS * 100 / \$TOTAL_REQUESTS\" | bc -l)
                AVG_RESPONSE_TIME=\$(awk -F, '{sum+=\$4; count++} END {if(count>0) print sum/count; else print 0}' /tmp/${service}_all_results.log)
                
                echo \"$service Results:\"
                echo \"  Total Requests: \$TOTAL_REQUESTS\"
                echo \"  Success Rate: \$SUCCESS_RATE%\"
                echo \"  Average Response Time: \$AVG_RESPONSE_TIME seconds\"
                
                if [ \$(echo \"\$SUCCESS_RATE >= 95\" | bc -l) -eq 1 ] && [ \$(echo \"\$AVG_RESPONSE_TIME <= $TARGET_RESPONSE_TIME\" | bc -l) -eq 1 ]; then
                    echo \"  Status: PASS\"
                else
                    echo \"  Status: FAIL\"
                fi
            fi
        "
        
        log_info "✓ Concurrent test completed for $service"
    done
}

# Stress test
stress_test() {
    log_test "Running stress test..."
    
    local stress_duration=60  # 1 minute stress test
    local high_rps=200  # Higher than normal load
    
    log_test "Applying stress load ($high_rps RPS for ${stress_duration}s)..."
    
    # Create stress test script
    kubectl exec acgs-load-tester -n $NAMESPACE -- sh -c "
cat > /tmp/stress_test.sh << 'SCRIPT'
#!/bin/sh
DURATION=\$1
RPS=\$2

echo \"Starting stress test: \$RPS RPS for \$DURATION seconds\"

END_TIME=\$((\$(date +%s) + \$DURATION))
REQUEST_COUNT=0
SUCCESS_COUNT=0

while [ \$(date +%s) -lt \$END_TIME ]; do
    START_TIME=\$(date +%s.%N)
    
    # Test constitutional AI service under stress
    RESPONSE=\$(curl -w '%{http_code}' -o /dev/null -s http://constitutional-ai-service:8001/health 2>/dev/null || echo '000')
    
    REQUEST_COUNT=\$((REQUEST_COUNT + 1))
    
    if [ \"\$RESPONSE\" = \"200\" ]; then
        SUCCESS_COUNT=\$((SUCCESS_COUNT + 1))
    fi
    
    # Calculate delay to maintain RPS
    ELAPSED=\$(echo \"\$(date +%s.%N) - \$START_TIME\" | bc -l)
    TARGET_DELAY=\$(echo \"1.0 / \$RPS\" | bc -l)
    SLEEP_TIME=\$(echo \"\$TARGET_DELAY - \$ELAPSED\" | bc -l)
    
    if [ \$(echo \"\$SLEEP_TIME > 0\" | bc -l) -eq 1 ]; then
        sleep \$SLEEP_TIME
    fi
done

SUCCESS_RATE=\$(echo \"scale=2; \$SUCCESS_COUNT * 100 / \$REQUEST_COUNT\" | bc -l)
echo \"Stress test completed:\"
echo \"  Total Requests: \$REQUEST_COUNT\"
echo \"  Success Rate: \$SUCCESS_RATE%\"

if [ \$(echo \"\$SUCCESS_RATE >= 90\" | bc -l) -eq 1 ]; then
    echo \"  Status: PASS\"
else
    echo \"  Status: FAIL\"
fi
SCRIPT
chmod +x /tmp/stress_test.sh
"
    
    # Run stress test
    kubectl exec acgs-load-tester -n $NAMESPACE -- /tmp/stress_test.sh "$stress_duration" "$high_rps"
    
    log_info "✓ Stress test completed"
}

# Resource monitoring during tests
monitor_resources() {
    log_test "Monitoring resource usage during tests..."
    
    # Monitor for 30 seconds
    for i in {1..6}; do
        log_perf "Resource check $i/6..."
        
        # Get resource usage
        local resource_output=$(kubectl top pods -n $NAMESPACE --no-headers 2>/dev/null || echo "metrics-unavailable")
        
        if [[ "$resource_output" != "metrics-unavailable" ]]; then
            echo "$resource_output" | while IFS= read -r line; do
                if [[ -n "$line" ]]; then
                    local pod_name=$(echo "$line" | awk '{print $1}')
                    local cpu_usage=$(echo "$line" | awk '{print $2}' | sed 's/m//')
                    local memory_usage=$(echo "$line" | awk '{print $3}' | sed 's/Mi//')
                    
                    # Check if usage is within limits
                    if [[ "$cpu_usage" -gt 400 ]]; then  # 80% of 500m limit
                        log_warn "High CPU usage: $pod_name ($cpu_usage m)"
                    fi
                    
                    if [[ "$memory_usage" -gt 800 ]]; then  # 80% of 1Gi limit
                        log_warn "High memory usage: $pod_name ($memory_usage Mi)"
                    fi
                fi
            done
        else
            log_warn "Resource metrics not available"
        fi
        
        sleep 5
    done
    
    log_info "✓ Resource monitoring completed"
}

# Generate comprehensive test report
generate_test_report() {
    local report_file="/tmp/acgs_load_test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS-PGP Comprehensive Load Test Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Namespace: $NAMESPACE"
        echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
        echo "Target RPS: $TARGET_RPS"
        echo "Target Response Time: ${TARGET_RESPONSE_TIME}s"
        echo "Constitutional Threshold: $CONSTITUTIONAL_THRESHOLD"
        echo "========================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        echo
        
        echo "Test Summary:"
        echo "1. Baseline Performance Test - Individual service response times"
        echo "2. Constitutional Compliance Test - 20 compliance validations"
        echo "3. Concurrent Load Test - 20 users, 50 requests each"
        echo "4. Stress Test - High RPS for 60 seconds"
        echo "5. Resource Monitoring - CPU/Memory usage tracking"
        echo
        
        echo "Service Status:"
        kubectl get pods -n $NAMESPACE -o wide
        echo
        
        echo "Resource Usage:"
        kubectl top pods -n $NAMESPACE 2>/dev/null || echo "Metrics not available"
        echo
        
        echo "Recent Events:"
        kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
        
    } > "$report_file"
    
    log_test "Comprehensive test report generated: $report_file"
    echo "$report_file"
}

# Cleanup test resources
cleanup_test_resources() {
    log_test "Cleaning up test resources..."
    
    kubectl delete pod acgs-load-tester -n $NAMESPACE --ignore-not-found=true
    
    log_info "✓ Test resources cleaned up"
}

# Main test execution
main() {
    local action=${1:-"full"}
    
    case $action in
        "full")
            log_test "Starting comprehensive ACGS-PGP load testing..."
            
            create_load_test_pod
            baseline_performance_test
            constitutional_compliance_test
            concurrent_load_test
            stress_test
            monitor_resources
            
            local report_file=$(generate_test_report)
            
            log_test "🎉 Comprehensive load testing completed!"
            log_test "Report: $report_file"
            
            cleanup_test_resources
            ;;
        "baseline")
            create_load_test_pod
            baseline_performance_test
            cleanup_test_resources
            ;;
        "compliance")
            create_load_test_pod
            constitutional_compliance_test
            cleanup_test_resources
            ;;
        "concurrent")
            create_load_test_pod
            concurrent_load_test
            cleanup_test_resources
            ;;
        "stress")
            create_load_test_pod
            stress_test
            cleanup_test_resources
            ;;
        *)
            echo "Usage: $0 {full|baseline|compliance|concurrent|stress}"
            echo "  full       - Run all load tests"
            echo "  baseline   - Run baseline performance test only"
            echo "  compliance - Run constitutional compliance test only"
            echo "  concurrent - Run concurrent load test only"
            echo "  stress     - Run stress test only"
            exit 1
            ;;
    esac
}

main "$@"
