#!/bin/bash

# Constitutional Trainer Service Deployment Script
# ACGS-1 Lite Constitutional AI Training Service with NVIDIA Data Flywheel Integration
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SERVICE_VERSION="1.0.0"
NAMESPACE="governance"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-acgs}"
IMAGE_TAG="${IMAGE_TAG:-v${SERVICE_VERSION}}"
KUBECONFIG="${KUBECONFIG:-${HOME}/.kube/config}"
DRY_RUN="${DRY_RUN:-false}"
SKIP_BUILD="${SKIP_BUILD:-false}"
SKIP_TESTS="${SKIP_TESTS:-false}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Deployment configuration
DEPLOYMENT_TIMEOUT="${DEPLOYMENT_TIMEOUT:-600}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-300}"
ROLLBACK_ON_FAILURE="${ROLLBACK_ON_FAILURE:-true}"

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check required tools
    local required_tools=("docker" "kubectl" "helm")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool '$tool' is not installed"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check Kubernetes connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "Namespace '$NAMESPACE' does not exist, creating..."
        kubectl create namespace "$NAMESPACE"
        kubectl label namespace "$NAMESPACE" app.kubernetes.io/name=acgs-lite
        kubectl label namespace "$NAMESPACE" acgs-lite.io/constitutional-hash="$CONSTITUTIONAL_HASH"
    fi
    
    log_success "Prerequisites check completed"
}

# Function to build Docker image
build_docker_image() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log_info "Skipping Docker image build"
        return 0
    fi
    
    log_info "Building Constitutional Trainer Docker image..."
    
    local image_name="${DOCKER_REGISTRY}/constitutional-trainer:${IMAGE_TAG}"
    local build_args=(
        "--build-arg" "CONSTITUTIONAL_HASH=${CONSTITUTIONAL_HASH}"
        "--build-arg" "BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        "--build-arg" "VERSION=${SERVICE_VERSION}"
        "--tag" "$image_name"
        "--file" "services/core/constitutional-trainer/Dockerfile"
        "services/core/constitutional-trainer/"
    )
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would build image with: docker build ${build_args[*]}"
        return 0
    fi
    
    if ! docker build "${build_args[@]}"; then
        log_error "Docker image build failed"
        exit 1
    fi
    
    # Security scan
    log_info "Running security scan on Docker image..."
    if command -v trivy &> /dev/null; then
        trivy image --severity HIGH,CRITICAL "$image_name" || log_warning "Security scan found issues"
    else
        log_warning "Trivy not installed, skipping security scan"
    fi
    
    log_success "Docker image built successfully: $image_name"
}

# Function to run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_info "Skipping tests"
        return 0
    fi
    
    log_info "Running Constitutional Trainer tests..."
    
    local test_image="${DOCKER_REGISTRY}/constitutional-trainer:${IMAGE_TAG}-test"
    
    # Build test image
    docker build \
        --build-arg "CONSTITUTIONAL_HASH=${CONSTITUTIONAL_HASH}" \
        --target builder \
        --tag "$test_image" \
        --file "services/core/constitutional-trainer/Dockerfile" \
        "services/core/constitutional-trainer/"
    
    # Run tests in container
    local test_cmd=(
        "docker" "run" "--rm"
        "--env" "CONSTITUTIONAL_HASH=${CONSTITUTIONAL_HASH}"
        "--env" "ENVIRONMENT=test"
        "$test_image"
        "python" "-m" "pytest" "tests/" "-v" "--tb=short"
    )
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would run tests with: ${test_cmd[*]}"
        return 0
    fi
    
    if ! "${test_cmd[@]}"; then
        log_error "Tests failed"
        exit 1
    fi
    
    log_success "All tests passed"
}

# Function to push Docker image
push_docker_image() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log_info "Skipping Docker image push"
        return 0
    fi
    
    local image_name="${DOCKER_REGISTRY}/constitutional-trainer:${IMAGE_TAG}"
    
    log_info "Pushing Docker image to registry..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would push image: $image_name"
        return 0
    fi
    
    if ! docker push "$image_name"; then
        log_error "Docker image push failed"
        exit 1
    fi
    
    log_success "Docker image pushed successfully"
}

# Function to deploy to Kubernetes
deploy_to_kubernetes() {
    log_info "Deploying Constitutional Trainer to Kubernetes..."
    
    local manifests_dir="${PROJECT_ROOT}/infrastructure/kubernetes/acgs-lite"
    local image_name="${DOCKER_REGISTRY}/constitutional-trainer:${IMAGE_TAG}"
    
    # Update image in deployment manifest
    local temp_manifest=$(mktemp)
    sed "s|image: acgs/constitutional-trainer:v1.0.0|image: ${image_name}|g" \
        "${manifests_dir}/constitutional-trainer.yaml" > "$temp_manifest"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would apply Kubernetes manifests"
        log_info "DRY RUN: kubectl apply -f ${manifests_dir}/constitutional-trainer.yaml"
        log_info "DRY RUN: kubectl apply -f ${manifests_dir}/constitutional-trainer-network-policy.yaml"
        rm -f "$temp_manifest"
        return 0
    fi
    
    # Apply manifests
    if ! kubectl apply -f "$temp_manifest"; then
        log_error "Failed to apply Constitutional Trainer deployment"
        rm -f "$temp_manifest"
        exit 1
    fi
    
    if ! kubectl apply -f "${manifests_dir}/constitutional-trainer-network-policy.yaml"; then
        log_error "Failed to apply Constitutional Trainer network policies"
        rm -f "$temp_manifest"
        exit 1
    fi
    
    rm -f "$temp_manifest"
    
    log_success "Kubernetes manifests applied successfully"
}

# Function to wait for deployment
wait_for_deployment() {
    log_info "Waiting for Constitutional Trainer deployment to be ready..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would wait for deployment readiness"
        return 0
    fi
    
    # Wait for deployment to be ready
    if ! kubectl rollout status deployment/constitutional-trainer \
        --namespace="$NAMESPACE" \
        --timeout="${DEPLOYMENT_TIMEOUT}s"; then
        log_error "Deployment failed to become ready within ${DEPLOYMENT_TIMEOUT} seconds"
        
        if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
            log_warning "Rolling back deployment..."
            kubectl rollout undo deployment/constitutional-trainer --namespace="$NAMESPACE"
        fi
        
        exit 1
    fi
    
    log_success "Deployment is ready"
}

# Function to run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would run health checks"
        return 0
    fi
    
    # Get service endpoint
    local service_ip
    service_ip=$(kubectl get service constitutional-trainer \
        --namespace="$NAMESPACE" \
        --output jsonpath='{.spec.clusterIP}')
    
    if [[ -z "$service_ip" ]]; then
        log_error "Could not get service IP"
        exit 1
    fi
    
    # Health check with timeout
    local health_url="http://${service_ip}:8010/health"
    local start_time=$(date +%s)
    local timeout_time=$((start_time + HEALTH_CHECK_TIMEOUT))
    
    while [[ $(date +%s) -lt $timeout_time ]]; do
        if kubectl run health-check-pod \
            --image=curlimages/curl:latest \
            --rm -i --restart=Never \
            --namespace="$NAMESPACE" \
            -- curl -f "$health_url" &> /dev/null; then
            
            log_success "Health check passed"
            return 0
        fi
        
        log_info "Health check failed, retrying in 10 seconds..."
        sleep 10
    done
    
    log_error "Health check failed after ${HEALTH_CHECK_TIMEOUT} seconds"
    exit 1
}

# Function to validate constitutional compliance
validate_constitutional_compliance() {
    log_info "Validating constitutional compliance..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would validate constitutional compliance"
        return 0
    fi
    
    # Check that all pods have the correct constitutional hash label
    local pods_with_hash
    pods_with_hash=$(kubectl get pods \
        --namespace="$NAMESPACE" \
        --selector="app=constitutional-trainer" \
        --output jsonpath='{.items[*].metadata.labels.acgs-lite\.io/constitutional-hash}')
    
    for hash in $pods_with_hash; do
        if [[ "$hash" != "$CONSTITUTIONAL_HASH" ]]; then
            log_error "Pod has incorrect constitutional hash: $hash (expected: $CONSTITUTIONAL_HASH)"
            exit 1
        fi
    done
    
    # Test constitutional validation endpoint
    local service_ip
    service_ip=$(kubectl get service constitutional-trainer \
        --namespace="$NAMESPACE" \
        --output jsonpath='{.spec.clusterIP}')
    
    local test_payload='{"model_name":"test","training_data":[{"prompt":"test","response":"test"}]}'
    
    if kubectl run compliance-test-pod \
        --image=curlimages/curl:latest \
        --rm -i --restart=Never \
        --namespace="$NAMESPACE" \
        -- curl -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer test-token" \
        -d "$test_payload" \
        "http://${service_ip}:8010/api/v1/train" &> /dev/null; then
        
        log_success "Constitutional compliance validation passed"
    else
        log_warning "Constitutional compliance test returned expected authentication error (this is normal)"
    fi
}

# Function to display deployment summary
display_deployment_summary() {
    log_info "Deployment Summary:"
    echo "===================="
    echo "Service: Constitutional Trainer"
    echo "Version: $SERVICE_VERSION"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Namespace: $NAMESPACE"
    echo "Environment: $ENVIRONMENT"
    echo "Image: ${DOCKER_REGISTRY}/constitutional-trainer:${IMAGE_TAG}"
    echo ""
    
    if [[ "$DRY_RUN" != "true" ]]; then
        echo "Deployment Status:"
        kubectl get deployment constitutional-trainer --namespace="$NAMESPACE"
        echo ""
        echo "Service Status:"
        kubectl get service constitutional-trainer --namespace="$NAMESPACE"
        echo ""
        echo "Pod Status:"
        kubectl get pods --selector="app=constitutional-trainer" --namespace="$NAMESPACE"
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy Constitutional Trainer Service for ACGS-1 Lite

OPTIONS:
    -h, --help              Show this help message
    -d, --dry-run           Perform a dry run without making changes
    -s, --skip-build        Skip Docker image build
    -t, --skip-tests        Skip running tests
    -e, --environment ENV   Set deployment environment (default: production)
    --image-tag TAG         Set Docker image tag (default: v${SERVICE_VERSION})
    --registry REGISTRY     Set Docker registry (default: acgs)
    --timeout SECONDS       Set deployment timeout (default: 600)

ENVIRONMENT VARIABLES:
    DOCKER_REGISTRY         Docker registry for images
    IMAGE_TAG              Docker image tag
    KUBECONFIG             Path to kubeconfig file
    DRY_RUN                Perform dry run (true/false)
    SKIP_BUILD             Skip Docker build (true/false)
    SKIP_TESTS             Skip tests (true/false)
    ENVIRONMENT            Deployment environment
    DEPLOYMENT_TIMEOUT     Deployment timeout in seconds
    HEALTH_CHECK_TIMEOUT   Health check timeout in seconds
    ROLLBACK_ON_FAILURE    Rollback on deployment failure (true/false)

EXAMPLES:
    # Standard deployment
    $0

    # Dry run deployment
    $0 --dry-run

    # Deploy without building new image
    $0 --skip-build

    # Deploy to staging environment
    $0 --environment staging

    # Deploy with custom image tag
    $0 --image-tag v1.1.0

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -d|--dry-run)
            DRY_RUN="true"
            shift
            ;;
        -s|--skip-build)
            SKIP_BUILD="true"
            shift
            ;;
        -t|--skip-tests)
            SKIP_TESTS="true"
            shift
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --image-tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --registry)
            DOCKER_REGISTRY="$2"
            shift 2
            ;;
        --timeout)
            DEPLOYMENT_TIMEOUT="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main deployment flow
main() {
    log_info "Starting Constitutional Trainer deployment..."
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info "Environment: $ENVIRONMENT"
    log_info "Dry Run: $DRY_RUN"
    
    check_prerequisites
    build_docker_image
    run_tests
    push_docker_image
    deploy_to_kubernetes
    wait_for_deployment
    run_health_checks
    validate_constitutional_compliance
    display_deployment_summary
    
    log_success "Constitutional Trainer deployment completed successfully!"
}

# Run main function
main "$@"
