# ACGS Constitutional Compliance Policy
# Constitutional hash: cdd01ef066bc6cf2

package acgs.constitutional

# Constants
constitutional_hash := "cdd01ef066bc6cf2"

# Default allow policy
default allow = false

# Allow access if constitutional hash is present and valid
allow if {
    input.constitutional_hash == constitutional_hash
}

# Allow health checks
allow if {
    input.path == "/health"
}

allow if {
    input.path == "/health/constitutional"
}

# Constitutional compliance validation
constitutional_compliant if {
    input.constitutional_hash == constitutional_hash
}

# Service-specific rules
api_gateway_access if {
    input.service == "api_gateway"
    input.constitutional_hash == constitutional_hash
}

constitutional_core_access if {
    input.service == "constitutional_core"
    input.constitutional_hash == constitutional_hash
}

integrity_service_access if {
    input.service == "integrity_service"
    input.constitutional_hash == constitutional_hash
}
