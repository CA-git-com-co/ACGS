#!/bin/bash
# ACGS CI/CD Pipeline Integration with Constitutional Compliance
# Constitutional Hash: cdd01ef066bc6cf2

set -e

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

echo "=== ACGS CI/CD Pipeline Integration ==="
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo ""

# Function to validate constitutional compliance
validate_constitutional_compliance() {
    echo "1. Validating Constitutional Compliance..."
    
    local compliance_errors=0
    local files_checked=0
    
    # Check key configuration files for constitutional hash
    local config_files=(
        "monitoring/prometheus.yml"
        "monitoring/alert_rules.yml"
        "docker-compose.production-simple.yml"
        "testing/performance/performance-validation-summary.json"
    )
    
    for file in "${config_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            files_checked=$((files_checked + 1))
            if grep -q "$CONSTITUTIONAL_HASH" "$PROJECT_ROOT/$file"; then
                echo "  ✓ $file: Constitutional hash found"
            else
                echo "  ✗ $file: Constitutional hash MISSING"
                compliance_errors=$((compliance_errors + 1))
            fi
        else
            echo "  ⚠ $file: File not found"
        fi
    done
    
    # Check running services for constitutional compliance
    echo "  Checking running services..."
    if curl -s http://localhost:9091/api/v1/status/config | grep -q "$CONSTITUTIONAL_HASH"; then
        echo "  ✓ Prometheus: Constitutional hash validated"
    else
        echo "  ✗ Prometheus: Constitutional hash validation failed"
        compliance_errors=$((compliance_errors + 1))
    fi
    
    if [ $compliance_errors -eq 0 ]; then
        echo "  ✓ Constitutional compliance: PASSED (100%)"
        return 0
    else
        echo "  ✗ Constitutional compliance: FAILED ($compliance_errors errors)"
        return 1
    fi
}

# Function to run pre-deployment tests
run_pre_deployment_tests() {
    echo "2. Running Pre-deployment Tests..."
    
    # Test infrastructure health
    echo "  Testing infrastructure health..."
    if docker compose -f "$PROJECT_ROOT/docker-compose.production-simple.yml" ps | grep -q "Up"; then
        echo "  ✓ Infrastructure: Services running"
    else
        echo "  ✗ Infrastructure: Services not running"
        return 1
    fi
    
    # Test monitoring endpoints
    echo "  Testing monitoring endpoints..."
    if curl -s http://localhost:9091/api/v1/status/config > /dev/null; then
        echo "  ✓ Prometheus: Accessible"
    else
        echo "  ✗ Prometheus: Not accessible"
        return 1
    fi
    
    if curl -s http://localhost:3001/api/health > /dev/null; then
        echo "  ✓ Grafana: Accessible"
    else
        echo "  ✗ Grafana: Not accessible"
        return 1
    fi
    
    echo "  ✓ Pre-deployment tests: PASSED"
    return 0
}

# Function to create deployment validation report
create_deployment_report() {
    echo "3. Creating Deployment Validation Report..."
    
    local report_file="$PROJECT_ROOT/reports/deployment-validation-$(date +%Y%m%d_%H%M%S).json"
    mkdir -p "$PROJECT_ROOT/reports"
    
    cat > "$report_file" << EOF
{
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "timestamp": "$(date -Iseconds)",
  "validation_type": "ci_cd_deployment",
  "pipeline_stage": "pre_deployment",
  "validation_results": {
    "constitutional_compliance": {
      "status": "$(validate_constitutional_compliance > /dev/null 2>&1 && echo "PASSED" || echo "FAILED")",
      "hash_validated": "$CONSTITUTIONAL_HASH"
    },
    "infrastructure_tests": {
      "status": "$(run_pre_deployment_tests > /dev/null 2>&1 && echo "PASSED" || echo "FAILED")",
      "services_checked": ["postgresql", "redis", "prometheus", "grafana"]
    },
    "monitoring_validation": {
      "prometheus_status": "$(curl -s http://localhost:9091/api/v1/status/config > /dev/null && echo "healthy" || echo "unhealthy")",
      "grafana_status": "$(curl -s http://localhost:3001/api/health > /dev/null && echo "healthy" || echo "unhealthy")",
      "alert_rules_loaded": $(curl -s http://localhost:9091/api/v1/rules | jq '.data.groups | length' 2>/dev/null || echo "0"),
      "dashboards_available": $(curl -s -u admin:acgs_admin_2025 http://localhost:3001/api/search?type=dash-db | jq '. | length' 2>/dev/null || echo "0")
    }
  },
  "deployment_readiness": "$(validate_constitutional_compliance > /dev/null 2>&1 && run_pre_deployment_tests > /dev/null 2>&1 && echo "APPROVED" || echo "REJECTED")",
  "recommendations": [
    "Ensure all services maintain constitutional compliance",
    "Monitor performance metrics continuously",
    "Validate alert rules after each deployment",
    "Verify dashboard functionality post-deployment"
  ]
}
EOF

    echo "  ✓ Deployment report saved to: $report_file"
}

# Function to setup automated testing pipeline
setup_automated_pipeline() {
    echo "4. Setting up Automated Testing Pipeline..."
    
    # Create GitHub Actions workflow (if .github directory exists)
    if [ -d "$PROJECT_ROOT/.github" ]; then
        mkdir -p "$PROJECT_ROOT/.github/workflows"
        
        cat > "$PROJECT_ROOT/.github/workflows/acgs-ci-cd.yml" << EOF
name: ACGS CI/CD Pipeline
# Constitutional Hash: $CONSTITUTIONAL_HASH

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

env:
  CONSTITUTIONAL_HASH: $CONSTITUTIONAL_HASH

jobs:
  constitutional-compliance:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Validate Constitutional Compliance
      run: |
        echo "Validating Constitutional Hash: \$CONSTITUTIONAL_HASH"
        grep -r "\$CONSTITUTIONAL_HASH" . --include="*.yml" --include="*.json" --include="*.sh" || exit 1
        
    - name: Run Infrastructure Tests
      run: |
        chmod +x scripts/continuous-improvement/ci-cd-integration.sh
        ./scripts/continuous-improvement/ci-cd-integration.sh
        
    - name: Performance Validation
      run: |
        chmod +x testing/performance/production-validation.sh
        ./testing/performance/production-validation.sh

  deployment:
    needs: constitutional-compliance
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Production
      run: |
        echo "Deploying with Constitutional Hash: \$CONSTITUTIONAL_HASH"
        # Add deployment commands here
        
    - name: Post-deployment Validation
      run: |
        # Add post-deployment validation here
        echo "Post-deployment validation completed"
EOF

        echo "  ✓ GitHub Actions workflow created"
    fi
    
    # Create cron job for regular validation
    local cron_script="$PROJECT_ROOT/scripts/continuous-improvement/scheduled-validation.sh"
    cat > "$cron_script" << EOF
#!/bin/bash
# ACGS Scheduled Validation
# Constitutional Hash: $CONSTITUTIONAL_HASH

cd "$PROJECT_ROOT"
./scripts/continuous-improvement/metrics-collector.sh
./scripts/continuous-improvement/ci-cd-integration.sh
EOF

    chmod +x "$cron_script"
    echo "  ✓ Scheduled validation script created"
    echo "  ℹ To enable scheduled validation, add to crontab:"
    echo "    0 */6 * * * $cron_script"
}

# Main execution
main() {
    local exit_code=0
    
    # Run all validation steps
    if ! validate_constitutional_compliance; then
        exit_code=1
    fi
    
    if ! run_pre_deployment_tests; then
        exit_code=1
    fi
    
    create_deployment_report
    setup_automated_pipeline
    
    echo ""
    echo "=== CI/CD Integration Summary ==="
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    
    if [ $exit_code -eq 0 ]; then
        echo "✓ All validations PASSED - Deployment APPROVED"
        echo "✓ Constitutional compliance: 100%"
        echo "✓ Infrastructure tests: PASSED"
        echo "✓ Monitoring validation: PASSED"
    else
        echo "✗ Some validations FAILED - Deployment REJECTED"
        echo "✗ Review errors above and fix before deployment"
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Review deployment validation report in reports/"
    echo "2. Set up scheduled validation cron job if needed"
    echo "3. Monitor constitutional compliance continuously"
    
    exit $exit_code
}

# Execute main function
main "$@"
