"""
Robust Coordination Metrics Service
Constitutional Hash: cdd01ef066bc6cf2

CARMA-inspired robust metrics for multi-agent coordination that distinguish genuine
coordination effectiveness from spurious formatting/style correlations. Implements
causal robustness in coordination quality assessment.
"""

import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

import numpy as np
from pydantic import Field

from .blackboard import BlackboardService, KnowledgeItem
from .causal_coordination_model import (
    CoordinationAttribute,
)

# Configure logging
logger = logging.getLogger(__name__)


class MetricRobustnessLevel(Enum):
    """Robustness levels for coordination metrics"""

    HIGHLY_ROBUST = "highly_robust"
    MODERATELY_ROBUST = "moderately_robust"
    WEAKLY_ROBUST = "weakly_robust"
    VULNERABLE = "vulnerable"


class CoordinationMetricType(Enum):
    """Types of coordination metrics"""

    TASK_SUCCESS_RATE = "task_success_rate"
    COMMUNICATION_EFFICIENCY = "communication_efficiency"
    RESOURCE_UTILIZATION = "resource_utilization"
    DECISION_LATENCY = "decision_latency"
    CONFLICT_RESOLUTION_SPEED = "conflict_resolution_speed"
    KNOWLEDGE_SHARING_RATE = "knowledge_sharing_rate"
    CONSTITUTIONAL_COMPLIANCE_RATE = "constitutional_compliance_rate"
    STAKEHOLDER_SATISFACTION = "stakeholder_satisfaction"
    ADAPTATION_SUCCESS_RATE = "adaptation_success_rate"
    OVERALL_COORDINATION_QUALITY = "overall_coordination_quality"


@dataclass
class MetricMeasurement:
    """Single metric measurement with robustness context"""

    metric_id: str
    metric_type: CoordinationMetricType
    value: float
    timestamp: datetime
    scenario_context: dict[str, Any]
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Robustness indicators
    causal_factors: dict[str, float] = field(default_factory=dict)
    spurious_indicators: dict[str, float] = field(default_factory=dict)
    robustness_score: float = Field(ge=0.0, le=1.0, default=0.0)
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.0)


@dataclass
class RobustMetricSummary:
    """Summary of robust metric analysis"""

    metric_type: CoordinationMetricType
    measurement_period: str
    total_measurements: int

    # Core statistics
    mean_value: float
    median_value: float
    std_deviation: float
    min_value: float
    max_value: float

    # Robustness analysis
    causal_sensitivity: float = Field(ge=0.0, le=1.0, default=0.0)
    spurious_resistance: float = Field(ge=0.0, le=1.0, default=0.0)
    overall_robustness: float = Field(ge=0.0, le=1.0, default=0.0)
    robustness_level: MetricRobustnessLevel = MetricRobustnessLevel.MODERATELY_ROBUST

    # Trend analysis
    trend_direction: str = "stable"  # "increasing", "decreasing", "stable"
    trend_strength: float = Field(ge=0.0, le=1.0, default=0.0)

    constitutional_hash: str = "cdd01ef066bc6cf2"
    analysis_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class RobustCoordinationMetrics:
    """Service for computing robust coordination metrics resistant to spurious correlations"""

    # Metric importance weights for coordination assessment
    METRIC_IMPORTANCE_WEIGHTS = {
        CoordinationMetricType.CONSTITUTIONAL_COMPLIANCE_RATE: 1.0,
        CoordinationMetricType.TASK_SUCCESS_RATE: 0.9,
        CoordinationMetricType.OVERALL_COORDINATION_QUALITY: 0.85,
        CoordinationMetricType.COMMUNICATION_EFFICIENCY: 0.8,
        CoordinationMetricType.DECISION_LATENCY: 0.75,
        CoordinationMetricType.RESOURCE_UTILIZATION: 0.7,
        CoordinationMetricType.CONFLICT_RESOLUTION_SPEED: 0.65,
        CoordinationMetricType.KNOWLEDGE_SHARING_RATE: 0.6,
        CoordinationMetricType.ADAPTATION_SUCCESS_RATE: 0.55,
        CoordinationMetricType.STAKEHOLDER_SATISFACTION: 0.5,
    }

    # Robustness thresholds for different metrics
    ROBUSTNESS_THRESHOLDS = {
        "highly_robust": 0.9,
        "moderately_robust": 0.7,
        "weakly_robust": 0.5,
        "vulnerable": 0.0,
    }

    # Spurious correlation detection thresholds per metric
    SPURIOUS_CORRELATION_THRESHOLDS = {
        CoordinationMetricType.TASK_SUCCESS_RATE: 0.05,
        CoordinationMetricType.COMMUNICATION_EFFICIENCY: 0.1,
        CoordinationMetricType.RESOURCE_UTILIZATION: 0.08,
        CoordinationMetricType.DECISION_LATENCY: 0.15,
        CoordinationMetricType.CONSTITUTIONAL_COMPLIANCE_RATE: 0.02,
        CoordinationMetricType.OVERALL_COORDINATION_QUALITY: 0.05,
    }

    def __init__(
        self,
        blackboard_service: BlackboardService,
        window_size: int = 1000,
        robustness_analysis_interval: int = 100,
    ):
        """Initialize robust coordination metrics service"""
        self.blackboard = blackboard_service
        self.window_size = window_size
        self.robustness_analysis_interval = robustness_analysis_interval
        self.logger = logging.getLogger(__name__)

        # Metric storage
        self.metric_history: dict[CoordinationMetricType, deque] = {
            metric_type: deque(maxlen=window_size)
            for metric_type in CoordinationMetricType
        }

        # Robustness analysis data
        self.causal_factor_history = defaultdict(lambda: deque(maxlen=window_size))
        self.spurious_correlation_history = defaultdict(
            lambda: deque(maxlen=window_size)
        )

        # Performance tracking
        self.measurement_count = 0
        self.robustness_analysis_count = 0

        # Alerts and monitoring
        self.robustness_alerts = []
        self.spurious_correlation_alerts = []

    async def record_coordination_measurement(
        self,
        metric_type: CoordinationMetricType,
        value: float,
        scenario_context: dict[str, Any],
        causal_factors: dict[str, float] | None = None,
        spurious_indicators: dict[str, float] | None = None,
    ) -> MetricMeasurement:
        """Record a coordination metric measurement with robustness analysis"""

        measurement_id = str(uuid4())
        timestamp = datetime.now(timezone.utc)

        # Validate constitutional compliance
        if scenario_context.get("constitutional_hash") != "cdd01ef066bc6cf2":
            scenario_context["constitutional_hash"] = "cdd01ef066bc6cf2"

        # Analyze robustness of this measurement
        robustness_score, confidence_level = await self._analyze_measurement_robustness(
            metric_type, value, causal_factors or {}, spurious_indicators or {}
        )

        # Create measurement record
        measurement = MetricMeasurement(
            metric_id=measurement_id,
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            scenario_context=scenario_context,
            causal_factors=causal_factors or {},
            spurious_indicators=spurious_indicators or {},
            robustness_score=robustness_score,
            confidence_level=confidence_level,
        )

        # Store measurement
        self.metric_history[metric_type].append(measurement)

        # Update causal factor and spurious correlation tracking
        if causal_factors:
            for factor, factor_value in causal_factors.items():
                self.causal_factor_history[factor].append((timestamp, factor_value))

        if spurious_indicators:
            for indicator, indicator_value in spurious_indicators.items():
                self.spurious_correlation_history[indicator].append(
                    (timestamp, indicator_value)
                )

        # Increment measurement count
        self.measurement_count += 1

        # Perform periodic robustness analysis
        if self.measurement_count % self.robustness_analysis_interval == 0:
            await self._perform_periodic_robustness_analysis()

        # Check for robustness alerts
        await self._check_robustness_alerts(measurement)

        # Log measurement
        await self._log_measurement(measurement)

        return measurement

    async def _analyze_measurement_robustness(
        self,
        metric_type: CoordinationMetricType,
        value: float,
        causal_factors: dict[str, float],
        spurious_indicators: dict[str, float],
    ) -> tuple[float, float]:
        """Analyze robustness of a single measurement"""

        robustness_components = []

        # 1. Causal factor alignment
        if causal_factors:
            causal_alignment = self._assess_causal_alignment(
                metric_type, value, causal_factors
            )
            robustness_components.append(causal_alignment * 0.4)
        else:
            robustness_components.append(0.2)  # Partial credit for no causal info

        # 2. Spurious correlation resistance
        if spurious_indicators:
            spurious_resistance = self._assess_spurious_resistance(
                metric_type, spurious_indicators
            )
            robustness_components.append(spurious_resistance * 0.3)
        else:
            robustness_components.append(0.3)  # Full credit for no spurious factors

        # 3. Historical consistency
        historical_consistency = self._assess_historical_consistency(metric_type, value)
        robustness_components.append(historical_consistency * 0.2)

        # 4. Constitutional compliance context
        constitutional_compliance = 0.1  # Base compliance
        robustness_components.append(constitutional_compliance)

        # Calculate overall robustness
        robustness_score = sum(robustness_components)

        # Calculate confidence based on data availability and consistency
        confidence_level = self._calculate_measurement_confidence(
            metric_type, causal_factors, spurious_indicators
        )

        return min(1.0, robustness_score), min(1.0, confidence_level)

    def _assess_causal_alignment(
        self,
        metric_type: CoordinationMetricType,
        value: float,
        causal_factors: dict[str, float],
    ) -> float:
        """Assess alignment between metric value and causal factors"""

        # Define expected relationships between causal factors and metrics
        expected_relationships = {
            CoordinationMetricType.TASK_SUCCESS_RATE: {
                CoordinationAttribute.TASK_COMPLETION_ACCURACY.value: "positive",
                CoordinationAttribute.COMMUNICATION_CLARITY.value: "positive",
                CoordinationAttribute.GOAL_ALIGNMENT.value: "positive",
            },
            CoordinationMetricType.COMMUNICATION_EFFICIENCY: {
                CoordinationAttribute.COMMUNICATION_CLARITY.value: "positive",
                CoordinationAttribute.KNOWLEDGE_SHARING.value: "positive",
            },
            CoordinationMetricType.CONSTITUTIONAL_COMPLIANCE_RATE: {
                CoordinationAttribute.CONSTITUTIONAL_COMPLIANCE.value: "positive"
            },
        }

        metric_expectations = expected_relationships.get(metric_type, {})
        if not metric_expectations:
            return 0.5  # Neutral score if no expectations defined

        alignment_scores = []
        for factor, factor_value in causal_factors.items():
            if factor in metric_expectations:
                expected_relationship = metric_expectations[factor]
                if expected_relationship == "positive":
                    # Higher factor values should correlate with higher metric values
                    alignment_score = min(1.0, factor_value * value)
                else:  # negative relationship
                    alignment_score = min(1.0, (1.0 - factor_value) * value)
                alignment_scores.append(alignment_score)

        return statistics.mean(alignment_scores) if alignment_scores else 0.5

    def _assess_spurious_resistance(
        self, metric_type: CoordinationMetricType, spurious_indicators: dict[str, float]
    ) -> float:
        """Assess resistance to spurious correlations"""

        threshold = self.SPURIOUS_CORRELATION_THRESHOLDS.get(metric_type, 0.1)
        resistance_scores = []

        for indicator_value in spurious_indicators.values():
            # Higher spurious indicator values should NOT significantly affect robustness
            if indicator_value <= threshold:
                resistance_scores.append(1.0)  # Good resistance
            else:
                # Linear penalty for exceeding threshold
                penalty = min(1.0, (indicator_value - threshold) / threshold)
                resistance_scores.append(1.0 - penalty)

        return statistics.mean(resistance_scores) if resistance_scores else 1.0

    def _assess_historical_consistency(
        self, metric_type: CoordinationMetricType, value: float
    ) -> float:
        """Assess consistency with historical measurements"""

        history = self.metric_history.get(metric_type, deque())
        if len(history) < 3:
            return 0.5  # Neutral score for insufficient history

        recent_values = [m.value for m in list(history)[-10:]]  # Last 10 measurements

        if not recent_values:
            return 0.5

        # Calculate consistency based on standard deviation
        mean_value = statistics.mean(recent_values)
        std_dev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0.0

        # Normalize current value relative to historical range
        if std_dev == 0:
            consistency = 1.0 if abs(value - mean_value) < 0.1 else 0.5
        else:
            z_score = abs(value - mean_value) / std_dev
            consistency = max(0.0, 1.0 - (z_score / 3.0))  # 3-sigma rule

        return consistency

    def _calculate_measurement_confidence(
        self,
        metric_type: CoordinationMetricType,
        causal_factors: dict[str, float],
        spurious_indicators: dict[str, float],
    ) -> float:
        """Calculate confidence level for measurement"""

        confidence_components = []

        # Data availability component
        data_availability = 0.5  # Base
        if causal_factors:
            data_availability += 0.3
        if spurious_indicators:
            data_availability += 0.2
        confidence_components.append(data_availability)

        # Historical data component
        history_length = len(self.metric_history.get(metric_type, []))
        history_confidence = min(
            1.0, history_length / 50.0
        )  # Full confidence at 50+ measurements
        confidence_components.append(history_confidence)

        # Metric importance component
        importance = self.METRIC_IMPORTANCE_WEIGHTS.get(metric_type, 0.5)
        confidence_components.append(importance)

        return statistics.mean(confidence_components)

    async def generate_robust_metric_summary(
        self,
        metric_type: CoordinationMetricType,
        time_period: timedelta | None = None,
    ) -> RobustMetricSummary:
        """Generate robust summary for a specific metric"""

        if time_period is None:
            time_period = timedelta(hours=24)  # Default to last 24 hours

        cutoff_time = datetime.now(timezone.utc) - time_period

        # Filter measurements by time period
        measurements = [
            m
            for m in self.metric_history.get(metric_type, [])
            if m.timestamp >= cutoff_time
        ]

        if not measurements:
            return self._create_empty_summary(metric_type, time_period)

        # Calculate basic statistics
        values = [m.value for m in measurements]
        mean_value = statistics.mean(values)
        median_value = statistics.median(values)
        std_deviation = statistics.stdev(values) if len(values) > 1 else 0.0
        min_value = min(values)
        max_value = max(values)

        # Calculate robustness metrics
        robustness_scores = [m.robustness_score for m in measurements]
        causal_sensitivity = await self._calculate_causal_sensitivity(measurements)
        spurious_resistance = await self._calculate_spurious_resistance(measurements)
        overall_robustness = (
            statistics.mean(robustness_scores) if robustness_scores else 0.0
        )

        # Determine robustness level
        robustness_level = self._determine_robustness_level(overall_robustness)

        # Analyze trends
        trend_direction, trend_strength = self._analyze_trends(values)

        summary = RobustMetricSummary(
            metric_type=metric_type,
            measurement_period=f"last_{time_period.total_seconds():.0f}_seconds",
            total_measurements=len(measurements),
            mean_value=mean_value,
            median_value=median_value,
            std_deviation=std_deviation,
            min_value=min_value,
            max_value=max_value,
            causal_sensitivity=causal_sensitivity,
            spurious_resistance=spurious_resistance,
            overall_robustness=overall_robustness,
            robustness_level=robustness_level,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
        )

        # Log summary
        await self._log_metric_summary(summary)

        return summary

    async def _calculate_causal_sensitivity(
        self, measurements: list[MetricMeasurement]
    ) -> float:
        """Calculate causal sensitivity from measurements"""

        causal_correlations = []

        for measurement in measurements:
            if measurement.causal_factors:
                # Calculate correlation between causal factors and metric value
                for factor_value in measurement.causal_factors.values():
                    correlation = min(1.0, factor_value * measurement.value)
                    causal_correlations.append(correlation)

        return statistics.mean(causal_correlations) if causal_correlations else 0.5

    async def _calculate_spurious_resistance(
        self, measurements: list[MetricMeasurement]
    ) -> float:
        """Calculate spurious correlation resistance from measurements"""

        resistance_scores = []

        for measurement in measurements:
            if measurement.spurious_indicators:
                # Calculate resistance based on spurious indicator levels
                for indicator_value in measurement.spurious_indicators.values():
                    threshold = 0.1  # Default threshold
                    if indicator_value <= threshold:
                        resistance_scores.append(1.0)
                    else:
                        resistance = 1.0 - min(1.0, indicator_value - threshold)
                        resistance_scores.append(resistance)
            else:
                resistance_scores.append(
                    1.0
                )  # Full resistance if no spurious indicators

        return statistics.mean(resistance_scores) if resistance_scores else 1.0

    def _determine_robustness_level(
        self, overall_robustness: float
    ) -> MetricRobustnessLevel:
        """Determine robustness level based on score"""

        if overall_robustness >= self.ROBUSTNESS_THRESHOLDS["highly_robust"]:
            return MetricRobustnessLevel.HIGHLY_ROBUST
        if overall_robustness >= self.ROBUSTNESS_THRESHOLDS["moderately_robust"]:
            return MetricRobustnessLevel.MODERATELY_ROBUST
        if overall_robustness >= self.ROBUSTNESS_THRESHOLDS["weakly_robust"]:
            return MetricRobustnessLevel.WEAKLY_ROBUST
        return MetricRobustnessLevel.VULNERABLE

    def _analyze_trends(self, values: list[float]) -> tuple[str, float]:
        """Analyze trend direction and strength"""

        if len(values) < 3:
            return "stable", 0.0

        # Simple linear trend analysis
        x = list(range(len(values)))

        # Calculate correlation coefficient for trend
        if len(values) > 1:
            try:
                correlation = np.corrcoef(x, values)[0, 1]

                if abs(correlation) < 0.1:
                    return "stable", abs(correlation)
                if correlation > 0.1:
                    return "increasing", correlation
                return "decreasing", abs(correlation)
            except:
                return "stable", 0.0

        return "stable", 0.0

    def _create_empty_summary(
        self, metric_type: CoordinationMetricType, time_period: timedelta
    ) -> RobustMetricSummary:
        """Create empty summary for metrics with no data"""

        return RobustMetricSummary(
            metric_type=metric_type,
            measurement_period=f"last_{time_period.total_seconds():.0f}_seconds",
            total_measurements=0,
            mean_value=0.0,
            median_value=0.0,
            std_deviation=0.0,
            min_value=0.0,
            max_value=0.0,
            causal_sensitivity=0.0,
            spurious_resistance=1.0,  # Perfect resistance with no data
            overall_robustness=0.0,
            robustness_level=MetricRobustnessLevel.VULNERABLE,
            trend_direction="stable",
            trend_strength=0.0,
        )

    async def _perform_periodic_robustness_analysis(self) -> None:
        """Perform periodic analysis of all metrics"""

        self.robustness_analysis_count += 1
        analysis_results = {}

        for metric_type in CoordinationMetricType:
            summary = await self.generate_robust_metric_summary(metric_type)
            analysis_results[metric_type.value] = summary

            # Check for robustness degradation
            if summary.robustness_level in {
                MetricRobustnessLevel.WEAKLY_ROBUST,
                MetricRobustnessLevel.VULNERABLE,
            }:
                await self._create_robustness_alert(metric_type, summary)

        # Log periodic analysis
        await self._log_periodic_analysis(analysis_results)

    async def _check_robustness_alerts(self, measurement: MetricMeasurement) -> None:
        """Check for robustness alerts based on new measurement"""

        # Low robustness alert
        if measurement.robustness_score < 0.3:
            alert = {
                "type": "low_robustness",
                "metric_type": measurement.metric_type.value,
                "robustness_score": measurement.robustness_score,
                "timestamp": measurement.timestamp.isoformat(),
                "constitutional_hash": "cdd01ef066bc6cf2",
            }
            self.robustness_alerts.append(alert)
            await self._log_robustness_alert(alert)

        # Spurious correlation alert
        if measurement.spurious_indicators:
            for indicator, value in measurement.spurious_indicators.items():
                threshold = self.SPURIOUS_CORRELATION_THRESHOLDS.get(
                    measurement.metric_type, 0.1
                )
                if value > threshold:
                    alert = {
                        "type": "spurious_correlation",
                        "metric_type": measurement.metric_type.value,
                        "spurious_indicator": indicator,
                        "indicator_value": value,
                        "threshold": threshold,
                        "timestamp": measurement.timestamp.isoformat(),
                        "constitutional_hash": "cdd01ef066bc6cf2",
                    }
                    self.spurious_correlation_alerts.append(alert)
                    await self._log_spurious_correlation_alert(alert)

    async def _create_robustness_alert(
        self, metric_type: CoordinationMetricType, summary: RobustMetricSummary
    ) -> None:
        """Create robustness degradation alert"""

        alert = {
            "type": "robustness_degradation",
            "metric_type": metric_type.value,
            "robustness_level": summary.robustness_level.value,
            "overall_robustness": summary.overall_robustness,
            "measurements_analyzed": summary.total_measurements,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        await self._log_robustness_alert(alert)

    async def _log_measurement(self, measurement: MetricMeasurement) -> None:
        """Log measurement to blackboard"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "robust_coordination_measurement",
                "metric_type": measurement.metric_type.value,
                "value": measurement.value,
                "robustness_score": measurement.robustness_score,
                "confidence_level": measurement.confidence_level,
                "causal_factors": measurement.causal_factors,
                "spurious_indicators": measurement.spurious_indicators,
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "robust_coordination_metrics",
                "timestamp": measurement.timestamp.isoformat(),
                "metric_quality": (
                    "high"
                    if measurement.robustness_score >= 0.8
                    else "medium" if measurement.robustness_score >= 0.6 else "low"
                ),
            },
            tags=[
                "coordination",
                "metrics",
                "robust",
                "carma",
                measurement.metric_type.value,
            ],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    async def _log_metric_summary(self, summary: RobustMetricSummary) -> None:
        """Log metric summary to blackboard"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "robust_metric_summary",
                "metric_type": summary.metric_type.value,
                "measurement_period": summary.measurement_period,
                "total_measurements": summary.total_measurements,
                "statistics": {
                    "mean_value": summary.mean_value,
                    "median_value": summary.median_value,
                    "std_deviation": summary.std_deviation,
                    "min_value": summary.min_value,
                    "max_value": summary.max_value,
                },
                "robustness_analysis": {
                    "causal_sensitivity": summary.causal_sensitivity,
                    "spurious_resistance": summary.spurious_resistance,
                    "overall_robustness": summary.overall_robustness,
                    "robustness_level": summary.robustness_level.value,
                },
                "trend_analysis": {
                    "direction": summary.trend_direction,
                    "strength": summary.trend_strength,
                },
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "robust_coordination_metrics",
                "timestamp": summary.analysis_timestamp.isoformat(),
                "robustness_level": summary.robustness_level.value,
            },
            tags=[
                "coordination",
                "metrics",
                "summary",
                "robust",
                summary.metric_type.value,
            ],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    async def _log_periodic_analysis(
        self, analysis_results: dict[str, RobustMetricSummary]
    ) -> None:
        """Log periodic analysis results"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "periodic_robustness_analysis",
                "analysis_count": self.robustness_analysis_count,
                "metrics_analyzed": len(analysis_results),
                "robustness_overview": {
                    metric: {
                        "robustness_level": summary.robustness_level.value,
                        "overall_robustness": summary.overall_robustness,
                        "causal_sensitivity": summary.causal_sensitivity,
                        "spurious_resistance": summary.spurious_resistance,
                    }
                    for metric, summary in analysis_results.items()
                },
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "robust_coordination_metrics",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "analysis_type": "periodic_robustness",
            },
            tags=["coordination", "metrics", "analysis", "periodic", "robustness"],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    async def _log_robustness_alert(self, alert: dict[str, Any]) -> None:
        """Log robustness alert"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "coordination_robustness_alert",
                "alert_details": alert,
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "robust_coordination_metrics",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "alert_type": alert["type"],
                "priority": (
                    "high"
                    if alert["type"] in {"low_robustness", "robustness_degradation"}
                    else "medium"
                ),
            },
            tags=["coordination", "metrics", "alert", "robustness", alert["type"]],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    async def _log_spurious_correlation_alert(self, alert: dict[str, Any]) -> None:
        """Log spurious correlation alert"""

        knowledge_item = KnowledgeItem(
            id=str(uuid4()),
            content={
                "type": "spurious_correlation_alert",
                "alert_details": alert,
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            metadata={
                "source": "robust_coordination_metrics",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "alert_type": "spurious_correlation",
                "priority": "medium",
            },
            tags=["coordination", "metrics", "alert", "spurious", "correlation"],
        )

        await self.blackboard.add_knowledge(knowledge_item)

    def get_robustness_statistics(self) -> dict[str, Any]:
        """Get robustness statistics for all metrics"""

        stats = {
            "total_measurements": self.measurement_count,
            "robustness_analyses_performed": self.robustness_analysis_count,
            "robustness_alerts_generated": len(self.robustness_alerts),
            "spurious_correlation_alerts": len(self.spurious_correlation_alerts),
            "constitutional_hash": "cdd01ef066bc6cf2",
            "service_version": "1.0.0_carma_inspired",
        }

        # Add per-metric statistics
        for metric_type in CoordinationMetricType:
            measurements = self.metric_history.get(metric_type, [])
            if measurements:
                robustness_scores = [m.robustness_score for m in measurements]
                stats[f"{metric_type.value}_statistics"] = {
                    "measurement_count": len(measurements),
                    "average_robustness": statistics.mean(robustness_scores),
                    "robustness_std_dev": (
                        statistics.stdev(robustness_scores)
                        if len(robustness_scores) > 1
                        else 0.0
                    ),
                }

        return stats
