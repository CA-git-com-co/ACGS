"""
Database Models for ACGS-PGP v8

SQLAlchemy models for data persistence with PostgreSQL integration.
Supports all ACGS-PGP v8 data models with proper indexing and relationships.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, JSON,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class PolicyGeneration(Base):
    """Policy generation records with constitutional compliance tracking."""
    
    __tablename__ = "policy_generations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Policy content
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    policy_content = Column(Text, nullable=False)
    semantic_hash = Column(String(64), nullable=False, index=True)
    
    # Generation metadata
    stakeholders = Column(JSON, default=list)
    constitutional_principles = Column(JSON, default=list)
    priority = Column(String(50), default="medium")
    context = Column(JSON, default=dict)
    
    # Compliance and quality metrics
    constitutional_compliance_score = Column(Float, nullable=False, default=0.0)
    confidence_score = Column(Float, nullable=False, default=0.0)
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    
    # Performance metrics
    generation_time_ms = Column(Float, nullable=False, default=0.0)
    model_consensus_data = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)
    
    # User and audit information
    user_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("StabilizerExecution", back_populates="policy_generation")
    diagnostics = relationship("SystemDiagnostic", back_populates="policy_generation")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_policy_generation_created_at', 'created_at'),
        Index('idx_policy_generation_compliance', 'constitutional_compliance_score'),
        Index('idx_policy_generation_user_created', 'user_id', 'created_at'),
    )


class StabilizerExecution(Base):
    """Stabilizer execution records with performance and error tracking."""
    
    __tablename__ = "stabilizer_executions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Execution details
    operation_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    result_data = Column(JSON, default=dict)
    
    # Performance metrics
    execution_time_ms = Column(Float, default=0.0)
    memory_usage_mb = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    
    # Error detection and correction
    errors_detected = Column(Integer, default=0)
    errors_corrected = Column(Integer, default=0)
    syndrome_vector_data = Column(JSON, default=dict)
    
    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    compliance_score = Column(Float, default=0.0)
    compliance_validated = Column(Boolean, default=False)
    
    # Circuit breaker and fault tolerance
    circuit_breaker_triggered = Column(Boolean, default=False)
    fault_tolerance_applied = Column(Boolean, default=False)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Execution logs and metadata
    execution_logs = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    
    # Foreign keys
    policy_generation_id = Column(UUID(as_uuid=True), ForeignKey('policy_generations.id'), nullable=True)
    
    # Relationships
    policy_generation = relationship("PolicyGeneration", back_populates="executions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_stabilizer_execution_started_at', 'started_at'),
        Index('idx_stabilizer_execution_status', 'status'),
        Index('idx_stabilizer_execution_performance', 'execution_time_ms', 'memory_usage_mb'),
    )


class SystemDiagnostic(Base):
    """System diagnostic records with error analysis and recovery recommendations."""
    
    __tablename__ = "system_diagnostics"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diagnostic_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Diagnostic details
    target_system = Column(String(255), nullable=False, index=True)
    error_count = Column(Integer, default=0)
    critical_error_count = Column(Integer, default=0)
    
    # Health and compliance scores
    overall_health_score = Column(Float, default=0.0)
    constitutional_compliance_score = Column(Float, default=0.0)
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    
    # Recommendations
    recommendations_count = Column(Integer, default=0)
    auto_executable_recommendations = Column(Integer, default=0)
    recommendations_data = Column(JSON, default=list)
    
    # Error analysis
    errors_detected_data = Column(JSON, default=list)
    error_patterns = Column(JSON, default=dict)
    
    # Performance metrics
    diagnostic_duration_ms = Column(Float, default=0.0)
    
    # Timestamps and metadata
    diagnostic_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    audit_trail = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    
    # Foreign keys
    policy_generation_id = Column(UUID(as_uuid=True), ForeignKey('policy_generations.id'), nullable=True)
    
    # Relationships
    policy_generation = relationship("PolicyGeneration", back_populates="diagnostics")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_system_diagnostic_timestamp', 'diagnostic_timestamp'),
        Index('idx_system_diagnostic_target_system', 'target_system'),
        Index('idx_system_diagnostic_health', 'overall_health_score', 'constitutional_compliance_score'),
    )


class LSURecord(Base):
    """Logical Semantic Unit records for quantum-inspired semantic tracking."""
    
    __tablename__ = "lsu_records"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semantic_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    # LSU content
    content = Column(Text, nullable=False)
    representation_type = Column(String(100), nullable=False, index=True)
    
    # Quantum-inspired state
    quantum_state = Column(JSON, default=dict)
    error_correction_bits = Column(JSON, default=list)
    
    # Constitutional compliance
    constitutional_compliance_score = Column(Float, default=0.0)
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    
    # Metadata and timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON, default=dict)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_lsu_record_created_at', 'created_at'),
        Index('idx_lsu_record_type', 'representation_type'),
        Index('idx_lsu_record_compliance', 'constitutional_compliance_score'),
    )


class ConfigurationSetting(Base):
    """Configuration settings for ACGS-PGP v8 system."""
    
    __tablename__ = "configuration_settings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), unique=True, nullable=False, index=True)
    
    # Configuration data
    value = Column(Text, nullable=False)
    value_type = Column(String(50), nullable=False, default="string")
    description = Column(Text, nullable=True)
    
    # Metadata
    category = Column(String(100), nullable=False, index=True)
    is_sensitive = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)
    
    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_configuration_category', 'category'),
        Index('idx_configuration_updated_at', 'updated_at'),
    )


class AuditLog(Base):
    """Audit log for all ACGS-PGP v8 operations."""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Audit details
    operation = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    
    # User and session information
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Operation details
    operation_data = Column(JSON, default=dict)
    result_status = Column(String(50), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    compliance_validated = Column(Boolean, default=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_log_timestamp', 'timestamp'),
        Index('idx_audit_log_user_operation', 'user_id', 'operation'),
        Index('idx_audit_log_resource', 'resource_type', 'resource_id'),
    )
