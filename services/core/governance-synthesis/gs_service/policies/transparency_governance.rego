# Transparency Governance Policy
# Package: acgs.transparency
#
# This policy enforces transparency requirements across all governance decisions
# and ensures explainable, auditable decision-making processes.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.transparency

import rego.v1

# Default deny for transparency compliance
default allow_decision := false

# Default transparency compliance score
default transparency_score := 0.0

# Transparency requirements
transparency_requirements := {
    "explainability": {
        "description": "All decisions must be explainable to affected parties",
        "weight": 0.4,
        "mandatory": true
    },
    "auditability": {
        "description": "All decisions must be auditable with complete trail",
        "weight": 0.3,
        "mandatory": true
    },
    "public_accountability": {
        "description": "Public decisions must be publicly accountable",
        "weight": 0.2,
        "mandatory": false
    },
    "information_access": {
        "description": "Relevant information must be accessible to stakeholders",
        "weight": 0.1,
        "mandatory": false
    }
}

# Allow decision if transparency requirements are met
allow_decision if {
    input.decision_type in {"policy_creation", "policy_modification", "governance_action", "constitutional_amendment"}
    transparency_compliance_check
    has_explainability_metadata
    has_audit_trail
    meets_minimum_transparency_score
}

# Check transparency compliance
transparency_compliance_check if {
    # Decision must include transparency metadata
    input.transparency_metadata
    
    # Decision must have rationale
    count(input.decision_rationale) > 0
    
    # Decision must identify affected parties
    count(input.affected_parties) > 0
    
    # Decision process must be documented
    valid_process_documentation
}

# Validate explainability metadata
has_explainability_metadata if {
    input.transparency_metadata.explanation_level in {"basic", "detailed", "comprehensive"}
    input.transparency_metadata.explanation_format in {"natural_language", "structured", "visual"}
    count(input.transparency_metadata.key_factors) > 0
}

# Validate audit trail presence
has_audit_trail if {
    input.audit_metadata.created_at
    input.audit_metadata.created_by
    input.audit_metadata.decision_id
    input.audit_metadata.constitutional_hash == "cdd01ef066bc6cf2"
}

# Validate process documentation
valid_process_documentation if {
    input.process_documentation.methodology
    input.process_documentation.consultation_process
    input.process_documentation.review_stages
}

# Calculate transparency score
transparency_score := score if {
    scores := [requirement_score |
        some requirement_id
        transparency_requirements[requirement_id]
        requirement := transparency_requirements[requirement_id]
        requirement_score := calculate_transparency_score(requirement_id, requirement)
    ]
    score := sum(scores) / count(scores)
}

# Calculate score for individual transparency requirement
calculate_transparency_score(requirement_id, requirement) := score if {
    transparency_requirement_satisfied(requirement_id)
    score := requirement.weight
}

calculate_transparency_score(requirement_id, requirement) := score if {
    not transparency_requirement_satisfied(requirement_id)
    requirement.mandatory == true
    score := 0.0
}

calculate_transparency_score(requirement_id, requirement) := score if {
    not transparency_requirement_satisfied(requirement_id)
    requirement.mandatory == false
    score := requirement.weight * 0.3  # Partial credit for non-mandatory requirements
}

# Check if specific transparency requirement is satisfied
transparency_requirement_satisfied("explainability") if {
    has_explainability_metadata
    input.transparency_metadata.explanation_completeness >= 0.7
}

transparency_requirement_satisfied("auditability") if {
    has_audit_trail
    input.audit_metadata.completeness_score >= 0.8
}

transparency_requirement_satisfied("public_accountability") if {
    input.decision_scope == "public"
    input.public_disclosure.enabled == true
    count(input.public_disclosure.channels) > 0
}

transparency_requirement_satisfied("information_access") if {
    count(input.accessible_information) > 0
    input.information_access.format in {"api", "dashboard", "report", "documentation"}
}

# Minimum transparency score requirement
meets_minimum_transparency_score if {
    transparency_score >= 0.8
}

# Transparency violation checks
transparency_violations := violations if {
    violations := [violation |
        violation_checks := [
            {"type": "missing_explanation", "violated": missing_explanation},
            {"type": "insufficient_audit_trail", "violated": insufficient_audit_trail},
            {"type": "opaque_process", "violated": opaque_process},
            {"type": "restricted_access", "violated": unreasonably_restricted_access}
        ]
        some check
        violation_checks[_] == check
        check.violated == true
        violation := check.type
    ]
}

# Check for missing explanation
missing_explanation if {
    not input.transparency_metadata.explanation
}

missing_explanation if {
    count(input.decision_rationale) == 0
}

# Check for insufficient audit trail
insufficient_audit_trail if {
    not has_audit_trail
}

insufficient_audit_trail if {
    input.audit_metadata.completeness_score < 0.6
}

# Check for opaque process
opaque_process if {
    not input.process_documentation.methodology
}

opaque_process if {
    input.transparency_metadata.explanation_level == "none"
}

# Check for unreasonably restricted access
unreasonably_restricted_access if {
    input.decision_scope == "public"
    input.public_disclosure.enabled == false
    not valid_restriction_justification
}

valid_restriction_justification if {
    input.restriction_justification.reason in {"security", "privacy", "legal", "competitive"}
    input.restriction_justification.review_date
    input.restriction_justification.approved_by
}

# Transparency enhancement recommendations
transparency_recommendations := recommendations if {
    recommendations := [recommendation |
        some requirement_id
        transparency_requirements[requirement_id]
        requirement := transparency_requirements[requirement_id]
        not transparency_requirement_satisfied(requirement_id)
        recommendation := sprintf("Enhance %s: %s", [requirement_id, requirement.description])
    ]
}

# Generate explanations for decisions
decision_explanation := explanation if {
    explanation := {
        "summary": sprintf("Decision %s was made because: %s", [input.decision_id, input.decision_rationale[0]]),
        "factors": input.transparency_metadata.key_factors,
        "process": input.process_documentation.methodology,
        "constitutional_basis": input.constitutional_justification,
        "affected_parties": input.affected_parties,
        "review_process": input.process_documentation.review_stages
    }
}

# Transparency compliance report
transparency_report := {
    "allowed": allow_decision,
    "transparency_score": transparency_score,
    "violations": transparency_violations,
    "recommendations": transparency_recommendations,
    "explanation": decision_explanation,
    "requirement_scores": requirement_scores,
    "constitutional_hash": "cdd01ef066bc6cf2"
}

# Individual requirement scores
requirement_scores := scores if {
    scores := {requirement_id: calculate_transparency_score(requirement_id, requirement) |
        some requirement_id
        transparency_requirements[requirement_id]
        requirement := transparency_requirements[requirement_id]
    }
}