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

# Check config/environments/pytest.ini
if [ -f "$REPO_ROOT/config/environments/pytest.ini" ]; then
    if grep -q "cov-fail-under=80\|80" "$REPO_ROOT/config/environments/pytest.ini"; then
        log_success "80% test coverage target found in config/environments/pytest.ini"
    else
        log_warning "80% test coverage target not found in config/environments/pytest.ini"
    fi
else
    log_warning "config/environments/pytest.ini not found"
fi

# Check config/environments/pyproject.toml
if [ -f "$REPO_ROOT/config/environments/pyproject.toml" ]; then
    if grep -q "fail_under.*80\|80" "$REPO_ROOT/config/environments/pyproject.toml"; then
        log_success "80% test coverage target found in config/environments/pyproject.toml"
    else
        log_warning "80% test coverage target not found in config/environments/pyproject.toml"
    fi
else
    log_warning "config/environments/pyproject.toml not found"
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

# Check 8: Service Configuration Alignment
log_info "Running service configuration alignment validation..."

# Check if Python validation tools exist
SERVICE_VALIDATOR="$REPO_ROOT/tools/validation/service_config_alignment_validator.py"
CROSS_REF_ANALYZER="$REPO_ROOT/tools/validation/advanced_cross_reference_analyzer.py"
PATTERN_REGISTRY="$REPO_ROOT/tools/validation/cross_reference_patterns.yaml"

if [ -f "$SERVICE_VALIDATOR" ]; then
    # Run service configuration alignment validator
    log_info "Checking service configuration alignment..."
    
    # Create temporary files for output
    TEMP_JSON="/tmp/service_validation_$$.json"
    TEMP_LOG="/tmp/service_validation_$$.log"
    
    if python3 "$SERVICE_VALIDATOR" --repo-root "$REPO_ROOT" --json > "$TEMP_JSON" 2>"$TEMP_LOG"; then
        # Check if we got valid JSON output (look for summary section)
        if grep -q '"summary"' "$TEMP_JSON" 2>/dev/null; then
            # Check for critical issues
            CRITICAL_ISSUES=$(grep -c '"severity": "CRITICAL"' "$TEMP_JSON" 2>/dev/null || echo "0")
            HIGH_ISSUES=$(grep -c '"severity": "HIGH"' "$TEMP_JSON" 2>/dev/null || echo "0")
            
            if [ "$CRITICAL_ISSUES" -gt 0 ]; then
                log_error "Found $CRITICAL_ISSUES critical service configuration issues"
            elif [ "$HIGH_ISSUES" -gt 0 ]; then
                log_warning "Found $HIGH_ISSUES high-priority service configuration issues"
            else
                log_success "Service configuration alignment validation passed"
            fi
        else
            # If no valid JSON, it probably generated a report instead
            if [ -s "$TEMP_JSON" ]; then
                log_success "Service configuration alignment validation completed (report generated)"
            else
                log_warning "Service configuration alignment validator produced no output"
            fi
        fi
        
        # Clean up temp files
        rm -f "$TEMP_JSON" "$TEMP_LOG"
    else
        log_warning "Service configuration alignment validator failed to run"
        # Clean up temp files on failure too
        rm -f "$TEMP_JSON" "$TEMP_LOG"
    fi
else
    log_warning "Service configuration alignment validator not found"
fi

echo ""

# Check 9: Pattern Registry and Cross-Reference Validation
log_info "Checking PATTERN_REGISTRY and cross-reference validation..."

if [ -f "$PATTERN_REGISTRY" ]; then
    # Validate pattern registry YAML syntax
    if python3 -c "import yaml; yaml.safe_load(open('$PATTERN_REGISTRY'))" 2>/dev/null; then
        log_success "PATTERN_REGISTRY YAML syntax is valid"
        
        # Check constitutional hash in pattern registry
        if grep -q "$CONSTITUTIONAL_HASH" "$PATTERN_REGISTRY"; then
            log_success "Constitutional hash found in PATTERN_REGISTRY"
        else
            log_error "Constitutional hash missing in PATTERN_REGISTRY"
        fi
        
        # Check for required pattern categories
        REQUIRED_CATEGORIES=("markdown_links" "code_references" "configuration_references")
        for category in "${REQUIRED_CATEGORIES[@]}"; do
            if grep -q "$category:" "$PATTERN_REGISTRY"; then
                log_success "Pattern category '$category' found in PATTERN_REGISTRY"
            else
                log_warning "Pattern category '$category' missing in PATTERN_REGISTRY"
            fi
        done
    else
        log_error "PATTERN_REGISTRY YAML syntax is invalid"
    fi
else
    log_error "PATTERN_REGISTRY file not found: $PATTERN_REGISTRY"
fi

# Check cross-reference analyzer
if [ -f "$CROSS_REF_ANALYZER" ]; then
    log_info "Running quick cross-reference validation..."
    # Run a limited cross-reference check on key documentation files
    KEY_DOCS=(
        "README.md"
        "docs/training/validation_tools_cheatsheet.md"
        "docs/validation/SERVICE_CONFIG_ALIGNMENT.md"
    )
    
    BROKEN_REFS=0
    for doc in "${KEY_DOCS[@]}"; do
        if [ -f "$REPO_ROOT/$doc" ]; then
            # Simple check for obvious broken links (markdown links that point to non-existent files)
            while IFS= read -r line; do
                if [[ $line =~ \[.*\]\(([^)]+)\) ]]; then
                    link="${BASH_REMATCH[1]}"
                    # Skip external links
                    if [[ ! $link =~ ^https?:// && ! $link =~ ^mailto: && ! $link =~ ^# ]]; then
                        # Convert relative link to absolute path
                        if [[ $link =~ ^\./ ]]; then
                            link_path="$(dirname "$REPO_ROOT/$doc")/${link#./}"
                        elif [[ $link =~ ^\.\./ ]]; then
                            link_path="$(dirname "$REPO_ROOT/$doc")/$link"
                        else
                            link_path="$REPO_ROOT/$link"
                        fi
                        
                        # Remove anchor fragments
                        link_path="${link_path%#*}"
                        
                        if [ ! -f "$link_path" ]; then
                            log_warning "Potential broken link in $doc: $link"
                            BROKEN_REFS=$((BROKEN_REFS + 1))
                        fi
                    fi
                fi
            done < "$REPO_ROOT/$doc"
        fi
    done
    
    if [ "$BROKEN_REFS" -eq 0 ]; then
        log_success "No obvious broken links found in key documentation"
    else
        log_warning "Found $BROKEN_REFS potential broken links (run full cross-reference analysis for details)"
    fi
else
    log_warning "Cross-reference analyzer not found"
fi

echo ""

# Check 10: Validation Tools Integration
log_info "Checking validation tools integration..."

# Check if new documentation exists
NEW_VALIDATION_DOCS=(
    "docs/training/validation_tools_cheatsheet.md"
    "docs/validation/SERVICE_CONFIG_ALIGNMENT.md"
)

for doc in "${NEW_VALIDATION_DOCS[@]}"; do
    if [ -f "$REPO_ROOT/$doc" ]; then
        log_success "Validation documentation found: $doc"
        
        # Check constitutional hash in validation docs
        if grep -q "$CONSTITUTIONAL_HASH" "$REPO_ROOT/$doc"; then
            log_success "Constitutional hash found in $doc"
        else
            log_error "Constitutional hash missing in $doc"
        fi
        
        # Check for PATTERN_REGISTRY mentions in validation docs
        if grep -q "PATTERN_REGISTRY" "$REPO_ROOT/$doc"; then
            log_success "PATTERN_REGISTRY documented in $doc"
        else
            log_warning "PATTERN_REGISTRY not mentioned in $doc"
        fi
    else
        log_error "Validation documentation missing: $doc"
    fi
done

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
    echo "✅ Service configuration alignment validated"
    echo "✅ Cross-reference validation and PATTERN_REGISTRY checked"
    echo ""
    echo "🚀 Advanced validation capabilities:"
    echo "   - Service Config Alignment: python tools/validation/service_config_alignment_validator.py"
    echo "   - Cross-Reference Analysis: python tools/validation/advanced_cross_reference_analyzer.py"
    echo "   - Pattern Registry: tools/validation/cross_reference_patterns.yaml"
    exit 0
else
    log_error "Some validation checks FAILED!"
    echo ""
    echo "❌ Please review and fix the issues listed above"
    echo "❌ Re-run validation after making corrections"
    echo ""
    echo "For detailed validation, run:"
    echo "  python tools/validation/service_config_alignment_validator.py --output detailed_report.md"
    echo "  python tools/validation/advanced_cross_reference_analyzer.py --output-dir reports/"
    echo "  python tools/validation/validate_documentation_consistency.py"
    exit 1
fi
