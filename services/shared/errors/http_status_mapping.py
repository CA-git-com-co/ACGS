"""
ACGS-1 HTTP Status Code Mapping

This module provides comprehensive HTTP status code mapping for ACGS error responses.
It ensures consistent status code usage across all services and provides automatic
status code assignment based on error categories and business logic.

HTTP Status Code Standards:
- 400 Bad Request: Client error in request format or parameters
- 401 Unauthorized: Authentication required or failed
- 403 Forbidden: Authenticated but insufficient permissions
- 404 Not Found: Requested resource does not exist
- 408 Request Timeout: Request processing timeout
- 409 Conflict: Resource conflict (e.g., duplicate creation)
- 422 Unprocessable Entity: Valid format but business logic error
- 429 Too Many Requests: Rate limiting exceeded
- 500 Internal Server Error: Unexpected server error
- 503 Service Unavailable: Service temporarily unavailable
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Set, Tuple

from .error_catalog import ErrorCategory, ErrorSeverity, ServiceCode


class HTTPStatusCode(int, Enum):
    """Standard HTTP status codes used in ACGS."""

    # Client Error Codes (4xx)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # Server Error Codes (5xx)
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

    @property
    def is_client_error(self) -> bool:
        """Check if status code is a client error (4xx)."""
        return 400 <= self.value < 500

    @property
    def is_server_error(self) -> bool:
        """Check if status code is a server error (5xx)."""
        return 500 <= self.value < 600

    @property
    def is_retryable(self) -> bool:
        """Check if the error is typically retryable."""
        retryable_codes = {
            HTTPStatusCode.REQUEST_TIMEOUT,
            HTTPStatusCode.TOO_MANY_REQUESTS,
            HTTPStatusCode.INTERNAL_SERVER_ERROR,
            HTTPStatusCode.SERVICE_UNAVAILABLE,
        }
        return self in retryable_codes


@dataclass
class StatusCodeRule:
    """Rule for determining HTTP status code based on error characteristics."""

    category: ErrorCategory
    severity: Optional[ErrorSeverity] = None
    service: Optional[ServiceCode] = None
    error_pattern: Optional[str] = None
    status_code: HTTPStatusCode = HTTPStatusCode.INTERNAL_SERVER_ERROR
    priority: int = 0  # Higher priority rules take precedence

    def matches(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        service: ServiceCode,
        error_code: str,
    ) -> bool:
        """Check if this rule matches the given error characteristics."""

        # Category must match
        if self.category != category:
            return False

        # Severity must match if specified
        if self.severity and self.severity != severity:
            return False

        # Service must match if specified
        if self.service and self.service != service:
            return False

        # Error pattern must match if specified
        if self.error_pattern and self.error_pattern not in error_code:
            return False

        return True


class HTTPStatusMapper:
    """Maps error characteristics to appropriate HTTP status codes."""

    def __init__(self):
        self.rules: List[StatusCodeRule] = []
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default status code mapping rules."""

        # High priority specific rules
        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.AUTHENTICATION,
                severity=ErrorSeverity.WARNING,
                error_pattern="ACCOUNT_LOCKED",
                status_code=HTTPStatusCode.UNAUTHORIZED,
                priority=100,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.AUTHENTICATION,
                severity=ErrorSeverity.INFO,
                error_pattern="TOKEN_EXPIRED",
                status_code=HTTPStatusCode.UNAUTHORIZED,
                priority=100,
            )
        )

        # Category-based rules (medium priority)
        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.VALIDATION,
                status_code=HTTPStatusCode.BAD_REQUEST,
                priority=50,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.AUTHENTICATION,
                status_code=HTTPStatusCode.UNAUTHORIZED,
                priority=50,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.AUTHORIZATION,
                status_code=HTTPStatusCode.FORBIDDEN,
                priority=50,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.BUSINESS_LOGIC,
                status_code=HTTPStatusCode.UNPROCESSABLE_ENTITY,
                priority=50,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.EXTERNAL_SERVICE,
                status_code=HTTPStatusCode.SERVICE_UNAVAILABLE,
                priority=50,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.SYSTEM_ERROR,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                priority=50,
            )
        )

        # Severity-based overrides (lower priority)
        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.BUSINESS_LOGIC,
                severity=ErrorSeverity.WARNING,
                error_pattern="CONFLICT",
                status_code=HTTPStatusCode.CONFLICT,
                priority=75,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.BUSINESS_LOGIC,
                severity=ErrorSeverity.WARNING,
                error_pattern="NOT_FOUND",
                status_code=HTTPStatusCode.NOT_FOUND,
                priority=75,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.EXTERNAL_SERVICE,
                severity=ErrorSeverity.WARNING,
                error_pattern="TIMEOUT",
                status_code=HTTPStatusCode.REQUEST_TIMEOUT,
                priority=75,
            )
        )

        # Service-specific rules
        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.BUSINESS_LOGIC,
                service=ServiceCode.FV,
                error_pattern="TIMEOUT",
                status_code=HTTPStatusCode.REQUEST_TIMEOUT,
                priority=60,
            )
        )

        self.add_rule(
            StatusCodeRule(
                category=ErrorCategory.BUSINESS_LOGIC,
                service=ServiceCode.DGM,
                severity=ErrorSeverity.CRITICAL,
                error_pattern="SAFETY_VIOLATION",
                status_code=HTTPStatusCode.FORBIDDEN,
                priority=90,
            )
        )

    def add_rule(self, rule: StatusCodeRule):
        """Add a status code mapping rule."""
        self.rules.append(rule)
        # Sort by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def get_status_code(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        service: ServiceCode,
        error_code: str,
    ) -> HTTPStatusCode:
        """Get appropriate HTTP status code for error characteristics."""

        # Find the highest priority matching rule
        for rule in self.rules:
            if rule.matches(category, severity, service, error_code):
                return rule.status_code

        # Fallback to default based on category
        category_defaults = {
            ErrorCategory.VALIDATION: HTTPStatusCode.BAD_REQUEST,
            ErrorCategory.AUTHENTICATION: HTTPStatusCode.UNAUTHORIZED,
            ErrorCategory.AUTHORIZATION: HTTPStatusCode.FORBIDDEN,
            ErrorCategory.BUSINESS_LOGIC: HTTPStatusCode.UNPROCESSABLE_ENTITY,
            ErrorCategory.EXTERNAL_SERVICE: HTTPStatusCode.SERVICE_UNAVAILABLE,
            ErrorCategory.SYSTEM_ERROR: HTTPStatusCode.INTERNAL_SERVER_ERROR,
        }

        return category_defaults.get(category, HTTPStatusCode.INTERNAL_SERVER_ERROR)

    def is_retryable_error(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        service: ServiceCode,
        error_code: str,
    ) -> bool:
        """Determine if error is retryable based on status code and characteristics."""
        status_code = self.get_status_code(category, severity, service, error_code)

        # Status code based retryability
        if status_code.is_retryable:
            return True

        # Additional business logic for retryability
        retryable_patterns = {"TIMEOUT", "UNAVAILABLE", "RATE_LIMIT", "TEMPORARY"}

        return any(pattern in error_code for pattern in retryable_patterns)

    def get_error_headers(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        service: ServiceCode,
        error_code: str,
    ) -> Dict[str, str]:
        """Get appropriate HTTP headers for error response."""
        headers = {}

        status_code = self.get_status_code(category, severity, service, error_code)

        # Add retry-after header for retryable errors
        if self.is_retryable_error(category, severity, service, error_code):
            if status_code == HTTPStatusCode.TOO_MANY_REQUESTS:
                headers["Retry-After"] = "60"  # 1 minute for rate limiting
            elif status_code == HTTPStatusCode.SERVICE_UNAVAILABLE:
                headers["Retry-After"] = "300"  # 5 minutes for service unavailable
            elif "TIMEOUT" in error_code:
                headers["Retry-After"] = "30"  # 30 seconds for timeouts

        # Add authentication headers
        if category == ErrorCategory.AUTHENTICATION:
            headers["WWW-Authenticate"] = "Bearer"

        # Add CORS headers for browser requests
        headers.update(
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID",
            }
        )

        return headers


class StatusCodeValidator:
    """Validates HTTP status code usage consistency."""

    def __init__(self):
        self.valid_status_codes = {code.value for code in HTTPStatusCode}
        self.usage_stats: Dict[int, int] = {}

    def validate_status_code(self, status_code: int) -> bool:
        """Validate that status code is in approved list."""
        return status_code in self.valid_status_codes

    def record_usage(self, status_code: int):
        """Record status code usage for monitoring."""
        self.usage_stats[status_code] = self.usage_stats.get(status_code, 0) + 1

    def get_usage_report(self) -> Dict[str, any]:
        """Get status code usage report."""
        total_usage = sum(self.usage_stats.values())

        return {
            "total_responses": total_usage,
            "status_code_distribution": {
                str(code): {
                    "count": count,
                    "percentage": (count / total_usage * 100) if total_usage > 0 else 0,
                }
                for code, count in self.usage_stats.items()
            },
            "client_error_rate": (
                sum(count for code, count in self.usage_stats.items() if 400 <= code < 500)
                / total_usage
                * 100
                if total_usage > 0
                else 0
            ),
            "server_error_rate": (
                sum(count for code, count in self.usage_stats.items() if 500 <= code < 600)
                / total_usage
                * 100
                if total_usage > 0
                else 0
            ),
        }


# ACGS-specific status code extensions
class ACGSStatusCode(HTTPStatusCode):
    """ACGS-specific status codes for domain-specific scenarios."""

    # Constitutional compliance failures (422 with specific meaning)
    CONSTITUTIONAL_VIOLATION = 422

    # Policy synthesis failures (422 with specific meaning)
    POLICY_SYNTHESIS_FAILED = 422

    # Formal verification failures (422 with specific meaning)
    VERIFICATION_FAILED = 422

    # Self-improvement safety violations (403 with specific meaning)
    SAFETY_CONSTRAINT_VIOLATION = 403


# Global instances
status_mapper = HTTPStatusMapper()
status_validator = StatusCodeValidator()


# Convenience functions
def get_http_status_code(
    category: ErrorCategory, severity: ErrorSeverity, service: ServiceCode, error_code: str
) -> HTTPStatusCode:
    """Get HTTP status code for error characteristics."""
    return status_mapper.get_status_code(category, severity, service, error_code)


def is_error_retryable(
    category: ErrorCategory, severity: ErrorSeverity, service: ServiceCode, error_code: str
) -> bool:
    """Check if error is retryable."""
    return status_mapper.is_retryable_error(category, severity, service, error_code)


def get_error_response_headers(
    category: ErrorCategory, severity: ErrorSeverity, service: ServiceCode, error_code: str
) -> Dict[str, str]:
    """Get appropriate headers for error response."""
    return status_mapper.get_error_headers(category, severity, service, error_code)


def validate_status_code_usage(status_code: int) -> bool:
    """Validate status code is approved for use."""
    is_valid = status_validator.validate_status_code(status_code)
    if is_valid:
        status_validator.record_usage(status_code)
    return is_valid


def get_status_code_usage_report() -> Dict[str, any]:
    """Get status code usage statistics."""
    return status_validator.get_usage_report()


# Export main classes and functions
__all__ = [
    "HTTPStatusCode",
    "ACGSStatusCode",
    "StatusCodeRule",
    "HTTPStatusMapper",
    "StatusCodeValidator",
    "status_mapper",
    "status_validator",
    "get_http_status_code",
    "is_error_retryable",
    "get_error_response_headers",
    "validate_status_code_usage",
    "get_status_code_usage_report",
]
