# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# ACGS-1 Docker Image Management Script
# Provides comprehensive Docker image build, push, and management capabilities

set -euo pipefail

# Configuration
REGISTRY="${REGISTRY:-ghcr.io}"
REPOSITORY="${REPOSITORY:-ca-git-com-co/acgs}"
BUILD_TARGET="${BUILD_TARGET:-production-runtime}"
PUSH_IMAGES="${PUSH_IMAGES:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Services configuration
SERVICES=("auth" "ac" "integrity" "fv" "gs" "pgc" "ec")
DOCKERFILES=(
    "infrastructure/docker/Dockerfile.acgs"
    "infrastructure/docker/Dockerfile.acgs"
    "infrastructure/docker/Dockerfile.acgs"
    "infrastructure/docker/Dockerfile.acgs"
    "infrastructure/docker/Dockerfile.acgs"
    "infrastructure/docker/Dockerfile.acgs"
    "infrastructure/docker/Dockerfile.acgs"
)

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
ACGS-1 Docker Image Management Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    build       Build Docker images
    push        Push Docker images to registry
    pull        Pull Docker images from registry
    clean       Clean up local Docker images
    scan        Scan images for vulnerabilities
    test        Test image functionality
    deploy      Deploy images using docker-compose
    help        Show this help message

Options:
    --service SERVICE       Build specific service (auth, ac, integrity, fv, gs, pgc, ec)
    --target TARGET         Build target (production-runtime, development)
    --tag TAG              Custom tag for images
    --registry REGISTRY     Container registry URL
    --push                 Push images after building
    --no-cache             Build without cache
    --platform PLATFORM    Target platform (linux/amd64, linux/arm64)

Examples:
    $0 build --service auth --target production-runtime
    $0 build --push --tag v1.0.0
    $0 scan --service ac
    $0 deploy --target development

Environment Variables:
    REGISTRY               Container registry URL (default: ghcr.io)
    REPOSITORY            Repository name (default: ca-git-com-co/acgs)
    BUILD_TARGET          Build target (default: production-runtime)
    PUSH_IMAGES           Push after build (default: false)
    DOCKER_BUILDKIT       Enable BuildKit (default: 1)

EOF
}

# Parse command line arguments
parse_args() {
    COMMAND=""
    SERVICE=""
    TAG="latest"
    NO_CACHE=""
    PLATFORM="linux/amd64"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            build|push|pull|clean|scan|test|deploy|help)
                COMMAND="$1"
                shift
                ;;
            --service)
                SERVICE="$2"
                shift 2
                ;;
            --target)
                BUILD_TARGET="$2"
                shift 2
                ;;
            --tag)
                TAG="$2"
                shift 2
                ;;
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --push)
                PUSH_IMAGES="true"
                shift
                ;;
            --no-cache)
                NO_CACHE="--no-cache"
                shift
                ;;
            --platform)
                PLATFORM="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    if [[ -z "$COMMAND" ]]; then
        log_error "No command specified"
        show_help
        exit 1
    fi
}

# Validate service name
validate_service() {
    if [[ -n "$SERVICE" ]]; then
        if [[ ! " ${SERVICES[@]} " =~ " ${SERVICE} " ]]; then
            log_error "Invalid service: $SERVICE"
            log_info "Available services: ${SERVICES[*]}"
            exit 1
        fi
    fi
}

# Get commit SHA for tagging
get_commit_sha() {
    if command -v git >/dev/null 2>&1; then
        git rev-parse --short HEAD 2>/dev/null || echo "unknown"
    else
        echo "unknown"
    fi
}

# Build Docker image
build_image() {
    local service="$1"
    local dockerfile="$2"
    local image_name="$REGISTRY/$REPOSITORY/$service:$TAG"
    local commit_sha=$(get_commit_sha)
    
    log_info "Building image for service: $service"
    log_info "Dockerfile: $dockerfile"
    log_info "Image name: $image_name"
    log_info "Build target: $BUILD_TARGET"
    
    # Build arguments
    local build_args=(
        "--target" "$BUILD_TARGET"
        "--tag" "$image_name"
        "--tag" "$REGISTRY/$REPOSITORY/$service:$commit_sha"
        "--file" "$dockerfile"
        "--platform" "$PLATFORM"
        "--label" "org.opencontainers.image.title=ACGS-1 $service Service"
        "--label" "org.opencontainers.image.description=Constitutional Governance System - $service Service"
        "--label" "org.opencontainers.image.vendor=ACGS Project"
        "--label" "org.opencontainers.image.version=$TAG"
        "--label" "org.opencontainers.image.revision=$commit_sha"
        "--label" "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    )
    
    if [[ -n "$NO_CACHE" ]]; then
        build_args+=("$NO_CACHE")
    fi
    
    # Build the image
    if docker build "${build_args[@]}" .; then
        log_success "Successfully built image: $image_name"
        
        # Push if requested
        if [[ "$PUSH_IMAGES" == "true" ]]; then
            push_image "$service"
        fi
    else
        log_error "Failed to build image: $image_name"
        return 1
    fi
}

# Push Docker image
push_image() {
    local service="$1"
    local image_name="$REGISTRY/$REPOSITORY/$service:$TAG"
    local commit_sha=$(get_commit_sha)
    
    log_info "Pushing image: $image_name"
    
    if docker push "$image_name" && docker push "$REGISTRY/$REPOSITORY/$service:$commit_sha"; then
        log_success "Successfully pushed image: $image_name"
    else
        log_error "Failed to push image: $image_name"
        return 1
    fi
}

# Pull Docker image
pull_image() {
    local service="$1"
    local image_name="$REGISTRY/$REPOSITORY/$service:$TAG"
    
    log_info "Pulling image: $image_name"
    
    if docker pull "$image_name"; then
        log_success "Successfully pulled image: $image_name"
    else
        log_error "Failed to pull image: $image_name"
        return 1
    fi
}

# Scan image for vulnerabilities
scan_image() {
    local service="$1"
    local image_name="$REGISTRY/$REPOSITORY/$service:$TAG"
    
    log_info "Scanning image for vulnerabilities: $image_name"
    
    # Check if trivy is installed
    if ! command -v trivy >/dev/null 2>&1; then
        log_warning "Trivy not installed, installing..."
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    fi
    
    # Run vulnerability scan
    if trivy image --severity HIGH,CRITICAL "$image_name"; then
        log_success "Vulnerability scan completed for: $image_name"
    else
        log_warning "Vulnerabilities found in: $image_name"
    fi
}

# Test image functionality
test_image() {
    local service="$1"
    local image_name="$REGISTRY/$REPOSITORY/$service:$TAG"
    local port=$((8000 + $(printf '%s\n' "${SERVICES[@]}" | grep -n "^$service$" | cut -d: -f1) - 1))
    
    log_info "Testing image functionality: $image_name"
    
    # Start container
    local container_id=$(docker run -d -p "$port:$port" "$image_name")
    
    # Wait for container to start
    sleep 10
    
    # Test health endpoint
    if curl -f "http://localhost:$port/health" >/dev/null 2>&1; then
        log_success "Health check passed for: $image_name"
    else
        log_warning "Health check failed for: $image_name"
    fi
    
    # Cleanup
    docker stop "$container_id" >/dev/null
    docker rm "$container_id" >/dev/null
}

# Clean up Docker images
clean_images() {
    log_info "Cleaning up Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old ACGS images (keep latest 5)
    for service in "${SERVICES[@]}"; do
        local images=$(docker images "$REGISTRY/$REPOSITORY/$service" --format "{{.ID}}" | tail -n +6)
        if [[ -n "$images" ]]; then
            echo "$images" | xargs docker rmi -f 2>/dev/null || true
        fi
    done
    
    log_success "Docker cleanup completed"
}

# Deploy using docker-compose
deploy_images() {
    log_info "Deploying images using docker-compose..."
    
    local compose_file
    case "$BUILD_TARGET" in
        "development")
            compose_file="infrastructure/docker/docker-compose.development.yml"
            ;;
        "production-runtime")
            compose_file="config/docker/docker-compose.production.yml"
            ;;
        *)
            compose_file="infrastructure/docker/docker-compose.yml"
            ;;
    esac
    
    if [[ -f "$compose_file" ]]; then
        export IMAGE_TAG="$TAG"
        docker-compose -f "$compose_file" up -d
        log_success "Deployment completed using: $compose_file"
    else
        log_error "Compose file not found: $compose_file"
        return 1
    fi
}

# Main execution
main() {
    log_info "ACGS-1 Docker Image Management"
    log_info "Registry: $REGISTRY"
    log_info "Repository: $REPOSITORY"
    log_info "Build Target: $BUILD_TARGET"
    log_info "Tag: $TAG"
    
    case "$COMMAND" in
        "build")
            if [[ -n "$SERVICE" ]]; then
                # Build specific service
                local index=0
                for i in "${!SERVICES[@]}"; do
                    if [[ "${SERVICES[$i]}" == "$SERVICE" ]]; then
                        index=$i
                        break
                    fi
                done
                build_image "$SERVICE" "${DOCKERFILES[$index]}"
            else
                # Build all services
                for i in "${!SERVICES[@]}"; do
                    build_image "${SERVICES[$i]}" "${DOCKERFILES[$i]}"
                done
            fi
            ;;
        "push")
            if [[ -n "$SERVICE" ]]; then
                push_image "$SERVICE"
            else
                for service in "${SERVICES[@]}"; do
                    push_image "$service"
                done
            fi
            ;;
        "pull")
            if [[ -n "$SERVICE" ]]; then
                pull_image "$SERVICE"
            else
                for service in "${SERVICES[@]}"; do
                    pull_image "$service"
                done
            fi
            ;;
        "scan")
            if [[ -n "$SERVICE" ]]; then
                scan_image "$SERVICE"
            else
                for service in "${SERVICES[@]}"; do
                    scan_image "$service"
                done
            fi
            ;;
        "test")
            if [[ -n "$SERVICE" ]]; then
                test_image "$SERVICE"
            else
                for service in "${SERVICES[@]}"; do
                    test_image "$service"
                done
            fi
            ;;
        "clean")
            clean_images
            ;;
        "deploy")
            deploy_images
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Parse arguments and run
parse_args "$@"
validate_service
main
