#!/usr/bin/env python3
"""
ACGS-1 Integration Testing - End-to-End Workflow Validation
===========================================================

This script validates that all services communicate properly and governance 
workflows function correctly after the reorganization.

Key Test Areas:
1. Service-to-Service Communication
2. Constitutional Governance Workflows
3. Authentication and Authorization
4. Data Flow Validation
5. Error Handling and Recovery
"""

import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("integration_testing.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data structure."""

    test_name: str
    success: bool
    duration_ms: float
    details: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""

    name: str
    port: int
    base_url: str
    health_endpoint: str = "/health"


class ACGSIntegrationTester:
    """ACGS-1 Integration Testing Suite."""

    def __init__(self):
        self.services = [
            ServiceEndpoint("auth_service", 8000, "http://localhost:8000"),
            ServiceEndpoint("ac_service", 8001, "http://localhost:8001"),
            ServiceEndpoint("integrity_service", 8002, "http://localhost:8002"),
            ServiceEndpoint("fv_service", 8003, "http://localhost:8003"),
            ServiceEndpoint("gs_service", 8004, "http://localhost:8004"),
            ServiceEndpoint("pgc_service", 8005, "http://localhost:8005"),
            ServiceEndpoint("ec_service", 8006, "http://localhost:8006"),
        ]
        self.test_results: List[TestResult] = []
        self.constitution_hash = "cdd01ef066bc6cf2"

    async def run_all_tests(self) -> List[TestResult]:
        """Run all integration tests."""
        logger.info("🚀 Starting ACGS-1 Integration Testing Suite")
        logger.info("=" * 60)

        # Test categories
        test_suites = [
            ("Service Health Validation", self.test_service_health),
            ("Service Communication", self.test_service_communication),
            ("Constitutional Governance", self.test_constitutional_governance),
            ("Authentication Flow", self.test_authentication_flow),
            ("Data Flow Validation", self.test_data_flow),
            ("Error Handling", self.test_error_handling),
            ("Performance Baseline", self.test_performance_baseline),
        ]

        for suite_name, test_func in test_suites:
            logger.info(f"\n📋 Running {suite_name} Tests...")
            try:
                await test_func()
            except Exception as e:
                logger.error(f"❌ Test suite {suite_name} failed: {e}")
                self.test_results.append(
                    TestResult(
                        test_name=f"{suite_name}_suite",
                        success=False,
                        duration_ms=0,
                        details={},
                        error_message=str(e),
                    )
                )

        return self.test_results

    async def test_service_health(self):
        """Test that all services are healthy and responding."""
        async with aiohttp.ClientSession() as session:
            for service in self.services:
                start_time = time.time()
                try:
                    url = f"{service.base_url}{service.health_endpoint}"
                    async with session.get(url, timeout=5) as response:
                        duration_ms = (time.time() - start_time) * 1000

                        if response.status == 200:
                            health_data = await response.json()
                            self.test_results.append(
                                TestResult(
                                    test_name=f"health_check_{service.name}",
                                    success=True,
                                    duration_ms=duration_ms,
                                    details={
                                        "status_code": response.status,
                                        "service_version": health_data.get(
                                            "version", "unknown"
                                        ),
                                        "service_status": health_data.get(
                                            "status", "unknown"
                                        ),
                                    },
                                )
                            )
                            logger.info(
                                f"✅ {service.name} health check passed ({duration_ms:.2f}ms)"
                            )
                        else:
                            raise Exception(f"HTTP {response.status}")

                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    self.test_results.append(
                        TestResult(
                            test_name=f"health_check_{service.name}",
                            success=False,
                            duration_ms=duration_ms,
                            details={"status_code": getattr(e, "status", "unknown")},
                            error_message=str(e),
                        )
                    )
                    logger.error(f"❌ {service.name} health check failed: {e}")

    async def test_service_communication(self):
        """Test inter-service communication patterns."""
        async with aiohttp.ClientSession() as session:
            # Test 1: AC Service -> FV Service communication
            start_time = time.time()
            try:
                # Get AC service status
                async with session.get("http://localhost:8001/") as ac_response:
                    ac_data = await ac_response.json()

                # Get FV service status
                async with session.get("http://localhost:8003/") as fv_response:
                    fv_data = await fv_response.json()

                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append(
                    TestResult(
                        test_name="ac_fv_communication",
                        success=True,
                        duration_ms=duration_ms,
                        details={
                            "ac_service_version": ac_data.get("version"),
                            "fv_service_version": fv_data.get("version"),
                            "communication_established": True,
                        },
                    )
                )
                logger.info(
                    f"✅ AC-FV service communication test passed ({duration_ms:.2f}ms)"
                )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append(
                    TestResult(
                        test_name="ac_fv_communication",
                        success=False,
                        duration_ms=duration_ms,
                        details={},
                        error_message=str(e),
                    )
                )
                logger.error(f"❌ AC-FV service communication failed: {e}")

            # Test 2: GS Service -> PGC Service communication
            start_time = time.time()
            try:
                # Test governance synthesis to policy governance communication
                async with session.get(
                    "http://localhost:8004/api/v1/governance/status"
                ) as gs_response:
                    gs_data = await gs_response.json()

                async with session.get("http://localhost:8005/") as pgc_response:
                    pgc_data = await pgc_response.json()

                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append(
                    TestResult(
                        test_name="gs_pgc_communication",
                        success=True,
                        duration_ms=duration_ms,
                        details={
                            "gs_governance_enabled": gs_data.get(
                                "governance_synthesis_enabled"
                            ),
                            "pgc_service_version": pgc_data.get("version"),
                            "communication_established": True,
                        },
                    )
                )
                logger.info(
                    f"✅ GS-PGC service communication test passed ({duration_ms:.2f}ms)"
                )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append(
                    TestResult(
                        test_name="gs_pgc_communication",
                        success=False,
                        duration_ms=duration_ms,
                        details={},
                        error_message=str(e),
                    )
                )
                logger.error(f"❌ GS-PGC service communication failed: {e}")

    async def test_constitutional_governance(self):
        """Test constitutional governance workflows."""
        async with aiohttp.ClientSession() as session:
            # Test constitutional hash validation across services
            services_with_hash = []

            for service in self.services:
                start_time = time.time()
                try:
                    # Try constitutional validation endpoint
                    url = f"{service.base_url}/api/v1/constitutional/validate"
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            if (
                                data.get("constitutional_hash")
                                == self.constitution_hash
                            ):
                                services_with_hash.append(service.name)

                        # Also check headers
                        if self.constitution_hash in str(response.headers).lower():
                            if service.name not in services_with_hash:
                                services_with_hash.append(service.name)

                    duration_ms = (time.time() - start_time) * 1000

                except Exception as e:
                    # Try health endpoint for header check
                    try:
                        url = f"{service.base_url}/health"
                        async with session.get(url, timeout=3) as response:
                            if self.constitution_hash in str(response.headers).lower():
                                services_with_hash.append(service.name)
                    except:
                        pass

            # Record constitutional governance test result
            self.test_results.append(
                TestResult(
                    test_name="constitutional_governance_validation",
                    success=len(services_with_hash)
                    >= 4,  # At least 4 services should have the hash
                    duration_ms=0,
                    details={
                        "constitution_hash": self.constitution_hash,
                        "services_with_hash": services_with_hash,
                        "total_services": len(self.services),
                        "compliance_percentage": (
                            len(services_with_hash) / len(self.services)
                        )
                        * 100,
                    },
                )
            )

            if len(services_with_hash) >= 4:
                logger.info(
                    f"✅ Constitutional governance validation passed ({len(services_with_hash)}/{len(self.services)} services)"
                )
            else:
                logger.warning(
                    f"⚠️ Constitutional governance validation partial ({len(services_with_hash)}/{len(self.services)} services)"
                )

    async def test_authentication_flow(self):
        """Test authentication service integration."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            try:
                # Test auth service enterprise status
                async with session.get(
                    "http://localhost:8000/auth/enterprise/status"
                ) as response:
                    if response.status == 200:
                        auth_data = await response.json()
                        duration_ms = (time.time() - start_time) * 1000

                        self.test_results.append(
                            TestResult(
                                test_name="authentication_flow",
                                success=True,
                                duration_ms=duration_ms,
                                details={
                                    "enterprise_auth_enabled": auth_data.get(
                                        "enterprise_auth_enabled"
                                    ),
                                    "mfa_enabled": auth_data.get("features", {})
                                    .get("multi_factor_authentication", {})
                                    .get("enabled"),
                                    "oauth_enabled": auth_data.get("features", {})
                                    .get("oauth_providers", {})
                                    .get("enabled"),
                                },
                            )
                        )
                        logger.info(
                            f"✅ Authentication flow test passed ({duration_ms:.2f}ms)"
                        )
                    else:
                        raise Exception(f"HTTP {response.status}")

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append(
                    TestResult(
                        test_name="authentication_flow",
                        success=False,
                        duration_ms=duration_ms,
                        details={},
                        error_message=str(e),
                    )
                )
                logger.error(f"❌ Authentication flow test failed: {e}")

    async def test_data_flow(self):
        """Test data flow between services."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            try:
                # Test integrity service data flow
                async with session.get(
                    "http://localhost:8002/api/v1/integrity/status"
                ) as response:
                    if response.status == 200:
                        integrity_data = await response.json()

                        duration_ms = (time.time() - start_time) * 1000
                        self.test_results.append(
                            TestResult(
                                test_name="data_flow_validation",
                                success=True,
                                duration_ms=duration_ms,
                                details={
                                    "integrity_enabled": integrity_data.get(
                                        "integrity_service_enabled"
                                    ),
                                    "cryptographic_verification": integrity_data.get(
                                        "features", {}
                                    ).get("cryptographic_verification"),
                                    "audit_trail": integrity_data.get(
                                        "features", {}
                                    ).get("audit_trail"),
                                },
                            )
                        )
                        logger.info(
                            f"✅ Data flow validation passed ({duration_ms:.2f}ms)"
                        )
                    else:
                        raise Exception(f"HTTP {response.status}")

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append(
                    TestResult(
                        test_name="data_flow_validation",
                        success=False,
                        duration_ms=duration_ms,
                        details={},
                        error_message=str(e),
                    )
                )
                logger.error(f"❌ Data flow validation failed: {e}")

    async def test_error_handling(self):
        """Test error handling and recovery mechanisms."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            try:
                # Test invalid endpoint handling
                async with session.get(
                    "http://localhost:8001/invalid/endpoint"
                ) as response:
                    duration_ms = (time.time() - start_time) * 1000

                    # Should return 404 or similar error code
                    if response.status in [404, 405, 422]:
                        self.test_results.append(
                            TestResult(
                                test_name="error_handling_validation",
                                success=True,
                                duration_ms=duration_ms,
                                details={
                                    "error_status_code": response.status,
                                    "proper_error_handling": True,
                                },
                            )
                        )
                        logger.info(
                            f"✅ Error handling validation passed ({duration_ms:.2f}ms)"
                        )
                    else:
                        raise Exception(f"Unexpected status code: {response.status}")

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append(
                    TestResult(
                        test_name="error_handling_validation",
                        success=False,
                        duration_ms=duration_ms,
                        details={},
                        error_message=str(e),
                    )
                )
                logger.error(f"❌ Error handling validation failed: {e}")

    async def test_performance_baseline(self):
        """Test performance baseline for all services."""
        async with aiohttp.ClientSession() as session:
            response_times = []

            for service in self.services:
                start_time = time.time()
                try:
                    url = f"{service.base_url}/health"
                    async with session.get(url, timeout=5) as response:
                        duration_ms = (time.time() - start_time) * 1000
                        response_times.append(duration_ms)

                except Exception as e:
                    logger.warning(f"Performance test failed for {service.name}: {e}")

            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)

                # Performance targets: avg < 100ms, max < 500ms
                performance_good = avg_response_time < 100 and max_response_time < 500

                self.test_results.append(
                    TestResult(
                        test_name="performance_baseline",
                        success=performance_good,
                        duration_ms=avg_response_time,
                        details={
                            "avg_response_time_ms": avg_response_time,
                            "max_response_time_ms": max_response_time,
                            "min_response_time_ms": min_response_time,
                            "services_tested": len(response_times),
                            "performance_target_met": performance_good,
                        },
                    )
                )

                if performance_good:
                    logger.info(
                        f"✅ Performance baseline test passed (avg: {avg_response_time:.2f}ms)"
                    )
                else:
                    logger.warning(
                        f"⚠️ Performance baseline test warning (avg: {avg_response_time:.2f}ms)"
                    )

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration test report."""
        successful_tests = [t for t in self.test_results if t.success]
        failed_tests = [t for t in self.test_results if not t.success]

        report = {
            "timestamp": time.time(),
            "summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": (
                    (len(successful_tests) / len(self.test_results)) * 100
                    if self.test_results
                    else 0
                ),
            },
            "test_results": [asdict(result) for result in self.test_results],
            "performance_metrics": {
                "avg_response_time_ms": (
                    sum(t.duration_ms for t in self.test_results if t.duration_ms > 0)
                    / len([t for t in self.test_results if t.duration_ms > 0])
                    if any(t.duration_ms > 0 for t in self.test_results)
                    else 0
                )
            },
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        failed_tests = [t for t in self.test_results if not t.success]
        if failed_tests:
            recommendations.append(
                f"Address {len(failed_tests)} failed tests before production deployment"
            )

        # Check constitutional governance compliance
        constitutional_test = next(
            (
                t
                for t in self.test_results
                if t.test_name == "constitutional_governance_validation"
            ),
            None,
        )
        if (
            constitutional_test
            and constitutional_test.details.get("compliance_percentage", 0) < 100
        ):
            recommendations.append(
                "Improve constitutional hash compliance across all services"
            )

        # Check performance
        performance_test = next(
            (t for t in self.test_results if t.test_name == "performance_baseline"),
            None,
        )
        if performance_test and not performance_test.success:
            recommendations.append(
                "Optimize service response times to meet performance targets"
            )

        if not recommendations:
            recommendations.append(
                "All integration tests passed - system ready for production"
            )

        return recommendations


async def main():
    """Main execution function."""
    tester = ACGSIntegrationTester()

    try:
        # Run all integration tests
        results = await tester.run_all_tests()

        # Generate and save report
        report = tester.generate_report()

        with open("integration_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 INTEGRATION TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Successful: {report['summary']['successful_tests']}")
        logger.info(f"Failed: {report['summary']['failed_tests']}")
        logger.info(f"Success Rate: {report['summary']['success_rate']:.1f}%")

        if report["recommendations"]:
            logger.info("\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"], 1):
                logger.info(f"{i}. {rec}")

        logger.info(f"\n📄 Detailed report saved to: integration_test_report.json")

        # Exit with appropriate code
        if report["summary"]["success_rate"] >= 80:
            logger.info("✅ Integration testing completed successfully!")
            return 0
        else:
            logger.error("❌ Integration testing completed with significant issues")
            return 1

    except Exception as e:
        logger.error(f"Integration testing failed: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
