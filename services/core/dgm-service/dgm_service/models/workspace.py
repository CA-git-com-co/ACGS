"""
Improvement workspace model for DGM service.
"""

import enum
from typing import Any, Dict

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class WorkspaceStatus(enum.Enum):
    """Status of improvement workspace."""

    CREATED = "created"
    ACTIVE = "active"
    TESTING = "testing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ImprovementWorkspace(Base):
    """Workspace for developing and testing improvements."""

    __tablename__ = "improvement_workspaces"
    __table_args__ = {"schema": "dgm"}

    id = Column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    improvement_id = Column(PG_UUID(as_uuid=True), nullable=False, unique=True)

    # Workspace metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(WorkspaceStatus), nullable=False, default=WorkspaceStatus.CREATED
    )

    # Workspace content
    source_code = Column(JSON, default=dict)  # Code changes
    configuration = Column(JSON, default=dict)  # Config changes
    test_results = Column(JSON, default=list)  # Test outcomes
    validation_results = Column(JSON, default=dict)  # Validation data

    # Environment information
    environment_snapshot = Column(JSON, default=dict)  # Pre-change state
    dependencies = Column(JSON, default=list)  # Required dependencies

    # Safety and rollback
    rollback_plan = Column(JSON, default=dict)  # How to undo changes
    safety_checks = Column(JSON, default=list)  # Safety validations
    risk_assessment = Column(JSON, default=dict)  # Risk analysis

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    compliance_validated = Column(Boolean, default=False)

    # Ownership and tracking
    created_by = Column(String(255), nullable=True)
    assigned_to = Column(String(255), nullable=True)

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
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return (
            f"<ImprovementWorkspace(id={self.improvement_id}, "
            f"name={self.name}, status={self.status})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "improvement_id": str(self.improvement_id),
            "name": self.name,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "source_code": self.source_code,
            "configuration": self.configuration,
            "test_results": self.test_results,
            "validation_results": self.validation_results,
            "environment_snapshot": self.environment_snapshot,
            "dependencies": self.dependencies,
            "rollback_plan": self.rollback_plan,
            "safety_checks": self.safety_checks,
            "risk_assessment": self.risk_assessment,
            "constitutional_hash": self.constitutional_hash,
            "compliance_validated": self.compliance_validated,
            "created_by": self.created_by,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }
