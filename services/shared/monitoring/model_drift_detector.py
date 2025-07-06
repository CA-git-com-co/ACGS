"""
Model Drift Detection System

Specialized drift detection system for ACGS that implements advanced statistical
methods to detect various types of model drift. Provides real-time monitoring
with configurable sensitivity and automated response capabilities.

Key Features:
- Multi-method drift detection (statistical, ML-based)
- Concept drift, data drift, and prediction drift detection
- Adaptive threshold management
- Feature-level drift analysis
- Real-time alerting with severity classification
- Automated remediation recommendations
"""
# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
import math
import statistics
import uuid
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import numpy as np

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)


class DriftDetectionMethod(Enum):
    """Drift detection methods"""

    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    POPULATION_STABILITY_INDEX = "population_stability_index"
    JENSEN_SHANNON_DIVERGENCE = "jensen_shannon_divergence"
    MAXIMUM_MEAN_DISCREPANCY = "maximum_mean_discrepancy"
    ADAPTIVE_WINDOWING = "adaptive_windowing"
    STATISTICAL_DISTANCE = "statistical_distance"


class DriftComponent(Enum):
    """Components that can experience drift"""

    INPUT_FEATURES = "input_features"
    PREDICTIONS = "predictions"
    FEATURE_IMPORTANCE = "feature_importance"
    MODEL_PERFORMANCE = "model_performance"
    PREDICTION_CONFIDENCE = "prediction_confidence"
    DECISION_PATTERNS = "decision_patterns"


class DriftSeverity(Enum):
    """Drift severity levels"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DriftDetectionConfig:
    """Configuration for drift detection"""

    method: DriftDetectionMethod
    component: DriftComponent
    sensitivity: float  # 0.0 - 1.0
    window_size: int
    baseline_size: int
    threshold_low: float
    threshold_medium: float
    threshold_high: float
    threshold_critical: float
    enabled: bool = True


@dataclass
class FeatureDriftResult:
    """Result of feature-level drift detection"""

    feature_name: str
    drift_score: float
    severity: DriftSeverity
    method_used: DriftDetectionMethod
    baseline_statistics: dict[str, float]
    current_statistics: dict[str, float]
    p_value: Optional[float]
    effect_size: float
    recommendations: list[str]


@dataclass
class DriftDetectionResult:
    """Complete drift detection result"""

    detection_id: str
    timestamp: datetime
    component: DriftComponent
    overall_drift_score: float
    overall_severity: DriftSeverity
    feature_results: list[FeatureDriftResult]
    method_results: dict[DriftDetectionMethod, float]
    baseline_period: tuple[datetime, datetime]
    detection_period: tuple[datetime, datetime]
    statistical_summary: dict[str, Any]
    remediation_plan: list[str]
    confidence: float
    requires_immediate_action: bool


@dataclass
class DriftAlert:
    """Drift alert information"""

    alert_id: str
    detection_result: DriftDetectionResult
    alert_level: str
    message: str
    stakeholders: list[str]
    recommended_actions: list[str]
    escalation_required: bool
    timestamp: datetime


class ModelDriftDetector:
    """
    Advanced model drift detection system for ACGS
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Detection configuration
        self.detection_configs = self._initialize_detection_configs()
        self.detection_interval_seconds = config.get(
            "detection_interval_seconds", 300
        )  # 5 minutes
        self.adaptive_thresholds = config.get("adaptive_thresholds", True)
        self.auto_baseline_update = config.get("auto_baseline_update", False)

        # Data storage
        self.baseline_data = {}  # component -> data
        self.current_windows = {}  # component -> data window
        self.drift_history = deque(maxlen=1000)
        self.detection_results = {}

        # State management
        self.running = False
        self.last_detection_time = datetime.utcnow()
        self.baseline_established = {}  # component -> bool

        # Adaptive threshold management
        self.threshold_adaptation_history = deque(maxlen=100)
        self.false_positive_rate = 0.05  # Target false positive rate

        # Feature tracking
        self.feature_importance_history = deque(maxlen=100)
        self.feature_drift_patterns = {}

    def _initialize_detection_configs(
        self,
    ) -> dict[DriftComponent, list[DriftDetectionConfig]]:
        """Initialize drift detection configurations"""
        configs = {}

        # Input features drift detection
        configs[DriftComponent.INPUT_FEATURES] = [
            DriftDetectionConfig(
                method=DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
                component=DriftComponent.INPUT_FEATURES,
                sensitivity=0.7,
                window_size=100,
                baseline_size=1000,
                threshold_low=0.05,
                threshold_medium=0.10,
                threshold_high=0.20,
                threshold_critical=0.35,
                enabled=True,
            ),
            DriftDetectionConfig(
                method=DriftDetectionMethod.POPULATION_STABILITY_INDEX,
                component=DriftComponent.INPUT_FEATURES,
                sensitivity=0.8,
                window_size=100,
                baseline_size=1000,
                threshold_low=0.1,
                threshold_medium=0.2,
                threshold_high=0.3,
                threshold_critical=0.5,
                enabled=True,
            ),
        ]

        # Predictions drift detection
        configs[DriftComponent.PREDICTIONS] = [
            DriftDetectionConfig(
                method=DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE,
                component=DriftComponent.PREDICTIONS,
                sensitivity=0.8,
                window_size=50,
                baseline_size=500,
                threshold_low=0.05,
                threshold_medium=0.15,
                threshold_high=0.25,
                threshold_critical=0.4,
                enabled=True,
            )
        ]

        # Model performance drift detection
        configs[DriftComponent.MODEL_PERFORMANCE] = [
            DriftDetectionConfig(
                method=DriftDetectionMethod.STATISTICAL_DISTANCE,
                component=DriftComponent.MODEL_PERFORMANCE,
                sensitivity=0.9,
                window_size=30,
                baseline_size=200,
                threshold_low=0.05,
                threshold_medium=0.10,
                threshold_high=0.15,
                threshold_critical=0.25,
                enabled=True,
            )
        ]

        # Feature importance drift detection
        configs[DriftComponent.FEATURE_IMPORTANCE] = [
            DriftDetectionConfig(
                method=DriftDetectionMethod.MAXIMUM_MEAN_DISCREPANCY,
                component=DriftComponent.FEATURE_IMPORTANCE,
                sensitivity=0.6,
                window_size=20,
                baseline_size=100,
                threshold_low=0.1,
                threshold_medium=0.2,
                threshold_high=0.3,
                threshold_critical=0.5,
                enabled=True,
            )
        ]

        # Prediction confidence drift detection
        configs[DriftComponent.PREDICTION_CONFIDENCE] = [
            DriftDetectionConfig(
                method=DriftDetectionMethod.KOLMOGOROV_SMIRNOV,
                component=DriftComponent.PREDICTION_CONFIDENCE,
                sensitivity=0.7,
                window_size=100,
                baseline_size=500,
                threshold_low=0.05,
                threshold_medium=0.10,
                threshold_high=0.20,
                threshold_critical=0.35,
                enabled=True,
            )
        ]

        return configs

    async def start_drift_detection(self):
        """Start continuous drift detection"""
        if self.running:
            logger.warning("Drift detection is already running")
            return

        self.running = True
        logger.info("Starting model drift detection")

        try:
            # Start detection tasks
            detection_tasks = [
                self._run_drift_detection_loop(),
                self._run_adaptive_threshold_management(),
                self._run_baseline_update_management(),
                self._run_drift_pattern_analysis(),
            ]

            await asyncio.gather(*detection_tasks)

        except Exception as e:
            logger.error(f"Drift detection failed: {e}")
            self.running = False
            raise
        finally:
            logger.info("Drift detection stopped")

    async def stop_drift_detection(self):
        """Stop drift detection"""
        self.running = False
        logger.info("Stopping drift detection")

    async def _run_drift_detection_loop(self):
        """Main drift detection loop"""
        while self.running:
            try:
                await asyncio.sleep(self.detection_interval_seconds)

                if not self.running:
                    break

                # Run drift detection for all configured components
                for component in DriftComponent:
                    if component in self.detection_configs:
                        await self._detect_component_drift(component)

                self.last_detection_time = datetime.utcnow()

            except Exception as e:
                logger.error(f"Drift detection loop error: {e}")
                await asyncio.sleep(60)

    async def _detect_component_drift(self, component: DriftComponent):
        """Detect drift for a specific component"""
        try:
            if not self.baseline_established.get(component, False):
                logger.debug(f"Baseline not established for {component.value}")
                return

            configs = self.detection_configs.get(component, [])
            if not configs:
                return

            # Get current data for the component
            current_data = await self._collect_current_data(component)
            if not current_data:
                return

            # Update current window
            if component not in self.current_windows:
                self.current_windows[component] = deque(
                    maxlen=max(config.window_size for config in configs)
                )

            self.current_windows[component].append(current_data)

            # Check if we have enough data for detection
            min_window_size = min(
                config.window_size for config in configs if config.enabled
            )
            if len(self.current_windows[component]) < min_window_size:
                return

            # Run drift detection with all enabled methods
            detection_results = {}
            feature_results = []

            for config in configs:
                if not config.enabled:
                    continue

                # Perform drift detection
                result = await self._perform_drift_detection(component, config)
                if result:
                    detection_results[config.method] = result["overall_score"]
                    if "feature_results" in result:
                        feature_results.extend(result["feature_results"])

            if detection_results:
                # Combine results and determine overall drift
                overall_result = await self._combine_detection_results(
                    component, detection_results, feature_results
                )

                if (
                    overall_result
                    and overall_result.overall_severity != DriftSeverity.NONE
                ):
                    await self._handle_drift_detection(overall_result)

        except Exception as e:
            logger.error(f"Component drift detection failed for {component.value}: {e}")

    async def _collect_current_data(
        self, component: DriftComponent
    ) -> Optional[dict[str, Any]]:
        """Collect current data for drift detection"""
        try:
            current_time = datetime.utcnow()

            # Simulate data collection based on component type
            if component == DriftComponent.INPUT_FEATURES:
                # Simulate feature data collection
                data = {
                    "timestamp": current_time,
                    "features": {
                        f"feature_{i}": np.random.normal(0, 1) for i in range(20)
                    },
                    "feature_importance": {
                        f"feature_{i}": np.random.uniform(0, 1) for i in range(20)
                    },
                }

            elif component == DriftComponent.PREDICTIONS:
                # Simulate prediction data collection
                data = {
                    "timestamp": current_time,
                    "predictions": np.random.uniform(0, 1, 50).tolist(),
                    "prediction_probabilities": np.random.uniform(0, 1, 50).tolist(),
                }

            elif component == DriftComponent.MODEL_PERFORMANCE:
                # Simulate performance metrics collection
                data = {
                    "timestamp": current_time,
                    "accuracy": np.random.normal(0.92, 0.02),
                    "precision": np.random.normal(0.88, 0.03),
                    "recall": np.random.normal(0.86, 0.03),
                    "f1_score": np.random.normal(0.87, 0.02),
                }

            elif component == DriftComponent.PREDICTION_CONFIDENCE:
                # Simulate confidence score collection
                data = {
                    "timestamp": current_time,
                    "confidence_scores": np.random.uniform(0.6, 0.99, 50).tolist(),
                    "low_confidence_rate": np.random.uniform(0.05, 0.15),
                }

            elif component == DriftComponent.FEATURE_IMPORTANCE:
                # Simulate feature importance collection
                importance_scores = np.random.dirichlet(np.ones(20))
                data = {
                    "timestamp": current_time,
                    "feature_importance": {
                        f"feature_{i}": importance_scores[i] for i in range(20)
                    },
                }

            else:
                return None

            return data

        except Exception as e:
            logger.error(f"Data collection failed for {component.value}: {e}")
            return None

    async def _perform_drift_detection(
        self, component: DriftComponent, config: DriftDetectionConfig
    ) -> Optional[dict[str, Any]]:
        """Perform drift detection using specified method"""
        try:
            baseline_data = self.baseline_data.get(component, [])
            current_data = list(self.current_windows[component])[-config.window_size :]

            if (
                len(baseline_data) < config.baseline_size
                or len(current_data) < config.window_size
            ):
                return None

            # Perform detection based on method
            if config.method == DriftDetectionMethod.KOLMOGOROV_SMIRNOV:
                return await self._ks_drift_detection(
                    baseline_data, current_data, config
                )
            elif config.method == DriftDetectionMethod.POPULATION_STABILITY_INDEX:
                return await self._psi_drift_detection(
                    baseline_data, current_data, config
                )
            elif config.method == DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE:
                return await self._js_drift_detection(
                    baseline_data, current_data, config
                )
            elif config.method == DriftDetectionMethod.MAXIMUM_MEAN_DISCREPANCY:
                return await self._mmd_drift_detection(
                    baseline_data, current_data, config
                )
            elif config.method == DriftDetectionMethod.STATISTICAL_DISTANCE:
                return await self._statistical_distance_detection(
                    baseline_data, current_data, config
                )
            else:
                logger.warning(f"Unknown drift detection method: {config.method}")
                return None

        except Exception as e:
            logger.error(
                f"Drift detection failed with method {config.method.value}: {e}"
            )
            return None

    async def _ks_drift_detection(
        self,
        baseline_data: list[dict],
        current_data: list[dict],
        config: DriftDetectionConfig,
    ) -> dict[str, Any]:
        """Kolmogorov-Smirnov drift detection"""
        feature_results = []
        overall_scores = []

        # Extract features for comparison
        if config.component == DriftComponent.INPUT_FEATURES:
            # Get all feature names
            all_features = set()
            for data_point in baseline_data + current_data:
                if "features" in data_point:
                    all_features.update(data_point["features"].keys())

            for feature_name in all_features:
                baseline_values = [
                    data_point["features"].get(feature_name, 0)
                    for data_point in baseline_data
                    if "features" in data_point
                    and feature_name in data_point["features"]
                ]
                current_values = [
                    data_point["features"].get(feature_name, 0)
                    for data_point in current_data
                    if "features" in data_point
                    and feature_name in data_point["features"]
                ]

                if len(baseline_values) < 10 or len(current_values) < 10:
                    continue

                # Simplified KS test (would use scipy.stats.ks_2samp in practice)
                ks_statistic = self._calculate_ks_statistic(
                    baseline_values, current_values
                )
                p_value = self._estimate_ks_p_value(
                    ks_statistic, len(baseline_values), len(current_values)
                )

                # Determine severity
                severity = self._determine_severity_from_score(ks_statistic, config)

                feature_result = FeatureDriftResult(
                    feature_name=feature_name,
                    drift_score=ks_statistic,
                    severity=severity,
                    method_used=config.method,
                    baseline_statistics={
                        "mean": statistics.mean(baseline_values),
                        "std": (
                            statistics.stdev(baseline_values)
                            if len(baseline_values) > 1
                            else 0
                        ),
                        "min": min(baseline_values),
                        "max": max(baseline_values),
                    },
                    current_statistics={
                        "mean": statistics.mean(current_values),
                        "std": (
                            statistics.stdev(current_values)
                            if len(current_values) > 1
                            else 0
                        ),
                        "min": min(current_values),
                        "max": max(current_values),
                    },
                    p_value=p_value,
                    effect_size=ks_statistic,
                    recommendations=self._get_feature_drift_recommendations(
                        feature_name, ks_statistic, severity
                    ),
                )

                feature_results.append(feature_result)
                overall_scores.append(ks_statistic)

        elif config.component == DriftComponent.PREDICTIONS:
            # Handle prediction drift
            baseline_predictions = [
                pred
                for data_point in baseline_data
                for pred in data_point.get("predictions", [])
            ]
            current_predictions = [
                pred
                for data_point in current_data
                for pred in data_point.get("predictions", [])
            ]

            if baseline_predictions and current_predictions:
                ks_statistic = self._calculate_ks_statistic(
                    baseline_predictions, current_predictions
                )
                overall_scores.append(ks_statistic)

        overall_score = max(overall_scores) if overall_scores else 0

        return {
            "overall_score": overall_score,
            "feature_results": feature_results,
            "method": config.method,
            "component": config.component,
        }

    def _calculate_ks_statistic(
        self, sample1: list[float], sample2: list[float]
    ) -> float:
        """Calculate Kolmogorov-Smirnov statistic"""
        try:
            # Sort both samples
            sorted1 = sorted(sample1)
            sorted2 = sorted(sample2)

            # Combine and sort all values
            all_values = sorted(set(sorted1 + sorted2))

            n1, n2 = len(sample1), len(sample2)
            max_diff = 0

            for value in all_values:
                # Calculate empirical CDFs
                cdf1 = sum(1 for x in sorted1 if x <= value) / n1
                cdf2 = sum(1 for x in sorted2 if x <= value) / n2

                diff = abs(cdf1 - cdf2)
                max_diff = max(max_diff, diff)

            return max_diff

        except Exception:
            return 0.0

    def _estimate_ks_p_value(self, ks_statistic: float, n1: int, n2: int) -> float:
        """Estimate p-value for KS test (simplified)"""
        try:
            effective_n = (n1 * n2) / (n1 + n2)
            lambda_val = (
                math.sqrt(effective_n) + 0.12 + 0.11 / math.sqrt(effective_n)
            ) * ks_statistic

            # Simplified p-value estimation
            if lambda_val >= 1.36:
                return 2 * math.exp(-2 * lambda_val * lambda_val)
            else:
                return 1.0

        except Exception:
            return 1.0

    async def _psi_drift_detection(
        self,
        baseline_data: list[dict],
        current_data: list[dict],
        config: DriftDetectionConfig,
    ) -> dict[str, Any]:
        """Population Stability Index drift detection"""
        feature_results = []
        overall_scores = []

        if config.component == DriftComponent.INPUT_FEATURES:
            # Get all feature names
            all_features = set()
            for data_point in baseline_data + current_data:
                if "features" in data_point:
                    all_features.update(data_point["features"].keys())

            for feature_name in all_features:
                baseline_values = [
                    data_point["features"].get(feature_name, 0)
                    for data_point in baseline_data
                    if "features" in data_point
                    and feature_name in data_point["features"]
                ]
                current_values = [
                    data_point["features"].get(feature_name, 0)
                    for data_point in current_data
                    if "features" in data_point
                    and feature_name in data_point["features"]
                ]

                if len(baseline_values) < 10 or len(current_values) < 10:
                    continue

                # Calculate PSI
                psi_score = self._calculate_psi(baseline_values, current_values)
                severity = self._determine_severity_from_score(psi_score, config)

                feature_result = FeatureDriftResult(
                    feature_name=feature_name,
                    drift_score=psi_score,
                    severity=severity,
                    method_used=config.method,
                    baseline_statistics={"mean": statistics.mean(baseline_values)},
                    current_statistics={"mean": statistics.mean(current_values)},
                    p_value=None,
                    effect_size=psi_score,
                    recommendations=self._get_feature_drift_recommendations(
                        feature_name, psi_score, severity
                    ),
                )

                feature_results.append(feature_result)
                overall_scores.append(psi_score)

        overall_score = max(overall_scores) if overall_scores else 0

        return {
            "overall_score": overall_score,
            "feature_results": feature_results,
            "method": config.method,
            "component": config.component,
        }

    def _calculate_psi(
        self, baseline: list[float], current: list[float], num_bins: int = 10
    ) -> float:
        """Calculate Population Stability Index"""
        try:
            # Determine bin edges from baseline distribution
            min_val = min(min(baseline), min(current))
            max_val = max(max(baseline), max(current))

            if min_val == max_val:
                return 0.0

            bin_edges = np.linspace(min_val, max_val, num_bins + 1)

            # Calculate baseline distribution
            baseline_hist, _ = np.histogram(baseline, bins=bin_edges, density=True)
            current_hist, _ = np.histogram(current, bins=bin_edges, density=True)

            # Normalize to get proportions
            baseline_props = baseline_hist / np.sum(baseline_hist)
            current_props = current_hist / np.sum(current_hist)

            # Calculate PSI
            psi = 0
            for i in range(len(baseline_props)):
                if baseline_props[i] > 0 and current_props[i] > 0:
                    psi += (current_props[i] - baseline_props[i]) * np.log(
                        current_props[i] / baseline_props[i]
                    )

            return abs(psi)

        except Exception:
            return 0.0

    async def _js_drift_detection(
        self,
        baseline_data: list[dict],
        current_data: list[dict],
        config: DriftDetectionConfig,
    ) -> dict[str, Any]:
        """Jensen-Shannon divergence drift detection"""
        overall_scores = []

        if config.component == DriftComponent.PREDICTIONS:
            baseline_predictions = [
                pred
                for data_point in baseline_data
                for pred in data_point.get("predictions", [])
            ]
            current_predictions = [
                pred
                for data_point in current_data
                for pred in data_point.get("predictions", [])
            ]

            if baseline_predictions and current_predictions:
                js_divergence = self._calculate_js_divergence(
                    baseline_predictions, current_predictions
                )
                overall_scores.append(js_divergence)

        overall_score = max(overall_scores) if overall_scores else 0

        return {
            "overall_score": overall_score,
            "feature_results": [],
            "method": config.method,
            "component": config.component,
        }

    def _calculate_js_divergence(
        self, baseline: list[float], current: list[float], num_bins: int = 20
    ) -> float:
        """Calculate Jensen-Shannon divergence"""
        try:
            # Create histograms
            min_val = min(min(baseline), min(current))
            max_val = max(max(baseline), max(current))

            if min_val == max_val:
                return 0.0

            bin_edges = np.linspace(min_val, max_val, num_bins + 1)

            baseline_hist, _ = np.histogram(baseline, bins=bin_edges, density=True)
            current_hist, _ = np.histogram(current, bins=bin_edges, density=True)

            # Normalize
            baseline_dist = baseline_hist / np.sum(baseline_hist)
            current_dist = current_hist / np.sum(current_hist)

            # Add small epsilon to avoid log(0)
            epsilon = 1e-10
            baseline_dist += epsilon
            current_dist += epsilon

            # Calculate M = (P + Q) / 2
            m_dist = (baseline_dist + current_dist) / 2

            # Calculate KL divergences
            kl_pm = np.sum(baseline_dist * np.log(baseline_dist / m_dist))
            kl_qm = np.sum(current_dist * np.log(current_dist / m_dist))

            # JS divergence
            js_divergence = 0.5 * (kl_pm + kl_qm)

            return js_divergence

        except Exception:
            return 0.0

    async def _mmd_drift_detection(
        self,
        baseline_data: list[dict],
        current_data: list[dict],
        config: DriftDetectionConfig,
    ) -> dict[str, Any]:
        """Maximum Mean Discrepancy drift detection"""
        overall_scores = []

        if config.component == DriftComponent.FEATURE_IMPORTANCE:
            # Extract feature importance vectors
            baseline_importance = []
            current_importance = []

            for data_point in baseline_data:
                if "feature_importance" in data_point:
                    importance_vector = list(data_point["feature_importance"].values())
                    baseline_importance.append(importance_vector)

            for data_point in current_data:
                if "feature_importance" in data_point:
                    importance_vector = list(data_point["feature_importance"].values())
                    current_importance.append(importance_vector)

            if baseline_importance and current_importance:
                mmd_score = self._calculate_mmd(baseline_importance, current_importance)
                overall_scores.append(mmd_score)

        overall_score = max(overall_scores) if overall_scores else 0

        return {
            "overall_score": overall_score,
            "feature_results": [],
            "method": config.method,
            "component": config.component,
        }

    def _calculate_mmd(
        self, baseline: list[list[float]], current: list[list[float]]
    ) -> float:
        """Calculate Maximum Mean Discrepancy (simplified RBF kernel)"""
        try:
            baseline_array = np.array(baseline)
            current_array = np.array(current)

            if baseline_array.size == 0 or current_array.size == 0:
                return 0.0

            # Calculate mean embeddings
            baseline_mean = np.mean(baseline_array, axis=0)
            current_mean = np.mean(current_array, axis=0)

            # Simplified MMD using Euclidean distance
            mmd_score = np.linalg.norm(baseline_mean - current_mean)

            return mmd_score

        except Exception:
            return 0.0

    async def _statistical_distance_detection(
        self,
        baseline_data: list[dict],
        current_data: list[dict],
        config: DriftDetectionConfig,
    ) -> dict[str, Any]:
        """Statistical distance drift detection for performance metrics"""
        overall_scores = []

        if config.component == DriftComponent.MODEL_PERFORMANCE:
            performance_metrics = ["accuracy", "precision", "recall", "f1_score"]

            for metric in performance_metrics:
                baseline_values = [
                    data_point.get(metric, 0)
                    for data_point in baseline_data
                    if metric in data_point
                ]
                current_values = [
                    data_point.get(metric, 0)
                    for data_point in current_data
                    if metric in data_point
                ]

                if len(baseline_values) > 1 and len(current_values) > 1:
                    # Calculate standardized mean difference
                    baseline_mean = statistics.mean(baseline_values)
                    current_mean = statistics.mean(current_values)
                    pooled_std = math.sqrt(
                        (
                            statistics.variance(baseline_values)
                            + statistics.variance(current_values)
                        )
                        / 2
                    )

                    if pooled_std > 0:
                        cohen_d = abs(baseline_mean - current_mean) / pooled_std
                        overall_scores.append(cohen_d)

        overall_score = max(overall_scores) if overall_scores else 0

        return {
            "overall_score": overall_score,
            "feature_results": [],
            "method": config.method,
            "component": config.component,
        }

    def _determine_severity_from_score(
        self, score: float, config: DriftDetectionConfig
    ) -> DriftSeverity:
        """Determine drift severity from score and thresholds"""
        if score >= config.threshold_critical:
            return DriftSeverity.CRITICAL
        elif score >= config.threshold_high:
            return DriftSeverity.HIGH
        elif score >= config.threshold_medium:
            return DriftSeverity.MEDIUM
        elif score >= config.threshold_low:
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NONE

    def _get_feature_drift_recommendations(
        self, feature_name: str, drift_score: float, severity: DriftSeverity
    ) -> list[str]:
        """Get recommendations for feature drift"""
        recommendations = []

        if severity == DriftSeverity.CRITICAL:
            recommendations.extend([
                f"URGENT: Investigate {feature_name} data source immediately",
                f"Consider emergency model rollback for {feature_name}",
                f"Implement immediate monitoring for {feature_name}",
            ])
        elif severity == DriftSeverity.HIGH:
            recommendations.extend([
                f"Review data collection process for {feature_name}",
                f"Consider feature engineering adjustments for {feature_name}",
                f"Increase monitoring frequency for {feature_name}",
            ])
        elif severity == DriftSeverity.MEDIUM:
            recommendations.extend([
                f"Monitor {feature_name} trends closely",
                f"Consider retraining with recent data including {feature_name}",
                f"Review feature importance of {feature_name}",
            ])
        elif severity == DriftSeverity.LOW:
            recommendations.extend([
                f"Continue standard monitoring for {feature_name}",
                f"Document drift pattern for {feature_name}",
            ])

        return recommendations

    async def _combine_detection_results(
        self,
        component: DriftComponent,
        detection_results: dict[DriftDetectionMethod, float],
        feature_results: list[FeatureDriftResult],
    ) -> Optional[DriftDetectionResult]:
        """Combine multiple detection method results"""
        try:
            if not detection_results:
                return None

            # Calculate overall drift score (weighted average)
            method_weights = {
                DriftDetectionMethod.KOLMOGOROV_SMIRNOV: 0.3,
                DriftDetectionMethod.POPULATION_STABILITY_INDEX: 0.25,
                DriftDetectionMethod.JENSEN_SHANNON_DIVERGENCE: 0.2,
                DriftDetectionMethod.MAXIMUM_MEAN_DISCREPANCY: 0.15,
                DriftDetectionMethod.STATISTICAL_DISTANCE: 0.1,
            }

            weighted_score = 0
            total_weight = 0

            for method, score in detection_results.items():
                weight = method_weights.get(method, 0.1)
                weighted_score += score * weight
                total_weight += weight

            overall_drift_score = (
                weighted_score / total_weight if total_weight > 0 else 0
            )

            # Determine overall severity
            overall_severity = DriftSeverity.NONE
            max_score = max(detection_results.values())

            # Use the most sensitive threshold from enabled configs
            configs = [
                config
                for config in self.detection_configs.get(component, [])
                if config.enabled
            ]
            if configs:
                sample_config = configs[0]  # Use first config's thresholds
                overall_severity = self._determine_severity_from_score(
                    max_score, sample_config
                )

            # Generate remediation plan
            remediation_plan = self._generate_remediation_plan(
                component, overall_severity, feature_results
            )

            # Calculate confidence
            confidence = self._calculate_detection_confidence(
                detection_results, feature_results
            )

            # Determine if immediate action is required
            requires_immediate_action = overall_severity in [
                DriftSeverity.HIGH,
                DriftSeverity.CRITICAL,
            ] or any(fr.severity == DriftSeverity.CRITICAL for fr in feature_results)

            current_time = datetime.utcnow()

            result = DriftDetectionResult(
                detection_id=str(uuid.uuid4()),
                timestamp=current_time,
                component=component,
                overall_drift_score=overall_drift_score,
                overall_severity=overall_severity,
                feature_results=feature_results,
                method_results=detection_results,
                baseline_period=(
                    current_time - timedelta(days=7),  # Approximate baseline period
                    current_time - timedelta(days=1),
                ),
                detection_period=(current_time - timedelta(hours=1), current_time),
                statistical_summary={
                    "methods_used": list(detection_results.keys()),
                    "features_analyzed": len(feature_results),
                    "max_drift_score": max_score,
                    "min_drift_score": min(detection_results.values()),
                    "score_variance": (
                        statistics.variance(detection_results.values())
                        if len(detection_results) > 1
                        else 0
                    ),
                },
                remediation_plan=remediation_plan,
                confidence=confidence,
                requires_immediate_action=requires_immediate_action,
            )

            return result

        except Exception as e:
            logger.error(f"Failed to combine detection results: {e}")
            return None

    def _generate_remediation_plan(
        self,
        component: DriftComponent,
        severity: DriftSeverity,
        feature_results: list[FeatureDriftResult],
    ) -> list[str]:
        """Generate remediation plan based on drift detection results"""
        plan = []

        # Component-specific recommendations
        if component == DriftComponent.INPUT_FEATURES:
            if severity == DriftSeverity.CRITICAL:
                plan.extend([
                    "IMMEDIATE: Stop model predictions and investigate data sources",
                    "Contact data engineering team to verify data pipeline integrity",
                    "Implement emergency data validation checks",
                    "Consider rolling back to previous model version",
                ])
            elif severity == DriftSeverity.HIGH:
                plan.extend([
                    "Investigate data source changes in the last 24-48 hours",
                    "Review feature engineering pipeline for issues",
                    "Increase data quality monitoring frequency",
                    "Prepare for potential model retraining",
                ])
            elif severity == DriftSeverity.MEDIUM:
                plan.extend([
                    "Monitor data sources for continued drift",
                    "Review recent changes to data collection processes",
                    "Consider gradual model adaptation strategies",
                    "Schedule model performance review",
                ])

        elif component == DriftComponent.PREDICTIONS:
            if severity >= DriftSeverity.HIGH:
                plan.extend([
                    "Review model outputs for accuracy and bias",
                    "Implement additional prediction validation checks",
                    "Consider adjusting prediction confidence thresholds",
                    "Increase human oversight for predictions",
                ])

        elif component == DriftComponent.MODEL_PERFORMANCE:
            if severity >= DriftSeverity.HIGH:
                plan.extend([
                    "Conduct comprehensive model evaluation",
                    "Review recent model updates or configuration changes",
                    "Check for infrastructure or resource constraints",
                    (
                        "Consider emergency model rollback if performance continues to"
                        " degrade"
                    ),
                ])

        # Feature-specific recommendations
        critical_features = [
            fr.feature_name
            for fr in feature_results
            if fr.severity == DriftSeverity.CRITICAL
        ]
        if critical_features:
            plan.append(
                "CRITICAL FEATURES: Immediately investigate"
                f" {', '.join(critical_features)}"
            )

        # General recommendations
        plan.extend([
            "Document drift incident for future reference",
            "Update monitoring thresholds based on findings",
            "Schedule post-incident review meeting",
            "Consider implementing additional preventive measures",
        ])

        return plan

    def _calculate_detection_confidence(
        self,
        detection_results: dict[DriftDetectionMethod, float],
        feature_results: list[FeatureDriftResult],
    ) -> float:
        """Calculate confidence in drift detection"""
        try:
            # Base confidence on method agreement
            scores = list(detection_results.values())
            if len(scores) <= 1:
                return 0.7  # Medium confidence with single method

            # Calculate coefficient of variation
            mean_score = statistics.mean(scores)
            if mean_score == 0:
                return 0.5

            std_score = statistics.stdev(scores)
            cv = std_score / mean_score

            # Lower CV means higher agreement and confidence
            agreement_confidence = max(0.5, 1.0 - cv)

            # Factor in feature-level evidence
            feature_confidence = 1.0
            if feature_results:
                critical_features = sum(
                    1
                    for fr in feature_results
                    if fr.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]
                )
                total_features = len(feature_results)
                feature_confidence = 0.5 + 0.5 * (critical_features / total_features)

            # Combine confidences
            overall_confidence = (agreement_confidence + feature_confidence) / 2

            return min(1.0, max(0.0, overall_confidence))

        except Exception:
            return 0.5

    async def _handle_drift_detection(self, result: DriftDetectionResult):
        """Handle detected drift with alerting and logging"""
        try:
            # Store result
            self.detection_results[result.detection_id] = result
            self.drift_history.append(result)

            # Create drift alert
            alert = await self._create_drift_alert(result)

            # Send alert
            await self.alerting.send_alert(
                f"model_drift_{result.component.value}",
                alert.message,
                severity=alert.alert_level,
            )

            # Log drift detection
            await self.audit_logger.log_compliance_event({
                "event_type": "model_drift_detected",
                "detection_id": result.detection_id,
                "component": result.component.value,
                "overall_severity": result.overall_severity.value,
                "overall_score": result.overall_drift_score,
                "confidence": result.confidence,
                "requires_immediate_action": result.requires_immediate_action,
                "methods_used": [
                    method.value for method in result.method_results.keys()
                ],
                "features_affected": len(result.feature_results),
                "timestamp": result.timestamp.isoformat(),
            })

            # Log feature-level drift
            for feature_result in result.feature_results:
                if feature_result.severity != DriftSeverity.NONE:
                    await self.audit_logger.log_compliance_event({
                        "event_type": "feature_drift_detected",
                        "detection_id": result.detection_id,
                        "feature_name": feature_result.feature_name,
                        "drift_score": feature_result.drift_score,
                        "severity": feature_result.severity.value,
                        "method": feature_result.method_used.value,
                        "timestamp": result.timestamp.isoformat(),
                    })

        except Exception as e:
            logger.error(f"Failed to handle drift detection: {e}")

    async def _create_drift_alert(self, result: DriftDetectionResult) -> DriftAlert:
        """Create drift alert from detection result"""
        # Determine alert level
        alert_level_map = {
            DriftSeverity.NONE: "info",
            DriftSeverity.LOW: "low",
            DriftSeverity.MEDIUM: "medium",
            DriftSeverity.HIGH: "high",
            DriftSeverity.CRITICAL: "critical",
        }
        alert_level = alert_level_map[result.overall_severity]

        # Create alert message
        component_name = result.component.value.replace("_", " ").title()
        message = f"Model drift detected in {component_name}: "
        message += f"Severity {result.overall_severity.value.upper()}, "
        message += f"Score {result.overall_drift_score:.3f}, "
        message += f"Confidence {result.confidence:.2%}"

        if result.feature_results:
            critical_features = [
                fr.feature_name
                for fr in result.feature_results
                if fr.severity == DriftSeverity.CRITICAL
            ]
            if critical_features:
                message += f". Critical features: {', '.join(critical_features)}"

        # Determine stakeholders
        stakeholders = ["ml_engineering_team", "data_science_team"]
        if result.overall_severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            stakeholders.extend(["operations_team", "product_team"])

        # Escalation required for critical drift
        escalation_required = result.overall_severity == DriftSeverity.CRITICAL

        alert = DriftAlert(
            alert_id=str(uuid.uuid4()),
            detection_result=result,
            alert_level=alert_level,
            message=message,
            stakeholders=stakeholders,
            recommended_actions=result.remediation_plan[:5],  # Top 5 actions
            escalation_required=escalation_required,
            timestamp=datetime.utcnow(),
        )

        return alert

    async def _run_adaptive_threshold_management(self):
        """Manage adaptive thresholds based on historical performance"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Run every hour

                if not self.running:
                    break

                if self.adaptive_thresholds:
                    await self._update_adaptive_thresholds()

            except Exception as e:
                logger.error(f"Adaptive threshold management error: {e}")
                await asyncio.sleep(300)

    async def _update_adaptive_thresholds(self):
        """Update detection thresholds based on historical false positive rates"""
        try:
            # Analyze recent detection history
            recent_detections = [
                result
                for result in self.drift_history
                if result.timestamp >= datetime.utcnow() - timedelta(days=7)
            ]

            if len(recent_detections) < 10:
                return  # Not enough data for adaptation

            # Calculate false positive rate proxy (detections that didn't require action)
            false_positives = sum(
                1
                for result in recent_detections
                if not result.requires_immediate_action
                and result.overall_severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM]
            )

            current_fp_rate = false_positives / len(recent_detections)

            # Adjust thresholds if FP rate is too high
            if current_fp_rate > self.false_positive_rate * 1.5:
                # Increase thresholds to reduce false positives
                adjustment_factor = 1.1
                await self._adjust_all_thresholds(adjustment_factor)

                logger.info(
                    f"Increased drift detection thresholds by {adjustment_factor}x due"
                    f" to high FP rate: {current_fp_rate:.3f}"
                )

            elif current_fp_rate < self.false_positive_rate * 0.5:
                # Decrease thresholds to catch more drift
                adjustment_factor = 0.95
                await self._adjust_all_thresholds(adjustment_factor)

                logger.info(
                    f"Decreased drift detection thresholds by {adjustment_factor}x due"
                    f" to low FP rate: {current_fp_rate:.3f}"
                )

            # Store adaptation history
            self.threshold_adaptation_history.append({
                "timestamp": datetime.utcnow(),
                "fp_rate": current_fp_rate,
                "detections_analyzed": len(recent_detections),
                "adjustment_made": current_fp_rate != self.false_positive_rate,
            })

        except Exception as e:
            logger.error(f"Adaptive threshold update failed: {e}")

    async def _adjust_all_thresholds(self, factor: float):
        """Adjust all detection thresholds by a factor"""
        for component_configs in self.detection_configs.values():
            for config in component_configs:
                config.threshold_low *= factor
                config.threshold_medium *= factor
                config.threshold_high *= factor
                config.threshold_critical *= factor

    async def _run_baseline_update_management(self):
        """Manage baseline updates"""
        while self.running:
            try:
                await asyncio.sleep(86400)  # Run daily

                if not self.running:
                    break

                if self.auto_baseline_update:
                    await self._update_baselines()

            except Exception as e:
                logger.error(f"Baseline update management error: {e}")
                await asyncio.sleep(3600)

    async def _update_baselines(self):
        """Update baselines with recent stable data"""
        try:
            # Only update if system has been stable (no high/critical drift in last 7 days)
            recent_critical_drift = [
                result
                for result in self.drift_history
                if (
                    result.timestamp >= datetime.utcnow() - timedelta(days=7)
                    and result.overall_severity
                    in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]
                )
            ]

            if recent_critical_drift:
                logger.info("Skipping baseline update due to recent critical drift")
                return

            # Update baselines with recent stable data
            for component in DriftComponent:
                if (
                    component in self.current_windows
                    and len(self.current_windows[component]) > 100
                ):
                    # Use recent stable data as new baseline
                    recent_stable_data = list(self.current_windows[component])[
                        -500:
                    ]  # Last 500 data points

                    if component not in self.baseline_data:
                        self.baseline_data[component] = []

                    # Replace baseline with recent stable data
                    self.baseline_data[component] = recent_stable_data
                    self.baseline_established[component] = True

                    logger.info(
                        f"Updated baseline for {component.value} with"
                        f" {len(recent_stable_data)} data points"
                    )

            await self.audit_logger.log_compliance_event({
                "event_type": "baseline_updated",
                "components_updated": [
                    component.value
                    for component in DriftComponent
                    if component in self.baseline_data
                ],
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            logger.error(f"Baseline update failed: {e}")

    async def _run_drift_pattern_analysis(self):
        """Analyze drift patterns for insights"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Run every hour

                if not self.running:
                    break

                await self._analyze_drift_patterns()

            except Exception as e:
                logger.error(f"Drift pattern analysis error: {e}")
                await asyncio.sleep(300)

    async def _analyze_drift_patterns(self):
        """Analyze patterns in drift detection"""
        try:
            if len(self.drift_history) < 10:
                return

            # Analyze temporal patterns
            recent_drift = list(self.drift_history)[-100:]  # Last 100 detections

            # Component drift frequency
            component_counts = {}
            for result in recent_drift:
                component = result.component.value
                component_counts[component] = component_counts.get(component, 0) + 1

            # Time-based patterns
            hourly_counts = {}
            for result in recent_drift:
                hour = result.timestamp.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

            # Severity trends
            severity_trends = []
            for result in recent_drift:
                severity_trends.append(result.overall_severity.value)

            # Log pattern analysis
            await self.audit_logger.log_compliance_event({
                "event_type": "drift_pattern_analysis",
                "analysis_period_detections": len(recent_drift),
                "component_frequency": component_counts,
                "hourly_distribution": hourly_counts,
                "severity_distribution": {
                    severity.value: severity_trends.count(severity.value)
                    for severity in DriftSeverity
                },
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            logger.error(f"Drift pattern analysis failed: {e}")

    # Public methods for baseline management and status

    async def establish_baseline(
        self, component: DriftComponent, baseline_data: list[dict[str, Any]]
    ):
        """Establish baseline for a specific component"""
        try:
            self.baseline_data[component] = baseline_data
            self.baseline_established[component] = True

            logger.info(
                f"Baseline established for {component.value} with"
                f" {len(baseline_data)} data points"
            )

            await self.audit_logger.log_compliance_event({
                "event_type": "baseline_established",
                "component": component.value,
                "baseline_size": len(baseline_data),
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            logger.error(f"Failed to establish baseline for {component.value}: {e}")
            raise

    def get_drift_status(self) -> dict[str, Any]:
        """Get current drift detection status"""
        current_time = datetime.utcnow()

        # Recent drift summary
        recent_drift = [
            result
            for result in self.drift_history
            if result.timestamp >= current_time - timedelta(hours=24)
        ]

        return {
            "detection_status": {
                "running": self.running,
                "last_detection_time": self.last_detection_time.isoformat(),
                "detection_interval_seconds": self.detection_interval_seconds,
            },
            "baseline_status": {
                component.value: {
                    "established": self.baseline_established.get(component, False),
                    "size": len(self.baseline_data.get(component, [])),
                }
                for component in DriftComponent
            },
            "recent_drift_summary": {
                "total_detections_24h": len(recent_drift),
                "by_component": {
                    component.value: len([
                        r for r in recent_drift if r.component == component
                    ])
                    for component in DriftComponent
                },
                "by_severity": {
                    severity.value: len([
                        r for r in recent_drift if r.overall_severity == severity
                    ])
                    for severity in DriftSeverity
                },
                "requires_immediate_action": sum(
                    1 for r in recent_drift if r.requires_immediate_action
                ),
            },
            "system_health": {
                "total_drift_history": len(self.drift_history),
                "adaptive_thresholds_enabled": self.adaptive_thresholds,
                "auto_baseline_update_enabled": self.auto_baseline_update,
                "current_window_sizes": {
                    component.value: len(window)
                    for component, window in self.current_windows.items()
                },
            },
        }


# Example usage
async def example_usage():
    """Example of using the model drift detector"""
    # Initialize detector
    detector = ModelDriftDetector({
        "detection_interval_seconds": 60,
        "adaptive_thresholds": True,
        "auto_baseline_update": False,
    })

    # Establish baselines for components
    for component in [DriftComponent.INPUT_FEATURES, DriftComponent.PREDICTIONS]:
        baseline_data = []
        for i in range(1000):
            if component == DriftComponent.INPUT_FEATURES:
                data = {
                    "timestamp": datetime.utcnow() - timedelta(days=10 - i * 0.01),
                    "features": {
                        f"feature_{j}": np.random.normal(0, 1) for j in range(20)
                    },
                }
            else:  # PREDICTIONS
                data = {
                    "timestamp": datetime.utcnow() - timedelta(days=10 - i * 0.01),
                    "predictions": np.random.uniform(0, 1, 10).tolist(),
                }
            baseline_data.append(data)

        await detector.establish_baseline(component, baseline_data)

    # Start drift detection (would run continuously in production)
    logger.info("Starting drift detection demo")
    detection_task = asyncio.create_task(detector.start_drift_detection())

    # Let it run for a short period
    await asyncio.sleep(30)

    # Stop detection
    await detector.stop_drift_detection()
    detection_task.cancel()

    # Get status
    status = detector.get_drift_status()
    logger.info(f"Drift detection status: {status}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
