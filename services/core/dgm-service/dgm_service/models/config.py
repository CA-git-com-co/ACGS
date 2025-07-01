"""
System configuration model for DGM service.
"""

from typing import Any, Dict

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class SystemConfiguration(Base):
    """System configuration settings for DGM service."""

    __tablename__ = "system_configurations"
    __table_args__ = {"schema": "dgm"}

    id = Column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )

    # Configuration key-value
    key = Column(String(255), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(50), nullable=False, default="string")

    # Metadata
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    is_sensitive = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self):
        return f"<SystemConfiguration(key={self.key}, category={self.category})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "key": self.key,
            "value": self.value if not self.is_sensitive else "***REDACTED***",
            "value_type": self.value_type,
            "description": self.description,
            "category": self.category,
            "is_sensitive": self.is_sensitive,
            "is_readonly": self.is_readonly,
            "constitutional_hash": self.constitutional_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
