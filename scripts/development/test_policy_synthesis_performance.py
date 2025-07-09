#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Policy Synthesis Engine Performance Test for ACGS-1

Tests the optimized Policy Synthesis Engine performance with four-tier risk strategy,
multi-model consensus, and LLM ensemble optimizations.
Target: <2s response times for policy synthesis operations.
"""

import asyncio
import json
import logging
import os
import statistics
import sys
import time
from typing import Any

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services", "shared"))

from policy_synthesis_performance_optimizer import (
    OptimizationLevel,
    PolicySynthesisPerformanceOptimizer,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolicySynthesisPerformanceTester:
    """
    Comprehensive performance tester for Policy Synthesis Engine.

    Tests all four risk strategies with performance optimizations
    and validates <2s response time targets.
    """

    def __init__(self):
        """Initialize performance tester."""
        self.test_policies = self._generate_test_policies()
        self.results = {}

    def _generate_test_policies(self) -> list[dict[str, Any]]:
        """Generate test policies for different risk levels."""
        return [
            {
                "title": "Standard Risk Policy",
                "description": "Basic governance policy for standard operations",
                "constitutional_principles": ["transparency", "accountability"],
                "risk_level": "low",
                "complexity": "simple",
                "expected_strategy": "standard",
            },
            {
                "title": "Enhanced Validation Policy",
                "description": "Medium-risk policy requiring enhanced validation",
                "constitutional_principles": [
                    "democratic_governance",
                    "transparency",
                    "fairness",
                ],
                "risk_level": "medium",
                "complexity": "moderate",
                "expected_strategy": "enhanced_validation",
            },
            {
                "title": "Multi-Model Consensus Policy",
                "description": "High-risk constitutional governance policy requiring consensus",
                "constitutional_principles": [
                    "constitutional_integrity",
                    "democratic_governance",
                    "separation_of_powers",
                ],
                "risk_level": "high",
                "complexity": "complex",
                "expected_strategy": "multi_model_consensus",
            },
            {
                "title": "Human Review Policy",
                "description": "Critical constitutional amendment requiring human oversight",
                "constitutional_principles": [
                    "constitutional_integrity",
                    "democratic_governance",
                    "rule_of_law",
                    "separation_of_powers",
                ],
                "risk_level": "critical",
                "complexity": "very_complex",
                "expected_strategy": "human_review",
            },
        ]

    async def test_optimization_levels(self) -> dict[str, Any]:
        """Test all optimization levels."""
        logger.info("🚀 Testing Policy Synthesis Engine optimization levels...")

        optimization_results = {}

        for level in [
            OptimizationLevel.BASIC,
            OptimizationLevel.ENHANCED,
            OptimizationLevel.MAXIMUM,
        ]:
            logger.info(f"Testing {level.value} optimization level...")

            optimizer = PolicySynthesisPerformanceOptimizer(level)
            await optimizer.initialize()

            try:
                level_results = await self._test_single_optimization_level(
                    optimizer, level
                )
                optimization_results[level.value] = level_results

            finally:
                await optimizer.close()

        return optimization_results

    async def _test_single_optimization_level(
        self, optimizer: PolicySynthesisPerformanceOptimizer, level: OptimizationLevel
    ) -> dict[str, Any]:
        """Test single optimization level with all policies."""
        level_results = {
            "optimization_level": level.value,
            "policy_results": [],
            "performance_summary": {},
        }

        response_times = []

        for policy in self.test_policies:
            logger.info(
                f"Testing policy: {policy['title']} ({policy['risk_level']} risk)"
            )

            start_time = time.time()

            try:
                # Test multi-model consensus
                models = [
                    "qwen3_32b_groq",
                    "deepseek_chat_v3",
                    "qwen3_235b",
                    "deepseek_r1",
                ]
                result = await optimizer.optimize_multi_model_consensus(
                    policy, models, "weighted_confidence"
                )

                response_time = time.time() - start_time
                response_times.append(response_time)

                policy_result = {
                    "policy_title": policy["title"],
                    "risk_level": policy["risk_level"],
                    "response_time_ms": response_time * 1000,
                    "success": True,
                    "consensus_score": result.get("consensus_result", {}).get(
                        "final_compliance_score", 0.0
                    ),
                    "confidence_score": result.get("consensus_result", {}).get(
                        "final_confidence_score", 0.0
                    ),
                    "agreement_score": result.get("consensus_result", {}).get(
                        "agreement_score", 0.0
                    ),
                    "participating_models": result.get("consensus_result", {}).get(
                        "participating_models", []
                    ),
                    "target_met": response_time < 2.0,
                }

                level_results["policy_results"].append(policy_result)

                logger.info(
                    f"✅ {policy['title']}: {response_time * 1000:.1f}ms (Target: <2000ms)"
                )

            except Exception as e:
                response_time = time.time() - start_time
                response_times.append(response_time)

                policy_result = {
                    "policy_title": policy["title"],
                    "risk_level": policy["risk_level"],
                    "response_time_ms": response_time * 1000,
                    "success": False,
                    "error": str(e),
                    "target_met": False,
                }

                level_results["policy_results"].append(policy_result)
                logger.error(f"❌ {policy['title']}: Failed - {e}")

        # Calculate performance summary
        if response_times:
            level_results["performance_summary"] = {
                "avg_response_time_ms": statistics.mean(response_times) * 1000,
                "p95_response_time_ms": (
                    statistics.quantiles(response_times, n=20)[18] * 1000
                    if len(response_times) >= 20
                    else max(response_times) * 1000
                ),
                "min_response_time_ms": min(response_times) * 1000,
                "max_response_time_ms": max(response_times) * 1000,
                "total_policies_tested": len(response_times),
                "policies_under_2s": sum(1 for t in response_times if t < 2.0),
                "target_achievement_rate": sum(1 for t in response_times if t < 2.0)
                / len(response_times)
                * 100,
            }

        return level_results

    async def test_concurrent_synthesis(
        self, concurrent_requests: int = 10
    ) -> dict[str, Any]:
        """Test concurrent policy synthesis performance."""
        logger.info(
            f"🔄 Testing concurrent synthesis with {concurrent_requests} requests..."
        )

        optimizer = PolicySynthesisPerformanceOptimizer(OptimizationLevel.ENHANCED)
        await optimizer.initialize()

        try:
            # Create concurrent synthesis tasks
            async def single_synthesis_task(policy_index: int):
                policy = self.test_policies[policy_index % len(self.test_policies)]
                start_time = time.time()

                try:
                    models = [
                        "qwen3_32b_groq",
                        "deepseek_chat_v3",
                    ]  # Use fewer models for concurrency test
                    result = await optimizer.optimize_multi_model_consensus(
                        policy, models, "weighted_confidence"
                    )

                    response_time = time.time() - start_time

                    return {
                        "task_id": policy_index,
                        "policy_title": policy["title"],
                        "response_time_ms": response_time * 1000,
                        "success": True,
                        "consensus_score": result.get("consensus_result", {}).get(
                            "final_compliance_score", 0.0
                        ),
                    }

                except Exception as e:
                    response_time = time.time() - start_time
                    return {
                        "task_id": policy_index,
                        "policy_title": policy["title"],
                        "response_time_ms": response_time * 1000,
                        "success": False,
                        "error": str(e),
                    }

            # Execute concurrent tasks
            start_time = time.time()
            tasks = [single_synthesis_task(i) for i in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time

            # Process results
            successful_results = [
                r for r in results if isinstance(r, dict) and r.get("success", False)
            ]
            failed_results = [
                r
                for r in results
                if isinstance(r, dict) and not r.get("success", False)
            ]

            response_times = [r["response_time_ms"] for r in successful_results]

            concurrent_results = {
                "concurrent_requests": concurrent_requests,
                "total_execution_time_ms": total_time * 1000,
                "successful_requests": len(successful_results),
                "failed_requests": len(failed_results),
                "success_rate": len(successful_results) / concurrent_requests * 100,
                "individual_results": results[:5],  # First 5 results for inspection
                "performance_metrics": {},
            }

            if response_times:
                concurrent_results["performance_metrics"] = {
                    "avg_response_time_ms": statistics.mean(response_times),
                    "p95_response_time_ms": (
                        statistics.quantiles(response_times, n=20)[18]
                        if len(response_times) >= 20
                        else max(response_times)
                    ),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                    "requests_under_2s": sum(1 for t in response_times if t < 2000),
                    "concurrent_target_achievement_rate": sum(
                        1 for t in response_times if t < 2000
                    )
                    / len(response_times)
                    * 100,
                }

            return concurrent_results

        finally:
            await optimizer.close()

    async def test_cache_performance(self) -> dict[str, Any]:
        """Test caching performance improvements."""
        logger.info("🗄️ Testing cache performance...")

        optimizer = PolicySynthesisPerformanceOptimizer(OptimizationLevel.ENHANCED)
        await optimizer.initialize()

        try:
            test_policy = self.test_policies[0]  # Use first policy for cache test
            models = ["qwen3_32b_groq", "deepseek_chat_v3"]

            # First request (cache miss)
            start_time = time.time()
            await optimizer.optimize_multi_model_consensus(
                test_policy, models, "weighted_confidence"
            )
            first_request_time = time.time() - start_time

            # Second request (cache hit)
            start_time = time.time()
            await optimizer.optimize_multi_model_consensus(
                test_policy, models, "weighted_confidence"
            )
            second_request_time = time.time() - start_time

            # Calculate cache improvement
            cache_improvement = (
                (first_request_time - second_request_time) / first_request_time * 100
            )

            return {
                "first_request_time_ms": first_request_time * 1000,
                "second_request_time_ms": second_request_time * 1000,
                "cache_improvement_percentage": cache_improvement,
                "cache_effective": second_request_time < first_request_time,
                "performance_report": await optimizer.get_performance_report(),
            }

        finally:
            await optimizer.close()

    async def run_comprehensive_performance_test(self) -> dict[str, Any]:
        """Run comprehensive performance test suite."""
        logger.info(
            "🏁 Starting comprehensive Policy Synthesis Engine performance test..."
        )

        test_results = {
            "test_timestamp": time.time(),
            "performance_targets": {
                "response_time_target_ms": 2000,
                "success_rate_target": 95.0,
                "concurrent_support_target": 10,
            },
        }

        # Test 1: Optimization levels
        test_results["optimization_levels"] = await self.test_optimization_levels()

        # Test 2: Concurrent synthesis
        test_results["concurrent_synthesis"] = await self.test_concurrent_synthesis(10)

        # Test 3: Cache performance
        test_results["cache_performance"] = await self.test_cache_performance()

        # Calculate overall performance score
        test_results["overall_assessment"] = self._calculate_overall_performance(
            test_results
        )

        return test_results

    def _calculate_overall_performance(self, results: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall performance assessment."""
        score = 100
        issues = []

        # Check optimization level performance
        enhanced_results = results.get("optimization_levels", {}).get("enhanced", {})
        enhanced_summary = enhanced_results.get("performance_summary", {})

        avg_response_time = enhanced_summary.get("avg_response_time_ms", 0)
        target_achievement_rate = enhanced_summary.get("target_achievement_rate", 0)

        if avg_response_time > 2000:
            score -= 30
            issues.append(
                f"Average response time {avg_response_time:.1f}ms > 2000ms target"
            )

        if target_achievement_rate < 95:
            score -= 25
            issues.append(
                f"Target achievement rate {target_achievement_rate:.1f}% < 95% target"
            )

        # Check concurrent performance
        concurrent_results = results.get("concurrent_synthesis", {})
        concurrent_success_rate = concurrent_results.get("success_rate", 0)

        if concurrent_success_rate < 95:
            score -= 20
            issues.append(
                f"Concurrent success rate {concurrent_success_rate:.1f}% < 95% target"
            )

        # Check cache effectiveness
        cache_results = results.get("cache_performance", {})
        cache_effective = cache_results.get("cache_effective", False)

        if not cache_effective:
            score -= 15
            issues.append("Cache performance not effective")

        return {
            "overall_score": max(0, score),
            "performance_grade": (
                "A"
                if score >= 90
                else "B" if score >= 80 else "C" if score >= 70 else "D"
            ),
            "targets_met": score >= 90,
            "issues": issues,
            "recommendations": [
                "Monitor response times continuously",
                "Optimize model selection for performance",
                "Implement adaptive caching strategies",
                "Consider model ensemble optimization",
            ],
        }


async def main():
    """Main performance test execution."""
    tester = PolicySynthesisPerformanceTester()

    try:
        results = await tester.run_comprehensive_performance_test()

        # Save results
        with open("policy_synthesis_performance_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Display summary
        assessment = results["overall_assessment"]
        print("\n" + "=" * 80)
        print("🏁 Policy Synthesis Engine Performance Test Results")
        print("=" * 80)
        print(
            f"Overall Score: {assessment['overall_score']}/100 (Grade: {assessment['performance_grade']})"
        )
        print(f"Targets Met: {'✅ YES' if assessment['targets_met'] else '❌ NO'}")

        # Show optimization level results
        enhanced_results = results.get("optimization_levels", {}).get("enhanced", {})
        enhanced_summary = enhanced_results.get("performance_summary", {})

        if enhanced_summary:
            print("\n📊 Enhanced Optimization Level Performance:")
            print(
                f"   Average Response Time: {enhanced_summary.get('avg_response_time_ms', 0):.1f}ms"
            )
            print(
                f"   Target Achievement Rate: {enhanced_summary.get('target_achievement_rate', 0):.1f}%"
            )
            print(
                f"   Policies Under 2s: {enhanced_summary.get('policies_under_2s', 0)}/{enhanced_summary.get('total_policies_tested', 0)}"
            )

        # Show concurrent results
        concurrent_results = results.get("concurrent_synthesis", {})
        if concurrent_results:
            print("\n🔄 Concurrent Synthesis Performance:")
            print(f"   Success Rate: {concurrent_results.get('success_rate', 0):.1f}%")
            print(
                f"   Concurrent Requests: {concurrent_results.get('concurrent_requests', 0)}"
            )

            concurrent_metrics = concurrent_results.get("performance_metrics", {})
            if concurrent_metrics:
                print(
                    f"   Avg Response Time: {concurrent_metrics.get('avg_response_time_ms', 0):.1f}ms"
                )

        # Show cache results
        cache_results = results.get("cache_performance", {})
        if cache_results:
            print("\n🗄️ Cache Performance:")
            print(
                f"   Cache Improvement: {cache_results.get('cache_improvement_percentage', 0):.1f}%"
            )
            print(
                f"   Cache Effective: {'✅ YES' if cache_results.get('cache_effective', False) else '❌ NO'}"
            )

        if assessment["issues"]:
            print("\n⚠️ Issues Found:")
            for issue in assessment["issues"]:
                print(f"   - {issue}")

        print("\n📄 Detailed results saved: policy_synthesis_performance_results.json")
        print("=" * 80)

        return assessment["targets_met"]

    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
