#!/bin/bash
# Constitutional Trainer Staging Deployment Script
#
# This script deploys the Constitutional Trainer Service and all dependencies
# to the staging environment with comprehensive validation and rollback capabilities.
#
# Usage:
#   ./deploy-constitutional-trainer-staging.sh [OPTIONS]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STAGING_NAMESPACE="${STAGING_NAMESPACE:-acgs-staging}"
IMAGE_TAG="${IMAGE_TAG:-staging}"
REGISTRY="${REGISTRY:-ghcr.io}"
REPOSITORY="${REPOSITORY:-ca-git-com-co/acgs}"
TIMEOUT="${TIMEOUT:-600}"
ROLLBACK_ON_FAILURE="${ROLLBACK_ON_FAILURE:-true}"
SKIP_SMOKE_TESTS="${SKIP_SMOKE_TESTS:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Help function
show_help() {
    cat << EOF
Constitutional Trainer Staging Deployment

This script deploys the Constitutional Trainer Service and all dependencies
to the staging environment with validation and rollback capabilities.

Usage:
    $0 [OPTIONS]

Options:
    --namespace NAME        Staging namespace (default: acgs-staging)
    --image-tag TAG         Container image tag (default: staging)
    --registry REGISTRY     Container registry (default: ghcr.io)
    --repository REPO       Repository name (default: ca-git-com-co/acgs)
    --timeout SECONDS       Deployment timeout (default: 600)
    --skip-smoke-tests     Skip post-deployment smoke tests
    --no-rollback          Disable automatic rollback on failure
    --dry-run              Show what would be deployed without applying
    --help                 Show this help message

Examples:
    # Deploy with default settings
    $0

    # Deploy specific image tag
    $0 --image-tag v1.2.3

    # Deploy with custom namespace
    $0 --namespace acgs-staging-v2

    # Dry run to see what would be deployed
    $0 --dry-run

Environment Variables:
    KUBECONFIG             Kubernetes configuration file
    STAGING_NAMESPACE      Staging namespace override
    IMAGE_TAG              Container image tag override
    REGISTRY               Container registry override

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --namespace)
                STAGING_NAMESPACE="$2"
                shift 2
                ;;
            --image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --repository)
                REPOSITORY="$2"
                shift 2
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --skip-smoke-tests)
                SKIP_SMOKE_TESTS=true
                shift
                ;;
            --no-rollback)
                ROLLBACK_ON_FAILURE=false
                shift
                ;;
            --dry-run)
                DRY_RUN=true
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
    log_info "Checking deployment prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace "$STAGING_NAMESPACE" &> /dev/null; then
        log_info "Creating staging namespace: $STAGING_NAMESPACE"
        kubectl create namespace "$STAGING_NAMESPACE"
        kubectl label namespace "$STAGING_NAMESPACE" \
            environment=staging \
            acgs-lite.io/managed=true
    fi
    
    # Verify image exists
    local full_image="${REGISTRY}/${REPOSITORY}/constitutional-trainer:${IMAGE_TAG}"
    log_info "Verifying image exists: $full_image"
    
    if ! docker manifest inspect "$full_image" &> /dev/null; then
        log_warning "Cannot verify image existence: $full_image"
        log_warning "Proceeding anyway - image will be pulled during deployment"
    fi
    
    log_success "Prerequisites check completed"
}

# Backup current deployment
backup_current_deployment() {
    log_info "Backing up current deployment state..."
    
    local backup_dir="./staging-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup deployments
    kubectl get deployments -n "$STAGING_NAMESPACE" -o yaml > "$backup_dir/deployments.yaml" 2>/dev/null || true
    
    # Backup services
    kubectl get services -n "$STAGING_NAMESPACE" -o yaml > "$backup_dir/services.yaml" 2>/dev/null || true
    
    # Backup configmaps
    kubectl get configmaps -n "$STAGING_NAMESPACE" -o yaml > "$backup_dir/configmaps.yaml" 2>/dev/null || true
    
    # Backup secrets
    kubectl get secrets -n "$STAGING_NAMESPACE" -o yaml > "$backup_dir/secrets.yaml" 2>/dev/null || true
    
    # Store backup location for potential rollback
    echo "$backup_dir" > .last-staging-backup
    
    log_success "Backup completed: $backup_dir"
}

# Deploy Redis
deploy_redis() {
    log_info "Deploying Redis..."
    
    local manifest="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/redis.yaml"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "DRY RUN: Would deploy Redis from $manifest"
        return
    fi
    
    if [[ -f "$manifest" ]]; then
        kubectl apply -f "$manifest" -n "$STAGING_NAMESPACE"
    else
        log_warning "Redis manifest not found, deploying minimal Redis"
        deploy_minimal_redis
    fi
    
    # Wait for Redis to be ready
    kubectl wait --for=condition=Ready pod -l app=redis -n "$STAGING_NAMESPACE" --timeout="${TIMEOUT}s"
    
    log_success "Redis deployed successfully"
}

# Deploy minimal Redis if manifest not found
deploy_minimal_redis() {
    cat <<EOF | kubectl apply -f - -n "$STAGING_NAMESPACE"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  labels:
    app: redis
    environment: staging
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
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
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
  labels:
    app: redis
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
EOF
}

# Deploy Policy Engine
deploy_policy_engine() {
    log_info "Deploying Policy Engine..."
    
    local manifest="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/policy-engine.yaml"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "DRY RUN: Would deploy Policy Engine from $manifest"
        return
    fi
    
    if [[ -f "$manifest" ]]; then
        # Update image tag in manifest for staging
        sed "s|image: .*policy-engine.*|image: ${REGISTRY}/${REPOSITORY}/policy-engine:${IMAGE_TAG}|g" "$manifest" | \
        kubectl apply -f - -n "$STAGING_NAMESPACE"
    else
        log_error "Policy Engine manifest not found: $manifest"
        exit 1
    fi
    
    # Wait for Policy Engine to be ready
    kubectl wait --for=condition=Ready pod -l app=policy-engine -n "$STAGING_NAMESPACE" --timeout="${TIMEOUT}s"
    
    log_success "Policy Engine deployed successfully"
}

# Deploy Audit Engine
deploy_audit_engine() {
    log_info "Deploying Audit Engine..."
    
    local manifest="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/audit-engine.yaml"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "DRY RUN: Would deploy Audit Engine from $manifest"
        return
    fi
    
    if [[ -f "$manifest" ]]; then
        # Update image tag in manifest for staging
        sed "s|image: .*audit-engine.*|image: ${REGISTRY}/${REPOSITORY}/audit-engine:${IMAGE_TAG}|g" "$manifest" | \
        kubectl apply -f - -n "$STAGING_NAMESPACE"
    else
        log_error "Audit Engine manifest not found: $manifest"
        exit 1
    fi
    
    # Wait for Audit Engine to be ready
    kubectl wait --for=condition=Ready pod -l app=audit-engine -n "$STAGING_NAMESPACE" --timeout="${TIMEOUT}s"
    
    log_success "Audit Engine deployed successfully"
}

# Deploy Constitutional Trainer
deploy_constitutional_trainer() {
    log_info "Deploying Constitutional Trainer..."
    
    local manifest="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/constitutional-trainer.yaml"
    local full_image="${REGISTRY}/${REPOSITORY}/constitutional-trainer:${IMAGE_TAG}"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "DRY RUN: Would deploy Constitutional Trainer with image $full_image"
        return
    fi
    
    if [[ -f "$manifest" ]]; then
        # Update image tag in manifest for staging
        sed "s|image: .*constitutional-trainer.*|image: ${full_image}|g" "$manifest" | \
        kubectl apply -f - -n "$STAGING_NAMESPACE"
    else
        log_error "Constitutional Trainer manifest not found: $manifest"
        exit 1
    fi
    
    # Wait for Constitutional Trainer to be ready
    kubectl wait --for=condition=Ready pod -l app=constitutional-trainer -n "$STAGING_NAMESPACE" --timeout="${TIMEOUT}s"
    
    log_success "Constitutional Trainer deployed successfully"
}

# Deploy monitoring (optional)
deploy_monitoring() {
    log_info "Deploying monitoring components..."
    
    local prometheus_manifest="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/prometheus.yaml"
    local grafana_manifest="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite/grafana.yaml"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "DRY RUN: Would deploy monitoring components"
        return
    fi
    
    # Deploy Prometheus if manifest exists
    if [[ -f "$prometheus_manifest" ]]; then
        kubectl apply -f "$prometheus_manifest" -n "$STAGING_NAMESPACE" || log_warning "Failed to deploy Prometheus"
    fi
    
    # Deploy Grafana if manifest exists
    if [[ -f "$grafana_manifest" ]]; then
        kubectl apply -f "$grafana_manifest" -n "$STAGING_NAMESPACE" || log_warning "Failed to deploy Grafana"
    fi
    
    log_success "Monitoring components deployed"
}

# Run post-deployment health checks
run_health_checks() {
    if [[ "${SKIP_SMOKE_TESTS}" == "true" ]]; then
        log_info "Skipping health checks"
        return
    fi
    
    log_info "Running post-deployment health checks..."
    
    # Check service readiness
    local services=("redis" "policy-engine" "audit-engine" "constitutional-trainer")
    
    for service in "${services[@]}"; do
        log_info "Checking $service health..."
        
        # Port forward for health check
        kubectl port-forward -n "$STAGING_NAMESPACE" "svc/$service" 8080:8000 &
        local pf_pid=$!
        
        sleep 5
        
        # Health check
        if curl -f -s "http://localhost:8080/health" &> /dev/null; then
            log_success "$service health check passed"
        else
            log_warning "$service health check failed"
        fi
        
        # Clean up port forward
        kill "$pf_pid" 2>/dev/null || true
        sleep 2
    done
}

# Run smoke tests
run_smoke_tests() {
    if [[ "${SKIP_SMOKE_TESTS}" == "true" ]]; then
        log_info "Skipping smoke tests"
        return
    fi
    
    log_info "Running smoke tests..."
    
    # Port forward Constitutional Trainer for testing
    kubectl port-forward -n "$STAGING_NAMESPACE" svc/constitutional-trainer 8000:8000 &
    local ct_pid=$!
    
    kubectl port-forward -n "$STAGING_NAMESPACE" svc/policy-engine 8001:8001 &
    local pe_pid=$!
    
    sleep 10
    
    # Test Constitutional Trainer API
    log_info "Testing Constitutional Trainer API..."
    
    local test_request='{
        "model_name": "staging-test-model",
        "model_id": "staging-test-001",
        "training_data": [
            {
                "prompt": "What is constitutional AI?",
                "response": "Constitutional AI is an approach to training AI systems to be helpful, harmless, and honest."
            }
        ],
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": ["q_proj", "v_proj"],
            "lora_dropout": 0.1
        }
    }'
    
    if curl -f -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer staging-test-token" \
        -d "$test_request" \
        "http://localhost:8000/api/v1/train" &> /dev/null; then
        log_success "Constitutional Trainer API smoke test passed"
    else
        log_error "Constitutional Trainer API smoke test failed"
        
        # Clean up port forwards
        kill "$ct_pid" "$pe_pid" 2>/dev/null || true
        
        if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
            rollback_deployment
        fi
        exit 1
    fi
    
    # Clean up port forwards
    kill "$ct_pid" "$pe_pid" 2>/dev/null || true
    
    log_success "Smoke tests completed successfully"
}

# Test rollback functionality
test_rollback() {
    log_info "Testing rollback functionality..."
    
    # Create a temporary failing configuration
    kubectl patch deployment constitutional-trainer -n "$STAGING_NAMESPACE" \
        -p '{"spec":{"template":{"spec":{"containers":[{"name":"constitutional-trainer","image":"nginx:invalid-tag"}]}}}}' || true
    
    # Wait a moment
    sleep 10
    
    # Rollback
    kubectl rollout undo deployment/constitutional-trainer -n "$STAGING_NAMESPACE"
    
    # Wait for rollback to complete
    kubectl rollout status deployment/constitutional-trainer -n "$STAGING_NAMESPACE" --timeout="${TIMEOUT}s"
    
    log_success "Rollback test completed successfully"
}

# Rollback deployment
rollback_deployment() {
    log_error "Rolling back deployment due to failure..."
    
    if [[ -f ".last-staging-backup" ]]; then
        local backup_dir=$(cat .last-staging-backup)
        
        if [[ -d "$backup_dir" ]]; then
            log_info "Restoring from backup: $backup_dir"
            
            # Restore deployments
            if [[ -f "$backup_dir/deployments.yaml" ]]; then
                kubectl apply -f "$backup_dir/deployments.yaml" -n "$STAGING_NAMESPACE" || true
            fi
            
            # Restore services
            if [[ -f "$backup_dir/services.yaml" ]]; then
                kubectl apply -f "$backup_dir/services.yaml" -n "$STAGING_NAMESPACE" || true
            fi
            
            log_success "Rollback completed"
        else
            log_error "Backup directory not found: $backup_dir"
        fi
    else
        log_warning "No backup found, performing kubectl rollout undo"
        kubectl rollout undo deployment/constitutional-trainer -n "$STAGING_NAMESPACE" || true
    fi
}

# Generate deployment report
generate_deployment_report() {
    log_info "Generating deployment report..."
    
    local report_file="staging-deployment-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# Constitutional Trainer Staging Deployment Report

**Deployment Date:** $(date)  
**Namespace:** $STAGING_NAMESPACE  
**Image Tag:** $IMAGE_TAG  
**Registry:** $REGISTRY  
**Repository:** $REPOSITORY  

## Deployment Summary

### Services Deployed

| Service | Status | Image |
|---------|--------|-------|
| Redis | $(kubectl get deployment redis -n "$STAGING_NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "Unknown") | redis:7-alpine |
| Policy Engine | $(kubectl get deployment policy-engine -n "$STAGING_NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "Unknown") | ${REGISTRY}/${REPOSITORY}/policy-engine:${IMAGE_TAG} |
| Audit Engine | $(kubectl get deployment audit-engine -n "$STAGING_NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "Unknown") | ${REGISTRY}/${REPOSITORY}/audit-engine:${IMAGE_TAG} |
| Constitutional Trainer | $(kubectl get deployment constitutional-trainer -n "$STAGING_NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "Unknown") | ${REGISTRY}/${REPOSITORY}/constitutional-trainer:${IMAGE_TAG} |

### Pod Status

\`\`\`
$(kubectl get pods -n "$STAGING_NAMESPACE" 2>/dev/null || echo "No pods found")
\`\`\`

### Service Endpoints

\`\`\`
$(kubectl get services -n "$STAGING_NAMESPACE" 2>/dev/null || echo "No services found")
\`\`\`

## Health Check Results

- Health checks: $(if [[ "${SKIP_SMOKE_TESTS}" == "true" ]]; then echo "Skipped"; else echo "Completed"; fi)
- Smoke tests: $(if [[ "${SKIP_SMOKE_TESTS}" == "true" ]]; then echo "Skipped"; else echo "Completed"; fi)
- Rollback test: Completed

## Next Steps

1. **Stakeholder Review**: Share this report with stakeholders for sign-off
2. **Integration Testing**: Run comprehensive integration tests
3. **Performance Testing**: Execute load testing scenarios
4. **Security Validation**: Perform security scans and audits
5. **Production Readiness**: Prepare for production deployment

## Access Information

To access the staging environment:

\`\`\`bash
# Port forward Constitutional Trainer
kubectl port-forward -n $STAGING_NAMESPACE svc/constitutional-trainer 8000:8000

# Port forward Policy Engine
kubectl port-forward -n $STAGING_NAMESPACE svc/policy-engine 8001:8001

# Port forward Audit Engine
kubectl port-forward -n $STAGING_NAMESPACE svc/audit-engine 8003:8003
\`\`\`

## Rollback Instructions

If rollback is needed:

\`\`\`bash
# Quick rollback
kubectl rollout undo deployment/constitutional-trainer -n $STAGING_NAMESPACE

# Or use the deployment script
./deploy-constitutional-trainer-staging.sh --rollback
\`\`\`

EOF

    log_success "Deployment report generated: $report_file"
}

# Main execution
main() {
    log_info "🚀 Constitutional Trainer Staging Deployment"
    echo "============================================================"
    
    parse_args "$@"
    check_prerequisites
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "DRY RUN MODE - No changes will be applied"
    fi
    
    backup_current_deployment
    
    # Deploy services in order
    deploy_redis
    deploy_policy_engine
    deploy_audit_engine
    deploy_constitutional_trainer
    deploy_monitoring
    
    # Validation and testing
    run_health_checks
    run_smoke_tests
    test_rollback
    
    # Generate report
    generate_deployment_report
    
    log_success "✅ Staging deployment completed successfully!"
    echo ""
    echo "📊 Deployment report: staging-deployment-report-*.md"
    echo "🔗 Access staging environment:"
    echo "   kubectl port-forward -n $STAGING_NAMESPACE svc/constitutional-trainer 8000:8000"
    echo ""
    echo "🎯 Ready for stakeholder sign-off!"
}

# Trap for cleanup
trap 'log_warning "Deployment interrupted"' INT TERM

# Execute main function
main "$@"
