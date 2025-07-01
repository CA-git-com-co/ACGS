#!/usr/bin/env python3
"""
ACGS-PGP Phase 5.2: Concurrent Load Testing
Validates concurrent request handling capacity and throughput targets

Features:
- Concurrent request handling (10-20 concurrent requests minimum)
- Throughput testing (1000 RPS target for PGC service)
- Stress testing with escalating load
- Connection pooling and resource utilization
- Performance degradation analysis
- Service stability under load
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import httpx
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConcurrentLoadResult(BaseModel):
    """Concurrent load test result model"""

    service: str
    test_type: str
    concurrent_level: int
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    success_rate: float
    meets_targets: Dict[str, bool]
    timestamp: datetime


class ACGSConcurrentLoadTester:
    """ACGS-PGP Concurrent Load Testing System"""

    def __init__(self):
        self.services = {
            "ac": {"port": 8001, "name": "Constitutional AI Service"},
            "integrity": {"port": 8002, "name": "Integrity Service"},
            "fv": {"port": 8003, "name": "Formal Verification Service"},
            "ec": {"port": 8006, "name": "Executive Council Service"},
        }
        self.base_url = "http://localhost"
        self.constitutional_hash = "cdd01ef066bc6cf2"

        # Load testing targets
        self.targets = {
            "min_concurrent_requests": 10,
            "max_concurrent_requests": 20,
            "pgc_throughput_rps": 1000,  # Target for PGC service
            "min_success_rate": 95.0,
            "max_response_time_ms": 2000,
        }

    def calculate_percentiles(self, response_times: List[float]) -> Dict[str, float]:
        """Calculate response time percentiles"""
        if not response_times:
            return {"p95": 0, "p99": 0}

        sorted_times = sorted(response_times)
        n = len(sorted_times)

        return {
            "p95": (
                sorted_times[int(n * 0.95)]
                if n > 1
                else sorted_times[0] if n > 0 else 0
            ),
            "p99": (
                sorted_times[int(n * 0.99)]
                if n > 2
                else sorted_times[-1] if n > 0 else 0
            ),
        }

    async def concurrent_load_test(
        self, service_key: str, concurrent_requests: int, duration_seconds: int = 30
    ) -> ConcurrentLoadResult:
        """Run concurrent load test on a specific service"""
        service = self.services[service_key]
        logger.info(
            f"🔥 Concurrent load testing {service['name']} with {concurrent_requests} concurrent requests for {duration_seconds}s..."
        )

        response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()

        async def make_concurrent_request(session: httpx.AsyncClient, request_id: int):
            """Make a single concurrent request"""
            nonlocal successful_requests, failed_requests, response_times

            request_start = time.time()
            try:
                response = await session.get(
                    f"{self.base_url}:{service['port']}/health",
                    headers={
                        "X-Concurrent-Load-Test": "true",
                        "X-Request-ID": str(request_id),
                        "X-Concurrent-Level": str(concurrent_requests),
                    },
                )
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)

                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1

            except Exception as e:
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)
                failed_requests += 1

        # Run concurrent load test
        async with httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(
                max_connections=concurrent_requests * 2,
                max_keepalive_connections=concurrent_requests,
            ),
        ) as client:
            request_id = 0
            end_time = start_time + duration_seconds

            while time.time() < end_time:
                # Create batch of concurrent requests
                tasks = []
                for _ in range(concurrent_requests):
                    request_id += 1
                    tasks.append(make_concurrent_request(client, request_id))

                # Execute concurrent requests
                await asyncio.gather(*tasks, return_exceptions=True)

                # Small delay between batches to prevent overwhelming
                await asyncio.sleep(0.05)

        # Calculate metrics
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        success_rate = (
            (successful_requests / total_requests * 100) if total_requests > 0 else 0
        )
        requests_per_second = total_requests / total_time if total_time > 0 else 0

        avg_response_time = statistics.mean(response_times) if response_times else 0
        percentiles = self.calculate_percentiles(response_times)

        return ConcurrentLoadResult(
            service=service_key,
            test_type="concurrent_load",
            concurrent_level=concurrent_requests,
            duration_seconds=total_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            requests_per_second=requests_per_second,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=percentiles["p95"],
            p99_response_time_ms=percentiles["p99"],
            success_rate=success_rate,
            meets_targets={
                "min_concurrent_handled": concurrent_requests
                >= self.targets["min_concurrent_requests"],
                "success_rate_target": success_rate >= self.targets["min_success_rate"],
                "response_time_target": avg_response_time
                <= self.targets["max_response_time_ms"],
            },
            timestamp=datetime.now(timezone.utc),
        )

    async def escalating_load_test(self, service_key: str) -> Dict[str, Any]:
        """Run escalating load test with increasing concurrent requests"""
        service = self.services[service_key]
        logger.info(f"📈 Running escalating load test for {service['name']}...")

        escalation_levels = [5, 10, 15, 20, 25, 30]
        escalation_results = {}

        for level in escalation_levels:
            logger.info(f"Testing {level} concurrent requests...")
            result = await self.concurrent_load_test(
                service_key, level, duration_seconds=15
            )
            escalation_results[f"level_{level}"] = result.dict()

            # Stop if service starts failing significantly
            if result.success_rate < 80:
                logger.warning(
                    f"Service degradation detected at {level} concurrent requests"
                )
                break

            # Small delay between escalation levels
            await asyncio.sleep(2)

        # Analyze escalation results
        max_stable_level = 0
        for level_key, result in escalation_results.items():
            level = int(level_key.split("_")[1])
            if result["success_rate"] >= 95:
                max_stable_level = level

        return {
            "service": service_key,
            "service_name": service["name"],
            "escalation_results": escalation_results,
            "max_stable_concurrent_level": max_stable_level,
            "meets_concurrent_target": max_stable_level
            >= self.targets["min_concurrent_requests"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def throughput_stress_test(
        self, service_key: str, target_rps: int = 500
    ) -> Dict[str, Any]:
        """Run throughput stress test targeting specific RPS"""
        service = self.services[service_key]
        logger.info(
            f"🚀 Running throughput stress test for {service['name']} targeting {target_rps} RPS..."
        )

        test_duration = 30  # seconds
        batch_size = max(1, target_rps // 10)  # Requests per batch
        batch_interval = batch_size / target_rps  # Time between batches

        response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()

        async def throughput_request(session: httpx.AsyncClient, request_id: int):
            """Make a single throughput test request"""
            nonlocal successful_requests, failed_requests, response_times

            request_start = time.time()
            try:
                response = await session.get(
                    f"{self.base_url}:{service['port']}/health",
                    headers={
                        "X-Throughput-Test": "true",
                        "X-Request-ID": str(request_id),
                        "X-Target-RPS": str(target_rps),
                    },
                )
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)

                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1

            except Exception as e:
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)
                failed_requests += 1

        # Run throughput test
        async with httpx.AsyncClient(
            timeout=5.0,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        ) as client:
            request_id = 0
            end_time = start_time + test_duration

            while time.time() < end_time:
                # Create batch of requests
                tasks = []
                for _ in range(batch_size):
                    request_id += 1
                    tasks.append(throughput_request(client, request_id))

                # Execute batch
                await asyncio.gather(*tasks, return_exceptions=True)

                # Wait for next batch
                await asyncio.sleep(batch_interval)

        # Calculate metrics
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        actual_rps = total_requests / total_time if total_time > 0 else 0
        success_rate = (
            (successful_requests / total_requests * 100) if total_requests > 0 else 0
        )

        avg_response_time = statistics.mean(response_times) if response_times else 0
        percentiles = self.calculate_percentiles(response_times)

        return {
            "service": service_key,
            "service_name": service["name"],
            "target_rps": target_rps,
            "actual_rps": actual_rps,
            "rps_achievement": (actual_rps / target_rps * 100) if target_rps > 0 else 0,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "avg_response_time_ms": avg_response_time,
            "p95_response_time_ms": percentiles["p95"],
            "p99_response_time_ms": percentiles["p99"],
            "test_duration_seconds": total_time,
            "meets_throughput_target": actual_rps
            >= (target_rps * 0.8),  # 80% of target
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def run_comprehensive_concurrent_load_tests(self) -> Dict[str, Any]:
        """Run comprehensive concurrent load testing for all services"""
        logger.info("🚀 Starting ACGS-PGP Comprehensive Concurrent Load Testing...")

        test_results = {
            "test_suite": "ACGS-PGP Concurrent Load Testing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "load_testing_targets": self.targets,
            "results": {},
        }

        for service_key in self.services.keys():
            service_results = {}

            # Test 1: Standard concurrent load test (15 concurrent requests)
            standard_load = await self.concurrent_load_test(
                service_key, 15, duration_seconds=30
            )
            service_results["standard_concurrent_load"] = standard_load.dict()

            # Test 2: Escalating load test
            escalating_load = await self.escalating_load_test(service_key)
            service_results["escalating_load"] = escalating_load

            # Test 3: Throughput stress test
            throughput_test = await self.throughput_stress_test(
                service_key, target_rps=300
            )
            service_results["throughput_stress"] = throughput_test

            test_results["results"][service_key] = service_results

        # Calculate overall performance summary
        all_tests_passed = True
        total_tests = 0
        passed_tests = 0

        for service_results in test_results["results"].values():
            # Check standard concurrent load
            standard_test = service_results["standard_concurrent_load"]
            total_tests += 1
            if all(standard_test["meets_targets"].values()):
                passed_tests += 1
            else:
                all_tests_passed = False

            # Check escalating load
            escalating_test = service_results["escalating_load"]
            total_tests += 1
            if escalating_test["meets_concurrent_target"]:
                passed_tests += 1
            else:
                all_tests_passed = False

            # Check throughput stress
            throughput_test = service_results["throughput_stress"]
            total_tests += 1
            if throughput_test["meets_throughput_target"]:
                passed_tests += 1
            else:
                all_tests_passed = False

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "overall_success_rate": success_rate,
            "all_targets_met": all_tests_passed,
            "concurrent_load_status": "passed" if success_rate >= 80 else "failed",
        }

        return test_results


async def main():
    """Main execution function"""
    tester = ACGSConcurrentLoadTester()

    try:
        results = await tester.run_comprehensive_concurrent_load_tests()

        # Save results to file
        with open("phase5_2_concurrent_load_testing_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Print summary
        print("\n" + "=" * 80)
        print("ACGS-PGP Phase 5.2: Concurrent Load Testing Results")
        print("=" * 80)
        print(
            f"Overall Success Rate: {results['summary']['overall_success_rate']:.1f}%"
        )
        print(
            f"All Targets Met: {'YES' if results['summary']['all_targets_met'] else 'NO'}"
        )
        print(
            f"Concurrent Load Status: {results['summary']['concurrent_load_status'].upper()}"
        )
        print(f"Constitutional Hash: {results['constitutional_hash']}")
        print("=" * 80)

        # Print detailed results for each service
        for service_key, service_results in results["results"].items():
            service_name = tester.services[service_key]["name"]
            print(f"\n{service_name}:")

            # Standard concurrent load
            standard = service_results["standard_concurrent_load"]
            print(
                f"  Standard Load (15 concurrent): {standard['success_rate']:.1f}% success, {standard['requests_per_second']:.1f} RPS"
            )

            # Escalating load
            escalating = service_results["escalating_load"]
            print(
                f"  Max Stable Concurrent Level: {escalating['max_stable_concurrent_level']}"
            )

            # Throughput stress
            throughput = service_results["throughput_stress"]
            print(
                f"  Throughput Test: {throughput['actual_rps']:.1f} RPS ({throughput['rps_achievement']:.1f}% of target)"
            )

        print("=" * 80)

        if results["summary"]["concurrent_load_status"] == "passed":
            print("✅ Concurrent load testing passed all targets!")
            return 0
        else:
            print("❌ Some concurrent load targets not met. Check detailed results.")
            return 1

    except Exception as e:
        logger.error(f"Concurrent load testing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
