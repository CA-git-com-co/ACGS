#!/bin/bash
# ACGS-1 Lite Audit Engine Deployment Script

set -e

echo "🚀 Deploying ACGS-1 Lite Audit Engine Service"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "================================================"

# Configuration
SERVICE_NAME="audit-engine"
PORT=8003
HEALTH_ENDPOINT="http://localhost:${PORT}/health"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if required environment variables are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️  Warning: AWS credentials not set. S3 archival will not work."
    echo "   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
fi

# Build the service
echo "📦 Building Audit Engine Docker image..."
docker build -t acgs-audit-engine:latest .

# Create network if it doesn't exist
docker network create acgs-network 2>/dev/null || true

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Create necessary volumes
echo "💾 Creating persistent volumes..."
docker volume create postgres_data 2>/dev/null || true
docker volume create redis_data 2>/dev/null || true
docker volume create redpanda_data 2>/dev/null || true

# Start services
echo "🔄 Starting Audit Engine and dependencies..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."

# Wait for PostgreSQL
echo "   Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
        echo "   ✅ PostgreSQL is ready"
        break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
        echo "   ❌ PostgreSQL failed to start within 60 seconds"
        exit 1
    fi
done

# Wait for Redis
echo "   Waiting for Redis..."
for i in {1..15}; do
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        echo "   ✅ Redis is ready"
        break
    fi
    sleep 2
    if [ $i -eq 15 ]; then
        echo "   ❌ Redis failed to start within 30 seconds"
        exit 1
    fi
done

# Wait for Redpanda
echo "   Waiting for Redpanda..."
for i in {1..30}; do
    if docker-compose exec -T redpanda rpk cluster health >/dev/null 2>&1; then
        echo "   ✅ Redpanda is ready"
        break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
        echo "   ⚠️  Redpanda may not be fully ready, continuing..."
        break
    fi
done

# Wait for Audit Engine
echo "   Waiting for Audit Engine..."
for i in {1..60}; do
    if curl -f -s "$HEALTH_ENDPOINT" >/dev/null 2>&1; then
        echo "   ✅ Audit Engine is ready"
        break
    fi
    sleep 2
    if [ $i -eq 60 ]; then
        echo "   ❌ Audit Engine failed to start within 120 seconds"
        echo "   Check logs: docker-compose logs audit-engine"
        exit 1
    fi
done

# Verify deployment
echo "🔍 Verifying deployment..."

# Test health endpoint
HEALTH_RESPONSE=$(curl -s "$HEALTH_ENDPOINT")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi

# Test constitutional hash verification
if echo "$HEALTH_RESPONSE" | grep -q "cdd01ef066bc6cf2"; then
    echo "   ✅ Constitutional hash verified"
else
    echo "   ❌ Constitutional hash verification failed"
    exit 1
fi

# Test chain integrity endpoint
INTEGRITY_RESPONSE=$(curl -s "http://localhost:${PORT}/api/v1/audit/verify")
if echo "$INTEGRITY_RESPONSE" | grep -q "constitutional_hash_verified.*true"; then
    echo "   ✅ Chain integrity verification working"
else
    echo "   ⚠️  Chain integrity verification may have issues"
    echo "   Response: $INTEGRITY_RESPONSE"
fi

# Show service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Audit Engine deployment completed successfully!"
echo ""
echo "Service Information:"
echo "  📍 Audit Engine API: http://localhost:${PORT}"
echo "  📖 API Documentation: http://localhost:${PORT}/docs"
echo "  📊 Metrics: http://localhost:${PORT}/metrics"
echo "  🏥 Health Check: $HEALTH_ENDPOINT"
echo ""
echo "Database Connections:"
echo "  🐘 PostgreSQL: localhost:5432 (audit_db)"
echo "  🔴 Redis: localhost:6379"
echo "  🟠 Redpanda: localhost:9092"
echo ""
echo "Quick Test Commands:"
echo "  # Ingest test event:"
echo "  curl -X POST http://localhost:${PORT}/api/v1/audit/events \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"event_type\":\"test\",\"service_name\":\"test\",\"action\":\"test\",\"outcome\":\"success\"}'"
echo ""
echo "  # Query events:"
echo "  curl http://localhost:${PORT}/api/v1/audit/events?limit=10"
echo ""
echo "  # Verify chain integrity:"
echo "  curl http://localhost:${PORT}/api/v1/audit/verify"
echo ""
echo "Logs:"
echo "  docker-compose logs audit-engine"
echo "  docker-compose logs postgres"
echo "  docker-compose logs redis"
echo "  docker-compose logs redpanda"