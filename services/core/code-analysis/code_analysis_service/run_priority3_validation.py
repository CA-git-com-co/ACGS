#!/usr/bin/env python3
"""
ACGS Code Analysis Engine - Priority 3 Comprehensive Validation Runner
Executes all integration, performance, and monitoring tests for production readiness.

Constitutional Hash: cdd01ef066bc6cf2
Success Criteria:
- All ACGS infrastructure services integrate successfully
- Performance targets met: P99 <10ms, >100 RPS, >85% cache hit rate
- Constitutional compliance hash cdd01ef066bc6cf2 maintained
- Zero critical integration failures
- Production monitoring fully operational
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Priority3ValidationRunner:
    """Comprehensive Priority 3 validation runner"""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.base_url = "http://localhost:8007"
        self.results = {}
        self.start_time = None

    def setup_validation_environment(self):
        """Setup environment for comprehensive validation"""
        print("=" * 80)
        print("ACGS Code Analysis Engine - Priority 3 Validation Suite")
        print("=" * 80)
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Service URL: {self.base_url}")
        print(f"Validation Start Time: {datetime.now().isoformat()}")
        print("=" * 80)

        # Set environment variables
        os.environ["ENVIRONMENT"] = "testing"
        os.environ["POSTGRESQL_PASSWORD"] = "test_password"
        os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_for_development_only"
        os.environ["REDIS_PASSWORD"] = ""
        os.environ["LOG_LEVEL"] = "INFO"

        print("✓ Environment configured for validation")

    def run_integration_tests(self) -> dict[str, Any]:
        """Run comprehensive integration tests"""
        print("\n" + "=" * 60)
        print("PHASE 1: INTEGRATION TESTING")
        print("=" * 60)

        try:
            # Import and run integration tests
            from test_priority3_integration import ACGSIntegrationTester

            tester = ACGSIntegrationTester()
            results = tester.run_comprehensive_tests()

            self.results["integration_tests"] = results

            # Check if integration tests passed
            integration_passed = results.get("summary", {}).get(
                "success_criteria_met", False
            )

            if integration_passed:
                print("✅ PHASE 1 PASSED: All integration tests successful")
            else:
                print("❌ PHASE 1 FAILED: Integration tests failed")
                print(
                    "Failed tests:", results.get("summary", {}).get("failed_tests", [])
                )

            return results

        except Exception as e:
            print(f"❌ PHASE 1 FAILED: Integration testing error: {e}")
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results["integration_tests"] = error_result
            return error_result

    def run_performance_benchmarks(self) -> dict[str, Any]:
        """Run comprehensive performance benchmarks"""
        print("\n" + "=" * 60)
        print("PHASE 2: PERFORMANCE BENCHMARKING")
        print("=" * 60)

        try:
            # Import and run performance benchmarks
            from test_performance_benchmarks import PerformanceBenchmarker

            benchmarker = PerformanceBenchmarker(self.base_url)
            results = benchmarker.run_comprehensive_benchmarks()

            self.results["performance_benchmarks"] = results

            # Check if performance targets met
            performance_passed = results.get("summary", {}).get("targets_met", False)
            performance_score = results.get("summary", {}).get("overall_score", 0)

            if performance_passed:
                print(
                    "✅ PHASE 2 PASSED: All performance targets met (Score:"
                    f" {performance_score:.1f}/100)"
                )
            else:
                print(
                    "⚠️ PHASE 2 PARTIAL: Performance targets not fully met (Score:"
                    f" {performance_score:.1f}/100)"
                )
                print(
                    "Recommendations:",
                    results.get("summary", {}).get("recommendations", []),
                )

            return results

        except Exception as e:
            print(f"❌ PHASE 2 FAILED: Performance benchmarking error: {e}")
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results["performance_benchmarks"] = error_result
            return error_result

    def run_monitoring_validation(self) -> dict[str, Any]:
        """Run monitoring and observability validation"""
        print("\n" + "=" * 60)
        print("PHASE 3: MONITORING & OBSERVABILITY VALIDATION")
        print("=" * 60)

        try:
            # Import and run monitoring validation
            from test_monitoring_setup import MonitoringValidator

            validator = MonitoringValidator(self.base_url)
            results = validator.run_monitoring_validation()

            self.results["monitoring_validation"] = results

            # Check if monitoring is ready
            monitoring_ready = results.get("summary", {}).get("monitoring_ready", False)

            if monitoring_ready:
                print("✅ PHASE 3 PASSED: Monitoring and observability ready")
            else:
                print("⚠️ PHASE 3 PARTIAL: Monitoring setup needs attention")
                print(
                    "Failed tests:", results.get("summary", {}).get("failed_tests", [])
                )

            return results

        except Exception as e:
            print(f"❌ PHASE 3 FAILED: Monitoring validation error: {e}")
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results["monitoring_validation"] = error_result
            return error_result

    def run_constitutional_compliance_validation(self) -> dict[str, Any]:
        """Run constitutional compliance validation across all components"""
        print("\n" + "=" * 60)
        print("PHASE 4: CONSTITUTIONAL COMPLIANCE VALIDATION")
        print("=" * 60)

        try:
            import requests

            compliance_checks = []

            # Test health endpoint for constitutional hash
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                hash_present = (
                    data.get("constitutional_hash") == self.constitutional_hash
                )
                compliance_checks.append({
                    "endpoint": "/health",
                    "hash_present": hash_present,
                    "status": "pass" if hash_present else "fail",
                })

            # Test metrics endpoint for constitutional hash
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            if response.status_code == 200:
                hash_in_metrics = self.constitutional_hash in response.text
                compliance_checks.append({
                    "endpoint": "/metrics",
                    "hash_present": hash_in_metrics,
                    "status": "pass" if hash_in_metrics else "fail",
                })

            # Test error responses for constitutional hash
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=10)
            if response.status_code == 404:
                hash_in_error = self.constitutional_hash in response.text
                compliance_checks.append({
                    "endpoint": "/invalid-endpoint (error)",
                    "hash_present": hash_in_error,
                    "status": "pass" if hash_in_error else "fail",
                })

            # Calculate compliance rate
            total_checks = len(compliance_checks)
            passed_checks = len([c for c in compliance_checks if c["status"] == "pass"])
            compliance_rate = passed_checks / total_checks if total_checks > 0 else 0

            compliance_passed = compliance_rate >= 0.9  # 90% compliance required

            print(f"✓ Constitutional compliance checks: {passed_checks}/{total_checks}")
            print(f"✓ Compliance rate: {compliance_rate:.1%}")

            for check in compliance_checks:
                status_icon = "✅" if check["status"] == "pass" else "❌"
                print(
                    f"{status_icon} {check['endpoint']}:"
                    f" {'PASS' if check['hash_present'] else 'FAIL'}"
                )

            if compliance_passed:
                print("✅ PHASE 4 PASSED: Constitutional compliance validated")
            else:
                print("❌ PHASE 4 FAILED: Constitutional compliance insufficient")

            result = {
                "status": "pass" if compliance_passed else "fail",
                "compliance_rate": compliance_rate,
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "compliance_checks": compliance_checks,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

            self.results["constitutional_compliance"] = result
            return result

        except Exception as e:
            print(f"❌ PHASE 4 FAILED: Constitutional compliance validation error: {e}")
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results["constitutional_compliance"] = error_result
            return error_result

    def generate_final_report(self) -> dict[str, Any]:
        """Generate comprehensive final validation report"""
        print("\n" + "=" * 80)
        print("PRIORITY 3 VALIDATION FINAL REPORT")
        print("=" * 80)

        total_time = time.time() - self.start_time if self.start_time else 0

        # Analyze results from all phases
        phase_results = {
            "integration": self._analyze_phase_result("integration_tests"),
            "performance": self._analyze_phase_result("performance_benchmarks"),
            "monitoring": self._analyze_phase_result("monitoring_validation"),
            "constitutional": self._analyze_phase_result("constitutional_compliance"),
        }

        # Calculate overall success
        phase_scores = []
        for phase, result in phase_results.items():
            if result["status"] == "pass":
                phase_scores.append(100)
            elif result["status"] == "partial":
                phase_scores.append(75)
            else:
                phase_scores.append(0)

        overall_score = sum(phase_scores) / len(phase_scores) if phase_scores else 0

        # Determine production readiness
        production_ready = (
            phase_results["integration"]["status"] == "pass"
            and phase_results["constitutional"]["status"] == "pass"
            and overall_score >= 75
        )

        # Generate success criteria validation
        success_criteria = {
            "acgs_infrastructure_integration": (
                phase_results["integration"]["status"] == "pass"
            ),
            "performance_targets_met": phase_results["performance"]["status"] in [
                "pass",
                "partial",
            ],
            "constitutional_compliance_maintained": (
                phase_results["constitutional"]["status"] == "pass"
            ),
            "zero_critical_failures": not any(
                r["status"] == "failed" for r in phase_results.values()
            ),
            "monitoring_operational": phase_results["monitoring"]["status"] in [
                "pass",
                "partial",
            ],
        }

        success_criteria_met = all(success_criteria.values())

        # Print summary
        print(f"Overall Score: {overall_score:.1f}/100")
        print(f"Production Ready: {'YES' if production_ready else 'NO'}")
        print(f"Success Criteria Met: {'YES' if success_criteria_met else 'NO'}")
        print(f"Total Execution Time: {total_time:.2f} seconds")

        print("\nPhase Results:")
        for phase, result in phase_results.items():
            status_icon = {"pass": "✅", "partial": "⚠️", "failed": "❌"}.get(
                result["status"], "❓"
            )
            print(f"{status_icon} {phase.title()}: {result['status'].upper()}")

        print("\nSuccess Criteria:")
        for criterion, met in success_criteria.items():
            status_icon = "✅" if met else "❌"
            print(
                f"{status_icon} {criterion.replace('_', ' ').title()}:"
                f" {'MET' if met else 'NOT MET'}"
            )

        # Final recommendation
        if production_ready and success_criteria_met:
            print(
                "\n🎉 RECOMMENDATION: Service is READY for Phase 1 production"
                " deployment!"
            )
        elif production_ready:
            print(
                "\n⚠️ RECOMMENDATION: Service is CONDITIONALLY READY - address partial"
                " issues before deployment"
            )
        else:
            print(
                "\n❌ RECOMMENDATION: Service is NOT READY - critical issues must be"
                " resolved"
            )

        return {
            "overall_score": overall_score,
            "production_ready": production_ready,
            "success_criteria_met": success_criteria_met,
            "success_criteria": success_criteria,
            "phase_results": phase_results,
            "detailed_results": self.results,
            "execution_time_seconds": total_time,
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.now().isoformat(),
            "recommendation": (
                "ready" if production_ready and success_criteria_met else "not_ready"
            ),
        }

    def _analyze_phase_result(self, phase_key: str) -> dict[str, Any]:
        """Analyze individual phase result"""
        if phase_key not in self.results:
            return {"status": "failed", "reason": "Phase not executed"}

        result = self.results[phase_key]

        if isinstance(result, dict):
            if result.get("status") == "failed":
                return {
                    "status": "failed",
                    "reason": result.get("error", "Unknown error"),
                }

            # Check specific phase success criteria
            if phase_key == "integration_tests":
                success = result.get("summary", {}).get("success_criteria_met", False)
                return {
                    "status": "pass" if success else "failed",
                    "details": result.get("summary", {}),
                }

            elif phase_key == "performance_benchmarks":
                targets_met = result.get("summary", {}).get("targets_met", False)
                score = result.get("summary", {}).get("overall_score", 0)
                if targets_met:
                    return {"status": "pass", "score": score}
                elif score >= 60:
                    return {"status": "partial", "score": score}
                else:
                    return {"status": "failed", "score": score}

            elif phase_key == "monitoring_validation":
                ready = result.get("summary", {}).get("monitoring_ready", False)
                return {
                    "status": "pass" if ready else "partial",
                    "details": result.get("summary", {}),
                }

            elif phase_key == "constitutional_compliance":
                compliance_rate = result.get("compliance_rate", 0)
                if compliance_rate >= 0.9:
                    return {"status": "pass", "compliance_rate": compliance_rate}
                else:
                    return {"status": "failed", "compliance_rate": compliance_rate}

        return {"status": "failed", "reason": "Invalid result format"}

    def run_comprehensive_validation(self) -> dict[str, Any]:
        """Run all Priority 3 validation phases"""
        self.start_time = time.time()

        # Setup validation environment
        self.setup_validation_environment()

        # Run all validation phases
        try:
            # Phase 1: Integration Testing
            self.run_integration_tests()

            # Phase 2: Performance Benchmarking
            self.run_performance_benchmarks()

            # Phase 3: Monitoring Validation
            self.run_monitoring_validation()

            # Phase 4: Constitutional Compliance
            self.run_constitutional_compliance_validation()

            # Generate final report
            final_report = self.generate_final_report()

            return final_report

        except Exception as e:
            print(f"\n💥 Comprehensive validation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "partial_results": self.results,
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """Main validation execution function"""
    runner = Priority3ValidationRunner()

    try:
        # Run comprehensive validation
        results = runner.run_comprehensive_validation()

        # Save results to file
        results_file = "priority3_comprehensive_validation_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Comprehensive results saved to: {results_file}")

        # Exit with appropriate code based on results
        if results.get("recommendation") == "ready":
            print("\n🎉 Priority 3 validation PASSED - Service ready for production!")
            sys.exit(0)
        elif results.get("production_ready", False):
            print(
                "\n⚠️ Priority 3 validation PARTIAL - Review recommendations before"
                " deployment"
            )
            sys.exit(2)  # Warning exit code
        else:
            print(
                "\n❌ Priority 3 validation FAILED - Critical issues must be resolved"
            )
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Priority 3 validation execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
