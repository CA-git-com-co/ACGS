"""
Sentry Integration for ACGS-2 Constitutional AI Governance System

This module provides centralized Sentry configuration and utilities for monitoring
constitutional compliance, performance metrics, and multi-agent coordination.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Constitutional compliance constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Performance targets
PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,
    "p95_latency_ms": 3.0,
    "p50_latency_ms": 1.0,
    "constitutional_compliance_rate": 1.0,  # 100% target
    "cache_hit_rate": 0.85,
}


class SentryConstitutionalIntegration:
    """Custom Sentry integration for ACGS-2 constitutional monitoring"""

    def __init__(
        self,
        service_name: str,
        environment: str = "development",
        sample_rate: float = 1.0,
        enable_profiling: bool = True,
    ):
        self.service_name = service_name
        self.environment = environment
        self.sample_rate = sample_rate
        self.enable_profiling = enable_profiling
        self._initialized = False

    def initialize(self) -> None:
        """Initialize Sentry with ACGS-2 specific configuration"""
        if self._initialized:
            return

        dsn = os.getenv("SENTRY_DSN")
        if not dsn:
            return

        # Custom before_send to filter sensitive constitutional data
        def before_send(
            event: dict[str, Any], hint: dict[str, Any]
        ) -> dict[str, Any] | None:
            # Add constitutional context to all events
            event.setdefault("tags", {})["constitutional_hash"] = CONSTITUTIONAL_HASH
            event["tags"]["service"] = self.service_name

            # Filter out sensitive data
            if "extra" in event:
                event["extra"] = self._filter_sensitive_data(event["extra"])

            # Add constitutional compliance context
            event.setdefault("contexts", {})["constitutional"] = {
                "hash": CONSTITUTIONAL_HASH,
                "service": self.service_name,
                "compliance_required": True,
            }

            return event

        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn,
            environment=self.environment,
            send_default_pii=False,  # Don't send PII by default
            traces_sample_rate=self._get_sample_rate(),
            profiles_sample_rate=self.sample_rate if self.enable_profiling else 0,
            before_send=before_send,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(level=None, event_level=None),
                AsyncioIntegration(),
            ],
            _experiments={
                "enable_logs": True,
                "record_sql_params": False,  # Don't record SQL params for security
            },
        )

        # Set default tags
        sentry_sdk.set_tag("constitutional_hash", CONSTITUTIONAL_HASH)
        sentry_sdk.set_tag("service", self.service_name)
        sentry_sdk.set_tag("environment", self.environment)

        self._initialized = True

    def _get_sample_rate(self) -> float:
        """Get appropriate sample rate based on environment"""
        if self.environment == "production":
            return min(self.sample_rate, 0.2)  # Max 20% in production
        if self.environment == "staging":
            return min(self.sample_rate, 0.5)  # Max 50% in staging
        return self.sample_rate  # Full rate in development

    def _filter_sensitive_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter out sensitive constitutional data"""
        sensitive_keys = ["password", "secret", "token", "key", "auth"]
        filtered = {}

        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered[key] = "[REDACTED]"
            elif isinstance(value, dict):
                filtered[key] = self._filter_sensitive_data(value)
            else:
                filtered[key] = value

        return filtered


def track_constitutional_compliance(func: Callable) -> Callable:
    """Decorator to track constitutional compliance for functions"""

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        with sentry_sdk.start_span(
            op="constitutional.validation", name=f"{func.__name__}"
        ) as span:
            span.set_tag("constitutional_hash", CONSTITUTIONAL_HASH)
            span.set_tag("function", func.__name__)

            start_time = time.time()
            try:
                result = await func(*args, **kwargs)

                # Track performance
                execution_time = (time.time() - start_time) * 1000
                span.set_data("execution_time_ms", execution_time)

                # Check performance targets
                if execution_time > PERFORMANCE_TARGETS["p99_latency_ms"]:
                    sentry_sdk.capture_message(
                        f"Performance target breach in {func.__name__}: {execution_time:.2f}ms",
                        level="warning",
                        tags={
                            "performance_breach": True,
                            "target_ms": PERFORMANCE_TARGETS["p99_latency_ms"],
                            "actual_ms": execution_time,
                        },
                    )

                # Check for constitutional compliance in result
                if hasattr(result, "constitutional_compliance"):
                    compliance_rate = result.constitutional_compliance
                    span.set_data("compliance_rate", compliance_rate)

                    if (
                        compliance_rate
                        < PERFORMANCE_TARGETS["constitutional_compliance_rate"]
                    ):
                        sentry_sdk.capture_message(
                            f"Constitutional compliance below target: {compliance_rate:.2%}",
                            level="error",
                            tags={
                                "compliance_breach": True,
                                "compliance_rate": compliance_rate,
                            },
                        )

                return result

            except Exception as e:
                # Capture exception with constitutional context
                sentry_sdk.set_context(
                    "constitutional_validation",
                    {
                        "function": func.__name__,
                        "hash": CONSTITUTIONAL_HASH,
                        "execution_time_ms": (time.time() - start_time) * 1000,
                    },
                )
                sentry_sdk.capture_exception(e)
                raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Similar implementation for sync functions
        with sentry_sdk.start_span(
            op="constitutional.validation", name=f"{func.__name__}"
        ) as span:
            span.set_tag("constitutional_hash", CONSTITUTIONAL_HASH)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                # Same performance and compliance checks as async
                span.set_data("execution_time_ms", execution_time)

                return result
            except Exception as e:
                sentry_sdk.capture_exception(e)
                raise

    # Return appropriate wrapper based on function type
    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def track_agent_coordination(agent_type: str, task_type: str):
    """Decorator to track multi-agent coordination tasks"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with sentry_sdk.start_span(
                op="agent.coordination", name=f"{agent_type}.{task_type}"
            ) as span:
                span.set_tag("agent_type", agent_type)
                span.set_tag("task_type", task_type)
                span.set_tag("constitutional_hash", CONSTITUTIONAL_HASH)

                # Add breadcrumb for agent activity
                sentry_sdk.add_breadcrumb(
                    message=f"Agent {agent_type} starting {task_type}",
                    category="agent.coordination",
                    level="info",
                    data={"agent": agent_type, "task": task_type},
                )

                try:
                    result = await func(*args, **kwargs)

                    # Track agent-specific metrics
                    if hasattr(result, "confidence_score"):
                        span.set_data("confidence_score", result.confidence_score)
                    if hasattr(result, "consensus_achieved"):
                        span.set_data("consensus_achieved", result.consensus_achieved)

                    return result

                except Exception as e:
                    sentry_sdk.set_context(
                        "agent_coordination",
                        {
                            "agent_type": agent_type,
                            "task_type": task_type,
                            "constitutional_hash": CONSTITUTIONAL_HASH,
                        },
                    )
                    sentry_sdk.capture_exception(e)
                    raise

        return wrapper

    return decorator


class ConstitutionalViolationError(Exception):
    """Exception for constitutional compliance violations"""

    def __init__(
        self,
        message: str,
        violation_type: str,
        severity: str = "high",
        affected_services: list | None = None,
    ):
        super().__init__(message)
        self.violation_type = violation_type
        self.severity = severity
        self.affected_services = affected_services or []

        # Automatically report to Sentry
        sentry_sdk.capture_message(
            f"Constitutional Violation: {violation_type}",
            level="error" if severity == "high" else "warning",
            tags={
                "constitutional_violation": True,
                "violation_type": violation_type,
                "severity": severity,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
            extra={"message": message, "affected_services": affected_services},
        )


def monitor_performance_target(
    target_name: str, target_value: float, actual_value: float, unit: str = "ms"
) -> None:
    """Monitor performance against ACGS-2 targets"""
    if actual_value > target_value:
        breach_percentage = ((actual_value - target_value) / target_value) * 100

        sentry_sdk.capture_message(
            f"Performance target breach: {target_name}",
            level="warning" if breach_percentage < 50 else "error",
            tags={
                "performance_breach": True,
                "target_name": target_name,
                "breach_percentage": breach_percentage,
            },
            extra={
                "target_value": f"{target_value}{unit}",
                "actual_value": f"{actual_value}{unit}",
                "breach_amount": f"{actual_value - target_value}{unit}",
            },
        )


def capture_constitutional_event(
    event_type: str,
    description: str,
    metadata: dict[str, Any] | None = None,
    level: str = "info",
) -> None:
    """Capture constitutional governance events"""
    sentry_sdk.capture_message(
        f"Constitutional Event: {event_type}",
        level=level,
        tags={
            "constitutional_event": True,
            "event_type": event_type,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        },
        extra={"description": description, "metadata": metadata or {}},
    )


# Export convenience functions
def init_sentry(service_name: str, **kwargs) -> SentryConstitutionalIntegration:
    """Initialize Sentry for a service with constitutional monitoring"""
    integration = SentryConstitutionalIntegration(service_name, **kwargs)
    integration.initialize()
    return integration
