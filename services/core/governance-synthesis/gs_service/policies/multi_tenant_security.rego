# Multi-Tenant Security Policy
# Package: acgs.multi_tenant_security
#
# This policy enforces multi-tenant security isolation, resource access controls,
# and tenant-specific governance constraints within the ACGS system.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.multi_tenant_security

import rego.v1

# Default deny for tenant operations
default allow_tenant_operation := false
default allow_cross_tenant_access := false
default tenant_isolation_compliant := false

# Tenant security levels
tenant_security_levels := {
    "enterprise": {
        "isolation_level": "strict",
        "encryption_required": true,
        "audit_level": "comprehensive",
        "network_isolation": true,
        "data_residency": true
    },
    "standard": {
        "isolation_level": "moderate",
        "encryption_required": true,
        "audit_level": "standard",
        "network_isolation": false,
        "data_residency": false
    },
    "basic": {
        "isolation_level": "basic",
        "encryption_required": false,
        "audit_level": "minimal",
        "network_isolation": false,
        "data_residency": false
    }
}

# Resource isolation requirements
resource_isolation_requirements := {
    "compute": ["namespace_isolation", "resource_quotas", "network_policies"],
    "storage": ["encryption_at_rest", "access_control", "backup_isolation"],
    "network": ["vlan_separation", "firewall_rules", "traffic_encryption"],
    "data": ["column_level_security", "row_level_security", "audit_logging"]
}

# Tenant operation validation
allow_tenant_operation if {
    tenant := input.tenant
    operation := input.operation
    resource := input.resource

    # Validate tenant exists and is active
    tenant_is_valid(tenant)

    # Check operation permissions
    operation_permitted(tenant, operation, resource)

    # Verify security constraints
    security_constraints_met(tenant, operation, resource)

    # Constitutional compliance check
    constitutional_compliance_verified(tenant, operation)
}

# Cross-tenant access control
allow_cross_tenant_access if {
    source_tenant := input.source_tenant
    target_tenant := input.target_tenant
    operation := input.operation
    resource := input.resource

    # Both tenants must be valid
    tenant_is_valid(source_tenant)
    tenant_is_valid(target_tenant)

    # Cross-tenant access must be explicitly permitted
    cross_tenant_permission_exists(source_tenant, target_tenant, operation, resource)

    # Security level compatibility check
    security_levels_compatible(source_tenant, target_tenant)

    # Audit logging required for cross-tenant access
    audit_logging_enabled(source_tenant, target_tenant, operation)
}

# Tenant isolation compliance
tenant_isolation_compliant if {
    tenant := input.tenant
    requested_resources := input.resources

    # Check all resource isolation requirements
    all(resource, resource in requested_resources; resource_isolation_valid(tenant, resource))

    # Verify no unauthorized cross-tenant dependencies
    no_unauthorized_dependencies(tenant, requested_resources)

    # Data residency requirements met
    data_residency_compliant(tenant, requested_resources)
}

# Helper functions
tenant_is_valid(tenant) if {
    tenant.id
    tenant.status == "active"
    tenant.security_level in {"enterprise", "standard", "basic"}
    tenant.constitutional_hash == "cdd01ef066bc6cf2"
}

operation_permitted(tenant, operation, resource) if {
    tenant_permissions := data.tenant_permissions[tenant.id]
    operation in tenant_permissions.allowed_operations
    resource in tenant_permissions.allowed_resources
}

security_constraints_met(tenant, operation, resource) if {
    security_level := tenant_security_levels[tenant.security_level]

    # Check encryption requirements
    encryption_requirements_met(security_level, operation, resource)

    # Check audit requirements
    audit_requirements_met(security_level, operation, resource)

    # Check isolation requirements
    isolation_requirements_met(security_level, operation, resource)
}

constitutional_compliance_verified(tenant, operation) if {
    # Ensure operation aligns with constitutional principles
    operation_respects_human_dignity(operation)
    operation_ensures_fairness(tenant, operation)
    operation_maintains_accountability(operation)
}

cross_tenant_permission_exists(source, target, operation, resource) if {
    permissions := data.cross_tenant_permissions[source.id][target.id]
    permission := permissions[_]
    permission.operation == operation
    permission.resource == resource
    permission.status == "approved"
    permission.expires_at > time.now_ns()
}

security_levels_compatible(source, target) if {
    source_level := tenant_security_levels[source.security_level]
    target_level := tenant_security_levels[target.security_level]

    # Cross-tenant access only allowed if security levels are compatible
    compatible_security_levels(source_level, target_level)
}

compatible_security_levels(source_level, target_level) if {
    # Enterprise can access all levels
    source_level.isolation_level == "strict"
}

compatible_security_levels(source_level, target_level) if {
    # Standard can access standard and basic
    source_level.isolation_level == "moderate"
    target_level.isolation_level in {"moderate", "basic"}
}

compatible_security_levels(source_level, target_level) if {
    # Basic can only access basic
    source_level.isolation_level == "basic"
    target_level.isolation_level == "basic"
}

resource_isolation_valid(tenant, resource) if {
    isolation_reqs := resource_isolation_requirements[resource.type]
    all(req, req in isolation_reqs; resource_meets_requirement(tenant, resource, req))
}

resource_meets_requirement(tenant, resource, requirement) if {
    security_level := tenant_security_levels[tenant.security_level]
    requirement_met(security_level, resource, requirement)
}

no_unauthorized_dependencies(tenant, resources) if {
    all(resource, resource in resources; resource.tenant_id == tenant.id)
}

data_residency_compliant(tenant, resources) if {
    tenant_security_level := tenant_security_levels[tenant.security_level]

    # If data residency required, check all resources comply
    not tenant_security_level.data_residency
} else {
    all(resource, resource in input.resources;
        resource.location in data.tenant_allowed_locations[tenant.id])
}

encryption_requirements_met(security_level, operation, resource) if {
    not security_level.encryption_required
} else {
    resource.encryption_enabled == true
    operation.encryption_in_transit == true
}

audit_requirements_met(security_level, operation, resource) if {
    audit_level := security_level.audit_level
    operation_audit_level := operation.audit_level

    audit_level_sufficient(audit_level, operation_audit_level)
}

audit_level_sufficient("comprehensive", _) := true
audit_level_sufficient("standard", operation_audit_level) if {
    operation_audit_level in {"standard", "minimal"}
}
audit_level_sufficient("minimal", "minimal") := true

isolation_requirements_met(security_level, operation, resource) if {
    isolation_level := security_level.isolation_level

    # Check based on isolation level
    isolation_level_requirements_met(isolation_level, operation, resource)
}

isolation_level_requirements_met("strict", operation, resource) if {
    operation.namespace_isolated == true
    resource.dedicated_resources == true
    operation.network_isolated == true
}

isolation_level_requirements_met("moderate", operation, resource) if {
    operation.namespace_isolated == true
    # Shared resources allowed but with quotas
    resource.resource_quotas_enforced == true
}

isolation_level_requirements_met("basic", operation, resource) if {
    # Basic isolation - minimal requirements
    operation.basic_access_control == true
}

operation_respects_human_dignity(operation) if {
    # No operations that violate human dignity
    not operation.type in ["surveillance_excessive", "discrimination", "privacy_violation"]
    operation.constitutional_principles.human_dignity == true
}

operation_ensures_fairness(tenant, operation) if {
    # Fair resource allocation and access
    operation.resource_allocation == "fair"

    # No preferential treatment without justification
    not unfair_preference(tenant, operation)
}

unfair_preference(tenant, operation) if {
    operation.preferential_treatment == true
    not operation.justification
}

operation_maintains_accountability(operation) if {
    # All operations must be auditable
    operation.audit_trail_enabled == true
    operation.responsible_party
    operation.approval_workflow_completed == true
}

audit_logging_enabled(source, target, operation) if {
    operation.audit_logging == true
    operation.cross_tenant_audit == true
}

# Tenant security score calculation
tenant_security_score := score if {
    tenant := input.tenant
    security_level := tenant_security_levels[tenant.security_level]

    # Base score from security level
    base_score := security_level_base_score(security_level)

    # Compliance adjustments
    compliance_adjustment := calculate_compliance_adjustment(tenant)

    # Final score
    score := base_score + compliance_adjustment
}

security_level_base_score(security_level) := 0.9 if {
    security_level.isolation_level == "strict"
}

security_level_base_score(security_level) := 0.7 if {
    security_level.isolation_level == "moderate"
}

security_level_base_score(security_level) := 0.5 if {
    security_level.isolation_level == "basic"
}

calculate_compliance_adjustment(tenant) := adjustment if {
    violations := count([v | v := tenant_violations[tenant.id][_]])
    adjustment := -0.1 * violations
}

# Violation detection
tenant_violations[tenant_id] := violations if {
    tenant := data.tenants[tenant_id]
    violations := [v |
        some operation in tenant.recent_operations
        v := detect_violation(tenant, operation)
        v != null
    ]
}

detect_violation(tenant, operation) := violation if {
    not operation_permitted(tenant, operation.type, operation.resource)
    violation := {
        "type": "unauthorized_operation",
        "operation": operation,
        "timestamp": time.now_ns(),
        "severity": "high"
    }
}

detect_violation(tenant, operation) := violation if {
    not security_constraints_met(tenant, operation.type, operation.resource)
    violation := {
        "type": "security_constraint_violation",
        "operation": operation,
        "timestamp": time.now_ns(),
        "severity": "critical"
    }
}

# Multi-tenant governance decisions
governance_decisions := {
    "tenant_onboarding": {
        "requires_approval": true,
        "approval_threshold": 0.8,
        "security_assessment_required": true
    },
    "cross_tenant_access": {
        "requires_approval": true,
        "approval_threshold": 0.9,
        "time_limited": true
    },
    "security_level_upgrade": {
        "requires_approval": false,
        "automatic_approval": true
    },
    "security_level_downgrade": {
        "requires_approval": true,
        "approval_threshold": 0.9,
        "risk_assessment_required": true
    }
}
