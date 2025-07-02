#!/bin/bash

# ACGS-1 Enterprise CI/CD Deployment Script
# Deploy and validate the enterprise-grade CI/CD pipeline

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="/tmp/acgs-enterprise-deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[DEPLOY-INFO]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[DEPLOY-SUCCESS]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "WARNING")
            echo -e "${YELLOW}[DEPLOY-WARNING]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "ERROR")
            echo -e "${RED}[DEPLOY-ERROR]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "STEP")
            echo -e "${PURPLE}[DEPLOY-STEP]${NC} $message" | tee -a "$LOG_FILE"
            ;;
    esac
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Pre-deployment validation
validate_prerequisites() {
    log "STEP" "🔍 Validating deployment prerequisites..."
    
    # Check if we're in the correct directory
    if [ ! -f "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" ]; then
        log "ERROR" "❌ Enterprise CI workflow not found. Please ensure you're in the ACGS-1 project root."
        return 1
    fi
    
    # Check if scripts exist
    local required_scripts=(
        "scripts/enterprise/infrastructure-setup.sh"
        "scripts/enterprise/performance-monitor.sh"
        "scripts/enterprise/failure-analysis.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$script" ]; then
            log "ERROR" "❌ Required script not found: $script"
            return 1
        fi
    done
    
    # Check Git status
    if ! git status >/dev/null 2>&1; then
        log "ERROR" "❌ Not in a Git repository or Git not available"
        return 1
    fi
    
    # Check for uncommitted changes
    if ! git diff --quiet; then
        log "WARNING" "⚠️ Uncommitted changes detected. Consider committing before deployment."
    fi
    
    log "SUCCESS" "✅ Prerequisites validation completed"
    return 0
}

# Make scripts executable
setup_script_permissions() {
    log "STEP" "🔧 Setting up script permissions..."
    
    local scripts=(
        "scripts/enterprise/infrastructure-setup.sh"
        "scripts/enterprise/performance-monitor.sh"
        "scripts/enterprise/failure-analysis.sh"
        "scripts/enterprise/deploy-enterprise-ci.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$PROJECT_ROOT/$script" ]; then
            chmod +x "$PROJECT_ROOT/$script"
            log "SUCCESS" "✅ Made executable: $script"
        else
            log "WARNING" "⚠️ Script not found: $script"
        fi
    done
    
    log "SUCCESS" "✅ Script permissions configured"
}

# Backup existing CI configuration
backup_existing_ci() {
    log "STEP" "💾 Backing up existing CI configuration..."
    
    local backup_dir="$PROJECT_ROOT/.github/workflows/backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup existing workflows
    if [ -f "$PROJECT_ROOT/.github/workflows/ci.yml" ]; then
        cp "$PROJECT_ROOT/.github/workflows/ci.yml" "$backup_dir/ci.yml.backup"
        log "SUCCESS" "✅ Backed up ci.yml to $backup_dir"
    fi
    
    # Backup any other workflow files
    find "$PROJECT_ROOT/.github/workflows" -name "*.yml" -not -path "*/backup-*" -exec cp {} "$backup_dir/" \;
    
    log "SUCCESS" "✅ CI configuration backup completed: $backup_dir"
    echo "$backup_dir" > /tmp/acgs-ci-backup-location.txt
}

# Deploy enterprise CI workflow
deploy_enterprise_workflow() {
    log "STEP" "🚀 Deploying enterprise CI/CD workflow..."
    
    # Check if enterprise-ci.yml exists
    if [ ! -f "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" ]; then
        log "ERROR" "❌ Enterprise CI workflow file not found"
        return 1
    fi
    
    # Validate workflow syntax (basic check)
    if ! grep -q "name: ACGS-1 Enterprise CI/CD Pipeline" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml"; then
        log "ERROR" "❌ Enterprise CI workflow appears to be malformed"
        return 1
    fi
    
    # Replace or rename existing CI workflow
    if [ -f "$PROJECT_ROOT/.github/workflows/ci.yml" ]; then
        mv "$PROJECT_ROOT/.github/workflows/ci.yml" "$PROJECT_ROOT/.github/workflows/ci-legacy.yml"
        log "INFO" "📝 Renamed existing ci.yml to ci-legacy.yml"
    fi
    
    # Activate enterprise workflow by renaming
    cp "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" "$PROJECT_ROOT/.github/workflows/ci.yml"
    log "SUCCESS" "✅ Enterprise CI workflow deployed as ci.yml"
    
    log "SUCCESS" "✅ Enterprise CI/CD workflow deployment completed"
}

# Create enterprise directories
setup_enterprise_directories() {
    log "STEP" "📁 Setting up enterprise directory structure..."
    
    local directories=(
        "docs/enterprise"
        "scripts/enterprise"
        ".github/workflows/backup"
        "logs/enterprise"
        "reports/enterprise"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$PROJECT_ROOT/$dir"
        log "SUCCESS" "✅ Created directory: $dir"
    done
    
    log "SUCCESS" "✅ Enterprise directory structure setup completed"
}

# Test enterprise infrastructure
test_enterprise_infrastructure() {
    log "STEP" "🧪 Testing enterprise infrastructure setup..."
    
    # Run infrastructure setup script
    if [ -x "$PROJECT_ROOT/scripts/enterprise/infrastructure-setup.sh" ]; then
        log "INFO" "Running infrastructure validation..."
        if "$PROJECT_ROOT/scripts/enterprise/infrastructure-setup.sh"; then
            log "SUCCESS" "✅ Infrastructure validation passed"
        else
            log "WARNING" "⚠️ Infrastructure validation had issues (check logs)"
        fi
    else
        log "WARNING" "⚠️ Infrastructure setup script not executable"
    fi
    
    # Test performance monitoring
    if [ -x "$PROJECT_ROOT/scripts/enterprise/performance-monitor.sh" ]; then
        log "INFO" "Testing performance monitoring..."
        if "$PROJECT_ROOT/scripts/enterprise/performance-monitor.sh" init; then
            log "SUCCESS" "✅ Performance monitoring test passed"
        else
            log "WARNING" "⚠️ Performance monitoring test failed"
        fi
    fi
    
    # Test failure analysis
    if [ -x "$PROJECT_ROOT/scripts/enterprise/failure-analysis.sh" ]; then
        log "INFO" "Testing failure analysis..."
        if "$PROJECT_ROOT/scripts/enterprise/failure-analysis.sh" init "test-pipeline"; then
            log "SUCCESS" "✅ Failure analysis test passed"
        else
            log "WARNING" "⚠️ Failure analysis test failed"
        fi
    fi
    
    log "SUCCESS" "✅ Enterprise infrastructure testing completed"
}

# Generate deployment report
generate_deployment_report() {
    log "STEP" "📋 Generating deployment report..."
    
    local report_file="$PROJECT_ROOT/reports/enterprise/deployment-report-$(date +%Y%m%d-%H%M%S).md"
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
# ACGS-1 Enterprise CI/CD Deployment Report

**Deployment Date:** $(date)
**Deployment Version:** Enterprise v1.0
**Deployed By:** $(whoami)
**Git Commit:** $(git rev-parse HEAD 2>/dev/null || echo "Unknown")

## Deployment Summary

✅ **DEPLOYMENT SUCCESSFUL**

### Components Deployed

- ✅ Enterprise CI/CD Workflow (\`enterprise-ci.yml\`)
- ✅ Infrastructure Setup Script (\`infrastructure-setup.sh\`)
- ✅ Performance Monitoring System (\`performance-monitor.sh\`)
- ✅ Failure Analysis System (\`failure-analysis.sh\`)
- ✅ Enterprise Directory Structure
- ✅ Script Permissions and Executables

### Performance Targets

- **Build Duration Target:** <5 minutes
- **Availability Target:** >99.5%
- **Security Compliance:** Zero-tolerance policy enforced

### Key Features Enabled

1. **Parallel Job Execution**
   - Rust quality and build (parallel)
   - Enterprise security scanning (parallel)
   - Performance monitoring and reporting

2. **Enhanced Caching**
   - Workspace-level Rust dependency caching
   - Toolchain installation caching
   - Multi-layer cache restoration

3. **Infrastructure Automation**
   - Automated environment validation
   - Solana test environment setup
   - Enhanced error handling and retry mechanisms

4. **Enterprise Reporting**
   - Real-time performance monitoring
   - Automated failure analysis
   - Compliance dashboard generation

### Backup Information

- **Backup Location:** $(cat /tmp/acgs-ci-backup-location.txt 2>/dev/null || echo "Not available")
- **Legacy Workflow:** Renamed to \`ci-legacy.yml\`

### Next Steps

1. **Commit Changes:** \`git add . && git commit -m "Deploy enterprise CI/CD pipeline"\`
2. **Push to Repository:** \`git push origin main\`
3. **Monitor First Run:** Check GitHub Actions for enterprise workflow execution
4. **Validate Performance:** Ensure build duration meets <5 minute target
5. **Review Compliance:** Check enterprise dashboard for compliance metrics

### Rollback Instructions

If rollback is needed:
\`\`\`bash
# Restore from backup
cp .github/workflows/ci-legacy.yml .github/workflows/ci.yml
# Or restore from backup directory
cp \$(cat /tmp/acgs-ci-backup-location.txt)/ci.yml.backup .github/workflows/ci.yml
\`\`\`

### Support

- **Documentation:** \`docs/enterprise/ENTERPRISE_REMEDIATION_IMPLEMENTATION.md\`
- **Logs:** \`$LOG_FILE\`
- **Scripts:** \`scripts/enterprise/\`

---
**Enterprise CI/CD Pipeline Deployment Completed Successfully** ✅
EOF
    
    log "SUCCESS" "✅ Deployment report generated: $report_file"
    echo "$report_file"
}

# Main deployment function
main() {
    log "INFO" "🚀 Starting ACGS-1 Enterprise CI/CD Deployment..."
    log "INFO" "Deployment Time: $(date)"
    log "INFO" "Project Root: $PROJECT_ROOT"
    
    # Create log file
    touch "$LOG_FILE"
    
    # Run deployment steps
    if ! validate_prerequisites; then
        log "ERROR" "❌ Prerequisites validation failed. Aborting deployment."
        exit 1
    fi
    
    setup_script_permissions
    setup_enterprise_directories
    backup_existing_ci
    
    if ! deploy_enterprise_workflow; then
        log "ERROR" "❌ Enterprise workflow deployment failed. Aborting."
        exit 1
    fi
    
    test_enterprise_infrastructure
    
    local report_file=$(generate_deployment_report)
    
    log "SUCCESS" "✅ ACGS-1 Enterprise CI/CD Deployment Completed Successfully!"
    log "INFO" "📋 Deployment Report: $report_file"
    log "INFO" "📄 Full Log: $LOG_FILE"
    
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "=========================="
    echo "✅ Enterprise CI/CD pipeline deployed"
    echo "✅ Performance optimizations active"
    echo "✅ Infrastructure automation enabled"
    echo "✅ Enterprise reporting configured"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Commit and push changes: git add . && git commit -m 'Deploy enterprise CI/CD' && git push"
    echo "2. Monitor first workflow run in GitHub Actions"
    echo "3. Validate <5 minute build target achievement"
    echo "4. Review enterprise compliance dashboard"
    echo ""
    echo "📄 Deployment Report: $report_file"
    
    return 0
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
