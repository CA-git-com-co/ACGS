#!/usr/bin/env python3
"""
ACGS-2 Constitutional Compliance Validator
Validates constitutional compliance across all test scenarios.
Constitutional Compliance: cdd01ef066bc6cf2
"""

import json
import argparse
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
import sys


class ConstitutionalComplianceValidator:
    """Validate constitutional compliance in ACGS-2 test results."""
    
    def __init__(self, expected_hash: str):
        self.expected_hash = expected_hash
        self.compliance_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "expected_constitutional_hash": expected_hash,
            "validation_results": {
                "hash_validation": False,
                "response_compliance": False,
                "test_coverage_compliance": False,
                "performance_compliance": False,
                "overall_compliance": False
            },
            "compliance_score": 0.0,
            "violations": [],
            "recommendations": [],
            "detailed_analysis": {}
        }
    
    def validate_hash_presence(self, test_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate constitutional hash presence in test outputs."""
        violations = []
        hash_found = False
        
        # Convert test data to string for searching
        test_content = json.dumps(test_data, default=str)
        
        # Check for constitutional hash in various formats
        hash_patterns = [
            self.expected_hash,
            f'"constitutional_hash": "{self.expected_hash}"',
            f"constitutional_hash={self.expected_hash}",
            f"hash: {self.expected_hash}"
        ]
        
        for pattern in hash_patterns:
            if pattern in test_content:
                hash_found = True
                break
        
        if not hash_found:
            violations.append(f"Constitutional hash {self.expected_hash} not found in test outputs")
        
        # Check for any constitutional hash references
        hash_references = re.findall(r'constitutional_hash["\s]*[:=]["\s]*([a-f0-9]+)', test_content)
        
        for ref in hash_references:
            if ref != self.expected_hash:
                violations.append(f"Invalid constitutional hash found: {ref} (expected: {self.expected_hash})")
        
        return hash_found and len(violations) == 0, violations
    
    def validate_response_compliance(self, test_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate that test responses include constitutional compliance indicators."""
        violations = []
        compliance_indicators = []
        
        # Look for compliance-related fields in test outputs
        test_content = json.dumps(test_data, default=str).lower()
        
        required_indicators = [
            "constitutional_compliance",
            "compliance_score",
            "constitutional_hash",
            "validation_details"
        ]
        
        for indicator in required_indicators:
            if indicator in test_content:
                compliance_indicators.append(indicator)
            else:
                violations.append(f"Missing constitutional compliance indicator: {indicator}")
        
        # Check for constitutional principles validation
        principle_indicators = [
            "democratic_participation",
            "transparency",
            "accountability",
            "fairness",
            "privacy",
            "human_dignity"
        ]
        
        principle_count = sum(1 for principle in principle_indicators if principle in test_content)
        
        if principle_count < 3:  # Require at least 3 constitutional principles
            violations.append(f"Insufficient constitutional principles coverage: {principle_count}/6")
        
        compliance_score = len(compliance_indicators) / len(required_indicators)
        return compliance_score >= 0.75, violations
    
    def validate_test_coverage_compliance(self, test_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate test coverage meets constitutional requirements."""
        violations = []
        
        # Extract test summary if available
        summary = test_data.get('summary', {})
        total_tests = summary.get('total', 0)
        passed_tests = summary.get('passed', 0)
        
        if total_tests == 0:
            violations.append("No tests found in test data")
            return False, violations
        
        success_rate = (passed_tests / total_tests) * 100
        
        # Constitutional requirement: >70% success rate
        if success_rate < 70.0:
            violations.append(f"Test success rate {success_rate:.1f}% below constitutional requirement (70%)")
        
        # Check for constitutional AI specific tests
        tests = test_data.get('tests', [])
        constitutional_tests = [
            test for test in tests 
            if any(keyword in test.get('nodeid', '').lower() 
                  for keyword in ['constitutional', 'compliance', 'validation', 'principle'])
        ]
        
        if len(constitutional_tests) < 3:
            violations.append(f"Insufficient constitutional AI tests: {len(constitutional_tests)} (minimum: 3)")
        
        return len(violations) == 0, violations
    
    def validate_performance_compliance(self, test_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate performance metrics meet constitutional requirements."""
        violations = []
        
        # Look for performance indicators in test data
        test_content = json.dumps(test_data, default=str)
        
        # Check for performance-related test execution
        performance_indicators = [
            "duration",
            "benchmark",
            "performance",
            "latency",
            "throughput"
        ]
        
        performance_found = any(indicator in test_content.lower() for indicator in performance_indicators)
        
        if not performance_found:
            violations.append("No performance metrics found in test execution")
        
        # Extract test durations if available
        tests = test_data.get('tests', [])
        durations = [test.get('duration', 0) for test in tests if 'duration' in test]
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            # Constitutional requirement: reasonable test execution times
            if avg_duration > 10.0:  # 10 seconds average
                violations.append(f"Average test duration {avg_duration:.2f}s exceeds reasonable limits")
            
            if max_duration > 60.0:  # 60 seconds maximum
                violations.append(f"Maximum test duration {max_duration:.2f}s exceeds constitutional limits")
        
        return len(violations) == 0, violations
    
    def generate_recommendations(self, violations: List[str]) -> List[str]:
        """Generate recommendations based on violations found."""
        recommendations = []
        
        if any("constitutional_hash" in v for v in violations):
            recommendations.append("Ensure all test responses include constitutional_hash field with correct value")
        
        if any("success rate" in v for v in violations):
            recommendations.append("Improve test implementation to achieve >70% success rate requirement")
        
        if any("compliance indicator" in v for v in violations):
            recommendations.append("Add constitutional compliance validation to test assertions")
        
        if any("constitutional principles" in v for v in violations):
            recommendations.append("Expand test coverage to include all constitutional principles")
        
        if any("performance" in v for v in violations):
            recommendations.append("Optimize test execution performance and add performance benchmarks")
        
        if any("constitutional AI tests" in v for v in violations):
            recommendations.append("Add more constitutional AI specific test scenarios")
        
        return recommendations
    
    def calculate_compliance_score(self, validation_results: Dict[str, bool]) -> float:
        """Calculate overall compliance score."""
        weights = {
            "hash_validation": 0.3,
            "response_compliance": 0.3,
            "test_coverage_compliance": 0.25,
            "performance_compliance": 0.15
        }
        
        score = sum(
            weights.get(key, 0) * (1.0 if value else 0.0)
            for key, value in validation_results.items()
            if key != "overall_compliance"
        )
        
        return round(score * 100, 2)
    
    def validate_compliance(self, test_reports_path: Path) -> Dict[str, Any]:
        """Perform comprehensive constitutional compliance validation."""
        try:
            with open(test_reports_path, 'r') as f:
                test_data = json.load(f)
        except Exception as e:
            self.compliance_report["violations"].append(f"Failed to load test data: {e}")
            return self.compliance_report
        
        all_violations = []
        
        # Perform all validation checks
        hash_valid, hash_violations = self.validate_hash_presence(test_data)
        self.compliance_report["validation_results"]["hash_validation"] = hash_valid
        all_violations.extend(hash_violations)
        
        response_valid, response_violations = self.validate_response_compliance(test_data)
        self.compliance_report["validation_results"]["response_compliance"] = response_valid
        all_violations.extend(response_violations)
        
        coverage_valid, coverage_violations = self.validate_test_coverage_compliance(test_data)
        self.compliance_report["validation_results"]["test_coverage_compliance"] = coverage_valid
        all_violations.extend(coverage_violations)
        
        performance_valid, performance_violations = self.validate_performance_compliance(test_data)
        self.compliance_report["validation_results"]["performance_compliance"] = performance_valid
        all_violations.extend(performance_violations)
        
        # Calculate overall compliance
        validation_results = self.compliance_report["validation_results"]
        overall_compliance = all(validation_results[key] for key in validation_results if key != "overall_compliance")
        validation_results["overall_compliance"] = overall_compliance
        
        # Store violations and generate recommendations
        self.compliance_report["violations"] = all_violations
        self.compliance_report["recommendations"] = self.generate_recommendations(all_violations)
        self.compliance_report["compliance_score"] = self.calculate_compliance_score(validation_results)
        
        # Detailed analysis
        self.compliance_report["detailed_analysis"] = {
            "total_violations": len(all_violations),
            "critical_violations": len([v for v in all_violations if "constitutional_hash" in v]),
            "performance_violations": len([v for v in all_violations if "performance" in v or "duration" in v]),
            "coverage_violations": len([v for v in all_violations if "success rate" in v or "tests" in v])
        }
        
        return self.compliance_report


def main():
    parser = argparse.ArgumentParser(description="Validate ACGS-2 constitutional compliance")
    parser.add_argument("--test-reports", type=Path, required=True, help="Path to test reports JSON")
    parser.add_argument("--expected-hash", required=True, help="Expected constitutional hash")
    parser.add_argument("--output", type=Path, required=True, help="Output compliance report JSON")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    validator = ConstitutionalComplianceValidator(args.expected_hash)
    compliance_report = validator.validate_compliance(args.test_reports)
    
    # Write compliance report
    with open(args.output, 'w') as f:
        json.dump(compliance_report, f, indent=2)
    
    # Print summary
    print(f"🔒 Constitutional Compliance Validation Complete")
    print(f"📊 Compliance Score: {compliance_report['compliance_score']}/100")
    print(f"✅ Overall Compliance: {'PASS' if compliance_report['validation_results']['overall_compliance'] else 'FAIL'}")
    print(f"⚠️ Total Violations: {len(compliance_report['violations'])}")
    
    if compliance_report['violations']:
        print("\n🚨 Violations Found:")
        for violation in compliance_report['violations'][:5]:  # Show first 5
            print(f"  - {violation}")
    
    if compliance_report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in compliance_report['recommendations'][:3]:  # Show first 3
            print(f"  - {rec}")
    
    # Exit with error if compliance fails
    if not compliance_report['validation_results']['overall_compliance']:
        sys.exit(1)


if __name__ == "__main__":
    main()
