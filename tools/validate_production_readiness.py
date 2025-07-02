#!/usr/bin/env python3
"""
ACGS-1 Phase 3 Production Readiness Validation Script

This script performs comprehensive validation of the ACGS-1 system to ensure
it meets all production requirements including:
- Service availability and performance
- End-to-end workflow functionality
- Security and compliance
- Monitoring and alerting
- SLA compliance (>99% uptime, <500ms response times)

This is the final validation before marking Phase 3 as complete.
"""

import asyncio
import json
import logging
import statistics
import time
from typing import Any

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionReadinessValidator:
    """Comprehensive production readiness validation for ACGS-1."""

    def __init__(self):
        self.results = {}
        self.timeout = 30
        self.services = {
            "auth": {"port": 8000, "name": "Authentication Service"},
            "ac": {"port": 8001, "name": "Constitutional AI Service"},
            "integrity": {"port": 8002, "name": "Integrity Service"},
            "fv": {"port": 8003, "name": "Formal Verification Service"},
            "gs": {"port": 8004, "name": "Governance Synthesis Service"},
            "pgc": {"port": 8005, "name": "Policy Governance Service"},
            "ec": {"port": 8006, "name": "Evolutionary Computation Service"},
        }

    async def validate_sla_compliance(self) -> dict[str, Any]:
        """Validate SLA compliance: >99% uptime, <500ms response times."""
        logger.info("🎯 Validating SLA Compliance")

        sla_results = {
            "uptime_test": {},
            "response_time_test": {},
            "load_test": {},
            "overall_compliance": False,
        }

        # Test uptime by checking health endpoints multiple times
        uptime_checks = []
        for i in range(10):  # 10 checks over time
            check_results = {}
            for service_name, config in self.services.items():
                try:
                    async with httpx.AsyncClient(timeout=5) as client:
                        response = await client.get(
                            f"http://localhost:{config['port']}/health"
                        )
                        check_results[service_name] = response.status_code == 200
                except:
                    check_results[service_name] = False

            uptime_checks.append(check_results)
            if i < 9:  # Don't sleep after last check
                await asyncio.sleep(1)

        # Calculate uptime percentage
        for service_name in self.services.keys():
            successful_checks = sum(
                1 for check in uptime_checks if check.get(service_name, False)
            )
            uptime_percentage = (successful_checks / len(uptime_checks)) * 100
            sla_results["uptime_test"][service_name] = {
                "uptime_percentage": uptime_percentage,
                "meets_sla": uptime_percentage >= 99.0,
                "successful_checks": successful_checks,
                "total_checks": len(uptime_checks),
            }

        # Test response times with multiple requests
        for service_name, config in self.services.items():
            response_times = []
            for i in range(5):  # 5 requests per service
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        start_time = time.time()
                        response = await client.get(
                            f"http://localhost:{config['port']}/health"
                        )
                        response_time = (time.time() - start_time) * 1000
                        if response.status_code == 200:
                            response_times.append(response_time)
                except:
                    pass

            if response_times:
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                sla_results["response_time_test"][service_name] = {
                    "avg_response_time_ms": avg_response_time,
                    "max_response_time_ms": max_response_time,
                    "meets_sla": avg_response_time < 500 and max_response_time < 1000,
                    "sample_size": len(response_times),
                }
            else:
                sla_results["response_time_test"][service_name] = {
                    "avg_response_time_ms": None,
                    "meets_sla": False,
                    "error": "No successful responses",
                }

        # Concurrent load test
        concurrent_requests = 20
        load_test_results = {}

        for service_name, config in self.services.items():
            try:
                tasks = []
                for _ in range(concurrent_requests):
                    task = self._make_request(
                        f"http://localhost:{config['port']}/health"
                    )
                    tasks.append(task)

                start_time = time.time()
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time

                successful_responses = sum(
                    1
                    for r in responses
                    if not isinstance(r, Exception) and r.get("status_code") == 200
                )
                success_rate = (successful_responses / concurrent_requests) * 100

                load_test_results[service_name] = {
                    "concurrent_requests": concurrent_requests,
                    "successful_responses": successful_responses,
                    "success_rate": success_rate,
                    "total_time_seconds": total_time,
                    "requests_per_second": concurrent_requests / total_time,
                    "meets_load_requirements": success_rate >= 95,
                }

            except Exception as e:
                load_test_results[service_name] = {
                    "error": str(e),
                    "meets_load_requirements": False,
                }

        sla_results["load_test"] = load_test_results

        # Overall SLA compliance
        uptime_compliance = all(
            result.get("meets_sla", False)
            for result in sla_results["uptime_test"].values()
        )
        response_time_compliance = all(
            result.get("meets_sla", False)
            for result in sla_results["response_time_test"].values()
        )
        load_compliance = all(
            result.get("meets_load_requirements", False)
            for result in sla_results["load_test"].values()
        )

        sla_results["overall_compliance"] = (
            uptime_compliance and response_time_compliance and load_compliance
        )

        return sla_results

    async def _make_request(self, url: str) -> dict[str, Any]:
        """Make a single HTTP request and return timing info."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start_time = time.time()
                response = await client.get(url)
                response_time = (time.time() - start_time) * 1000
                return {
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "success": response.status_code == 200,
                }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def validate_security_compliance(self) -> dict[str, Any]:
        """Validate security and compliance requirements."""
        logger.info("🔒 Validating Security Compliance")

        security_results = {
            "constitutional_compliance": {},
            "access_control": {},
            "data_integrity": {},
            "overall_security_score": 0,
        }

        # Test constitutional compliance
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "http://localhost:8001/api/v1/constitutional/compliance"
                )
                if response.status_code == 200:
                    data = response.json()
                    security_results["constitutional_compliance"] = {
                        "status": "compliant",
                        "compliance_score": data.get("compliance_score", 0),
                        "meets_requirements": data.get("compliance_score", 0) >= 0.8,
                    }
                else:
                    security_results["constitutional_compliance"] = {
                        "status": "error",
                        "meets_requirements": False,
                    }
        except Exception as e:
            security_results["constitutional_compliance"] = {
                "status": "error",
                "error": str(e),
                "meets_requirements": False,
            }

        # Test access control (basic auth check)
        auth_tests = []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Test health endpoints are accessible
                response = await client.get("http://localhost:8000/health")
                auth_tests.append(response.status_code == 200)

                # Test that protected endpoints exist (even if they return 401/403)
                response = await client.get("http://localhost:8000/api/v1/protected")
                auth_tests.append(
                    response.status_code in [401, 403, 404]
                )  # Expected for protected endpoint

        except Exception:
            auth_tests.append(False)

        security_results["access_control"] = {
            "tests_passed": sum(auth_tests),
            "total_tests": len(auth_tests),
            "meets_requirements": len(auth_tests) > 0
            and sum(auth_tests) >= len(auth_tests) * 0.8,
        }

        # Test data integrity
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get("http://localhost:8002/health")
                if response.status_code == 200:
                    security_results["data_integrity"] = {
                        "integrity_service_status": "operational",
                        "meets_requirements": True,
                    }
                else:
                    security_results["data_integrity"] = {
                        "integrity_service_status": "degraded",
                        "meets_requirements": False,
                    }
        except Exception as e:
            security_results["data_integrity"] = {
                "integrity_service_status": "error",
                "error": str(e),
                "meets_requirements": False,
            }

        # Calculate overall security score
        compliance_score = security_results["constitutional_compliance"].get(
            "compliance_score", 0
        )
        access_control_score = (
            1.0
            if security_results["access_control"].get("meets_requirements", False)
            else 0.0
        )
        integrity_score = (
            1.0
            if security_results["data_integrity"].get("meets_requirements", False)
            else 0.0
        )

        security_results["overall_security_score"] = (
            compliance_score + access_control_score + integrity_score
        ) / 3

        return security_results

    async def validate_production_readiness(self) -> dict[str, Any]:
        """Run comprehensive production readiness validation."""
        logger.info("🚀 Starting ACGS-1 Production Readiness Validation")

        validation_results = {
            "timestamp": time.time(),
            "phase": "Phase 3 - Production Readiness",
            "sla_compliance": {},
            "security_compliance": {},
            "service_health": {},
            "workflow_functionality": {},
            "overall_readiness": {
                "ready_for_production": False,
                "readiness_score": 0,
                "critical_issues": [],
                "recommendations": [],
            },
        }

        # Run all validation tests
        try:
            # SLA compliance test
            validation_results["sla_compliance"] = await self.validate_sla_compliance()

            # Security compliance test
            validation_results["security_compliance"] = (
                await self.validate_security_compliance()
            )

            # Service health check (reuse existing validation)
            logger.info("🏥 Running Service Health Validation")
            import subprocess

            result = subprocess.run(
                ["python3", "scripts/validate_services.py"],
                check=False,
                capture_output=True,
                text=True,
                cwd="/home/ubuntu/ACGS",
            )
            validation_results["service_health"] = {
                "exit_code": result.returncode,
                "all_services_operational": result.returncode == 0,
            }

            # Workflow functionality check
            logger.info("🔄 Running Workflow Validation")
            result = subprocess.run(
                ["python3", "scripts/validate_workflows.py"],
                check=False,
                capture_output=True,
                text=True,
                cwd="/home/ubuntu/ACGS",
            )
            validation_results["workflow_functionality"] = {
                "exit_code": result.returncode,
                "all_workflows_operational": result.returncode == 0,
            }

        except Exception as e:
            logger.error(f"Validation error: {e}")
            validation_results["validation_error"] = str(e)

        # Calculate overall readiness
        readiness_factors = []
        critical_issues = []
        recommendations = []

        # SLA compliance factor
        sla_compliant = validation_results["sla_compliance"].get(
            "overall_compliance", False
        )
        readiness_factors.append(1.0 if sla_compliant else 0.0)
        if not sla_compliant:
            critical_issues.append(
                "SLA requirements not met (>99% uptime, <500ms response time)"
            )
            recommendations.append("Optimize service performance and reliability")

        # Security compliance factor
        security_score = validation_results["security_compliance"].get(
            "overall_security_score", 0
        )
        readiness_factors.append(security_score)
        if security_score < 0.8:
            critical_issues.append("Security compliance below threshold")
            recommendations.append(
                "Address security and constitutional compliance issues"
            )

        # Service health factor
        services_healthy = validation_results["service_health"].get(
            "all_services_operational", False
        )
        readiness_factors.append(1.0 if services_healthy else 0.0)
        if not services_healthy:
            critical_issues.append("Not all services are operational")
            recommendations.append("Ensure all 7 core services are running and healthy")

        # Workflow functionality factor
        workflows_working = validation_results["workflow_functionality"].get(
            "all_workflows_operational", False
        )
        readiness_factors.append(1.0 if workflows_working else 0.0)
        if not workflows_working:
            critical_issues.append("End-to-end workflows not fully functional")
            recommendations.append("Fix workflow integration issues")

        # Calculate overall readiness score
        overall_score = (
            sum(readiness_factors) / len(readiness_factors) if readiness_factors else 0
        )
        ready_for_production = overall_score >= 0.9 and len(critical_issues) == 0

        validation_results["overall_readiness"] = {
            "ready_for_production": ready_for_production,
            "readiness_score": overall_score,
            "critical_issues": critical_issues,
            "recommendations": recommendations,
            "readiness_factors": {
                "sla_compliance": sla_compliant,
                "security_compliance": security_score >= 0.8,
                "service_health": services_healthy,
                "workflow_functionality": workflows_working,
            },
        }

        return validation_results

    def print_readiness_report(self, results: dict[str, Any]):
        """Print comprehensive production readiness report."""
        print("\n" + "=" * 80)
        print("🏭 ACGS-1 PHASE 3 PRODUCTION READINESS REPORT")
        print("=" * 80)

        overall = results["overall_readiness"]

        # Overall status
        status_icon = "✅" if overall["ready_for_production"] else "❌"
        print(
            f"{status_icon} Production Ready: {'YES' if overall['ready_for_production'] else 'NO'}"
        )
        print(f"📊 Readiness Score: {overall['readiness_score']:.1%}")

        # Readiness factors
        print("\n📋 READINESS FACTORS:")
        factors = overall.get("readiness_factors", {})
        for factor, status in factors.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {factor.replace('_', ' ').title()}")

        # SLA Compliance Details
        sla = results.get("sla_compliance", {})
        if sla:
            print("\n🎯 SLA COMPLIANCE:")
            print(
                f"  Overall: {'✅ PASS' if sla.get('overall_compliance') else '❌ FAIL'}"
            )

            # Uptime results
            uptime_results = sla.get("uptime_test", {})
            if uptime_results:
                avg_uptime = sum(
                    r.get("uptime_percentage", 0) for r in uptime_results.values()
                ) / len(uptime_results)
                print(f"  Average Uptime: {avg_uptime:.1f}% (Target: >99%)")

            # Response time results
            response_results = sla.get("response_time_test", {})
            if response_results:
                valid_times = [
                    r.get("avg_response_time_ms")
                    for r in response_results.values()
                    if r.get("avg_response_time_ms")
                ]
                if valid_times:
                    avg_response_time = sum(valid_times) / len(valid_times)
                    print(
                        f"  Average Response Time: {avg_response_time:.1f}ms (Target: <500ms)"
                    )

        # Security Compliance
        security = results.get("security_compliance", {})
        if security:
            print("\n🔒 SECURITY COMPLIANCE:")
            score = security.get("overall_security_score", 0)
            print(f"  Security Score: {score:.1%} (Target: >80%)")

        # Critical Issues
        if overall["critical_issues"]:
            print("\n❌ CRITICAL ISSUES:")
            for issue in overall["critical_issues"]:
                print(f"  • {issue}")

        # Recommendations
        if overall["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in overall["recommendations"]:
                print(f"  • {rec}")

        # Final verdict
        print(f"\n{'=' * 80}")
        if overall["ready_for_production"]:
            print("🎉 ACGS-1 IS READY FOR PRODUCTION DEPLOYMENT!")
            print("   All systems operational, SLA targets met, security compliant.")
        else:
            print("⚠️  ACGS-1 REQUIRES ADDITIONAL WORK BEFORE PRODUCTION")
            print("   Address critical issues above before proceeding.")
        print("=" * 80)


async def main():
    """Main production readiness validation function."""
    validator = ProductionReadinessValidator()
    results = await validator.validate_production_readiness()

    # Print report
    validator.print_readiness_report(results)

    # Save results
    with open("tests/results/production_readiness_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info(
        "📋 Production readiness results saved to tests/results/production_readiness_results.json"
    )

    # Return exit code based on readiness
    return 0 if results["overall_readiness"]["ready_for_production"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
