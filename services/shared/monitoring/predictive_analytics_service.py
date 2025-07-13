"""
ACGS Predictive Analytics Service for Monitoring Integration
Constitutional Hash: cdd01ef066bc6cf2

Provides ML-based predictive analytics for Grafana dashboards including:
- Performance trend prediction
- Constitutional compliance forecasting
- Anomaly detection and alerting
- Resource utilization predictions
"""

import logging
import math
import time
from datetime import datetime, timedelta, timezone
from typing import Any

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    import numpy as np
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from sklearn.preprocessing import StandardScaler

    ML_AVAILABLE = True
except ImportError:
    logger.warning("ML libraries not available, using simplified predictions")
    ML_AVAILABLE = False

# Try to import prometheus client for metrics
try:
    from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("Prometheus client not available")
    PROMETHEUS_AVAILABLE = False


class PredictiveAnalyticsService:
    """ML-based predictive analytics for ACGS monitoring."""

    def __init__(self, window_size: int = 100, prediction_horizon: int = 24):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.window_size = window_size  # Number of data points for training
        self.prediction_horizon = prediction_horizon  # Hours to predict ahead

        # Data storage for time series
        self.metrics_history = {
            "constitutional_compliance_rate": [],
            "performance_latency": [],
            "throughput_rps": [],
            "error_rate": [],
            "resource_utilization": [],
            "security_events": [],
        }

        # ML models
        self.models = {}
        self.scalers = {}
        self.last_training_time = {}

        # Predictions cache
        self.predictions_cache = {}
        self.cache_ttl = 300  # 5 minutes

        # Anomaly detection
        self.anomaly_detectors = {}

        # Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self.registry = CollectorRegistry()
            self._setup_prometheus_metrics()

        logger.info(
            f"Predictive Analytics Service initialized with constitutional hash {CONSTITUTIONAL_HASH}"
        )

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for predictions."""
        self.prediction_metrics = {
            "constitutional_compliance_prediction": Gauge(
                "acgs_constitutional_compliance_prediction",
                "Predicted constitutional compliance rate",
                ["horizon_hours"],
                registry=self.registry,
            ),
            "performance_latency_prediction": Gauge(
                "acgs_performance_latency_prediction",
                "Predicted performance latency",
                ["horizon_hours"],
                registry=self.registry,
            ),
            "throughput_prediction": Gauge(
                "acgs_throughput_prediction",
                "Predicted throughput RPS",
                ["horizon_hours"],
                registry=self.registry,
            ),
            "anomaly_score": Gauge(
                "acgs_anomaly_score",
                "Current anomaly score",
                ["metric_type"],
                registry=self.registry,
            ),
            "prediction_accuracy": Gauge(
                "acgs_prediction_accuracy",
                "Model prediction accuracy",
                ["metric_type"],
                registry=self.registry,
            ),
        }

    async def ingest_metrics(
        self, metrics: dict[str, float], timestamp: datetime | None = None
    ):
        """Ingest new metrics data for prediction training."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # Store metrics with timestamp
        for metric_name, value in metrics.items():
            if metric_name in self.metrics_history:
                self.metrics_history[metric_name].append(
                    {
                        "timestamp": timestamp,
                        "value": value,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    }
                )

                # Keep only recent data within window
                cutoff_time = timestamp - timedelta(hours=self.window_size)
                self.metrics_history[metric_name] = [
                    entry
                    for entry in self.metrics_history[metric_name]
                    if entry["timestamp"] > cutoff_time
                ]

        # Trigger model retraining if enough data
        await self._check_and_retrain_models()

    async def get_predictions(
        self, metric_name: str, horizons: list[int] | None = None
    ) -> dict[str, Any]:
        """Get predictions for a specific metric."""
        if horizons is None:
            horizons = [1, 6, 12, 24]  # 1, 6, 12, 24 hours ahead

        cache_key = f"{metric_name}:{':'.join(map(str, horizons))}"

        # Check cache
        if cache_key in self.predictions_cache:
            cached_data = self.predictions_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["predictions"]

        # Generate new predictions
        predictions = await self._generate_predictions(metric_name, horizons)

        # Cache results
        self.predictions_cache[cache_key] = {
            "predictions": predictions,
            "timestamp": time.time(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # Update Prometheus metrics
        self._update_prometheus_predictions(metric_name, predictions)

        return predictions

    async def _generate_predictions(
        self, metric_name: str, horizons: list[int]
    ) -> dict[str, Any]:
        """Generate predictions using ML models."""
        if metric_name not in self.metrics_history:
            return {
                "error": f"Unknown metric: {metric_name}",
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

        history = self.metrics_history[metric_name]
        if len(history) < 10:  # Need minimum data points
            return self._fallback_prediction(metric_name, horizons)

        if ML_AVAILABLE and metric_name in self.models:
            return await self._ml_prediction(metric_name, horizons)
        return self._statistical_prediction(metric_name, horizons)

    async def _ml_prediction(
        self, metric_name: str, horizons: list[int]
    ) -> dict[str, Any]:
        """Generate ML-based predictions."""
        try:
            model = self.models[metric_name]
            scaler = self.scalers.get(metric_name)
            history = self.metrics_history[metric_name]

            # Prepare recent data for prediction
            recent_values = [entry["value"] for entry in history[-10:]]

            if scaler:
                scaled_values = scaler.transform(
                    np.array(recent_values).reshape(-1, 1)
                ).flatten()
            else:
                scaled_values = recent_values

            # Generate features (simple time series features)
            features = self._create_time_series_features(scaled_values)

            predictions = {}
            for horizon in horizons:
                # Predict future value
                feature_vector = np.array(features[-1:]).reshape(1, -1)
                pred_value = model.predict(feature_vector)[0]

                # Inverse transform if scaler used
                if scaler:
                    pred_value = scaler.inverse_transform([[pred_value]])[0][0]

                # Add uncertainty estimate
                uncertainty = self._estimate_uncertainty(metric_name, pred_value)

                predictions[f"{horizon}h"] = {
                    "value": float(pred_value),
                    "uncertainty": float(uncertainty),
                    "confidence": self._calculate_confidence(metric_name),
                }

            return {
                "metric_name": metric_name,
                "predictions": predictions,
                "model_type": "ml",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.exception(f"ML prediction failed for {metric_name}: {e}")
            return self._statistical_prediction(metric_name, horizons)

    def _statistical_prediction(
        self, metric_name: str, horizons: list[int]
    ) -> dict[str, Any]:
        """Generate statistical predictions using moving averages and trends."""
        history = self.metrics_history[metric_name]
        values = [entry["value"] for entry in history]

        # Calculate moving averages
        short_window = min(5, len(values))
        long_window = min(20, len(values))

        short_ma = sum(values[-short_window:]) / short_window if short_window > 0 else 0
        sum(values[-long_window:]) / long_window if long_window > 0 else 0

        # Calculate trend
        if len(values) >= 2:
            trend = (values[-1] - values[-min(10, len(values))]) / min(10, len(values))
        else:
            trend = 0

        predictions = {}
        for horizon in horizons:
            # Simple trend-based prediction
            predicted_value = short_ma + (trend * horizon)

            # Apply bounds based on historical data
            if len(values) > 0:
                min_val = min(values)
                max_val = max(values)
                predicted_value = max(
                    min_val * 0.5, min(max_val * 1.5, predicted_value)
                )

            # Estimate uncertainty based on recent volatility
            if len(values) >= 5:
                recent_std = (
                    np.std(values[-5:])
                    if ML_AVAILABLE
                    else self._simple_std(values[-5:])
                )
                uncertainty = recent_std * math.sqrt(horizon)
            else:
                uncertainty = abs(predicted_value) * 0.1

            predictions[f"{horizon}h"] = {
                "value": float(predicted_value),
                "uncertainty": float(uncertainty),
                "confidence": 0.7,  # Lower confidence for statistical methods
            }

        return {
            "metric_name": metric_name,
            "predictions": predictions,
            "model_type": "statistical",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _fallback_prediction(
        self, metric_name: str, horizons: list[int]
    ) -> dict[str, Any]:
        """Fallback prediction when insufficient data."""
        history = self.metrics_history[metric_name]

        if len(history) > 0:
            last_value = history[-1]["value"]
        else:
            # Default values based on metric type
            defaults = {
                "constitutional_compliance_rate": 0.95,
                "performance_latency": 50.0,
                "throughput_rps": 100.0,
                "error_rate": 0.01,
                "resource_utilization": 0.5,
                "security_events": 0.0,
            }
            last_value = defaults.get(metric_name, 0.0)

        predictions = {}
        for horizon in horizons:
            predictions[f"{horizon}h"] = {
                "value": float(last_value),
                "uncertainty": float(abs(last_value) * 0.2),
                "confidence": 0.3,  # Low confidence for fallback
            }

        return {
            "metric_name": metric_name,
            "predictions": predictions,
            "model_type": "fallback",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "warning": "Insufficient data for reliable prediction",
        }

    async def detect_anomalies(self, metric_name: str) -> dict[str, Any]:
        """Detect anomalies in current metrics."""
        if metric_name not in self.metrics_history:
            return {"error": f"Unknown metric: {metric_name}"}

        history = self.metrics_history[metric_name]
        if len(history) < 10:
            return {"anomaly_detected": False, "reason": "Insufficient data"}

        recent_values = [entry["value"] for entry in history[-50:]]
        current_value = recent_values[-1]

        # Statistical anomaly detection
        if len(recent_values) >= 10:
            mean_val = sum(recent_values[:-1]) / len(recent_values[:-1])
            std_val = (
                self._simple_std(recent_values[:-1])
                if not ML_AVAILABLE
                else np.std(recent_values[:-1])
            )

            # Z-score based detection
            z_score = abs(current_value - mean_val) / (std_val + 1e-8)
            is_anomaly = z_score > 3.0  # 3-sigma rule

            anomaly_score = min(z_score / 3.0, 1.0)
        else:
            is_anomaly = False
            anomaly_score = 0.0
            z_score = 0.0

        # ML-based anomaly detection if available
        if ML_AVAILABLE and metric_name in self.anomaly_detectors:
            try:
                detector = self.anomaly_detectors[metric_name]
                ml_score = detector.decision_function([[current_value]])[0]
                ml_anomaly = detector.predict([[current_value]])[0] == -1

                # Combine statistical and ML detection
                is_anomaly = is_anomaly or ml_anomaly
                anomaly_score = max(anomaly_score, abs(ml_score))

            except Exception as e:
                logger.warning(f"ML anomaly detection failed for {metric_name}: {e}")

        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE and "anomaly_score" in self.prediction_metrics:
            self.prediction_metrics["anomaly_score"].labels(
                metric_type=metric_name
            ).set(anomaly_score)

        result = {
            "metric_name": metric_name,
            "anomaly_detected": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "current_value": float(current_value),
            "z_score": float(z_score),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if is_anomaly:
            result["severity"] = "high" if anomaly_score > 0.8 else "medium"
            result["recommendation"] = self._get_anomaly_recommendation(
                metric_name, current_value
            )

        return result

    def _get_anomaly_recommendation(
        self, metric_name: str, current_value: float
    ) -> str:
        """Get recommendation for handling detected anomaly."""
        recommendations = {
            "constitutional_compliance_rate": "Review recent policy changes and constitutional validation processes",
            "performance_latency": "Check system resources and optimize slow operations",
            "throughput_rps": "Investigate potential bottlenecks or traffic spikes",
            "error_rate": "Review error logs and fix underlying issues",
            "resource_utilization": "Scale resources or optimize resource usage",
            "security_events": "Investigate potential security threats and review access logs",
        }

        return recommendations.get(
            metric_name, "Monitor the metric closely and investigate root cause"
        )

    async def _check_and_retrain_models(self):
        """Check if models need retraining and retrain if necessary."""
        current_time = time.time()

        for metric_name, history in self.metrics_history.items():
            if len(history) < 20:  # Need minimum data for training
                continue

            last_training = self.last_training_time.get(metric_name, 0)

            # Retrain every hour or if enough new data
            if current_time - last_training > 3600:  # 1 hour
                await self._train_model(metric_name)
                self.last_training_time[metric_name] = current_time

    async def _train_model(self, metric_name: str):
        """Train ML model for a specific metric."""
        if not ML_AVAILABLE:
            return

        try:
            history = self.metrics_history[metric_name]
            values = [entry["value"] for entry in history]

            if len(values) < 20:
                return

            # Prepare training data
            X, y = self._prepare_training_data(values)

            if len(X) < 10:
                return

            # Scale data
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train prediction model
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_scaled, y)

            # Train anomaly detector
            anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            anomaly_detector.fit(np.array(values).reshape(-1, 1))

            # Store models
            self.models[metric_name] = model
            self.scalers[metric_name] = scaler
            self.anomaly_detectors[metric_name] = anomaly_detector

            # Calculate and store model accuracy
            accuracy = self._calculate_model_accuracy(model, scaler, X, y)

            # Update Prometheus metrics
            if (
                PROMETHEUS_AVAILABLE
                and "prediction_accuracy" in self.prediction_metrics
            ):
                self.prediction_metrics["prediction_accuracy"].labels(
                    metric_type=metric_name
                ).set(accuracy)

            logger.info(f"Trained model for {metric_name} with accuracy {accuracy:.3f}")

        except Exception as e:
            logger.exception(f"Model training failed for {metric_name}: {e}")

    def _prepare_training_data(
        self, values: list[float]
    ) -> tuple[np.ndarray, np.ndarray]:
        """Prepare time series data for training."""
        window = 5  # Use 5 previous values to predict next
        X, y = [], []

        for i in range(window, len(values)):
            X.append(values[i - window : i])
            y.append(values[i])

        return np.array(X), np.array(y)

    def _create_time_series_features(self, values: list[float]) -> list[list[float]]:
        """Create features from time series data."""
        features = []
        window = min(5, len(values))

        for i in range(window, len(values) + 1):
            window_data = values[i - window : i]
            feature_vector = [
                sum(window_data) / len(window_data),  # Mean
                max(window_data) - min(window_data),  # Range
                window_data[-1] - window_data[0],  # Trend
                len([x for x in window_data if x > sum(window_data) / len(window_data)])
                / len(window_data),  # Above average ratio
            ]
            features.append(feature_vector)

        return features

    def _simple_std(self, values: list[float]) -> float:
        """Simple standard deviation calculation when numpy not available."""
        if len(values) <= 1:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def _estimate_uncertainty(self, metric_name: str, predicted_value: float) -> float:
        """Estimate prediction uncertainty."""
        history = self.metrics_history[metric_name]
        if len(history) < 5:
            return abs(predicted_value) * 0.2

        recent_values = [entry["value"] for entry in history[-10:]]
        std_dev = (
            self._simple_std(recent_values)
            if not ML_AVAILABLE
            else np.std(recent_values)
        )

        return max(std_dev, abs(predicted_value) * 0.05)

    def _calculate_confidence(self, metric_name: str) -> float:
        """Calculate prediction confidence based on data quality."""
        history = self.metrics_history[metric_name]

        if len(history) < 10:
            return 0.3
        if len(history) < 50:
            return 0.6
        return 0.8

    def _calculate_model_accuracy(
        self, model, scaler, X: np.ndarray, y: np.ndarray
    ) -> float:
        """Calculate model accuracy using cross-validation."""
        try:
            # Simple train-test split
            split_point = int(len(X) * 0.8)
            X_train, X_test = X[:split_point], X[split_point:]
            y_train, y_test = y[:split_point], y[split_point:]

            if len(X_test) == 0:
                return 0.5

            X_train_scaled = scaler.transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            model.fit(X_train_scaled, y_train)
            predictions = model.predict(X_test_scaled)

            mae = mean_absolute_error(y_test, predictions)
            mean_squared_error(y_test, predictions)

            # Convert to accuracy score (0-1)
            max_error = max(abs(max(y_test) - min(y_test)), 1e-8)
            accuracy = max(0, 1 - (mae / max_error))

            return min(accuracy, 1.0)

        except Exception:
            return 0.5

    def _update_prometheus_predictions(
        self, metric_name: str, predictions: dict[str, Any]
    ):
        """Update Prometheus metrics with predictions."""
        if not PROMETHEUS_AVAILABLE or "predictions" not in predictions:
            return

        try:
            pred_data = predictions["predictions"]

            # Map metric names to Prometheus metrics
            metric_mapping = {
                "constitutional_compliance_rate": "constitutional_compliance_prediction",
                "performance_latency": "performance_latency_prediction",
                "throughput_rps": "throughput_prediction",
            }

            prom_metric_name = metric_mapping.get(metric_name)
            if prom_metric_name and prom_metric_name in self.prediction_metrics:
                for horizon, pred_info in pred_data.items():
                    horizon_hours = horizon.replace("h", "")
                    self.prediction_metrics[prom_metric_name].labels(
                        horizon_hours=horizon_hours
                    ).set(pred_info["value"])

        except Exception as e:
            logger.warning(f"Failed to update Prometheus predictions: {e}")

    async def get_dashboard_data(self) -> dict[str, Any]:
        """Get comprehensive data for Grafana dashboard."""
        dashboard_data = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "predictions": {},
            "anomalies": {},
            "model_status": {},
        }

        # Get predictions for all metrics
        for metric_name in self.metrics_history:
            if len(self.metrics_history[metric_name]) >= 5:
                dashboard_data["predictions"][metric_name] = await self.get_predictions(
                    metric_name
                )
                dashboard_data["anomalies"][metric_name] = await self.detect_anomalies(
                    metric_name
                )

                # Model status
                dashboard_data["model_status"][metric_name] = {
                    "trained": metric_name in self.models,
                    "data_points": len(self.metrics_history[metric_name]),
                    "last_training": self.last_training_time.get(metric_name, 0),
                    "confidence": self._calculate_confidence(metric_name),
                }

        return dashboard_data

    def get_prometheus_metrics_registry(self):
        """Get Prometheus metrics registry for integration."""
        return self.registry if PROMETHEUS_AVAILABLE else None
