"""
Causal Coordination Model
Constitutional Hash: cdd01ef066bc6cf2

CARMA-inspired causal modeling for multi-agent coordination quality assessment.
Distinguishes genuine coordination effectiveness from spurious correlation factors
to enable robust evaluation of agent collaboration quality.
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from .ai_model_service import AIModelService
from .blackboard import BlackboardService, KnowledgeItem
from .constitutional_safety_framework import ConstitutionalSafetyValidator

# Configure logging
logger = logging.getLogger(__name__)


class CoordinationAttribute(Enum):
    """Causal coordination attributes that should influence quality assessment"""

    TASK_COMPLETION_ACCURACY = "task_completion_accuracy"
    COMMUNICATION_CLARITY = "communication_clarity"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    CONFLICT_RESOLUTION = "conflict_resolution"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    GOAL_ALIGNMENT = "goal_alignment"
    ADAPTATION_CAPABILITY = "adaptation_capability"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    DECISION_QUALITY = "decision_quality"
    STAKEHOLDER_SATISFACTION = "stakeholder_satisfaction"


class SpuriousCoordinationAttribute(Enum):
    """Spurious attributes that should NOT influence coordination quality assessment"""

    RESPONSE_TIMING = "response_timing"
    MESSAGE_LENGTH = "message_length"
    AGENT_IDENTIFIER_FORMAT = "agent_identifier_format"
    COMMUNICATION_STYLE = "communication_style"
    METADATA_VERBOSITY = "metadata_verbosity"
    TECHNICAL_JARGON_USAGE = "technical_jargon_usage"
    TIMESTAMP_PRECISION = "timestamp_precision"
    LOG_FORMAT_STYLE = "log_format_style"
    AGENT_PERSONALITY_TRAITS = "agent_personality_traits"


class CoordinationQualityMetric(Enum):
    """Metrics for evaluating coordination quality"""

    EFFECTIVENESS = "effectiveness"
    EFFICIENCY = "efficiency"
    ROBUSTNESS = "robustness"
    SCALABILITY = "scalability"
    TRANSPARENCY = "transparency"
    ADAPTABILITY = "adaptability"
    CONSTITUTIONAL_ADHERENCE = "constitutional_adherence"


@dataclass
class CoordinationScenario:
    """Single coordination scenario for testing"""

    scenario_id: str
    agents_involved: List[str]
    task_description: Dict[str, Any]
    coordination_context: Dict[str, Any]
    expected_outcomes: List[str]
    constitutional_requirements: List[str]
    constitutional_hash: str = "cdd01ef066bc6cf2"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoordinationTestResult:
    """Result of coordination quality test"""

    test_id: str
    scenario: CoordinationScenario
    attribute_tested: Union[CoordinationAttribute, SpuriousCoordinationAttribute]
    test_type: str  # "causal_sensitivity" or "spurious_invariance"

    # Test outcomes
    baseline_quality: float = Field(ge=0.0, le=1.0)
    intervention_quality: float = Field(ge=0.0, le=1.0)
    expected_change: bool
    actual_change_detected: bool

    # Quality assessment
    coordination_effectiveness: float = Field(ge=0.0, le=1.0)
    constitutional_compliance: float = Field(ge=0.0, le=1.0)
    robustness_score: float = Field(ge=0.0, le=1.0)

    # Metadata
    constitutional_hash: str = "cdd01ef066bc6cf2"
    test_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CoordinationCausalAnalysisResult(BaseModel):
    """Result of causal coordination analysis"""

    analysis_id: str
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Overall coordination metrics
    overall_coordination_quality: float = Field(ge=0.0, le=1.0)
    causal_sensitivity_score: float = Field(ge=0.0, le=1.0)
    spurious_invariance_score: float = Field(ge=0.0, le=1.0)
    coordination_robustness_score: float = Field(ge=0.0, le=1.0)

    # Detailed results
    test_results: List[CoordinationTestResult] = Field(default_factory=list)
    causal_factors: Dict[str, float] = Field(default_factory=dict)
    spurious_correlations: Dict[str, float] = Field(default_factory=dict)

    # Quality assessments
    coordination_metrics: Dict[CoordinationQualityMetric, float] = Field(
        default_factory=dict
    )
    constitutional_adherence: float = Field(ge=0.0, le=1.0)

    # Recommendations
    coordination_improvements: List[str] = Field(default_factory=list)
    robustness_recommendations: List[str] = Field(default_factory=list)

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CausalCoordinationModel:
    """CARMA-inspired causal model for coordination quality assessment"""

    # Target sensitivity levels for causal coordination attributes
    COORDINATION_SENSITIVITY_TARGETS = {
        CoordinationAttribute.TASK_COMPLETION_ACCURACY: 0.9,
        CoordinationAttribute.COMMUNICATION_CLARITY: 0.8,
        CoordinationAttribute.RESOURCE_EFFICIENCY: 0.7,
        CoordinationAttribute.CONFLICT_RESOLUTION: 0.85,
        CoordinationAttribute.KNOWLEDGE_SHARING: 0.75,
        CoordinationAttribute.GOAL_ALIGNMENT: 0.9,
        CoordinationAttribute.ADAPTATION_CAPABILITY: 0.8,
        CoordinationAttribute.CONSTITUTIONAL_COMPLIANCE: 0.95,
        CoordinationAttribute.DECISION_QUALITY: 0.85,
        CoordinationAttribute.STAKEHOLDER_SATISFACTION: 0.7,
    }

    # Maximum acceptable correlation for spurious attributes
    SPURIOUS_CORRELATION_LIMITS = {
        SpuriousCoordinationAttribute.RESPONSE_TIMING: 0.1,
        SpuriousCoordinationAttribute.MESSAGE_LENGTH: 0.15,
        SpuriousCoordinationAttribute.AGENT_IDENTIFIER_FORMAT: 0.05,
        SpuriousCoordinationAttribute.COMMUNICATION_STYLE: 0.2,
        SpuriousCoordinationAttribute.METADATA_VERBOSITY: 0.1,
        SpuriousCoordinationAttribute.TECHNICAL_JARGON_USAGE: 0.15,
        SpuriousCoordinationAttribute.TIMESTAMP_PRECISION: 0.05,
        SpuriousCoordinationAttribute.LOG_FORMAT_STYLE: 0.05,
        SpuriousCoordinationAttribute.AGENT_PERSONALITY_TRAITS: 0.25,
    }

    def __init__(
        self,
        blackboard_service: BlackboardService,
        constitutional_validator: ConstitutionalSafetyValidator,
        ai_model_service: Optional[AIModelService] = None,
    ):
        """Initialize causal coordination model"""
        self.blackboard = blackboard_service
        self.constitutional_validator = constitutional_validator
        self.ai_model_service = ai_model_service
        self.logger = logging.getLogger(__name__)

        # Model statistics
        self.model_stats = {
            "coordination_analyses": 0,
            "causal_tests_performed": 0,
            "spurious_correlations_detected": 0,
            "coordination_improvements_suggested": 0,
        }

    async def analyze_coordination_quality(
        self,
        coordination_scenario: CoordinationScenario,
        coordination_function: callable,
        test_attributes: Optional[Dict[str, List]] = None,
        enable_counterfactual_testing: bool = True,
    ) -> CoordinationCausalAnalysisResult:
        """Perform causal analysis of coordination quality"""

        analysis_id = str(uuid4())
        self.logger.info(f"Starting coordination causal analysis: {analysis_id}")

        # Validate constitutional compliance
        if coordination_scenario.constitutional_hash != "cdd01ef066bc6cf2":
            raise ValueError(
                "Constitutional hash validation required for coordination analysis"
            )

        # Set default test attributes
        if test_attributes is None:
            test_attributes = {
                "causal": list(CoordinationAttribute),
                "spurious": list(SpuriousCoordinationAttribute),
            }

        all_test_results = []

        # Test causal coordination attribute sensitivity
        causal_results = await self._test_causal_coordination_sensitivity(
            coordination_scenario,
            coordination_function,
            test_attributes.get("causal", []),
            enable_counterfactual_testing,
        )
        all_test_results.extend(causal_results)

        # Test spurious attribute invariance
        spurious_results = await self._test_spurious_coordination_invariance(
            coordination_scenario,
            coordination_function,
            test_attributes.get("spurious", []),
            enable_counterfactual_testing,
        )
        all_test_results.extend(spurious_results)

        # Calculate overall coordination metrics
        coordination_metrics = await self._calculate_coordination_metrics(
            coordination_scenario, coordination_function
        )

        # Analyze causal factors and spurious correlations
        causal_factors = self._extract_causal_factors(all_test_results)
        spurious_correlations = self._extract_spurious_correlations(all_test_results)

        # Calculate robustness scores
        causal_sensitivity = self._calculate_causal_sensitivity_score(causal_factors)
        spurious_invariance = self._calculate_spurious_invariance_score(
            spurious_correlations
        )
        coordination_robustness = causal_sensitivity * 0.7 + spurious_invariance * 0.3

        # Generate improvement recommendations
        coordination_improvements = self._generate_coordination_improvements(
            coordination_metrics, causal_factors, spurious_correlations
        )
        robustness_recommendations = self._generate_robustness_recommendations(
            causal_sensitivity, spurious_invariance, coordination_robustness
        )

        # Create analysis result
        analysis_result = CoordinationCausalAnalysisResult(
            analysis_id=analysis_id,
            overall_coordination_quality=coordination_metrics.get(
                CoordinationQualityMetric.EFFECTIVENESS, 0.0
            ),
            causal_sensitivity_score=causal_sensitivity,
            spurious_invariance_score=spurious_invariance,
            coordination_robustness_score=coordination_robustness,
            test_results=all_test_results,
            causal_factors=causal_factors,
            spurious_correlations=spurious_correlations,
            coordination_metrics=coordination_metrics,
            constitutional_adherence=coordination_metrics.get(
                CoordinationQualityMetric.CONSTITUTIONAL_ADHERENCE, 0.0
            ),
            coordination_improvements=coordination_improvements,
            robustness_recommendations=robustness_recommendations,
        )

        # Log analysis results
        await self._log_coordination_analysis(analysis_result)

        # Update statistics
        self.model_stats["coordination_analyses"] += 1
        self.model_stats["causal_tests_performed"] += len(causal_results)
        if spurious_correlations:
            self.model_stats["spurious_correlations_detected"] += len(
                spurious_correlations
            )
        if coordination_improvements:
            self.model_stats["coordination_improvements_suggested"] += len(
                coordination_improvements
            )

        return analysis_result

    async def _test_causal_coordination_sensitivity(
        self,
        scenario: CoordinationScenario,
        coordination_function: callable,
        causal_attributes: List[CoordinationAttribute],
        enable_counterfactual: bool,
    ) -> List[CoordinationTestResult]:
        """Test sensitivity to causal coordination attributes"""

        test_results = []

        for attribute in causal_attributes:
            self.logger.debug(f"Testing coordination sensitivity for {attribute.value}")

            try:
                # Get baseline coordination quality
                baseline_quality = await self._evaluate_coordination_quality(
                    coordination_function, scenario
                )

                if enable_counterfactual:
                    # Generate improved coordination scenario
                    improved_scenario = await self._generate_coordination_improvement(
                        scenario, attribute
                    )
                    improved_quality = await self._evaluate_coordination_quality(
                        coordination_function, improved_scenario
                    )

                    # Generate degraded coordination scenario
                    degraded_scenario = await self._generate_coordination_degradation(
                        scenario, attribute
                    )
                    degraded_quality = await self._evaluate_coordination_quality(
                        coordination_function, degraded_scenario
                    )

                    # Calculate sensitivity
                    sensitivity = self._calculate_coordination_sensitivity(
                        baseline_quality, improved_quality, degraded_quality
                    )

                    # Check if meets target sensitivity
                    target = self.COORDINATION_SENSITIVITY_TARGETS.get(attribute, 0.7)
                    expected_change = True
                    actual_change = sensitivity >= target

                    test_result = CoordinationTestResult(
                        test_id=f"coord_causal_{attribute.value}_{uuid4()}",
                        scenario=scenario,
                        attribute_tested=attribute,
                        test_type="causal_sensitivity",
                        baseline_quality=baseline_quality,
                        intervention_quality=improved_quality,
                        expected_change=expected_change,
                        actual_change_detected=actual_change,
                        coordination_effectiveness=improved_quality,
                        constitutional_compliance=1.0,  # Assume compliant for now
                        robustness_score=sensitivity,
                        test_details={
                            "improved_quality": improved_quality,
                            "degraded_quality": degraded_quality,
                            "sensitivity_score": sensitivity,
                            "target_sensitivity": target,
                        },
                    )

                else:
                    # Simplified test without counterfactuals
                    test_result = CoordinationTestResult(
                        test_id=f"coord_causal_simple_{attribute.value}_{uuid4()}",
                        scenario=scenario,
                        attribute_tested=attribute,
                        test_type="causal_sensitivity_simple",
                        baseline_quality=baseline_quality,
                        intervention_quality=baseline_quality,
                        expected_change=True,
                        actual_change_detected=False,
                        coordination_effectiveness=baseline_quality,
                        constitutional_compliance=1.0,
                        robustness_score=0.5,  # Neutral score
                        test_details={"note": "No counterfactual testing available"},
                    )

                test_results.append(test_result)

            except Exception as e:
                self.logger.warning(
                    f"Failed to test coordination attribute {attribute.value}: {e}"
                )
                # Add failed test result
                failed_result = CoordinationTestResult(
                    test_id=f"coord_causal_failed_{attribute.value}_{uuid4()}",
                    scenario=scenario,
                    attribute_tested=attribute,
                    test_type="causal_sensitivity_failed",
                    baseline_quality=0.0,
                    intervention_quality=0.0,
                    expected_change=True,
                    actual_change_detected=False,
                    coordination_effectiveness=0.0,
                    constitutional_compliance=0.0,
                    robustness_score=0.0,
                    test_details={"error": str(e)},
                )
                test_results.append(failed_result)

        return test_results

    async def _test_spurious_coordination_invariance(
        self,
        scenario: CoordinationScenario,
        coordination_function: callable,
        spurious_attributes: List[SpuriousCoordinationAttribute],
        enable_counterfactual: bool,
    ) -> List[CoordinationTestResult]:
        """Test invariance to spurious coordination attributes"""

        test_results = []

        for attribute in spurious_attributes:
            self.logger.debug(f"Testing coordination invariance for {attribute.value}")

            try:
                # Get baseline coordination quality
                baseline_quality = await self._evaluate_coordination_quality(
                    coordination_function, scenario
                )

                if enable_counterfactual:
                    # Generate spurious variation
                    varied_scenario = (
                        await self._generate_spurious_coordination_variation(
                            scenario, attribute
                        )
                    )
                    varied_quality = await self._evaluate_coordination_quality(
                        coordination_function, varied_scenario
                    )

                    # Calculate correlation (should be low)
                    correlation = abs(varied_quality - baseline_quality)

                    # Check if within acceptable limits
                    limit = self.SPURIOUS_CORRELATION_LIMITS.get(attribute, 0.1)
                    expected_change = False
                    actual_change = correlation > limit

                    test_result = CoordinationTestResult(
                        test_id=f"coord_spurious_{attribute.value}_{uuid4()}",
                        scenario=scenario,
                        attribute_tested=attribute,
                        test_type="spurious_invariance",
                        baseline_quality=baseline_quality,
                        intervention_quality=varied_quality,
                        expected_change=expected_change,
                        actual_change_detected=actual_change,
                        coordination_effectiveness=min(
                            baseline_quality, varied_quality
                        ),
                        constitutional_compliance=1.0,
                        robustness_score=1.0
                        - correlation,  # Higher invariance = higher score
                        test_details={
                            "correlation_strength": correlation,
                            "correlation_limit": limit,
                            "invariance_achieved": not actual_change,
                        },
                    )

                else:
                    # Simplified test
                    test_result = CoordinationTestResult(
                        test_id=f"coord_spurious_simple_{attribute.value}_{uuid4()}",
                        scenario=scenario,
                        attribute_tested=attribute,
                        test_type="spurious_invariance_simple",
                        baseline_quality=baseline_quality,
                        intervention_quality=baseline_quality,
                        expected_change=False,
                        actual_change_detected=False,
                        coordination_effectiveness=baseline_quality,
                        constitutional_compliance=1.0,
                        robustness_score=1.0,  # Assume perfect invariance
                        test_details={"note": "No variation testing available"},
                    )

                test_results.append(test_result)

            except Exception as e:
                self.logger.warning(
                    f"Failed to test spurious attribute {attribute.value}: {e}"
                )
                failed_result = CoordinationTestResult(
                    test_id=f"coord_spurious_failed_{attribute.value}_{uuid4()}",
                    scenario=scenario,
                    attribute_tested=attribute,
                    test_type="spurious_invariance_failed",
                    baseline_quality=0.0,
                    intervention_quality=0.0,
                    expected_change=False,
                    actual_change_detected=True,  # Assume failure means correlation
                    coordination_effectiveness=0.0,
                    constitutional_compliance=0.0,
                    robustness_score=0.0,
                    test_details={"error": str(e)},
                )
                test_results.append(failed_result)

        return test_results

    async def _evaluate_coordination_quality(
        self, coordination_function: callable, scenario: CoordinationScenario
    ) -> float:
        """Evaluate coordination quality for given scenario"""

        try:
            if asyncio.iscoroutinefunction(coordination_function):
                result = await coordination_function(scenario)
            else:
                result = coordination_function(scenario)

            # Extract quality score from result
            if isinstance(result, (int, float)):
                return float(max(0.0, min(1.0, result)))
            elif isinstance(result, dict):
                return float(
                    result.get("quality_score", result.get("effectiveness", 0.5))
                )
            elif hasattr(result, "quality_score"):
                return float(result.quality_score)
            else:
                return 0.5  # Default neutral score

        except Exception as e:
            self.logger.warning(f"Coordination function evaluation failed: {e}")
            return 0.0

    async def _generate_coordination_improvement(
        self, scenario: CoordinationScenario, attribute: CoordinationAttribute
    ) -> CoordinationScenario:
        """Generate improved coordination scenario for specific attribute"""

        improved_scenario = CoordinationScenario(
            scenario_id=f"{scenario.scenario_id}_improved_{attribute.value}",
            agents_involved=scenario.agents_involved.copy(),
            task_description=scenario.task_description.copy(),
            coordination_context=scenario.coordination_context.copy(),
            expected_outcomes=scenario.expected_outcomes.copy(),
            constitutional_requirements=scenario.constitutional_requirements.copy(),
            metadata=scenario.metadata.copy(),
        )

        # Apply attribute-specific improvements
        if attribute == CoordinationAttribute.COMMUNICATION_CLARITY:
            improved_scenario.coordination_context["communication_enhancement"] = True
            improved_scenario.coordination_context["clarity_protocols"] = [
                "structured_messaging",
                "clear_objectives",
            ]
        elif attribute == CoordinationAttribute.TASK_COMPLETION_ACCURACY:
            improved_scenario.coordination_context["accuracy_enhancement"] = True
            improved_scenario.coordination_context["quality_checks"] = [
                "validation_steps",
                "peer_review",
            ]
        elif attribute == CoordinationAttribute.RESOURCE_EFFICIENCY:
            improved_scenario.coordination_context["efficiency_optimization"] = True
            improved_scenario.coordination_context["resource_management"] = [
                "optimal_allocation",
                "waste_reduction",
            ]
        elif attribute == CoordinationAttribute.CONSTITUTIONAL_COMPLIANCE:
            improved_scenario.coordination_context["compliance_enhancement"] = True
            improved_scenario.coordination_context["constitutional_checks"] = [
                "pre_execution",
                "runtime",
                "post_execution",
            ]

        improved_scenario.metadata["causal_improvement"] = attribute.value
        improved_scenario.metadata["improvement_type"] = "causal_enhancement"

        return improved_scenario

    async def _generate_coordination_degradation(
        self, scenario: CoordinationScenario, attribute: CoordinationAttribute
    ) -> CoordinationScenario:
        """Generate degraded coordination scenario for specific attribute"""

        degraded_scenario = CoordinationScenario(
            scenario_id=f"{scenario.scenario_id}_degraded_{attribute.value}",
            agents_involved=scenario.agents_involved.copy(),
            task_description=scenario.task_description.copy(),
            coordination_context=scenario.coordination_context.copy(),
            expected_outcomes=scenario.expected_outcomes.copy(),
            constitutional_requirements=scenario.constitutional_requirements.copy(),
            metadata=scenario.metadata.copy(),
        )

        # Apply attribute-specific degradations
        if attribute == CoordinationAttribute.COMMUNICATION_CLARITY:
            degraded_scenario.coordination_context["communication_degradation"] = True
            degraded_scenario.coordination_context["clarity_issues"] = [
                "ambiguous_messages",
                "unclear_objectives",
            ]
        elif attribute == CoordinationAttribute.TASK_COMPLETION_ACCURACY:
            degraded_scenario.coordination_context["accuracy_degradation"] = True
            degraded_scenario.coordination_context["quality_issues"] = [
                "skipped_validation",
                "no_review",
            ]
        elif attribute == CoordinationAttribute.RESOURCE_EFFICIENCY:
            degraded_scenario.coordination_context["efficiency_degradation"] = True
            degraded_scenario.coordination_context["resource_waste"] = [
                "poor_allocation",
                "redundant_work",
            ]
        elif attribute == CoordinationAttribute.CONSTITUTIONAL_COMPLIANCE:
            degraded_scenario.coordination_context["compliance_degradation"] = True
            degraded_scenario.coordination_context["constitutional_risks"] = [
                "bypass_attempts",
                "validation_skips",
            ]

        degraded_scenario.metadata["causal_degradation"] = attribute.value
        degraded_scenario.metadata["degradation_type"] = "causal_reduction"

        return degraded_scenario

    async def _generate_spurious_coordination_variation(
        self, scenario: CoordinationScenario, attribute: SpuriousCoordinationAttribute
    ) -> CoordinationScenario:
        """Generate spurious variation preserving coordination quality"""

        varied_scenario = CoordinationScenario(
            scenario_id=f"{scenario.scenario_id}_spurious_{attribute.value}",
            agents_involved=scenario.agents_involved.copy(),
            task_description=scenario.task_description.copy(),
            coordination_context=scenario.coordination_context.copy(),
            expected_outcomes=scenario.expected_outcomes.copy(),
            constitutional_requirements=scenario.constitutional_requirements.copy(),
            metadata=scenario.metadata.copy(),
        )

        # Apply spurious variations
        if attribute == SpuriousCoordinationAttribute.RESPONSE_TIMING:
            varied_scenario.metadata["response_timing_variation"] = "delayed_responses"
        elif attribute == SpuriousCoordinationAttribute.MESSAGE_LENGTH:
            varied_scenario.metadata["message_length_variation"] = (
                "verbose" if len(str(scenario)) < 1000 else "concise"
            )
        elif attribute == SpuriousCoordinationAttribute.COMMUNICATION_STYLE:
            varied_scenario.metadata["communication_style_variation"] = (
                "formal" if "informal" in str(scenario).lower() else "informal"
            )
        elif attribute == SpuriousCoordinationAttribute.TECHNICAL_JARGON_USAGE:
            varied_scenario.metadata["jargon_variation"] = (
                "simplified" if "technical" in str(scenario).lower() else "technical"
            )
        elif attribute == SpuriousCoordinationAttribute.AGENT_PERSONALITY_TRAITS:
            varied_scenario.metadata["personality_variation"] = (
                "alternative_agent_personas"
            )

        varied_scenario.metadata["spurious_variation"] = attribute.value
        varied_scenario.metadata["coordination_content_preserved"] = True

        return varied_scenario

    def _calculate_coordination_sensitivity(
        self, baseline: float, improved: float, degraded: float
    ) -> float:
        """Calculate sensitivity to coordination changes"""

        sensitivity = 0.0

        # Good sensitivity: improvements should increase quality
        if improved > baseline:
            sensitivity += improved - baseline

        # Good sensitivity: degradations should decrease quality
        if degraded < baseline:
            sensitivity += baseline - degraded

        # Normalize to 0-1 range
        return min(1.0, sensitivity)

    async def _calculate_coordination_metrics(
        self, scenario: CoordinationScenario, coordination_function: callable
    ) -> Dict[CoordinationQualityMetric, float]:
        """Calculate comprehensive coordination quality metrics"""

        metrics = {}

        # Base effectiveness
        effectiveness = await self._evaluate_coordination_quality(
            coordination_function, scenario
        )
        metrics[CoordinationQualityMetric.EFFECTIVENESS] = effectiveness

        # Estimate other metrics based on scenario context
        metrics[CoordinationQualityMetric.EFFICIENCY] = (
            effectiveness * 0.9
        )  # Simplified
        metrics[CoordinationQualityMetric.ROBUSTNESS] = effectiveness * 0.8
        metrics[CoordinationQualityMetric.SCALABILITY] = effectiveness * 0.85
        metrics[CoordinationQualityMetric.TRANSPARENCY] = effectiveness * 0.75
        metrics[CoordinationQualityMetric.ADAPTABILITY] = effectiveness * 0.8

        # Constitutional adherence
        constitutional_score = (
            1.0 if scenario.constitutional_hash == "cdd01ef066bc6cf2" else 0.0
        )
        metrics[CoordinationQualityMetric.CONSTITUTIONAL_ADHERENCE] = (
            constitutional_score
        )

        return metrics

    def _extract_causal_factors(
        self, test_results: List[CoordinationTestResult]
    ) -> Dict[str, float]:
        """Extract causal factor scores from test results"""

        causal_factors = {}

        for result in test_results:
            if "causal" in result.test_type and isinstance(
                result.attribute_tested, CoordinationAttribute
            ):
                causal_factors[result.attribute_tested.value] = result.robustness_score

        return causal_factors

    def _extract_spurious_correlations(
        self, test_results: List[CoordinationTestResult]
    ) -> Dict[str, float]:
        """Extract spurious correlation scores from test results"""

        spurious_correlations = {}

        for result in test_results:
            if "spurious" in result.test_type and isinstance(
                result.attribute_tested, SpuriousCoordinationAttribute
            ):
                # For spurious tests, higher correlation is worse
                correlation_strength = 1.0 - result.robustness_score
                if correlation_strength > self.SPURIOUS_CORRELATION_LIMITS.get(
                    result.attribute_tested, 0.1
                ):
                    spurious_correlations[result.attribute_tested.value] = (
                        correlation_strength
                    )

        return spurious_correlations

    def _calculate_causal_sensitivity_score(
        self, causal_factors: Dict[str, float]
    ) -> float:
        """Calculate overall causal sensitivity score"""

        if not causal_factors:
            return 0.0

        # Weight by attribute importance
        weighted_scores = []
        for attr_name, score in causal_factors.items():
            try:
                attr = CoordinationAttribute(attr_name)
                target = self.COORDINATION_SENSITIVITY_TARGETS.get(attr, 0.7)
                weighted_score = score * target  # Weight by target importance
                weighted_scores.append(weighted_score)
            except ValueError:
                weighted_scores.append(score)

        return sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0

    def _calculate_spurious_invariance_score(
        self, spurious_correlations: Dict[str, float]
    ) -> float:
        """Calculate spurious invariance score"""

        if not spurious_correlations:
            return 1.0  # Perfect invariance if no correlations detected

        # Calculate average correlation strength (lower is better)
        avg_correlation = sum(spurious_correlations.values()) / len(
            spurious_correlations
        )
        return 1.0 - avg_correlation  # Invert: lower correlation = higher invariance

    def _generate_coordination_improvements(
        self,
        metrics: Dict[CoordinationQualityMetric, float],
        causal_factors: Dict[str, float],
        spurious_correlations: Dict[str, float],
    ) -> List[str]:
        """Generate coordination improvement recommendations"""

        improvements = []

        # Effectiveness improvements
        if metrics.get(CoordinationQualityMetric.EFFECTIVENESS, 0.0) < 0.7:
            improvements.append(
                "Enhance overall coordination effectiveness through better task decomposition"
            )

        # Causal factor improvements
        for factor, score in causal_factors.items():
            if score < 0.6:
                improvements.append(
                    f"Improve {factor} through targeted training and process optimization"
                )

        # Constitutional adherence
        if metrics.get(CoordinationQualityMetric.CONSTITUTIONAL_ADHERENCE, 0.0) < 0.9:
            improvements.append(
                "Strengthen constitutional compliance in coordination processes"
            )

        # Spurious correlation mitigation
        if spurious_correlations:
            improvements.append(
                "Implement spurious correlation mitigation in coordination assessment"
            )

        return improvements

    def _generate_robustness_recommendations(
        self,
        causal_sensitivity: float,
        spurious_invariance: float,
        overall_robustness: float,
    ) -> List[str]:
        """Generate robustness improvement recommendations"""

        recommendations = []

        if causal_sensitivity < 0.7:
            recommendations.append(
                "Apply CARMA-style causal augmentation to coordination training"
            )
            recommendations.append(
                "Increase sensitivity to genuine coordination quality factors"
            )

        if spurious_invariance < 0.8:
            recommendations.append(
                "Add neutral augmentations for spurious invariance in coordination"
            )
            recommendations.append(
                "Implement spurious correlation detection in coordination metrics"
            )

        if overall_robustness < 0.6:
            recommendations.append(
                "Apply comprehensive CARMA methodology to coordination assessment"
            )
            recommendations.append(
                "Implement counterfactual robustness testing for coordination"
            )

        return recommendations

    async def _log_coordination_analysis(
        self, analysis_result: CoordinationCausalAnalysisResult
    ) -> None:
        """Log coordination analysis to blackboard"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "coordination_causal_analysis",
                "analysis_id": analysis_result.analysis_id,
                "coordination_metrics": {
                    "overall_quality": analysis_result.overall_coordination_quality,
                    "causal_sensitivity": analysis_result.causal_sensitivity_score,
                    "spurious_invariance": analysis_result.spurious_invariance_score,
                    "robustness": analysis_result.coordination_robustness_score,
                },
                "causal_factors": analysis_result.causal_factors,
                "spurious_correlations": analysis_result.spurious_correlations,
                "constitutional_adherence": analysis_result.constitutional_adherence,
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "causal_coordination_model",
                "timestamp": analysis_result.timestamp.isoformat(),
                "coordination_quality": (
                    "high"
                    if analysis_result.overall_coordination_quality >= 0.8
                    else (
                        "medium"
                        if analysis_result.overall_coordination_quality >= 0.6
                        else "low"
                    )
                ),
            },
            tags=[
                "coordination",
                "causal",
                "carma",
                "quality_assessment",
                "robustness",
            ],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    def get_model_statistics(self) -> Dict[str, Any]:
        """Get coordination model statistics"""

        stats = self.model_stats.copy()
        stats.update(
            {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "model_version": "1.0.0_carma_inspired",
                "spurious_detection_rate": (
                    stats.get("spurious_correlations_detected", 0)
                    / max(1, stats.get("coordination_analyses", 1))
                ),
                "improvement_suggestion_rate": (
                    stats.get("coordination_improvements_suggested", 0)
                    / max(1, stats.get("coordination_analyses", 1))
                ),
            }
        )

        return stats
