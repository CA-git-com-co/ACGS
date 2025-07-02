package acgs.constitutional

# Constitutional hash validation for ACGS-PGP
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
COMPLIANCE_THRESHOLD = 0.8

# Default deny
default allow := false
default compliance_score := 0.0

# Constitutional compliance check
constitutional_valid {
    input.constitutional_hash == CONSTITUTIONAL_HASH
    input.compliance_score >= COMPLIANCE_THRESHOLD
}

# Service validation
service_valid {
    input.service_name
    input.service_port
    input.service_port >= 8000
    input.service_port <= 8006
}

# Resource limits validation
resource_limits_valid {
    input.cpu_request == "200m"
    input.memory_request == "512Mi"
}

# Main authorization
allow {
    constitutional_valid
    service_valid
    resource_limits_valid
}

# Emergency response authorization
allow {
    input.emergency_type
    input.response_time_seconds <= 1800
    input.authorized_responder == true
    constitutional_valid
}

# Compliance score calculation
compliance_score = score {
    constitutional_valid
    service_valid
    resource_limits_valid
    score = 1.0
}

compliance_score = score {
    constitutional_valid
    service_valid
    not resource_limits_valid
    score = 0.75
}

compliance_score = score {
    constitutional_valid
    not service_valid
    score = 0.5
}

compliance_score = 0.0 {
    not constitutional_valid
}
