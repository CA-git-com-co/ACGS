# ACGS-1 Lite Evolution Approval Rules
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.evolution

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Constitutional hash verification
constitutional_hash := "cdd01ef066bc6cf2"

# Evolution approval thresholds
approval_thresholds := {
    "auto_approve": 0.95,
    "fast_track": 0.90,
    "human_review": 0.0
}

# Evolution risk categories
evolution_risk_levels := {
    "minor_update": 0.1,
    "patch": 0.15,
    "configuration": 0.2,
    "feature_addition": 0.4,
    "major_update": 0.7,
    "architecture_change": 0.9
}

# Main evolution evaluation entry point
evaluate = response {
    input.type == "evolution_approval"
    evolution_request := input.evolution_request
    
    # Evaluate all evolution criteria
    risk_assessment := assess_evolution_risk(evolution_request)
    constitutional_compliance := check_constitutional_compliance(evolution_request)
    performance_impact := assess_performance_impact(evolution_request)
    rollback_capability := check_rollback_capability(evolution_request)
    approval_requirements := check_approval_requirements(evolution_request)
    
    # Calculate overall evolution score
    evolution_score := calculate_evolution_score([
        risk_assessment,
        constitutional_compliance,
        performance_impact,
        rollback_capability,
        approval_requirements
    ])
    
    # Determine approval decision
    approval_decision := determine_approval_path(evolution_score, evolution_request)
    
    # Compile all concerns
    all_concerns := array.concat([
        risk_assessment.concerns,
        constitutional_compliance.concerns,
        performance_impact.concerns,
        rollback_capability.concerns,
        approval_requirements.concerns
    ])
    
    response := {
        "allow": approval_decision.approved,
        "approval_path": approval_decision.path,
        "evolution_score": evolution_score,
        "constitutional_hash": constitutional_hash,
        "concerns": all_concerns,
        "evaluation_details": {
            "risk_assessment": risk_assessment,
            "constitutional_compliance": constitutional_compliance,
            "performance_impact": performance_impact,
            "rollback_capability": rollback_capability,
            "approval_requirements": approval_requirements
        },
        "required_actions": approval_decision.required_actions,
        "estimated_processing_time": approval_decision.estimated_time
    }
}

# Risk assessment for evolution
assess_evolution_risk(evolution_request) = result {
    evolution_type := object.get(evolution_request, "type", "unknown")
    base_risk := object.get(evolution_risk_levels, evolution_type, 0.5)
    
    # Check for risk-increasing factors
    risk_factors := check_risk_factors(evolution_request)
    
    # Check for risk-mitigating factors
    mitigation_factors := check_mitigation_factors(evolution_request)
    
    # Calculate adjusted risk score
    adjusted_risk := calculate_adjusted_risk(base_risk, risk_factors, mitigation_factors)
    
    concerns := [concern |
        factor := risk_factors[_]
        factor.severity >= 0.3
        concern := sprintf("Risk factor: %s (severity: %v)", [factor.description, factor.severity])
    ]
    
    result := {
        "passed": adjusted_risk <= 0.5,
        "score": 1.0 - adjusted_risk,
        "concerns": concerns,
        "risk_level": classify_risk_level(adjusted_risk),
        "base_risk": base_risk,
        "adjusted_risk": adjusted_risk,
        "risk_factors": risk_factors,
        "mitigation_factors": mitigation_factors
    }
}

# Constitutional compliance for evolutions
check_constitutional_compliance(evolution_request) = result {
    changes := object.get(evolution_request, "changes", {})
    
    # Check if evolution affects constitutional principles
    affects_principles := check_principle_impact(changes)
    
    # Check for constitutional violations
    violations := check_constitutional_violations(changes)
    
    # Check constitutional hash preservation
    hash_preserved := check_hash_preservation(evolution_request)
    
    concerns := [concern |
        violation := violations[_]
        concern := sprintf("Constitutional violation: %s", [violation])
    ]
    
    concerns2 := array.concat(concerns, [concern |
        not hash_preserved
        concern := "Constitutional hash not preserved"
    ])
    
    compliance_score := constitutional_compliance_score(
        count(violations),
        hash_preserved,
        affects_principles
    )
    
    result := {
        "passed": compliance_score >= 0.95,
        "score": compliance_score,
        "concerns": concerns2,
        "affected_principles": affects_principles,
        "violations": violations,
        "hash_preserved": hash_preserved
    }
}

# Performance impact assessment
assess_performance_impact(evolution_request) = result {
    performance_data := object.get(evolution_request, "performance_analysis", {})
    
    # Check computational complexity changes
    complexity_change := object.get(performance_data, "complexity_delta", 0.0)
    
    # Check memory usage changes
    memory_change := object.get(performance_data, "memory_delta", 0.0)
    
    # Check response time impact
    latency_change := object.get(performance_data, "latency_delta", 0.0)
    
    # Check resource utilization
    resource_change := object.get(performance_data, "resource_delta", 0.0)
    
    # Performance degradation thresholds
    performance_thresholds := {
        "complexity_max": 0.3,
        "memory_max": 0.2,
        "latency_max": 0.15,
        "resource_max": 0.25
    }
    
    violations := [violation |
        complexity_change > performance_thresholds.complexity_max
        violation := sprintf("Complexity increase too high: %v%% (max: %v%%)", 
                           [complexity_change * 100, performance_thresholds.complexity_max * 100])
    ]
    
    violations2 := array.concat(violations, [violation |
        memory_change > performance_thresholds.memory_max
        violation := sprintf("Memory usage increase too high: %v%% (max: %v%%)", 
                           [memory_change * 100, performance_thresholds.memory_max * 100])
    ])
    
    violations3 := array.concat(violations2, [violation |
        latency_change > performance_thresholds.latency_max
        violation := sprintf("Latency increase too high: %v%% (max: %v%%)", 
                           [latency_change * 100, performance_thresholds.latency_max * 100])
    ])
    
    violations4 := array.concat(violations3, [violation |
        resource_change > performance_thresholds.resource_max
        violation := sprintf("Resource usage increase too high: %v%% (max: %v%%)", 
                           [resource_change * 100, performance_thresholds.resource_max * 100])
    ])
    
    performance_score := calculate_performance_score(
        complexity_change,
        memory_change,
        latency_change,
        resource_change,
        performance_thresholds
    )
    
    result := {
        "passed": performance_score >= 0.8,
        "score": performance_score,
        "concerns": violations4,
        "performance_changes": {
            "complexity_delta": complexity_change,
            "memory_delta": memory_change,
            "latency_delta": latency_change,
            "resource_delta": resource_change
        }
    }
}

# Rollback capability check
check_rollback_capability(evolution_request) = result {
    rollback_plan := object.get(evolution_request, "rollback_plan", {})
    
    # Check if rollback plan exists
    has_rollback_plan := count(object.keys(rollback_plan)) > 0
    
    # Check rollback plan completeness
    required_fields := ["procedure", "verification", "timeline", "dependencies"]
    missing_fields := [field |
        field := required_fields[_]
        not object.get(rollback_plan, field, null)
    ]
    
    # Check rollback testing
    rollback_tested := object.get(rollback_plan, "tested", false)
    
    # Check rollback automation
    rollback_automated := object.get(rollback_plan, "automated", false)
    
    concerns := [concern |
        not has_rollback_plan
        concern := "No rollback plan provided"
    ]
    
    concerns2 := array.concat(concerns, [concern |
        field := missing_fields[_]
        concern := sprintf("Rollback plan missing field: %s", [field])
    ])
    
    concerns3 := array.concat(concerns2, [concern |
        has_rollback_plan
        not rollback_tested
        concern := "Rollback plan not tested"
    ])
    
    rollback_score := calculate_rollback_score(
        has_rollback_plan,
        count(missing_fields),
        rollback_tested,
        rollback_automated
    )
    
    result := {
        "passed": rollback_score >= 0.8,
        "score": rollback_score,
        "concerns": concerns3,
        "rollback_status": {
            "has_plan": has_rollback_plan,
            "tested": rollback_tested,
            "automated": rollback_automated,
            "missing_fields": missing_fields
        }
    }
}

# Approval requirements check
check_approval_requirements(evolution_request) = result {
    evolution_type := object.get(evolution_request, "type", "unknown")
    
    # Check human approval requirements
    human_approval_required := requires_human_approval(evolution_type, evolution_request)
    has_human_approval := object.get(evolution_request, "human_approved", false)
    
    # Check security review requirements
    security_review_required := requires_security_review(evolution_type, evolution_request)
    has_security_review := object.get(evolution_request, "security_review_passed", false)
    
    # Check peer review requirements
    peer_review_required := requires_peer_review(evolution_type, evolution_request)
    has_peer_review := object.get(evolution_request, "peer_reviewed", false)
    
    concerns := [concern |
        human_approval_required
        not has_human_approval
        concern := sprintf("Human approval required for %s evolution", [evolution_type])
    ]
    
    concerns2 := array.concat(concerns, [concern |
        security_review_required
        not has_security_review
        concern := sprintf("Security review required for %s evolution", [evolution_type])
    ])
    
    concerns3 := array.concat(concerns2, [concern |
        peer_review_required
        not has_peer_review
        concern := sprintf("Peer review required for %s evolution", [evolution_type])
    ])
    
    approval_score := calculate_approval_score(
        human_approval_required, has_human_approval,
        security_review_required, has_security_review,
        peer_review_required, has_peer_review
    )
    
    result := {
        "passed": approval_score >= 0.9,
        "score": approval_score,
        "concerns": concerns3,
        "requirements": {
            "human_approval": {"required": human_approval_required, "satisfied": has_human_approval},
            "security_review": {"required": security_review_required, "satisfied": has_security_review},
            "peer_review": {"required": peer_review_required, "satisfied": has_peer_review}
        }
    }
}

# Helper functions

check_risk_factors(evolution_request) = factors {
    changes := object.get(evolution_request, "changes", {})
    
    base_factors := []
    
    # Check for external dependencies
    factors1 := array.concat(base_factors, [{
        "description": "introduces external dependencies",
        "severity": 0.4
    }]) if count(object.get(changes, "external_dependencies", [])) > 0
    
    # Check for privilege changes
    factors2 := array.concat(factors1, [{
        "description": "modifies privilege requirements",
        "severity": 0.6
    }]) if object.get(changes, "privilege_escalation", false)
    
    # Check for network changes
    factors3 := array.concat(factors2, [{
        "description": "modifies network access patterns",
        "severity": 0.3
    }]) if object.get(changes, "network_changes", false)
    
    # Check for experimental features
    factors4 := array.concat(factors3, [{
        "description": "includes experimental features",
        "severity": 0.5
    }]) if object.get(changes, "experimental_features", false)
    
    factors := factors4
}

check_mitigation_factors(evolution_request) = factors {
    mitigations := object.get(evolution_request, "mitigations", {})
    
    base_factors := []
    
    # Sandbox deployment
    factors1 := array.concat(base_factors, [{
        "description": "deployed in sandbox first",
        "mitigation": 0.2
    }]) if object.get(mitigations, "sandbox_deployment", false)
    
    # Gradual rollout
    factors2 := array.concat(factors1, [{
        "description": "gradual rollout planned",
        "mitigation": 0.15
    }]) if object.get(mitigations, "gradual_rollout", false)
    
    # Enhanced monitoring
    factors3 := array.concat(factors2, [{
        "description": "enhanced monitoring enabled",
        "mitigation": 0.1
    }]) if object.get(mitigations, "enhanced_monitoring", false)
    
    factors := factors3
}

check_principle_impact(changes) = affected_principles {
    affected := []
    
    # Check autonomy impact
    affected1 := array.concat(affected, ["autonomy"]) if {
        object.get(changes, "user_interaction_changes", false)
    }
    
    # Check transparency impact
    affected2 := array.concat(affected1, ["transparency"]) if {
        object.get(changes, "decision_logic_changes", false)
    }
    
    # Check privacy impact
    affected3 := array.concat(affected2, ["privacy"]) if {
        object.get(changes, "data_handling_changes", false)
    }
    
    affected_principles := affected3
}

check_constitutional_violations(changes) = violations {
    base_violations := []
    
    # Check for transparency violations
    violations1 := array.concat(base_violations, ["reduces system transparency"]) if {
        object.get(changes, "logging_disabled", false)
    }
    
    # Check for accountability violations
    violations2 := array.concat(violations1, ["reduces traceability"]) if {
        object.get(changes, "audit_disabled", false)
    }
    
    # Check for privacy violations
    violations3 := array.concat(violations2, ["increases data exposure risk"]) if {
        object.get(changes, "data_encryption_weakened", false)
    }
    
    violations := violations3
}

check_hash_preservation(evolution_request) = preserved {
    provided_hash := object.get(evolution_request, "constitutional_hash", "")
    preserved := provided_hash == constitutional_hash
}

requires_human_approval(evolution_type, evolution_request) = required {
    high_risk_types := {"major_update", "architecture_change"}
    
    required := evolution_type in high_risk_types
}

requires_security_review(evolution_type, evolution_request) = required {
    security_sensitive_types := {"major_update", "architecture_change", "configuration"}
    changes := object.get(evolution_request, "changes", {})
    
    required := evolution_type in security_sensitive_types or
                object.get(changes, "security_changes", false)
}

requires_peer_review(evolution_type, evolution_request) = required {
    peer_review_types := {"feature_addition", "major_update", "architecture_change"}
    
    required := evolution_type in peer_review_types
}

determine_approval_path(evolution_score, evolution_request) = decision {
    evolution_score >= approval_thresholds.auto_approve
    decision := {
        "approved": true,
        "path": "auto_approve",
        "required_actions": [],
        "estimated_time": "immediate"
    }
}

determine_approval_path(evolution_score, evolution_request) = decision {
    evolution_score >= approval_thresholds.fast_track
    evolution_score < approval_thresholds.auto_approve
    decision := {
        "approved": false,
        "path": "fast_track",
        "required_actions": ["human_review_expedited"],
        "estimated_time": "5-15 minutes"
    }
}

determine_approval_path(evolution_score, evolution_request) = decision {
    evolution_score < approval_thresholds.fast_track
    decision := {
        "approved": false,
        "path": "human_review",
        "required_actions": ["comprehensive_human_review", "security_assessment"],
        "estimated_time": "30-60 minutes"
    }
}

classify_risk_level(risk_score) = level {
    risk_score <= 0.2
    level := "LOW"
}

classify_risk_level(risk_score) = level {
    risk_score > 0.2
    risk_score <= 0.5
    level := "MEDIUM"
}

classify_risk_level(risk_score) = level {
    risk_score > 0.5
    risk_score <= 0.8
    level := "HIGH"
}

classify_risk_level(risk_score) = level {
    risk_score > 0.8
    level := "CRITICAL"
}

# Scoring functions

calculate_adjusted_risk(base_risk, risk_factors, mitigation_factors) = adjusted_risk {
    risk_increase := sum([factor.severity | factor := risk_factors[_]])
    risk_decrease := sum([factor.mitigation | factor := mitigation_factors[_]])
    
    adjusted_risk := max([0.0, min([1.0, base_risk + risk_increase - risk_decrease])])
}

constitutional_compliance_score(violation_count, hash_preserved, principle_count) = score {
    base_score := 0.5
    violation_penalty := violation_count * 0.2
    hash_bonus := 0.3 if hash_preserved else 0.0
    principle_bonus := min([0.2, principle_count * 0.05])
    
    score := max([0.0, base_score - violation_penalty + hash_bonus + principle_bonus])
}

calculate_performance_score(complexity_delta, memory_delta, latency_delta, resource_delta, thresholds) = score {
    # Normalize each metric against its threshold
    complexity_score := max([0.0, 1.0 - (complexity_delta / thresholds.complexity_max)])
    memory_score := max([0.0, 1.0 - (memory_delta / thresholds.memory_max)])
    latency_score := max([0.0, 1.0 - (latency_delta / thresholds.latency_max)])
    resource_score := max([0.0, 1.0 - (resource_delta / thresholds.resource_max)])
    
    # Weighted average
    score := (complexity_score * 0.3 + memory_score * 0.25 + latency_score * 0.25 + resource_score * 0.2)
}

calculate_rollback_score(has_plan, missing_fields, tested, automated) = score {
    base_score := 0.4 if has_plan else 0.0
    completeness_score := max([0.0, 0.3 - (missing_fields * 0.075)])
    testing_score := 0.2 if tested else 0.0
    automation_score := 0.1 if automated else 0.0
    
    score := base_score + completeness_score + testing_score + automation_score
}

calculate_approval_score(human_req, human_ok, security_req, security_ok, peer_req, peer_ok) = score {
    requirements_met := 0
    total_requirements := 0
    
    requirements_met := requirements_met + 1 if human_req and human_ok
    requirements_met := requirements_met + 1 if not human_req
    total_requirements := total_requirements + 1
    
    requirements_met := requirements_met + 1 if security_req and security_ok
    requirements_met := requirements_met + 1 if not security_req
    total_requirements := total_requirements + 1
    
    requirements_met := requirements_met + 1 if peer_req and peer_ok
    requirements_met := requirements_met + 1 if not peer_req
    total_requirements := total_requirements + 1
    
    score := requirements_met / total_requirements
}

calculate_evolution_score(checks) = score {
    # Weighted average of all checks
    weights := [0.25, 0.35, 0.2, 0.15, 0.05]  # Risk, constitutional, performance, rollback, approval
    
    weighted_sum := sum([checks[i].score * weights[i] | i := range(0, count(checks))])
    
    score := weighted_sum
}