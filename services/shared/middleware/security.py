"""
ACGS-1 Security Middleware
Comprehensive security middleware for all services
"""

import logging
import re
import secrets
import time
from functools import wraps
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Comprehensive security middleware for ACGS-1"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.rate_limits = {}
        self.failed_attempts = {}

    def add_security_headers(self, response):
        """Add security headers to response"""
        headers = self.config.get("headers", {})
        for header, value in headers.items():
            response.headers[header] = value
        return response

    def validate_input(self, data: str) -> bool:
        """Validate input for security threats"""
        # Check for common injection patterns
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",  # XSS
            r"javascript:",  # JavaScript injection
            r"on\w+\s*=",  # Event handlers
            r"union\s+select",  # SQL injection
            r"drop\s+table",  # SQL injection
            r"exec\s*\(",  # Code execution
            r"eval\s*\(",  # Code execution
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False

        return True

    def rate_limit(self, identifier: str, limit: int = 60) -> bool:
        """Rate limiting implementation"""
        current_time = time.time()

        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []

        # Clean old requests
        self.rate_limits[identifier] = [
            req_time
            for req_time in self.rate_limits[identifier]
            if current_time - req_time < 60
        ]

        # Check limit
        if len(self.rate_limits[identifier]) >= limit:
            return False

        # Add current request
        self.rate_limits[identifier].append(current_time)
        return True

    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)

    def validate_csrf_token(self, token: str, expected: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, expected)

    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        import bcrypt

        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password"""
        import bcrypt

        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def security_required(f: Callable) -> Callable:
    """Decorator for security-required endpoints"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add security checks here
        return f(*args, **kwargs)

    return decorated_function


def rate_limited(limit: int = 60):
    """Rate limiting decorator"""

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Add rate limiting logic here
            return f(*args, **kwargs)

        return decorated_function

    return decorator
