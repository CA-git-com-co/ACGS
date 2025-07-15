#!/bin/bash
# Production Deployment Script for 5-Tier Hybrid Inference Router
# Constitutional Hash: cdd01ef066bc6cf2

set -e

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
ENVIRONMENT="production"

echo "🚀 Starting Production Deployment"
echo "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."

# Check required files
required_files=("config/environments/developmentconfig/environments/productionconfig/environments/developmentconfig/environments/development.env.backup" "config/docker/config/docker/config/docker/docker-compose.production.yml" "nginx.production.conf")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Required file not found: $file"
        exit 1
    fi
done

# Check environment variables
if [[ -z "$OPENROUTER_API_KEY" ]] || [[ -z "$GROQ_API_KEY" ]]; then
    echo "❌ Required API keys not set"
    exit 1
fi

# Backup current deployment
echo "💾 Creating backup..."
./scripts/deployment/backup_production.sh

# Deploy new version
echo "🚀 Deploying production services..."
docker-compose -f config/docker/config/docker/config/docker/docker-compose.production.yml --env-file config/environments/developmentconfig/environments/productionconfig/environments/developmentconfig/environments/development.env.backup up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health checks
echo "🔍 Running health checks..."
for i in {1..10}; do
    if curl -f -s https://localhost/health > /dev/null; then
        echo "✅ Health check passed"
        break
    fi
    if [[ $i -eq 10 ]]; then
        echo "❌ Health check failed after 10 attempts"
        echo "🔄 Rolling back..."
        ./scripts/deployment/rollback_production.sh
        exit 1
    fi
    sleep 10
done

# Validate constitutional compliance
echo "🔒 Validating constitutional compliance..."
response=$(curl -s https://localhost/api/health)
if echo "$response" | grep -q "$CONSTITUTIONAL_HASH"; then
    echo "✅ Constitutional compliance validated"
else
    echo "❌ Constitutional compliance validation failed"
    exit 1
fi

echo "🎉 Production deployment completed successfully!"
echo "🔗 Service URL: https://localhost"
echo "📊 Monitoring: http://localhost:3000"
