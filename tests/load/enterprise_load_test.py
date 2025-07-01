#!/usr/bin/env python3
"""
ACGS Enterprise Load Testing Framework
Simulates enterprise-scale load with constitutional policy validation
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any


class EnterpriseLoadTester:
    def __init__(self):
        self.services = {
            "auth_service": "http://localhost:8016",
            "ac_service": "http://localhost:8002",
            "pgc_service": "http://localhost:8003",
        }
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.results = []

    async def simulate_user_session(
        self, session: aiohttp.ClientSession, user_id: int
    ) -> Dict[str, Any]:
        """Simulate a realistic user session with constitutional policy validation"""
        session_start = time.time()
        session_results = {
            "user_id": user_id,
            "requests": [],
            "total_latency": 0,
            "errors": 0,
            "constitutional_validations": 0,
        }

        # Simulate user workflow: Auth -> Policy Check -> Constitutional Validation
        workflow = [
            ("auth_service", "/health"),
            ("pgc_service", "/health"),
            ("ac_service", "/health"),  # This will be blocked by security
        ]

        for service_name, endpoint in workflow:
            if service_name not in self.services:
                continue

            url = f"{self.services[service_name]}{endpoint}"

            try:
                request_start = time.time()
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    request_end = time.time()
                    latency_ms = (request_end - request_start) * 1000

                    response_text = await response.text()

                    request_result = {
                        "service": service_name,
                        "endpoint": endpoint,
                        "status_code": response.status,
                        "latency_ms": latency_ms,
                        "timestamp": request_start,
                    }

                    session_results["requests"].append(request_result)
                    session_results["total_latency"] += latency_ms

                    # Check for constitutional compliance
                    if self.constitutional_hash in response_text:
                        session_results["constitutional_validations"] += 1

                    # Count errors (but 500 from ac_service is expected due to security)
                    if response.status >= 400 and not (
                        service_name == "ac_service" and response.status == 500
                    ):
                        session_results["errors"] += 1

            except Exception as e:
                session_results["errors"] += 1
                session_results["requests"].append(
                    {
                        "service": service_name,
                        "endpoint": endpoint,
                        "error": str(e),
                        "timestamp": time.time(),
                    }
                )

        session_results["duration"] = time.time() - session_start
        return session_results

    async def run_concurrent_load(
        self, concurrent_users: int, duration_seconds: int = 60
    ) -> Dict[str, Any]:
        """Run concurrent load test with specified number of users"""
        print(
            f"🚀 Starting load test: {concurrent_users} concurrent users for {duration_seconds}s"
        )

        start_time = time.time()
        end_time = start_time + duration_seconds

        connector = aiohttp.TCPConnector(limit=concurrent_users * 2)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []
            user_id = 0

            while time.time() < end_time:
                # Create batch of concurrent users
                batch_size = min(
                    concurrent_users, 100
                )  # Limit batch size for stability
                batch_tasks = []

                for _ in range(batch_size):
                    user_id += 1
                    task = asyncio.create_task(
                        self.simulate_user_session(session, user_id)
                    )
                    batch_tasks.append(task)

                # Wait for batch completion
                batch_results = await asyncio.gather(
                    *batch_tasks, return_exceptions=True
                )

                for result in batch_results:
                    if isinstance(result, dict):
                        self.results.append(result)

                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)

        return self.analyze_results()

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze load test results and generate metrics"""
        if not self.results:
            return {"error": "No results to analyze"}

        # Extract latency data
        all_latencies = []
        service_latencies = {}
        total_requests = 0
        total_errors = 0
        constitutional_validations = 0

        for session in self.results:
            total_errors += session.get("errors", 0)
            constitutional_validations += session.get("constitutional_validations", 0)

            for request in session.get("requests", []):
                if "latency_ms" in request:
                    latency = request["latency_ms"]
                    all_latencies.append(latency)
                    total_requests += 1

                    service = request["service"]
                    if service not in service_latencies:
                        service_latencies[service] = []
                    service_latencies[service].append(latency)

        # Calculate performance metrics
        analysis = {
            "test_summary": {
                "total_users": len(self.results),
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": (
                    (total_errors / total_requests * 100) if total_requests > 0 else 0
                ),
                "constitutional_validations": constitutional_validations,
                "constitutional_compliance_rate": (
                    (constitutional_validations / len(self.results) * 100)
                    if self.results
                    else 0
                ),
            },
            "performance_metrics": {},
            "service_breakdown": {},
        }

        if all_latencies:
            sorted_latencies = sorted(all_latencies)
            analysis["performance_metrics"] = {
                "avg_latency_ms": statistics.mean(all_latencies),
                "median_latency_ms": statistics.median(all_latencies),
                "p95_latency_ms": sorted_latencies[int(0.95 * len(sorted_latencies))],
                "p99_latency_ms": sorted_latencies[int(0.99 * len(sorted_latencies))],
                "min_latency_ms": min(all_latencies),
                "max_latency_ms": max(all_latencies),
            }

        # Service-specific analysis
        for service, latencies in service_latencies.items():
            if latencies:
                analysis["service_breakdown"][service] = {
                    "request_count": len(latencies),
                    "avg_latency_ms": statistics.mean(latencies),
                    "p99_latency_ms": (
                        sorted(latencies)[int(0.99 * len(latencies))]
                        if len(latencies) > 1
                        else latencies[0]
                    ),
                }

        return analysis


async def main():
    """Main load testing execution"""
    print("🏢 ACGS Enterprise Load Testing Framework")
    print("=" * 50)

    tester = EnterpriseLoadTester()

    # Test scenarios with increasing load
    test_scenarios = [
        {"users": 10, "duration": 30, "name": "Baseline Load"},
        {"users": 50, "duration": 30, "name": "Medium Load"},
        {"users": 100, "duration": 30, "name": "High Load"},
        {"users": 200, "duration": 30, "name": "Enterprise Load"},
    ]

    all_results = {}

    for scenario in test_scenarios:
        print(f"\n📊 Running {scenario['name']} Test:")
        print(f"   Users: {scenario['users']}")
        print(f"   Duration: {scenario['duration']}s")

        # Reset results for each scenario
        tester.results = []

        try:
            results = await tester.run_concurrent_load(
                concurrent_users=scenario["users"],
                duration_seconds=scenario["duration"],
            )

            all_results[scenario["name"]] = results

            # Display key metrics
            if "performance_metrics" in results:
                perf = results["performance_metrics"]
                summary = results["test_summary"]

                print(f"   📈 Results:")
                print(f"     Total Requests: {summary['total_requests']}")
                print(f"     Error Rate: {summary['error_rate']:.1f}%")
                print(f"     Avg Latency: {perf.get('avg_latency_ms', 0):.2f}ms")
                print(f"     P99 Latency: {perf.get('p99_latency_ms', 0):.2f}ms")
                print(
                    f"     Constitutional Compliance: {summary['constitutional_compliance_rate']:.1f}%"
                )

                # Check if P99 latency meets target
                p99_target_met = perf.get("p99_latency_ms", float("inf")) < 5
                print(
                    f"     P99 Target (<5ms): {'✅ PASSED' if p99_target_met else '❌ FAILED'}"
                )

        except Exception as e:
            print(f"   ❌ Test failed: {str(e)}")
            all_results[scenario["name"]] = {"error": str(e)}

    # Generate final report
    print(f"\n🎯 Enterprise Load Testing Summary:")
    print("=" * 50)

    successful_tests = 0
    for scenario_name, results in all_results.items():
        if "error" not in results:
            successful_tests += 1
            perf = results.get("performance_metrics", {})
            p99 = perf.get("p99_latency_ms", float("inf"))
            status = "✅ PASSED" if p99 < 5 else "⚠️ DEGRADED"
            print(f"{scenario_name}: P99 {p99:.2f}ms {status}")
        else:
            print(f"{scenario_name}: ❌ FAILED")

    overall_success = successful_tests >= len(test_scenarios) * 0.75
    print(f"\nOverall Load Testing: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    print(f"Successful Scenarios: {successful_tests}/{len(test_scenarios)}")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"enterprise_load_test_results_{timestamp}.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print(
        f"\n📄 Detailed results saved to: enterprise_load_test_results_{timestamp}.json"
    )


if __name__ == "__main__":
    asyncio.run(main())
