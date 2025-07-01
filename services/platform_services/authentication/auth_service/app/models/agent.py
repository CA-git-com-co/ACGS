"""
Agent Identity Management Models

This module defines the database models for autonomous agent identity management,
extending the existing authentication system to support agents as first-class entities.

Key Features:
- Unique agent identities with stable credentials
- Agent lifecycle management (active, suspended, retired)
- Owner assignment and responsibility tracking
- Role-based permissions and capability definitions
- Integration with existing RBAC system
- Audit trail for all agent identity changes
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class AgentStatus(str, Enum):
    """Agent lifecycle status enumeration."""

    PENDING = "pending"  # Agent created but not yet activated
    ACTIVE = "active"  # Agent is operational
    SUSPENDED = "suspended"  # Agent temporarily disabled
    RETIRED = "retired"  # Agent permanently deactivated
    COMPROMISED = "compromised"  # Agent credentials potentially compromised


class AgentType(str, Enum):
    """Agent type classification."""

    CODING_AGENT = "coding_agent"  # Code generation and modification
    POLICY_AGENT = "policy_agent"  # Policy enforcement and governance
    MONITORING_AGENT = "monitoring_agent"  # System monitoring and alerting
    ANALYSIS_AGENT = "analysis_agent"  # Data analysis and reporting
    INTEGRATION_AGENT = "integration_agent"  # External system integration
    CUSTOM_AGENT = "custom_agent"  # Custom agent types


class Agent(Base):
    """
    Agent identity model for autonomous agents in the ACGS system.

    Agents are autonomous entities that can perform actions within the system
    under human oversight and constitutional constraints.
    """

    __tablename__ = "agents"

    # Primary identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(
        String(100), unique=True, nullable=False, index=True
    )  # Human-readable ID
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Agent classification
    agent_type = Column(
        String(50), nullable=False, default=AgentType.CODING_AGENT.value
    )
    version = Column(String(50), nullable=False, default="1.0.0")

    # Status and lifecycle
    status = Column(
        String(20), nullable=False, default=AgentStatus.PENDING.value, index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    activated_at = Column(DateTime(timezone=True), nullable=True)
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    retired_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)

    # Ownership and responsibility
    owner_user_id = Column(
        Integer, ForeignKey("auth_users.id"), nullable=False, index=True
    )
    responsible_team = Column(String(100), nullable=True)  # Team responsible for agent
    contact_email = Column(String(255), nullable=True)

    # Capabilities and permissions
    capabilities = Column(
        JSON, nullable=False, default=list
    )  # List of agent capabilities
    permissions = Column(JSON, nullable=False, default=list)  # Specific permissions
    role_assignments = Column(JSON, nullable=False, default=list)  # Assigned roles

    # Security and access control
    api_key_hash = Column(String(255), nullable=True)  # Hashed API key for agent auth
    allowed_services = Column(
        JSON, nullable=False, default=list
    )  # Services agent can access
    allowed_operations = Column(
        JSON, nullable=False, default=list
    )  # Operations agent can perform
    ip_whitelist = Column(JSON, nullable=True)  # Allowed IP addresses

    # Resource limits and constraints
    max_requests_per_minute = Column(Integer, default=100, nullable=False)
    max_concurrent_operations = Column(Integer, default=5, nullable=False)
    resource_quota = Column(JSON, nullable=True)  # CPU, memory, storage limits

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    compliance_level = Column(
        String(20), nullable=False, default="standard"
    )  # standard, high, critical
    requires_human_approval = Column(Boolean, default=True, nullable=False)

    # Monitoring and metrics
    total_operations = Column(Integer, default=0, nullable=False)
    successful_operations = Column(Integer, default=0, nullable=False)
    failed_operations = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata and configuration
    configuration = Column(JSON, nullable=True)  # Agent-specific configuration
    metadata = Column(JSON, nullable=True)  # Additional metadata
    tags = Column(JSON, nullable=False, default=list)  # Searchable tags

    # Relationships
    owner = relationship("User", back_populates="owned_agents")
    audit_logs = relationship(
        "AgentAuditLog", back_populates="agent", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "AgentSession", back_populates="agent", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (UniqueConstraint("agent_id", name="uq_agent_id"),)

    def __repr__(self):
        return f"<Agent(id={self.id}, agent_id='{self.agent_id}', name='{self.name}', status='{self.status}')>"

    def is_active(self) -> bool:
        """Check if agent is currently active."""
        return self.status == AgentStatus.ACTIVE.value

    def can_perform_operation(self, operation: str) -> bool:
        """Check if agent is allowed to perform a specific operation."""
        if not self.is_active():
            return False
        return operation in self.allowed_operations

    def can_access_service(self, service: str) -> bool:
        """Check if agent can access a specific service."""
        if not self.is_active():
            return False
        return service in self.allowed_services

    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities

    def get_effective_permissions(self) -> List[str]:
        """Get all effective permissions including role-based permissions."""
        effective_permissions = set(self.permissions)

        # Add permissions from role assignments
        # This would integrate with the existing Role/Permission system
        # Implementation depends on how roles are resolved

        return list(effective_permissions)


class AgentSession(Base):
    """
    Agent session tracking for monitoring active agent sessions.
    """

    __tablename__ = "agent_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True
    )
    session_token = Column(String(255), unique=True, nullable=False, index=True)

    # Session details
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_activity_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Session context
    client_ip = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    service_context = Column(
        JSON, nullable=True
    )  # Context about which service initiated session

    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    termination_reason = Column(
        String(100), nullable=True
    )  # timeout, manual, error, etc.

    # Relationships
    agent = relationship("Agent", back_populates="sessions")

    def __repr__(self):
        return f"<AgentSession(id={self.id}, agent_id={self.agent_id}, active={self.is_active})>"


class AgentAuditLog(Base):
    """
    Comprehensive audit logging for all agent identity and activity changes.
    """

    __tablename__ = "agent_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True
    )

    # Audit details
    event_type = Column(
        String(50), nullable=False, index=True
    )  # created, updated, activated, etc.
    event_description = Column(Text, nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("auth_users.id"), nullable=True)
    performed_by_system = Column(
        String(100), nullable=True
    )  # System component that made change

    # Change tracking
    old_values = Column(JSON, nullable=True)  # Previous values for updates
    new_values = Column(JSON, nullable=True)  # New values for updates

    # Context and metadata
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True)  # For tracing requests

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False)
    compliance_verified = Column(Boolean, default=False, nullable=False)

    # Additional context
    metadata = Column(JSON, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="audit_logs")
    performed_by = relationship("User", foreign_keys=[performed_by_user_id])

    def __repr__(self):
        return f"<AgentAuditLog(id={self.id}, agent_id={self.agent_id}, event_type='{self.event_type}')>"


# Update User model to include agent ownership relationship
# This would be added to the existing User model
def extend_user_model():
    """
    Extension to add agent ownership relationship to existing User model.
    This should be integrated into the existing User model definition.
    """
    # User.owned_agents = relationship("Agent", back_populates="owner")
    pass
