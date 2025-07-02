package acgs.simple

# Constitutional hash for ACGS-PGP system
CONSTITUTIONAL_HASH := "cdd01ef066bc6cf2"
COMPLIANCE_THRESHOLD := 0.8

# Default deny
default allow = false

# Allow requests with valid constitutional hash and compliance
allow {
    input.constitutional_hash == CONSTITUTIONAL_HASH
    input.compliance_score >= COMPLIANCE_THRESHOLD
}

# Allow health checks
allow {
    input.path == "/health"
}

# Allow metrics endpoints
allow {
    input.path == "/metrics"
}

# Service-specific rules for ACGS-PGP services
allow {
    input.service_name == "auth_service"
    input.service_port == 8000
    input.constitutional_hash == CONSTITUTIONAL_HASH
}

allow {
    input.service_name == "ac_service"
    input.service_port == 8001
    input.constitutional_hash == CONSTITUTIONAL_HASH
}

allow {
    input.service_name == "integrity_service"
    input.service_port == 8002
    input.constitutional_hash == CONSTITUTIONAL_HASH
}

allow {
    input.service_name == "fv_service"
    input.service_port == 8003
    input.constitutional_hash == CONSTITUTIONAL_HASH
}

allow {
    input.service_name == "gs_service"
    input.service_port == 8004
    input.constitutional_hash == CONSTITUTIONAL_HASH
}

allow {
    input.service_name == "pgc_service"
    input.service_port == 8005
    input.constitutional_hash == CONSTITUTIONAL_HASH
}

allow {
    input.service_name == "ec_service"
    input.service_port == 8006
    input.constitutional_hash == CONSTITUTIONAL_HASH
}

# Policy governance service rules
pgc_allow {
    input.service_name == "pgc_service"
    input.service_port == 8005
    input.constitutional_hash == CONSTITUTIONAL_HASH
    input.compliance_score >= COMPLIANCE_THRESHOLD
}

# Constitutional compliance validation
constitutional_compliance {
    input.constitutional_hash == CONSTITUTIONAL_HASH
    input.compliance_score >= COMPLIANCE_THRESHOLD
}

# High-security operations require higher compliance
high_security_compliance {
    input.constitutional_hash == CONSTITUTIONAL_HASH
    input.compliance_score >= 0.95
    input.operation_type == "policy_creation"
}

high_security_compliance {
    input.constitutional_hash == CONSTITUTIONAL_HASH
    input.compliance_score >= 0.95
    input.operation_type == "governance_change"
}

high_security_compliance {
    input.constitutional_hash == CONSTITUTIONAL_HASH
    input.compliance_score >= 0.95
    input.operation_type == "constitutional_update"
}
