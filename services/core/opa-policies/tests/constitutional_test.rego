# ACGS-1 Lite Constitutional Policies Test Suite
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.constitutional_test

import data.acgs.constitutional
import data.acgs.main

# Test constitutional hash verification
test_constitutional_hash_verification {
    constitutional.constitutional_hash == "cdd01ef066bc6cf2"
}

# Test dangerous action blocking
test_dangerous_action_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "system.execute_shell",
        "context": {
            "environment": {"sandbox_enabled": true},
            "agent": {"trust_level": 0.9}
        }
    }
}

test_network_bypass_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "network.bypass_firewall", 
        "context": {
            "environment": {"sandbox_enabled": true},
            "agent": {"trust_level": 0.9}
        }
    }
}

test_privilege_escalation_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "auth.escalate_privileges",
        "context": {
            "environment": {"sandbox_enabled": true},
            "agent": {"trust_level": 0.9}
        }
    }
}

# Test safe action allowance
test_safe_action_allowed {
    constitutional.evaluate.allow with input as {
        "action": "data.read_public",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1, "memory_gb": 2}}
        }
    }
}

test_safe_computation_allowed {
    constitutional.evaluate.allow with input as {
        "action": "compute.process_data",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.8, "requested_resources": {"cpu_cores": 1, "memory_gb": 1}},
            "explanation": "Processing user data for analytics as requested by user"
        }
    }
}

# Test trust level requirements
test_low_trust_agent_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "data.process_user",
        "context": {
            "environment": {"sandbox_enabled": true},
            "agent": {"trust_level": 0.5}  # Below 0.8 threshold
        }
    }
}

test_high_trust_agent_allowed {
    constitutional.evaluate.allow with input as {
        "action": "data.read_internal",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1, "memory_gb": 1}},
            "explanation": "Reading internal data for authorized processing"
        }
    }
}

# Test sandbox requirements
test_unsandboxed_action_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "data.process_files",
        "context": {
            "environment": {"sandbox_enabled": false},
            "agent": {"trust_level": 0.9}
        }
    }
}

test_sandboxed_action_allowed {
    constitutional.evaluate.allow with input as {
        "action": "data.process_files",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1, "memory_gb": 1}},
            "explanation": "Processing files in secure sandbox environment"
        }
    }
}

# Test resource limit enforcement
test_excessive_cpu_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "compute.heavy_processing",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {
                "trust_level": 0.9,
                "requested_resources": {"cpu_cores": 5}  # Exceeds limit of 2
            }
        }
    }
}

test_excessive_memory_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "data.load_dataset",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {
                "trust_level": 0.9,
                "requested_resources": {"memory_gb": 8}  # Exceeds limit of 4
            }
        }
    }
}

test_reasonable_resources_allowed {
    constitutional.evaluate.allow with input as {
        "action": "compute.standard_processing",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {
                "trust_level": 0.9,
                "requested_resources": {"cpu_cores": 1, "memory_gb": 2}  # Within limits
            },
            "explanation": "Standard data processing within resource limits"
        }
    }
}

# Test transparency requirements
test_explanation_required_action_without_explanation_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "decision.make_automated",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}}
            # Missing explanation for transparency-required action
        }
    }
}

test_explanation_required_action_with_explanation_allowed {
    constitutional.evaluate.allow with input as {
        "action": "decision.make_automated",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "explanation": "Making automated decision based on user preferences and historical data patterns to optimize user experience"
        }
    }
}

test_short_explanation_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "decision.make_automated",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "explanation": "Auto decision"  # Too short (< 50 characters)
        }
    }
}

# Test autonomy principle
test_user_override_without_consent_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "user.override_preference",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "overrides_user_preference": true,
            "user_consent": false,
            "explanation": "Overriding user preference for system optimization"
        }
    }
}

test_user_override_with_consent_allowed {
    constitutional.evaluate.allow with input as {
        "action": "user.override_preference",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "overrides_user_preference": true,
            "user_consent": true,
            "explanation": "Overriding user preference with explicit user consent for emergency response"
        }
    }
}

# Test non-maleficence principle
test_high_harm_risk_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "system.modify_critical",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "harm_risk_assessment": 0.5,  # High harm risk (> 0.2 threshold)
            "explanation": "Modifying critical system component for performance improvement"
        }
    }
}

test_low_harm_risk_allowed {
    constitutional.evaluate.allow with input as {
        "action": "data.generate_report",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "harm_risk_assessment": 0.1,  # Low harm risk
            "explanation": "Generating user-requested analytics report from aggregated data"
        }
    }
}

# Test fairness principle
test_discriminatory_action_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "user.recommend_content",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "affects_protected_groups": true,
            "fairness_assessment": 0.7,  # Below 0.9 threshold for protected groups
            "explanation": "Recommending content based on user demographic analysis"
        }
    }
}

test_fair_recommendation_allowed {
    constitutional.evaluate.allow with input as {
        "action": "user.recommend_content",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "affects_protected_groups": true,
            "fairness_assessment": 0.95,  # High fairness score
            "explanation": "Recommending content based on user preferences and behavior patterns using fair algorithms"
        }
    }
}

# Test accountability principle
test_no_audit_trail_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "data.process_personal",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": false},  # No audit trail
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "explanation": "Processing personal data for analytics"
        }
    }
}

test_no_responsible_party_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "system.update_configuration",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            # Missing responsible_party
            "explanation": "Updating system configuration for optimization"
        }
    }
}

test_proper_accountability_allowed {
    constitutional.evaluate.allow with input as {
        "action": "system.backup_data",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "responsible_party": "system_admin",
            "explanation": "Creating scheduled backup of user data with proper oversight"
        }
    }
}

# Test rate limiting
test_rate_limit_exceeded_blocked {
    not constitutional.evaluate.allow with input as {
        "action": "data.query_database",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "current_usage_count": 250,  # Exceeds limit of 200 for data category
            "responsible_party": "data_analyst",
            "explanation": "Querying database for analytics processing"
        }
    }
}

test_rate_limit_within_bounds_allowed {
    constitutional.evaluate.allow with input as {
        "action": "data.query_database",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "current_usage_count": 50,  # Within limit
            "responsible_party": "data_analyst",
            "explanation": "Querying database for user-requested analytics report"
        }
    }
}

# Test main policy routing
test_main_policy_constitutional_evaluation {
    main.decision.allow with input as {
        "type": "constitutional_evaluation",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "action": "data.read_public",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "responsible_party": "data_processor",
            "explanation": "Reading public data for user dashboard display"
        }
    }
}

test_main_policy_wrong_hash_blocked {
    not main.decision.allow with input as {
        "type": "constitutional_evaluation",
        "constitutional_hash": "wrong_hash",
        "action": "data.read_public",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.9}
        }
    }
}

test_main_policy_unknown_type_blocked {
    not main.decision.allow with input as {
        "type": "unknown_request_type",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "action": "data.read_public"
    }
}

# Test health check
test_health_check_returns_correct_info {
    health := main.health
    health.status == "healthy"
    health.constitutional_hash == "cdd01ef066bc6cf2"
    "acgs.constitutional" in health.policies_loaded
    "acgs.main" in health.policies_loaded
}

# Test compliance scoring
test_high_compliance_score {
    result := constitutional.evaluate with input as {
        "action": "data.read_internal",
        "context": {
            "environment": {"sandbox_enabled": true, "audit_enabled": true},
            "agent": {"trust_level": 0.95, "requested_resources": {"cpu_cores": 1, "memory_gb": 1}},
            "responsible_party": "authorized_user",
            "explanation": "Reading internal data for authorized business process with full compliance checks",
            "benefit_assessment": 0.9,
            "harm_risk_assessment": 0.05,
            "fairness_assessment": 0.95
        }
    }
    
    result.compliance_score >= 0.95
    result.allow == true
}

test_low_compliance_score {
    result := constitutional.evaluate with input as {
        "action": "system.execute_untrusted",
        "context": {
            "environment": {"sandbox_enabled": false, "audit_enabled": false},
            "agent": {"trust_level": 0.3, "requested_resources": {"cpu_cores": 10}},
            "harm_risk_assessment": 0.8,
            "fairness_assessment": 0.4
        }
    }
    
    result.compliance_score < 0.5
    result.allow == false
}