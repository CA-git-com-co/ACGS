"""
AI Types for ACGS System
Constitutional Hash: cdd01ef066bc6cf2

Common type definitions for AI-related operations across the ACGS system.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4


class ContentType(str, Enum):
    """Types of content that can be processed."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CODE = "code"
    STRUCTURED_DATA = "structured_data"
    MULTIMODAL = "multimodal"


class ModelType(str, Enum):
    """Types of AI models available in the system."""
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3 = "claude-3"
    CLAUDE_2 = "claude-2"
    LLAMA_2 = "llama-2"
    MISTRAL = "mistral"
    GEMINI = "gemini"
    CUSTOM = "custom"


class RequestType(str, Enum):
    """Types of AI requests."""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    QUESTION_ANSWERING = "question_answering"
    CODE_GENERATION = "code_generation"
    MULTIMODAL_ANALYSIS = "multimodal_analysis"


class MultimodalRequest(BaseModel):
    """Request for multimodal AI processing."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    request_type: RequestType
    content_type: ContentType
    content: Any
    model_preferences: List[ModelType] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    constitutional_hash: str = Field(default="cdd01ef066bc6cf2")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MultimodalResponse(BaseModel):
    """Response from multimodal AI processing."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    request_id: str
    model_type: ModelType
    content: Any
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    constitutional_compliance: bool = True
    constitutional_hash: str = Field(default="cdd01ef066bc6cf2")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AICapability(BaseModel):
    """Represents an AI model's capability."""
    model_type: ModelType
    supported_content_types: List[ContentType]
    supported_request_types: List[RequestType]
    max_context_length: int
    average_latency_ms: float
    cost_per_1k_tokens: float
    constitutional_compliant: bool = True


class ModelPerformanceMetrics(BaseModel):
    """Performance metrics for AI models."""
    model_type: ModelType
    request_type: RequestType
    content_type: ContentType
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    success_rate: float
    error_rate: float
    throughput_rps: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)


__all__ = [
    'ContentType',
    'ModelType',
    'RequestType',
    'MultimodalRequest',
    'MultimodalResponse',
    'AICapability',
    'ModelPerformanceMetrics',
]