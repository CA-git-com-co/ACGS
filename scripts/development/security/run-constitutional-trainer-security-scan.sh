# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# Constitutional Trainer Security Scanning Script
#
# Comprehensive security scanning for Constitutional Trainer Service including:
# - Container image vulnerability scanning (Trivy/Snyk)
# - Kubernetes manifest security auditing (kube-score/Polaris)
# - Static Application Security Testing (SAST)
# - Security policy validation
#
# Usage:
#   ./run-constitutional-trainer-security-scan.sh [OPTIONS]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESULTS_DIR="${RESULTS_DIR:-./security-scan-results}"
IMAGE_NAME="${IMAGE_NAME:-constitutional-trainer}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
NAMESPACE="${NAMESPACE:-acgs-security-test}"
FAIL_ON_HIGH="${FAIL_ON_HIGH:-true}"
SCAN_TOOLS="${SCAN_TOOLS:-trivy,kube-score,bandit}"

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
Constitutional Trainer Security Scanning

This script performs comprehensive security scanning of the Constitutional Trainer Service
including container images, Kubernetes manifests, and source code.

Usage:
    $0 [OPTIONS]

Options:
    --image-name NAME       Container image name (default: constitutional-trainer)
    --image-tag TAG         Container image tag (default: latest)
    --namespace NAME        Kubernetes namespace (default: acgs-security-test)
    --results-dir DIR       Results output directory (default: ./security-scan-results)
    --tools TOOLS           Comma-separated list of tools: trivy,snyk,kube-score,polaris,bandit (default: trivy,kube-score,bandit)
    --fail-on-high         Fail on high severity vulnerabilities (default: true)
    --skip-build           Skip container image build
    --skip-deploy          Skip Kubernetes deployment
    --help                 Show this help message

Examples:
    # Run all security scans
    $0

    # Run specific tools only
    $0 --tools trivy,bandit

    # Scan existing image without building
    $0 --skip-build --image-name myregistry/constitutional-trainer:v1.0.0

Environment Variables:
    DOCKER_REGISTRY        Container registry for image scanning
    SNYK_TOKEN            Snyk authentication token
    KUBECONFIG            Kubernetes configuration file

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --image-name)
                IMAGE_NAME="$2"
                shift 2
                ;;
            --image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --results-dir)
                RESULTS_DIR="$2"
                shift 2
                ;;
            --tools)
                SCAN_TOOLS="$2"
                shift 2
                ;;
            --fail-on-high)
                FAIL_ON_HIGH="$2"
                shift 2
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-deploy)
                SKIP_DEPLOY=true
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
    log_info "Checking security scanning prerequisites..."
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check required tools based on SCAN_TOOLS
    IFS=',' read -ra TOOLS <<< "$SCAN_TOOLS"
    for tool in "${TOOLS[@]}"; do
        case $tool in
            trivy)
                if ! command -v trivy &> /dev/null; then
                    log_warning "Trivy not found, installing..."
                    install_trivy
                fi
                ;;
            snyk)
                if ! command -v snyk &> /dev/null; then
                    log_warning "Snyk not found, please install: npm install -g snyk"
                fi
                ;;
            kube-score)
                if ! command -v kube-score &> /dev/null; then
                    log_warning "kube-score not found, installing..."
                    install_kube_score
                fi
                ;;
            polaris)
                if ! command -v polaris &> /dev/null; then
                    log_warning "Polaris not found, installing..."
                    install_polaris
                fi
                ;;
            bandit)
                if ! command -v bandit &> /dev/null; then
                    log_warning "Bandit not found, installing..."
                    pip install bandit[toml] || log_warning "Failed to install bandit"
                fi
                ;;
        esac
    done
    
    log_success "Prerequisites check completed"
}

# Install Trivy
install_trivy() {
    log_info "Installing Trivy..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install trivy
    else
        log_error "Unsupported OS for Trivy installation"
        exit 1
    fi
}

# Install kube-score
install_kube_score() {
    log_info "Installing kube-score..."
    
    local version="1.16.1"
    local os="linux"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        os="darwin"
    fi
    
    curl -L "https://github.com/zegl/kube-score/releases/download/v${version}/kube-score_${version}_${os}_amd64.tar.gz" | tar xz
    sudo mv kube-score /usr/local/bin/
}

# Install Polaris
install_polaris() {
    log_info "Installing Polaris..."
    
    local version="8.5.1"
    local os="linux"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        os="darwin"
    fi
    
    curl -L "https://github.com/FairwindsOps/polaris/releases/download/${version}/polaris_${os}_amd64.tar.gz" | tar xz
    sudo mv polaris /usr/local/bin/
}

# Build container image
build_image() {
    if [[ "${SKIP_BUILD:-false}" == "true" ]]; then
        log_info "Skipping container image build"
        return
    fi
    
    log_info "Building Constitutional Trainer container image..."
    
    cd "$PROJECT_ROOT/services/core/constitutional-trainer"
    
    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    
    log_success "Container image built: ${IMAGE_NAME}:${IMAGE_TAG}"
}

# Container vulnerability scanning with Trivy
scan_container_trivy() {
    log_info "🔍 Running Trivy container vulnerability scan..."
    
    local output_file="$RESULTS_DIR/trivy-container-scan.json"
    local report_file="$RESULTS_DIR/trivy-container-report.txt"
    
    # Scan for vulnerabilities
    trivy image \
        --format json \
        --output "$output_file" \
        "${IMAGE_NAME}:${IMAGE_TAG}"
    
    # Generate human-readable report
    trivy image \
        --format table \
        --output "$report_file" \
        "${IMAGE_NAME}:${IMAGE_TAG}"
    
    # Check for high/critical vulnerabilities
    local high_critical_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH" or .Severity == "CRITICAL")] | length' "$output_file" 2>/dev/null || echo "0")
    
    if [[ "$high_critical_count" -gt 0 ]]; then
        log_warning "Found $high_critical_count high/critical vulnerabilities"
        
        if [[ "$FAIL_ON_HIGH" == "true" ]]; then
            log_error "Failing due to high/critical vulnerabilities"
            return 1
        fi
    else
        log_success "No high/critical vulnerabilities found"
    fi
    
    log_success "Trivy scan completed: $output_file"
}

# Container vulnerability scanning with Snyk
scan_container_snyk() {
    if ! command -v snyk &> /dev/null; then
        log_warning "Snyk not available, skipping container scan"
        return
    fi
    
    log_info "🔍 Running Snyk container vulnerability scan..."
    
    local output_file="$RESULTS_DIR/snyk-container-scan.json"
    
    # Authenticate if token is available
    if [[ -n "${SNYK_TOKEN:-}" ]]; then
        snyk auth "$SNYK_TOKEN"
    fi
    
    # Scan container image
    snyk container test "${IMAGE_NAME}:${IMAGE_TAG}" \
        --json \
        --file=Dockerfile > "$output_file" || true
    
    log_success "Snyk container scan completed: $output_file"
}

# Kubernetes manifest security audit with kube-score
audit_k8s_manifests_kube_score() {
    log_info "🔍 Running kube-score Kubernetes manifest audit..."
    
    local output_file="$RESULTS_DIR/kube-score-audit.txt"
    local manifest_dir="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite"
    
    # Find all YAML manifests
    local manifests=()
    while IFS= read -r -d '' file; do
        manifests+=("$file")
    done < <(find "$manifest_dir" -name "*.yaml" -print0)
    
    if [[ ${#manifests[@]} -eq 0 ]]; then
        log_warning "No Kubernetes manifests found in $manifest_dir"
        return
    fi
    
    # Run kube-score on all manifests
    {
        echo "# Kubernetes Manifest Security Audit - kube-score"
        echo "Generated: $(date)"
        echo ""
        
        for manifest in "${manifests[@]}"; do
            echo "## $(basename "$manifest")"
            echo ""
            kube-score score "$manifest" || true
            echo ""
        done
    } > "$output_file"
    
    log_success "kube-score audit completed: $output_file"
}

# Kubernetes manifest security audit with Polaris
audit_k8s_manifests_polaris() {
    if ! command -v polaris &> /dev/null; then
        log_warning "Polaris not available, skipping K8s manifest audit"
        return
    fi
    
    log_info "🔍 Running Polaris Kubernetes manifest audit..."
    
    local output_file="$RESULTS_DIR/polaris-audit.json"
    local manifest_dir="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite"
    
    # Run Polaris audit
    polaris audit \
        --audit-path "$manifest_dir" \
        --format json \
        --output-file "$output_file"
    
    # Generate summary
    local summary_file="$RESULTS_DIR/polaris-summary.txt"
    {
        echo "# Polaris Security Audit Summary"
        echo "Generated: $(date)"
        echo ""
        
        local total_checks=$(jq '.AuditResults | length' "$output_file")
        local passed_checks=$(jq '[.AuditResults[] | select(.Results.Totals.Successes > 0)] | length' "$output_file")
        local failed_checks=$(jq '[.AuditResults[] | select(.Results.Totals.Errors > 0)] | length' "$output_file")
        
        echo "Total Checks: $total_checks"
        echo "Passed: $passed_checks"
        echo "Failed: $failed_checks"
        echo ""
        
        # List failed checks
        if [[ "$failed_checks" -gt 0 ]]; then
            echo "Failed Checks:"
            jq -r '.AuditResults[] | select(.Results.Totals.Errors > 0) | "- \(.Name): \(.Results.Totals.Errors) errors"' "$output_file"
        fi
    } > "$summary_file"
    
    log_success "Polaris audit completed: $output_file"
}

# Static Application Security Testing with Bandit
run_sast_bandit() {
    if ! command -v bandit &> /dev/null; then
        log_warning "Bandit not available, skipping SAST"
        return
    fi
    
    log_info "🔍 Running Bandit SAST scan..."
    
    local output_file="$RESULTS_DIR/bandit-sast.json"
    local report_file="$RESULTS_DIR/bandit-report.txt"
    local source_dir="$PROJECT_ROOT/services/core/constitutional-trainer"
    
    # Run Bandit scan
    bandit -r "$source_dir" \
        -f json \
        -o "$output_file" \
        --skip B101,B601 || true  # Skip assert and shell injection (common false positives)
    
    # Generate human-readable report
    bandit -r "$source_dir" \
        -f txt \
        -o "$report_file" \
        --skip B101,B601 || true
    
    # Check for high/medium severity issues
    local high_issues=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' "$output_file" 2>/dev/null || echo "0")
    local medium_issues=$(jq '[.results[] | select(.issue_severity == "MEDIUM")] | length' "$output_file" 2>/dev/null || echo "0")
    
    if [[ "$high_issues" -gt 0 ]]; then
        log_warning "Found $high_issues high severity security issues"
    fi
    
    if [[ "$medium_issues" -gt 0 ]]; then
        log_warning "Found $medium_issues medium severity security issues"
    fi
    
    log_success "Bandit SAST scan completed: $output_file"
}

# Validate security policies
validate_security_policies() {
    log_info "🔍 Validating security policies..."
    
    local policy_file="$RESULTS_DIR/security-policy-validation.txt"
    local manifest_dir="$PROJECT_ROOT/infrastructure/kubernetes/acgs-lite"

    # Change to project root to ensure relative paths work
    cd "$PROJECT_ROOT"
    
    {
        echo "# Security Policy Validation"
        echo "Generated: $(date)"
        echo ""
        
        # Check for PodSecurityContext
        echo "## PodSecurityContext Validation"
        if grep -r "runAsNonRoot: true" "$manifest_dir" &>/dev/null; then
            echo "✅ runAsNonRoot: true found in manifests"
        else
            echo "❌ runAsNonRoot: true not found in manifests"
        fi
        
        if grep -r "readOnlyRootFilesystem: true" "$manifest_dir" &>/dev/null; then
            echo "✅ readOnlyRootFilesystem: true found in manifests"
        else
            echo "⚠️ readOnlyRootFilesystem: true not found in manifests"
        fi
        
        # Check for NetworkPolicy
        echo ""
        echo "## NetworkPolicy Validation"
        if find "$manifest_dir" -name "*network-policy*" -o -name "*networkpolicy*" | grep -q .; then
            echo "✅ NetworkPolicy manifests found"
        else
            echo "❌ No NetworkPolicy manifests found"
        fi
        
        # Check for resource limits
        echo ""
        echo "## Resource Limits Validation"

        # Check for CPU limits
        local cpu_limits_count=$(grep -A 5 -r "limits:" "$manifest_dir" | grep "cpu:" | wc -l)
        if [[ "$cpu_limits_count" -gt 0 ]]; then
            echo "✅ CPU limits found in manifests ($cpu_limits_count instances)"
        else
            echo "❌ No CPU limits found in manifests"
        fi

        # Check for memory limits
        local memory_limits_count=$(grep -A 5 -r "limits:" "$manifest_dir" | grep "memory:" | wc -l)
        if [[ "$memory_limits_count" -gt 0 ]]; then
            echo "✅ Memory limits found in manifests ($memory_limits_count instances)"
        else
            echo "❌ No memory limits found in manifests"
        fi

        # Check for resource requests
        local requests_count=$(grep -A 5 -r "requests:" "$manifest_dir" | grep -E "cpu:|memory:" | wc -l)
        if [[ "$requests_count" -gt 0 ]]; then
            echo "✅ Resource requests found in manifests ($requests_count instances)"
        else
            echo "❌ No resource requests found in manifests"
        fi

        # Detailed resource validation for key services
        echo ""
        echo "### Service-Specific Resource Validation"

        # Constitutional Trainer
        if grep -A 15 "name: constitutional-trainer" "$manifest_dir"/*.yaml | grep -A 10 "resources:" | grep -q "cpu.*500m"; then
            echo "✅ Constitutional Trainer has appropriate CPU requests (500m)"
        else
            echo "⚠️ Constitutional Trainer CPU requests may need adjustment"
        fi

        if grep -A 15 "name: constitutional-trainer" "$manifest_dir"/*.yaml | grep -A 10 "resources:" | grep -q "memory.*2Gi"; then
            echo "✅ Constitutional Trainer has appropriate memory requests (2Gi)"
        else
            echo "⚠️ Constitutional Trainer memory requests may need adjustment"
        fi

        if grep -A 15 "name: constitutional-trainer" "$manifest_dir"/*.yaml | grep -A 10 "resources:" | grep -q "nvidia.com/gpu.*1"; then
            echo "✅ Constitutional Trainer has GPU allocation (1 GPU)"
        else
            echo "⚠️ Constitutional Trainer GPU allocation may need adjustment"
        fi

        # Policy Engine
        if grep -A 15 "name: policy-engine" "$manifest_dir"/*.yaml | grep -A 10 "resources:" | grep -q "cpu.*150m"; then
            echo "✅ Policy Engine has appropriate CPU requests (150m)"
        else
            echo "⚠️ Policy Engine CPU requests may need adjustment"
        fi

        # Redis
        if grep -A 15 "name: redis" "$manifest_dir"/*.yaml | grep -A 10 "resources:" | grep -q "cpu.*100m"; then
            echo "✅ Redis has appropriate CPU requests (100m)"
        else
            echo "⚠️ Redis CPU requests may need adjustment"
        fi

        # Audit Engine
        if grep -A 15 "name: audit-engine" "$manifest_dir"/*.yaml | grep -A 10 "resources:" | grep -q "cpu.*150m"; then
            echo "✅ Audit Engine has appropriate CPU requests (150m)"
        else
            echo "⚠️ Audit Engine CPU requests may need adjustment"
        fi
        
        # Check for security annotations
        echo ""
        echo "## Security Annotations"
        if grep -r "seccomp" "$manifest_dir" &>/dev/null; then
            echo "✅ Seccomp annotations found"
        else
            echo "⚠️ No seccomp annotations found"
        fi
        
    } > "$policy_file"
    
    log_success "Security policy validation completed: $policy_file"
}

# Generate comprehensive security report
generate_security_report() {
    log_info "📊 Generating comprehensive security report..."
    
    local report_file="$RESULTS_DIR/security-scan-summary-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# Constitutional Trainer Security Scan Report

**Generated:** $(date)  
**Image:** ${IMAGE_NAME}:${IMAGE_TAG}  
**Namespace:** $NAMESPACE  
**Scan Tools:** $SCAN_TOOLS  

## Executive Summary

This report contains the results of comprehensive security scanning for the Constitutional Trainer Service,
including container vulnerability scanning, Kubernetes manifest auditing, and static application security testing.

## Scan Results

EOF

    # Add container scan results
    if [[ -f "$RESULTS_DIR/trivy-container-scan.json" ]]; then
        local total_vulns=$(jq '[.Results[]?.Vulnerabilities[]?] | length' "$RESULTS_DIR/trivy-container-scan.json" 2>/dev/null || echo "0")
        local critical_vulns=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$RESULTS_DIR/trivy-container-scan.json" 2>/dev/null || echo "0")
        local high_vulns=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$RESULTS_DIR/trivy-container-scan.json" 2>/dev/null || echo "0")
        
        cat >> "$report_file" << EOF
### Container Vulnerability Scan (Trivy)

| Severity | Count |
|----------|-------|
| Critical | $critical_vulns |
| High | $high_vulns |
| Total | $total_vulns |

EOF
    fi
    
    # Add SAST results
    if [[ -f "$RESULTS_DIR/bandit-sast.json" ]]; then
        local high_issues=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' "$RESULTS_DIR/bandit-sast.json" 2>/dev/null || echo "0")
        local medium_issues=$(jq '[.results[] | select(.issue_severity == "MEDIUM")] | length' "$RESULTS_DIR/bandit-sast.json" 2>/dev/null || echo "0")
        local low_issues=$(jq '[.results[] | select(.issue_severity == "LOW")] | length' "$RESULTS_DIR/bandit-sast.json" 2>/dev/null || echo "0")
        
        cat >> "$report_file" << EOF
### Static Application Security Testing (Bandit)

| Severity | Count |
|----------|-------|
| High | $high_issues |
| Medium | $medium_issues |
| Low | $low_issues |

EOF
    fi
    
    cat >> "$report_file" << EOF
## Detailed Reports

- Container Vulnerability Scan: \`trivy-container-scan.json\`
- Kubernetes Manifest Audit: \`kube-score-audit.txt\`
- Static Application Security Testing: \`bandit-sast.json\`
- Security Policy Validation: \`security-policy-validation.txt\`

## Recommendations

1. **Address High/Critical Vulnerabilities**: Review and remediate all high and critical severity vulnerabilities found in container images.

2. **Implement Security Policies**: Ensure all Kubernetes manifests include proper security contexts, resource limits, and network policies.

3. **Code Security**: Address any high or medium severity issues found in static analysis.

4. **Regular Scanning**: Integrate security scanning into CI/CD pipeline for continuous monitoring.

## Next Steps

1. Review detailed scan reports
2. Create remediation plan for identified issues
3. Implement security fixes
4. Re-run security scans to validate fixes
5. Update security policies and procedures

EOF

    log_success "Security report generated: $report_file"
}

# Main execution
main() {
    log_info "🔒 Constitutional Trainer Security Scanning"
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    parse_args "$@"
    check_prerequisites
    build_image
    
    # Run security scans based on selected tools
    IFS=',' read -ra TOOLS <<< "$SCAN_TOOLS"
    for tool in "${TOOLS[@]}"; do
        case $tool in
            trivy)
                scan_container_trivy
                ;;
            snyk)
                scan_container_snyk
                ;;
            kube-score)
                audit_k8s_manifests_kube_score
                ;;
            polaris)
                audit_k8s_manifests_polaris
                ;;
            bandit)
                run_sast_bandit
                ;;
            *)
                log_warning "Unknown tool: $tool"
                ;;
        esac
    done
    
    # Always run security policy validation
    validate_security_policies
    
    # Generate comprehensive report
    generate_security_report
    
    log_success "✅ Security scanning completed successfully!"
    echo ""
    echo "📊 Results available in: $RESULTS_DIR"
    echo "📄 Summary report: $RESULTS_DIR/security-scan-summary-*.md"
    echo ""
}

# Execute main function
main "$@"
