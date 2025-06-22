"""
Comprehensive Unit Tests for Unified Response Format

Tests all functionality of the unified response system including:
- Response builder creation and configuration
- Success and error response generation
- Pagination metadata handling
- Response validation and format compliance
- Service-specific response builders
- Legacy response migration
- Performance and serialization

Target: >90% test coverage for unified response module
"""

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from fastapi import Request

from services.shared.response.unified_response import (
    UnifiedResponse,
    ResponseBuilder,
    PaginationMetadata,
    ResponseMetadata,
    ResponseStatus,
    UnifiedJSONResponse,
    create_auth_response_builder,
    create_ac_response_builder,
    create_integrity_response_builder,
    create_fv_response_builder,
    create_gs_response_builder,
    create_pgc_response_builder,
    create_ec_response_builder,
    create_dgm_response_builder,
    get_response_builder,
    validate_response_format,
    migrate_legacy_response,
    create_legacy_response
)


class TestPaginationMetadata:
    """Test pagination metadata functionality."""
    
    def test_pagination_metadata_creation(self):
        """Test pagination metadata creation with calculated fields."""
        pagination = PaginationMetadata.create(page=2, limit=10, total=45)
        
        assert pagination.page == 2
        assert pagination.limit == 10
        assert pagination.total == 45
        assert pagination.has_next is True  # Page 2 of 5 pages
        assert pagination.has_previous is True
    
    def test_pagination_first_page(self):
        """Test pagination metadata for first page."""
        pagination = PaginationMetadata.create(page=1, limit=10, total=25)
        
        assert pagination.page == 1
        assert pagination.has_next is True  # Page 1 of 3 pages
        assert pagination.has_previous is False
    
    def test_pagination_last_page(self):
        """Test pagination metadata for last page."""
        pagination = PaginationMetadata.create(page=3, limit=10, total=25)
        
        assert pagination.page == 3
        assert pagination.has_next is False  # Last page
        assert pagination.has_previous is True
    
    def test_pagination_single_page(self):
        """Test pagination metadata for single page."""
        pagination = PaginationMetadata.create(page=1, limit=10, total=5)
        
        assert pagination.page == 1
        assert pagination.has_next is False
        assert pagination.has_previous is False
    
    def test_pagination_empty_results(self):
        """Test pagination metadata for empty results."""
        pagination = PaginationMetadata.create(page=1, limit=10, total=0)
        
        assert pagination.page == 1
        assert pagination.total == 0
        assert pagination.has_next is False
        assert pagination.has_previous is False


class TestResponseMetadata:
    """Test response metadata functionality."""
    
    def test_response_metadata_creation(self):
        """Test response metadata creation."""
        metadata = ResponseMetadata.create(
            service="test-service",
            version="1.0.0",
            request_id="test-request-id"
        )
        
        assert metadata.service == "test-service"
        assert metadata.version == "1.0.0"
        assert metadata.request_id == "test-request-id"
        assert metadata.timestamp is not None
        
        # Validate timestamp format
        datetime.fromisoformat(metadata.timestamp.replace('Z', '+00:00'))
    
    def test_response_metadata_auto_request_id(self):
        """Test response metadata with auto-generated request ID."""
        metadata = ResponseMetadata.create(service="test-service")
        
        assert metadata.request_id is not None
        assert len(metadata.request_id) == 36  # UUID format
        
        # Validate UUID format
        uuid.UUID(metadata.request_id)


class TestResponseBuilder:
    """Test response builder functionality."""
    
    @pytest.fixture
    def response_builder(self):
        """Create response builder for testing."""
        return ResponseBuilder("test-service", "1.0.0")
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request for testing."""
        request = Mock(spec=Request)
        request.headers = {"X-Request-ID": "test-request-id"}
        request.url.path = "/api/v1/test"
        return request
    
    def test_response_builder_initialization(self, response_builder):
        """Test response builder initialization."""
        assert response_builder.service_name == "test-service"
        assert response_builder.version == "1.0.0"
        assert response_builder.request_id is None
        assert response_builder.execution_start_time is None
    
    def test_set_request_context(self, response_builder, mock_request):
        """Test setting request context."""
        builder = response_builder.set_request_context(mock_request)
        
        assert builder.request_id == "test-request-id"
        assert builder.execution_start_time is not None
        assert isinstance(builder.execution_start_time, float)
    
    def test_success_response(self, response_builder):
        """Test successful response creation."""
        test_data = {"key": "value", "number": 42}
        response = response_builder.success(
            data=test_data,
            message="Test successful"
        )
        
        assert isinstance(response, UnifiedResponse)
        assert response.success is True
        assert response.data == test_data
        assert response.message == "Test successful"
        assert response.metadata.service == "test-service"
        assert response.metadata.version == "1.0.0"
        assert response.pagination is None
    
    def test_error_response(self, response_builder):
        """Test error response creation."""
        error_data = {"field": "username", "issue": "required"}
        response = response_builder.error(
            message="Validation failed",
            data=error_data,
            error_code="VALIDATION_ERROR"
        )
        
        assert isinstance(response, UnifiedResponse)
        assert response.success is False
        assert response.data["error_code"] == "VALIDATION_ERROR"
        assert response.data["details"] == error_data
        assert response.message == "Validation failed"
        assert response.metadata.service == "test-service"
    
    def test_paginated_success_response(self, response_builder):
        """Test paginated successful response creation."""
        test_data = [{"id": 1}, {"id": 2}, {"id": 3}]
        response = response_builder.paginated_success(
            data=test_data,
            page=1,
            limit=10,
            total=25,
            message="Paginated results"
        )
        
        assert isinstance(response, UnifiedResponse)
        assert response.success is True
        assert response.data == test_data
        assert response.message == "Paginated results"
        assert response.pagination is not None
        assert response.pagination.page == 1
        assert response.pagination.limit == 10
        assert response.pagination.total == 25
        assert response.pagination.has_next is True
    
    def test_execution_time_tracking(self, response_builder, mock_request):
        """Test execution time tracking."""
        import time
        
        response_builder.set_request_context(mock_request)
        time.sleep(0.01)  # Small delay to test timing
        
        response = response_builder.success(data={"test": "data"})
        
        assert response.metadata.execution_time_ms is not None
        assert response.metadata.execution_time_ms > 0
        assert response.metadata.execution_time_ms < 1000  # Should be less than 1 second


class TestServiceSpecificBuilders:
    """Test service-specific response builders."""
    
    def test_auth_response_builder(self):
        """Test authentication service response builder."""
        builder = create_auth_response_builder()
        assert builder.service_name == "authentication-service"
        assert builder.version == "2.1.0"
    
    def test_ac_response_builder(self):
        """Test constitutional AI service response builder."""
        builder = create_ac_response_builder()
        assert builder.service_name == "constitutional-ai-service"
        assert builder.version == "2.1.0"
    
    def test_integrity_response_builder(self):
        """Test integrity service response builder."""
        builder = create_integrity_response_builder()
        assert builder.service_name == "integrity-service"
        assert builder.version == "2.0.0"
    
    def test_fv_response_builder(self):
        """Test formal verification service response builder."""
        builder = create_fv_response_builder()
        assert builder.service_name == "formal-verification-service"
        assert builder.version == "1.5.0"
    
    def test_gs_response_builder(self):
        """Test governance synthesis service response builder."""
        builder = create_gs_response_builder()
        assert builder.service_name == "governance-synthesis-service"
        assert builder.version == "2.2.0"
    
    def test_pgc_response_builder(self):
        """Test policy governance service response builder."""
        builder = create_pgc_response_builder()
        assert builder.service_name == "policy-governance-service"
        assert builder.version == "2.0.0"
    
    def test_ec_response_builder(self):
        """Test evolutionary computation service response builder."""
        builder = create_ec_response_builder()
        assert builder.service_name == "evolutionary-computation-service"
        assert builder.version == "1.8.0"
    
    def test_dgm_response_builder(self):
        """Test Darwin Gödel Machine service response builder."""
        builder = create_dgm_response_builder()
        assert builder.service_name == "darwin-godel-machine-service"
        assert builder.version == "1.0.0"


class TestUnifiedJSONResponse:
    """Test unified JSON response functionality."""
    
    def test_unified_json_response_rendering(self):
        """Test JSON response rendering with UnifiedResponse."""
        builder = ResponseBuilder("test-service")
        unified_response = builder.success(data={"test": "data"})
        
        json_response = UnifiedJSONResponse(content=unified_response)
        rendered = json_response.render(unified_response)
        
        assert isinstance(rendered, bytes)
        
        # Parse and validate JSON
        parsed = json.loads(rendered)
        assert parsed["success"] is True
        assert parsed["data"]["test"] == "data"
        assert "metadata" in parsed
    
    def test_json_response_with_dict(self):
        """Test JSON response rendering with dictionary."""
        test_data = {"success": True, "data": {"key": "value"}}
        
        json_response = UnifiedJSONResponse(content=test_data)
        rendered = json_response.render(test_data)
        
        assert isinstance(rendered, bytes)
        parsed = json.loads(rendered)
        assert parsed == test_data


class TestResponseValidation:
    """Test response validation functionality."""
    
    def test_valid_response_format(self):
        """Test validation of valid response format."""
        valid_response = {
            "success": True,
            "data": {"key": "value"},
            "message": "Success",
            "metadata": {
                "timestamp": "2025-06-22T10:00:00Z",
                "request_id": "test-id",
                "version": "1.0.0",
                "service": "test-service"
            }
        }
        
        assert validate_response_format(valid_response) is True
    
    def test_valid_response_with_pagination(self):
        """Test validation of valid response with pagination."""
        valid_response = {
            "success": True,
            "data": [{"id": 1}],
            "message": "Success",
            "metadata": {
                "timestamp": "2025-06-22T10:00:00Z",
                "request_id": "test-id",
                "version": "1.0.0",
                "service": "test-service"
            },
            "pagination": {
                "page": 1,
                "limit": 10,
                "total": 25,
                "has_next": True,
                "has_previous": False
            }
        }
        
        assert validate_response_format(valid_response) is True
    
    def test_invalid_response_missing_fields(self):
        """Test validation of invalid response missing required fields."""
        invalid_response = {
            "success": True,
            "data": {"key": "value"}
            # Missing message and metadata
        }
        
        assert validate_response_format(invalid_response) is False
    
    def test_invalid_response_missing_metadata_fields(self):
        """Test validation of invalid response missing metadata fields."""
        invalid_response = {
            "success": True,
            "data": {"key": "value"},
            "message": "Success",
            "metadata": {
                "timestamp": "2025-06-22T10:00:00Z"
                # Missing request_id, version, service
            }
        }
        
        assert validate_response_format(invalid_response) is False
    
    def test_invalid_response_incomplete_pagination(self):
        """Test validation of invalid response with incomplete pagination."""
        invalid_response = {
            "success": True,
            "data": [{"id": 1}],
            "message": "Success",
            "metadata": {
                "timestamp": "2025-06-22T10:00:00Z",
                "request_id": "test-id",
                "version": "1.0.0",
                "service": "test-service"
            },
            "pagination": {
                "page": 1,
                "limit": 10
                # Missing total, has_next, has_previous
            }
        }
        
        assert validate_response_format(invalid_response) is False


class TestLegacyResponseMigration:
    """Test legacy response migration functionality."""
    
    def test_create_legacy_response(self):
        """Test creation of legacy response format."""
        test_data = {"key": "value"}
        legacy_response = create_legacy_response(test_data, "success")
        
        assert legacy_response["status"] == "success"
        assert legacy_response["data"] == test_data
        assert "timestamp" in legacy_response
    
    def test_migrate_legacy_success_response(self):
        """Test migration of legacy success response."""
        legacy_response = {
            "status": "success",
            "data": {"key": "value"},
            "message": "Operation successful"
        }
        
        unified_response = migrate_legacy_response(legacy_response, "test-service")
        
        assert isinstance(unified_response, UnifiedResponse)
        assert unified_response.success is True
        assert unified_response.data == {"key": "value"}
        assert unified_response.message == "Operation successful"
        assert unified_response.metadata.service == "test-service"
    
    def test_migrate_legacy_error_response(self):
        """Test migration of legacy error response."""
        legacy_response = {
            "status": "error",
            "data": {"error_details": "Something went wrong"},
            "message": "Operation failed"
        }
        
        unified_response = migrate_legacy_response(legacy_response, "test-service")
        
        assert isinstance(unified_response, UnifiedResponse)
        assert unified_response.success is False
        assert unified_response.data == {"error_details": "Something went wrong"}
        assert unified_response.message == "Operation failed"
        assert unified_response.metadata.service == "test-service"


@pytest.mark.asyncio
class TestFastAPIDependency:
    """Test FastAPI dependency functionality."""
    
    async def test_get_response_builder_with_service_header(self):
        """Test getting response builder with service header."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-Service-Name": "custom-service"}
        mock_request.url.path = "/api/v1/test"
        
        builder = await get_response_builder(mock_request)
        
        assert isinstance(builder, ResponseBuilder)
        assert builder.service_name == "custom-service"
        assert builder.request_id is not None
    
    async def test_get_response_builder_with_path_mapping(self):
        """Test getting response builder with path-based service detection."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.url.path = "/api/v1/constitutional/principles"
        
        builder = await get_response_builder(mock_request)
        
        assert isinstance(builder, ResponseBuilder)
        assert builder.service_name == "constitutional-ai-service"
    
    async def test_get_response_builder_unknown_service(self):
        """Test getting response builder for unknown service."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.url.path = "/unknown/path"
        
        builder = await get_response_builder(mock_request)
        
        assert isinstance(builder, ResponseBuilder)
        assert builder.service_name == "unknown-service"


class TestPerformanceAndSerialization:
    """Test performance and serialization aspects."""
    
    def test_large_data_serialization(self):
        """Test serialization of large data sets."""
        large_data = [{"id": i, "data": f"item_{i}"} for i in range(1000)]
        
        builder = ResponseBuilder("test-service")
        response = builder.success(data=large_data)
        
        json_response = UnifiedJSONResponse(content=response)
        rendered = json_response.render(response)
        
        assert isinstance(rendered, bytes)
        assert len(rendered) > 0
        
        # Verify it can be parsed back
        parsed = json.loads(rendered)
        assert len(parsed["data"]) == 1000
    
    def test_nested_data_serialization(self):
        """Test serialization of deeply nested data."""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": "deep_value",
                        "list": [1, 2, 3, {"nested": True}]
                    }
                }
            }
        }
        
        builder = ResponseBuilder("test-service")
        response = builder.success(data=nested_data)
        
        json_response = UnifiedJSONResponse(content=response)
        rendered = json_response.render(response)
        
        parsed = json.loads(rendered)
        assert parsed["data"]["level1"]["level2"]["level3"]["data"] == "deep_value"
    
    def test_datetime_serialization(self):
        """Test datetime serialization in responses."""
        test_data = {
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        builder = ResponseBuilder("test-service")
        response = builder.success(data=test_data)
        
        json_response = UnifiedJSONResponse(content=response)
        rendered = json_response.render(response)
        
        parsed = json.loads(rendered)
        
        # Verify datetime fields are properly serialized as ISO strings
        assert isinstance(parsed["data"]["created_at"], str)
        assert isinstance(parsed["data"]["updated_at"], str)
        
        # Verify they can be parsed back to datetime
        datetime.fromisoformat(parsed["data"]["created_at"].replace('Z', '+00:00'))
        datetime.fromisoformat(parsed["data"]["updated_at"].replace('Z', '+00:00'))


# Integration test for complete workflow
@pytest.mark.integration
class TestUnifiedResponseIntegration:
    """Integration tests for unified response system."""
    
    def test_complete_response_workflow(self):
        """Test complete response creation and validation workflow."""
        # Create response builder
        builder = ResponseBuilder("integration-test-service", "1.0.0")
        
        # Create successful response
        test_data = {"users": [{"id": 1, "name": "Test User"}]}
        response = builder.success(data=test_data, message="Users retrieved")
        
        # Convert to dictionary
        response_dict = response.dict()
        
        # Validate format
        assert validate_response_format(response_dict) is True
        
        # Serialize to JSON
        json_response = UnifiedJSONResponse(content=response)
        rendered = json_response.render(response)
        
        # Parse back and validate
        parsed = json.loads(rendered)
        assert parsed["success"] is True
        assert parsed["data"]["users"][0]["name"] == "Test User"
        assert parsed["metadata"]["service"] == "integration-test-service"
    
    def test_error_response_workflow(self):
        """Test error response creation and validation workflow."""
        builder = ResponseBuilder("integration-test-service", "1.0.0")
        
        # Create error response
        error_response = builder.error(
            message="User not found",
            data={"user_id": 123},
            error_code="USER_NOT_FOUND"
        )
        
        # Convert to dictionary
        response_dict = error_response.dict()
        
        # Validate format
        assert validate_response_format(response_dict) is True
        
        # Verify error structure
        assert response_dict["success"] is False
        assert response_dict["data"]["error_code"] == "USER_NOT_FOUND"
        assert response_dict["data"]["details"]["user_id"] == 123
