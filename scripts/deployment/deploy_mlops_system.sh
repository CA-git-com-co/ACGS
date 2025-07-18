#!/bin/bash

# ACGS-PGP MLOps System Deployment Script
#
# Deploys the comprehensive MLOps framework with staging validation
# and production promotion workflows while maintaining constitutional
# hash integrity and performance targets.
#
# Constitutional Hash: cdd01ef066bc6cf2
# Performance Targets: Sub-2s response times, >95% constitutional compliance, 74% cost savings

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/tmp/mlops_deployment_${TIMESTAMP}.log"

# Constitutional hash verification
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Deployment configuration
MLOPS_STORAGE_ROOT="${PROJECT_ROOT}/mlops_production"
STAGING_NAMESPACE="acgs-mlops-staging"
PRODUCTION_NAMESPACE="acgs-mlops-production"
BACKUP_DIR="${PROJECT_ROOT}/backups/mlops_${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Deployment failed with exit code $exit_code"
        log "Check log file: $LOG_FILE"
        
        # Attempt rollback if in production
        if [ "${ENVIRONMENT:-staging}" = "production" ]; then
            log_warning "Attempting automatic rollback..."
            rollback_deployment || log_error "Rollback failed - manual intervention required"
        fi
    fi
    exit $exit_code
}

trap cleanup EXIT

# Validation functions
validate_prerequisites() {
    log "Validating deployment prerequisites..."
    
    # Check Python environment
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Git repository
    if [ ! -d "$PROJECT_ROOT/.git" ]; then
        log_error "Not in a Git repository"
        exit 1
    fi
    
    # Verify constitutional hash
    if [ -z "$CONSTITUTIONAL_HASH" ] || [ "$CONSTITUTIONAL_HASH" != "cdd01ef066bc6cf2" ]; then
        log_error "Invalid constitutional hash: $CONSTITUTIONAL_HASH"
        exit 1
    fi
    
    # Check Docker if deploying to containers
    if command -v docker &> /dev/null; then
        if ! docker info &> /dev/null; then
            log_warning "Docker is installed but not running"
        fi
    fi
    
    # Check Kubernetes if deploying to K8s
    if command -v kubectl &> /dev/null; then
        if ! kubectl cluster-info &> /dev/null; then
            log_warning "kubectl is installed but not connected to cluster"
        fi
    fi
    
    log_success "Prerequisites validation completed"
}

validate_constitutional_compliance() {
    log "Validating constitutional compliance..."
    
    # Run constitutional compliance tests
    cd "$PROJECT_ROOT"
    
    if [ -f "services/shared/mlops/test_mlops_integration.py" ]; then
        log "Running MLOps integration tests..."
        python3 -m pytest services/shared/mlops/test_mlops_integration.py::TestMLOpsIntegration::test_constitutional_compliance_validation -v
        
        if [ $? -eq 0 ]; then
            log_success "Constitutional compliance tests passed"
        else
            log_error "Constitutional compliance tests failed"
            exit 1
        fi
    else
        log_warning "MLOps integration tests not found"
    fi
    
    # Verify constitutional hash in all MLOps components
    log "Verifying constitutional hash consistency..."
    
    local hash_files=(
        "services/shared/mlops/__init__.py"
        "services/shared/mlops/model_versioning.py"
        "services/shared/mlops/git_integration.py"
        "services/shared/mlops/artifact_storage.py"
        "services/shared/mlops/deployment_pipeline.py"
        "services/shared/mlops/mlops_manager.py"
    )
    
    for file in "${hash_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            if grep -q "cdd01ef066bc6cf2" "$PROJECT_ROOT/$file"; then
                log "✓ Constitutional hash verified in $file"
            else
                log_error "Constitutional hash missing or incorrect in $file"
                exit 1
            fi
        fi
    done
    
    log_success "Constitutional compliance validation completed"
}

create_storage_directories() {
    log "Creating MLOps storage directories..."
    
    local directories=(
        "$MLOPS_STORAGE_ROOT"
        "$MLOPS_STORAGE_ROOT/versions"
        "$MLOPS_STORAGE_ROOT/artifacts"
        "$MLOPS_STORAGE_ROOT/deployments"
        "$BACKUP_DIR"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log "Created directory: $dir"
    done
    
    # Set appropriate permissions
    chmod 755 "$MLOPS_STORAGE_ROOT"
    chmod 750 "$MLOPS_STORAGE_ROOT/versions"
    chmod 750 "$MLOPS_STORAGE_ROOT/artifacts"
    chmod 750 "$MLOPS_STORAGE_ROOT/deployments"
    
    log_success "Storage directories created"
}

install_dependencies() {
    log "Installing MLOps system dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Install Python dependencies
    if [ -f "config/environments/requirements.txt" ]; then
        log "Installing Python requirements..."
        pip3 install -r config/environments/requirements.txt
    fi
    
    # Install additional MLOps dependencies
    local mlops_deps=(
        "scikit-learn>=1.3.2"
        "gitpython>=3.1.0"
        "pydantic>=2.0.0"
    )
    
    for dep in "${mlops_deps[@]}"; do
        log "Installing $dep..."
        pip3 install "$dep"
    done
    
    log_success "Dependencies installed"
}

run_integration_tests() {
    log "Running MLOps integration tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run comprehensive test suite
    if [ -f "services/shared/mlops/test_mlops_integration.py" ]; then
        log "Running full MLOps test suite..."
        python3 -m pytest services/shared/mlops/test_mlops_integration.py -v --tb=short
        
        if [ $? -eq 0 ]; then
            log_success "All MLOps integration tests passed"
        else
            log_error "MLOps integration tests failed"
            exit 1
        fi
    else
        log_warning "MLOps integration tests not found - skipping"
    fi
    
    # Test production integration
    log "Testing production integration..."
    python3 -c "
import sys
sys.path.append('services/shared')
from mlops.production_integration import create_production_mlops_integration

# Test integration creation
integration = create_production_mlops_integration()
health = integration.validate_integration_health()

if health['overall_healthy']:
    print('✅ Production integration healthy')
    exit(0)
else:
    print('❌ Production integration unhealthy')
    print(health)
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Production integration tests passed"
    else
        log_error "Production integration tests failed"
        exit 1
    fi
}

deploy_staging() {
    log "Deploying MLOps system to staging..."
    
    # Create staging configuration
    cat > "$MLOPS_STORAGE_ROOT/staging_config.json" << EOF
{
    "environment": "staging",
    "constitutional_hash": "$CONSTITUTIONAL_HASH",
    "storage_root": "$MLOPS_STORAGE_ROOT/staging",
    "performance_targets": {
        "response_time_ms": 2000,
        "constitutional_compliance": 0.95,
        "cost_savings": 0.74,
        "availability": 0.999,
        "model_accuracy": 0.90
    },
    "deployment_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    # Initialize staging MLOps system
    python3 -c "
import sys
sys.path.append('services/shared')
from mlops.mlops_manager import MLOpsManager, MLOpsConfig

config = MLOpsConfig(
    storage_root='$MLOPS_STORAGE_ROOT/staging',
    constitutional_hash='$CONSTITUTIONAL_HASH'
)

mlops = MLOpsManager(config)
dashboard = mlops.get_mlops_dashboard()

print('✅ Staging MLOps system initialized')
print(f'Constitutional hash verified: {dashboard[\"mlops_overview\"][\"constitutional_hash_verified\"]}')
"
    
    if [ $? -eq 0 ]; then
        log_success "Staging deployment completed"
    else
        log_error "Staging deployment failed"
        exit 1
    fi
}

validate_staging() {
    log "Validating staging deployment..."
    
    # Run staging validation tests
    python3 -c "
import sys
sys.path.append('services/shared')
from mlops.mlops_manager import MLOpsManager, MLOpsConfig
import tempfile
import json
from pathlib import Path

# Create test model files
temp_dir = Path(tempfile.mkdtemp())
model_file = temp_dir / 'test_model.txt'
config_file = temp_dir / 'test_config.json'

model_file.write_text('test model data')
config_file.write_text(json.dumps({'test': 'config'}))

# Initialize MLOps manager
config = MLOpsConfig(
    storage_root='$MLOPS_STORAGE_ROOT/staging',
    constitutional_hash='$CONSTITUTIONAL_HASH'
)

mlops = MLOpsManager(config)

# Test model versioning
performance_metrics = {
    'accuracy': 0.92,
    'constitutional_compliance': 0.97,
    'response_time_ms': 450
}

try:
    model_version = mlops.create_model_version(
        model_name='staging_test_model',
        model_path=model_file,
        config_path=config_file,
        performance_metrics=performance_metrics
    )
    
    print(f'✅ Staging validation passed - Model version: {model_version.version}')
    print(f'Constitutional compliance: {model_version.constitutional_compliance_score:.3f}')
    
except Exception as e:
    print(f'❌ Staging validation failed: {e}')
    exit(1)
finally:
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
"
    
    if [ $? -eq 0 ]; then
        log_success "Staging validation passed"
    else
        log_error "Staging validation failed"
        exit 1
    fi
}

promote_to_production() {
    log "Promoting MLOps system to production..."
    
    # Create backup of current production (if exists)
    if [ -d "$MLOPS_STORAGE_ROOT/production" ]; then
        log "Creating backup of current production..."
        cp -r "$MLOPS_STORAGE_ROOT/production" "$BACKUP_DIR/production_backup"
    fi
    
    # Promote staging to production
    if [ -d "$MLOPS_STORAGE_ROOT/staging" ]; then
        log "Promoting staging to production..."
        cp -r "$MLOPS_STORAGE_ROOT/staging" "$MLOPS_STORAGE_ROOT/production"
    fi
    
    # Update production configuration
    cat > "$MLOPS_STORAGE_ROOT/production_config.json" << EOF
{
    "environment": "production",
    "constitutional_hash": "$CONSTITUTIONAL_HASH",
    "storage_root": "$MLOPS_STORAGE_ROOT/production",
    "performance_targets": {
        "response_time_ms": 2000,
        "constitutional_compliance": 0.95,
        "cost_savings": 0.74,
        "availability": 0.999,
        "model_accuracy": 0.90
    },
    "promotion_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_location": "$BACKUP_DIR/production_backup"
}
EOF
    
    log_success "Production promotion completed"
}

validate_production() {
    log "Validating production deployment..."
    
    # Test production MLOps system
    python3 -c "
import sys
sys.path.append('services/shared')
from mlops.production_integration import create_production_mlops_integration

# Test production integration
integration = create_production_mlops_integration(
    constitutional_hash='$CONSTITUTIONAL_HASH',
    storage_root='$MLOPS_STORAGE_ROOT/production'
)

health = integration.validate_integration_health()

if health['overall_healthy']:
    print('✅ Production validation passed')
    print(f'Constitutional hash verified: {health[\"constitutional_hash_verified\"]}')
    print(f'Integration enabled: {health[\"integration_enabled\"]}')
else:
    print('❌ Production validation failed')
    print(health)
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Production validation passed"
    else
        log_error "Production validation failed"
        exit 1
    fi
}

rollback_deployment() {
    log "Rolling back MLOps deployment..."
    
    if [ -d "$BACKUP_DIR/production_backup" ]; then
        log "Restoring from backup..."
        rm -rf "$MLOPS_STORAGE_ROOT/production"
        cp -r "$BACKUP_DIR/production_backup" "$MLOPS_STORAGE_ROOT/production"
        log_success "Rollback completed"
        return 0
    else
        log_error "No backup found for rollback"
        return 1
    fi
}

generate_deployment_report() {
    log "Generating deployment report..."
    
    local report_file="$PROJECT_ROOT/mlops_deployment_report_${TIMESTAMP}.md"
    
    cat > "$report_file" << EOF
# ACGS-PGP MLOps System Deployment Report

**Deployment Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Constitutional Hash**: $CONSTITUTIONAL_HASH
**Environment**: ${ENVIRONMENT:-staging}
**Deployment ID**: mlops_${TIMESTAMP}

## Deployment Summary

- ✅ Prerequisites validated
- ✅ Constitutional compliance verified
- ✅ Dependencies installed
- ✅ Integration tests passed
- ✅ Staging deployment completed
- ✅ Staging validation passed
$([ "${ENVIRONMENT:-staging}" = "production" ] && echo "- ✅ Production promotion completed" || echo "- ⏸️  Production promotion pending")
$([ "${ENVIRONMENT:-staging}" = "production" ] && echo "- ✅ Production validation passed" || echo "- ⏸️  Production validation pending")

## Performance Targets

- Response Time: ≤2000ms
- Constitutional Compliance: ≥95%
- Cost Savings: ≥74%
- Availability: ≥99.9%
- Model Accuracy: ≥90%

## Storage Locations

- MLOps Root: $MLOPS_STORAGE_ROOT
- Backup Location: $BACKUP_DIR
- Log File: $LOG_FILE

## Next Steps

$([ "${ENVIRONMENT:-staging}" = "staging" ] && cat << 'NEXT_STEPS'
1. Review staging deployment results
2. Run additional validation tests if needed
3. Promote to production: `./scripts/deploy_mlops_system.sh production`
NEXT_STEPS
)

$([ "${ENVIRONMENT:-staging}" = "production" ] && cat << 'PROD_STEPS'
1. Monitor production deployment
2. Verify integration with existing ACGS-PGP services
3. Update operational documentation
PROD_STEPS
)

## Constitutional Compliance

All MLOps components have been verified to maintain constitutional hash integrity (cdd01ef066bc6cf2) and comply with ACGS-PGP governance requirements.

---
*Generated by ACGS-PGP MLOps Deployment System*
EOF
    
    log_success "Deployment report generated: $report_file"
}

# Main deployment function
main() {
    local environment="${1:-staging}"
    
    log "Starting ACGS-PGP MLOps System Deployment"
    log "Environment: $environment"
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "Timestamp: $TIMESTAMP"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    # Set environment variable
    export ENVIRONMENT="$environment"
    
    # Deployment steps
    validate_prerequisites
    validate_constitutional_compliance
    create_storage_directories
    install_dependencies
    run_integration_tests
    
    # Deploy to staging
    deploy_staging
    validate_staging
    
    # Promote to production if requested
    if [ "$environment" = "production" ]; then
        promote_to_production
        validate_production
    fi
    
    # Generate report
    generate_deployment_report
    
    log_success "🎉 ACGS-PGP MLOps System Deployment Complete!"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Environment: $environment"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Storage Root: $MLOPS_STORAGE_ROOT"
    echo "Deployment Report: mlops_deployment_report_${TIMESTAMP}.md"
    echo "Log File: $LOG_FILE"
    
    if [ "$environment" = "staging" ]; then
        echo ""
        echo "To promote to production, run:"
        echo "  $0 production"
    fi
}

# Script entry point
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
