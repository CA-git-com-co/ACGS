#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION=${GITHUB_SHA:-$TIMESTAMP}

echo "🏗️ Building and pushing Docker images for $ENVIRONMENT..."

# Build services
services=("auth-service" "constitutional-ai" "policy-governance" "governance-synthesis")

for service in "${services[@]}"; do
    echo "Building $service..."
    docker build -t $CONTAINER_REGISTRY/acgs-$service:$VERSION -f services/core/$service/Dockerfile .
    docker build -t $CONTAINER_REGISTRY/acgs-$service:$ENVIRONMENT-latest -f services/core/$service/Dockerfile .

    echo "Pushing $service..."
    docker push $CONTAINER_REGISTRY/acgs-$service:$VERSION
    docker push $CONTAINER_REGISTRY/acgs-$service:$ENVIRONMENT-latest
done

echo "✅ All images built and pushed successfully"
