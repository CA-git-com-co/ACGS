# Fairness Governance Policy
# Package: acgs.fairness
#
# This policy enforces fairness principles including bias prevention,
# equal treatment, and non-discrimination in all governance decisions.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.fairness

import rego.v1

# Default deny for fairness compliance
default allow_policy := false

# Default fairness compliance score
default fairness_score := 0.0

# Fairness requirements
fairness_requirements := {
    "bias_prevention": {
        "description": "Systematic prevention of algorithmic and human bias",
        "weight": 0.3,
        "mandatory": true
    },
    "equal_treatment": {
        "description": "Equal treatment regardless of protected characteristics",
        "weight": 0.25,
        "mandatory": true
    },
    "proportional_representation": {
        "description": "Fair representation of affected groups in decision-making",
        "weight": 0.2,
        "mandatory": false
    },
    "outcome_equity": {
        "description": "Equitable outcomes across different demographic groups",
        "weight": 0.15,
        "mandatory": false
    },
    "process_fairness": {
        "description": "Fair and consistent decision-making processes",
        "weight": 0.1,
        "mandatory": true
    }
}

# Protected characteristics
protected_characteristics := {
    "race", "ethnicity", "gender", "age", "religion", "sexual_orientation",
    "gender_identity", "disability", "national_origin", "socioeconomic_status",
    "political_affiliation", "veteran_status"
}

# Bias detection patterns
bias_indicators := {
    "disparate_impact": {
        "threshold": 0.8,  # 80% rule for disparate impact
        "description": "Selection rate for protected group < 80% of highest group"
    },
    "statistical_parity": {
        "threshold": 0.05,  # 5% difference threshold
        "description": "Difference in positive outcome rates > 5% between groups"
    },
    "equalized_odds": {
        "threshold": 0.1,  # 10% difference threshold
        "description": "Difference in true positive rates > 10% between groups"
    }
}

# Allow policy if fairness requirements are met
allow_policy if {
    input.policy_type in {"algorithmic_decision", "human_decision", "hybrid_decision", "governance_rule"}
    fairness_compliance_check
    no_bias_detected
    equal_treatment_verified
    meets_minimum_fairness_score
}

# Check fairness compliance
fairness_compliance_check if {
    # Policy must include bias assessment
    input.bias_assessment
    
    # Policy must address protected characteristics
    protected_characteristics_considered
    
    # Policy must have fairness monitoring
    fairness_monitoring_enabled
    
    # Policy must have bias mitigation measures
    bias_mitigation_measures_present
}

# Verify protected characteristics are considered
protected_characteristics_considered if {
    input.protected_characteristics_analysis
    count(input.protected_characteristics_analysis.groups_analyzed) > 0
    input.protected_characteristics_analysis.impact_assessment
}

# Verify fairness monitoring is enabled
fairness_monitoring_enabled if {
    input.fairness_monitoring.enabled == true
    input.fairness_monitoring.metrics
    input.fairness_monitoring.frequency
    input.fairness_monitoring.alert_thresholds
}

# Verify bias mitigation measures are present
bias_mitigation_measures_present if {
    count(input.bias_mitigation.techniques) > 0
    input.bias_mitigation.validation_method
    input.bias_mitigation.continuous_improvement
}

# Check for bias detection
no_bias_detected if {
    not disparate_impact_detected
    not statistical_parity_violation
    not equalized_odds_violation
    not prohibited_bias_patterns
}

# Disparate impact detection
disparate_impact_detected if {
    some group
    input.bias_assessment.group_outcomes[group]
    group_outcome := input.bias_assessment.group_outcomes[group]
    
    some other_group
    input.bias_assessment.group_outcomes[other_group]
    other_outcome := input.bias_assessment.group_outcomes[other_group]
    
    group != other_group
    max_outcome := max([group_outcome.selection_rate, other_outcome.selection_rate])
    min_outcome := min([group_outcome.selection_rate, other_outcome.selection_rate])
    
    ratio := min_outcome / max_outcome
    ratio < bias_indicators.disparate_impact.threshold
}

# Statistical parity violation
statistical_parity_violation if {
    some group1, group2
    input.bias_assessment.group_outcomes[group1]
    input.bias_assessment.group_outcomes[group2]
    
    outcome1 := input.bias_assessment.group_outcomes[group1].positive_rate
    outcome2 := input.bias_assessment.group_outcomes[group2].positive_rate
    
    group1 != group2
    abs(outcome1 - outcome2) > bias_indicators.statistical_parity.threshold
}

# Equalized odds violation
equalized_odds_violation if {
    some group1, group2
    input.bias_assessment.group_outcomes[group1]
    input.bias_assessment.group_outcomes[group2]
    
    tpr1 := input.bias_assessment.group_outcomes[group1].true_positive_rate
    tpr2 := input.bias_assessment.group_outcomes[group2].true_positive_rate
    
    group1 != group2
    abs(tpr1 - tpr2) > bias_indicators.equalized_odds.threshold
}

# Check for prohibited bias patterns
prohibited_bias_patterns if {
    # Check for explicit bias in policy text
    contains(lower(input.policy_content), "discriminate against")
}

prohibited_bias_patterns if {
    # Check for coded language that may indicate bias
    coded_bias_language_detected
}

coded_bias_language_detected if {
    some phrase
    biased_phrases := [
        "cultural fit", "aggressive", "articulate", "urban", "inner city",
        "traditional values", "normal family", "natural ability"
    ]
    biased_phrases[_] == phrase
    contains(lower(input.policy_content), phrase)
}

# Verify equal treatment
equal_treatment_verified if {
    # All groups receive same process
    consistent_process_application
    
    # No preferential treatment based on protected characteristics
    no_preferential_treatment
    
    # Reasonable accommodations provided where needed
    reasonable_accommodations_considered
}

consistent_process_application if {
    input.process_consistency.same_criteria == true
    input.process_consistency.same_procedures == true
    input.process_consistency.same_timeline == true
}

no_preferential_treatment if {
    not input.preferential_treatment.enabled
    input.merit_based_decisions == true
}

reasonable_accommodations_considered if {
    input.accommodations.policy_exists == true
    input.accommodations.request_process
    input.accommodations.evaluation_criteria
}

# Calculate fairness score
fairness_score := score if {
    scores := [requirement_score |
        some requirement_id
        fairness_requirements[requirement_id]
        requirement := fairness_requirements[requirement_id]
        requirement_score := calculate_fairness_score(requirement_id, requirement)
    ]
    score := sum(scores) / count(scores)
}

# Calculate score for individual fairness requirement
calculate_fairness_score(requirement_id, requirement) := score if {
    fairness_requirement_satisfied(requirement_id)
    score := requirement.weight
}

calculate_fairness_score(requirement_id, requirement) := score if {
    not fairness_requirement_satisfied(requirement_id)
    requirement.mandatory == true
    score := 0.0
}

calculate_fairness_score(requirement_id, requirement) := score if {
    not fairness_requirement_satisfied(requirement_id)
    requirement.mandatory == false
    score := requirement.weight * 0.3  # Partial credit for non-mandatory requirements
}

# Check if specific fairness requirement is satisfied
fairness_requirement_satisfied("bias_prevention") if {
    no_bias_detected
    bias_mitigation_measures_present
    input.bias_prevention_score >= 0.8
}

fairness_requirement_satisfied("equal_treatment") if {
    equal_treatment_verified
    input.equal_treatment_score >= 0.9
}

fairness_requirement_satisfied("proportional_representation") if {
    input.representation_analysis.enabled == true
    input.representation_analysis.proportionality_score >= 0.7
}

fairness_requirement_satisfied("outcome_equity") if {
    input.outcome_analysis.equity_score >= 0.8
    not significant_outcome_disparities
}

fairness_requirement_satisfied("process_fairness") if {
    consistent_process_application
    input.process_fairness_score >= 0.85
}

significant_outcome_disparities if {
    some metric
    input.outcome_analysis.disparity_metrics[metric]
    disparity := input.outcome_analysis.disparity_metrics[metric]
    disparity.coefficient_of_variation > 0.2  # 20% CV threshold
}

# Minimum fairness score requirement
meets_minimum_fairness_score if {
    fairness_score >= 0.85
}

# Fairness violation detection
fairness_violations := violations if {
    violations := [violation |
        violation_checks := [
            {"type": "disparate_impact", "violated": disparate_impact_detected},
            {"type": "statistical_parity", "violated": statistical_parity_violation},
            {"type": "equalized_odds", "violated": equalized_odds_violation},
            {"type": "prohibited_bias", "violated": prohibited_bias_patterns},
            {"type": "unequal_treatment", "violated": not equal_treatment_verified},
            {"type": "outcome_disparity", "violated": significant_outcome_disparities}
        ]
        some check
        violation_checks[_] == check
        check.violated == true
        violation := check.type
    ]
}

# Fairness enhancement recommendations
fairness_recommendations := recommendations if {
    recommendations := [recommendation |
        some requirement_id
        fairness_requirements[requirement_id]
        requirement := fairness_requirements[requirement_id]
        not fairness_requirement_satisfied(requirement_id)
        recommendation := generate_fairness_recommendation(requirement_id, requirement)
    ]
}

generate_fairness_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "bias_prevention"
    recommendation := "Implement comprehensive bias testing including disparate impact analysis and algorithmic auditing"
}

generate_fairness_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "equal_treatment"
    recommendation := "Ensure consistent application of criteria and procedures across all demographic groups"
}

generate_fairness_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "proportional_representation"
    recommendation := "Analyze representation of affected groups and implement measures to ensure fair participation"
}

generate_fairness_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "outcome_equity"
    recommendation := "Monitor outcome distributions across groups and adjust processes to reduce disparities"
}

generate_fairness_recommendation(requirement_id, requirement) := recommendation if {
    requirement_id == "process_fairness"
    recommendation := "Standardize decision-making processes and provide clear appeal mechanisms"
}

# Bias mitigation strategies
bias_mitigation_strategies := {
    "pre_processing": ["data_augmentation", "re_sampling", "feature_selection"],
    "in_processing": ["fairness_constraints", "adversarial_debiasing", "multi_task_learning"],
    "post_processing": ["threshold_optimization", "calibration", "outcome_adjustment"]
}

# Fairness metrics calculation
fairness_metrics := {
    "demographic_parity": calculate_demographic_parity,
    "equalized_odds": calculate_equalized_odds,
    "equal_opportunity": calculate_equal_opportunity,
    "calibration": calculate_calibration
}

# Calculate demographic parity
calculate_demographic_parity := metric if {
    group_rates := [rate |
        some group
        input.bias_assessment.group_outcomes[group]
        rate := input.bias_assessment.group_outcomes[group].positive_rate
    ]
    metric := 1.0 - (max(group_rates) - min(group_rates))
}

# Calculate equalized odds
calculate_equalized_odds := metric if {
    tpr_rates := [tpr |
        some group
        input.bias_assessment.group_outcomes[group]
        tpr := input.bias_assessment.group_outcomes[group].true_positive_rate
    ]
    fpr_rates := [fpr |
        some group
        input.bias_assessment.group_outcomes[group]
        fpr := input.bias_assessment.group_outcomes[group].false_positive_rate
    ]
    tpr_diff := max(tpr_rates) - min(tpr_rates)
    fpr_diff := max(fpr_rates) - min(fpr_rates)
    metric := 1.0 - max([tpr_diff, fpr_diff])
}

# Fairness compliance report
fairness_report := {
    "allowed": allow_policy,
    "fairness_score": fairness_score,
    "violations": fairness_violations,
    "recommendations": fairness_recommendations,
    "bias_assessment": input.bias_assessment,
    "fairness_metrics": fairness_metrics,
    "requirement_scores": requirement_scores,
    "constitutional_hash": "cdd01ef066bc6cf2"
}

# Individual requirement scores
requirement_scores := scores if {
    scores := {requirement_id: calculate_fairness_score(requirement_id, requirement) |
        some requirement_id
        fairness_requirements[requirement_id]
        requirement := fairness_requirements[requirement_id]
    }
}