# Human Dignity Governance Policy
# Package: acgs.human_dignity
#
# This policy enforces human dignity principles including respect for persons,
# human autonomy, and protection of fundamental human rights.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.human_dignity

import rego.v1

# Default deny for human dignity compliance
default allow_action := false

# Default human dignity compliance score
default dignity_score := 0.0

# Human dignity requirements
dignity_requirements := {
    "respect_for_persons": {
        "description": "Treat all persons as ends in themselves, never merely as means",
        "weight": 0.35,
        "mandatory": true
    },
    "human_autonomy": {
        "description": "Respect and preserve human agency and decision-making capacity",
        "weight": 0.3,
        "mandatory": true
    },
    "fundamental_rights": {
        "description": "Protect and uphold fundamental human rights",
        "weight": 0.2,
        "mandatory": true
    },
    "human_welfare": {
        "description": "Promote human flourishing and well-being",
        "weight": 0.1,
        "mandatory": false
    },
    "dignity_preservation": {
        "description": "Maintain human dignity even in error correction or enforcement",
        "weight": 0.05,
        "mandatory": true
    }
}

# Fundamental human rights checklist
fundamental_rights := {
    "life": "Right to life and physical security",
    "liberty": "Right to freedom and personal autonomy",
    "privacy": "Right to privacy and personal data protection",
    "expression": "Right to freedom of expression and opinion",
    "association": "Right to freedom of association and assembly",
    "due_process": "Right to fair treatment and due process",
    "equality": "Right to equal treatment and non-discrimination",
    "education": "Right to access information and education",
    "participation": "Right to participate in decisions affecting oneself"
}

# Prohibited dignity violations
dignity_violations := {
    "dehumanization": [
        "treating persons as objects",
        "reducing humans to mere data points",
        "denying human agency"
    ],
    "instrumentalization": [
        "using persons solely as means to ends",
        "treating humans as mere resources",
        "exploitation without consent"
    ],
    "degradation": [
        "humiliating treatment",
        "public shaming without due process",
        "cruel or unusual punishment"
    ],
    "autonomy_violation": [
        "coercion without justification",
        "manipulation through deception",
        "paternalism without consent"
    ]
}

# Allow action if human dignity requirements are met
allow_action if {
    input.action_type in {"governance_decision", "policy_implementation", "enforcement_action", "system_operation"}
    dignity_compliance_check
    no_dignity_violations
    respects_human_autonomy
    protects_fundamental_rights
    meets_minimum_dignity_score
}

# Check human dignity compliance
dignity_compliance_check if {
    # Action must include dignity impact assessment
    input.dignity_impact_assessment
    
    # Action must respect human agency
    human_agency_preserved
    
    # Action must have consent mechanism where required
    consent_mechanism_appropriate
    
    # Action must have safeguards against abuse
    abuse_safeguards_present
}

# Verify human agency is preserved
human_agency_preserved if {
    input.human_agency.preserved == true
    input.human_agency.decision_points_identified
    input.human_agency.override_mechanisms
}

# Verify appropriate consent mechanism
consent_mechanism_appropriate if {
    # For high-impact actions, explicit consent required
    input.impact_level in {"low", "medium"}
}

consent_mechanism_appropriate if {
    input.impact_level in {"high", "critical"}
    input.consent.type in {"explicit", "informed"}
    input.consent.freely_given == true
    input.consent.revocable == true
}

# Verify abuse safeguards are present
abuse_safeguards_present if {
    input.safeguards.human_oversight == true
    input.safeguards.appeal_mechanism
    input.safeguards.audit_trail
    input.safeguards.harm_detection
}

# Check for dignity violations
no_dignity_violations if {
    not dehumanization_detected
    not instrumentalization_detected
    not degradation_detected
    not autonomy_violation_detected
}

# Dehumanization detection
dehumanization_detected if {
    # Check for language that treats humans as objects
    contains(lower(input.action_description), "human resources")
    not contains(lower(input.action_description), "human resources department")
}

dehumanization_detected if {
    contains(lower(input.action_description), "process humans")
}

dehumanization_detected if {
    input.human_consideration.agency_ignored == true
}

# Instrumentalization detection
instrumentalization_detected if {
    input.benefit_analysis.human_benefit == 0
    input.benefit_analysis.system_benefit > 0
    not legitimate_system_priority
}

instrumentalization_detected if {
    # Using humans solely for data without benefit
    input.data_usage.purpose == "pure_extraction"
    input.data_usage.human_benefit == false
}

legitimate_system_priority if {
    input.priority_justification.safety_critical == true
    input.priority_justification.legal_requirement == true
}

legitimate_system_priority if {
    input.priority_justification.emergency_response == true
    input.priority_justification.harm_prevention == true
}

# Degradation detection
degradation_detected if {
    input.treatment_quality.respectful == false
}

degradation_detected if {
    contains(lower(input.action_description), "shame")
    not contains(lower(input.action_description), "without shame")
}

degradation_detected if {
    input.enforcement_method.humiliating == true
}

# Autonomy violation detection
autonomy_violation_detected if {
    input.coercion.present == true
    not input.coercion.justified == true
}

autonomy_violation_detected if {
    input.manipulation.deceptive == true
}

autonomy_violation_detected if {
    input.paternalism.overrides_choice == true
    not input.paternalism.incapacity_justified == true
}

# Verify respect for human autonomy
respects_human_autonomy if {
    # Humans retain meaningful choice
    meaningful_choice_preserved
    
    # Information for informed decisions provided
    informed_decision_support
    
    # Override mechanisms available
    override_mechanisms_available
}

meaningful_choice_preserved if {
    input.choice_preservation.options_available > 1
    input.choice_preservation.real_alternatives == true
    input.choice_preservation.no_coercion == true
}

informed_decision_support if {
    input.information_provision.adequate == true
    input.information_provision.understandable == true
    input.information_provision.timely == true
}

override_mechanisms_available if {
    input.override_mechanisms.human_review == true
    input.override_mechanisms.appeal_process == true
    input.override_mechanisms.opt_out_option == true
}

# Verify protection of fundamental rights
protects_fundamental_rights if {
    no_fundamental_rights_violations
    positive_rights_protection
}

no_fundamental_rights_violations if {
    not violates_right_to_life
    not violates_right_to_liberty
    not violates_right_to_privacy
    not violates_due_process
}

violates_right_to_life if {
    input.safety_impact.life_threatening == true
    not input.safety_justification.proportionate == true
}

violates_right_to_liberty if {
    input.liberty_impact.restricts_freedom == true
    not input.liberty_restriction.legally_justified == true
}

violates_right_to_privacy if {
    input.privacy_impact.invasive == true
    not input.privacy_justification.proportionate == true
}

violates_due_process if {
    input.procedural_fairness.due_process == false
    input.impact_level in {"medium", "high", "critical"}
}

positive_rights_protection if {
    input.rights_protection.active_protection == true
    input.rights_protection.enhancement_considered == true
}

# Calculate human dignity score
dignity_score := score if {
    scores := [requirement_score |
        some requirement_id
        dignity_requirements[requirement_id]
        requirement := dignity_requirements[requirement_id]
        requirement_score := calculate_dignity_score(requirement_id, requirement)
    ]
    score := sum(scores) / count(scores)
}

# Calculate score for individual dignity requirement
calculate_dignity_score(requirement_id, requirement) := score if {
    dignity_requirement_satisfied(requirement_id)
    score := requirement.weight
}

calculate_dignity_score(requirement_id, requirement) := score if {
    not dignity_requirement_satisfied(requirement_id)
    requirement.mandatory == true
    score := 0.0
}

calculate_dignity_score(requirement_id, requirement) := score if {
    not dignity_requirement_satisfied(requirement_id)
    requirement.mandatory == false
    score := requirement.weight * 0.2  # Minimal partial credit for dignity
}

# Check if specific dignity requirement is satisfied
dignity_requirement_satisfied("respect_for_persons") if {
    not dehumanization_detected
    not instrumentalization_detected
    input.person_respect_score >= 0.9
}

dignity_requirement_satisfied("human_autonomy") if {
    respects_human_autonomy
    not autonomy_violation_detected
    input.autonomy_preservation_score >= 0.85
}

dignity_requirement_satisfied("fundamental_rights") if {
    protects_fundamental_rights
    input.rights_protection_score >= 0.9
}

dignity_requirement_satisfied("human_welfare") if {
    input.welfare_impact.positive == true
    input.welfare_impact.harm_mitigation >= 0.8
}

dignity_requirement_satisfied("dignity_preservation") if {
    not degradation_detected
    input.dignity_preservation.maintained == true
    input.dignity_preservation.restoration_plan
}

# Minimum dignity score requirement (highest threshold)
meets_minimum_dignity_score if {
    dignity_score >= 0.95
}

# Human dignity enhancement recommendations
dignity_recommendations := recommendations if {
    recommendations := [recommendation |
        some requirement_id
        dignity_requirements[requirement_id]
        requirement := dignity_requirements[requirement_id]
        not dignity_requirement_satisfied(requirement_id)
        recommendation := generate_dignity_recommendation(requirement_id)
    ]
}

generate_dignity_recommendation(requirement_id) := recommendation if {
    requirement_id == "respect_for_persons"
    recommendation := "Ensure all actions treat persons as ends in themselves with inherent worth and dignity"
}

generate_dignity_recommendation(requirement_id) := recommendation if {
    requirement_id == "human_autonomy"
    recommendation := "Preserve meaningful human choice and decision-making authority with proper information"
}

generate_dignity_recommendation(requirement_id) := recommendation if {
    requirement_id == "fundamental_rights"
    recommendation := "Actively protect fundamental human rights and provide due process protections"
}

generate_dignity_recommendation(requirement_id) := recommendation if {
    requirement_id == "human_welfare"
    recommendation := "Consider positive impact on human flourishing and well-being in all decisions"
}

generate_dignity_recommendation(requirement_id) := recommendation if {
    requirement_id == "dignity_preservation"
    recommendation := "Maintain human dignity throughout all processes including correction and enforcement"
}

# Dignity safeguards checklist
dignity_safeguards := {
    "human_oversight": input.safeguards.human_oversight,
    "meaningful_appeal": input.safeguards.appeal_mechanism,
    "transparent_process": input.safeguards.transparency,
    "proportionate_response": input.safeguards.proportionality,
    "harm_prevention": input.safeguards.harm_detection,
    "dignity_restoration": input.safeguards.restoration_mechanisms
}

# Human dignity compliance report
dignity_report := {
    "allowed": allow_action,
    "dignity_score": dignity_score,
    "violations": dignity_violation_details,
    "recommendations": dignity_recommendations,
    "safeguards_status": dignity_safeguards,
    "rights_assessment": rights_assessment,
    "requirement_scores": requirement_scores,
    "constitutional_hash": "cdd01ef066bc6cf2"
}

# Detailed dignity violations
dignity_violation_details := violations if {
    violations := [violation |
        violation_types := ["dehumanization", "instrumentalization", "degradation", "autonomy_violation"]
        some violation_type
        violation_types[_] == violation_type
        violation_detected(violation_type)
        violation := {
            "type": violation_type,
            "description": dignity_violations[violation_type],
            "severity": "critical"
        }
    ]
}

violation_detected("dehumanization") if dehumanization_detected
violation_detected("instrumentalization") if instrumentalization_detected
violation_detected("degradation") if degradation_detected
violation_detected("autonomy_violation") if autonomy_violation_detected

# Rights assessment
rights_assessment := {
    "protected_rights": protected_rights_list,
    "violated_rights": violated_rights_list,
    "enhancement_opportunities": rights_enhancement_opportunities
}

protected_rights_list := [right |
    some right_id
    fundamental_rights[right_id]
    right := right_id
    not right_violated(right_id)
]

violated_rights_list := [right |
    some right_id
    fundamental_rights[right_id]
    right := right_id
    right_violated(right_id)
]

right_violated("life") if violates_right_to_life
right_violated("liberty") if violates_right_to_liberty
right_violated("privacy") if violates_right_to_privacy
right_violated("due_process") if violates_due_process

rights_enhancement_opportunities := [opportunity |
    some right_id
    fundamental_rights[right_id]
    opportunity := sprintf("Enhance protection of %s: %s", [right_id, fundamental_rights[right_id]])
    input.rights_protection.enhancement_potential[right_id] == true
]

# Individual requirement scores
requirement_scores := scores if {
    scores := {requirement_id: calculate_dignity_score(requirement_id, requirement) |
        some requirement_id
        dignity_requirements[requirement_id]
        requirement := dignity_requirements[requirement_id]
    }
}