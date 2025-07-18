"""
Blockchain Audit Module - Data Models and Schemas
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class EventType(str, Enum):
    """Audit event types"""

    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    COMPLIANCE_CHECK = "compliance_check"
    REVIEW_DECISION = "review_decision"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"


class BlockchainNetwork(str, Enum):
    """Supported blockchain networks"""

    ETHEREUM = "ethereum"
    SOLANA = "solana"
    POLYGON = "polygon"
    LOCAL = "local"


class AuditEvent(BaseModel):
    """Audit event model for blockchain logging"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    user_id: str
    service_name: str
    action: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class BlockchainRecord(BaseModel):
    """Blockchain record model"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    blockchain_network: BlockchainNetwork
    transaction_hash: str
    block_number: Optional[int] = None
    contract_address: Optional[str] = None
    gas_used: Optional[int] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class AuditLogRequest(BaseModel):
    """Request for creating audit log entry"""

    event_type: EventType
    user_id: str
    service_name: str
    action: str
    data: Dict[str, Any] = Field(default_factory=dict)
    blockchain_enabled: bool = Field(default=True)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class AuditLogResponse(BaseModel):
    """Response for audit log operations"""

    event_id: str
    blockchain_record_id: Optional[str] = None
    transaction_hash: Optional[str] = None
    status: str
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(default="healthy")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(default_factory=dict)
