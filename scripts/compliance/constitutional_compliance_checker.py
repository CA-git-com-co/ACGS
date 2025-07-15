#!/usr/bin/env python3
"""
ACGS-2 Automated Constitutional Compliance Checker
Comprehensive validation system for constitutional compliance monitoring.
Constitutional Compliance: cdd01ef066bc6cf2
"""

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ComplianceViolation:
    """Represents a constitutional compliance violation."""
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'hash', 'principle', 'performance', 'coverage'
    description: str
    location: str
    recommendation: str
    timestamp: datetime


@dataclass
class ComplianceMetrics:
    """Constitutional compliance metrics."""
    total_checks: int
    passed_checks: int
    failed_checks: int
    compliance_score: float
    constitutional_hash_valid: bool
    principle_coverage_score: float
    performance_compliance_score: float
    overall_grade: str  # 'A', 'B', 'C', 'D', 'F'


class ConstitutionalComplianceChecker:
    """Automated constitutional compliance validation system."""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    REQUIRED_PRINCIPLES = [
        "democratic_participation",
        "transparency", 
        "accountability",
        "fairness",
        "privacy",
        "human_dignity"
    ]
    
    PERFORMANCE_THRESHOLDS = {
        "p99_latency_ms": 5.0,
        "throughput_rps": 100.0,
        "cache_hit_rate_percent": 85.0
    }
    
    def __init__(self):
        self.violations: List[ComplianceViolation] = []
        self.metrics = ComplianceMetrics(0, 0, 0, 0.0, False, 0.0, 0.0, 'F')
        self.start_time = datetime.now(timezone.utc)
    
    def add_violation(self, severity: str, category: str, description: str, 
                     location: str, recommendation: str):
        """Add a compliance violation."""
        violation = ComplianceViolation(
            severity=severity,
            category=category,
            description=description,
            location=location,
            recommendation=recommendation,
            timestamp=datetime.now(timezone.utc)
        )
        self.violations.append(violation)
        logger.warning(f"Compliance violation: {description}")
    
    def validate_constitutional_hash(self, data: Any, location: str = "unknown") -> bool:
        """Validate constitutional hash presence and correctness."""
        self.metrics.total_checks += 1
        
        # Convert data to string for searching
        data_str = json.dumps(data, default=str) if not isinstance(data, str) else data
        
        # Check for exact hash match
        if self.CONSTITUTIONAL_HASH in data_str:
            # Verify it's in the correct format
            hash_patterns = [
                f'"constitutional_hash": "{self.CONSTITUTIONAL_HASH}"',
                f"constitutional_hash={self.CONSTITUTIONAL_HASH}",
                f"'constitutional_hash': '{self.CONSTITUTIONAL_HASH}'"
            ]
            
            if any(pattern in data_str for pattern in hash_patterns):
                self.metrics.passed_checks += 1
                return True
        
        # Check for any constitutional hash (might be wrong)
        wrong_hashes = re.findall(r'constitutional_hash["\s]*[:=]["\s]*([a-f0-9]+)', data_str)
        if wrong_hashes:
            for wrong_hash in wrong_hashes:
                if wrong_hash != self.CONSTITUTIONAL_HASH:
                    self.add_violation(
                        severity="critical",
                        category="hash",
                        description=f"Invalid constitutional hash: {wrong_hash}",
                        location=location,
                        recommendation=f"Replace with correct hash: {self.CONSTITUTIONAL_HASH}"
                    )
        else:
            self.add_violation(
                severity="critical",
                category="hash",
                description="Constitutional hash missing",
                location=location,
                recommendation=f"Add constitutional_hash field with value: {self.CONSTITUTIONAL_HASH}"
            )
        
        self.metrics.failed_checks += 1
        return False
    
    def validate_constitutional_principles(self, data: Dict[str, Any], location: str = "unknown") -> float:
        """Validate constitutional principles coverage."""
        self.metrics.total_checks += 1
        
        data_str = json.dumps(data, default=str).lower()
        principles_found = []
        
        for principle in self.REQUIRED_PRINCIPLES:
            if principle in data_str:
                principles_found.append(principle)
        
        coverage_score = len(principles_found) / len(self.REQUIRED_PRINCIPLES)
        
        if coverage_score < 0.5:  # Less than 50% coverage
            self.add_violation(
                severity="high",
                category="principle",
                description=f"Insufficient constitutional principles coverage: {coverage_score:.1%}",
                location=location,
                recommendation="Ensure all constitutional principles are validated"
            )
            self.metrics.failed_checks += 1
        else:
            self.metrics.passed_checks += 1
        
        return coverage_score
    
    def validate_performance_compliance(self, metrics: Dict[str, Any], location: str = "unknown") -> float:
        """Validate performance metrics against constitutional requirements."""
        self.metrics.total_checks += 1
        
        performance_score = 0.0
        total_metrics = len(self.PERFORMANCE_THRESHOLDS)
        
        for metric, threshold in self.PERFORMANCE_THRESHOLDS.items():
            if metric in metrics:
                value = metrics[metric]
                
                if metric == "p99_latency_ms":
                    if value <= threshold:
                        performance_score += 1.0 / total_metrics
                    else:
                        self.add_violation(
                            severity="medium",
                            category="performance",
                            description=f"P99 latency {value}ms exceeds threshold {threshold}ms",
                            location=location,
                            recommendation="Optimize critical path performance"
                        )
                
                elif metric == "throughput_rps":
                    if value >= threshold:
                        performance_score += 1.0 / total_metrics
                    else:
                        self.add_violation(
                            severity="medium",
                            category="performance",
                            description=f"Throughput {value} RPS below threshold {threshold} RPS",
                            location=location,
                            recommendation="Implement async processing and connection pooling"
                        )
                
                elif metric == "cache_hit_rate_percent":
                    if value >= threshold:
                        performance_score += 1.0 / total_metrics
                    else:
                        self.add_violation(
                            severity="low",
                            category="performance",
                            description=f"Cache hit rate {value}% below threshold {threshold}%",
                            location=location,
                            recommendation="Implement multi-tier caching strategy"
                        )
        
        if performance_score >= 0.8:
            self.metrics.passed_checks += 1
        else:
            self.metrics.failed_checks += 1
        
        return performance_score
    
    def validate_test_coverage(self, test_results: Dict[str, Any], location: str = "unknown") -> float:
        """Validate test coverage meets constitutional requirements."""
        self.metrics.total_checks += 1
        
        summary = test_results.get('summary', {})
        total_tests = summary.get('total', 0)
        passed_tests = summary.get('passed', 0)
        
        if total_tests == 0:
            self.add_violation(
                severity="critical",
                category="coverage",
                description="No tests found",
                location=location,
                recommendation="Implement comprehensive test suite"
            )
            self.metrics.failed_checks += 1
            return 0.0
        
        success_rate = passed_tests / total_tests
        
        if success_rate < 0.7:  # Constitutional requirement: >70%
            self.add_violation(
                severity="high",
                category="coverage",
                description=f"Test success rate {success_rate:.1%} below constitutional requirement (70%)",
                location=location,
                recommendation="Fix failing tests to achieve >70% success rate"
            )
            self.metrics.failed_checks += 1
        else:
            self.metrics.passed_checks += 1
        
        return success_rate
    
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single file for constitutional compliance."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for constitutional hash in file content
            hash_valid = self.validate_constitutional_hash(content, str(file_path))
            
            # If it's a JSON file, parse and validate structure
            if file_path.suffix == '.json':
                try:
                    data = json.loads(content)
                    principle_score = self.validate_constitutional_principles(data, str(file_path))
                    
                    # Check for performance metrics
                    if 'performance' in content.lower() or 'benchmark' in content.lower():
                        perf_score = self.validate_performance_compliance(data, str(file_path))
                    else:
                        perf_score = 1.0  # Not applicable
                    
                    # Check for test results
                    if 'tests' in data or 'summary' in data:
                        coverage_score = self.validate_test_coverage(data, str(file_path))
                    else:
                        coverage_score = 1.0  # Not applicable
                    
                except json.JSONDecodeError:
                    self.add_violation(
                        severity="medium",
                        category="format",
                        description="Invalid JSON format",
                        location=str(file_path),
                        recommendation="Fix JSON syntax errors"
                    )
                    principle_score = perf_score = coverage_score = 0.0
            else:
                # For non-JSON files, just check principles in content
                principle_score = self.validate_constitutional_principles(
                    {"content": content}, str(file_path)
                )
                perf_score = coverage_score = 1.0  # Not applicable
            
            return {
                "file": str(file_path),
                "hash_valid": hash_valid,
                "principle_score": principle_score,
                "performance_score": perf_score,
                "coverage_score": coverage_score,
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
            
        except Exception as e:
            self.add_violation(
                severity="high",
                category="access",
                description=f"Failed to validate file: {e}",
                location=str(file_path),
                recommendation="Ensure file is accessible and properly formatted"
            )
            return {
                "file": str(file_path),
                "error": str(e),
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
    
    def validate_directory(self, directory: Path, patterns: List[str] = None) -> Dict[str, Any]:
        """Validate all files in a directory for constitutional compliance."""
        if patterns is None:
            patterns = ["*.py", "*.json", "*.md", "*.yml", "*.yaml"]
        
        results = []
        
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    result = self.validate_file(file_path)
                    results.append(result)
        
        return {
            "directory": str(directory),
            "files_validated": len(results),
            "results": results,
            "constitutional_hash": self.CONSTITUTIONAL_HASH
        }
    
    def calculate_final_metrics(self) -> ComplianceMetrics:
        """Calculate final compliance metrics."""
        if self.metrics.total_checks > 0:
            self.metrics.compliance_score = self.metrics.passed_checks / self.metrics.total_checks
        
        # Determine overall grade
        if self.metrics.compliance_score >= 0.95:
            self.metrics.overall_grade = 'A'
        elif self.metrics.compliance_score >= 0.85:
            self.metrics.overall_grade = 'B'
        elif self.metrics.compliance_score >= 0.70:
            self.metrics.overall_grade = 'C'
        elif self.metrics.compliance_score >= 0.60:
            self.metrics.overall_grade = 'D'
        else:
            self.metrics.overall_grade = 'F'
        
        # Check if constitutional hash validation passed
        hash_violations = [v for v in self.violations if v.category == "hash"]
        self.metrics.constitutional_hash_valid = len(hash_violations) == 0
        
        return self.metrics
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self.start_time).total_seconds()
        
        # Calculate final metrics
        final_metrics = self.calculate_final_metrics()
        
        # Group violations by severity
        violations_by_severity = {}
        for violation in self.violations:
            if violation.severity not in violations_by_severity:
                violations_by_severity[violation.severity] = []
            violations_by_severity[violation.severity].append({
                "category": violation.category,
                "description": violation.description,
                "location": violation.location,
                "recommendation": violation.recommendation,
                "timestamp": violation.timestamp.isoformat()
            })
        
        return {
            "constitutional_compliance_report": {
                "timestamp": end_time.isoformat(),
                "duration_seconds": round(duration, 2),
                "constitutional_hash": self.CONSTITUTIONAL_HASH,
                "metrics": {
                    "total_checks": final_metrics.total_checks,
                    "passed_checks": final_metrics.passed_checks,
                    "failed_checks": final_metrics.failed_checks,
                    "compliance_score": round(final_metrics.compliance_score, 3),
                    "overall_grade": final_metrics.overall_grade,
                    "constitutional_hash_valid": final_metrics.constitutional_hash_valid
                },
                "violations": {
                    "total_count": len(self.violations),
                    "by_severity": violations_by_severity,
                    "by_category": self._group_violations_by_category()
                },
                "recommendations": self._generate_top_recommendations(),
                "compliance_status": "PASS" if final_metrics.compliance_score >= 0.7 else "FAIL"
            }
        }
    
    def _group_violations_by_category(self) -> Dict[str, int]:
        """Group violations by category."""
        categories = {}
        for violation in self.violations:
            categories[violation.category] = categories.get(violation.category, 0) + 1
        return categories
    
    def _generate_top_recommendations(self) -> List[str]:
        """Generate top recommendations based on violations."""
        recommendations = set()
        
        # Add recommendations from violations
        for violation in self.violations:
            recommendations.add(violation.recommendation)
        
        # Add general recommendations
        if any(v.category == "hash" for v in self.violations):
            recommendations.add("Implement automated constitutional hash validation in CI/CD")
        
        if any(v.category == "performance" for v in self.violations):
            recommendations.add("Establish performance monitoring and alerting")
        
        if any(v.category == "coverage" for v in self.violations):
            recommendations.add("Expand test coverage to meet constitutional requirements")
        
        return list(recommendations)[:10]  # Top 10 recommendations


async def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS-2 Constitutional Compliance Checker")
    parser.add_argument("--directory", type=Path, default=".", help="Directory to validate")
    parser.add_argument("--output", type=Path, help="Output report file")
    parser.add_argument("--patterns", nargs="+", default=["*.py", "*.json"], help="File patterns to check")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    checker = ConstitutionalComplianceChecker()
    
    print(f"🔒 Starting Constitutional Compliance Check")
    print(f"📁 Directory: {args.directory}")
    print(f"🔍 Patterns: {args.patterns}")
    print(f"⚖️ Constitutional Hash: {checker.CONSTITUTIONAL_HASH}")
    
    # Validate directory
    results = checker.validate_directory(args.directory, args.patterns)
    
    # Generate report
    report = checker.generate_report()
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {args.output}")
    
    # Print summary
    metrics = report["constitutional_compliance_report"]["metrics"]
    print(f"\n📊 Compliance Summary:")
    print(f"  Grade: {metrics['overall_grade']}")
    print(f"  Score: {metrics['compliance_score']:.1%}")
    print(f"  Checks: {metrics['passed_checks']}/{metrics['total_checks']}")
    print(f"  Constitutional Hash: {'✅' if metrics['constitutional_hash_valid'] else '❌'}")
    
    violations = report["constitutional_compliance_report"]["violations"]
    if violations["total_count"] > 0:
        print(f"\n⚠️ Violations Found: {violations['total_count']}")
        for severity, count in violations["by_severity"].items():
            print(f"  {severity.title()}: {len(count)}")
    
    # Exit with appropriate code
    if report["constitutional_compliance_report"]["compliance_status"] == "FAIL":
        sys.exit(1)
    else:
        print(f"\n✅ Constitutional Compliance: PASS")


def pytest_configure(config):
    """Configure pytest plugin for constitutional compliance checking."""
    config.addinivalue_line(
        "markers",
        "constitutional: mark test as constitutional compliance test"
    )


def pytest_runtest_teardown(item, nextitem=None):
    """Check constitutional compliance after each test."""
    if hasattr(item, 'funcargs'):
        # Check test result for constitutional compliance
        checker = ConstitutionalComplianceChecker()

        # Validate any test outputs that might contain constitutional data
        for _, arg_value in item.funcargs.items():
            if isinstance(arg_value, dict) and 'constitutional_hash' in str(arg_value):
                checker.validate_constitutional_hash(arg_value, f"test:{item.name}")


def pytest_sessionfinish(session, exitstatus=None):
    """Generate constitutional compliance report at end of test session."""
    if hasattr(session.config, 'constitutional_checker'):
        checker = session.config.constitutional_checker
        report = checker.generate_report()

        # Save compliance report
        report_path = Path("test-reports/constitutional-compliance-report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\n🔒 Constitutional Compliance Report: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
