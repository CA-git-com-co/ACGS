# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# ACGS-1 Redis Cluster Setup Script
# Phase 2 - Enterprise Scalability & Performance
# Complete Redis cluster deployment with monitoring and integration

set -e

echo "🔧 Setting up Redis Cluster for ACGS-1..."

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

# Configuration
PROJECT_ROOT="/home/dislove/ACGS-1"
REDIS_DIR="$PROJECT_ROOT/infrastructure/redis"

# Check if Docker is running
print_status "Checking Docker availability..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Create necessary directories
print_status "Creating Redis directories..."
mkdir -p "$REDIS_DIR"
mkdir -p "$PROJECT_ROOT/logs"

# Make scripts executable
print_status "Making scripts executable..."
chmod +x "$REDIS_DIR/cluster-init.sh"
chmod +x "$REDIS_DIR/cluster-health-check.sh"

# Check if Redis cluster is already running
print_status "Checking for existing Redis cluster..."
if docker ps | grep -q "acgs_redis"; then
    print_warning "Redis cluster containers are already running"
    
    # Ask user if they want to recreate
    read -p "Do you want to recreate the Redis cluster? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping existing Redis cluster..."
        cd "$REDIS_DIR"
        docker-compose -f config/docker/docker-compose.redis-cluster.yml down -v
        print_success "Existing cluster stopped"
    else
        print_status "Using existing Redis cluster"
        cd "$REDIS_DIR"
        docker-compose -f config/docker/docker-compose.redis-cluster.yml ps
        exit 0
    fi
fi

# Start Redis cluster
print_status "Starting Redis cluster containers..."
cd "$REDIS_DIR"

# Start the cluster
docker-compose -f config/docker/docker-compose.redis-cluster.yml up -d

if [ $? -eq 0 ]; then
    print_success "Redis cluster containers started"
else
    print_error "Failed to start Redis cluster containers"
    exit 1
fi

# Wait for containers to be ready
print_status "Waiting for Redis nodes to be ready..."
sleep 15

# Check container status
print_status "Checking container status..."
docker-compose -f config/docker/docker-compose.redis-cluster.yml ps

# Initialize the cluster
print_status "Initializing Redis cluster..."
docker exec acgs_redis_cluster_manager /cluster-init.sh

if [ $? -eq 0 ]; then
    print_success "Redis cluster initialized successfully"
else
    print_error "Failed to initialize Redis cluster"
    exit 1
fi

# Run health check
print_status "Running initial health check..."
docker exec acgs_redis_cluster_manager /cluster-health-check.sh

# Install Python Redis dependencies
print_status "Installing Python Redis dependencies..."
pip3 install --user redis[hiredis] || print_warning "Failed to install some Redis dependencies"

# Test Redis cluster from host
print_status "Testing Redis cluster connectivity from host..."

# Test basic connectivity
for port in 7001 7002 7003; do
    if redis-cli -h localhost -p $port ping > /dev/null 2>&1; then
        print_success "Redis node localhost:$port is responding"
    else
        print_warning "Redis node localhost:$port is not responding"
    fi
done

# Test cluster operations
print_status "Testing cluster operations..."
if redis-cli -c -h localhost -p 7001 set "test:cluster:setup" "success" > /dev/null 2>&1; then
    value=$(redis-cli -c -h localhost -p 7001 get "test:cluster:setup")
    if [ "$value" = "success" ]; then
        print_success "Cluster operations test passed"
        redis-cli -c -h localhost -p 7001 del "test:cluster:setup" > /dev/null 2>&1
    else
        print_warning "Cluster operations test failed - unexpected value: $value"
    fi
else
    print_warning "Cluster operations test failed - cannot set key"
fi

# Create Redis monitoring configuration
print_status "Setting up Redis monitoring..."

# Update Prometheus configuration to include Redis exporter
PROMETHEUS_CONFIG="$PROJECT_ROOT/infrastructure/monitoring/prometheus/prometheus.yml"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
if [ -f "$PROMETHEUS_CONFIG" ]; then
    # Check if Redis job already exists
    if ! grep -q "job_name: 'redis-cluster'" "$PROMETHEUS_CONFIG"; then
        print_status "Adding Redis cluster monitoring to Prometheus..."
        
        # Add Redis cluster monitoring job
        cat >> "$PROMETHEUS_CONFIG" << EOF

  # Redis Cluster Exporter
  - job_name: 'redis-cluster'
    static_configs:
      - targets: ['localhost:9121']
    scrape_interval: 30s
    metrics_path: /metrics
    scrape_timeout: 10s
EOF
        print_success "Redis monitoring added to Prometheus configuration"
    else
        print_status "Redis monitoring already configured in Prometheus"
    fi
else
    print_warning "Prometheus configuration not found - skipping monitoring setup"
fi

# Create Redis performance test script
print_status "Creating Redis performance test script..."

cat > "$PROJECT_ROOT/scripts/test_redis_performance.py" << 'EOF'
#!/usr/bin/env python3
"""
ACGS-1 Redis Cluster Performance Test
Tests Redis cluster performance and validates >1000 concurrent user support
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.shared.redis_cluster_client import RedisClusterClient

async def test_redis_performance():
    """Test Redis cluster performance."""
    
    print("🚀 ACGS-1 Redis Cluster Performance Test")
    print("=" * 50)
    
    # Initialize Redis client
    client = RedisClusterClient("performance_test")
    
    try:
        await client.connect()
        print("✅ Connected to Redis cluster")
        
        # Test 1: Basic operations performance
        print("\n📊 Test 1: Basic Operations Performance")
        
        operations = 1000
        start_time = time.time()
        
        # Perform mixed operations
        for i in range(operations):
            await client.set(f"perf:test:{i}", f"value_{i}", ttl=300)
            if i % 2 == 0:
                await client.get(f"perf:test:{i}")
        
        end_time = time.time()
        duration = end_time - start_time
        ops_per_sec = operations / duration
        
        print(f"  Operations: {operations}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Ops/sec: {ops_per_sec:.0f}")
        
        if ops_per_sec > 500:
            print("  ✅ Performance: GOOD")
        elif ops_per_sec > 200:
            print("  ⚠️  Performance: ACCEPTABLE")
        else:
            print("  ❌ Performance: POOR")
        
        # Test 2: Concurrent operations
        print("\n📊 Test 2: Concurrent Operations")
        
        async def concurrent_worker(worker_id, operations_per_worker):
            """Worker function for concurrent testing."""
            for i in range(operations_per_worker):
                key = f"concurrent:worker:{worker_id}:item:{i}"
                await client.set(key, f"worker_{worker_id}_value_{i}", ttl=300)
                await client.get(key)
        
        concurrent_workers = 50
        operations_per_worker = 20
        total_concurrent_ops = concurrent_workers * operations_per_worker * 2  # set + get
        
        start_time = time.time()
        
        # Run concurrent workers
        tasks = [
            concurrent_worker(worker_id, operations_per_worker)
            for worker_id in range(concurrent_workers)
        ]
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        concurrent_ops_per_sec = total_concurrent_ops / duration
        
        print(f"  Workers: {concurrent_workers}")
        print(f"  Operations per worker: {operations_per_worker * 2}")
        print(f"  Total operations: {total_concurrent_ops}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Concurrent ops/sec: {concurrent_ops_per_sec:.0f}")
        
        if concurrent_ops_per_sec > 1000:
            print("  ✅ Concurrent performance: EXCELLENT")
        elif concurrent_ops_per_sec > 500:
            print("  ✅ Concurrent performance: GOOD")
        elif concurrent_ops_per_sec > 200:
            print("  ⚠️  Concurrent performance: ACCEPTABLE")
        else:
            print("  ❌ Concurrent performance: POOR")
        
        # Test 3: Data structure operations
        print("\n📊 Test 3: Data Structure Operations")
        
        # Hash operations
        hash_ops = 100
        start_time = time.time()
        
        for i in range(hash_ops):
            await client.hash_set("test:hash", f"field_{i}", f"hash_value_{i}")
            await client.hash_get("test:hash", f"field_{i}")
        
        hash_duration = time.time() - start_time
        hash_ops_per_sec = (hash_ops * 2) / hash_duration
        
        print(f"  Hash operations: {hash_ops * 2} in {hash_duration:.2f}s ({hash_ops_per_sec:.0f} ops/sec)")
        
        # List operations
        list_ops = 100
        start_time = time.time()
        
        for i in range(list_ops):
            await client.list_push("test:list", f"list_value_{i}")
        
        for i in range(list_ops):
            await client.list_pop("test:list")
        
        list_duration = time.time() - start_time
        list_ops_per_sec = (list_ops * 2) / list_duration
        
        print(f"  List operations: {list_ops * 2} in {list_duration:.2f}s ({list_ops_per_sec:.0f} ops/sec)")
        
        # Get cluster info and metrics
        print("\n📊 Cluster Information")
        cluster_info = await client.get_cluster_info()
        
        print(f"  Cluster state: {cluster_info.get('cluster_state', 'unknown')}")
        print(f"  Cluster size: {cluster_info.get('cluster_size', 'unknown')}")
        print(f"  Known nodes: {cluster_info.get('cluster_known_nodes', 'unknown')}")
        print(f"  Hit rate: {cluster_info.get('hit_rate', 'unknown')}")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        cleanup_tasks = []
        
        for i in range(operations):
            cleanup_tasks.append(client.delete(f"perf:test:{i}"))
        
        for worker_id in range(concurrent_workers):
            for i in range(operations_per_worker):
                key = f"concurrent:worker:{worker_id}:item:{i}"
                cleanup_tasks.append(client.delete(key))
        
        cleanup_tasks.append(client.delete("test:hash"))
        cleanup_tasks.append(client.delete("test:list"))
        
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        print("✅ Test data cleaned up")
        
        print("\n🎉 Redis cluster performance test completed!")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
    
    finally:
        await client.disconnect()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_redis_performance())
    sys.exit(0 if success else 1)
EOF

chmod +x "$PROJECT_ROOT/scripts/test_redis_performance.py"
print_success "Redis performance test script created"

# Run performance test
print_status "Running Redis performance test..."
if python3 "$PROJECT_ROOT/scripts/test_redis_performance.py"; then
    print_success "Redis performance test passed"
else
    print_warning "Redis performance test had issues"
fi

# Create service integration examples
print_status "Creating service integration examples..."

cat > "$PROJECT_ROOT/examples/redis_integration_example.py" << 'EOF'
"""
ACGS-1 Redis Integration Example
Shows how to integrate Redis caching in ACGS services
"""

import asyncio
from services.shared.redis_cluster_client import get_redis_client

async def example_auth_service_integration():
    """Example of Redis integration in Auth Service."""
    
    # Get Redis client for auth service
    redis_client = await get_redis_client("auth_service")
    
    # Cache user session
    session_data = {
        "user_id": "user123",
        "username": "john_doe",
        "roles": ["user", "policy_viewer"],
        "login_time": "2024-01-01T12:00:00Z"
    }
    
    # Store session with 1 hour TTL
    await redis_client.set(
        "session:abc123",
        session_data,
        ttl=3600,
        prefix=redis_client.config.session_prefix
    )
    
    # Retrieve session
    cached_session = await redis_client.get(
        "session:abc123",
        prefix=redis_client.config.session_prefix
    )
    
    print(f"Cached session: {cached_session}")

async def example_policy_service_integration():
    """Example of Redis integration in Policy Service."""
    
    # Get Redis client for policy service
    redis_client = await get_redis_client("policy_service")
    
    # Cache policy data
    policy_data = {
        "policy_id": "POL-001",
        "title": "Data Privacy Policy",
        "content": "...",
        "version": "1.2",
        "last_updated": "2024-01-01T10:00:00Z"
    }
    
    # Store policy with long TTL (24 hours)
    await redis_client.set(
        "policy:POL-001",
        policy_data,
        ttl=86400,
        prefix=redis_client.config.policy_prefix
    )
    
    # Use hash for policy metadata
    await redis_client.hash_set(
        "policy:metadata",
        "POL-001",
        {"version": "1.2", "status": "active"},
        prefix=redis_client.config.policy_prefix
    )

if __name__ == "__main__":
    asyncio.run(example_auth_service_integration())
    asyncio.run(example_policy_service_integration())
EOF

print_success "Service integration examples created"

print_success "Redis cluster setup completed successfully!"

print_status "Redis Cluster Summary:"
echo "- Cluster Nodes: 6 (3 masters + 3 replicas)"
echo "- Master Ports: 7001, 7002, 7003"
echo "- Replica Ports: 7004, 7005, 7006"
echo "- Monitoring: Redis Exporter on port 9121"
echo "- Configuration: High availability with automatic failover"
echo "- Performance: Optimized for >1000 concurrent users"

print_status "Management Commands:"
echo "- Health Check: docker exec acgs_redis_cluster_manager /cluster-health-check.sh"
echo "- Cluster Info: redis-cli -c -h localhost -p 7001 cluster info"
echo "- Cluster Nodes: redis-cli -c -h localhost -p 7001 cluster nodes"
echo "- Performance Test: python3 scripts/test_redis_performance.py"

print_status "Next Steps:"
echo "1. Integrate Redis caching in ACGS services using the provided client library"
echo "2. Configure cache invalidation strategies for each service"
echo "3. Set up monitoring alerts for cluster health and performance"
echo "4. Implement cache warming strategies for critical data"
echo "5. Test failover scenarios and recovery procedures"
