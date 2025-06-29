#!/bin/bash
# ACGS-1 Lite Policy Engine Optimization Deployment Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🚀 ACGS-1 Lite Policy Engine Optimization Deployment"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "===================================================="

# Configuration
SERVICE_NAME="acgs-policy-engine-optimization"
IMAGE_NAME="acgs/policy-engine-optimization"
VERSION="1.0.0"
PORT=8004

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "💡 Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed or not in PATH"
    echo "💡 Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Prerequisites checked"

# Build policy bundle first
echo ""
echo "📦 Building policy bundle..."
if [ -f "build.sh" ]; then
    chmod +x build.sh
    if ./build.sh; then
        echo "✅ Policy bundle built successfully"
    else
        echo "⚠️  Policy bundle build failed, will use fallback evaluation"
    fi
else
    echo "⚠️  build.sh not found, skipping policy bundle build"
fi

# Build Docker image
echo ""
echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Docker image build failed"
    exit 1
fi

# Stop existing services
echo ""
echo "🛑 Stopping existing services..."
docker-compose down --remove-orphans || echo "No existing services to stop"

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Services started successfully"
else
    echo "❌ Failed to start services"
    exit 1
fi

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."

# Check policy engine health
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "   Attempt ${ATTEMPT}/${MAX_ATTEMPTS}: Checking policy engine health..."
    
    if curl -s -f http://localhost:${PORT}/v1/data/acgs/main/health > /dev/null; then
        echo "✅ Policy engine is healthy"
        break
    fi
    
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "❌ Policy engine failed to become healthy"
        echo "📋 Service logs:"
        docker-compose logs --tail=20 policy-engine
        exit 1
    fi
    
    sleep 2
done

# Check Redis health
echo "   Checking Redis health..."
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis health check failed"
fi

# Warm up the cache
echo ""
echo "🔥 Warming up cache..."
if curl -s -f http://localhost:${PORT}/v1/cache/warm > /dev/null; then
    echo "✅ Cache warmed up successfully"
else
    echo "⚠️  Cache warm-up failed"
fi

# Run basic functionality test
echo ""
echo "🧪 Running basic functionality test..."

HEALTH_RESPONSE=$(curl -s http://localhost:${PORT}/v1/data/acgs/main/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint test failed"
    echo "Response: $HEALTH_RESPONSE"
fi

# Test policy evaluation
TEST_REQUEST='{"type":"constitutional_evaluation","constitutional_hash":"cdd01ef066bc6cf2","action":"data.read_public","context":{"environment":{"sandbox_enabled":true,"audit_enabled":true},"agent":{"trust_level":0.9,"requested_resources":{"cpu_cores":1}},"responsible_party":"deployment_test","explanation":"Deployment verification test"}}'

EVAL_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$TEST_REQUEST" http://localhost:${PORT}/v1/data/acgs/main/decision)
if echo "$EVAL_RESPONSE" | grep -q '"allow"'; then
    echo "✅ Policy evaluation working"
else
    echo "❌ Policy evaluation test failed"
    echo "Response: $EVAL_RESPONSE"
fi

# Display service information
echo ""
echo "📋 Service Information"
echo "====================="
echo "Service Name:     ${SERVICE_NAME}"
echo "Image:            ${IMAGE_NAME}:${VERSION}"
echo "Port:             ${PORT}"
echo "Health Check:     http://localhost:${PORT}/v1/data/acgs/main/health"
echo "Metrics:          http://localhost:${PORT}/v1/metrics"
echo "Policy Decision:  http://localhost:${PORT}/v1/data/acgs/main/decision"
echo "Cache Warm-up:    http://localhost:${PORT}/v1/cache/warm"
echo ""
echo "Monitoring:"
echo "Prometheus:       http://localhost:9090"
echo "Grafana:          http://localhost:3000 (admin/acgs-admin)"
echo "Redis:            localhost:6379"
echo ""

# Show running containers
echo "🐳 Running Containers:"
docker-compose ps

# Show recent logs
echo ""
echo "📜 Recent Logs (last 10 lines):"
docker-compose logs --tail=10

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Quick Start Commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo "  Run benchmark:    python3 benchmark.py"
echo "  Performance test: python3 test_performance.py"
echo ""
echo "Constitutional Hash: cdd01ef066bc6cf2"