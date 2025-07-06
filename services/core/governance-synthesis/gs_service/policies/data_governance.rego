# Data Governance Policy
# Package: acgs.data_governance
#
# This policy enforces data privacy, protection, and governance requirements
# within the ACGS constitutional framework including GDPR, CCPA compliance.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.data_governance

import rego.v1

# Default deny for data operations
default allow_data_access := false
default allow_data_processing := false
default allow_data_sharing := false
default allow_data_retention := false

# Data classification levels
data_classification_levels := {
    "public": {
        "protection_level": "basic",
        "encryption_required": false,
        "access_logging_required": true,
        "retention_limit_days": 2555,  # 7 years
        "cross_border_transfer_allowed": true
    },
    "internal": {
        "protection_level": "standard",
        "encryption_required": true,
        "access_logging_required": true,
        "retention_limit_days": 1825,  # 5 years
        "cross_border_transfer_allowed": false
    },
    "confidential": {
        "protection_level": "high",
        "encryption_required": true,
        "access_logging_required": true,
        "retention_limit_days": 1095,  # 3 years
        "cross_border_transfer_allowed": false,
        "access_approval_required": true
    },
    "restricted": {
        "protection_level": "maximum",
        "encryption_required": true,
        "access_logging_required": true,
        "retention_limit_days": 365,   # 1 year
        "cross_border_transfer_allowed": false,
        "access_approval_required": true,
        "multi_party_access_required": true
    }
}

# Privacy regulation compliance frameworks
privacy_regulations := {
    "gdpr": {
        "name": "General Data Protection Regulation",
        "jurisdiction": "EU",
        "personal_data_protection": true,
        "consent_required": true,
        "right_to_erasure": true,
        "data_portability": true,
        "privacy_by_design": true
    },
    "ccpa": {
        "name": "California Consumer Privacy Act",
        "jurisdiction": "California",
        "personal_data_protection": true,
        "opt_out_rights": true,
        "data_deletion_rights": true,
        "data_transparency": true
    },
    "pipeda": {
        "name": "Personal Information Protection and Electronic Documents Act",
        "jurisdiction": "Canada",
        "consent_required": true,
        "purpose_limitation": true,
        "data_minimization": true
    }
}

# Constitutional data principles
constitutional_data_principles := {
    "human_dignity": {
        "principle": "Data processing must respect human dignity and autonomy",
        "requirements": ["consent_verification", "purpose_limitation", "data_minimization"],
        "weight": 1.0
    },
    "privacy": {
        "principle": "Individual privacy rights must be protected",
        "requirements": ["access_control", "encryption", "anonymization"],
        "weight": 0.95
    },
    "transparency": {
        "principle": "Data processing must be transparent and explainable",
        "requirements": ["purpose_declaration", "processing_transparency", "audit_trail"],
        "weight": 0.9
    },
    "fairness": {
        "principle": "Data processing must be fair and non-discriminatory",
        "requirements": ["bias_detection", "fair_processing", "equitable_access"],
        "weight": 0.9
    },
    "accountability": {
        "principle": "Clear accountability for data processing decisions",
        "requirements": ["responsible_party", "governance_framework", "compliance_monitoring"],
        "weight": 0.85
    }
}

# Data access authorization
allow_data_access if {
    requestor := input.requestor
    data_resource := input.data_resource
    access_purpose := input.access_purpose

    # Validate requestor authorization
    requestor_authorized(requestor, data_resource)

    # Check data classification and access requirements
    classification_requirements_met(data_resource, requestor)

    # Verify purpose legitimacy
    purpose_legitimate(access_purpose, data_resource)

    # Constitutional compliance check
    constitutional_principles_satisfied(requestor, data_resource, access_purpose)

    # Privacy regulation compliance
    privacy_regulations_compliant(requestor, data_resource, access_purpose)

    # Audit trail enabled
    audit_trail_enabled(requestor, data_resource)
}

# Data processing authorization
allow_data_processing if {
    processor := input.processor
    data_resource := input.data_resource
    processing_purpose := input.processing_purpose
    processing_method := input.processing_method

    # Processor must be authorized
    processor_authorized(processor, data_resource)

    # Processing purpose must be legitimate
    processing_purpose_legitimate(processing_purpose, data_resource)

    # Processing method must be appropriate
    processing_method_appropriate(processing_method, data_resource)

    # Data subject consent obtained (if required)
    consent_requirements_met(data_resource, processing_purpose)

    # Technical and organizational measures in place
    technical_measures_adequate(processing_method, data_resource)

    # Constitutional compliance verified
    processing_constitutional_compliant(processor, data_resource, processing_purpose)
}

# Data sharing authorization
allow_data_sharing if {
    sharer := input.sharer
    recipient := input.recipient
    data_resource := input.data_resource
    sharing_purpose := input.sharing_purpose

    # Both parties must be authorized
    sharer_authorized(sharer, data_resource)
    recipient_authorized(recipient, data_resource)

    # Sharing purpose must be legitimate
    sharing_purpose_legitimate(sharing_purpose, data_resource)

    # Data transfer protections in place
    transfer_protections_adequate(sharer, recipient, data_resource)

    # Cross-border transfer compliance (if applicable)
    cross_border_compliance_verified(sharer, recipient, data_resource)

    # Data subject rights protected
    data_subject_rights_protected(data_resource, sharing_purpose)

    # Constitutional principles maintained
    sharing_constitutional_compliant(sharer, recipient, data_resource)
}

# Data retention authorization
allow_data_retention if {
    custodian := input.custodian
    data_resource := input.data_resource
    retention_period := input.retention_period
    retention_purpose := input.retention_purpose

    # Custodian authorized for retention
    custodian_retention_authorized(custodian, data_resource)

    # Retention period within limits
    retention_period_compliant(data_resource, retention_period)

    # Retention purpose legitimate
    retention_purpose_legitimate(retention_purpose, data_resource)

    # Security measures adequate for retention
    retention_security_adequate(custodian, data_resource, retention_period)

    # Disposal plan exists
    disposal_plan_exists(custodian, data_resource)
}

# Helper functions for access control
requestor_authorized(requestor, data_resource) if {
    # Check role-based access
    requestor.role in data_resource.authorized_roles

    # Check individual permissions
    requestor.id in data_resource.authorized_users

    # Verify requestor authentication
    requestor.authenticated == true
    requestor.multi_factor_verified == true
}

requestor_authorized(requestor, data_resource) if {
    # Check group-based access
    some group in requestor.groups
    group in data_resource.authorized_groups

    # Verify group membership is current
    group_membership_current(requestor, group)
}

classification_requirements_met(data_resource, requestor) if {
    classification := data_classification_levels[data_resource.classification]

    # Check protection level clearance
    requestor.clearance_level >= classification.protection_level

    # Check access approval if required
    access_approval_satisfied(data_resource, requestor, classification)

    # Multi-party access if required
    multi_party_access_satisfied(data_resource, requestor, classification)
}

access_approval_satisfied(data_resource, requestor, classification) if {
    not classification.access_approval_required
}

access_approval_satisfied(data_resource, requestor, classification) if {
    classification.access_approval_required
    approval := data_resource.access_approvals[requestor.id]
    approval.status == "approved"
    approval.expires_at > time.now_ns()
}

multi_party_access_satisfied(data_resource, requestor, classification) if {
    not classification.multi_party_access_required
}

multi_party_access_satisfied(data_resource, requestor, classification) if {
    classification.multi_party_access_required
    approvals := data_resource.multi_party_approvals[requestor.id]
    count(approvals) >= 2
    all(approval, approval in approvals; approval.status == "approved")
}

purpose_legitimate(purpose, data_resource) if {
    purpose.type in data_resource.allowed_purposes
    purpose.description
    purpose.legal_basis
    purpose.data_minimization_applied == true
}

# Constitutional compliance validation
constitutional_principles_satisfied(requestor, data_resource, purpose) if {
    all(principle_name, principle in constitutional_data_principles;
        data_principle_satisfied(principle_name, principle, requestor, data_resource, purpose))
}

data_principle_satisfied(principle_name, principle, requestor, data_resource, purpose) if {
    all(requirement, requirement in principle.requirements;
        principle_requirement_met(requirement, requestor, data_resource, purpose))
}

principle_requirement_met("consent_verification", requestor, data_resource, purpose) if {
    not data_resource.personal_data
} else {
    consent := data_resource.consent_records[data_resource.data_subject_id]
    consent.valid == true
    consent.purpose_covers(purpose.type)
    consent.expires_at > time.now_ns()
}

principle_requirement_met("purpose_limitation", requestor, data_resource, purpose) if {
    purpose.type in data_resource.allowed_purposes
    purpose.scope_limited == true
}

principle_requirement_met("data_minimization", requestor, data_resource, purpose) if {
    purpose.data_minimization_applied == true
    data_resource.fields_requested <= data_resource.minimum_required_fields
}

principle_requirement_met("access_control", requestor, data_resource, purpose) if {
    requestor_authorized(requestor, data_resource)
    access_controls_enforced(data_resource)
}

principle_requirement_met("encryption", requestor, data_resource, purpose) if {
    classification := data_classification_levels[data_resource.classification]
    not classification.encryption_required
} else {
    data_resource.encrypted == true
    data_resource.encryption_algorithm in ["AES-256", "ChaCha20-Poly1305"]
}

principle_requirement_met("anonymization", requestor, data_resource, purpose) if {
    not data_resource.personal_data
} else {
    data_resource.anonymization_applied == true
    data_resource.re_identification_risk <= 0.05
}

# Privacy regulation compliance
privacy_regulations_compliant(requestor, data_resource, purpose) if {
    applicable_regulations := determine_applicable_regulations(data_resource)
    all(regulation, regulation in applicable_regulations;
        regulation_compliant(regulation, requestor, data_resource, purpose))
}

determine_applicable_regulations(data_resource) := regulations if {
    regulations := [reg_name |
        some reg_name, regulation in privacy_regulations
        regulation_applies(regulation, data_resource)
    ]
}

regulation_applies(regulation, data_resource) if {
    data_resource.jurisdiction == regulation.jurisdiction
    data_resource.personal_data == true
}

regulation_compliant("gdpr", requestor, data_resource, purpose) if {
    # GDPR specific requirements
    gdpr_consent_obtained(data_resource, purpose)
    gdpr_legal_basis_exists(purpose)
    gdpr_data_subject_rights_respected(data_resource)
    gdpr_privacy_by_design_implemented(data_resource)
}

regulation_compliant("ccpa", requestor, data_resource, purpose) if {
    # CCPA specific requirements
    ccpa_consumer_rights_respected(data_resource)
    ccpa_opt_out_honored(data_resource, purpose)
    ccpa_transparency_provided(data_resource, purpose)
}

regulation_compliant("pipeda", requestor, data_resource, purpose) if {
    # PIPEDA specific requirements
    pipeda_consent_obtained(data_resource, purpose)
    pipeda_purpose_limitation_applied(purpose)
    pipeda_data_minimization_applied(data_resource, purpose)
}

# Processing validation
processor_authorized(processor, data_resource) if {
    processor.id in data_resource.authorized_processors
    processor.data_processing_agreement_signed == true
    processor.security_assessment_passed == true
    processor.constitutional_compliance_verified == true
}

processing_purpose_legitimate(purpose, data_resource) if {
    purpose.type in data_resource.allowed_processing_purposes
    purpose.necessity_demonstrated == true
    purpose.proportionality_assessed == true
    purpose.alternative_analysis_completed == true
}

processing_method_appropriate(method, data_resource) if {
    method.security_level >= required_security_level(data_resource)
    method.data_protection_measures_adequate == true
    method.constitutional_safeguards_implemented == true
}

required_security_level(data_resource) := level if {
    classification := data_classification_levels[data_resource.classification]
    level := classification.protection_level
}

consent_requirements_met(data_resource, purpose) if {
    not data_resource.personal_data
} else {
    consent := data_resource.consent_records[data_resource.data_subject_id]
    consent_valid_for_purpose(consent, purpose)
}

consent_valid_for_purpose(consent, purpose) if {
    consent.valid == true
    consent.specific == true
    consent.informed == true
    consent.freely_given == true
    purpose.type in consent.purposes
    consent.expires_at > time.now_ns()
}

technical_measures_adequate(method, data_resource) if {
    # Encryption in transit and at rest
    method.encryption_in_transit == true
    method.encryption_at_rest == true

    # Access controls
    method.access_controls_implemented == true
    method.authentication_required == true
    method.authorization_verified == true

    # Audit logging
    method.audit_logging_enabled == true
    method.integrity_monitoring_enabled == true

    # Data protection specific to classification
    classification_specific_measures_implemented(method, data_resource)
}

classification_specific_measures_implemented(method, data_resource) if {
    classification := data_classification_levels[data_resource.classification]

    # Apply measures based on classification level
    protection_measures_for_level(method, classification.protection_level)
}

protection_measures_for_level(method, "maximum") if {
    method.hardware_security_module == true
    method.secure_enclaves == true
    method.zero_trust_architecture == true
    method.continuous_monitoring == true
}

protection_measures_for_level(method, "high") if {
    method.key_management_system == true
    method.data_loss_prevention == true
    method.privileged_access_management == true
}

protection_measures_for_level(method, "standard") if {
    method.encryption_key_rotation == true
    method.secure_backup_procedures == true
    method.incident_response_plan == true
}

protection_measures_for_level(method, "basic") if {
    method.basic_encryption == true
    method.access_logging == true
}

# Data sharing validation
transfer_protections_adequate(sharer, recipient, data_resource) if {
    # Adequate level of protection at recipient
    recipient.data_protection_level >= required_protection_level(data_resource)

    # Transfer security measures
    transfer_encryption_enabled(sharer, recipient)
    transfer_integrity_verified(sharer, recipient)
    transfer_audit_trail_maintained(sharer, recipient)

    # Contractual protections
    data_processing_agreement_exists(sharer, recipient, data_resource)
}

required_protection_level(data_resource) := level if {
    classification := data_classification_levels[data_resource.classification]
    level := classification.protection_level
}

cross_border_compliance_verified(sharer, recipient, data_resource) if {
    # If not cross-border, no additional requirements
    sharer.jurisdiction == recipient.jurisdiction
}

cross_border_compliance_verified(sharer, recipient, data_resource) if {
    # Cross-border transfer must be allowed
    classification := data_classification_levels[data_resource.classification]
    classification.cross_border_transfer_allowed == true

    # Adequacy decision or appropriate safeguards
    transfer_mechanism_adequate(sharer, recipient, data_resource)
}

transfer_mechanism_adequate(sharer, recipient, data_resource) if {
    # Adequacy decision exists
    adequacy_decision_exists(sharer.jurisdiction, recipient.jurisdiction)
}

transfer_mechanism_adequate(sharer, recipient, data_resource) if {
    # Standard contractual clauses
    standard_contractual_clauses_executed(sharer, recipient)
    supplementary_measures_implemented(sharer, recipient, data_resource)
}

# Data retention validation
retention_period_compliant(data_resource, retention_period) if {
    classification := data_classification_levels[data_resource.classification]
    retention_period <= classification.retention_limit_days

    # Legal retention requirements satisfied
    legal_retention_requirements_met(data_resource, retention_period)

    # Business justification exists
    business_justification_adequate(data_resource, retention_period)
}

legal_retention_requirements_met(data_resource, retention_period) if {
    applicable_laws := determine_applicable_retention_laws(data_resource)
    all(law, law in applicable_laws;
        law.minimum_retention <= retention_period
        retention_period <= law.maximum_retention)
}

disposal_plan_exists(custodian, data_resource) if {
    disposal_plan := custodian.data_disposal_plans[data_resource.id]
    disposal_plan.method in ["secure_deletion", "cryptographic_erasure", "physical_destruction"]
    disposal_plan.verification_process_defined == true
    disposal_plan.certificate_of_destruction_required == true
    disposal_plan.constitutional_compliance_verified == true
}

# Data governance scoring
data_governance_score := score if {
    access_score := calculate_access_governance_score(input)
    processing_score := calculate_processing_governance_score(input)
    sharing_score := calculate_sharing_governance_score(input)
    retention_score := calculate_retention_governance_score(input)

    score := (access_score + processing_score + sharing_score + retention_score) / 4
}

calculate_access_governance_score(input) := score if {
    base_score := 0.5

    # Constitutional compliance bonus
    constitutional_bonus := constitutional_compliance_bonus(input)

    # Privacy regulation compliance bonus
    privacy_bonus := privacy_regulation_compliance_bonus(input)

    # Security measures bonus
    security_bonus := security_measures_bonus(input)

    score := base_score + constitutional_bonus + privacy_bonus + security_bonus
}

constitutional_compliance_bonus(input) := bonus if {
    violations := count([v |
        some principle_name, principle in constitutional_data_principles
        not data_principle_satisfied(principle_name, principle, input.requestor, input.data_resource, input.purpose)
    ])
    bonus := max(0, 0.3 - (violations * 0.1))
}

privacy_regulation_compliance_bonus(input) := bonus if {
    applicable_regs := determine_applicable_regulations(input.data_resource)
    compliant_regs := count([reg |
        some reg in applicable_regs
        regulation_compliant(reg, input.requestor, input.data_resource, input.purpose)
    ])

    bonus := (compliant_regs / count(applicable_regs)) * 0.2
}

security_measures_bonus(input) := bonus if {
    security_score := calculate_security_measures_score(input)
    bonus := security_score * 0.2
}

calculate_security_measures_score(input) := score if {
    measures := [
        input.data_resource.encrypted,
        input.requestor.multi_factor_verified,
        audit_trail_enabled(input.requestor, input.data_resource),
        access_controls_enforced(input.data_resource)
    ]

    implemented_measures := count([m | m := measures[_]; m == true])
    score := implemented_measures / count(measures)
}
