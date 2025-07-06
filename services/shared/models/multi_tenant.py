"""
Multi-Tenant Foundation Models for ACGS

This module provides the core multi-tenant models and mixins for implementing
tenant isolation and security across the ACGS platform.

Constitutional Hash: cdd01ef066bc6cf2
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, JSON, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_mixin
from sqlalchemy.ext.declarative import declared_attr

from ..database import Base

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TenantTier(str, Enum):
    """Tenant service tiers with different feature sets and limits."""
    BASIC = "basic"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"
    CONSTITUTIONAL = "constitutional"  # Special tier for constitutional oversight


class TenantStatus(str, Enum):
    """Tenant account status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    PENDING = "pending"
    TRIAL = "trial"


class SecurityLevel(str, Enum):
    """Security classification levels for tenant isolation."""
    BASIC = "basic"
    MODERATE = "moderate"
    STRICT = "strict"
    MAXIMUM = "maximum"


class DataResidency(str, Enum):
    """Data residency requirements for compliance."""
    ANY = "any"
    US = "us"
    EU = "eu"
    CANADA = "canada"
    UK = "uk"
    AUSTRALIA = "australia"


class Organization(Base):
    """
    Top-level organization entity for multi-tenant architecture.
    
    Organizations can contain multiple tenants and represent the billing
    and contract entity for enterprise customers.
    """
    __tablename__ = "organizations"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Contact and legal information
    legal_name = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=False)
    billing_email = Column(String(255), nullable=True)
    
    # Business details
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)  # startup, small, medium, large, enterprise
    website = Column(String(500), nullable=True)
    
    # Address information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Organization status and configuration
    status = Column(String(20), nullable=False, default=TenantStatus.PENDING.value)
    tier = Column(String(20), nullable=False, default=TenantTier.BASIC.value)
    
    # Compliance and governance
    constitutional_hash = Column(String(64), nullable=False, default=CONSTITUTIONAL_HASH)
    constitutional_compliance_required = Column(Boolean, default=True, nullable=False)
    data_residency = Column(String(20), nullable=False, default=DataResidency.ANY.value)
    
    # Limits and quotas
    max_tenants = Column(Integer, default=1, nullable=False)
    max_users_per_tenant = Column(Integer, default=100, nullable=False)
    max_api_requests_per_hour = Column(Integer, default=10000, nullable=False)
    
    # Security settings
    enforce_mfa = Column(Boolean, default=False, nullable=False)
    session_timeout_minutes = Column(Integer, default=480, nullable=False)  # 8 hours
    password_policy = Column(JSON, nullable=True)
    
    # Audit and timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenants = relationship("Tenant", back_populates="organization", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("max_tenants > 0", name="check_max_tenants_positive"),
        CheckConstraint("max_users_per_tenant > 0", name="check_max_users_positive"),
        CheckConstraint("max_api_requests_per_hour > 0", name="check_max_api_requests_positive"),
        CheckConstraint("session_timeout_minutes > 0", name="check_session_timeout_positive"),
        Index("idx_org_status_tier", "status", "tier"),
        Index("idx_org_created", "created_at"),
    )


class Tenant(Base):
    """
    Individual tenant within an organization.
    
    Tenants represent isolated environments within an organization,
    providing data and resource isolation for different departments,
    projects, or environments (dev/staging/prod).
    """
    __tablename__ = "tenants"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Tenant details
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Environment type
    environment_type = Column(String(20), default="production", nullable=False)  # production, staging, development, testing
    
    # Tenant status and configuration
    status = Column(String(20), nullable=False, default=TenantStatus.ACTIVE.value)
    tier = Column(String(20), nullable=False, default=TenantTier.BASIC.value)
    security_level = Column(String(20), nullable=False, default=SecurityLevel.BASIC.value)
    
    # Compliance and governance
    constitutional_hash = Column(String(64), nullable=False, default=CONSTITUTIONAL_HASH)
    constitutional_compliance_score = Column(Integer, default=100, nullable=False)
    governance_policies = Column(JSON, nullable=True)
    
    # Resource limits and quotas
    max_users = Column(Integer, nullable=True)  # Inherits from organization if null
    max_agents = Column(Integer, default=10, nullable=False)
    max_storage_gb = Column(Integer, default=100, nullable=False)
    max_compute_units = Column(Integer, default=1000, nullable=False)
    
    # API and rate limiting
    api_rate_limit_per_hour = Column(Integer, nullable=True)  # Inherits from organization if null
    api_burst_limit = Column(Integer, default=100, nullable=False)
    
    # Security and encryption
    encryption_key_id = Column(String(255), nullable=True)  # Reference to external key management
    data_encryption_required = Column(Boolean, default=True, nullable=False)
    network_isolation_required = Column(Boolean, default=False, nullable=False)
    
    # Compliance requirements
    audit_retention_days = Column(Integer, default=2555, nullable=False)  # 7 years default
    data_residency = Column(String(20), nullable=True)  # Inherits from organization if null
    compliance_frameworks = Column(JSON, nullable=True)  # ["SOC2", "GDPR", "HIPAA", etc.]
    
    # Configuration and settings
    feature_flags = Column(JSON, nullable=True)
    tenant_settings = Column(JSON, nullable=True)
    integration_settings = Column(JSON, nullable=True)
    
    # Audit and timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="tenants")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("organization_id", "slug", name="uq_tenant_org_slug"),
        CheckConstraint("max_users IS NULL OR max_users > 0", name="check_tenant_max_users_positive"),
        CheckConstraint("max_agents > 0", name="check_max_agents_positive"),
        CheckConstraint("max_storage_gb > 0", name="check_max_storage_positive"),
        CheckConstraint("max_compute_units > 0", name="check_max_compute_positive"),
        CheckConstraint("constitutional_compliance_score >= 0 AND constitutional_compliance_score <= 100", 
                       name="check_compliance_score_range"),
        CheckConstraint("audit_retention_days > 0", name="check_audit_retention_positive"),
        Index("idx_tenant_status_tier", "status", "tier"),
        Index("idx_tenant_org_status", "organization_id", "status"),
        Index("idx_tenant_created", "created_at"),
        Index("idx_tenant_accessed", "last_accessed_at"),
    )


class TenantUser(Base):
    """
    Association table linking users to tenants with role-based access.
    
    Users can belong to multiple tenants within an organization with
    different roles and permissions in each tenant.
    """
    __tablename__ = "tenant_users"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to users table
    
    # Role and permissions within this tenant
    role = Column(String(50), nullable=False, default="user")
    permissions = Column(JSON, nullable=True)
    
    # Access control
    is_active = Column(Boolean, default=True, nullable=False)
    access_level = Column(String(20), default="standard", nullable=False)  # readonly, standard, admin, owner
    
    # Invitation and activation
    invited_by_user_id = Column(Integer, nullable=True)
    invitation_token = Column(String(255), nullable=True, unique=True)
    invitation_expires_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit and timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user"),
        Index("idx_tenant_user_role", "tenant_id", "role"),
        Index("idx_tenant_user_active", "tenant_id", "is_active"),
        Index("idx_user_tenants", "user_id", "is_active"),
    )


@declarative_mixin
class TenantMixin:
    """
    Mixin class to add tenant isolation to any model.
    
    This mixin automatically adds tenant_id and ensures proper
    tenant isolation through database constraints and query filtering.
    """
    
    @declared_attr
    def tenant_id(cls):
        return Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    @declared_attr
    def __table_args__(cls):
        # Get existing table args if any
        existing_args = getattr(cls, '_table_args', ())
        if isinstance(existing_args, dict):
            existing_args = (existing_args,)
        elif existing_args is None:
            existing_args = ()
        
        # Add tenant index
        tenant_index = Index(f"idx_{cls.__tablename__}_tenant", "tenant_id")
        
        return existing_args + (tenant_index,)


@declarative_mixin
class AuditMixin:
    """
    Mixin class to add audit fields to any model.
    
    Provides created_at, updated_at, and deleted_at timestamps
    along with audit user tracking.
    """
    
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    @declared_attr
    def created_by_user_id(cls):
        return Column(Integer, nullable=True)
    
    @declared_attr
    def updated_by_user_id(cls):
        return Column(Integer, nullable=True)
    
    @declared_attr
    def deleted_by_user_id(cls):
        return Column(Integer, nullable=True)


class TenantMultiBase(TenantMixin, AuditMixin, Base):
    """
    Base class for all tenant-aware models.
    
    Combines TenantMixin and AuditMixin to provide complete
    multi-tenant support with audit trails.
    """
    __abstract__ = True


class TenantSettings(TenantMultiBase):
    """
    Flexible key-value settings storage for tenants.
    
    Allows tenants to store custom configuration and settings
    that can be retrieved at runtime.
    """
    __tablename__ = "tenant_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(100), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    
    # Setting metadata
    data_type = Column(String(50), default="string", nullable=False)  # string, integer, boolean, json
    is_sensitive = Column(Boolean, default=False, nullable=False)
    is_readonly = Column(Boolean, default=False, nullable=False)
    
    # Validation
    validation_rules = Column(JSON, nullable=True)
    default_value = Column(JSON, nullable=True)
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "category", "key", name="uq_tenant_setting"),
        Index("idx_tenant_settings_category", "tenant_id", "category"),
    )


class TenantInvitation(TenantMultiBase):
    """
    Tenant invitation system for adding users to tenants.
    
    Manages the invitation workflow for adding new users
    to tenants with specific roles and permissions.
    """
    __tablename__ = "tenant_invitations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    permissions = Column(JSON, nullable=True)
    
    # Invitation details
    invitation_token = Column(String(255), nullable=False, unique=True, index=True)
    invited_by_user_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=True)
    
    # Status and expiration
    status = Column(String(20), default="pending", nullable=False)  # pending, accepted, expired, revoked
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("idx_tenant_invitation_email", "tenant_id", "email"),
        Index("idx_tenant_invitation_status", "tenant_id", "status"),
        Index("idx_invitation_token", "invitation_token"),
    )


# Utility functions for tenant operations
def get_effective_data_residency(tenant: Tenant) -> str:
    """Get the effective data residency requirement for a tenant."""
    return tenant.data_residency or tenant.organization.data_residency


def get_effective_api_rate_limit(tenant: Tenant) -> int:
    """Get the effective API rate limit for a tenant."""
    return tenant.api_rate_limit_per_hour or tenant.organization.max_api_requests_per_hour


def get_effective_max_users(tenant: Tenant) -> int:
    """Get the effective maximum users for a tenant."""
    return tenant.max_users or tenant.organization.max_users_per_tenant


def is_tenant_constitutional_compliant(tenant: Tenant, threshold: int = 80) -> bool:
    """Check if tenant meets constitutional compliance threshold."""
    return (
        tenant.constitutional_hash == CONSTITUTIONAL_HASH and
        tenant.constitutional_compliance_score >= threshold
    )