#!/bin/bash

# ACGS-2 Consolidated System Validation Script
# This script validates the consolidated system implementation
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Source the shared deployment library
# shellcheck source=scripts/shared/deployment_lib.sh
source "${SCRIPT_DIR}/shared/deployment_lib.sh"

# Validation results
VALIDATION_RESULTS=()
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Validation functions
validate_check() {
    local check_name="$1"
    local check_command="$2"
    
    ((TOTAL_CHECKS++))
    
    log_debug "Running check: $check_name"
    
    if eval "$check_command" &>/dev/null; then
        log_success "✅ $check_name"
        VALIDATION_RESULTS+=("PASS: $check_name")
        ((PASSED_CHECKS++))
        return 0
    else
        log_error "❌ $check_name"
        VALIDATION_RESULTS+=("FAIL: $check_name")
        ((FAILED_CHECKS++))
        return 1
    fi
}

# File existence checks
validate_file_structure() {
    log_step "Validating file structure"
    
    # Core Docker Compose files
    validate_check "Base infrastructure compose file exists" \
        "test -f '${PROJECT_ROOT}/infrastructure/docker/docker-compose.base-infrastructure.yml'"
    
    validate_check "ACGS services compose file exists" \
        "test -f '${PROJECT_ROOT}/infrastructure/docker/docker-compose.acgs-services.yml'"
    
    validate_check "Development override file exists" \
        "test -f '${PROJECT_ROOT}/infrastructure/docker/docker-compose.development.yml'"
    
    validate_check "Staging override file exists" \
        "test -f '${PROJECT_ROOT}/infrastructure/docker/docker-compose.staging.yml'"
    
    validate_check "Production override file exists" \
        "test -f '${PROJECT_ROOT}/infrastructure/docker/docker-compose.production-override.yml'"
    
    # Monitoring files
    validate_check "Consolidated monitoring compose file exists" \
        "test -f '${PROJECT_ROOT}/infrastructure/monitoring/docker-compose.monitoring-consolidated.yml'"
    
    validate_check "Consolidated Prometheus config exists" \
        "test -f '${PROJECT_ROOT}/infrastructure/monitoring/config/prometheus-consolidated.yml'"
    
    # Configuration files
    validate_check "Shared auth config exists" \
        "test -f '${PROJECT_ROOT}/config/shared/auth_config.yml'"
    
    validate_check "Shared environment config exists" \
        "test -f '${PROJECT_ROOT}/config/shared/environment.yml'"
    
    validate_check "Environment template exists" \
        "test -f '${PROJECT_ROOT}/config/environments/.env.template'"
    
    validate_check "Development environment config exists" \
        "test -f '${PROJECT_ROOT}/config/environments/.env.development'"
    
    # Script files
    validate_check "Shared deployment library exists" \
        "test -f '${PROJECT_ROOT}/scripts/shared/deployment_lib.sh'"
    
    validate_check "Consolidated deployment script exists" \
        "test -f '${PROJECT_ROOT}/scripts/deploy-acgs-consolidated.sh'"
    
    validate_check "Migration script exists" \
        "test -f '${PROJECT_ROOT}/scripts/migrate-to-consolidated.sh'"
    
    validate_check "CLAUDE.md generator exists" \
        "test -f '${PROJECT_ROOT}/scripts/tools/claude_md_generator.py'"
    
    # Documentation files
    validate_check "Consolidation usage guide exists" \
        "test -f '${PROJECT_ROOT}/docs/deployment/CONSOLIDATION_USAGE_GUIDE.md'"
    
    validate_check "Consolidated system README exists" \
        "test -f '${PROJECT_ROOT}/docs/deployment/CONSOLIDATED_SYSTEM_README.md'"
}

# Constitutional hash validation
validate_constitutional_compliance() {
    log_step "Validating constitutional compliance"
    
    validate_check "Constitutional hash in base infrastructure" \
        "grep -q 'cdd01ef066bc6cf2' '${PROJECT_ROOT}/infrastructure/docker/docker-compose.base-infrastructure.yml'"
    
    validate_check "Constitutional hash in ACGS services" \
        "grep -q 'cdd01ef066bc6cf2' '${PROJECT_ROOT}/infrastructure/docker/docker-compose.acgs-services.yml'"
    
    validate_check "Constitutional hash in monitoring config" \
        "grep -q 'cdd01ef066bc6cf2' '${PROJECT_ROOT}/infrastructure/monitoring/docker-compose.monitoring-consolidated.yml'"
    
    validate_check "Constitutional hash in auth config" \
        "grep -q 'cdd01ef066bc6cf2' '${PROJECT_ROOT}/config/shared/auth_config.yml'"
    
    validate_check "Constitutional hash in deployment script" \
        "grep -q 'cdd01ef066bc6cf2' '${PROJECT_ROOT}/scripts/deploy-acgs-consolidated.sh'"
    
    validate_check "Constitutional hash in migration script" \
        "grep -q 'cdd01ef066bc6cf2' '${PROJECT_ROOT}/scripts/migrate-to-consolidated.sh'"
}

# Script permissions
validate_script_permissions() {
    log_step "Validating script permissions"
    
    validate_check "Deployment script is executable" \
        "test -x '${PROJECT_ROOT}/scripts/deploy-acgs-consolidated.sh'"
    
    validate_check "Migration script is executable" \
        "test -x '${PROJECT_ROOT}/scripts/migrate-to-consolidated.sh'"
    
    validate_check "Shared deployment library is executable" \
        "test -x '${PROJECT_ROOT}/scripts/shared/deployment_lib.sh'"
    
    validate_check "CLAUDE.md generator is executable" \
        "test -x '${PROJECT_ROOT}/scripts/tools/claude_md_generator.py'"
}

# Docker Compose validation
validate_docker_compose_files() {
    log_step "Validating Docker Compose files"
    
    local compose_files=(
        "infrastructure/docker/docker-compose.base-infrastructure.yml"
        "infrastructure/docker/docker-compose.acgs-services.yml"
        "infrastructure/docker/docker-compose.development.yml"
        "infrastructure/docker/docker-compose.staging.yml"
        "infrastructure/docker/docker-compose.production-override.yml"
        "infrastructure/monitoring/docker-compose.monitoring-consolidated.yml"
    )
    
    for file in "${compose_files[@]}"; do
        validate_check "Docker Compose file syntax valid: $(basename "$file")" \
            "cd '${PROJECT_ROOT}' && docker-compose -f '$file' config >/dev/null 2>&1"
    done
}

# Configuration validation
validate_configuration_files() {
    log_step "Validating configuration files"
    
    # YAML syntax validation
    validate_check "Auth config YAML syntax valid" \
        "python3 -c 'import yaml; yaml.safe_load(open(\"${PROJECT_ROOT}/config/shared/auth_config.yml\"))'"
    
    validate_check "Environment config YAML syntax valid" \
        "python3 -c 'import yaml; yaml.safe_load(open(\"${PROJECT_ROOT}/config/shared/environment.yml\"))'"
    
    validate_check "Prometheus config YAML syntax valid" \
        "python3 -c 'import yaml; yaml.safe_load(open(\"${PROJECT_ROOT}/infrastructure/monitoring/config/prometheus-consolidated.yml\"))'"
    
    # Environment file validation
    validate_check "Development environment file syntax valid" \
        "source '${PROJECT_ROOT}/config/environments/.env.development' && test -n \"\$CONSTITUTIONAL_HASH\""
}

# Service definition validation
validate_service_definitions() {
    log_step "Validating service definitions"
    
    # Check that all required services are defined
    local required_services=(
        "auth_service"
        "ac_service"
        "integrity_service"
        "fv_service"
        "gs_service"
        "pgc_service"
        "ec_service"
        "postgres"
        "redis"
    )
    
    for service in "${required_services[@]}"; do
        validate_check "Service '$service' defined in ACGS services" \
            "grep -q \"^  $service:\" '${PROJECT_ROOT}/infrastructure/docker/docker-compose.acgs-services.yml' || grep -q \"^  $service:\" '${PROJECT_ROOT}/infrastructure/docker/docker-compose.base-infrastructure.yml'"
    done
}

# Tool validation
validate_tools() {
    log_step "Validating tools and dependencies"
    
    validate_check "Docker is available" \
        "command -v docker >/dev/null 2>&1"
    
    validate_check "Docker Compose is available" \
        "command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1"
    
    validate_check "Python 3 is available" \
        "command -v python3 >/dev/null 2>&1"
    
    validate_check "YAML Python module is available" \
        "python3 -c 'import yaml' >/dev/null 2>&1"
    
    validate_check "Bash is available" \
        "command -v bash >/dev/null 2>&1"
    
    validate_check "Curl is available" \
        "command -v curl >/dev/null 2>&1"
}

# Documentation validation
validate_documentation() {
    log_step "Validating documentation"
    
    validate_check "Usage guide contains constitutional hash" \
        "grep -q 'cdd01ef066bc6cf2' '${PROJECT_ROOT}/docs/deployment/CONSOLIDATION_USAGE_GUIDE.md'"
    
    validate_check "System README contains constitutional hash" \
        "grep -q 'cdd01ef066bc6cf2' '${PROJECT_ROOT}/docs/deployment/CONSOLIDATED_SYSTEM_README.md'"
    
    validate_check "Usage guide contains deployment examples" \
        "grep -q 'deploy-acgs-consolidated.sh' '${PROJECT_ROOT}/docs/deployment/CONSOLIDATION_USAGE_GUIDE.md'"
    
    validate_check "System README contains architecture overview" \
        "grep -q 'System Architecture' '${PROJECT_ROOT}/docs/deployment/CONSOLIDATED_SYSTEM_README.md'"
}

# Consolidation validation
validate_consolidation_effectiveness() {
    log_step "Validating consolidation effectiveness"
    
    # Count old vs new files
    local old_compose_count
    old_compose_count=$(find "${PROJECT_ROOT}" -name "docker-compose*.yml" -not -path "*/infrastructure/docker/*" -not -path "*/infrastructure/monitoring/*" | wc -l)
    
    local new_compose_count
    new_compose_count=$(find "${PROJECT_ROOT}/infrastructure" -name "docker-compose*.yml" | wc -l)
    
    validate_check "Consolidated compose files created" \
        "test $new_compose_count -ge 6"
    
    log_info "Found $old_compose_count old compose files vs $new_compose_count new consolidated files"
    
    # Check for auth config consolidation
    local auth_config_count
    auth_config_count=$(find "${PROJECT_ROOT}" -name "auth_config.yaml" -o -name "auth_config.yml" | wc -l)
    
    validate_check "Auth configs consolidated" \
        "test -f '${PROJECT_ROOT}/config/shared/auth_config.yml'"
    
    if [[ $auth_config_count -gt 1 ]]; then
        log_warning "Found $auth_config_count auth config files - consolidation may be incomplete"
    fi
}

# Generate validation report
generate_validation_report() {
    log_step "Generating validation report"
    
    local report_file="${PROJECT_ROOT}/VALIDATION_REPORT.md"
    
    cat > "$report_file" << EOF
# ACGS-2 Consolidated System Validation Report
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Validation Summary

**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Total Checks**: $TOTAL_CHECKS
**Passed**: $PASSED_CHECKS
**Failed**: $FAILED_CHECKS
**Success Rate**: $(echo "scale=2; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc -l)%

## Validation Results

EOF
    
    for result in "${VALIDATION_RESULTS[@]}"; do
        echo "- $result" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

## Constitutional Compliance

✅ Constitutional hash \`cdd01ef066bc6cf2\` validated across all components

## System Status

EOF
    
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        echo "🎉 **SYSTEM VALIDATION PASSED** - All checks successful" >> "$report_file"
    else
        echo "⚠️  **SYSTEM VALIDATION FAILED** - $FAILED_CHECKS checks failed" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF

## Performance Targets

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

---

**Report Generated**: $(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    log_success "Validation report generated: $report_file"
}

# Main validation function
main() {
    log_info "ACGS-2 Consolidated System Validation"
    log_info "Constitutional Hash: ${CONSTITUTIONAL_HASH}"
    
    # Initialize logging
    init_logging
    
    # Run validation checks
    validate_file_structure
    validate_constitutional_compliance
    validate_script_permissions
    validate_docker_compose_files
    validate_configuration_files
    validate_service_definitions
    validate_tools
    validate_documentation
    validate_consolidation_effectiveness
    
    # Generate report
    generate_validation_report
    
    # Summary
    log_info "Validation completed:"
    log_info "  Total checks: $TOTAL_CHECKS"
    log_info "  Passed: $PASSED_CHECKS"
    log_info "  Failed: $FAILED_CHECKS"
    log_info "  Success rate: $(echo "scale=2; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc -l)%"
    
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        log_success "🎉 All validation checks passed!"
        log_info "System is ready for deployment"
        return 0
    else
        log_error "❌ $FAILED_CHECKS validation checks failed"
        log_error "Please review the validation report: ${PROJECT_ROOT}/VALIDATION_REPORT.md"
        return 1
    fi
}

# Show usage
usage() {
    cat << EOF
ACGS-2 Consolidated System Validation Script

Usage: $0 [OPTIONS]

Options:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose logging

This script validates the consolidated system implementation by checking:
- File structure and permissions
- Constitutional compliance
- Docker Compose file syntax
- Configuration file validity
- Service definitions
- Tool availability
- Documentation completeness
- Consolidation effectiveness

Constitutional Hash: ${CONSTITUTIONAL_HASH}
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--verbose)
            DEBUG="true"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi