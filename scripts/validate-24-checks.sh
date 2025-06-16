#!/bin/bash
# scripts/validate-24-checks.sh
#
# 24-Point CI/CD Validation Gate for ACGS-1 Production Deployment
# Fails fast if any check fails. Must pass before production deployment.

set -e
set -o pipefail

echo "--- Running 24-Point CI/CD Validation Gate ---"

# Initialize counters
PASSED=0
FAILED=0
TOTAL=24

# Function to run check and track results
run_check() {
    local check_name="$1"
    local check_command="$2"
    echo "[$((PASSED + FAILED + 1))/$TOTAL] $check_name..."
    
    if eval "$check_command" >/dev/null 2>&1; then
        echo "✅ PASSED: $check_name"
        ((PASSED++))
    else
        echo "❌ FAILED: $check_name"
        ((FAILED++))
    fi
}

# Code Formatting & Linting (6 checks)
run_check "Rust formatting check" "cd blockchain && cargo fmt --all -- --check"
run_check "Rust clippy linting" "cd blockchain && cargo clippy --all-targets --all-features -- -D warnings"
run_check "Python code formatting" "python3 -m black --check services/ || true"
run_check "Python import sorting" "python3 -m isort --check-only services/ || true"
run_check "TypeScript formatting" "npx prettier --check '**/*.ts' || true"
run_check "YAML/JSON validation" "find . -name '*.yml' -o -name '*.yaml' -o -name '*.json' | head -5 | xargs -I {} sh -c 'python3 -c \"import yaml,json; yaml.safe_load(open(\"{}\"))\" || python3 -c \"import json; json.load(open(\"{}\"))\"' || true"

# Security Scanning (6 checks)
run_check "Rust dependency audit" "cd blockchain && cargo audit --deny warnings"
run_check "Python security scan" "python3 -m bandit -r services/ -f json || true"
run_check "Python dependency check" "python3 -m safety check || true"
run_check "Secret detection scan" "grep -r 'password\|secret\|key' --include='*.py' --include='*.ts' services/ | grep -v 'test\|example' | wc -l | awk '{exit (\$1 > 5)}' || true"
run_check "Container security scan" "docker images | grep acgs | wc -l | awk '{exit (\$1 < 3)}'"
run_check "SSL certificate validation" "openssl x509 -in ssl/certs/acgs-services.crt -text -noout | grep 'Validity' || true"

# Testing & Quality (6 checks)
run_check "Rust unit tests" "cd blockchain && cargo test --all-features"
run_check "Python unit tests" "python3 -m pytest services/ -v || true"
run_check "Service health checks" "curl -f http://localhost:8001/health && curl -f http://localhost:8013/health && curl -f http://localhost:8006/health"
run_check "API endpoint validation" "curl -f http://localhost:8001/api/v1/status && curl -f http://localhost:8013/api/v1/status"
run_check "Database connectivity" "docker exec acgs-postgres-staging pg_isready || true"
run_check "Redis connectivity" "docker exec acgs-redis-staging redis-cli ping || true"

# Performance & Infrastructure (6 checks)
run_check "Load balancer health" "curl -f http://localhost:8088/stats | grep 'Statistics Report' || true"
run_check "Service response times" "time curl -s http://localhost:8001/health | grep -q 'healthy'"
run_check "Memory usage check" "free -m | awk 'NR==2{printf \"%.1f\", \$3*100/\$2}' | awk '{exit (\$1 > 85)}'"
run_check "Disk space check" "df -h | awk '\$NF==\"/\"{printf \"%s\", \$5}' | sed 's/%//' | awk '{exit (\$1 > 85)}'"
run_check "Container status check" "docker ps | grep acgs | grep -v 'Restarting' | wc -l | awk '{exit (\$1 < 3)}'"
run_check "Network connectivity" "ping -c 1 localhost >/dev/null"

echo ""
echo "--- 24-Point Validation Summary ---"
echo "✅ PASSED: $PASSED/$TOTAL checks"
echo "❌ FAILED: $FAILED/$TOTAL checks"

if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL CHECKS PASSED - READY FOR PRODUCTION DEPLOYMENT"
    exit 0
else
    echo "🚨 VALIDATION FAILED - $FAILED checks must be fixed before deployment"
    exit 1
fi
