# Evolutionary Governance Policy
# Package: acgs.evolutionary_governance
#
# This policy governs agent evolution, capability upgrades, and adaptive
# governance mechanisms within the ACGS constitutional framework.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.evolutionary_governance

import rego.v1

# Default deny for evolution operations
default allow_evolution := false
default allow_capability_upgrade := false
default allow_autonomous_adaptation := false

# Evolution risk categories
evolution_risk_categories := {
    "capability_enhancement": {
        "risk_level": "medium",
        "approval_required": true,
        "testing_required": true,
        "rollback_plan_required": true
    },
    "behavior_modification": {
        "risk_level": "high",
        "approval_required": true,
        "testing_required": true,
        "constitutional_review_required": true
    },
    "autonomy_increase": {
        "risk_level": "critical",
        "approval_required": true,
        "testing_required": true,
        "constitutional_review_required": true,
        "human_oversight_required": true
    },
    "safety_mechanism_change": {
        "risk_level": "critical",
        "approval_required": true,
        "testing_required": true,
        "multi_party_approval_required": true
    }
}

# Constitutional constraints for evolution
constitutional_evolution_constraints := {
    "human_dignity": {
        "constraint": "Evolution must not compromise human dignity or autonomy",
        "validation_required": true,
        "weight": 1.0
    },
    "fairness": {
        "constraint": "Evolution must maintain fairness in decision-making",
        "validation_required": true,
        "weight": 0.9
    },
    "transparency": {
        "constraint": "Evolution processes must be transparent and explainable",
        "validation_required": true,
        "weight": 0.8
    },
    "accountability": {
        "constraint": "Clear accountability must be maintained post-evolution",
        "validation_required": true,
        "weight": 0.9
    },
    "safety": {
        "constraint": "Evolution must not compromise system safety",
        "validation_required": true,
        "weight": 1.0
    }
}

# Agent evolution approval
allow_evolution if {
    agent := input.agent
    evolution_request := input.evolution_request

    # Validate agent eligibility for evolution
    agent_eligible_for_evolution(agent)

    # Check evolution request validity
    evolution_request_valid(evolution_request)

    # Risk assessment passed
    evolution_risk_acceptable(evolution_request)

    # Constitutional constraints satisfied
    constitutional_constraints_satisfied(evolution_request)

    # Required approvals obtained
    required_approvals_obtained(evolution_request)

    # Rollback plan exists
    rollback_plan_exists(evolution_request)
}

# Capability upgrade authorization
allow_capability_upgrade if {
    agent := input.agent
    capability := input.capability
    upgrade_request := input.upgrade_request

    # Agent must be in good standing
    agent_in_good_standing(agent)

    # Capability upgrade must be compatible
    capability_compatible(agent, capability)

    # Safety checks passed
    capability_safety_verified(capability, upgrade_request)

    # Resource constraints satisfied
    resource_constraints_satisfied(agent, capability)

    # Constitutional compliance verified
    capability_constitutional_compliant(capability)
}

# Autonomous adaptation authorization
allow_autonomous_adaptation if {
    agent := input.agent
    adaptation := input.adaptation

    # Agent has autonomous adaptation privileges
    agent_has_adaptation_privileges(agent)

    # Adaptation within allowed parameters
    adaptation_within_bounds(agent, adaptation)

    # No constitutional violations
    adaptation_constitutional_safe(adaptation)

    # Continuous monitoring enabled
    monitoring_enabled(agent, adaptation)

    # Emergency stop mechanism available
    emergency_stop_available(agent, adaptation)
}

# Helper functions for agent validation
agent_eligible_for_evolution(agent) if {
    agent.status == "active"
    agent.constitutional_compliance_score >= 0.8
    agent.safety_record_score >= 0.9
    agent.last_evolution_timestamp < time.now_ns() - (24 * 60 * 60 * 1000000000) # 24 hours
    not agent.evolution_locked
}

agent_in_good_standing(agent) if {
    agent.status == "active"
    agent.constitutional_compliance_score >= 0.7
    count(agent.recent_violations) == 0
    agent.performance_score >= 0.6
}

agent_has_adaptation_privileges(agent) if {
    agent.adaptation_level in {"limited", "moderate", "advanced"}
    agent.constitutional_compliance_score >= 0.9
    agent.safety_certification_current == true
    agent.human_oversight_enabled == true
}

# Evolution request validation
evolution_request_valid(request) if {
    request.type in {"capability_enhancement", "behavior_modification", "autonomy_increase", "safety_mechanism_change"}
    request.description
    request.justification
    request.expected_outcomes
    request.risk_assessment
    request.constitutional_impact_analysis
}

evolution_risk_acceptable(request) if {
    risk_category := evolution_risk_categories[request.type]
    risk_score := calculate_evolution_risk_score(request)

    # Risk score within acceptable bounds
    risk_score <= acceptable_risk_threshold(risk_category.risk_level)

    # All required risk mitigation measures in place
    risk_mitigation_adequate(request, risk_category)
}

calculate_evolution_risk_score(request) := score if {
    base_risk := base_risk_score(request.type)
    complexity_factor := complexity_risk_factor(request)
    novelty_factor := novelty_risk_factor(request)
    impact_factor := impact_risk_factor(request)

    score := base_risk * (1 + complexity_factor + novelty_factor + impact_factor)
}

base_risk_score("capability_enhancement") := 0.3
base_risk_score("behavior_modification") := 0.6
base_risk_score("autonomy_increase") := 0.8
base_risk_score("safety_mechanism_change") := 0.9

complexity_risk_factor(request) := factor if {
    complexity := request.complexity_score
    factor := complexity / 10.0  # Normalize to 0-1 range
}

novelty_risk_factor(request) := factor if {
    novelty := request.novelty_score
    factor := novelty / 10.0  # Normalize to 0-1 range
}

impact_risk_factor(request) := factor if {
    impact := request.impact_score
    factor := impact / 10.0  # Normalize to 0-1 range
}

acceptable_risk_threshold("low") := 0.3
acceptable_risk_threshold("medium") := 0.5
acceptable_risk_threshold("high") := 0.7
acceptable_risk_threshold("critical") := 0.8

risk_mitigation_adequate(request, risk_category) if {
    # Check all required mitigation measures are present
    all(measure, measure in risk_category.required_mitigations;
        measure in request.mitigation_measures)

    # Validate mitigation effectiveness
    all(measure, measure in request.mitigation_measures;
        mitigation_measure_effective(measure, request))
}

mitigation_measure_effective(measure, request) if {
    measure.effectiveness_score >= 0.7
    measure.implementation_verified == true
    measure.monitoring_enabled == true
}

# Constitutional constraints validation
constitutional_constraints_satisfied(request) if {
    all(constraint_name, constraint in constitutional_evolution_constraints;
        constraint_satisfied(constraint_name, constraint, request))
}

constraint_satisfied(constraint_name, constraint, request) if {
    constraint_analysis := request.constitutional_impact_analysis[constraint_name]
    constraint_analysis.compliant == true
    constraint_analysis.confidence_score >= 0.8
    constraint_analysis.mitigation_plan_adequate == true
}

# Approval workflow validation
required_approvals_obtained(request) if {
    risk_category := evolution_risk_categories[request.type]
    approvals_required := determine_required_approvals(risk_category)

    all(approval_type, approval_type in approvals_required;
        approval_obtained(request, approval_type))
}

determine_required_approvals(risk_category) := approvals if {
    base_approvals := ["technical_review", "constitutional_review"]

    additional_approvals := [approval |
        some condition, approval in additional_approval_conditions
        condition_met(risk_category, condition)
    ]

    approvals := array.concat(base_approvals, additional_approvals)
}

additional_approval_conditions := {
    "high_risk": "ethics_committee_approval",
    "critical_risk": "human_oversight_board_approval",
    "multi_party_required": "multi_stakeholder_approval",
    "safety_critical": "safety_board_approval"
}

condition_met(risk_category, "high_risk") if {
    risk_category.risk_level in {"high", "critical"}
}

condition_met(risk_category, "critical_risk") if {
    risk_category.risk_level == "critical"
}

condition_met(risk_category, "multi_party_required") if {
    risk_category.multi_party_approval_required == true
}

condition_met(risk_category, "safety_critical") if {
    risk_category.safety_review_required == true
}

approval_obtained(request, approval_type) if {
    approval := request.approvals[approval_type]
    approval.status == "approved"
    approval.approver_verified == true
    approval.timestamp > request.submission_timestamp
    approval.expires_at > time.now_ns()
}

# Rollback plan validation
rollback_plan_exists(request) if {
    rollback_plan := request.rollback_plan
    rollback_plan.steps
    rollback_plan.triggers
    rollback_plan.validation_criteria
    rollback_plan.estimated_rollback_time
    rollback_plan.data_preservation_plan
    rollback_plan.stakeholder_notification_plan
}

# Capability upgrade validation
capability_compatible(agent, capability) if {
    # Check compatibility matrix
    compatibility := data.capability_compatibility[agent.type][capability.type]
    compatibility.compatible == true
    compatibility.version_compatible == true

    # Check resource requirements
    agent.available_resources >= capability.resource_requirements

    # Check dependency satisfaction
    all(dep, dep in capability.dependencies; dependency_satisfied(agent, dep))
}

dependency_satisfied(agent, dependency) if {
    dependency.type == "capability"
    dependency.name in agent.current_capabilities
    agent.capability_versions[dependency.name] >= dependency.min_version
}

dependency_satisfied(agent, dependency) if {
    dependency.type == "resource"
    agent.available_resources[dependency.resource_type] >= dependency.amount
}

capability_safety_verified(capability, upgrade_request) if {
    safety_analysis := upgrade_request.safety_analysis
    safety_analysis.risk_score <= 0.5
    safety_analysis.safety_measures_adequate == true
    safety_analysis.testing_completed == true
    safety_analysis.validation_passed == true
}

resource_constraints_satisfied(agent, capability) if {
    total_resource_usage := calculate_total_resource_usage(agent, capability)
    all(resource_type, usage in total_resource_usage;
        usage <= agent.resource_limits[resource_type])
}

calculate_total_resource_usage(agent, capability) := total_usage if {
    current_usage := agent.current_resource_usage
    capability_usage := capability.resource_requirements

    total_usage := {resource_type: current_usage[resource_type] + capability_usage[resource_type] |
                   some resource_type in object.keys(current_usage)}
}

capability_constitutional_compliant(capability) if {
    # Check capability against constitutional principles
    all(principle, principle in constitutional_evolution_constraints;
        capability_respects_principle(capability, principle))
}

capability_respects_principle(capability, principle) if {
    principle_check := capability.constitutional_analysis[principle]
    principle_check.compliant == true
    principle_check.confidence >= 0.8
}

# Autonomous adaptation validation
adaptation_within_bounds(agent, adaptation) if {
    adaptation_bounds := agent.adaptation_bounds

    # Check parameter bounds
    all(param, value in adaptation.parameters;
        param_within_bounds(param, value, adaptation_bounds))

    # Check rate limits
    adaptation_rate_acceptable(agent, adaptation)

    # Check scope limits
    adaptation_scope_acceptable(agent, adaptation)
}

param_within_bounds(param, value, bounds) if {
    param_bounds := bounds.parameters[param]
    value >= param_bounds.min
    value <= param_bounds.max
}

adaptation_rate_acceptable(agent, adaptation) if {
    current_adaptations := count(agent.recent_adaptations)
    rate_limit := agent.adaptation_bounds.rate_limit
    current_adaptations < rate_limit
}

adaptation_scope_acceptable(agent, adaptation) if {
    adaptation.scope in agent.adaptation_bounds.allowed_scopes
    adaptation.impact_level <= agent.adaptation_bounds.max_impact_level
}

adaptation_constitutional_safe(adaptation) if {
    # Verify adaptation doesn't violate constitutional principles
    all(principle, weight in constitutional_evolution_constraints;
        adaptation_safe_for_principle(adaptation, principle))
}

adaptation_safe_for_principle(adaptation, principle) if {
    principle_impact := adaptation.constitutional_impact[principle]
    principle_impact.safe == true
    principle_impact.risk_score <= 0.3
}

monitoring_enabled(agent, adaptation) if {
    monitoring_plan := adaptation.monitoring_plan
    monitoring_plan.continuous_monitoring == true
    monitoring_plan.alert_conditions
    monitoring_plan.reporting_frequency
    monitoring_plan.stakeholder_notifications
}

emergency_stop_available(agent, adaptation) if {
    emergency_stop := adaptation.emergency_stop
    emergency_stop.available == true
    emergency_stop.trigger_conditions
    emergency_stop.response_time <= 30  # seconds
    emergency_stop.rollback_capability == true
}

# Evolution outcome validation
evolution_outcome_acceptable := outcome if {
    evolution_result := input.evolution_result
    baseline_metrics := input.baseline_metrics

    # Compare post-evolution metrics with baseline
    performance_improvement := calculate_performance_improvement(evolution_result, baseline_metrics)
    constitutional_compliance_maintained := constitutional_compliance_check(evolution_result)
    safety_maintained := safety_check(evolution_result)

    outcome := {
        "acceptable": performance_improvement >= 0.05,  # 5% improvement required
        "constitutional_compliant": constitutional_compliance_maintained,
        "safety_maintained": safety_maintained,
        "performance_score": performance_improvement
    }
}

calculate_performance_improvement(result, baseline) := improvement if {
    result_score := result.performance_metrics.overall_score
    baseline_score := baseline.performance_metrics.overall_score
    improvement := (result_score - baseline_score) / baseline_score
}

constitutional_compliance_check(result) if {
    result.constitutional_compliance_score >= 0.8
    count(result.constitutional_violations) == 0
}

safety_check(result) if {
    result.safety_score >= 0.9
    count(result.safety_incidents) == 0
    result.safety_mechanisms_functional == true
}
