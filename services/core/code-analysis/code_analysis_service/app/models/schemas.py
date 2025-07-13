"""
ACGS Code Analysis Engine - Pydantic Schemas
Request/response models matching the OpenAPI specification.

Constitutional Hash: cdd01ef066bc6cf2
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SymbolType(str, Enum):
    """Code symbol types."""

    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    IMPORT = "import"
    CONSTANT = "constant"
    METHOD = "method"
    PROPERTY = "property"


class DependencyType(str, Enum):
    """Dependency relationship types."""

    IMPORT = "import"
    CALL = "call"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    REFERENCE = "reference"


class AnalysisType(str, Enum):
    """Analysis operation types."""

    FILE = "file"
    DIRECTORY = "directory"
    FULL_SCAN = "full_scan"


class ContextType(str, Enum):
    """Context types for integration."""

    DOMAIN_CONTEXT = "DomainContext"
    POLICY_CONTEXT = "PolicyContext"
    CONSTITUTIONAL_CONTEXT = "ConstitutionalContext"
    AGENT_CONTEXT = "AgentContext"


# Base models with constitutional compliance
class ConstitutionalBaseModel(BaseModel):
    """Base model with constitutional compliance."""

    constitutional_hash: str = Field(
        default="cdd01ef066bc6cf2", description="Constitutional compliance hash"
    )

    @field_validator("constitutional_hash")
    @classmethod
    def validate_constitutional_hash(cls, v):
        if v != "cdd01ef066bc6cf2":
            raise ValueError("Invalid constitutional hash")
        return v


# Request models
class SemanticSearchRequest(BaseModel):
    """Request model for semantic search."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    limit: int = Field(
        default=10, ge=1, le=100, description="Maximum number of results"
    )
    min_confidence: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum confidence score"
    )
    symbol_types: list[SymbolType] | None = Field(
        default=None, description="Filter by symbol types"
    )
    file_paths: list[str] | None = Field(
        default=None, description="Filter by file paths"
    )
    include_embeddings: bool = Field(
        default=False, description="Include embedding vectors in response"
    )


class AnalysisRequest(ConstitutionalBaseModel):
    """Request model for triggering code analysis."""

    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    file_paths: list[str] | None = Field(
        default=None, description="Specific file paths to analyze"
    )
    force_reanalysis: bool = Field(
        default=False, description="Force re-analysis of existing files"
    )
    include_embeddings: bool = Field(
        default=True, description="Generate embeddings during analysis"
    )
    include_dependencies: bool = Field(
        default=True, description="Extract dependencies during analysis"
    )


class ContextEnrichmentRequest(ConstitutionalBaseModel):
    """Request model for context enrichment."""

    symbol_ids: list[UUID] = Field(..., description="Symbol IDs to enrich with context")
    context_types: list[ContextType] | None = Field(
        default=None, description="Types of context to retrieve"
    )
    min_confidence: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum confidence score"
    )


# Response models
class CodeSymbol(ConstitutionalBaseModel):
    """Code symbol response model."""

    id: UUID = Field(..., description="Unique symbol identifier")
    file_path: str = Field(..., description="File path containing the symbol")
    symbol_name: str = Field(..., description="Name of the symbol")
    symbol_type: SymbolType = Field(..., description="Type of the symbol")
    start_line: int = Field(..., ge=1, description="Starting line number")
    end_line: int = Field(..., ge=1, description="Ending line number")
    signature: str | None = Field(default=None, description="Symbol signature")
    docstring: str | None = Field(default=None, description="Symbol documentation")
    language: str = Field(..., description="Programming language")
    complexity_score: int | None = Field(
        default=None, ge=0, description="Complexity score"
    )
    is_public: bool = Field(
        default=True, description="Whether symbol is publicly accessible"
    )
    is_deprecated: bool = Field(
        default=False, description="Whether symbol is deprecated"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class CodeDependency(ConstitutionalBaseModel):
    """Code dependency response model."""

    id: UUID = Field(..., description="Unique dependency identifier")
    source_symbol_id: UUID = Field(..., description="Source symbol ID")
    target_symbol_id: UUID | None = Field(
        default=None, description="Target symbol ID (if internal)"
    )
    dependency_type: DependencyType = Field(..., description="Type of dependency")
    target_name: str | None = Field(
        default=None, description="Target name (if external)"
    )
    target_module: str | None = Field(
        default=None, description="Target module (if external)"
    )
    is_external: bool = Field(
        default=False, description="Whether dependency is external"
    )
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    created_at: datetime = Field(..., description="Creation timestamp")


class CodeEmbedding(ConstitutionalBaseModel):
    """Code embedding response model."""

    id: UUID = Field(..., description="Unique embedding identifier")
    symbol_id: UUID = Field(..., description="Associated symbol ID")
    embedding: list[float] | None = Field(default=None, description="Embedding vector")
    embedding_model: str = Field(..., description="Model used for embedding")
    embedding_version: str = Field(..., description="Model version")
    chunk_text: str = Field(..., description="Text that was embedded")
    chunk_type: str = Field(..., description="Type of text chunk")
    created_at: datetime = Field(..., description="Creation timestamp")


class SemanticSearchResult(ConstitutionalBaseModel):
    """Semantic search result."""

    symbol: CodeSymbol = Field(..., description="Matching code symbol")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Search confidence score"
    )
    embedding: CodeEmbedding | None = Field(
        default=None, description="Associated embedding"
    )
    context_snippet: str | None = Field(
        default=None, description="Relevant context snippet"
    )


class SemanticSearchResponse(ConstitutionalBaseModel):
    """Response model for semantic search."""

    query: str = Field(..., description="Original search query")
    results: list[SemanticSearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., ge=0, description="Total number of results found")
    search_time_ms: float = Field(
        ..., ge=0, description="Search execution time in milliseconds"
    )
    cache_hit: bool = Field(default=False, description="Whether result was cached")


class AnalysisJob(ConstitutionalBaseModel):
    """Analysis job response model."""

    id: UUID = Field(..., description="Unique job identifier")
    job_type: str = Field(..., description="Type of analysis job")
    status: str = Field(..., description="Current job status")
    file_path: str | None = Field(default=None, description="File path being analyzed")
    progress_percentage: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Job progress percentage"
    )
    symbols_found: int = Field(default=0, ge=0, description="Number of symbols found")
    symbols_updated: int = Field(
        default=0, ge=0, description="Number of symbols updated"
    )
    dependencies_created: int = Field(
        default=0, ge=0, description="Number of dependencies created"
    )
    embeddings_created: int = Field(
        default=0, ge=0, description="Number of embeddings created"
    )
    processing_time_ms: int | None = Field(
        default=None, ge=0, description="Processing time in milliseconds"
    )
    error_message: str | None = Field(
        default=None, description="Error message if job failed"
    )
    started_at: datetime | None = Field(default=None, description="Job start timestamp")
    completed_at: datetime | None = Field(
        default=None, description="Job completion timestamp"
    )
    created_at: datetime = Field(..., description="Job creation timestamp")


class AnalysisResponse(ConstitutionalBaseModel):
    """Response model for analysis trigger."""

    job: AnalysisJob = Field(..., description="Created analysis job")
    message: str = Field(..., description="Response message")


class HealthCheck(ConstitutionalBaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service health status")
    service: str = Field(
        default="acgs-code-analysis-engine", description="Service name"
    )
    version: str = Field(default="1.0.0", description="Service version")
    checks: dict[str, str] = Field(
        default_factory=dict, description="Individual health checks"
    )
    uptime_seconds: int = Field(
        default=0, ge=0, description="Service uptime in seconds"
    )
    last_analysis_job: datetime | None = Field(
        default=None, description="Last analysis job timestamp"
    )


class ErrorResponse(ConstitutionalBaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(
        default=None, description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )
    request_id: str | None = Field(default=None, description="Request ID for tracking")


class ContextLink(ConstitutionalBaseModel):
    """Context link response model."""

    id: UUID = Field(..., description="Unique link identifier")
    code_symbol_id: UUID = Field(..., description="Code symbol ID")
    context_id: str = Field(..., description="Context ID from Context Service")
    context_type: ContextType = Field(..., description="Type of context")
    relationship_type: str = Field(..., description="Type of relationship")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ContextEnrichmentResponse(ConstitutionalBaseModel):
    """Response model for context enrichment."""

    symbol_ids: list[UUID] = Field(..., description="Processed symbol IDs")
    context_links: list[ContextLink] = Field(..., description="Created context links")
    total_links_created: int = Field(
        ..., ge=0, description="Total number of links created"
    )
    processing_time_ms: float = Field(
        ..., ge=0, description="Processing time in milliseconds"
    )
