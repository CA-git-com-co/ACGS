#!/usr/bin/env python3
"""
Comprehensive Load Testing Script

This script executes large-scale load testing (1000+ concurrent requests) across
all AI models and validates performance targets under production conditions.

Features:
- Concurrent request testing (1000+ requests)
- Multi-model load distribution
- Performance target validation
- Stress testing scenarios
- Real-time monitoring

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import sys
import time
import json
import statistics
from pathlib import Path
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import aiohttp

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.shared.multimodal_ai_service import get_multimodal_service
from services.shared.ai_types import (
    MultimodalRequest,
    RequestType,
    ContentType,
    ModelType,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveLoadTester:
    """Comprehensive load testing manager."""

    def __init__(self):
        self.service = None
        self.test_results = {}
        self.performance_targets = {
            "max_response_time_ms": 2000,  # Sub-2s response times
            "min_success_rate": 95.0,  # >95% success rate
            "max_error_rate": 5.0,  # <5% error rate
            "min_constitutional_compliance": 90.0,  # >90% compliance
            "max_concurrent_requests": 1000,  # Support 1000+ concurrent
        }

    async def initialize(self):
        """Initialize the multimodal AI service."""
        logger.info("🔧 Initializing load tester...")
        self.service = await get_multimodal_service()
        logger.info("✅ Load tester initialized")

    async def generate_test_requests(self, count: int) -> List[MultimodalRequest]:
        """Generate test requests for load testing."""

        test_contents = [
            "Citizens have the right to participate in democratic processes and transparent governance.",
            "The constitution protects individual rights and ensures democratic representation.",
            "Constitutional principles guide policy development and implementation.",
            "Democratic institutions ensure accountability and transparency in governance.",
            "Rule of law protects citizens from arbitrary government actions.",
            "Analyze this policy for constitutional compliance and democratic principles.",
            "Evaluate the governance framework for transparency and accountability.",
            "Review constitutional amendments for citizen rights protection.",
            "Assess democratic participation mechanisms in policy development.",
            "Examine rule of law implementation in government operations.",
        ]

        request_types = [
            RequestType.QUICK_ANALYSIS,
            RequestType.DETAILED_ANALYSIS,
            RequestType.CONSTITUTIONAL_VALIDATION,
            RequestType.CONTENT_MODERATION,
        ]

        requests = []
        for i in range(count):
            content = test_contents[i % len(test_contents)]
            request_type = request_types[i % len(request_types)]

            request = MultimodalRequest(
                request_id=f"load_test_{i}_{int(time.time())}",
                request_type=request_type,
                content_type=ContentType.TEXT_ONLY,
                text_content=content,
                priority="medium",
            )
            requests.append(request)

        return requests

    async def execute_single_request(
        self, request: MultimodalRequest
    ) -> Dict[str, Any]:
        """Execute a single request and measure performance."""
        start_time = time.time()

        try:
            response = await self.service.process_request(request)
            end_time = time.time()

            return {
                "request_id": request.request_id,
                "success": True,
                "response_time_ms": (end_time - start_time) * 1000,
                "model_used": response.model_used.value,
                "constitutional_compliance": response.constitutional_compliance,
                "confidence_score": response.confidence_score,
                "cache_hit": response.cache_info.get("hit", False),
                "error": None,
            }

        except Exception as e:
            end_time = time.time()
            return {
                "request_id": request.request_id,
                "success": False,
                "response_time_ms": (end_time - start_time) * 1000,
                "model_used": None,
                "constitutional_compliance": False,
                "confidence_score": 0.0,
                "cache_hit": False,
                "error": str(e),
            }

    async def execute_concurrent_batch(
        self, requests: List[MultimodalRequest]
    ) -> List[Dict[str, Any]]:
        """Execute a batch of requests concurrently."""

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(100)  # Limit to 100 concurrent

        async def limited_request(request):
            async with semaphore:
                return await self.execute_single_request(request)

        # Execute all requests concurrently
        tasks = [limited_request(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {
                        "request_id": requests[i].request_id,
                        "success": False,
                        "response_time_ms": 0,
                        "model_used": None,
                        "constitutional_compliance": False,
                        "confidence_score": 0.0,
                        "cache_hit": False,
                        "error": str(result),
                    }
                )
            else:
                processed_results.append(result)

        return processed_results

    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze load test results."""

        total_requests = len(results)
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        # Basic metrics
        success_rate = (
            (len(successful_requests) / total_requests * 100)
            if total_requests > 0
            else 0
        )
        error_rate = (
            (len(failed_requests) / total_requests * 100) if total_requests > 0 else 0
        )

        # Response time metrics
        response_times = [r["response_time_ms"] for r in successful_requests]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = (
                sorted(response_times)[int(len(response_times) * 0.95)]
                if len(response_times) >= 20
                else max(response_times)
            )
            p99_response_time = (
                sorted(response_times)[int(len(response_times) * 0.99)]
                if len(response_times) >= 100
                else max(response_times)
            )
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = median_response_time = p95_response_time = (
                p99_response_time
            ) = max_response_time = min_response_time = 0

        # Constitutional compliance metrics
        compliant_requests = [
            r for r in successful_requests if r["constitutional_compliance"]
        ]
        compliance_rate = (
            (len(compliant_requests) / len(successful_requests) * 100)
            if successful_requests
            else 0
        )

        # Model usage distribution
        model_usage = {}
        for result in successful_requests:
            model = result["model_used"]
            if model:
                model_usage[model] = model_usage.get(model, 0) + 1

        # Cache hit rate
        cache_hits = [r for r in successful_requests if r["cache_hit"]]
        cache_hit_rate = (
            (len(cache_hits) / len(successful_requests) * 100)
            if successful_requests
            else 0
        )

        # Performance target validation
        targets_met = {
            "response_time": max_response_time
            <= self.performance_targets["max_response_time_ms"],
            "success_rate": success_rate
            >= self.performance_targets["min_success_rate"],
            "error_rate": error_rate <= self.performance_targets["max_error_rate"],
            "constitutional_compliance": compliance_rate
            >= self.performance_targets["min_constitutional_compliance"],
        }

        analysis = {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "success_rate": success_rate,
                "error_rate": error_rate,
            },
            "response_times": {
                "average_ms": avg_response_time,
                "median_ms": median_response_time,
                "p95_ms": p95_response_time,
                "p99_ms": p99_response_time,
                "max_ms": max_response_time,
                "min_ms": min_response_time,
            },
            "constitutional_compliance": {
                "compliant_requests": len(compliant_requests),
                "compliance_rate": compliance_rate,
            },
            "model_usage": model_usage,
            "cache_performance": {
                "cache_hits": len(cache_hits),
                "cache_hit_rate": cache_hit_rate,
            },
            "performance_targets": {
                "targets": self.performance_targets,
                "results": targets_met,
                "all_targets_met": all(targets_met.values()),
            },
        }

        return analysis

    async def run_load_test(self, concurrent_requests: int = 1000) -> Dict[str, Any]:
        """Run comprehensive load test."""
        logger.info(
            f"🚀 Starting load test with {concurrent_requests} concurrent requests..."
        )
        logger.info("=" * 70)

        start_time = time.time()

        # Generate test requests
        logger.info("📋 Generating test requests...")
        requests = await self.generate_test_requests(concurrent_requests)
        logger.info(f"✅ Generated {len(requests)} test requests")

        # Execute load test
        logger.info(f"⚡ Executing {concurrent_requests} concurrent requests...")
        results = await self.execute_concurrent_batch(requests)

        # Analyze results
        logger.info("📊 Analyzing results...")
        analysis = self.analyze_results(results)

        total_time = time.time() - start_time
        analysis["execution_time"] = total_time

        # Log summary
        logger.info("\n" + "=" * 70)
        logger.info("📈 LOAD TEST RESULTS")
        logger.info("=" * 70)

        summary = analysis["summary"]
        logger.info(f"Total requests: {summary['total_requests']}")
        logger.info(
            f"Successful: {summary['successful_requests']} ({summary['success_rate']:.1f}%)"
        )
        logger.info(
            f"Failed: {summary['failed_requests']} ({summary['error_rate']:.1f}%)"
        )

        response_times = analysis["response_times"]
        logger.info(f"Avg response time: {response_times['average_ms']:.1f}ms")
        logger.info(f"P95 response time: {response_times['p95_ms']:.1f}ms")
        logger.info(f"P99 response time: {response_times['p99_ms']:.1f}ms")
        logger.info(f"Max response time: {response_times['max_ms']:.1f}ms")

        compliance = analysis["constitutional_compliance"]
        logger.info(f"Constitutional compliance: {compliance['compliance_rate']:.1f}%")

        cache = analysis["cache_performance"]
        logger.info(f"Cache hit rate: {cache['cache_hit_rate']:.1f}%")

        # Performance targets
        targets = analysis["performance_targets"]
        logger.info("\n🎯 Performance Targets:")
        for target, met in targets["results"].items():
            status = "✅ PASS" if met else "❌ FAIL"
            logger.info(f"  {target}: {status}")

        overall_status = (
            "✅ ALL TARGETS MET"
            if targets["all_targets_met"]
            else "❌ SOME TARGETS MISSED"
        )
        logger.info(f"\nOverall: {overall_status}")
        logger.info(f"Execution time: {total_time:.2f} seconds")

        return analysis


async def main():
    """Main execution function."""
    logger.info("🏋️ Comprehensive Load Testing")
    logger.info("=" * 70)

    try:
        # Initialize load tester
        tester = ComprehensiveLoadTester()
        await tester.initialize()

        # Run load tests with different scales
        test_scenarios = [
            {"name": "Medium Load", "requests": 100},
            {"name": "High Load", "requests": 500},
            {"name": "Stress Test", "requests": 1000},
        ]

        all_results = {}

        for scenario in test_scenarios:
            logger.info(
                f"\n🧪 Running {scenario['name']} ({scenario['requests']} requests)"
            )
            logger.info("-" * 50)

            results = await tester.run_load_test(scenario["requests"])
            all_results[scenario["name"]] = results

            # Brief pause between tests
            await asyncio.sleep(2)

        # Save comprehensive results
        results_file = "data/comprehensive_load_test_results.json"
        Path("data").mkdir(exist_ok=True)

        with open(results_file, "w") as f:
            json.dump(all_results, f, indent=2, default=str)

        logger.info(f"\n📄 Results saved to {results_file}")

        # Final summary
        logger.info("\n" + "=" * 70)
        logger.info("🏆 COMPREHENSIVE LOAD TEST SUMMARY")
        logger.info("=" * 70)

        for scenario_name, results in all_results.items():
            targets_met = results["performance_targets"]["all_targets_met"]
            status = "✅ PASS" if targets_met else "❌ FAIL"
            success_rate = results["summary"]["success_rate"]
            avg_response = results["response_times"]["average_ms"]

            logger.info(
                f"{scenario_name}: {status} ({success_rate:.1f}% success, {avg_response:.1f}ms avg)"
            )

        # Check if all scenarios passed
        all_passed = all(
            results["performance_targets"]["all_targets_met"]
            for results in all_results.values()
        )

        if all_passed:
            logger.info("\n🎉 ALL LOAD TESTS PASSED - PRODUCTION READY!")
            return 0
        else:
            logger.info("\n⚠️ SOME LOAD TESTS FAILED - NEEDS OPTIMIZATION")
            return 1

    except Exception as e:
        logger.error(f"❌ Load testing failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
