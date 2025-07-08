#!/bin/bash

# Full Constitutional Compliance Check
# HASH-OK:cdd01ef066bc6cf2
# Orchestrates pre-, runtime, and post-execution compliance hooks

set -euo pipefail

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
AUDIT_LOG="/tmp/compliance_audit.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize audit log
echo "=== CONSTITUTIONAL COMPLIANCE AUDIT TRAIL ===" > "${AUDIT_LOG}"
echo "Timestamp: ${TIMESTAMP}" >> "${AUDIT_LOG}"
echo "Constitutional Hash: ${CONSTITUTIONAL_HASH}" >> "${AUDIT_LOG}"
echo "=========================================" >> "${AUDIT_LOG}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     ACGS-2 FULL CONSTITUTIONAL COMPLIANCE CHECK                      ║${NC}"
echo -e "${BLUE}║                                                                                      ║${NC}"
echo -e "${BLUE}║  Hash: ${CONSTITUTIONAL_HASH}                                              ║${NC}"
echo -e "${BLUE}║  Timestamp: ${TIMESTAMP}                                                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════╝${NC}"

# Step 1: Pre-execution compliance hook
echo -e "\n${YELLOW}Step 1: Executing pre-execution compliance hook...${NC}"
if "${SCRIPT_DIR}/pre_execution_hook.sh"; then
    echo -e "${GREEN}✓ Pre-execution compliance hook completed successfully${NC}"
else
    echo -e "${RED}✗ Pre-execution compliance hook failed${NC}"
    exit 1
fi

# Step 2: Runtime compliance hook
echo -e "\n${YELLOW}Step 2: Executing runtime compliance hook...${NC}"
if "${SCRIPT_DIR}/runtime_hook.sh"; then
    echo -e "${GREEN}✓ Runtime compliance hook completed successfully${NC}"
else
    echo -e "${RED}✗ Runtime compliance hook failed${NC}"
    exit 1
fi

# Step 3: Main hash validation
echo -e "\n${YELLOW}Step 3: Executing main hash validation...${NC}"
VALIDATION_RESULT=0
if "${SCRIPT_DIR}/validate_hash.sh"; then
    echo -e "${GREEN}✓ Hash validation completed successfully${NC}"
    VALIDATION_RESULT=0
else
    echo -e "${RED}✗ Hash validation failed - continuing to post-execution hook${NC}"
    VALIDATION_RESULT=1
fi

# Step 4: Post-execution compliance hook
echo -e "\n${YELLOW}Step 4: Executing post-execution compliance hook...${NC}"
if "${SCRIPT_DIR}/post_execution_hook.sh"; then
    echo -e "${GREEN}✓ Post-execution compliance hook completed successfully${NC}"
else
    echo -e "${RED}✗ Post-execution compliance hook failed${NC}"
    exit 1
fi

# Final result
echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                COMPLIANCE SUMMARY                                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════════════╝${NC}"

if [[ $VALIDATION_RESULT -eq 0 ]]; then
    echo -e "${GREEN}✓ 100% compliance achieved${NC}"
    echo -e "${GREEN}✓ All compliance hooks executed successfully${NC}"
    echo -e "${GREEN}✓ Constitutional hash ${CONSTITUTIONAL_HASH} validation passed${NC}"
    echo -e "${GREEN}✓ No violations detected${NC}"

    # Log success
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FINAL RESULT: 100% compliance achieved" >> "${AUDIT_LOG}"
    echo -e "\n${GREEN}COMPLIANCE STATUS: 100% COMPLIANT${NC}"
else
    echo -e "${RED}✗ Compliance violations detected${NC}"
    echo -e "${RED}✗ Constitutional hash ${CONSTITUTIONAL_HASH} validation failed${NC}"
    echo -e "${RED}✗ Manual remediation required${NC}"

    # Log failure
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FINAL RESULT: Compliance violations detected" >> "${AUDIT_LOG}"
    echo -e "\n${RED}COMPLIANCE STATUS: VIOLATIONS DETECTED${NC}"
    echo -e "${RED}ABORTING: Files missing constitutional hash where mandated${NC}"
    exit 1
fi

echo -e "\n${BLUE}Audit Trail: ${AUDIT_LOG}${NC}"
echo -e "${BLUE}Validation Log: /tmp/compliance_validation.log${NC}"
echo -e "${BLUE}Constitutional Hash: ${CONSTITUTIONAL_HASH}${NC}"

echo -e "\n${GREEN}Full constitutional compliance check completed successfully.${NC}"
exit 0
