"""
ACGS Human-in-the-Loop (HITL) Tests

Comprehensive tests for HITL decision processing, uncertainty assessment,
and sub-5ms P99 latency validation for human oversight integration.
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import statistics
import time
from typing import Any, Dict, List

from ..framework.base import E2ETestResult, PerformanceTest
from ..framework.config import ServiceType
from ..framework.utils import TestDataGenerator


class HITLLatencyTest(PerformanceTest):
    """Test HITL decision processing latency requirements."""

    test_type = "hitl"
    tags = ["hitl", "performance", "latency"]

    def __init__(self, config, load_duration_seconds: int = 30):
        super().__init__(config, load_duration_seconds)
        self.target_p99_latency_ms = 5.0  # Sub-5ms P99 requirement

    async def run_test(self) -> List[E2ETestResult]:
        """Run HITL latency tests."""
        results = []

        # Test uncertainty assessment latency
        result = await self._test_uncertainty_assessment_latency()
        results.append(result)

        # Test HITL decision latency under load
        result = await self._test_hitl_decision_latency_load()
        results.append(result)

        # Test concurrent HITL requests
        result = await self._test_concurrent_hitl_requests()
        results.append(result)

        return results

    async def _test_uncertainty_assessment_latency(self) -> E2ETestResult:
        """Test uncertainty assessment endpoint latency."""
        start_time = time.perf_counter()

        try:
            if not self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
                return E2ETestResult(
                    test_name="hitl_uncertainty_assessment_latency",
                    success=False,
                    duration_ms=0,
                    error_message="Constitutional AI service not enabled",
                )

            # Generate test data for uncertainty assessment
            test_request = {
                "request_id": "latency_test_uncertainty",
                "constitutional_hash": self.config.constitutional_hash,
                "decision_context": {
                    "policy_id": "test_policy_uncertainty",
                    "action": "policy_validation",
                    "complexity": "medium",
                },
                "confidence_threshold": 0.8,
            }

            # Measure multiple requests to get latency distribution
            latencies = []
            successful_requests = 0
            total_requests = 50  # Sample size for latency measurement

            for _ in range(total_requests):
                request_start = time.perf_counter()

                try:
                    response = await self.make_service_request(
                        ServiceType.CONSTITUTIONAL_AI,
                        "POST",
                        "/api/v1/hitl/assess",
                        json=test_request,
                    )

                    request_end = time.perf_counter()
                    request_latency_ms = (request_end - request_start) * 1000
                    latencies.append(request_latency_ms)

                    if response.status_code == 200:
                        successful_requests += 1

                except Exception:
                    request_end = time.perf_counter()
                    request_latency_ms = (request_end - request_start) * 1000
                    latencies.append(request_latency_ms)

            end_time = time.perf_counter()
            total_duration_ms = (end_time - start_time) * 1000

            # Calculate latency percentiles
            if latencies:
                latencies.sort()
                p50 = latencies[int(len(latencies) * 0.5)]
                p95 = latencies[int(len(latencies) * 0.95)]
                p99 = latencies[int(len(latencies) * 0.99)]
                avg_latency = statistics.mean(latencies)
            else:
                p50 = p95 = p99 = avg_latency = 0

            # Check if P99 latency meets requirement
            latency_requirement_met = p99 <= self.target_p99_latency_ms
            success_rate = (
                successful_requests / total_requests if total_requests > 0 else 0
            )

            overall_success = latency_requirement_met and success_rate >= 0.9

            return E2ETestResult(
                test_name="hitl_uncertainty_assessment_latency",
                success=overall_success,
                duration_ms=total_duration_ms,
                performance_metrics={
                    "p50_latency_ms": p50,
                    "p95_latency_ms": p95,
                    "p99_latency_ms": p99,
                    "average_latency_ms": avg_latency,
                    "success_rate": success_rate,
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "latency_requirement_met": latency_requirement_met,
                    "target_p99_latency_ms": self.target_p99_latency_ms,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="hitl_uncertainty_assessment_latency",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Uncertainty assessment latency test failed: {str(e)}",
            )

    async def _test_hitl_decision_latency_load(self) -> E2ETestResult:
        """Test HITL decision latency under sustained load."""
        start_time = time.perf_counter()

        try:
            if not self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
                return E2ETestResult(
                    test_name="hitl_decision_latency_load",
                    success=False,
                    duration_ms=0,
                    error_message="Constitutional AI service not enabled",
                )

            # Define load test function
            async def hitl_decision_request():
                test_request = {
                    "request_id": f"load_test_{time.time()}",
                    "constitutional_hash": self.config.constitutional_hash,
                    "decision_context": {
                        "policy_id": "load_test_policy",
                        "action": "governance_decision",
                        "urgency": "high",
                    },
                    "require_human_review": False,
                }

                response = await self.make_service_request(
                    ServiceType.CONSTITUTIONAL_AI,
                    "POST",
                    "/api/v1/hitl/assess",
                    json=test_request,
                )

                return response.status_code == 200

            # Run load test
            metrics = await self.run_load_test(
                hitl_decision_request, concurrent_requests=5
            )

            end_time = time.perf_counter()
            total_duration_ms = (end_time - start_time) * 1000

            # Check performance targets
            latency_target_met = metrics.latency_p99_ms <= self.target_p99_latency_ms
            throughput_target_met = (
                metrics.throughput_rps >= 10
            )  # Minimum 10 RPS for HITL
            success_rate_target_met = metrics.success_rate >= 0.95

            overall_success = (
                latency_target_met and throughput_target_met and success_rate_target_met
            )

            return E2ETestResult(
                test_name="hitl_decision_latency_load",
                success=overall_success,
                duration_ms=total_duration_ms,
                performance_metrics={
                    "p50_latency_ms": metrics.latency_p50_ms,
                    "p95_latency_ms": metrics.latency_p95_ms,
                    "p99_latency_ms": metrics.latency_p99_ms,
                    "throughput_rps": metrics.throughput_rps,
                    "success_rate": metrics.success_rate,
                    "latency_target_met": latency_target_met,
                    "throughput_target_met": throughput_target_met,
                    "success_rate_target_met": success_rate_target_met,
                    "target_p99_latency_ms": self.target_p99_latency_ms,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="hitl_decision_latency_load",
                success=False,
                duration_ms=duration_ms,
                error_message=f"HITL decision latency load test failed: {str(e)}",
            )

    async def _test_concurrent_hitl_requests(self) -> E2ETestResult:
        """Test concurrent HITL requests for latency consistency."""
        start_time = time.perf_counter()

        try:
            if not self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
                return E2ETestResult(
                    test_name="hitl_concurrent_requests",
                    success=False,
                    duration_ms=0,
                    error_message="Constitutional AI service not enabled",
                )

            # Generate multiple concurrent requests
            concurrent_requests = 10
            request_tasks = []

            for i in range(concurrent_requests):
                test_request = {
                    "request_id": f"concurrent_test_{i}",
                    "constitutional_hash": self.config.constitutional_hash,
                    "decision_context": {
                        "policy_id": f"concurrent_policy_{i}",
                        "action": "concurrent_validation",
                        "batch_id": "concurrent_batch",
                    },
                }

                task = self._measure_hitl_request_latency(test_request)
                request_tasks.append(task)

            # Execute all requests concurrently
            results = await asyncio.gather(*request_tasks, return_exceptions=True)

            end_time = time.perf_counter()
            total_duration_ms = (end_time - start_time) * 1000

            # Analyze results
            successful_results = [
                r for r in results if not isinstance(r, Exception) and r["success"]
            ]
            latencies = [r["latency_ms"] for r in successful_results]

            if latencies:
                latencies.sort()
                p99_latency = (
                    latencies[int(len(latencies) * 0.99)]
                    if len(latencies) > 1
                    else latencies[0]
                )
                avg_latency = statistics.mean(latencies)
                max_latency = max(latencies)
            else:
                p99_latency = avg_latency = max_latency = 0

            success_rate = len(successful_results) / concurrent_requests
            latency_consistency = p99_latency <= self.target_p99_latency_ms

            overall_success = success_rate >= 0.9 and latency_consistency

            return E2ETestResult(
                test_name="hitl_concurrent_requests",
                success=overall_success,
                duration_ms=total_duration_ms,
                performance_metrics={
                    "concurrent_requests": concurrent_requests,
                    "successful_requests": len(successful_results),
                    "success_rate": success_rate,
                    "p99_latency_ms": p99_latency,
                    "average_latency_ms": avg_latency,
                    "max_latency_ms": max_latency,
                    "latency_consistency": latency_consistency,
                    "target_p99_latency_ms": self.target_p99_latency_ms,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="hitl_concurrent_requests",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Concurrent HITL requests test failed: {str(e)}",
            )

    async def _measure_hitl_request_latency(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Measure latency for a single HITL request."""
        start_time = time.perf_counter()

        try:
            response = await self.make_service_request(
                ServiceType.CONSTITUTIONAL_AI,
                "POST",
                "/api/v1/hitl/assess",
                json=request_data,
            )

            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            return {
                "success": response.status_code == 200,
                "latency_ms": latency_ms,
                "status_code": response.status_code,
            }

        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            return {"success": False, "latency_ms": latency_ms, "error": str(e)}


class HITLFunctionalTest(PerformanceTest):
    """Test HITL functional capabilities and decision accuracy."""

    test_type = "hitl"
    tags = ["hitl", "functional", "decision"]

    async def run_test(self) -> List[E2ETestResult]:
        """Run HITL functional tests."""
        results = []

        # Test uncertainty quantification
        result = await self._test_uncertainty_quantification()
        results.append(result)

        # Test human escalation triggers
        result = await self._test_human_escalation_triggers()
        results.append(result)

        # Test decision confidence scoring
        result = await self._test_decision_confidence_scoring()
        results.append(result)

        return results

    async def _test_uncertainty_quantification(self) -> E2ETestResult:
        """Test uncertainty quantification accuracy."""
        start_time = time.perf_counter()

        try:
            if not self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
                return E2ETestResult(
                    test_name="hitl_uncertainty_quantification",
                    success=False,
                    duration_ms=0,
                    error_message="Constitutional AI service not enabled",
                )

            # Test scenarios with different uncertainty levels
            test_scenarios = [
                {
                    "scenario": "high_confidence",
                    "policy_complexity": "simple",
                    "expected_uncertainty": "low",
                },
                {
                    "scenario": "medium_confidence",
                    "policy_complexity": "moderate",
                    "expected_uncertainty": "medium",
                },
                {
                    "scenario": "low_confidence",
                    "policy_complexity": "complex",
                    "expected_uncertainty": "high",
                },
            ]

            uncertainty_results = []

            for scenario in test_scenarios:
                test_request = {
                    "request_id": f"uncertainty_test_{scenario['scenario']}",
                    "constitutional_hash": self.config.constitutional_hash,
                    "decision_context": {
                        "policy_complexity": scenario["policy_complexity"],
                        "scenario_type": scenario["scenario"],
                    },
                }

                try:
                    response = await self.make_service_request(
                        ServiceType.CONSTITUTIONAL_AI,
                        "POST",
                        "/api/v1/hitl/assess",
                        json=test_request,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        uncertainty_score = data.get("uncertainty_score", 0.5)
                        confidence_level = data.get("confidence_level", 0.5)

                        uncertainty_results.append(
                            {
                                "scenario": scenario["scenario"],
                                "uncertainty_score": uncertainty_score,
                                "confidence_level": confidence_level,
                                "success": True,
                            }
                        )
                    else:
                        uncertainty_results.append(
                            {"scenario": scenario["scenario"], "success": False}
                        )

                except Exception:
                    uncertainty_results.append(
                        {"scenario": scenario["scenario"], "success": False}
                    )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            # Evaluate uncertainty quantification accuracy
            successful_assessments = [r for r in uncertainty_results if r["success"]]
            success_rate = len(successful_assessments) / len(test_scenarios)

            # Check if uncertainty scores are reasonable
            reasonable_scores = all(
                0.0 <= r.get("uncertainty_score", 0.5) <= 1.0
                for r in successful_assessments
            )

            overall_success = success_rate >= 0.8 and reasonable_scores

            return E2ETestResult(
                test_name="hitl_uncertainty_quantification",
                success=overall_success,
                duration_ms=duration_ms,
                performance_metrics={
                    "scenarios_tested": len(test_scenarios),
                    "successful_assessments": len(successful_assessments),
                    "success_rate": success_rate,
                    "reasonable_scores": reasonable_scores,
                    "uncertainty_results": uncertainty_results,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="hitl_uncertainty_quantification",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Uncertainty quantification test failed: {str(e)}",
            )

    async def _test_human_escalation_triggers(self) -> E2ETestResult:
        """Test human escalation trigger logic."""
        start_time = time.perf_counter()

        try:
            if not self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
                return E2ETestResult(
                    test_name="hitl_human_escalation_triggers",
                    success=False,
                    duration_ms=0,
                    error_message="Constitutional AI service not enabled",
                )

            # Test escalation scenarios
            escalation_scenarios = [
                {
                    "scenario": "high_uncertainty",
                    "uncertainty_threshold": 0.8,
                    "should_escalate": True,
                },
                {
                    "scenario": "low_uncertainty",
                    "uncertainty_threshold": 0.2,
                    "should_escalate": False,
                },
                {
                    "scenario": "critical_decision",
                    "decision_criticality": "high",
                    "should_escalate": True,
                },
            ]

            escalation_results = []

            for scenario in escalation_scenarios:
                test_request = {
                    "request_id": f"escalation_test_{scenario['scenario']}",
                    "constitutional_hash": self.config.constitutional_hash,
                    "decision_context": {
                        "scenario_type": scenario["scenario"],
                        "criticality": scenario.get("decision_criticality", "medium"),
                    },
                    "uncertainty_threshold": scenario.get("uncertainty_threshold", 0.5),
                }

                try:
                    response = await self.make_service_request(
                        ServiceType.CONSTITUTIONAL_AI,
                        "POST",
                        "/api/v1/hitl/assess",
                        json=test_request,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        requires_human_review = data.get("requires_human_review", False)

                        escalation_results.append(
                            {
                                "scenario": scenario["scenario"],
                                "requires_human_review": requires_human_review,
                                "expected_escalation": scenario["should_escalate"],
                                "correct_escalation": requires_human_review
                                == scenario["should_escalate"],
                                "success": True,
                            }
                        )
                    else:
                        escalation_results.append(
                            {"scenario": scenario["scenario"], "success": False}
                        )

                except Exception:
                    escalation_results.append(
                        {"scenario": scenario["scenario"], "success": False}
                    )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            # Evaluate escalation accuracy
            successful_tests = [r for r in escalation_results if r["success"]]
            correct_escalations = [
                r for r in successful_tests if r.get("correct_escalation", False)
            ]

            success_rate = len(successful_tests) / len(escalation_scenarios)
            escalation_accuracy = (
                len(correct_escalations) / len(successful_tests)
                if successful_tests
                else 0
            )

            overall_success = success_rate >= 0.8 and escalation_accuracy >= 0.8

            return E2ETestResult(
                test_name="hitl_human_escalation_triggers",
                success=overall_success,
                duration_ms=duration_ms,
                performance_metrics={
                    "scenarios_tested": len(escalation_scenarios),
                    "successful_tests": len(successful_tests),
                    "correct_escalations": len(correct_escalations),
                    "success_rate": success_rate,
                    "escalation_accuracy": escalation_accuracy,
                    "escalation_results": escalation_results,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="hitl_human_escalation_triggers",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Human escalation triggers test failed: {str(e)}",
            )

    async def _test_decision_confidence_scoring(self) -> E2ETestResult:
        """Test decision confidence scoring consistency."""
        start_time = time.perf_counter()

        try:
            if not self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
                return E2ETestResult(
                    test_name="hitl_decision_confidence_scoring",
                    success=False,
                    duration_ms=0,
                    error_message="Constitutional AI service not enabled",
                )

            # Test confidence scoring with repeated requests
            test_request = {
                "request_id": "confidence_consistency_test",
                "constitutional_hash": self.config.constitutional_hash,
                "decision_context": {
                    "policy_id": "confidence_test_policy",
                    "action": "confidence_validation",
                },
            }

            confidence_scores = []
            successful_requests = 0
            total_requests = 10

            for i in range(total_requests):
                try:
                    response = await self.make_service_request(
                        ServiceType.CONSTITUTIONAL_AI,
                        "POST",
                        "/api/v1/hitl/assess",
                        json={**test_request, "request_id": f"confidence_test_{i}"},
                    )

                    if response.status_code == 200:
                        data = response.json()
                        confidence_level = data.get("confidence_level", 0.5)
                        confidence_scores.append(confidence_level)
                        successful_requests += 1

                except Exception:
                    pass

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            # Analyze confidence score consistency
            if confidence_scores:
                avg_confidence = statistics.mean(confidence_scores)
                confidence_std_dev = (
                    statistics.stdev(confidence_scores)
                    if len(confidence_scores) > 1
                    else 0
                )
                confidence_consistency = (
                    confidence_std_dev < 0.1
                )  # Low standard deviation indicates consistency
            else:
                avg_confidence = 0
                confidence_std_dev = 0
                confidence_consistency = False

            success_rate = successful_requests / total_requests
            overall_success = success_rate >= 0.9 and confidence_consistency

            return E2ETestResult(
                test_name="hitl_decision_confidence_scoring",
                success=overall_success,
                duration_ms=duration_ms,
                performance_metrics={
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "success_rate": success_rate,
                    "average_confidence": avg_confidence,
                    "confidence_std_dev": confidence_std_dev,
                    "confidence_consistency": confidence_consistency,
                    "confidence_scores": confidence_scores,
                },
            )

        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return E2ETestResult(
                test_name="hitl_decision_confidence_scoring",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Decision confidence scoring test failed: {str(e)}",
            )
