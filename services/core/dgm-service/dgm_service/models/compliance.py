"""
Constitutional compliance model for DGM service.
"""

import enum
from typing import Any

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ComplianceLevel(enum.Enum):
    """Level of constitutional compliance."""

    CRITICAL_VIOLATION = "critical_violation"
    MAJOR_VIOLATION = "major_violation"
    MINOR_VIOLATION = "minor_violation"
    WARNING = "warning"
    COMPLIANT = "compliant"
    EXEMPLARY = "exemplary"


class ComplianceStatus(enum.Enum):
    """Status of compliance check."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class ConstitutionalComplianceLog(Base):
    """Constitutional compliance logging and validation."""

    __tablename__ = "constitutional_compliance_logs"
    __table_args__ = {"schema": "dgm"}

    id = Column(
        PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )

    # Reference information
    improvement_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    service_name = Column(String(255), nullable=False, index=True)
    operation_type = Column(String(100), nullable=False, index=True)

    # Compliance assessment
    compliance_level = Column(Enum(ComplianceLevel), nullable=False, index=True)
    compliance_score = Column(Numeric(3, 2), nullable=False)
    status = Column(
        Enum(ComplianceStatus), nullable=False, default=ComplianceStatus.PENDING
    )

    # Constitutional reference
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    constitutional_version = Column(String(50), nullable=False, default="1.0")

    # Compliance details
    violations = Column(JSON, default=list)  # List of violations found
    recommendations = Column(JSON, default=list)  # Remediation recommendations
    evidence = Column(JSON, default=dict)  # Supporting evidence

    # Assessment metadata
    assessment_method = Column(String(100), nullable=False)  # manual, automated, hybrid
    assessor_id = Column(String(255), nullable=True)  # Who performed assessment
    review_required = Column(Boolean, default=False)

    # Timestamps
    assessed_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
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
            f"<ConstitutionalComplianceLog(service={self.service_name}, "
            f"level={self.compliance_level}, score={self.compliance_score})>"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "improvement_id": str(self.improvement_id) if self.improvement_id else None,
            "service_name": self.service_name,
            "operation_type": self.operation_type,
            "compliance_level": (
                self.compliance_level.value if self.compliance_level else None
            ),
            "compliance_score": float(self.compliance_score),
            "status": self.status.value if self.status else None,
            "constitutional_hash": self.constitutional_hash,
            "constitutional_version": self.constitutional_version,
            "violations": self.violations,
            "recommendations": self.recommendations,
            "evidence": self.evidence,
            "assessment_method": self.assessment_method,
            "assessor_id": self.assessor_id,
            "review_required": self.review_required,
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
