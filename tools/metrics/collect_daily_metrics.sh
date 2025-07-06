#!/bin/bash
# ACGS Daily Documentation Metrics Collection
# Constitutional Hash: cdd01ef066bc6cf2

set -e

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
METRICS_DATE=$(date +%Y-%m-%d)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
METRICS_DIR="$REPO_ROOT/metrics"
METRICS_FILE="$METRICS_DIR/daily_metrics_${METRICS_DATE}.json"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create metrics directory
mkdir -p "$METRICS_DIR"

echo -e "${BLUE}📊 Collecting ACGS Documentation Metrics for $METRICS_DATE${NC}"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Repository: $REPO_ROOT"
echo ""

# Initialize metrics object
cat > "$METRICS_FILE" << EOF
{
  "date": "$METRICS_DATE",
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "repository": "$REPO_ROOT",
  "collection_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "metrics": {}
}
EOF

# 1. Constitutional Compliance Metrics
echo -e "${BLUE}🔒 Measuring Constitutional Compliance...${NC}"

TOTAL_DOCS=$(find "$REPO_ROOT/docs" -name "*.md" -type f 2>/dev/null | wc -l || echo "0")
DOCS_WITH_HASH=$(find "$REPO_ROOT/docs" -name "*.md" -exec grep -l "$CONSTITUTIONAL_HASH" {} \; 2>/dev/null | wc -l || echo "0")

# Check critical files specifically
CRITICAL_FILES=("docs/configuration/README.md" "docs/api/index.md" "README.md" "infrastructure/docker/docker-compose.acgs.yml")
CRITICAL_COMPLIANT=0
CRITICAL_TOTAL=${#CRITICAL_FILES[@]}

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        if grep -q "$CONSTITUTIONAL_HASH" "$REPO_ROOT/$file"; then
            CRITICAL_COMPLIANT=$((CRITICAL_COMPLIANT + 1))
        fi
    fi
done

if [ "$TOTAL_DOCS" -gt 0 ]; then
    COMPLIANCE_RATE=$((DOCS_WITH_HASH * 100 / TOTAL_DOCS))
else
    COMPLIANCE_RATE=0
fi

CRITICAL_COMPLIANCE_RATE=$((CRITICAL_COMPLIANT * 100 / CRITICAL_TOTAL))

echo "  Total documentation files: $TOTAL_DOCS"
echo "  Files with constitutional hash: $DOCS_WITH_HASH"
echo "  Overall compliance rate: $COMPLIANCE_RATE%"
echo "  Critical files compliance: $CRITICAL_COMPLIANT/$CRITICAL_TOTAL ($CRITICAL_COMPLIANCE_RATE%)"

# Update metrics file
jq --arg rate "$COMPLIANCE_RATE" \
   --arg total "$TOTAL_DOCS" \
   --arg compliant "$DOCS_WITH_HASH" \
   --arg critical_rate "$CRITICAL_COMPLIANCE_RATE" \
   --arg critical_compliant "$CRITICAL_COMPLIANT" \
   --arg critical_total "$CRITICAL_TOTAL" \
   '.metrics.constitutional_compliance = {
     "rate": ($rate | tonumber),
     "total_docs": ($total | tonumber),
     "compliant_docs": ($compliant | tonumber),
     "critical_compliance_rate": ($critical_rate | tonumber),
     "critical_compliant": ($critical_compliant | tonumber),
     "critical_total": ($critical_total | tonumber),
     "target": 100,
     "status": (if ($rate | tonumber) == 100 then "PASS" else "FAIL" end)
   }' "$METRICS_FILE" > "$METRICS_FILE.tmp" && mv "$METRICS_FILE.tmp" "$METRICS_FILE" 2>/dev/null || {
    # Fallback if jq is not available
    sed -i 's/"metrics": {}/"metrics": {"constitutional_compliance": {"rate": '$COMPLIANCE_RATE', "total_docs": '$TOTAL_DOCS', "compliant_docs": '$DOCS_WITH_HASH', "target": 100}}/' "$METRICS_FILE"
}

# 2. Link Validity Metrics
echo -e "${BLUE}🔗 Measuring Link Validity...${NC}"

TOTAL_LINKS=0
BROKEN_LINKS=0
FILES_WITH_LINKS=0
FILES_WITH_BROKEN_LINKS=0

# Check internal markdown links
find "$REPO_ROOT/docs" -name "*.md" -type f | while read -r file; do
    INTERNAL_LINKS=$(grep -o '\[.*\](.*\.md[^)]*)' "$file" 2>/dev/null || true)
    
    if [ -n "$INTERNAL_LINKS" ]; then
        FILES_WITH_LINKS=$((FILES_WITH_LINKS + 1))
        FILE_BROKEN_LINKS=0
        
        echo "$INTERNAL_LINKS" | while read -r link; do
            if [ -n "$link" ]; then
                TOTAL_LINKS=$((TOTAL_LINKS + 1))
                LINK_PATH=$(echo "$link" | sed 's/.*](\([^)]*\)).*/\1/')
                
                if [[ "$LINK_PATH" == *.md ]] && [[ "$LINK_PATH" != http* ]]; then
                    # Resolve relative path
                    if [[ "$LINK_PATH" == /* ]]; then
                        FULL_LINK_PATH="$REPO_ROOT$LINK_PATH"
                    else
                        FILE_DIR=$(dirname "$file")
                        FULL_LINK_PATH="$FILE_DIR/$LINK_PATH"
                    fi
                    
                    if [ ! -f "$FULL_LINK_PATH" ]; then
                        BROKEN_LINKS=$((BROKEN_LINKS + 1))
                        FILE_BROKEN_LINKS=$((FILE_BROKEN_LINKS + 1))
                    fi
                fi
            fi
        done
        
        if [ "$FILE_BROKEN_LINKS" -gt 0 ]; then
            FILES_WITH_BROKEN_LINKS=$((FILES_WITH_BROKEN_LINKS + 1))
        fi
    fi
done

# Calculate link validity rate
if [ "$TOTAL_LINKS" -gt 0 ]; then
    LINK_VALIDITY_RATE=$(((TOTAL_LINKS - BROKEN_LINKS) * 100 / TOTAL_LINKS))
else
    LINK_VALIDITY_RATE=100
fi

echo "  Total internal links found: $TOTAL_LINKS"
echo "  Broken links: $BROKEN_LINKS"
echo "  Link validity rate: $LINK_VALIDITY_RATE%"
echo "  Files with broken links: $FILES_WITH_BROKEN_LINKS"

# Update metrics file with link validity
jq --arg rate "$LINK_VALIDITY_RATE" \
   --arg total "$TOTAL_LINKS" \
   --arg broken "$BROKEN_LINKS" \
   --arg files_broken "$FILES_WITH_BROKEN_LINKS" \
   '.metrics.link_validity = {
     "rate": ($rate | tonumber),
     "total_links": ($total | tonumber),
     "broken_links": ($broken | tonumber),
     "files_with_broken_links": ($files_broken | tonumber),
     "target": 100,
     "status": (if ($rate | tonumber) == 100 then "PASS" else "FAIL" end)
   }' "$METRICS_FILE" > "$METRICS_FILE.tmp" && mv "$METRICS_FILE.tmp" "$METRICS_FILE" 2>/dev/null || {
    # Fallback if jq is not available
    echo "Link validity metrics collected (jq not available for JSON update)"
}

# 3. Documentation Freshness Metrics
echo -e "${BLUE}📅 Measuring Documentation Freshness...${NC}"

TOTAL_CHECKED=0
STALE_DOCS=0
VERY_STALE_DOCS=0
CURRENT_TIME=$(date +%s)

find "$REPO_ROOT/docs" -name "*.md" -type f | while read -r file; do
    TOTAL_CHECKED=$((TOTAL_CHECKED + 1))
    LAST_MODIFIED=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null || echo "$CURRENT_TIME")
    DAYS_OLD=$(((CURRENT_TIME - LAST_MODIFIED) / 86400))
    
    # Consider docs stale if not updated in 90 days
    if [ "$DAYS_OLD" -gt 90 ]; then
        STALE_DOCS=$((STALE_DOCS + 1))
    fi
    
    # Consider docs very stale if not updated in 180 days
    if [ "$DAYS_OLD" -gt 180 ]; then
        VERY_STALE_DOCS=$((VERY_STALE_DOCS + 1))
    fi
done

if [ "$TOTAL_CHECKED" -gt 0 ]; then
    FRESHNESS_RATE=$(((TOTAL_CHECKED - STALE_DOCS) * 100 / TOTAL_CHECKED))
else
    FRESHNESS_RATE=100
fi

echo "  Total documentation files checked: $TOTAL_CHECKED"
echo "  Stale documents (>90 days): $STALE_DOCS"
echo "  Very stale documents (>180 days): $VERY_STALE_DOCS"
echo "  Freshness rate: $FRESHNESS_RATE%"

# Update metrics file with freshness
jq --arg rate "$FRESHNESS_RATE" \
   --arg total "$TOTAL_CHECKED" \
   --arg stale "$STALE_DOCS" \
   --arg very_stale "$VERY_STALE_DOCS" \
   '.metrics.documentation_freshness = {
     "rate": ($rate | tonumber),
     "total_docs": ($total | tonumber),
     "stale_docs": ($stale | tonumber),
     "very_stale_docs": ($very_stale | tonumber),
     "target": 85,
     "status": (if ($rate | tonumber) >= 85 then "PASS" else "FAIL" end)
   }' "$METRICS_FILE" > "$METRICS_FILE.tmp" && mv "$METRICS_FILE.tmp" "$METRICS_FILE" 2>/dev/null || {
    echo "Freshness metrics collected (jq not available for JSON update)"
}

# 4. Documentation Coverage Metrics
echo -e "${BLUE}📋 Measuring Documentation Coverage...${NC}"

# Count expected API documentation files based on our service architecture
EXPECTED_API_DOCS=(
    "authentication"
    "constitutional-ai"
    "integrity"
    "formal-verification"
    "governance_synthesis"
    "policy-governance"
    "evolutionary-computation"
)

TOTAL_EXPECTED=${#EXPECTED_API_DOCS[@]}
DOCUMENTED_SERVICES=0

for service in "${EXPECTED_API_DOCS[@]}"; do
    if [ -f "$REPO_ROOT/docs/api/${service}.md" ]; then
        DOCUMENTED_SERVICES=$((DOCUMENTED_SERVICES + 1))
        echo "  ✅ $service.md found"
    else
        echo "  ❌ $service.md missing"
    fi
done

if [ "$TOTAL_EXPECTED" -gt 0 ]; then
    COVERAGE_RATE=$((DOCUMENTED_SERVICES * 100 / TOTAL_EXPECTED))
else
    COVERAGE_RATE=100
fi

echo "  Total expected API docs: $TOTAL_EXPECTED"
echo "  Documented services: $DOCUMENTED_SERVICES"
echo "  Documentation coverage rate: $COVERAGE_RATE%"

# Update metrics file with coverage
jq --arg rate "$COVERAGE_RATE" \
   --arg total "$TOTAL_EXPECTED" \
   --arg documented "$DOCUMENTED_SERVICES" \
   '.metrics.documentation_coverage = {
     "rate": ($rate | tonumber),
     "total_expected": ($total | tonumber),
     "documented_services": ($documented | tonumber),
     "target": 80,
     "status": (if ($rate | tonumber) >= 80 then "PASS" else "FAIL" end)
   }' "$METRICS_FILE" > "$METRICS_FILE.tmp" && mv "$METRICS_FILE.tmp" "$METRICS_FILE" 2>/dev/null || {
    echo "Coverage metrics collected (jq not available for JSON update)"
}

# 5. Calculate Overall Quality Score
echo -e "${BLUE}🎯 Calculating Overall Quality Score...${NC}"

# Weight the metrics (can be adjusted based on importance)
COMPLIANCE_WEIGHT=30
LINK_WEIGHT=25
FRESHNESS_WEIGHT=25
COVERAGE_WEIGHT=20

WEIGHTED_SCORE=$(((COMPLIANCE_RATE * COMPLIANCE_WEIGHT + LINK_VALIDITY_RATE * LINK_WEIGHT + FRESHNESS_RATE * FRESHNESS_WEIGHT + COVERAGE_RATE * COVERAGE_WEIGHT) / 100))

# Determine overall status
if [ "$WEIGHTED_SCORE" -ge 95 ]; then
    OVERALL_STATUS="EXCELLENT"
elif [ "$WEIGHTED_SCORE" -ge 85 ]; then
    OVERALL_STATUS="GOOD"
elif [ "$WEIGHTED_SCORE" -ge 70 ]; then
    OVERALL_STATUS="NEEDS_IMPROVEMENT"
else
    OVERALL_STATUS="CRITICAL"
fi

echo "  Overall quality score: $WEIGHTED_SCORE%"
echo "  Overall status: $OVERALL_STATUS"

# Update metrics file with overall score
jq --arg score "$WEIGHTED_SCORE" \
   --arg status "$OVERALL_STATUS" \
   '.metrics.overall_quality = {
     "score": ($score | tonumber),
     "status": $status,
     "weights": {
       "constitutional_compliance": 30,
       "link_validity": 25,
       "documentation_freshness": 25,
       "documentation_coverage": 20
     }
   }' "$METRICS_FILE" > "$METRICS_FILE.tmp" && mv "$METRICS_FILE.tmp" "$METRICS_FILE" 2>/dev/null || {
    echo "Overall quality metrics collected (jq not available for JSON update)"
}

# Generate summary
echo ""
echo -e "${GREEN}✅ Daily metrics collection completed!${NC}"
echo "📊 Metrics saved to: $METRICS_FILE"
echo ""
echo "📈 Summary:"
echo "  Constitutional Compliance: $COMPLIANCE_RATE% (Target: 100%)"
echo "  Link Validity: $LINK_VALIDITY_RATE% (Target: 100%)"
echo "  Documentation Freshness: $FRESHNESS_RATE% (Target: 85%)"
echo "  Documentation Coverage: $COVERAGE_RATE% (Target: 80%)"
echo "  Overall Quality Score: $WEIGHTED_SCORE%"
echo "  Status: $OVERALL_STATUS"
echo ""
echo "Constitutional Hash: $CONSTITUTIONAL_HASH ✅"

# Create latest metrics symlink
ln -sf "daily_metrics_${METRICS_DATE}.json" "$METRICS_DIR/latest_metrics.json"

exit 0
