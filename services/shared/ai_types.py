#!/usr/bin/env python3
"""
Shared AI Types for ACGS-PGP System

This module contains shared type definitions used across the AI services
to avoid circular imports.

Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ModelType(Enum):
    """Available AI models."""

    FLASH_LITE = "google/gemini-2.5-flash-lite-preview-06-17"
    FLASH_FULL = "google/gemini-2.5-flash-preview-06-17"
    DEEPSEEK_R1 = "deepseek/deepseek-r1-0528:free"


class RequestType(Enum):
    """Types of multimodal requests."""

    QUICK_ANALYSIS = "quick_analysis"
    DETAILED_ANALYSIS = "detailed_analysis"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"
    MULTIMODAL_PROCESSING = "multimodal_processing"
    CONTENT_MODERATION = "content_moderation"
    POLICY_ANALYSIS = "policy_analysis"
    AUDIT_VALIDATION = "audit_validation"


class ContentType(Enum):
    """Types of content in requests."""

    TEXT_ONLY = "text_only"
    IMAGE_ONLY = "image_only"
    TEXT_AND_IMAGE = "text_and_image"


@dataclass
class ModelMetrics:
    """Performance metrics for a model response."""

    response_time_ms: float
    token_count: int
    cost_estimate: float
    quality_score: float
    constitutional_compliance: bool
    cache_hit: bool = False
    cache_level: str | None = None


@dataclass
class MultimodalRequest:
    """Request for multimodal AI processing."""

    request_id: str
    request_type: RequestType
    content_type: ContentType
    text_content: str | None = None
    image_url: str | None = None
    image_data: str | None = None  # Base64 encoded
    priority: str = "medium"  # low, medium, high
    constitutional_context: dict[str, Any] | None = None

    def __post_init__(self):
        """Validate request after initialization."""
        if self.content_type == ContentType.TEXT_ONLY and not self.text_content:
            raise ValueError("Text content required for TEXT_ONLY requests")
        if self.content_type == ContentType.IMAGE_ONLY and not (
            self.image_url or self.image_data
        ):
            raise ValueError("Image URL or data required for IMAGE_ONLY requests")
        if self.content_type == ContentType.TEXT_AND_IMAGE:
            if not self.text_content or not (self.image_url or self.image_data):
                raise ValueError(
                    "Both text and image required for TEXT_AND_IMAGE requests"
                )


@dataclass
class MultimodalResponse:
    """Response from multimodal AI processing."""

    request_id: str
    model_used: ModelType
    response_content: str
    constitutional_compliance: bool
    confidence_score: float
    metrics: ModelMetrics
    constitutional_hash: str
    violations: list[str] = None
    warnings: list[str] = None
    timestamp: str = None
    cache_info: dict[str, Any] | None = None

    def __post_init__(self):
        """Set defaults after initialization."""
        if self.violations is None:
            self.violations = []
        if self.warnings is None:
            self.warnings = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.cache_info is None:
            self.cache_info = {"hit": False}
