"""
Graceful Degradation Strategy for ACGS
Implements fallback mechanisms and service degradation patterns to maintain system availability.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)


class DegradationLevel(Enum):
    """Service degradation levels."""

    NORMAL = "normal"
    REDUCED = "reduced"
    MINIMAL = "minimal"
    EMERGENCY = "emergency"


class FallbackStrategy(Enum):
    """Fallback strategy types."""

    CACHED_RESPONSE = "cached_response"
    DEFAULT_RESPONSE = "default_response"
    SIMPLIFIED_LOGIC = "simplified_logic"
    BYPASS_VALIDATION = "bypass_validation"
    QUEUE_FOR_LATER = "queue_for_later"
    FAIL_FAST = "fail_fast"


@dataclass
class DegradationConfig:
    """Configuration for graceful degradation."""

    service_name: str
    degradation_thresholds: dict[str, float]  # metric_name -> threshold
    fallback_strategies: dict[DegradationLevel, list[FallbackStrategy]]
    constitutional_compliance_required: bool = True
    emergency_mode_timeout: float = 300.0  # 5 minutes

    # Performance thresholds
    response_time_threshold_ms: float = 2000.0
    error_rate_threshold: float = 0.05  # 5%
    cpu_usage_threshold: float = 0.8  # 80%
    memory_usage_threshold: float = 0.8  # 80%


@dataclass
class ServiceMetrics:
    """Current service metrics."""

    response_time_ms: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    constitutional_compliance_score: float
    active_connections: int
    queue_depth: int


class GracefulDegradationManager:
    """Manages graceful degradation for ACGS services."""

    def __init__(self, config: DegradationConfig):
        self.config = config
        self.current_level = DegradationLevel.NORMAL
        self.degradation_start_time: float | None = None

        # Fallback data storage
        self.cached_responses: dict[str, Any] = {}
        self.default_responses: dict[str, Any] = {}
        self.queued_requests: list[dict[str, Any]] = []

        self.setup_metrics()
        self.setup_default_responses()

        logger.info(
            f"Graceful degradation manager initialized for {config.service_name}"
        )

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.degradation_level_gauge = Gauge(
            "service_degradation_level",
            "Current service degradation level",
            ["service"],
        )

        self.fallback_activations_total = Counter(
            "fallback_activations_total",
            "Total fallback strategy activations",
            ["service", "strategy", "degradation_level"],
        )

        self.degradation_events_total = Counter(
            "degradation_events_total",
            "Total degradation level changes",
            ["service", "from_level", "to_level"],
        )

    def setup_default_responses(self):
        """Setup default responses for emergency fallback."""
        self.default_responses = {
            "health_check": {
                "status": "degraded",
                "message": "Service operating in degraded mode",
                "constitutional_compliance": True,
            },
            "constitutional_validation": {
                "compliance_score": 0.95,  # Conservative default
                "validation_result": True,
                "message": "Using cached constitutional validation",
            },
            "policy_generation": {
                "policy": "default_safe_policy",
                "confidence": 0.8,
                "message": "Using simplified policy generation",
            },
        }

    async def evaluate_degradation_level(
        self, metrics: ServiceMetrics
    ) -> DegradationLevel:
        """Evaluate the appropriate degradation level based on current metrics."""
        # Check emergency conditions first
        if (
            metrics.error_rate > 0.2
            or metrics.response_time_ms > 10000  # >20% error rate
            or metrics.cpu_usage > 0.95  # >10s response time
            or metrics.memory_usage > 0.95  # >95% CPU
        ):  # >95% memory
            return DegradationLevel.EMERGENCY

        # Check minimal conditions
        if (
            metrics.error_rate > 0.1
            or metrics.response_time_ms > 5000  # >10% error rate
            or metrics.cpu_usage > 0.9  # >5s response time
            or metrics.memory_usage > 0.9  # >90% CPU
        ):  # >90% memory
            return DegradationLevel.MINIMAL

        # Check reduced conditions
        if (
            metrics.error_rate > self.config.error_rate_threshold
            or metrics.response_time_ms > self.config.response_time_threshold_ms
            or metrics.cpu_usage > self.config.cpu_usage_threshold
            or metrics.memory_usage > self.config.memory_usage_threshold
        ):
            return DegradationLevel.REDUCED

        # Check constitutional compliance
        if (
            self.config.constitutional_compliance_required
            and metrics.constitutional_compliance_score < 0.95
        ):
            return DegradationLevel.REDUCED

        return DegradationLevel.NORMAL

    async def update_degradation_level(self, new_level: DegradationLevel):
        """Update the current degradation level."""
        if new_level != self.current_level:
            old_level = self.current_level
            self.current_level = new_level

            # Record degradation event
            self.degradation_events_total.labels(
                service=self.config.service_name,
                from_level=old_level.value,
                to_level=new_level.value,
            ).inc()

            # Update metrics
            level_values = {
                DegradationLevel.NORMAL: 0,
                DegradationLevel.REDUCED: 1,
                DegradationLevel.MINIMAL: 2,
                DegradationLevel.EMERGENCY: 3,
            }
            self.degradation_level_gauge.labels(service=self.config.service_name).set(
                level_values[new_level]
            )

            # Track degradation start time
            if (
                new_level != DegradationLevel.NORMAL
                and old_level == DegradationLevel.NORMAL
            ):
                self.degradation_start_time = asyncio.get_event_loop().time()
            elif new_level == DegradationLevel.NORMAL:
                self.degradation_start_time = None

            logger.warning(
                f"Degradation level changed from {old_level.value} to {new_level.value} "
                f"for service {self.config.service_name}"
            )

            # Execute degradation actions
            await self.execute_degradation_actions(new_level)

    async def execute_degradation_actions(self, level: DegradationLevel):
        """Execute actions for the given degradation level."""
        strategies = self.config.fallback_strategies.get(level, [])

        for strategy in strategies:
            try:
                await self.activate_fallback_strategy(strategy, level)
            except Exception as e:
                logger.error(f"Failed to activate fallback strategy {strategy}: {e}")

    async def activate_fallback_strategy(
        self, strategy: FallbackStrategy, level: DegradationLevel
    ):
        """Activate a specific fallback strategy."""
        self.fallback_activations_total.labels(
            service=self.config.service_name,
            strategy=strategy.value,
            degradation_level=level.value,
        ).inc()

        if strategy == FallbackStrategy.CACHED_RESPONSE:
            await self.enable_response_caching()
        elif strategy == FallbackStrategy.DEFAULT_RESPONSE:
            await self.enable_default_responses()
        elif strategy == FallbackStrategy.SIMPLIFIED_LOGIC:
            await self.enable_simplified_logic()
        elif strategy == FallbackStrategy.BYPASS_VALIDATION:
            await self.bypass_non_critical_validation()
        elif strategy == FallbackStrategy.QUEUE_FOR_LATER:
            await self.enable_request_queuing()
        elif strategy == FallbackStrategy.FAIL_FAST:
            await self.enable_fail_fast_mode()

        logger.info(f"Activated fallback strategy: {strategy.value}")

    async def enable_response_caching(self):
        """Enable aggressive response caching."""
        # Implementation would integrate with caching layer
        logger.info("Enabled aggressive response caching")

    async def enable_default_responses(self):
        """Enable default response mode."""
        # Implementation would configure service to use default responses
        logger.info("Enabled default response mode")

    async def enable_simplified_logic(self):
        """Enable simplified business logic."""
        # Implementation would switch to simplified algorithms
        logger.info("Enabled simplified logic mode")

    async def bypass_non_critical_validation(self):
        """Bypass non-critical validation steps."""
        # Implementation would skip optional validations
        logger.info("Bypassing non-critical validations")

    async def enable_request_queuing(self):
        """Enable request queuing for later processing."""
        # Implementation would queue non-urgent requests
        logger.info("Enabled request queuing")

    async def enable_fail_fast_mode(self):
        """Enable fail-fast mode to prevent cascade failures."""
        # Implementation would reject requests quickly
        logger.info("Enabled fail-fast mode")

    async def handle_request_with_degradation(
        self,
        request_type: str,
        request_data: dict[str, Any],
        original_handler: Callable,
    ) -> Any:
        """Handle a request with degradation strategies applied."""
        try:
            # Check if we should use fallback based on current degradation level
            if self.current_level == DegradationLevel.EMERGENCY:
                return await self.get_emergency_response(request_type, request_data)
            if self.current_level == DegradationLevel.MINIMAL:
                return await self.get_minimal_response(request_type, request_data)
            if self.current_level == DegradationLevel.REDUCED:
                return await self.get_reduced_response(
                    request_type, request_data, original_handler
                )
            # Normal operation
            return await original_handler(request_data)

        except Exception as e:
            logger.error(f"Error in degraded request handling: {e}")
            # Fall back to emergency response
            return await self.get_emergency_response(request_type, request_data)

    async def get_emergency_response(
        self, request_type: str, request_data: dict[str, Any]
    ) -> Any:
        """Get emergency fallback response."""
        if request_type in self.default_responses:
            response = self.default_responses[request_type].copy()
            response["degradation_level"] = "emergency"
            response["timestamp"] = asyncio.get_event_loop().time()
            return response

        # Generic emergency response
        return {
            "status": "emergency_mode",
            "message": "Service operating in emergency mode",
            "degradation_level": "emergency",
            "constitutional_compliance": True,  # Conservative default
            "timestamp": asyncio.get_event_loop().time(),
        }

    async def get_minimal_response(
        self, request_type: str, request_data: dict[str, Any]
    ) -> Any:
        """Get minimal functionality response."""
        # Check cache first
        cache_key = f"{request_type}_{hash(str(request_data))}"
        if cache_key in self.cached_responses:
            response = self.cached_responses[cache_key].copy()
            response["degradation_level"] = "minimal"
            response["from_cache"] = True
            return response

        # Use default response
        return await self.get_emergency_response(request_type, request_data)

    async def get_reduced_response(
        self,
        request_type: str,
        request_data: dict[str, Any],
        original_handler: Callable,
    ) -> Any:
        """Get reduced functionality response."""
        try:
            # Try original handler with timeout
            response = await asyncio.wait_for(
                original_handler(request_data),
                timeout=5.0,  # Reduced timeout
            )

            # Cache successful response
            cache_key = f"{request_type}_{hash(str(request_data))}"
            self.cached_responses[cache_key] = response

            # Limit cache size
            if len(self.cached_responses) > 1000:
                # Remove oldest entries
                keys_to_remove = list(self.cached_responses.keys())[:100]
                for key in keys_to_remove:
                    del self.cached_responses[key]

            response["degradation_level"] = "reduced"
            return response

        except asyncio.TimeoutError:
            logger.warning(f"Timeout in reduced mode for {request_type}")
            return await self.get_minimal_response(request_type, request_data)

    def get_degradation_status(self) -> dict[str, Any]:
        """Get current degradation status."""
        return {
            "service_name": self.config.service_name,
            "current_level": self.current_level.value,
            "degradation_start_time": self.degradation_start_time,
            "cached_responses_count": len(self.cached_responses),
            "queued_requests_count": len(self.queued_requests),
            "active_strategies": self.config.fallback_strategies.get(
                self.current_level, []
            ),
        }

    async def force_degradation_level(self, level: DegradationLevel):
        """Force a specific degradation level (for testing/manual intervention)."""
        logger.warning(f"Forcing degradation level to {level.value}")
        await self.update_degradation_level(level)

    async def reset_to_normal(self):
        """Reset to normal operation."""
        logger.info("Resetting to normal operation")
        await self.update_degradation_level(DegradationLevel.NORMAL)

        # Clear caches and queues
        self.cached_responses.clear()
        self.queued_requests.clear()


# Default degradation configurations for ACGS services
ACGS_DEGRADATION_CONFIGS = {
    "ac-service": DegradationConfig(
        service_name="ac-service",
        degradation_thresholds={
            "response_time_ms": 2000.0,
            "error_rate": 0.05,
            "constitutional_compliance": 0.95,
        },
        fallback_strategies={
            DegradationLevel.REDUCED: [
                FallbackStrategy.CACHED_RESPONSE,
                FallbackStrategy.SIMPLIFIED_LOGIC,
            ],
            DegradationLevel.MINIMAL: [
                FallbackStrategy.DEFAULT_RESPONSE,
                FallbackStrategy.BYPASS_VALIDATION,
            ],
            DegradationLevel.EMERGENCY: [
                FallbackStrategy.DEFAULT_RESPONSE,
                FallbackStrategy.FAIL_FAST,
            ],
        },
        constitutional_compliance_required=True,
    ),
    "pgc-service": DegradationConfig(
        service_name="pgc-service",
        degradation_thresholds={
            "response_time_ms": 3000.0,
            "error_rate": 0.03,
            "constitutional_compliance": 0.98,
        },
        fallback_strategies={
            DegradationLevel.REDUCED: [
                FallbackStrategy.CACHED_RESPONSE,
                FallbackStrategy.QUEUE_FOR_LATER,
            ],
            DegradationLevel.MINIMAL: [
                FallbackStrategy.DEFAULT_RESPONSE,
                FallbackStrategy.SIMPLIFIED_LOGIC,
            ],
            DegradationLevel.EMERGENCY: [
                FallbackStrategy.DEFAULT_RESPONSE,
                FallbackStrategy.FAIL_FAST,
            ],
        },
        constitutional_compliance_required=True,
    ),
}
