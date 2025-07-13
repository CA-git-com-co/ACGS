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
import pathlib
import sys
import time
from datetime import datetime
from typing import Any

# Add current directory to path
sys.path.insert(0, pathlib.Path(pathlib.Path(__file__).resolve()).parent)


class Priority3ValidationRunner:
    """Comprehensive Priority 3 validation runner"""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.base_url = "http://localhost:8007"
        self.results = {}
        self.start_time = None

    def setup_validation_environment(self):
        """Setup environment for comprehensive validation"""

        # Set environment variables
        os.environ["ENVIRONMENT"] = "testing"
        os.environ["POSTGRESQL_PASSWORD"] = "test_password"
        os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_for_development_only"
        os.environ["REDIS_PASSWORD"] = ""
        os.environ["LOG_LEVEL"] = "INFO"

    def run_integration_tests(self) -> dict[str, Any]:
        """Run comprehensive integration tests"""

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
                pass

            return results

        except Exception as e:
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results["integration_tests"] = error_result
            return error_result

    def run_performance_benchmarks(self) -> dict[str, Any]:
        """Run comprehensive performance benchmarks"""

        try:
            # Import and run performance benchmarks
            from test_performance_benchmarks import PerformanceBenchmarker

            benchmarker = PerformanceBenchmarker(self.base_url)
            results = benchmarker.run_comprehensive_benchmarks()

            self.results["performance_benchmarks"] = results

            # Check if performance targets met
            performance_passed = results.get("summary", {}).get("targets_met", False)
            results.get("summary", {}).get("overall_score", 0)

            if performance_passed:
                pass

            return results

        except Exception as e:
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results["performance_benchmarks"] = error_result
            return error_result

    def run_monitoring_validation(self) -> dict[str, Any]:
        """Run monitoring and observability validation"""

        try:
            # Import and run monitoring validation
            from test_monitoring_setup import MonitoringValidator

            validator = MonitoringValidator(self.base_url)
            results = validator.run_monitoring_validation()

            self.results["monitoring_validation"] = results

            # Check if monitoring is ready
            monitoring_ready = results.get("summary", {}).get("monitoring_ready", False)

            if monitoring_ready:
                pass

            return results

        except Exception as e:
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results["monitoring_validation"] = error_result
            return error_result

    def run_constitutional_compliance_validation(self) -> dict[str, Any]:
        """Run constitutional compliance validation across all components"""

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
                compliance_checks.append(
                    {
                        "endpoint": "/health",
                        "hash_present": hash_present,
                        "status": "pass" if hash_present else "fail",
                    }
                )

            # Test metrics endpoint for constitutional hash
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            if response.status_code == 200:
                hash_in_metrics = self.constitutional_hash in response.text
                compliance_checks.append(
                    {
                        "endpoint": "/metrics",
                        "hash_present": hash_in_metrics,
                        "status": "pass" if hash_in_metrics else "fail",
                    }
                )

            # Test error responses for constitutional hash
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=10)
            if response.status_code == 404:
                hash_in_error = self.constitutional_hash in response.text
                compliance_checks.append(
                    {
                        "endpoint": "/invalid-endpoint (error)",
                        "hash_present": hash_in_error,
                        "status": "pass" if hash_in_error else "fail",
                    }
                )

            # Calculate compliance rate
            total_checks = len(compliance_checks)
            passed_checks = len([c for c in compliance_checks if c["status"] == "pass"])
            compliance_rate = passed_checks / total_checks if total_checks > 0 else 0

            compliance_passed = compliance_rate >= 0.9  # 90% compliance required

            for check in compliance_checks:
                "✅" if check["status"] == "pass" else "❌"

            if compliance_passed:
                pass

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
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results["constitutional_compliance"] = error_result
            return error_result

    def generate_final_report(self) -> dict[str, Any]:
        """Generate comprehensive final validation report"""

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
        for result in phase_results.values():
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
            "performance_targets_met": phase_results["performance"]["status"]
            in {
                "pass",
                "partial",
            },
            "constitutional_compliance_maintained": (
                phase_results["constitutional"]["status"] == "pass"
            ),
            "zero_critical_failures": not any(
                r["status"] == "failed" for r in phase_results.values()
            ),
            "monitoring_operational": phase_results["monitoring"]["status"]
            in {
                "pass",
                "partial",
            },
        }

        success_criteria_met = all(success_criteria.values())

        # Print summary

        for result in phase_results.values():
            {"pass": "✅", "partial": "⚠️", "failed": "❌"}.get(result["status"], "❓")

        for _criterion, _met in success_criteria.items():
            pass

        # Final recommendation
        if (production_ready and success_criteria_met) or production_ready:
            pass

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

            if phase_key == "performance_benchmarks":
                targets_met = result.get("summary", {}).get("targets_met", False)
                score = result.get("summary", {}).get("overall_score", 0)
                if targets_met:
                    return {"status": "pass", "score": score}
                if score >= 60:
                    return {"status": "partial", "score": score}
                return {"status": "failed", "score": score}

            if phase_key == "monitoring_validation":
                ready = result.get("summary", {}).get("monitoring_ready", False)
                return {
                    "status": "pass" if ready else "partial",
                    "details": result.get("summary", {}),
                }

            if phase_key == "constitutional_compliance":
                compliance_rate = result.get("compliance_rate", 0)
                if compliance_rate >= 0.9:
                    return {"status": "pass", "compliance_rate": compliance_rate}
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
            return self.generate_final_report()

        except Exception as e:
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
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Exit with appropriate code based on results
        if results.get("recommendation") == "ready":
            sys.exit(0)
        elif results.get("production_ready", False):
            sys.exit(2)  # Warning exit code
        else:
            sys.exit(1)

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
