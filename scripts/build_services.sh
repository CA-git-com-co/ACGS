#!/bin/bash
# Build ACGS-2 services locally

set -e

echo "🏗️ Building ACGS-2 Services"
echo "============================"

# Build each service
services=(
    "services/core/constitutional-ai"
    "services/core/groqcloud-policy-integration"
    "services/core/a2a-policy-integration"
    "services/core/security-validation"
    "services/mcp/aggregator"
    "services/mcp/filesystem"
    "services/mcp/github"
    "services/mcp/browser"
)

for service in "${services[@]}"; do
    if [ -d "$service" ]; then
        echo "🔨 Building $service..."
        docker build -f infrastructure/docker/Dockerfile.local -t "acgs-${service##*/}:latest" "$service"
        echo "✅ Built ${service##*/}"
    fi
done

echo "✅ All services built successfully"
