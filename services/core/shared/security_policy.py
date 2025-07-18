"""
Production Security Policy Implementation for ACGS-2
Constitutional Hash: cdd01ef066bc6cf2

This module provides comprehensive security policies to replace
placeholder implementations and ensure production-ready security.
"""

import hashlib
import hmac
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import secrets
import jwt
from datetime import datetime, timedelta
import re
import ipaddress

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security classification levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class ThreatLevel(Enum):
    """Threat assessment levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityContext:
    """Security context for requests."""

    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    security_level: SecurityLevel
    permissions: List[str]
    constitutional_hash: str = "cdd01ef066bc6cf2"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "security_level": self.security_level.value,
            "permissions": self.permissions,
            "constitutional_hash": self.constitutional_hash,
        }


class SecurityPolicy:
    """
    Comprehensive security policy implementation.

    Features:
    - Input validation and sanitization
    - Authentication and authorization
    - Rate limiting and DDoS protection
    - Constitutional compliance validation
    - Audit logging and monitoring
    - Threat detection and response
    """

    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    # Security patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+\'\w+\'\s*=\s*\'\w+\')",
        r"(\;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION))",
        r"(\-\-|\#|\\\*|\\\*/)",
    ]

    XSS_PATTERNS = [
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(on\w+\s*=)",
        r"(<iframe[^>]*>.*?</iframe>)",
        r"(<embed[^>]*>.*?</embed>)",
        r"(<object[^>]*>.*?</object>)",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r"(\||\&|\;|\$\(|\`)",
        r"(\\x[0-9a-fA-F]{2})",
        r"(\.\./)",
        r"(\\\\)",
    ]

    def __init__(self, jwt_secret: str):
        """Initialize security policy."""
        self.jwt_secret = jwt_secret
        self.failed_attempts: Dict[str, int] = {}
        self.blocked_ips: Dict[str, float] = {}
        self.rate_limits: Dict[str, List[float]] = {}

        # Compile regex patterns for performance
        self.sql_injection_regex = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SQL_INJECTION_PATTERNS
        ]
        self.xss_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS
        ]
        self.command_injection_regex = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.COMMAND_INJECTION_PATTERNS
        ]

        logger.info("Security policy initialized with constitutional compliance")

    def validate_input(self, input_data: Any, context: SecurityContext) -> bool:
        """
        Validate input data for security threats.

        Args:
            input_data: Input data to validate
            context: Security context

        Returns:
            bool: True if input is safe
        """
        if not isinstance(input_data, str):
            input_data = str(input_data)

        # Check for SQL injection
        if self._detect_sql_injection(input_data):
            logger.warning(f"SQL injection attempt detected from {context.ip_address}")
            return False

        # Check for XSS
        if self._detect_xss(input_data):
            logger.warning(f"XSS attempt detected from {context.ip_address}")
            return False

        # Check for command injection
        if self._detect_command_injection(input_data):
            logger.warning(
                f"Command injection attempt detected from {context.ip_address}"
            )
            return False

        # Check input length
        if len(input_data) > 10000:  # 10KB limit
            logger.warning(f"Input length exceeds limit from {context.ip_address}")
            return False

        return True

    def _detect_sql_injection(self, input_data: str) -> bool:
        """Detect SQL injection patterns."""
        for pattern in self.sql_injection_regex:
            if pattern.search(input_data):
                return True
        return False

    def _detect_xss(self, input_data: str) -> bool:
        """Detect XSS patterns."""
        for pattern in self.xss_regex:
            if pattern.search(input_data):
                return True
        return False

    def _detect_command_injection(self, input_data: str) -> bool:
        """Detect command injection patterns."""
        for pattern in self.command_injection_regex:
            if pattern.search(input_data):
                return True
        return False

    def validate_constitutional_compliance(self, request_data: Dict[str, Any]) -> bool:
        """
        Validate constitutional compliance.

        Args:
            request_data: Request data to validate

        Returns:
            bool: True if constitutionally compliant
        """
        # Check constitutional hash
        constitutional_hash = request_data.get("constitutional_hash")
        if constitutional_hash != self.CONSTITUTIONAL_HASH:
            logger.warning(f"Constitutional hash mismatch: {constitutional_hash}")
            return False

        # Check required fields
        required_fields = ["user_id", "operation", "timestamp"]
        for field in required_fields:
            if field not in request_data:
                logger.warning(f"Missing required field: {field}")
                return False

        # Check timestamp validity (within 5 minutes)
        try:
            timestamp = float(request_data["timestamp"])
            current_time = time.time()
            if abs(current_time - timestamp) > 300:  # 5 minutes
                logger.warning(f"Timestamp outside valid window: {timestamp}")
                return False
        except (ValueError, TypeError):
            logger.warning(f"Invalid timestamp format: {request_data.get('timestamp')}")
            return False

        return True

    def authenticate_user(self, token: str) -> Optional[SecurityContext]:
        """
        Authenticate user with JWT token.

        Args:
            token: JWT token to validate

        Returns:
            Optional[SecurityContext]: Security context if valid
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])

            # Extract user information
            user_id = payload.get("user_id")
            session_id = payload.get("session_id")
            permissions = payload.get("permissions", [])
            security_level = SecurityLevel(payload.get("security_level", "internal"))

            # Validate constitutional compliance
            if payload.get("constitutional_hash") != self.CONSTITUTIONAL_HASH:
                logger.warning(
                    f"Constitutional hash mismatch in token for user: {user_id}"
                )
                return None

            # Check token expiration
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                logger.warning(f"Expired token for user: {user_id}")
                return None

            return SecurityContext(
                user_id=user_id,
                session_id=session_id,
                ip_address="",  # Will be filled by middleware
                user_agent="",  # Will be filled by middleware
                security_level=security_level,
                permissions=permissions,
                constitutional_hash=self.CONSTITUTIONAL_HASH,
            )

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    def authorize_operation(
        self, context: SecurityContext, operation: str, resource: str
    ) -> bool:
        """
        Authorize operation based on security context.

        Args:
            context: Security context
            operation: Operation to authorize
            resource: Resource being accessed

        Returns:
            bool: True if authorized
        """
        # Check if user has required permission
        required_permission = f"{operation}:{resource}"
        if required_permission not in context.permissions:
            # Check for wildcard permissions
            wildcard_permission = f"{operation}:*"
            if wildcard_permission not in context.permissions:
                admin_permission = "admin:*"
                if admin_permission not in context.permissions:
                    logger.warning(
                        f"Unauthorized operation: {required_permission} for user: {context.user_id}"
                    )
                    return False

        # Check security level requirements
        resource_security_requirements = {
            "constitutional_data": SecurityLevel.CONFIDENTIAL,
            "user_data": SecurityLevel.INTERNAL,
            "system_config": SecurityLevel.RESTRICTED,
            "audit_logs": SecurityLevel.RESTRICTED,
        }

        required_level = resource_security_requirements.get(
            resource, SecurityLevel.INTERNAL
        )
        if not self._check_security_level(context.security_level, required_level):
            logger.warning(f"Insufficient security level for resource: {resource}")
            return False

        return True

    def _check_security_level(
        self, user_level: SecurityLevel, required_level: SecurityLevel
    ) -> bool:
        """Check if user security level meets requirement."""
        level_hierarchy = {
            SecurityLevel.PUBLIC: 0,
            SecurityLevel.INTERNAL: 1,
            SecurityLevel.CONFIDENTIAL: 2,
            SecurityLevel.RESTRICTED: 3,
            SecurityLevel.TOP_SECRET: 4,
        }

        return level_hierarchy.get(user_level, 0) >= level_hierarchy.get(
            required_level, 0
        )

    def check_rate_limit(
        self, identifier: str, limit: int = 100, window: int = 60
    ) -> bool:
        """
        Check rate limit for identifier.

        Args:
            identifier: Identifier to check (IP, user_id, etc.)
            limit: Request limit
            window: Time window in seconds

        Returns:
            bool: True if within limit
        """
        current_time = time.time()

        # Clean old entries
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                timestamp
                for timestamp in self.rate_limits[identifier]
                if current_time - timestamp < window
            ]
        else:
            self.rate_limits[identifier] = []

        # Check limit
        if len(self.rate_limits[identifier]) >= limit:
            logger.warning(f"Rate limit exceeded for: {identifier}")
            return False

        # Add current request
        self.rate_limits[identifier].append(current_time)
        return True

    def detect_threat(
        self, context: SecurityContext, request_data: Dict[str, Any]
    ) -> ThreatLevel:
        """
        Detect potential security threats.

        Args:
            context: Security context
            request_data: Request data

        Returns:
            ThreatLevel: Assessed threat level
        """
        threat_score = 0

        # Check for suspicious patterns
        if self._is_suspicious_ip(context.ip_address):
            threat_score += 3

        if self._is_suspicious_user_agent(context.user_agent):
            threat_score += 2

        if self._has_suspicious_parameters(request_data):
            threat_score += 2

        if self._check_failed_attempts(context.user_id):
            threat_score += 1

        # Determine threat level
        if threat_score >= 6:
            return ThreatLevel.CRITICAL
        elif threat_score >= 4:
            return ThreatLevel.HIGH
        elif threat_score >= 2:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious."""
        try:
            ip = ipaddress.ip_address(ip_address)

            # Check for private/internal IPs in external requests
            if ip.is_private and not ip.is_loopback:
                return True

            # Check blocked IPs
            if ip_address in self.blocked_ips:
                return True

            return False
        except ValueError:
            return True  # Invalid IP is suspicious

    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious."""
        suspicious_agents = [
            "sqlmap",
            "nikto",
            "burp",
            "nmap",
            "gobuster",
            "dirb",
            "dirbuster",
            "wpscan",
            "curl",
            "wget",
        ]

        user_agent_lower = user_agent.lower()
        return any(agent in user_agent_lower for agent in suspicious_agents)

    def _has_suspicious_parameters(self, request_data: Dict[str, Any]) -> bool:
        """Check for suspicious parameters."""
        # Check for suspicious parameter names
        suspicious_params = [
            "admin",
            "root",
            "system",
            "config",
            "passwd",
            "shadow",
            "sql",
            "query",
            "exec",
            "eval",
        ]

        for key in request_data.keys():
            if any(param in key.lower() for param in suspicious_params):
                return True

        return False

    def _check_failed_attempts(self, user_id: str) -> bool:
        """Check for repeated failed attempts."""
        return self.failed_attempts.get(user_id, 0) > 3

    def generate_secure_token(
        self,
        user_id: str,
        permissions: List[str],
        security_level: SecurityLevel = SecurityLevel.INTERNAL,
        expires_in: int = 3600,
    ) -> str:
        """
        Generate secure JWT token.

        Args:
            user_id: User identifier
            permissions: User permissions
            security_level: Security level
            expires_in: Token expiration in seconds

        Returns:
            str: JWT token
        """
        payload = {
            "user_id": user_id,
            "session_id": secrets.token_urlsafe(32),
            "permissions": permissions,
            "security_level": security_level.value,
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        }

        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def log_security_event(
        self, event_type: str, context: SecurityContext, details: Dict[str, Any]
    ):
        """
        Log security event for audit.

        Args:
            event_type: Type of security event
            context: Security context
            details: Event details
        """
        log_entry = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": context.user_id,
            "session_id": context.session_id,
            "ip_address": context.ip_address,
            "user_agent": context.user_agent,
            "security_level": context.security_level.value,
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "details": details,
        }

        logger.info(f"Security event: {event_type}", extra=log_entry)


# Global security policy instance
_security_policy = None


def get_security_policy(jwt_secret: str = None) -> SecurityPolicy:
    """Get global security policy instance."""
    global _security_policy
    if _security_policy is None:
        if jwt_secret is None:
            raise ValueError("JWT secret required for security policy initialization")
        _security_policy = SecurityPolicy(jwt_secret)
    return _security_policy


# Convenience functions
def validate_input(input_data: Any, context: SecurityContext) -> bool:
    """Validate input data."""
    policy = get_security_policy()
    return policy.validate_input(input_data, context)


def authenticate_user(token: str) -> Optional[SecurityContext]:
    """Authenticate user."""
    policy = get_security_policy()
    return policy.authenticate_user(token)


def authorize_operation(
    context: SecurityContext, operation: str, resource: str
) -> bool:
    """Authorize operation."""
    policy = get_security_policy()
    return policy.authorize_operation(context, operation, resource)


def check_rate_limit(identifier: str, limit: int = 100, window: int = 60) -> bool:
    """Check rate limit."""
    policy = get_security_policy()
    return policy.check_rate_limit(identifier, limit, window)


def detect_threat(
    context: SecurityContext, request_data: Dict[str, Any]
) -> ThreatLevel:
    """Detect threats."""
    policy = get_security_policy()
    return policy.detect_threat(context, request_data)


def log_security_event(
    event_type: str, context: SecurityContext, details: Dict[str, Any]
):
    """Log security event."""
    policy = get_security_policy()
    policy.log_security_event(event_type, context, details)
