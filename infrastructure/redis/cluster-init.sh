#!/bin/bash
# ACGS-1 Redis Cluster Initialization Script
# Phase 2 - Enterprise Scalability & Performance
# Initializes 6-node Redis cluster with proper sharding

set -e

echo "🔧 Initializing ACGS-1 Redis Cluster..."

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

# Wait for all Redis nodes to be ready
print_status "Waiting for Redis nodes to be ready..."
for node in "${ALL_NODES[@]}"; do
    host=$(echo $node | cut -d: -f1)
    port=$(echo $node | cut -d: -f2)
    
    print_status "Checking $host:$port..."
    
    # Wait up to 60 seconds for each node
    timeout=60
    while [ $timeout -gt 0 ]; do
        if redis-cli -h $host -p $port ping > /dev/null 2>&1; then
            print_success "$host:$port is ready"
            break
        fi
        
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "$host:$port is not responding after 60 seconds"
        exit 1
    fi
done

print_success "All Redis nodes are ready"

# Check if cluster is already initialized
print_status "Checking if cluster is already initialized..."
if redis-cli -h redis-master-1 -p 7001 cluster nodes 2>/dev/null | grep -q "master"; then
    print_warning "Redis cluster appears to be already initialized"
    
    # Show current cluster status
    print_status "Current cluster status:"
    redis-cli -h redis-master-1 -p 7001 cluster nodes
    
    print_status "Cluster info:"
    redis-cli -h redis-master-1 -p 7001 cluster info
    
    exit 0
fi

# Create the cluster
print_status "Creating Redis cluster with 3 masters and 3 replicas..."

# Build the cluster create command
CLUSTER_NODES=""
for node in "${ALL_NODES[@]}"; do
    host=$(echo $node | cut -d: -f1)
    port=$(echo $node | cut -d: -f2)
    CLUSTER_NODES="$CLUSTER_NODES $host:$port"
done

print_status "Cluster nodes: $CLUSTER_NODES"

# Create cluster with automatic slot assignment
print_status "Executing cluster create command..."
redis-cli --cluster create $CLUSTER_NODES \
    --cluster-replicas 1 \
    --cluster-yes

if [ $? -eq 0 ]; then
    print_success "Redis cluster created successfully!"
else
    print_error "Failed to create Redis cluster"
    exit 1
fi

# Wait a moment for cluster to stabilize
sleep 5

# Verify cluster status
print_status "Verifying cluster status..."

# Check cluster info
print_status "Cluster info:"
redis-cli -h redis-master-1 -p 7001 cluster info

# Check cluster nodes
print_status "Cluster nodes:"
redis-cli -h redis-master-1 -p 7001 cluster nodes

# Check cluster slots distribution
print_status "Cluster slots distribution:"
redis-cli -h redis-master-1 -p 7001 cluster slots

# Test cluster functionality
print_status "Testing cluster functionality..."

# Test setting and getting keys across different slots
test_keys=(
    "test:key1"
    "test:key2" 
    "test:key3"
    "acgs:auth:session:123"
    "acgs:cache:policy:456"
    "acgs:temp:data:789"
)

for key in "${test_keys[@]}"; do
    # Set key
    if redis-cli -c -h redis-master-1 -p 7001 set "$key" "test_value_$(date +%s)" > /dev/null; then
        # Get key
        value=$(redis-cli -c -h redis-master-1 -p 7001 get "$key")
        if [ -n "$value" ]; then
            print_success "Test key '$key' set and retrieved successfully"
        else
            print_error "Failed to retrieve test key '$key'"
        fi
        
        # Clean up test key
        redis-cli -c -h redis-master-1 -p 7001 del "$key" > /dev/null
    else
        print_error "Failed to set test key '$key'"
    fi
done

# Check cluster health
print_status "Checking cluster health..."

cluster_state=$(redis-cli -h redis-master-1 -p 7001 cluster info | grep cluster_state | cut -d: -f2 | tr -d '\r')
if [ "$cluster_state" = "ok" ]; then
    print_success "Cluster state: OK"
else
    print_error "Cluster state: $cluster_state"
fi

cluster_slots_assigned=$(redis-cli -h redis-master-1 -p 7001 cluster info | grep cluster_slots_assigned | cut -d: -f2 | tr -d '\r')
if [ "$cluster_slots_assigned" = "16384" ]; then
    print_success "All 16384 slots assigned"
else
    print_warning "Only $cluster_slots_assigned slots assigned (expected 16384)"
fi

# Performance test
print_status "Running basic performance test..."
redis-cli -c -h redis-master-1 -p 7001 --latency-history -i 1 > /tmp/redis_latency.log &
LATENCY_PID=$!

# Run a quick benchmark
print_status "Running benchmark (1000 operations)..."
redis-cli -c -h redis-master-1 -p 7001 eval "
for i=1,1000 do
    redis.call('set', 'bench:key:' .. i, 'value' .. i)
    redis.call('get', 'bench:key:' .. i)
end
return 'OK'
" 0

# Stop latency monitoring
kill $LATENCY_PID 2>/dev/null || true

# Clean up benchmark keys
print_status "Cleaning up benchmark keys..."
redis-cli -c -h redis-master-1 -p 7001 eval "
for i=1,1000 do
    redis.call('del', 'bench:key:' .. i)
end
return 'OK'
" 0

print_success "Redis cluster initialization completed successfully!"

print_status "Cluster Summary:"
echo "- Masters: ${MASTER_NODES[*]}"
echo "- Replicas: ${REPLICA_NODES[*]}"
echo "- Total Nodes: ${#ALL_NODES[@]}"
echo "- Slots: 16384 (distributed across 3 masters)"
echo "- Replication Factor: 1 (each master has 1 replica)"

print_status "Connection Examples:"
echo "- Connect to cluster: redis-cli -c -h redis-master-1 -p 7001"
echo "- Check cluster status: redis-cli -h redis-master-1 -p 7001 cluster info"
echo "- Monitor cluster: redis-cli -h redis-master-1 -p 7001 cluster nodes"

print_status "Next Steps:"
echo "1. Configure application connection strings to use cluster endpoints"
echo "2. Implement Redis client with cluster support in applications"
echo "3. Set up monitoring and alerting for cluster health"
echo "4. Configure backup and persistence strategies"
echo "5. Test failover scenarios and recovery procedures"
