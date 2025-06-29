# ACGS-1 Lite Constitutional Core Principles
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.constitutional

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Constitutional hash must be preserved
constitutional_hash := "cdd01ef066bc6cf2"

# Core constitutional principles
principles := {
    "autonomy": "AI agents must respect user autonomy and choice",
    "beneficence": "AI actions must aim to benefit users and society", 
    "non_maleficence": "AI must not cause harm",
    "transparency": "AI decision-making must be explainable",
    "fairness": "AI must not discriminate unfairly",
    "privacy": "User data must be protected",
    "accountability": "All actions must be traceable"
}

# Main evaluation entry point
evaluate = response {
    input.action
    input.context
    
    # Check all constitutional requirements
    safety_check := check_safety(input.action, input.context)
    constitutional_check := check_constitutional_compliance(input.action, input.context)
    resource_check := check_resource_limits(input.context)
    transparency_check := check_transparency_requirements(input.action, input.context)
    
    # Calculate overall compliance score
    compliance_score := calculate_compliance_score([
        safety_check,
        constitutional_check, 
        resource_check,
        transparency_check
    ])
    
    # Determine if action is allowed
    action_allowed := compliance_score >= 0.95
    
    # Collect all reasons
    all_reasons := array.concat([
        safety_check.reasons,
        constitutional_check.reasons,
        resource_check.reasons,
        transparency_check.reasons
    ])
    
    # Build response
    response := {
        "allow": action_allowed,
        "compliance_score": compliance_score,
        "reasons": all_reasons,
        "constitutional_hash": constitutional_hash,
        "principles_checked": object.keys(principles),
        "evaluation_details": {
            "safety": safety_check,
            "constitutional": constitutional_check,
            "resources": resource_check,
            "transparency": transparency_check
        }
    }
}

# Safety rules check
check_safety(action, context) = result {
    # Dangerous actions that are always denied
    dangerous_actions := {
        "system.execute_shell",
        "network.access_external", 
        "file.write_system",
        "process.spawn_child",
        "memory.access_kernel",
        "network.bypass_firewall",
        "system.modify_configuration",
        "auth.escalate_privileges",
        "crypto.break_encryption",
        "data.exfiltrate"
    }
    
    # Check if action is dangerous
    action_safe := not action in dangerous_actions
    
    # Check agent trust level
    agent_trusted := context.agent.trust_level >= 0.8
    
    # Check sandboxing
    properly_sandboxed := context.environment.sandbox_enabled == true
    
    # Check rate limiting
    rate_limited := check_rate_limits(action, context)
    
    # Compile safety violations
    violations := [reason |
        not action_safe
        reason := sprintf("Dangerous action blocked: %s", [action])
    ]
    
    violations2 := array.concat(violations, [reason |
        not agent_trusted
        reason := sprintf("Agent trust level too low: %v (required: 0.8)", [context.agent.trust_level])
    ])
    
    violations3 := array.concat(violations2, [reason |
        not properly_sandboxed
        reason := "Sandbox not enabled for this action"
    ])
    
    final_violations := array.concat(violations3, [reason |
        not rate_limited.allowed
        reason := sprintf("Rate limit exceeded: %s", [rate_limited.reason])
    ])
    
    result := {
        "passed": action_safe and properly_sandboxed and rate_limited.allowed,
        "score": safety_score(action_safe, properly_sandboxed, rate_limited.allowed),
        "reasons": final_violations
    }
}

# Constitutional compliance check
check_constitutional_compliance(action, context) = result {
    # Check autonomy principle
    autonomy_check := check_autonomy(action, context)
    
    # Check beneficence principle  
    beneficence_check := check_beneficence(action, context)
    
    # Check non-maleficence principle
    non_maleficence_check := check_non_maleficence(action, context)
    
    # Check fairness principle
    fairness_check := check_fairness(action, context)
    
    # Check accountability principle
    accountability_check := check_accountability(action, context)
    
    # Aggregate all principle checks
    all_checks := [
        autonomy_check,
        beneficence_check,
        non_maleficence_check,
        fairness_check,
        accountability_check
    ]
    
    # Calculate aggregate score
    total_score := sum([check.score | check := all_checks[_]])
    avg_score := total_score / count(all_checks)
    
    # Collect all violations
    all_violations := [violation |
        check := all_checks[_]
        violation := check.violations[_]
    ]
    
    result := {
        "passed": avg_score >= 0.9,
        "score": avg_score,
        "reasons": all_violations,
        "principle_scores": {
            "autonomy": autonomy_check.score,
            "beneficence": beneficence_check.score,
            "non_maleficence": non_maleficence_check.score,
            "fairness": fairness_check.score,
            "accountability": accountability_check.score
        }
    }
}

# Resource limits check
check_resource_limits(context) = result {
    # Default resource limits per agent
    resource_limits := {
        "cpu_cores": 2,
        "memory_gb": 4, 
        "disk_gb": 10,
        "network_bandwidth_mbps": 10,
        "max_execution_time_seconds": 300,
        "max_file_operations_per_minute": 100,
        "max_network_requests_per_minute": 50
    }
    
    # Get agent's requested resources
    agent_resources := object.get(context.agent, "requested_resources", {})
    
    # Check each resource limit
    violations := [reason |
        some resource, limit in resource_limits
        requested := object.get(agent_resources, resource, 0)
        requested > limit
        reason := sprintf("Resource %s exceeds limit: requested %v, limit %v", 
                         [resource, requested, limit])
    ]
    
    result := {
        "passed": count(violations) == 0,
        "score": resource_compliance_score(agent_resources, resource_limits),
        "reasons": violations,
        "resource_usage": agent_resources,
        "resource_limits": resource_limits
    }
}

# Transparency requirements check
check_transparency_requirements(action, context) = result {
    # Actions that require explanation
    explanation_required_actions := {
        "decision.make_automated",
        "data.process_personal",
        "policy.update_rules",
        "user.recommend_action",
        "system.modify_behavior"
    }
    
    # Check if explanation is required and provided
    requires_explanation := action in explanation_required_actions
    has_explanation := object.get(context, "explanation", "") != ""
    explanation_adequate := count(object.get(context, "explanation", "")) >= 50
    
    # Check audit trail requirements
    audit_enabled := object.get(context.environment, "audit_enabled", false)
    
    violations := [reason |
        requires_explanation
        not has_explanation
        reason := sprintf("Action %s requires explanation but none provided", [action])
    ]
    
    violations2 := array.concat(violations, [reason |
        requires_explanation 
        has_explanation
        not explanation_adequate
        reason := sprintf("Explanation too short for action %s (minimum 50 characters)", [action])
    ])
    
    violations3 := array.concat(violations2, [reason |
        not audit_enabled
        reason := "Audit trail not enabled for transparency"
    ])
    
    transparency_score := transparency_compliance_score(
        requires_explanation, 
        has_explanation, 
        explanation_adequate,
        audit_enabled
    )
    
    result := {
        "passed": transparency_score >= 0.9,
        "score": transparency_score,
        "reasons": violations3
    }
}

# Helper functions for principle checks

check_autonomy(action, context) = result {
    # Check if action respects user choice
    user_consent := object.get(context, "user_consent", false)
    overrides_user := object.get(context, "overrides_user_preference", false)
    
    violations := [reason |
        overrides_user
        not user_consent
        reason := "Action overrides user preference without consent"
    ]
    
    result := {
        "score": autonomy_score(user_consent, overrides_user),
        "violations": violations
    }
}

check_beneficence(action, context) = result {
    # Check if action aims to benefit users
    benefit_score := object.get(context, "benefit_assessment", 0.5)
    
    violations := [reason |
        benefit_score < 0.3
        reason := sprintf("Action benefit score too low: %v", [benefit_score])
    ]
    
    result := {
        "score": benefit_score,
        "violations": violations
    }
}

check_non_maleficence(action, context) = result {
    # Check potential for harm
    harm_risk := object.get(context, "harm_risk_assessment", 0.0)
    
    violations := [reason |
        harm_risk > 0.2
        reason := sprintf("Unacceptable harm risk: %v", [harm_risk])
    ]
    
    result := {
        "score": 1.0 - harm_risk,
        "violations": violations
    }
}

check_fairness(action, context) = result {
    # Check for discriminatory patterns
    fairness_score := object.get(context, "fairness_assessment", 1.0)
    protected_groups := object.get(context, "affects_protected_groups", false)
    
    violations := [reason |
        protected_groups
        fairness_score < 0.9
        reason := sprintf("Potential discrimination detected: fairness score %v", [fairness_score])
    ]
    
    result := {
        "score": fairness_score,
        "violations": violations
    }
}

check_accountability(action, context) = result {
    # Check traceability requirements
    has_audit_trail := object.get(context.environment, "audit_enabled", false)
    has_responsible_party := object.get(context, "responsible_party", "") != ""
    
    violations := [reason |
        not has_audit_trail
        reason := "No audit trail configured"
    ]
    
    violations2 := array.concat(violations, [reason |
        not has_responsible_party
        reason := "No responsible party identified"
    ])
    
    result := {
        "score": accountability_score(has_audit_trail, has_responsible_party),
        "violations": violations2
    }
}

# Rate limiting check
check_rate_limits(action, context) = result {
    agent_id := object.get(context.agent, "id", "unknown")
    time_window := object.get(context, "time_window_minutes", 1)
    
    # Default rate limits
    default_rate_limits := {
        "data.read": 100,
        "data.write": 50,
        "network.request": 20,
        "system.query": 200
    }
    
    action_category := split(action, ".")[0]
    rate_limit := object.get(default_rate_limits, action_category, 10)
    
    # In a real implementation, this would check actual usage
    # For now, simulate based on context
    current_usage := object.get(context, "current_usage_count", 0)
    
    result := {
        "allowed": current_usage < rate_limit,
        "current": current_usage,
        "limit": rate_limit,
        "reason": sprintf("Rate limit for %s: %d/%d", [action_category, current_usage, rate_limit])
    }
}

# Scoring functions

safety_score(action_safe, sandboxed, rate_ok) = score {
    factors := [factor |
        action_safe
        factor := 0.5
    ]
    
    factors2 := array.concat(factors, [factor |
        sandboxed
        factor := 0.3
    ])
    
    factors3 := array.concat(factors2, [factor |
        rate_ok
        factor := 0.2
    ])
    
    score := sum(factors3)
}

resource_compliance_score(requested, limits) = score {
    # Calculate compliance as percentage of resources within limits
    compliance_factors := [factor |
        some resource, limit in limits
        requested_amount := object.get(requested, resource, 0)
        factor := min([1.0, limit / max([requested_amount, 1])])
    ]
    
    score := sum(compliance_factors) / count(compliance_factors)
}

transparency_compliance_score(requires_explanation, has_explanation, adequate_explanation, audit_enabled) = score {
    base_score := 0.6
    
    explanation_bonus := 0.0
    explanation_bonus := 0.2 if not requires_explanation
    explanation_bonus := 0.2 if requires_explanation and has_explanation and adequate_explanation
    
    audit_bonus := 0.2 if audit_enabled
    
    score := base_score + explanation_bonus + audit_bonus
}

autonomy_score(user_consent, overrides_user) = score {
    score := 1.0 if not overrides_user
    score := 0.8 if overrides_user and user_consent
    score := 0.2 if overrides_user and not user_consent
}

accountability_score(has_audit_trail, has_responsible_party) = score {
    factors := []
    factors := array.concat(factors, [0.5]) if has_audit_trail
    factors := array.concat(factors, [0.5]) if has_responsible_party
    
    score := sum(factors)
}

calculate_compliance_score(checks) = score {
    # Weighted average of all check scores
    weights := {
        "safety": 0.3,
        "constitutional": 0.4,
        "resources": 0.2, 
        "transparency": 0.1
    }
    
    safety_score := checks[0].score
    constitutional_score := checks[1].score
    resource_score := checks[2].score
    transparency_score := checks[3].score
    
    weighted_sum := (
        safety_score * weights.safety +
        constitutional_score * weights.constitutional + 
        resource_score * weights.resources +
        transparency_score * weights.transparency
    )
    
    score := weighted_sum
}