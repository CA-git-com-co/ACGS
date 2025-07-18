# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# ACGS-1 Optimized Service Startup Script
# Ensures proper dependency order and health checks

set -e

echo "🚀 Starting ACGS-1 optimized deployment..."

# Start infrastructure services first
echo "Starting infrastructure services..."
docker-compose -f config/docker/docker-compose.acgs.yml up -d postgres redis

# Wait for infrastructure to be ready
echo "Waiting for infrastructure services..."
sleep 30

# Verify infrastructure health
docker exec acgs_postgres pg_isready -U acgs_user || exit 1
docker exec acgs_redis redis-cli ping || exit 1

# Start core services in dependency order
echo "Starting core services..."
docker-compose -f config/docker/docker-compose.acgs.yml up -d auth_service
sleep 15

docker-compose -f config/docker/docker-compose.acgs.yml up -d ac_service integrity_service fv_service
sleep 20

docker-compose -f config/docker/docker-compose.acgs.yml up -d gs_service pgc_service
sleep 15

docker-compose -f config/docker/docker-compose.acgs.yml up -d ec_service
sleep 10

# Start load balancer
echo "Starting load balancer..."
docker-compose -f config/docker/docker-compose.acgs.yml up -d haproxy

# Start monitoring (optional)
echo "Starting monitoring stack..."
docker-compose -f docker-compose-monitoring.yml up -d || echo "Monitoring stack optional"

echo "✅ ACGS-1 deployment completed successfully"
