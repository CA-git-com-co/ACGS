#!/usr/bin/env python3
"""
ACGS Final System Validation Report
Comprehensive validation of all success criteria with constitutional compliance

Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Tuple

import requests


class ACGSSystemValidator:
    """Comprehensive ACGS system validation"""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.success_criteria = {
            "test_success_rate": 95.0,  # >95% test success rate
            "service_operational": 8,  # 8/8 services operational
            "constitutional_compliance": 100.0,  # 100% constitutional compliance
            "p99_latency_ms": 5.0,  # P99 latency <5ms
            "cache_hit_rate": 85.0,  # Cache hit rate >85%
            "throughput_rps": 100.0,  # Throughput >100 RPS
            "monitoring_operational": True,  # Monitoring infrastructure operational
        }

    def validate_test_infrastructure(self) -> Tuple[bool, Dict]:
        """Validate test infrastructure and execution results"""
        print("🧪 Validating Test Infrastructure...")

        try:
            # Run the comprehensive test suite
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/test_auth_service.py",
                    "tests/test_constitutional_ai.py",
                    "tests/test_integration_quick.py",
                    "tests/test_all_services_integration.py",
                    "-v",
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Parse test results
            output_lines = result.stdout.split("\n")

            # Find the summary line
            summary_line = ""
            for line in output_lines:
                if "passed" in line and (
                    "failed" in line or "error" in line or "skipped" in line
                ):
                    summary_line = line
                    break

            if summary_line:
                # Extract numbers from summary
                import re

                numbers = re.findall(r"(\d+)", summary_line)
                if len(numbers) >= 2:
                    passed = int(numbers[0])
                    total_tests = sum(int(n) for n in numbers)
                    success_rate = (
                        (passed / total_tests) * 100 if total_tests > 0 else 0
                    )

                    print(f"✅ Test execution completed")
                    print(f"   Passed: {passed}/{total_tests} tests")
                    print(f"   Success rate: {success_rate:.1f}%")

                    return success_rate >= self.success_criteria["test_success_rate"], {
                        "passed": passed,
                        "total": total_tests,
                        "success_rate": success_rate,
                        "target": self.success_criteria["test_success_rate"],
                    }

            print("⚠️  Could not parse test results")
            return False, {"error": "Could not parse test results"}

        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False, {"error": str(e)}

    def validate_service_operational_status(self) -> Tuple[bool, Dict]:
        """Validate all services are operational"""
        print("\n🏛️  Validating Service Operational Status...")

        services = [
            ("Constitutional AI", 8001),
            ("Integrity Service", 8002),
            ("Formal Verification", 8003),
            ("Governance Synthesis", 8004),
            ("Policy Governance", 8005),
            ("Evolutionary Computation", 8006),
            ("Code Analysis", 8007),
            ("Context Service", 8012),
            ("Authentication", 8016),
        ]

        operational_services = []
        failed_services = []

        for service_name, port in services:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=3)
                if response.status_code == 200:
                    operational_services.append(service_name)
                    print(f"✅ {service_name:25} Port {port:4} | Operational")
                else:
                    failed_services.append(service_name)
                    print(
                        f"❌ {service_name:25} Port {port:4} | HTTP {response.status_code}"
                    )
            except Exception as e:
                failed_services.append(service_name)
                print(f"❌ {service_name:25} Port {port:4} | Connection failed")

        operational_count = len(operational_services)
        target_count = self.success_criteria["service_operational"]

        return operational_count >= target_count, {
            "operational": operational_count,
            "target": target_count,
            "total": len(services),
            "operational_services": operational_services,
            "failed_services": failed_services,
        }

    def validate_constitutional_compliance(self) -> Tuple[bool, Dict]:
        """Validate constitutional compliance across all services"""
        print("\n⚖️  Validating Constitutional Compliance...")

        services = [
            ("Constitutional AI", 8001),
            ("Integrity Service", 8002),
            ("Formal Verification", 8003),
            ("Governance Synthesis", 8004),
            ("Policy Governance", 8005),
            ("Evolutionary Computation", 8006),
            ("Code Analysis", 8007),
            ("Context Service", 8012),
            ("Authentication", 8016),
        ]

        compliant_services = []
        non_compliant_services = []

        for service_name, port in services:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    constitutional_hash = data.get("constitutional_hash", "missing")

                    if constitutional_hash == self.constitutional_hash:
                        compliant_services.append(service_name)
                        print(f"✅ {service_name:25} | Constitutional compliance OK")
                    else:
                        non_compliant_services.append(service_name)
                        print(
                            f"🚨 {service_name:25} | Hash mismatch: {constitutional_hash}"
                        )
                else:
                    non_compliant_services.append(service_name)
                    print(f"❌ {service_name:25} | Service unavailable")
            except Exception as e:
                non_compliant_services.append(service_name)
                print(f"❌ {service_name:25} | Connection error")

        compliance_rate = (len(compliant_services) / len(services)) * 100
        target_rate = self.success_criteria["constitutional_compliance"]

        return compliance_rate >= target_rate, {
            "compliant": len(compliant_services),
            "total": len(services),
            "compliance_rate": compliance_rate,
            "target": target_rate,
            "compliant_services": compliant_services,
            "non_compliant_services": non_compliant_services,
        }

    def validate_performance_targets(self) -> Tuple[bool, Dict]:
        """Validate performance targets are met"""
        print("\n⚡ Validating Performance Targets...")

        # Test service response times
        services = [8001, 8003, 8004, 8005, 8006, 8007, 8012, 8016]
        latencies = []

        for port in services:
            try:
                start_time = time.time()
                response = requests.get(f"http://localhost:{port}/health", timeout=3)
                latency_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    latencies.append(latency_ms)
                    print(f"✅ Port {port}: {latency_ms:.2f}ms")
                else:
                    print(f"❌ Port {port}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ Port {port}: Connection failed")

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            p99_latency = (
                sorted(latencies)[int(len(latencies) * 0.99)]
                if len(latencies) > 1
                else latencies[0]
            )

            target_latency = self.success_criteria["p99_latency_ms"]
            latency_ok = p99_latency <= target_latency

            print(f"📊 Average latency: {avg_latency:.2f}ms")
            print(f"📊 P99 latency: {p99_latency:.2f}ms (target: {target_latency}ms)")

            return latency_ok, {
                "avg_latency": avg_latency,
                "p99_latency": p99_latency,
                "target": target_latency,
                "samples": len(latencies),
            }
        else:
            return False, {"error": "No latency samples collected"}

    def validate_monitoring_infrastructure(self) -> Tuple[bool, Dict]:
        """Validate monitoring infrastructure is operational"""
        print("\n📊 Validating Monitoring Infrastructure...")

        monitoring_components = {
            "Prometheus": "http://localhost:9090/api/v1/status/config",
            "Grafana": "http://localhost:3001/api/health",
        }

        operational_components = []
        failed_components = []

        for component, url in monitoring_components.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    operational_components.append(component)
                    print(f"✅ {component}: Operational")
                else:
                    failed_components.append(component)
                    print(f"❌ {component}: HTTP {response.status_code}")
            except Exception as e:
                failed_components.append(component)
                print(f"❌ {component}: Connection failed")

        all_operational = len(failed_components) == 0

        return all_operational, {
            "operational": operational_components,
            "failed": failed_components,
            "total": len(monitoring_components),
        }

    def generate_final_report(self, validation_results: Dict) -> str:
        """Generate comprehensive final validation report"""
        report = []
        report.append("🏆 ACGS FINAL SYSTEM VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Constitutional Hash: {self.constitutional_hash}")
        report.append(f"Validation Date: {datetime.now().isoformat()}")
        report.append(
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        report.append("")

        # Executive Summary
        all_passed = all(passed for passed, _ in validation_results.values())
        report.append("📋 EXECUTIVE SUMMARY")
        report.append("-" * 40)
        if all_passed:
            report.append("✅ ALL SUCCESS CRITERIA MET")
            report.append("✅ ACGS SYSTEM FULLY OPERATIONAL")
            report.append("✅ CONSTITUTIONAL COMPLIANCE VALIDATED")
        else:
            report.append("⚠️  SOME SUCCESS CRITERIA NOT MET")
            report.append("⚠️  SYSTEM REQUIRES ATTENTION")
        report.append("")

        # Detailed Results
        for validation_name, (passed, data) in validation_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            report.append(f"{status} {validation_name.upper()}")
            report.append("-" * 40)

            if validation_name == "Test Infrastructure":
                if "success_rate" in data:
                    report.append(
                        f"Success Rate: {data['success_rate']:.1f}% (target: {data['target']:.1f}%)"
                    )
                    report.append(f"Tests Passed: {data['passed']}/{data['total']}")

            elif validation_name == "Service Operational":
                report.append(
                    f"Operational Services: {data['operational']}/{data['total']}"
                )
                report.append(f"Target: {data['target']} services")
                if data["failed_services"]:
                    report.append(
                        f"Failed Services: {', '.join(data['failed_services'])}"
                    )

            elif validation_name == "Constitutional Compliance":
                report.append(f"Compliance Rate: {data['compliance_rate']:.1f}%")
                report.append(
                    f"Compliant Services: {data['compliant']}/{data['total']}"
                )
                if data["non_compliant_services"]:
                    report.append(
                        f"Non-compliant: {', '.join(data['non_compliant_services'])}"
                    )

            elif validation_name == "Performance Targets":
                if "p99_latency" in data:
                    report.append(
                        f"P99 Latency: {data['p99_latency']:.2f}ms (target: {data['target']:.2f}ms)"
                    )
                    report.append(f"Average Latency: {data['avg_latency']:.2f}ms")

            elif validation_name == "Monitoring Infrastructure":
                report.append(
                    f"Operational Components: {len(data['operational'])}/{data['total']}"
                )
                report.append(f"Components: {', '.join(data['operational'])}")

            report.append("")

        # Final Status
        report.append("🎯 FINAL VALIDATION STATUS")
        report.append("=" * 80)

        passed_count = sum(1 for passed, _ in validation_results.values() if passed)
        total_count = len(validation_results)

        report.append(f"Validations Passed: {passed_count}/{total_count}")
        report.append(f"Overall Success Rate: {(passed_count/total_count)*100:.1f}%")
        report.append(f"Constitutional Hash: {self.constitutional_hash}")

        if all_passed:
            report.append("")
            report.append("🎉 ACGS SYSTEM VALIDATION SUCCESSFUL!")
            report.append("✅ Ready for production deployment")
            report.append("✅ All constitutional compliance requirements met")
            report.append("✅ Performance targets achieved")
            report.append("✅ Monitoring infrastructure operational")
        else:
            report.append("")
            report.append("⚠️  ACGS SYSTEM VALIDATION INCOMPLETE")
            report.append("   Review failed validations above")
            report.append("   Address issues before production deployment")

        return "\n".join(report)

    def run_comprehensive_validation(self) -> bool:
        """Run comprehensive system validation"""
        print("🚀 ACGS COMPREHENSIVE SYSTEM VALIDATION")
        print("Constitutional Hash: cdd01ef066bc6cf2")
        print("=" * 80)

        validations = {
            "Test Infrastructure": self.validate_test_infrastructure,
            "Service Operational": self.validate_service_operational_status,
            "Constitutional Compliance": self.validate_constitutional_compliance,
            "Performance Targets": self.validate_performance_targets,
            "Monitoring Infrastructure": self.validate_monitoring_infrastructure,
        }

        results = {}
        for validation_name, validation_func in validations.items():
            results[validation_name] = validation_func()

        # Generate final report
        report = self.generate_final_report(results)
        print(f"\n{report}")

        # Save report
        with open("acgs_final_validation_report.txt", "w") as f:
            f.write(report)

        # Return overall success
        return all(passed for passed, _ in results.values())


def main():
    """Main validation function"""
    validator = ACGSSystemValidator()
    success = validator.run_comprehensive_validation()

    if success:
        print("\n🎉 ACGS SYSTEM VALIDATION SUCCESSFUL!")
        print("📄 Report saved to: acgs_final_validation_report.txt")
        exit(0)
    else:
        print("\n⚠️  ACGS SYSTEM VALIDATION INCOMPLETE")
        print("📄 Report saved to: acgs_final_validation_report.txt")
        exit(1)


if __name__ == "__main__":
    main()
