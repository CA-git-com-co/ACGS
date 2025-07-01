"""
Router Optimization Load Testing for gs-service

This module provides comprehensive load testing for the enhanced multi-model coordinator
with router optimization, targeting 97.2% consensus success rate and performance validation.
"""

import asyncio
import json
import logging
import statistics
import time
from typing import Any

# Test configuration
TEST_CONFIG = {
    "concurrent_requests": 20,
    "total_requests": 100,
    "target_response_time_ms": 2000,
    "target_consensus_rate": 0.972,
    "redis_url": "redis://localhost:6379/0",
}

# Sample synthesis requests for testing
SAMPLE_REQUESTS = [
    {
        "type": "simple",
        "policy_type": "access_control",
        "description": "Basic user access policy",
        "stakeholders": ["users"],
        "constitutional_principles": ["fairness"],
    },
    {
        "type": "complex",
        "policy_type": "governance_framework",
        "description": "Multi-stakeholder governance policy with consensus requirements",
        "stakeholders": ["users", "administrators", "auditors"],
        "constitutional_principles": ["transparency", "accountability", "fairness"],
    },
    {
        "type": "high_stakes",
        "policy_type": "security_compliance",
        "description": "Critical security policy for constitutional compliance",
        "stakeholders": ["security_team", "legal", "executives"],
        "constitutional_principles": [
            "security",
            "constitutional_compliance",
            "audit_trail",
        ],
    },
]


class RouterOptimizationTester:
    """Load tester for router optimization validation."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.results: list[dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)

    async def run_load_test(self) -> dict[str, Any]:
        """Execute comprehensive load test."""
        self.logger.info("Starting router optimization load test...")

        # Import the coordinator here to avoid import issues during testing
        import os
        import sys

        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))
        try:
            from core.multi_model_coordinator import MultiModelCoordinator
        except ImportError:
            # Fallback for direct execution
            sys.path.append(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
            )
            from services.core.governance_synthesis.gs_service.app.core.multi_model_coordinator import (
                MultiModelCoordinator,
            )

        # Initialize coordinator with test configuration
        coordinator_config = {
            "primary_model": "gemini-2.5-pro",
            "fallback_models": ["gemini-2.0-flash", "deepseek-r1"],
            "ensemble_strategy": "weighted_voting",
            "cache_enabled": True,
            "redis_url": self.config["redis_url"],
            "target_response_time_ms": 200,
        }

        coordinator = MultiModelCoordinator(coordinator_config)
        await coordinator.initialize()

        # Execute concurrent load test
        start_time = time.time()

        tasks = []
        for i in range(self.config["total_requests"]):
            request = SAMPLE_REQUESTS[i % len(SAMPLE_REQUESTS)]
            task = self._execute_synthesis_request(coordinator, request, i)
            tasks.append(task)

            # Control concurrency
            if len(tasks) >= self.config["concurrent_requests"]:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                self._process_batch_results(batch_results)
                tasks = []

        # Process remaining tasks
        if tasks:
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            self._process_batch_results(batch_results)

        total_time = time.time() - start_time

        # Generate comprehensive test report
        return self._generate_test_report(total_time, coordinator)

    async def _execute_synthesis_request(
        self, coordinator, request: dict[str, Any], request_id: int
    ) -> dict[str, Any]:
        """Execute single synthesis request with timing."""
        start_time = time.time()

        try:
            result = await coordinator.coordinate_synthesis(request, enable_wina=True)

            execution_time = (time.time() - start_time) * 1000

            return {
                "request_id": request_id,
                "success": True,
                "execution_time_ms": execution_time,
                "confidence_score": result.confidence_score,
                "constitutional_fidelity": result.constitutional_fidelity,
                "contributing_models": result.contributing_models,
                "ensemble_strategy": result.ensemble_strategy_used.value,
                "wina_optimization": result.wina_optimization_applied,
                "cache_hit": execution_time < 50,  # Assume cache hit if very fast
            }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.logger.error(f"Request {request_id} failed: {e}")

            return {
                "request_id": request_id,
                "success": False,
                "execution_time_ms": execution_time,
                "error": str(e),
            }

    def _process_batch_results(self, batch_results: list[Any]):
        """Process batch of results, handling exceptions."""
        for result in batch_results:
            if isinstance(result, Exception):
                self.logger.error(f"Batch execution error: {result}")
                self.results.append(
                    {"success": False, "error": str(result), "execution_time_ms": 0}
                )
            else:
                self.results.append(result)

    def _generate_test_report(self, total_time: float, coordinator) -> dict[str, Any]:
        """Generate comprehensive test report."""
        successful_results = [r for r in self.results if r.get("success", False)]
        failed_results = [r for r in self.results if not r.get("success", False)]

        if not successful_results:
            return {
                "status": "FAILED",
                "error": "No successful requests",
                "total_requests": len(self.results),
                "failed_requests": len(failed_results),
            }

        # Calculate performance metrics
        response_times = [r["execution_time_ms"] for r in successful_results]
        confidence_scores = [r["confidence_score"] for r in successful_results]
        fidelity_scores = [r["constitutional_fidelity"] for r in successful_results]

        # Cache performance
        cache_hits = sum(1 for r in successful_results if r.get("cache_hit", False))
        cache_hit_rate = (
            cache_hits / len(successful_results) if successful_results else 0
        )

        # Consensus success rate (confidence > 0.8)
        high_confidence_results = [
            r for r in successful_results if r["confidence_score"] > 0.8
        ]
        consensus_success_rate = len(high_confidence_results) / len(successful_results)

        # Performance summary from coordinator
        coordinator_summary = coordinator.get_performance_summary()

        report = {
            "status": (
                "PASSED"
                if consensus_success_rate >= self.config["target_consensus_rate"]
                else "FAILED"
            ),
            "test_duration_seconds": total_time,
            "total_requests": len(self.results),
            "successful_requests": len(successful_results),
            "failed_requests": len(failed_results),
            "success_rate": len(successful_results) / len(self.results),
            # Performance metrics
            "response_time_stats": {
                "mean_ms": statistics.mean(response_times),
                "median_ms": statistics.median(response_times),
                "p95_ms": self._percentile(response_times, 95),
                "p99_ms": self._percentile(response_times, 99),
                "max_ms": max(response_times),
                "target_met": statistics.mean(response_times)
                <= self.config["target_response_time_ms"],
            },
            # Quality metrics
            "consensus_metrics": {
                "success_rate": consensus_success_rate,
                "target_rate": self.config["target_consensus_rate"],
                "target_met": consensus_success_rate
                >= self.config["target_consensus_rate"],
                "mean_confidence": statistics.mean(confidence_scores),
                "mean_fidelity": statistics.mean(fidelity_scores),
            },
            # Cache performance
            "cache_performance": {
                "hit_rate": cache_hit_rate,
                "total_hits": cache_hits,
                "enabled": coordinator_summary.get("cache_enabled", False),
            },
            # Model utilization
            "model_utilization": coordinator_summary.get("model_metrics", {}),
            # Recommendations
            "recommendations": self._generate_recommendations(
                consensus_success_rate, statistics.mean(response_times), cache_hit_rate
            ),
        }

        return report

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _generate_recommendations(
        self, consensus_rate: float, avg_response_time: float, cache_hit_rate: float
    ) -> list[str]:
        """Generate optimization recommendations."""
        recommendations = []

        if consensus_rate < self.config["target_consensus_rate"]:
            recommendations.append(
                f"Consensus success rate ({consensus_rate:.3f}) below target "
                f"({self.config['target_consensus_rate']:.3f}). Consider tuning ensemble weights."
            )

        if avg_response_time > self.config["target_response_time_ms"]:
            recommendations.append(
                f"Average response time ({avg_response_time:.1f}ms) exceeds target "
                f"({self.config['target_response_time_ms']}ms). Consider optimizing model selection."
            )

        if cache_hit_rate < 0.3:
            recommendations.append(
                f"Cache hit rate ({cache_hit_rate:.3f}) is low. Consider increasing cache TTL "
                "or improving cache key generation."
            )

        if not recommendations:
            recommendations.append("All performance targets met. System is optimized.")

        return recommendations


async def main():
    """Main test execution function."""
    logging.basicConfig(level=logging.INFO)

    tester = RouterOptimizationTester(TEST_CONFIG)
    report = await tester.run_load_test()

    print("\n" + "=" * 80)
    print("ROUTER OPTIMIZATION LOAD TEST REPORT")
    print("=" * 80)
    print(json.dumps(report, indent=2))
    print("=" * 80)

    return report["status"] == "PASSED"


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
