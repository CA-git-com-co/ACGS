"""
Bias Drift Monitoring System

Specialized bias drift detection and monitoring system for ACGS that implements
advanced fairness metrics tracking, bias pattern detection, and automated
remediation strategies. Ensures constitutional AI systems maintain fairness
across different demographic groups and decision contexts.

Key Features:
- Multi-dimensional bias detection (demographic, intersectional, contextual)
- Real-time fairness metric monitoring
- Bias drift pattern analysis and prediction
- Automated bias mitigation recommendations
- Constitutional fairness compliance tracking
- Protected group monitoring and analysis
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
import math
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import numpy as np

from services.shared.fairness.fairlearn_integration import FairlearnBiasDetector
from services.shared.fairness.whatif_tool_integration import WhatIfToolAnalyzer
from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)


class BiasType(Enum):
    """Types of bias to monitor"""

    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUALITY_OF_OPPORTUNITY = "equality_of_opportunity"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"
    COUNTERFACTUAL_FAIRNESS = "counterfactual_fairness"
    TREATMENT_EQUALITY = "treatment_equality"
    CONDITIONAL_STATISTICAL_PARITY = "conditional_statistical_parity"


class ProtectedAttribute(Enum):
    """Protected attributes to monitor"""

    AGE = "age"
    GENDER = "gender"
    RACE_ETHNICITY = "race_ethnicity"
    RELIGION = "religion"
    POLITICAL_AFFILIATION = "political_affiliation"
    SOCIOECONOMIC_STATUS = "socioeconomic_status"
    GEOGRAPHIC_REGION = "geographic_region"
    DISABILITY_STATUS = "disability_status"
    EDUCATION_LEVEL = "education_level"
    EMPLOYMENT_STATUS = "employment_status"


class BiasSeverity(Enum):
    """Severity levels for bias drift"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BiasContext(Enum):
    """Contexts where bias can occur"""

    POLICY_RECOMMENDATION = "policy_recommendation"
    RESOURCE_ALLOCATION = "resource_allocation"
    LEGAL_INTERPRETATION = "legal_interpretation"
    DEMOCRATIC_PARTICIPATION = "democratic_participation"
    CONSTITUTIONAL_ANALYSIS = "constitutional_analysis"
    CITIZEN_SERVICE_DELIVERY = "citizen_service_delivery"
    JUDICIAL_SUPPORT = "judicial_support"
    LEGISLATIVE_ANALYSIS = "legislative_analysis"


@dataclass
class BiasMetricResult:
    """Result of a bias metric calculation"""

    metric_id: str
    bias_type: BiasType
    protected_attribute: ProtectedAttribute
    context: BiasContext
    metric_value: float
    baseline_value: float
    drift_score: float
    severity: BiasSeverity
    affected_groups: list[str]
    group_disparities: dict[str, float]
    confidence_interval: tuple[float, float]
    statistical_significance: float
    timestamp: datetime


@dataclass
class BiasDriftAlert:
    """Alert for detected bias drift"""

    alert_id: str
    drift_type: str
    severity: BiasSeverity
    affected_metrics: list[BiasMetricResult]
    temporal_pattern: dict[str, Any]
    root_cause_analysis: list[str]
    recommended_actions: list[str]
    stakeholders: list[str]
    regulatory_implications: list[str]
    timestamp: datetime


@dataclass
class IntersectionalBiasAnalysis:
    """Analysis of intersectional bias patterns"""

    analysis_id: str
    attribute_combinations: list[tuple[ProtectedAttribute, ...]]
    bias_interactions: dict[str, float]
    amplification_factors: dict[str, float]
    mitigation_complexity: float
    priority_combinations: list[tuple[ProtectedAttribute, ...]]
    timestamp: datetime


@dataclass
class BiasPattern:
    """Detected bias pattern"""

    pattern_id: str
    pattern_type: str
    description: str
    affected_attributes: list[ProtectedAttribute]
    temporal_characteristics: dict[str, Any]
    predictive_indicators: list[str]
    mitigation_strategies: list[str]
    confidence: float
    risk_level: BiasSeverity


@dataclass
class FairnessCompliance:
    """Fairness compliance status"""

    compliance_id: str
    context: BiasContext
    overall_fairness_score: float
    metric_compliance: dict[BiasType, bool]
    protected_group_compliance: dict[ProtectedAttribute, bool]
    constitutional_alignment: float
    regulatory_compliance: dict[str, bool]
    improvement_recommendations: list[str]
    timestamp: datetime


class BiasDriftMonitor:
    """
    Comprehensive bias drift monitoring system for constitutional AI
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Initialize bias detection integrations
        self.fairlearn_detector = FairlearnBiasDetector()
        self.whatif_analyzer = WhatIfToolAnalyzer()

        # Monitoring configuration
        self.monitoring_enabled = config.get("monitoring_enabled", True)
        self.monitoring_interval_seconds = config.get(
            "monitoring_interval_seconds", 300
        )  # 5 minutes
        self.intersectional_analysis_enabled = config.get(
            "intersectional_analysis_enabled", True
        )
        self.real_time_alerts_enabled = config.get("real_time_alerts_enabled", True)

        # Bias thresholds for different contexts
        self.bias_thresholds = config.get(
            "bias_thresholds",
            {
                BiasContext.CONSTITUTIONAL_ANALYSIS: {
                    BiasType.DEMOGRAPHIC_PARITY: {
                        "low": 0.02,
                        "medium": 0.05,
                        "high": 0.10,
                        "critical": 0.15,
                    },
                    BiasType.EQUALIZED_ODDS: {
                        "low": 0.03,
                        "medium": 0.07,
                        "high": 0.12,
                        "critical": 0.20,
                    },
                    BiasType.CALIBRATION: {
                        "low": 0.02,
                        "medium": 0.05,
                        "high": 0.10,
                        "critical": 0.15,
                    },
                },
                BiasContext.POLICY_RECOMMENDATION: {
                    BiasType.DEMOGRAPHIC_PARITY: {
                        "low": 0.03,
                        "medium": 0.08,
                        "high": 0.15,
                        "critical": 0.25,
                    },
                    BiasType.EQUALIZED_ODDS: {
                        "low": 0.04,
                        "medium": 0.10,
                        "high": 0.18,
                        "critical": 0.30,
                    },
                },
                BiasContext.RESOURCE_ALLOCATION: {
                    BiasType.DEMOGRAPHIC_PARITY: {
                        "low": 0.01,
                        "medium": 0.03,
                        "high": 0.07,
                        "critical": 0.12,
                    },
                    BiasType.TREATMENT_EQUALITY: {
                        "low": 0.02,
                        "medium": 0.05,
                        "high": 0.10,
                        "critical": 0.18,
                    },
                },
            },
        )

        # Default thresholds for contexts not explicitly configured
        self.default_thresholds = {
            BiasType.DEMOGRAPHIC_PARITY: {
                "low": 0.05,
                "medium": 0.10,
                "high": 0.20,
                "critical": 0.35,
            },
            BiasType.EQUALIZED_ODDS: {
                "low": 0.05,
                "medium": 0.10,
                "high": 0.20,
                "critical": 0.35,
            },
            BiasType.CALIBRATION: {
                "low": 0.03,
                "medium": 0.08,
                "high": 0.15,
                "critical": 0.25,
            },
        }

        # Data storage
        self.baseline_metrics = {}  # (context, bias_type, attribute) -> baseline_value
        self.metric_history = deque(maxlen=10000)
        self.drift_alerts = {}
        self.bias_patterns = deque(maxlen=500)
        self.compliance_history = deque(maxlen=1000)

        # Analysis state
        self.running = False
        self.last_analysis_time = datetime.utcnow()

        # Pattern tracking
        self.temporal_patterns = defaultdict(list)
        self.group_performance_trends = defaultdict(lambda: deque(maxlen=100))

        # Constitutional fairness principles
        self.constitutional_principles = {
            "equal_protection": (
                "All citizens must receive equal protection under the law"
            ),
            "due_process": "Fair treatment through normal judicial system",
            "non_discrimination": (
                "No discrimination based on protected characteristics"
            ),
            "proportional_representation": (
                "Fair representation across demographic groups"
            ),
            "democratic_participation": (
                "Equal opportunity for democratic participation"
            ),
        }

    async def start_monitoring(self):
        """Start bias drift monitoring"""
        if self.running:
            logger.warning("Bias drift monitoring is already running")
            return

        self.running = True
        logger.info("Starting bias drift monitoring")

        try:
            # Start monitoring tasks
            monitoring_tasks = [
                self._run_bias_monitoring_loop(),
                self._run_intersectional_analysis(),
                self._run_pattern_detection(),
                self._run_compliance_tracking(),
                self._run_constitutional_alignment_check(),
                self._run_real_time_alerting(),
            ]

            await asyncio.gather(*monitoring_tasks)

        except Exception as e:
            logger.error(f"Bias drift monitoring failed: {e}")
            self.running = False
            raise
        finally:
            logger.info("Bias drift monitoring stopped")

    async def stop_monitoring(self):
        """Stop bias drift monitoring"""
        self.running = False
        logger.info("Stopping bias drift monitoring")

    async def _run_bias_monitoring_loop(self):
        """Main bias monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(self.monitoring_interval_seconds)

                if not self.running:
                    break

                # Run comprehensive bias analysis
                await self._analyze_current_bias_metrics()

                self.last_analysis_time = datetime.utcnow()

            except Exception as e:
                logger.error(f"Bias monitoring loop error: {e}")
                await asyncio.sleep(60)

    async def _analyze_current_bias_metrics(self):
        """Analyze current bias metrics across all dimensions"""
        try:
            current_time = datetime.utcnow()

            # Collect current data for bias analysis
            current_data = await self._collect_current_decision_data()
            if not current_data:
                return

            # Analyze bias for each context and protected attribute combination
            for context in BiasContext:
                for protected_attr in ProtectedAttribute:
                    # Check if we have data for this combination
                    context_data = [
                        d
                        for d in current_data
                        if d.get("context") == context.value
                        and protected_attr.value in d.get("protected_attributes", {})
                    ]

                    if len(context_data) < 10:  # Need minimum sample size
                        continue

                    # Calculate bias metrics
                    bias_results = await self._calculate_bias_metrics(
                        context, protected_attr, context_data
                    )

                    # Store results and check for drift
                    for result in bias_results:
                        self.metric_history.append(result)
                        await self._check_bias_drift(result)

        except Exception as e:
            logger.error(f"Bias metrics analysis failed: {e}")

    async def _collect_current_decision_data(self) -> list[dict[str, Any]]:
        """Collect current decision data for bias analysis"""
        try:
            # In a real implementation, this would collect actual decision data
            # For now, we'll simulate realistic decision data

            current_time = datetime.utcnow()
            simulated_data = []

            # Simulate decisions across different contexts
            contexts = list(BiasContext)

            for _ in range(100):  # Simulate 100 recent decisions
                context = np.random.choice(contexts)

                # Simulate protected attributes
                protected_attributes = {
                    "age": np.random.choice(["18-30", "31-50", "51-70", "70+"]),
                    "gender": np.random.choice(["male", "female", "non-binary"]),
                    "race_ethnicity": np.random.choice(
                        ["white", "black", "hispanic", "asian", "other"]
                    ),
                    "geographic_region": np.random.choice(
                        ["urban", "suburban", "rural"]
                    ),
                    "socioeconomic_status": np.random.choice(["low", "middle", "high"]),
                }

                # Simulate decision outcome and confidence
                # Introduce subtle bias patterns for demonstration
                bias_factor = 1.0
                if protected_attributes["race_ethnicity"] in ["black", "hispanic"]:
                    bias_factor *= 0.95  # Slight bias
                if protected_attributes["socioeconomic_status"] == "low":
                    bias_factor *= 0.97

                decision_score = np.random.normal(0.7, 0.15) * bias_factor
                decision_score = max(0, min(1, decision_score))

                data_point = {
                    "decision_id": str(uuid.uuid4()),
                    "timestamp": current_time
                    - timedelta(minutes=np.random.randint(0, 60)),
                    "context": context.value,
                    "protected_attributes": protected_attributes,
                    "decision_score": decision_score,
                    "decision_outcome": decision_score > 0.5,
                    "confidence": np.random.uniform(0.6, 0.95),
                    "features": {f"feature_{i}": np.random.normal() for i in range(10)},
                }

                simulated_data.append(data_point)

            return simulated_data

        except Exception as e:
            logger.error(f"Data collection failed: {e}")
            return []

    async def _calculate_bias_metrics(
        self,
        context: BiasContext,
        protected_attr: ProtectedAttribute,
        data: list[dict[str, Any]],
    ) -> list[BiasMetricResult]:
        """Calculate bias metrics for a specific context and protected attribute"""
        try:
            results = []

            # Group data by protected attribute values
            groups = defaultdict(list)
            for item in data:
                attr_value = item["protected_attributes"].get(
                    protected_attr.value, "unknown"
                )
                groups[attr_value].append(item)

            if len(groups) < 2:  # Need at least 2 groups for comparison
                return results

            # Calculate different bias metrics
            bias_metrics_to_calculate = [
                BiasType.DEMOGRAPHIC_PARITY,
                BiasType.EQUALIZED_ODDS,
                BiasType.CALIBRATION,
            ]

            for bias_type in bias_metrics_to_calculate:
                metric_result = await self._calculate_specific_bias_metric(
                    bias_type, context, protected_attr, groups
                )
                if metric_result:
                    results.append(metric_result)

            return results

        except Exception as e:
            logger.error(f"Bias metrics calculation failed: {e}")
            return []

    async def _calculate_specific_bias_metric(
        self,
        bias_type: BiasType,
        context: BiasContext,
        protected_attr: ProtectedAttribute,
        groups: dict[str, list[dict]],
    ) -> Optional[BiasMetricResult]:
        """Calculate a specific bias metric"""
        try:
            if bias_type == BiasType.DEMOGRAPHIC_PARITY:
                return await self._calculate_demographic_parity(
                    context, protected_attr, groups
                )
            elif bias_type == BiasType.EQUALIZED_ODDS:
                return await self._calculate_equalized_odds(
                    context, protected_attr, groups
                )
            elif bias_type == BiasType.CALIBRATION:
                return await self._calculate_calibration(
                    context, protected_attr, groups
                )
            else:
                logger.warning(f"Bias metric {bias_type.value} not implemented")
                return None

        except Exception as e:
            logger.error(
                f"Specific bias metric calculation failed for {bias_type.value}: {e}"
            )
            return None

    async def _calculate_demographic_parity(
        self,
        context: BiasContext,
        protected_attr: ProtectedAttribute,
        groups: dict[str, list[dict]],
    ) -> Optional[BiasMetricResult]:
        """Calculate demographic parity metric"""
        try:
            group_rates = {}
            group_disparities = {}

            # Calculate positive decision rate for each group
            for group_name, group_data in groups.items():
                if len(group_data) == 0:
                    continue

                positive_decisions = sum(
                    1 for item in group_data if item["decision_outcome"]
                )
                group_rates[group_name] = positive_decisions / len(group_data)

            if len(group_rates) < 2:
                return None

            # Calculate disparities
            max_rate = max(group_rates.values())
            min_rate = min(group_rates.values())

            for group_name, rate in group_rates.items():
                group_disparities[group_name] = rate - min_rate

            # Overall bias metric (max disparity)
            metric_value = max_rate - min_rate

            # Get baseline value
            baseline_key = (context, BiasType.DEMOGRAPHIC_PARITY, protected_attr)
            baseline_value = self.baseline_metrics.get(
                baseline_key, 0.02
            )  # Default baseline

            # Calculate drift
            drift_score = abs(metric_value - baseline_value)
            severity = self._determine_bias_severity(
                context, BiasType.DEMOGRAPHIC_PARITY, drift_score
            )

            # Calculate confidence interval (simplified)
            total_samples = sum(len(group_data) for group_data in groups.values())
            confidence_interval = (
                max(
                    0,
                    metric_value
                    - 1.96
                    * math.sqrt(metric_value * (1 - metric_value) / total_samples),
                ),
                min(
                    1,
                    metric_value
                    + 1.96
                    * math.sqrt(metric_value * (1 - metric_value) / total_samples),
                ),
            )

            result = BiasMetricResult(
                metric_id=str(uuid.uuid4()),
                bias_type=BiasType.DEMOGRAPHIC_PARITY,
                protected_attribute=protected_attr,
                context=context,
                metric_value=metric_value,
                baseline_value=baseline_value,
                drift_score=drift_score,
                severity=severity,
                affected_groups=list(groups.keys()),
                group_disparities=group_disparities,
                confidence_interval=confidence_interval,
                statistical_significance=(
                    0.95 if drift_score > 0.05 else 0.5
                ),  # Simplified
                timestamp=datetime.utcnow(),
            )

            return result

        except Exception as e:
            logger.error(f"Demographic parity calculation failed: {e}")
            return None

    async def _calculate_equalized_odds(
        self,
        context: BiasContext,
        protected_attr: ProtectedAttribute,
        groups: dict[str, list[dict]],
    ) -> Optional[BiasMetricResult]:
        """Calculate equalized odds metric"""
        try:
            # For equalized odds, we need true labels (ground truth)
            # In this simulation, we'll use decision_score > 0.7 as "true positive"

            group_tpr = {}  # True Positive Rate
            group_fpr = {}  # False Positive Rate
            group_disparities = {}

            for group_name, group_data in groups.items():
                if len(group_data) == 0:
                    continue

                # Simulate ground truth based on decision score
                true_positives = 0
                false_positives = 0
                true_negatives = 0
                false_negatives = 0

                for item in group_data:
                    # Ground truth: score > 0.7 is "positive"
                    true_label = item["decision_score"] > 0.7
                    predicted_label = item["decision_outcome"]

                    if true_label and predicted_label:
                        true_positives += 1
                    elif not true_label and predicted_label:
                        false_positives += 1
                    elif not true_label and not predicted_label:
                        true_negatives += 1
                    else:
                        false_negatives += 1

                # Calculate rates
                tpr = (
                    true_positives / (true_positives + false_negatives)
                    if (true_positives + false_negatives) > 0
                    else 0
                )
                fpr = (
                    false_positives / (false_positives + true_negatives)
                    if (false_positives + true_negatives) > 0
                    else 0
                )

                group_tpr[group_name] = tpr
                group_fpr[group_name] = fpr

            if len(group_tpr) < 2:
                return None

            # Calculate equalized odds violation (max difference in TPR or FPR)
            tpr_values = list(group_tpr.values())
            fpr_values = list(group_fpr.values())

            tpr_disparity = max(tpr_values) - min(tpr_values)
            fpr_disparity = max(fpr_values) - min(fpr_values)

            metric_value = max(tpr_disparity, fpr_disparity)

            # Calculate group disparities
            for group_name in groups:
                tpr_diff = group_tpr.get(group_name, 0) - min(tpr_values)
                fpr_diff = group_fpr.get(group_name, 0) - min(fpr_values)
                group_disparities[group_name] = max(tpr_diff, fpr_diff)

            # Get baseline and calculate drift
            baseline_key = (context, BiasType.EQUALIZED_ODDS, protected_attr)
            baseline_value = self.baseline_metrics.get(baseline_key, 0.03)

            drift_score = abs(metric_value - baseline_value)
            severity = self._determine_bias_severity(
                context, BiasType.EQUALIZED_ODDS, drift_score
            )

            # Simplified confidence interval
            total_samples = sum(len(group_data) for group_data in groups.values())
            confidence_interval = (
                max(0, metric_value - 0.1),
                min(1, metric_value + 0.1),
            )

            result = BiasMetricResult(
                metric_id=str(uuid.uuid4()),
                bias_type=BiasType.EQUALIZED_ODDS,
                protected_attribute=protected_attr,
                context=context,
                metric_value=metric_value,
                baseline_value=baseline_value,
                drift_score=drift_score,
                severity=severity,
                affected_groups=list(groups.keys()),
                group_disparities=group_disparities,
                confidence_interval=confidence_interval,
                statistical_significance=0.95 if drift_score > 0.05 else 0.5,
                timestamp=datetime.utcnow(),
            )

            return result

        except Exception as e:
            logger.error(f"Equalized odds calculation failed: {e}")
            return None

    async def _calculate_calibration(
        self,
        context: BiasContext,
        protected_attr: ProtectedAttribute,
        groups: dict[str, list[dict]],
    ) -> Optional[BiasMetricResult]:
        """Calculate calibration metric"""
        try:
            group_calibration_errors = {}
            group_disparities = {}

            for group_name, group_data in groups.items():
                if len(group_data) < 5:  # Need minimum samples for calibration
                    continue

                # Calculate calibration error for this group
                predicted_probs = [item["decision_score"] for item in group_data]
                actual_outcomes = [
                    1 if item["decision_outcome"] else 0 for item in group_data
                ]

                # Bin predictions and calculate calibration error
                n_bins = 5
                calibration_error = 0

                for i in range(n_bins):
                    bin_lower = i / n_bins
                    bin_upper = (i + 1) / n_bins

                    # Get predictions in this bin
                    bin_indices = [
                        j
                        for j, prob in enumerate(predicted_probs)
                        if bin_lower <= prob < bin_upper
                        or (i == n_bins - 1 and prob == 1.0)
                    ]

                    if len(bin_indices) == 0:
                        continue

                    bin_probs = [predicted_probs[j] for j in bin_indices]
                    bin_outcomes = [actual_outcomes[j] for j in bin_indices]

                    avg_predicted = statistics.mean(bin_probs)
                    avg_actual = statistics.mean(bin_outcomes)

                    bin_weight = len(bin_indices) / len(group_data)
                    calibration_error += bin_weight * abs(avg_predicted - avg_actual)

                group_calibration_errors[group_name] = calibration_error

            if len(group_calibration_errors) < 2:
                return None

            # Calculate calibration disparity
            max_error = max(group_calibration_errors.values())
            min_error = min(group_calibration_errors.values())
            metric_value = max_error - min_error

            # Calculate group disparities
            for group_name, error in group_calibration_errors.items():
                group_disparities[group_name] = error - min_error

            # Get baseline and calculate drift
            baseline_key = (context, BiasType.CALIBRATION, protected_attr)
            baseline_value = self.baseline_metrics.get(baseline_key, 0.02)

            drift_score = abs(metric_value - baseline_value)
            severity = self._determine_bias_severity(
                context, BiasType.CALIBRATION, drift_score
            )

            # Simplified confidence interval
            confidence_interval = (
                max(0, metric_value - 0.05),
                min(1, metric_value + 0.05),
            )

            result = BiasMetricResult(
                metric_id=str(uuid.uuid4()),
                bias_type=BiasType.CALIBRATION,
                protected_attribute=protected_attr,
                context=context,
                metric_value=metric_value,
                baseline_value=baseline_value,
                drift_score=drift_score,
                severity=severity,
                affected_groups=list(groups.keys()),
                group_disparities=group_disparities,
                confidence_interval=confidence_interval,
                statistical_significance=0.95 if drift_score > 0.03 else 0.5,
                timestamp=datetime.utcnow(),
            )

            return result

        except Exception as e:
            logger.error(f"Calibration calculation failed: {e}")
            return None

    def _determine_bias_severity(
        self, context: BiasContext, bias_type: BiasType, drift_score: float
    ) -> BiasSeverity:
        """Determine bias severity based on context and drift score"""
        # Get thresholds for this context and bias type
        context_thresholds = self.bias_thresholds.get(context, {})
        thresholds = context_thresholds.get(
            bias_type, self.default_thresholds[bias_type]
        )

        if drift_score >= thresholds["critical"]:
            return BiasSeverity.CRITICAL
        elif drift_score >= thresholds["high"]:
            return BiasSeverity.HIGH
        elif drift_score >= thresholds["medium"]:
            return BiasSeverity.MEDIUM
        elif drift_score >= thresholds["low"]:
            return BiasSeverity.LOW
        else:
            return BiasSeverity.NONE

    async def _check_bias_drift(self, result: BiasMetricResult):
        """Check for bias drift and handle accordingly"""
        try:
            if result.severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]:
                # Create and handle bias drift alert
                alert = await self._create_bias_drift_alert([result])
                await self._handle_bias_drift_alert(alert)

            # Update temporal patterns
            pattern_key = f"{result.context.value}_{result.bias_type.value}_{result.protected_attribute.value}"
            self.temporal_patterns[pattern_key].append(
                {
                    "timestamp": result.timestamp,
                    "metric_value": result.metric_value,
                    "drift_score": result.drift_score,
                    "severity": result.severity.value,
                }
            )

            # Keep only recent patterns (last 30 days)
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            self.temporal_patterns[pattern_key] = [
                p
                for p in self.temporal_patterns[pattern_key]
                if p["timestamp"] >= cutoff_time
            ]

            # Log bias metric
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "bias_metric_calculated",
                    "metric_id": result.metric_id,
                    "bias_type": result.bias_type.value,
                    "protected_attribute": result.protected_attribute.value,
                    "context": result.context.value,
                    "metric_value": result.metric_value,
                    "drift_score": result.drift_score,
                    "severity": result.severity.value,
                    "affected_groups": result.affected_groups,
                    "timestamp": result.timestamp.isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Bias drift check failed: {e}")

    async def _create_bias_drift_alert(
        self, affected_metrics: list[BiasMetricResult]
    ) -> BiasDriftAlert:
        """Create bias drift alert from affected metrics"""
        try:
            # Determine overall severity
            max_severity = max(metric.severity for metric in affected_metrics)

            # Analyze temporal patterns
            temporal_pattern = await self._analyze_temporal_bias_pattern(
                affected_metrics
            )

            # Perform root cause analysis
            root_causes = await self._analyze_bias_root_causes(affected_metrics)

            # Generate recommendations
            recommendations = await self._generate_bias_mitigation_recommendations(
                affected_metrics
            )

            # Determine stakeholders
            stakeholders = self._determine_bias_alert_stakeholders(
                affected_metrics, max_severity
            )

            # Assess regulatory implications
            regulatory_implications = self._assess_regulatory_implications(
                affected_metrics
            )

            alert = BiasDriftAlert(
                alert_id=str(uuid.uuid4()),
                drift_type=f"bias_drift_{max_severity.value}",
                severity=max_severity,
                affected_metrics=affected_metrics,
                temporal_pattern=temporal_pattern,
                root_cause_analysis=root_causes,
                recommended_actions=recommendations,
                stakeholders=stakeholders,
                regulatory_implications=regulatory_implications,
                timestamp=datetime.utcnow(),
            )

            return alert

        except Exception as e:
            logger.error(f"Bias drift alert creation failed: {e}")
            # Return minimal alert
            return BiasDriftAlert(
                alert_id=str(uuid.uuid4()),
                drift_type="bias_drift_unknown",
                severity=BiasSeverity.MEDIUM,
                affected_metrics=affected_metrics,
                temporal_pattern={},
                root_cause_analysis=["Unknown cause"],
                recommended_actions=["Investigate bias metrics"],
                stakeholders=["ml_team"],
                regulatory_implications=["Review required"],
                timestamp=datetime.utcnow(),
            )

    async def _analyze_temporal_bias_pattern(
        self, metrics: list[BiasMetricResult]
    ) -> dict[str, Any]:
        """Analyze temporal patterns in bias metrics"""
        try:
            pattern_analysis = {
                "trend_direction": "stable",
                "acceleration": 0.0,
                "periodicity": None,
                "volatility": 0.0,
                "time_to_threshold": None,
            }

            if not metrics:
                return pattern_analysis

            # Get historical data for the same metric types
            metric_key = f"{metrics[0].context.value}_{metrics[0].bias_type.value}_{metrics[0].protected_attribute.value}"
            historical_data = self.temporal_patterns.get(metric_key, [])

            if len(historical_data) < 3:
                return pattern_analysis

            # Analyze trend
            recent_values = [p["metric_value"] for p in historical_data[-10:]]
            if len(recent_values) >= 3:
                # Simple linear trend analysis
                x = list(range(len(recent_values)))
                slope = self._calculate_trend_slope(x, recent_values)

                if slope > 0.01:
                    pattern_analysis["trend_direction"] = "increasing"
                elif slope < -0.01:
                    pattern_analysis["trend_direction"] = "decreasing"

                pattern_analysis["acceleration"] = slope

            # Calculate volatility
            if len(recent_values) > 1:
                pattern_analysis["volatility"] = statistics.stdev(recent_values)

            return pattern_analysis

        except Exception as e:
            logger.error(f"Temporal pattern analysis failed: {e}")
            return {"trend_direction": "unknown"}

    def _calculate_trend_slope(self, x: list[float], y: list[float]) -> float:
        """Calculate trend slope using simple linear regression"""
        try:
            n = len(x)
            if n < 2:
                return 0.0

            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
            return slope

        except Exception:
            return 0.0

    async def _analyze_bias_root_causes(
        self, metrics: list[BiasMetricResult]
    ) -> list[str]:
        """Analyze potential root causes of bias drift"""
        try:
            root_causes = []

            # Analyze affected groups
            all_affected_groups = set()
            for metric in metrics:
                all_affected_groups.update(metric.affected_groups)

            # Check for systematic patterns
            if len(all_affected_groups) > 2:
                root_causes.append(
                    "Systematic bias affecting multiple demographic groups"
                )

            # Check bias types
            bias_types = set(metric.bias_type for metric in metrics)
            if (
                BiasType.DEMOGRAPHIC_PARITY in bias_types
                and BiasType.EQUALIZED_ODDS in bias_types
            ):
                root_causes.append(
                    "Both representation and performance disparities detected"
                )

            # Check contexts
            contexts = set(metric.context for metric in metrics)
            if len(contexts) > 1:
                root_causes.append("Cross-context bias indicating systemic issues")

            # Check severity levels
            high_severity_metrics = [
                m
                for m in metrics
                if m.severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]
            ]
            if len(high_severity_metrics) > 2:
                root_causes.append(
                    "Multiple high-severity bias violations suggest training data"
                    " issues"
                )

            # Default causes if none identified
            if not root_causes:
                root_causes = [
                    "Training data imbalance or bias",
                    "Model architecture bias amplification",
                    "Feature selection bias",
                ]

            return root_causes

        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            return ["Unknown bias sources"]

    async def _generate_bias_mitigation_recommendations(
        self, metrics: list[BiasMetricResult]
    ) -> list[str]:
        """Generate bias mitigation recommendations"""
        try:
            recommendations = []

            # Severity-based recommendations
            critical_metrics = [
                m for m in metrics if m.severity == BiasSeverity.CRITICAL
            ]
            if critical_metrics:
                recommendations.extend(
                    [
                        "URGENT: Halt automated decisions for affected groups",
                        "Implement immediate human oversight for all decisions",
                        "Conduct emergency bias audit",
                        "Consider model rollback to previous version",
                    ]
                )

            high_severity_metrics = [
                m for m in metrics if m.severity == BiasSeverity.HIGH
            ]
            if high_severity_metrics:
                recommendations.extend(
                    [
                        "Increase human review rate for affected demographic groups",
                        "Implement bias-aware post-processing",
                        "Review and retrain model with fairness constraints",
                        "Enhanced monitoring for affected groups",
                    ]
                )

            # Bias type specific recommendations
            bias_types = set(metric.bias_type for metric in metrics)

            if BiasType.DEMOGRAPHIC_PARITY in bias_types:
                recommendations.extend(
                    [
                        "Implement demographic parity constraints in model training",
                        "Review data sampling strategies for balanced representation",
                        "Consider fair representation learning techniques",
                    ]
                )

            if BiasType.EQUALIZED_ODDS in bias_types:
                recommendations.extend(
                    [
                        "Implement equalized odds post-processing",
                        "Review threshold optimization across groups",
                        "Consider adversarial debiasing techniques",
                    ]
                )

            if BiasType.CALIBRATION in bias_types:
                recommendations.extend(
                    [
                        "Implement group-specific calibration",
                        "Review confidence score reliability across groups",
                        "Consider Platt scaling for each demographic group",
                    ]
                )

            # Constitutional AI specific recommendations
            recommendations.extend(
                [
                    "Review constitutional principle alignment",
                    "Engage ethics committee for bias assessment",
                    "Update constitutional AI training with fairness examples",
                    "Implement principle-based bias detection",
                ]
            )

            # General recommendations
            recommendations.extend(
                [
                    "Document bias incident for compliance reporting",
                    "Schedule bias audit with external evaluators",
                    "Update bias monitoring thresholds based on findings",
                    "Provide bias awareness training to human reviewers",
                ]
            )

            return list(set(recommendations))  # Remove duplicates

        except Exception as e:
            logger.error(f"Bias mitigation recommendations failed: {e}")
            return ["Conduct comprehensive bias review"]

    def _determine_bias_alert_stakeholders(
        self, metrics: list[BiasMetricResult], severity: BiasSeverity
    ) -> list[str]:
        """Determine stakeholders for bias alert"""
        stakeholders = ["ml_team", "fairness_team", "compliance_team"]

        if severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]:
            stakeholders.extend(["legal_team", "ethics_committee", "executive_team"])

        # Context-specific stakeholders
        contexts = set(metric.context for metric in metrics)
        if BiasContext.CONSTITUTIONAL_ANALYSIS in contexts:
            stakeholders.append("constitutional_experts")
        if BiasContext.POLICY_RECOMMENDATION in contexts:
            stakeholders.append("policy_team")
        if BiasContext.LEGAL_INTERPRETATION in contexts:
            stakeholders.append("legal_specialists")

        return list(set(stakeholders))

    def _assess_regulatory_implications(
        self, metrics: list[BiasMetricResult]
    ) -> list[str]:
        """Assess regulatory implications of bias drift"""
        implications = []

        # Check severity
        critical_metrics = [m for m in metrics if m.severity == BiasSeverity.CRITICAL]
        if critical_metrics:
            implications.extend(
                [
                    "EU AI Act Article 10 compliance violation (data governance)",
                    "Potential discrimination law violations",
                    "Regulatory reporting required within 72 hours",
                ]
            )

        high_severity_metrics = [m for m in metrics if m.severity == BiasSeverity.HIGH]
        if high_severity_metrics:
            implications.extend(
                [
                    "EU AI Act compliance review required",
                    "Fair Credit Reporting Act implications (if applicable)",
                    "Equal Protection Clause considerations",
                ]
            )

        # Context-specific implications
        contexts = set(metric.context for metric in metrics)
        if BiasContext.RESOURCE_ALLOCATION in contexts:
            implications.append("Equal protection under law implications")
        if BiasContext.DEMOCRATIC_PARTICIPATION in contexts:
            implications.append("Voting Rights Act considerations")

        return implications

    async def _handle_bias_drift_alert(self, alert: BiasDriftAlert):
        """Handle bias drift alert with logging and notifications"""
        try:
            # Store alert
            self.drift_alerts[alert.alert_id] = alert

            # Send alert notification
            alert_severity = {
                BiasSeverity.LOW: "low",
                BiasSeverity.MEDIUM: "medium",
                BiasSeverity.HIGH: "high",
                BiasSeverity.CRITICAL: "critical",
            }[alert.severity]

            await self.alerting.send_alert(
                f"bias_drift_{alert.drift_type}",
                f"Bias drift detected: {len(alert.affected_metrics)} metrics affected,"
                f" severity {alert.severity.value}",
                severity=alert_severity,
            )

            # Log comprehensive alert information
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "bias_drift_alert",
                    "alert_id": alert.alert_id,
                    "drift_type": alert.drift_type,
                    "severity": alert.severity.value,
                    "affected_metrics_count": len(alert.affected_metrics),
                    "affected_bias_types": list(
                        set(m.bias_type.value for m in alert.affected_metrics)
                    ),
                    "affected_attributes": list(
                        set(m.protected_attribute.value for m in alert.affected_metrics)
                    ),
                    "affected_contexts": list(
                        set(m.context.value for m in alert.affected_metrics)
                    ),
                    "root_causes": alert.root_cause_analysis,
                    "recommended_actions": alert.recommended_actions,
                    "regulatory_implications": alert.regulatory_implications,
                    "stakeholders": alert.stakeholders,
                    "timestamp": alert.timestamp.isoformat(),
                }
            )

            # Log individual metric details
            for metric in alert.affected_metrics:
                await self.audit_logger.log_compliance_event(
                    {
                        "event_type": "bias_metric_alert_detail",
                        "alert_id": alert.alert_id,
                        "metric_id": metric.metric_id,
                        "bias_type": metric.bias_type.value,
                        "protected_attribute": metric.protected_attribute.value,
                        "context": metric.context.value,
                        "metric_value": metric.metric_value,
                        "baseline_value": metric.baseline_value,
                        "drift_score": metric.drift_score,
                        "severity": metric.severity.value,
                        "affected_groups": metric.affected_groups,
                        "group_disparities": metric.group_disparities,
                        "statistical_significance": metric.statistical_significance,
                        "timestamp": metric.timestamp.isoformat(),
                    }
                )

        except Exception as e:
            logger.error(f"Bias drift alert handling failed: {e}")

    async def _run_intersectional_analysis(self):
        """Run intersectional bias analysis"""
        while self.running:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes

                if not self.running:
                    break

                if self.intersectional_analysis_enabled:
                    await self._perform_intersectional_analysis()

            except Exception as e:
                logger.error(f"Intersectional analysis error: {e}")
                await asyncio.sleep(300)

    async def _perform_intersectional_analysis(self):
        """Perform intersectional bias analysis"""
        try:
            # Get recent decision data
            current_data = await self._collect_current_decision_data()
            if len(current_data) < 50:
                return

            # Define intersectional combinations to analyze
            attribute_combinations = [
                (ProtectedAttribute.RACE_ETHNICITY, ProtectedAttribute.GENDER),
                (ProtectedAttribute.AGE, ProtectedAttribute.SOCIOECONOMIC_STATUS),
                (ProtectedAttribute.GENDER, ProtectedAttribute.SOCIOECONOMIC_STATUS),
                (
                    ProtectedAttribute.RACE_ETHNICITY,
                    ProtectedAttribute.GEOGRAPHIC_REGION,
                ),
                (
                    ProtectedAttribute.AGE,
                    ProtectedAttribute.GENDER,
                    ProtectedAttribute.RACE_ETHNICITY,
                ),
            ]

            bias_interactions = {}
            amplification_factors = {}

            for combination in attribute_combinations:
                interaction_analysis = await self._analyze_attribute_interaction(
                    current_data, combination
                )
                if interaction_analysis:
                    combo_key = "_".join([attr.value for attr in combination])
                    bias_interactions[combo_key] = interaction_analysis[
                        "interaction_strength"
                    ]
                    amplification_factors[combo_key] = interaction_analysis[
                        "amplification_factor"
                    ]

            if bias_interactions:
                # Create intersectional analysis result
                analysis = IntersectionalBiasAnalysis(
                    analysis_id=str(uuid.uuid4()),
                    attribute_combinations=attribute_combinations,
                    bias_interactions=bias_interactions,
                    amplification_factors=amplification_factors,
                    mitigation_complexity=self._calculate_mitigation_complexity(
                        bias_interactions
                    ),
                    priority_combinations=self._prioritize_intersectional_combinations(
                        attribute_combinations, bias_interactions, amplification_factors
                    ),
                    timestamp=datetime.utcnow(),
                )

                await self._handle_intersectional_analysis(analysis)

        except Exception as e:
            logger.error(f"Intersectional analysis failed: {e}")

    async def _analyze_attribute_interaction(
        self, data: list[dict[str, Any]], attributes: tuple[ProtectedAttribute, ...]
    ) -> Optional[dict[str, float]]:
        """Analyze interaction between multiple protected attributes"""
        try:
            # Group data by intersectional categories
            intersectional_groups = defaultdict(list)

            for item in data:
                protected_attrs = item.get("protected_attributes", {})

                # Create intersectional group key
                group_values = []
                for attr in attributes:
                    value = protected_attrs.get(attr.value, "unknown")
                    group_values.append(value)

                group_key = "_".join(group_values)
                intersectional_groups[group_key].append(item)

            # Filter groups with minimum sample size
            valid_groups = {
                k: v for k, v in intersectional_groups.items() if len(v) >= 5
            }

            if len(valid_groups) < 2:
                return None

            # Calculate bias for intersectional groups
            group_rates = {}
            for group_key, group_data in valid_groups.items():
                positive_decisions = sum(
                    1 for item in group_data if item["decision_outcome"]
                )
                group_rates[group_key] = positive_decisions / len(group_data)

            # Calculate interaction strength
            max_rate = max(group_rates.values())
            min_rate = min(group_rates.values())
            interaction_strength = max_rate - min_rate

            # Calculate amplification factor (compared to individual attribute bias)
            individual_biases = []
            for attr in attributes:
                attr_groups = defaultdict(list)
                for item in data:
                    attr_value = item["protected_attributes"].get(attr.value, "unknown")
                    attr_groups[attr_value].append(item)

                if len(attr_groups) >= 2:
                    attr_rates = {}
                    for attr_group_key, attr_group_data in attr_groups.items():
                        if len(attr_group_data) >= 5:
                            positive = sum(
                                1
                                for item in attr_group_data
                                if item["decision_outcome"]
                            )
                            attr_rates[attr_group_key] = positive / len(attr_group_data)

                    if len(attr_rates) >= 2:
                        attr_bias = max(attr_rates.values()) - min(attr_rates.values())
                        individual_biases.append(attr_bias)

            # Calculate amplification factor
            max_individual_bias = max(individual_biases) if individual_biases else 0.01
            amplification_factor = (
                interaction_strength / max_individual_bias
                if max_individual_bias > 0
                else 1.0
            )

            return {
                "interaction_strength": interaction_strength,
                "amplification_factor": amplification_factor,
                "group_count": len(valid_groups),
                "sample_size": sum(
                    len(group_data) for group_data in valid_groups.values()
                ),
            }

        except Exception as e:
            logger.error(f"Attribute interaction analysis failed: {e}")
            return None

    def _calculate_mitigation_complexity(
        self, bias_interactions: dict[str, float]
    ) -> float:
        """Calculate complexity of bias mitigation"""
        try:
            if not bias_interactions:
                return 0.0

            # Complexity increases with number of interactions and their strength
            num_interactions = len(bias_interactions)
            avg_interaction_strength = statistics.mean(bias_interactions.values())
            max_interaction_strength = max(bias_interactions.values())

            # Normalized complexity score
            complexity = (
                (num_interactions / 10) * 0.4
                + avg_interaction_strength * 0.3
                + max_interaction_strength * 0.3
            )

            return min(1.0, complexity)

        except Exception:
            return 0.5

    def _prioritize_intersectional_combinations(
        self,
        combinations: list[tuple[ProtectedAttribute, ...]],
        interactions: dict[str, float],
        amplifications: dict[str, float],
    ) -> list[tuple[ProtectedAttribute, ...]]:
        """Prioritize intersectional combinations by severity"""
        try:
            # Score each combination
            combination_scores = []

            for combination in combinations:
                combo_key = "_".join([attr.value for attr in combination])
                interaction_score = interactions.get(combo_key, 0)
                amplification_score = amplifications.get(combo_key, 1)

                # Combined priority score
                priority_score = interaction_score * amplification_score
                combination_scores.append((combination, priority_score))

            # Sort by priority score (descending)
            combination_scores.sort(key=lambda x: x[1], reverse=True)

            return [combo for combo, score in combination_scores]

        except Exception:
            return combinations

    async def _handle_intersectional_analysis(
        self, analysis: IntersectionalBiasAnalysis
    ):
        """Handle intersectional analysis results"""
        try:
            # Log intersectional analysis
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "intersectional_bias_analysis",
                    "analysis_id": analysis.analysis_id,
                    "attribute_combinations": [
                        [attr.value for attr in combo]
                        for combo in analysis.attribute_combinations
                    ],
                    "bias_interactions": analysis.bias_interactions,
                    "amplification_factors": analysis.amplification_factors,
                    "mitigation_complexity": analysis.mitigation_complexity,
                    "priority_combinations": [
                        [attr.value for attr in combo]
                        for combo in analysis.priority_combinations
                    ],
                    "timestamp": analysis.timestamp.isoformat(),
                }
            )

            # Alert on high-severity intersectional bias
            high_interactions = [
                (combo, score)
                for combo, score in analysis.bias_interactions.items()
                if score > 0.15
            ]

            if high_interactions:
                await self.alerting.send_alert(
                    "intersectional_bias_detected",
                    "High intersectional bias detected:"
                    f" {len(high_interactions)} combinations affected",
                    severity="high",
                )

        except Exception as e:
            logger.error(f"Intersectional analysis handling failed: {e}")

    async def _run_pattern_detection(self):
        """Run bias pattern detection"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Run every hour

                if not self.running:
                    break

                await self._detect_bias_patterns()

            except Exception as e:
                logger.error(f"Pattern detection error: {e}")
                await asyncio.sleep(300)

    async def _detect_bias_patterns(self):
        """Detect patterns in bias metrics"""
        try:
            # Analyze temporal patterns across all metrics
            patterns_detected = []

            for pattern_key, pattern_data in self.temporal_patterns.items():
                if len(pattern_data) < 10:  # Need minimum data points
                    continue

                # Detect different types of patterns
                temporal_pattern = await self._detect_temporal_bias_pattern(
                    pattern_key, pattern_data
                )
                if temporal_pattern:
                    patterns_detected.append(temporal_pattern)

            # Store and analyze patterns
            for pattern in patterns_detected:
                self.bias_patterns.append(pattern)
                await self._analyze_bias_pattern_significance(pattern)

        except Exception as e:
            logger.error(f"Bias pattern detection failed: {e}")

    async def _detect_temporal_bias_pattern(
        self, pattern_key: str, pattern_data: list[dict]
    ) -> Optional[BiasPattern]:
        """Detect temporal bias patterns"""
        try:
            # Extract values and timestamps
            values = [p["metric_value"] for p in pattern_data]
            timestamps = [p["timestamp"] for p in pattern_data]

            # Detect trend
            trend_slope = self._calculate_trend_slope(list(range(len(values))), values)

            # Detect volatility
            volatility = statistics.stdev(values) if len(values) > 1 else 0

            # Detect periodicity (simplified)
            has_periodicity = False
            if len(values) >= 24:  # Need enough data for period detection
                # Simple check for weekly patterns
                weekly_groups = defaultdict(list)
                for i, timestamp in enumerate(timestamps):
                    weekday = timestamp.weekday()
                    weekly_groups[weekday].append(values[i])

                weekday_means = {
                    k: statistics.mean(v)
                    for k, v in weekly_groups.items()
                    if len(v) > 1
                }
                if len(weekday_means) >= 3:
                    weekday_variance = statistics.variance(list(weekday_means.values()))
                    if (
                        weekday_variance > 0.01
                    ):  # Threshold for meaningful weekly pattern
                        has_periodicity = True

            # Determine pattern significance
            pattern_context, bias_type, protected_attr = pattern_key.split("_", 2)

            # Create pattern if significant
            if abs(trend_slope) > 0.01 or volatility > 0.05 or has_periodicity:
                pattern_type = "temporal_bias_pattern"
                if abs(trend_slope) > 0.01:
                    pattern_type += "_trending"
                if volatility > 0.05:
                    pattern_type += "_volatile"
                if has_periodicity:
                    pattern_type += "_periodic"

                description = (
                    f"Bias pattern detected in {pattern_context} for {protected_attr}"
                )
                if trend_slope > 0.01:
                    description += " (increasing trend)"
                elif trend_slope < -0.01:
                    description += " (decreasing trend)"
                if volatility > 0.05:
                    description += " (high volatility)"
                if has_periodicity:
                    description += " (weekly periodicity)"

                # Determine risk level
                risk_level = BiasSeverity.LOW
                if abs(trend_slope) > 0.05 or volatility > 0.15:
                    risk_level = BiasSeverity.MEDIUM
                if abs(trend_slope) > 0.10 or volatility > 0.25:
                    risk_level = BiasSeverity.HIGH

                pattern = BiasPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=pattern_type,
                    description=description,
                    affected_attributes=[ProtectedAttribute(protected_attr)],
                    temporal_characteristics={
                        "trend_slope": trend_slope,
                        "volatility": volatility,
                        "has_periodicity": has_periodicity,
                        "data_points": len(values),
                        "time_span_days": (
                            (timestamps[-1] - timestamps[0]).days
                            if len(timestamps) > 1
                            else 0
                        ),
                    },
                    predictive_indicators=self._generate_predictive_indicators(
                        trend_slope, volatility, has_periodicity
                    ),
                    mitigation_strategies=self._generate_pattern_mitigation_strategies(
                        pattern_type, trend_slope, volatility
                    ),
                    confidence=self._calculate_pattern_confidence(
                        len(values), trend_slope, volatility
                    ),
                    risk_level=risk_level,
                )

                return pattern

            return None

        except Exception as e:
            logger.error(f"Temporal bias pattern detection failed: {e}")
            return None

    def _generate_predictive_indicators(
        self, trend_slope: float, volatility: float, has_periodicity: bool
    ) -> list[str]:
        """Generate predictive indicators for bias patterns"""
        indicators = []

        if trend_slope > 0.02:
            indicators.append("Bias likely to continue increasing")
        elif trend_slope < -0.02:
            indicators.append("Bias decreasing but may rebound")

        if volatility > 0.10:
            indicators.append("High unpredictability in bias levels")
            indicators.append("Frequent monitoring required")

        if has_periodicity:
            indicators.append("Bias follows predictable weekly pattern")
            indicators.append("Resource planning can account for pattern")

        return indicators

    def _generate_pattern_mitigation_strategies(
        self, pattern_type: str, trend_slope: float, volatility: float
    ) -> list[str]:
        """Generate mitigation strategies for bias patterns"""
        strategies = []

        if "trending" in pattern_type:
            if trend_slope > 0:
                strategies.extend(
                    [
                        "Implement immediate bias correction measures",
                        "Review recent model changes for bias introduction",
                        "Increase human oversight until trend reverses",
                    ]
                )
            else:
                strategies.extend(
                    [
                        "Monitor for bias rebound",
                        "Document successful bias reduction methods",
                        "Maintain current mitigation measures",
                    ]
                )

        if "volatile" in pattern_type:
            strategies.extend(
                [
                    "Implement bias smoothing techniques",
                    "Increase monitoring frequency",
                    "Review environmental factors causing volatility",
                    "Consider ensemble methods for stability",
                ]
            )

        if "periodic" in pattern_type:
            strategies.extend(
                [
                    "Adjust human oversight schedules to match pattern",
                    "Implement time-aware bias correction",
                    "Investigate underlying causes of periodicity",
                ]
            )

        return strategies

    def _calculate_pattern_confidence(
        self, data_points: int, trend_slope: float, volatility: float
    ) -> float:
        """Calculate confidence in pattern detection"""
        try:
            # Base confidence on data quantity
            data_confidence = min(
                1.0, data_points / 30
            )  # Full confidence at 30+ points

            # Adjust for signal strength
            signal_strength = abs(trend_slope) + (
                1 / (1 + volatility)
            )  # Strong trend or low volatility = strong signal
            signal_confidence = min(1.0, signal_strength / 0.5)

            # Combined confidence
            confidence = (data_confidence + signal_confidence) / 2

            return confidence

        except Exception:
            return 0.5

    async def _analyze_bias_pattern_significance(self, pattern: BiasPattern):
        """Analyze significance of detected bias pattern"""
        try:
            # Log pattern detection
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "bias_pattern_detected",
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "description": pattern.description,
                    "affected_attributes": [
                        attr.value for attr in pattern.affected_attributes
                    ],
                    "risk_level": pattern.risk_level.value,
                    "confidence": pattern.confidence,
                    "temporal_characteristics": pattern.temporal_characteristics,
                    "predictive_indicators": pattern.predictive_indicators,
                    "mitigation_strategies": pattern.mitigation_strategies,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Alert on high-risk patterns
            if (
                pattern.risk_level in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]
                and pattern.confidence > 0.7
            ):
                await self.alerting.send_alert(
                    f"bias_pattern_{pattern.pattern_type}",
                    f"High-risk bias pattern detected: {pattern.description}",
                    severity="high",
                )

        except Exception as e:
            logger.error(f"Pattern significance analysis failed: {e}")

    async def _run_compliance_tracking(self):
        """Run fairness compliance tracking"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Run every hour

                if not self.running:
                    break

                await self._assess_fairness_compliance()

            except Exception as e:
                logger.error(f"Compliance tracking error: {e}")
                await asyncio.sleep(300)

    async def _assess_fairness_compliance(self):
        """Assess overall fairness compliance"""
        try:
            # Assess compliance for each context
            for context in BiasContext:
                compliance = await self._calculate_context_compliance(context)
                if compliance:
                    self.compliance_history.append(compliance)
                    await self._handle_compliance_assessment(compliance)

        except Exception as e:
            logger.error(f"Fairness compliance assessment failed: {e}")

    async def _calculate_context_compliance(
        self, context: BiasContext
    ) -> Optional[FairnessCompliance]:
        """Calculate fairness compliance for a specific context"""
        try:
            # Get recent metrics for this context
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            context_metrics = [
                metric
                for metric in self.metric_history
                if metric.context == context and metric.timestamp >= recent_cutoff
            ]

            if not context_metrics:
                return None

            # Calculate metric compliance
            metric_compliance = {}
            for bias_type in BiasType:
                type_metrics = [m for m in context_metrics if m.bias_type == bias_type]
                if type_metrics:
                    # Check if any metrics exceed thresholds
                    compliant = all(
                        m.severity in [BiasSeverity.NONE, BiasSeverity.LOW]
                        for m in type_metrics
                    )
                    metric_compliance[bias_type] = compliant

            # Calculate protected group compliance
            protected_group_compliance = {}
            for protected_attr in ProtectedAttribute:
                attr_metrics = [
                    m
                    for m in context_metrics
                    if m.protected_attribute == protected_attr
                ]
                if attr_metrics:
                    compliant = all(
                        m.severity in [BiasSeverity.NONE, BiasSeverity.LOW]
                        for m in attr_metrics
                    )
                    protected_group_compliance[protected_attr] = compliant

            # Calculate overall fairness score
            all_compliant = list(metric_compliance.values()) + list(
                protected_group_compliance.values()
            )
            overall_fairness_score = (
                sum(all_compliant) / len(all_compliant) if all_compliant else 0
            )

            # Calculate constitutional alignment
            constitutional_alignment = await self._calculate_constitutional_alignment(
                context_metrics
            )

            # Calculate regulatory compliance
            regulatory_compliance = {
                "eu_ai_act": overall_fairness_score > 0.8,
                "equal_protection": all(protected_group_compliance.values()),
                "civil_rights": overall_fairness_score > 0.9,
            }

            # Generate improvement recommendations
            improvement_recommendations = (
                await self._generate_compliance_recommendations(
                    context,
                    metric_compliance,
                    protected_group_compliance,
                    overall_fairness_score,
                )
            )

            compliance = FairnessCompliance(
                compliance_id=str(uuid.uuid4()),
                context=context,
                overall_fairness_score=overall_fairness_score,
                metric_compliance=metric_compliance,
                protected_group_compliance=protected_group_compliance,
                constitutional_alignment=constitutional_alignment,
                regulatory_compliance=regulatory_compliance,
                improvement_recommendations=improvement_recommendations,
                timestamp=datetime.utcnow(),
            )

            return compliance

        except Exception as e:
            logger.error(f"Context compliance calculation failed: {e}")
            return None

    async def _calculate_constitutional_alignment(
        self, metrics: list[BiasMetricResult]
    ) -> float:
        """Calculate alignment with constitutional fairness principles"""
        try:
            # Score alignment with each constitutional principle
            principle_scores = {}

            # Equal protection
            equal_protection_violations = sum(
                1
                for metric in metrics
                if metric.severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]
            )
            principle_scores["equal_protection"] = max(
                0, 1 - (equal_protection_violations / len(metrics))
            )

            # Due process (approximated by calibration and fairness)
            calibration_metrics = [
                m for m in metrics if m.bias_type == BiasType.CALIBRATION
            ]
            if calibration_metrics:
                due_process_score = statistics.mean(
                    [1 - m.drift_score for m in calibration_metrics]
                )
                principle_scores["due_process"] = max(0, min(1, due_process_score))
            else:
                principle_scores["due_process"] = 0.8  # Default if no calibration data

            # Non-discrimination
            demographic_parity_metrics = [
                m for m in metrics if m.bias_type == BiasType.DEMOGRAPHIC_PARITY
            ]
            if demographic_parity_metrics:
                non_discrimination_score = statistics.mean(
                    [1 - m.drift_score for m in demographic_parity_metrics]
                )
                principle_scores["non_discrimination"] = max(
                    0, min(1, non_discrimination_score)
                )
            else:
                principle_scores["non_discrimination"] = 0.8

            # Overall constitutional alignment
            alignment = statistics.mean(principle_scores.values())

            return alignment

        except Exception:
            return 0.5

    async def _generate_compliance_recommendations(
        self,
        context: BiasContext,
        metric_compliance: dict[BiasType, bool],
        group_compliance: dict[ProtectedAttribute, bool],
        overall_score: float,
    ) -> list[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []

        # Overall score recommendations
        if overall_score < 0.7:
            recommendations.append("URGENT: Comprehensive bias audit required")
            recommendations.append("Consider suspending automated decisions")
        elif overall_score < 0.8:
            recommendations.append("Enhanced bias monitoring required")
            recommendations.append("Increase human oversight")

        # Metric-specific recommendations
        for bias_type, compliant in metric_compliance.items():
            if not compliant:
                if bias_type == BiasType.DEMOGRAPHIC_PARITY:
                    recommendations.append("Implement demographic parity constraints")
                elif bias_type == BiasType.EQUALIZED_ODDS:
                    recommendations.append(
                        "Review threshold optimization across groups"
                    )
                elif bias_type == BiasType.CALIBRATION:
                    recommendations.append("Implement group-specific calibration")

        # Group-specific recommendations
        non_compliant_groups = [
            attr for attr, compliant in group_compliance.items() if not compliant
        ]
        if non_compliant_groups:
            group_names = [attr.value for attr in non_compliant_groups]
            recommendations.append(
                f"Focus bias mitigation on: {', '.join(group_names)}"
            )

        # Context-specific recommendations
        if context == BiasContext.CONSTITUTIONAL_ANALYSIS:
            recommendations.append("Review constitutional principle alignment")
        elif context == BiasContext.POLICY_RECOMMENDATION:
            recommendations.append("Engage policy stakeholders for bias review")

        return recommendations

    async def _handle_compliance_assessment(self, compliance: FairnessCompliance):
        """Handle fairness compliance assessment"""
        try:
            # Log compliance assessment
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "fairness_compliance_assessment",
                    "compliance_id": compliance.compliance_id,
                    "context": compliance.context.value,
                    "overall_fairness_score": compliance.overall_fairness_score,
                    "metric_compliance": {
                        k.value: v for k, v in compliance.metric_compliance.items()
                    },
                    "protected_group_compliance": {
                        k.value: v
                        for k, v in compliance.protected_group_compliance.items()
                    },
                    "constitutional_alignment": compliance.constitutional_alignment,
                    "regulatory_compliance": compliance.regulatory_compliance,
                    "improvement_recommendations": compliance.improvement_recommendations,
                    "timestamp": compliance.timestamp.isoformat(),
                }
            )

            # Alert on poor compliance
            if compliance.overall_fairness_score < 0.7:
                await self.alerting.send_alert(
                    f"poor_fairness_compliance_{compliance.context.value}",
                    f"Poor fairness compliance in {compliance.context.value}:"
                    f" {compliance.overall_fairness_score:.2%}",
                    severity="high",
                )

        except Exception as e:
            logger.error(f"Compliance assessment handling failed: {e}")

    async def _run_constitutional_alignment_check(self):
        """Run constitutional alignment checks"""
        while self.running:
            try:
                await asyncio.sleep(7200)  # Run every 2 hours

                if not self.running:
                    break

                await self._check_constitutional_alignment()

            except Exception as e:
                logger.error(f"Constitutional alignment check error: {e}")
                await asyncio.sleep(600)

    async def _check_constitutional_alignment(self):
        """Check alignment with constitutional principles"""
        try:
            # Get recent metrics across all contexts
            recent_cutoff = datetime.utcnow() - timedelta(hours=6)
            recent_metrics = [
                metric
                for metric in self.metric_history
                if metric.timestamp >= recent_cutoff
            ]

            if not recent_metrics:
                return

            # Assess alignment with each constitutional principle
            principle_assessments = {}

            for principle, description in self.constitutional_principles.items():
                assessment = await self._assess_constitutional_principle(
                    principle, recent_metrics
                )
                principle_assessments[principle] = assessment

            # Log constitutional alignment
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "constitutional_alignment_check",
                    "principle_assessments": principle_assessments,
                    "metrics_analyzed": len(recent_metrics),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Alert on poor alignment
            poor_alignments = [
                p for p, a in principle_assessments.items() if a["score"] < 0.7
            ]
            if poor_alignments:
                await self.alerting.send_alert(
                    "poor_constitutional_alignment",
                    "Poor constitutional alignment detected:"
                    f" {', '.join(poor_alignments)}",
                    severity="high",
                )

        except Exception as e:
            logger.error(f"Constitutional alignment check failed: {e}")

    async def _assess_constitutional_principle(
        self, principle: str, metrics: list[BiasMetricResult]
    ) -> dict[str, Any]:
        """Assess alignment with a specific constitutional principle"""
        try:
            if principle == "equal_protection":
                # Equal protection requires minimal bias across all groups
                violations = [
                    m
                    for m in metrics
                    if m.severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]
                ]
                score = max(0, 1 - (len(violations) / len(metrics)))

                return {
                    "score": score,
                    "violations": len(violations),
                    "total_metrics": len(metrics),
                    "status": "compliant" if score > 0.8 else "non_compliant",
                }

            elif principle == "due_process":
                # Due process requires fair and consistent treatment
                calibration_metrics = [
                    m for m in metrics if m.bias_type == BiasType.CALIBRATION
                ]
                if calibration_metrics:
                    avg_calibration = statistics.mean(
                        [1 - m.drift_score for m in calibration_metrics]
                    )
                    score = max(0, min(1, avg_calibration))
                else:
                    score = 0.5

                return {
                    "score": score,
                    "calibration_metrics": len(calibration_metrics),
                    "status": "compliant" if score > 0.8 else "non_compliant",
                }

            elif principle == "non_discrimination":
                # Non-discrimination requires equal treatment regardless of protected attributes
                demo_parity_metrics = [
                    m for m in metrics if m.bias_type == BiasType.DEMOGRAPHIC_PARITY
                ]
                if demo_parity_metrics:
                    avg_parity = statistics.mean(
                        [1 - m.drift_score for m in demo_parity_metrics]
                    )
                    score = max(0, min(1, avg_parity))
                else:
                    score = 0.5

                return {
                    "score": score,
                    "demographic_parity_metrics": len(demo_parity_metrics),
                    "status": "compliant" if score > 0.8 else "non_compliant",
                }

            else:
                # Default assessment for other principles
                return {
                    "score": 0.5,
                    "status": "unknown",
                    "note": f"Assessment method not implemented for {principle}",
                }

        except Exception as e:
            logger.error(
                f"Constitutional principle assessment failed for {principle}: {e}"
            )
            return {"score": 0.0, "status": "error", "error": str(e)}

    async def _run_real_time_alerting(self):
        """Run real-time bias alerting"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                if not self.running:
                    break

                if self.real_time_alerts_enabled:
                    await self._check_real_time_bias_alerts()

            except Exception as e:
                logger.error(f"Real-time alerting error: {e}")
                await asyncio.sleep(60)

    async def _check_real_time_bias_alerts(self):
        """Check for real-time bias alerts"""
        try:
            # Check recent metrics for immediate alerting
            immediate_cutoff = datetime.utcnow() - timedelta(minutes=5)
            immediate_metrics = [
                metric
                for metric in self.metric_history
                if metric.timestamp >= immediate_cutoff
                and metric.severity == BiasSeverity.CRITICAL
            ]

            if immediate_metrics:
                # Group by context for consolidated alerting
                context_groups = defaultdict(list)
                for metric in immediate_metrics:
                    context_groups[metric.context].append(metric)

                for context, metrics in context_groups.items():
                    await self.alerting.send_alert(
                        f"immediate_bias_alert_{context.value}",
                        f"CRITICAL: Immediate bias detected in {context.value}:"
                        f" {len(metrics)} violations",
                        severity="critical",
                    )

        except Exception as e:
            logger.error(f"Real-time bias alert check failed: {e}")

    # Public methods for baseline management and status

    async def establish_baseline(
        self,
        context: BiasContext,
        bias_type: BiasType,
        protected_attr: ProtectedAttribute,
        baseline_value: float,
    ):
        """Establish baseline bias metric"""
        try:
            baseline_key = (context, bias_type, protected_attr)
            self.baseline_metrics[baseline_key] = baseline_value

            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "bias_baseline_established",
                    "context": context.value,
                    "bias_type": bias_type.value,
                    "protected_attribute": protected_attr.value,
                    "baseline_value": baseline_value,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            logger.info(
                f"Bias baseline established: {context.value} - {bias_type.value} -"
                f" {protected_attr.value}: {baseline_value}"
            )

        except Exception as e:
            logger.error(f"Failed to establish bias baseline: {e}")
            raise

    def get_bias_monitoring_status(self) -> dict[str, Any]:
        """Get current bias monitoring status"""
        try:
            current_time = datetime.utcnow()

            # Recent metrics summary
            recent_cutoff = current_time - timedelta(hours=24)
            recent_metrics = [
                m for m in self.metric_history if m.timestamp >= recent_cutoff
            ]

            # Severity breakdown
            severity_counts = {severity.value: 0 for severity in BiasSeverity}
            for metric in recent_metrics:
                severity_counts[metric.severity.value] += 1

            # Context breakdown
            context_counts = {context.value: 0 for context in BiasContext}
            for metric in recent_metrics:
                context_counts[metric.context.value] += 1

            # Protected attribute breakdown
            attr_counts = {attr.value: 0 for attr in ProtectedAttribute}
            for metric in recent_metrics:
                attr_counts[metric.protected_attribute.value] += 1

            return {
                "monitoring_status": {
                    "enabled": self.monitoring_enabled,
                    "running": self.running,
                    "last_analysis_time": self.last_analysis_time.isoformat(),
                    "monitoring_interval_seconds": self.monitoring_interval_seconds,
                },
                "recent_metrics_24h": {
                    "total_metrics": len(recent_metrics),
                    "by_severity": severity_counts,
                    "by_context": context_counts,
                    "by_protected_attribute": attr_counts,
                },
                "alert_status": {
                    "total_alerts": len(self.drift_alerts),
                    "recent_alerts": len(
                        [
                            alert
                            for alert in self.drift_alerts.values()
                            if alert.timestamp >= recent_cutoff
                        ]
                    ),
                },
                "pattern_analysis": {
                    "patterns_detected": len(self.bias_patterns),
                    "temporal_patterns_tracked": len(self.temporal_patterns),
                },
                "compliance_status": {
                    "recent_assessments": len(
                        [
                            c
                            for c in self.compliance_history
                            if c.timestamp >= recent_cutoff
                        ]
                    ),
                    "total_assessments": len(self.compliance_history),
                },
                "baseline_metrics": len(self.baseline_metrics),
                "configuration": {
                    "intersectional_analysis_enabled": (
                        self.intersectional_analysis_enabled
                    ),
                    "real_time_alerts_enabled": self.real_time_alerts_enabled,
                    "contexts_monitored": len(self.bias_thresholds),
                    "bias_types_configured": len(
                        set().union(
                            *[
                                list(context_thresholds.keys())
                                for context_thresholds in self.bias_thresholds.values()
                            ]
                        )
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {"error": str(e)}

    def get_bias_summary_report(
        self, time_window: timedelta = timedelta(days=7)
    ) -> dict[str, Any]:
        """Get comprehensive bias summary report"""
        try:
            current_time = datetime.utcnow()
            start_time = current_time - time_window

            # Filter data by time window
            window_metrics = [
                m for m in self.metric_history if m.timestamp >= start_time
            ]
            window_alerts = [
                a for a in self.drift_alerts.values() if a.timestamp >= start_time
            ]
            window_compliance = [
                c for c in self.compliance_history if c.timestamp >= start_time
            ]

            # Summary statistics
            if window_metrics:
                avg_metric_value = statistics.mean(
                    [m.metric_value for m in window_metrics]
                )
                avg_drift_score = statistics.mean(
                    [m.drift_score for m in window_metrics]
                )
                max_drift_score = max([m.drift_score for m in window_metrics])
            else:
                avg_metric_value = avg_drift_score = max_drift_score = 0

            # Compliance summary
            if window_compliance:
                avg_fairness_score = statistics.mean(
                    [c.overall_fairness_score for c in window_compliance]
                )
                avg_constitutional_alignment = statistics.mean(
                    [c.constitutional_alignment for c in window_compliance]
                )
            else:
                avg_fairness_score = avg_constitutional_alignment = 0

            return {
                "report_period": {
                    "start_time": start_time.isoformat(),
                    "end_time": current_time.isoformat(),
                    "duration_days": time_window.days,
                },
                "bias_metrics_summary": {
                    "total_metrics_calculated": len(window_metrics),
                    "average_metric_value": avg_metric_value,
                    "average_drift_score": avg_drift_score,
                    "maximum_drift_score": max_drift_score,
                    "critical_violations": len(
                        [
                            m
                            for m in window_metrics
                            if m.severity == BiasSeverity.CRITICAL
                        ]
                    ),
                    "high_severity_violations": len(
                        [m for m in window_metrics if m.severity == BiasSeverity.HIGH]
                    ),
                },
                "alert_summary": {
                    "total_alerts": len(window_alerts),
                    "critical_alerts": len(
                        [
                            a
                            for a in window_alerts
                            if a.severity == BiasSeverity.CRITICAL
                        ]
                    ),
                    "high_severity_alerts": len(
                        [a for a in window_alerts if a.severity == BiasSeverity.HIGH]
                    ),
                    "unique_affected_contexts": len(
                        set(
                            m.context
                            for alert in window_alerts
                            for m in alert.affected_metrics
                        )
                    ),
                    "unique_affected_attributes": len(
                        set(
                            m.protected_attribute
                            for alert in window_alerts
                            for m in alert.affected_metrics
                        )
                    ),
                },
                "compliance_summary": {
                    "assessments_completed": len(window_compliance),
                    "average_fairness_score": avg_fairness_score,
                    "average_constitutional_alignment": avg_constitutional_alignment,
                    "fully_compliant_contexts": len(
                        [c for c in window_compliance if c.overall_fairness_score > 0.9]
                    ),
                    "non_compliant_contexts": len(
                        [c for c in window_compliance if c.overall_fairness_score < 0.7]
                    ),
                },
                "pattern_summary": {
                    "patterns_detected": len([p for p in self.bias_patterns]),
                    "high_risk_patterns": len(
                        [
                            p
                            for p in self.bias_patterns
                            if p.risk_level
                            in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]
                        ]
                    ),
                },
                "recommendations": self._generate_summary_recommendations(
                    window_metrics, window_alerts, window_compliance
                ),
            }

        except Exception as e:
            logger.error(f"Bias summary report generation failed: {e}")
            return {"error": str(e)}

    def _generate_summary_recommendations(
        self,
        metrics: list[BiasMetricResult],
        alerts: list[BiasDriftAlert],
        compliance: list[FairnessCompliance],
    ) -> list[str]:
        """Generate summary recommendations based on analysis"""
        recommendations = []

        # Metrics-based recommendations
        critical_metrics = [m for m in metrics if m.severity == BiasSeverity.CRITICAL]
        if critical_metrics:
            recommendations.extend(
                [
                    f"URGENT: Address {len(critical_metrics)} critical bias violations",
                    "Consider emergency bias audit and model review",
                    "Implement immediate human oversight for affected decisions",
                ]
            )

        high_metrics = [m for m in metrics if m.severity == BiasSeverity.HIGH]
        if len(high_metrics) > 5:
            recommendations.append(
                f"Review bias mitigation strategies ({len(high_metrics)} high-severity"
                " violations)"
            )

        # Alert-based recommendations
        if len(alerts) > 3:
            recommendations.append(
                "High alert frequency suggests systematic bias issues"
            )

        # Compliance-based recommendations
        poor_compliance = [c for c in compliance if c.overall_fairness_score < 0.7]
        if poor_compliance:
            recommendations.append(
                f"Improve fairness compliance in {len(poor_compliance)} contexts"
            )

        # General recommendations
        if not recommendations:
            recommendations.extend(
                [
                    "Continue current bias monitoring practices",
                    "Consider expanding baseline metrics coverage",
                    "Schedule regular bias audit reviews",
                ]
            )

        return recommendations


# Example usage
async def example_usage():
    """Example of using the bias drift monitor"""
    # Initialize monitor
    monitor = BiasDriftMonitor(
        {
            "monitoring_enabled": True,
            "monitoring_interval_seconds": 60,
            "intersectional_analysis_enabled": True,
            "real_time_alerts_enabled": True,
        }
    )

    # Establish some baselines
    await monitor.establish_baseline(
        BiasContext.CONSTITUTIONAL_ANALYSIS,
        BiasType.DEMOGRAPHIC_PARITY,
        ProtectedAttribute.RACE_ETHNICITY,
        0.02,
    )

    await monitor.establish_baseline(
        BiasContext.POLICY_RECOMMENDATION,
        BiasType.EQUALIZED_ODDS,
        ProtectedAttribute.GENDER,
        0.03,
    )

    # Start monitoring (would run continuously in production)
    logger.info("Starting bias drift monitoring demo")
    monitoring_task = asyncio.create_task(monitor.start_monitoring())

    # Let it run for a short period
    await asyncio.sleep(30)

    # Stop monitoring
    await monitor.stop_monitoring()
    monitoring_task.cancel()

    # Get status and reports
    status = monitor.get_bias_monitoring_status()
    summary_report = monitor.get_bias_summary_report(timedelta(hours=1))

    logger.info(f"Monitoring status: {status}")
    logger.info(f"Summary report: {summary_report}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
