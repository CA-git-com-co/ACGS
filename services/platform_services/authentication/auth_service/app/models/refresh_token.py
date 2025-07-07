from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import Base

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class RefreshToken(Base):
    """Refresh token model for JWT token management"""

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Token details
    token = Column(
        String(1024), unique=True, index=True, nullable=False
    )  # Store the refresh token string (or its hash)
    jti = Column(
        String(255), unique=True, index=True, nullable=False
    )  # JTI of the refresh token itself

    # Token lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    revoked = Column(Boolean, default=False, nullable=False, index=True)
    is_revoked = Column(
        Boolean, default=False, nullable=False, index=True
    )  # Alias for compatibility

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, jti='{self.jti}', revoked={self.revoked})>"
