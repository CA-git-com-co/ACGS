"""
Core Context Data Models

Defines the data structures for different types of context in the ACGS system,
providing hierarchical context management with TTL-based lifecycle management.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, validator

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ContextType(str, Enum):
    """Types of context in the ACGS system with hierarchical TTL."""

    CONVERSATION = "conversation"  # TTL: 1-10 minutes
    DOMAIN = "domain"  # TTL: 1-24 hours
    CONSTITUTIONAL = "constitutional"  # TTL: weeks
    AGENT = "agent"  # TTL: per-agent lifecycle
    POLICY = "policy"  # TTL: indefinite with versioning


class ContextPriority(str, Enum):
    """Priority levels for context operations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContextStatus(str, Enum):
    """Status of context entries."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    PENDING = "pending"


class ContextMetadata(BaseModel):
    """Metadata associated with context entries."""

    model_config = ConfigDict(extra="allow")

    source_service: str = Field(description="Service that created this context")
    created_by: str | None = Field(
        None, description="User or agent that created context"
    )
    constitutional_compliant: bool = Field(
        True, description="Constitutional compliance status"
    )
    compliance_version: str = Field("1.0", description="Compliance validation version")
    wina_optimized: bool = Field(
        False, description="Whether WINA optimization was applied"
    )
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        description="Model used for embeddings",
    )
    tags: list[str] = Field(
        default_factory=list, description="Context tags for categorization"
    )
    sensitivity_level: str = Field("normal", description="Data sensitivity level")
    retention_policy: str = Field("standard", description="Data retention policy")
    access_level: str = Field("internal", description="Access control level")


class BaseContext(BaseModel):
    """Base context model with common fields."""

    model_config = ConfigDict(validate_assignment=True)

    context_id: UUID = Field(
        default_factory=uuid4, description="Unique context identifier"
    )
    context_type: ContextType = Field(description="Type of context")
    priority: ContextPriority = Field(
        default=ContextPriority.MEDIUM, description="Context priority"
    )
    status: ContextStatus = Field(
        default=ContextStatus.ACTIVE, description="Context status"
    )

    content: str = Field(description="Main context content")
    content_hash: str = Field(description="SHA256 hash of content for integrity")

    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    expires_at: datetime | None = Field(None, description="Expiration timestamp")
    accessed_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last access timestamp"
    )

    metadata: ContextMetadata = Field(
        default_factory=ContextMetadata, description="Context metadata"
    )

    # Hierarchical relationships
    parent_context_id: UUID | None = Field(None, description="Parent context ID")
    child_context_ids: list[UUID] = Field(
        default_factory=list, description="Child context IDs"
    )

    # Search and retrieval
    embedding_vector: list[float] | None = Field(
        None, description="Vector embedding for semantic search"
    )
    keywords: list[str] = Field(
        default_factory=list, description="Keywords for traditional search"
    )

    @validator("expires_at", pre=True, always=True)
    def set_expiration(self, v, values):
        """Set default expiration based on context type."""
        if v is not None:
            return v

        context_type = values.get("context_type")
        created_at = values.get("created_at", datetime.utcnow())

        if context_type == ContextType.CONVERSATION:
            return created_at + timedelta(minutes=10)
        if context_type == ContextType.DOMAIN:
            return created_at + timedelta(hours=24)
        if context_type == ContextType.CONSTITUTIONAL:
            return created_at + timedelta(weeks=4)
        if context_type == ContextType.AGENT:
            return created_at + timedelta(hours=48)
        # POLICY type has no expiration (None)
        return None

    def is_expired(self) -> bool:
        """Check if context has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def refresh_access(self) -> None:
        """Update last access timestamp."""
        self.accessed_at = datetime.utcnow()


class ConversationContext(BaseContext):
    """Context for active conversations and dialogue."""

    context_type: ContextType = Field(default=ContextType.CONVERSATION, frozen=True)

    conversation_id: str = Field(description="Conversation identifier")
    participant_ids: list[str] = Field(description="Conversation participants")
    turn_number: int = Field(default=1, description="Turn number in conversation")
    dialogue_state: dict[str, Any] = Field(
        default_factory=dict, description="Current dialogue state"
    )
    intent_classification: str | None = Field(
        None, description="Classified user intent"
    )
    sentiment_score: float | None = Field(None, description="Sentiment analysis score")


class DomainContext(BaseContext):
    """Context for domain-specific knowledge and information."""

    context_type: ContextType = Field(default=ContextType.DOMAIN, frozen=True)

    domain: str = Field(
        description="Domain identifier (e.g., legal, medical, financial)"
    )
    subdomain: str | None = Field(None, description="Subdomain specification")
    expertise_level: str = Field(
        default="general", description="Required expertise level"
    )
    domain_principles: list[str] = Field(
        default_factory=list, description="Relevant domain principles"
    )
    regulatory_context: dict[str, Any] = Field(
        default_factory=dict, description="Regulatory information"
    )


class ConstitutionalContext(BaseContext):
    """Context for constitutional principles and compliance rules."""

    context_type: ContextType = Field(default=ContextType.CONSTITUTIONAL, frozen=True)

    principle_id: str = Field(description="Constitutional principle identifier")
    principle_text: str = Field(description="Full principle text")
    interpretation_guidelines: list[str] = Field(
        default_factory=list, description="Interpretation guidelines"
    )
    compliance_requirements: dict[str, Any] = Field(
        default_factory=dict, description="Compliance requirements"
    )
    precedent_cases: list[str] = Field(
        default_factory=list, description="Related precedent cases"
    )
    constitutional_weight: float = Field(
        default=1.0, description="Relative importance weight"
    )


class AgentContext(BaseContext):
    """Context for agent-specific memory and state."""

    context_type: ContextType = Field(default=ContextType.AGENT, frozen=True)

    agent_id: str = Field(description="Agent identifier")
    agent_type: str = Field(
        description="Type of agent (e.g., ethics, legal, operational)"
    )
    task_context: dict[str, Any] = Field(
        default_factory=dict, description="Current task context"
    )
    learned_preferences: dict[str, Any] = Field(
        default_factory=dict, description="Agent learned preferences"
    )
    interaction_history: list[dict[str, Any]] = Field(
        default_factory=list, description="Interaction history"
    )
    performance_metrics: dict[str, float] = Field(
        default_factory=dict, description="Agent performance metrics"
    )


class PolicyContext(BaseContext):
    """Context for policy definitions and governance rules."""

    context_type: ContextType = Field(default=ContextType.POLICY, frozen=True)

    policy_id: str = Field(description="Policy identifier")
    policy_version: str = Field(description="Policy version")
    policy_category: str = Field(description="Policy category")
    enforcement_level: str = Field(default="mandatory", description="Enforcement level")
    policy_rules: list[dict[str, Any]] = Field(
        default_factory=list, description="Policy rules"
    )
    exceptions: list[dict[str, Any]] = Field(
        default_factory=list, description="Policy exceptions"
    )
    review_schedule: str | None = Field(None, description="Policy review schedule")


class ContextSearchQuery(BaseModel):
    """Query model for context search operations."""

    query_text: str = Field(description="Search query text")
    context_types: list[ContextType] = Field(
        default_factory=list, description="Filter by context types"
    )
    semantic_search: bool = Field(
        default=True, description="Enable semantic vector search"
    )
    keyword_search: bool = Field(default=True, description="Enable keyword search")

    # Filtering options
    priority_filter: ContextPriority | None = Field(
        None, description="Filter by priority"
    )
    created_after: datetime | None = Field(None, description="Filter by creation date")
    created_before: datetime | None = Field(None, description="Filter by creation date")
    tags_filter: list[str] = Field(default_factory=list, description="Filter by tags")

    # Search options
    limit: int = Field(
        default=10, ge=1, le=100, description="Maximum results to return"
    )
    offset: int = Field(default=0, ge=0, description="Result offset for pagination")
    similarity_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum similarity score"
    )

    # WINA optimization
    apply_wina_optimization: bool = Field(
        default=True, description="Apply WINA optimization to search"
    )


class ContextSearchResult(BaseModel):
    """Result model for context search operations."""

    context: BaseContext = Field(description="Found context")
    similarity_score: float = Field(description="Similarity score (0.0 to 1.0)")
    rank: int = Field(description="Result rank")
    matched_keywords: list[str] = Field(
        default_factory=list, description="Matched keywords"
    )
    relevance_explanation: str | None = Field(
        None, description="Explanation of relevance"
    )


class ContextStats(BaseModel):
    """Statistics about context storage and usage."""

    total_contexts: int = Field(description="Total number of contexts")
    contexts_by_type: dict[ContextType, int] = Field(
        description="Context count by type"
    )
    contexts_by_status: dict[ContextStatus, int] = Field(
        description="Context count by status"
    )

    # Storage metrics
    total_storage_size: int = Field(description="Total storage size in bytes")
    average_context_size: float = Field(description="Average context size in bytes")

    # Performance metrics
    average_retrieval_latency_ms: float = Field(description="Average retrieval latency")
    average_storage_latency_ms: float = Field(description="Average storage latency")
    cache_hit_rate: float = Field(description="Cache hit rate percentage")

    # Usage metrics
    contexts_accessed_today: int = Field(description="Contexts accessed today")
    most_accessed_types: list[ContextType] = Field(
        description="Most accessed context types"
    )

    # System health
    expired_contexts_pending_cleanup: int = Field(
        description="Expired contexts awaiting cleanup"
    )
    constitutional_compliance_rate: float = Field(
        description="Constitutional compliance rate"
    )
    wina_optimization_rate: float = Field(description="WINA optimization usage rate")

    collection_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Stats collection time"
    )
