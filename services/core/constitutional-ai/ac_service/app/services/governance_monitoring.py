"""
Governance Framework Monitoring and Production Hardening
Constitutional Hash: cdd01ef066bc6cf2

This module implements comprehensive monitoring, alerting, and production hardening
features for the enhanced constitutional governance framework.

Key Features:
- Real-time performance monitoring with P99 <5ms targets
- Intelligent alerting for governance anomalies
- Circuit breaker patterns for resilience
- Health checks and readiness probes
- Metrics collection and dashboard integration
- Cache optimization for >85% hit rates
"""

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from services.shared.metrics import get_metrics
from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.validation.constitutional_validator import CONSTITUTIONAL_HASH

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class AlertSeverity(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""

    p99_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    throughput_rps: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    constitutional_compliance_rate: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CircuitBreakerState:
    """Circuit breaker state tracking"""

    is_open: bool = False
    failure_count: int = 0
    last_failure_time: datetime | None = None
    success_count: int = 0
    total_requests: int = 0


class GovernanceMonitor:
    """
    Comprehensive monitoring system for governance framework with production hardening.
    Implements circuit breaker patterns, health checks, and intelligent alerting.
    """

    def __init__(
        self,
        alerting_system: AlertingSystem | None = None,
        performance_targets: dict[str, float] | None = None,
        circuit_breaker_config: dict[str, Any] | None = None,
    ):
        """
        Initialize governance monitoring system.

        Args:
            alerting_system: Intelligent alerting system
            performance_targets: Performance target thresholds
            circuit_breaker_config: Circuit breaker configuration
        """
        self.alerting_system = alerting_system
        self.metrics = get_metrics("governance_monitoring")

        # Performance targets (ACGS-2 requirements)
        self.performance_targets = performance_targets or {
            "p99_latency_ms": 5.0,
            "throughput_rps": 100.0,
            "cache_hit_rate": 0.85,
            "error_rate": 0.01,
            "constitutional_compliance_rate": 1.0,
        }

        # Circuit breaker configuration
        self.circuit_breaker_config = circuit_breaker_config or {
            "failure_threshold": 5,
            "recovery_timeout_seconds": 30,
            "success_threshold": 3,
        }

        # Monitoring state
        self.circuit_breaker = CircuitBreakerState()
        self.latency_samples = deque(maxlen=1000)  # Rolling window
        self.error_samples = deque(maxlen=1000)
        self.cache_samples = deque(maxlen=1000)
        self.compliance_samples = deque(maxlen=1000)

        # Health tracking
        self.health_status = HealthStatus.HEALTHY
        self.last_health_check = datetime.now(timezone.utc)

        # Alert tracking
        self.active_alerts = defaultdict(list)
        self.alert_cooldowns = defaultdict(datetime)

    async def record_request(
        self,
        latency_ms: float,
        success: bool,
        cache_hit: bool,
        constitutional_compliant: bool,
    ) -> None:
        """
        Record request metrics for monitoring.

        Args:
            latency_ms: Request latency in milliseconds
            success: Whether request was successful
            cache_hit: Whether request was served from cache
            constitutional_compliant: Whether request was constitutionally compliant
        """
        timestamp = time.time()

        # Record samples
        self.latency_samples.append((timestamp, latency_ms))
        self.error_samples.append((timestamp, not success))
        self.cache_samples.append((timestamp, cache_hit))
        self.compliance_samples.append((timestamp, constitutional_compliant))

        # Update circuit breaker
        await self._update_circuit_breaker(success)

        # Record metrics
        if self.metrics:
            self.metrics.histogram("governance_request_latency_ms", latency_ms)
            self.metrics.counter("governance_requests_total").inc()
            if success:
                self.metrics.counter("governance_requests_success").inc()
            else:
                self.metrics.counter("governance_requests_error").inc()
            if cache_hit:
                self.metrics.counter("governance_cache_hits").inc()
            if constitutional_compliant:
                self.metrics.counter("governance_constitutional_compliant").inc()

        # Check for performance violations
        await self._check_performance_violations()

    async def _update_circuit_breaker(self, success: bool) -> None:
        """Update circuit breaker state based on request outcome."""
        self.circuit_breaker.total_requests += 1

        if success:
            self.circuit_breaker.success_count += 1

            # Check if we can close the circuit breaker
            if (
                self.circuit_breaker.is_open
                and self.circuit_breaker.success_count
                >= self.circuit_breaker_config["success_threshold"]
            ):
                self.circuit_breaker.is_open = False
                self.circuit_breaker.failure_count = 0
                logger.info("Circuit breaker closed - service recovered")

                if self.alerting_system:
                    await self.alerting_system.send_alert(
                        "LOW",
                        "Governance service circuit breaker closed - service recovered",
                    )
        else:
            self.circuit_breaker.failure_count += 1
            self.circuit_breaker.last_failure_time = datetime.now(timezone.utc)
            self.circuit_breaker.success_count = 0

            # Check if we should open the circuit breaker
            if (
                not self.circuit_breaker.is_open
                and self.circuit_breaker.failure_count
                >= self.circuit_breaker_config["failure_threshold"]
            ):
                self.circuit_breaker.is_open = True
                logger.error("Circuit breaker opened - service degraded")

                if self.alerting_system:
                    await self.alerting_system.send_alert(
                        "CRITICAL",
                        "Governance service circuit breaker opened - service degraded",
                    )

    async def _check_performance_violations(self) -> None:
        """Check for performance target violations and trigger alerts."""
        current_metrics = self.get_current_metrics()

        # Check P99 latency
        if current_metrics.p99_latency_ms > self.performance_targets["p99_latency_ms"]:
            await self._trigger_alert(
                AlertSeverity.HIGH,
                f"P99 latency violation: {current_metrics.p99_latency_ms:.2f}ms > "
                f"{self.performance_targets['p99_latency_ms']}ms target",
                "p99_latency_violation",
            )

        # Check throughput
        if current_metrics.throughput_rps < self.performance_targets["throughput_rps"]:
            await self._trigger_alert(
                AlertSeverity.MEDIUM,
                f"Throughput below target: {current_metrics.throughput_rps:.2f} RPS < "
                f"{self.performance_targets['throughput_rps']} RPS target",
                "throughput_violation",
            )

        # Check cache hit rate
        if current_metrics.cache_hit_rate < self.performance_targets["cache_hit_rate"]:
            await self._trigger_alert(
                AlertSeverity.MEDIUM,
                f"Cache hit rate below target: {current_metrics.cache_hit_rate:.2%} < "
                f"{self.performance_targets['cache_hit_rate']:.2%} target",
                "cache_hit_rate_violation",
            )

        # Check error rate
        if current_metrics.error_rate > self.performance_targets["error_rate"]:
            await self._trigger_alert(
                AlertSeverity.HIGH,
                f"Error rate above target: {current_metrics.error_rate:.2%} > "
                f"{self.performance_targets['error_rate']:.2%} target",
                "error_rate_violation",
            )

        # Check constitutional compliance
        if (
            current_metrics.constitutional_compliance_rate
            < self.performance_targets["constitutional_compliance_rate"]
        ):
            await self._trigger_alert(
                AlertSeverity.CRITICAL,
                f"Constitutional compliance below target: {current_metrics.constitutional_compliance_rate:.2%} < "
                f"{self.performance_targets['constitutional_compliance_rate']:.2%} target",
                "constitutional_compliance_violation",
            )

    async def _trigger_alert(
        self, severity: AlertSeverity, message: str, alert_type: str
    ) -> None:
        """Trigger alert with cooldown to prevent spam."""
        cooldown_key = f"{alert_type}_{severity.value}"
        now = datetime.now(timezone.utc)

        # Check cooldown (5 minutes for most alerts, 1 minute for critical)
        cooldown_minutes = 1 if severity == AlertSeverity.CRITICAL else 5
        if cooldown_key in self.alert_cooldowns and now - self.alert_cooldowns[
            cooldown_key
        ] < timedelta(minutes=cooldown_minutes):
            return

        # Record alert
        self.active_alerts[alert_type].append(
            {
                "severity": severity.value,
                "message": message,
                "timestamp": now,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
        )

        # Update cooldown
        self.alert_cooldowns[cooldown_key] = now

        # Send alert
        if self.alerting_system:
            await self.alerting_system.send_alert(severity.value.upper(), message)

        logger.warning("Governance alert triggered: %s - %s", severity.value, message)

    def get_current_metrics(self) -> PerformanceMetrics:
        """Calculate current performance metrics from samples."""
        now = time.time()
        window_seconds = 60  # 1-minute window

        # Filter samples to recent window
        recent_latency = [
            latency
            for timestamp, latency in self.latency_samples
            if now - timestamp <= window_seconds
        ]
        recent_errors = [
            error
            for timestamp, error in self.error_samples
            if now - timestamp <= window_seconds
        ]
        recent_cache = [
            hit
            for timestamp, hit in self.cache_samples
            if now - timestamp <= window_seconds
        ]
        recent_compliance = [
            compliant
            for timestamp, compliant in self.compliance_samples
            if now - timestamp <= window_seconds
        ]

        # Calculate metrics
        if recent_latency:
            p99_latency = float(np.percentile(recent_latency, 99))
            p95_latency = float(np.percentile(recent_latency, 95))
            p50_latency = float(np.percentile(recent_latency, 50))
        else:
            p99_latency = p95_latency = p50_latency = 0.0

        throughput_rps = len(recent_latency) / window_seconds if recent_latency else 0.0
        error_rate = sum(recent_errors) / len(recent_errors) if recent_errors else 0.0
        cache_hit_rate = sum(recent_cache) / len(recent_cache) if recent_cache else 0.0
        compliance_rate = (
            sum(recent_compliance) / len(recent_compliance)
            if recent_compliance
            else 0.0
        )

        return PerformanceMetrics(
            p99_latency_ms=p99_latency,
            p95_latency_ms=p95_latency,
            p50_latency_ms=p50_latency,
            throughput_rps=throughput_rps,
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate,
            constitutional_compliance_rate=compliance_rate,
        )

    def get_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status for readiness/liveness probes."""
        current_metrics = self.get_current_metrics()

        # Determine overall health
        health_issues = []

        if self.circuit_breaker.is_open:
            health_issues.append("Circuit breaker is open")

        if (
            current_metrics.p99_latency_ms
            > self.performance_targets["p99_latency_ms"] * 2
        ):
            health_issues.append("Severe latency degradation")

        if current_metrics.error_rate > self.performance_targets["error_rate"] * 5:
            health_issues.append("High error rate")

        if current_metrics.constitutional_compliance_rate < 0.95:
            health_issues.append("Constitutional compliance issues")

        # Determine status
        if not health_issues:
            status = HealthStatus.HEALTHY
        elif len(health_issues) == 1 and "Circuit breaker" not in health_issues[0]:
            status = HealthStatus.DEGRADED
        elif any(
            "Severe" in issue or "Constitutional" in issue for issue in health_issues
        ):
            status = HealthStatus.CRITICAL
        else:
            status = HealthStatus.UNHEALTHY

        self.health_status = status
        self.last_health_check = datetime.now(timezone.utc)

        return {
            "status": status.value,
            "timestamp": self.last_health_check.isoformat(),
            "metrics": {
                "p99_latency_ms": current_metrics.p99_latency_ms,
                "throughput_rps": current_metrics.throughput_rps,
                "cache_hit_rate": current_metrics.cache_hit_rate,
                "error_rate": current_metrics.error_rate,
                "constitutional_compliance_rate": current_metrics.constitutional_compliance_rate,
            },
            "circuit_breaker": {
                "is_open": self.circuit_breaker.is_open,
                "failure_count": self.circuit_breaker.failure_count,
                "success_count": self.circuit_breaker.success_count,
            },
            "issues": health_issues,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    def is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open (service should be unavailable)."""
        if not self.circuit_breaker.is_open:
            return False

        # Check if recovery timeout has passed
        if self.circuit_breaker.last_failure_time and datetime.now(
            timezone.utc
        ) - self.circuit_breaker.last_failure_time > timedelta(
            seconds=self.circuit_breaker_config["recovery_timeout_seconds"]
        ):
            # Allow a test request
            return False

        return True
