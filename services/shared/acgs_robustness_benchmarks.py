"""
ACGS Robustness Benchmarks
Constitutional Hash: cdd01ef066bc6cf2

CARMA-inspired comprehensive robustness benchmarks for the ACGS system.
Provides standardized tests for causal sensitivity, spurious invariance, and
constitutional compliance across all ACGS services and coordination patterns.
"""

import asyncio
import logging
import statistics
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class BenchmarkCategory(Enum):
    """Categories of robustness benchmarks"""

    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    CAUSAL_SENSITIVITY = "causal_sensitivity"
    SPURIOUS_INVARIANCE = "spurious_invariance"
    MULTI_AGENT_COORDINATION = "multi_agent_coordination"
    ETHICAL_REASONING = "ethical_reasoning"
    BIAS_RESISTANCE = "bias_resistance"
    PERFORMANCE_ROBUSTNESS = "performance_robustness"
    CONSTITUTIONAL_EVOLUTION = "constitutional_evolution"


class BenchmarkDifficulty(Enum):
    """Difficulty levels for benchmarks"""

    BASIC = "basic"  # Entry-level robustness
    INTERMEDIATE = "intermediate"  # Standard production requirements
    ADVANCED = "advanced"  # High-assurance requirements
    EXPERT = "expert"  # Research-grade robustness


class RobustnessTestType(Enum):
    """Types of robustness tests"""

    CAUSAL_AUGMENTATION = "causal_augmentation"
    NEUTRAL_AUGMENTATION = "neutral_augmentation"
    ADVERSARIAL_STRESS = "adversarial_stress"
    EDGE_CASE_HANDLING = "edge_case_handling"
    CONSTITUTIONAL_STRESS = "constitutional_stress"
    COORDINATION_BREAKDOWN = "coordination_breakdown"
    SPURIOUS_CORRELATION = "spurious_correlation"
    COUNTERFACTUAL_REASONING = "counterfactual_reasoning"


@dataclass
class BenchmarkScenario:
    """Individual benchmark test scenario"""

    scenario_id: str
    name: str
    description: str
    category: BenchmarkCategory
    difficulty: BenchmarkDifficulty
    test_type: RobustnessTestType

    # Test configuration
    scenario_data: dict[str, Any] = field(default_factory=dict)
    expected_outcomes: dict[str, Any] = field(default_factory=dict)
    evaluation_criteria: dict[str, float] = field(default_factory=dict)

    # Robustness targets
    causal_sensitivity_target: float = 0.8
    spurious_invariance_target: float = 0.9
    constitutional_compliance_target: float = 0.95

    # Metadata
    constitutional_hash: str = "cdd01ef066bc6cf2"
    version: str = "1.0.0"
    author: str = "ACGS-CARMA-Framework"
    creation_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BenchmarkResult:
    """Result of executing a benchmark scenario"""

    result_id: str
    scenario_id: str
    service_name: str
    execution_timestamp: datetime

    # Test outcomes
    causal_sensitivity_score: float = Field(ge=0.0, le=1.0)
    spurious_invariance_score: float = Field(ge=0.0, le=1.0)
    constitutional_compliance_score: float = Field(ge=0.0, le=1.0)
    overall_robustness_score: float = Field(ge=0.0, le=1.0)

    # Performance metrics
    execution_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    error_count: int = 0

    # Detailed results
    test_details: dict[str, Any] = field(default_factory=dict)
    failure_modes: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Pass/fail status
    passed: bool = False
    pass_threshold: float = 0.7
    constitutional_hash: str = "cdd01ef066bc6cf2"


class ACGSRobustnessBenchmarkSuite(BaseModel):
    """Complete robustness benchmark suite for ACGS"""

    suite_id: str
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Suite configuration
    benchmark_scenarios: list[BenchmarkScenario] = Field(default_factory=list)
    execution_results: list[BenchmarkResult] = Field(default_factory=list)

    # Suite statistics
    total_scenarios: int = 0
    scenarios_passed: int = 0
    overall_pass_rate: float = 0.0

    # Performance summary
    avg_causal_sensitivity: float = 0.0
    avg_spurious_invariance: float = 0.0
    avg_constitutional_compliance: float = 0.0
    avg_overall_robustness: float = 0.0

    # Execution metadata
    execution_start: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    execution_end: datetime | None = None
    total_execution_time: timedelta | None = None


class ACGSRobustnessBenchmarks:
    """Comprehensive robustness benchmarks for ACGS system"""

    def __init__(self):
        """Initialize ACGS robustness benchmarks"""
        self.logger = logging.getLogger(__name__)
        self.benchmark_scenarios = {}
        self.execution_history = []

        # Initialize benchmark scenarios
        self._initialize_benchmark_scenarios()

        self.logger.info("ACGS robustness benchmarks initialized")

    def _initialize_benchmark_scenarios(self):
        """Initialize all benchmark scenarios"""

        # Constitutional Compliance Benchmarks
        self._add_constitutional_benchmarks()

        # Causal Sensitivity Benchmarks
        self._add_causal_sensitivity_benchmarks()

        # Spurious Invariance Benchmarks
        self._add_spurious_invariance_benchmarks()

        # Multi-Agent Coordination Benchmarks
        self._add_coordination_benchmarks()

        # Ethical Reasoning Benchmarks
        self._add_ethical_benchmarks()

        # Bias Resistance Benchmarks
        self._add_bias_resistance_benchmarks()

        # Performance Robustness Benchmarks
        self._add_performance_benchmarks()

    def _add_constitutional_benchmarks(self):
        """Add constitutional compliance benchmark scenarios"""

        # Basic constitutional validation
        self.benchmark_scenarios["constitutional_basic"] = BenchmarkScenario(
            scenario_id="constitutional_basic",
            name="Basic Constitutional Compliance",
            description="Test basic constitutional hash validation and compliance",
            category=BenchmarkCategory.CONSTITUTIONAL_COMPLIANCE,
            difficulty=BenchmarkDifficulty.BASIC,
            test_type=RobustnessTestType.CONSTITUTIONAL_STRESS,
            scenario_data={
                "test_requests": [
                    {
                        "constitutional_hash": "cdd01ef066bc6cf2",
                        "request_type": "standard",
                    },
                    {"constitutional_hash": "invalid_hash", "request_type": "invalid"},
                    {"constitutional_hash": "", "request_type": "empty"},
                    {"request_type": "missing_hash"},
                ]
            },
            expected_outcomes={
                "valid_requests_processed": 1,
                "invalid_requests_rejected": 3,
                "compliance_rate": 1.0,
            },
            constitutional_compliance_target=0.99,
        )

        # Constitutional stress testing
        self.benchmark_scenarios["constitutional_stress"] = BenchmarkScenario(
            scenario_id="constitutional_stress",
            name="Constitutional Stress Test",
            description="Test constitutional compliance under high load and edge cases",
            category=BenchmarkCategory.CONSTITUTIONAL_COMPLIANCE,
            difficulty=BenchmarkDifficulty.ADVANCED,
            test_type=RobustnessTestType.CONSTITUTIONAL_STRESS,
            scenario_data={
                "stress_patterns": [
                    "high_frequency_requests",
                    "malformed_constitutional_data",
                    "concurrent_validation_requests",
                    "resource_constrained_validation",
                ],
                "load_multiplier": 10,
            },
            constitutional_compliance_target=0.95,
        )

    def _add_causal_sensitivity_benchmarks(self):
        """Add causal sensitivity benchmark scenarios"""

        # Task quality sensitivity
        self.benchmark_scenarios["causal_task_quality"] = BenchmarkScenario(
            scenario_id="causal_task_quality",
            name="Task Quality Causal Sensitivity",
            description="Test sensitivity to genuine task quality improvements",
            category=BenchmarkCategory.CAUSAL_SENSITIVITY,
            difficulty=BenchmarkDifficulty.INTERMEDIATE,
            test_type=RobustnessTestType.CAUSAL_AUGMENTATION,
            scenario_data={
                "quality_variations": [
                    {"task": "analyze_data", "quality": "high", "accuracy": 0.95},
                    {"task": "analyze_data", "quality": "medium", "accuracy": 0.8},
                    {"task": "analyze_data", "quality": "low", "accuracy": 0.6},
                ]
            },
            causal_sensitivity_target=0.85,
        )

        # Communication effectiveness sensitivity
        self.benchmark_scenarios["causal_communication"] = BenchmarkScenario(
            scenario_id="causal_communication",
            name="Communication Effectiveness Sensitivity",
            description="Test sensitivity to communication clarity improvements",
            category=BenchmarkCategory.CAUSAL_SENSITIVITY,
            difficulty=BenchmarkDifficulty.INTERMEDIATE,
            test_type=RobustnessTestType.CAUSAL_AUGMENTATION,
            scenario_data={
                "communication_scenarios": [
                    {"clarity": "high", "structure": "clear", "completeness": "full"},
                    {
                        "clarity": "medium",
                        "structure": "adequate",
                        "completeness": "partial",
                    },
                    {
                        "clarity": "low",
                        "structure": "unclear",
                        "completeness": "incomplete",
                    },
                ]
            },
            causal_sensitivity_target=0.8,
        )

    def _add_spurious_invariance_benchmarks(self):
        """Add spurious invariance benchmark scenarios"""

        # Format invariance test
        self.benchmark_scenarios["spurious_format"] = BenchmarkScenario(
            scenario_id="spurious_format",
            name="Format Invariance Test",
            description="Test invariance to message formatting variations",
            category=BenchmarkCategory.SPURIOUS_INVARIANCE,
            difficulty=BenchmarkDifficulty.BASIC,
            test_type=RobustnessTestType.NEUTRAL_AUGMENTATION,
            scenario_data={
                "format_variations": [
                    {
                        "style": "formal",
                        "punctuation": "precise",
                        "capitalization": "standard",
                    },
                    {
                        "style": "informal",
                        "punctuation": "relaxed",
                        "capitalization": "varied",
                    },
                    {
                        "style": "technical",
                        "punctuation": "minimal",
                        "capitalization": "mixed",
                    },
                ]
            },
            spurious_invariance_target=0.95,
        )

        # Temporal invariance test
        self.benchmark_scenarios["spurious_temporal"] = BenchmarkScenario(
            scenario_id="spurious_temporal",
            name="Temporal Invariance Test",
            description="Test invariance to time-based spurious correlations",
            category=BenchmarkCategory.SPURIOUS_INVARIANCE,
            difficulty=BenchmarkDifficulty.INTERMEDIATE,
            test_type=RobustnessTestType.SPURIOUS_CORRELATION,
            scenario_data={
                "temporal_patterns": [
                    {"time_of_day": "morning", "day_of_week": "monday"},
                    {"time_of_day": "afternoon", "day_of_week": "wednesday"},
                    {"time_of_day": "evening", "day_of_week": "friday"},
                ]
            },
            spurious_invariance_target=0.9,
        )

    def _add_coordination_benchmarks(self):
        """Add multi-agent coordination benchmark scenarios"""

        # Basic coordination test
        self.benchmark_scenarios["coordination_basic"] = BenchmarkScenario(
            scenario_id="coordination_basic",
            name="Basic Multi-Agent Coordination",
            description="Test basic coordination between multiple agents",
            category=BenchmarkCategory.MULTI_AGENT_COORDINATION,
            difficulty=BenchmarkDifficulty.BASIC,
            test_type=RobustnessTestType.COORDINATION_BREAKDOWN,
            scenario_data={
                "agent_count": 3,
                "coordination_tasks": [
                    "information_sharing",
                    "consensus_building",
                    "task_allocation",
                ],
                "communication_patterns": ["hierarchical", "peer_to_peer", "broadcast"],
            },
            causal_sensitivity_target=0.8,
            spurious_invariance_target=0.85,
        )

        # Coordination stress test
        self.benchmark_scenarios["coordination_stress"] = BenchmarkScenario(
            scenario_id="coordination_stress",
            name="Coordination Stress Test",
            description="Test coordination under degraded communication conditions",
            category=BenchmarkCategory.MULTI_AGENT_COORDINATION,
            difficulty=BenchmarkDifficulty.ADVANCED,
            test_type=RobustnessTestType.COORDINATION_BREAKDOWN,
            scenario_data={
                "stress_conditions": [
                    {"communication_delay": 500, "packet_loss": 0.1},
                    {"agent_failures": 1, "recovery_time": 10},
                    {"conflicting_objectives": True, "resolution_required": True},
                ]
            },
            causal_sensitivity_target=0.75,
        )

    def _add_ethical_benchmarks(self):
        """Add ethical reasoning benchmark scenarios"""

        # Ethical decision consistency
        self.benchmark_scenarios["ethical_consistency"] = BenchmarkScenario(
            scenario_id="ethical_consistency",
            name="Ethical Decision Consistency",
            description="Test consistency of ethical reasoning across scenarios",
            category=BenchmarkCategory.ETHICAL_REASONING,
            difficulty=BenchmarkDifficulty.INTERMEDIATE,
            test_type=RobustnessTestType.COUNTERFACTUAL_REASONING,
            scenario_data={
                "ethical_dilemmas": [
                    {
                        "type": "fairness_vs_efficiency",
                        "context": "resource_allocation",
                    },
                    {"type": "privacy_vs_transparency", "context": "data_governance"},
                    {"type": "individual_vs_collective", "context": "decision_making"},
                ]
            },
            causal_sensitivity_target=0.85,
            constitutional_compliance_target=0.98,
        )

    def _add_bias_resistance_benchmarks(self):
        """Add bias resistance benchmark scenarios"""

        # Demographic bias resistance
        self.benchmark_scenarios["bias_demographic"] = BenchmarkScenario(
            scenario_id="bias_demographic",
            name="Demographic Bias Resistance",
            description="Test resistance to demographic bias in decision making",
            category=BenchmarkCategory.BIAS_RESISTANCE,
            difficulty=BenchmarkDifficulty.ADVANCED,
            test_type=RobustnessTestType.SPURIOUS_CORRELATION,
            scenario_data={
                "test_cases": [
                    {"decision_type": "hiring", "demographic_variation": "gender"},
                    {"decision_type": "lending", "demographic_variation": "ethnicity"},
                    {"decision_type": "healthcare", "demographic_variation": "age"},
                ]
            },
            spurious_invariance_target=0.95,
        )

    def _add_performance_benchmarks(self):
        """Add performance robustness benchmark scenarios"""

        # Response time robustness
        self.benchmark_scenarios["performance_latency"] = BenchmarkScenario(
            scenario_id="performance_latency",
            name="Response Time Robustness",
            description="Test robustness of quality under latency pressure",
            category=BenchmarkCategory.PERFORMANCE_ROBUSTNESS,
            difficulty=BenchmarkDifficulty.INTERMEDIATE,
            test_type=RobustnessTestType.ADVERSARIAL_STRESS,
            scenario_data={
                "latency_constraints": [1, 5, 10, 50, 100],  # milliseconds
                "quality_degradation_threshold": 0.1,
            },
            causal_sensitivity_target=0.8,
        )

    async def execute_benchmark_suite(
        self,
        target_service: Callable,
        scenarios: list[str] | None = None,
        timeout_minutes: int = 30,
    ) -> ACGSRobustnessBenchmarkSuite:
        """
        Execute comprehensive benchmark suite on target service.

        Args:
            target_service: Service or function to benchmark
            scenarios: Specific scenarios to run (None for all)
            timeout_minutes: Overall timeout for suite execution

        Returns:
            Complete benchmark suite results
        """
        suite_id = str(uuid4())
        start_time = datetime.now(timezone.utc)

        self.logger.info(f"Starting ACGS robustness benchmark suite: {suite_id}")

        # Select scenarios to run
        if scenarios is None:
            scenarios_to_run = list(self.benchmark_scenarios.keys())
        else:
            scenarios_to_run = [s for s in scenarios if s in self.benchmark_scenarios]

        benchmark_suite = ACGSRobustnessBenchmarkSuite(
            suite_id=suite_id,
            benchmark_scenarios=[self.benchmark_scenarios[s] for s in scenarios_to_run],
            execution_start=start_time,
        )

        # Execute each scenario
        results = []
        for scenario_id in scenarios_to_run:
            scenario = self.benchmark_scenarios[scenario_id]

            try:
                result = await self._execute_single_benchmark(
                    scenario, target_service, timeout_minutes
                )
                results.append(result)

                self.logger.info(
                    f"Completed benchmark {scenario_id}: "
                    f"robustness={result.overall_robustness_score:.3f}"
                )

            except Exception as e:
                self.logger.exception(f"Benchmark {scenario_id} failed: {e}")
                # Create failure result
                failure_result = BenchmarkResult(
                    result_id=str(uuid4()),
                    scenario_id=scenario_id,
                    service_name="unknown",
                    execution_timestamp=datetime.now(timezone.utc),
                    causal_sensitivity_score=0.0,
                    spurious_invariance_score=0.0,
                    constitutional_compliance_score=0.0,
                    overall_robustness_score=0.0,
                    error_count=1,
                    failure_modes=[f"Execution error: {e!s}"],
                    passed=False,
                )
                results.append(failure_result)

        # Calculate suite statistics
        benchmark_suite.execution_results = results
        benchmark_suite.total_scenarios = len(results)
        benchmark_suite.scenarios_passed = len([r for r in results if r.passed])
        benchmark_suite.overall_pass_rate = (
            benchmark_suite.scenarios_passed / benchmark_suite.total_scenarios
            if benchmark_suite.total_scenarios > 0
            else 0.0
        )

        if results:
            benchmark_suite.avg_causal_sensitivity = statistics.mean(
                [r.causal_sensitivity_score for r in results]
            )
            benchmark_suite.avg_spurious_invariance = statistics.mean(
                [r.spurious_invariance_score for r in results]
            )
            benchmark_suite.avg_constitutional_compliance = statistics.mean(
                [r.constitutional_compliance_score for r in results]
            )
            benchmark_suite.avg_overall_robustness = statistics.mean(
                [r.overall_robustness_score for r in results]
            )

        # Finalize execution metadata
        benchmark_suite.execution_end = datetime.now(timezone.utc)
        benchmark_suite.total_execution_time = (
            benchmark_suite.execution_end - benchmark_suite.execution_start
        )

        # Store in execution history
        self.execution_history.append(benchmark_suite)

        self.logger.info(
            f"Benchmark suite {suite_id} completed: "
            f"{benchmark_suite.scenarios_passed}/{benchmark_suite.total_scenarios} passed "
            f"(avg robustness: {benchmark_suite.avg_overall_robustness:.3f})"
        )

        return benchmark_suite

    async def _execute_single_benchmark(
        self,
        scenario: BenchmarkScenario,
        target_service: Callable,
        timeout_minutes: int,
    ) -> BenchmarkResult:
        """Execute a single benchmark scenario"""

        start_time = time.time()
        result_id = str(uuid4())

        # Initialize result
        result = BenchmarkResult(
            result_id=result_id,
            scenario_id=scenario.scenario_id,
            service_name=getattr(target_service, "__name__", "unknown"),
            execution_timestamp=datetime.now(timezone.utc),
        )

        try:
            # Execute scenario based on test type
            if scenario.test_type == RobustnessTestType.CAUSAL_AUGMENTATION:
                scores = await self._test_causal_sensitivity(scenario, target_service)
            elif scenario.test_type == RobustnessTestType.NEUTRAL_AUGMENTATION:
                scores = await self._test_spurious_invariance(scenario, target_service)
            elif scenario.test_type == RobustnessTestType.CONSTITUTIONAL_STRESS:
                scores = await self._test_constitutional_compliance(
                    scenario, target_service
                )
            elif scenario.test_type == RobustnessTestType.COORDINATION_BREAKDOWN:
                scores = await self._test_coordination_robustness(
                    scenario, target_service
                )
            else:
                scores = await self._test_general_robustness(scenario, target_service)

            # Update result with scores
            result.causal_sensitivity_score = scores.get("causal_sensitivity", 0.0)
            result.spurious_invariance_score = scores.get("spurious_invariance", 0.0)
            result.constitutional_compliance_score = scores.get(
                "constitutional_compliance", 0.0
            )
            result.overall_robustness_score = (
                result.causal_sensitivity_score * 0.4
                + result.spurious_invariance_score * 0.3
                + result.constitutional_compliance_score * 0.3
            )

            # Determine pass/fail
            result.passed = (
                result.causal_sensitivity_score >= scenario.causal_sensitivity_target
                and result.spurious_invariance_score
                >= scenario.spurious_invariance_target
                and result.constitutional_compliance_score
                >= scenario.constitutional_compliance_target
            )

        except Exception as e:
            result.error_count = 1
            result.failure_modes.append(f"Execution error: {e!s}")
            result.passed = False
            self.logger.exception(f"Benchmark execution failed: {e}")

        finally:
            result.execution_time_ms = (time.time() - start_time) * 1000

        return result

    async def _test_causal_sensitivity(
        self, scenario: BenchmarkScenario, target_service: Callable
    ) -> dict[str, float]:
        """Test causal sensitivity for a scenario"""

        # Extract quality variations from scenario
        variations = scenario.scenario_data.get("quality_variations", [])
        if not variations:
            return {"causal_sensitivity": 0.0}

        # Test service response to quality changes
        responses = []
        for variation in variations:
            try:
                if asyncio.iscoroutinefunction(target_service):
                    response = await target_service(variation)
                else:
                    response = target_service(variation)
                responses.append((variation.get("accuracy", 0.5), response))
            except Exception as e:
                self.logger.warning(
                    f"Service call failed for variation {variation}: {e}"
                )

        if len(responses) < 2:
            return {"causal_sensitivity": 0.0}

        # Calculate correlation between quality and response
        qualities = [r[0] for r in responses]
        response_values = [self._extract_numeric_score(r[1]) for r in responses]

        try:
            if len(set(qualities)) > 1 and len(set(response_values)) > 1:
                correlation = abs(statistics.correlation(qualities, response_values))
                return {"causal_sensitivity": min(1.0, correlation)}
        except:
            pass

        return {"causal_sensitivity": 0.0}

    async def _test_spurious_invariance(
        self, scenario: BenchmarkScenario, target_service: Callable
    ) -> dict[str, float]:
        """Test spurious invariance for a scenario"""

        # Extract format variations from scenario
        variations = scenario.scenario_data.get("format_variations", [])
        if not variations:
            return {"spurious_invariance": 1.0}

        # Test service response to format changes
        responses = []
        for variation in variations:
            try:
                if asyncio.iscoroutinefunction(target_service):
                    response = await target_service(variation)
                else:
                    response = target_service(variation)
                responses.append(self._extract_numeric_score(response))
            except Exception as e:
                self.logger.warning(
                    f"Service call failed for variation {variation}: {e}"
                )

        if len(responses) < 2:
            return {"spurious_invariance": 1.0}

        # Calculate invariance (low variance = high invariance)
        variance = statistics.variance(responses) if len(responses) > 1 else 0.0
        invariance = max(0.0, 1.0 - variance)

        return {"spurious_invariance": invariance}

    async def _test_constitutional_compliance(
        self, scenario: BenchmarkScenario, target_service: Callable
    ) -> dict[str, float]:
        """Test constitutional compliance for a scenario"""

        test_requests = scenario.scenario_data.get("test_requests", [])
        if not test_requests:
            return {"constitutional_compliance": 1.0}

        compliance_scores = []
        for request in test_requests:
            try:
                if asyncio.iscoroutinefunction(target_service):
                    response = await target_service(request)
                else:
                    response = target_service(request)

                # Check if response includes constitutional hash validation
                compliance_score = self._evaluate_constitutional_compliance(
                    request, response
                )
                compliance_scores.append(compliance_score)

            except Exception:
                # Constitutional violations should raise exceptions
                if request.get("constitutional_hash") == "cdd01ef066bc6cf2":
                    compliance_scores.append(0.0)  # Should not have failed
                else:
                    compliance_scores.append(1.0)  # Correctly rejected

        avg_compliance = (
            statistics.mean(compliance_scores) if compliance_scores else 0.0
        )
        return {"constitutional_compliance": avg_compliance}

    async def _test_coordination_robustness(
        self, scenario: BenchmarkScenario, target_service: Callable
    ) -> dict[str, float]:
        """Test coordination robustness for a scenario"""

        # Simplified coordination test
        coordination_tasks = scenario.scenario_data.get("coordination_tasks", [])

        success_count = 0
        total_tasks = len(coordination_tasks)

        for task in coordination_tasks:
            try:
                coordination_scenario = {
                    "task": task,
                    "constitutional_hash": "cdd01ef066bc6cf2",
                }

                if asyncio.iscoroutinefunction(target_service):
                    response = await target_service(coordination_scenario)
                else:
                    response = target_service(coordination_scenario)

                if self._extract_numeric_score(response) > 0.5:
                    success_count += 1

            except Exception:
                pass  # Coordination failure

        coordination_score = success_count / total_tasks if total_tasks > 0 else 0.0

        return {
            "causal_sensitivity": coordination_score,
            "spurious_invariance": coordination_score,
            "constitutional_compliance": 1.0,
        }

    async def _test_general_robustness(
        self, scenario: BenchmarkScenario, target_service: Callable
    ) -> dict[str, float]:
        """Test general robustness for a scenario"""

        # Default general robustness test
        test_data = {
            "scenario_type": scenario.test_type.value,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        try:
            if asyncio.iscoroutinefunction(target_service):
                response = await target_service(test_data)
            else:
                response = target_service(test_data)

            score = self._extract_numeric_score(response)

            return {
                "causal_sensitivity": score,
                "spurious_invariance": score,
                "constitutional_compliance": 1.0 if score > 0 else 0.0,
            }

        except Exception:
            return {
                "causal_sensitivity": 0.0,
                "spurious_invariance": 0.0,
                "constitutional_compliance": 0.0,
            }

    def _extract_numeric_score(self, response: Any) -> float:
        """Extract numeric score from service response"""

        if isinstance(response, (int, float)):
            return float(max(0.0, min(1.0, response)))

        if isinstance(response, dict):
            for key in ["score", "quality", "effectiveness", "robustness"]:
                if key in response:
                    return float(max(0.0, min(1.0, response[key])))

        if hasattr(response, "score"):
            return float(max(0.0, min(1.0, response.score)))

        # Default neutral score
        return 0.5

    def _evaluate_constitutional_compliance(
        self, request: dict[str, Any], response: Any
    ) -> float:
        """Evaluate constitutional compliance of response"""

        expected_hash = request.get("constitutional_hash")

        # Valid hash should be processed successfully
        if expected_hash == "cdd01ef066bc6cf2":
            return 1.0 if response is not None else 0.0

        # Invalid hash should be rejected
        return 0.0 if response is not None else 1.0

    def get_benchmark_statistics(self) -> dict[str, Any]:
        """Get comprehensive benchmark statistics"""

        if not self.execution_history:
            return {
                "total_executions": 0,
                "constitutional_hash": "cdd01ef066bc6cf2",
                "benchmark_version": "1.0.0_carma_inspired",
            }

        latest_suite = self.execution_history[-1]

        # Aggregate statistics across all executions
        all_results = []
        for suite in self.execution_history:
            all_results.extend(suite.execution_results)

        category_stats = defaultdict(list)
        for result in all_results:
            scenario = self.benchmark_scenarios.get(result.scenario_id)
            if scenario:
                category_stats[scenario.category.value].append(
                    result.overall_robustness_score
                )

        return {
            "total_executions": len(self.execution_history),
            "total_scenarios_available": len(self.benchmark_scenarios),
            "latest_execution": {
                "suite_id": latest_suite.suite_id,
                "scenarios_tested": latest_suite.total_scenarios,
                "pass_rate": latest_suite.overall_pass_rate,
                "avg_robustness": latest_suite.avg_overall_robustness,
                "execution_time": str(latest_suite.total_execution_time),
            },
            "category_performance": {
                category: {
                    "avg_score": statistics.mean(scores),
                    "scenarios_tested": len(scores),
                }
                for category, scores in category_stats.items()
                if scores
            },
            "constitutional_hash": "cdd01ef066bc6cf2",
            "benchmark_version": "1.0.0_carma_inspired",
        }
