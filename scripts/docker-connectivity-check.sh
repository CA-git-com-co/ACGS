#!/bin/bash

# Docker-based GitHub connectivity check
# Useful for containerized CI/CD environments

set -e

# Configuration
DOCKER_IMAGE="curlimages/curl:latest"
TIMEOUT=30
MAX_RETRIES=3

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Test connectivity using Docker container
test_with_docker() {
    local url="$1"
    local description="$2"
    
    log "🐳 Testing $description using Docker..."
    
    if docker run --rm --network host \
        "$DOCKER_IMAGE" \
        curl -s --max-time "$TIMEOUT" --head "$url" >/dev/null 2>&1; then
        log "✅ Docker-based test for $description successful"
        return 0
    else
        log "❌ Docker-based test for $description failed"
        return 1
    fi
}

# Main function
main() {
    log "🚀 Starting Docker-based connectivity check..."
    
    # Pull the curl image first
    log "📦 Pulling curl Docker image..."
    if ! docker pull "$DOCKER_IMAGE" >/dev/null 2>&1; then
        log "❌ Failed to pull Docker image"
        exit 1
    fi
    
    # Test GitHub connectivity
    local tests_passed=0
    local total_tests=2
    
    if test_with_docker "https://github.com" "GitHub main site"; then
        ((tests_passed++))
    fi
    
    if test_with_docker "https://api.github.com" "GitHub API"; then
        ((tests_passed++))
    fi
    
    if [[ $tests_passed -ge 1 ]]; then
        log "🎉 Docker-based connectivity check passed!"
        exit 0
    else
        log "💥 Docker-based connectivity check failed!"
        exit 1
    fi
}

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    log "❌ Docker not available, skipping Docker-based tests"
    exit 1
fi

main "$@"
