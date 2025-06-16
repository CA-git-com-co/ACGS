from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from services.shared.database import Base  # Assuming shared/database.py provides Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Enterprise MFA Features
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String, nullable=True)  # TOTP secret
    backup_codes = Column(JSON, nullable=True)  # List of backup codes

    # Enterprise Session Management
    max_concurrent_sessions = Column(Integer, default=5, nullable=False)
    session_timeout_minutes = Column(Integer, default=480, nullable=False)  # 8 hours default

    # Enterprise Security Features
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String, nullable=True)

    # Enterprise Permissions (JSON field for fine-grained permissions)
    permissions = Column(JSON, default=list, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    security_events = relationship(
        "SecurityEvent", back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(
        String, unique=True, index=True, nullable=False
    )  # Store the refresh token string (or its hash)
    jti = Column(String, unique=True, index=True, nullable=False)  # JTI of the refresh token itself
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")


class ApiKey(Base):
    """Enterprise API Key Management for Service-to-Service Authentication"""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)  # Human-readable name for the API key
    key_hash = Column(String, unique=True, index=True, nullable=False)  # Hashed API key
    key_prefix = Column(String, index=True, nullable=False)  # First 8 chars for identification

    # Enterprise API Key Features
    scopes = Column(JSON, default=list, nullable=False)  # List of allowed scopes/permissions
    rate_limit_per_minute = Column(Integer, default=1000, nullable=False)
    allowed_ips = Column(JSON, default=list, nullable=True)  # IP whitelist (empty = all IPs)

    # Lifecycle Management
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="api_keys")


class UserSession(Base):
    """Enterprise Session Management"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, index=True, nullable=False)

    # Session Details
    ip_address = Column(String, nullable=False)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String, nullable=True)

    # Session State
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Security Features
    mfa_verified = Column(Boolean, default=False, nullable=False)
    risk_score = Column(Integer, default=0, nullable=False)  # 0-100 risk assessment

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="user_sessions")


class SecurityEvent(Base):
    """Comprehensive Security Audit Logging"""

    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # Nullable for anonymous events

    # Event Classification
    event_type = Column(String, nullable=False)  # login, logout, mfa_setup, password_change, etc.
    event_category = Column(
        String, nullable=False
    )  # authentication, authorization, security, audit
    severity = Column(String, default="info", nullable=False)  # info, warning, error, critical

    # Event Details
    description = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict, nullable=False)  # Additional event-specific data

    # Request Context
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String, nullable=True)
    request_id = Column(String, nullable=True)

    # Outcome
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="security_events")
