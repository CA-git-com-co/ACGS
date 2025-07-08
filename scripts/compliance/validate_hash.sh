#!/bin/bash

# Constitutional Hash Validation Script
# HASH-OK:cdd01ef066bc6cf2
# Validates constitutional compliance hash across LaTeX, figures, and source code

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
LOG_FILE="/tmp/compliance_validation.log"
VALIDATION_TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
COMPLIANCE_RATE=0
TOTAL_FILES=0
COMPLIANT_FILES=0
VIOLATIONS=()

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Header
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ACGS-2 Constitutional Compliance Hash Validation${NC}"
echo -e "${BLUE}  Hash: ${CONSTITUTIONAL_HASH}${NC}"
echo -e "${BLUE}  Timestamp: ${VALIDATION_TIMESTAMP}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════${NC}"

# Initialize log
log "Starting constitutional hash validation for ${CONSTITUTIONAL_HASH}"

# Function to validate a single file
validate_file() {
    local file="$1"
    local mandatory="$2"

    TOTAL_FILES=$((TOTAL_FILES + 1))

    if grep -q "${CONSTITUTIONAL_HASH}" "${file}" 2>/dev/null; then
        log "✓ COMPLIANT: ${file}"
        COMPLIANT_FILES=$((COMPLIANT_FILES + 1))
        return 0
    else
        if [[ "${mandatory}" == "true" ]]; then
            log "✗ VIOLATION: ${file} (MANDATORY)"
            VIOLATIONS+=("${file} (MANDATORY)")
            return 1
        else
            log "⚠ WARNING: ${file} (OPTIONAL)"
            return 0
        fi
    fi
}

# Validate LaTeX files
echo -e "\n${YELLOW}Validating LaTeX files...${NC}"
log "Validating LaTeX files"

# Find and validate .tex files
if find . -name "*.tex" -type f | head -1 > /dev/null 2>&1; then
    while IFS= read -r -d '' file; do
        validate_file "$file" "true"
    done < <(find . -name "*.tex" -type f -print0)
else
    log "No LaTeX files found"
fi

# Validate figures
echo -e "\n${YELLOW}Validating figure files...${NC}"
log "Validating figure files"

# Find and validate image files with metadata
if find . -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.svg" -o -name "*.pdf" | head -1 > /dev/null 2>&1; then
    while IFS= read -r file; do
        # Check if there's a corresponding metadata file or if hash is in filename
        if [[ "$file" == *"${CONSTITUTIONAL_HASH}"* ]]; then
            log "✓ COMPLIANT: ${file} (hash in filename)"
            COMPLIANT_FILES=$((COMPLIANT_FILES + 1))
        else
            # Check for accompanying metadata file
            metadata_file="${file}.meta"
            if [[ -f "$metadata_file" ]]; then
                validate_file "$metadata_file" "false"
            else
                log "⚠ WARNING: ${file} (no metadata file)"
            fi
        fi
        TOTAL_FILES=$((TOTAL_FILES + 1))
    done < <(find . -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.svg" -o -name "*.pdf")
else
    log "No figure files found"
fi

# Validate source code files
echo -e "\n${YELLOW}Validating source code files...${NC}"
log "Validating source code files"

# Key source files that must have the hash
MANDATORY_FILES=(
    "CLAUDE.md"
    "README.md"
    "services/core/constitutional-ai/ac_service/app/main.py"
    "services/core/integrity/integrity_service/app/main.py"
    "services/platform_services/api_gateway/gateway_service/app/main.py"
)

# Check mandatory files
for file in "${MANDATORY_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        validate_file "$file" "true"
    else
        log "✗ MISSING: ${file} (MANDATORY FILE NOT FOUND)"
        VIOLATIONS+=("${file} (MISSING)")
    fi
done

# Check Python files in core services
if find services/core -name "*.py" -type f | head -1 > /dev/null 2>&1; then
    while IFS= read -r -d '' file; do
        validate_file "$file" "false"
    done < <(find services/core -name "*.py" -type f -print0)
fi

# Check configuration files
config_files=(
    "infrastructure/docker/docker-compose.acgs.yml"
    ".env.acgs"
    "infrastructure/kubernetes/acgs-deployment.yml"
)

for file in "${config_files[@]}"; do
    if [[ -f "$file" ]]; then
        validate_file "$file" "true"
    fi
done

# Calculate compliance rate
if [[ $TOTAL_FILES -gt 0 ]]; then
    COMPLIANCE_RATE=$(echo "scale=2; $COMPLIANT_FILES * 100 / $TOTAL_FILES" | bc)
else
    COMPLIANCE_RATE=0
fi

# Report results
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  VALIDATION SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════${NC}"

log "Validation completed"
log "Total files checked: $TOTAL_FILES"
log "Compliant files: $COMPLIANT_FILES"
log "Compliance rate: ${COMPLIANCE_RATE}%"

echo -e "Total files checked: ${TOTAL_FILES}"
echo -e "Compliant files: ${COMPLIANT_FILES}"
echo -e "Compliance rate: ${COMPLIANCE_RATE}%"

# Check for violations
if [[ ${#VIOLATIONS[@]} -gt 0 ]]; then
    echo -e "\n${RED}CONSTITUTIONAL VIOLATIONS DETECTED:${NC}"
    for violation in "${VIOLATIONS[@]}"; do
        echo -e "${RED}  ✗ ${violation}${NC}"
        log "VIOLATION: ${violation}"
    done

    echo -e "\n${RED}COMPLIANCE CHECK FAILED${NC}"
    echo -e "${RED}ABORTING: Constitutional hash ${CONSTITUTIONAL_HASH} missing from mandatory files${NC}"
    log "COMPLIANCE CHECK FAILED - ABORTING"
    exit 1
else
    if [[ $(echo "$COMPLIANCE_RATE == 100" | bc) -eq 1 ]]; then
        echo -e "\n${GREEN}✓ 100% compliance achieved${NC}"
        log "100% compliance achieved"
    else
        echo -e "\n${GREEN}✓ No mandatory violations found${NC}"
        log "No mandatory violations found"
    fi

    echo -e "${GREEN}COMPLIANCE CHECK PASSED${NC}"
    log "COMPLIANCE CHECK PASSED"
fi

echo -e "\n${BLUE}Validation log: ${LOG_FILE}${NC}"
echo -e "${BLUE}Constitutional hash: ${CONSTITUTIONAL_HASH}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════${NC}"

exit 0
