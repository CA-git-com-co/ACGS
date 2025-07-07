# Accountability Governance Policy
# Package: acgs.accountability
#
# This policy enforces accountability requirements for all governance decisions
# ensuring clear responsibility chains and remediation mechanisms.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.accountability

import rego.v1

# Default deny for accountability compliance
default allow_action := false

# Default accountability compliance score
default accountability_score := 0.0

# Accountability requirements
accountability_requirements := {
    "responsibility_assignment": {
        "description": "Clear assignment of responsibility for decisions and outcomes",
        "weight": 0.3,
        "mandatory": true
    },
    "oversight_mechanisms": {
        "description": "Appropriate oversight and review mechanisms must be in place",
        "weight": 0.25,
        "mandatory": true
    },
    "remediation_process": {
        "description": "Clear processes for addressing errors or harm",
        "weight": 0.2,
        "mandatory": true
    },
    "performance_monitoring": {
        "description": "Continuous monitoring of decision outcomes and impacts",
        "weight": 0.15,
        "mandatory": false
    },
    "stakeholder_recourse": {
        "description": "Mechanisms for stakeholders to seek recourse or appeal",
        "weight": 0.1,
        "mandatory": false
    }
}

# Role definitions for accountability
accountability_roles := {
    "decision_maker": {
        "responsibilities": ["final_decision", "outcome_ownership"],
        "required_qualifications": ["domain_expertise", "governance_training"]
    },
    "oversight_authority": {
        "responsibilities": ["review_decisions", "ensure_compliance"],
        "required_qualifications": ["independence", "relevant_expertise"]
    },
    "remediation_officer": {
        "responsibilities": ["investigate_issues", "implement_corrections"],
        "required_qualifications": ["investigation_skills", "corrective_authority"]
    }
}

# Allow action if accountability requirements are met
allow_action if {
    input.action_type in {"policy_execution", "governance_decision", "constitutional_interpretation", "oversight_action"}
    accountability_compliance_check
    has_responsible_parties
    has_oversight_framework
    has_remediation_mechanism
    meets_minimum_accountability_score
}

# Check accountability compliance
accountability_compliance_check if {
    # Action must have designated responsible parties
    count(input.responsible_parties) > 0
    
    # Action must have oversight mechanism
    input.oversight_framework
    
    # Action must have remediation process
    input.remediation_process
    
    # Action must have monitoring plan
    valid_monitoring_plan
}

# Validate responsible parties assignment
has_responsible_parties if {
    # Must have at least one decision maker
    some party
    input.responsible_parties[_] == party
    party.role == "decision_maker"
    valid_role_assignment(party)
}

# Validate oversight framework
has_oversight_framework if {
    input.oversight_framework.authority
    input.oversight_framework.review_frequency
    input.oversight_framework.escalation_path
    input.oversight_framework.reporting_requirements
}

# Validate remediation mechanism
has_remediation_mechanism if {
    input.remediation_process.issue_identification
    input.remediation_process.investigation_procedure
    input.remediation_process.correction_mechanism
    input.remediation_process.prevention_measures
}

# Validate monitoring plan
valid_monitoring_plan if {
    input.monitoring_plan.metrics
    input.monitoring_plan.frequency
    input.monitoring_plan.responsible_party
    input.monitoring_plan.reporting_schedule
}

# Validate role assignment
valid_role_assignment(party) if {
    accountability_roles[party.role]
    role_def := accountability_roles[party.role]
    
    # Check qualifications
    has_required_qualifications(party, role_def.required_qualifications)
    
    # Check responsibilities are understood
    responsibilities_acknowledged(party, role_def.responsibilities)
}

# Check required qualifications
has_required_qualifications(party, required_quals) if {
    party.qualifications
    all_qualifications_met(party.qualifications, required_quals)
}

all_qualifications_met(party_quals, required_quals) if {
    count([qual | 
        some required_qual
        required_quals[_] == required_qual
        some party_qual
        party_quals[_] == party_qual
        party_qual == required_qual
    ]) == count(required_quals)
}

# Check responsibilities are acknowledged
responsibilities_acknowledged(party, responsibilities) if {
    party.acknowledged_responsibilities
    count([resp |
        some responsibility
        responsibilities[_] == responsibility
        some ack_resp
        party.acknowledged_responsibilities[_] == ack_resp
        ack_resp == responsibility
    ]) == count(responsibilities)
}

# Calculate accountability score
accountability_score := score if {
    scores := [requirement_score |
        some requirement_id
        accountability_requirements[requirement_id]
        requirement := accountability_requirements[requirement_id]
        requirement_score := calculate_accountability_score(requirement_id, requirement)
    ]
    score := sum(scores) / count(scores)
}

# Calculate score for individual accountability requirement
calculate_accountability_score(requirement_id, requirement) := score if {
    accountability_requirement_satisfied(requirement_id)
    score := requirement.weight
}

calculate_accountability_score(requirement_id, requirement) := score if {
    not accountability_requirement_satisfied(requirement_id)
    requirement.mandatory == true
    score := 0.0
}

calculate_accountability_score(requirement_id, requirement) := score if {
    not accountability_requirement_satisfied(requirement_id)
    requirement.mandatory == false
    score := requirement.weight * 0.4  # Partial credit for non-mandatory requirements
}

# Check if specific accountability requirement is satisfied
accountability_requirement_satisfied("responsibility_assignment") if {
    has_responsible_parties
    input.responsibility_clarity_score >= 0.8
}

accountability_requirement_satisfied("oversight_mechanisms") if {
    has_oversight_framework
    input.oversight_framework.effectiveness_score >= 0.7
}

accountability_requirement_satisfied("remediation_process") if {
    has_remediation_mechanism
    input.remediation_process.completeness_score >= 0.8
}

accountability_requirement_satisfied("performance_monitoring") if {
    valid_monitoring_plan
    input.monitoring_plan.coverage_score >= 0.7
}

accountability_requirement_satisfied("stakeholder_recourse") if {
    input.stakeholder_recourse.available == true
    count(input.stakeholder_recourse.mechanisms) > 0
    input.stakeholder_recourse.accessibility_score >= 0.7
}

# Minimum accountability score requirement
meets_minimum_accountability_score if {
    accountability_score >= 0.8
}

# Accountability violation checks
accountability_violations := violations if {
    violations := [violation |
        violation_checks := [
            {"type": "unclear_responsibility", "violated": unclear_responsibility},
            {"type": "insufficient_oversight", "violated": insufficient_oversight},
            {"type": "missing_remediation", "violated": missing_remediation},
            {"type": "inadequate_monitoring", "violated": inadequate_monitoring},
            {"type": "no_recourse_mechanism", "violated": no_recourse_mechanism}
        ]
        some check
        violation_checks[_] == check
        check.violated == true
        violation := check.type
    ]
}

# Check for unclear responsibility
unclear_responsibility if {
    not has_responsible_parties
}

unclear_responsibility if {
    input.responsibility_clarity_score < 0.6
}

# Check for insufficient oversight
insufficient_oversight if {
    not has_oversight_framework
}

insufficient_oversight if {
    input.oversight_framework.independence_score < 0.7
}

# Check for missing remediation
missing_remediation if {
    not has_remediation_mechanism
}

missing_remediation if {
    input.remediation_process.response_time_sla == ""
}

# Check for inadequate monitoring
inadequate_monitoring if {
    not valid_monitoring_plan
}

inadequate_monitoring if {
    input.monitoring_plan.coverage_score < 0.5
}

# Check for no recourse mechanism
no_recourse_mechanism if {
    input.action_impact_level in {"high", "critical"}
    input.stakeholder_recourse.available == false
}

# Accountability enhancement recommendations
accountability_recommendations := recommendations if {
    recommendations := [recommendation |
        some requirement_id
        accountability_requirements[requirement_id]
        requirement := accountability_requirements[requirement_id]
        not accountability_requirement_satisfied(requirement_id)
        recommendation := generate_accountability_recommendation(requirement_id, requirement)
    ]
}

generate_accountability_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "responsibility_assignment"
    recommendation := "Clarify decision-making roles and assign specific individuals to each responsibility"
}

generate_accountability_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "oversight_mechanisms"
    recommendation := "Establish independent oversight body with clear review authority and escalation procedures"
}

generate_accountability_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "remediation_process"
    recommendation := "Define clear remediation procedures with response time SLAs and correction mechanisms"
}

generate_accountability_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "performance_monitoring"
    recommendation := "Implement comprehensive monitoring with metrics, dashboards, and regular reporting"
}

generate_accountability_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "stakeholder_recourse"
    recommendation := "Provide accessible mechanisms for stakeholders to appeal decisions or seek remediation"
}

# Accountability trail for audit
accountability_trail := {
    "decision_chain": input.responsible_parties,
    "oversight_actions": input.oversight_framework.review_history,
    "monitoring_results": input.monitoring_plan.results,
    "remediation_actions": input.remediation_process.actions_taken,
    "stakeholder_interactions": input.stakeholder_recourse.cases,
    "constitutional_compliance": {
        "hash": "cdd01ef066bc6cf2",
        "validated_at": time.now_ns(),
        "validator": "acgs.accountability"
    }
}

# Accountability compliance report
accountability_report := {
    "allowed": allow_action,
    "accountability_score": accountability_score,
    "violations": accountability_violations,
    "recommendations": accountability_recommendations,
    "accountability_trail": accountability_trail,
    "requirement_scores": requirement_scores,
    "constitutional_hash": "cdd01ef066bc6cf2"
}

# Individual requirement scores
requirement_scores := scores if {
    scores := {requirement_id: calculate_accountability_score(requirement_id, requirement) |
        some requirement_id
        accountability_requirements[requirement_id]
        requirement := accountability_requirements[requirement_id]
    }
}