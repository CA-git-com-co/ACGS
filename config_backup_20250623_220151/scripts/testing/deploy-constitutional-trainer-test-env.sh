#!/bin/bash
# Constitutional Trainer Integration Test Environment Deployment Script
#
# This script deploys all required services for Constitutional Trainer integration testing
# in a temporary Kubernetes namespace with proper configuration and monitoring.
#
# Usage:
#   ./deploy-constitutional-trainer-test-env.sh [OPTIONS]
#
# Options:
#   --namespace NAME    Test namespace (default: acgs-integration-test)
#   --timeout SECONDS   Deployment timeout (default: 600)
#   --cleanup          Clean up existing test environment first
#   --mock-services    Use mock services instead of full deployments
#   --help             Show this help message

set -euo pipefail

# Default configuration
NAMESPACE="acgs-integration-test"
TIMEOUT=600
CLEANUP=false
MOCK_SERVICES=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

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

# Help function
show_help() {
    cat << EOF
Constitutional Trainer Integration Test Environment Deployment

This script deploys all required services for Constitutional Trainer integration testing
in a temporary Kubernetes namespace.

Usage:
    $0 [OPTIONS]

Options:
    --namespace NAME    Test namespace (default: acgs-integration-test)
    --timeout SECONDS   Deployment timeout (default: 600)
    --cleanup          Clean up existing test environment first
    --mock-services    Use mock services instead of full deployments
    --help             Show this help message

Examples:
    # Deploy with default settings
    $0

    # Deploy with custom namespace and cleanup
    $0 --namespace my-test --cleanup

    # Deploy with mock services for faster testing
    $0 --mock-services

    # Clean up existing environment first
    $0 --cleanup --namespace acgs-integration-test

Environment Variables:
    KUBECONFIG         Path to kubectl configuration file
    ACGS_TEST_REGISTRY Container registry for test images

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --cleanup)
                CLEANUP=true
                shift
                ;;
            --mock-services)
                MOCK_SERVICES=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check kubectl connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check if namespace already exists
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        if [[ "$CLEANUP" == "true" ]]; then
            log_warning "Namespace $NAMESPACE exists, will clean up first"
        else
            log_warning "Namespace $NAMESPACE already exists, use --cleanup to remove it first"
        fi
    fi
    
    log_success "Prerequisites check passed"
}

# Cleanup existing environment
cleanup_environment() {
    log_info "Cleaning up existing test environment..."
    
    # Delete namespace (cascades to all resources)
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
        
        # Wait for namespace deletion
        log_info "Waiting for namespace deletion..."
        while kubectl get namespace "$NAMESPACE" &> /dev/null; do
            sleep 2
        done
    fi
    
    log_success "Environment cleanup completed"
}

# Create test namespace
create_namespace() {
    log_info "Creating test namespace: $NAMESPACE"
    
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: $NAMESPACE
  labels:
    acgs-lite.io/test-environment: "true"
    acgs-lite.io/created-by: "integration-tests"
    acgs-lite.io/created-at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EOF

    log_success "Namespace created: $NAMESPACE"
}

# Deploy Redis
deploy_redis() {
    log_info "Deploying Redis..."
    
    if [[ "$MOCK_SERVICES" == "true" ]]; then
        deploy_mock_redis
    else
        deploy_full_redis
    fi
}

deploy_mock_redis() {
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: $NAMESPACE
  labels:
    app: redis
    acgs-lite.io/service-type: cache
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        readinessProbe:
          tcpSocket:
            port: 6379
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          tcpSocket:
            port: 6379
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: $NAMESPACE
  labels:
    app: redis
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
    name: redis
EOF
}

deploy_full_redis() {
    # Use existing Redis manifest with namespace override
    if [[ -f "$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/redis.yaml" ]]; then
        kubectl apply -f "$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/redis.yaml" -n "$NAMESPACE"
    else
        log_warning "Redis manifest not found, using mock deployment"
        deploy_mock_redis
    fi
}

# Deploy Policy Engine
deploy_policy_engine() {
    log_info "Deploying Policy Engine..."
    
    if [[ "$MOCK_SERVICES" == "true" ]]; then
        deploy_mock_policy_engine
    else
        deploy_full_policy_engine
    fi
}

deploy_mock_policy_engine() {
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: policy-engine
  namespace: $NAMESPACE
  labels:
    app: policy-engine
    acgs-lite.io/service-type: policy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: policy-engine
  template:
    metadata:
      labels:
        app: policy-engine
    spec:
      containers:
      - name: policy-engine
        image: nginx:alpine
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "50m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 15
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: policy-engine
  namespace: $NAMESPACE
  labels:
    app: policy-engine
spec:
  selector:
    app: policy-engine
  ports:
  - port: 8001
    targetPort: 8001
    name: http
EOF
}

deploy_full_policy_engine() {
    if [[ -f "$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/policy-engine.yaml" ]]; then
        kubectl apply -f "$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/policy-engine.yaml" -n "$NAMESPACE"
    else
        log_warning "Policy Engine manifest not found, using mock deployment"
        deploy_mock_policy_engine
    fi
}

# Deploy Audit Engine
deploy_audit_engine() {
    log_info "Deploying Audit Engine..."
    
    if [[ "$MOCK_SERVICES" == "true" ]]; then
        deploy_mock_audit_engine
    else
        deploy_full_audit_engine
    fi
}

deploy_mock_audit_engine() {
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: audit-engine
  namespace: $NAMESPACE
  labels:
    app: audit-engine
    acgs-lite.io/service-type: audit
spec:
  replicas: 1
  selector:
    matchLabels:
      app: audit-engine
  template:
    metadata:
      labels:
        app: audit-engine
    spec:
      containers:
      - name: audit-engine
        image: nginx:alpine
        ports:
        - containerPort: 8003
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "50m"
---
apiVersion: v1
kind: Service
metadata:
  name: audit-engine
  namespace: $NAMESPACE
  labels:
    app: audit-engine
spec:
  selector:
    app: audit-engine
  ports:
  - port: 8003
    targetPort: 8003
    name: http
EOF
}

deploy_full_audit_engine() {
    if [[ -f "$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/audit-engine.yaml" ]]; then
        kubectl apply -f "$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/audit-engine.yaml" -n "$NAMESPACE"
    else
        log_warning "Audit Engine manifest not found, using mock deployment"
        deploy_mock_audit_engine
    fi
}

# Deploy Constitutional Trainer
deploy_constitutional_trainer() {
    log_info "Deploying Constitutional Trainer..."

    if [[ -f "$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/constitutional-trainer.yaml" ]]; then
        kubectl apply -f "$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/constitutional-trainer.yaml" -n "$NAMESPACE"
    else
        log_warning "Constitutional Trainer manifest not found, skipping deployment"
        return 1
    fi
}

# Wait for all services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready (timeout: ${TIMEOUT}s)..."

    local start_time=$(date +%s)
    local services=("redis" "policy-engine" "audit-engine")

    # Add constitutional-trainer if not using mock services
    if [[ "$MOCK_SERVICES" == "false" ]]; then
        services+=("constitutional-trainer")
    fi

    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [[ $elapsed -gt $TIMEOUT ]]; then
            log_error "Timeout waiting for services to be ready"
            return 1
        fi

        local all_ready=true

        for service in "${services[@]}"; do
            if ! kubectl get deployment "$service" -n "$NAMESPACE" &> /dev/null; then
                log_warning "Deployment $service not found"
                all_ready=false
                break
            fi

            local ready_replicas=$(kubectl get deployment "$service" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
            local desired_replicas=$(kubectl get deployment "$service" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "1")

            if [[ "$ready_replicas" != "$desired_replicas" ]]; then
                all_ready=false
                break
            fi
        done

        if [[ "$all_ready" == "true" ]]; then
            log_success "All services are ready"
            break
        fi

        log_info "Waiting for services... (${elapsed}s elapsed)"
        sleep 5
    done
}

# Verify service health
verify_service_health() {
    log_info "Verifying service health..."

    # Port forward services for health checks
    local pids=()

    kubectl port-forward -n "$NAMESPACE" svc/redis 6379:6379 &
    pids+=($!)

    kubectl port-forward -n "$NAMESPACE" svc/policy-engine 8001:8001 &
    pids+=($!)

    kubectl port-forward -n "$NAMESPACE" svc/audit-engine 8003:8003 &
    pids+=($!)

    if [[ "$MOCK_SERVICES" == "false" ]]; then
        kubectl port-forward -n "$NAMESPACE" svc/constitutional-trainer 8000:8000 &
        pids+=($!)
    fi

    # Wait for port forwards to be established
    sleep 10

    # Test Redis connectivity
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h localhost -p 6379 ping | grep -q PONG; then
            log_success "Redis health check passed"
        else
            log_warning "Redis health check failed"
        fi
    else
        log_info "redis-cli not available, skipping Redis health check"
    fi

    # Test HTTP services
    local http_services=("policy-engine:8001" "audit-engine:8003")

    if [[ "$MOCK_SERVICES" == "false" ]]; then
        http_services+=("constitutional-trainer:8000")
    fi

    for service_port in "${http_services[@]}"; do
        local service_name="${service_port%:*}"
        local port="${service_port#*:}"

        if curl -f -s "http://localhost:$port/health" &> /dev/null; then
            log_success "$service_name health check passed"
        else
            log_warning "$service_name health check failed"
        fi
    done

    # Clean up port forwards
    for pid in "${pids[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
}

# Print deployment summary
print_summary() {
    log_info "Deployment Summary"
    echo "===================="
    echo "Namespace: $NAMESPACE"
    echo "Mock Services: $MOCK_SERVICES"
    echo "Timeout: ${TIMEOUT}s"
    echo ""

    log_info "Deployed Services:"
    kubectl get deployments -n "$NAMESPACE" -o wide
    echo ""

    log_info "Service Endpoints:"
    kubectl get services -n "$NAMESPACE" -o wide
    echo ""

    log_info "Pod Status:"
    kubectl get pods -n "$NAMESPACE" -o wide
    echo ""

    log_success "Test environment deployed successfully!"
    echo ""
    echo "To run integration tests:"
    echo "  pytest tests/integration/test_constitutional_trainer_integration.py -v"
    echo ""
    echo "To access services locally:"
    echo "  kubectl port-forward -n $NAMESPACE svc/constitutional-trainer 8000:8000"
    echo "  kubectl port-forward -n $NAMESPACE svc/policy-engine 8001:8001"
    echo "  kubectl port-forward -n $NAMESPACE svc/audit-engine 8003:8003"
    echo "  kubectl port-forward -n $NAMESPACE svc/redis 6379:6379"
    echo ""
    echo "To clean up:"
    echo "  kubectl delete namespace $NAMESPACE"
}

# Main execution
main() {
    log_info "Constitutional Trainer Integration Test Environment Deployment"
    echo "=============================================================="

    parse_args "$@"
    check_prerequisites

    if [[ "$CLEANUP" == "true" ]]; then
        cleanup_environment
    fi

    create_namespace
    deploy_redis
    deploy_policy_engine
    deploy_audit_engine

    if [[ "$MOCK_SERVICES" == "false" ]]; then
        deploy_constitutional_trainer
    fi

    wait_for_services
    verify_service_health
    print_summary
}

# Execute main function with all arguments
main "$@"
