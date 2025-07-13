"""
Advanced Metrics Collector for ACGS

Comprehensive metrics collection system for monitoring model drift, human intervention
rates, and other critical AI system metrics. Provides real-time monitoring capabilities
with automated alerting and trend analysis.

Key Features:
- Model drift detection and measurement
- Human intervention rate tracking
- Performance degradation monitoring
- Bias drift detection
- Constitutional compliance metrics
- Real-time alerting and threshold management
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
import statistics
import uuid
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)


class DriftType(Enum):
    """Types of drift detection"""

    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    BIAS_DRIFT = "bias_drift"
    PERFORMANCE_DRIFT = "performance_drift"


class DriftSeverity(Enum):
    """Severity levels for detected drift"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionReason(Enum):
    """Reasons for human intervention"""

    LOW_CONFIDENCE = "low_confidence"
    BIAS_DETECTED = "bias_detected"
    CONSTITUTIONAL_CONFLICT = "constitutional_conflict"
    POLICY_VIOLATION = "policy_violation"
    ERROR_DETECTED = "error_detected"
    USER_REQUEST = "user_request"
    REGULATORY_REQUIREMENT = "regulatory_requirement"
    QUALITY_THRESHOLD = "quality_threshold"


@dataclass
class DriftMeasurement:
    """Model drift measurement result"""

    measurement_id: str
    drift_type: DriftType
    severity: DriftSeverity
    drift_score: float
    threshold: float
    baseline_window: int
    current_window: int
    timestamp: datetime
    feature_impacts: dict[str, float]
    statistical_test_results: dict[str, Any]
    remediation_suggested: list[str]


@dataclass
class InterventionRecord:
    """Human intervention tracking record"""

    intervention_id: str
    timestamp: datetime
    reason: InterventionReason
    decision_id: str
    original_prediction: dict[str, Any]
    human_decision: dict[str, Any]
    intervention_duration_seconds: float
    reviewer_id: str
    confidence_before: float
    confidence_after: float
    outcome_quality: float | None
    follow_up_required: bool


@dataclass
class PerformanceMetrics:
    """System performance metrics"""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    prediction_latency_ms: float
    throughput_requests_per_second: float
    error_rate: float
    availability: float
    constitutional_compliance_score: float


@dataclass
class BiasMetrics:
    """Bias detection and measurement metrics"""

    demographic_parity: float
    equalized_odds: float
    calibration_score: float
    individual_fairness: float
    group_fairness: float
    bias_score_by_group: dict[str, float]
    protected_attributes: list[str]
    measurement_timestamp: datetime


@dataclass
class ConstitutionalMetrics:
    """Constitutional AI compliance metrics"""

    principle_adherence_score: float
    conflict_resolution_success_rate: float
    democratic_value_alignment: float
    transparency_score: float
    accountability_score: float
    human_oversight_effectiveness: float
    citizen_satisfaction_score: float


class AdvancedMetricsCollector:
    """
    Advanced metrics collection system for ACGS monitoring
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Collection configuration
        self.collection_interval_seconds = config.get("collection_interval_seconds", 60)
        self.drift_detection_window = config.get("drift_detection_window", 100)
        self.baseline_window_size = config.get("baseline_window_size", 1000)
        self.intervention_tracking_enabled = config.get(
            "intervention_tracking_enabled", True
        )

        # Drift thresholds
        self.drift_thresholds = config.get(
            "drift_thresholds",
            {
                DriftType.DATA_DRIFT: {
                    "low": 0.1,
                    "medium": 0.3,
                    "high": 0.5,
                    "critical": 0.7,
                },
                DriftType.CONCEPT_DRIFT: {
                    "low": 0.05,
                    "medium": 0.15,
                    "high": 0.25,
                    "critical": 0.4,
                },
                DriftType.PREDICTION_DRIFT: {
                    "low": 0.1,
                    "medium": 0.2,
                    "high": 0.3,
                    "critical": 0.5,
                },
                DriftType.BIAS_DRIFT: {
                    "low": 0.05,
                    "medium": 0.1,
                    "high": 0.2,
                    "critical": 0.3,
                },
                DriftType.PERFORMANCE_DRIFT: {
                    "low": 0.05,
                    "medium": 0.1,
                    "high": 0.15,
                    "critical": 0.25,
                },
            },
        )

        # Performance thresholds
        self.performance_thresholds = config.get(
            "performance_thresholds",
            {
                "accuracy_min": 0.9,
                "precision_min": 0.85,
                "recall_min": 0.85,
                "latency_max_ms": 1000,
                "error_rate_max": 0.05,
                "availability_min": 0.999,
            },
        )

        # Data storage
        self.baseline_data = deque(maxlen=self.baseline_window_size)
        self.current_window_data = deque(maxlen=self.drift_detection_window)
        self.drift_measurements = {}
        self.intervention_records = {}
        self.performance_history = deque(maxlen=1000)
        self.bias_history = deque(maxlen=1000)
        self.constitutional_metrics_history = deque(maxlen=1000)

        # State management
        self.running = False
        self.last_collection_time = datetime.utcnow()
        self.baseline_established = False

        # Intervention tracking
        self.intervention_rate_window = deque(
            maxlen=1440
        )  # 24 hours at 1-minute intervals
        self.intervention_reasons_counter = dict.fromkeys(InterventionReason, 0)

    async def start_collection(self):
        """Start metrics collection"""
        if self.running:
            logger.warning("Metrics collection is already running")
            return

        self.running = True
        logger.info("Starting advanced metrics collection")

        try:
            # Start collection tasks
            collection_tasks = [
                self._run_drift_detection(),
                self._run_intervention_monitoring(),
                self._run_performance_monitoring(),
                self._run_bias_monitoring(),
                self._run_constitutional_monitoring(),
                self._run_alerting_and_reporting(),
            ]

            await asyncio.gather(*collection_tasks)

        except Exception as e:
            logger.exception(f"Metrics collection failed: {e}")
            self.running = False
            raise
        finally:
            logger.info("Metrics collection stopped")

    async def stop_collection(self):
        """Stop metrics collection"""
        self.running = False
        logger.info("Stopping metrics collection")

    async def _run_drift_detection(self):
        """Run continuous drift detection"""
        while self.running:
            try:
                await asyncio.sleep(self.collection_interval_seconds)

                if not self.running:
                    break

                # Collect current predictions and features for drift analysis
                current_data = await self._collect_current_data()
                if current_data:
                    self.current_window_data.append(current_data)

                    # Perform drift detection if we have enough data
                    if (
                        self.baseline_established
                        and len(self.current_window_data) >= 10
                    ):
                        await self._detect_all_drift_types()

            except Exception as e:
                logger.exception(f"Drift detection error: {e}")
                await asyncio.sleep(60)

    async def _collect_current_data(self) -> dict[str, Any] | None:
        """Collect current system data for drift analysis"""
        try:
            # This would integrate with the actual ACGS prediction system
            # For now, we'll simulate data collection

            current_time = datetime.utcnow()

            # Simulate collecting prediction data
            return {
                "timestamp": current_time,
                "predictions": np.random.normal(
                    0.5, 0.1, 10
                ).tolist(),  # Simulated predictions
                "features": {f"feature_{i}": np.random.normal(0, 1) for i in range(20)},
                "confidence_scores": np.random.uniform(0.7, 0.99, 10).tolist(),
                "processing_time_ms": np.random.uniform(50, 200),
                "model_version": self.config.get("model_version", "1.0.0"),
            }

        except Exception as e:
            logger.exception(f"Data collection failed: {e}")
            return None

    async def _detect_all_drift_types(self):
        """Detect all types of drift"""
        try:
            # Data drift detection
            data_drift = await self._detect_data_drift()
            if data_drift:
                await self._handle_drift_detection(data_drift)

            # Prediction drift detection
            prediction_drift = await self._detect_prediction_drift()
            if prediction_drift:
                await self._handle_drift_detection(prediction_drift)

            # Performance drift detection
            performance_drift = await self._detect_performance_drift()
            if performance_drift:
                await self._handle_drift_detection(performance_drift)

        except Exception as e:
            logger.exception(f"Drift detection failed: {e}")

    async def _detect_data_drift(self) -> DriftMeasurement | None:
        """Detect data drift using statistical tests"""
        try:
            if len(self.baseline_data) < 100 or len(self.current_window_data) < 10:
                return None

            # Extract features from baseline and current data
            baseline_features = self._extract_features(list(self.baseline_data))
            current_features = self._extract_features(list(self.current_window_data))

            # Calculate drift score using Kolmogorov-Smirnov test
            drift_scores = {}
            feature_impacts = {}

            for feature_name in baseline_features:
                if feature_name in current_features:
                    # Simplified drift calculation (would use scipy.stats in practice)
                    baseline_values = baseline_features[feature_name]
                    current_values = current_features[feature_name]

                    # Calculate mean difference as a proxy for drift
                    baseline_mean = statistics.mean(baseline_values)
                    current_mean = statistics.mean(current_values)
                    baseline_std = (
                        statistics.stdev(baseline_values)
                        if len(baseline_values) > 1
                        else 1
                    )

                    drift_score = abs(current_mean - baseline_mean) / (
                        baseline_std + 1e-10
                    )
                    drift_scores[feature_name] = drift_score
                    feature_impacts[feature_name] = drift_score

            # Calculate overall drift score
            overall_drift_score = max(drift_scores.values()) if drift_scores else 0

            # Determine severity
            severity = self._determine_drift_severity(
                DriftType.DATA_DRIFT, overall_drift_score
            )

            if (
                severity != DriftSeverity.LOW
                or overall_drift_score
                > self.drift_thresholds[DriftType.DATA_DRIFT]["low"]
            ):
                return DriftMeasurement(
                    measurement_id=str(uuid.uuid4()),
                    drift_type=DriftType.DATA_DRIFT,
                    severity=severity,
                    drift_score=overall_drift_score,
                    threshold=self.drift_thresholds[DriftType.DATA_DRIFT][
                        severity.value
                    ],
                    baseline_window=len(self.baseline_data),
                    current_window=len(self.current_window_data),
                    timestamp=datetime.utcnow(),
                    feature_impacts=feature_impacts,
                    statistical_test_results={"ks_test_scores": drift_scores},
                    remediation_suggested=self._suggest_drift_remediation(
                        DriftType.DATA_DRIFT, overall_drift_score
                    ),
                )

            return None

        except Exception as e:
            logger.exception(f"Data drift detection failed: {e}")
            return None

    async def _detect_prediction_drift(self) -> DriftMeasurement | None:
        """Detect prediction drift"""
        try:
            if len(self.baseline_data) < 100 or len(self.current_window_data) < 10:
                return None

            # Extract predictions
            baseline_predictions = [
                pred
                for data in self.baseline_data
                for pred in data.get("predictions", [])
            ]
            current_predictions = [
                pred
                for data in self.current_window_data
                for pred in data.get("predictions", [])
            ]

            if not baseline_predictions or not current_predictions:
                return None

            # Calculate prediction distribution drift
            baseline_mean = statistics.mean(baseline_predictions)
            current_mean = statistics.mean(current_predictions)
            baseline_std = (
                statistics.stdev(baseline_predictions)
                if len(baseline_predictions) > 1
                else 1
            )

            drift_score = abs(current_mean - baseline_mean) / (baseline_std + 1e-10)

            # Determine severity
            severity = self._determine_drift_severity(
                DriftType.PREDICTION_DRIFT, drift_score
            )

            if (
                severity != DriftSeverity.LOW
                or drift_score
                > self.drift_thresholds[DriftType.PREDICTION_DRIFT]["low"]
            ):
                return DriftMeasurement(
                    measurement_id=str(uuid.uuid4()),
                    drift_type=DriftType.PREDICTION_DRIFT,
                    severity=severity,
                    drift_score=drift_score,
                    threshold=self.drift_thresholds[DriftType.PREDICTION_DRIFT][
                        severity.value
                    ],
                    baseline_window=len(baseline_predictions),
                    current_window=len(current_predictions),
                    timestamp=datetime.utcnow(),
                    feature_impacts={"prediction_distribution": drift_score},
                    statistical_test_results={
                        "baseline_mean": baseline_mean,
                        "current_mean": current_mean,
                        "drift_magnitude": drift_score,
                    },
                    remediation_suggested=self._suggest_drift_remediation(
                        DriftType.PREDICTION_DRIFT, drift_score
                    ),
                )

            return None

        except Exception as e:
            logger.exception(f"Prediction drift detection failed: {e}")
            return None

    async def _detect_performance_drift(self) -> DriftMeasurement | None:
        """Detect performance drift"""
        try:
            if len(self.performance_history) < 20:
                return None

            # Get recent performance metrics
            recent_metrics = list(self.performance_history)[-10:]
            historical_metrics = list(self.performance_history)[:-10]

            if len(historical_metrics) < 10:
                return None

            # Calculate performance drift for key metrics
            metrics_to_check = ["accuracy", "precision", "recall", "f1_score"]
            drift_scores = {}

            for metric in metrics_to_check:
                historical_values = [getattr(m, metric) for m in historical_metrics]
                recent_values = [getattr(m, metric) for m in recent_metrics]

                historical_mean = statistics.mean(historical_values)
                recent_mean = statistics.mean(recent_values)
                historical_std = (
                    statistics.stdev(historical_values)
                    if len(historical_values) > 1
                    else 0.01
                )

                # Performance drift is typically degradation, so we look for decreases
                drift_score = max(
                    0, (historical_mean - recent_mean) / (historical_std + 1e-10)
                )
                drift_scores[metric] = drift_score

            # Overall performance drift score
            overall_drift_score = max(drift_scores.values()) if drift_scores else 0

            # Determine severity
            severity = self._determine_drift_severity(
                DriftType.PERFORMANCE_DRIFT, overall_drift_score
            )

            if (
                severity != DriftSeverity.LOW
                or overall_drift_score
                > self.drift_thresholds[DriftType.PERFORMANCE_DRIFT]["low"]
            ):
                return DriftMeasurement(
                    measurement_id=str(uuid.uuid4()),
                    drift_type=DriftType.PERFORMANCE_DRIFT,
                    severity=severity,
                    drift_score=overall_drift_score,
                    threshold=self.drift_thresholds[DriftType.PERFORMANCE_DRIFT][
                        severity.value
                    ],
                    baseline_window=len(historical_metrics),
                    current_window=len(recent_metrics),
                    timestamp=datetime.utcnow(),
                    feature_impacts=drift_scores,
                    statistical_test_results={
                        "performance_degradation": drift_scores,
                        "recent_period_days": len(recent_metrics),
                        "historical_period_days": len(historical_metrics),
                    },
                    remediation_suggested=self._suggest_drift_remediation(
                        DriftType.PERFORMANCE_DRIFT, overall_drift_score
                    ),
                )

            return None

        except Exception as e:
            logger.exception(f"Performance drift detection failed: {e}")
            return None

    def _extract_features(
        self, data_list: list[dict[str, Any]]
    ) -> dict[str, list[float]]:
        """Extract features from data for drift analysis"""
        features = {}

        for data in data_list:
            if "features" in data:
                for feature_name, feature_value in data["features"].items():
                    if feature_name not in features:
                        features[feature_name] = []
                    features[feature_name].append(float(feature_value))

        return features

    def _determine_drift_severity(
        self, drift_type: DriftType, drift_score: float
    ) -> DriftSeverity:
        """Determine drift severity based on score and thresholds"""
        thresholds = self.drift_thresholds[drift_type]

        if drift_score >= thresholds["critical"]:
            return DriftSeverity.CRITICAL
        if drift_score >= thresholds["high"]:
            return DriftSeverity.HIGH
        if drift_score >= thresholds["medium"]:
            return DriftSeverity.MEDIUM
        return DriftSeverity.LOW

    def _suggest_drift_remediation(
        self, drift_type: DriftType, drift_score: float
    ) -> list[str]:
        """Suggest remediation actions for detected drift"""
        remediation_actions = []

        if drift_type == DriftType.DATA_DRIFT:
            remediation_actions.extend(
                [
                    "Review data sources for quality issues",
                    "Check for changes in data collection processes",
                    "Consider retraining with recent data",
                    "Investigate feature engineering pipeline",
                ]
            )
        elif drift_type == DriftType.PREDICTION_DRIFT:
            remediation_actions.extend(
                [
                    "Analyze prediction patterns for anomalies",
                    "Review model confidence thresholds",
                    "Consider model recalibration",
                    "Investigate input data changes",
                ]
            )
        elif drift_type == DriftType.PERFORMANCE_DRIFT:
            remediation_actions.extend(
                [
                    "Conduct comprehensive model evaluation",
                    "Consider model retraining or fine-tuning",
                    "Review system resource allocation",
                    "Investigate data quality degradation",
                ]
            )

        # Add severity-specific actions
        if drift_score >= 0.5:
            remediation_actions.extend(
                [
                    "URGENT: Implement immediate monitoring",
                    "Consider emergency model rollback",
                    "Escalate to ML engineering team",
                ]
            )

        return remediation_actions

    async def _handle_drift_detection(self, drift_measurement: DriftMeasurement):
        """Handle detected drift with logging and alerting"""
        try:
            # Store measurement
            self.drift_measurements[drift_measurement.measurement_id] = (
                drift_measurement
            )

            # Log drift detection
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "drift_detected",
                    "drift_type": drift_measurement.drift_type.value,
                    "severity": drift_measurement.severity.value,
                    "drift_score": drift_measurement.drift_score,
                    "threshold": drift_measurement.threshold,
                    "timestamp": drift_measurement.timestamp.isoformat(),
                }
            )

            # Send alert based on severity
            alert_severity = {
                DriftSeverity.LOW: "low",
                DriftSeverity.MEDIUM: "medium",
                DriftSeverity.HIGH: "high",
                DriftSeverity.CRITICAL: "critical",
            }[drift_measurement.severity]

            await self.alerting.send_alert(
                f"model_drift_{drift_measurement.drift_type.value}",
                f"Model drift detected: {drift_measurement.drift_type.value} (score:"
                f" {drift_measurement.drift_score:.3f}, severity:"
                f" {drift_measurement.severity.value})",
                severity=alert_severity,
            )

        except Exception as e:
            logger.exception(f"Drift handling failed: {e}")

    async def _run_intervention_monitoring(self):
        """Monitor human intervention rates and patterns"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute

                if not self.running:
                    break

                # Calculate intervention rate for the last hour
                current_time = datetime.utcnow()
                hour_ago = current_time - timedelta(hours=1)

                recent_interventions = [
                    record
                    for record in self.intervention_records.values()
                    if record.timestamp >= hour_ago
                ]

                # Calculate intervention rate
                intervention_rate = len(recent_interventions) / 60  # per minute
                self.intervention_rate_window.append(
                    {
                        "timestamp": current_time,
                        "rate": intervention_rate,
                        "count": len(recent_interventions),
                    }
                )

                # Analyze intervention patterns
                await self._analyze_intervention_patterns(recent_interventions)

            except Exception as e:
                logger.exception(f"Intervention monitoring error: {e}")
                await asyncio.sleep(60)

    async def _analyze_intervention_patterns(
        self, interventions: list[InterventionRecord]
    ):
        """Analyze patterns in human interventions"""
        try:
            if not interventions:
                return

            # Count interventions by reason
            reason_counts = {}
            total_duration = 0
            quality_scores = []

            for intervention in interventions:
                reason = intervention.reason.value
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
                total_duration += intervention.intervention_duration_seconds

                if intervention.outcome_quality is not None:
                    quality_scores.append(intervention.outcome_quality)

            # Calculate metrics
            avg_duration = total_duration / len(interventions) if interventions else 0
            avg_quality = statistics.mean(quality_scores) if quality_scores else None

            # Check for concerning patterns
            critical_reasons = [
                InterventionReason.BIAS_DETECTED,
                InterventionReason.CONSTITUTIONAL_CONFLICT,
            ]
            critical_interventions = sum(
                reason_counts.get(reason.value, 0) for reason in critical_reasons
            )

            # Alert on high critical intervention rate
            if (
                critical_interventions > 3
            ):  # More than 3 critical interventions per hour
                await self.alerting.send_alert(
                    "high_critical_intervention_rate",
                    f"High rate of critical interventions: {critical_interventions} in"
                    " last hour",
                    severity="high",
                )

            # Log intervention analysis
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "intervention_analysis",
                    "total_interventions": len(interventions),
                    "critical_interventions": critical_interventions,
                    "avg_duration_seconds": avg_duration,
                    "avg_quality_score": avg_quality,
                    "reason_breakdown": reason_counts,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.exception(f"Intervention pattern analysis failed: {e}")

    async def _run_performance_monitoring(self):
        """Monitor system performance metrics"""
        while self.running:
            try:
                await asyncio.sleep(self.collection_interval_seconds)

                if not self.running:
                    break

                # Collect performance metrics
                metrics = await self._collect_performance_metrics()
                if metrics:
                    self.performance_history.append(metrics)

                    # Check thresholds
                    await self._check_performance_thresholds(metrics)

            except Exception as e:
                logger.exception(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)

    async def _collect_performance_metrics(self) -> PerformanceMetrics | None:
        """Collect current performance metrics"""
        try:
            # Simulate performance metrics collection
            # In practice, this would integrate with actual system metrics

            return PerformanceMetrics(
                accuracy=np.random.normal(0.92, 0.02),
                precision=np.random.normal(0.88, 0.03),
                recall=np.random.normal(0.86, 0.03),
                f1_score=np.random.normal(0.87, 0.02),
                auc_roc=np.random.normal(0.94, 0.02),
                prediction_latency_ms=np.random.normal(150, 30),
                throughput_requests_per_second=np.random.normal(45, 5),
                error_rate=np.random.normal(0.02, 0.01),
                availability=np.random.normal(0.9995, 0.0005),
                constitutional_compliance_score=np.random.normal(0.95, 0.02),
            )

        except Exception as e:
            logger.exception(f"Performance metrics collection failed: {e}")
            return None

    async def _check_performance_thresholds(self, metrics: PerformanceMetrics):
        """Check performance metrics against thresholds"""
        try:
            violations = []

            # Check each threshold
            if metrics.accuracy < self.performance_thresholds["accuracy_min"]:
                violations.append(f"Accuracy below threshold: {metrics.accuracy:.3f}")

            if metrics.precision < self.performance_thresholds["precision_min"]:
                violations.append(f"Precision below threshold: {metrics.precision:.3f}")

            if metrics.recall < self.performance_thresholds["recall_min"]:
                violations.append(f"Recall below threshold: {metrics.recall:.3f}")

            if (
                metrics.prediction_latency_ms
                > self.performance_thresholds["latency_max_ms"]
            ):
                violations.append(
                    f"Latency above threshold: {metrics.prediction_latency_ms:.1f}ms"
                )

            if metrics.error_rate > self.performance_thresholds["error_rate_max"]:
                violations.append(
                    f"Error rate above threshold: {metrics.error_rate:.3f}"
                )

            if metrics.availability < self.performance_thresholds["availability_min"]:
                violations.append(
                    f"Availability below threshold: {metrics.availability:.4f}"
                )

            # Send alerts for violations
            if violations:
                await self.alerting.send_alert(
                    "performance_threshold_violations",
                    f"Performance threshold violations: {'; '.join(violations)}",
                    severity="high",
                )

                await self.audit_logger.log_compliance_event(
                    {
                        "event_type": "performance_threshold_violation",
                        "violations": violations,
                        "metrics": asdict(metrics),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

        except Exception as e:
            logger.exception(f"Performance threshold check failed: {e}")

    async def _run_bias_monitoring(self):
        """Monitor bias metrics"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                if not self.running:
                    break

                # Collect bias metrics
                bias_metrics = await self._collect_bias_metrics()
                if bias_metrics:
                    self.bias_history.append(bias_metrics)

                    # Check for bias drift
                    await self._check_bias_drift(bias_metrics)

            except Exception as e:
                logger.exception(f"Bias monitoring error: {e}")
                await asyncio.sleep(60)

    async def _collect_bias_metrics(self) -> BiasMetrics | None:
        """Collect bias fairness metrics"""
        try:
            # Simulate bias metrics collection
            return BiasMetrics(
                demographic_parity=np.random.normal(0.95, 0.02),
                equalized_odds=np.random.normal(0.93, 0.03),
                calibration_score=np.random.normal(0.91, 0.02),
                individual_fairness=np.random.normal(0.94, 0.02),
                group_fairness=np.random.normal(0.92, 0.03),
                bias_score_by_group={
                    "group_a": np.random.normal(0.02, 0.01),
                    "group_b": np.random.normal(0.03, 0.01),
                    "group_c": np.random.normal(0.025, 0.01),
                },
                protected_attributes=["age", "gender", "ethnicity"],
                measurement_timestamp=datetime.utcnow(),
            )

        except Exception as e:
            logger.exception(f"Bias metrics collection failed: {e}")
            return None

    async def _check_bias_drift(self, current_metrics: BiasMetrics):
        """Check for bias drift"""
        try:
            if len(self.bias_history) < 10:
                return

            # Compare with historical bias metrics
            historical_metrics = list(self.bias_history)[-10:]

            # Calculate bias drift for key metrics
            bias_drift_scores = {}

            fairness_metrics = [
                "demographic_parity",
                "equalized_odds",
                "calibration_score",
                "individual_fairness",
                "group_fairness",
            ]

            for metric in fairness_metrics:
                historical_values = [getattr(m, metric) for m in historical_metrics]
                current_value = getattr(current_metrics, metric)

                historical_mean = statistics.mean(historical_values)
                historical_std = (
                    statistics.stdev(historical_values)
                    if len(historical_values) > 1
                    else 0.01
                )

                # Bias drift is degradation in fairness
                drift_score = max(
                    0, (historical_mean - current_value) / (historical_std + 1e-10)
                )
                bias_drift_scores[metric] = drift_score

            # Overall bias drift score
            overall_bias_drift = (
                max(bias_drift_scores.values()) if bias_drift_scores else 0
            )

            # Check threshold
            if (
                overall_bias_drift
                > self.drift_thresholds[DriftType.BIAS_DRIFT]["medium"]
            ):
                severity = self._determine_drift_severity(
                    DriftType.BIAS_DRIFT, overall_bias_drift
                )

                # Create bias drift measurement
                measurement = DriftMeasurement(
                    measurement_id=str(uuid.uuid4()),
                    drift_type=DriftType.BIAS_DRIFT,
                    severity=severity,
                    drift_score=overall_bias_drift,
                    threshold=self.drift_thresholds[DriftType.BIAS_DRIFT][
                        severity.value
                    ],
                    baseline_window=len(historical_metrics),
                    current_window=1,
                    timestamp=datetime.utcnow(),
                    feature_impacts=bias_drift_scores,
                    statistical_test_results={
                        "fairness_degradation": bias_drift_scores,
                        "affected_groups": list(
                            current_metrics.bias_score_by_group.keys()
                        ),
                    },
                    remediation_suggested=[
                        "Conduct immediate bias assessment",
                        "Review training data for bias",
                        "Implement bias mitigation techniques",
                        "Increase human oversight for affected groups",
                    ],
                )

                await self._handle_drift_detection(measurement)

        except Exception as e:
            logger.exception(f"Bias drift check failed: {e}")

    async def _run_constitutional_monitoring(self):
        """Monitor constitutional AI compliance metrics"""
        while self.running:
            try:
                await asyncio.sleep(600)  # Every 10 minutes

                if not self.running:
                    break

                # Collect constitutional metrics
                constitutional_metrics = await self._collect_constitutional_metrics()
                if constitutional_metrics:
                    self.constitutional_metrics_history.append(constitutional_metrics)

            except Exception as e:
                logger.exception(f"Constitutional monitoring error: {e}")
                await asyncio.sleep(60)

    async def _collect_constitutional_metrics(self) -> ConstitutionalMetrics | None:
        """Collect constitutional AI compliance metrics"""
        try:
            # Simulate constitutional metrics collection
            return ConstitutionalMetrics(
                principle_adherence_score=np.random.normal(0.94, 0.02),
                conflict_resolution_success_rate=np.random.normal(0.91, 0.03),
                democratic_value_alignment=np.random.normal(0.93, 0.02),
                transparency_score=np.random.normal(0.89, 0.03),
                accountability_score=np.random.normal(0.92, 0.02),
                human_oversight_effectiveness=np.random.normal(0.95, 0.02),
                citizen_satisfaction_score=np.random.normal(0.87, 0.04),
            )

        except Exception as e:
            logger.exception(f"Constitutional metrics collection failed: {e}")
            return None

    async def _run_alerting_and_reporting(self):
        """Run periodic alerting and reporting"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Every hour

                if not self.running:
                    break

                # Generate hourly summary
                await self._generate_hourly_summary()

            except Exception as e:
                logger.exception(f"Alerting and reporting error: {e}")
                await asyncio.sleep(60)

    async def _generate_hourly_summary(self):
        """Generate hourly metrics summary"""
        try:
            current_time = datetime.utcnow()
            hour_ago = current_time - timedelta(hours=1)

            # Count recent drift measurements
            recent_drift = [
                dm
                for dm in self.drift_measurements.values()
                if dm.timestamp >= hour_ago
            ]

            # Count recent interventions
            recent_interventions = [
                ir
                for ir in self.intervention_records.values()
                if ir.timestamp >= hour_ago
            ]

            # Calculate intervention rate
            intervention_rate = len(recent_interventions) / 60  # per minute

            summary = {
                "timestamp": current_time.isoformat(),
                "period_hours": 1,
                "drift_detections": {
                    "total": len(recent_drift),
                    "by_type": {
                        dt.value: len([d for d in recent_drift if d.drift_type == dt])
                        for dt in DriftType
                    },
                    "by_severity": {
                        ds.value: len([d for d in recent_drift if d.severity == ds])
                        for ds in DriftSeverity
                    },
                },
                "human_interventions": {
                    "total": len(recent_interventions),
                    "rate_per_minute": intervention_rate,
                    "by_reason": {
                        ir.value: len(
                            [i for i in recent_interventions if i.reason == ir]
                        )
                        for ir in InterventionReason
                    },
                },
                "system_health": {
                    "performance_metrics_collected": len(
                        [m for m in self.performance_history if hasattr(m, "accuracy")]
                    ),
                    "bias_metrics_collected": len(list(self.bias_history)),
                    "constitutional_metrics_collected": len(
                        list(self.constitutional_metrics_history)
                    ),
                },
            }

            # Log summary
            await self.audit_logger.log_compliance_event(
                {"event_type": "hourly_metrics_summary", "summary": summary}
            )

            # Alert on concerning patterns
            if len(recent_drift) > 5:  # More than 5 drift detections per hour
                await self.alerting.send_alert(
                    "high_drift_detection_rate",
                    f"High drift detection rate: {len(recent_drift)} detections in last"
                    " hour",
                    severity="medium",
                )

            if intervention_rate > 0.5:  # More than 0.5 interventions per minute
                await self.alerting.send_alert(
                    "high_intervention_rate",
                    f"High intervention rate: {intervention_rate:.2f} interventions per"
                    " minute",
                    severity="medium",
                )

        except Exception as e:
            logger.exception(f"Hourly summary generation failed: {e}")

    # Public methods for recording interventions and establishing baseline

    async def record_human_intervention(self, intervention_data: dict[str, Any]) -> str:
        """Record a human intervention"""
        try:
            intervention_id = str(uuid.uuid4())

            intervention = InterventionRecord(
                intervention_id=intervention_id,
                timestamp=datetime.utcnow(),
                reason=InterventionReason(
                    intervention_data.get("reason", "user_request")
                ),
                decision_id=intervention_data.get("decision_id", ""),
                original_prediction=intervention_data.get("original_prediction", {}),
                human_decision=intervention_data.get("human_decision", {}),
                intervention_duration_seconds=intervention_data.get(
                    "duration_seconds", 0.0
                ),
                reviewer_id=intervention_data.get("reviewer_id", ""),
                confidence_before=intervention_data.get("confidence_before", 0.0),
                confidence_after=intervention_data.get("confidence_after", 0.0),
                outcome_quality=intervention_data.get("outcome_quality"),
                follow_up_required=intervention_data.get("follow_up_required", False),
            )

            self.intervention_records[intervention_id] = intervention

            # Update intervention reason counter
            self.intervention_reasons_counter[intervention.reason] += 1

            # Log intervention
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "human_intervention_recorded",
                    "intervention_id": intervention_id,
                    "reason": intervention.reason.value,
                    "duration_seconds": intervention.intervention_duration_seconds,
                    "timestamp": intervention.timestamp.isoformat(),
                }
            )

            return intervention_id

        except Exception as e:
            logger.exception(f"Failed to record human intervention: {e}")
            raise

    async def establish_baseline(self, baseline_data: list[dict[str, Any]]):
        """Establish baseline data for drift detection"""
        try:
            self.baseline_data.clear()
            self.baseline_data.extend(baseline_data)
            self.baseline_established = True

            logger.info(f"Baseline established with {len(baseline_data)} data points")

            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "baseline_established",
                    "baseline_size": len(baseline_data),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.exception(f"Failed to establish baseline: {e}")
            raise

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get current metrics summary"""
        current_time = datetime.utcnow()

        return {
            "collection_status": {
                "running": self.running,
                "last_collection": self.last_collection_time.isoformat(),
                "baseline_established": self.baseline_established,
                "baseline_size": len(self.baseline_data),
            },
            "drift_monitoring": {
                "total_measurements": len(self.drift_measurements),
                "current_window_size": len(self.current_window_data),
                "recent_drift_detections": len(
                    [
                        dm
                        for dm in self.drift_measurements.values()
                        if dm.timestamp >= current_time - timedelta(hours=24)
                    ]
                ),
            },
            "intervention_monitoring": {
                "total_interventions": len(self.intervention_records),
                "current_rate_per_minute": len(self.intervention_rate_window),
                "recent_interventions": len(
                    [
                        ir
                        for ir in self.intervention_records.values()
                        if ir.timestamp >= current_time - timedelta(hours=24)
                    ]
                ),
                "intervention_reasons": dict(self.intervention_reasons_counter),
            },
            "performance_monitoring": {
                "metrics_history_size": len(self.performance_history),
                "bias_history_size": len(self.bias_history),
                "constitutional_history_size": len(self.constitutional_metrics_history),
            },
        }


# Example usage
async def example_usage():
    """Example of using the advanced metrics collector"""
    # Initialize collector
    collector = AdvancedMetricsCollector(
        {
            "collection_interval_seconds": 30,
            "drift_detection_window": 50,
            "intervention_tracking_enabled": True,
        }
    )

    # Establish baseline
    baseline_data = [
        {
            "timestamp": datetime.utcnow() - timedelta(days=i),
            "predictions": np.random.normal(0.5, 0.1, 10).tolist(),
            "features": {f"feature_{j}": np.random.normal(0, 1) for j in range(20)},
        }
        for i in range(100)
    ]

    await collector.establish_baseline(baseline_data)

    # Start collection (would run continuously in production)
    logger.info("Starting metrics collection demo")
    collection_task = asyncio.create_task(collector.start_collection())

    # Simulate some interventions
    for i in range(3):
        await collector.record_human_intervention(
            {
                "reason": "low_confidence",
                "decision_id": f"decision_{i}",
                "duration_seconds": 45.0,
                "reviewer_id": "reviewer_001",
                "confidence_before": 0.6,
                "confidence_after": 0.9,
            }
        )
        await asyncio.sleep(1)

    # Let it run for a short period
    await asyncio.sleep(10)

    # Stop collection
    await collector.stop_collection()
    collection_task.cancel()

    # Get summary
    summary = collector.get_metrics_summary()
    logger.info(f"Metrics summary: {summary}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
