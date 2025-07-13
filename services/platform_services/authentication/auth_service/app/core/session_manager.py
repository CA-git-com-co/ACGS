# Enterprise Session Management
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.crud import crud_user
from app.models import User, UserSession
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class SessionManager:
    """Enterprise Session Management Service"""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.default_session_timeout = 480  # 8 hours in minutes
        self.max_concurrent_sessions = 5
        self.session_cleanup_interval = 3600  # 1 hour in seconds

    def generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)

    def generate_device_fingerprint(self, request: Request) -> str:
        """Generate device fingerprint from request headers"""
        fingerprint_data = {
            "user_agent": request.headers.get("user-agent", ""),
            "accept_language": request.headers.get("accept-language", ""),
            "accept_encoding": request.headers.get("accept-encoding", ""),
            "accept": request.headers.get("accept", ""),
        }

        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]

    def calculate_risk_score(
        self, request: Request, user: User, existing_sessions: list[UserSession]
    ) -> int:
        """Calculate session risk score (0-100)"""
        risk_score = 0

        # Check for new IP address
        current_ip = self.get_client_ip(request)
        known_ips = {session.ip_address for session in existing_sessions}
        if current_ip not in known_ips and user.last_login_ip != current_ip:
            risk_score += 30

        # Check for new device fingerprint
        current_fingerprint = self.generate_device_fingerprint(request)
        known_fingerprints = {
            session.device_fingerprint for session in existing_sessions
        }
        if current_fingerprint not in known_fingerprints:
            risk_score += 20

        # Check time since last login
        if user.last_login_at:
            time_since_last = datetime.now(timezone.utc) - user.last_login_at
            if time_since_last > timedelta(days=30):
                risk_score += 25
            elif time_since_last > timedelta(days=7):
                risk_score += 15

        # Check failed login attempts
        if user.failed_login_attempts > 0:
            risk_score += min(user.failed_login_attempts * 10, 25)

        return min(risk_score, 100)

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (reverse proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        if hasattr(request.client, "host"):
            return request.client.host

        return "unknown"

    async def create_session(
        self, db: AsyncSession, user: User, request: Request
    ) -> UserSession:
        """Create new user session"""
        # Check concurrent session limit
        active_sessions = await self.get_active_sessions(db, user.id)

        if len(active_sessions) >= user.max_concurrent_sessions:
            # Remove oldest session
            oldest_session = min(active_sessions, key=lambda s: s.last_activity_at)
            await self.terminate_session(db, oldest_session.session_id)

        # Calculate session expiration
        timeout_minutes = user.session_timeout_minutes or self.default_session_timeout
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=timeout_minutes)

        # Create session
        session = UserSession(
            user_id=user.id,
            session_id=self.generate_session_id(),
            ip_address=self.get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            device_fingerprint=self.generate_device_fingerprint(request),
            expires_at=expires_at,
            risk_score=self.calculate_risk_score(request, user, active_sessions),
            mfa_verified=False,  # Will be set to True after MFA verification
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return session

    async def get_session(
        self, db: AsyncSession, session_id: str
    ) -> UserSession | None:
        """Get session by ID"""
        result = await db.execute(
            select(UserSession).where(
                UserSession.session_id == session_id, UserSession.is_active
            )
        )
        return result.scalar_one_or_none()

    async def get_active_sessions(
        self, db: AsyncSession, user_id: int
    ) -> list[UserSession]:
        """Get all active sessions for a user"""
        result = await db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active,
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalars().all()

    async def update_session_activity(self, db: AsyncSession, session_id: str) -> bool:
        """Update session last activity timestamp"""
        session = await self.get_session(db, session_id)
        if not session:
            return False

        # Check if session is expired
        if session.expires_at <= datetime.now(timezone.utc):
            await self.terminate_session(db, session_id)
            return False

        session.last_activity_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    async def verify_mfa_for_session(self, db: AsyncSession, session_id: str) -> bool:
        """Mark session as MFA verified"""
        session = await self.get_session(db, session_id)
        if not session:
            return False

        session.mfa_verified = True
        await db.commit()
        return True

    async def terminate_session(self, db: AsyncSession, session_id: str) -> bool:
        """Terminate a specific session"""
        session = await self.get_session(db, session_id)
        if not session:
            return False

        session.is_active = False
        await db.commit()
        return True

    async def terminate_all_sessions(
        self, db: AsyncSession, user_id: int, exclude_session_id: str | None = None
    ) -> int:
        """Terminate all sessions for a user (except optionally one)"""
        query = select(UserSession).where(
            UserSession.user_id == user_id, UserSession.is_active
        )

        if exclude_session_id:
            query = query.where(UserSession.session_id != exclude_session_id)

        result = await db.execute(query)
        sessions = result.scalars().all()

        for session in sessions:
            session.is_active = False

        await db.commit()
        return len(sessions)

    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """Clean up expired sessions"""
        current_time = datetime.now(timezone.utc)

        result = await db.execute(
            select(UserSession).where(
                UserSession.expires_at <= current_time, UserSession.is_active
            )
        )
        expired_sessions = result.scalars().all()

        for session in expired_sessions:
            session.is_active = False

        await db.commit()
        return len(expired_sessions)

    async def get_session_info(
        self, db: AsyncSession, session_id: str
    ) -> dict[str, Any] | None:
        """Get detailed session information"""
        session = await self.get_session(db, session_id)
        if not session:
            return None

        user = await crud_user.get_user(db, user_id=session.user_id)
        if not user:
            return None

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "username": user.username,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "device_fingerprint": session.device_fingerprint,
            "created_at": session.created_at,
            "last_activity_at": session.last_activity_at,
            "expires_at": session.expires_at,
            "mfa_verified": session.mfa_verified,
            "risk_score": session.risk_score,
            "is_active": session.is_active,
        }

    async def validate_session(
        self, db: AsyncSession, session_id: str, request: Request
    ) -> UserSession | None:
        """Validate session and update activity"""
        session = await self.get_session(db, session_id)
        if not session:
            return None

        # Check expiration
        if session.expires_at <= datetime.now(timezone.utc):
            await self.terminate_session(db, session_id)
            return None

        # Update activity
        await self.update_session_activity(db, session_id)

        # Optional: Verify IP consistency for high-risk sessions
        if session.risk_score > 70:
            current_ip = self.get_client_ip(request)
            if current_ip != session.ip_address:
                # IP changed for high-risk session - require re-authentication
                await self.terminate_session(db, session_id)
                return None

        return session


# Global session manager instance
session_manager = SessionManager()
