"""
ACGS FastAPI Service Database Models Template
Constitutional Hash: cdd01ef066bc6cf2

This module provides standardized SQLAlchemy models for ACGS services including:
- Constitutional compliance integration
- Multi-tenant support with RLS
- Audit trail functionality
- Standardized model patterns
- Database optimization patterns
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_mixin

# Try to import services.shared components
try:
    from services.shared.database import Base
    from services.shared.database.simplified_rls import SimpleTenantMixin

    SHARED_COMPONENTS_AVAILABLE = True
except ImportError:
    # Fallback for standalone services
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()
    SHARED_COMPONENTS_AVAILABLE = False

    @declarative_mixin
    class SimpleTenantMixin:
        """Fallback tenant mixin for standalone services."""

        @declared_attr
        def tenant_id(self):
            return Column(UUID(as_uuid=True), nullable=False, index=True)


# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@declarative_mixin
class ConstitutionalMixin:
    """
    Mixin for constitutional compliance tracking.

    This mixin adds constitutional compliance fields to any model,
    ensuring that all data operations maintain governance standards.
    """

    @declared_attr
    def constitutional_hash(self):
        return Column(
            String(64),
            nullable=False,
            default=CONSTITUTIONAL_HASH,
            index=True,
            comment="Constitutional compliance hash for ACGS governance",
        )

    @declared_attr
    def constitutional_compliance_score(self):
        return Column(
            Integer, nullable=True, comment="Constitutional compliance score (0-100)"
        )


@declarative_mixin
class AuditMixin:
    """
    Mixin for audit trail functionality.

    This mixin adds standard audit fields to track when records
    are created, updated, and by whom.
    """

    @declared_attr
    def created_at(self):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            comment="Record creation timestamp",
        )

    @declared_attr
    def updated_at(self):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            comment="Record last update timestamp",
        )

    @declared_attr
    def created_by_user_id(self):
        return Column(
            Integer, nullable=True, comment="ID of user who created this record"
        )

    @declared_attr
    def updated_by_user_id(self):
        return Column(
            Integer, nullable=True, comment="ID of user who last updated this record"
        )


@declarative_mixin
class StatusMixin:
    """
    Mixin for status tracking.

    This mixin adds standard status fields that are common
    across many entity types in ACGS services.
    """

    @declared_attr
    def status(self):
        return Column(
            String(50),
            nullable=False,
            default="active",
            index=True,
            comment="Entity status (active, inactive, deleted, etc.)",
        )

    @declared_attr
    def is_active(self):
        return Column(
            Boolean,
            nullable=False,
            default=True,
            index=True,
            comment="Whether the entity is currently active",
        )


class BaseACGSModel(
    Base, SimpleTenantMixin, ConstitutionalMixin, AuditMixin, StatusMixin
):
    """
    Base model class for all ACGS service entities.

    This class combines all standard mixins to provide a complete
    foundation for ACGS entities with constitutional compliance,
    multi-tenant support, audit trails, and status tracking.
    """

    __abstract__ = True

    @declared_attr
    def id(self):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            index=True,
            comment="Unique identifier for the entity",
        )


# Example service-specific models
class ExampleResource(BaseACGSModel):
    """
    Example resource model demonstrating ACGS patterns.

    This model shows how to create service-specific entities
    that inherit all the standard ACGS functionality.
    """

    __tablename__ = "example_resources"

    # Basic entity fields
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Human-readable name for the resource",
    )

    description = Column(
        Text, nullable=True, comment="Detailed description of the resource"
    )

    # Metadata and configuration
    metadata = Column(
        JSON, nullable=False, default=dict, comment="Additional metadata as JSON"
    )

    # Service-specific fields
    resource_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type categorization for the resource",
    )

    priority = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Priority level for processing or display",
    )

    # Relationship examples would go here
    # parent_id = Column(UUID(as_uuid=True), ForeignKey("example_resources.id"), nullable=True)
    # parent = relationship("ExampleResource", remote_side=[id])

    def __repr__(self):
        return f"<ExampleResource(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>"


class ExampleConfiguration(BaseACGSModel):
    """
    Example configuration model for service settings.

    This model demonstrates how to store service-specific
    configuration with constitutional compliance.
    """

    __tablename__ = "example_configurations"

    # Configuration identification
    config_key = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Unique key for the configuration setting",
    )

    config_value = Column(
        Text,
        nullable=True,
        comment="Configuration value (can be JSON for complex values)",
    )

    config_type = Column(
        String(50),
        nullable=False,
        default="string",
        comment="Type of configuration value (string, json, boolean, etc.)",
    )

    # Configuration metadata
    description = Column(
        Text, nullable=True, comment="Description of what this configuration controls"
    )

    is_sensitive = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this configuration contains sensitive data",
    )

    is_system_managed = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this configuration is managed by the system",
    )

    # Validation and constraints
    validation_rules = Column(
        JSON, nullable=True, comment="JSON schema or validation rules for the value"
    )

    def __repr__(self):
        return f"<ExampleConfiguration(key='{self.config_key}', tenant_id={self.tenant_id})>"


class ExampleAuditLog(Base, SimpleTenantMixin, ConstitutionalMixin):
    """
    Example audit log model for tracking service activities.

    This model demonstrates how to create audit logging
    without the standard audit mixin (to avoid circular logging).
    """

    __tablename__ = "example_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Event identification
    event_type = Column(
        String(100), nullable=False, index=True, comment="Type of event that occurred"
    )

    entity_type = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Type of entity that was affected",
    )

    entity_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the entity that was affected",
    )

    # Event details
    action = Column(String(100), nullable=False, comment="Action that was performed")

    result = Column(
        String(50),
        nullable=False,
        comment="Result of the action (success, failure, etc.)",
    )

    details = Column(JSON, nullable=True, comment="Additional details about the event")

    # User and request context
    user_id = Column(
        Integer,
        nullable=True,
        index=True,
        comment="ID of user who performed the action",
    )

    request_id = Column(
        String(255), nullable=True, index=True, comment="Request ID for tracing"
    )

    ip_address = Column(
        String(45),  # IPv6 compatible
        nullable=True,
        comment="IP address of the request",
    )

    user_agent = Column(
        Text, nullable=True, comment="User agent string from the request"
    )

    # Timestamp (single field for audit logs)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
        comment="When the event occurred",
    )

    def __repr__(self):
        return f"<ExampleAuditLog(event_type='{self.event_type}', action='{self.action}', tenant_id={self.tenant_id})>"


# Model utilities and helpers
class ModelUtilities:
    """
    Utility class for common model operations.

    This class provides helper methods for working with ACGS models
    in a consistent way across all services.
    """

    @staticmethod
    def to_dict(model_instance, exclude_fields: list | None = None) -> dict:
        """
        Convert a model instance to a dictionary.

        Args:
            model_instance: SQLAlchemy model instance
            exclude_fields: List of field names to exclude from the result

        Returns:
            Dictionary representation of the model
        """
        exclude_fields = exclude_fields or []
        result = {}

        for column in model_instance.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(model_instance, column.name)

                # Handle special types
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    result[column.name] = str(value)
                else:
                    result[column.name] = value

        return result

    @staticmethod
    def validate_constitutional_compliance(model_instance) -> bool:
        """
        Validate constitutional compliance for a model instance.

        Args:
            model_instance: SQLAlchemy model instance with constitutional compliance

        Returns:
            True if compliant, False otherwise
        """
        if hasattr(model_instance, "constitutional_hash"):
            return model_instance.constitutional_hash == CONSTITUTIONAL_HASH
        return True  # Non-constitutional models are considered compliant

    @staticmethod
    def update_constitutional_compliance(model_instance):
        """
        Update constitutional compliance fields for a model instance.

        Args:
            model_instance: SQLAlchemy model instance
        """
        if hasattr(model_instance, "constitutional_hash"):
            model_instance.constitutional_hash = CONSTITUTIONAL_HASH

        if hasattr(model_instance, "updated_at"):
            model_instance.updated_at = datetime.now(timezone.utc)


# Database event listeners for constitutional compliance (if SQLAlchemy events are available)
try:
    from sqlalchemy import event

    @event.listens_for(BaseACGSModel, "before_insert", propagate=True)
    def validate_constitutional_compliance_on_insert(mapper, connection, target):
        """Ensure constitutional compliance on insert."""
        if hasattr(target, "constitutional_hash"):
            target.constitutional_hash = CONSTITUTIONAL_HASH

    @event.listens_for(BaseACGSModel, "before_update", propagate=True)
    def validate_constitutional_compliance_on_update(mapper, connection, target):
        """Ensure constitutional compliance on update."""
        if hasattr(target, "constitutional_hash"):
            target.constitutional_hash = CONSTITUTIONAL_HASH
        if hasattr(target, "updated_at"):
            target.updated_at = datetime.now(timezone.utc)

except ImportError:
    # SQLAlchemy events not available, compliance will be handled in application layer
    pass


# Export commonly used classes
__all__ = [
    "CONSTITUTIONAL_HASH",
    "AuditMixin",
    "BaseACGSModel",
    "ConstitutionalMixin",
    "ExampleAuditLog",
    "ExampleConfiguration",
    "ExampleResource",
    "ModelUtilities",
    "SimpleTenantMixin",
    "StatusMixin",
]
