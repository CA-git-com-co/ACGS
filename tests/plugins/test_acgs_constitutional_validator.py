"""
Test suite for ACGS-2 Constitutional Compliance Automation Plugin
Constitutional Hash: cdd01ef066bc6cf2

This module tests the automated constitutional governance validation plugin
including hash verification, principle coverage matrix testing, violation tracking,
and compliance reporting with letter grades.
"""

import pytest
import time
from unittest.mock import Mock, patch

from tests.plugins.acgs_constitutional_validator import (
    ConstitutionalComplianceValidator,
    ConstitutionalPrinciple,
    ViolationSeverity,
    ConstitutionalViolation,
    ComplianceScore,
    validate_constitutional_response,
    validate_all_principles
)


class TestConstitutionalComplianceValidator:
    """Test the main constitutional compliance validation engine"""
    
    def setup_method(self):
        """Setup test environment"""
        self.validator = ConstitutionalComplianceValidator()
        self.test_name = "test_constitutional_compliance"
    
    def test_constitutional_hash_validation_success(self):
        """Test successful constitutional hash validation"""
        response_data = {
            "status": "success",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "data": {"result": "validated"}
        }
        
        result = self.validator.validate_constitutional_hash(response_data, self.test_name)
        
        assert result is True
        assert len(self.validator.violations) == 0
    
    def test_constitutional_hash_validation_failure(self):
        """Test constitutional hash validation failure"""
        response_data = {
            "status": "success",
            "data": {"result": "validated"}
            # Missing constitutional_hash
        }
        
        result = self.validator.validate_constitutional_hash(response_data, self.test_name)
        
        assert result is False
        assert len(self.validator.violations) == 1
        
        violation = self.validator.violations[0]
        assert violation.principle == ConstitutionalPrinciple.ACCOUNTABILITY
        assert violation.severity == ViolationSeverity.CRITICAL
        assert "cdd01ef066bc6cf2" in violation.description
    
    def test_constitutional_hash_validation_string_response(self):
        """Test constitutional hash validation in string response"""
        response_data = "Response with constitutional hash cdd01ef066bc6cf2 embedded"
        
        result = self.validator.validate_constitutional_hash(response_data, self.test_name)
        
        assert result is True
        assert len(self.validator.violations) == 0
    
    def test_democratic_participation_validation_success(self):
        """Test successful democratic participation validation"""
        test_data = {
            "stakeholders": ["citizens", "government", "experts"],
            "decision_process": "consensus_based"
        }
        
        result = self.validator.validate_democratic_participation(test_data, self.test_name)
        
        assert result is True
        assert self.test_name in self.validator.principle_coverage[ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION]
    
    def test_democratic_participation_validation_failure(self):
        """Test democratic participation validation failure"""
        test_data = {
            "stakeholders": ["government"],  # Only one stakeholder
            "decision_process": "unilateral"
        }
        
        result = self.validator.validate_democratic_participation(test_data, self.test_name)
        
        assert result is False
        assert len(self.validator.violations) == 1
        
        violation = self.validator.violations[0]
        assert violation.principle == ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION
        assert violation.severity == ViolationSeverity.HIGH
    
    def test_transparency_validation_success(self):
        """Test successful transparency validation"""
        test_data = {
            "decision": "policy_approved",
            "rationale": "Based on comprehensive analysis and stakeholder input"
        }
        
        result = self.validator.validate_transparency(test_data, self.test_name)
        
        assert result is True
        assert self.test_name in self.validator.principle_coverage[ConstitutionalPrinciple.TRANSPARENCY]
    
    def test_transparency_validation_failure(self):
        """Test transparency validation failure"""
        test_data = {
            "decision": "policy_approved"
            # Missing rationale or explanation
        }
        
        result = self.validator.validate_transparency(test_data, self.test_name)
        
        assert result is False
        assert len(self.validator.violations) == 1
        
        violation = self.validator.violations[0]
        assert violation.principle == ConstitutionalPrinciple.TRANSPARENCY
        assert violation.severity == ViolationSeverity.MEDIUM
    
    def test_accountability_validation_success(self):
        """Test successful accountability validation"""
        test_data = {
            "decision": "policy_approved",
            "audit_trail": "decision_12345",
            "timestamp": time.time()
        }
        
        result = self.validator.validate_accountability(test_data, self.test_name)
        
        assert result is True
        assert self.test_name in self.validator.principle_coverage[ConstitutionalPrinciple.ACCOUNTABILITY]
    
    def test_accountability_validation_failure(self):
        """Test accountability validation failure"""
        test_data = {
            "decision": "policy_approved"
            # Missing audit trail, decision_id, or timestamp
        }
        
        result = self.validator.validate_accountability(test_data, self.test_name)
        
        assert result is False
        assert len(self.validator.violations) == 1
        
        violation = self.validator.violations[0]
        assert violation.principle == ConstitutionalPrinciple.ACCOUNTABILITY
        assert violation.severity == ViolationSeverity.HIGH
    
    def test_fairness_validation_success(self):
        """Test successful fairness validation"""
        test_data = {
            "decision": "policy_approved",
            "bias_score": 0.1  # Low bias score
        }
        
        result = self.validator.validate_fairness(test_data, self.test_name)
        
        assert result is True
        assert self.test_name in self.validator.principle_coverage[ConstitutionalPrinciple.FAIRNESS]
    
    def test_fairness_validation_failure(self):
        """Test fairness validation failure"""
        test_data = {
            "decision": "policy_approved",
            "bias_score": 0.5  # High bias score
        }
        
        result = self.validator.validate_fairness(test_data, self.test_name)
        
        assert result is False
        assert len(self.validator.violations) == 1
        
        violation = self.validator.violations[0]
        assert violation.principle == ConstitutionalPrinciple.FAIRNESS
        assert violation.severity == ViolationSeverity.MEDIUM
    
    def test_privacy_validation_success(self):
        """Test successful privacy validation"""
        test_data = {
            "decision": "policy_approved",
            "user_id": "anonymous_123",  # No PII
            "metadata": {"timestamp": time.time()}
        }
        
        result = self.validator.validate_privacy(test_data, self.test_name)
        
        assert result is True
        assert self.test_name in self.validator.principle_coverage[ConstitutionalPrinciple.PRIVACY]
    
    def test_privacy_validation_failure(self):
        """Test privacy validation failure"""
        test_data = {
            "decision": "policy_approved",
            "email": "user@example.com",  # PII exposure
            "ssn": "123-45-6789"  # Sensitive PII
        }
        
        result = self.validator.validate_privacy(test_data, self.test_name)
        
        assert result is False
        assert len(self.validator.violations) == 1
        
        violation = self.validator.violations[0]
        assert violation.principle == ConstitutionalPrinciple.PRIVACY
        assert violation.severity == ViolationSeverity.CRITICAL
    
    def test_human_dignity_validation_success(self):
        """Test successful human dignity validation"""
        test_data = {
            "decision": "policy_approved",
            "automation_level": 0.5  # Moderate automation
        }
        
        result = self.validator.validate_human_dignity(test_data, self.test_name)
        
        assert result is True
        assert self.test_name in self.validator.principle_coverage[ConstitutionalPrinciple.HUMAN_DIGNITY]
    
    def test_human_dignity_validation_failure(self):
        """Test human dignity validation failure"""
        test_data = {
            "decision": "policy_approved",
            "automation_level": 0.9  # Very high automation
        }
        
        result = self.validator.validate_human_dignity(test_data, self.test_name)
        
        assert result is False
        assert len(self.validator.violations) == 1
        
        violation = self.validator.violations[0]
        assert violation.principle == ConstitutionalPrinciple.HUMAN_DIGNITY
        assert violation.severity == ViolationSeverity.MEDIUM
    
    def test_compliance_score_calculation(self):
        """Test compliance score calculation"""
        # Add some violations
        self.validator.violations = [
            ConstitutionalViolation(
                principle=ConstitutionalPrinciple.TRANSPARENCY,
                severity=ViolationSeverity.MEDIUM,
                description="Missing rationale",
                test_name="test_1",
                timestamp=time.time(),
                context={},
                recommendation="Add rationale"
            ),
            ConstitutionalViolation(
                principle=ConstitutionalPrinciple.FAIRNESS,
                severity=ViolationSeverity.HIGH,
                description="High bias detected",
                test_name="test_2",
                timestamp=time.time(),
                context={},
                recommendation="Reduce bias"
            )
        ]
        
        # Add some test coverage
        self.validator.principle_coverage[ConstitutionalPrinciple.TRANSPARENCY] = ["test_1", "test_2"]
        self.validator.principle_coverage[ConstitutionalPrinciple.FAIRNESS] = ["test_2"]
        self.validator.test_results = {"test_1": {}, "test_2": {}}
        
        scores = self.validator.calculate_compliance_scores()
        
        assert ConstitutionalPrinciple.TRANSPARENCY in scores
        assert ConstitutionalPrinciple.FAIRNESS in scores
        
        transparency_score = scores[ConstitutionalPrinciple.TRANSPARENCY]
        assert transparency_score.score < 1.0  # Should be reduced due to violation
        assert len(transparency_score.violations) == 1
        
        fairness_score = scores[ConstitutionalPrinciple.FAIRNESS]
        assert fairness_score.score < transparency_score.score  # Should be lower due to HIGH severity
    
    def test_letter_grade_generation(self):
        """Test letter grade generation"""
        test_cases = [
            (0.98, "A+"),
            (0.92, "A"),
            (0.87, "A-"),
            (0.82, "B+"),
            (0.77, "B"),
            (0.72, "B-"),
            (0.67, "C+"),
            (0.62, "C"),
            (0.57, "C-"),
            (0.52, "D"),
            (0.42, "F")
        ]
        
        for score, expected_grade in test_cases:
            grade = self.validator.generate_letter_grade(score)
            assert grade == expected_grade, f"Score {score} should generate grade {expected_grade}, got {grade}"
    
    def test_compliance_report_generation(self):
        """Test comprehensive compliance report generation"""
        # Setup test data
        self.validator.violations = [
            ConstitutionalViolation(
                principle=ConstitutionalPrinciple.TRANSPARENCY,
                severity=ViolationSeverity.MEDIUM,
                description="Missing rationale",
                test_name="test_1",
                timestamp=time.time(),
                context={},
                recommendation="Add rationale field"
            )
        ]
        
        self.validator.principle_coverage[ConstitutionalPrinciple.TRANSPARENCY] = ["test_1"]
        self.validator.test_results = {"test_1": {}}
        
        report = self.validator.generate_compliance_report()
        
        # Validate report structure
        assert "constitutional_hash" in report
        assert report["constitutional_hash"] == "cdd01ef066bc6cf2"
        assert "overall_score" in report
        assert "letter_grade" in report
        assert "principle_scores" in report
        assert "violation_summary" in report
        assert "total_violations" in report
        assert "total_tests" in report
        assert "recommendations" in report
        assert "compliance_status" in report
        
        # Validate content
        assert report["total_violations"] == 1
        assert report["total_tests"] == 1
        assert "Add rationale field" in report["recommendations"]
        assert report["violation_summary"]["MEDIUM"] == 1


class TestHelperFunctions:
    """Test helper functions for constitutional compliance"""
    
    def test_validate_constitutional_response_helper(self):
        """Test validate_constitutional_response helper function"""
        response_data = {
            "status": "success",
            "constitutional_hash": "cdd01ef066bc6cf2"
        }
        
        result = validate_constitutional_response(response_data, "test_helper")
        assert result is True
    
    def test_validate_all_principles_helper(self):
        """Test validate_all_principles helper function"""
        test_data = {
            "stakeholders": ["citizens", "government"],
            "rationale": "Democratic decision",
            "audit_trail": "decision_123",
            "bias_score": 0.1,
            "automation_level": 0.3
        }
        
        results = validate_all_principles(test_data, "test_all_principles")
        
        # Should validate all principles
        assert len(results) == 6
        assert all(principle in results for principle in ConstitutionalPrinciple)
        
        # Most should pass with good test data
        passed_count = sum(1 for result in results.values() if result)
        assert passed_count >= 4  # At least 4 out of 6 should pass


@pytest.mark.constitutional
class TestConstitutionalComplianceIntegration:
    """Integration tests for constitutional compliance validation"""
    
    def test_end_to_end_compliance_validation(self):
        """Test end-to-end constitutional compliance validation"""
        validator = ConstitutionalComplianceValidator()
        
        # Test data with good compliance
        good_test_data = {
            "constitutional_hash": "cdd01ef066bc6cf2",
            "stakeholders": ["citizens", "government", "experts"],
            "rationale": "Comprehensive democratic process",
            "audit_trail": "decision_12345",
            "timestamp": time.time(),
            "bias_score": 0.1,
            "automation_level": 0.3
        }
        
        # Validate all aspects
        hash_valid = validator.validate_constitutional_hash(good_test_data, "integration_test")
        all_principles = validate_all_principles(good_test_data, "integration_test")
        
        assert hash_valid is True
        assert all(result for result in all_principles.values())
        
        # Generate compliance report
        report = validator.generate_compliance_report()
        
        assert report["compliance_status"] == "PASSED"
        assert report["letter_grade"] in ["A+", "A", "A-"]
        assert report["total_violations"] == 0
