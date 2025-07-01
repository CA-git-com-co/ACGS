"""
Archive model for DGM improvements.
"""

import enum
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Enum, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ImprovementStatus(enum.Enum):
    """Status of an improvement."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DGMArchive(Base):
    """Archive table for DGM improvements."""

    __tablename__ = "dgm_archive"
    __table_args__ = {"schema": "dgm"}

    id = Column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    improvement_id = Column(PG_UUID(as_uuid=True), nullable=False, unique=True)
    timestamp = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    description = Column(Text, nullable=False)
    algorithm_changes = Column(JSON)
    performance_before = Column(JSON)
    performance_after = Column(JSON)
    constitutional_compliance_score = Column(Numeric(3, 2), nullable=False)
    compliance_details = Column(JSON)
    status = Column(
        Enum(ImprovementStatus), nullable=False, default=ImprovementStatus.PENDING
    )
    rollback_data = Column(JSON)
    metadata = Column(JSON)
    created_by = Column(String(255))
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
        return (
            f"<DGMArchive(improvement_id={self.improvement_id}, status={self.status})>"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "improvement_id": str(self.improvement_id),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "description": self.description,
            "algorithm_changes": self.algorithm_changes,
            "performance_before": self.performance_before,
            "performance_after": self.performance_after,
            "constitutional_compliance_score": float(
                self.constitutional_compliance_score
            ),
            "compliance_details": self.compliance_details,
            "status": self.status.value if self.status else None,
            "rollback_data": self.rollback_data,
            "metadata": self.metadata,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
