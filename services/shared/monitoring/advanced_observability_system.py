"""
Advanced Monitoring and Observability System

This module implements advanced monitoring with:
- Predictive analytics for performance forecasting
- Machine learning-based anomaly detection
- Real-time performance optimization recommendations
- Intelligent alerting with context-aware notifications
- Constitutional compliance monitoring

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import redis.asyncio as redis
from collections import deque, defaultdict

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(str, Enum):
    """Types of metrics to monitor."""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    CONSTITUTIONAL = "constitutional"
    SECURITY = "security"
    BUSINESS = "business"


class AnomalyType(str, Enum):
    """Types of anomalies."""
    STATISTICAL = "statistical"
    TREND = "trend"
    SEASONAL = "seasonal"
    CONTEXTUAL = "contextual"


@dataclass
class MetricPoint:
    """A single metric data point."""
    timestamp: datetime
    value: float
    metric_name: str
    labels: Dict[str, str] = field(default_factory=dict)
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class Anomaly:
    """Detected anomaly information."""
    metric_name: str
    timestamp: datetime
    value: float
    expected_value: float
    anomaly_score: float
    anomaly_type: AnomalyType
    severity: AlertSeverity
    context: Dict[str, Any] = field(default_factory=dict)
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class PredictionResult:
    """Prediction result for a metric."""
    metric_name: str
    predicted_values: List[float]
    prediction_timestamps: List[datetime]
    confidence_intervals: List[Tuple[float, float]]
    prediction_horizon_minutes: int
    model_accuracy: float
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    recommendation_id: str
    title: str
    description: str
    metric_name: str
    current_value: float
    target_value: float
    expected_improvement: float
    implementation_effort: str
    priority: AlertSeverity
    action_items: List[str]
    estimated_impact: Dict[str, float]
    constitutional_compliance_impact: float
    constitutional_hash: str = CONSTITUTIONAL_HASH


class PredictiveAnalyticsEngine:
    """Predictive analytics engine for performance forecasting with Redis storage."""

    def __init__(self, history_window_hours: int = 24, redis_url: str = "redis://localhost:6389"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.history_window_hours = history_window_hours
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.prediction_models: Dict[str, Dict[str, Any]] = {}

        # Redis connection for persistent storage
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.redis_key_prefix = "acgs:observability:metrics"

        logger.info("Initialized Predictive Analytics Engine with Redis storage")

    async def connect_redis(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis for observability data storage")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Using in-memory storage only.")
            self.redis_client = None

    async def disconnect_redis(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def add_metric_point(self, metric_point: MetricPoint):
        """Add a metric point to the history and Redis."""
        # Add to in-memory history
        self.metric_history[metric_point.metric_name].append(metric_point)

        # Store in Redis for persistence
        if self.redis_client:
            try:
                redis_key = f"{self.redis_key_prefix}:{metric_point.metric_name}"
                metric_data = {
                    "timestamp": metric_point.timestamp.isoformat(),
                    "value": metric_point.value,
                    "labels": json.dumps(metric_point.labels),
                    "constitutional_hash": metric_point.constitutional_hash
                }

                # Store as sorted set with timestamp as score for time-based queries
                await self.redis_client.zadd(
                    redis_key,
                    {json.dumps(metric_data): metric_point.timestamp.timestamp()}
                )

                # Keep only recent data (last 24 hours)
                cutoff_time = (metric_point.timestamp - timedelta(hours=self.history_window_hours)).timestamp()
                await self.redis_client.zremrangebyscore(redis_key, 0, cutoff_time)

            except Exception as e:
                logger.warning(f"Failed to store metric in Redis: {e}")

    async def load_metric_history_from_redis(self, metric_name: str) -> List[MetricPoint]:
        """Load metric history from Redis."""
        if not self.redis_client:
            return []

        try:
            redis_key = f"{self.redis_key_prefix}:{metric_name}"

            # Get recent data from Redis
            cutoff_time = (datetime.now() - timedelta(hours=self.history_window_hours)).timestamp()
            raw_data = await self.redis_client.zrangebyscore(redis_key, cutoff_time, "+inf")

            metric_points = []
            for data_str in raw_data:
                try:
                    data = json.loads(data_str)
                    metric_point = MetricPoint(
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        value=data["value"],
                        metric_name=metric_name,
                        labels=json.loads(data["labels"]),
                        constitutional_hash=data["constitutional_hash"]
                    )
                    metric_points.append(metric_point)
                except Exception as e:
                    logger.warning(f"Failed to parse metric data: {e}")

            return metric_points

        except Exception as e:
            logger.warning(f"Failed to load metric history from Redis: {e}")
            return []

    def predict_metric_trend(
        self,
        metric_name: str,
        prediction_horizon_minutes: int = 60
    ) -> Optional[PredictionResult]:
        """Predict future values for a metric using time series analysis."""

        if metric_name not in self.metric_history:
            return None

        history = list(self.metric_history[metric_name])
        if len(history) < 10:
            return None

        # Extract values and timestamps
        values = np.array([point.value for point in history])
        timestamps = [point.timestamp for point in history]

        # Simple linear trend prediction (in production, use more sophisticated models)
        if len(values) >= 2:
            # Calculate trend using linear regression
            x = np.arange(len(values))
            coeffs = np.polyfit(x, values, 1)
            trend_slope = coeffs[0]
            trend_intercept = coeffs[1]

            # Generate predictions
            prediction_steps = prediction_horizon_minutes // 5  # Predict every 5 minutes
            future_x = np.arange(len(values), len(values) + prediction_steps)
            predicted_values = trend_slope * future_x + trend_intercept

            # Generate prediction timestamps
            last_timestamp = timestamps[-1]
            prediction_timestamps = [
                last_timestamp + timedelta(minutes=i * 5)
                for i in range(1, prediction_steps + 1)
            ]

            # Calculate confidence intervals (simplified)
            residuals = values - (trend_slope * x + trend_intercept)
            std_error = np.std(residuals)
            confidence_intervals = [
                (pred - 2 * std_error, pred + 2 * std_error)
                for pred in predicted_values
            ]

            # Calculate model accuracy
            model_accuracy = max(0.0, 1.0 - (std_error / np.mean(values)))

            return PredictionResult(
                metric_name=metric_name,
                predicted_values=predicted_values.tolist(),
                prediction_timestamps=prediction_timestamps,
                confidence_intervals=confidence_intervals,
                prediction_horizon_minutes=prediction_horizon_minutes,
                model_accuracy=model_accuracy
            )

        return None

    def detect_trend_anomalies(self, metric_name: str) -> List[Anomaly]:
        """Detect trend-based anomalies in metrics."""

        anomalies = []

        if metric_name not in self.metric_history:
            return anomalies

        history = list(self.metric_history[metric_name])
        if len(history) < 20:
            return anomalies

        # Get recent values
        recent_values = [point.value for point in history[-10:]]
        historical_values = [point.value for point in history[-20:-10]]

        # Calculate trend changes
        recent_mean = np.mean(recent_values)
        historical_mean = np.mean(historical_values)

        # Detect significant trend changes
        if len(historical_values) > 0:
            historical_std = np.std(historical_values)
            if historical_std > 0:
                trend_change = abs(recent_mean - historical_mean) / historical_std

                if trend_change > 2.0:  # Significant trend change
                    severity = AlertSeverity.HIGH if trend_change > 3.0 else AlertSeverity.MEDIUM

                    anomaly = Anomaly(
                        metric_name=metric_name,
                        timestamp=history[-1].timestamp,
                        value=recent_mean,
                        expected_value=historical_mean,
                        anomaly_score=trend_change,
                        anomaly_type=AnomalyType.TREND,
                        severity=severity,
                        context={
                            "trend_change_magnitude": trend_change,
                            "recent_mean": recent_mean,
                            "historical_mean": historical_mean
                        }
                    )
                    anomalies.append(anomaly)

        return anomalies

    def forecast_resource_needs(self, metric_name: str) -> Dict[str, Any]:
        """Forecast future resource needs based on trends."""

        prediction = self.predict_metric_trend(metric_name, prediction_horizon_minutes=120)

        if not prediction:
            return {}

        # Analyze predicted values
        max_predicted = max(prediction.predicted_values)
        min_predicted = min(prediction.predicted_values)
        avg_predicted = np.mean(prediction.predicted_values)

        # Current value
        current_value = list(self.metric_history[metric_name])[-1].value if self.metric_history[metric_name] else 0

        # Calculate resource recommendations
        recommendations = {}

        if max_predicted > current_value * 1.5:  # 50% increase predicted
            recommendations["scale_up"] = {
                "recommended": True,
                "urgency": "high" if max_predicted > current_value * 2.0 else "medium",
                "predicted_peak": max_predicted,
                "current_value": current_value,
                "increase_factor": max_predicted / current_value if current_value > 0 else 1.0
            }

        if min_predicted < current_value * 0.7:  # 30% decrease predicted
            recommendations["scale_down"] = {
                "recommended": True,
                "potential_savings": (current_value - avg_predicted) / current_value,
                "predicted_minimum": min_predicted,
                "current_value": current_value
            }

        return {
            "metric_name": metric_name,
            "forecast_horizon_minutes": prediction.prediction_horizon_minutes,
            "current_value": current_value,
            "predicted_range": (min_predicted, max_predicted),
            "predicted_average": avg_predicted,
            "model_accuracy": prediction.model_accuracy,
            "recommendations": recommendations,
            "constitutional_hash": self.constitutional_hash
        }


class MLAnomalyDetector:
    """Machine learning-based anomaly detection with Redis storage."""

    def __init__(self, redis_url: str = "redis://localhost:6389"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.metric_models: Dict[str, Dict[str, Any]] = {}
        self.training_data: Dict[str, List[float]] = defaultdict(list)

        # Redis connection for model storage
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.redis_model_prefix = "acgs:observability:models"
        self.redis_training_prefix = "acgs:observability:training"

        logger.info("Initialized ML Anomaly Detector with Redis storage")

    async def connect_redis(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis for anomaly detection models")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Using in-memory storage only.")
            self.redis_client = None

    async def disconnect_redis(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def save_model_to_redis(self, metric_name: str, model_data: Dict[str, Any]):
        """Save trained model to Redis."""
        if self.redis_client:
            try:
                redis_key = f"{self.redis_model_prefix}:{metric_name}"
                await self.redis_client.hset(redis_key, mapping={
                    "model_data": json.dumps(model_data),
                    "constitutional_hash": self.constitutional_hash,
                    "last_updated": datetime.now().isoformat()
                })
                # Set expiration (7 days)
                await self.redis_client.expire(redis_key, 7 * 24 * 3600)
            except Exception as e:
                logger.warning(f"Failed to save model to Redis: {e}")

    async def load_model_from_redis(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Load trained model from Redis."""
        if not self.redis_client:
            return None

        try:
            redis_key = f"{self.redis_model_prefix}:{metric_name}"
            model_info = await self.redis_client.hgetall(redis_key)

            if model_info and "model_data" in model_info:
                return json.loads(model_info["model_data"])
        except Exception as e:
            logger.warning(f"Failed to load model from Redis: {e}")

        return None

    async def save_training_data_to_redis(self, metric_name: str, training_data: List[float]):
        """Save training data to Redis."""
        if self.redis_client:
            try:
                redis_key = f"{self.redis_training_prefix}:{metric_name}"
                # Store as list with timestamp
                data_with_timestamp = {
                    "data": json.dumps(training_data),
                    "timestamp": datetime.now().isoformat(),
                    "constitutional_hash": self.constitutional_hash
                }
                await self.redis_client.hset(redis_key, mapping=data_with_timestamp)
                # Set expiration (3 days)
                await self.redis_client.expire(redis_key, 3 * 24 * 3600)
            except Exception as e:
                logger.warning(f"Failed to save training data to Redis: {e}")

    async def train_model(self, metric_name: str, training_data: List[float]):
        """Train anomaly detection model for a metric."""

        if len(training_data) < 50:
            logger.warning(f"Insufficient training data for {metric_name}")
            return

        # Simple statistical model (in production, use more sophisticated ML models)
        mean = np.mean(training_data)
        std = np.std(training_data)

        # Calculate percentiles for threshold setting
        p95 = np.percentile(training_data, 95)
        p99 = np.percentile(training_data, 99)

        model_data = {
            "mean": float(mean),
            "std": float(std),
            "p95": float(p95),
            "p99": float(p99),
            "training_size": len(training_data),
            "last_trained": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash
        }

        # Store in memory
        self.metric_models[metric_name] = model_data

        # Save to Redis
        await self.save_model_to_redis(metric_name, model_data)
        await self.save_training_data_to_redis(metric_name, training_data)

        logger.info(f"Trained anomaly model for {metric_name} with {len(training_data)} samples")

    def detect_anomalies(self, metric_name: str, value: float) -> List[Anomaly]:
        """Detect anomalies using ML models."""

        anomalies = []

        if metric_name not in self.metric_models:
            # Auto-train if we have enough data
            if len(self.training_data[metric_name]) >= 50:
                self.train_model(metric_name, self.training_data[metric_name])
            else:
                self.training_data[metric_name].append(value)
                return anomalies

        model = self.metric_models[metric_name]

        # Statistical anomaly detection
        z_score = abs(value - model["mean"]) / model["std"] if model["std"] > 0 else 0

        # Determine anomaly severity
        if z_score > 3.0:  # 3 sigma
            severity = AlertSeverity.CRITICAL
            anomaly_type = AnomalyType.STATISTICAL
        elif z_score > 2.5:  # 2.5 sigma
            severity = AlertSeverity.HIGH
            anomaly_type = AnomalyType.STATISTICAL
        elif value > model["p99"]:  # Above 99th percentile
            severity = AlertSeverity.MEDIUM
            anomaly_type = AnomalyType.STATISTICAL
        else:
            # No anomaly detected
            self.training_data[metric_name].append(value)
            return anomalies

        anomaly = Anomaly(
            metric_name=metric_name,
            timestamp=datetime.now(),
            value=value,
            expected_value=model["mean"],
            anomaly_score=z_score,
            anomaly_type=anomaly_type,
            severity=severity,
            context={
                "z_score": z_score,
                "percentile_rank": self._calculate_percentile_rank(value, metric_name),
                "model_stats": {
                    "mean": model["mean"],
                    "std": model["std"],
                    "p95": model["p95"],
                    "p99": model["p99"]
                }
            }
        )

        anomalies.append(anomaly)

        # Update training data
        self.training_data[metric_name].append(value)
        if len(self.training_data[metric_name]) > 1000:
            self.training_data[metric_name] = self.training_data[metric_name][-1000:]

        return anomalies

    def _calculate_percentile_rank(self, value: float, metric_name: str) -> float:
        """Calculate percentile rank of value in training data."""

        if metric_name not in self.training_data or not self.training_data[metric_name]:
            return 50.0

        data = self.training_data[metric_name]
        rank = sum(1 for x in data if x <= value) / len(data) * 100
        return rank


class IntelligentRecommendationEngine:
    """Generates intelligent performance optimization recommendations."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.recommendation_templates = self._initialize_recommendation_templates()
        self.performance_baselines = {}

        logger.info("Initialized Intelligent Recommendation Engine")

    def _initialize_recommendation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize recommendation templates."""
        return {
            "high_latency": {
                "title": "High Response Latency Detected",
                "description": "Response latency is above acceptable thresholds",
                "action_items": [
                    "Implement caching for frequently accessed data",
                    "Optimize database queries and add indexes",
                    "Consider connection pooling optimization",
                    "Review and optimize critical code paths"
                ],
                "implementation_effort": "medium",
                "expected_improvement": 0.3
            },
            "low_cache_hit_rate": {
                "title": "Low Cache Hit Rate",
                "description": "Cache hit rate is below optimal levels",
                "action_items": [
                    "Increase cache size allocation",
                    "Optimize cache key strategies",
                    "Implement cache warming for critical data",
                    "Review cache TTL settings"
                ],
                "implementation_effort": "low",
                "expected_improvement": 0.25
            },
            "high_cpu_usage": {
                "title": "High CPU Utilization",
                "description": "CPU usage is consistently high",
                "action_items": [
                    "Profile CPU-intensive operations",
                    "Implement algorithmic optimizations",
                    "Consider horizontal scaling",
                    "Optimize resource-heavy processes"
                ],
                "implementation_effort": "high",
                "expected_improvement": 0.4
            },
            "constitutional_compliance_drift": {
                "title": "Constitutional Compliance Drift",
                "description": "Constitutional compliance score is declining",
                "action_items": [
                    "Review constitutional validation logic",
                    "Enhance compliance monitoring",
                    "Update constitutional principles",
                    "Implement additional safeguards"
                ],
                "implementation_effort": "medium",
                "expected_improvement": 0.15
            }
        }

    def generate_recommendations(
        self,
        metrics: Dict[str, float],
        anomalies: List[Anomaly]
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on metrics and anomalies."""

        recommendations = []

        # Analyze metrics for optimization opportunities
        for metric_name, value in metrics.items():
            recs = self._analyze_metric_for_recommendations(metric_name, value)
            recommendations.extend(recs)

        # Generate recommendations from anomalies
        for anomaly in anomalies:
            rec = self._generate_anomaly_recommendation(anomaly)
            if rec:
                recommendations.append(rec)

        # Prioritize and deduplicate recommendations
        recommendations = self._prioritize_recommendations(recommendations)

        return recommendations

    def _analyze_metric_for_recommendations(
        self,
        metric_name: str,
        value: float
    ) -> List[OptimizationRecommendation]:
        """Analyze a metric and generate recommendations."""

        recommendations = []

        # Define metric thresholds and corresponding recommendations
        metric_rules = {
            "response_time_p99": {
                "threshold": 100.0,  # 100ms
                "template": "high_latency",
                "target_improvement": 0.3
            },
            "cache_hit_rate": {
                "threshold": 0.8,  # 80%
                "template": "low_cache_hit_rate",
                "target_improvement": 0.15,
                "invert": True  # Lower values trigger recommendation
            },
            "cpu_utilization": {
                "threshold": 0.8,  # 80%
                "template": "high_cpu_usage",
                "target_improvement": 0.25
            },
            "constitutional_compliance_score": {
                "threshold": 0.95,  # 95%
                "template": "constitutional_compliance_drift",
                "target_improvement": 0.05,
                "invert": True
            }
        }

        if metric_name in metric_rules:
            rule = metric_rules[metric_name]
            threshold = rule["threshold"]
            invert = rule.get("invert", False)

            # Check if recommendation should be triggered
            should_recommend = (value < threshold) if invert else (value > threshold)

            if should_recommend:
                template = self.recommendation_templates[rule["template"]]

                # Calculate target value
                if invert:
                    target_value = threshold + (threshold * rule["target_improvement"])
                else:
                    target_value = threshold - (threshold * rule["target_improvement"])

                recommendation = OptimizationRecommendation(
                    recommendation_id=f"{metric_name}_{int(time.time())}",
                    title=template["title"],
                    description=f"{template['description']} (Current: {value:.2f})",
                    metric_name=metric_name,
                    current_value=value,
                    target_value=target_value,
                    expected_improvement=rule["target_improvement"],
                    implementation_effort=template["implementation_effort"],
                    priority=self._calculate_priority(metric_name, value, threshold),
                    action_items=template["action_items"],
                    estimated_impact={
                        "performance_improvement": template["expected_improvement"],
                        "resource_savings": template["expected_improvement"] * 0.5
                    },
                    constitutional_compliance_impact=0.02 if "constitutional" in metric_name else 0.0
                )

                recommendations.append(recommendation)

        return recommendations

    def _generate_anomaly_recommendation(self, anomaly: Anomaly) -> Optional[OptimizationRecommendation]:
        """Generate recommendation from anomaly."""

        if anomaly.severity in [AlertSeverity.LOW]:
            return None  # Skip low severity anomalies

        # Generate recommendation based on anomaly type
        if anomaly.anomaly_type == AnomalyType.TREND:
            title = f"Trend Anomaly in {anomaly.metric_name}"
            description = f"Detected significant trend change in {anomaly.metric_name}"
            action_items = [
                "Investigate root cause of trend change",
                "Monitor metric closely for continued deviation",
                "Consider adjusting thresholds if change is expected",
                "Implement corrective measures if needed"
            ]
        else:
            title = f"Statistical Anomaly in {anomaly.metric_name}"
            description = f"Detected statistical anomaly in {anomaly.metric_name}"
            action_items = [
                "Investigate immediate cause of anomaly",
                "Check for system issues or configuration changes",
                "Verify data quality and collection accuracy",
                "Implement preventive measures"
            ]

        return OptimizationRecommendation(
            recommendation_id=f"anomaly_{anomaly.metric_name}_{int(time.time())}",
            title=title,
            description=description,
            metric_name=anomaly.metric_name,
            current_value=anomaly.value,
            target_value=anomaly.expected_value,
            expected_improvement=0.1,  # Conservative estimate
            implementation_effort="medium",
            priority=anomaly.severity,
            action_items=action_items,
            estimated_impact={
                "stability_improvement": 0.2,
                "anomaly_reduction": 0.3
            },
            constitutional_compliance_impact=0.01
        )

    def _calculate_priority(self, metric_name: str, current_value: float, threshold: float) -> AlertSeverity:
        """Calculate priority based on how far the metric deviates from threshold."""

        deviation = abs(current_value - threshold) / threshold

        if deviation > 0.5:  # 50% deviation
            return AlertSeverity.CRITICAL
        elif deviation > 0.3:  # 30% deviation
            return AlertSeverity.HIGH
        elif deviation > 0.1:  # 10% deviation
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW

    def _prioritize_recommendations(
        self,
        recommendations: List[OptimizationRecommendation]
    ) -> List[OptimizationRecommendation]:
        """Prioritize and deduplicate recommendations."""

        # Remove duplicates based on metric name
        seen_metrics = set()
        unique_recommendations = []

        for rec in recommendations:
            if rec.metric_name not in seen_metrics:
                unique_recommendations.append(rec)
                seen_metrics.add(rec.metric_name)

        # Sort by priority and expected improvement
        priority_order = {
            AlertSeverity.CRITICAL: 4,
            AlertSeverity.HIGH: 3,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 1
        }

        unique_recommendations.sort(
            key=lambda x: (priority_order[x.priority], x.expected_improvement),
            reverse=True
        )

        return unique_recommendations


class AdvancedObservabilitySystem:
    """Main advanced observability system with Redis integration."""

    def __init__(self, redis_url: str = "redis://localhost:6389"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_url = redis_url

        # Initialize components
        self.predictive_engine = PredictiveAnalyticsEngine(redis_url=redis_url)
        self.anomaly_detector = MLAnomalyDetector(redis_url=redis_url)
        self.recommendation_engine = IntelligentRecommendationEngine()

        # System state
        self.monitoring_active = False
        self.current_metrics: Dict[str, float] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        self.performance_history: List[Dict[str, Any]] = []

        # Redis client for system-level data
        self.redis_client: Optional[redis.Redis] = None
        self.redis_alerts_key = "acgs:observability:alerts"
        self.redis_history_key = "acgs:observability:history"

        logger.info("Initialized Advanced Observability System with Redis integration")

    async def connect_redis(self):
        """Connect to Redis for all components."""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis for observability system")

            # Connect components
            await self.predictive_engine.connect_redis()
            await self.anomaly_detector.connect_redis()

        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None

    async def disconnect_redis(self):
        """Disconnect from Redis for all components."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

        await self.predictive_engine.disconnect_redis()
        await self.anomaly_detector.disconnect_redis()

    async def start_monitoring(self, monitoring_interval_seconds: int = 30):
        """Start the advanced monitoring system."""

        logger.info("🚀 Starting Advanced Observability System")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")

        # Connect to Redis
        await self.connect_redis()

        self.monitoring_active = True

        try:
            while self.monitoring_active:
                # Collect current metrics
                metrics = await self._collect_metrics()

                # Update predictive engine
                for metric_name, value in metrics.items():
                    metric_point = MetricPoint(
                        timestamp=datetime.now(),
                        value=value,
                        metric_name=metric_name
                    )
                    await self.predictive_engine.add_metric_point(metric_point)

                # Detect anomalies
                anomalies = await self._detect_anomalies(metrics)

                # Generate predictions
                predictions = await self._generate_predictions(metrics)

                # Generate recommendations
                recommendations = self.recommendation_engine.generate_recommendations(metrics, anomalies)

                # Process alerts
                await self._process_alerts(anomalies, recommendations)

                # Update system state
                self.current_metrics = metrics
                self._update_performance_history(metrics, anomalies, predictions, recommendations)

                # Wait for next cycle
                await asyncio.sleep(monitoring_interval_seconds)

        except Exception as e:
            logger.error(f"❌ Monitoring system error: {str(e)}")
            self.monitoring_active = False
            raise

    async def _collect_metrics(self) -> Dict[str, float]:
        """Collect current system metrics."""

        # Simulate metric collection (in production, integrate with Prometheus/metrics endpoints)
        base_time = time.time()

        metrics = {
            "response_time_p99": 45.0 + np.random.normal(0, 10),
            "response_time_p95": 35.0 + np.random.normal(0, 8),
            "throughput_rps": 150.0 + np.random.normal(0, 20),
            "error_rate": 0.02 + np.random.normal(0, 0.005),
            "cpu_utilization": 0.65 + np.random.normal(0, 0.1),
            "memory_utilization": 0.70 + np.random.normal(0, 0.08),
            "cache_hit_rate": 0.85 + np.random.normal(0, 0.05),
            "database_connections": 45 + np.random.normal(0, 5),
            "constitutional_compliance_score": 0.94 + np.random.normal(0, 0.02),
            "active_users": 85 + np.random.normal(0, 10),
            "network_latency_ms": 12.0 + np.random.normal(0, 3),
            "disk_io_utilization": 0.35 + np.random.normal(0, 0.1)
        }

        # Ensure values are within reasonable bounds
        for key, value in metrics.items():
            if "rate" in key or "utilization" in key or "score" in key:
                metrics[key] = max(0.0, min(1.0, value))
            else:
                metrics[key] = max(0.0, value)

        return metrics

    async def _detect_anomalies(self, metrics: Dict[str, float]) -> List[Anomaly]:
        """Detect anomalies in current metrics."""

        all_anomalies = []

        # ML-based anomaly detection
        for metric_name, value in metrics.items():
            ml_anomalies = self.anomaly_detector.detect_anomalies(metric_name, value)
            all_anomalies.extend(ml_anomalies)

        # Trend-based anomaly detection
        for metric_name in metrics.keys():
            trend_anomalies = self.predictive_engine.detect_trend_anomalies(metric_name)
            all_anomalies.extend(trend_anomalies)

        return all_anomalies

    async def _generate_predictions(self, metrics: Dict[str, float]) -> Dict[str, PredictionResult]:
        """Generate predictions for key metrics."""

        predictions = {}

        # Generate predictions for critical metrics
        critical_metrics = [
            "response_time_p99", "cpu_utilization", "memory_utilization",
            "constitutional_compliance_score", "throughput_rps"
        ]

        for metric_name in critical_metrics:
            if metric_name in metrics:
                prediction = self.predictive_engine.predict_metric_trend(metric_name, 60)
                if prediction:
                    predictions[metric_name] = prediction

        return predictions

    async def _process_alerts(self, anomalies: List[Anomaly], recommendations: List[OptimizationRecommendation]):
        """Process alerts for anomalies and recommendations."""

        # Process anomaly alerts
        for anomaly in anomalies:
            if anomaly.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                alert = {
                    "type": "anomaly",
                    "timestamp": anomaly.timestamp.isoformat(),
                    "severity": anomaly.severity.value,
                    "metric": anomaly.metric_name,
                    "message": f"Anomaly detected in {anomaly.metric_name}: {anomaly.value:.2f}",
                    "anomaly_score": anomaly.anomaly_score,
                    "constitutional_hash": self.constitutional_hash
                }
                self.active_alerts.append(alert)
                logger.warning(f"🚨 {alert['message']}")

        # Process recommendation alerts
        for rec in recommendations:
            if rec.priority in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                alert = {
                    "type": "recommendation",
                    "timestamp": datetime.now().isoformat(),
                    "severity": rec.priority.value,
                    "metric": rec.metric_name,
                    "message": f"Optimization needed: {rec.title}",
                    "expected_improvement": rec.expected_improvement,
                    "constitutional_hash": self.constitutional_hash
                }
                self.active_alerts.append(alert)
                logger.info(f"💡 {alert['message']}")

    def _update_performance_history(
        self,
        metrics: Dict[str, float],
        anomalies: List[Anomaly],
        predictions: Dict[str, PredictionResult],
        recommendations: List[OptimizationRecommendation]
    ):
        """Update performance history."""

        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "anomaly_count": len(anomalies),
            "prediction_count": len(predictions),
            "recommendation_count": len(recommendations),
            "constitutional_compliance": metrics.get("constitutional_compliance_score", 0.0),
            "constitutional_hash": self.constitutional_hash
        }

        self.performance_history.append(history_entry)

        # Keep only last 1000 entries
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]

    async def get_system_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report."""

        if not self.current_metrics:
            return {"error": "No metrics available"}

        # Calculate overall health score
        health_score = self._calculate_health_score()

        # Get recent anomalies
        recent_anomalies = [
            anomaly for anomaly in self.active_alerts
            if anomaly["type"] == "anomaly"
        ][-10:]  # Last 10 anomalies

        # Get active recommendations
        active_recommendations = [
            rec for rec in self.active_alerts
            if rec["type"] == "recommendation"
        ][-5:]  # Last 5 recommendations

        # Generate resource forecasts
        resource_forecasts = {}
        for metric in ["cpu_utilization", "memory_utilization"]:
            forecast = self.predictive_engine.forecast_resource_needs(metric)
            if forecast:
                resource_forecasts[metric] = forecast

        return {
            "system_health": {
                "overall_score": health_score,
                "status": self._get_health_status(health_score),
                "constitutional_compliance": self.current_metrics.get("constitutional_compliance_score", 0.0),
                "monitoring_active": self.monitoring_active
            },
            "current_metrics": self.current_metrics,
            "recent_anomalies": recent_anomalies,
            "active_recommendations": active_recommendations,
            "resource_forecasts": resource_forecasts,
            "performance_trends": self._calculate_performance_trends(),
            "constitutional_hash": self.constitutional_hash
        }

    def _calculate_health_score(self) -> float:
        """Calculate overall system health score."""

        if not self.current_metrics:
            return 0.0

        # Weight different metrics for health calculation
        weights = {
            "constitutional_compliance_score": 0.3,
            "response_time_p99": 0.2,  # Lower is better
            "error_rate": 0.2,  # Lower is better
            "cpu_utilization": 0.1,  # Moderate is better
            "cache_hit_rate": 0.1,
            "throughput_rps": 0.1
        }

        health_score = 0.0
        total_weight = 0.0

        for metric, weight in weights.items():
            if metric in self.current_metrics:
                value = self.current_metrics[metric]

                # Normalize different metrics to 0-1 scale
                if metric == "constitutional_compliance_score" or metric == "cache_hit_rate":
                    normalized = value  # Already 0-1
                elif metric == "response_time_p99":
                    normalized = max(0, 1 - (value / 200))  # 200ms = 0 score
                elif metric == "error_rate":
                    normalized = max(0, 1 - (value / 0.1))  # 10% error = 0 score
                elif metric == "cpu_utilization":
                    normalized = 1 - abs(value - 0.7) / 0.3  # Optimal around 70%
                elif metric == "throughput_rps":
                    normalized = min(1, value / 200)  # 200 RPS = perfect score
                else:
                    normalized = value

                health_score += normalized * weight
                total_weight += weight

        return health_score / total_weight if total_weight > 0 else 0.0

    def _get_health_status(self, health_score: float) -> str:
        """Get health status from score."""

        if health_score >= 0.9:
            return "excellent"
        elif health_score >= 0.8:
            return "good"
        elif health_score >= 0.7:
            return "fair"
        elif health_score >= 0.6:
            return "poor"
        else:
            return "critical"

    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends from history."""

        if len(self.performance_history) < 2:
            return {}

        # Get recent history
        recent_history = self.performance_history[-10:]

        # Calculate trends for key metrics
        trends = {}

        for metric in ["constitutional_compliance", "anomaly_count", "recommendation_count"]:
            values = [entry.get(metric, 0) for entry in recent_history]
            if len(values) >= 2:
                # Simple trend calculation
                trend = "stable"
                if values[-1] > values[0] * 1.1:
                    trend = "increasing"
                elif values[-1] < values[0] * 0.9:
                    trend = "decreasing"

                trends[metric] = {
                    "trend": trend,
                    "current_value": values[-1],
                    "change_percent": ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0
                }

        return trends

    async def stop_monitoring(self):
        """Stop the monitoring system."""

        logger.info("🛑 Stopping Advanced Observability System")
        self.monitoring_active = False

        # Disconnect from Redis
        await self.disconnect_redis()