# Enterprise Intrusion Detection System
import ipaddress
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from .security_audit import security_audit


@dataclass
class SecurityThreat:
    """Security threat detection result"""

    threat_type: str
    severity: str  # low, medium, high, critical
    description: str
    ip_address: str
    user_id: Optional[int] = None
    metadata: Dict = None
    detected_at: datetime = None

    def __post_init__(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        if self.detected_at is None:
            self.detected_at = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}


class IntrusionDetectionSystem:
    """Enterprise Intrusion Detection and Prevention System"""

    def __init__(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        # Rate limiting tracking
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        self.failed_login_attempts: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: Dict[str, datetime] = {}

        # Suspicious patterns tracking
        self.user_agent_patterns: Dict[str, int] = defaultdict(int)
        self.endpoint_access_patterns: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        # Configuration
        self.max_requests_per_minute = 100
        self.max_failed_logins_per_hour = 5
        self.block_duration_minutes = 60
        self.suspicious_user_agents = {
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "zap",
            "burp",
            "dirb",
            "gobuster",
        }

        # Known malicious IP ranges (example - in production, use threat intelligence feeds)
        self.malicious_ip_ranges = [
            "10.0.0.0/8",  # Private networks (adjust based on your setup)
            "192.168.0.0/16",  # Private networks
            "172.16.0.0/12",  # Private networks
        ]

        # Honeypot endpoints (fake endpoints to detect scanners)
        self.honeypot_endpoints = {
            "/admin",
            "/wp-admin",
            "/phpmyadmin",
            "/.env",
            "/config.php",
            "/backup",
            "/test",
            "/debug",
            "/api/admin",
            "/management",
        }

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        if hasattr(request.client, "host"):
            return request.client.host

        return "unknown"

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is currently blocked"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            if datetime.now(timezone.utc) - block_time < timedelta(
                minutes=self.block_duration_minutes
            ):
                return True
            else:
                # Block expired, remove it
                del self.blocked_ips[ip_address]
        return False

    def block_ip(self, ip_address: str, duration_minutes: int = None):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Block IP address for specified duration"""
        if duration_minutes is None:
            duration_minutes = self.block_duration_minutes

        self.blocked_ips[ip_address] = datetime.now(timezone.utc)

    def is_malicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is in known malicious ranges"""
        try:
            ip = ipaddress.ip_address(ip_address)
            for range_str in self.malicious_ip_ranges:
                network = ipaddress.ip_network(range_str, strict=False)
                if ip in network:
                    return True
        except ValueError:
            # Invalid IP address
            return True
        return False

    def detect_rate_limiting_violation(
        self, ip_address: str
    ) -> Optional[SecurityThreat]:
        """Detect rate limiting violations"""
        current_time = time.time()
        minute_ago = current_time - 60

        # Clean old entries
        while (
            self.request_counts[ip_address]
            and self.request_counts[ip_address][0] < minute_ago
        ):
            self.request_counts[ip_address].popleft()

        # Add current request
        self.request_counts[ip_address].append(current_time)

        # Check if rate limit exceeded
        if len(self.request_counts[ip_address]) > self.max_requests_per_minute:
            return SecurityThreat(
                threat_type="rate_limit_violation",
                severity="medium",
                description=f"Rate limit exceeded: {len(self.request_counts[ip_address])} requests in 1 minute",
                ip_address=ip_address,
                metadata={"requests_per_minute": len(self.request_counts[ip_address])},
            )

        return None

    def detect_brute_force_attack(
        self, ip_address: str, user_id: int = None
    ) -> Optional[SecurityThreat]:
        """Detect brute force login attempts"""
        current_time = time.time()
        hour_ago = current_time - 3600

        # Clean old entries
        while (
            self.failed_login_attempts[ip_address]
            and self.failed_login_attempts[ip_address][0] < hour_ago
        ):
            self.failed_login_attempts[ip_address].popleft()

        # Add current failed attempt
        self.failed_login_attempts[ip_address].append(current_time)

        # Check if brute force threshold exceeded
        if (
            len(self.failed_login_attempts[ip_address])
            > self.max_failed_logins_per_hour
        ):
            return SecurityThreat(
                threat_type="brute_force_attack",
                severity="high",
                description=f"Brute force attack detected: {len(self.failed_login_attempts[ip_address])} failed logins in 1 hour",
                ip_address=ip_address,
                user_id=user_id,
                metadata={
                    "failed_attempts": len(self.failed_login_attempts[ip_address])
                },
            )

        return None

    def detect_suspicious_user_agent(
        self, request: Request
    ) -> Optional[SecurityThreat]:
        """Detect suspicious user agents"""
        user_agent = request.headers.get("user-agent", "").lower()
        ip_address = self.get_client_ip(request)

        for suspicious_pattern in self.suspicious_user_agents:
            if suspicious_pattern in user_agent:
                return SecurityThreat(
                    threat_type="suspicious_user_agent",
                    severity="medium",
                    description=f"Suspicious user agent detected: {suspicious_pattern}",
                    ip_address=ip_address,
                    metadata={"user_agent": user_agent, "pattern": suspicious_pattern},
                )

        # Detect empty or very short user agents
        if not user_agent or len(user_agent) < 10:
            return SecurityThreat(
                threat_type="suspicious_user_agent",
                severity="low",
                description="Empty or very short user agent",
                ip_address=ip_address,
                metadata={"user_agent": user_agent},
            )

        return None

    def detect_honeypot_access(self, request: Request) -> Optional[SecurityThreat]:
        """Detect access to honeypot endpoints"""
        path = request.url.path.lower()
        ip_address = self.get_client_ip(request)

        for honeypot in self.honeypot_endpoints:
            if path.startswith(honeypot.lower()):
                return SecurityThreat(
                    threat_type="honeypot_access",
                    severity="high",
                    description=f"Access to honeypot endpoint: {path}",
                    ip_address=ip_address,
                    metadata={"endpoint": path, "honeypot": honeypot},
                )

        return None

    def detect_sql_injection_attempt(
        self, request: Request
    ) -> Optional[SecurityThreat]:
        """Detect potential SQL injection attempts"""
        ip_address = self.get_client_ip(request)

        # Check query parameters and path for SQL injection patterns
        sql_patterns = [
            "union select",
            "drop table",
            "insert into",
            "delete from",
            "update set",
            "exec(",
            "execute(",
            "sp_",
            "xp_",
            "' or '1'='1",
            "' or 1=1",
            "'; drop",
            "'; delete",
            "'; insert",
            "'; update",
        ]

        # Check URL path and query string
        full_url = str(request.url).lower()

        for pattern in sql_patterns:
            if pattern in full_url:
                return SecurityThreat(
                    threat_type="sql_injection_attempt",
                    severity="critical",
                    description=f"SQL injection attempt detected: {pattern}",
                    ip_address=ip_address,
                    metadata={"url": str(request.url), "pattern": pattern},
                )

        return None

    def detect_xss_attempt(self, request: Request) -> Optional[SecurityThreat]:
        """Detect potential XSS attempts"""
        ip_address = self.get_client_ip(request)

        xss_patterns = [
            "<script",
            "javascript:",
            "onload=",
            "onerror=",
            "onclick=",
            "onmouseover=",
            "alert(",
            "document.cookie",
            "eval(",
            "fromcharcode",
            "string.fromcharcode",
        ]

        full_url = str(request.url).lower()

        for pattern in xss_patterns:
            if pattern in full_url:
                return SecurityThreat(
                    threat_type="xss_attempt",
                    severity="high",
                    description=f"XSS attempt detected: {pattern}",
                    ip_address=ip_address,
                    metadata={"url": str(request.url), "pattern": pattern},
                )

        return None

    async def analyze_request(
        self, request: Request, db: AsyncSession, user_id: int = None
    ) -> List[SecurityThreat]:
        """Comprehensive request analysis for security threats"""
        threats = []
        ip_address = self.get_client_ip(request)

        # Check if IP is already blocked
        if self.is_ip_blocked(ip_address):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="IP address is temporarily blocked due to suspicious activity",
            )

        # Check if IP is in malicious ranges
        if self.is_malicious_ip(ip_address):
            threat = SecurityThreat(
                threat_type="malicious_ip",
                severity="high",
                description="Request from known malicious IP range",
                ip_address=ip_address,
                user_id=user_id,
            )
            threats.append(threat)

        # Rate limiting detection
        rate_threat = self.detect_rate_limiting_violation(ip_address)
        if rate_threat:
            threats.append(rate_threat)

        # Suspicious user agent detection
        ua_threat = self.detect_suspicious_user_agent(request)
        if ua_threat:
            threats.append(ua_threat)

        # Honeypot access detection
        honeypot_threat = self.detect_honeypot_access(request)
        if honeypot_threat:
            threats.append(honeypot_threat)

        # SQL injection detection
        sql_threat = self.detect_sql_injection_attempt(request)
        if sql_threat:
            threats.append(sql_threat)

        # XSS detection
        xss_threat = self.detect_xss_attempt(request)
        if xss_threat:
            threats.append(xss_threat)

        # Log all detected threats
        for threat in threats:
            await security_audit.log_event(
                db=db,
                event_type="intrusion_detected",
                user_id=user_id,
                request=request,
                success=False,
                error_message=threat.description,
                metadata=threat.metadata,
                severity=threat.severity,
            )

            # Block IP for critical or high severity threats
            if threat.severity in ["critical", "high"]:
                self.block_ip(ip_address)

        return threats

    async def record_failed_login(
        self, ip_address: str, user_id: int = None, db: AsyncSession = None
    ) -> Optional[SecurityThreat]:
        """Record failed login attempt and check for brute force"""
        threat = self.detect_brute_force_attack(ip_address, user_id)

        if threat and db:
            await security_audit.log_event(
                db=db,
                event_type="brute_force_attempt",
                user_id=user_id,
                success=False,
                error_message=threat.description,
                metadata=threat.metadata,
                severity=threat.severity,
            )

            # Block IP for brute force attacks
            self.block_ip(ip_address)

        return threat


# Global intrusion detection system instance
ids = IntrusionDetectionSystem()
