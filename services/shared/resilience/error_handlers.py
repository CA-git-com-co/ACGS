"""
Comprehensive Error Handlers
Constitutional Hash: cdd01ef066bc6cf2

Centralized error handling with recovery strategies and monitoring.
"""

import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from .exceptions import (
    ACGSError,
    ConfigurationError,
    ConstitutionalComplianceError,
    DomainError,
    InfrastructureError,
    PerformanceError,
    SecurityError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(str, Enum):
    """Available recovery actions."""

    IGNORE = "ignore"
    RETRY = "retry"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    SHUTDOWN = "shutdown"


class ErrorContext:
    """Context information for error handling."""

    def __init__(
        self,
        operation: str,
        user_id: str = None,
        tenant_id: str = None,
        correlation_id: str = None,
        additional_context: Dict[str, Any] = None,
    ):
        self.operation = operation
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.correlation_id = correlation_id
        self.additional_context = additional_context or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "operation": self.operation,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "additional_context": self.additional_context,
            "timestamp": self.timestamp.isoformat(),
        }


class ErrorHandlingResult:
    """Result of error handling operation."""

    def __init__(
        self,
        action_taken: RecoveryAction,
        severity: ErrorSeverity,
        recovered: bool = False,
        fallback_result: Any = None,
        should_retry: bool = False,
        escalated: bool = False,
        additional_info: Dict[str, Any] = None,
    ):
        self.action_taken = action_taken
        self.severity = severity
        self.recovered = recovered
        self.fallback_result = fallback_result
        self.should_retry = should_retry
        self.escalated = escalated
        self.additional_info = additional_info or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action_taken": self.action_taken.value,
            "severity": self.severity.value,
            "recovered": self.recovered,
            "should_retry": self.should_retry,
            "escalated": self.escalated,
            "additional_info": self.additional_info,
            "timestamp": self.timestamp.isoformat(),
        }


class ErrorHandler(ABC):
    """Abstract base class for error handlers."""

    def __init__(self, name: str):
        self.name = name
        self.handled_count = 0
        self.recovery_count = 0
        self.escalation_count = 0

    @abstractmethod
    def can_handle(self, error: Exception) -> bool:
        """Check if this handler can handle the given error."""
        pass

    @abstractmethod
    async def handle(
        self, error: Exception, context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle the error and return result."""
        pass

    def get_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity."""
        if isinstance(error, ConstitutionalComplianceError):
            return ErrorSeverity.CRITICAL
        elif isinstance(error, SecurityError):
            return ErrorSeverity.HIGH
        elif isinstance(error, DomainError):
            return ErrorSeverity.MEDIUM
        elif isinstance(error, ValidationError):
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM

    def log_error(
        self, error: Exception, context: ErrorContext, severity: ErrorSeverity
    ) -> None:
        """Log error with appropriate level."""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "severity": severity.value,
            "context": context.to_dict(),
            "handler": self.name,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error in {context.operation}", extra=error_info)
        elif severity == ErrorSeverity.HIGH:
            logger.error(
                f"High severity error in {context.operation}", extra=error_info
            )
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(
                f"Medium severity error in {context.operation}", extra=error_info
            )
        else:
            logger.info(f"Low severity error in {context.operation}", extra=error_info)

    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics."""
        return {
            "name": self.name,
            "handled_count": self.handled_count,
            "recovery_count": self.recovery_count,
            "escalation_count": self.escalation_count,
            "recovery_rate": self.recovery_count / max(self.handled_count, 1),
        }


class DomainErrorHandler(ErrorHandler):
    """Handler for domain-specific errors."""

    def __init__(self):
        super().__init__("DomainErrorHandler")
        self.fallback_strategies = {}

    def can_handle(self, error: Exception) -> bool:
        """Check if this is a domain error."""
        return isinstance(error, DomainError)

    async def handle(
        self, error: Exception, context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle domain errors with business logic recovery."""
        self.handled_count += 1
        severity = self.get_severity(error)
        self.log_error(error, context, severity)

        # Constitutional compliance errors are critical
        if isinstance(error, ConstitutionalComplianceError):
            return await self._handle_constitutional_error(error, context)

        # Try to recover based on error type
        if (
            hasattr(error, "error_code")
            and error.error_code in self.fallback_strategies
        ):
            strategy = self.fallback_strategies[error.error_code]
            try:
                fallback_result = await strategy(error, context)
                self.recovery_count += 1
                return ErrorHandlingResult(
                    action_taken=RecoveryAction.FALLBACK,
                    severity=severity,
                    recovered=True,
                    fallback_result=fallback_result,
                )
            except Exception as fallback_error:
                logger.error(f"Fallback strategy failed: {fallback_error}")

        # Default action based on severity
        if severity == ErrorSeverity.CRITICAL:
            self.escalation_count += 1
            return ErrorHandlingResult(
                action_taken=RecoveryAction.ESCALATE, severity=severity, escalated=True
            )
        else:
            return ErrorHandlingResult(
                action_taken=RecoveryAction.RETRY, severity=severity, should_retry=True
            )

    async def _handle_constitutional_error(
        self, error: ConstitutionalComplianceError, context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle constitutional compliance errors."""
        logger.critical(
            f"Constitutional compliance violation detected: {error.compliance_issue}",
            extra={
                "expected_hash": error.expected_hash,
                "actual_hash": error.actual_hash,
                "context": context.to_dict(),
            },
        )

        # Constitutional errors always escalate
        self.escalation_count += 1
        return ErrorHandlingResult(
            action_taken=RecoveryAction.ESCALATE,
            severity=ErrorSeverity.CRITICAL,
            escalated=True,
            additional_info={
                "constitutional_violation": True,
                "expected_hash": error.expected_hash,
                "actual_hash": error.actual_hash,
            },
        )

    def register_fallback_strategy(self, error_code: str, strategy: Callable) -> None:
        """Register fallback strategy for specific error code."""
        self.fallback_strategies[error_code] = strategy
        logger.info(f"Registered fallback strategy for error code: {error_code}")


class InfrastructureErrorHandler(ErrorHandler):
    """Handler for infrastructure-related errors."""

    def __init__(self):
        super().__init__("InfrastructureErrorHandler")

    def can_handle(self, error: Exception) -> bool:
        """Check if this is an infrastructure error."""
        return isinstance(error, InfrastructureError)

    async def handle(
        self, error: Exception, context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle infrastructure errors with retry and circuit breaker logic."""
        self.handled_count += 1
        severity = self.get_severity(error)
        self.log_error(error, context, severity)

        # Database errors might be transient
        if "Database" in type(error).__name__:
            return ErrorHandlingResult(
                action_taken=RecoveryAction.RETRY,
                severity=severity,
                should_retry=True,
                additional_info={"retry_delay": 2.0},
            )

        # External service errors
        if "ExternalService" in type(error).__name__:
            return ErrorHandlingResult(
                action_taken=RecoveryAction.FALLBACK,
                severity=severity,
                additional_info={"use_cache": True},
            )

        # Default retry for infrastructure issues
        return ErrorHandlingResult(
            action_taken=RecoveryAction.RETRY, severity=severity, should_retry=True
        )


class ValidationErrorHandler(ErrorHandler):
    """Handler for validation errors."""

    def __init__(self):
        super().__init__("ValidationErrorHandler")

    def can_handle(self, error: Exception) -> bool:
        """Check if this is a validation error."""
        return isinstance(error, ValidationError)

    async def handle(
        self, error: Exception, context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle validation errors (usually not retryable)."""
        self.handled_count += 1
        severity = ErrorSeverity.LOW
        self.log_error(error, context, severity)

        # Validation errors are usually client-side issues
        return ErrorHandlingResult(
            action_taken=RecoveryAction.IGNORE,
            severity=severity,
            additional_info={
                "client_error": True,
                "field_errors": getattr(error, "field_errors", {}),
            },
        )


class SecurityErrorHandler(ErrorHandler):
    """Handler for security-related errors."""

    def __init__(self):
        super().__init__("SecurityErrorHandler")

    def can_handle(self, error: Exception) -> bool:
        """Check if this is a security error."""
        return isinstance(error, SecurityError)

    async def handle(
        self, error: Exception, context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle security errors with escalation."""
        self.handled_count += 1
        severity = ErrorSeverity.HIGH
        self.log_error(error, context, severity)

        # Log security incident
        logger.warning(
            f"Security incident: {type(error).__name__}",
            extra={
                "user_id": context.user_id,
                "tenant_id": context.tenant_id,
                "operation": context.operation,
                "error_details": str(error),
            },
        )

        # Security errors always escalate
        self.escalation_count += 1
        return ErrorHandlingResult(
            action_taken=RecoveryAction.ESCALATE,
            severity=severity,
            escalated=True,
            additional_info={"security_incident": True},
        )


class PerformanceErrorHandler(ErrorHandler):
    """Handler for performance-related errors."""

    def __init__(self):
        super().__init__("PerformanceErrorHandler")

    def can_handle(self, error: Exception) -> bool:
        """Check if this is a performance error."""
        return isinstance(error, PerformanceError)

    async def handle(
        self, error: Exception, context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle performance errors with adaptive strategies."""
        self.handled_count += 1
        severity = self.get_severity(error)
        self.log_error(error, context, severity)

        # Timeout errors might be retryable with longer timeout
        if "Timeout" in type(error).__name__:
            return ErrorHandlingResult(
                action_taken=RecoveryAction.RETRY,
                severity=severity,
                should_retry=True,
                additional_info={"increase_timeout": True},
            )

        # Rate limit errors should back off
        if "RateLimit" in type(error).__name__:
            return ErrorHandlingResult(
                action_taken=RecoveryAction.RETRY,
                severity=severity,
                should_retry=True,
                additional_info={"backoff_delay": 10.0},
            )

        return ErrorHandlingResult(
            action_taken=RecoveryAction.FALLBACK, severity=severity
        )


class GlobalErrorHandler:
    """Global error handler that coordinates multiple specific handlers."""

    def __init__(self):
        self.handlers: List[ErrorHandler] = [
            DomainErrorHandler(),
            InfrastructureErrorHandler(),
            ValidationErrorHandler(),
            SecurityErrorHandler(),
            PerformanceErrorHandler(),
        ]
        self.default_handler = self._create_default_handler()
        self.error_history: List[Dict[str, Any]] = []
        self.max_history = 1000

    def _create_default_handler(self) -> ErrorHandler:
        """Create default handler for unclassified errors."""

        class DefaultErrorHandler(ErrorHandler):
            def __init__(self):
                super().__init__("DefaultErrorHandler")

            def can_handle(self, error: Exception) -> bool:
                return True

            async def handle(
                self, error: Exception, context: ErrorContext
            ) -> ErrorHandlingResult:
                self.handled_count += 1
                severity = ErrorSeverity.MEDIUM
                self.log_error(error, context, severity)

                return ErrorHandlingResult(
                    action_taken=RecoveryAction.ESCALATE,
                    severity=severity,
                    escalated=True,
                    additional_info={"unclassified_error": True},
                )

        return DefaultErrorHandler()

    async def handle_error(
        self, error: Exception, context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle error using appropriate handler."""
        # Find suitable handler
        handler = None
        for h in self.handlers:
            if h.can_handle(error):
                handler = h
                break

        if handler is None:
            handler = self.default_handler

        # Handle the error
        try:
            result = await handler.handle(error, context)

            # Record in history
            self._record_error(error, context, result)

            return result

        except Exception as handler_error:
            logger.error(f"Error handler failed: {handler_error}")

            # Fallback to basic escalation
            return ErrorHandlingResult(
                action_taken=RecoveryAction.ESCALATE,
                severity=ErrorSeverity.CRITICAL,
                escalated=True,
                additional_info={"handler_failed": True},
            )

    def _record_error(
        self, error: Exception, context: ErrorContext, result: ErrorHandlingResult
    ) -> None:
        """Record error in history for analysis."""
        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context.to_dict(),
            "handling_result": result.to_dict(),
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        self.error_history.append(error_record)

        # Trim history if too large
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history :]

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        handler_stats = {
            handler.name: handler.get_stats()
            for handler in self.handlers + [self.default_handler]
        }

        total_handled = sum(stats["handled_count"] for stats in handler_stats.values())
        total_recovered = sum(
            stats["recovery_count"] for stats in handler_stats.values()
        )
        total_escalated = sum(
            stats["escalation_count"] for stats in handler_stats.values()
        )

        return {
            "total_errors_handled": total_handled,
            "total_recovered": total_recovered,
            "total_escalated": total_escalated,
            "overall_recovery_rate": total_recovered / max(total_handled, 1),
            "escalation_rate": total_escalated / max(total_handled, 1),
            "handler_statistics": handler_stats,
            "recent_errors": self.error_history[-10:],  # Last 10 errors
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

    def register_custom_handler(self, handler: ErrorHandler) -> None:
        """Register a custom error handler."""
        self.handlers.insert(0, handler)  # Insert at beginning for priority
        logger.info(f"Registered custom error handler: {handler.name}")


# Global error handler instance
_global_error_handler = GlobalErrorHandler()


def get_global_error_handler() -> GlobalErrorHandler:
    """Get the global error handler instance."""
    return _global_error_handler


async def handle_error(error: Exception, context: ErrorContext) -> ErrorHandlingResult:
    """Convenience function to handle errors globally."""
    return await _global_error_handler.handle_error(error, context)
