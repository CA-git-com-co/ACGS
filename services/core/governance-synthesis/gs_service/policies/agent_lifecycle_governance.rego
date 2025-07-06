# Agent Lifecycle Governance Policy
# Package: acgs.agent_lifecycle
#
# This policy governs the complete lifecycle of AI agents including creation,
# deployment, monitoring, evolution, and decommissioning within constitutional constraints.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.agent_lifecycle

import rego.v1

# Default deny for lifecycle operations
default allow_agent_creation := false
default allow_agent_deployment := false
default allow_agent_evolution := false
default allow_agent_decommission := false

# Agent lifecycle stages
lifecycle_stages := {
    "design": {
        "requirements": ["constitutional_analysis", "capability_specification", "risk_assessment"],
        "approvals_required": ["technical_review", "constitutional_review"],
        "documentation_required": ["design_document", "constitutional_impact_assessment"]
    },
    "development": {
        "requirements": ["secure_development", "testing_framework", "quality_assurance"],
        "approvals_required": ["code_review", "security_review"],
        "documentation_required": ["technical_specification", "security_analysis"]
    },
    "testing": {
        "requirements": ["functional_testing", "security_testing", "constitutional_compliance_testing"],
        "approvals_required": ["testing_approval", "constitutional_validation"],
        "documentation_required": ["test_results", "compliance_report"]
    },
    "deployment": {
        "requirements": ["production_readiness", "monitoring_setup", "rollback_plan"],
        "approvals_required": ["deployment_approval", "constitutional_certification"],
        "documentation_required": ["deployment_guide", "operational_procedures"]
    },
    "operation": {
        "requirements": ["continuous_monitoring", "performance_tracking", "compliance_verification"],
        "approvals_required": [],
        "documentation_required": ["operational_logs", "performance_reports"]
    },
    "evolution": {
        "requirements": ["evolution_justification", "impact_analysis", "constitutional_review"],
        "approvals_required": ["evolution_approval", "constitutional_revalidation"],
        "documentation_required": ["evolution_plan", "constitutional_update"]
    },
    "decommission": {
        "requirements": ["data_preservation", "knowledge_transfer", "impact_assessment"],
        "approvals_required": ["decommission_approval", "stakeholder_approval"],
        "documentation_required": ["decommission_plan", "post_mortem_analysis"]
    }
}

# Constitutional agent requirements
constitutional_agent_requirements := {
    "human_dignity": {
        "requirement": "Agent must respect and protect human dignity in all operations",
        "validation_methods": ["behavior_analysis", "decision_audit", "impact_assessment"],
        "weight": 1.0,
        "mandatory": true
    },
    "fairness": {
        "requirement": "Agent must ensure fair and unbiased treatment",
        "validation_methods": ["bias_testing", "fairness_metrics", "outcome_analysis"],
        "weight": 0.95,
        "mandatory": true
    },
    "transparency": {
        "requirement": "Agent decisions must be explainable and transparent",
        "validation_methods": ["explainability_testing", "decision_logging", "transparency_metrics"],
        "weight": 0.9,
        "mandatory": true
    },
    "accountability": {
        "requirement": "Clear accountability chains must be maintained",
        "validation_methods": ["responsibility_mapping", "audit_trails", "governance_verification"],
        "weight": 0.9,
        "mandatory": true
    },
    "safety": {
        "requirement": "Agent must operate safely and not cause harm",
        "validation_methods": ["safety_testing", "risk_assessment", "harm_prevention_analysis"],
        "weight": 1.0,
        "mandatory": true
    },
    "privacy": {
        "requirement": "Agent must protect individual privacy and data rights",
        "validation_methods": ["privacy_testing", "data_flow_analysis", "consent_verification"],
        "weight": 0.85,
        "mandatory": true
    }
}

# Agent capability categories
agent_capability_categories := {
    "cognitive": {
        "capabilities": ["reasoning", "learning", "memory", "planning"],
        "risk_level": "medium",
        "approval_threshold": 0.8
    },
    "autonomous": {
        "capabilities": ["autonomous_decision_making", "self_modification", "goal_setting"],
        "risk_level": "high",
        "approval_threshold": 0.9
    },
    "interaction": {
        "capabilities": ["human_interaction", "multi_agent_coordination", "external_communication"],
        "risk_level": "medium",
        "approval_threshold": 0.75
    },
    "physical": {
        "capabilities": ["robotic_control", "environmental_interaction", "physical_manipulation"],
        "risk_level": "high",
        "approval_threshold": 0.85
    },
    "data_processing": {
        "capabilities": ["data_analysis", "pattern_recognition", "information_synthesis"],
        "risk_level": "low",
        "approval_threshold": 0.7
    }
}

# Agent creation authorization
allow_agent_creation if {
    agent_spec := input.agent_specification
    creator := input.creator
    context := input.context

    # Creator authorization verified
    creator_authorized_for_creation(creator, agent_spec)

    # Agent specification valid
    agent_specification_valid(agent_spec)

    # Constitutional requirements satisfied
    constitutional_requirements_satisfied(agent_spec)

    # Risk assessment completed and acceptable
    creation_risk_acceptable(agent_spec, context)

    # Required approvals obtained
    creation_approvals_obtained(agent_spec, creator)

    # Resource allocation approved
    resource_allocation_approved(agent_spec, context)
}

# Agent deployment authorization
allow_agent_deployment if {
    agent := input.agent
    deployment_plan := input.deployment_plan
    operator := input.operator

    # Operator authorized for deployment
    operator_authorized_for_deployment(operator, agent)

    # Agent ready for deployment
    agent_deployment_ready(agent)

    # Deployment plan adequate
    deployment_plan_adequate(deployment_plan, agent)

    # Production environment suitable
    production_environment_suitable(deployment_plan.environment, agent)

    # Monitoring and safeguards in place
    monitoring_safeguards_adequate(deployment_plan, agent)

    # Constitutional compliance verified
    deployment_constitutional_compliant(agent, deployment_plan)
}

# Agent evolution authorization
allow_agent_evolution if {
    agent := input.agent
    evolution_request := input.evolution_request
    requestor := input.requestor

    # Requestor authorized for evolution
    requestor_authorized_for_evolution(requestor, agent)

    # Agent eligible for evolution
    agent_eligible_for_evolution(agent)

    # Evolution request valid
    evolution_request_valid(evolution_request, agent)

    # Evolution risk acceptable
    evolution_risk_acceptable(evolution_request, agent)

    # Constitutional impact assessed
    evolution_constitutional_impact_acceptable(evolution_request, agent)

    # Required approvals for evolution obtained
    evolution_approvals_obtained(evolution_request, agent)
}

# Agent decommission authorization
allow_agent_decommission if {
    agent := input.agent
    decommission_plan := input.decommission_plan
    requestor := input.requestor

    # Requestor authorized for decommission
    requestor_authorized_for_decommission(requestor, agent)

    # Decommission justification adequate
    decommission_justification_adequate(decommission_plan, agent)

    # Impact assessment completed
    decommission_impact_assessed(decommission_plan, agent)

    # Data preservation plan adequate
    data_preservation_adequate(decommission_plan, agent)

    # Knowledge transfer completed
    knowledge_transfer_completed(decommission_plan, agent)

    # Stakeholder approval obtained
    decommission_stakeholder_approval_obtained(decommission_plan, agent)
}

# Helper functions for creation
creator_authorized_for_creation(creator, agent_spec) if {
    # Creator has appropriate role and permissions
    creator.role in ["ai_architect", "senior_developer", "system_designer"]
    creator.permissions.agent_creation == true
    creator.security_clearance >= determine_required_clearance(agent_spec)

    # Creator has necessary qualifications
    creator.qualifications.ai_development == true
    creator.qualifications.constitutional_ai == true

    # No recent violations
    count(creator.recent_violations) == 0
}

determine_required_clearance(agent_spec) := clearance if {
    max_capability_risk := max([cat.risk_level |
                               some cat_name in agent_spec.capability_categories
                               cat := agent_capability_categories[cat_name]])
    clearance := clearance_for_risk_level(max_capability_risk)
}

clearance_for_risk_level("low") := 1
clearance_for_risk_level("medium") := 2
clearance_for_risk_level("high") := 3
clearance_for_risk_level("critical") := 4

agent_specification_valid(agent_spec) if {
    # Required fields present
    agent_spec.name
    agent_spec.purpose
    agent_spec.capability_categories
    agent_spec.constitutional_constraints
    agent_spec.resource_requirements

    # Capability categories valid
    all(cat, cat in agent_spec.capability_categories;
        cat in object.keys(agent_capability_categories))

    # Constitutional constraints specified
    all(constraint, constraint in constitutional_agent_requirements;
        constraint in agent_spec.constitutional_constraints)

    # Resource requirements reasonable
    resource_requirements_reasonable(agent_spec.resource_requirements)
}

resource_requirements_reasonable(requirements) if {
    # CPU, memory, storage within reasonable bounds
    requirements.cpu_cores <= 64
    requirements.memory_gb <= 512
    requirements.storage_gb <= 10240
    requirements.estimated_cost_monthly <= 50000
}

constitutional_requirements_satisfied(agent_spec) if {
    all(req_name, requirement in constitutional_agent_requirements;
        constitutional_requirement_satisfied(req_name, requirement, agent_spec))
}

constitutional_requirement_satisfied(req_name, requirement, agent_spec) if {
    # Requirement addressed in specification
    req_name in agent_spec.constitutional_constraints

    # Validation methods specified
    constraint_spec := agent_spec.constitutional_constraints[req_name]
    all(method, method in requirement.validation_methods;
        method in constraint_spec.validation_methods)

    # Implementation approach documented
    constraint_spec.implementation_approach
    constraint_spec.validation_criteria
}

creation_risk_acceptable(agent_spec, context) if {
    risk_assessment := agent_spec.risk_assessment

    # Risk assessment comprehensive
    risk_assessment_comprehensive(risk_assessment)

    # Overall risk within acceptable bounds
    risk_assessment.overall_risk_score <= acceptable_creation_risk_threshold(agent_spec)

    # High-risk areas have mitigation plans
    high_risk_mitigated(risk_assessment)

    # Constitutional risks assessed
    constitutional_risks_assessed(risk_assessment, agent_spec)
}

risk_assessment_comprehensive(risk_assessment) if {
    required_risk_categories := ["technical", "operational", "legal", "ethical", "constitutional"]
    all(category, category in required_risk_categories;
        category in risk_assessment.categories_assessed)

    risk_assessment.methodology_documented == true
    risk_assessment.stakeholder_input_considered == true
}

acceptable_creation_risk_threshold(agent_spec) := threshold if {
    max_capability_risk := max([agent_capability_categories[cat].risk_level |
                               cat := agent_spec.capability_categories[_]])
    threshold := risk_threshold_for_capability(max_capability_risk)
}

risk_threshold_for_capability("low") := 0.4
risk_threshold_for_capability("medium") := 0.3
risk_threshold_for_capability("high") := 0.2
risk_threshold_for_capability("critical") := 0.1

creation_approvals_obtained(agent_spec, creator) if {
    required_approvals := determine_required_creation_approvals(agent_spec)
    all(approval_type, approval_type in required_approvals;
        approval_obtained(agent_spec.approvals, approval_type))
}

determine_required_creation_approvals(agent_spec) := approvals if {
    base_approvals := ["technical_review", "constitutional_review"]

    additional_approvals := [approval |
        some condition, approval in additional_creation_approval_conditions
        creation_condition_met(agent_spec, condition)
    ]

    approvals := array.concat(base_approvals, additional_approvals)
}

additional_creation_approval_conditions := {
    "autonomous_capabilities": "ethics_committee_approval",
    "high_risk": "risk_committee_approval",
    "physical_capabilities": "safety_board_approval",
    "sensitive_data_access": "privacy_board_approval"
}

creation_condition_met(agent_spec, "autonomous_capabilities") if {
    "autonomous" in agent_spec.capability_categories
}

creation_condition_met(agent_spec, "high_risk") if {
    agent_spec.risk_assessment.overall_risk_score > 0.2
}

creation_condition_met(agent_spec, "physical_capabilities") if {
    "physical" in agent_spec.capability_categories
}

creation_condition_met(agent_spec, "sensitive_data_access") if {
    agent_spec.data_access_requirements.sensitive_data == true
}

approval_obtained(approvals, approval_type) if {
    approval := approvals[approval_type]
    approval.status == "approved"
    approval.approver_verified == true
    approval.approval_date > 0
    approval.expires_at > time.now_ns()
}

# Helper functions for deployment
operator_authorized_for_deployment(operator, agent) if {
    operator.role in ["deployment_engineer", "devops_specialist", "system_administrator"]
    operator.permissions.agent_deployment == true
    operator.experience.agent_deployment_years >= 2

    # Specific authorization for this agent type
    agent_type_authorization_valid(operator, agent)
}

agent_type_authorization_valid(operator, agent) if {
    agent_risk_level := determine_agent_risk_level(agent)
    operator.authorized_risk_levels[agent_risk_level] == true
}

determine_agent_risk_level(agent) := risk_level if {
    capability_risks := [agent_capability_categories[cat].risk_level |
                        cat := agent.capability_categories[_]]
    risk_level := max(capability_risks)
}

agent_deployment_ready(agent) if {
    # All lifecycle stage requirements met
    all(stage, stage in ["design", "development", "testing"];
        lifecycle_stage_completed(agent, stage))

    # Agent passes all tests
    agent.test_results.overall_pass == true
    agent.test_results.constitutional_compliance_pass == true
    agent.test_results.security_tests_pass == true

    # No critical issues outstanding
    count(agent.critical_issues) == 0

    # Documentation complete
    deployment_documentation_complete(agent)
}

lifecycle_stage_completed(agent, stage) if {
    stage_config := lifecycle_stages[stage]
    stage_status := agent.lifecycle_status[stage]

    # All requirements satisfied
    all(requirement, requirement in stage_config.requirements;
        requirement in stage_status.completed_requirements)

    # All approvals obtained
    all(approval, approval in stage_config.approvals_required;
        approval_obtained(stage_status.approvals, approval))

    # All documentation provided
    all(doc, doc in stage_config.documentation_required;
        doc in stage_status.completed_documentation)
}

deployment_plan_adequate(deployment_plan, agent) if {
    # Environment specifications complete
    deployment_plan.environment.specifications_complete == true
    deployment_plan.environment.capacity_adequate == true

    # Deployment strategy appropriate
    deployment_strategy_appropriate(deployment_plan.strategy, agent)

    # Rollback plan exists
    deployment_plan.rollback_plan.exists == true
    deployment_plan.rollback_plan.tested == true

    # Monitoring plan comprehensive
    monitoring_plan_comprehensive(deployment_plan.monitoring, agent)
}

deployment_strategy_appropriate(strategy, agent) if {
    agent_risk := determine_agent_risk_level(agent)
    strategy_for_risk_level(strategy, agent_risk)
}

strategy_for_risk_level(strategy, "low") if {
    strategy.type in ["direct", "blue_green", "canary"]
}

strategy_for_risk_level(strategy, "medium") if {
    strategy.type in ["blue_green", "canary"]
    strategy.validation_gates == true
}

strategy_for_risk_level(strategy, "high") if {
    strategy.type == "canary"
    strategy.validation_gates == true
    strategy.gradual_rollout == true
    strategy.human_oversight_required == true
}

monitoring_plan_comprehensive(monitoring, agent) if {
    # Performance monitoring
    monitoring.performance_metrics_defined == true
    monitoring.performance_thresholds_set == true

    # Constitutional compliance monitoring
    monitoring.constitutional_compliance_tracking == true
    monitoring.bias_detection_enabled == true

    # Security monitoring
    monitoring.security_monitoring_enabled == true
    monitoring.anomaly_detection_configured == true

    # Alert configuration
    monitoring.alert_escalation_defined == true
    monitoring.incident_response_integrated == true
}

# Helper functions for evolution
evolution_request_valid(evolution_request, agent) if {
    # Request has required information
    evolution_request.type in ["capability_enhancement", "behavior_modification", "performance_optimization"]
    evolution_request.justification
    evolution_request.expected_outcomes
    evolution_request.risk_assessment

    # Impact analysis completed
    evolution_request.impact_analysis.technical_impact
    evolution_request.impact_analysis.operational_impact
    evolution_request.impact_analysis.constitutional_impact

    # Implementation plan exists
    evolution_request.implementation_plan.steps
    evolution_request.implementation_plan.timeline
    evolution_request.implementation_plan.validation_criteria
}

evolution_constitutional_impact_acceptable(evolution_request, agent) if {
    constitutional_impact := evolution_request.impact_analysis.constitutional_impact

    # No negative impact on mandatory constitutional requirements
    all(req_name, requirement in constitutional_agent_requirements;
        requirement.mandatory == false or
        constitutional_impact.principles[req_name].impact_severity != "negative")

    # Overall constitutional compliance maintained or improved
    constitutional_impact.overall_compliance_change >= 0

    # Mitigation plans for any negative impacts
    negative_impacts_mitigated(constitutional_impact)
}

negative_impacts_mitigated(constitutional_impact) if {
    negative_impacts := [principle |
        some principle_name, impact in constitutional_impact.principles
        impact.impact_severity == "negative"
    ]

    all(impact, impact in negative_impacts;
        mitigation_plan_adequate(constitutional_impact.mitigation_plans[impact]))
}

mitigation_plan_adequate(mitigation_plan) if {
    mitigation_plan.measures
    mitigation_plan.effectiveness_verified == true
    mitigation_plan.implementation_timeline
    mitigation_plan.success_criteria
}

# Agent lifecycle monitoring
agent_lifecycle_compliant := compliant if {
    agent := input.agent
    current_stage := agent.current_lifecycle_stage

    # Current stage requirements satisfied
    current_stage_compliant := lifecycle_stage_requirements_met(agent, current_stage)

    # Constitutional requirements continuously satisfied
    constitutional_compliance_maintained := agent_constitutional_compliance_current(agent)

    # Performance within acceptable bounds
    performance_acceptable := agent_performance_acceptable(agent)

    # No critical violations
    no_critical_violations := count(agent.critical_violations) == 0

    compliant := current_stage_compliant and constitutional_compliance_maintained and
                performance_acceptable and no_critical_violations
}

lifecycle_stage_requirements_met(agent, stage) if {
    stage_config := lifecycle_stages[stage]

    # Ongoing requirements satisfied
    ongoing_requirements := [req |
        some req in stage_config.requirements
        requirement_is_ongoing(req)
    ]

    all(requirement, requirement in ongoing_requirements;
        ongoing_requirement_satisfied(agent, requirement))
}

requirement_is_ongoing("continuous_monitoring") := true
requirement_is_ongoing("performance_tracking") := true
requirement_is_ongoing("compliance_verification") := true
requirement_is_ongoing(_) := false

ongoing_requirement_satisfied(agent, "continuous_monitoring") if {
    agent.monitoring.status == "active"
    agent.monitoring.last_health_check > time.now_ns() - (300 * 1000000000) # 5 minutes
}

ongoing_requirement_satisfied(agent, "performance_tracking") if {
    agent.performance_tracking.enabled == true
    agent.performance_tracking.metrics_current == true
}

ongoing_requirement_satisfied(agent, "compliance_verification") if {
    agent.compliance_verification.last_check > time.now_ns() - (3600 * 1000000000) # 1 hour
    agent.compliance_verification.status == "compliant"
}

agent_constitutional_compliance_current(agent) if {
    agent.constitutional_compliance.last_assessment > time.now_ns() - (86400 * 1000000000) # 24 hours
    agent.constitutional_compliance.overall_score >= 0.8
    count(agent.constitutional_compliance.violations) == 0
}

agent_performance_acceptable(agent) if {
    performance := agent.performance_metrics

    # Key performance indicators within bounds
    performance.response_time <= performance.sla_response_time
    performance.accuracy_rate >= performance.minimum_accuracy
    performance.availability >= 0.99

    # Resource utilization reasonable
    performance.resource_utilization.cpu <= 0.8
    performance.resource_utilization.memory <= 0.8

    # Error rates acceptable
    performance.error_rate <= 0.01
}
