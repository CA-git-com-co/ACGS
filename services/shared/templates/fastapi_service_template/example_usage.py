"""
ACGS FastAPI Service Template - Example Usage
Constitutional Hash: cdd01ef066bc6cf2

This file demonstrates how to use the FastAPI service template to create
a new ACGS service with constitutional compliance and multi-tenant support.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Field, HTTPException, Query, status
from pydantic import validator
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings

# Import template components
from .main import app, health_checker
from .models import BaseACGSModel
from .schemas import (
    ConstitutionalBaseModel,
    FilterParams,
    PaginatedResponse,
    PaginationMeta,
    PaginationParams,
    SuccessResponse,
    TenantAwareModel,
)

# Import multi-tenant components (if available)
try:
    from services.shared.middleware.simple_tenant_middleware import (
        SimpleTenantContext,
        SimpleTenantService,
        get_tenant_context,
        get_tenant_db,
    )

    MULTI_TENANT_AVAILABLE = True
except ImportError:
    MULTI_TENANT_AVAILABLE = False

    def get_tenant_context():
        return None

    def get_tenant_db():
        return None


# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Get service configuration
settings = get_settings()

# Example: Document Management Service
# This demonstrates a complete service implementation using the template

# ============================================================================
# Database Models
# ============================================================================


class Document(BaseACGSModel):
    """
    Example document model demonstrating template usage.

    This model inherits all standard ACGS functionality:
    - Constitutional compliance (constitutional_hash field)
    - Multi-tenant support (tenant_id field with RLS)
    - Audit trails (created_at, updated_at, created_by_user_id, etc.)
    - Status tracking (status, is_active fields)
    """

    __tablename__ = "documents"

    # Document-specific fields
    title = Column(String(255), nullable=False, index=True, comment="Document title")

    content = Column(Text, nullable=True, comment="Document content")

    document_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of document (policy, procedure, analysis, etc.)",
    )

    author = Column(String(255), nullable=True, comment="Document author")

    version = Column(
        Integer, nullable=False, default=1, comment="Document version number"
    )

    word_count = Column(
        Integer, nullable=True, comment="Number of words in the document"
    )

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', tenant_id={self.tenant_id})>"


class DocumentCategory(BaseACGSModel):
    """Example category model for document organization."""

    __tablename__ = "document_categories"

    name = Column(String(255), nullable=False, index=True, comment="Category name")

    description = Column(Text, nullable=True, comment="Category description")

    parent_category_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="Parent category for hierarchical organization",
    )


# ============================================================================
# Pydantic Schemas
# ============================================================================


class DocumentCreateRequest(TenantAwareModel):
    """Request schema for creating documents."""

    title: str = Field(
        min_length=1,
        max_length=255,
        description="Document title",
        example="Constitutional Analysis Report",
    )

    content: str | None = Field(None, max_length=50000, description="Document content")

    document_type: str = Field(description="Type of document", example="analysis")

    author: str | None = Field(None, max_length=255, description="Document author")

    @validator("title")
    def validate_title(self, v):
        """Validate title meets constitutional requirements."""
        if len(v.strip()) < 3:
            raise ValueError(
                "Title must be at least 3 characters for constitutional compliance"
            )
        return v.strip()


class DocumentUpdateRequest(ConstitutionalBaseModel):
    """Request schema for updating documents."""

    title: str | None = Field(
        None, min_length=1, max_length=255, description="Document title"
    )

    content: str | None = Field(None, max_length=50000, description="Document content")

    document_type: str | None = Field(None, description="Type of document")

    author: str | None = Field(None, max_length=255, description="Document author")


class DocumentResponse(TenantAwareModel):
    """Response schema for document data."""

    id: uuid.UUID = Field(description="Document unique identifier")
    title: str = Field(description="Document title")
    content: str | None = Field(None, description="Document content")
    document_type: str = Field(description="Document type")
    author: str | None = Field(None, description="Document author")
    version: int = Field(description="Document version")
    word_count: int | None = Field(None, description="Word count")
    status: str = Field(description="Document status")
    is_active: bool = Field(description="Whether document is active")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    @validator("content")
    def sanitize_content(self, v):
        """Sanitize content for constitutional compliance."""
        if v and len(v) > 1000:  # Truncate for API response
            return v[:1000] + "..."
        return v


class DocumentListResponse(ConstitutionalBaseModel):
    """Response schema for document listings (without full content)."""

    id: uuid.UUID
    title: str
    document_type: str
    author: str | None
    version: int
    word_count: int | None
    status: str
    created_at: datetime
    updated_at: datetime


# ============================================================================
# API Routes
# ============================================================================

# Create API router for document management
documents_router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Document Management"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)


@documents_router.post(
    "",
    response_model=SuccessResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Document",
    description="Create a new document with constitutional compliance validation",
)
async def create_document(
    request: DocumentCreateRequest,
    tenant_context: SimpleTenantContext = (
        Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
    ),
    db: AsyncSession = Depends(get_tenant_db) if MULTI_TENANT_AVAILABLE else None,
):
    """
    Create a new document with constitutional compliance validation.

    This endpoint demonstrates:
    - Constitutional compliance validation
    - Multi-tenant support with automatic tenant assignment
    - Comprehensive error handling
    - Audit trail creation
    """
    try:
        # Validate constitutional compliance
        if len(request.title) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document title must meet constitutional requirements (minimum 3 characters)",
            )

        # Calculate word count if content provided
        word_count = len(request.content.split()) if request.content else 0

        # Create document (in real implementation, this would save to database)
        document_id = uuid.uuid4()

        # Mock document creation for demonstration
        document_data = {
            "id": document_id,
            "tenant_id": tenant_context.tenant_id if tenant_context else uuid.uuid4(),
            "title": request.title,
            "content": request.content,
            "document_type": request.document_type,
            "author": (
                request.author or f"User {tenant_context.user_id}"
                if tenant_context
                else "Anonymous"
            ),
            "version": 1,
            "word_count": word_count,
            "status": "draft",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        # In real implementation:
        # document = Document(**document_data)
        # db.add(document)
        # await db.commit()
        # await db.refresh(document)

        response_data = DocumentResponse(**document_data)

        # Log audit trail
        if MULTI_TENANT_AVAILABLE and db:
            tenant_service = SimpleTenantService(db)
            await tenant_service.log_access(
                "document_create", f"document:{document_id}", "success"
            )

        return SuccessResponse(
            message="Document created successfully",
            data=response_data,
            service_name=settings.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log error for debugging
        if MULTI_TENANT_AVAILABLE and db:
            tenant_service = SimpleTenantService(db)
            await tenant_service.log_access("document_create", "document", "error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {e!s}",
        )


@documents_router.get(
    "",
    response_model=PaginatedResponse[DocumentListResponse],
    summary="List Documents",
    description="Retrieve a paginated list of documents with filtering options",
)
async def list_documents(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    document_type: str | None = Query(None, description="Filter by document type"),
    tenant_context: SimpleTenantContext = (
        Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
    ),
    db: AsyncSession = Depends(get_tenant_db) if MULTI_TENANT_AVAILABLE else None,
):
    """
    List documents with pagination and filtering.

    This endpoint demonstrates:
    - Pagination with metadata
    - Filtering capabilities
    - Multi-tenant automatic filtering
    - Constitutional compliance in responses
    """
    try:
        # In real implementation, this would query the database with tenant filtering
        # Example query:
        # query = select(Document).where(Document.tenant_id == tenant_context.tenant_id)
        # if document_type:
        #     query = query.where(Document.document_type == document_type)
        # if filters.search:
        #     query = query.where(Document.title.ilike(f"%{filters.search}%"))
        #
        # documents = await db.execute(query.offset(pagination.offset).limit(pagination.page_size))
        # total_count = await db.scalar(select(func.count(Document.id)).where(Document.tenant_id == tenant_context.tenant_id))

        # Mock data for demonstration
        mock_documents = [
            DocumentListResponse(
                id=uuid.uuid4(),
                title=f"Document {i}",
                document_type=document_type or "analysis",
                author=f"Author {i}",
                version=1,
                word_count=500 + i * 10,
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            for i in range(1, pagination.page_size + 1)
        ]

        total_items = 100  # Mock total count
        total_pages = (total_items + pagination.page_size - 1) // pagination.page_size

        pagination_meta = PaginationMeta(
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_previous=pagination.page > 1,
        )

        return PaginatedResponse(
            status="success",
            message="Documents retrieved successfully",
            data=mock_documents,
            pagination=pagination_meta,
            service_name=settings.name,
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {e!s}",
        )


@documents_router.get(
    "/{document_id}",
    response_model=SuccessResponse[DocumentResponse],
    summary="Get Document",
    description="Retrieve a specific document by ID",
)
async def get_document(
    document_id: uuid.UUID,
    tenant_context: SimpleTenantContext = (
        Depends(get_tenant_context) if MULTI_TENANT_AVAILABLE else None
    ),
    db: AsyncSession = Depends(get_tenant_db) if MULTI_TENANT_AVAILABLE else None,
):
    """
    Get a specific document by ID.

    This endpoint demonstrates:
    - Individual resource retrieval
    - Tenant isolation (automatic filtering)
    - Constitutional compliance validation
    - Proper error handling for not found cases
    """
    try:
        # In real implementation:
        # document = await db.get(Document, document_id)
        # if not document or document.tenant_id != tenant_context.tenant_id:
        #     raise HTTPException(status_code=404, detail="Document not found")

        # Mock document for demonstration
        document_data = {
            "id": document_id,
            "tenant_id": tenant_context.tenant_id if tenant_context else uuid.uuid4(),
            "title": "Example Document",
            "content": "This is an example document demonstrating the ACGS FastAPI template...",
            "document_type": "example",
            "author": "Template Author",
            "version": 1,
            "word_count": 250,
            "status": "active",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

        document = DocumentResponse(**document_data)

        return SuccessResponse(
            message="Document retrieved successfully",
            data=document,
            service_name=settings.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {e!s}",
        )


# ============================================================================
# Health Check Integration
# ============================================================================


async def check_document_service_health() -> bool:
    """Custom health check for document service components."""
    try:
        # Check if we can perform basic operations
        # In real implementation, this might check database connectivity,
        # external service availability, etc.

        # Mock health check
        return True

    except Exception:
        return False


# Register the custom health check
health_checker.register_component("document_service", check_document_service_health)


# ============================================================================
# Service Integration
# ============================================================================

# Add the document router to the main application
app.include_router(documents_router)


# Example of how to add custom startup/shutdown procedures
@app.on_event("startup")
async def document_service_startup():
    """Custom startup procedures for document service."""

    # In real implementation, you might:
    # - Initialize document storage systems
    # - Set up document processing pipelines
    # - Validate document templates
    # - Initialize search indexing


@app.on_event("shutdown")
async def document_service_shutdown():
    """Custom shutdown procedures for document service."""

    # In real implementation, you might:
    # - Close document processing pipelines
    # - Flush pending document operations
    # - Clean up temporary files


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    """
    Example of how to run the service with custom configuration.

    This demonstrates how to use the template for a complete service
    implementation with constitutional compliance and multi-tenant support.
    """
    import uvicorn

    # Get service configuration
    config = get_settings()

    # Run the service
    uvicorn.run(
        "example_usage:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level=config.monitoring.log_level.lower(),
    )


# ============================================================================
# Testing Examples
# ============================================================================

# Example test cases for the document service
from fastapi.testclient import TestClient


def test_document_creation():
    """Example test for document creation endpoint."""
    client = TestClient(app)

    response = client.post(
        "/api/v1/documents",
        json={
            "title": "Test Document",
            "content": "This is a test document",
            "document_type": "test",
            "tenant_id": str(uuid.uuid4()),
        },
        headers={"Authorization": "Bearer mock-jwt-token"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
    assert data["data"]["title"] == "Test Document"


def test_constitutional_compliance():
    """Example test for constitutional compliance validation."""
    client = TestClient(app)

    # Test with title too short (should fail constitutional validation)
    response = client.post(
        "/api/v1/documents",
        json={
            "title": "X",  # Too short
            "document_type": "test",
            "tenant_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 400
    assert "constitutional requirements" in response.json()["detail"]


def test_health_check():
    """Example test for health check endpoint."""
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["constitutional_hash"] == CONSTITUTIONAL_HASH
    assert data["service"] == settings.name
    assert "document_service" in data["components"]
