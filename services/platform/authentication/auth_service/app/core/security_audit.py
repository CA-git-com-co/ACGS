# Enterprise Security Audit Logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import Request
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SecurityEvent


class SecurityAuditLogger:
    """Enterprise Security Audit Logging Service"""

    # Event Types
    EVENT_TYPES = {
        # Authentication Events
        "login_success": "Successful user login",
        "login_failure": "Failed login attempt",
        "logout": "User logout",
        "token_refresh": "Access token refreshed",
        "token_revoked": "Token revoked",
        # MFA Events
        "mfa_setup": "MFA setup initiated",
        "mfa_enabled": "MFA enabled for user",
        "mfa_disabled": "MFA disabled for user",
        "mfa_verification_success": "MFA verification successful",
        "mfa_verification_failure": "MFA verification failed",
        "backup_codes_used": "MFA backup code used",
        "backup_codes_regenerated": "MFA backup codes regenerated",
        # Account Events
        "account_created": "User account created",
        "account_locked": "User account locked",
        "account_unlocked": "User account unlocked",
        "password_changed": "Password changed",
        "password_reset_requested": "Password reset requested",
        "password_reset_completed": "Password reset completed",
        "profile_updated": "User profile updated",
        # Session Events
        "session_created": "User session created",
        "session_terminated": "User session terminated",
        "concurrent_session_limit": "Concurrent session limit reached",
        "session_expired": "User session expired",
        # Authorization Events
        "permission_granted": "Permission granted",
        "permission_denied": "Permission denied",
        "role_changed": "User role changed",
        "privilege_escalation": "Privilege escalation attempt",
        # API Key Events
        "api_key_created": "API key created",
        "api_key_used": "API key used",
        "api_key_revoked": "API key revoked",
        "api_key_expired": "API key expired",
        # Security Events
        "suspicious_activity": "Suspicious activity detected",
        "brute_force_attempt": "Brute force attack detected",
        "ip_blocked": "IP address blocked",
        "rate_limit_exceeded": "Rate limit exceeded",
        "intrusion_detected": "Intrusion attempt detected",
        # OAuth Events
        "oauth_login_success": "OAuth login successful",
        "oauth_login_failure": "OAuth login failed",
        "oauth_account_linked": "OAuth account linked",
        "oauth_account_unlinked": "OAuth account unlinked",
    }

    # Event Categories
    CATEGORIES = {
        "authentication": "Authentication and login events",
        "authorization": "Authorization and permission events",
        "security": "Security-related events",
        "audit": "Audit and compliance events",
        "session": "Session management events",
        "account": "Account management events",
        "api": "API access events",
        "oauth": "OAuth and SSO events",
    }

    # Severity Levels
    SEVERITY_LEVELS = ["info", "warning", "error", "critical"]

    def __init__(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        self.request_id_header = "X-Request-ID"

    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())

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

    async def log_event(
        self,
        db: AsyncSession,
        event_type: str,
        user_id: Optional[int] = None,
        request: Optional[Request] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        severity: str = "info",
    ) -> SecurityEvent:
        """Log a security event"""

        # Validate inputs
        if event_type not in self.EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event_type}")

        if severity not in self.SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity level: {severity}")

        # Determine category from event type
        category = self._get_event_category(event_type)

        # Extract request information
        ip_address = None
        user_agent = None
        endpoint = None
        request_id = None

        if request:
            ip_address = self.get_client_ip(request)
            user_agent = request.headers.get("user-agent")
            endpoint = f"{request.method} {request.url.path}"
            request_id = (
                request.headers.get(self.request_id_header)
                or self.generate_request_id()
            )

        # Create security event
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            event_category=category,
            severity=severity,
            description=self.EVENT_TYPES[event_type],
            event_metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            request_id=request_id,
            success=success,
            error_message=error_message,
        )

        db.add(event)
        await db.commit()
        await db.refresh(event)

        return event

    def _get_event_category(self, event_type: str) -> str:
        """Determine event category from event type"""
        category_mapping = {
            "login_success": "authentication",
            "login_failure": "authentication",
            "logout": "authentication",
            "token_refresh": "authentication",
            "token_revoked": "authentication",
            "mfa_setup": "security",
            "mfa_enabled": "security",
            "mfa_disabled": "security",
            "mfa_verification_success": "security",
            "mfa_verification_failure": "security",
            "backup_codes_used": "security",
            "backup_codes_regenerated": "security",
            "account_created": "account",
            "account_locked": "security",
            "account_unlocked": "security",
            "password_changed": "account",
            "password_reset_requested": "account",
            "password_reset_completed": "account",
            "profile_updated": "account",
            "session_created": "session",
            "session_terminated": "session",
            "concurrent_session_limit": "session",
            "session_expired": "session",
            "permission_granted": "authorization",
            "permission_denied": "authorization",
            "role_changed": "authorization",
            "privilege_escalation": "security",
            "api_key_created": "api",
            "api_key_used": "api",
            "api_key_revoked": "api",
            "api_key_expired": "api",
            "suspicious_activity": "security",
            "brute_force_attempt": "security",
            "ip_blocked": "security",
            "rate_limit_exceeded": "security",
            "intrusion_detected": "security",
            "oauth_login_success": "oauth",
            "oauth_login_failure": "oauth",
            "oauth_account_linked": "oauth",
            "oauth_account_unlinked": "oauth",
        }

        return category_mapping.get(event_type, "audit")

    async def get_events(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        event_type: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        success: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SecurityEvent]:
        """Query security events with filters"""

        query = select(SecurityEvent)

        # Apply filters
        conditions = []

        if user_id is not None:
            conditions.append(SecurityEvent.user_id == user_id)

        if event_type:
            conditions.append(SecurityEvent.event_type == event_type)

        if category:
            conditions.append(SecurityEvent.event_category == category)

        if severity:
            conditions.append(SecurityEvent.severity == severity)

        if success is not None:
            conditions.append(SecurityEvent.success == success)

        if start_date:
            conditions.append(SecurityEvent.created_at >= start_date)

        if end_date:
            conditions.append(SecurityEvent.created_at <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        # Order by creation time (newest first)
        query = query.order_by(desc(SecurityEvent.created_at))

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_security_summary(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get security event summary statistics"""

        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=7)

        if not end_date:
            end_date = datetime.now(timezone.utc)

        # Get all events in date range
        events = await self.get_events(
            db, start_date=start_date, end_date=end_date, limit=10000
        )

        # Calculate statistics
        total_events = len(events)
        successful_events = sum(1 for event in events if event.success)
        failed_events = total_events - successful_events

        # Group by category
        category_counts = {}
        for event in events:
            category_counts[event.event_category] = (
                category_counts.get(event.event_category, 0) + 1
            )

        # Group by severity
        severity_counts = {}
        for event in events:
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1

        # Group by event type
        event_type_counts = {}
        for event in events:
            event_type_counts[event.event_type] = (
                event_type_counts.get(event.event_type, 0) + 1
            )

        # Get top IP addresses
        ip_counts = {}
        for event in events:
            if event.ip_address:
                ip_counts[event.ip_address] = ip_counts.get(event.ip_address, 0) + 1

        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "summary": {
                "total_events": total_events,
                "successful_events": successful_events,
                "failed_events": failed_events,
                "success_rate": (
                    successful_events / total_events if total_events > 0 else 0
                ),
            },
            "by_category": category_counts,
            "by_severity": severity_counts,
            "by_event_type": event_type_counts,
            "top_ip_addresses": top_ips,
        }


# Global security audit logger instance
security_audit = SecurityAuditLogger()
