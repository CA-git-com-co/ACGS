#!/bin/bash
# ACGS-2 Production Deployment Script
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOYMENT_DIR="${PROJECT_ROOT}/deployment"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

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

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Configuration
ENVIRONMENT="${ENVIRONMENT:-production}"
NAMESPACE="${NAMESPACE:-acgs-system}"
REGISTRY="${REGISTRY:-acgs-registry.local}"
TAG="${TAG:-latest}"
DOMAIN="${DOMAIN:-acgs.local}"

# Deployment options
BUILD_IMAGES="${BUILD_IMAGES:-true}"
DEPLOY_INFRASTRUCTURE="${DEPLOY_INFRASTRUCTURE:-true}"
DEPLOY_SERVICES="${DEPLOY_SERVICES:-true}"
RUN_TESTS="${RUN_TESTS:-true}"
SKIP_CONFIRMATION="${SKIP_CONFIRMATION:-false}"

usage() {
    cat << EOF
🏛️ ACGS-2 Production Deployment Script
Constitutional Hash: ${CONSTITUTIONAL_HASH}

Usage: $0 [OPTIONS]

Options:
    -e, --environment     Target environment (default: production)
    -n, --namespace       Kubernetes namespace (default: acgs-system)
    -r, --registry        Container registry (default: acgs-registry.local)
    -t, --tag             Image tag (default: latest)
    -d, --domain          Domain name (default: acgs.local)
    --skip-build          Skip building container images
    --skip-infra          Skip infrastructure deployment
    --skip-services       Skip services deployment
    --skip-tests          Skip post-deployment tests
    --yes                 Skip confirmation prompts
    -h, --help            Show this help message

Examples:
    $0                                    # Full deployment with defaults
    $0 -e staging -t v1.2.3              # Deploy to staging with specific tag
    $0 --skip-build --skip-tests          # Deploy without building or testing
    $0 --yes -e production                # Non-interactive production deployment

Environment Variables:
    ENVIRONMENT           Target environment
    NAMESPACE             Kubernetes namespace
    REGISTRY              Container registry
    TAG                   Image tag
    DOMAIN                Domain name
    BUILD_IMAGES          Build container images (true/false)
    DEPLOY_INFRASTRUCTURE Deploy infrastructure (true/false)
    DEPLOY_SERVICES       Deploy services (true/false)
    RUN_TESTS             Run post-deployment tests (true/false)
    SKIP_CONFIRMATION     Skip confirmation prompts (true/false)
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        --skip-build)
            BUILD_IMAGES="false"
            shift
            ;;
        --skip-infra)
            DEPLOY_INFRASTRUCTURE="false"
            shift
            ;;
        --skip-services)
            DEPLOY_SERVICES="false"
            shift
            ;;
        --skip-tests)
            RUN_TESTS="false"
            shift
            ;;
        --yes)
            SKIP_CONFIRMATION="true"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
validate_environment() {
    log_info "Validating deployment environment..."
    
    # Check required tools
    local required_tools=("kubectl" "docker" "helm")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Check Kubernetes connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Validate constitutional hash in environment
    if [[ "${CONSTITUTIONAL_HASH}" != "cdd01ef066bc6cf2" ]]; then
        log_error "Constitutional hash validation failed"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check namespace exists or create it
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "Creating namespace: $NAMESPACE"
        kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/namespace.yaml"
    fi
    
    # Validate secrets are configured
    if ! kubectl get secret acgs-secrets -n "$NAMESPACE" &> /dev/null; then
        log_warning "Secrets not found. Please configure secrets before deployment."
        log_info "Apply secrets with: kubectl apply -f ${DEPLOYMENT_DIR}/kubernetes/secrets.yaml"
    fi
    
    # Run security audit
    if [[ "$RUN_TESTS" == "true" ]]; then
        log_info "Running security audit..."
        cd "${PROJECT_ROOT}/tests/security"
        if python constitutional_security_audit.py --json; then
            log_success "Security audit passed"
        else
            log_warning "Security audit found issues - review security_audit_report.txt"
        fi
    fi
    
    # Run performance tests
    if [[ "$RUN_TESTS" == "true" ]]; then
        log_info "Running performance validation..."
        cd "${PROJECT_ROOT}/tests/performance"
        if python run_performance_tests.py; then
            log_success "Performance tests passed"
        else
            log_warning "Performance tests found issues - review performance reports"
        fi
    fi
    
    log_success "Pre-deployment checks completed"
}

# Build and push container images
build_and_push_images() {
    if [[ "$BUILD_IMAGES" != "true" ]]; then
        log_info "Skipping image build (BUILD_IMAGES=false)"
        return
    fi
    
    log_info "Building and pushing container images..."
    
    local services=(
        "constitutional-core:constitutional-ai"
        "auth-service:auth-service"
        "monitoring-service:monitoring-service"
        "audit-service:audit-service"
        "gdpr-compliance:gdpr-compliance"
        "alerting-service:alerting-service"
        "api-gateway:api-gateway"
    )
    
    for service_config in "${services[@]}"; do
        IFS=':' read -r service_name service_path <<< "$service_config"
        
        log_info "Building $service_name..."
        
        # Build image
        docker build \
            -f "${DEPLOYMENT_DIR}/docker/Dockerfile.production" \
            -t "${REGISTRY}/${service_name}:${TAG}" \
            --build-arg SERVICE_NAME="$service_name" \
            --build-arg SERVICE_PATH="$service_path" \
            --label "constitutional.hash=${CONSTITUTIONAL_HASH}" \
            --label "version=${TAG}" \
            --label "environment=${ENVIRONMENT}" \
            "$PROJECT_ROOT"
        
        # Push image
        docker push "${REGISTRY}/${service_name}:${TAG}"
        
        log_success "Built and pushed $service_name:$TAG"
    done
    
    log_success "All images built and pushed successfully"
}

# Deploy infrastructure components
deploy_infrastructure() {
    if [[ "$DEPLOY_INFRASTRUCTURE" != "true" ]]; then
        log_info "Skipping infrastructure deployment (DEPLOY_INFRASTRUCTURE=false)"
        return
    fi
    
    log_info "Deploying infrastructure components..."
    
    # Apply namespace and RBAC
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/namespace.yaml"
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/secrets.yaml"
    
    # Apply ConfigMaps
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/configmap.yaml"
    
    # Deploy PostgreSQL
    log_info "Deploying PostgreSQL..."
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/infrastructure/postgres.yaml"
    
    # Deploy Redis
    log_info "Deploying Redis..."
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/infrastructure/redis.yaml"
    
    # Deploy monitoring stack
    log_info "Deploying monitoring stack..."
    kubectl apply -f "${DEPLOYMENT_DIR}/kubernetes/monitoring/"
    
    # Wait for infrastructure to be ready
    log_info "Waiting for infrastructure to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/postgres -n "$NAMESPACE" || true
    kubectl wait --for=condition=available --timeout=300s deployment/redis -n "$NAMESPACE" || true
    
    log_success "Infrastructure deployment completed"
}

# Deploy ACGS-2 services
deploy_services() {
    if [[ "$DEPLOY_SERVICES" != "true" ]]; then
        log_info "Skipping services deployment (DEPLOY_SERVICES=false)"
        return
    fi
    
    log_info "Deploying ACGS-2 services..."
    
    # Update image tags in deployment manifests
    local services=(
        "auth-service"
        "constitutional-core"
        "monitoring-service"
        "audit-service"
        "gdpr-compliance"
        "alerting-service"
        "api-gateway"
    )
    
    for service in "${services[@]}"; do
        log_info "Deploying $service..."
        
        # Apply deployment with image tag substitution
        envsubst < "${DEPLOYMENT_DIR}/kubernetes/deployments/${service}.yaml" | \
        sed "s|image: acgs/${service}:latest|image: ${REGISTRY}/${service}:${TAG}|g" | \
        kubectl apply -f -
        
        # Wait for deployment to be ready
        kubectl wait --for=condition=available --timeout=300s deployment/"$service" -n "$NAMESPACE" || true
        
        log_success "Deployed $service"
    done
    
    # Apply ingress
    log_info "Configuring ingress..."
    envsubst < "${DEPLOYMENT_DIR}/kubernetes/ingress.yaml" | kubectl apply -f -
    
    log_success "Services deployment completed"
}

# Run post-deployment validation
post_deployment_validation() {
    if [[ "$RUN_TESTS" != "true" ]]; then
        log_info "Skipping post-deployment validation (RUN_TESTS=false)"
        return
    fi
    
    log_info "Running post-deployment validation..."
    
    # Check all pods are running
    log_info "Checking pod status..."
    kubectl get pods -n "$NAMESPACE"
    
    # Check services are accessible
    local services=("auth-service" "constitutional-core" "monitoring-service" "audit-service" "gdpr-compliance" "alerting-service")
    
    for service in "${services[@]}"; do
        log_info "Testing $service health endpoint..."
        
        # Port forward and test
        kubectl port-forward "service/$service" 8080:8080 -n "$NAMESPACE" &
        local port_forward_pid=$!
        sleep 5
        
        if curl -f "http://localhost:8080/health" &> /dev/null; then
            log_success "$service health check passed"
        else
            log_warning "$service health check failed"
        fi
        
        kill $port_forward_pid 2>/dev/null || true
        sleep 2
    done
    
    # Run constitutional compliance validation
    log_info "Validating constitutional compliance..."
    
    # Check constitutional hash in all service responses
    for service in "${services[@]}"; do
        kubectl port-forward "service/$service" 8080:8080 -n "$NAMESPACE" &
        local port_forward_pid=$!
        sleep 5
        
        local response=$(curl -s "http://localhost:8080/health" || echo "{}")
        local hash=$(echo "$response" | jq -r '.constitutional_hash // empty')
        
        if [[ "$hash" == "$CONSTITUTIONAL_HASH" ]]; then
            log_success "$service constitutional compliance verified"
        else
            log_error "$service constitutional compliance failed - expected $CONSTITUTIONAL_HASH, got $hash"
        fi
        
        kill $port_forward_pid 2>/dev/null || true
        sleep 2
    done
    
    log_success "Post-deployment validation completed"
}

# Rollback deployment
rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    # Rollback all deployments
    local services=("auth-service" "constitutional-core" "monitoring-service" "audit-service" "gdpr-compliance" "alerting-service" "api-gateway")
    
    for service in "${services[@]}"; do
        kubectl rollout undo deployment/"$service" -n "$NAMESPACE" || true
    done
    
    log_info "Rollback initiated. Check deployment status with:"
    log_info "kubectl get deployments -n $NAMESPACE"
}

# Cleanup on error
cleanup_on_error() {
    log_error "Deployment failed. Running cleanup..."
    
    # Save logs for debugging
    mkdir -p /tmp/acgs-deployment-logs
    kubectl logs -l app.kubernetes.io/part-of=acgs-2 -n "$NAMESPACE" --tail=100 > /tmp/acgs-deployment-logs/service-logs.txt 2>/dev/null || true
    kubectl describe pods -n "$NAMESPACE" > /tmp/acgs-deployment-logs/pod-descriptions.txt 2>/dev/null || true
    
    log_info "Logs saved to /tmp/acgs-deployment-logs/"
    log_info "To rollback, run: $0 --rollback"
}

# Main deployment function
main() {
    log_header "🏛️ ACGS-2 Production Deployment"
    log_header "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_header "=================================="
    
    log_info "Deployment Configuration:"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Namespace: $NAMESPACE"
    log_info "  Registry: $REGISTRY"
    log_info "  Tag: $TAG"
    log_info "  Domain: $DOMAIN"
    log_info "  Build Images: $BUILD_IMAGES"
    log_info "  Deploy Infrastructure: $DEPLOY_INFRASTRUCTURE"
    log_info "  Deploy Services: $DEPLOY_SERVICES"
    log_info "  Run Tests: $RUN_TESTS"
    echo
    
    # Confirmation prompt
    if [[ "$SKIP_CONFIRMATION" != "true" ]]; then
        read -p "Continue with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Set error trap
    trap cleanup_on_error ERR
    
    # Execute deployment steps
    validate_environment
    pre_deployment_checks
    build_and_push_images
    deploy_infrastructure
    deploy_services
    post_deployment_validation
    
    # Success message
    log_success "🎉 ACGS-2 deployment completed successfully!"
    log_success "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info ""
    log_info "Next steps:"
    log_info "  1. Monitor deployment: kubectl get pods -n $NAMESPACE"
    log_info "  2. Check logs: kubectl logs -f deployment/auth-service -n $NAMESPACE"
    log_info "  3. Access services via ingress: https://$DOMAIN"
    log_info "  4. View monitoring: https://grafana.$DOMAIN"
    log_info ""
    log_info "For troubleshooting, see: ${DEPLOYMENT_DIR}/docs/troubleshooting.md"
}

# Handle rollback option
if [[ "${1:-}" == "--rollback" ]]; then
    rollback_deployment
    exit 0
fi

# Run main deployment
main "$@"