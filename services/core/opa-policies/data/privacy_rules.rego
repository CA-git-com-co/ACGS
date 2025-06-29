# ACGS-1 Lite Data Privacy Rules
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.data

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Constitutional hash verification
constitutional_hash := "cdd01ef066bc6cf2"

# Data classification levels
data_classifications := {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3,
    "top_secret": 4
}

# Sensitive data categories requiring special protection
sensitive_data_categories := {
    "personal_identifiable_information",
    "financial_information",
    "health_records",
    "biometric_data",
    "authentication_credentials",
    "cryptographic_keys",
    "trade_secrets",
    "legal_documents"
}

# Main data access evaluation
evaluate = response {
    input.type == "data_access"
    data_request := input.data_request
    
    # Evaluate all data access criteria
    classification_check := check_data_classification(data_request)
    consent_check := check_user_consent(data_request)
    purpose_check := check_purpose_limitation(data_request)
    minimization_check := check_data_minimization(data_request)
    retention_check := check_retention_policies(data_request)
    encryption_check := check_encryption_requirements(data_request)
    
    # Calculate overall data access score
    access_score := calculate_data_access_score([
        classification_check,
        consent_check,
        purpose_check,
        minimization_check,
        retention_check,
        encryption_check
    ])
    
    # Determine if access is allowed
    access_allowed := access_score >= 0.95
    
    # Compile all privacy concerns
    all_concerns := array.concat([
        classification_check.concerns,
        consent_check.concerns,
        purpose_check.concerns,
        minimization_check.concerns,
        retention_check.concerns,
        encryption_check.concerns
    ])
    
    response := {
        "allow": access_allowed,
        "access_score": access_score,
        "constitutional_hash": constitutional_hash,
        "concerns": all_concerns,
        "privacy_evaluation": {
            "classification": classification_check,
            "consent": consent_check,
            "purpose": purpose_check,
            "minimization": minimization_check,
            "retention": retention_check,
            "encryption": encryption_check
        },
        "access_conditions": determine_access_conditions(data_request, access_score),
        "audit_requirements": determine_audit_requirements(data_request)
    }
}

# Data classification compliance check
check_data_classification(data_request) = result {
    requested_data := object.get(data_request, "data_fields", [])
    requester_clearance := object.get(data_request, "requester_clearance_level", 0)
    
    # Check each requested data field
    classification_violations := [violation |
        field := requested_data[_]
        field_classification := object.get(field, "classification_level", 1)
        field_classification > requester_clearance
        violation := sprintf("Insufficient clearance for field %s (required: %d, have: %d)", 
                           [field.name, field_classification, requester_clearance])
    ]
    
    # Check for sensitive data categories
    sensitive_data_access := [access |
        field := requested_data[_]
        field.category in sensitive_data_categories
        access := field.category
    ]
    
    # Special authorization required for sensitive categories
    sensitive_violations := [violation |
        category := sensitive_data_access[_]
        not object.get(data_request, "special_authorization", false)
        violation := sprintf("Special authorization required for sensitive category: %s", [category])
    ]
    
    all_violations := array.concat(classification_violations, sensitive_violations)
    
    classification_score := calculate_classification_score(
        count(classification_violations),
        count(sensitive_violations),
        count(requested_data)
    )
    
    result := {
        "passed": classification_score >= 0.9,
        "score": classification_score,
        "concerns": all_violations,
        "sensitive_categories": sensitive_data_access,
        "clearance_level": requester_clearance
    }
}

# User consent verification
check_user_consent(data_request) = result {
    data_subjects := object.get(data_request, "data_subjects", [])
    consent_provided := object.get(data_request, "consent_records", [])
    
    # Check consent for each data subject
    consent_violations := [violation |
        subject := data_subjects[_]
        not subject_has_consent(subject, consent_provided)
        violation := sprintf("No valid consent found for data subject: %s", [subject])
    ]
    
    # Check consent specificity
    purpose := object.get(data_request, "purpose", "")
    consent_specific_violations := [violation |
        consent := consent_provided[_]
        purpose != ""
        not purpose in consent.allowed_purposes
        violation := sprintf("Consent does not cover purpose: %s", [purpose])
    ]
    
    # Check consent expiration
    current_time := object.get(data_request, "timestamp", 0)
    expired_consent_violations := [violation |
        consent := consent_provided[_]
        consent.expiry_time < current_time
        violation := sprintf("Consent expired for subject: %s", [consent.subject_id])
    ]
    
    all_consent_violations := array.concat([
        consent_violations,
        consent_specific_violations,
        expired_consent_violations
    ])
    
    consent_score := calculate_consent_score(
        count(data_subjects),
        count(consent_violations),
        count(consent_specific_violations),
        count(expired_consent_violations)
    )
    
    result := {
        "passed": consent_score >= 0.95,
        "score": consent_score,
        "concerns": all_consent_violations,
        "consent_status": analyze_consent_status(data_subjects, consent_provided)
    }
}

# Purpose limitation check
check_purpose_limitation(data_request) = result {
    stated_purpose := object.get(data_request, "purpose", "")
    allowed_purposes := object.get(data_request, "allowed_purposes", [])
    
    # Check if purpose is specified
    purpose_specified := stated_purpose != ""
    
    # Check if purpose is allowed
    purpose_allowed := stated_purpose in allowed_purposes
    
    # Check for purpose creep indicators
    historical_purposes := object.get(data_request, "historical_purposes", [])
    purpose_drift := check_purpose_drift(stated_purpose, historical_purposes)
    
    concerns := [concern |
        not purpose_specified
        concern := "Data access purpose not specified"
    ]
    
    concerns2 := array.concat(concerns, [concern |
        purpose_specified
        not purpose_allowed
        concern := sprintf("Purpose '%s' not in allowed purposes", [stated_purpose])
    ])
    
    concerns3 := array.concat(concerns2, [concern |
        purpose_drift.detected
        concern := sprintf("Purpose drift detected: %s", [purpose_drift.description])
    ])
    
    purpose_score := calculate_purpose_score(
        purpose_specified,
        purpose_allowed,
        purpose_drift.score
    )
    
    result := {
        "passed": purpose_score >= 0.9,
        "score": purpose_score,
        "concerns": concerns3,
        "purpose_analysis": {
            "stated_purpose": stated_purpose,
            "allowed_purposes": allowed_purposes,
            "purpose_drift": purpose_drift
        }
    }
}

# Data minimization check
check_data_minimization(data_request) = result {
    requested_fields := object.get(data_request, "data_fields", [])
    justified_fields := object.get(data_request, "justified_fields", [])
    purpose := object.get(data_request, "purpose", "")
    
    # Check if data request is minimized
    excessive_data := [field |
        field := requested_fields[_]
        not field.name in justified_fields
    ]
    
    # Check field necessity justification
    unjustified_fields := [field |
        field := requested_fields[_]
        field.name in justified_fields
        not field_necessity_justified(field, purpose)
    ]
    
    # Check for bulk data access patterns
    bulk_access_indicators := check_bulk_access_patterns(data_request)
    
    concerns := [concern |
        field := excessive_data[_]
        concern := sprintf("Excessive data requested: field '%s' not justified", [field.name])
    ]
    
    concerns2 := array.concat(concerns, [concern |
        field := unjustified_fields[_]
        concern := sprintf("Field necessity not justified: '%s'", [field.name])
    ])
    
    concerns3 := array.concat(concerns2, [concern |
        indicator := bulk_access_indicators[_]
        concern := sprintf("Bulk access indicator: %s", [indicator])
    ])
    
    minimization_score := calculate_minimization_score(
        count(requested_fields),
        count(excessive_data),
        count(unjustified_fields),
        count(bulk_access_indicators)
    )
    
    result := {
        "passed": minimization_score >= 0.85,
        "score": minimization_score,
        "concerns": concerns3,
        "minimization_analysis": {
            "total_requested": count(requested_fields),
            "excessive_fields": count(excessive_data),
            "unjustified_fields": count(unjustified_fields),
            "bulk_indicators": count(bulk_access_indicators)
        }
    }
}

# Data retention policy check
check_retention_policies(data_request) = result {
    retention_policy := object.get(data_request, "retention_policy", {})
    data_categories := extract_data_categories(data_request)
    
    # Check if retention policy is specified
    has_retention_policy := count(object.keys(retention_policy)) > 0
    
    # Check retention periods against regulatory requirements
    retention_violations := check_retention_compliance(retention_policy, data_categories)
    
    # Check data disposal procedures
    disposal_procedures := object.get(retention_policy, "disposal_procedures", {})
    disposal_adequate := check_disposal_adequacy(disposal_procedures)
    
    concerns := [concern |
        not has_retention_policy
        concern := "No data retention policy specified"
    ]
    
    concerns2 := array.concat(concerns, [concern |
        violation := retention_violations[_]
        concern := sprintf("Retention policy violation: %s", [violation])
    ])
    
    concerns3 := array.concat(concerns2, [concern |
        not disposal_adequate.adequate
        concern := sprintf("Inadequate disposal procedures: %s", [disposal_adequate.reason])
    ])
    
    retention_score := calculate_retention_score(
        has_retention_policy,
        count(retention_violations),
        disposal_adequate.adequate
    )
    
    result := {
        "passed": retention_score >= 0.9,
        "score": retention_score,
        "concerns": concerns3,
        "retention_analysis": {
            "has_policy": has_retention_policy,
            "violations": retention_violations,
            "disposal_adequate": disposal_adequate
        }
    }
}

# Encryption requirements check
check_encryption_requirements(data_request) = result {
    data_fields := object.get(data_request, "data_fields", [])
    encryption_config := object.get(data_request, "encryption_config", {})
    
    # Check encryption for sensitive data
    encryption_violations := [violation |
        field := data_fields[_]
        field.category in sensitive_data_categories
        not field_properly_encrypted(field, encryption_config)
        violation := sprintf("Sensitive field '%s' requires encryption", [field.name])
    ]
    
    # Check encryption strength
    encryption_strength_violations := [violation |
        config := encryption_config[_]
        not adequate_encryption_strength(config)
        violation := sprintf("Inadequate encryption strength: %s", [config.algorithm])
    ]
    
    # Check key management
    key_management_check := check_key_management(encryption_config)
    
    all_encryption_violations := array.concat([
        encryption_violations,
        encryption_strength_violations,
        key_management_check.violations
    ])
    
    encryption_score := calculate_encryption_score(
        count(data_fields),
        count(encryption_violations),
        count(encryption_strength_violations),
        key_management_check.score
    )
    
    result := {
        "passed": encryption_score >= 0.95,
        "score": encryption_score,
        "concerns": all_encryption_violations,
        "encryption_analysis": {
            "required_encryptions": count(encryption_violations),
            "strength_issues": count(encryption_strength_violations),
            "key_management": key_management_check
        }
    }
}

# Helper functions

subject_has_consent(subject, consent_records) = has_consent {
    some consent in consent_records
    consent.subject_id == subject
    consent.status == "granted"
    has_consent := true
}

subject_has_consent(subject, consent_records) = has_consent {
    not some consent in consent_records
    has_consent := false
}

check_purpose_drift(current_purpose, historical_purposes) = result {
    # Simple purpose drift detection
    drift_detected := count(historical_purposes) > 0 and not current_purpose in historical_purposes
    
    result := {
        "detected": drift_detected,
        "score": 1.0 if not drift_detected else 0.5,
        "description": "Purpose differs from historical patterns" if drift_detected else "No drift detected"
    }
}

field_necessity_justified(field, purpose) = justified {
    # Check if field is necessary for stated purpose
    necessary_for_purpose := field.purpose_relevance >= 0.7
    justified := necessary_for_purpose
}

check_bulk_access_patterns(data_request) = indicators {
    base_indicators := []
    
    # Large number of records
    record_count := object.get(data_request, "record_count", 0)
    indicators1 := array.concat(base_indicators, ["large_record_count"]) if record_count > 1000
    
    # Wide field selection
    field_count := count(object.get(data_request, "data_fields", []))
    indicators2 := array.concat(indicators1, ["wide_field_selection"]) if field_count > 10
    
    # Automated request
    is_automated := object.get(data_request, "automated_request", false)
    indicators3 := array.concat(indicators2, ["automated_request"]) if is_automated
    
    indicators := indicators3
}

extract_data_categories(data_request) = categories {
    data_fields := object.get(data_request, "data_fields", [])
    categories := [field.category | field := data_fields[_]]
}

check_retention_compliance(retention_policy, data_categories) = violations {
    # Regulatory retention limits by category
    regulatory_limits := {
        "personal_identifiable_information": 2557600,  # 30 days in seconds
        "financial_information": 31536000,             # 1 year
        "health_records": 315360000,                   # 10 years
        "authentication_credentials": 86400            # 1 day
    }
    
    violations := [violation |
        category := data_categories[_]
        category in object.keys(regulatory_limits)
        retention_period := object.get(retention_policy, category, 0)
        max_allowed := regulatory_limits[category]
        retention_period > max_allowed
        violation := sprintf("Category %s retention exceeds limit: %d > %d seconds", 
                           [category, retention_period, max_allowed])
    ]
}

check_disposal_adequacy(disposal_procedures) = result {
    required_elements := ["method", "verification", "documentation", "timeline"]
    missing_elements := [element |
        element := required_elements[_]
        not object.get(disposal_procedures, element, null)
    ]
    
    result := {
        "adequate": count(missing_elements) == 0,
        "reason": sprintf("Missing disposal elements: %s", [missing_elements]) if count(missing_elements) > 0 else "All elements present"
    }
}

field_properly_encrypted(field, encryption_config) = encrypted {
    field_config := object.get(encryption_config, field.name, {})
    encrypted := object.get(field_config, "encrypted", false)
}

adequate_encryption_strength(config) = adequate {
    algorithm := object.get(config, "algorithm", "")
    key_length := object.get(config, "key_length", 0)
    
    strong_algorithms := {
        "AES": 256,
        "ChaCha20": 256,
        "RSA": 2048
    }
    
    required_length := object.get(strong_algorithms, algorithm, 0)
    adequate := required_length > 0 and key_length >= required_length
}

check_key_management(encryption_config) = result {
    key_management := object.get(encryption_config, "key_management", {})
    
    violations := []
    
    # Check key rotation
    violations1 := array.concat(violations, ["No key rotation policy"]) if {
        not object.get(key_management, "rotation_enabled", false)
    }
    
    # Check key storage
    violations2 := array.concat(violations1, ["Insecure key storage"]) if {
        not object.get(key_management, "secure_storage", false)
    }
    
    # Check access controls
    violations3 := array.concat(violations2, ["Inadequate key access controls"]) if {
        not object.get(key_management, "access_controlled", false)
    }
    
    key_mgmt_score := max([0.0, 1.0 - (count(violations3) * 0.25)])
    
    result := {
        "score": key_mgmt_score,
        "violations": violations3
    }
}

analyze_consent_status(data_subjects, consent_records) = status {
    consented_subjects := [subject |
        subject := data_subjects[_]
        subject_has_consent(subject, consent_records)
    ]
    
    status := {
        "total_subjects": count(data_subjects),
        "consented_subjects": count(consented_subjects),
        "consent_rate": count(consented_subjects) / count(data_subjects)
    }
}

determine_access_conditions(data_request, access_score) = conditions {
    base_conditions := []
    
    # Enhanced monitoring for lower scores
    conditions1 := array.concat(base_conditions, ["enhanced_monitoring"]) if access_score < 0.9
    
    # Time-limited access
    conditions2 := array.concat(conditions1, ["time_limited_access"]) if access_score < 0.8
    
    # Approval required
    conditions3 := array.concat(conditions2, ["supervisor_approval"]) if access_score < 0.7
    
    conditions := conditions3
}

determine_audit_requirements(data_request) = requirements {
    sensitive_count := count([field |
        field := object.get(data_request, "data_fields", [])[_]
        field.category in sensitive_data_categories
    ])
    
    base_requirements := ["basic_audit_trail"]
    
    # Enhanced auditing for sensitive data
    requirements1 := array.concat(base_requirements, ["detailed_access_log"]) if sensitive_count > 0
    
    # Real-time monitoring for high-volume access
    record_count := object.get(data_request, "record_count", 0)
    requirements2 := array.concat(requirements1, ["real_time_monitoring"]) if record_count > 100
    
    requirements := requirements2
}

# Scoring functions

calculate_classification_score(classification_violations, sensitive_violations, total_fields) = score {
    base_score := 1.0
    classification_penalty := min([0.5, classification_violations * 0.1])
    sensitive_penalty := min([0.3, sensitive_violations * 0.15])
    
    score := max([0.0, base_score - classification_penalty - sensitive_penalty])
}

calculate_consent_score(total_subjects, consent_violations, specific_violations, expired_violations) = score {
    if total_subjects == 0 {
        score := 1.0
    } else {
        base_score := 1.0
        consent_penalty := min([0.8, consent_violations / total_subjects])
        specific_penalty := min([0.1, specific_violations * 0.05])
        expired_penalty := min([0.1, expired_violations * 0.05])
        
        score := max([0.0, base_score - consent_penalty - specific_penalty - expired_penalty])
    }
}

calculate_purpose_score(purpose_specified, purpose_allowed, drift_score) = score {
    base_score := 0.0
    base_score := 0.4 if purpose_specified
    base_score := 0.8 if purpose_specified and purpose_allowed
    
    drift_penalty := (1.0 - drift_score) * 0.2
    
    score := max([0.0, base_score + drift_score * 0.2 - drift_penalty])
}

calculate_minimization_score(total_fields, excessive_fields, unjustified_fields, bulk_indicators) = score {
    if total_fields == 0 {
        score := 1.0
    } else {
        base_score := 1.0
        excessive_penalty := (excessive_fields / total_fields) * 0.4
        unjustified_penalty := (unjustified_fields / total_fields) * 0.3
        bulk_penalty := min([0.3, bulk_indicators * 0.1])
        
        score := max([0.0, base_score - excessive_penalty - unjustified_penalty - bulk_penalty])
    }
}

calculate_retention_score(has_policy, violation_count, disposal_adequate) = score {
    base_score := 0.5 if has_policy else 0.0
    violation_penalty := min([0.3, violation_count * 0.1])
    disposal_bonus := 0.3 if disposal_adequate else 0.0
    policy_bonus := 0.2 if has_policy else 0.0
    
    score := max([0.0, base_score + policy_bonus + disposal_bonus - violation_penalty])
}

calculate_encryption_score(total_fields, encryption_violations, strength_violations, key_mgmt_score) = score {
    if total_fields == 0 {
        score := 1.0
    } else {
        base_score := 0.7
        encryption_penalty := min([0.5, encryption_violations / total_fields])
        strength_penalty := min([0.2, strength_violations * 0.1])
        key_mgmt_bonus := key_mgmt_score * 0.3
        
        score := max([0.0, base_score - encryption_penalty - strength_penalty + key_mgmt_bonus])
    }
}

calculate_data_access_score(checks) = score {
    # Weighted average with privacy-critical checks having higher weight
    weights := [0.2, 0.25, 0.15, 0.15, 0.1, 0.15]  # Classification, consent, purpose, minimization, retention, encryption
    
    weighted_sum := sum([checks[i].score * weights[i] | i := range(0, count(checks))])
    
    score := weighted_sum
}