"""
Sandbox Execution Models

Database models for execution sessions and audit logs.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ExecutionStatus(str, Enum):
    """Status of an execution session."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    KILLED = "killed"
    ERROR = "error"


class ExecutionEnvironment(str, Enum):
    """Supported execution environments."""

    PYTHON = "python"
    BASH = "bash"
    NODE = "node"
    DOCKER = "docker"


class SandboxExecution(Base):
    """Model for sandbox execution sessions."""

    __tablename__ = "sandbox_executions"

    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(String(100), unique=True, nullable=False, index=True)

    # Agent and request information
    agent_id = Column(String(100), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False)
    request_id = Column(String(100), index=True)
    session_id = Column(String(100), index=True)

    # Execution details
    environment = Column(String(50), nullable=False, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    entry_point = Column(String(500))  # Main file or command

    # Execution context and parameters
    execution_context = Column(JSON, default={})
    environment_variables = Column(JSON, default={})
    input_files = Column(JSON, default=[])  # List of file objects
    command_args = Column(JSON, default=[])

    # Resource limits and configuration
    memory_limit_mb = Column(Integer, default=512)
    cpu_limit = Column(Float, default=0.5)
    timeout_seconds = Column(Integer, default=300)
    disk_limit_mb = Column(Integer, default=1024)
    network_enabled = Column(Boolean, default=False)

    # Docker/container configuration
    container_id = Column(String(100), index=True)
    container_image = Column(String(200))
    container_config = Column(JSON, default={})

    # Execution status and results
    status = Column(
        String(20), nullable=False, default=ExecutionStatus.PENDING.value, index=True
    )
    exit_code = Column(Integer)
    stdout = Column(Text)
    stderr = Column(Text)
    output_files = Column(JSON, default=[])  # List of generated files

    # Performance metrics
    execution_time_ms = Column(Integer)
    memory_usage_mb = Column(Float)
    cpu_usage_percent = Column(Float)
    disk_usage_mb = Column(Float)

    # Timing information
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, index=True)
    completed_at = Column(DateTime, index=True)

    # Security and compliance
    constitutional_hash = Column(String(64), nullable=False)
    policy_violations = Column(JSON, default=[])
    security_violations = Column(JSON, default=[])

    # Error and debugging information
    error_message = Column(Text)
    debug_info = Column(JSON, default={})

    # Cleanup information
    cleaned_up = Column(Boolean, default=False)
    cleanup_at = Column(DateTime)

    # Additional metadata
    metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "execution_id": self.execution_id,
            "agent_id": self.agent_id,
            "environment": self.environment,
            "language": self.language,
            "status": self.status,
            "exit_code": self.exit_code,
            "execution_time_ms": self.execution_time_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


class ExecutionPolicy(Base):
    """Model for execution policies and restrictions."""

    __tablename__ = "execution_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(String(100), unique=True, nullable=False)

    # Policy scope
    agent_id = Column(String(100), index=True)  # Agent-specific policy
    agent_type = Column(String(50), index=True)  # Agent type policy
    environment = Column(String(50), index=True)  # Environment policy

    # Policy definition
    policy_name = Column(String(200), nullable=False)
    policy_description = Column(Text)
    policy_rules = Column(JSON, nullable=False)

    # Policy status
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher number = higher priority

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    expires_at = Column(DateTime)

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False)

    # Metadata
    created_by = Column(String(100))
    metadata = Column(JSON, default={})


class ExecutionAuditLog(Base):
    """Model for execution audit logs."""

    __tablename__ = "execution_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Audit event details
    event_type = Column(String(50), nullable=False, index=True)
    event_description = Column(Text, nullable=False)
    event_data = Column(JSON, default={})

    # Timing and context
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    container_id = Column(String(100))

    # Security context
    security_level = Column(String(20), default="standard")
    violations_detected = Column(JSON, default=[])

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False)

    # Additional context
    metadata = Column(JSON, default={})
