#!/bin/bash
# HPA Validation Script for ACGS-2
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="acgs-system"
KUBECTL_CMD="kubectl"
DRY_RUN=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--dry-run] [--verbose] [--namespace NAMESPACE]"
            echo "  --dry-run    Validate without applying"
            echo "  --verbose    Show detailed output"
            echo "  --namespace  Kubernetes namespace (default: acgs-system)"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v $KUBECTL_CMD &> /dev/null; then
        error "kubectl not found. Please install kubectl."
        exit 1
    fi
    
    # Check cluster connection
    if ! $KUBECTL_CMD cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster."
        exit 1
    fi
    
    # Check namespace
    if ! $KUBECTL_CMD get namespace $NAMESPACE &> /dev/null; then
        warning "Namespace $NAMESPACE does not exist. Creating..."
        if [[ $DRY_RUN == false ]]; then
            $KUBECTL_CMD create namespace $NAMESPACE
        fi
    fi
    
    success "Prerequisites check passed"
}

validate_hpa_syntax() {
    log "Validating HPA YAML syntax..."
    
    local hpa_files=(
        "infrastructure/kubernetes/hpa-vpa.yaml"
        "infrastructure/kubernetes/production/autoscaling/hpa.yaml"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        "infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    )
    
    for file in "${hpa_files[@]}"; do
        if [[ -f "$file" ]]; then
            log "Validating $file..."
            if $KUBECTL_CMD apply --dry-run=client -f "$file" &> /dev/null; then
                success "✓ $file syntax valid"
            else
                error "✗ $file syntax invalid"
                if [[ $VERBOSE == true ]]; then
                    $KUBECTL_CMD apply --dry-run=client -f "$file"
                fi
                return 1
            fi
        else
            warning "File $file not found"
        fi
    done
    
    success "HPA syntax validation completed"
}

check_metrics_server() {
    log "Checking metrics server..."
    
    if $KUBECTL_CMD get deployment metrics-server -n kube-system &> /dev/null; then
        success "Metrics server is deployed"
        
        # Check if metrics server is ready
        local ready=$($KUBECTL_CMD get deployment metrics-server -n kube-system -o jsonpath='{.status.readyReplicas}')
        local replicas=$($KUBECTL_CMD get deployment metrics-server -n kube-system -o jsonpath='{.spec.replicas}')
        
        if [[ "$ready" == "$replicas" ]]; then
            success "Metrics server is ready ($ready/$replicas)"
        else
            warning "Metrics server not fully ready ($ready/$replicas)"
        fi
    else
        warning "Metrics server not found. HPA may not work without it."
    fi
}

apply_hpa_configs() {
    if [[ $DRY_RUN == true ]]; then
        log "Dry run mode - would apply HPA configurations"
        return 0
    fi
    
    log "Applying HPA configurations..."
    
    # Apply enhanced HPA first
    if [[ -f "infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml" ]]; then  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        log "Applying enhanced HPA configuration..."
        $KUBECTL_CMD apply -f "infrastructure/kubernetes/autoscaling/enhanced-hpa-core.yaml"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        success "Enhanced HPA configuration applied"
    fi
    
    # Apply standard HPA
    if [[ -f "infrastructure/kubernetes/hpa-vpa.yaml" ]]; then
        log "Applying standard HPA configuration..."
        $KUBECTL_CMD apply -f "infrastructure/kubernetes/hpa-vpa.yaml"
        success "Standard HPA configuration applied"
    fi
    
    success "HPA configurations applied successfully"
}

validate_hpa_status() {
    log "Validating HPA status..."
    
    local hpa_list=$($KUBECTL_CMD get hpa -n $NAMESPACE -o name)
    
    if [[ -z "$hpa_list" ]]; then
        warning "No HPA resources found in namespace $NAMESPACE"
        return 0
    fi
    
    echo "$hpa_list" | while read -r hpa; do
        local hpa_name=$(echo "$hpa" | cut -d'/' -f2)
        log "Checking HPA: $hpa_name"
        
        # Get HPA details
        local status=$($KUBECTL_CMD get hpa "$hpa_name" -n $NAMESPACE -o jsonpath='{.status.conditions[0].type}')
        local ready=$($KUBECTL_CMD get hpa "$hpa_name" -n $NAMESPACE -o jsonpath='{.status.conditions[0].status}')
        
        if [[ "$status" == "AbleToScale" && "$ready" == "True" ]]; then
            success "✓ $hpa_name is ready"
        else
            warning "⚠ $hpa_name status: $status ($ready)"
        fi
        
        if [[ $VERBOSE == true ]]; then
            $KUBECTL_CMD describe hpa "$hpa_name" -n $NAMESPACE
        fi
    done
}

performance_test() {
    log "Running performance validation..."
    
    # Check for deployment readiness
    local deployments=(
        "constitutional-ai-service"
        "governance-synthesis-service"
        "evolutionary-computation-service"
        "api-gateway-service"
    )
    
    for deployment in "${deployments[@]}"; do
        if $KUBECTL_CMD get deployment "$deployment" -n $NAMESPACE &> /dev/null; then
            local ready=$($KUBECTL_CMD get deployment "$deployment" -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
            local replicas=$($KUBECTL_CMD get deployment "$deployment" -n $NAMESPACE -o jsonpath='{.spec.replicas}')
            
            if [[ "$ready" == "$replicas" && "$ready" -gt 0 ]]; then
                success "✓ $deployment is ready ($ready/$replicas)"
            else
                warning "⚠ $deployment not fully ready ($ready/$replicas)"
            fi
        else
            warning "Deployment $deployment not found"
        fi
    done
}

generate_report() {
    log "Generating HPA validation report..."
    
    local report_file="hpa_validation_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ACGS-2 HPA Validation Report"
        echo "Constitutional Hash: cdd01ef066bc6cf2"
        echo "Generated: $(date)"
        echo "Namespace: $NAMESPACE"
        echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        echo ""
        
        echo "HPA Resources:"
        $KUBECTL_CMD get hpa -n $NAMESPACE -o wide || echo "No HPA resources found"
        echo ""
        
        echo "VPA Resources:"
        $KUBECTL_CMD get vpa -n $NAMESPACE -o wide || echo "No VPA resources found"
        echo ""
        
        echo "Pod Disruption Budgets:"
        $KUBECTL_CMD get pdb -n $NAMESPACE -o wide || echo "No PDB resources found"
        echo ""
        
        echo "Deployment Status:"
        $KUBECTL_CMD get deployments -n $NAMESPACE -o wide
        echo ""
        
        echo "Performance Targets:"
        echo "- P99 Latency: <5ms"
        echo "- Throughput: >100 RPS"
        echo "- Cache Hit Rate: >85%"
        echo "- Constitutional Compliance: 100%"
        
    } > "$report_file"
    
    success "Report generated: $report_file"
}

main() {
    log "Starting ACGS-2 HPA validation..."
    log "Constitutional Hash: cdd01ef066bc6cf2"
    
    check_prerequisites
    validate_hpa_syntax
    check_metrics_server
    
    if [[ $DRY_RUN == false ]]; then
        apply_hpa_configs
        
        # Wait for HPA to initialize
        log "Waiting for HPA initialization..."
        sleep 30
        
        validate_hpa_status
        performance_test
    fi
    
    generate_report
    
    success "HPA validation completed successfully!"
}

# Run main function
main "$@"