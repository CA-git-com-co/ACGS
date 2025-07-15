# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# GitHub Actions Validation Fix Script
# This script helps resolve the remaining validation errors

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

# Check if GitHub token is available
check_github_token() {
    if [ -z "${GITHUB_TOKEN:-}" ]; then
        log_error "GITHUB_TOKEN environment variable is not set"
        log_info "Please set your GitHub token:"
        log_info "export GITHUB_TOKEN=os.environ.get("AUTH_TOKEN")"
        log_info ""
        log_info "You can create a token at: https://github.com/settings/tokens"
        log_info "Required permissions: repo, workflow"
        return 1
    fi
    return 0
}

# Setup GitHub environments
setup_environments() {
    log_info "Setting up GitHub environments..."
    
    if [ ! -f "scripts/setup-github-environments.sh" ]; then
        log_error "Environment setup script not found"
        return 1
    fi
    
    chmod +x scripts/setup-github-environments.sh
    
    if ./scripts/setup-github-environments.sh; then
        log_success "GitHub environments created successfully"
        return 0
    else
        log_error "Failed to create GitHub environments"
        return 1
    fi
}

# Validate workflow files
validate_workflows() {
    log_info "Validating workflow files..."
    
    local validation_errors=0
    
    # Check if workflow files exist
    local workflows=(
        ".github/workflows/deployment-automation.yml"
        ".github/workflows/database-migration.yml"
        ".github/workflows/documentation-automation.yml"
    )
    
    for workflow in "${workflows[@]}"; do
        if [ ! -f "$workflow" ]; then
            log_error "Workflow file not found: $workflow"
            ((validation_errors++))
        else
            log_success "Found workflow: $workflow"
        fi
    done
    
    if [ $validation_errors -eq 0 ]; then
        log_success "All workflow files found"
        return 0
    else
        log_error "Missing workflow files: $validation_errors"
        return 1
    fi
}

# Display manual setup instructions
show_manual_instructions() {
    log_info "Manual setup instructions:"
    echo ""
    echo "1. Configure Repository Secrets (if needed):"
    echo "   - Go to: https://github.com/CA-git-com-co/ACGS/settings/secrets/actions"
    echo "   - Add the following secrets if required:"
    echo "     * DATABASE_URL (for database migration workflows)"
    echo "     * DEV_CLUSTER_URL (for development kubectl access)"
    echo "     * DEV_CLUSTER_TOKEN (for development kubectl access)"
    echo ""
    echo "2. Verify Environment Creation:"
    echo "   - Go to: https://github.com/CA-git-com-co/ACGS/settings/environments"
    echo "   - Verify these environments exist:"
    echo "     * development"
    echo "     * staging"
    echo "     * production"
    echo "     * github-pages"
    echo ""
    echo "3. Test Workflow Execution:"
    echo "   - Go to: https://github.com/CA-git-com-co/ACGS/actions"
    echo "   - Manually trigger a workflow to test environment access"
    echo ""
}

# Main execution
main() {
    log_info "GitHub Actions Validation Fix Script"
    log_info "===================================="
    echo ""
    
    # Validate workflow files first
    if ! validate_workflows; then
        log_error "Workflow validation failed"
        exit 1
    fi
    
    echo ""
    
    # Check GitHub token
    if check_github_token; then
        log_success "GitHub token is available"
        echo ""
        
        # Setup environments
        if setup_environments; then
            log_success "Environment setup completed successfully"
            echo ""
            log_info "✅ All automated fixes have been applied!"
            echo ""
        else
            log_warning "Environment setup failed - manual setup required"
            echo ""
        fi
    else
        log_warning "GitHub token not available - manual setup required"
        echo ""
    fi
    
    # Show manual instructions
    show_manual_instructions
    
    log_success "Validation fix script completed"
    log_info "Check GITHUB_ACTIONS_VALIDATION_FIXES.md for detailed information"
}

# Run main function
main "$@"
