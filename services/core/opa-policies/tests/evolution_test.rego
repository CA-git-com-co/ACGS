# ACGS-1 Lite Evolution Approval Test Suite
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.evolution_test

import data.acgs.evolution
import data.acgs.main

# Test evolution approval thresholds
test_auto_approval_high_score {
    result := evolution.evaluate with input as {
        "type": "evolution_approval",
        "evolution_request": {
            "type": "patch",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "changes": {
                "code_changes": ["Minor bug fix"],
                "external_dependencies": [],
                "privilege_escalation": false,
                "network_changes": false,
                "experimental_features": false
            },
            "performance_analysis": {
                "complexity_delta": 0.02,
                "memory_delta": 0.01,
                "latency_delta": -0.05,
                "resource_delta": 0.0
            },
            "rollback_plan": {
                "procedure": "Automated rollback via git revert",
                "verification": "Unit tests + smoke tests",
                "timeline": "< 5 minutes",
                "dependencies": "None",
                "tested": true,
                "automated": true
            },
            "mitigations": {
                "sandbox_deployment": true,
                "gradual_rollout": true,
                "enhanced_monitoring": true
            }
        }
    }
    
    result.allow == true
    result.approval_path == "auto_approve"
    result.evolution_score >= 0.95
}

test_fast_track_medium_score {
    result := evolution.evaluate with input as {
        "type": "evolution_approval",
        "evolution_request": {
            "type": "feature_addition",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "changes": {
                "code_changes": ["New analytics feature"],
                "external_dependencies": ["analytics-lib"],
                "privilege_escalation": false,
                "network_changes": false,
                "experimental_features": false
            },
            "performance_analysis": {
                "complexity_delta": 0.15,
                "memory_delta": 0.1,
                "latency_delta": 0.05,
                "resource_delta": 0.08
            },
            "rollback_plan": {
                "procedure": "Feature flag disable + rollback",
                "verification": "Full test suite",
                "timeline": "< 15 minutes", 
                "dependencies": "Database migration rollback",
                "tested": true,
                "automated": false
            },
            "human_approved": false,
            "security_review_passed": false,
            "peer_reviewed": true
        }
    }
    
    result.allow == false
    result.approval_path == "fast_track"
    result.evolution_score >= 0.9
    result.evolution_score < 0.95
}

test_human_review_low_score {
    result := evolution.evaluate with input as {
        "type": "evolution_approval",
        "evolution_request": {
            "type": "architecture_change",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "changes": {
                "code_changes": ["Major architecture refactor"],
                "external_dependencies": ["new-framework", "cloud-service"],
                "privilege_escalation": true,
                "network_changes": true,
                "experimental_features": true,
                "security_changes": true
            },
            "performance_analysis": {
                "complexity_delta": 0.4,
                "memory_delta": 0.3,
                "latency_delta": 0.2,
                "resource_delta": 0.35
            },
            "rollback_plan": {
                "procedure": "Manual rollback process",
                "verification": "Manual testing",
                "timeline": "2-4 hours",
                "dependencies": "Multiple service coordination",
                "tested": false,
                "automated": false
            },
            "human_approved": false,
            "security_review_passed": false,
            "peer_reviewed": false
        }
    }
    
    result.allow == false
    result.approval_path == "human_review"
    result.evolution_score < 0.9
}

# Test risk assessment
test_low_risk_minor_update {
    result := evolution.assess_evolution_risk({
        "type": "minor_update",
        "changes": {
            "code_changes": ["UI text update"],
            "external_dependencies": [],
            "privilege_escalation": false,
            "experimental_features": false
        },
        "mitigations": {
            "sandbox_deployment": true
        }
    })
    
    result.passed == true
    result.risk_level == "LOW"
    result.adjusted_risk <= 0.3
}

test_high_risk_architecture_change {
    result := evolution.assess_evolution_risk({
        "type": "architecture_change",
        "changes": {
            "code_changes": ["Complete system redesign"],
            "external_dependencies": ["microservice-framework"],
            "privilege_escalation": true,
            "experimental_features": true
        },
        "mitigations": {}
    })
    
    result.passed == false
    result.risk_level == "CRITICAL"
    result.adjusted_risk > 0.8
}

# Test constitutional compliance for evolutions
test_constitutional_compliance_preserved_hash {
    result := evolution.check_constitutional_compliance({
        "constitutional_hash": "cdd01ef066bc6cf2",
        "changes": {
            "logging_disabled": false,
            "audit_disabled": false,
            "data_encryption_weakened": false
        }
    })
    
    result.passed == true
    result.hash_preserved == true
    count(result.violations) == 0
}

test_constitutional_violation_logging_disabled {
    result := evolution.check_constitutional_compliance({
        "constitutional_hash": "cdd01ef066bc6cf2",
        "changes": {
            "logging_disabled": true,  # Violates transparency
            "audit_disabled": false,
            "data_encryption_weakened": false
        }
    })
    
    result.passed == false
    "reduces system transparency" in result.violations
}

test_constitutional_violation_wrong_hash {
    result := evolution.check_constitutional_compliance({
        "constitutional_hash": "wrong_hash",
        "changes": {}
    })
    
    result.passed == false
    result.hash_preserved == false
}

# Test performance impact assessment
test_acceptable_performance_impact {
    result := evolution.assess_performance_impact({
        "performance_analysis": {
            "complexity_delta": 0.1,   # 10% increase, within 30% limit
            "memory_delta": 0.05,      # 5% increase, within 20% limit  
            "latency_delta": 0.08,     # 8% increase, within 15% limit
            "resource_delta": 0.12     # 12% increase, within 25% limit
        }
    })
    
    result.passed == true
    result.score >= 0.8
}

test_excessive_performance_impact {
    result := evolution.assess_performance_impact({
        "performance_analysis": {
            "complexity_delta": 0.5,   # 50% increase, exceeds 30% limit
            "memory_delta": 0.3,       # 30% increase, exceeds 20% limit
            "latency_delta": 0.25,     # 25% increase, exceeds 15% limit
            "resource_delta": 0.4      # 40% increase, exceeds 25% limit
        }
    })
    
    result.passed == false
    result.score < 0.8
    count(result.concerns) >= 4  # All thresholds exceeded
}

# Test rollback capability
test_complete_rollback_plan {
    result := evolution.check_rollback_capability({
        "rollback_plan": {
            "procedure": "Automated git revert + deployment",
            "verification": "Full test suite execution",
            "timeline": "< 10 minutes",
            "dependencies": "CI/CD pipeline",
            "tested": true,
            "automated": true
        }
    })
    
    result.passed == true
    result.score >= 0.8
    count(result.concerns) == 0
}

test_incomplete_rollback_plan {
    result := evolution.check_rollback_capability({
        "rollback_plan": {
            "procedure": "Manual process",
            # Missing verification, timeline, dependencies
            "tested": false,
            "automated": false
        }
    })
    
    result.passed == false
    result.score < 0.8
    count(result.concerns) >= 3  # Missing fields + not tested
}

test_missing_rollback_plan {
    result := evolution.check_rollback_capability({})
    
    result.passed == false
    result.score < 0.8
    "No rollback plan provided" in result.concerns
}

# Test approval requirements
test_major_update_requires_human_approval {
    result := evolution.check_approval_requirements({
        "type": "major_update",
        "human_approved": false,
        "security_review_passed": false,
        "peer_reviewed": false
    })
    
    result.passed == false
    count([concern | concern := result.concerns[_]; contains(concern, "Human approval required")]) >= 1
}

test_architecture_change_requires_all_approvals {
    result := evolution.check_approval_requirements({
        "type": "architecture_change",
        "human_approved": false,
        "security_review_passed": false,
        "peer_reviewed": false
    })
    
    result.passed == false
    # Should require human, security, and peer review
    count(result.concerns) >= 3
}

test_patch_minimal_requirements {
    result := evolution.check_approval_requirements({
        "type": "patch",
        "human_approved": false,
        "security_review_passed": false,
        "peer_reviewed": false
    })
    
    result.passed == true  # Patches don't require special approvals
    count(result.concerns) == 0
}

test_all_approvals_satisfied {
    result := evolution.check_approval_requirements({
        "type": "architecture_change",
        "human_approved": true,
        "security_review_passed": true,
        "peer_reviewed": true
    })
    
    result.passed == true
    count(result.concerns) == 0
}

# Test risk factor detection
test_privilege_escalation_risk_factor {
    factors := evolution.check_risk_factors({
        "changes": {
            "privilege_escalation": true
        }
    })
    
    risk_descriptions := [factor.description | factor := factors[_]]
    "modifies privilege requirements" in risk_descriptions
}

test_external_dependencies_risk_factor {
    factors := evolution.check_risk_factors({
        "changes": {
            "external_dependencies": ["new-service", "third-party-lib"]
        }
    })
    
    risk_descriptions := [factor.description | factor := factors[_]]
    "introduces external dependencies" in risk_descriptions
}

test_experimental_features_risk_factor {
    factors := evolution.check_risk_factors({
        "changes": {
            "experimental_features": true
        }
    })
    
    risk_descriptions := [factor.description | factor := factors[_]]
    "includes experimental features" in risk_descriptions
}

# Test mitigation factors
test_sandbox_deployment_mitigation {
    factors := evolution.check_mitigation_factors({
        "mitigations": {
            "sandbox_deployment": true
        }
    })
    
    mitigation_descriptions := [factor.description | factor := factors[_]]
    "deployed in sandbox first" in mitigation_descriptions
}

test_gradual_rollout_mitigation {
    factors := evolution.check_mitigation_factors({
        "mitigations": {
            "gradual_rollout": true,
            "enhanced_monitoring": true
        }
    })
    
    mitigation_descriptions := [factor.description | factor := factors[_]]
    "gradual rollout planned" in mitigation_descriptions
    "enhanced monitoring enabled" in mitigation_descriptions
}

# Test main policy routing for evolution
test_main_policy_evolution_approval {
    result := main.decision with input as {
        "type": "evolution_approval",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "evolution_request": {
            "type": "patch",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "changes": {
                "code_changes": ["Bug fix"],
                "external_dependencies": [],
                "privilege_escalation": false
            },
            "performance_analysis": {
                "complexity_delta": 0.01,
                "memory_delta": 0.005,
                "latency_delta": 0.0,
                "resource_delta": 0.0
            },
            "rollback_plan": {
                "procedure": "Git revert",
                "verification": "Tests",
                "timeline": "5 min",
                "dependencies": "None",
                "tested": true,
                "automated": true
            }
        }
    }
    
    result.allow == true
}

# Test evolution score calculation edge cases
test_perfect_evolution_score {
    checks := [
        {"score": 1.0},  # Risk
        {"score": 1.0},  # Constitutional 
        {"score": 1.0},  # Performance
        {"score": 1.0},  # Rollback
        {"score": 1.0}   # Approval
    ]
    
    score := evolution.calculate_evolution_score(checks)
    score == 1.0
}

test_failing_evolution_score {
    checks := [
        {"score": 0.0},  # Risk
        {"score": 0.0},  # Constitutional
        {"score": 0.0},  # Performance
        {"score": 0.0},  # Rollback
        {"score": 0.0}   # Approval
    ]
    
    score := evolution.calculate_evolution_score(checks)
    score == 0.0
}

test_mixed_evolution_score {
    checks := [
        {"score": 0.8},  # Risk (weight 0.25)
        {"score": 0.9},  # Constitutional (weight 0.35)
        {"score": 0.7},  # Performance (weight 0.2)
        {"score": 0.6},  # Rollback (weight 0.15)
        {"score": 1.0}   # Approval (weight 0.05)
    ]
    
    score := evolution.calculate_evolution_score(checks)
    expected := 0.8 * 0.25 + 0.9 * 0.35 + 0.7 * 0.2 + 0.6 * 0.15 + 1.0 * 0.05
    score == expected
}