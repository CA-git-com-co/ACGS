#!/bin/bash
# Deployment script for ACGS-1 Lite Evolution Oversight Service
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🔄 Deploying ACGS-1 Lite Evolution Oversight Service"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "=================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

# Configuration
SERVICE_NAME="evolution-oversight-service"
IMAGE_NAME="acgs-evolution-oversight"
VERSION="latest"
SERVICE_PORT=8004
METRICS_PORT=9004

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if PostgreSQL is running (for database)
if ! nc -z localhost 5432 2>/dev/null; then
    echo "⚠️  PostgreSQL not detected on localhost:5432"
    echo "💡 Ensure PostgreSQL is running with ACGS database setup"
fi

# Check if Redis is running (for caching)
if ! nc -z localhost 6379 2>/dev/null; then
    echo "⚠️  Redis not detected on localhost:6379"
    echo "💡 Ensure Redis is running for caching"
fi

echo "✅ Prerequisites check completed"

# Build Docker image
echo "📦 Building evolution oversight service image..."

docker build -t ${IMAGE_NAME}:${VERSION} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker stop ${SERVICE_NAME} 2>/dev/null || true
docker rm ${SERVICE_NAME} 2>/dev/null || true

# Run the service
echo "🚀 Starting evolution oversight service..."

docker run -d \
    --name ${SERVICE_NAME} \
    --network host \
    -p ${SERVICE_PORT}:${SERVICE_PORT} \
    -p ${METRICS_PORT}:${METRICS_PORT} \
    -e DATABASE_URL=os.environ.get("DATABASE_URL") \
    -e REDIS_URL="redis://localhost:6379/3" \
    -e AUDIT_ENGINE_URL="http://localhost:8003" \
    -e POLICY_ENGINE_URL="http://localhost:8001" \
    --restart unless-stopped \
    ${IMAGE_NAME}:${VERSION}

if [ $? -ne 0 ]; then
    echo "❌ Container start failed"
    exit 1
fi

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."

for i in {1..30}; do
    if curl -s -f http://localhost:${SERVICE_PORT}/health > /dev/null 2>&1; then
        echo "✅ Service is ready!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Service failed to start within 30 seconds"
        echo "📋 Container logs:"
        docker logs ${SERVICE_NAME} --tail=50
        exit 1
    fi
    
    echo "   Attempt $i: Waiting for service..."
    sleep 1
done

# Test basic functionality
echo "🧪 Testing basic functionality..."

# Test health endpoint
HEALTH_RESPONSE=$(curl -s http://localhost:${SERVICE_PORT}/health)
if [ $? -eq 0 ]; then
    echo "✅ Health check passed"
    echo "   $(echo $HEALTH_RESPONSE | python3 -c 'import sys, json; data=json.load(sys.stdin); print(f"Status: {data[\"status\"]}, Hash: {data[\"constitutional_hash\"]}")')"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test metrics endpoint
METRICS_RESPONSE=$(curl -s http://localhost:${SERVICE_PORT}/metrics)
if [ $? -eq 0 ]; then
    echo "✅ Metrics endpoint accessible"
else
    echo "⚠️  Metrics endpoint not accessible"
fi

# Test evolution submission (basic)
echo "🔄 Testing evolution submission..."

TEST_EVOLUTION=$(cat <<'EOF'
{
    "agent_id": "test_deployment_agent",
    "new_version": {
        "version": "1.0.0",
        "changes": {
            "code_changes": ["Deployment test change"],
            "config_changes": {}
        },
        "complexity_delta": 0.01,
        "resource_delta": 0.005
    },
    "change_description": "Deployment test evolution",
    "requester_id": "deployment_test",
    "priority": "low"
}
EOF
)

SUBMIT_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$TEST_EVOLUTION" \
    http://localhost:${SERVICE_PORT}/api/v1/evolution/submit)

if [ $? -eq 0 ]; then
    EVOLUTION_ID=$(echo $SUBMIT_RESPONSE | python3 -c 'import sys, json; data=json.load(sys.stdin); print(data.get("evolution_id", ""))')
    if [ ! -z "$EVOLUTION_ID" ]; then
        echo "✅ Evolution submission test passed"
        echo "   Evolution ID: $EVOLUTION_ID"
        
        # Wait a moment and check status
        sleep 2
        STATUS_RESPONSE=$(curl -s http://localhost:${SERVICE_PORT}/api/v1/evolution/$EVOLUTION_ID)
        if [ $? -eq 0 ]; then
            echo "✅ Evolution status retrieval test passed"
        else
            echo "⚠️  Evolution status retrieval had issues"
        fi
    else
        echo "⚠️  Evolution submission response invalid"
    fi
else
    echo "⚠️  Evolution submission test failed"
fi

# Check container status
echo "📊 Container status:"
docker ps --filter name=${SERVICE_NAME} --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Display deployment information
echo ""
echo "🎉 Evolution Oversight Service deployed successfully!"
echo ""
echo "Deployment Information:"
echo "  🐳 Container: ${SERVICE_NAME}"
echo "  🏷️  Image: ${IMAGE_NAME}:${VERSION}"
echo "  🌐 Service Port: ${SERVICE_PORT}"
echo "  📊 Metrics Port: ${METRICS_PORT}"
echo ""
echo "Service Endpoints:"
echo "  🔗 Health: http://localhost:${SERVICE_PORT}/health"
echo "  📖 API Docs: http://localhost:${SERVICE_PORT}/docs"
echo "  📊 Metrics: http://localhost:${SERVICE_PORT}/metrics"
echo "  📈 Prometheus: http://localhost:${METRICS_PORT}/metrics"
echo ""
echo "API Examples:"
echo "  # Submit evolution:"
echo "  curl -X POST http://localhost:${SERVICE_PORT}/api/v1/evolution/submit \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"agent_id\":\"test\",\"new_version\":{\"version\":\"1.0.0\"},\"change_description\":\"Test\",\"requester_id\":\"user\"}'"
echo ""
echo "  # Get pending reviews:"
echo "  curl http://localhost:${SERVICE_PORT}/api/v1/reviews/pending"
echo ""
echo "  # Get agent history:"
echo "  curl http://localhost:${SERVICE_PORT}/api/v1/agents/test_agent/history"
echo ""
echo "Monitoring Commands:"
echo "  # View logs:"
echo "  docker logs ${SERVICE_NAME} -f"
echo ""
echo "  # Check container status:"
echo "  docker ps --filter name=${SERVICE_NAME}"
echo ""
echo "  # Stop service:"
echo "  docker stop ${SERVICE_NAME}"
echo ""
echo "Constitutional Hash: cdd01ef066bc6cf2"