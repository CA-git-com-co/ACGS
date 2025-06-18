#!/bin/bash
# ACGS-1 Redis Cluster Health Check Script
# Phase 2 - Enterprise Scalability & Performance
# Comprehensive health monitoring for Redis cluster

set -e

echo "🔍 ACGS-1 Redis Cluster Health Check"

# Colors for output
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

# Redis cluster nodes
MASTER_NODES=(
    "redis-master-1:7001"
    "redis-master-2:7002"
    "redis-master-3:7003"
)

REPLICA_NODES=(
    "redis-replica-1:7004"
    "redis-replica-2:7005"
    "redis-replica-3:7006"
)

ALL_NODES=("${MASTER_NODES[@]}" "${REPLICA_NODES[@]}")

# Health check results
HEALTH_RESULTS=()
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Function to record health check result
record_check() {
    local check_name="$1"
    local status="$2"
    local details="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ "$status" = "PASS" ]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        print_success "$check_name: PASS"
    elif [ "$status" = "WARN" ]; then
        print_warning "$check_name: WARNING - $details"
    else
        print_error "$check_name: FAIL - $details"
    fi
    
    HEALTH_RESULTS+=("$check_name:$status:$details")
}

# Check individual node connectivity
print_status "Checking individual node connectivity..."
for node in "${ALL_NODES[@]}"; do
    host=$(echo $node | cut -d: -f1)
    port=$(echo $node | cut -d: -f2)
    
    if redis-cli -h $host -p $port ping > /dev/null 2>&1; then
        record_check "Node $host:$port connectivity" "PASS" ""
    else
        record_check "Node $host:$port connectivity" "FAIL" "Node not responding to ping"
    fi
done

# Check cluster state
print_status "Checking cluster state..."
cluster_info=$(redis-cli -h redis-master-1 -p 7001 cluster info 2>/dev/null)

if [ $? -eq 0 ]; then
    cluster_state=$(echo "$cluster_info" | grep cluster_state | cut -d: -f2 | tr -d '\r')
    if [ "$cluster_state" = "ok" ]; then
        record_check "Cluster state" "PASS" ""
    else
        record_check "Cluster state" "FAIL" "State is $cluster_state (expected: ok)"
    fi
    
    # Check slots assignment
    cluster_slots_assigned=$(echo "$cluster_info" | grep cluster_slots_assigned | cut -d: -f2 | tr -d '\r')
    if [ "$cluster_slots_assigned" = "16384" ]; then
        record_check "Slot assignment" "PASS" ""
    else
        record_check "Slot assignment" "FAIL" "Only $cluster_slots_assigned/16384 slots assigned"
    fi
    
    # Check known nodes
    cluster_known_nodes=$(echo "$cluster_info" | grep cluster_known_nodes | cut -d: -f2 | tr -d '\r')
    if [ "$cluster_known_nodes" = "6" ]; then
        record_check "Known nodes count" "PASS" ""
    else
        record_check "Known nodes count" "WARN" "Expected 6 nodes, found $cluster_known_nodes"
    fi
    
    # Check cluster size
    cluster_size=$(echo "$cluster_info" | grep cluster_size | cut -d: -f2 | tr -d '\r')
    if [ "$cluster_size" = "3" ]; then
        record_check "Cluster size" "PASS" ""
    else
        record_check "Cluster size" "FAIL" "Expected 3 masters, found $cluster_size"
    fi
else
    record_check "Cluster info retrieval" "FAIL" "Cannot retrieve cluster info"
fi

# Check individual node roles and status
print_status "Checking node roles and status..."
cluster_nodes=$(redis-cli -h redis-master-1 -p 7001 cluster nodes 2>/dev/null)

if [ $? -eq 0 ]; then
    master_count=$(echo "$cluster_nodes" | grep -c "master")
    replica_count=$(echo "$cluster_nodes" | grep -c "slave")
    
    if [ "$master_count" = "3" ]; then
        record_check "Master nodes count" "PASS" ""
    else
        record_check "Master nodes count" "FAIL" "Expected 3 masters, found $master_count"
    fi
    
    if [ "$replica_count" = "3" ]; then
        record_check "Replica nodes count" "PASS" ""
    else
        record_check "Replica nodes count" "FAIL" "Expected 3 replicas, found $replica_count"
    fi
    
    # Check for failed nodes
    failed_nodes=$(echo "$cluster_nodes" | grep -c "fail")
    if [ "$failed_nodes" = "0" ]; then
        record_check "Failed nodes" "PASS" ""
    else
        record_check "Failed nodes" "FAIL" "$failed_nodes nodes in failed state"
    fi
else
    record_check "Cluster nodes retrieval" "FAIL" "Cannot retrieve cluster nodes info"
fi

# Test cluster functionality
print_status "Testing cluster functionality..."

# Test key distribution across slots
test_keys=(
    "health:test:1"
    "health:test:2"
    "health:test:3"
)

successful_operations=0
total_operations=0

for key in "${test_keys[@]}"; do
    # Test SET operation
    total_operations=$((total_operations + 1))
    if redis-cli -c -h redis-master-1 -p 7001 set "$key" "health_check_$(date +%s)" > /dev/null 2>&1; then
        successful_operations=$((successful_operations + 1))
        
        # Test GET operation
        total_operations=$((total_operations + 1))
        if redis-cli -c -h redis-master-1 -p 7001 get "$key" > /dev/null 2>&1; then
            successful_operations=$((successful_operations + 1))
        fi
        
        # Clean up
        redis-cli -c -h redis-master-1 -p 7001 del "$key" > /dev/null 2>&1
    fi
done

if [ "$successful_operations" = "$total_operations" ]; then
    record_check "Cluster operations" "PASS" ""
else
    record_check "Cluster operations" "FAIL" "$successful_operations/$total_operations operations successful"
fi

# Check memory usage
print_status "Checking memory usage..."
for node in "${MASTER_NODES[@]}"; do
    host=$(echo $node | cut -d: -f1)
    port=$(echo $node | cut -d: -f2)
    
    memory_info=$(redis-cli -h $host -p $port info memory 2>/dev/null)
    if [ $? -eq 0 ]; then
        used_memory=$(echo "$memory_info" | grep "used_memory:" | cut -d: -f2 | tr -d '\r')
        max_memory=$(echo "$memory_info" | grep "maxmemory:" | cut -d: -f2 | tr -d '\r')
        
        if [ "$max_memory" != "0" ]; then
            # Calculate memory usage percentage
            usage_percent=$(echo "scale=2; $used_memory * 100 / $max_memory" | bc 2>/dev/null || echo "0")
            
            if (( $(echo "$usage_percent < 80" | bc -l) )); then
                record_check "Memory usage $host:$port" "PASS" "${usage_percent}%"
            elif (( $(echo "$usage_percent < 90" | bc -l) )); then
                record_check "Memory usage $host:$port" "WARN" "${usage_percent}% (approaching limit)"
            else
                record_check "Memory usage $host:$port" "FAIL" "${usage_percent}% (critical)"
            fi
        else
            record_check "Memory usage $host:$port" "WARN" "No memory limit set"
        fi
    else
        record_check "Memory info $host:$port" "FAIL" "Cannot retrieve memory info"
    fi
done

# Check replication lag
print_status "Checking replication lag..."
for node in "${REPLICA_NODES[@]}"; do
    host=$(echo $node | cut -d: -f1)
    port=$(echo $node | cut -d: -f2)
    
    replication_info=$(redis-cli -h $host -p $port info replication 2>/dev/null)
    if [ $? -eq 0 ]; then
        master_link_status=$(echo "$replication_info" | grep "master_link_status:" | cut -d: -f2 | tr -d '\r')
        
        if [ "$master_link_status" = "up" ]; then
            # Check replication lag
            master_last_io=$(echo "$replication_info" | grep "master_last_io_seconds_ago:" | cut -d: -f2 | tr -d '\r')
            
            if [ -n "$master_last_io" ] && [ "$master_last_io" -lt 5 ]; then
                record_check "Replication $host:$port" "PASS" "Lag: ${master_last_io}s"
            elif [ -n "$master_last_io" ] && [ "$master_last_io" -lt 30 ]; then
                record_check "Replication $host:$port" "WARN" "High lag: ${master_last_io}s"
            else
                record_check "Replication $host:$port" "FAIL" "Critical lag: ${master_last_io}s"
            fi
        else
            record_check "Replication $host:$port" "FAIL" "Master link status: $master_link_status"
        fi
    else
        record_check "Replication info $host:$port" "FAIL" "Cannot retrieve replication info"
    fi
done

# Performance check
print_status "Running performance check..."
start_time=$(date +%s%N)
redis-cli -c -h redis-master-1 -p 7001 eval "
for i=1,100 do
    redis.call('set', 'perf:test:' .. i, 'value' .. i)
    redis.call('get', 'perf:test:' .. i)
    redis.call('del', 'perf:test:' .. i)
end
return 'OK'
" 0 > /dev/null 2>&1
end_time=$(date +%s%N)

if [ $? -eq 0 ]; then
    duration_ms=$(( (end_time - start_time) / 1000000 ))
    ops_per_sec=$(( 300 * 1000 / duration_ms ))  # 300 operations (100 sets + 100 gets + 100 dels)
    
    if [ "$ops_per_sec" -gt 1000 ]; then
        record_check "Performance test" "PASS" "${ops_per_sec} ops/sec"
    elif [ "$ops_per_sec" -gt 500 ]; then
        record_check "Performance test" "WARN" "${ops_per_sec} ops/sec (below optimal)"
    else
        record_check "Performance test" "FAIL" "${ops_per_sec} ops/sec (poor performance)"
    fi
else
    record_check "Performance test" "FAIL" "Performance test failed to execute"
fi

# Generate health report
print_status "Generating health report..."

echo ""
echo "=" * 60
echo "ACGS-1 Redis Cluster Health Report"
echo "Generated: $(date)"
echo "=" * 60

echo ""
echo "Overall Health: $PASSED_CHECKS/$TOTAL_CHECKS checks passed"

if [ "$PASSED_CHECKS" = "$TOTAL_CHECKS" ]; then
    print_success "Cluster is HEALTHY"
    exit_code=0
elif [ "$PASSED_CHECKS" -ge $((TOTAL_CHECKS * 80 / 100)) ]; then
    print_warning "Cluster has WARNINGS"
    exit_code=1
else
    print_error "Cluster is UNHEALTHY"
    exit_code=2
fi

echo ""
echo "Detailed Results:"
for result in "${HEALTH_RESULTS[@]}"; do
    IFS=':' read -r check status details <<< "$result"
    if [ "$status" = "PASS" ]; then
        echo "  ✅ $check"
    elif [ "$status" = "WARN" ]; then
        echo "  ⚠️  $check - $details"
    else
        echo "  ❌ $check - $details"
    fi
done

echo ""
echo "Cluster Information:"
if [ -n "$cluster_info" ]; then
    echo "$cluster_info" | while IFS= read -r line; do
        echo "  $line"
    done
fi

# Save report to file
report_file="logs/redis_cluster_health_$(date +%Y%m%d_%H%M%S).log"
{
    echo "ACGS-1 Redis Cluster Health Report"
    echo "Generated: $(date)"
    echo "Overall Health: $PASSED_CHECKS/$TOTAL_CHECKS checks passed"
    echo ""
    for result in "${HEALTH_RESULTS[@]}"; do
        echo "$result"
    done
} > "$report_file"

print_status "Health report saved to: $report_file"

exit $exit_code
