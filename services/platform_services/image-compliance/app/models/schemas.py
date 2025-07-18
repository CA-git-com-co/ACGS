"""
Image Compliance Service - Data Models and Schemas
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid
from datetime import datetime

# Constitutional compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ImageContentType(str, Enum):
    """Image content classification types"""

    SAFE = "safe"
    NSFW = "nsfw"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    POLITICAL_SENSITIVE = "political_sensitive"
    UNKNOWN = "unknown"


class ComplianceViolation(str, Enum):
    """Types of compliance violations"""

    NSFW_CONTENT = "nsfw_content"
    VIOLENT_CONTENT = "violent_content"
    HATE_SPEECH_CONTENT = "hate_speech_content"
    POLITICAL_CONTENT = "political_content"
    DEEPFAKE_CONTENT = "deepfake_content"
    COPYRIGHTED_CONTENT = "copyrighted_content"


class ImageAuditRequest(BaseModel):
    """Request model for image audit"""

    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    image_url: Optional[str] = Field(None, description="URL to image")
    context: Optional[str] = Field(None, description="Additional context for analysis")
    user_id: Optional[str] = Field(None, description="User ID for audit trail")
    constitutional_hash: str = Field(
        default=CONSTITUTIONAL_HASH, description="Constitutional compliance hash"
    )

    @validator("constitutional_hash")
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(
                f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        return v

    @validator("image_data", "image_url")
    def validate_image_source(cls, v, values):
        if not values.get("image_data") and not v:
            raise ValueError("Either image_data or image_url must be provided")
        return v


class ImageAuditResult(BaseModel):
    """Result model for image audit"""

    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    compliant: bool = Field(description="Whether image is compliant")
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence in the assessment"
    )
    violations: List[ComplianceViolation] = Field(default_factory=list)
    labels: Dict[ImageContentType, float] = Field(default_factory=dict)
    analysis_details: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None


class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""

    prompt: str = Field(
        min_length=1, max_length=1000, description="Text prompt for image generation"
    )
    negative_prompt: Optional[str] = Field(
        None, description="Negative prompt to avoid certain content"
    )
    width: int = Field(default=512, ge=64, le=2048, description="Image width")
    height: int = Field(default=512, ge=64, le=2048, description="Image height")
    num_inference_steps: int = Field(
        default=20, ge=1, le=100, description="Number of denoising steps"
    )
    guidance_scale: float = Field(
        default=7.5, ge=1.0, le=20.0, description="Guidance scale"
    )
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    user_id: Optional[str] = Field(None, description="User ID for audit trail")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    @validator("constitutional_hash")
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(
                f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
            )
        return v


class ImageGenerationResult(BaseModel):
    """Result model for image generation"""

    generation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    success: bool = Field(description="Whether generation was successful")
    image_url: Optional[str] = Field(None, description="URL to generated image")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    prompt_used: str = Field(description="Final prompt used for generation")
    safety_check: str = Field(default="passed", description="Safety check result")
    audit_result: Optional[ImageAuditResult] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None


class ImageIndexRequest(BaseModel):
    """Request model for indexing image content"""

    content_id: str = Field(description="Unique content identifier")
    image_url: str = Field(description="URL to image")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    category: Optional[str] = None
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
