"""
Bias Mitigation Engine

Advanced bias mitigation system that implements automated and semi-automated
bias correction strategies for ACGS constitutional AI systems. Provides
real-time bias correction, proactive bias prevention, and adaptive mitigation
strategies based on detected bias patterns.

Key Features:
- Multi-strategy bias mitigation (pre-processing, in-processing, post-processing)
- Adaptive mitigation based on bias type and severity
- Constitutional fairness-aware bias correction
- Real-time bias intervention and correction
- Mitigation effectiveness tracking and optimization
- Integration with bias drift monitoring systems
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import numpy as np

from services.shared.fairness.bias_drift_monitor import (
    BiasContext,
    BiasDriftMonitor,
    BiasSeverity,
    BiasType,
    ProtectedAttribute,
)
from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)


class MitigationStrategy(Enum):
    """Bias mitigation strategies"""

    PREPROCESSING_RESAMPLING = "preprocessing_resampling"
    PREPROCESSING_REWEIGHTING = "preprocessing_reweighting"
    PREPROCESSING_FEATURE_SELECTION = "preprocessing_feature_selection"
    INPROCESSING_FAIRNESS_CONSTRAINTS = "inprocessing_fairness_constraints"
    INPROCESSING_ADVERSARIAL_DEBIASING = "inprocessing_adversarial_debiasing"
    INPROCESSING_MULTI_OBJECTIVE = "inprocessing_multi_objective"
    POSTPROCESSING_THRESHOLD_OPTIMIZATION = "postprocessing_threshold_optimization"
    POSTPROCESSING_CALIBRATION = "postprocessing_calibration"
    POSTPROCESSING_OUTCOME_REDISTRIBUTION = "postprocessing_outcome_redistribution"
    CONSTITUTIONAL_PRINCIPLE_ALIGNMENT = "constitutional_principle_alignment"
    HUMAN_IN_THE_LOOP_CORRECTION = "human_in_the_loop_correction"
    ENSEMBLE_DEBIASING = "ensemble_debiasing"


class MitigationMode(Enum):
    """Mitigation execution modes"""

    AUTOMATIC = "automatic"
    SEMI_AUTOMATIC = "semi_automatic"
    MANUAL = "manual"
    EMERGENCY = "emergency"


class InterventionTrigger(Enum):
    """Triggers for bias intervention"""

    THRESHOLD_EXCEEDED = "threshold_exceeded"
    PATTERN_DETECTED = "pattern_detected"
    DRIFT_ALERT = "drift_alert"
    COMPLIANCE_VIOLATION = "compliance_violation"
    HUMAN_REQUEST = "human_request"
    SCHEDULED_REVIEW = "scheduled_review"
    EMERGENCY_OVERRIDE = "emergency_override"


@dataclass
class MitigationAction:
    """Individual bias mitigation action"""

    action_id: str
    strategy: MitigationStrategy
    target_bias_type: BiasType
    target_attribute: ProtectedAttribute
    target_context: BiasContext
    parameters: dict[str, Any]
    expected_improvement: float
    confidence: float
    computational_cost: float
    implementation_time_minutes: float
    side_effects: list[str]
    prerequisites: list[str]


@dataclass
class MitigationPlan:
    """Comprehensive bias mitigation plan"""

    plan_id: str
    target_metrics: list[str]
    mitigation_actions: list[MitigationAction]
    execution_order: list[str]  # Action IDs in execution order
    overall_expected_improvement: float
    total_computational_cost: float
    estimated_duration_minutes: float
    risk_assessment: dict[str, str]
    fallback_strategies: list[MitigationStrategy]
    success_criteria: dict[str, float]
    monitoring_requirements: list[str]
    created_at: datetime
    created_by: str


@dataclass
class MitigationResult:
    """Result of bias mitigation execution"""

    result_id: str
    plan_id: str
    action_id: str
    strategy_used: MitigationStrategy
    execution_status: str
    start_time: datetime
    end_time: datetime
    bias_reduction_achieved: float
    side_effects_observed: list[str]
    performance_impact: dict[str, float]
    effectiveness_score: float
    lessons_learned: list[str]
    recommendations: list[str]


@dataclass
class BiasCorrection:
    """Real-time bias correction record"""

    correction_id: str
    original_decision: dict[str, Any]
    corrected_decision: dict[str, Any]
    correction_method: str
    bias_detected: dict[str, float]
    correction_strength: float
    confidence_impact: float
    human_review_required: bool
    timestamp: datetime


class BiasMitigationEngine:
    """
    Advanced bias mitigation engine for constitutional AI systems
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Initialize bias drift monitor integration
        self.bias_monitor = None  # Will be set via set_bias_monitor()

        # Mitigation configuration
        self.mitigation_enabled = config.get("mitigation_enabled", True)
        self.automatic_mitigation = config.get("automatic_mitigation", True)
        self.emergency_mitigation = config.get("emergency_mitigation", True)
        self.real_time_correction = config.get("real_time_correction", True)

        # Mitigation thresholds
        self.intervention_thresholds = config.get(
            "intervention_thresholds",
            {
                BiasSeverity.MEDIUM: {"auto_trigger": True, "human_approval": False},
                BiasSeverity.HIGH: {"auto_trigger": True, "human_approval": True},
                BiasSeverity.CRITICAL: {
                    "auto_trigger": True,
                    "human_approval": False,
                    "emergency": True,
                },
            },
        )

        # Strategy effectiveness tracking
        self.strategy_effectiveness = defaultdict(
            lambda: {
                "success_rate": 0.5,
                "avg_improvement": 0.0,
                "computational_cost": 1.0,
                "side_effects_rate": 0.1,
                "usage_count": 0,
            }
        )

        # Data storage
        self.mitigation_plans = {}  # plan_id -> MitigationPlan
        self.mitigation_results = {}  # result_id -> MitigationResult
        self.correction_history = deque(maxlen=5000)
        self.active_mitigations = {}  # Currently running mitigations

        # State management
        self.running = False
        self.last_mitigation_check = datetime.utcnow()

        # Constitutional principles for bias mitigation
        self.constitutional_mitigation_principles = {
            "proportionality": (
                "Mitigation strength should be proportional to bias severity"
            ),
            "transparency": "All mitigation actions must be transparent and auditable",
            "accountability": "Clear responsibility for mitigation decisions",
            "effectiveness": "Mitigation must demonstrably reduce bias",
            "minimal_harm": "Mitigation should minimize negative side effects",
        }

        # Strategy compatibility matrix
        self.strategy_compatibility = self._initialize_strategy_compatibility()

        # Real-time correction models
        self.correction_models = self._initialize_correction_models()

    def _initialize_strategy_compatibility(
        self,
    ) -> dict[tuple[MitigationStrategy, MitigationStrategy], float]:
        """Initialize strategy compatibility matrix"""
        compatibility = {}

        strategies = list(MitigationStrategy)

        # Define compatibility scores between strategies
        for i, strategy1 in enumerate(strategies):
            for j, strategy2 in enumerate(strategies):
                if i == j:
                    compatibility[(strategy1, strategy2)] = (
                        1.0  # Perfect self-compatibility
                    )
                elif (
                    "preprocessing" in strategy1.value
                    and "preprocessing" in strategy2.value
                ):
                    compatibility[(strategy1, strategy2)] = (
                        0.3  # Low compatibility between preprocessing methods
                    )
                elif (
                    "inprocessing" in strategy1.value
                    and "inprocessing" in strategy2.value
                ):
                    compatibility[(strategy1, strategy2)] = (
                        0.2  # Very low compatibility
                    )
                elif (
                    "postprocessing" in strategy1.value
                    and "postprocessing" in strategy2.value
                ):
                    compatibility[(strategy1, strategy2)] = (
                        0.4  # Moderate compatibility
                    )
                elif (
                    "preprocessing" in strategy1.value
                    and "postprocessing" in strategy2.value
                ) or (
                    "postprocessing" in strategy1.value
                    and "preprocessing" in strategy2.value
                ):
                    compatibility[(strategy1, strategy2)] = 0.8  # High compatibility
                elif (
                    "inprocessing" in strategy1.value
                    and "postprocessing" in strategy2.value
                ) or (
                    "postprocessing" in strategy1.value
                    and "inprocessing" in strategy2.value
                ):
                    compatibility[(strategy1, strategy2)] = 0.6  # Good compatibility
                else:
                    compatibility[(strategy1, strategy2)] = (
                        0.5  # Default moderate compatibility
                    )

        return compatibility

    def _initialize_correction_models(self) -> dict[str, dict[str, Any]]:
        """Initialize real-time correction models"""
        return {
            "threshold_adjustment": {
                "description": (
                    "Adjust decision thresholds based on protected attributes"
                ),
                "parameters": {"sensitivity": 0.1, "max_adjustment": 0.2},
                "effectiveness": 0.7,
                "computational_cost": 0.1,
            },
            "score_calibration": {
                "description": "Calibrate prediction scores for fairness across groups",
                "parameters": {
                    "calibration_method": "platt_scaling",
                    "group_specific": True,
                },
                "effectiveness": 0.8,
                "computational_cost": 0.3,
            },
            "outcome_redistribution": {
                "description": "Redistribute positive outcomes to ensure fairness",
                "parameters": {
                    "redistribution_rate": 0.05,
                    "fairness_constraint": "demographic_parity",
                },
                "effectiveness": 0.9,
                "computational_cost": 0.2,
            },
            "constitutional_override": {
                "description": (
                    "Apply constitutional principles to override biased decisions"
                ),
                "parameters": {
                    "principle_weights": {
                        "equal_protection": 0.4,
                        "due_process": 0.3,
                        "fairness": 0.3,
                    }
                },
                "effectiveness": 0.95,
                "computational_cost": 0.5,
            },
        }

    def set_bias_monitor(self, bias_monitor: BiasDriftMonitor):
        """Set bias drift monitor for integration"""
        self.bias_monitor = bias_monitor

    async def start_mitigation_engine(self):
        """Start bias mitigation engine"""
        if self.running:
            logger.warning("Bias mitigation engine is already running")
            return

        self.running = True
        logger.info("Starting bias mitigation engine")

        try:
            # Start mitigation tasks
            mitigation_tasks = [
                self._run_mitigation_monitoring(),
                self._run_automatic_mitigation(),
                self._run_real_time_correction(),
                self._run_effectiveness_analysis(),
                self._run_strategy_optimization(),
            ]

            await asyncio.gather(*mitigation_tasks)

        except Exception as e:
            logger.error(f"Bias mitigation engine failed: {e}")
            self.running = False
            raise
        finally:
            logger.info("Bias mitigation engine stopped")

    async def stop_mitigation_engine(self):
        """Stop bias mitigation engine"""
        self.running = False
        logger.info("Stopping bias mitigation engine")

    async def _run_mitigation_monitoring(self):
        """Monitor for bias mitigation triggers"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute

                if not self.running:
                    break

                # Check for mitigation triggers
                await self._check_mitigation_triggers()

                self.last_mitigation_check = datetime.utcnow()

            except Exception as e:
                logger.error(f"Mitigation monitoring error: {e}")
                await asyncio.sleep(60)

    async def _check_mitigation_triggers(self):
        """Check for conditions that trigger bias mitigation"""
        try:
            if not self.bias_monitor:
                return

            # Get recent bias metrics from monitor
            current_time = datetime.utcnow()
            recent_cutoff = current_time - timedelta(minutes=30)

            # Check bias monitor for recent high-severity metrics
            recent_metrics = [
                metric
                for metric in self.bias_monitor.metric_history
                if metric.timestamp >= recent_cutoff
                and metric.severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]
            ]

            # Group metrics by context and attribute for targeted mitigation
            grouped_metrics = defaultdict(list)
            for metric in recent_metrics:
                key = (metric.context, metric.bias_type, metric.protected_attribute)
                grouped_metrics[key].append(metric)

            # Create mitigation plans for each group
            for (
                context,
                bias_type,
                protected_attr,
            ), metrics in grouped_metrics.items():
                if len(metrics) >= 2:  # Multiple recent violations
                    await self._trigger_mitigation(
                        context,
                        bias_type,
                        protected_attr,
                        metrics,
                        InterventionTrigger.THRESHOLD_EXCEEDED,
                    )

        except Exception as e:
            logger.error(f"Mitigation trigger check failed: {e}")

    async def _trigger_mitigation(
        self,
        context: BiasContext,
        bias_type: BiasType,
        protected_attr: ProtectedAttribute,
        metrics: list[Any],
        trigger: InterventionTrigger,
    ):
        """Trigger bias mitigation for specific conditions"""
        try:
            # Determine severity level
            max_severity = max(metric.severity for metric in metrics)

            # Check if automatic mitigation is allowed
            threshold_config = self.intervention_thresholds.get(max_severity, {})
            auto_trigger = threshold_config.get("auto_trigger", False)
            human_approval = threshold_config.get("human_approval", True)
            emergency = threshold_config.get("emergency", False)

            if not auto_trigger and not emergency:
                logger.info(
                    "Mitigation trigger ignored - auto trigger disabled for"
                    f" {max_severity.value}"
                )
                return

            # Create mitigation plan
            mitigation_plan = await self._create_mitigation_plan(
                context, bias_type, protected_attr, max_severity, metrics
            )

            if not mitigation_plan:
                logger.warning("Failed to create mitigation plan")
                return

            # Execute mitigation based on mode
            if emergency:
                await self._execute_emergency_mitigation(mitigation_plan)
            elif auto_trigger and not human_approval:
                await self._execute_automatic_mitigation(mitigation_plan)
            elif auto_trigger and human_approval:
                await self._request_human_approval_for_mitigation(mitigation_plan)

        except Exception as e:
            logger.error(f"Mitigation trigger failed: {e}")

    async def _create_mitigation_plan(
        self,
        context: BiasContext,
        bias_type: BiasType,
        protected_attr: ProtectedAttribute,
        severity: BiasSeverity,
        metrics: list[Any],
    ) -> Optional[MitigationPlan]:
        """Create bias mitigation plan"""
        try:
            plan_id = str(uuid.uuid4())

            # Select appropriate mitigation strategies
            candidate_strategies = await self._select_mitigation_strategies(
                context, bias_type, protected_attr, severity
            )

            if not candidate_strategies:
                return None

            # Create mitigation actions
            mitigation_actions = []
            execution_order = []

            for strategy in candidate_strategies:
                action = await self._create_mitigation_action(
                    strategy, bias_type, protected_attr, context, severity, metrics
                )
                if action:
                    mitigation_actions.append(action)
                    execution_order.append(action.action_id)

            if not mitigation_actions:
                return None

            # Calculate plan metrics
            overall_improvement = sum(
                action.expected_improvement for action in mitigation_actions
            )
            total_cost = sum(action.computational_cost for action in mitigation_actions)
            estimated_duration = sum(
                action.implementation_time_minutes for action in mitigation_actions
            )

            # Risk assessment
            risk_assessment = await self._assess_mitigation_risks(mitigation_actions)

            # Success criteria
            success_criteria = {
                "bias_reduction_target": 0.5,  # 50% reduction
                "max_performance_degradation": 0.05,  # 5% max performance loss
                "min_fairness_improvement": 0.3,  # 30% fairness improvement
            }

            # Monitoring requirements
            monitoring_requirements = [
                "Real-time bias metric tracking",
                "Performance impact monitoring",
                "Fairness metric validation",
                "Side effect detection",
            ]

            plan = MitigationPlan(
                plan_id=plan_id,
                target_metrics=[f"{bias_type.value}_{protected_attr.value}"],
                mitigation_actions=mitigation_actions,
                execution_order=execution_order,
                overall_expected_improvement=overall_improvement,
                total_computational_cost=total_cost,
                estimated_duration_minutes=estimated_duration,
                risk_assessment=risk_assessment,
                fallback_strategies=await self._identify_fallback_strategies(
                    candidate_strategies
                ),
                success_criteria=success_criteria,
                monitoring_requirements=monitoring_requirements,
                created_at=datetime.utcnow(),
                created_by="bias_mitigation_engine",
            )

            # Store plan
            self.mitigation_plans[plan_id] = plan

            # Log plan creation
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "mitigation_plan_created",
                    "plan_id": plan_id,
                    "target_context": context.value,
                    "target_bias_type": bias_type.value,
                    "target_attribute": protected_attr.value,
                    "severity": severity.value,
                    "strategies_count": len(mitigation_actions),
                    "expected_improvement": overall_improvement,
                    "estimated_duration": estimated_duration,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            return plan

        except Exception as e:
            logger.error(f"Mitigation plan creation failed: {e}")
            return None

    async def _select_mitigation_strategies(
        self,
        context: BiasContext,
        bias_type: BiasType,
        protected_attr: ProtectedAttribute,
        severity: BiasSeverity,
    ) -> list[MitigationStrategy]:
        """Select appropriate mitigation strategies"""
        try:
            strategies = []

            # Strategy selection based on bias type
            if bias_type == BiasType.DEMOGRAPHIC_PARITY:
                strategies.extend(
                    [
                        MitigationStrategy.PREPROCESSING_RESAMPLING,
                        MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION,
                        MitigationStrategy.POSTPROCESSING_OUTCOME_REDISTRIBUTION,
                    ]
                )

            elif bias_type == BiasType.EQUALIZED_ODDS:
                strategies.extend(
                    [
                        MitigationStrategy.INPROCESSING_FAIRNESS_CONSTRAINTS,
                        MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION,
                        MitigationStrategy.POSTPROCESSING_CALIBRATION,
                    ]
                )

            elif bias_type == BiasType.CALIBRATION:
                strategies.extend(
                    [
                        MitigationStrategy.POSTPROCESSING_CALIBRATION,
                        MitigationStrategy.INPROCESSING_MULTI_OBJECTIVE,
                    ]
                )

            # Add constitutional strategies for constitutional contexts
            if context in [
                BiasContext.CONSTITUTIONAL_ANALYSIS,
                BiasContext.LEGAL_INTERPRETATION,
            ]:
                strategies.append(MitigationStrategy.CONSTITUTIONAL_PRINCIPLE_ALIGNMENT)

            # Add human-in-the-loop for high severity
            if severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]:
                strategies.append(MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION)

            # Add ensemble methods for complex cases
            if len(strategies) > 2:
                strategies.append(MitigationStrategy.ENSEMBLE_DEBIASING)

            # Filter strategies based on effectiveness and context
            filtered_strategies = []
            for strategy in strategies:
                effectiveness = self.strategy_effectiveness[strategy]["success_rate"]
                if (
                    effectiveness > 0.3
                ):  # Only include strategies with >30% success rate
                    filtered_strategies.append(strategy)

            # Sort by effectiveness
            filtered_strategies.sort(
                key=lambda s: self.strategy_effectiveness[s]["success_rate"],
                reverse=True,
            )

            # Return top strategies (limit to prevent over-complexity)
            return filtered_strategies[:5]

        except Exception as e:
            logger.error(f"Strategy selection failed: {e}")
            return []

    async def _create_mitigation_action(
        self,
        strategy: MitigationStrategy,
        bias_type: BiasType,
        protected_attr: ProtectedAttribute,
        context: BiasContext,
        severity: BiasSeverity,
        metrics: list[Any],
    ) -> Optional[MitigationAction]:
        """Create individual mitigation action"""
        try:
            action_id = str(uuid.uuid4())

            # Get strategy-specific parameters
            parameters = await self._get_strategy_parameters(
                strategy, bias_type, protected_attr, context
            )

            # Estimate expected improvement
            baseline_bias = statistics.mean([m.metric_value for m in metrics])
            expected_improvement = await self._estimate_improvement(
                strategy, baseline_bias, parameters
            )

            # Get strategy effectiveness data
            strategy_data = self.strategy_effectiveness[strategy]
            confidence = strategy_data["success_rate"]
            computational_cost = strategy_data["computational_cost"]

            # Estimate implementation time
            implementation_time = await self._estimate_implementation_time(
                strategy, parameters
            )

            # Identify potential side effects
            side_effects = await self._identify_side_effects(strategy, context)

            # Identify prerequisites
            prerequisites = await self._identify_prerequisites(strategy, context)

            action = MitigationAction(
                action_id=action_id,
                strategy=strategy,
                target_bias_type=bias_type,
                target_attribute=protected_attr,
                target_context=context,
                parameters=parameters,
                expected_improvement=expected_improvement,
                confidence=confidence,
                computational_cost=computational_cost,
                implementation_time_minutes=implementation_time,
                side_effects=side_effects,
                prerequisites=prerequisites,
            )

            return action

        except Exception as e:
            logger.error(f"Mitigation action creation failed: {e}")
            return None

    async def _get_strategy_parameters(
        self,
        strategy: MitigationStrategy,
        bias_type: BiasType,
        protected_attr: ProtectedAttribute,
        context: BiasContext,
    ) -> dict[str, Any]:
        """Get strategy-specific parameters"""
        try:
            if strategy == MitigationStrategy.PREPROCESSING_RESAMPLING:
                return {
                    "resampling_method": "smote",
                    "target_ratio": 1.0,
                    "random_state": 42,
                }

            elif strategy == MitigationStrategy.PREPROCESSING_REWEIGHTING:
                return {
                    "reweighting_method": "inverse_propensity",
                    "smoothing_factor": 0.1,
                }

            elif strategy == MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION:
                return {
                    "optimization_metric": bias_type.value,
                    "constraint_type": "equality",
                    "tolerance": 0.05,
                }

            elif strategy == MitigationStrategy.POSTPROCESSING_CALIBRATION:
                return {
                    "calibration_method": "platt_scaling",
                    "group_specific": True,
                    "cross_validation_folds": 5,
                }

            elif strategy == MitigationStrategy.CONSTITUTIONAL_PRINCIPLE_ALIGNMENT:
                return {
                    "primary_principle": "equal_protection",
                    "alignment_strength": 0.8,
                    "context_weight": (
                        1.0 if context == BiasContext.CONSTITUTIONAL_ANALYSIS else 0.5
                    ),
                }

            elif strategy == MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION:
                return {
                    "review_threshold": 0.7,
                    "escalation_criteria": ["high_bias", "constitutional_conflict"],
                    "reviewer_expertise": (
                        "constitutional_law"
                        if context == BiasContext.CONSTITUTIONAL_ANALYSIS
                        else "fairness"
                    ),
                }

            else:
                # Default parameters
                return {"method": "default", "strength": 0.5, "iterations": 10}

        except Exception as e:
            logger.error(f"Parameter generation failed for {strategy.value}: {e}")
            return {}

    async def _estimate_improvement(
        self,
        strategy: MitigationStrategy,
        baseline_bias: float,
        parameters: dict[str, Any],
    ) -> float:
        """Estimate expected bias improvement from strategy"""
        try:
            # Base improvement rates by strategy type
            base_improvements = {
                MitigationStrategy.PREPROCESSING_RESAMPLING: 0.3,
                MitigationStrategy.PREPROCESSING_REWEIGHTING: 0.25,
                MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION: 0.4,
                MitigationStrategy.POSTPROCESSING_CALIBRATION: 0.35,
                MitigationStrategy.CONSTITUTIONAL_PRINCIPLE_ALIGNMENT: 0.5,
                MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION: 0.6,
                MitigationStrategy.ENSEMBLE_DEBIASING: 0.45,
            }

            base_improvement = base_improvements.get(strategy, 0.2)

            # Adjust based on baseline bias level
            if baseline_bias > 0.5:
                # High bias - easier to improve
                improvement_factor = 1.2
            elif baseline_bias > 0.2:
                # Medium bias - normal improvement
                improvement_factor = 1.0
            else:
                # Low bias - harder to improve further
                improvement_factor = 0.7

            # Adjust based on strategy parameters
            parameter_adjustment = 1.0
            if "strength" in parameters:
                parameter_adjustment = 0.8 + 0.4 * parameters["strength"]

            expected_improvement = (
                base_improvement * improvement_factor * parameter_adjustment
            )

            # Cap improvement (can't eliminate all bias)
            max_improvement = min(0.8, baseline_bias * 0.9)

            return min(expected_improvement, max_improvement)

        except Exception as e:
            logger.error(f"Improvement estimation failed: {e}")
            return 0.1

    async def _estimate_implementation_time(
        self, strategy: MitigationStrategy, parameters: dict[str, Any]
    ) -> float:
        """Estimate implementation time in minutes"""
        try:
            # Base implementation times by strategy
            base_times = {
                MitigationStrategy.PREPROCESSING_RESAMPLING: 15,
                MitigationStrategy.PREPROCESSING_REWEIGHTING: 10,
                MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION: 20,
                MitigationStrategy.POSTPROCESSING_CALIBRATION: 25,
                MitigationStrategy.CONSTITUTIONAL_PRINCIPLE_ALIGNMENT: 30,
                MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION: 60,
                MitigationStrategy.ENSEMBLE_DEBIASING: 45,
            }

            base_time = base_times.get(strategy, 20)

            # Adjust based on parameters
            if "iterations" in parameters:
                base_time *= 1 + parameters["iterations"] / 100

            if "cross_validation_folds" in parameters:
                base_time *= parameters["cross_validation_folds"] / 5

            return base_time

        except Exception:
            return 20.0

    async def _identify_side_effects(
        self, strategy: MitigationStrategy, context: BiasContext
    ) -> list[str]:
        """Identify potential side effects of mitigation strategy"""
        side_effects_map = {
            MitigationStrategy.PREPROCESSING_RESAMPLING: [
                "Potential overfitting to synthetic data",
                "Reduced model generalization",
                "Increased training time",
            ],
            MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION: [
                "Potential accuracy reduction",
                "Threshold instability",
                "Group-specific performance variance",
            ],
            MitigationStrategy.POSTPROCESSING_CALIBRATION: [
                "Calibration overfitting",
                "Reduced discrimination ability",
                "Group-specific calibration errors",
            ],
            MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION: [
                "Increased decision latency",
                "Human reviewer bias introduction",
                "Scalability limitations",
            ],
            MitigationStrategy.CONSTITUTIONAL_PRINCIPLE_ALIGNMENT: [
                "Potential principle conflicts",
                "Reduced computational efficiency",
                "Complex interpretability",
            ],
        }

        return side_effects_map.get(strategy, ["Unknown side effects"])

    async def _identify_prerequisites(
        self, strategy: MitigationStrategy, context: BiasContext
    ) -> list[str]:
        """Identify prerequisites for mitigation strategy"""
        prerequisites_map = {
            MitigationStrategy.PREPROCESSING_RESAMPLING: [
                "Access to training data",
                "Sufficient computational resources",
                "Model retraining capability",
            ],
            MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION: [
                "Validation dataset availability",
                "Group membership information",
                "Threshold adjustment capability",
            ],
            MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION: [
                "Qualified human reviewers available",
                "Review process infrastructure",
                "Escalation procedures in place",
            ],
            MitigationStrategy.CONSTITUTIONAL_PRINCIPLE_ALIGNMENT: [
                "Constitutional principle definitions",
                "Principle weighting framework",
                "Legal expertise available",
            ],
        }

        return prerequisites_map.get(strategy, ["Standard prerequisites"])

    async def _assess_mitigation_risks(
        self, actions: list[MitigationAction]
    ) -> dict[str, str]:
        """Assess risks of mitigation plan"""
        try:
            risks = {}

            # Performance risk
            total_cost = sum(action.computational_cost for action in actions)
            if total_cost > 2.0:
                risks["performance"] = "high"
            elif total_cost > 1.0:
                risks["performance"] = "medium"
            else:
                risks["performance"] = "low"

            # Side effects risk
            all_side_effects = [
                effect for action in actions for effect in action.side_effects
            ]
            if len(all_side_effects) > 10:
                risks["side_effects"] = "high"
            elif len(all_side_effects) > 5:
                risks["side_effects"] = "medium"
            else:
                risks["side_effects"] = "low"

            # Implementation risk
            total_time = sum(action.implementation_time_minutes for action in actions)
            if total_time > 180:  # More than 3 hours
                risks["implementation"] = "high"
            elif total_time > 60:  # More than 1 hour
                risks["implementation"] = "medium"
            else:
                risks["implementation"] = "low"

            # Effectiveness risk
            avg_confidence = statistics.mean([action.confidence for action in actions])
            if avg_confidence < 0.5:
                risks["effectiveness"] = "high"
            elif avg_confidence < 0.7:
                risks["effectiveness"] = "medium"
            else:
                risks["effectiveness"] = "low"

            return risks

        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {"overall": "unknown"}

    async def _identify_fallback_strategies(
        self, primary_strategies: list[MitigationStrategy]
    ) -> list[MitigationStrategy]:
        """Identify fallback strategies if primary strategies fail"""
        fallback_map = {
            MitigationStrategy.PREPROCESSING_RESAMPLING: [
                MitigationStrategy.PREPROCESSING_REWEIGHTING,
                MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION,
            ],
            MitigationStrategy.INPROCESSING_FAIRNESS_CONSTRAINTS: [
                MitigationStrategy.POSTPROCESSING_CALIBRATION,
                MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION,
            ],
            MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION: [
                MitigationStrategy.POSTPROCESSING_CALIBRATION,
                MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION,
            ],
        }

        fallbacks = []
        for strategy in primary_strategies:
            strategy_fallbacks = fallback_map.get(strategy, [])
            fallbacks.extend(
                [f for f in strategy_fallbacks if f not in primary_strategies]
            )

        # Always include human intervention as ultimate fallback
        if MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION not in fallbacks:
            fallbacks.append(MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION)

        return fallbacks[:3]  # Limit to 3 fallback strategies

    async def _execute_automatic_mitigation(self, plan: MitigationPlan):
        """Execute automatic bias mitigation"""
        try:
            logger.info(
                f"Starting automatic mitigation execution for plan {plan.plan_id}"
            )

            # Mark plan as active
            self.active_mitigations[plan.plan_id] = {
                "plan": plan,
                "start_time": datetime.utcnow(),
                "status": "executing",
                "current_action": None,
            }

            # Execute actions in order
            overall_success = True
            results = []

            for action_id in plan.execution_order:
                action = next(
                    (a for a in plan.mitigation_actions if a.action_id == action_id),
                    None,
                )
                if not action:
                    continue

                # Update status
                self.active_mitigations[plan.plan_id]["current_action"] = action_id

                # Execute action
                result = await self._execute_mitigation_action(action)
                results.append(result)

                # Check if action was successful
                if result.execution_status != "success":
                    overall_success = False
                    logger.warning(
                        f"Mitigation action {action_id} failed:"
                        f" {result.execution_status}"
                    )

                    # Consider fallback strategies
                    if result.effectiveness_score < 0.3:
                        logger.info(
                            "Considering fallback strategies due to poor effectiveness"
                        )
                        # Could implement fallback logic here

                # Log action result
                await self.audit_logger.log_compliance_event(
                    {
                        "event_type": "mitigation_action_executed",
                        "plan_id": plan.plan_id,
                        "action_id": action_id,
                        "strategy": action.strategy.value,
                        "execution_status": result.execution_status,
                        "effectiveness_score": result.effectiveness_score,
                        "bias_reduction": result.bias_reduction_achieved,
                        "timestamp": result.end_time.isoformat(),
                    }
                )

            # Complete mitigation
            self.active_mitigations[plan.plan_id]["status"] = (
                "completed" if overall_success else "partial_failure"
            )
            self.active_mitigations[plan.plan_id]["end_time"] = datetime.utcnow()

            # Calculate overall results
            overall_bias_reduction = sum(r.bias_reduction_achieved for r in results)
            overall_effectiveness = statistics.mean(
                [r.effectiveness_score for r in results]
            )

            # Log plan completion
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "automatic_mitigation_completed",
                    "plan_id": plan.plan_id,
                    "overall_success": overall_success,
                    "actions_executed": len(results),
                    "overall_bias_reduction": overall_bias_reduction,
                    "overall_effectiveness": overall_effectiveness,
                    "execution_time_minutes": (
                        datetime.utcnow()
                        - self.active_mitigations[plan.plan_id]["start_time"]
                    ).total_seconds()
                    / 60,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Send completion alert
            await self.alerting.send_alert(
                f"mitigation_completed_{plan.plan_id}",
                "Automatic bias mitigation completed:"
                f" {overall_bias_reduction:.2%} bias reduction achieved",
                severity="medium",
            )

        except Exception as e:
            logger.error(f"Automatic mitigation execution failed: {e}")
            if plan.plan_id in self.active_mitigations:
                self.active_mitigations[plan.plan_id]["status"] = "error"
                self.active_mitigations[plan.plan_id]["error"] = str(e)

    async def _execute_mitigation_action(
        self, action: MitigationAction
    ) -> MitigationResult:
        """Execute individual mitigation action"""
        try:
            start_time = datetime.utcnow()
            result_id = str(uuid.uuid4())

            # Simulate action execution (in practice, this would call actual mitigation algorithms)
            execution_status = "success"
            bias_reduction = 0.0
            effectiveness_score = 0.0
            side_effects_observed = []
            performance_impact = {}

            if action.strategy == MitigationStrategy.PREPROCESSING_RESAMPLING:
                # Simulate resampling execution
                bias_reduction = min(
                    action.expected_improvement, np.random.normal(0.3, 0.1)
                )
                effectiveness_score = 0.7 + np.random.normal(0, 0.1)
                performance_impact = {"accuracy": -0.02, "training_time": 1.3}

            elif (
                action.strategy
                == MitigationStrategy.POSTPROCESSING_THRESHOLD_OPTIMIZATION
            ):
                # Simulate threshold optimization
                bias_reduction = min(
                    action.expected_improvement, np.random.normal(0.4, 0.15)
                )
                effectiveness_score = 0.8 + np.random.normal(0, 0.1)
                performance_impact = {"accuracy": -0.01, "latency": 1.1}

            elif (
                action.strategy == MitigationStrategy.CONSTITUTIONAL_PRINCIPLE_ALIGNMENT
            ):
                # Simulate constitutional alignment
                bias_reduction = min(
                    action.expected_improvement, np.random.normal(0.5, 0.1)
                )
                effectiveness_score = 0.9 + np.random.normal(0, 0.05)
                performance_impact = {
                    "computational_cost": 1.4,
                    "interpretability": 1.2,
                }

            elif action.strategy == MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION:
                # Simulate human review process
                bias_reduction = min(
                    action.expected_improvement, np.random.normal(0.6, 0.2)
                )
                effectiveness_score = 0.85 + np.random.normal(0, 0.1)
                performance_impact = {"latency": 10.0, "cost": 5.0}
                side_effects_observed = [
                    "Increased decision time",
                    "Human reviewer workload",
                ]

            else:
                # Default simulation
                bias_reduction = min(
                    action.expected_improvement, np.random.normal(0.2, 0.1)
                )
                effectiveness_score = 0.6 + np.random.normal(0, 0.2)

            # Ensure realistic bounds
            bias_reduction = max(0, min(1, bias_reduction))
            effectiveness_score = max(0, min(1, effectiveness_score))

            # Determine if execution was successful
            if effectiveness_score < 0.3:
                execution_status = "poor_effectiveness"
            elif bias_reduction < 0.1:
                execution_status = "insufficient_improvement"

            end_time = datetime.utcnow()

            # Create result
            result = MitigationResult(
                result_id=result_id,
                plan_id="",  # Will be set by caller
                action_id=action.action_id,
                strategy_used=action.strategy,
                execution_status=execution_status,
                start_time=start_time,
                end_time=end_time,
                bias_reduction_achieved=bias_reduction,
                side_effects_observed=side_effects_observed,
                performance_impact=performance_impact,
                effectiveness_score=effectiveness_score,
                lessons_learned=await self._extract_lessons_learned(
                    action, effectiveness_score, bias_reduction
                ),
                recommendations=await self._generate_action_recommendations(
                    action, effectiveness_score
                ),
            )

            # Store result
            self.mitigation_results[result_id] = result

            # Update strategy effectiveness
            await self._update_strategy_effectiveness(
                action.strategy, effectiveness_score, bias_reduction
            )

            return result

        except Exception as e:
            logger.error(f"Mitigation action execution failed: {e}")
            return MitigationResult(
                result_id=str(uuid.uuid4()),
                plan_id="",
                action_id=action.action_id,
                strategy_used=action.strategy,
                execution_status="error",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                bias_reduction_achieved=0.0,
                side_effects_observed=[f"Execution error: {e!s}"],
                performance_impact={},
                effectiveness_score=0.0,
                lessons_learned=["Action execution failed"],
                recommendations=["Review action implementation"],
            )

    async def _extract_lessons_learned(
        self, action: MitigationAction, effectiveness: float, bias_reduction: float
    ) -> list[str]:
        """Extract lessons learned from mitigation action"""
        lessons = []

        if effectiveness > 0.8:
            lessons.append(
                f"{action.strategy.value} was highly effective for this bias type"
            )
        elif effectiveness < 0.4:
            lessons.append(
                f"{action.strategy.value} showed poor effectiveness, consider"
                " alternatives"
            )

        if bias_reduction > action.expected_improvement:
            lessons.append("Bias reduction exceeded expectations")
        elif bias_reduction < action.expected_improvement * 0.5:
            lessons.append("Bias reduction significantly below expectations")

        if action.computational_cost > 1.5:
            lessons.append("High computational cost may limit scalability")

        return lessons

    async def _generate_action_recommendations(
        self, action: MitigationAction, effectiveness: float
    ) -> list[str]:
        """Generate recommendations based on action performance"""
        recommendations = []

        if effectiveness < 0.5:
            recommendations.extend(
                [
                    f"Consider alternative strategies to {action.strategy.value}",
                    "Investigate root causes of poor effectiveness",
                    "Review action parameters for optimization",
                ]
            )

        if effectiveness > 0.8:
            recommendations.extend(
                [
                    f"Document successful parameters for {action.strategy.value}",
                    "Consider this strategy for similar future cases",
                    "Share lessons learned with team",
                ]
            )

        # Strategy-specific recommendations
        if action.strategy == MitigationStrategy.HUMAN_IN_THE_LOOP_CORRECTION:
            recommendations.append("Monitor human reviewer workload and performance")

        if action.strategy == MitigationStrategy.CONSTITUTIONAL_PRINCIPLE_ALIGNMENT:
            recommendations.append("Validate constitutional principle applications")

        return recommendations

    async def _update_strategy_effectiveness(
        self, strategy: MitigationStrategy, effectiveness: float, bias_reduction: float
    ):
        """Update strategy effectiveness tracking"""
        try:
            strategy_data = self.strategy_effectiveness[strategy]

            # Update usage count
            strategy_data["usage_count"] += 1

            # Update success rate (moving average)
            alpha = 0.1  # Learning rate
            strategy_data["success_rate"] = (1 - alpha) * strategy_data[
                "success_rate"
            ] + alpha * effectiveness

            # Update average improvement
            strategy_data["avg_improvement"] = (1 - alpha) * strategy_data[
                "avg_improvement"
            ] + alpha * bias_reduction

            # Log effectiveness update
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "strategy_effectiveness_updated",
                    "strategy": strategy.value,
                    "new_success_rate": strategy_data["success_rate"],
                    "new_avg_improvement": strategy_data["avg_improvement"],
                    "usage_count": strategy_data["usage_count"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Strategy effectiveness update failed: {e}")

    async def _execute_emergency_mitigation(self, plan: MitigationPlan):
        """Execute emergency bias mitigation"""
        try:
            logger.critical(
                "EMERGENCY: Executing emergency bias mitigation for plan"
                f" {plan.plan_id}"
            )

            # Emergency mitigation prioritizes speed over optimization
            # Execute highest-impact actions first
            high_impact_actions = sorted(
                plan.mitigation_actions,
                key=lambda a: a.expected_improvement,
                reverse=True,
            )

            # Execute top 2 actions immediately
            emergency_actions = high_impact_actions[:2]

            for action in emergency_actions:
                result = await self._execute_mitigation_action(action)

                # Log emergency action
                await self.audit_logger.log_compliance_event(
                    {
                        "event_type": "emergency_mitigation_action",
                        "plan_id": plan.plan_id,
                        "action_id": action.action_id,
                        "strategy": action.strategy.value,
                        "bias_reduction": result.bias_reduction_achieved,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Send emergency alert
            await self.alerting.send_alert(
                f"emergency_mitigation_{plan.plan_id}",
                "EMERGENCY: Bias mitigation executed for critical bias violation",
                severity="critical",
            )

        except Exception as e:
            logger.error(f"Emergency mitigation failed: {e}")

    async def _request_human_approval_for_mitigation(self, plan: MitigationPlan):
        """Request human approval for mitigation plan"""
        try:
            # Create approval request
            approval_request = {
                "request_id": str(uuid.uuid4()),
                "plan_id": plan.plan_id,
                "request_type": "mitigation_approval",
                "urgency": "high",
                "plan_summary": {
                    "strategies_count": len(plan.mitigation_actions),
                    "expected_improvement": plan.overall_expected_improvement,
                    "estimated_duration": plan.estimated_duration_minutes,
                    "risk_level": max(plan.risk_assessment.values()),
                },
                "requested_at": datetime.utcnow(),
                "timeout_minutes": 60,  # 1 hour timeout
            }

            # Log approval request
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "mitigation_approval_requested",
                    "request_id": approval_request["request_id"],
                    "plan_id": plan.plan_id,
                    "urgency": approval_request["urgency"],
                    "timeout_minutes": approval_request["timeout_minutes"],
                    "timestamp": approval_request["requested_at"].isoformat(),
                }
            )

            # Send alert to request approval
            await self.alerting.send_alert(
                f"mitigation_approval_needed_{plan.plan_id}",
                "Human approval required for bias mitigation plan (estimated"
                f" {plan.estimated_duration_minutes:.0f} minutes)",
                severity="high",
            )

            # In a real implementation, this would integrate with a human approval workflow
            logger.info(f"Human approval requested for mitigation plan {plan.plan_id}")

        except Exception as e:
            logger.error(f"Human approval request failed: {e}")

    async def _run_automatic_mitigation(self):
        """Run automatic mitigation engine"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                if not self.running:
                    break

                if not self.automatic_mitigation:
                    continue

                # Check for pending mitigation plans that can be auto-executed
                # This would typically be triggered by the monitoring system

            except Exception as e:
                logger.error(f"Automatic mitigation error: {e}")
                await asyncio.sleep(300)

    async def _run_real_time_correction(self):
        """Run real-time bias correction"""
        while self.running:
            try:
                await asyncio.sleep(
                    10
                )  # Check every 10 seconds for real-time corrections

                if not self.running:
                    break

                if not self.real_time_correction:
                    continue

                # This would integrate with the decision pipeline for real-time corrections
                # For now, we'll simulate periodic corrections

            except Exception as e:
                logger.error(f"Real-time correction error: {e}")
                await asyncio.sleep(60)

    async def apply_real_time_correction(
        self, decision_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply real-time bias correction to a decision"""
        try:
            original_decision = decision_data.copy()

            # Detect bias in the decision
            bias_detected = await self._detect_decision_bias(decision_data)

            if not bias_detected or max(bias_detected.values()) < 0.1:
                # No significant bias detected
                return decision_data

            # Select appropriate correction method
            correction_method = await self._select_correction_method(
                bias_detected, decision_data
            )

            # Apply correction
            corrected_decision = await self._apply_correction(
                decision_data, correction_method, bias_detected
            )

            # Calculate correction strength
            correction_strength = await self._calculate_correction_strength(
                original_decision, corrected_decision
            )

            # Create correction record
            correction = BiasCorrection(
                correction_id=str(uuid.uuid4()),
                original_decision=original_decision,
                corrected_decision=corrected_decision,
                correction_method=correction_method,
                bias_detected=bias_detected,
                correction_strength=correction_strength,
                confidence_impact=abs(
                    corrected_decision.get("confidence", 0.5)
                    - original_decision.get("confidence", 0.5)
                ),
                human_review_required=correction_strength
                > 0.3,  # High corrections need review
                timestamp=datetime.utcnow(),
            )

            # Store correction
            self.correction_history.append(correction)

            # Log correction
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "real_time_bias_correction",
                    "correction_id": correction.correction_id,
                    "decision_id": decision_data.get("decision_id", "unknown"),
                    "correction_method": correction_method,
                    "bias_detected": bias_detected,
                    "correction_strength": correction_strength,
                    "human_review_required": correction.human_review_required,
                    "timestamp": correction.timestamp.isoformat(),
                }
            )

            # Alert on high-strength corrections
            if correction_strength > 0.5:
                await self.alerting.send_alert(
                    f"high_strength_correction_{correction.correction_id}",
                    "High-strength bias correction applied (strength:"
                    f" {correction_strength:.2f})",
                    severity="medium",
                )

            return corrected_decision

        except Exception as e:
            logger.error(f"Real-time correction failed: {e}")
            return decision_data  # Return original if correction fails

    async def _detect_decision_bias(
        self, decision_data: dict[str, Any]
    ) -> dict[str, float]:
        """Detect bias in individual decision"""
        try:
            bias_scores = {}

            # Extract relevant features
            protected_attributes = decision_data.get("protected_attributes", {})
            decision_score = decision_data.get("decision_score", 0.5)
            context = decision_data.get("context", "unknown")

            # Simple bias detection based on protected attributes
            # In practice, this would use sophisticated bias detection algorithms

            for attr, value in protected_attributes.items():
                # Simulate bias detection for different attributes
                if attr == "race_ethnicity" and value in ["black", "hispanic"]:
                    bias_scores[attr] = np.random.uniform(0.1, 0.3)
                elif attr == "gender" and value == "female":
                    bias_scores[attr] = np.random.uniform(0.05, 0.2)
                elif attr == "age" and value in ["18-30", "70+"]:
                    bias_scores[attr] = np.random.uniform(0.05, 0.15)
                else:
                    bias_scores[attr] = np.random.uniform(0.0, 0.05)

            return bias_scores

        except Exception as e:
            logger.error(f"Decision bias detection failed: {e}")
            return {}

    async def _select_correction_method(
        self, bias_detected: dict[str, float], decision_data: dict[str, Any]
    ) -> str:
        """Select appropriate bias correction method"""
        try:
            max_bias = max(bias_detected.values()) if bias_detected else 0
            context = decision_data.get("context", "unknown")

            if max_bias > 0.3:
                # High bias - use constitutional override
                return "constitutional_override"
            elif max_bias > 0.2:
                # Medium bias - use outcome redistribution
                return "outcome_redistribution"
            elif max_bias > 0.1:
                # Low bias - use score calibration
                return "score_calibration"
            else:
                # Minimal bias - use threshold adjustment
                return "threshold_adjustment"

        except Exception:
            return "threshold_adjustment"

    async def _apply_correction(
        self,
        decision_data: dict[str, Any],
        correction_method: str,
        bias_detected: dict[str, float],
    ) -> dict[str, Any]:
        """Apply bias correction to decision"""
        try:
            corrected_data = decision_data.copy()

            if correction_method == "threshold_adjustment":
                # Adjust decision threshold based on bias
                current_score = corrected_data.get("decision_score", 0.5)
                bias_adjustment = sum(bias_detected.values()) * 0.1  # Small adjustment
                corrected_data["decision_score"] = max(
                    0, min(1, current_score + bias_adjustment)
                )

            elif correction_method == "score_calibration":
                # Calibrate score for fairness
                current_score = corrected_data.get("decision_score", 0.5)
                calibration_factor = 1 + sum(bias_detected.values()) * 0.2
                corrected_data["decision_score"] = max(
                    0, min(1, current_score * calibration_factor)
                )

            elif correction_method == "outcome_redistribution":
                # Adjust outcome based on bias detection
                current_outcome = corrected_data.get("decision_outcome", False)
                bias_strength = sum(bias_detected.values())
                if bias_strength > 0.2 and not current_outcome:
                    # Flip negative outcome if significant bias detected
                    corrected_data["decision_outcome"] = True
                    corrected_data["correction_applied"] = True

            elif correction_method == "constitutional_override":
                # Apply constitutional principles to override decision
                constitutional_score = await self._calculate_constitutional_score(
                    decision_data
                )
                corrected_data["decision_score"] = constitutional_score
                corrected_data["decision_outcome"] = constitutional_score > 0.5
                corrected_data["constitutional_override"] = True

            # Add correction metadata
            corrected_data["bias_correction_applied"] = True
            corrected_data["correction_method"] = correction_method
            corrected_data["original_bias_scores"] = bias_detected

            return corrected_data

        except Exception as e:
            logger.error(f"Bias correction application failed: {e}")
            return decision_data

    async def _calculate_constitutional_score(
        self, decision_data: dict[str, Any]
    ) -> float:
        """Calculate constitutional fairness score for decision"""
        try:
            # Simulate constitutional analysis
            base_score = decision_data.get("decision_score", 0.5)

            # Apply constitutional principles
            equal_protection_factor = 0.9  # Slightly favor equal protection
            due_process_factor = 0.95  # Ensure due process
            fairness_factor = 0.85  # Apply fairness constraints

            constitutional_score = (
                base_score
                * equal_protection_factor
                * due_process_factor
                * fairness_factor
            )

            return max(0, min(1, constitutional_score))

        except Exception:
            return 0.5

    async def _calculate_correction_strength(
        self, original: dict[str, Any], corrected: dict[str, Any]
    ) -> float:
        """Calculate strength of bias correction applied"""
        try:
            # Compare key decision metrics
            score_diff = abs(
                corrected.get("decision_score", 0.5)
                - original.get("decision_score", 0.5)
            )
            outcome_changed = corrected.get("decision_outcome") != original.get(
                "decision_outcome"
            )

            strength = score_diff
            if outcome_changed:
                strength += 0.5  # Outcome change is significant

            return min(1.0, strength)

        except Exception:
            return 0.0

    async def _run_effectiveness_analysis(self):
        """Run mitigation effectiveness analysis"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Run every hour

                if not self.running:
                    break

                await self._analyze_mitigation_effectiveness()

            except Exception as e:
                logger.error(f"Effectiveness analysis error: {e}")
                await asyncio.sleep(300)

    async def _analyze_mitigation_effectiveness(self):
        """Analyze effectiveness of mitigation strategies"""
        try:
            # Get recent mitigation results
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_results = [
                result
                for result in self.mitigation_results.values()
                if result.end_time >= recent_cutoff
            ]

            if not recent_results:
                return

            # Analyze by strategy
            strategy_analysis = defaultdict(list)
            for result in recent_results:
                strategy_analysis[result.strategy_used].append(result)

            effectiveness_summary = {}

            for strategy, results in strategy_analysis.items():
                avg_effectiveness = statistics.mean(
                    [r.effectiveness_score for r in results]
                )
                avg_bias_reduction = statistics.mean(
                    [r.bias_reduction_achieved for r in results]
                )
                success_rate = sum(
                    1 for r in results if r.execution_status == "success"
                ) / len(results)

                effectiveness_summary[strategy.value] = {
                    "count": len(results),
                    "avg_effectiveness": avg_effectiveness,
                    "avg_bias_reduction": avg_bias_reduction,
                    "success_rate": success_rate,
                }

            # Log effectiveness analysis
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "mitigation_effectiveness_analysis",
                    "analysis_period_hours": 24,
                    "strategies_analyzed": len(effectiveness_summary),
                    "total_mitigations": len(recent_results),
                    "effectiveness_summary": effectiveness_summary,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Effectiveness analysis failed: {e}")

    async def _run_strategy_optimization(self):
        """Run strategy optimization based on performance"""
        while self.running:
            try:
                await asyncio.sleep(7200)  # Run every 2 hours

                if not self.running:
                    break

                await self._optimize_mitigation_strategies()

            except Exception as e:
                logger.error(f"Strategy optimization error: {e}")
                await asyncio.sleep(600)

    async def _optimize_mitigation_strategies(self):
        """Optimize mitigation strategy selection based on performance"""
        try:
            # Analyze strategy performance over time
            optimization_recommendations = []

            for strategy, data in self.strategy_effectiveness.items():
                if data["usage_count"] < 5:
                    continue  # Need minimum usage for optimization

                # Check if strategy is underperforming
                if data["success_rate"] < 0.4:
                    optimization_recommendations.append(
                        f"Consider deprecating {strategy.value} due to low success rate"
                        f" ({data['success_rate']:.2%})"
                    )

                # Check if strategy is highly effective
                elif data["success_rate"] > 0.8 and data["avg_improvement"] > 0.4:
                    optimization_recommendations.append(
                        f"Prioritize {strategy.value} for similar cases (success rate:"
                        f" {data['success_rate']:.2%})"
                    )

            if optimization_recommendations:
                await self.audit_logger.log_compliance_event(
                    {
                        "event_type": "strategy_optimization_recommendations",
                        "recommendations": optimization_recommendations,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

        except Exception as e:
            logger.error(f"Strategy optimization failed: {e}")

    # Public methods for external integration

    def get_mitigation_status(self) -> dict[str, Any]:
        """Get current mitigation engine status"""
        try:
            current_time = datetime.utcnow()

            # Recent activity summary
            recent_cutoff = current_time - timedelta(hours=24)
            recent_plans = len(
                [
                    p
                    for p in self.mitigation_plans.values()
                    if p.created_at >= recent_cutoff
                ]
            )
            recent_results = len(
                [
                    r
                    for r in self.mitigation_results.values()
                    if r.end_time >= recent_cutoff
                ]
            )
            recent_corrections = len(
                [c for c in self.correction_history if c.timestamp >= recent_cutoff]
            )

            # Active mitigations
            active_count = len(
                [
                    m
                    for m in self.active_mitigations.values()
                    if m["status"] == "executing"
                ]
            )

            return {
                "engine_status": {
                    "enabled": self.mitigation_enabled,
                    "running": self.running,
                    "automatic_mitigation": self.automatic_mitigation,
                    "real_time_correction": self.real_time_correction,
                    "last_check": self.last_mitigation_check.isoformat(),
                },
                "recent_activity_24h": {
                    "plans_created": recent_plans,
                    "actions_executed": recent_results,
                    "real_time_corrections": recent_corrections,
                    "active_mitigations": active_count,
                },
                "strategy_effectiveness": {
                    strategy.value: {
                        "success_rate": data["success_rate"],
                        "avg_improvement": data["avg_improvement"],
                        "usage_count": data["usage_count"],
                    }
                    for strategy, data in self.strategy_effectiveness.items()
                    if data["usage_count"] > 0
                },
                "correction_models": list(self.correction_models.keys()),
                "configuration": {
                    "intervention_thresholds": {
                        severity.value: thresholds
                        for severity, thresholds in self.intervention_thresholds.items()
                    }
                },
            }

        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {"error": str(e)}

    async def manual_mitigation_request(
        self,
        context: BiasContext,
        bias_type: BiasType,
        protected_attr: ProtectedAttribute,
        severity: BiasSeverity,
        requester: str,
    ) -> str:
        """Request manual bias mitigation"""
        try:
            # Create mitigation plan
            plan = await self._create_mitigation_plan(
                context, bias_type, protected_attr, severity, []
            )

            if not plan:
                raise ValueError("Failed to create mitigation plan")

            # Log manual request
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "manual_mitigation_requested",
                    "plan_id": plan.plan_id,
                    "context": context.value,
                    "bias_type": bias_type.value,
                    "protected_attribute": protected_attr.value,
                    "severity": severity.value,
                    "requester": requester,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Execute based on severity
            if severity == BiasSeverity.CRITICAL:
                await self._execute_emergency_mitigation(plan)
            else:
                await self._request_human_approval_for_mitigation(plan)

            return plan.plan_id

        except Exception as e:
            logger.error(f"Manual mitigation request failed: {e}")
            raise

    def get_mitigation_history(
        self, time_window: timedelta = timedelta(days=7)
    ) -> dict[str, Any]:
        """Get mitigation history summary"""
        try:
            current_time = datetime.utcnow()
            start_time = current_time - time_window

            # Filter data by time window
            window_plans = [
                p for p in self.mitigation_plans.values() if p.created_at >= start_time
            ]
            window_results = [
                r for r in self.mitigation_results.values() if r.end_time >= start_time
            ]
            window_corrections = [
                c for c in self.correction_history if c.timestamp >= start_time
            ]

            # Summary statistics
            if window_results:
                avg_effectiveness = statistics.mean(
                    [r.effectiveness_score for r in window_results]
                )
                avg_bias_reduction = statistics.mean(
                    [r.bias_reduction_achieved for r in window_results]
                )
                success_rate = sum(
                    1 for r in window_results if r.execution_status == "success"
                ) / len(window_results)
            else:
                avg_effectiveness = avg_bias_reduction = success_rate = 0

            return {
                "period": {
                    "start_time": start_time.isoformat(),
                    "end_time": current_time.isoformat(),
                    "duration_days": time_window.days,
                },
                "summary": {
                    "mitigation_plans_created": len(window_plans),
                    "mitigation_actions_executed": len(window_results),
                    "real_time_corrections_applied": len(window_corrections),
                    "average_effectiveness": avg_effectiveness,
                    "average_bias_reduction": avg_bias_reduction,
                    "success_rate": success_rate,
                },
                "strategy_usage": {
                    strategy.value: len(
                        [r for r in window_results if r.strategy_used == strategy]
                    )
                    for strategy in MitigationStrategy
                },
                "correction_methods": (
                    {
                        method: len(
                            [
                                c
                                for c in window_corrections
                                if c.correction_method == method
                            ]
                        )
                        for method in set(
                            c.correction_method for c in window_corrections
                        )
                    }
                    if window_corrections
                    else {}
                ),
            }

        except Exception as e:
            logger.error(f"History retrieval failed: {e}")
            return {"error": str(e)}


# Example usage
async def example_usage():
    """Example of using the bias mitigation engine"""
    # Initialize mitigation engine
    engine = BiasMitigationEngine(
        {
            "mitigation_enabled": True,
            "automatic_mitigation": True,
            "real_time_correction": True,
        }
    )

    # Start engine (would run continuously in production)
    logger.info("Starting bias mitigation engine demo")
    engine_task = asyncio.create_task(engine.start_mitigation_engine())

    # Simulate a manual mitigation request
    try:
        plan_id = await engine.manual_mitigation_request(
            BiasContext.POLICY_RECOMMENDATION,
            BiasType.DEMOGRAPHIC_PARITY,
            ProtectedAttribute.RACE_ETHNICITY,
            BiasSeverity.HIGH,
            "demo_user",
        )
        logger.info(f"Manual mitigation plan created: {plan_id}")
    except Exception as e:
        logger.error(f"Manual mitigation request failed: {e}")

    # Simulate real-time correction
    decision_data = {
        "decision_id": "test_decision_001",
        "decision_score": 0.3,
        "decision_outcome": False,
        "confidence": 0.8,
        "context": "policy_recommendation",
        "protected_attributes": {
            "race_ethnicity": "black",
            "gender": "female",
            "age": "25-35",
        },
    }

    corrected_decision = await engine.apply_real_time_correction(decision_data)
    logger.info(
        "Real-time correction applied:"
        f" {corrected_decision.get('bias_correction_applied', False)}"
    )

    # Let it run for a short period
    await asyncio.sleep(10)

    # Stop engine
    await engine.stop_mitigation_engine()
    engine_task.cancel()

    # Get status and history
    status = engine.get_mitigation_status()
    history = engine.get_mitigation_history(timedelta(hours=1))

    logger.info(f"Engine status: {status}")
    logger.info(f"Mitigation history: {history}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
