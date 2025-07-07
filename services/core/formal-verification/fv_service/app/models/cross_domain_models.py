"""
Cross-domain testing models for formal verification service.
Constitutional compliance hash: cdd01ef066bc6cf2
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, JSON, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DomainType(str, Enum):
    """Domain types for cross-domain testing."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"


class DomainContext(Base):
    """Domain context for cross-domain testing."""
    __tablename__ = "domain_contexts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    domain_type = Column(String(50), nullable=False)
    description = Column(Text)
    configuration = Column(JSON)
    constitutional_hash = Column(String(16), default=CONSTITUTIONAL_HASH)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class CrossDomainTestScenario(Base):
    """Cross-domain test scenario definition."""
    __tablename__ = "cross_domain_test_scenarios"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    source_domain = Column(String(50), nullable=False)
    target_domain = Column(String(50), nullable=False)
    test_parameters = Column(JSON)
    expected_outcomes = Column(JSON)
    constitutional_hash = Column(String(16), default=CONSTITUTIONAL_HASH)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class CrossDomainTestResult(Base):
    """Cross-domain test execution result."""
    __tablename__ = "cross_domain_test_results"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    scenario_id = Column(PGUUID(as_uuid=True), nullable=False)
    test_name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_ms = Column(Integer)
    results = Column(JSON)
    metrics = Column(JSON)
    errors = Column(JSON)
    constitutional_hash = Column(String(16), default=CONSTITUTIONAL_HASH)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic models for API
class DomainContextBase(BaseModel):
    """Base domain context model."""
    name: str = Field(..., description="Domain context name")
    domain_type: DomainType = Field(..., description="Type of domain")
    description: Optional[str] = Field(None, description="Domain description")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Domain configuration")


class DomainContextCreate(DomainContextBase):
    """Domain context creation model."""
    pass


class DomainContextUpdate(BaseModel):
    """Domain context update model."""
    name: Optional[str] = None
    domain_type: Optional[DomainType] = None
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DomainContextResponse(DomainContextBase):
    """Domain context response model."""
    id: UUID
    constitutional_hash: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class CrossDomainTestScenarioBase(BaseModel):
    """Base cross-domain test scenario model."""
    name: str = Field(..., description="Scenario name")
    description: Optional[str] = Field(None, description="Scenario description")
    source_domain: DomainType = Field(..., description="Source domain")
    target_domain: DomainType = Field(..., description="Target domain")
    test_parameters: Optional[Dict[str, Any]] = Field(None, description="Test parameters")
    expected_outcomes: Optional[Dict[str, Any]] = Field(None, description="Expected outcomes")


class CrossDomainTestScenarioCreate(CrossDomainTestScenarioBase):
    """Cross-domain test scenario creation model."""
    pass


class CrossDomainTestScenarioResponse(CrossDomainTestScenarioBase):
    """Cross-domain test scenario response model."""
    id: UUID
    constitutional_hash: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class CrossDomainTestResultBase(BaseModel):
    """Base cross-domain test result model."""
    scenario_id: UUID = Field(..., description="Test scenario ID")
    test_name: str = Field(..., description="Test name")
    status: TestStatus = Field(..., description="Test status")
    start_time: datetime = Field(..., description="Test start time")
    end_time: Optional[datetime] = Field(None, description="Test end time")
    duration_ms: Optional[int] = Field(None, description="Test duration in milliseconds")
    results: Optional[Dict[str, Any]] = Field(None, description="Test results")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Test metrics")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Test errors")


class CrossDomainTestResultResponse(CrossDomainTestResultBase):
    """Cross-domain test result response model."""
    id: UUID
    constitutional_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CrossDomainTestRequest(BaseModel):
    """Cross-domain test execution request."""
    scenario_id: UUID = Field(..., description="Test scenario ID")
    test_parameters: Optional[Dict[str, Any]] = Field(None, description="Override test parameters")
    timeout_seconds: Optional[int] = Field(300, description="Test timeout in seconds")


class CrossDomainTestResponse(BaseModel):
    """Cross-domain test execution response."""
    test_id: UUID = Field(..., description="Test execution ID")
    scenario_id: UUID = Field(..., description="Test scenario ID")
    status: TestStatus = Field(..., description="Test status")
    message: str = Field(..., description="Response message")
    constitutional_hash: str = Field(CONSTITUTIONAL_HASH, description="Constitutional compliance hash")
