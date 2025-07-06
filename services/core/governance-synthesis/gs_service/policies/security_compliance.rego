# Security Compliance Policy
# Package: acgs.security_compliance
#
# This policy enforces enterprise security compliance including SOC 2, ISO 27001,
# NIST, and constitutional security requirements within the ACGS framework.
#
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.security_compliance

import rego.v1

# Default deny for security operations
default allow_security_operation := false
default security_posture_adequate := false
default compliance_framework_satisfied := false

# Security compliance frameworks
compliance_frameworks := {
    "soc2": {
        "name": "SOC 2 Type II",
        "categories": ["security", "availability", "processing_integrity", "confidentiality", "privacy"],
        "audit_frequency": "annual",
        "continuous_monitoring": true,
        "risk_threshold": 0.2
    },
    "iso27001": {
        "name": "ISO/IEC 27001:2022",
        "categories": ["isms", "risk_management", "incident_response", "business_continuity"],
        "audit_frequency": "annual",
        "continuous_monitoring": true,
        "risk_threshold": 0.15
    },
    "nist_csf": {
        "name": "NIST Cybersecurity Framework",
        "categories": ["identify", "protect", "detect", "respond", "recover"],
        "maturity_levels": ["partial", "risk_informed", "repeatable", "adaptive"],
        "target_maturity": "repeatable",
        "risk_threshold": 0.25
    },
    "fedramp": {
        "name": "FedRAMP Moderate",
        "categories": ["access_control", "audit_accountability", "configuration_management", "identification_authentication"],
        "audit_frequency": "continuous",
        "ato_required": true,
        "risk_threshold": 0.1
    }
}

# Constitutional security principles
constitutional_security_principles := {
    "human_dignity": {
        "principle": "Security measures must respect human dignity and rights",
        "requirements": ["privacy_preserving_security", "proportionate_measures", "transparency"],
        "weight": 1.0
    },
    "fairness": {
        "principle": "Security controls must be applied fairly and consistently",
        "requirements": ["equal_protection", "non_discriminatory", "consistent_enforcement"],
        "weight": 0.9
    },
    "transparency": {
        "principle": "Security processes must be transparent and auditable",
        "requirements": ["audit_trails", "policy_transparency", "incident_disclosure"],
        "weight": 0.85
    },
    "accountability": {
        "principle": "Clear accountability for security decisions and incidents",
        "requirements": ["responsible_parties", "decision_tracking", "incident_response"],
        "weight": 0.9
    },
    "proportionality": {
        "principle": "Security measures must be proportionate to risk",
        "requirements": ["risk_assessment", "cost_benefit_analysis", "graduated_response"],
        "weight": 0.8
    }
}

# Security control categories
security_control_categories := {
    "access_control": {
        "controls": ["authentication", "authorization", "privileged_access", "session_management"],
        "criticality": "high",
        "compliance_threshold": 0.9
    },
    "data_protection": {
        "controls": ["encryption", "data_classification", "data_loss_prevention", "backup_recovery"],
        "criticality": "critical",
        "compliance_threshold": 0.95
    },
    "network_security": {
        "controls": ["firewalls", "intrusion_detection", "network_segmentation", "vpn"],
        "criticality": "high",
        "compliance_threshold": 0.85
    },
    "incident_response": {
        "controls": ["detection", "containment", "eradication", "recovery", "lessons_learned"],
        "criticality": "critical",
        "compliance_threshold": 0.9
    },
    "vulnerability_management": {
        "controls": ["vulnerability_scanning", "patch_management", "penetration_testing", "threat_intelligence"],
        "criticality": "high",
        "compliance_threshold": 0.85
    },
    "business_continuity": {
        "controls": ["backup_procedures", "disaster_recovery", "business_impact_analysis", "continuity_planning"],
        "criticality": "high",
        "compliance_threshold": 0.8
    }
}

# Security operation authorization
allow_security_operation if {
    operation := input.operation
    requestor := input.requestor
    context := input.context
    
    # Validate requestor authorization
    requestor_security_authorized(requestor, operation)
    
    # Check operation security requirements
    security_requirements_met(operation, context)
    
    # Verify constitutional compliance
    constitutional_security_compliant(operation, context)
    
    # Compliance framework requirements satisfied
    compliance_requirements_satisfied(operation, context)
    
    # Risk assessment completed
    risk_assessment_adequate(operation, context)
    
    # Audit trail enabled
    security_audit_trail_enabled(operation, context)
}

# Security posture assessment
security_posture_adequate if {
    organization := input.organization
    assessment_scope := input.assessment_scope
    
    # All critical security controls implemented
    critical_controls_implemented(organization, assessment_scope)
    
    # Security metrics within acceptable ranges
    security_metrics_acceptable(organization)
    
    # Incident response capability verified
    incident_response_capability_verified(organization)
    
    # Vulnerability management effective
    vulnerability_management_effective(organization)
    
    # Security awareness and training adequate
    security_training_adequate(organization)
    
    # Constitutional security principles upheld
    constitutional_security_principles_upheld(organization)
}

# Compliance framework satisfaction
compliance_framework_satisfied if {
    organization := input.organization
    target_frameworks := input.target_frameworks
    
    # All target frameworks meet requirements
    all(framework, framework in target_frameworks;
        framework_requirements_met(organization, framework))
    
    # Continuous monitoring in place
    continuous_monitoring_operational(organization)
    
    # Audit evidence available
    audit_evidence_adequate(organization, target_frameworks)
    
    # Remediation plans for gaps exist
    remediation_plans_adequate(organization)
}

# Helper functions for authorization
requestor_security_authorized(requestor, operation) if {
    # Role-based authorization
    requestor.role in operation.authorized_roles
    
    # Security clearance adequate
    requestor.security_clearance >= operation.required_clearance
    
    # Multi-factor authentication verified
    requestor.mfa_verified == true
    
    # No recent security violations
    count(requestor.recent_security_violations) == 0
    
    # Constitutional compliance verified
    requestor.constitutional_compliance_score >= 0.8
}

security_requirements_met(operation, context) if {
    # Operation classification requirements
    classification_requirements_met(operation, context)
    
    # Security controls appropriate for operation
    security_controls_appropriate(operation, context)
    
    # Environment security adequate
    environment_security_adequate(operation, context)
    
    # Data handling requirements met
    data_handling_requirements_met(operation, context)
}

classification_requirements_met(operation, context) if {
    operation_classification := determine_operation_classification(operation)
    context_classification := context.security_classification
    
    # Context must support operation classification
    context_classification >= operation_classification
    
    # Appropriate protective measures in place
    protective_measures_adequate(operation_classification, context)
}

determine_operation_classification(operation) := classification if {
    classification := operation.security_classification
}

determine_operation_classification(operation) := classification if {
    not operation.security_classification
    
    # Determine based on data and impact
    data_sensitivity := max([d.classification | d := operation.data_accessed[_]])
    impact_level := operation.impact_level
    
    classification := max(data_sensitivity, impact_level)
}

protective_measures_adequate(classification, context) if {
    required_measures := security_measures_for_classification(classification)
    all(measure, measure in required_measures;
        protective_measure_implemented(measure, context))
}

security_measures_for_classification("public") := ["basic_logging", "standard_authentication"]
security_measures_for_classification("internal") := ["enhanced_logging", "multi_factor_auth", "encryption_in_transit"]
security_measures_for_classification("confidential") := ["comprehensive_logging", "strong_authentication", "encryption_at_rest", "network_segmentation"]
security_measures_for_classification("restricted") := ["full_audit_trail", "privileged_access_controls", "hardware_security_modules", "air_gap_isolation"]

protective_measure_implemented(measure, context) if {
    measure in context.implemented_security_measures
    context.security_measure_status[measure] == "operational"
}

# Constitutional compliance validation
constitutional_security_compliant(operation, context) if {
    all(principle_name, principle in constitutional_security_principles;
        security_principle_satisfied(principle_name, principle, operation, context))
}

security_principle_satisfied(principle_name, principle, operation, context) if {
    all(requirement, requirement in principle.requirements;
        security_requirement_met(requirement, operation, context))
}

security_requirement_met("privacy_preserving_security", operation, context) if {
    # Security measures don't unnecessarily compromise privacy
    operation.privacy_impact_assessed == true
    operation.privacy_preserving_controls_implemented == true
    not operation.excessive_surveillance
}

security_requirement_met("proportionate_measures", operation, context) if {
    # Security measures proportionate to risk
    risk_level := operation.risk_assessment.overall_risk
    security_level := operation.security_level
    
    proportionality_verified(risk_level, security_level)
}

proportionality_verified(risk_level, security_level) if {
    risk_level == "low"
    security_level in ["basic", "standard"]
}

proportionality_verified(risk_level, security_level) if {
    risk_level == "medium"
    security_level in ["standard", "enhanced"]
}

proportionality_verified(risk_level, security_level) if {
    risk_level == "high"
    security_level in ["enhanced", "maximum"]
}

proportionality_verified(risk_level, security_level) if {
    risk_level == "critical"
    security_level == "maximum"
}

security_requirement_met("transparency", operation, context) if {
    # Security processes are transparent
    operation.security_policies_published == true
    operation.incident_disclosure_policy_exists == true
    operation.audit_results_available == true
}

security_requirement_met("equal_protection", operation, context) if {
    # Equal security protection for all users
    operation.discriminatory_security_controls == false
    operation.fair_access_controls == true
    operation.consistent_policy_enforcement == true
}

security_requirement_met("audit_trails", operation, context) if {
    # Comprehensive audit trails maintained
    operation.audit_logging_enabled == true
    operation.audit_trail_integrity_protected == true
    operation.audit_log_retention_adequate == true
}

# Compliance framework validation
framework_requirements_met(organization, framework) if {
    framework_config := compliance_frameworks[framework]
    
    # All framework categories satisfied
    all(category, category in framework_config.categories;
        framework_category_satisfied(organization, framework, category))
    
    # Risk threshold not exceeded
    organization.risk_scores[framework] <= framework_config.risk_threshold
    
    # Audit requirements met
    framework_audit_requirements_met(organization, framework)
    
    # Continuous monitoring if required
    framework_monitoring_adequate(organization, framework)
}

framework_category_satisfied(organization, framework, category) if {
    category_controls := organization.compliance_controls[framework][category]
    category_requirements := determine_category_requirements(framework, category)
    
    # All required controls implemented
    all(requirement, requirement in category_requirements;
        control_requirement_satisfied(category_controls, requirement))
    
    # Category compliance score adequate
    category_score := organization.compliance_scores[framework][category]
    category_score >= framework_category_threshold(framework, category)
}

determine_category_requirements("soc2", "security") := [
    "access_controls", "multi_factor_authentication", "encryption", 
    "vulnerability_management", "incident_response", "security_monitoring"
]

determine_category_requirements("soc2", "availability") := [
    "uptime_monitoring", "redundancy", "disaster_recovery",
    "capacity_planning", "performance_monitoring"
]

determine_category_requirements("iso27001", "isms") := [
    "information_security_policy", "risk_management_process",
    "security_organization", "asset_management", "access_control"
]

determine_category_requirements("nist_csf", "identify") := [
    "asset_management", "business_environment", "governance",
    "risk_assessment", "risk_management_strategy"
]

determine_category_requirements("nist_csf", "protect") := [
    "identity_management", "awareness_training", "data_security",
    "information_protection", "maintenance", "protective_technology"
]

control_requirement_satisfied(controls, requirement) if {
    requirement in controls.implemented
    controls.status[requirement] == "operational"
    controls.effectiveness[requirement] >= 0.8
}

framework_category_threshold("soc2", category) := 0.9
framework_category_threshold("iso27001", category) := 0.85
framework_category_threshold("nist_csf", category) := 0.8
framework_category_threshold("fedramp", category) := 0.95

# Critical controls assessment
critical_controls_implemented(organization, scope) if {
    critical_categories := [cat | 
        some cat, config in security_control_categories
        config.criticality == "critical"
    ]
    
    all(category, category in critical_categories;
        security_category_implemented(organization, category, scope))
}

security_category_implemented(organization, category, scope) if {
    category_config := security_control_categories[category]
    implemented_controls := organization.security_controls[category]
    
    # All required controls implemented
    all(control, control in category_config.controls;
        security_control_implemented(implemented_controls, control))
    
    # Category compliance threshold met
    category_score := organization.security_scores[category]
    category_score >= category_config.compliance_threshold
}

security_control_implemented(implemented_controls, control) if {
    control in implemented_controls.active
    implemented_controls.status[control] == "operational"
    implemented_controls.last_tested[control] > time.now_ns() - (90 * 24 * 60 * 60 * 1000000000) # 90 days
}

# Security metrics assessment
security_metrics_acceptable(organization) if {
    metrics := organization.security_metrics
    
    # Key performance indicators within range
    metrics.mean_time_to_detect <= 300 # 5 minutes
    metrics.mean_time_to_respond <= 900 # 15 minutes
    metrics.vulnerability_remediation_rate >= 0.95
    metrics.security_incident_rate <= 0.01
    metrics.compliance_score >= 0.85
    
    # Trend analysis positive
    security_trends_positive(metrics)
}

security_trends_positive(metrics) if {
    # Incident rate decreasing or stable
    metrics.incident_rate_trend <= 0
    
    # Response times improving or stable
    metrics.response_time_trend <= 0
    
    # Vulnerability remediation improving
    metrics.remediation_rate_trend >= 0
    
    # Overall security posture improving
    metrics.security_posture_trend >= 0
}

# Incident response capability
incident_response_capability_verified(organization) if {
    ir_capability := organization.incident_response
    
    # IR plan exists and is current
    ir_capability.plan_exists == true
    ir_capability.plan_last_updated > time.now_ns() - (365 * 24 * 60 * 60 * 1000000000) # 1 year
    
    # IR team trained and available
    ir_capability.team_trained == true
    ir_capability.team_available_24x7 == true
    
    # IR procedures tested
    ir_capability.procedures_tested == true
    ir_capability.last_exercise > time.now_ns() - (180 * 24 * 60 * 60 * 1000000000) # 6 months
    
    # IR tools and capabilities operational
    ir_capability.tools_operational == true
    ir_capability.communication_channels_tested == true
}

# Vulnerability management effectiveness
vulnerability_management_effective(organization) if {
    vm_program := organization.vulnerability_management
    
    # Regular vulnerability assessments
    vm_program.scanning_frequency >= "weekly"
    vm_program.assessment_coverage >= 0.95
    
    # Timely remediation
    vm_program.critical_remediation_sla <= 24 # hours
    vm_program.high_remediation_sla <= 168 # 1 week
    vm_program.medium_remediation_sla <= 720 # 1 month
    
    # Remediation rate adequate
    vm_program.remediation_rate >= 0.9
    vm_program.false_positive_rate <= 0.1
    
    # Threat intelligence integrated
    vm_program.threat_intelligence_integrated == true
    vm_program.risk_based_prioritization == true
}

# Security training adequacy
security_training_adequate(organization) if {
    training_program := organization.security_training
    
    # All personnel trained
    training_program.coverage_rate >= 0.95
    training_program.completion_rate >= 0.9
    
    # Training current and relevant
    training_program.content_current == true
    training_program.role_specific_training == true
    
    # Training effectiveness measured
    training_program.effectiveness_measured == true
    training_program.knowledge_retention_rate >= 0.8
    
    # Phishing simulation program
    training_program.phishing_simulation_enabled == true
    training_program.phishing_success_rate <= 0.05
}

# Continuous monitoring
continuous_monitoring_operational(organization) if {
    monitoring := organization.continuous_monitoring
    
    # Automated monitoring tools deployed
    monitoring.tools_deployed == true
    monitoring.coverage_comprehensive == true
    
    # Real-time alerting configured
    monitoring.real_time_alerting == true
    monitoring.alert_response_automated == true
    
    # Monitoring data analyzed
    monitoring.data_analysis_automated == true
    monitoring.anomaly_detection_enabled == true
    
    # Constitutional compliance monitored
    monitoring.constitutional_compliance_tracked == true
    monitoring.governance_metrics_tracked == true
}

# Risk assessment adequacy
risk_assessment_adequate(operation, context) if {
    risk_assessment := operation.risk_assessment
    
    # Risk assessment methodology sound
    risk_assessment.methodology_documented == true
    risk_assessment.methodology_validated == true
    
    # All risk categories assessed
    required_risk_categories := ["technical", "operational", "legal", "constitutional"]
    all(category, category in required_risk_categories;
        category in risk_assessment.categories_assessed)
    
    # Risk assessment current
    risk_assessment.last_updated > time.now_ns() - (90 * 24 * 60 * 60 * 1000000000) # 90 days
    
    # Risk mitigation plans exist
    risk_assessment.mitigation_plans_exist == true
    risk_assessment.residual_risk_acceptable == true
}

# Security compliance scoring
security_compliance_score := score if {
    organization := input.organization
    
    # Framework compliance scores
    framework_scores := [score |
        some framework in organization.target_frameworks
        score := organization.compliance_scores[framework]
    ]
    
    # Security control scores
    control_scores := [score |
        some category, config in security_control_categories
        score := organization.security_scores[category] * control_category_weight(config.criticality)
    ]
    
    # Constitutional compliance score
    constitutional_score := organization.constitutional_security_score
    
    # Calculate weighted average
    total_weight := count(framework_scores) + sum([control_category_weight(config.criticality) | 
                                                   some category, config in security_control_categories]) + 1
    
    weighted_sum := sum(framework_scores) + sum(control_scores) + constitutional_score
    
    score := weighted_sum / total_weight
}

control_category_weight("critical") := 3
control_category_weight("high") := 2
control_category_weight("medium") := 1
control_category_weight("low") := 0.5

# Security violations detection
security_violations := violations if {
    organization := input.organization
    
    violations := [violation |
        some control_category, controls in organization.security_controls
        some control, status in controls.status
        status != "operational"
        violation := {
            "type": "control_failure",
            "category": control_category,
            "control": control,
            "status": status,
            "risk_level": determine_violation_risk(control_category, control),
            "constitutional_impact": assess_constitutional_impact(control_category, control)
        }
    ]
}

determine_violation_risk(category, control) := risk if {
    category_config := security_control_categories[category]
    risk := category_config.criticality
}

assess_constitutional_impact(category, control) := impact if {
    # Assess impact on constitutional principles
    impacted_principles := [principle |
        some principle_name, principle in constitutional_security_principles
        control_impacts_principle(category, control, principle_name, principle)
    ]
    
    impact := {
        "impacted_principles": impacted_principles,
        "severity": calculate_constitutional_impact_severity(impacted_principles)
    }
}

control_impacts_principle(category, control, principle_name, principle) if {
    # Determine if control failure impacts constitutional principle
    category == "access_control"
    principle_name in ["fairness", "human_dignity"]
}

control_impacts_principle(category, control, principle_name, principle) if {
    category == "data_protection"
    principle_name in ["human_dignity", "transparency"]
}

calculate_constitutional_impact_severity(impacted_principles) := "critical" if {
    count(impacted_principles) >= 3
}

calculate_constitutional_impact_severity(impacted_principles) := "high" if {
    count(impacted_principles) == 2
}

calculate_constitutional_impact_severity(impacted_principles) := "medium" if {
    count(impacted_principles) == 1
}

calculate_constitutional_impact_severity(impacted_principles) := "low" if {
    count(impacted_principles) == 0
}