"""
Counterfactual Coordination Tester
Constitutional Hash: cdd01ef066bc6cf2

CARMA-inspired counterfactual testing framework for multi-agent coordination systems.
Tests coordination robustness through systematic counterfactual scenario generation
and causal attribution analysis.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from .ai_model_service import AIModelService
from .blackboard import BlackboardService, KnowledgeItem
from .causal_coordination_model import (
    CoordinationAttribute,
    CoordinationQualityMetric,
    CoordinationScenario,
    SpuriousCoordinationAttribute,
)
from .robust_coordination_metrics import (
    CoordinationMetricType,
    MetricMeasurement,
    RobustCoordinationMetrics,
)

# Configure logging
logger = logging.getLogger(__name__)


class CounterfactualTestType(Enum):
    """Types of counterfactual tests for coordination"""

    CAUSAL_SENSITIVITY = "causal_sensitivity"
    SPURIOUS_INVARIANCE = "spurious_invariance"
    ROBUSTNESS_STRESS = "robustness_stress"
    EDGE_CASE = "edge_case"
    ADVERSARIAL = "adversarial"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"


class CoordinationInterventionType(Enum):
    """Types of interventions for coordination testing"""

    IMPROVE_COMMUNICATION = "improve_communication"
    DEGRADE_COMMUNICATION = "degrade_communication"
    ENHANCE_TASK_CLARITY = "enhance_task_clarity"
    OBSCURE_TASK_OBJECTIVES = "obscure_task_objectives"
    OPTIMIZE_RESOURCE_ALLOCATION = "optimize_resource_allocation"
    CONSTRAIN_RESOURCES = "constrain_resources"
    STRENGTHEN_COORDINATION = "strengthen_coordination"
    DISRUPT_COORDINATION = "disrupt_coordination"
    VARY_AGENT_PERSONALITIES = "vary_agent_personalities"
    CHANGE_COMMUNICATION_STYLE = "change_communication_style"
    MODIFY_RESPONSE_TIMING = "modify_response_timing"
    ALTER_MESSAGE_FORMAT = "alter_message_format"


@dataclass
class CoordinationCounterfactual:
    """Single counterfactual scenario for coordination testing"""

    counterfactual_id: str
    original_scenario: CoordinationScenario
    modified_scenario: CoordinationScenario
    intervention_type: CoordinationInterventionType
    test_type: CounterfactualTestType
    target_attribute: Union[CoordinationAttribute, SpuriousCoordinationAttribute]
    expected_outcome: str  # "improvement", "degradation", "no_change"
    constitutional_hash: str = "cdd01ef066bc6cf2"
    metadata: Dict[str, Any] = field(default_factory=dict)
    generation_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class CounterfactualTestResult:
    """Result of counterfactual coordination test"""

    test_id: str
    counterfactual: CoordinationCounterfactual

    # Test execution results
    original_coordination_quality: float = Field(ge=0.0, le=1.0)
    modified_coordination_quality: float = Field(ge=0.0, le=1.0)
    quality_change: float  # modified - original

    # Test validation
    expected_outcome_achieved: bool
    causal_attribution_score: float = Field(ge=0.0, le=1.0)
    spurious_resistance_score: float = Field(ge=0.0, le=1.0)

    # Performance metrics
    original_metrics: Dict[str, float] = field(default_factory=dict)
    modified_metrics: Dict[str, float] = field(default_factory=dict)
    metric_changes: Dict[str, float] = field(default_factory=dict)

    # Constitutional compliance
    constitutional_compliance_maintained: bool = True
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Metadata
    execution_time_ms: float = 0.0
    test_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CounterfactualTestSuite(BaseModel):
    """Complete test suite for coordination system"""

    suite_id: str
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Test configuration
    base_scenarios: List[CoordinationScenario] = Field(default_factory=list)
    test_types_enabled: List[CounterfactualTestType] = Field(default_factory=list)
    causal_attributes_tested: List[CoordinationAttribute] = Field(default_factory=list)
    spurious_attributes_tested: List[SpuriousCoordinationAttribute] = Field(
        default_factory=list
    )

    # Test results
    counterfactuals_generated: List[CoordinationCounterfactual] = Field(
        default_factory=list
    )
    test_results: List[CounterfactualTestResult] = Field(default_factory=list)

    # Summary metrics
    total_tests_executed: int = 0
    tests_passed: int = 0
    causal_sensitivity_score: float = Field(ge=0.0, le=1.0, default=0.0)
    spurious_invariance_score: float = Field(ge=0.0, le=1.0, default=0.0)
    overall_robustness_score: float = Field(ge=0.0, le=1.0, default=0.0)

    creation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completion_timestamp: Optional[datetime] = None


class CounterfactualCoordinationTester:
    """Service for comprehensive counterfactual testing of coordination systems"""

    # Intervention templates for different coordination aspects
    INTERVENTION_TEMPLATES = {
        CoordinationInterventionType.IMPROVE_COMMUNICATION: """
        Enhance the communication aspects of this coordination scenario:
        {scenario}
        
        Improvements to apply:
        - Increase message clarity and precision
        - Add structured communication protocols
        - Enhance information sharing mechanisms
        - Improve feedback loops between agents
        
        Maintain constitutional hash: cdd01ef066bc6cf2
        Preserve task objectives and agent roles while improving communication.
        """,
        CoordinationInterventionType.DEGRADE_COMMUNICATION: """
        Introduce communication issues into this coordination scenario:
        {scenario}
        
        Degradations to apply:
        - Reduce message clarity
        - Introduce communication delays
        - Add ambiguous instructions
        - Create information bottlenecks
        
        Maintain constitutional hash: cdd01ef066bc6cf2
        Preserve core task while degrading communication quality.
        """,
        CoordinationInterventionType.ENHANCE_TASK_CLARITY: """
        Improve task clarity and objective definition in this coordination scenario:
        {scenario}
        
        Enhancements to apply:
        - Clarify task objectives and success criteria
        - Define clear roles and responsibilities
        - Establish measurable milestones
        - Provide comprehensive context
        
        Maintain constitutional hash: cdd01ef066bc6cf2
        Focus on task clarity while preserving coordination context.
        """,
        CoordinationInterventionType.VARY_AGENT_PERSONALITIES: """
        Modify agent personality traits in this coordination scenario:
        {scenario}
        
        Variations to apply:
        - Change agent communication styles
        - Alter decision-making approaches
        - Modify collaboration preferences
        - Adjust personality characteristics
        
        Maintain constitutional hash: cdd01ef066bc6cf2
        Preserve task objectives while varying agent personalities.
        """,
        CoordinationInterventionType.CHANGE_COMMUNICATION_STYLE: """
        Alter communication style in this coordination scenario:
        {scenario}
        
        Style changes to apply:
        - Modify formality level (formal ↔ informal)
        - Change technical complexity (technical ↔ simplified)
        - Alter verbosity (concise ↔ detailed)
        - Adjust tone (direct ↔ diplomatic)
        
        Maintain constitutional hash: cdd01ef066bc6cf2
        Preserve coordination content while changing communication style.
        """,
    }

    # Expected sensitivity targets for causal attributes
    CAUSAL_SENSITIVITY_TARGETS = {
        CoordinationAttribute.TASK_COMPLETION_ACCURACY: 0.8,
        CoordinationAttribute.COMMUNICATION_CLARITY: 0.9,
        CoordinationAttribute.RESOURCE_EFFICIENCY: 0.7,
        CoordinationAttribute.CONFLICT_RESOLUTION: 0.85,
        CoordinationAttribute.KNOWLEDGE_SHARING: 0.75,
        CoordinationAttribute.GOAL_ALIGNMENT: 0.9,
        CoordinationAttribute.CONSTITUTIONAL_COMPLIANCE: 0.95,
    }

    # Maximum acceptable correlation for spurious attributes
    SPURIOUS_CORRELATION_LIMITS = {
        SpuriousCoordinationAttribute.RESPONSE_TIMING: 0.1,
        SpuriousCoordinationAttribute.MESSAGE_LENGTH: 0.15,
        SpuriousCoordinationAttribute.COMMUNICATION_STYLE: 0.2,
        SpuriousCoordinationAttribute.AGENT_PERSONALITY_TRAITS: 0.25,
        SpuriousCoordinationAttribute.TECHNICAL_JARGON_USAGE: 0.15,
    }

    def __init__(
        self,
        blackboard_service: BlackboardService,
        robust_metrics_service: RobustCoordinationMetrics,
        ai_model_service: Optional[AIModelService] = None,
    ):
        """Initialize counterfactual coordination tester"""
        self.blackboard = blackboard_service
        self.robust_metrics = robust_metrics_service
        self.ai_model_service = ai_model_service
        self.logger = logging.getLogger(__name__)

        # Testing statistics
        self.testing_stats = {
            "test_suites_executed": 0,
            "counterfactuals_generated": 0,
            "tests_executed": 0,
            "causal_tests_passed": 0,
            "spurious_tests_passed": 0,
            "robustness_improvements_identified": 0,
        }

    async def execute_counterfactual_test_suite(
        self,
        base_scenarios: List[CoordinationScenario],
        coordination_function: Callable,
        test_types: Optional[List[CounterfactualTestType]] = None,
        causal_attributes: Optional[List[CoordinationAttribute]] = None,
        spurious_attributes: Optional[List[SpuriousCoordinationAttribute]] = None,
    ) -> CounterfactualTestSuite:
        """Execute comprehensive counterfactual test suite"""

        suite_id = str(uuid4())
        self.logger.info(f"Executing counterfactual test suite: {suite_id}")

        # Set defaults
        if test_types is None:
            test_types = [
                CounterfactualTestType.CAUSAL_SENSITIVITY,
                CounterfactualTestType.SPURIOUS_INVARIANCE,
                CounterfactualTestType.CONSTITUTIONAL_COMPLIANCE,
            ]

        if causal_attributes is None:
            causal_attributes = [
                CoordinationAttribute.COMMUNICATION_CLARITY,
                CoordinationAttribute.TASK_COMPLETION_ACCURACY,
                CoordinationAttribute.CONSTITUTIONAL_COMPLIANCE,
            ]

        if spurious_attributes is None:
            spurious_attributes = [
                SpuriousCoordinationAttribute.COMMUNICATION_STYLE,
                SpuriousCoordinationAttribute.MESSAGE_LENGTH,
                SpuriousCoordinationAttribute.AGENT_PERSONALITY_TRAITS,
            ]

        # Create test suite
        test_suite = CounterfactualTestSuite(
            suite_id=suite_id,
            base_scenarios=base_scenarios,
            test_types_enabled=test_types,
            causal_attributes_tested=causal_attributes,
            spurious_attributes_tested=spurious_attributes,
        )

        # Generate counterfactuals
        all_counterfactuals = await self._generate_test_counterfactuals(
            base_scenarios, test_types, causal_attributes, spurious_attributes
        )
        test_suite.counterfactuals_generated = all_counterfactuals

        # Execute tests
        all_test_results = []
        for counterfactual in all_counterfactuals:
            test_result = await self._execute_counterfactual_test(
                counterfactual, coordination_function
            )
            all_test_results.append(test_result)

        test_suite.test_results = all_test_results

        # Calculate summary metrics
        await self._calculate_test_suite_metrics(test_suite)

        # Complete test suite
        test_suite.completion_timestamp = datetime.now(timezone.utc)

        # Log test suite results
        await self._log_test_suite_results(test_suite)

        # Update statistics
        self.testing_stats["test_suites_executed"] += 1
        self.testing_stats["counterfactuals_generated"] += len(all_counterfactuals)
        self.testing_stats["tests_executed"] += len(all_test_results)

        return test_suite

    async def _generate_test_counterfactuals(
        self,
        base_scenarios: List[CoordinationScenario],
        test_types: List[CounterfactualTestType],
        causal_attributes: List[CoordinationAttribute],
        spurious_attributes: List[SpuriousCoordinationAttribute],
    ) -> List[CoordinationCounterfactual]:
        """Generate counterfactuals for testing"""

        all_counterfactuals = []

        for scenario in base_scenarios:
            # Generate causal sensitivity tests
            if CounterfactualTestType.CAUSAL_SENSITIVITY in test_types:
                causal_counterfactuals = await self._generate_causal_counterfactuals(
                    scenario, causal_attributes
                )
                all_counterfactuals.extend(causal_counterfactuals)

            # Generate spurious invariance tests
            if CounterfactualTestType.SPURIOUS_INVARIANCE in test_types:
                spurious_counterfactuals = (
                    await self._generate_spurious_counterfactuals(
                        scenario, spurious_attributes
                    )
                )
                all_counterfactuals.extend(spurious_counterfactuals)

            # Generate constitutional compliance tests
            if CounterfactualTestType.CONSTITUTIONAL_COMPLIANCE in test_types:
                constitutional_counterfactuals = (
                    await self._generate_constitutional_counterfactuals(scenario)
                )
                all_counterfactuals.extend(constitutional_counterfactuals)

            # Generate edge case tests
            if CounterfactualTestType.EDGE_CASE in test_types:
                edge_case_counterfactuals = (
                    await self._generate_edge_case_counterfactuals(scenario)
                )
                all_counterfactuals.extend(edge_case_counterfactuals)

        return all_counterfactuals

    async def _generate_causal_counterfactuals(
        self,
        scenario: CoordinationScenario,
        causal_attributes: List[CoordinationAttribute],
    ) -> List[CoordinationCounterfactual]:
        """Generate counterfactuals for causal sensitivity testing"""

        counterfactuals = []

        for attribute in causal_attributes:
            # Generate improvement counterfactual
            improved_scenario = await self._apply_causal_improvement(
                scenario, attribute
            )
            if improved_scenario:
                counterfactual = CoordinationCounterfactual(
                    counterfactual_id=f"causal_improve_{attribute.value}_{uuid4()}",
                    original_scenario=scenario,
                    modified_scenario=improved_scenario,
                    intervention_type=self._get_improvement_intervention(attribute),
                    test_type=CounterfactualTestType.CAUSAL_SENSITIVITY,
                    target_attribute=attribute,
                    expected_outcome="improvement",
                    metadata={
                        "causal_attribute": attribute.value,
                        "intervention_direction": "improvement",
                        "generation_method": "causal_enhancement",
                    },
                )
                counterfactuals.append(counterfactual)

            # Generate degradation counterfactual
            degraded_scenario = await self._apply_causal_degradation(
                scenario, attribute
            )
            if degraded_scenario:
                counterfactual = CoordinationCounterfactual(
                    counterfactual_id=f"causal_degrade_{attribute.value}_{uuid4()}",
                    original_scenario=scenario,
                    modified_scenario=degraded_scenario,
                    intervention_type=self._get_degradation_intervention(attribute),
                    test_type=CounterfactualTestType.CAUSAL_SENSITIVITY,
                    target_attribute=attribute,
                    expected_outcome="degradation",
                    metadata={
                        "causal_attribute": attribute.value,
                        "intervention_direction": "degradation",
                        "generation_method": "causal_reduction",
                    },
                )
                counterfactuals.append(counterfactual)

        return counterfactuals

    async def _generate_spurious_counterfactuals(
        self,
        scenario: CoordinationScenario,
        spurious_attributes: List[SpuriousCoordinationAttribute],
    ) -> List[CoordinationCounterfactual]:
        """Generate counterfactuals for spurious invariance testing"""

        counterfactuals = []

        for attribute in spurious_attributes:
            # Generate spurious variation
            varied_scenario = await self._apply_spurious_variation(scenario, attribute)
            if varied_scenario:
                counterfactual = CoordinationCounterfactual(
                    counterfactual_id=f"spurious_{attribute.value}_{uuid4()}",
                    original_scenario=scenario,
                    modified_scenario=varied_scenario,
                    intervention_type=self._get_spurious_intervention(attribute),
                    test_type=CounterfactualTestType.SPURIOUS_INVARIANCE,
                    target_attribute=attribute,
                    expected_outcome="no_change",
                    metadata={
                        "spurious_attribute": attribute.value,
                        "coordination_content_preserved": True,
                        "generation_method": "spurious_variation",
                    },
                )
                counterfactuals.append(counterfactual)

        return counterfactuals

    async def _generate_constitutional_counterfactuals(
        self, scenario: CoordinationScenario
    ) -> List[CoordinationCounterfactual]:
        """Generate counterfactuals for constitutional compliance testing"""

        counterfactuals = []

        # Test constitutional hash validation
        modified_scenario = CoordinationScenario(
            scenario_id=f"{scenario.scenario_id}_const_test",
            agents_involved=scenario.agents_involved.copy(),
            task_description=scenario.task_description.copy(),
            coordination_context=scenario.coordination_context.copy(),
            expected_outcomes=scenario.expected_outcomes.copy(),
            constitutional_requirements=scenario.constitutional_requirements.copy(),
            constitutional_hash="invalid_hash_test",  # Intentionally invalid
            metadata=scenario.metadata.copy(),
        )

        counterfactual = CoordinationCounterfactual(
            counterfactual_id=f"constitutional_invalid_{uuid4()}",
            original_scenario=scenario,
            modified_scenario=modified_scenario,
            intervention_type=CoordinationInterventionType.VARY_AGENT_PERSONALITIES,  # Placeholder
            test_type=CounterfactualTestType.CONSTITUTIONAL_COMPLIANCE,
            target_attribute=CoordinationAttribute.CONSTITUTIONAL_COMPLIANCE,
            expected_outcome="degradation",
            metadata={
                "constitutional_test_type": "invalid_hash",
                "expected_failure": True,
            },
        )
        counterfactuals.append(counterfactual)

        return counterfactuals

    async def _generate_edge_case_counterfactuals(
        self, scenario: CoordinationScenario
    ) -> List[CoordinationCounterfactual]:
        """Generate edge case counterfactuals for stress testing"""

        counterfactuals = []

        # Extreme resource constraints
        constrained_scenario = CoordinationScenario(
            scenario_id=f"{scenario.scenario_id}_constrained",
            agents_involved=scenario.agents_involved.copy(),
            task_description=scenario.task_description.copy(),
            coordination_context=scenario.coordination_context.copy(),
            expected_outcomes=scenario.expected_outcomes.copy(),
            constitutional_requirements=scenario.constitutional_requirements.copy(),
            metadata=scenario.metadata.copy(),
        )
        constrained_scenario.coordination_context["resource_constraints"] = {
            "severe_time_pressure": True,
            "limited_communication_bandwidth": True,
            "reduced_agent_availability": True,
        }

        counterfactual = CoordinationCounterfactual(
            counterfactual_id=f"edge_case_constrained_{uuid4()}",
            original_scenario=scenario,
            modified_scenario=constrained_scenario,
            intervention_type=CoordinationInterventionType.CONSTRAIN_RESOURCES,
            test_type=CounterfactualTestType.EDGE_CASE,
            target_attribute=CoordinationAttribute.RESOURCE_EFFICIENCY,
            expected_outcome="degradation",
            metadata={"edge_case_type": "severe_constraints", "stress_test": True},
        )
        counterfactuals.append(counterfactual)

        return counterfactuals

    async def _execute_counterfactual_test(
        self,
        counterfactual: CoordinationCounterfactual,
        coordination_function: Callable,
    ) -> CounterfactualTestResult:
        """Execute single counterfactual test"""

        test_id = str(uuid4())
        start_time = time.time()

        try:
            # Execute original scenario
            original_quality = await self._evaluate_coordination_quality(
                coordination_function, counterfactual.original_scenario
            )
            original_metrics = await self._collect_coordination_metrics(
                coordination_function, counterfactual.original_scenario
            )

            # Execute modified scenario
            modified_quality = await self._evaluate_coordination_quality(
                coordination_function, counterfactual.modified_scenario
            )
            modified_metrics = await self._collect_coordination_metrics(
                coordination_function, counterfactual.modified_scenario
            )

            # Calculate quality change
            quality_change = modified_quality - original_quality

            # Validate expected outcome
            expected_outcome_achieved = self._validate_expected_outcome(
                counterfactual.expected_outcome, quality_change
            )

            # Calculate attribution scores
            causal_attribution_score = self._calculate_causal_attribution(
                counterfactual, quality_change
            )
            spurious_resistance_score = self._calculate_spurious_resistance(
                counterfactual, quality_change
            )

            # Calculate metric changes
            metric_changes = {}
            for metric_name in original_metrics:
                if metric_name in modified_metrics:
                    metric_changes[metric_name] = (
                        modified_metrics[metric_name] - original_metrics[metric_name]
                    )

            # Check constitutional compliance
            constitutional_compliance_maintained = (
                counterfactual.modified_scenario.constitutional_hash
                == "cdd01ef066bc6cf2"
                or counterfactual.test_type
                == CounterfactualTestType.CONSTITUTIONAL_COMPLIANCE
            )

            # Calculate test confidence
            test_confidence = self._calculate_test_confidence(
                counterfactual, original_quality, modified_quality
            )

            execution_time_ms = (time.time() - start_time) * 1000

            test_result = CounterfactualTestResult(
                test_id=test_id,
                counterfactual=counterfactual,
                original_coordination_quality=original_quality,
                modified_coordination_quality=modified_quality,
                quality_change=quality_change,
                expected_outcome_achieved=expected_outcome_achieved,
                causal_attribution_score=causal_attribution_score,
                spurious_resistance_score=spurious_resistance_score,
                original_metrics=original_metrics,
                modified_metrics=modified_metrics,
                metric_changes=metric_changes,
                constitutional_compliance_maintained=constitutional_compliance_maintained,
                execution_time_ms=execution_time_ms,
                test_confidence=test_confidence,
            )

            # Log test result
            await self._log_test_result(test_result)

            return test_result

        except Exception as e:
            self.logger.error(f"Counterfactual test execution failed: {e}")
            # Return failed test result
            return CounterfactualTestResult(
                test_id=test_id,
                counterfactual=counterfactual,
                original_coordination_quality=0.0,
                modified_coordination_quality=0.0,
                quality_change=0.0,
                expected_outcome_achieved=False,
                causal_attribution_score=0.0,
                spurious_resistance_score=0.0,
                constitutional_compliance_maintained=False,
                execution_time_ms=(time.time() - start_time) * 1000,
                test_confidence=0.0,
            )

    async def _evaluate_coordination_quality(
        self, coordination_function: Callable, scenario: CoordinationScenario
    ) -> float:
        """Evaluate coordination quality for scenario"""

        try:
            if asyncio.iscoroutinefunction(coordination_function):
                result = await coordination_function(scenario)
            else:
                result = coordination_function(scenario)

            # Extract quality score
            if isinstance(result, (int, float)):
                return float(max(0.0, min(1.0, result)))
            elif isinstance(result, dict):
                return float(
                    result.get("quality_score", result.get("effectiveness", 0.5))
                )
            else:
                return 0.5  # Default neutral score

        except Exception as e:
            self.logger.warning(f"Coordination quality evaluation failed: {e}")
            return 0.0

    async def _collect_coordination_metrics(
        self, coordination_function: Callable, scenario: CoordinationScenario
    ) -> Dict[str, float]:
        """Collect detailed coordination metrics"""

        metrics = {}

        try:
            # Basic quality metric
            quality = await self._evaluate_coordination_quality(
                coordination_function, scenario
            )
            metrics["overall_quality"] = quality

            # Estimate other metrics based on scenario context
            metrics["communication_efficiency"] = quality * 0.9
            metrics["resource_utilization"] = quality * 0.8
            metrics["task_completion_rate"] = quality * 0.95
            metrics["constitutional_compliance"] = (
                1.0 if scenario.constitutional_hash == "cdd01ef066bc6cf2" else 0.0
            )

        except Exception as e:
            self.logger.warning(f"Metric collection failed: {e}")
            metrics = {"overall_quality": 0.0}

        return metrics

    def _validate_expected_outcome(
        self, expected_outcome: str, quality_change: float
    ) -> bool:
        """Validate if expected outcome was achieved"""

        threshold = 0.05  # Minimum change to be considered significant

        if expected_outcome == "improvement":
            return quality_change > threshold
        elif expected_outcome == "degradation":
            return quality_change < -threshold
        elif expected_outcome == "no_change":
            return abs(quality_change) <= threshold
        else:
            return False

    def _calculate_causal_attribution(
        self, counterfactual: CoordinationCounterfactual, quality_change: float
    ) -> float:
        """Calculate causal attribution score"""

        if counterfactual.test_type == CounterfactualTestType.CAUSAL_SENSITIVITY:
            # For causal tests, measure how well change aligns with expectation
            if counterfactual.expected_outcome == "improvement":
                return max(0.0, min(1.0, quality_change * 2))  # Scale positive changes
            elif counterfactual.expected_outcome == "degradation":
                return max(0.0, min(1.0, -quality_change * 2))  # Scale negative changes

        return 0.5  # Neutral score for non-causal tests

    def _calculate_spurious_resistance(
        self, counterfactual: CoordinationCounterfactual, quality_change: float
    ) -> float:
        """Calculate spurious resistance score"""

        if counterfactual.test_type == CounterfactualTestType.SPURIOUS_INVARIANCE:
            # For spurious tests, lower change indicates better resistance
            resistance = 1.0 - min(1.0, abs(quality_change) * 5)  # Scale change impact
            return max(0.0, resistance)

        return 1.0  # Perfect resistance for non-spurious tests

    def _calculate_test_confidence(
        self,
        counterfactual: CoordinationCounterfactual,
        original_quality: float,
        modified_quality: float,
    ) -> float:
        """Calculate confidence in test results"""

        confidence_components = []

        # Data quality component
        if original_quality > 0.1 and modified_quality > 0.1:
            confidence_components.append(0.4)
        else:
            confidence_components.append(0.2)

        # Constitutional compliance component
        if counterfactual.modified_scenario.constitutional_hash == "cdd01ef066bc6cf2":
            confidence_components.append(0.3)
        else:
            confidence_components.append(0.1)

        # Intervention appropriateness component
        if counterfactual.intervention_type and counterfactual.target_attribute:
            confidence_components.append(0.3)
        else:
            confidence_components.append(0.1)

        return sum(confidence_components)

    # Helper methods for applying interventions
    async def _apply_causal_improvement(
        self, scenario: CoordinationScenario, attribute: CoordinationAttribute
    ) -> Optional[CoordinationScenario]:
        """Apply causal improvement intervention"""

        # Implementation details would depend on specific coordination system
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
        improved_scenario.coordination_context["causal_improvement"] = attribute.value
        improved_scenario.metadata["intervention_applied"] = True

        return improved_scenario

    async def _apply_causal_degradation(self, scenario, attribute):
        """Apply causal degradation intervention"""
        # Similar to improvement but with degradations
        degraded_scenario = CoordinationScenario(
            scenario_id=f"{scenario.scenario_id}_degraded_{attribute.value}",
            agents_involved=scenario.agents_involved.copy(),
            task_description=scenario.task_description.copy(),
            coordination_context=scenario.coordination_context.copy(),
            expected_outcomes=scenario.expected_outcomes.copy(),
            constitutional_requirements=scenario.constitutional_requirements.copy(),
            metadata=scenario.metadata.copy(),
        )

        degraded_scenario.coordination_context["causal_degradation"] = attribute.value
        degraded_scenario.metadata["intervention_applied"] = True

        return degraded_scenario

    async def _apply_spurious_variation(self, scenario, attribute):
        """Apply spurious variation"""
        varied_scenario = CoordinationScenario(
            scenario_id=f"{scenario.scenario_id}_spurious_{attribute.value}",
            agents_involved=scenario.agents_involved.copy(),
            task_description=scenario.task_description.copy(),
            coordination_context=scenario.coordination_context.copy(),
            expected_outcomes=scenario.expected_outcomes.copy(),
            constitutional_requirements=scenario.constitutional_requirements.copy(),
            metadata=scenario.metadata.copy(),
        )

        varied_scenario.metadata["spurious_variation"] = attribute.value
        varied_scenario.metadata["coordination_content_preserved"] = True

        return varied_scenario

    # Helper methods for intervention mapping
    def _get_improvement_intervention(
        self, attribute: CoordinationAttribute
    ) -> CoordinationInterventionType:
        mapping = {
            CoordinationAttribute.COMMUNICATION_CLARITY: CoordinationInterventionType.IMPROVE_COMMUNICATION,
            CoordinationAttribute.TASK_COMPLETION_ACCURACY: CoordinationInterventionType.ENHANCE_TASK_CLARITY,
            CoordinationAttribute.RESOURCE_EFFICIENCY: CoordinationInterventionType.OPTIMIZE_RESOURCE_ALLOCATION,
        }
        return mapping.get(
            attribute, CoordinationInterventionType.STRENGTHEN_COORDINATION
        )

    def _get_degradation_intervention(
        self, attribute: CoordinationAttribute
    ) -> CoordinationInterventionType:
        mapping = {
            CoordinationAttribute.COMMUNICATION_CLARITY: CoordinationInterventionType.DEGRADE_COMMUNICATION,
            CoordinationAttribute.TASK_COMPLETION_ACCURACY: CoordinationInterventionType.OBSCURE_TASK_OBJECTIVES,
            CoordinationAttribute.RESOURCE_EFFICIENCY: CoordinationInterventionType.CONSTRAIN_RESOURCES,
        }
        return mapping.get(attribute, CoordinationInterventionType.DISRUPT_COORDINATION)

    def _get_spurious_intervention(
        self, attribute: SpuriousCoordinationAttribute
    ) -> CoordinationInterventionType:
        mapping = {
            SpuriousCoordinationAttribute.COMMUNICATION_STYLE: CoordinationInterventionType.CHANGE_COMMUNICATION_STYLE,
            SpuriousCoordinationAttribute.AGENT_PERSONALITY_TRAITS: CoordinationInterventionType.VARY_AGENT_PERSONALITIES,
            SpuriousCoordinationAttribute.RESPONSE_TIMING: CoordinationInterventionType.MODIFY_RESPONSE_TIMING,
        }
        return mapping.get(attribute, CoordinationInterventionType.ALTER_MESSAGE_FORMAT)

    async def _calculate_test_suite_metrics(
        self, test_suite: CounterfactualTestSuite
    ) -> None:
        """Calculate summary metrics for test suite"""

        if not test_suite.test_results:
            return

        # Count tests passed
        tests_passed = sum(
            1 for result in test_suite.test_results if result.expected_outcome_achieved
        )
        test_suite.tests_passed = tests_passed
        test_suite.total_tests_executed = len(test_suite.test_results)

        # Calculate causal sensitivity score
        causal_tests = [
            r
            for r in test_suite.test_results
            if r.counterfactual.test_type == CounterfactualTestType.CAUSAL_SENSITIVITY
        ]
        if causal_tests:
            causal_scores = [r.causal_attribution_score for r in causal_tests]
            test_suite.causal_sensitivity_score = sum(causal_scores) / len(
                causal_scores
            )

        # Calculate spurious invariance score
        spurious_tests = [
            r
            for r in test_suite.test_results
            if r.counterfactual.test_type == CounterfactualTestType.SPURIOUS_INVARIANCE
        ]
        if spurious_tests:
            spurious_scores = [r.spurious_resistance_score for r in spurious_tests]
            test_suite.spurious_invariance_score = sum(spurious_scores) / len(
                spurious_scores
            )

        # Calculate overall robustness
        test_suite.overall_robustness_score = (
            test_suite.causal_sensitivity_score * 0.6
            + test_suite.spurious_invariance_score * 0.4
        )

    async def _log_test_result(self, test_result: CounterfactualTestResult) -> None:
        """Log individual test result"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "counterfactual_coordination_test_result",
                "test_id": test_result.test_id,
                "test_type": test_result.counterfactual.test_type.value,
                "intervention_type": test_result.counterfactual.intervention_type.value,
                "target_attribute": test_result.counterfactual.target_attribute.value,
                "results": {
                    "original_quality": test_result.original_coordination_quality,
                    "modified_quality": test_result.modified_coordination_quality,
                    "quality_change": test_result.quality_change,
                    "expected_outcome_achieved": test_result.expected_outcome_achieved,
                    "causal_attribution_score": test_result.causal_attribution_score,
                    "spurious_resistance_score": test_result.spurious_resistance_score,
                },
                "constitutional_compliance": test_result.constitutional_compliance_maintained,
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "counterfactual_coordination_tester",
                "timestamp": test_result.timestamp.isoformat(),
                "test_outcome": (
                    "passed" if test_result.expected_outcome_achieved else "failed"
                ),
            },
            tags=[
                "coordination",
                "counterfactual",
                "testing",
                "carma",
                test_result.counterfactual.test_type.value,
            ],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    async def _log_test_suite_results(
        self, test_suite: CounterfactualTestSuite
    ) -> None:
        """Log test suite results"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "counterfactual_test_suite_results",
                "suite_id": test_suite.suite_id,
                "summary_metrics": {
                    "total_tests_executed": test_suite.total_tests_executed,
                    "tests_passed": test_suite.tests_passed,
                    "pass_rate": test_suite.tests_passed
                    / max(1, test_suite.total_tests_executed),
                    "causal_sensitivity_score": test_suite.causal_sensitivity_score,
                    "spurious_invariance_score": test_suite.spurious_invariance_score,
                    "overall_robustness_score": test_suite.overall_robustness_score,
                },
                "test_configuration": {
                    "test_types_enabled": [
                        t.value for t in test_suite.test_types_enabled
                    ],
                    "causal_attributes_tested": [
                        a.value for a in test_suite.causal_attributes_tested
                    ],
                    "spurious_attributes_tested": [
                        a.value for a in test_suite.spurious_attributes_tested
                    ],
                },
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "counterfactual_coordination_tester",
                "timestamp": (
                    test_suite.completion_timestamp or datetime.now(timezone.utc)
                ).isoformat(),
                "test_suite_quality": (
                    "high"
                    if test_suite.overall_robustness_score >= 0.8
                    else (
                        "medium"
                        if test_suite.overall_robustness_score >= 0.6
                        else "low"
                    )
                ),
            },
            tags=["coordination", "testing", "suite", "carma", "robustness"],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    def get_testing_statistics(self) -> Dict[str, Any]:
        """Get testing statistics"""

        stats = self.testing_stats.copy()
        stats.update(
            {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "tester_version": "1.0.0_carma_inspired",
                "causal_test_pass_rate": (
                    stats.get("causal_tests_passed", 0)
                    / max(1, stats.get("tests_executed", 1))
                ),
                "spurious_test_pass_rate": (
                    stats.get("spurious_tests_passed", 0)
                    / max(1, stats.get("tests_executed", 1))
                ),
            }
        )

        return stats
