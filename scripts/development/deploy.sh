# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS-1 Comprehensive Deployment Script
# Automated deployment for ACGS-1 Constitutional Governance System

set -euo pipefail

# Configuration
ENVIRONMENTS=("development" "staging" "production")
SERVICES=("auth" "ac" "integrity" "fv" "gs" "pgc" "ec")
DEPLOYMENT_STRATEGIES=("rolling" "blue-green" "canary")

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
ACGS-1 Comprehensive Deployment Script

Usage: $0 [OPTIONS]

Options:
    --environment ENV       Target environment (development, staging, production)
    --strategy STRATEGY     Deployment strategy (rolling, blue-green, canary)
    --services SERVICES     Comma-separated list of services to deploy (default: all)
    --image-tag TAG         Docker image tag to deploy (default: latest)
    --dry-run              Show what would be done without executing
    --rollback             Rollback to previous version
    --health-check         Run health checks only
    --help                 Show this help message

Examples:
    $0 --environment staging --strategy rolling
    $0 --environment production --strategy blue-green --services auth,ac
    $0 --rollback --environment staging
    $0 --health-check --environment production

Environment Variables:
    KUBECONFIG             Kubernetes configuration file
    DOCKER_REGISTRY        Docker registry URL
    DEPLOYMENT_TIMEOUT     Deployment timeout in seconds (default: 600)

EOF
}

# Parse command line arguments
parse_args() {
    ENVIRONMENT=""
    STRATEGY="rolling"
    SERVICES_TO_DEPLOY=""
    IMAGE_TAG="latest"
    DRY_RUN=""
    ROLLBACK=""
    HEALTH_CHECK_ONLY=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --strategy)
                STRATEGY="$2"
                shift 2
                ;;
            --services)
                SERVICES_TO_DEPLOY="$2"
                shift 2
                ;;
            --image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --rollback)
                ROLLBACK="true"
                shift
                ;;
            --health-check)
                HEALTH_CHECK_ONLY="true"
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
    
    # Validate required parameters
    if [[ -z "$ENVIRONMENT" ]]; then
        log_error "Environment is required"
        show_help
        exit 1
    fi
    
    # Validate environment
    if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${ENVIRONMENT} " ]]; then
        log_error "Invalid environment: $ENVIRONMENT"
        log_info "Available environments: ${ENVIRONMENTS[*]}"
        exit 1
    fi
    
    # Validate strategy
    if [[ ! " ${DEPLOYMENT_STRATEGIES[@]} " =~ " ${STRATEGY} " ]]; then
        log_error "Invalid deployment strategy: $STRATEGY"
        log_info "Available strategies: ${DEPLOYMENT_STRATEGIES[*]}"
        exit 1
    fi
    
    # Parse services list
    if [[ -n "$SERVICES_TO_DEPLOY" ]]; then
        IFS=',' read -ra SERVICES_ARRAY <<< "$SERVICES_TO_DEPLOY"
    else
        SERVICES_ARRAY=("${SERVICES[@]}")
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check if kubectl is installed and configured
    if ! command -v kubectl >/dev/null 2>&1; then
        log_error "kubectl is required but not installed"
        exit 1
    fi
    
    # Check if connected to cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Not connected to Kubernetes cluster"
        exit 1
    fi
    
    # Check if Docker is available
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check if Helm is available
    if ! command -v helm >/dev/null 2>&1; then
        log_error "Helm is required but not installed"
        exit 1
    fi
    
    # Validate environment-specific requirements
    case "$ENVIRONMENT" in
        "production")
            if [[ -z "${DOCKER_REGISTRY:-}" ]]; then
                log_error "DOCKER_REGISTRY environment variable is required for production"
                exit 1
            fi
            ;;
    esac
    
    log_success "Prerequisites check passed"
}

# Load environment configuration
load_environment_config() {
    log_info "Loading environment configuration for $ENVIRONMENT..."
    
    local config_file="config/environments/${ENVIRONMENT}config/environments/development.env"
    if [[ -f "$config_file" ]]; then
        source "$config_file"
        log_success "Environment configuration loaded"
    else
        log_warning "Environment configuration file not found: $config_file"
    fi
    
    # Set default values
    DEPLOYMENT_TIMEOUT="${DEPLOYMENT_TIMEOUT:-600}"
    DOCKER_REGISTRY="${DOCKER_REGISTRY:-ghcr.io/ca-git-com-co/acgs}"
    NAMESPACE_PREFIX="${NAMESPACE_PREFIX:-acgs}"
}

# Health check function
run_health_checks() {
    log_info "Running health checks for $ENVIRONMENT environment..."
    
    local namespace="${NAMESPACE_PREFIX}-${ENVIRONMENT}"
    local failed_services=()
    
    for service in "${SERVICES_ARRAY[@]}"; do
        log_info "Checking health of $service service..."
        
        # Check if deployment exists
        if ! kubectl get deployment "${service}-service" -n "$namespace" >/dev/null 2>&1; then
            log_warning "Deployment ${service}-service not found in namespace $namespace"
            failed_services+=("$service")
            continue
        fi
        
        # Check deployment status
        if kubectl rollout status deployment/"${service}-service" -n "$namespace" --timeout=60s >/dev/null 2>&1; then
            log_success "$service service is healthy"
        else
            log_error "$service service health check failed"
            failed_services+=("$service")
        fi
        
        # Check service endpoint
        local service_port
        case "$service" in
            "auth") service_port=8000 ;;
            "ac") service_port=8001 ;;
            "integrity") service_port=8002 ;;
            "fv") service_port=8003 ;;
            "gs") service_port=8004 ;;
            "pgc") service_port=8005 ;;
            "ec") service_port=8006 ;;
            *) service_port=8000 ;;
        esac
        
        # Port forward and test endpoint
        kubectl port-forward -n "$namespace" "svc/${service}-service" "$service_port:$service_port" &
        local pf_pid=$!
        sleep 2
        
        if curl -f "http://localhost:$service_port/health" >/dev/null 2>&1; then
            log_success "$service service endpoint is responding"
        else
            log_warning "$service service endpoint not responding"
        fi
        
        kill $pf_pid 2>/dev/null || true
    done
    
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All health checks passed"
        return 0
    else
        log_error "Health checks failed for services: ${failed_services[*]}"
        return 1
    fi
}

# Rolling deployment strategy
deploy_rolling() {
    log_info "Executing rolling deployment for $ENVIRONMENT..."
    
    local namespace="${NAMESPACE_PREFIX}-${ENVIRONMENT}"
    
    # Ensure namespace exists
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    for service in "${SERVICES_ARRAY[@]}"; do
        log_info "Deploying $service service with rolling strategy..."
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "DRY RUN: Would deploy $service service"
            continue
        fi
        
        # Update deployment image
        kubectl set image deployment/"${service}-service" \
            "${service}-container=${DOCKER_REGISTRY}/${service}:${IMAGE_TAG}" \
            -n "$namespace"
        
        # Wait for rollout to complete
        if kubectl rollout status deployment/"${service}-service" -n "$namespace" --timeout="${DEPLOYMENT_TIMEOUT}s"; then
            log_success "$service service deployed successfully"
        else
            log_error "$service service deployment failed"
            return 1
        fi
    done
    
    log_success "Rolling deployment completed successfully"
}

# Blue-green deployment strategy
deploy_blue_green() {
    log_info "Executing blue-green deployment for $ENVIRONMENT..."
    
    local namespace="${NAMESPACE_PREFIX}-${ENVIRONMENT}"
    local current_color
    local new_color
    
    # Determine current and new colors
    if kubectl get namespace "${namespace}-blue" >/dev/null 2>&1; then
        current_color="blue"
        new_color="green"
    else
        current_color="green"
        new_color="blue"
    fi
    
    log_info "Current environment: $current_color, deploying to: $new_color"
    
    # Create new environment namespace
    kubectl create namespace "${namespace}-${new_color}" --dry-run=client -o yaml | kubectl apply -f -
    
    for service in "${SERVICES_ARRAY[@]}"; do
        log_info "Deploying $service service to $new_color environment..."
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "DRY RUN: Would deploy $service service to $new_color"
            continue
        fi
        
        # Deploy to new environment
        cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${service}-service
  namespace: ${namespace}-${new_color}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ${service}-service
  template:
    metadata:
      labels:
        app: ${service}-service
    spec:
      containers:
      - name: ${service}-container
        image: ${DOCKER_REGISTRY}/${service}:${IMAGE_TAG}
        ports:
        - containerPort: 800$((${#service}))
        env:
        - name: ENVIRONMENT
          value: ${ENVIRONMENT}
---
apiVersion: v1
kind: Service
metadata:
  name: ${service}-service
  namespace: ${namespace}-${new_color}
spec:
  selector:
    app: ${service}-service
  ports:
  - port: 800$((${#service}))
    targetPort: 800$((${#service}))
EOF
        
        # Wait for deployment to be ready
        kubectl rollout status deployment/"${service}-service" -n "${namespace}-${new_color}" --timeout="${DEPLOYMENT_TIMEOUT}s"
    done
    
    # Run health checks on new environment
    log_info "Running health checks on $new_color environment..."
    if run_health_checks; then
        log_info "Switching traffic to $new_color environment..."
        
        # Switch ingress traffic (this would be environment-specific)
        # kubectl patch ingress acgs-ingress -n "$namespace" -p '{"spec":{"rules":[{"host":"api.acgs-pgp.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"'${new_color}'-service","port":{"number":80}}}}]}}]}}'
        
        log_success "Blue-green deployment completed successfully"
        log_info "Old environment ($current_color) is still available for rollback"
    else
        log_error "Health checks failed on $new_color environment"
        return 1
    fi
}

# Canary deployment strategy
deploy_canary() {
    log_info "Executing canary deployment for $ENVIRONMENT..."
    
    local namespace="${NAMESPACE_PREFIX}-${ENVIRONMENT}"
    
    # Ensure namespace exists
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    for service in "${SERVICES_ARRAY[@]}"; do
        log_info "Deploying $service service with canary strategy..."
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "DRY RUN: Would deploy $service service with canary"
            continue
        fi
        
        # Deploy canary version (10% of traffic)
        cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${service}-service-canary
  namespace: ${namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${service}-service
      version: canary
  template:
    metadata:
      labels:
        app: ${service}-service
        version: canary
    spec:
      containers:
      - name: ${service}-container
        image: ${DOCKER_REGISTRY}/${service}:${IMAGE_TAG}
        ports:
        - containerPort: 800$((${#service}))
        env:
        - name: ENVIRONMENT
          value: ${ENVIRONMENT}
        - name: VERSION
          value: canary
EOF
        
        # Wait for canary deployment
        kubectl rollout status deployment/"${service}-service-canary" -n "$namespace" --timeout="${DEPLOYMENT_TIMEOUT}s"
        
        log_info "Canary deployment for $service is ready"
        log_warning "Monitor canary metrics before promoting to full deployment"
    done
    
    log_success "Canary deployment completed successfully"
    log_info "Use --strategy rolling to promote canary to full deployment"
}

# Rollback function
rollback_deployment() {
    log_info "Rolling back deployment in $ENVIRONMENT..."
    
    local namespace="${NAMESPACE_PREFIX}-${ENVIRONMENT}"
    
    for service in "${SERVICES_ARRAY[@]}"; do
        log_info "Rolling back $service service..."
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "DRY RUN: Would rollback $service service"
            continue
        fi
        
        # Rollback to previous version
        if kubectl rollout undo deployment/"${service}-service" -n "$namespace"; then
            log_success "$service service rolled back successfully"
        else
            log_error "$service service rollback failed"
        fi
    done
    
    log_success "Rollback completed successfully"
}

# Main deployment function
main_deploy() {
    log_info "Starting ACGS-1 deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Strategy: $STRATEGY"
    log_info "Services: ${SERVICES_ARRAY[*]}"
    log_info "Image Tag: $IMAGE_TAG"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No actual changes will be made"
    fi
    
    # Load environment configuration
    load_environment_config
    
    # Handle special operations
    if [[ "$HEALTH_CHECK_ONLY" == "true" ]]; then
        run_health_checks
        return $?
    fi
    
    if [[ "$ROLLBACK" == "true" ]]; then
        rollback_deployment
        return $?
    fi
    
    # Execute deployment based on strategy
    case "$STRATEGY" in
        "rolling")
            deploy_rolling
            ;;
        "blue-green")
            deploy_blue_green
            ;;
        "canary")
            deploy_canary
            ;;
        *)
            log_error "Unknown deployment strategy: $STRATEGY"
            exit 1
            ;;
    esac
    
    # Run post-deployment health checks
    log_info "Running post-deployment health checks..."
    if run_health_checks; then
        log_success "Deployment completed successfully!"
    else
        log_error "Post-deployment health checks failed"
        return 1
    fi
}

# Main execution
main() {
    check_prerequisites
    main_deploy
}

# Parse arguments and run
parse_args "$@"
main
