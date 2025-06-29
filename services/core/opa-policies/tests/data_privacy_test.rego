# ACGS-1 Lite Data Privacy Test Suite
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.data_test

import data.acgs.data
import data.acgs.main

# Test public data access
test_public_data_access_allowed {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "public_metrics", "classification_level": 0, "category": "analytics"}
            ],
            "requester_clearance_level": 0,
            "purpose": "dashboard_display",
            "allowed_purposes": ["dashboard_display", "reporting"],
            "justified_fields": ["public_metrics"],
            "timestamp": 1704067200,
            "retention_policy": {
                "analytics": 2592000  # 30 days
            },
            "encryption_config": {
                "public_metrics": {"encrypted": false}  # Public data doesn't need encryption
            }
        }
    }
    
    result.allow == true
    result.access_score >= 0.95
}

# Test sensitive data access with proper authorization
test_sensitive_data_access_with_authorization {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_email", "classification_level": 2, "category": "personal_identifiable_information"}
            ],
            "requester_clearance_level": 3,
            "special_authorization": true,
            "data_subjects": ["user123"],
            "consent_records": [
                {
                    "subject_id": "user123",
                    "status": "granted",
                    "allowed_purposes": ["user_communication", "account_management"],
                    "expiry_time": 1735689600  # Future timestamp
                }
            ],
            "purpose": "user_communication",
            "allowed_purposes": ["user_communication", "account_management"],
            "justified_fields": ["user_email"],
            "timestamp": 1704067200,
            "retention_policy": {
                "personal_identifiable_information": 2592000  # 30 days
            },
            "encryption_config": {
                "user_email": {
                    "encrypted": true,
                    "algorithm": "AES",
                    "key_length": 256
                },
                "key_management": {
                    "rotation_enabled": true,
                    "secure_storage": true,
                    "access_controlled": true
                }
            }
        }
    }
    
    result.allow == true
    result.access_score >= 0.95
}

# Test insufficient clearance level
test_insufficient_clearance_blocked {
    result := data.evaluate with input as {
        "type": "data_access", 
        "data_request": {
            "data_fields": [
                {"name": "classified_data", "classification_level": 3, "category": "confidential"}
            ],
            "requester_clearance_level": 1,  # Insufficient clearance
            "purpose": "analysis",
            "allowed_purposes": ["analysis"],
            "justified_fields": ["classified_data"],
            "timestamp": 1704067200
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "Insufficient clearance")]) >= 1
}

# Test missing consent
test_missing_consent_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_profile", "classification_level": 2, "category": "personal_identifiable_information"}
            ],
            "requester_clearance_level": 3,
            "special_authorization": true,
            "data_subjects": ["user456"],
            "consent_records": [],  # No consent provided
            "purpose": "marketing",
            "allowed_purposes": ["marketing"],
            "justified_fields": ["user_profile"],
            "timestamp": 1704067200
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "No valid consent")]) >= 1
}

# Test expired consent
test_expired_consent_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_data", "classification_level": 2, "category": "personal_identifiable_information"}
            ],
            "requester_clearance_level": 3,
            "special_authorization": true,
            "data_subjects": ["user789"],
            "consent_records": [
                {
                    "subject_id": "user789",
                    "status": "granted",
                    "allowed_purposes": ["analytics"],
                    "expiry_time": 1640995200  # Past timestamp
                }
            ],
            "purpose": "analytics",
            "allowed_purposes": ["analytics"],
            "justified_fields": ["user_data"],
            "timestamp": 1704067200
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "Consent expired")]) >= 1
}

# Test purpose limitation violation
test_purpose_not_allowed_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_behavior", "classification_level": 1, "category": "analytics"}
            ],
            "requester_clearance_level": 2,
            "purpose": "unauthorized_tracking",  # Not in allowed purposes
            "allowed_purposes": ["analytics", "reporting"],
            "justified_fields": ["user_behavior"],
            "timestamp": 1704067200
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "not in allowed purposes")]) >= 1
}

# Test data minimization violation
test_excessive_data_request_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_email", "classification_level": 1, "category": "contact"},
                {"name": "user_phone", "classification_level": 1, "category": "contact"},
                {"name": "user_address", "classification_level": 2, "category": "personal_identifiable_information"},
                {"name": "user_ssn", "classification_level": 3, "category": "personal_identifiable_information"}
            ],
            "requester_clearance_level": 3,
            "purpose": "email_notification",
            "allowed_purposes": ["email_notification"],
            "justified_fields": ["user_email"],  # Only email justified for email notification
            "timestamp": 1704067200
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "Excessive data requested")]) >= 3
}

# Test bulk access pattern detection
test_bulk_access_flagged {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_id", "classification_level": 1, "category": "identifier"},
                {"name": "user_email", "classification_level": 2, "category": "personal_identifiable_information"},
                {"name": "user_phone", "classification_level": 2, "category": "personal_identifiable_information"},
                {"name": "user_name", "classification_level": 2, "category": "personal_identifiable_information"},
                {"name": "user_address", "classification_level": 2, "category": "personal_identifiable_information"},
                {"name": "user_dob", "classification_level": 3, "category": "personal_identifiable_information"},
                {"name": "user_preferences", "classification_level": 1, "category": "settings"},
                {"name": "user_activity", "classification_level": 1, "category": "analytics"},
                {"name": "user_purchases", "classification_level": 2, "category": "financial_information"},
                {"name": "user_payment", "classification_level": 3, "category": "financial_information"},
                {"name": "user_location", "classification_level": 2, "category": "location_data"}
            ],
            "requester_clearance_level": 3,
            "record_count": 5000,  # Large record count
            "automated_request": true,
            "purpose": "bulk_analysis",
            "allowed_purposes": ["bulk_analysis"],
            "justified_fields": ["user_id", "user_email", "user_phone", "user_name", "user_address", "user_dob", "user_preferences", "user_activity", "user_purchases", "user_payment", "user_location"],
            "timestamp": 1704067200
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "Bulk access indicator")]) >= 3
}

# Test encryption requirements
test_unencrypted_sensitive_data_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "credit_card", "classification_level": 3, "category": "financial_information"}
            ],
            "requester_clearance_level": 4,
            "special_authorization": true,
            "purpose": "payment_processing",
            "allowed_purposes": ["payment_processing"],
            "justified_fields": ["credit_card"],
            "timestamp": 1704067200,
            "encryption_config": {
                "credit_card": {"encrypted": false}  # Should be encrypted!
            }
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "requires encryption")]) >= 1
}

# Test weak encryption
test_weak_encryption_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "personal_data", "classification_level": 2, "category": "personal_identifiable_information"}
            ],
            "requester_clearance_level": 3,
            "special_authorization": true,
            "purpose": "analysis",
            "allowed_purposes": ["analysis"],
            "justified_fields": ["personal_data"],
            "timestamp": 1704067200,
            "encryption_config": {
                "personal_data": {
                    "encrypted": true,
                    "algorithm": "DES",  # Weak algorithm
                    "key_length": 56     # Weak key length
                }
            }
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "Inadequate encryption strength")]) >= 1
}

# Test retention policy violations
test_excessive_retention_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_login", "classification_level": 1, "category": "authentication_credentials"}
            ],
            "requester_clearance_level": 2,
            "purpose": "security_analysis",
            "allowed_purposes": ["security_analysis"],
            "justified_fields": ["user_login"],
            "timestamp": 1704067200,
            "retention_policy": {
                "authentication_credentials": 31536000  # 1 year - exceeds 1 day limit
            }
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "retention exceeds limit")]) >= 1
}

# Test missing retention policy
test_missing_retention_policy_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_data", "classification_level": 2, "category": "personal_identifiable_information"}
            ],
            "requester_clearance_level": 3,
            "purpose": "processing",
            "allowed_purposes": ["processing"],
            "justified_fields": ["user_data"],
            "timestamp": 1704067200
            # Missing retention_policy
        }
    }
    
    result.allow == false
    count([concern | concern := result.concerns[_]; contains(concern, "No data retention policy")]) >= 1
}

# Test key management requirements
test_poor_key_management_blocked {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "sensitive_data", "classification_level": 3, "category": "personal_identifiable_information"}
            ],
            "requester_clearance_level": 4,
            "special_authorization": true,
            "purpose": "analysis", 
            "allowed_purposes": ["analysis"],
            "justified_fields": ["sensitive_data"],
            "timestamp": 1704067200,
            "encryption_config": {
                "sensitive_data": {
                    "encrypted": true,
                    "algorithm": "AES",
                    "key_length": 256
                },
                "key_management": {
                    "rotation_enabled": false,   # Poor key management
                    "secure_storage": false,     # Poor key management
                    "access_controlled": false   # Poor key management
                }
            }
        }
    }
    
    result.allow == false
    count(result.privacy_evaluation.encryption.encryption_analysis.key_management.violations) >= 3
}

# Test access conditions for lower scores
test_access_conditions_applied {
    result := data.evaluate with input as {
        "type": "data_access",
        "data_request": {
            "data_fields": [
                {"name": "user_data", "classification_level": 2, "category": "personal_identifiable_information"}
            ],
            "requester_clearance_level": 2,  # Marginal clearance
            "purpose": "limited_analysis",
            "allowed_purposes": ["limited_analysis"],
            "justified_fields": ["user_data"],
            "timestamp": 1704067200,
            "retention_policy": {
                "personal_identifiable_information": 1800000  # 21 days - acceptable
            },
            "encryption_config": {
                "user_data": {
                    "encrypted": true,
                    "algorithm": "AES",
                    "key_length": 256
                },
                "key_management": {
                    "rotation_enabled": true,
                    "secure_storage": true,
                    "access_controlled": false  # One weakness
                }
            }
        }
    }
    
    result.access_score < 0.95
    result.access_score >= 0.9
    count(result.access_conditions) >= 1  # Should have conditions applied
}

# Test main policy routing for data access
test_main_policy_data_access {
    result := main.decision with input as {
        "type": "data_access",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "data_request": {
            "data_fields": [
                {"name": "public_info", "classification_level": 0, "category": "public"}
            ],
            "requester_clearance_level": 1,
            "purpose": "display",
            "allowed_purposes": ["display"],
            "justified_fields": ["public_info"],
            "timestamp": 1704067200,
            "retention_policy": {
                "public": 86400  # 1 day
            },
            "encryption_config": {
                "public_info": {"encrypted": false}
            }
        }
    }
    
    result.allow == true
}

# Test consent analysis
test_consent_analysis_complete {
    status := data.analyze_consent_status(
        ["user1", "user2", "user3"],
        [
            {"subject_id": "user1", "status": "granted"},
            {"subject_id": "user2", "status": "granted"}
        ]
    )
    
    status.total_subjects == 3
    status.consented_subjects == 2
    status.consent_rate == 2.0 / 3.0
}

# Test purpose drift detection
test_purpose_drift_detected {
    drift := data.check_purpose_drift("new_purpose", ["old_purpose1", "old_purpose2"])
    
    drift.detected == true
    drift.score == 0.5
}

test_purpose_drift_not_detected {
    drift := data.check_purpose_drift("existing_purpose", ["existing_purpose", "other_purpose"])
    
    drift.detected == false
    drift.score == 1.0
}

# Test field necessity justification
test_field_necessity_justified {
    justified := data.field_necessity_justified(
        {"purpose_relevance": 0.8},
        "analytics"
    )
    
    justified == true
}

test_field_necessity_not_justified {
    justified := data.field_necessity_justified(
        {"purpose_relevance": 0.5},
        "analytics"
    )
    
    justified == false
}