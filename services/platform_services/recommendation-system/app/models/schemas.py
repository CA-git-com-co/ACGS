"""
Recommendation System Service - Data Models and Schemas
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid
from datetime import datetime

# Constitutional compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class RecommendationType(str, Enum):
    """Types of recommendation algorithms"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    VECTOR_SIMILARITY = "vector_similarity"
    CONSTITUTIONAL_ALIGNED = "constitutional_aligned"


class ContentType(str, Enum):
    """Types of content that can be recommended"""
    DOCUMENT = "document"
    ARTICLE = "article"
    CONVERSATION = "conversation"
    SERVICE = "service"
    POLICY = "policy"
    CONSTITUTIONAL_CONTENT = "constitutional_content"


class InteractionType(str, Enum):
    """Types of user interactions"""
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    BOOKMARK = "bookmark"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"


class RecommendationContext(BaseModel):
    """Context for recommendation requests"""
    user_id: str = Field(description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    tenant_id: Optional[str] = Field(None, description="Tenant identifier")
    location: Optional[str] = Field(None, description="User location")
    device_type: Optional[str] = Field(None, description="Device type")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ContentItem(BaseModel):
    """Content item for recommendations"""
    id: str = Field(description="Content identifier")
    title: str = Field(description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content_type: ContentType = Field(description="Type of content")
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_score: float = Field(default=0.0, ge=0.0, le=1.0)
    embedding: Optional[List[float]] = Field(None, description="Content embedding vector")


class UserInteraction(BaseModel):
    """User interaction with content"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(description="User identifier")
    content_id: str = Field(description="Content identifier")
    interaction_type: InteractionType = Field(description="Type of interaction")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="User rating")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context: Optional[Dict[str, Any]] = Field(None, description="Interaction context")
    constitutional_compliant: bool = Field(default=True)


class RecommendationRequest(BaseModel):
    """Request for recommendations"""
    user_id: str = Field(description="User identifier")
    recommendation_type: RecommendationType = Field(default=RecommendationType.HYBRID)
    content_types: List[ContentType] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=100)
    context: Optional[RecommendationContext] = Field(None)
    filters: Dict[str, Any] = Field(default_factory=dict)
    exclude_ids: List[str] = Field(default_factory=list)
    constitutional_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    @validator('constitutional_hash')
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}")
        return v


class RecommendationItem(BaseModel):
    """Individual recommendation item"""
    content_id: str = Field(description="Content identifier")
    title: str = Field(description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content_type: ContentType = Field(description="Type of content")
    score: float = Field(ge=0.0, le=1.0, description="Recommendation score")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in recommendation")
    reason: str = Field(description="Reason for recommendation")
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    constitutional_score: float = Field(default=0.0, ge=0.0, le=1.0)


class RecommendationResponse(BaseModel):
    """Response with recommendations"""
    user_id: str = Field(description="User identifier")
    recommendations: List[RecommendationItem] = Field(description="List of recommendations")
    algorithm_used: RecommendationType = Field(description="Algorithm used for recommendations")
    total_items: int = Field(ge=0, description="Total number of available items")
    personalization_score: float = Field(ge=0.0, le=1.0, description="Personalization effectiveness")
    constitutional_compliance: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None


class UserProfile(BaseModel):
    """User profile for personalization"""
    user_id: str = Field(description="User identifier")
    preferences: Dict[str, Any] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    interaction_history: List[UserInteraction] = Field(default_factory=list)
    constitutional_preferences: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = Field(None, description="User embedding vector")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class SimilaritySearchRequest(BaseModel):
    """Request for similarity search"""
    query_vector: List[float] = Field(description="Query embedding vector")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    filters: Dict[str, Any] = Field(default_factory=dict)
    constitutional_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class SimilaritySearchResult(BaseModel):
    """Result from similarity search"""
    content_id: str = Field(description="Content identifier")
    similarity_score: float = Field(ge=0.0, le=1.0, description="Similarity score")
    constitutional_score: float = Field(ge=0.0, le=1.0, description="Constitutional score")
    combined_score: float = Field(ge=0.0, le=1.0, description="Combined score")
    content: ContentItem = Field(description="Content item")


class ModelTrainingRequest(BaseModel):
    """Request for model training"""
    model_type: RecommendationType = Field(description="Type of model to train")
    training_data_filter: Dict[str, Any] = Field(default_factory=dict)
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    constitutional_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ModelTrainingResult(BaseModel):
    """Result from model training"""
    model_id: str = Field(description="Trained model identifier")
    model_type: RecommendationType = Field(description="Type of model")
    training_metrics: Dict[str, float] = Field(default_factory=dict)
    constitutional_compliance: Dict[str, Any] = Field(default_factory=dict)
    training_time_ms: float = Field(ge=0.0, description="Training time in milliseconds")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeedbackRequest(BaseModel):
    """User feedback on recommendations"""
    user_id: str = Field(description="User identifier")
    recommendation_id: str = Field(description="Recommendation identifier")
    content_id: str = Field(description="Content identifier")
    feedback_type: str = Field(description="Type of feedback (positive/negative)")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="User rating")
    comment: Optional[str] = Field(None, description="User comment")
    constitutional_compliant: bool = Field(default=True)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class RecommendationAnalytics(BaseModel):
    """Analytics for recommendation system"""
    total_recommendations: int = Field(ge=0)
    total_interactions: int = Field(ge=0)
    click_through_rate: float = Field(ge=0.0, le=1.0)
    conversion_rate: float = Field(ge=0.0, le=1.0)
    constitutional_compliance_rate: float = Field(ge=0.0, le=1.0)
    avg_rating: float = Field(ge=0.0, le=5.0)
    personalization_effectiveness: float = Field(ge=0.0, le=1.0)
    top_content_types: List[Dict[str, Any]] = Field(default_factory=list)
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


class VectorIndexRequest(BaseModel):
    """Request to index content vectors"""
    content_id: str = Field(description="Content identifier")
    embedding: List[float] = Field(description="Content embedding vector")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    constitutional_score: float = Field(default=0.0, ge=0.0, le=1.0)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class PersonalizationMetrics(BaseModel):
    """Metrics for personalization effectiveness"""
    user_id: str = Field(description="User identifier")
    diversity_score: float = Field(ge=0.0, le=1.0, description="Recommendation diversity")
    novelty_score: float = Field(ge=0.0, le=1.0, description="Recommendation novelty")
    coverage_score: float = Field(ge=0.0, le=1.0, description="Content coverage")
    constitutional_alignment: float = Field(ge=0.0, le=1.0, description="Constitutional alignment")
    satisfaction_score: float = Field(ge=0.0, le=1.0, description="User satisfaction")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)