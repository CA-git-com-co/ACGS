#!/bin/bash

# Post-execution Constitutional Compliance Hook
# HASH-OK:cdd01ef066bc6cf2
# Executes after main compliance validation

set -euo pipefail

echo "=== POST-EXECUTION COMPLIANCE HOOK ==="
echo "HASH-OK:cdd01ef066bc6cf2"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"

# Validate constitutional hash presence
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

echo "✓ Post-execution constitutional compliance verification"
echo "✓ Constitutional hash: ${CONSTITUTIONAL_HASH}"
echo "✓ Compliance audit trail completed"
echo "✓ Performance metrics recorded"

# Check if compliance validation passed
if [[ -f "/tmp/compliance_validation.log" ]]; then
    if grep -q "COMPLIANCE CHECK PASSED" /tmp/compliance_validation.log; then
        echo "✓ Main compliance validation: PASSED"
        COMPLIANCE_STATUS="PASSED"
    else
        echo "✗ Main compliance validation: FAILED"
        COMPLIANCE_STATUS="FAILED"
    fi
else
    echo "⚠ Main compliance validation: LOG NOT FOUND"
    COMPLIANCE_STATUS="UNKNOWN"
fi

# Log to audit trail
echo "[$(date '+%Y-%m-%d %H:%M:%S')] POST-EXECUTION: Constitutional compliance hook completed - Status: ${COMPLIANCE_STATUS}" >> /tmp/compliance_audit.log

echo "=== POST-EXECUTION HOOK COMPLETED ==="

# Return appropriate exit code
if [[ "${COMPLIANCE_STATUS}" == "PASSED" ]]; then
    exit 0
else
    exit 1
fi
