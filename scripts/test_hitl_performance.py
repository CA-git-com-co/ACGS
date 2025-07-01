#!/usr/bin/env python3
"""
HITL Service Performance Testing Script

Tests the Human-in-the-Loop decision engine performance including:
- Decision latency measurement (targeting sub-5ms P99)
- Automated vs human escalation scenarios
- Constitutional compliance validation
- Load testing with concurrent operations
"""

import asyncio
import json
import time
import statistics
from typing import List, Dict, Any
import httpx
import uuid
from datetime import datetime

# Service endpoints
HITL_SERVICE_URL = "http://localhost:8008"
AUTH_SERVICE_URL = "http://localhost:8016"


class HITLPerformanceTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "decision_latencies": [],
            "automated_decisions": 0,
            "human_escalations": 0,
            "constitutional_violations": 0,
            "errors": [],
            "test_start": None,
            "test_end": None,
        }

    async def test_decision_latency(self, num_requests: int = 100) -> Dict[str, Any]:
        """Test decision latency with multiple requests."""
        print(f"🚀 Testing HITL decision latency with {num_requests} requests...")

        latencies = []
        for i in range(num_requests):
            try:
                start_time = time.perf_counter()

                # Create test evaluation request
                test_request = {
                    "agent_id": f"test-agent-{i}",
                    "agent_type": "autonomous_coder",
                    "operation_type": "code_modification",
                    "operation_description": f"Test operation {i} - modify configuration file",
                    "operation_context": {
                        "file_path": "/config/test.yaml",
                        "change_type": "parameter_update",
                        "risk_level": "low",
                        "constitutional_hash": "cdd01ef066bc6cf2",
                    },
                    "operation_target": "configuration_file",
                    "request_metadata": {
                        "test_id": f"perf-test-{i}",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                }

                # Make request to HITL service
                response = await self.client.post(
                    f"{HITL_SERVICE_URL}/api/v1/reviews/evaluate",
                    json=test_request,
                    headers={"Content-Type": "application/json"},
                )

                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000

                latencies.append(latency_ms)

                if response.status_code == 200:
                    result = response.json()
                    if result.get("escalation_level", 0) <= 1:
                        self.results["automated_decisions"] += 1
                    else:
                        self.results["human_escalations"] += 1

                    # Check constitutional compliance
                    if result.get("constitutional_compliance_score", 1.0) < 0.95:
                        self.results["constitutional_violations"] += 1
                else:
                    self.results["errors"].append(
                        f"Request {i}: HTTP {response.status_code}"
                    )

            except Exception as e:
                self.results["errors"].append(f"Request {i}: {str(e)}")

            # Small delay to avoid overwhelming the service
            if i % 10 == 0:
                await asyncio.sleep(0.01)

        self.results["decision_latencies"] = latencies
        return self._calculate_latency_metrics(latencies)

    async def test_concurrent_load(
        self, concurrent_requests: int = 20, duration_seconds: int = 10
    ) -> Dict[str, Any]:
        """Test concurrent load on HITL service."""
        print(
            f"🔥 Testing concurrent load: {concurrent_requests} concurrent requests for {duration_seconds}s..."
        )

        async def make_concurrent_request(request_id: int):
            """Make a single concurrent request."""
            try:
                test_request = {
                    "agent_id": f"concurrent-agent-{request_id}",
                    "agent_type": "autonomous_coder",
                    "operation_type": "file_operation",
                    "operation_description": f"Concurrent test operation {request_id}",
                    "operation_context": {
                        "operation_id": f"concurrent-{request_id}",
                        "timestamp": datetime.utcnow().isoformat(),
                        "constitutional_hash": "cdd01ef066bc6cf2",
                    },
                }

                start_time = time.perf_counter()
                response = await self.client.post(
                    f"{HITL_SERVICE_URL}/api/v1/reviews/evaluate", json=test_request
                )
                end_time = time.perf_counter()

                return {
                    "latency_ms": (end_time - start_time) * 1000,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                }
            except Exception as e:
                return {
                    "latency_ms": None,
                    "status_code": None,
                    "success": False,
                    "error": str(e),
                }

        # Run concurrent requests for specified duration
        start_time = time.time()
        all_results = []

        while time.time() - start_time < duration_seconds:
            # Launch concurrent requests
            tasks = [make_concurrent_request(i) for i in range(concurrent_requests)]
            batch_results = await asyncio.gather(*tasks)
            all_results.extend(batch_results)

            # Small delay between batches
            await asyncio.sleep(0.1)

        # Analyze results
        successful_requests = [r for r in all_results if r["success"]]
        failed_requests = [r for r in all_results if not r["success"]]
        latencies = [
            r["latency_ms"] for r in successful_requests if r["latency_ms"] is not None
        ]

        return {
            "total_requests": len(all_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": (
                len(successful_requests) / len(all_results) if all_results else 0
            ),
            "latency_metrics": (
                self._calculate_latency_metrics(latencies) if latencies else {}
            ),
            "errors": [r.get("error") for r in failed_requests if r.get("error")],
        }

    async def test_constitutional_compliance(self) -> Dict[str, Any]:
        """Test constitutional compliance validation."""
        print("⚖️ Testing constitutional compliance validation...")

        # Test with valid constitutional hash
        valid_request = {
            "agent_id": "compliance-test-agent",
            "agent_type": "autonomous_coder",
            "operation_type": "policy_validation",
            "operation_description": "Test constitutional compliance",
            "operation_context": {
                "constitutional_hash": "cdd01ef066bc6cf2",  # Valid hash
                "compliance_check": True,
            },
        }

        # Test with invalid constitutional hash
        invalid_request = {
            "agent_id": "compliance-test-agent-invalid",
            "agent_type": "autonomous_coder",
            "operation_type": "policy_validation",
            "operation_description": "Test constitutional compliance with invalid hash",
            "operation_context": {
                "constitutional_hash": "invalid-hash-12345",  # Invalid hash
                "compliance_check": True,
            },
        }

        results = {"valid_hash_test": None, "invalid_hash_test": None}

        try:
            # Test valid hash
            response = await self.client.post(
                f"{HITL_SERVICE_URL}/api/v1/reviews/evaluate", json=valid_request
            )
            if response.status_code == 200:
                result = response.json()
                results["valid_hash_test"] = {
                    "constitutional_compliance_score": result.get(
                        "constitutional_compliance_score"
                    ),
                    "escalation_level": result.get("escalation_level"),
                    "passed": result.get("constitutional_compliance_score", 0) >= 0.95,
                }

            # Test invalid hash
            response = await self.client.post(
                f"{HITL_SERVICE_URL}/api/v1/reviews/evaluate", json=invalid_request
            )
            if response.status_code == 200:
                result = response.json()
                results["invalid_hash_test"] = {
                    "constitutional_compliance_score": result.get(
                        "constitutional_compliance_score"
                    ),
                    "escalation_level": result.get("escalation_level"),
                    "escalated": result.get("escalation_level", 0)
                    > 2,  # Should escalate
                }

        except Exception as e:
            results["error"] = str(e)

        return results

    def _calculate_latency_metrics(self, latencies: List[float]) -> Dict[str, float]:
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

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive HITL performance test suite."""
        print("🧪 Starting comprehensive HITL performance test suite...")
        self.results["test_start"] = datetime.utcnow().isoformat()

        # Test 1: Decision latency
        latency_results = await self.test_decision_latency(50)

        # Test 2: Concurrent load
        load_results = await self.test_concurrent_load(10, 5)

        # Test 3: Constitutional compliance
        compliance_results = await self.test_constitutional_compliance()

        self.results["test_end"] = datetime.utcnow().isoformat()

        # Compile final results
        final_results = {
            "test_summary": {
                "test_start": self.results["test_start"],
                "test_end": self.results["test_end"],
                "total_errors": len(self.results["errors"]),
                "automated_decisions": self.results["automated_decisions"],
                "human_escalations": self.results["human_escalations"],
                "constitutional_violations": self.results["constitutional_violations"],
            },
            "latency_test": latency_results,
            "load_test": load_results,
            "compliance_test": compliance_results,
            "performance_targets": {
                "p99_latency_target_ms": 5.0,
                "p99_latency_achieved_ms": latency_results.get("p99_ms", float("inf")),
                "p99_target_met": latency_results.get("p99_ms", float("inf")) <= 5.0,
                "constitutional_compliance_target": 0.95,
                "constitutional_compliance_rate": 1.0
                - (
                    self.results["constitutional_violations"]
                    / max(
                        1,
                        self.results["automated_decisions"]
                        + self.results["human_escalations"],
                    )
                ),
            },
            "errors": self.results["errors"],
        }

        return final_results

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main test execution."""
    tester = HITLPerformanceTester()

    try:
        # Check if HITL service is available
        response = await tester.client.get(f"{HITL_SERVICE_URL}/health")
        if response.status_code != 200:
            print(f"❌ HITL service not available at {HITL_SERVICE_URL}")
            return

        print(f"✅ HITL service available at {HITL_SERVICE_URL}")

        # Run comprehensive tests
        results = await tester.run_comprehensive_test()

        # Print results
        print("\n" + "=" * 80)
        print("🎯 HITL PERFORMANCE TEST RESULTS")
        print("=" * 80)

        print(f"\n📊 Test Summary:")
        summary = results["test_summary"]
        print(f"  • Test Duration: {summary['test_start']} to {summary['test_end']}")
        print(f"  • Total Errors: {summary['total_errors']}")
        print(f"  • Automated Decisions: {summary['automated_decisions']}")
        print(f"  • Human Escalations: {summary['human_escalations']}")
        print(f"  • Constitutional Violations: {summary['constitutional_violations']}")

        print(f"\n⚡ Latency Performance:")
        latency = results["latency_test"]
        if latency:
            print(f"  • Mean Latency: {latency.get('mean_ms', 0):.2f}ms")
            print(f"  • P95 Latency: {latency.get('p95_ms', 0):.2f}ms")
            print(f"  • P99 Latency: {latency.get('p99_ms', 0):.2f}ms")
            print(f"  • Max Latency: {latency.get('max_ms', 0):.2f}ms")

        print(f"\n🔥 Load Test Results:")
        load = results["load_test"]
        print(f"  • Total Requests: {load.get('total_requests', 0)}")
        print(f"  • Success Rate: {load.get('success_rate', 0)*100:.1f}%")
        if load.get("latency_metrics"):
            print(
                f"  • P99 Under Load: {load['latency_metrics'].get('p99_ms', 0):.2f}ms"
            )

        print(f"\n⚖️ Constitutional Compliance:")
        compliance = results["compliance_test"]
        if compliance.get("valid_hash_test"):
            print(
                f"  • Valid Hash Test: {'✅ PASSED' if compliance['valid_hash_test'].get('passed') else '❌ FAILED'}"
            )
        if compliance.get("invalid_hash_test"):
            print(
                f"  • Invalid Hash Escalation: {'✅ ESCALATED' if compliance['invalid_hash_test'].get('escalated') else '❌ NOT ESCALATED'}"
            )

        print(f"\n🎯 Performance Targets:")
        targets = results["performance_targets"]
        print(f"  • P99 Latency Target: {targets['p99_latency_target_ms']}ms")
        print(f"  • P99 Latency Achieved: {targets['p99_latency_achieved_ms']:.2f}ms")
        print(
            f"  • P99 Target Met: {'✅ YES' if targets['p99_target_met'] else '❌ NO'}"
        )
        print(
            f"  • Constitutional Compliance Rate: {targets['constitutional_compliance_rate']*100:.1f}%"
        )

        if results["errors"]:
            print(f"\n❌ Errors Encountered:")
            for error in results["errors"][:5]:  # Show first 5 errors
                print(f"  • {error}")
            if len(results["errors"]) > 5:
                print(f"  • ... and {len(results['errors']) - 5} more errors")

        # Save detailed results
        with open("hitl_performance_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Detailed results saved to: hitl_performance_test_results.json")

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
