"""
AICI Monitoring and Observability for ACGS-PGP

Implements comprehensive monitoring for AICI controller performance,
policy evaluation, and constitutional compliance.
"""

import time
import logging
from typing import Dict, List, Optional

import prometheus_client as prom

logger = logging.getLogger(__name__)

# Prometheus metrics
CONTROLLER_LATENCY = prom.Histogram(
    "aici_controller_latency_seconds",
    "AICI controller execution time",
    ["phase", "model_id"],
)
POLICY_EVALUATION_LATENCY = prom.Histogram(
    "aici_policy_evaluation_latency_seconds",
    "OPA policy evaluation time",
    ["policy_name"],
)
CONSTITUTIONAL_COMPLIANCE = prom.Gauge(
    "aici_constitutional_compliance_score",
    "Constitutional compliance score (0-1)",
    ["model_id"],
)
BLOCKED_TOKENS = prom.Counter(
    "aici_blocked_tokens_total",
    "Number of tokens blocked by constitutional constraints",
    ["model_id", "reason"],
)


class AICIMonitoring:
    """Monitoring and observability for AICI integration."""

    def __init__(self):
        self.start_time = time.time()

    def record_controller_latency(self, phase: str, model_id: str, duration: float):
        """Record controller execution latency."""
        CONTROLLER_LATENCY.labels(phase=phase, model_id=model_id).observe(duration)

        if duration > 0.005:  # 5ms threshold
            logger.warning(
                f"AICI controller {phase} phase exceeded 5ms: {duration*1000:.2f}ms"
            )

    def record_policy_evaluation(self, policy_name: str, duration: float):
        """Record policy evaluation latency."""
        POLICY_EVALUATION_LATENCY.labels(policy_name=policy_name).observe(duration)
