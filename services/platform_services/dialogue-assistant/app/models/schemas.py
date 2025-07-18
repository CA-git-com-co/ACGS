"""
Dialogue Assistant Service - Data Models and Schemas
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid
from datetime import datetime

# Constitutional compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class MessageRole(str, Enum):
    """Message role types in conversation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationStatus(str, Enum):
    """Conversation status types"""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ComplianceLevel(str, Enum):
    """Compliance checking levels"""

    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


class ConversationMessage(BaseModel):
    """Individual message in conversation"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole = Field(description="Message role (user/assistant/system)")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    compliance_checked: bool = Field(default=False)
    compliance_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ConversationContext(BaseModel):
    """Context information for conversation"""

    user_id: str = Field(description="User identifier")
    session_id: str = Field(description="Session identifier")
    conversation_id: str = Field(description="Conversation identifier")
    tenant_id: Optional[str] = Field(None, description="Tenant identifier")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ChatRequest(BaseModel):
    """Request for chat conversation"""

    message: str = Field(min_length=1, max_length=4000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    context: Optional[ConversationContext] = Field(
        None, description="Conversation context"
    )
    compliance_level: ComplianceLevel = Field(default=ComplianceLevel.MODERATE)
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = Field(default=False, description="Enable streaming response")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    @validator("constitutional_hash")
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(
                f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        return v


class ChatResponse(BaseModel):
    """Response from chat conversation"""

    response: str = Field(description="Assistant response")
    conversation_id: str = Field(description="Conversation identifier")
    message_id: str = Field(description="Message identifier")
    compliance_check: Dict[str, Any] = Field(default_factory=dict)
    usage: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None


class ConversationHistory(BaseModel):
    """Full conversation history"""

    conversation_id: str = Field(description="Conversation identifier")
    messages: List[ConversationMessage] = Field(description="List of messages")
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    context: Optional[ConversationContext] = None
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class StreamingChatResponse(BaseModel):
    """Streaming chat response chunk"""

    chunk: str = Field(description="Response chunk")
    conversation_id: str = Field(description="Conversation identifier")
    message_id: str = Field(description="Message identifier")
    is_final: bool = Field(default=False, description="Whether this is the final chunk")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ConversationSummary(BaseModel):
    """Summary of conversation for context management"""

    conversation_id: str = Field(description="Conversation identifier")
    summary: str = Field(description="Conversation summary")
    key_topics: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = Field(None, description="Overall sentiment")
    compliance_summary: Dict[str, Any] = Field(default_factory=dict)
    message_count: int = Field(ge=0, description="Number of messages")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ComplianceCheck(BaseModel):
    """Compliance check result"""

    compliant: bool = Field(description="Whether content is compliant")
    score: float = Field(ge=0.0, le=1.0, description="Compliance confidence score")
    violations: List[str] = Field(default_factory=list)
    categories: Dict[str, float] = Field(default_factory=dict)
    recommendation: str = Field(description="Recommended action")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ConversationAnalytics(BaseModel):
    """Analytics for conversation patterns"""

    total_conversations: int = Field(ge=0)
    total_messages: int = Field(ge=0)
    avg_response_time: float = Field(ge=0.0)
    compliance_rate: float = Field(ge=0.0, le=1.0)
    top_topics: List[str] = Field(default_factory=list)
    user_satisfaction: Optional[float] = Field(None, ge=0.0, le=1.0)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(default="healthy")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")
    services: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(description="Error message")
    error_code: str = Field(description="Error code")
    details: Optional[Dict[str, Any]] = None
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationSearchRequest(BaseModel):
    """Search request for conversations"""

    query: str = Field(min_length=1, description="Search query")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    date_from: Optional[datetime] = Field(None, description="Start date filter")
    date_to: Optional[datetime] = Field(None, description="End date filter")
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ConversationSearchResult(BaseModel):
    """Search result for conversations"""

    conversations: List[ConversationSummary] = Field(description="Found conversations")
    total: int = Field(ge=0, description="Total number of results")
    limit: int = Field(description="Result limit")
    offset: int = Field(description="Result offset")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
