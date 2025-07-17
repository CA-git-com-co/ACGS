"""
Adaptive Learning System - Data Models and Schemas
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid
from datetime import datetime

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class FeedbackType(str, Enum):
    """Feedback types for adaptive learning"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"

class ModelType(str, Enum):
    """Model types for adaptive learning"""
    CONSTITUTIONAL_AI = "constitutional_ai"
    GOVERNANCE = "governance"
    MULTIMODAL = "multimodal"
    RECOMMENDATION = "recommendation"
    CHAT = "chat"
    GENERAL = "general"

class FeedbackSource(str, Enum):
    """Sources of feedback"""
    USER_EXPLICIT = "user_explicit"
    USER_IMPLICIT = "user_implicit"
    SYSTEM_METRICS = "system_metrics"
    HUMAN_REVIEW = "human_review"
    AUTOMATED_EVALUATION = "automated_evaluation"

class ModelStatus(str, Enum):
    """Model training/deployment status"""
    TRAINING = "training"
    VALIDATING = "validating"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"

class Feedback(BaseModel):
    """User feedback model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: Optional[str] = None
    model_type: ModelType
    feedback_type: FeedbackType
    feedback_source: FeedbackSource
    content: str
    context: Dict[str, Any] = Field(default_factory=dict)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 0.0 or v > 5.0):
            raise ValueError('Rating must be between 0.0 and 5.0')
        return v

class LearningMetric(BaseModel):
    """Learning performance metric"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_type: ModelType
    metric_name: str
    metric_value: float
    baseline_value: Optional[float] = None
    improvement_percentage: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class ModelConfiguration(BaseModel):
    """Model configuration for adaptive learning"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_type: ModelType
    model_name: str
    configuration: Dict[str, Any]
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0.0"
    status: ModelStatus = ModelStatus.TRAINING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class TrainingJob(BaseModel):
    """Training job model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_type: ModelType
    model_configuration_id: str
    training_data_size: int
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001
    status: ModelStatus = ModelStatus.TRAINING
    progress: float = Field(0.0, ge=0.0, le=1.0)
    metrics: Dict[str, float] = Field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class FeedbackRequest(BaseModel):
    """Request for submitting feedback"""
    user_id: str
    session_id: Optional[str] = None
    model_type: ModelType
    feedback_type: FeedbackType
    feedback_source: FeedbackSource
    content: str
    context: Dict[str, Any] = Field(default_factory=dict)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class FeedbackResponse(BaseModel):
    """Response for feedback submission"""
    feedback_id: str
    status: str = "received"
    message: str = "Feedback received and processed"
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class ModelUpdateRequest(BaseModel):
    """Request for model update"""
    model_type: ModelType
    trigger_reason: str
    configuration_updates: Dict[str, Any] = Field(default_factory=dict)
    force_retrain: bool = False
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class ModelUpdateResponse(BaseModel):
    """Response for model update"""
    job_id: str
    model_type: ModelType
    status: str
    estimated_duration: Optional[int] = None  # in seconds
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class LearningStats(BaseModel):
    """Learning system statistics"""
    total_feedback_count: int
    feedback_by_type: Dict[str, int]
    feedback_by_source: Dict[str, int]
    active_models: int
    training_jobs: int
    average_rating: float
    improvement_trend: Dict[str, float]
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class ModelPerformance(BaseModel):
    """Model performance metrics"""
    model_type: ModelType
    model_name: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    constitutional_compliance: float
    user_satisfaction: float
    response_time: float
    throughput: float
    last_updated: datetime
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class AdaptiveLearningConfig(BaseModel):
    """Adaptive learning configuration"""
    min_feedback_threshold: int = 100
    retrain_threshold: float = 0.1  # 10% improvement threshold
    max_model_age_days: int = 30
    feedback_weight_decay: float = 0.9
    constitutional_compliance_threshold: float = 0.95
    auto_deployment_enabled: bool = False
    human_review_required: bool = True
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)