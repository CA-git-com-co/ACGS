#!/bin/bash

# ACGS GitOps Monitoring Script
# Monitor and validate ACGS GitOps workflow components

set -euo pipefail

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
NAMESPACE_CROSSPLANE="crossplane-system"
NAMESPACE_ARGOCD="argocd"
NAMESPACE_ACGS="acgs-system"

# Check cluster status
check_cluster() {
    log_info "Checking cluster status..."
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        return 1
    fi
    
    local nodes
    nodes=$(kubectl get nodes --no-headers | wc -l)
    log_success "Connected to cluster with $nodes nodes"
    
    kubectl get nodes -o wide
}

# Check Crossplane status
check_crossplane() {
    log_info "Checking Crossplane status..."
    
    # Check namespace
    if ! kubectl get namespace $NAMESPACE_CROSSPLANE &> /dev/null; then
        log_error "Crossplane namespace not found"
        return 1
    fi
    
    # Check pods
    local crossplane_pods
    crossplane_pods=$(kubectl get pods -n $NAMESPACE_CROSSPLANE --no-headers | grep -c "Running" || echo "0")
    log_info "Crossplane pods running: $crossplane_pods"
    
    # Check providers
    log_info "Checking providers..."
    kubectl get providers -o wide
    
    # Check functions
    log_info "Checking functions..."
    kubectl get functions -o wide
    
    # Check compositions
    log_info "Checking compositions..."
    kubectl get compositions -o wide
    
    # Check provider health
    local healthy_providers
    healthy_providers=$(kubectl get providers -o jsonpath='{.items[?(@.status.conditions[?(@.type=="Healthy")].status=="True")].metadata.name}' | wc -w)
    log_info "Healthy providers: $healthy_providers"
    
    if [[ $healthy_providers -eq 0 ]]; then
        log_warning "No healthy providers found"
        kubectl describe providers
    fi
}

# Check ArgoCD status
check_argocd() {
    log_info "Checking ArgoCD status..."
    
    # Check namespace
    if ! kubectl get namespace $NAMESPACE_ARGOCD &> /dev/null; then
        log_error "ArgoCD namespace not found"
        return 1
    fi
    
    # Check pods
    local argocd_pods
    argocd_pods=$(kubectl get pods -n $NAMESPACE_ARGOCD --no-headers | grep -c "Running" || echo "0")
    log_info "ArgoCD pods running: $argocd_pods"
    
    # Check applications
    log_info "Checking ArgoCD applications..."
    kubectl get applications -n $NAMESPACE_ARGOCD -o wide
    
    # Check application health
    if command -v argocd &> /dev/null; then
        log_info "Checking application health with ArgoCD CLI..."
        argocd app list --output wide 2>/dev/null || log_warning "ArgoCD CLI not configured"
    fi
}

# Check ACGS service claims
check_service_claims() {
    log_info "Checking ACGS service claims..."
    
    # Check namespace
    if ! kubectl get namespace $NAMESPACE_ACGS &> /dev/null; then
        log_warning "ACGS namespace not found"
        return 0
    fi
    
    # Check CRD
    if ! kubectl get crd acgsserviceclaims.acgs.io &> /dev/null; then
        log_error "ACGSServiceClaim CRD not found"
        return 1
    fi
    
    # List service claims
    local claims_count
    claims_count=$(kubectl get acgsserviceclaims -n $NAMESPACE_ACGS --no-headers 2>/dev/null | wc -l || echo "0")
    log_info "Service claims found: $claims_count"
    
    if [[ $claims_count -gt 0 ]]; then
        kubectl get acgsserviceclaims -n $NAMESPACE_ACGS -o wide
        
        # Check claim status
        log_info "Checking claim status..."
        kubectl get acgsserviceclaims -n $NAMESPACE_ACGS -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}' | column -t
    fi
}

# Check GitHub resources
check_github_resources() {
    log_info "Checking GitHub resources..."
    
    # Check repositories
    local repos_count
    repos_count=$(kubectl get repositories.github.upbound.io --no-headers 2>/dev/null | wc -l || echo "0")
    log_info "GitHub repositories: $repos_count"
    
    if [[ $repos_count -gt 0 ]]; then
        kubectl get repositories.github.upbound.io -o wide
    fi
    
    # Check repository files
    local files_count
    files_count=$(kubectl get repositoryfiles.github.upbound.io --no-headers 2>/dev/null | wc -l || echo "0")
    log_info "Repository files: $files_count"
    
    if [[ $files_count -gt 0 ]]; then
        kubectl get repositoryfiles.github.upbound.io -o wide
    fi
}

# Check events
check_events() {
    log_info "Checking recent events..."
    
    # Crossplane events
    log_info "Crossplane events (last 10):"
    kubectl get events -n $NAMESPACE_CROSSPLANE --sort-by=.metadata.creationTimestamp | tail -10
    
    # ArgoCD events
    log_info "ArgoCD events (last 10):"
    kubectl get events -n $NAMESPACE_ARGOCD --sort-by=.metadata.creationTimestamp | tail -10
    
    # ACGS events
    if kubectl get namespace $NAMESPACE_ACGS &> /dev/null; then
        log_info "ACGS events (last 10):"
        kubectl get events -n $NAMESPACE_ACGS --sort-by=.metadata.creationTimestamp | tail -10
    fi
}

# Watch service claims
watch_claims() {
    log_info "Watching service claims (Ctrl+C to stop)..."
    kubectl get acgsserviceclaims -n $NAMESPACE_ACGS -w
}

# Show logs
show_logs() {
    local component="${1:-crossplane}"
    
    case $component in
        crossplane)
            log_info "Showing Crossplane logs..."
            kubectl logs -n $NAMESPACE_CROSSPLANE -l app=crossplane --tail=50
            ;;
        github-provider)
            log_info "Showing GitHub provider logs..."
            kubectl logs -n $NAMESPACE_CROSSPLANE -l pkg.crossplane.io/provider=github --tail=50
            ;;
        argocd)
            log_info "Showing ArgoCD application controller logs..."
            kubectl logs -n $NAMESPACE_ARGOCD -l app.kubernetes.io/name=argocd-application-controller --tail=50
            ;;
        argocd-server)
            log_info "Showing ArgoCD server logs..."
            kubectl logs -n $NAMESPACE_ARGOCD -l app.kubernetes.io/name=argocd-server --tail=50
            ;;
        *)
            log_error "Unknown component: $component"
            log_info "Available components: crossplane, github-provider, argocd, argocd-server"
            return 1
            ;;
    esac
}

# Validate specific service claim
validate_claim() {
    local claim_name="${1:-}"
    
    if [[ -z "$claim_name" ]]; then
        log_error "Please provide a claim name"
        return 1
    fi
    
    log_info "Validating service claim: $claim_name"
    
    # Check if claim exists
    if ! kubectl get acgsserviceclaim $claim_name -n $NAMESPACE_ACGS &> /dev/null; then
        log_error "Service claim '$claim_name' not found"
        return 1
    fi
    
    # Show claim details
    kubectl describe acgsserviceclaim $claim_name -n $NAMESPACE_ACGS
    
    # Check related resources
    log_info "Checking related GitHub resources..."
    kubectl get repositories.github.upbound.io -l crossplane.io/claim-name=$claim_name 2>/dev/null || log_warning "No repositories found"
    kubectl get repositoryfiles.github.upbound.io -l crossplane.io/claim-name=$claim_name 2>/dev/null || log_warning "No repository files found"
}

# Generate status report
generate_report() {
    local report_file="acgs-gitops-status-$(date +%Y%m%d-%H%M%S).txt"
    
    log_info "Generating status report: $report_file"
    
    {
        echo "ACGS GitOps Status Report"
        echo "Generated: $(date)"
        echo "========================="
        echo
        
        echo "Cluster Information:"
        kubectl cluster-info
        echo
        
        echo "Crossplane Status:"
        kubectl get providers -o wide
        kubectl get functions -o wide
        kubectl get compositions -o wide
        echo
        
        echo "ArgoCD Applications:"
        kubectl get applications -n $NAMESPACE_ARGOCD -o wide
        echo
        
        echo "Service Claims:"
        kubectl get acgsserviceclaims -n $NAMESPACE_ACGS -o wide 2>/dev/null || echo "No service claims found"
        echo
        
        echo "GitHub Resources:"
        kubectl get repositories.github.upbound.io -o wide 2>/dev/null || echo "No repositories found"
        kubectl get repositoryfiles.github.upbound.io -o wide 2>/dev/null || echo "No repository files found"
        echo
        
        echo "Recent Events:"
        kubectl get events --all-namespaces --sort-by=.metadata.creationTimestamp | tail -20
        
    } > $report_file
    
    log_success "Report generated: $report_file"
}

# Main monitoring function
main() {
    log_info "ACGS GitOps Monitoring Dashboard"
    echo "================================="
    
    check_cluster
    echo
    check_crossplane
    echo
    check_argocd
    echo
    check_service_claims
    echo
    check_github_resources
    echo
    check_events
}

# Help function
show_help() {
    echo "ACGS GitOps Monitoring Script"
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  status          - Show overall status (default)"
    echo "  watch           - Watch service claims"
    echo "  logs [component] - Show logs for component"
    echo "  validate [claim] - Validate specific service claim"
    echo "  report          - Generate status report"
    echo "  help            - Show this help"
    echo
    echo "Log components:"
    echo "  crossplane      - Crossplane core logs"
    echo "  github-provider - GitHub provider logs"
    echo "  argocd          - ArgoCD application controller logs"
    echo "  argocd-server   - ArgoCD server logs"
    echo
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 watch"
    echo "  $0 logs github-provider"
    echo "  $0 validate gs-service-demo"
    echo "  $0 report"
}

# Handle script arguments
case "${1:-status}" in
    status)
        main
        ;;
    watch)
        watch_claims
        ;;
    logs)
        show_logs "${2:-crossplane}"
        ;;
    validate)
        validate_claim "${2:-}"
        ;;
    report)
        generate_report
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
