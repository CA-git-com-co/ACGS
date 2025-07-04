#!/usr/bin/env python3
"""
Anomaly Detection System for ACGS-2 Observability
Detects anomalies in metrics and triggers alerts.
"""

import logging
from datetime import datetime, timedelta

import numpy as np

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Statistical anomaly detection for observability metrics."""

    def __init__(self, window_size: int = 100, threshold: float = 3.0):
        self.window_size = window_size
        self.threshold = threshold
        self.metric_history: dict[str, list[float]] = {}

    def add_metric_value(
        self, metric_name: str, value: float, timestamp: datetime = None
    ):
        """Add a new metric value for anomaly detection."""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = []

        self.metric_history[metric_name].append(value)

        # Keep only the last window_size values
        if len(self.metric_history[metric_name]) > self.window_size:
            self.metric_history[metric_name] = self.metric_history[metric_name][
                -self.window_size :
            ]

    def detect_anomaly(
        self, metric_name: str, current_value: float
    ) -> tuple[bool, float]:
        """Detect if current value is anomalous using statistical methods."""
        if metric_name not in self.metric_history:
            return False, 0.0

        history = self.metric_history[metric_name]
        if len(history) < 10:  # Need minimum history
            return False, 0.0

        # Calculate z-score
        mean = np.mean(history)
        std = np.std(history)

        if std == 0:
            return False, 0.0

        z_score = abs((current_value - mean) / std)
        is_anomaly = z_score > self.threshold

        return is_anomaly, z_score

    def get_metric_statistics(self, metric_name: str) -> dict:
        """Get statistical summary of a metric."""
        if metric_name not in self.metric_history:
            return {}

        history = self.metric_history[metric_name]
        if not history:
            return {}

        return {
            "mean": np.mean(history),
            "std": np.std(history),
            "min": np.min(history),
            "max": np.max(history),
            "count": len(history),
        }


class ObservabilityAnomalyMonitor:
    """Monitor observability metrics for anomalies."""

    def __init__(self):
        self.detector = AnomalyDetector()
        self.alert_cooldown = {}  # Prevent alert spam
        self.cooldown_minutes = 15

    def monitor_metrics(self, metrics: dict[str, float]):
        """Monitor multiple metrics for anomalies."""
        anomalies_detected = []

        for metric_name, value in metrics.items():
            # Add to history
            self.detector.add_metric_value(metric_name, value)

            # Check for anomaly
            is_anomaly, z_score = self.detector.detect_anomaly(metric_name, value)

            if is_anomaly and self._should_alert(metric_name):
                anomaly_info = {
                    "metric": metric_name,
                    "value": value,
                    "z_score": z_score,
                    "timestamp": datetime.now(),
                    "statistics": self.detector.get_metric_statistics(metric_name),
                }
                anomalies_detected.append(anomaly_info)
                self._record_alert(metric_name)
                logger.warning(
                    f"Anomaly detected in {metric_name}: {value} (z-score: {z_score:.2f})"
                )

        return anomalies_detected

    def _should_alert(self, metric_name: str) -> bool:
        """Check if we should alert for this metric (respecting cooldown)."""
        if metric_name not in self.alert_cooldown:
            return True

        last_alert = self.alert_cooldown[metric_name]
        cooldown_period = timedelta(minutes=self.cooldown_minutes)

        return datetime.now() - last_alert > cooldown_period

    def _record_alert(self, metric_name: str):
        """Record that we alerted for this metric."""
        self.alert_cooldown[metric_name] = datetime.now()


def main():
    """Main anomaly monitoring loop."""
    monitor = ObservabilityAnomalyMonitor()

    # Simulate metric monitoring
    test_metrics = {
        "response_time_p95": 2.5,
        "constitutional_compliance_score": 0.92,
        "policy_evaluation_success_rate": 0.98,
        "request_rate": 850,
    }

    anomalies = monitor.monitor_metrics(test_metrics)

    if anomalies:
        print(f"🚨 {len(anomalies)} anomalies detected")
        for anomaly in anomalies:
            print(
                f"  - {anomaly['metric']}: {anomaly['value']} (z-score: {anomaly['z_score']:.2f})"
            )
    else:
        print("✅ No anomalies detected")


if __name__ == "__main__":
    main()
