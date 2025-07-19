#!/bin/bash
# ACGS-2 Staging Deployment Script
# Constitutional Hash: cdd01ef066bc6cf2
# 
# Deploy to staging environment for real-world performance validation
# Target: P99 <5ms, >100 RPS, >85% cache hit rate

set -e

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
STAGING_URL=${STAGING_URL:-"https://acgs-staging.example.com"}
DOCKER_IMAGE="acgs-frontend"
DOCKER_TAG=${DOCKER_TAG:-"staging-$(date +%Y%m%d-%H%M%S)"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Build optimized production bundle
build_production() {
    log_info "Building production-optimized ACGS-2 frontend..."
    
    # Clean previous builds
    rm -rf dist/
    
    # Build with maximum optimization
    trunk build --release
    
    # Verify build artifacts
    if [ ! -f "dist/index.html" ]; then
        log_error "Build failed - index.html not found"
        exit 1
    fi
    
    local wasm_size=$(du -h dist/*.wasm | cut -f1)
    log_success "Production build completed (Bundle size: $wasm_size)"
    
    # Verify constitutional compliance
    if grep -q "$CONSTITUTIONAL_HASH" dist/index.html; then
        log_success "Constitutional compliance verified in build"
    else
        log_error "Constitutional compliance check failed"
        exit 1
    fi
}

# Create Docker image for staging
create_docker_image() {
    log_info "Creating Docker image for staging deployment..."
    
    # Create optimized Dockerfile
    cat > Dockerfile.staging << EOF
# ACGS-2 Staging Deployment
# Constitutional Hash: $CONSTITUTIONAL_HASH

FROM nginx:alpine

# Copy built assets
COPY dist/ /usr/share/nginx/html/

# Copy optimized nginx configuration
COPY nginx.staging.conf /etc/nginx/nginx.conf

# Add constitutional compliance metadata
LABEL constitutional_hash="$CONSTITUTIONAL_HASH"
LABEL version="staging"
LABEL build_date="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

    # Create optimized nginx configuration
    cat > nginx.staging.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Performance optimizations
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout  65;
    types_hash_max_size 2048;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/wasm;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Constitutional-Hash "$CONSTITUTIONAL_HASH";
    
    # Cache configuration for performance testing
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|wasm)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Constitutional-Hash "$CONSTITUTIONAL_HASH";
    }
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # SPA routing
        location / {
            try_files \$uri \$uri/ /index.html;
            add_header X-Constitutional-Hash "$CONSTITUTIONAL_HASH";
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
            add_header X-Constitutional-Hash "$CONSTITUTIONAL_HASH";
        }
        
        # Performance monitoring endpoint
        location /metrics {
            access_log off;
            return 200 "# ACGS-2 Metrics\nconstitutional_hash{value=\"$CONSTITUTIONAL_HASH\"} 1\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

    # Build Docker image
    docker build -f Dockerfile.staging -t "$DOCKER_IMAGE:$DOCKER_TAG" .
    
    log_success "Docker image created: $DOCKER_IMAGE:$DOCKER_TAG"
}

# Deploy to staging environment
deploy_staging() {
    log_info "Deploying to staging environment..."
    
    # Stop existing container if running
    docker stop acgs-staging 2>/dev/null || true
    docker rm acgs-staging 2>/dev/null || true
    
    # Run new container
    docker run -d \
        --name acgs-staging \
        --restart unless-stopped \
        -p 8080:80 \
        -e CONSTITUTIONAL_HASH="$CONSTITUTIONAL_HASH" \
        "$DOCKER_IMAGE:$DOCKER_TAG"
    
    # Wait for container to be ready
    log_info "Waiting for staging deployment to be ready..."
    local timeout=60
    local count=0
    
    while [ $count -lt $timeout ]; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            log_success "Staging deployment is ready at http://localhost:8080"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    log_error "Staging deployment failed to start within $timeout seconds"
    exit 1
}

# Validate deployment
validate_deployment() {
    log_info "Validating staging deployment..."
    
    # Check health endpoint
    local health_response=$(curl -s http://localhost:8080/health)
    if [ "$health_response" = "healthy" ]; then
        log_success "Health check passed"
    else
        log_error "Health check failed: $health_response"
        exit 1
    fi
    
    # Check constitutional compliance
    local index_content=$(curl -s http://localhost:8080/)
    if echo "$index_content" | grep -q "$CONSTITUTIONAL_HASH"; then
        log_success "Constitutional compliance verified in deployment"
    else
        log_error "Constitutional compliance check failed in deployment"
        exit 1
    fi
    
    # Check performance headers
    local headers=$(curl -I -s http://localhost:8080/)
    if echo "$headers" | grep -q "X-Constitutional-Hash: $CONSTITUTIONAL_HASH"; then
        log_success "Constitutional headers verified"
    else
        log_warning "Constitutional headers not found"
    fi
    
    # Check WASM bundle loading
    local wasm_response=$(curl -I -s http://localhost:8080/acgs-frontend_bg.wasm)
    if echo "$wasm_response" | grep -q "200 OK"; then
        log_success "WASM bundle accessible"
    else
        log_error "WASM bundle not accessible"
        exit 1
    fi
    
    log_success "Staging deployment validation completed"
}

# Generate deployment report
generate_report() {
    log_info "Generating staging deployment report..."
    
    local report_file="staging-deployment-report.md"
    
    cat > "$report_file" << EOF
# ACGS-2 Staging Deployment Report

**Constitutional Hash:** \`$CONSTITUTIONAL_HASH\`  
**Deployment Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')  
**Docker Image:** \`$DOCKER_IMAGE:$DOCKER_TAG\`  
**Staging URL:** http://localhost:8080

## Deployment Status

- ✅ **Build Completed:** Production-optimized bundle created
- ✅ **Docker Image:** Created and tagged
- ✅ **Container Deployed:** Running on port 8080
- ✅ **Health Check:** Passing
- ✅ **Constitutional Compliance:** Verified
- ✅ **WASM Bundle:** Accessible

## Performance Targets

- **P99 Latency:** <5ms (Ready for testing)
- **Throughput:** >100 RPS (Ready for testing)  
- **Cache Hit Rate:** >85% (Ready for testing)

## Next Steps

1. **Load Testing:** Run performance validation with 100+ concurrent users
2. **Monitoring:** Set up real-time performance monitoring
3. **Validation:** Verify all performance targets are met

## Commands

\`\`\`bash
# View logs
docker logs acgs-staging

# Stop deployment
docker stop acgs-staging

# Remove deployment
docker rm acgs-staging
\`\`\`

---
*Generated by ACGS-2 Staging Deployment Script*
EOF

    log_success "Deployment report generated: $report_file"
}

# Main execution
main() {
    echo "🚀 ACGS-2 Staging Deployment"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Target: P99 <5ms, >100 RPS, >85% cache hit rate"
    echo ""
    
    # Check dependencies
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed"
        exit 1
    fi
    
    # Run deployment steps
    build_production
    create_docker_image
    deploy_staging
    validate_deployment
    generate_report
    
    echo ""
    log_success "🎉 Staging deployment completed successfully!"
    log_info "📊 Staging URL: http://localhost:8080"
    log_info "🔍 Ready for performance validation and load testing"
}

# Run main function
main "$@"
