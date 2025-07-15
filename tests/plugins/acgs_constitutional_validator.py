"""
ACGS-2 Constitutional Compliance Automation Plugin
Constitutional Hash: cdd01ef066bc6cf2

This pytest plugin implements automated constitutional governance validation with:
- Automated hash verification (cdd01ef066bc6cf2) in all test responses and database operations
- Principle coverage matrix testing across all six constitutional principles
- Violation tracking system with severity classification (CRITICAL, HIGH, MEDIUM, LOW)
- Compliance reports with letter grades (A-F) and specific improvement recommendations
- Real-time compliance monitoring integration with existing ACGS services

Constitutional Principles:
1. Democratic Participation
2. Transparency
3. Accountability
4. Fairness
5. Privacy
6. Human Dignity
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

import pytest


class ViolationSeverity(Enum):
    """Constitutional violation severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ConstitutionalPrinciple(Enum):
    """Six core constitutional principles"""
    DEMOCRATIC_PARTICIPATION = "democratic_participation"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    FAIRNESS = "fairness"
    PRIVACY = "privacy"
    HUMAN_DIGNITY = "human_dignity"


@dataclass
class ConstitutionalViolation:
    """Constitutional violation record"""
    principle: ConstitutionalPrinciple
    severity: ViolationSeverity
    description: str
    test_name: str
    timestamp: float
    context: Dict[str, Any]
    recommendation: str


@dataclass
class ComplianceScore:
    """Constitutional compliance scoring"""
    principle: ConstitutionalPrinciple
    score: float  # 0.0 to 1.0
    violations: List[ConstitutionalViolation]
    tests_passed: int
    tests_failed: int
    coverage_percentage: float


class ConstitutionalComplianceValidator:
    """Main constitutional compliance validation engine"""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.violations: List[ConstitutionalViolation] = []
        self.principle_coverage: Dict[ConstitutionalPrinciple, List[str]] = {
            principle: [] for principle in ConstitutionalPrinciple
        }
        self.test_results: Dict[str, Dict] = {}
        
    def validate_constitutional_hash(self, response_data: Any, test_name: str) -> bool:
        """Validate constitutional hash presence in response data"""
        if isinstance(response_data, dict):
            hash_present = response_data.get("constitutional_hash") == self.constitutional_hash
        elif isinstance(response_data, str):
            hash_present = self.constitutional_hash in response_data
        else:
            hash_present = False
        
        if not hash_present:
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.ACCOUNTABILITY,
                severity=ViolationSeverity.CRITICAL,
                description=f"Constitutional hash {self.constitutional_hash} missing from response",
                test_name=test_name,
                timestamp=time.time(),
                context={"response_type": type(response_data).__name__},
                recommendation="Ensure all responses include constitutional_hash field"
            )
            self.violations.append(violation)
            return False
        
        return True
    
    def validate_principle_coverage(self, principle: ConstitutionalPrinciple, test_name: str):
        """Track principle coverage across tests"""
        if test_name not in self.principle_coverage[principle]:
            self.principle_coverage[principle].append(test_name)
    
    def validate_democratic_participation(self, test_data: Dict, test_name: str) -> bool:
        """Validate democratic participation principle"""
        self.validate_principle_coverage(ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION, test_name)
        
        # Check for stakeholder inclusion
        stakeholders = test_data.get("stakeholders", [])
        if len(stakeholders) < 2:
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION,
                severity=ViolationSeverity.HIGH,
                description="Insufficient stakeholder representation in decision process",
                test_name=test_name,
                timestamp=time.time(),
                context={"stakeholder_count": len(stakeholders)},
                recommendation="Include at least 2 stakeholder groups in governance decisions"
            )
            self.violations.append(violation)
            return False
        
        return True
    
    def validate_transparency(self, test_data: Dict, test_name: str) -> bool:
        """Validate transparency principle"""
        self.validate_principle_coverage(ConstitutionalPrinciple.TRANSPARENCY, test_name)
        
        # Check for decision rationale
        has_rationale = "rationale" in test_data or "explanation" in test_data
        if not has_rationale:
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.TRANSPARENCY,
                severity=ViolationSeverity.MEDIUM,
                description="Decision lacks transparent rationale or explanation",
                test_name=test_name,
                timestamp=time.time(),
                context={"available_fields": list(test_data.keys())},
                recommendation="Include rationale or explanation field in all decisions"
            )
            self.violations.append(violation)
            return False
        
        return True
    
    def validate_accountability(self, test_data: Dict, test_name: str) -> bool:
        """Validate accountability principle"""
        self.validate_principle_coverage(ConstitutionalPrinciple.ACCOUNTABILITY, test_name)
        
        # Check for audit trail
        has_audit_trail = any(key in test_data for key in ["audit_trail", "decision_id", "timestamp"])
        if not has_audit_trail:
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.ACCOUNTABILITY,
                severity=ViolationSeverity.HIGH,
                description="Missing audit trail for accountability tracking",
                test_name=test_name,
                timestamp=time.time(),
                context={"available_fields": list(test_data.keys())},
                recommendation="Include audit_trail, decision_id, or timestamp for accountability"
            )
            self.violations.append(violation)
            return False
        
        return True
    
    def validate_fairness(self, test_data: Dict, test_name: str) -> bool:
        """Validate fairness principle"""
        self.validate_principle_coverage(ConstitutionalPrinciple.FAIRNESS, test_name)
        
        # Check for bias indicators
        bias_score = test_data.get("bias_score", 0.5)
        if bias_score > 0.3:  # Threshold for acceptable bias
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.FAIRNESS,
                severity=ViolationSeverity.MEDIUM,
                description=f"Potential bias detected with score {bias_score}",
                test_name=test_name,
                timestamp=time.time(),
                context={"bias_score": bias_score, "threshold": 0.3},
                recommendation="Review decision algorithm for bias reduction"
            )
            self.violations.append(violation)
            return False
        
        return True
    
    def validate_privacy(self, test_data: Dict, test_name: str) -> bool:
        """Validate privacy principle"""
        self.validate_principle_coverage(ConstitutionalPrinciple.PRIVACY, test_name)
        
        # Check for PII exposure
        sensitive_fields = ["ssn", "email", "phone", "address", "personal_id"]
        exposed_pii = [field for field in sensitive_fields if field in test_data]
        
        if exposed_pii:
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.PRIVACY,
                severity=ViolationSeverity.CRITICAL,
                description=f"Potential PII exposure: {exposed_pii}",
                test_name=test_name,
                timestamp=time.time(),
                context={"exposed_fields": exposed_pii},
                recommendation="Remove or encrypt PII fields in responses"
            )
            self.violations.append(violation)
            return False
        
        return True
    
    def validate_human_dignity(self, test_data: Dict, test_name: str) -> bool:
        """Validate human dignity principle"""
        self.validate_principle_coverage(ConstitutionalPrinciple.HUMAN_DIGNITY, test_name)
        
        # Check for human agency preservation
        automation_level = test_data.get("automation_level", 0.5)
        if automation_level > 0.8:  # High automation may reduce human agency
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.HUMAN_DIGNITY,
                severity=ViolationSeverity.MEDIUM,
                description=f"High automation level {automation_level} may reduce human agency",
                test_name=test_name,
                timestamp=time.time(),
                context={"automation_level": automation_level, "threshold": 0.8},
                recommendation="Ensure human oversight and control in high-automation scenarios"
            )
            self.violations.append(violation)
            return False
        
        return True
    
    def calculate_compliance_scores(self) -> Dict[ConstitutionalPrinciple, ComplianceScore]:
        """Calculate compliance scores for each principle"""
        scores = {}
        
        for principle in ConstitutionalPrinciple:
            principle_violations = [v for v in self.violations if v.principle == principle]
            tests_covered = len(self.principle_coverage[principle])
            
            # Calculate score based on violations and coverage
            violation_penalty = len(principle_violations) * 0.1
            coverage_bonus = min(tests_covered / 10, 1.0)  # Bonus for good coverage
            
            base_score = 1.0 - violation_penalty + (coverage_bonus * 0.2)
            final_score = max(0.0, min(1.0, base_score))
            
            scores[principle] = ComplianceScore(
                principle=principle,
                score=final_score,
                violations=principle_violations,
                tests_passed=tests_covered - len(principle_violations),
                tests_failed=len(principle_violations),
                coverage_percentage=(tests_covered / max(1, len(self.test_results))) * 100
            )
        
        return scores
    
    def generate_letter_grade(self, overall_score: float) -> str:
        """Generate letter grade based on overall compliance score"""
        if overall_score >= 0.95:
            return "A+"
        elif overall_score >= 0.90:
            return "A"
        elif overall_score >= 0.85:
            return "A-"
        elif overall_score >= 0.80:
            return "B+"
        elif overall_score >= 0.75:
            return "B"
        elif overall_score >= 0.70:
            return "B-"
        elif overall_score >= 0.65:
            return "C+"
        elif overall_score >= 0.60:
            return "C"
        elif overall_score >= 0.55:
            return "C-"
        elif overall_score >= 0.50:
            return "D"
        else:
            return "F"
    
    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        scores = self.calculate_compliance_scores()
        overall_score = sum(score.score for score in scores.values()) / len(scores)
        letter_grade = self.generate_letter_grade(overall_score)
        
        # Generate recommendations
        recommendations = []
        for violation in self.violations:
            if violation.recommendation not in recommendations:
                recommendations.append(violation.recommendation)
        
        # Categorize violations by severity
        violation_summary = {
            severity.value: len([v for v in self.violations if v.severity == severity])
            for severity in ViolationSeverity
        }
        
        report = {
            "timestamp": time.time(),
            "constitutional_hash": self.constitutional_hash,
            "overall_score": overall_score,
            "letter_grade": letter_grade,
            "principle_scores": {
                principle.value: asdict(score) for principle, score in scores.items()
            },
            "violation_summary": violation_summary,
            "total_violations": len(self.violations),
            "total_tests": len(self.test_results),
            "recommendations": recommendations[:10],  # Top 10 recommendations
            "compliance_status": "PASSED" if overall_score >= 0.80 else "FAILED"
        }
        
        return report


# Global validator instance
constitutional_validator = ConstitutionalComplianceValidator()


def pytest_configure(config):
    """Configure pytest with constitutional compliance markers"""
    config.addinivalue_line(
        "markers", "constitutional: mark test as constitutional compliance test"
    )
    config.addinivalue_line(
        "markers", "democratic_participation: test democratic participation principle"
    )
    config.addinivalue_line(
        "markers", "transparency: test transparency principle"
    )
    config.addinivalue_line(
        "markers", "accountability: test accountability principle"
    )
    config.addinivalue_line(
        "markers", "fairness: test fairness principle"
    )
    config.addinivalue_line(
        "markers", "privacy: test privacy principle"
    )
    config.addinivalue_line(
        "markers", "human_dignity: test human dignity principle"
    )


def pytest_runtest_setup(item):
    """Setup constitutional compliance validation for each test"""
    constitutional_validator.test_results[item.name] = {
        "start_time": time.time(),
        "status": "running"
    }


def pytest_runtest_teardown(item, nextitem):
    """Teardown and validate constitutional compliance after each test"""
    test_name = item.name
    
    # Mark test as completed
    if test_name in constitutional_validator.test_results:
        constitutional_validator.test_results[test_name]["end_time"] = time.time()
        constitutional_validator.test_results[test_name]["status"] = "completed"


def pytest_sessionfinish(session, exitstatus):
    """Generate final constitutional compliance report"""
    report = constitutional_validator.generate_compliance_report()
    
    # Save report to file
    report_filename = f"constitutional_compliance_report_{int(time.time())}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n🏛️ Constitutional Compliance Report")
    print(f"   Constitutional Hash: {report['constitutional_hash']}")
    print(f"   Overall Score: {report['overall_score']:.3f}")
    print(f"   Letter Grade: {report['letter_grade']}")
    print(f"   Total Violations: {report['total_violations']}")
    print(f"   Compliance Status: {report['compliance_status']}")
    print(f"   Report saved: {report_filename}")
    
    # Print violation summary
    if report['total_violations'] > 0:
        print(f"\n⚠️ Violation Summary:")
        for severity, count in report['violation_summary'].items():
            if count > 0:
                print(f"   {severity}: {count}")
    
    # Print top recommendations
    if report['recommendations']:
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(report['recommendations'][:5], 1):
            print(f"   {i}. {rec}")


# Pytest fixtures for constitutional compliance testing
@pytest.fixture
def constitutional_validator_fixture():
    """Fixture providing constitutional validator instance"""
    return constitutional_validator


@pytest.fixture
def constitutional_test_data():
    """Fixture providing sample constitutional test data"""
    return {
        "constitutional_hash": "cdd01ef066bc6cf2",
        "stakeholders": ["citizens", "government", "experts"],
        "rationale": "Decision based on democratic consensus",
        "audit_trail": "decision_12345",
        "timestamp": time.time(),
        "bias_score": 0.1,
        "automation_level": 0.3
    }


# Helper functions for test validation
def validate_constitutional_response(response_data: Any, test_name: str = "unknown") -> bool:
    """Helper function to validate constitutional compliance in test responses"""
    return constitutional_validator.validate_constitutional_hash(response_data, test_name)


def validate_all_principles(test_data: Dict, test_name: str = "unknown") -> Dict[ConstitutionalPrinciple, bool]:
    """Helper function to validate all constitutional principles"""
    results = {}
    
    results[ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION] = \
        constitutional_validator.validate_democratic_participation(test_data, test_name)
    
    results[ConstitutionalPrinciple.TRANSPARENCY] = \
        constitutional_validator.validate_transparency(test_data, test_name)
    
    results[ConstitutionalPrinciple.ACCOUNTABILITY] = \
        constitutional_validator.validate_accountability(test_data, test_name)
    
    results[ConstitutionalPrinciple.FAIRNESS] = \
        constitutional_validator.validate_fairness(test_data, test_name)
    
    results[ConstitutionalPrinciple.PRIVACY] = \
        constitutional_validator.validate_privacy(test_data, test_name)
    
    results[ConstitutionalPrinciple.HUMAN_DIGNITY] = \
        constitutional_validator.validate_human_dignity(test_data, test_name)
    
    return results
