#!/usr/bin/env python3
"""
Issue Prioritization and Classification Framework for ACGS-2
Analyzes all discovered issues from testing phases, classifies by severity,
and creates a prioritized remediation plan.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class IssueSeverity(Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"

class IssueCategory(Enum):
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    FUNCTIONALITY = "FUNCTIONALITY"
    RELIABILITY = "RELIABILITY"
    MAINTAINABILITY = "MAINTAINABILITY"
    USABILITY = "USABILITY"

@dataclass
class Issue:
    id: str
    title: str
    description: str
    severity: IssueSeverity
    category: IssueCategory
    source_test: str
    impact_score: float  # 0-10 scale
    effort_estimate: str  # LOW, MEDIUM, HIGH
    affected_components: List[str]
    risk_level: str
    recommendations: List[str]
    details: Dict[str, Any]

class IssueAnalyzer:
    def __init__(self):
        self.issues = []
        self.project_root = project_root
        
    def load_test_results(self):
        """Load all test results from previous testing phases."""
        test_result_files = [
            "test_coverage_analysis.json",
            "core_algorithm_test_results.json",
            "wina_performance_test_results.json",
            "business_rules_test_results.json",
            "integration_test_results.json",
            "e2e_workflow_test_results.json",
            "performance_benchmark_results.json",
            "security_validation_results.json"
        ]
        
        all_results = {}
        
        for result_file in test_result_files:
            file_path = self.project_root / result_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        all_results[result_file] = data
                        print(f"✓ Loaded {result_file}")
                except Exception as e:
                    print(f"✗ Failed to load {result_file}: {e}")
            else:
                print(f"⊝ {result_file} not found")
        
        return all_results
    
    def analyze_coverage_issues(self, coverage_data: Dict[str, Any]) -> List[Issue]:
        """Analyze test coverage issues."""
        issues = []
        
        if "coverage_gaps" in coverage_data:
            gaps = coverage_data["coverage_gaps"]
            
            # Critical gaps in core components
            if gaps.get("critical_gaps"):
                for critical_gap in gaps["critical_gaps"]:
                    issues.append(Issue(
                        id=f"COV-CRIT-{len(issues)+1:03d}",
                        title=f"Critical component lacks test coverage: {critical_gap['name']}",
                        description=f"Critical component {critical_gap['name']} has no test coverage with {critical_gap['python_files']} Python files",
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.RELIABILITY,
                        source_test="test_coverage_analysis",
                        impact_score=9.0,
                        effort_estimate="HIGH",
                        affected_components=[critical_gap['name']],
                        risk_level="HIGH",
                        recommendations=[
                            f"Create comprehensive test suite for {critical_gap['name']}",
                            "Implement unit tests for all public methods",
                            "Add integration tests for component interactions"
                        ],
                        details=critical_gap
                    ))
            
            # Overall low coverage
            coverage_percentage = gaps.get("coverage_percentage", 0)
            if coverage_percentage < 80:
                issues.append(Issue(
                    id=f"COV-MAJ-{len(issues)+1:03d}",
                    title=f"Overall test coverage below target: {coverage_percentage:.1f}%",
                    description=f"Current test coverage is {coverage_percentage:.1f}%, below the 80% target",
                    severity=IssueSeverity.MAJOR,
                    category=IssueCategory.RELIABILITY,
                    source_test="test_coverage_analysis",
                    impact_score=7.0,
                    effort_estimate="HIGH",
                    affected_components=["entire_system"],
                    risk_level="MEDIUM",
                    recommendations=[
                        "Increase test coverage to meet 80% target",
                        "Focus on untested critical paths",
                        "Implement automated coverage reporting"
                    ],
                    details={"current_coverage": coverage_percentage, "target_coverage": 80}
                ))
        
        return issues
    
    def analyze_performance_issues(self, performance_data: Dict[str, Any]) -> List[Issue]:
        """Analyze performance benchmark issues."""
        issues = []
        
        if "results" in performance_data:
            for result in performance_data["results"]:
                if not result.get("meets_targets", True):
                    # Determine severity based on how far from targets
                    target_metrics = result.get("target_metrics", {})
                    actual_metrics = result.get("actual_metrics", {})
                    
                    severity = IssueSeverity.MINOR
                    impact_score = 5.0
                    
                    # Check for critical performance issues
                    for metric, target in target_metrics.items():
                        actual = actual_metrics.get(metric, 0)
                        if "latency" in metric.lower():
                            if actual > target * 2:  # More than 2x target
                                severity = IssueSeverity.CRITICAL
                                impact_score = 9.0
                            elif actual > target * 1.5:  # More than 1.5x target
                                severity = IssueSeverity.MAJOR
                                impact_score = 7.0
                        elif "throughput" in metric.lower() or "hit_rate" in metric.lower():
                            if actual < target * 0.5:  # Less than 50% of target
                                severity = IssueSeverity.CRITICAL
                                impact_score = 9.0
                            elif actual < target * 0.75:  # Less than 75% of target
                                severity = IssueSeverity.MAJOR
                                impact_score = 7.0
                    
                    issues.append(Issue(
                        id=f"PERF-{severity.value[:4]}-{len(issues)+1:03d}",
                        title=f"Performance target not met: {result['test_name']}",
                        description=f"Performance benchmark {result['test_name']} failed to meet targets",
                        severity=severity,
                        category=IssueCategory.PERFORMANCE,
                        source_test="performance_benchmark",
                        impact_score=impact_score,
                        effort_estimate="MEDIUM" if severity == IssueSeverity.MINOR else "HIGH",
                        affected_components=[result['test_name']],
                        risk_level="HIGH" if severity == IssueSeverity.CRITICAL else "MEDIUM",
                        recommendations=[
                            "Optimize performance-critical code paths",
                            "Review algorithm complexity",
                            "Consider caching strategies",
                            "Profile and identify bottlenecks"
                        ],
                        details=result
                    ))
        
        return issues
    
    def analyze_security_issues(self, security_data: Dict[str, Any]) -> List[Issue]:
        """Analyze security validation issues."""
        issues = []
        
        if "results" in security_data:
            for result in security_data["results"]:
                vulnerabilities = result.get("vulnerabilities_found", 0)
                
                if vulnerabilities > 0:
                    # Map risk level to severity
                    risk_level = result.get("risk_level", "MEDIUM")
                    if risk_level == "CRITICAL":
                        severity = IssueSeverity.CRITICAL
                        impact_score = 10.0
                    elif risk_level == "HIGH":
                        severity = IssueSeverity.MAJOR
                        impact_score = 8.0
                    elif risk_level == "MEDIUM":
                        severity = IssueSeverity.MAJOR
                        impact_score = 6.0
                    else:
                        severity = IssueSeverity.MINOR
                        impact_score = 4.0
                    
                    issues.append(Issue(
                        id=f"SEC-{severity.value[:4]}-{len(issues)+1:03d}",
                        title=f"Security vulnerabilities found: {result['test_name']}",
                        description=f"Found {vulnerabilities} security vulnerabilities in {result['test_name']}",
                        severity=severity,
                        category=IssueCategory.SECURITY,
                        source_test="security_validation",
                        impact_score=impact_score,
                        effort_estimate="HIGH" if severity == IssueSeverity.CRITICAL else "MEDIUM",
                        affected_components=[result['test_name']],
                        risk_level=risk_level,
                        recommendations=result.get("recommendations", []),
                        details=result
                    ))
        
        return issues
    
    def analyze_functionality_issues(self, test_results: Dict[str, Any]) -> List[Issue]:
        """Analyze functionality test issues."""
        issues = []
        
        # Check business rules test results
        if "business_rules_test_results.json" in test_results:
            br_data = test_results["business_rules_test_results.json"]
            if br_data.get("failed", 0) > 0 or br_data.get("errors", 0) > 0:
                edge_case_rate = br_data.get("edge_case_summary", {}).get("edge_case_success_rate", 0)
                
                severity = IssueSeverity.MAJOR if edge_case_rate < 50 else IssueSeverity.MINOR
                
                issues.append(Issue(
                    id=f"FUNC-{severity.value[:4]}-{len(issues)+1:03d}",
                    title="Business rule validation failures",
                    description=f"Business rule tests failed with {edge_case_rate:.1f}% edge case success rate",
                    severity=severity,
                    category=IssueCategory.FUNCTIONALITY,
                    source_test="business_rules_testing",
                    impact_score=7.0 if severity == IssueSeverity.MAJOR else 5.0,
                    effort_estimate="MEDIUM",
                    affected_components=["business_rules", "policy_governance"],
                    risk_level="MEDIUM",
                    recommendations=[
                        "Improve edge case handling in business rules",
                        "Review policy validation logic",
                        "Enhance error handling patterns"
                    ],
                    details=br_data
                ))
        
        return issues
    
    def prioritize_issues(self, issues: List[Issue]) -> List[Issue]:
        """Prioritize issues based on severity, impact, and risk."""
        def priority_score(issue: Issue) -> float:
            # Base score from severity
            severity_scores = {
                IssueSeverity.CRITICAL: 100,
                IssueSeverity.MAJOR: 75,
                IssueSeverity.MINOR: 50,
                IssueSeverity.INFO: 25
            }
            
            # Category multipliers
            category_multipliers = {
                IssueCategory.SECURITY: 1.2,
                IssueCategory.PERFORMANCE: 1.1,
                IssueCategory.FUNCTIONALITY: 1.0,
                IssueCategory.RELIABILITY: 1.1,
                IssueCategory.MAINTAINABILITY: 0.8,
                IssueCategory.USABILITY: 0.7
            }
            
            base_score = severity_scores[issue.severity]
            category_multiplier = category_multipliers[issue.category]
            impact_multiplier = issue.impact_score / 10.0
            
            return base_score * category_multiplier * impact_multiplier
        
        return sorted(issues, key=priority_score, reverse=True)
    
    def generate_remediation_plan(self, prioritized_issues: List[Issue]) -> Dict[str, Any]:
        """Generate a prioritized remediation plan."""
        plan = {
            "immediate_action_required": [],
            "short_term_fixes": [],
            "medium_term_improvements": [],
            "long_term_enhancements": []
        }
        
        for issue in prioritized_issues:
            if issue.severity == IssueSeverity.CRITICAL:
                plan["immediate_action_required"].append({
                    "issue_id": issue.id,
                    "title": issue.title,
                    "effort": issue.effort_estimate,
                    "components": issue.affected_components,
                    "recommendations": issue.recommendations[:3]  # Top 3 recommendations
                })
            elif issue.severity == IssueSeverity.MAJOR:
                if issue.category in [IssueCategory.SECURITY, IssueCategory.PERFORMANCE]:
                    plan["short_term_fixes"].append({
                        "issue_id": issue.id,
                        "title": issue.title,
                        "effort": issue.effort_estimate,
                        "components": issue.affected_components,
                        "recommendations": issue.recommendations[:2]
                    })
                else:
                    plan["medium_term_improvements"].append({
                        "issue_id": issue.id,
                        "title": issue.title,
                        "effort": issue.effort_estimate,
                        "components": issue.affected_components,
                        "recommendations": issue.recommendations[:2]
                    })
            else:
                plan["long_term_enhancements"].append({
                    "issue_id": issue.id,
                    "title": issue.title,
                    "effort": issue.effort_estimate,
                    "components": issue.affected_components,
                    "recommendations": issue.recommendations[:1]
                })
        
        return plan
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete issue analysis and prioritization."""
        print("Starting Issue Prioritization and Classification...")
        print("=" * 60)
        
        # Load all test results
        test_results = self.load_test_results()
        
        # Analyze issues from different test phases
        all_issues = []
        
        if "test_coverage_analysis.json" in test_results:
            coverage_issues = self.analyze_coverage_issues(test_results["test_coverage_analysis.json"])
            all_issues.extend(coverage_issues)
            print(f"✓ Analyzed coverage issues: {len(coverage_issues)} found")
        
        if "performance_benchmark_results.json" in test_results:
            performance_issues = self.analyze_performance_issues(test_results["performance_benchmark_results.json"])
            all_issues.extend(performance_issues)
            print(f"✓ Analyzed performance issues: {len(performance_issues)} found")
        
        if "security_validation_results.json" in test_results:
            security_issues = self.analyze_security_issues(test_results["security_validation_results.json"])
            all_issues.extend(security_issues)
            print(f"✓ Analyzed security issues: {len(security_issues)} found")
        
        functionality_issues = self.analyze_functionality_issues(test_results)
        all_issues.extend(functionality_issues)
        print(f"✓ Analyzed functionality issues: {len(functionality_issues)} found")
        
        # Prioritize issues
        prioritized_issues = self.prioritize_issues(all_issues)
        
        # Generate remediation plan
        remediation_plan = self.generate_remediation_plan(prioritized_issues)
        
        # Generate summary statistics
        severity_counts = {
            "critical": sum(1 for issue in all_issues if issue.severity == IssueSeverity.CRITICAL),
            "major": sum(1 for issue in all_issues if issue.severity == IssueSeverity.MAJOR),
            "minor": sum(1 for issue in all_issues if issue.severity == IssueSeverity.MINOR),
            "info": sum(1 for issue in all_issues if issue.severity == IssueSeverity.INFO)
        }
        
        category_counts = {}
        for category in IssueCategory:
            category_counts[category.value.lower()] = sum(1 for issue in all_issues if issue.category == category)
        
        analysis_result = {
            "total_issues": len(all_issues),
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "prioritized_issues": [
                {
                    "id": issue.id,
                    "title": issue.title,
                    "description": issue.description,
                    "severity": issue.severity.value,
                    "category": issue.category.value,
                    "source_test": issue.source_test,
                    "impact_score": issue.impact_score,
                    "effort_estimate": issue.effort_estimate,
                    "affected_components": issue.affected_components,
                    "risk_level": issue.risk_level,
                    "recommendations": issue.recommendations,
                    "details": issue.details
                }
                for issue in prioritized_issues
            ],
            "remediation_plan": remediation_plan,
            "analysis_metadata": {
                "analysis_timestamp": time.time(),
                "test_results_analyzed": list(test_results.keys()),
                "total_test_phases": len(test_results)
            }
        }
        
        print("\n" + "=" * 60)
        print("ISSUE ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total Issues Found: {len(all_issues)}")
        print(f"Critical: {severity_counts['critical']}")
        print(f"Major: {severity_counts['major']}")
        print(f"Minor: {severity_counts['minor']}")
        print(f"Info: {severity_counts['info']}")
        print("\nCategory Breakdown:")
        for category, count in category_counts.items():
            if count > 0:
                print(f"  {category.title()}: {count}")
        
        print(f"\nRemediation Plan:")
        print(f"  Immediate Action Required: {len(remediation_plan['immediate_action_required'])}")
        print(f"  Short-term Fixes: {len(remediation_plan['short_term_fixes'])}")
        print(f"  Medium-term Improvements: {len(remediation_plan['medium_term_improvements'])}")
        print(f"  Long-term Enhancements: {len(remediation_plan['long_term_enhancements'])}")
        
        return analysis_result

def main():
    analyzer = IssueAnalyzer()
    analysis_result = analyzer.run_analysis()
    
    # Save results
    output_file = project_root / "issue_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    print(f"\nDetailed analysis saved to: {output_file}")
    
    # Return appropriate exit code based on critical issues
    critical_issues = analysis_result["severity_breakdown"]["critical"]
    if critical_issues > 0:
        print(f"\n⚠️  {critical_issues} critical issues require immediate attention!")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
