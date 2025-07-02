#!/usr/bin/env python3
"""
Concurrent Load Testing Script

Load test system with multiple concurrent agent operations across all services.
"""

import asyncio
import json
import statistics
import time
from datetime import datetime
from typing import Any

import httpx

# Service endpoints
SERVICES = {
    "auth_service": "http://localhost:8016",
    "hitl_service": "http://localhost:8008",
    "ac_service": "http://localhost:8001",  # Constitutional AI service
}


class ConcurrentLoadTester:
    def __init__(self):
        self.results = {
            "test_start": None,
            "test_end": None,
            "concurrent_tests": {},
            "service_performance": {},
            "errors": [],
            "summary": {},
        }
        self.client = httpx.AsyncClient(timeout=30.0)

    async def test_auth_service_load(
        self, concurrent_requests: int, duration_seconds: int
    ) -> dict[str, Any]:
        """Test Auth Service under concurrent load."""
        print(
            f"🔐 Testing Auth Service with {concurrent_requests} concurrent requests for {duration_seconds}s..."
        )

        async def make_auth_request(request_id: int):
            try:
                # Test token generation
                start_time = time.perf_counter()
                response = await self.client.post(
                    f"{SERVICES['auth_service']}/api/v1/auth/token",
                    json={
                        "username": f"test_user_{request_id}",
                        "password": "test_password",
                    },
                )
                token_time = time.perf_counter() - start_time

                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Token generation failed: {response.status_code}",
                        "latency_ms": token_time * 1000,
                    }

                token_data = response.json()
                token = token_data.get("access_token")

                # Test token validation
                start_time = time.perf_counter()
                response = await self.client.post(
                    f"{SERVICES['auth_service']}/api/v1/auth/validate",
                    json={"token": token},
                )
                validate_time = time.perf_counter() - start_time

                return {
                    "success": response.status_code == 200,
                    "token_generation_ms": token_time * 1000,
                    "token_validation_ms": validate_time * 1000,
                    "total_latency_ms": (token_time + validate_time) * 1000,
                    "constitutional_hash": token_data.get("constitutional_hash"),
                }

            except Exception as e:
                return {"success": False, "error": str(e), "latency_ms": 0}

        return await self._run_concurrent_test(
            make_auth_request, concurrent_requests, duration_seconds
        )

    async def test_hitl_service_load(
        self, concurrent_requests: int, duration_seconds: int
    ) -> dict[str, Any]:
        """Test HITL Service under concurrent load."""
        print(
            f"🤖 Testing HITL Service with {concurrent_requests} concurrent requests for {duration_seconds}s..."
        )

        async def make_hitl_request(request_id: int):
            try:
                test_request = {
                    "agent_id": f"load-test-agent-{request_id}",
                    "agent_type": "autonomous_coder",
                    "operation_type": "code_analysis",
                    "operation_description": f"Load test operation {request_id}",
                    "operation_context": {
                        "file_path": f"/test/file_{request_id}.py",
                        "operation_id": f"load-test-{request_id}",
                        "constitutional_hash": "cdd01ef066bc6cf2",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    "operation_target": "test_file",
                }

                start_time = time.perf_counter()
                response = await self.client.post(
                    f"{SERVICES['hitl_service']}/api/v1/reviews/evaluate",
                    json=test_request,
                )
                end_time = time.perf_counter()

                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "latency_ms": (end_time - start_time) * 1000,
                    "response_data": (
                        response.json() if response.status_code == 200 else None
                    ),
                }

            except Exception as e:
                return {"success": False, "error": str(e), "latency_ms": 0}

        return await self._run_concurrent_test(
            make_hitl_request, concurrent_requests, duration_seconds
        )

    async def test_ac_service_load(
        self, concurrent_requests: int, duration_seconds: int
    ) -> dict[str, Any]:
        """Test Constitutional AI Service under concurrent load."""
        print(
            f"⚖️ Testing Constitutional AI Service with {concurrent_requests} concurrent requests for {duration_seconds}s..."
        )

        async def make_ac_request(request_id: int):
            try:
                # Test health endpoint first (most services should have this)
                start_time = time.perf_counter()
                response = await self.client.get(f"{SERVICES['ac_service']}/health")
                end_time = time.perf_counter()

                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "latency_ms": (end_time - start_time) * 1000,
                    "response_data": (
                        response.json() if response.status_code == 200 else None
                    ),
                }

            except Exception as e:
                return {"success": False, "error": str(e), "latency_ms": 0}

        return await self._run_concurrent_test(
            make_ac_request, concurrent_requests, duration_seconds
        )

    async def _run_concurrent_test(
        self, request_func, concurrent_requests: int, duration_seconds: int
    ) -> dict[str, Any]:
        """Run a concurrent test with the given request function."""
        start_time = time.time()
        all_results = []

        while time.time() - start_time < duration_seconds:
            # Launch concurrent requests
            tasks = [request_func(i) for i in range(concurrent_requests)]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    all_results.append(
                        {"success": False, "error": str(result), "latency_ms": 0}
                    )
                else:
                    all_results.append(result)

            # Small delay between batches
            await asyncio.sleep(0.1)

        # Analyze results
        successful_requests = [r for r in all_results if r.get("success")]
        failed_requests = [r for r in all_results if not r.get("success")]
        latencies = [
            r.get("latency_ms", 0)
            for r in successful_requests
            if r.get("latency_ms", 0) > 0
        ]

        return {
            "total_requests": len(all_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": (
                len(successful_requests) / len(all_results) if all_results else 0
            ),
            "requests_per_second": len(all_results) / duration_seconds,
            "latency_metrics": (
                self._calculate_latency_metrics(latencies) if latencies else {}
            ),
            "errors": [r.get("error") for r in failed_requests if r.get("error")][
                :10
            ],  # First 10 errors
        }

    def _calculate_latency_metrics(self, latencies: list[float]) -> dict[str, float]:
        """Calculate latency statistics."""
        if not latencies:
            return {}

        sorted_latencies = sorted(latencies)
        return {
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "p95_ms": sorted_latencies[int(0.95 * len(sorted_latencies))],
            "p99_ms": sorted_latencies[int(0.99 * len(sorted_latencies))],
            "std_dev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "count": len(latencies),
        }

    async def test_mixed_workload(
        self, concurrent_requests: int, duration_seconds: int
    ) -> dict[str, Any]:
        """Test mixed workload across all services."""
        print(
            f"🔄 Testing mixed workload with {concurrent_requests} concurrent requests for {duration_seconds}s..."
        )

        async def make_mixed_request(request_id: int):
            # Randomly choose a service to test
            service_choice = request_id % 3

            try:
                if service_choice == 0:
                    # Auth service request
                    start_time = time.perf_counter()
                    response = await self.client.get(
                        f"{SERVICES['auth_service']}/api/v1/auth/info"
                    )
                    end_time = time.perf_counter()
                    service_name = "auth_service"

                elif service_choice == 1:
                    # HITL service request
                    start_time = time.perf_counter()
                    response = await self.client.get(f"{SERVICES['hitl_service']}/")
                    end_time = time.perf_counter()
                    service_name = "hitl_service"

                else:
                    # AC service request
                    start_time = time.perf_counter()
                    response = await self.client.get(f"{SERVICES['ac_service']}/health")
                    end_time = time.perf_counter()
                    service_name = "ac_service"

                return {
                    "success": response.status_code == 200,
                    "service": service_name,
                    "status_code": response.status_code,
                    "latency_ms": (end_time - start_time) * 1000,
                }

            except Exception as e:
                return {
                    "success": False,
                    "service": f"service_{service_choice}",
                    "error": str(e),
                    "latency_ms": 0,
                }

        return await self._run_concurrent_test(
            make_mixed_request, concurrent_requests, duration_seconds
        )

    async def run_comprehensive_load_test(self) -> dict[str, Any]:
        """Run comprehensive load testing across all services."""
        print("🚀 Starting comprehensive concurrent load testing...")
        self.results["test_start"] = datetime.utcnow().isoformat()

        # Test parameters
        concurrent_requests = 10
        test_duration = 10  # seconds

        # Test each service individually
        self.results["service_performance"]["auth_service"] = (
            await self.test_auth_service_load(concurrent_requests, test_duration)
        )

        self.results["service_performance"]["hitl_service"] = (
            await self.test_hitl_service_load(concurrent_requests, test_duration)
        )

        self.results["service_performance"]["ac_service"] = (
            await self.test_ac_service_load(concurrent_requests, test_duration)
        )

        # Test mixed workload
        self.results["concurrent_tests"]["mixed_workload"] = (
            await self.test_mixed_workload(concurrent_requests * 2, test_duration)
        )

        self.results["test_end"] = datetime.utcnow().isoformat()

        # Calculate summary metrics
        total_requests = sum(
            test_result.get("total_requests", 0)
            for test_result in self.results["service_performance"].values()
        )
        total_requests += self.results["concurrent_tests"]["mixed_workload"].get(
            "total_requests", 0
        )

        successful_requests = sum(
            test_result.get("successful_requests", 0)
            for test_result in self.results["service_performance"].values()
        )
        successful_requests += self.results["concurrent_tests"]["mixed_workload"].get(
            "successful_requests", 0
        )

        self.results["summary"] = {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "overall_success_rate": successful_requests / max(1, total_requests),
            "total_errors": len(self.results["errors"]),
            "test_duration": test_duration * 4,  # 4 tests run
            "average_rps": total_requests / (test_duration * 4),
        }

        return self.results

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main test execution."""
    tester = ConcurrentLoadTester()

    try:
        results = await tester.run_comprehensive_load_test()

        # Print results
        print("\n" + "=" * 80)
        print("🎯 CONCURRENT LOAD TEST RESULTS")
        print("=" * 80)

        print("\n📊 Overall Summary:")
        summary = results["summary"]
        print(f"  • Total Requests: {summary['total_requests']}")
        print(f"  • Successful Requests: {summary['successful_requests']}")
        print(f"  • Overall Success Rate: {summary['overall_success_rate'] * 100:.1f}%")
        print(f"  • Average RPS: {summary['average_rps']:.1f}")
        print(f"  • Test Duration: {summary['test_duration']}s")
        print(f"  • Total Errors: {summary['total_errors']}")

        print("\n🔧 Service Performance:")
        for service_name, perf in results["service_performance"].items():
            print(f"\n  {service_name.upper()}:")
            print(f"    • Success Rate: {perf.get('success_rate', 0) * 100:.1f}%")
            print(f"    • Requests/sec: {perf.get('requests_per_second', 0):.1f}")

            latency = perf.get("latency_metrics", {})
            if latency:
                print(f"    • Mean Latency: {latency.get('mean_ms', 0):.2f}ms")
                print(f"    • P95 Latency: {latency.get('p95_ms', 0):.2f}ms")
                print(f"    • P99 Latency: {latency.get('p99_ms', 0):.2f}ms")

            if perf.get("errors"):
                print(f"    • Sample Errors: {perf['errors'][:2]}")

        print("\n🔄 Mixed Workload Test:")
        mixed = results["concurrent_tests"]["mixed_workload"]
        print(f"  • Success Rate: {mixed.get('success_rate', 0) * 100:.1f}%")
        print(f"  • Requests/sec: {mixed.get('requests_per_second', 0):.1f}")

        mixed_latency = mixed.get("latency_metrics", {})
        if mixed_latency:
            print(f"  • Mean Latency: {mixed_latency.get('mean_ms', 0):.2f}ms")
            print(f"  • P99 Latency: {mixed_latency.get('p99_ms', 0):.2f}ms")

        # Save detailed results
        with open("concurrent_load_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n💾 Detailed results saved to: concurrent_load_test_results.json")

    except Exception as e:
        print(f"❌ Load test execution failed: {e}")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
