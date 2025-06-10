# Enterprise Security Event Model
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base


class SecurityEvent(Base):
    """Security audit event model for enterprise logging"""

    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)
    severity = Column(
        String(20), nullable=False, index=True
    )  # info, warning, error, critical
    description = Column(Text, nullable=False)

    # Request context
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    request_id = Column(String(100), nullable=True, index=True)

    # Event outcome
    success = Column(Boolean, nullable=False, default=True, index=True)
    error_message = Column(Text, nullable=True)

    # Additional metadata (renamed to avoid SQLAlchemy reserved word)
    event_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("User", back_populates="security_events")


class ApiKey(Base):
    """API Key model for enterprise API access management"""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Key details
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    prefix = Column(
        String(20), nullable=False, index=True
    )  # First few chars for identification

    # Permissions and limits
    scopes = Column(JSON, nullable=False, default=list)  # List of allowed scopes
    rate_limit_per_minute = Column(Integer, nullable=False, default=1000)
    allowed_ips = Column(JSON, nullable=True)  # List of allowed IP addresses

    # Status and usage
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    usage_count = Column(Integer, nullable=False, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class OAuthAccount(Base):
    """OAuth account linking model"""

    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # OAuth provider details
    provider = Column(String(50), nullable=False, index=True)  # github, google, etc.
    provider_user_id = Column(String(255), nullable=False, index=True)
    provider_username = Column(String(255), nullable=True)
    provider_email = Column(String(255), nullable=True)

    # OAuth tokens (encrypted in production)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Account metadata
    provider_data = Column(JSON, nullable=True)  # Additional provider-specific data

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="oauth_accounts")


class UserSession(Base):
    """User session model for enterprise session management"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Session details
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    refresh_token_jti = Column(String(255), nullable=False, unique=True, index=True)

    # Session context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)

    # Session status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_activity_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
