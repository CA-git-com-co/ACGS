"""
ACGS Exception Hierarchy
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive exception hierarchy for proper error handling and classification.
"""

from datetime import datetime
from typing import Any


class ACGSError(Exception):
    """Base exception for all ACGS-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
        constitutional_hash: str = "cdd01ef066bc6cf2",
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause
        self.constitutional_hash = constitutional_hash
        self.timestamp = datetime.utcnow()
        self.context = {}

    def add_context(self, key: str, value: Any) -> "ACGSError":
        """Add contextual information to the error."""
        self.context[key] = value
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "cause": str(self.cause) if self.cause else None,
        }


class DomainError(ACGSError):
    """Base class for domain-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated."""

    def __init__(self, rule_name: str, violation_details: dict[str, Any], **kwargs):
        message = f"Business rule violation: {rule_name}"
        super().__init__(message, **kwargs)
        self.rule_name = rule_name
        self.violation_details = violation_details
        self.details.update(
            {"rule_name": rule_name, "violation_details": violation_details}
        )


class ConstitutionalComplianceError(DomainError):
    """Raised when constitutional compliance is violated."""

    def __init__(
        self,
        compliance_issue: str,
        expected_hash: str,
        actual_hash: str | None = None,
        **kwargs,
    ):
        message = f"Constitutional compliance violation: {compliance_issue}"
        super().__init__(message, **kwargs)
        self.compliance_issue = compliance_issue
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        self.details.update(
            {
                "compliance_issue": compliance_issue,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
            }
        )


class AggregateNotFoundError(DomainError):
    """Raised when an aggregate is not found."""

    def __init__(self, aggregate_type: str, aggregate_id: str, **kwargs):
        message = f"{aggregate_type} with ID {aggregate_id} not found"
        super().__init__(message, **kwargs)
        self.aggregate_type = aggregate_type
        self.aggregate_id = aggregate_id
        self.details.update(
            {"aggregate_type": aggregate_type, "aggregate_id": aggregate_id}
        )


class DomainValidationError(DomainError):
    """Raised when domain validation fails."""

    def __init__(
        self, field_name: str, validation_message: str, value: Any = None, **kwargs
    ):
        message = f"Validation failed for {field_name}: {validation_message}"
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.validation_message = validation_message
        self.value = value
        self.details.update(
            {
                "field_name": field_name,
                "validation_message": validation_message,
                "value": str(value) if value is not None else None,
            }
        )


class InfrastructureError(ACGSError):
    """Base class for infrastructure-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class DatabaseError(InfrastructureError):
    """Raised when database operations fail."""

    def __init__(
        self,
        operation: str,
        table: str | None = None,
        query: str | None = None,
        **kwargs,
    ):
        message = f"Database error during {operation}"
        if table:
            message += f" on table {table}"
        super().__init__(message, **kwargs)
        self.operation = operation
        self.table = table
        self.query = query
        self.details.update({"operation": operation, "table": table, "query": query})


class EventStoreError(InfrastructureError):
    """Raised when event store operations fail."""

    def __init__(self, stream_id: str, operation: str, **kwargs):
        message = f"Event store error for stream {stream_id} during {operation}"
        super().__init__(message, **kwargs)
        self.stream_id = stream_id
        self.operation = operation
        self.details.update({"stream_id": stream_id, "operation": operation})


class ExternalServiceError(InfrastructureError):
    """Raised when external service calls fail."""

    def __init__(
        self, service_name: str, endpoint: str, status_code: int | None = None, **kwargs
    ):
        message = f"External service error: {service_name} at {endpoint}"
        if status_code:
            message += f" (HTTP {status_code})"
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.endpoint = endpoint
        self.status_code = status_code
        self.details.update(
            {
                "service_name": service_name,
                "endpoint": endpoint,
                "status_code": status_code,
            }
        )


class ValidationError(ACGSError):
    """Base class for validation errors."""

    def __init__(
        self, message: str, field_errors: dict[str, str] | None = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field_errors = field_errors or {}
        self.details.update({"field_errors": self.field_errors})


class InputValidationError(ValidationError):
    """Raised when input validation fails."""

    def __init__(self, field_name: str, value: Any, constraint: str, **kwargs):
        message = f"Input validation failed for {field_name}: {constraint}"
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.value = value
        self.constraint = constraint
        self.details.update(
            {"field_name": field_name, "value": str(value), "constraint": constraint}
        )


class SchemaValidationError(ValidationError):
    """Raised when schema validation fails."""

    def __init__(self, schema_name: str, validation_errors: list, **kwargs):
        message = f"Schema validation failed for {schema_name}"
        super().__init__(message, **kwargs)
        self.schema_name = schema_name
        self.validation_errors = validation_errors
        self.details.update(
            {"schema_name": schema_name, "validation_errors": validation_errors}
        )


class ConfigurationError(ACGSError):
    """Base class for configuration-related errors."""

    def __init__(self, config_key: str, issue: str, **kwargs):
        message = f"Configuration error for {config_key}: {issue}"
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.issue = issue
        self.details.update({"config_key": config_key, "issue": issue})


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, config_key: str, **kwargs):
        super().__init__(config_key, "Required configuration missing", **kwargs)


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration is invalid."""

    def __init__(
        self, config_key: str, expected_type: str, actual_value: Any, **kwargs
    ):
        issue = f"Expected {expected_type}, got {type(actual_value).__name__}: {actual_value}"
        super().__init__(config_key, issue, **kwargs)
        self.expected_type = expected_type
        self.actual_value = actual_value


class SecurityError(ACGSError):
    """Base class for security-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class AuthenticationError(SecurityError):
    """Raised when authentication fails."""

    def __init__(self, reason: str, **kwargs):
        message = f"Authentication failed: {reason}"
        super().__init__(message, **kwargs)
        self.reason = reason
        self.details.update({"reason": reason})


class AuthorizationError(SecurityError):
    """Raised when authorization fails."""

    def __init__(self, user_id: str, resource: str, action: str, **kwargs):
        message = f"Authorization failed: User {user_id} cannot {action} on {resource}"
        super().__init__(message, **kwargs)
        self.user_id = user_id
        self.resource = resource
        self.action = action
        self.details.update(
            {"user_id": user_id, "resource": resource, "action": action}
        )


class TenantIsolationError(SecurityError):
    """Raised when tenant isolation is violated."""

    def __init__(self, tenant_id: str, violation_type: str, **kwargs):
        message = f"Tenant isolation violation for {tenant_id}: {violation_type}"
        super().__init__(message, **kwargs)
        self.tenant_id = tenant_id
        self.violation_type = violation_type
        self.details.update({"tenant_id": tenant_id, "violation_type": violation_type})


class PerformanceError(ACGSError):
    """Base class for performance-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class TimeoutError(PerformanceError):
    """Raised when operations timeout."""

    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, **kwargs)
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        self.details.update(
            {"operation": operation, "timeout_seconds": timeout_seconds}
        )


class RateLimitExceededError(PerformanceError):
    """Raised when rate limits are exceeded."""

    def __init__(self, limit: int, window_seconds: int, **kwargs):
        message = f"Rate limit exceeded: {limit} requests per {window_seconds} seconds"
        super().__init__(message, **kwargs)
        self.limit = limit
        self.window_seconds = window_seconds
        self.details.update({"limit": limit, "window_seconds": window_seconds})


class ResourceExhaustionError(PerformanceError):
    """Raised when system resources are exhausted."""

    def __init__(
        self, resource_type: str, current_usage: float, limit: float, **kwargs
    ):
        message = f"Resource exhaustion: {resource_type} usage {current_usage:.2f} exceeds limit {limit:.2f}"
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.current_usage = current_usage
        self.limit = limit
        self.details.update(
            {
                "resource_type": resource_type,
                "current_usage": current_usage,
                "limit": limit,
            }
        )


class ConcurrencyError(ACGSError):
    """Base class for concurrency-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class OptimisticLockingError(ConcurrencyError):
    """Raised when optimistic locking fails."""

    def __init__(
        self, aggregate_id: str, expected_version: int, actual_version: int, **kwargs
    ):
        message = f"Optimistic locking failed for {aggregate_id}: expected version {expected_version}, got {actual_version}"
        super().__init__(message, **kwargs)
        self.aggregate_id = aggregate_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        self.details.update(
            {
                "aggregate_id": aggregate_id,
                "expected_version": expected_version,
                "actual_version": actual_version,
            }
        )


class DeadlockError(ConcurrencyError):
    """Raised when database deadlocks occur."""

    def __init__(self, operation: str, **kwargs):
        message = f"Deadlock detected during {operation}"
        super().__init__(message, **kwargs)
        self.operation = operation
        self.details.update({"operation": operation})
