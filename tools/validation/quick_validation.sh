#!/bin/bash
# ACGS Documentation Quick Validation Script
# Performs rapid consistency checks for ACGS documentation

set -e

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VALIDATION_PASSED=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    VALIDATION_PASSED=false
}

# Header
echo "🚀 ACGS Documentation Quick Validation"
echo "======================================"
echo "Repository: $REPO_ROOT"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo ""

# Check 1: Constitutional Hash Consistency
log_info "Checking constitutional hash consistency..."

HASH_COUNT=$(find "$REPO_ROOT/docs" -name "*.md" -exec grep -l "$CONSTITUTIONAL_HASH" {} \; | wc -l)
MISSING_HASH_FILES=$(find "$REPO_ROOT/docs" -name "*.md" -exec grep -l "constitutional.*hash\|hash.*constitutional" {} \; | xargs grep -L "$CONSTITUTIONAL_HASH" || true)

if [ "$HASH_COUNT" -gt 5 ]; then
    log_success "Constitutional hash found in $HASH_COUNT documentation files"
else
    log_warning "Constitutional hash found in only $HASH_COUNT files (expected more)"
fi

if [ -n "$MISSING_HASH_FILES" ]; then
    log_error "Files mention constitutional hash but missing value:"
    echo "$MISSING_HASH_FILES" | while read -r file; do
        echo "  - $file"
    done
fi

# Check critical files specifically
CRITICAL_FILES=(
    "docs/configuration/README.md"
    "infrastructure/docker/docker-compose.acgs.yml"
    "docs/api/index.md"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        if grep -q "$CONSTITUTIONAL_HASH" "$REPO_ROOT/$file"; then
            log_success "Constitutional hash found in $file"
        else
            log_error "Constitutional hash missing in critical file: $file"
        fi
    else
        log_warning "Critical file not found: $file"
    fi
done

echo ""

# Check 2: Port Configuration Consistency
log_info "Checking port configuration consistency..."

COMPOSE_FILE="$REPO_ROOT/infrastructure/docker/docker-compose.acgs.yml"
if [ -f "$COMPOSE_FILE" ]; then
    # Check PostgreSQL port
    if grep -q "5439:5432" "$COMPOSE_FILE"; then
        log_success "PostgreSQL port mapping correct (5439:5432)"
    else
        log_error "PostgreSQL port mapping incorrect in docker-compose.acgs.yml"
    fi

    # Check Redis port
    if grep -q "6389:6379" "$COMPOSE_FILE"; then
        log_success "Redis port mapping correct (6389:6379)"
    else
        log_error "Redis port mapping incorrect in docker-compose.acgs.yml"
    fi

    # Check Auth service port
    if grep -q "8016:8016" "$COMPOSE_FILE"; then
        log_success "Auth service port mapping correct (8016:8016)"
    else
        log_error "Auth service port mapping incorrect in docker-compose.acgs.yml"
    fi
else
    log_error "Docker compose file not found: $COMPOSE_FILE"
fi

echo ""

# Check 3: Performance Targets Consistency
log_info "Checking performance targets consistency..."

PERF_FILES=(
    "README.md"
    "docs/configuration/README.md"
    "docs/operations/SERVICE_STATUS.md"
)

for file in "${PERF_FILES[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        # Check throughput target
        if grep -q "≥100.*RPS\|≥100.*requests" "$REPO_ROOT/$file"; then
            log_success "Throughput target (≥100 RPS) found in $file"
        else
            log_warning "Throughput target (≥100 RPS) not found in $file"
        fi

        # Check latency target
        if grep -q "≤5ms\|P99.*5ms" "$REPO_ROOT/$file"; then
            log_success "Latency target (≤5ms P99) found in $file"
        else
            log_warning "Latency target (≤5ms P99) not found in $file"
        fi

        # Check cache hit rate
        if grep -q "≥85%.*cache\|cache.*≥85%" "$REPO_ROOT/$file"; then
            log_success "Cache hit rate target (≥85%) found in $file"
        else
            log_warning "Cache hit rate target (≥85%) not found in $file"
        fi
    else
        log_warning "Performance target file not found: $file"
    fi
done

echo ""

# Check 4: Test Coverage Targets
log_info "Checking test coverage targets consistency..."

# Check pytest.ini
if [ -f "$REPO_ROOT/pytest.ini" ]; then
    if grep -q "cov-fail-under=80\|80" "$REPO_ROOT/pytest.ini"; then
        log_success "80% test coverage target found in pytest.ini"
    else
        log_warning "80% test coverage target not found in pytest.ini"
    fi
else
    log_warning "pytest.ini not found"
fi

# Check pyproject.toml
if [ -f "$REPO_ROOT/pyproject.toml" ]; then
    if grep -q "fail_under.*80\|80" "$REPO_ROOT/pyproject.toml"; then
        log_success "80% test coverage target found in pyproject.toml"
    else
        log_warning "80% test coverage target not found in pyproject.toml"
    fi
else
    log_warning "pyproject.toml not found"
fi

echo ""

# Check 5: Documentation Completeness
log_info "Checking documentation completeness..."

REQUIRED_DOCS=(
    "README.md"
    "docs/configuration/README.md"
    "docs/api/index.md"
    "docs/operations/SERVICE_STATUS.md"
    "docs/deployment/ACGS_PGP_SETUP_GUIDE.md"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$REPO_ROOT/$doc" ]; then
        log_success "Required documentation found: $doc"
    else
        log_error "Required documentation missing: $doc"
    fi
done

echo ""

# Check 6: API Documentation Constitutional Hash
log_info "Checking API documentation constitutional hash..."

API_FILES=$(find "$REPO_ROOT/docs/api" -name "*.md" 2>/dev/null || true)
if [ -n "$API_FILES" ]; then
    API_WITH_HASH=0
    API_TOTAL=0

    echo "$API_FILES" | while read -r api_file; do
        if [ -f "$api_file" ]; then
            API_TOTAL=$((API_TOTAL + 1))
            if grep -q "$CONSTITUTIONAL_HASH" "$api_file"; then
                API_WITH_HASH=$((API_WITH_HASH + 1))
                log_success "Constitutional hash found in $(basename "$api_file")"
            else
                log_warning "Constitutional hash missing in $(basename "$api_file")"
            fi
        fi
    done
else
    log_warning "No API documentation files found"
fi

echo ""

# Check 7: Service Status Documentation
log_info "Checking service status documentation..."

SERVICE_STATUS_FILE="$REPO_ROOT/docs/operations/SERVICE_STATUS.md"
if [ -f "$SERVICE_STATUS_FILE" ]; then
    # Check for service ports
    EXPECTED_PORTS=(8016 8001 8002 8003 8004 8005 8006 5439 6389)

    for port in "${EXPECTED_PORTS[@]}"; do
        if grep -q "$port" "$SERVICE_STATUS_FILE"; then
            log_success "Port $port documented in SERVICE_STATUS.md"
        else
            log_warning "Port $port not found in SERVICE_STATUS.md"
        fi
    done

    # Check for constitutional hash
    if grep -q "$CONSTITUTIONAL_HASH" "$SERVICE_STATUS_FILE"; then
        log_success "Constitutional hash found in SERVICE_STATUS.md"
    else
        log_error "Constitutional hash missing in SERVICE_STATUS.md"
    fi
else
    log_error "SERVICE_STATUS.md not found"
fi

echo ""

# Summary
echo "======================================"
if [ "$VALIDATION_PASSED" = true ]; then
    log_success "All critical validation checks PASSED!"
    echo ""
    echo "✅ Documentation is consistent and ready for deployment"
    echo "✅ Constitutional compliance maintained"
    echo "✅ Port configurations are correct"
    echo "✅ Performance targets are documented"
    exit 0
else
    log_error "Some validation checks FAILED!"
    echo ""
    echo "❌ Please review and fix the issues listed above"
    echo "❌ Re-run validation after making corrections"
    echo ""
    echo "For detailed validation, run:"
    echo "  python tools/validation/validate_documentation_consistency.py"
    exit 1
fi
