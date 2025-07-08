"""
ACGS Exception Classes
Constitutional Hash: cdd01ef066bc6cf2

Custom exception classes for ACGS scripts.
"""

from typing import Any, Optional

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ACGSError(Exception):
    """Base exception class for all ACGS errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "constitutional_hash": self.constitutional_hash,
        }


class ValidationError(ACGSError):
    """Exception raised when validation fails."""

    def __init__(
        self,
        message: str,
        validation_type: Optional[str] = None,
        failed_checks: Optional[list] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.validation_type = validation_type
        self.failed_checks = failed_checks or []

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        result = super().to_dict()
        result.update({
            "validation_type": self.validation_type,
            "failed_checks": self.failed_checks,
        })
        return result


class ConfigurationError(ACGSError):
    """Exception raised when configuration is invalid."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        expected_value: Optional[str] = None,
        actual_value: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.expected_value = expected_value
        self.actual_value = actual_value

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        result = super().to_dict()
        result.update({
            "config_key": self.config_key,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
        })
        return result


class ServiceError(ACGSError):
    """Exception raised when service operations fail."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.status_code = status_code
        self.response_data = response_data or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        result = super().to_dict()
        result.update({
            "service_name": self.service_name,
            "status_code": self.status_code,
            "response_data": self.response_data,
        })
        return result


class TimeoutError(ACGSError):
    """Exception raised when operations timeout."""

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.operation = operation

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        result = super().to_dict()
        result.update({
            "timeout_seconds": self.timeout_seconds,
            "operation": self.operation,
        })
        return result


class RetryExhaustedError(ACGSError):
    """Exception raised when retry attempts are exhausted."""

    def __init__(
        self,
        message: str,
        max_retries: Optional[int] = None,
        last_error: Optional[Exception] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.max_retries = max_retries
        self.last_error = last_error

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        result = super().to_dict()
        result.update({
            "max_retries": self.max_retries,
            "last_error": str(self.last_error) if self.last_error else None,
        })
        return result


class ConstitutionalComplianceError(ValidationError):
    """Exception raised when constitutional compliance checks fail."""

    def __init__(
        self,
        message: str,
        expected_hash: str = CONSTITUTIONAL_HASH,
        actual_hash: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, validation_type="constitutional_compliance", **kwargs)
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        result = super().to_dict()
        result.update({
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
        })
        return result
