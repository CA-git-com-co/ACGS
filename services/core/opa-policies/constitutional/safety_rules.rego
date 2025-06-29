# ACGS-1 Lite Constitutional Safety Rules
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.constitutional

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Critical safety patterns that must be blocked
critical_safety_violations := {
    # System compromise attempts
    "system.execute_arbitrary_code",
    "system.modify_kernel",
    "system.bypass_security",
    "system.disable_logging",
    "system.escalate_privileges",
    
    # Network security violations
    "network.scan_internal",
    "network.ddos_attack", 
    "network.man_in_middle",
    "network.packet_injection",
    "network.bypass_firewall",
    
    # Data exfiltration attempts
    "data.bulk_download",
    "data.unauthorized_copy",
    "data.steganography",
    "data.covert_channel",
    "data.encryption_bypass",
    
    # Resource exhaustion attacks
    "resource.memory_bomb",
    "resource.cpu_exhaust",
    "resource.disk_fill",
    "resource.fork_bomb",
    "resource.infinite_loop",
    
    # Social engineering patterns
    "social.phishing_attempt",
    "social.impersonation",
    "social.manipulation",
    "social.credential_harvesting"
}

# High-risk actions requiring additional scrutiny
high_risk_actions := {
    "crypto.key_generation",
    "auth.password_reset",
    "config.security_change",
    "backup.restore_system",
    "network.external_connection",
    "file.executable_creation",
    "process.service_modification",
    "database.schema_change"
}

# Suspicious behavioral patterns
suspicious_patterns := {
    "rapid_successive_failures",
    "unusual_time_access",
    "geographic_anomaly", 
    "privilege_escalation_attempt",
    "data_access_pattern_change",
    "network_traffic_anomaly",
    "resource_usage_spike",
    "error_rate_increase"
}

# Enhanced safety evaluation
evaluate_safety = result {
    action := input.action
    context := input.context
    
    # Check for critical violations
    critical_violation := check_critical_violations(action)
    
    # Check high-risk patterns
    high_risk_check := check_high_risk_patterns(action, context)
    
    # Check behavioral anomalies
    behavioral_check := check_behavioral_patterns(context)
    
    # Check sandboxing and isolation
    isolation_check := check_isolation_requirements(action, context)
    
    # Check temporal safety constraints
    temporal_check := check_temporal_constraints(action, context)
    
    # Calculate overall safety score
    safety_score := calculate_safety_score([
        critical_violation,
        high_risk_check,
        behavioral_check,
        isolation_check,
        temporal_check
    ])
    
    # Compile all safety violations
    all_violations := array.concat([
        critical_violation.violations,
        high_risk_check.violations,
        behavioral_check.violations,
        isolation_check.violations,
        temporal_check.violations
    ])
    
    result := {
        "safe": safety_score >= 0.95,
        "safety_score": safety_score,
        "violations": all_violations,
        "safety_checks": {
            "critical": critical_violation,
            "high_risk": high_risk_check,
            "behavioral": behavioral_check,
            "isolation": isolation_check,
            "temporal": temporal_check
        },
        "action_classification": classify_action_risk(action),
        "required_mitigations": suggest_mitigations(action, context, safety_score)
    }
}

# Critical violation check
check_critical_violations(action) = result {
    violations := [violation |
        action in critical_safety_violations
        violation := sprintf("CRITICAL: Action %s is explicitly prohibited", [action])
    ]
    
    # Check for pattern matching
    pattern_violations := [violation |
        some pattern in critical_safety_violations
        contains(action, split(pattern, ".")[0])
        contains(action, split(pattern, ".")[1])
        violation := sprintf("CRITICAL: Action %s matches prohibited pattern %s", [action, pattern])
    ]
    
    all_violations := array.concat(violations, pattern_violations)
    
    result := {
        "passed": count(all_violations) == 0,
        "score": critical_safety_score(count(all_violations)),
        "violations": all_violations
    }
}

# High-risk pattern check
check_high_risk_patterns(action, context) = result {
    # Check if action is high-risk
    is_high_risk := action in high_risk_actions
    
    # Additional authorization required for high-risk actions
    has_additional_auth := object.get(context, "additional_authorization", false)
    security_review := object.get(context, "security_review_passed", false)
    
    violations := [violation |
        is_high_risk
        not has_additional_auth
        violation := sprintf("High-risk action %s requires additional authorization", [action])
    ]
    
    violations2 := array.concat(violations, [violation |
        is_high_risk
        not security_review
        violation := sprintf("High-risk action %s requires security review", [action])
    ])
    
    result := {
        "passed": not is_high_risk or (has_additional_auth and security_review),
        "score": high_risk_score(is_high_risk, has_additional_auth, security_review),
        "violations": violations2,
        "risk_level": risk_level(action)
    }
}

# Behavioral pattern analysis
check_behavioral_patterns(context) = result {
    agent_behavior := object.get(context, "behavioral_analysis", {})
    
    detected_patterns := [pattern |
        some pattern in suspicious_patterns
        object.get(agent_behavior, pattern, false) == true
    ]
    
    # Check for multiple suspicious patterns
    pattern_count := count(detected_patterns)
    multiple_patterns := pattern_count >= 2
    
    violations := [violation |
        pattern := detected_patterns[_]
        violation := sprintf("Suspicious behavioral pattern detected: %s", [pattern])
    ]
    
    violations2 := array.concat(violations, [violation |
        multiple_patterns
        violation := sprintf("Multiple suspicious patterns detected: %d", [pattern_count])
    ])
    
    result := {
        "passed": pattern_count <= 1,
        "score": behavioral_score(pattern_count),
        "violations": violations2,
        "detected_patterns": detected_patterns,
        "risk_escalation": multiple_patterns
    }
}

# Isolation and sandboxing check
check_isolation_requirements(action, context) = result {
    environment := object.get(context, "environment", {})
    
    # Check sandbox status
    sandbox_enabled := object.get(environment, "sandbox_enabled", false)
    sandbox_type := object.get(environment, "sandbox_type", "none")
    
    # Check network isolation
    network_isolated := object.get(environment, "network_isolated", false)
    
    # Check file system isolation
    fs_isolated := object.get(environment, "filesystem_isolated", false)
    
    # Actions requiring full isolation
    isolation_required_actions := {
        "code.execute_untrusted",
        "file.process_upload",
        "network.external_request",
        "system.install_package"
    }
    
    requires_isolation := action in isolation_required_actions
    properly_isolated := sandbox_enabled and network_isolated and fs_isolated
    
    violations := [violation |
        requires_isolation
        not sandbox_enabled
        violation := sprintf("Action %s requires sandbox but none enabled", [action])
    ]
    
    violations2 := array.concat(violations, [violation |
        requires_isolation
        sandbox_enabled
        not network_isolated
        violation := sprintf("Action %s requires network isolation", [action])
    ])
    
    violations3 := array.concat(violations2, [violation |
        requires_isolation
        sandbox_enabled
        not fs_isolated
        violation := sprintf("Action %s requires filesystem isolation", [action])
    ])
    
    result := {
        "passed": not requires_isolation or properly_isolated,
        "score": isolation_score(requires_isolation, properly_isolated),
        "violations": violations3,
        "isolation_status": {
            "sandbox_enabled": sandbox_enabled,
            "sandbox_type": sandbox_type,
            "network_isolated": network_isolated,
            "filesystem_isolated": fs_isolated
        }
    }
}

# Temporal constraint check
check_temporal_constraints(action, context) = result {
    current_time := object.get(context, "timestamp", 0)
    
    # Check business hours for sensitive operations
    sensitive_actions := {
        "user.delete_account",
        "config.modify_security",
        "backup.system_restore",
        "auth.revoke_access"
    }
    
    is_sensitive := action in sensitive_actions
    business_hours := check_business_hours(current_time)
    
    # Check for rate limiting windows
    rate_limit_check := check_action_rate_limits(action, context)
    
    # Check for maintenance windows
    maintenance_window := object.get(context, "maintenance_window", false)
    
    violations := [violation |
        is_sensitive
        not business_hours
        not maintenance_window
        violation := sprintf("Sensitive action %s not allowed outside business hours", [action])
    ]
    
    violations2 := array.concat(violations, [violation |
        not rate_limit_check.allowed
        violation := sprintf("Rate limit exceeded: %s", [rate_limit_check.reason])
    ])
    
    result := {
        "passed": (not is_sensitive or business_hours or maintenance_window) and rate_limit_check.allowed,
        "score": temporal_score(is_sensitive, business_hours, maintenance_window, rate_limit_check.allowed),
        "violations": violations2,
        "temporal_status": {
            "business_hours": business_hours,
            "maintenance_window": maintenance_window,
            "rate_limit_status": rate_limit_check
        }
    }
}

# Helper functions

classify_action_risk(action) = risk_class {
    action in critical_safety_violations
    risk_class := "CRITICAL"
}

classify_action_risk(action) = risk_class {
    action in high_risk_actions
    not action in critical_safety_violations
    risk_class := "HIGH"
}

classify_action_risk(action) = risk_class {
    not action in critical_safety_violations
    not action in high_risk_actions
    risk_class := "MEDIUM"
}

risk_level(action) = level {
    action in critical_safety_violations
    level := 5
}

risk_level(action) = level {
    action in high_risk_actions
    not action in critical_safety_violations
    level := 3
}

risk_level(action) = level {
    not action in critical_safety_violations
    not action in high_risk_actions
    level := 1
}

suggest_mitigations(action, context, safety_score) = mitigations {
    base_mitigations := []
    
    # Add sandbox requirement
    mitigations1 := array.concat(base_mitigations, ["Enable sandbox isolation"]) if {
        safety_score < 0.8
        not object.get(context.environment, "sandbox_enabled", false)
    }
    
    # Add additional monitoring
    mitigations2 := array.concat(mitigations1, ["Enable enhanced monitoring"]) if {
        safety_score < 0.9
    }
    
    # Add human approval requirement
    mitigations3 := array.concat(mitigations2, ["Require human approval"]) if {
        safety_score < 0.7
    }
    
    mitigations := mitigations3
}

check_business_hours(timestamp) = is_business_hours {
    # Simplified business hours check (9 AM - 5 PM UTC)
    # In real implementation, this would use proper time libraries
    hour := timestamp % 86400 / 3600
    is_business_hours := hour >= 9 and hour <= 17
}

check_action_rate_limits(action, context) = result {
    # Simplified rate limiting - in real implementation would check actual usage
    current_usage := object.get(context, "recent_action_count", 0)
    
    # Different limits for different action types
    limits := {
        "data.": 100,
        "system.": 10,
        "auth.": 5,
        "network.": 50
    }
    
    action_prefix := sprintf("%s.", [split(action, ".")[0]])
    limit := object.get(limits, action_prefix, 20)
    
    result := {
        "allowed": current_usage < limit,
        "current": current_usage,
        "limit": limit,
        "reason": sprintf("Action rate: %d/%d for %s", [current_usage, limit, action_prefix])
    }
}

# Scoring functions

critical_safety_score(violation_count) = score {
    score := 0.0 if violation_count > 0
    score := 1.0 if violation_count == 0
}

high_risk_score(is_high_risk, has_auth, has_review) = score {
    score := 1.0 if not is_high_risk
    score := 0.9 if is_high_risk and has_auth and has_review
    score := 0.5 if is_high_risk and (has_auth or has_review)
    score := 0.1 if is_high_risk and not has_auth and not has_review
}

behavioral_score(pattern_count) = score {
    score := 1.0 if pattern_count == 0
    score := 0.7 if pattern_count == 1
    score := 0.3 if pattern_count == 2
    score := 0.0 if pattern_count >= 3
}

isolation_score(requires_isolation, properly_isolated) = score {
    score := 1.0 if not requires_isolation
    score := 1.0 if requires_isolation and properly_isolated
    score := 0.2 if requires_isolation and not properly_isolated
}

temporal_score(is_sensitive, business_hours, maintenance_window, rate_ok) = score {
    base_score := 0.8 if rate_ok else 0.0
    
    time_bonus := 0.0
    time_bonus := 0.2 if not is_sensitive
    time_bonus := 0.2 if is_sensitive and (business_hours or maintenance_window)
    
    score := base_score + time_bonus
}

calculate_safety_score(checks) = score {
    # Weighted average with critical violations having highest weight
    weights := [0.4, 0.25, 0.15, 0.15, 0.05]  # Critical, high-risk, behavioral, isolation, temporal
    
    weighted_sum := sum([checks[i].score * weights[i] | i := range(0, count(checks))])
    
    score := weighted_sum
}