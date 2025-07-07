# ACGS Constitutional Compliance Policy
# Constitutional hash: cdd01ef066bc6cf2

package acgs.constitutional

# Constants
constitutional_hash := "cdd01ef066bc6cf2"

# Default allow policy
default allow = false

# Allow access if constitutional hash is present and valid
allow {
    input.constitutional_hash == constitutional_hash
}

# Allow health checks
allow {
    input.path == "/health"
}

allow {
    input.path == "/health/constitutional"
}

# Constitutional compliance validation
constitutional_compliant {
    input.constitutional_hash == constitutional_hash
}

# Service-specific rules
api_gateway_access {
    input.service == "api_gateway"
    input.constitutional_hash == constitutional_hash
}

constitutional_core_access {
    input.service == "constitutional_core"
    input.constitutional_hash == constitutional_hash
}

integrity_service_access {
    input.service == "integrity_service"
    input.constitutional_hash == constitutional_hash
}
