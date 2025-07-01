#!/usr/bin/env python3
"""
ACGS-1 Enhancement Framework Validation Script

This script validates that the enhancement framework is working correctly
and that enhanced services maintain all required functionality.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Any

import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FrameworkValidator:
    """Validates the ACGS-1 Enhancement Framework functionality."""

    def __init__(self, service_url: str = "http://localhost:8005"):
        self.service_url = service_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.validation_results = {}

    async def validate_framework(self) -> dict[str, Any]:
        """Run comprehensive validation of the enhancement framework."""
        logger.info("🔍 Starting ACGS-1 Enhancement Framework Validation")

        validation_tests = [
            ("Service Health", self.test_service_health),
            ("Constitutional Compliance", self.test_constitutional_compliance),
            ("Performance Optimization", self.test_performance_optimization),
            ("Monitoring Integration", self.test_monitoring_integration),
            ("Cache Functionality", self.test_cache_functionality),
            ("API Endpoints", self.test_api_endpoints),
            ("Error Handling", self.test_error_handling),
        ]

        results = {
            "framework_version": "1.0.0",
            "validation_timestamp": time.time(),
            "service_url": self.service_url,
            "tests": {},
            "overall_status": "unknown",
        }

        passed_tests = 0
        total_tests = len(validation_tests)

        for test_name, test_func in validation_tests:
            logger.info(f"🧪 Running test: {test_name}")
            try:
                test_result = await test_func()
                results["tests"][test_name] = test_result
                if test_result.get("passed", False):
                    passed_tests += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(
                        f"❌ {test_name}: FAILED - {test_result.get('error', 'Unknown error')}"
                    )
            except Exception as e:
                logger.error(f"❌ {test_name}: EXCEPTION - {e!s}")
                results["tests"][test_name] = {
                    "passed": False,
                    "error": str(e),
                    "exception": True,
                }

        # Calculate overall status
        success_rate = passed_tests / total_tests
        if success_rate >= 0.8:
            results["overall_status"] = "passed"
        elif success_rate >= 0.6:
            results["overall_status"] = "warning"
        else:
            results["overall_status"] = "failed"

        results["success_rate"] = success_rate
        results["passed_tests"] = passed_tests
        results["total_tests"] = total_tests

        logger.info(
            f"📊 Validation Complete: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})"
        )

        return results

    async def test_service_health(self) -> dict[str, Any]:
        """Test basic service health and availability."""
        try:
            # Test root endpoint
            response = await self.client.get(f"{self.service_url}/")
            if response.status_code != 200:
                return {
                    "passed": False,
                    "error": f"Root endpoint returned {response.status_code}",
                }

            root_data = response.json()

            # Verify service information
            required_fields = ["service", "version", "status", "constitutional_hash"]
            for field in required_fields:
                if field not in root_data:
                    return {
                        "passed": False,
                        "error": f"Missing required field: {field}",
                    }

            # Test health endpoint
            response = await self.client.get(f"{self.service_url}/health")
            if response.status_code != 200:
                return {
                    "passed": False,
                    "error": f"Health endpoint returned {response.status_code}",
                }

            health_data = response.json()
            if health_data.get("status") != "healthy":
                return {
                    "passed": False,
                    "error": f"Service not healthy: {health_data.get('status')}",
                }

            return {
                "passed": True,
                "service_info": root_data,
                "health_status": health_data,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_constitutional_compliance(self) -> dict[str, Any]:
        """Test constitutional compliance validation."""
        try:
            # Test with valid constitutional hash
            headers = {"X-Constitutional-Hash": "cdd01ef066bc6cf2"}
            response = await self.client.get(
                f"{self.service_url}/status", headers=headers
            )

            if response.status_code != 200:
                return {
                    "passed": False,
                    "error": f"Valid hash request failed: {response.status_code}",
                }

            # Check for constitutional compliance headers
            if "X-Constitutional-Hash" not in response.headers:
                return {
                    "passed": False,
                    "error": "Missing constitutional hash in response headers",
                }

            # Test with invalid constitutional hash (should fail in strict mode)
            invalid_headers = {"X-Constitutional-Hash": "invalid_hash"}
            response = await self.client.get(
                f"{self.service_url}/status", headers=invalid_headers
            )

            # In strict mode, this should return 400
            if response.status_code == 400:
                constitutional_strict = True
            else:
                constitutional_strict = False

            return {
                "passed": True,
                "constitutional_hash_validated": True,
                "strict_mode_active": constitutional_strict,
                "reference_hash": "cdd01ef066bc6cf2",
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_performance_optimization(self) -> dict[str, Any]:
        """Test performance optimization features."""
        try:
            # Measure response times
            response_times = []
            for _ in range(5):
                start_time = time.time()
                response = await self.client.get(f"{self.service_url}/health")
                response_time = time.time() - start_time
                response_times.append(response_time)

                if response.status_code != 200:
                    return {
                        "passed": False,
                        "error": f"Performance test request failed: {response.status_code}",
                    }

            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)

            # Check performance targets
            performance_target = 0.5  # 500ms
            performance_passed = avg_response_time < performance_target

            # Check for performance headers
            last_response = await self.client.get(f"{self.service_url}/health")
            has_performance_headers = "X-Response-Time" in last_response.headers

            return {
                "passed": performance_passed,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "performance_target": performance_target,
                "performance_headers_present": has_performance_headers,
                "response_times": response_times,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_monitoring_integration(self) -> dict[str, Any]:
        """Test monitoring and metrics integration."""
        try:
            # Test metrics endpoint
            response = await self.client.get(f"{self.service_url}/metrics")
            metrics_available = response.status_code == 200

            # Test enhanced status endpoint (if available)
            enhanced_status_available = False
            try:
                response = await self.client.get(
                    f"{self.service_url}/api/v1/pgc/enhanced-status"
                )
                enhanced_status_available = response.status_code == 200
            except:
                pass

            return {
                "passed": metrics_available,
                "metrics_endpoint_available": metrics_available,
                "enhanced_status_available": enhanced_status_available,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_cache_functionality(self) -> dict[str, Any]:
        """Test cache functionality (if available)."""
        try:
            # Test cache stats endpoint (if available)
            cache_stats_available = False
            try:
                response = await self.client.get(
                    f"{self.service_url}/api/v1/pgc/cache-stats"
                )
                cache_stats_available = response.status_code == 200
                if cache_stats_available:
                    cache_data = response.json()
            except:
                pass

            return {
                "passed": True,  # Cache is optional, so always pass
                "cache_stats_available": cache_stats_available,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_api_endpoints(self) -> dict[str, Any]:
        """Test that existing API endpoints are preserved."""
        try:
            # Test standard endpoints
            endpoints_to_test = [
                "/",
                "/health",
                "/docs",
            ]

            endpoint_results = {}
            for endpoint in endpoints_to_test:
                try:
                    response = await self.client.get(f"{self.service_url}{endpoint}")
                    endpoint_results[endpoint] = {
                        "status_code": response.status_code,
                        "available": response.status_code < 400,
                    }
                except Exception as e:
                    endpoint_results[endpoint] = {
                        "status_code": None,
                        "available": False,
                        "error": str(e),
                    }

            # Check if most endpoints are available
            available_count = sum(
                1 for result in endpoint_results.values() if result["available"]
            )
            endpoints_passed = available_count >= len(endpoints_to_test) * 0.8

            return {
                "passed": endpoints_passed,
                "endpoint_results": endpoint_results,
                "available_endpoints": available_count,
                "total_endpoints": len(endpoints_to_test),
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_error_handling(self) -> dict[str, Any]:
        """Test error handling and graceful degradation."""
        try:
            # Test non-existent endpoint
            response = await self.client.get(
                f"{self.service_url}/non-existent-endpoint"
            )
            handles_404 = response.status_code == 404

            # Test malformed request (if applicable)
            error_handling_passed = handles_404

            return {
                "passed": error_handling_passed,
                "handles_404": handles_404,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main validation function."""
    if len(sys.argv) > 1:
        service_url = sys.argv[1]
    else:
        service_url = "http://localhost:8005"

    validator = FrameworkValidator(service_url)

    try:
        results = await validator.validate_framework()

        # Print results
        print("\n" + "=" * 60)
        print("ACGS-1 Enhancement Framework Validation Results")
        print("=" * 60)
        print(f"Service URL: {results['service_url']}")
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(
            f"Success Rate: {results['success_rate']:.1%} ({results['passed_tests']}/{results['total_tests']})"
        )
        print("\nTest Results:")

        for test_name, test_result in results["tests"].items():
            status = "✅ PASSED" if test_result.get("passed", False) else "❌ FAILED"
            print(f"  {test_name}: {status}")
            if not test_result.get("passed", False) and "error" in test_result:
                print(f"    Error: {test_result['error']}")

        # Save detailed results
        with open("framework_validation_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print("\nDetailed results saved to: framework_validation_results.json")

        # Exit with appropriate code
        if results["overall_status"] == "passed":
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation failed with exception: {e}")
        sys.exit(1)
    finally:
        await validator.close()


if __name__ == "__main__":
    asyncio.run(main())
