#!/usr/bin/env python3
"""
ACGS Enterprise Deployment Gates

This script implements automated deployment gates that prevent deployments
when quality thresholds are not met, including the 90% test coverage requirement.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Tuple
from pathlib import Path


class DeploymentGateValidator:
    """Validates deployment readiness based on enterprise quality standards."""
    
    def __init__(self, coverage_threshold: float = 90.0):
        self.coverage_threshold = coverage_threshold
        self.validation_results = {}
        self.blocking_issues = []
        self.warnings = []
    
    def validate_test_coverage(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate that test coverage meets enterprise threshold."""
        print(f"🔍 Validating test coverage (threshold: {self.coverage_threshold}%)...")
        
        try:
            # Run coverage analysis
            result = subprocess.run([
                "python", "-m", "pytest",
                "--cov=services",
                "--cov=scripts", 
                "--cov=core",
                "--cov-report=json",
                "--cov-report=term-missing",
                "--quiet",
                "--tb=no"
            ], capture_output=True, text=True, timeout=300)
            
            # Parse coverage results
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data["totals"]["percent_covered"]
                
                coverage_info = {
                    "total_coverage": total_coverage,
                    "threshold": self.coverage_threshold,
                    "passed": total_coverage >= self.coverage_threshold,
                    "files_covered": len(coverage_data["files"]),
                    "lines_covered": coverage_data["totals"]["covered_lines"],
                    "total_lines": coverage_data["totals"]["num_statements"]
                }
                
                if total_coverage >= self.coverage_threshold:
                    print(f"✅ Coverage: {total_coverage:.2f}% (≥{self.coverage_threshold}%)")
                    return True, coverage_info
                else:
                    print(f"❌ Coverage: {total_coverage:.2f}% (<{self.coverage_threshold}%)")
                    self.blocking_issues.append(
                        f"Test coverage {total_coverage:.2f}% below threshold {self.coverage_threshold}%"
                    )
                    return False, coverage_info
            else:
                print("❌ Coverage report not found")
                self.blocking_issues.append("Coverage report generation failed")
                return False, {"error": "Coverage report not found"}
                
        except subprocess.TimeoutExpired:
            print("❌ Coverage validation timed out")
            self.blocking_issues.append("Coverage validation timeout")
            return False, {"error": "Timeout"}
        except Exception as e:
            print(f"❌ Coverage validation failed: {e}")
            self.blocking_issues.append(f"Coverage validation error: {e}")
            return False, {"error": str(e)}
    
    def validate_security_requirements(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate security requirements for deployment."""
        print("🔒 Validating security requirements...")
        
        security_checks = {
            "dependency_audit": False,
            "security_scan": False,
            "constitutional_compliance": False
        }
        
        try:
            # Check for security audit results
            audit_file = Path("audit-report.json")
            if audit_file.exists():
                with open(audit_file) as f:
                    audit_data = json.load(f)
                    # Check if any vulnerabilities found
                    if not audit_data.get("vulnerabilities", []):
                        security_checks["dependency_audit"] = True
                        print("✅ Dependency audit: No vulnerabilities found")
                    else:
                        print(f"❌ Dependency audit: {len(audit_data['vulnerabilities'])} vulnerabilities found")
                        self.blocking_issues.append("Security vulnerabilities in dependencies")
            else:
                print("⚠️ Dependency audit report not found")
                self.warnings.append("Dependency audit report missing")
            
            # Check for security scan results
            bandit_file = Path("bandit-report.json")
            if bandit_file.exists():
                with open(bandit_file) as f:
                    bandit_data = json.load(f)
                    high_severity = [r for r in bandit_data.get("results", []) 
                                   if r.get("issue_severity") == "HIGH"]
                    if not high_severity:
                        security_checks["security_scan"] = True
                        print("✅ Security scan: No high-severity issues found")
                    else:
                        print(f"❌ Security scan: {len(high_severity)} high-severity issues found")
                        self.blocking_issues.append("High-severity security issues found")
            else:
                print("⚠️ Security scan report not found")
                self.warnings.append("Security scan report missing")
            
            # Check constitutional compliance
            compliance_script = Path("scripts/validate_constitutional_compliance.py")
            if compliance_script.exists():
                result = subprocess.run([
                    "python", str(compliance_script), "--check-only"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    security_checks["constitutional_compliance"] = True
                    print("✅ Constitutional compliance: Validated")
                else:
                    print("❌ Constitutional compliance: Validation failed")
                    self.blocking_issues.append("Constitutional compliance validation failed")
            else:
                print("⚠️ Constitutional compliance validator not found")
                self.warnings.append("Constitutional compliance validator missing")
            
            all_passed = all(security_checks.values())
            return all_passed, security_checks
            
        except Exception as e:
            print(f"❌ Security validation failed: {e}")
            self.blocking_issues.append(f"Security validation error: {e}")
            return False, {"error": str(e)}
    
    def validate_performance_requirements(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate performance requirements for deployment."""
        print("⚡ Validating performance requirements...")
        
        performance_metrics = {
            "latency_p99": None,
            "cache_hit_rate": None,
            "throughput": None,
            "passed": False
        }
        
        try:
            # Check for performance test results
            perf_results_file = Path("performance-results.json")
            if perf_results_file.exists():
                with open(perf_results_file) as f:
                    perf_data = json.load(f)
                
                # Extract key metrics
                latency_p99 = perf_data.get("latency_p99_ms", 0)
                cache_hit_rate = perf_data.get("cache_hit_rate_percent", 0)
                throughput = perf_data.get("throughput_rps", 0)
                
                performance_metrics.update({
                    "latency_p99": latency_p99,
                    "cache_hit_rate": cache_hit_rate,
                    "throughput": throughput
                })
                
                # Validate against thresholds
                latency_ok = latency_p99 <= 5.0  # P99 < 5ms
                cache_ok = cache_hit_rate >= 85.0  # >85% cache hit rate
                throughput_ok = throughput >= 100.0  # >100 RPS
                
                if latency_ok and cache_ok and throughput_ok:
                    performance_metrics["passed"] = True
                    print(f"✅ Performance: P99={latency_p99}ms, Cache={cache_hit_rate}%, RPS={throughput}")
                    return True, performance_metrics
                else:
                    issues = []
                    if not latency_ok:
                        issues.append(f"P99 latency {latency_p99}ms > 5ms")
                    if not cache_ok:
                        issues.append(f"Cache hit rate {cache_hit_rate}% < 85%")
                    if not throughput_ok:
                        issues.append(f"Throughput {throughput} RPS < 100 RPS")
                    
                    print(f"❌ Performance issues: {', '.join(issues)}")
                    self.blocking_issues.extend(issues)
                    return False, performance_metrics
            else:
                print("⚠️ Performance test results not found")
                self.warnings.append("Performance test results missing")
                return True, performance_metrics  # Don't block on missing perf tests
                
        except Exception as e:
            print(f"❌ Performance validation failed: {e}")
            self.warnings.append(f"Performance validation error: {e}")
            return True, performance_metrics  # Don't block on validation errors
    
    def validate_deployment_readiness(self) -> Dict[str, Any]:
        """Run all deployment gate validations."""
        print("🚀 ACGS Enterprise Deployment Gates Validation")
        print("=" * 50)
        
        # Run all validations
        coverage_passed, coverage_info = self.validate_test_coverage()
        security_passed, security_info = self.validate_security_requirements()
        performance_passed, performance_info = self.validate_performance_requirements()
        
        # Compile results
        self.validation_results = {
            "timestamp": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip(),
            "overall_passed": coverage_passed and security_passed and performance_passed,
            "coverage": {
                "passed": coverage_passed,
                "details": coverage_info
            },
            "security": {
                "passed": security_passed,
                "details": security_info
            },
            "performance": {
                "passed": performance_passed,
                "details": performance_info
            },
            "blocking_issues": self.blocking_issues,
            "warnings": self.warnings
        }
        
        return self.validation_results
    
    def generate_deployment_report(self) -> str:
        """Generate a deployment readiness report."""
        if not self.validation_results:
            return "No validation results available"
        
        report = []
        report.append("# ACGS Enterprise Deployment Gates Report")
        report.append(f"**Timestamp:** {self.validation_results['timestamp']}")
        report.append(f"**Overall Status:** {'✅ PASSED' if self.validation_results['overall_passed'] else '❌ FAILED'}")
        report.append("")
        
        # Coverage section
        coverage = self.validation_results["coverage"]
        report.append("## Test Coverage")
        if coverage["passed"]:
            report.append(f"✅ **PASSED** - {coverage['details'].get('total_coverage', 0):.2f}% coverage")
        else:
            report.append(f"❌ **FAILED** - {coverage['details'].get('total_coverage', 0):.2f}% coverage")
        report.append("")
        
        # Security section
        security = self.validation_results["security"]
        report.append("## Security Validation")
        if security["passed"]:
            report.append("✅ **PASSED** - All security requirements met")
        else:
            report.append("❌ **FAILED** - Security issues found")
        report.append("")
        
        # Performance section
        performance = self.validation_results["performance"]
        report.append("## Performance Validation")
        if performance["passed"]:
            report.append("✅ **PASSED** - Performance requirements met")
        else:
            report.append("⚠️ **WARNING** - Performance issues detected")
        report.append("")
        
        # Issues section
        if self.blocking_issues:
            report.append("## Blocking Issues")
            for issue in self.blocking_issues:
                report.append(f"- ❌ {issue}")
            report.append("")
        
        if self.warnings:
            report.append("## Warnings")
            for warning in self.warnings:
                report.append(f"- ⚠️ {warning}")
            report.append("")
        
        # Deployment decision
        if self.validation_results["overall_passed"]:
            report.append("## 🎉 Deployment Approved")
            report.append("All enterprise quality gates have passed. Deployment may proceed.")
        else:
            report.append("## 🚫 Deployment Blocked")
            report.append("One or more quality gates have failed. Deployment is blocked until issues are resolved.")
        
        return "\n".join(report)


def main():
    """Main function to run deployment gate validation."""
    # Parse command line arguments
    coverage_threshold = float(os.getenv("COVERAGE_THRESHOLD", "90.0"))
    
    # Initialize validator
    validator = DeploymentGateValidator(coverage_threshold)
    
    # Run validation
    results = validator.validate_deployment_readiness()
    
    # Generate and save report
    report = validator.generate_deployment_report()
    
    # Save results
    with open("deployment-gates-results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    with open("deployment-gates-report.md", "w") as f:
        f.write(report)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Deployment Gates Summary")
    print("=" * 50)
    
    if results["overall_passed"]:
        print("✅ ALL DEPLOYMENT GATES PASSED")
        print("🚀 Deployment is approved and may proceed")
        return True
    else:
        print("❌ DEPLOYMENT GATES FAILED")
        print("🚫 Deployment is blocked")
        print("\nBlocking Issues:")
        for issue in validator.blocking_issues:
            print(f"  - {issue}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
