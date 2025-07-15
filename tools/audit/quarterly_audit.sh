#!/bin/bash
# ACGS Quarterly Documentation Audit Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
AUDIT_DATE=$(date +%Y%m%d)
AUDIT_QUARTER="Q$((($(date +%-m)-1)/3+1))_$(date +%Y)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUDIT_REPORTS_DIR="$REPO_ROOT/audit_reports"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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
}

log_section() {
    echo -e "${PURPLE}🔍 $1${NC}"
}

# Create audit reports directory
mkdir -p "$AUDIT_REPORTS_DIR"

# Initialize audit report
AUDIT_REPORT="$AUDIT_REPORTS_DIR/quarterly_audit_${AUDIT_QUARTER}_${AUDIT_DATE}.md"

cat > "$AUDIT_REPORT" << EOF
# ACGS Quarterly Documentation Audit Report

**Audit Period**: $AUDIT_QUARTER
**Audit Date**: $(date)
**Constitutional Hash**: $CONSTITUTIONAL_HASH
**Auditor**: $(whoami)

## Executive Summary

This report presents the findings of the quarterly documentation audit for ACGS, covering implementation alignment, cross-reference validation, performance metrics updates, and constitutional compliance verification.

## Audit Scope

- Infrastructure documentation alignment
- Service API documentation accuracy
- Cross-reference validation
- Performance metrics consistency
- Constitutional compliance verification

---

EOF

echo "🚀 ACGS Quarterly Documentation Audit - $AUDIT_QUARTER"
echo "======================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Audit Date: $(date)"
echo "Repository: $REPO_ROOT"
echo ""

# Phase 1: Implementation Alignment Review
log_section "Phase 1: Implementation Alignment Review"

echo "## Phase 1: Implementation Alignment Review" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# 1.1 Infrastructure Alignment Audit
log_info "Checking infrastructure configuration alignment..."

INFRASTRUCTURE_SCORE=0
INFRASTRUCTURE_TOTAL=0

# Check PostgreSQL port alignment
INFRASTRUCTURE_TOTAL=$((INFRASTRUCTURE_TOTAL + 1))
DOCUMENTED_POSTGRES_PORT=$(grep -o "5439" "$REPO_ROOT/docs/configuration/README.md" 2>/dev/null | head -1 || echo "")
ACTUAL_POSTGRES_PORT=$(grep -o "5439:5432" "$REPO_ROOT/infrastructure/docker/docker-compose.acgs.yml" 2>/dev/null | cut -d: -f1 || echo "")

if [ "$DOCUMENTED_POSTGRES_PORT" = "5439" ] && [ "$ACTUAL_POSTGRES_PORT" = "5439" ]; then
    log_success "PostgreSQL port alignment verified (5439)"
    INFRASTRUCTURE_SCORE=$((INFRASTRUCTURE_SCORE + 1))
    echo "- ✅ PostgreSQL port alignment: PASS" >> "$AUDIT_REPORT"
else
    log_error "PostgreSQL port mismatch: Doc=$DOCUMENTED_POSTGRES_PORT, Actual=$ACTUAL_POSTGRES_PORT"
    echo "- ❌ PostgreSQL port alignment: FAIL (Doc=$DOCUMENTED_POSTGRES_PORT, Actual=$ACTUAL_POSTGRES_PORT)" >> "$AUDIT_REPORT"
fi

# Check Redis port alignment
INFRASTRUCTURE_TOTAL=$((INFRASTRUCTURE_TOTAL + 1))
DOCUMENTED_REDIS_PORT=$(grep -o "6389" "$REPO_ROOT/docs/configuration/README.md" 2>/dev/null | head -1 || echo "")
ACTUAL_REDIS_PORT=$(grep -o "6389:6379" "$REPO_ROOT/infrastructure/docker/docker-compose.acgs.yml" 2>/dev/null | cut -d: -f1 || echo "")

if [ "$DOCUMENTED_REDIS_PORT" = "6389" ] && [ "$ACTUAL_REDIS_PORT" = "6389" ]; then
    log_success "Redis port alignment verified (6389)"
    INFRASTRUCTURE_SCORE=$((INFRASTRUCTURE_SCORE + 1))
    echo "- ✅ Redis port alignment: PASS" >> "$AUDIT_REPORT"
else
    log_error "Redis port mismatch: Doc=$DOCUMENTED_REDIS_PORT, Actual=$ACTUAL_REDIS_PORT"
    echo "- ❌ Redis port alignment: FAIL (Doc=$DOCUMENTED_REDIS_PORT, Actual=$ACTUAL_REDIS_PORT)" >> "$AUDIT_REPORT"
fi

# Check Auth service port alignment
INFRASTRUCTURE_TOTAL=$((INFRASTRUCTURE_TOTAL + 1))
DOCUMENTED_AUTH_PORT=$(grep -o "8016" "$REPO_ROOT/docs/configuration/README.md" 2>/dev/null | head -1 || echo "")
ACTUAL_AUTH_PORT=$(grep -o "8016:8016" "$REPO_ROOT/infrastructure/docker/docker-compose.acgs.yml" 2>/dev/null | cut -d: -f1 || echo "")

if [ "$DOCUMENTED_AUTH_PORT" = "8016" ] && [ "$ACTUAL_AUTH_PORT" = "8016" ]; then
    log_success "Auth service port alignment verified (8016)"
    INFRASTRUCTURE_SCORE=$((INFRASTRUCTURE_SCORE + 1))
    echo "- ✅ Auth service port alignment: PASS" >> "$AUDIT_REPORT"
else
    log_error "Auth service port mismatch: Doc=$DOCUMENTED_AUTH_PORT, Actual=$ACTUAL_AUTH_PORT"
    echo "- ❌ Auth service port alignment: FAIL (Doc=$DOCUMENTED_AUTH_PORT, Actual=$ACTUAL_AUTH_PORT)" >> "$AUDIT_REPORT"
fi

INFRASTRUCTURE_PERCENTAGE=$((INFRASTRUCTURE_SCORE * 100 / INFRASTRUCTURE_TOTAL))
log_info "Infrastructure alignment score: $INFRASTRUCTURE_SCORE/$INFRASTRUCTURE_TOTAL ($INFRASTRUCTURE_PERCENTAGE%)"

echo "" >> "$AUDIT_REPORT"
echo "**Infrastructure Alignment Score**: $INFRASTRUCTURE_SCORE/$INFRASTRUCTURE_TOTAL ($INFRASTRUCTURE_PERCENTAGE%)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# 1.2 Service API Alignment Audit
log_info "Checking service API documentation alignment..."

API_SCORE=0
API_TOTAL=0

SERVICES=("authentication:8016" "constitutional-ai:8001" "integrity:8002" "formal-verification:8003" "governance_synthesis:8004" "policy-governance:8005" "evolutionary-computation:8006")

echo "### Service API Alignment" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

for service in "${SERVICES[@]}"; do
    SERVICE_NAME="${service%%:*}"
    SERVICE_PORT="${service##*:}"

    log_info "Auditing $SERVICE_NAME service..."

    API_TOTAL=$((API_TOTAL + 3)) # 3 checks per service

    # Check if documentation exists
    if [ -f "$REPO_ROOT/docs/api/${SERVICE_NAME}.md" ]; then
        log_success "Documentation exists for $SERVICE_NAME"
        API_SCORE=$((API_SCORE + 1))
        echo "- ✅ $SERVICE_NAME documentation exists" >> "$AUDIT_REPORT"

        # Check if port is correct in documentation
        if grep -q "$SERVICE_PORT" "$REPO_ROOT/docs/api/${SERVICE_NAME}.md"; then
            log_success "Port $SERVICE_PORT correctly documented for $SERVICE_NAME"
            API_SCORE=$((API_SCORE + 1))
            echo "- ✅ $SERVICE_NAME port $SERVICE_PORT correctly documented" >> "$AUDIT_REPORT"
        else
            log_warning "Port $SERVICE_PORT missing in documentation for $SERVICE_NAME"
            echo "- ⚠️ $SERVICE_NAME port $SERVICE_PORT missing in documentation" >> "$AUDIT_REPORT"
        fi

        # Check constitutional hash in examples
        if grep -q "$CONSTITUTIONAL_HASH" "$REPO_ROOT/docs/api/${SERVICE_NAME}.md"; then
            log_success "Constitutional hash present in $SERVICE_NAME documentation"
            API_SCORE=$((API_SCORE + 1))
            echo "- ✅ $SERVICE_NAME constitutional hash present" >> "$AUDIT_REPORT"
        else
            log_warning "Constitutional hash missing in $SERVICE_NAME documentation"
            echo "- ⚠️ $SERVICE_NAME constitutional hash missing" >> "$AUDIT_REPORT"
        fi
    else
        log_error "Documentation missing for $SERVICE_NAME"
        echo "- ❌ $SERVICE_NAME documentation missing" >> "$AUDIT_REPORT"
    fi
done

API_PERCENTAGE=$((API_SCORE * 100 / API_TOTAL))
log_info "Service API alignment score: $API_SCORE/$API_TOTAL ($API_PERCENTAGE%)"

echo "" >> "$AUDIT_REPORT"
echo "**Service API Alignment Score**: $API_SCORE/$API_TOTAL ($API_PERCENTAGE%)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Phase 2: Cross-Reference Validation
log_section "Phase 2: Cross-Reference Validation"

echo "## Phase 2: Cross-Reference Validation" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# 2.1 Link Validation
log_info "Validating internal documentation links..."

LINK_SCORE=0
LINK_TOTAL=0

# Find all markdown files
find "$REPO_ROOT/docs" -name "*.md" -type f > /tmp/markdown_files_audit.txt
echo "$REPO_ROOT/README.md" >> /tmp/markdown_files_audit.txt

BROKEN_LINKS=""
TOTAL_FILES=0
FAILED_FILES=0

echo "### Link Validation Results" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

while IFS= read -r file; do
    if [ -f "$file" ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        RELATIVE_FILE=$(echo "$file" | sed "s|$REPO_ROOT/||")

        # Simple link validation (check for broken internal references)
        INTERNAL_LINKS=$(grep -o '\[.*\](.*\.md[^)]*)' "$file" 2>/dev/null || true)

        if [ -n "$INTERNAL_LINKS" ]; then
            LINK_TOTAL=$((LINK_TOTAL + 1))

            # Check if internal links are valid (simplified check)
            BROKEN_IN_FILE=false
            while IFS= read -r link; do
                if [ -n "$link" ]; then
                    LINK_PATH=$(echo "$link" | sed 's/.*](\([^)]*\)).*/\1/')
                    if [[ "$LINK_PATH" == *.md ]] && [[ "$LINK_PATH" != http* ]]; then
                        # Resolve relative path
                        FULL_LINK_PATH="$REPO_ROOT/docs/$LINK_PATH"
                        if [ ! -f "$FULL_LINK_PATH" ]; then
                            BROKEN_IN_FILE=true
                            break
                        fi
                    fi
                fi
            done <<< "$INTERNAL_LINKS"

            if [ "$BROKEN_IN_FILE" = false ]; then
                LINK_SCORE=$((LINK_SCORE + 1))
                echo "- ✅ $RELATIVE_FILE: All internal links valid" >> "$AUDIT_REPORT"
            else
                FAILED_FILES=$((FAILED_FILES + 1))
                echo "- ❌ $RELATIVE_FILE: Contains broken internal links" >> "$AUDIT_REPORT"
            fi
        fi
    fi
done < /tmp/markdown_files_audit.txt

if [ "$LINK_TOTAL" -gt 0 ]; then
    LINK_PERCENTAGE=$((LINK_SCORE * 100 / LINK_TOTAL))
else
    LINK_PERCENTAGE=100
fi

log_info "Link validation score: $LINK_SCORE/$LINK_TOTAL ($LINK_PERCENTAGE%)"

echo "" >> "$AUDIT_REPORT"
echo "**Link Validation Score**: $LINK_SCORE/$LINK_TOTAL ($LINK_PERCENTAGE%)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Phase 3: Performance Metrics Validation
log_section "Phase 3: Performance Metrics Validation"

echo "## Phase 3: Performance Metrics Validation" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

PERFORMANCE_SCORE=0
PERFORMANCE_TOTAL=0

# Performance targets to validate
PERFORMANCE_TARGETS=(
    "≥100.*RPS:throughput"
    "≤5ms:latency"
    "≥85%.*cache:cache_hit_rate"
    "≥80%.*coverage:test_coverage"
)

echo "### Performance Target Consistency" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

for target in "${PERFORMANCE_TARGETS[@]}"; do
    TARGET_PATTERN="${target%%:*}"
    TARGET_TYPE="${target##*:}"

    PERFORMANCE_TOTAL=$((PERFORMANCE_TOTAL + 1))

    log_info "Validating $TARGET_TYPE target pattern: $TARGET_PATTERN"

    # Count occurrences across documentation
    COUNT=$(grep -r "$TARGET_PATTERN" "$REPO_ROOT/docs/" 2>/dev/null | wc -l || echo "0")

    if [ "$COUNT" -ge 2 ]; then
        log_success "$TARGET_TYPE target consistently documented ($COUNT occurrences)"
        PERFORMANCE_SCORE=$((PERFORMANCE_SCORE + 1))
        echo "- ✅ $TARGET_TYPE target: Consistently documented ($COUNT occurrences)" >> "$AUDIT_REPORT"
    else
        log_warning "$TARGET_TYPE target inconsistently documented ($COUNT occurrences)"
        echo "- ⚠️ $TARGET_TYPE target: Inconsistently documented ($COUNT occurrences)" >> "$AUDIT_REPORT"
    fi
done

PERFORMANCE_PERCENTAGE=$((PERFORMANCE_SCORE * 100 / PERFORMANCE_TOTAL))
log_info "Performance metrics validation score: $PERFORMANCE_SCORE/$PERFORMANCE_TOTAL ($PERFORMANCE_PERCENTAGE%)"

echo "" >> "$AUDIT_REPORT"
echo "**Performance Metrics Score**: $PERFORMANCE_SCORE/$PERFORMANCE_TOTAL ($PERFORMANCE_PERCENTAGE%)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Phase 4: Constitutional Compliance Verification
log_section "Phase 4: Constitutional Compliance Verification"

echo "## Phase 4: Constitutional Compliance Verification" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

COMPLIANCE_SCORE=0
COMPLIANCE_TOTAL=0

# Check critical files for constitutional hash
CRITICAL_FILES=(
    "docs/configuration/README.md"
    "docs/api/index.md"
    "infrastructure/docker/docker-compose.acgs.yml"
    "README.md"
)

echo "### Critical Files Constitutional Hash Validation" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

for file in "${CRITICAL_FILES[@]}"; do
    COMPLIANCE_TOTAL=$((COMPLIANCE_TOTAL + 1))
    FULL_PATH="$REPO_ROOT/$file"

    if [ -f "$FULL_PATH" ]; then
        if grep -q "$CONSTITUTIONAL_HASH" "$FULL_PATH"; then
            log_success "Constitutional hash found in $file"
            COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
            echo "- ✅ $file: Constitutional hash present" >> "$AUDIT_REPORT"
        else
            log_error "Constitutional hash MISSING in critical file: $file"
            echo "- ❌ $file: Constitutional hash MISSING" >> "$AUDIT_REPORT"
        fi
    else
        log_warning "Critical file not found: $file"
        echo "- ⚠️ $file: File not found" >> "$AUDIT_REPORT"
    fi
done

# Check API documentation files
API_FILES=$(find "$REPO_ROOT/docs/api/" -name "*.md" -type f 2>/dev/null || true)
API_WITH_HASH=0
API_TOTAL_COUNT=0

echo "" >> "$AUDIT_REPORT"
echo "### API Documentation Constitutional Hash Validation" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

if [ -n "$API_FILES" ]; then
    while IFS= read -r api_file; do
        if [ -f "$api_file" ]; then
            API_TOTAL_COUNT=$((API_TOTAL_COUNT + 1))
            RELATIVE_API_FILE=$(echo "$api_file" | sed "s|$REPO_ROOT/||")

            if grep -q "$CONSTITUTIONAL_HASH" "$api_file"; then
                API_WITH_HASH=$((API_WITH_HASH + 1))
                echo "- ✅ $RELATIVE_API_FILE: Constitutional hash present" >> "$AUDIT_REPORT"
            else
                echo "- ❌ $RELATIVE_API_FILE: Constitutional hash missing" >> "$AUDIT_REPORT"
            fi
        fi
    done <<< "$API_FILES"
fi

# Calculate overall compliance
TOTAL_DOC_FILES=$(find "$REPO_ROOT/docs/" -name "*.md" -type f 2>/dev/null | wc -l || echo "0")
FILES_WITH_HASH=$(find "$REPO_ROOT/docs/" -name "*.md" -exec grep -l "$CONSTITUTIONAL_HASH" {} \; 2>/dev/null | wc -l || echo "0")

if [ "$TOTAL_DOC_FILES" -gt 0 ]; then
    OVERALL_COMPLIANCE_PERCENTAGE=$((FILES_WITH_HASH * 100 / TOTAL_DOC_FILES))
else
    OVERALL_COMPLIANCE_PERCENTAGE=0
fi

COMPLIANCE_PERCENTAGE=$((COMPLIANCE_SCORE * 100 / COMPLIANCE_TOTAL))

log_info "Critical files compliance score: $COMPLIANCE_SCORE/$COMPLIANCE_TOTAL ($COMPLIANCE_PERCENTAGE%)"
log_info "Overall documentation compliance: $FILES_WITH_HASH/$TOTAL_DOC_FILES ($OVERALL_COMPLIANCE_PERCENTAGE%)"

echo "" >> "$AUDIT_REPORT"
echo "**Critical Files Compliance Score**: $COMPLIANCE_SCORE/$COMPLIANCE_TOTAL ($COMPLIANCE_PERCENTAGE%)" >> "$AUDIT_REPORT"
echo "**Overall Documentation Compliance**: $FILES_WITH_HASH/$TOTAL_DOC_FILES ($OVERALL_COMPLIANCE_PERCENTAGE%)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Generate Overall Audit Summary
log_section "Generating Audit Summary"

TOTAL_SCORE=$((INFRASTRUCTURE_SCORE + API_SCORE + LINK_SCORE + PERFORMANCE_SCORE + COMPLIANCE_SCORE))
TOTAL_POSSIBLE=$((INFRASTRUCTURE_TOTAL + API_TOTAL + LINK_TOTAL + PERFORMANCE_TOTAL + COMPLIANCE_TOTAL))

if [ "$TOTAL_POSSIBLE" -gt 0 ]; then
    OVERALL_PERCENTAGE=$((TOTAL_SCORE * 100 / TOTAL_POSSIBLE))
else
    OVERALL_PERCENTAGE=0
fi

# Determine overall status
if [ "$OVERALL_PERCENTAGE" -ge 95 ]; then
    OVERALL_STATUS="EXCELLENT"
    STATUS_EMOJI="🟢"
elif [ "$OVERALL_PERCENTAGE" -ge 85 ]; then
    OVERALL_STATUS="GOOD"
    STATUS_EMOJI="🟡"
elif [ "$OVERALL_PERCENTAGE" -ge 70 ]; then
    OVERALL_STATUS="NEEDS IMPROVEMENT"
    STATUS_EMOJI="🟠"
else
    OVERALL_STATUS="CRITICAL"
    STATUS_EMOJI="🔴"
fi

cat >> "$AUDIT_REPORT" << EOF

## Overall Audit Summary

**Overall Score**: $TOTAL_SCORE/$TOTAL_POSSIBLE ($OVERALL_PERCENTAGE%)
**Status**: $STATUS_EMOJI $OVERALL_STATUS
**Constitutional Hash**: $CONSTITUTIONAL_HASH ✅

### Detailed Scores

| Category | Score | Percentage | Status |
|----------|-------|------------|--------|
| Infrastructure Alignment | $INFRASTRUCTURE_SCORE/$INFRASTRUCTURE_TOTAL | $INFRASTRUCTURE_PERCENTAGE% | $([ $INFRASTRUCTURE_PERCENTAGE -ge 90 ] && echo "✅ PASS" || echo "⚠️ NEEDS ATTENTION") |
| Service API Alignment | $API_SCORE/$API_TOTAL | $API_PERCENTAGE% | $([ $API_PERCENTAGE -ge 90 ] && echo "✅ PASS" || echo "⚠️ NEEDS ATTENTION") |
| Link Validation | $LINK_SCORE/$LINK_TOTAL | $LINK_PERCENTAGE% | $([ $LINK_PERCENTAGE -ge 95 ] && echo "✅ PASS" || echo "⚠️ NEEDS ATTENTION") |
| Performance Metrics | $PERFORMANCE_SCORE/$PERFORMANCE_TOTAL | $PERFORMANCE_PERCENTAGE% | $([ $PERFORMANCE_PERCENTAGE -ge 90 ] && echo "✅ PASS" || echo "⚠️ NEEDS ATTENTION") |
| Constitutional Compliance | $COMPLIANCE_SCORE/$COMPLIANCE_TOTAL | $COMPLIANCE_PERCENTAGE% | $([ $COMPLIANCE_PERCENTAGE -eq 100 ] && echo "✅ PASS" || echo "❌ CRITICAL") |

### Recommendations

EOF

# Add recommendations based on scores
if [ "$INFRASTRUCTURE_PERCENTAGE" -lt 90 ]; then
    echo "- **Infrastructure**: Update port configurations and environment variable documentation" >> "$AUDIT_REPORT"
fi

if [ "$API_PERCENTAGE" -lt 90 ]; then
    echo "- **API Documentation**: Add missing service documentation and constitutional hash examples" >> "$AUDIT_REPORT"
fi

if [ "$LINK_PERCENTAGE" -lt 95 ]; then
    echo "- **Links**: Fix broken internal documentation links and references" >> "$AUDIT_REPORT"
fi

if [ "$PERFORMANCE_PERCENTAGE" -lt 90 ]; then
    echo "- **Performance**: Standardize performance targets across all documentation" >> "$AUDIT_REPORT"
fi

if [ "$COMPLIANCE_PERCENTAGE" -lt 100 ]; then
    echo "- **Constitutional Compliance**: Add constitutional hash $CONSTITUTIONAL_HASH to all critical files" >> "$AUDIT_REPORT"
fi

cat >> "$AUDIT_REPORT" << EOF

### Next Steps

1. **Immediate Actions** (Within 1 week):
   - Fix critical constitutional compliance issues
   - Repair broken documentation links
   - Update missing service documentation

2. **Short-term Actions** (Within 1 month):
   - Standardize performance targets across documentation
   - Improve infrastructure documentation alignment
   - Enhance API documentation completeness

3. **Long-term Actions** (Next quarter):
   - Implement automated documentation validation
   - Establish continuous compliance monitoring
   - Develop documentation quality metrics dashboard

---

**Audit Completed**: $(date)
**Next Audit**: $(date -d "+3 months" +%Y-%m-%d)
**Constitutional Hash**: $CONSTITUTIONAL_HASH ✅
EOF

# Display summary
echo ""
echo "======================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
log_section "AUDIT COMPLETED"
echo "======================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
echo ""
log_info "Overall Score: $TOTAL_SCORE/$TOTAL_POSSIBLE ($OVERALL_PERCENTAGE%)"
log_info "Status: $STATUS_EMOJI $OVERALL_STATUS"
log_info "Constitutional Hash: $CONSTITUTIONAL_HASH ✅"
echo ""
log_info "Detailed audit report saved to: $AUDIT_REPORT"
echo ""

# Cleanup
rm -f /tmp/markdown_files_audit.txt

# Exit with appropriate code
if [ "$OVERALL_PERCENTAGE" -ge 85 ]; then
    log_success "Quarterly audit completed successfully!"
    exit 0
else
    log_warning "Quarterly audit completed with issues requiring attention."
    exit 1
fi
