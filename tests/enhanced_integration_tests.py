"""
Enhanced ACGS Integration Tests
Comprehensive testing framework for performance, reliability, and failure scenarios
"""

import asyncio
import logging
import os

# Import enhanced modules
import sys
import time
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.shared.enhanced_auth import enhanced_auth_service
from services.shared.enhanced_service_client import (
    RequestMethod,
    enhanced_service_client,
)
from services.shared.enhanced_service_registry import (
    enhanced_service_registry,
)

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data structure."""

    test_name: str
    success: bool
    duration: float
    error: str | None = None
    metrics: dict[str, Any] | None = None


class ChaosEngineeringTests:
    """Chaos engineering tests for ACGS integration reliability."""

    def __init__(self):
        self.test_results: list[TestResult] = []

    async def test_service_registry_under_load(
        self, concurrent_requests: int = 50
    ) -> TestResult:
        """Test service registry performance under load."""
        start_time = time.time()

        try:
            # Start enhanced service registry
            await enhanced_service_registry.start()

            # Create concurrent health check tasks
            tasks = []
            for _ in range(concurrent_requests):
                task = enhanced_service_registry.check_all_services_health_parallel()
                tasks.append(task)

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful_checks = sum(1 for r in results if not isinstance(r, Exception))
            failed_checks = len(results) - successful_checks

            duration = time.time() - start_time

            # Get performance metrics
            performance_report = (
                await enhanced_service_registry.get_registry_performance_report()
            )

            success = (successful_checks / len(results)) >= 0.8  # 80% success threshold

            return TestResult(
                test_name="service_registry_load_test",
                success=success,
                duration=duration,
                metrics={
                    "concurrent_requests": concurrent_requests,
                    "successful_checks": successful_checks,
                    "failed_checks": failed_checks,
                    "success_rate": successful_checks / len(results),
                    "avg_response_time": performance_report["registry_metrics"][
                        "avg_check_time"
                    ],
                },
            )

        except Exception as e:
            return TestResult(
                test_name="service_registry_load_test",
                success=False,
                duration=time.time() - start_time,
                error=str(e),
            )

    async def test_circuit_breaker_functionality(self) -> TestResult:
        """Test circuit breaker behavior under service failures."""
        start_time = time.time()

        try:
            # Mock a failing service
            with patch("httpx.AsyncClient.get") as mock_get:
                # Configure mock to always fail
                mock_get.side_effect = httpx.ConnectError("Connection failed")

                # Get a test service
                test_service = enhanced_service_registry.get_service("auth_service")
                if not test_service:
                    raise Exception("Test service not found")

                # Make multiple requests to trigger circuit breaker
                failure_count = 0
                for _i in range(10):
                    is_healthy = await enhanced_service_registry.check_service_health(
                        test_service
                    )
                    if not is_healthy:
                        failure_count += 1

                # Check if circuit breaker opened
                circuit_breaker_opened = (
                    test_service.circuit_breaker.state.value == "open"
                )

                duration = time.time() - start_time

                return TestResult(
                    test_name="circuit_breaker_test",
                    success=circuit_breaker_opened and failure_count >= 5,
                    duration=duration,
                    metrics={
                        "failure_count": failure_count,
                        "circuit_breaker_state": test_service.circuit_breaker.state.value,
                        "service_status": test_service.status.value,
                    },
                )

        except Exception as e:
            return TestResult(
                test_name="circuit_breaker_test",
                success=False,
                duration=time.time() - start_time,
                error=str(e),
            )

    async def test_service_client_retry_mechanism(self) -> TestResult:
        """Test service client retry behavior."""
        start_time = time.time()

        try:
            # Mock intermittent failures
            call_count = 0

            async def mock_request(*args, **kwargs):
                nonlocal call_count
                call_count += 1

                # Fail first 2 attempts, succeed on 3rd
                if call_count <= 2:
                    raise httpx.ConnectError("Temporary failure")
                else:
                    # Return successful response
                    response = AsyncMock()
                    response.status_code = 200
                    response.json.return_value = {"status": "ok"}
                    response.content = b'{"status": "ok"}'
                    return response

            with patch.object(
                enhanced_service_client.http_client, "get", side_effect=mock_request
            ):
                result = await enhanced_service_client.call_service(
                    service_name="auth_service",
                    endpoint="/health",
                    method=RequestMethod.GET,
                )

                duration = time.time() - start_time

                return TestResult(
                    test_name="service_client_retry_test",
                    success=result.success and call_count == 3,
                    duration=duration,
                    metrics={
                        "retry_attempts": call_count,
                        "final_success": result.success,
                        "response_time": result.response_time,
                    },
                )

        except Exception as e:
            return TestResult(
                test_name="service_client_retry_test",
                success=False,
                duration=time.time() - start_time,
                error=str(e),
            )

    async def test_auth_service_performance(
        self, concurrent_auths: int = 100
    ) -> TestResult:
        """Test authentication service performance under load."""
        start_time = time.time()

        try:
            # Initialize auth service
            await enhanced_auth_service.initialize()

            # Create concurrent authentication tasks
            tasks = []
            for i in range(concurrent_auths):
                # Alternate between valid and invalid credentials
                if i % 2 == 0:
                    username, password = "admin", "admin_password"
                else:
                    username, password = "invalid_user", "invalid_password"

                task = enhanced_auth_service.authenticate_user(
                    username=username,
                    password=password,
                    ip_address=f"192.168.1.{i % 255}",
                    user_agent="test_client",
                )
                tasks.append(task)

            # Execute all authentication attempts
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful_auths = sum(
                1 for r in results if r is not None and not isinstance(r, Exception)
            )
            failed_auths = len(results) - successful_auths

            duration = time.time() - start_time

            # Get performance metrics
            auth_metrics = enhanced_auth_service.get_performance_metrics()

            # Success criteria: reasonable performance and expected success rate
            expected_success_rate = 0.5  # 50% since we're using 50% valid credentials
            actual_success_rate = successful_auths / len(results)
            success = (
                duration < 10.0  # Should complete within 10 seconds
                and abs(actual_success_rate - expected_success_rate)
                < 0.1  # Within 10% of expected
            )

            return TestResult(
                test_name="auth_service_performance_test",
                success=success,
                duration=duration,
                metrics={
                    "concurrent_auths": concurrent_auths,
                    "successful_auths": successful_auths,
                    "failed_auths": failed_auths,
                    "success_rate": actual_success_rate,
                    "avg_auth_time": auth_metrics["avg_auth_time"],
                    "cache_hit_rate": auth_metrics["cache_hit_rate"],
                },
            )

        except Exception as e:
            return TestResult(
                test_name="auth_service_performance_test",
                success=False,
                duration=time.time() - start_time,
                error=str(e),
            )

    async def test_network_partition_simulation(self) -> TestResult:
        """Simulate network partitions and test graceful degradation."""
        start_time = time.time()

        try:
            # Simulate network partition by making some services unreachable
            unreachable_services = ["ac_service", "fv_service", "gs_service"]

            with patch("httpx.AsyncClient.get") as mock_get:

                async def selective_failure(*args, **kwargs):
                    url = args[0] if args else kwargs.get("url", "")

                    # Check if this is a call to an unreachable service
                    for service in unreachable_services:
                        if (
                            f":{enhanced_service_registry.get_service(service).port}"
                            in url
                        ):
                            raise httpx.ConnectError("Network partition")

                    # Return success for other services
                    response = AsyncMock()
                    response.status_code = 200
                    response.json.return_value = {"status": "ok"}
                    return response

                mock_get.side_effect = selective_failure

                # Test service discovery with fallbacks
                fallback_results = []
                for service_name in unreachable_services:
                    fallback_service = (
                        enhanced_service_registry.get_service_with_fallback(
                            service_name
                        )
                    )
                    fallback_results.append(fallback_service is not None)

                # Test service client with fallback chain
                client_result = (
                    await enhanced_service_client.call_service_with_fallback_chain(
                        primary_service="ac_service",
                        fallback_services=["integrity_service", "auth_service"],
                        endpoint="/health",
                    )
                )

                duration = time.time() - start_time

                # Success if fallback mechanisms work
                fallback_success_rate = sum(fallback_results) / len(fallback_results)
                success = fallback_success_rate > 0.5 and client_result.success

                return TestResult(
                    test_name="network_partition_test",
                    success=success,
                    duration=duration,
                    metrics={
                        "unreachable_services": len(unreachable_services),
                        "fallback_success_rate": fallback_success_rate,
                        "client_fallback_success": client_result.success,
                    },
                )

        except Exception as e:
            return TestResult(
                test_name="network_partition_test",
                success=False,
                duration=time.time() - start_time,
                error=str(e),
            )

    async def run_all_chaos_tests(self) -> dict[str, Any]:
        """Run all chaos engineering tests."""
        logger.info("🧪 Starting chaos engineering tests...")

        test_methods = [
            self.test_service_registry_under_load,
            self.test_circuit_breaker_functionality,
            self.test_service_client_retry_mechanism,
            self.test_auth_service_performance,
            self.test_network_partition_simulation,
        ]

        results = []
        for test_method in test_methods:
            try:
                result = await test_method()
                results.append(result)
                status = "✅ PASSED" if result.success else "❌ FAILED"
                logger.info(f"{status} {result.test_name} ({result.duration:.2f}s)")

                if result.error:
                    logger.error(f"  Error: {result.error}")

                if result.metrics:
                    logger.info(f"  Metrics: {result.metrics}")

            except Exception as e:
                logger.error(f"❌ FAILED {test_method.__name__}: {e}")
                results.append(
                    TestResult(
                        test_name=test_method.__name__,
                        success=False,
                        duration=0.0,
                        error=str(e),
                    )
                )

        # Generate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        total_duration = sum(r.duration for r in results)

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_duration": total_duration,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error,
                    "metrics": r.metrics,
                }
                for r in results
            ],
        }

        logger.info(
            f"🏁 Chaos tests completed: {passed_tests}/{total_tests} passed ({summary['success_rate']:.1%})"
        )

        return summary


# Pytest test functions
@pytest.mark.asyncio
async def test_enhanced_service_registry():
    """Test enhanced service registry functionality."""
    chaos_tests = ChaosEngineeringTests()
    result = await chaos_tests.test_service_registry_under_load(concurrent_requests=20)
    assert result.success, f"Service registry test failed: {result.error}"


@pytest.mark.asyncio
async def test_enhanced_service_client():
    """Test enhanced service client functionality."""
    chaos_tests = ChaosEngineeringTests()
    result = await chaos_tests.test_service_client_retry_mechanism()
    assert result.success, f"Service client test failed: {result.error}"


@pytest.mark.asyncio
async def test_enhanced_auth_service():
    """Test enhanced auth service functionality."""
    chaos_tests = ChaosEngineeringTests()
    result = await chaos_tests.test_auth_service_performance(concurrent_auths=50)
    assert result.success, f"Auth service test failed: {result.error}"


@pytest.mark.asyncio
async def test_full_chaos_engineering_suite():
    """Run the complete chaos engineering test suite."""
    chaos_tests = ChaosEngineeringTests()
    summary = await chaos_tests.run_all_chaos_tests()

    # Require at least 80% of tests to pass
    assert (
        summary["success_rate"] >= 0.8
    ), f"Chaos tests failed: {summary['success_rate']:.1%} success rate"


if __name__ == "__main__":
    # Run chaos tests directly
    async def main():
        chaos_tests = ChaosEngineeringTests()
        summary = await chaos_tests.run_all_chaos_tests()

        print("\n" + "=" * 60)
        print("ACGS Enhanced Integration Test Results")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Duration: {summary['total_duration']:.2f} seconds")

        if summary["success_rate"] >= 0.8:
            print("🎉 Integration tests PASSED!")
        else:
            print("❌ Integration tests FAILED!")
            exit(1)

    asyncio.run(main())
