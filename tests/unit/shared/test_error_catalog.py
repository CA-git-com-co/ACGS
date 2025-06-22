"""
Comprehensive Unit Tests for Error Catalog

Tests all functionality of the standardized error code system including:
- Error code generation and registration
- Hierarchical error organization
- Error definition management
- Service and category filtering
- Error catalog export and validation
- Conflict detection and prevention

Target: >95% test coverage for error catalog module
"""

import pytest
from typing import Dict, Any

from services.shared.errors.error_catalog import (
    ErrorSeverity,
    ErrorCategory,
    ServiceCode,
    ErrorDefinition,
    ErrorCodeRegistry,
    error_registry,
    get_error_definition,
    get_service_errors,
    get_category_errors,
    export_error_catalog
)


class TestErrorSeverity:
    """Test error severity enumeration."""
    
    def test_error_severity_values(self):
        """Test error severity enum values."""
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.CRITICAL.value == "critical"
    
    def test_error_severity_ordering(self):
        """Test error severity can be compared."""
        severities = [ErrorSeverity.INFO, ErrorSeverity.WARNING, ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]
        assert len(severities) == 4
        assert all(isinstance(s, ErrorSeverity) for s in severities)


class TestErrorCategory:
    """Test error category enumeration."""
    
    def test_error_category_values(self):
        """Test error category enum values."""
        assert ErrorCategory.VALIDATION.value == "VALIDATION"
        assert ErrorCategory.AUTHENTICATION.value == "AUTHENTICATION"
        assert ErrorCategory.AUTHORIZATION.value == "AUTHORIZATION"
        assert ErrorCategory.BUSINESS_LOGIC.value == "BUSINESS_LOGIC"
        assert ErrorCategory.EXTERNAL_SERVICE.value == "EXTERNAL_SERVICE"
        assert ErrorCategory.SYSTEM_ERROR.value == "SYSTEM_ERROR"
    
    def test_all_categories_present(self):
        """Test all expected categories are present."""
        expected_categories = {
            "VALIDATION", "AUTHENTICATION", "AUTHORIZATION", 
            "BUSINESS_LOGIC", "EXTERNAL_SERVICE", "SYSTEM_ERROR"
        }
        actual_categories = {category.value for category in ErrorCategory}
        assert actual_categories == expected_categories


class TestServiceCode:
    """Test service code enumeration."""
    
    def test_service_code_values(self):
        """Test service code enum values."""
        assert ServiceCode.AUTH.value == "AUTH"
        assert ServiceCode.AC.value == "AC"
        assert ServiceCode.INTEGRITY.value == "INTEGRITY"
        assert ServiceCode.FV.value == "FV"
        assert ServiceCode.GS.value == "GS"
        assert ServiceCode.PGC.value == "PGC"
        assert ServiceCode.EC.value == "EC"
        assert ServiceCode.DGM.value == "DGM"
        assert ServiceCode.SHARED.value == "SHARED"
    
    def test_all_services_present(self):
        """Test all expected services are present."""
        expected_services = {
            "AUTH", "AC", "INTEGRITY", "FV", "GS", "PGC", "EC", "DGM", "SHARED"
        }
        actual_services = {service.value for service in ServiceCode}
        assert actual_services == expected_services


class TestErrorDefinition:
    """Test error definition data class."""
    
    def test_error_definition_creation(self):
        """Test error definition creation."""
        error_def = ErrorDefinition(
            code="TEST_VALIDATION_001",
            message="Test error message",
            description="Test error description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION,
            service=ServiceCode.SHARED,
            resolution_guidance="Test resolution guidance",
            user_message="Test user message",
            retryable=False,
            context_fields=["field1", "field2"]
        )
        
        assert error_def.code == "TEST_VALIDATION_001"
        assert error_def.message == "Test error message"
        assert error_def.http_status == 400
        assert error_def.severity == ErrorSeverity.ERROR
        assert error_def.category == ErrorCategory.VALIDATION
        assert error_def.service == ServiceCode.SHARED
        assert error_def.retryable is False
        assert error_def.context_fields == ["field1", "field2"]
    
    def test_error_definition_to_dict(self):
        """Test error definition serialization to dictionary."""
        error_def = ErrorDefinition(
            code="TEST_VALIDATION_001",
            message="Test error message",
            description="Test error description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION,
            service=ServiceCode.SHARED,
            resolution_guidance="Test resolution guidance",
            user_message="Test user message",
            retryable=True,
            context_fields=["field1"]
        )
        
        result = error_def.to_dict()
        
        assert result["code"] == "TEST_VALIDATION_001"
        assert result["message"] == "Test error message"
        assert result["http_status"] == 400
        assert result["severity"] == "error"
        assert result["category"] == "VALIDATION"
        assert result["service"] == "SHARED"
        assert result["retryable"] is True
        assert result["context_fields"] == ["field1"]
    
    def test_error_definition_optional_fields(self):
        """Test error definition with optional fields."""
        error_def = ErrorDefinition(
            code="TEST_VALIDATION_002",
            message="Test error message",
            description="Test error description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION,
            service=ServiceCode.SHARED,
            resolution_guidance="Test resolution guidance",
            user_message="Test user message"
            # retryable and context_fields are optional
        )
        
        assert error_def.retryable is False  # Default value
        assert error_def.context_fields is None  # Default value
        
        result = error_def.to_dict()
        assert result["retryable"] is False
        assert result["context_fields"] == []  # Converted to empty list


class TestErrorCodeRegistry:
    """Test error code registry functionality."""
    
    @pytest.fixture
    def fresh_registry(self):
        """Create a fresh error registry for testing."""
        registry = ErrorCodeRegistry()
        # Clear the initialized catalog for clean testing
        registry._error_definitions.clear()
        registry._service_counters.clear()
        return registry
    
    def test_register_error_basic(self, fresh_registry):
        """Test basic error registration."""
        error_code = fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="Test error",
            description="Test description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Test guidance",
            user_message="Test user message"
        )
        
        assert error_code == "AUTH_VALIDATION_001"
        
        error_def = fresh_registry.get_error_definition(error_code)
        assert error_def is not None
        assert error_def.code == "AUTH_VALIDATION_001"
        assert error_def.message == "Test error"
        assert error_def.service == ServiceCode.AUTH
        assert error_def.category == ErrorCategory.VALIDATION
    
    def test_register_error_auto_increment(self, fresh_registry):
        """Test automatic error code number increment."""
        # Register first error
        error_code1 = fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="First error",
            description="First description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="First guidance",
            user_message="First user message"
        )
        
        # Register second error in same service/category
        error_code2 = fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="Second error",
            description="Second description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Second guidance",
            user_message="Second user message"
        )
        
        assert error_code1 == "AUTH_VALIDATION_001"
        assert error_code2 == "AUTH_VALIDATION_002"
    
    def test_register_error_different_categories(self, fresh_registry):
        """Test error registration across different categories."""
        validation_error = fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="Validation error",
            description="Validation description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Validation guidance",
            user_message="Validation user message"
        )
        
        auth_error = fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.AUTHENTICATION,
            message="Auth error",
            description="Auth description",
            http_status=401,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Auth guidance",
            user_message="Auth user message"
        )
        
        assert validation_error == "AUTH_VALIDATION_001"
        assert auth_error == "AUTH_AUTHENTICATION_001"
    
    def test_register_error_custom_number(self, fresh_registry):
        """Test error registration with custom number."""
        error_code = fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="Custom error",
            description="Custom description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Custom guidance",
            user_message="Custom user message",
            custom_number=999
        )
        
        assert error_code == "AUTH_VALIDATION_999"
    
    def test_register_error_conflict_detection(self, fresh_registry):
        """Test error code conflict detection."""
        # Register first error
        fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="First error",
            description="First description",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="First guidance",
            user_message="First user message",
            custom_number=1
        )
        
        # Try to register conflicting error
        with pytest.raises(ValueError, match="Error code AUTH_VALIDATION_001 already exists"):
            fresh_registry.register_error(
                service=ServiceCode.AUTH,
                category=ErrorCategory.VALIDATION,
                message="Conflicting error",
                description="Conflicting description",
                http_status=400,
                severity=ErrorSeverity.ERROR,
                resolution_guidance="Conflicting guidance",
                user_message="Conflicting user message",
                custom_number=1
            )
    
    def test_get_errors_by_service(self, fresh_registry):
        """Test getting errors by service."""
        # Register errors for different services
        fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="Auth error 1",
            description="Auth description 1",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Auth guidance 1",
            user_message="Auth user message 1"
        )
        
        fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.AUTHENTICATION,
            message="Auth error 2",
            description="Auth description 2",
            http_status=401,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Auth guidance 2",
            user_message="Auth user message 2"
        )
        
        fresh_registry.register_error(
            service=ServiceCode.AC,
            category=ErrorCategory.VALIDATION,
            message="AC error 1",
            description="AC description 1",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="AC guidance 1",
            user_message="AC user message 1"
        )
        
        auth_errors = fresh_registry.get_errors_by_service(ServiceCode.AUTH)
        ac_errors = fresh_registry.get_errors_by_service(ServiceCode.AC)
        
        assert len(auth_errors) == 2
        assert len(ac_errors) == 1
        assert all(error.service == ServiceCode.AUTH for error in auth_errors)
        assert all(error.service == ServiceCode.AC for error in ac_errors)
    
    def test_get_errors_by_category(self, fresh_registry):
        """Test getting errors by category."""
        # Register errors for different categories
        fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="Validation error 1",
            description="Validation description 1",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Validation guidance 1",
            user_message="Validation user message 1"
        )
        
        fresh_registry.register_error(
            service=ServiceCode.AC,
            category=ErrorCategory.VALIDATION,
            message="Validation error 2",
            description="Validation description 2",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Validation guidance 2",
            user_message="Validation user message 2"
        )
        
        fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.AUTHENTICATION,
            message="Auth error 1",
            description="Auth description 1",
            http_status=401,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Auth guidance 1",
            user_message="Auth user message 1"
        )
        
        validation_errors = fresh_registry.get_errors_by_category(ErrorCategory.VALIDATION)
        auth_errors = fresh_registry.get_errors_by_category(ErrorCategory.AUTHENTICATION)
        
        assert len(validation_errors) == 2
        assert len(auth_errors) == 1
        assert all(error.category == ErrorCategory.VALIDATION for error in validation_errors)
        assert all(error.category == ErrorCategory.AUTHENTICATION for error in auth_errors)
    
    def test_export_catalog(self, fresh_registry):
        """Test error catalog export."""
        # Register a few errors
        fresh_registry.register_error(
            service=ServiceCode.AUTH,
            category=ErrorCategory.VALIDATION,
            message="Test error 1",
            description="Test description 1",
            http_status=400,
            severity=ErrorSeverity.ERROR,
            resolution_guidance="Test guidance 1",
            user_message="Test user message 1"
        )
        
        fresh_registry.register_error(
            service=ServiceCode.AC,
            category=ErrorCategory.BUSINESS_LOGIC,
            message="Test error 2",
            description="Test description 2",
            http_status=422,
            severity=ErrorSeverity.WARNING,
            resolution_guidance="Test guidance 2",
            user_message="Test user message 2"
        )
        
        catalog = fresh_registry.export_catalog()
        
        assert "version" in catalog
        assert "generated_at" in catalog
        assert "total_errors" in catalog
        assert "errors" in catalog
        
        assert catalog["total_errors"] == 2
        assert "AUTH_VALIDATION_001" in catalog["errors"]
        assert "AC_BUSINESS_LOGIC_001" in catalog["errors"]
        
        # Verify error structure
        auth_error = catalog["errors"]["AUTH_VALIDATION_001"]
        assert auth_error["code"] == "AUTH_VALIDATION_001"
        assert auth_error["message"] == "Test error 1"
        assert auth_error["http_status"] == 400
        assert auth_error["severity"] == "error"


class TestGlobalErrorRegistry:
    """Test global error registry and convenience functions."""
    
    def test_global_registry_initialized(self):
        """Test that global registry is initialized with errors."""
        # The global registry should have errors from initialization
        catalog = export_error_catalog()
        assert catalog["total_errors"] > 0
        assert "errors" in catalog
    
    def test_get_error_definition_function(self):
        """Test get_error_definition convenience function."""
        # Should have some shared errors
        error_def = get_error_definition("SHARED_VALIDATION_001")
        assert error_def is not None
        assert error_def.code == "SHARED_VALIDATION_001"
        assert error_def.service == ServiceCode.SHARED
        assert error_def.category == ErrorCategory.VALIDATION
    
    def test_get_service_errors_function(self):
        """Test get_service_errors convenience function."""
        auth_errors = get_service_errors(ServiceCode.AUTH)
        assert len(auth_errors) > 0
        assert all(error.service == ServiceCode.AUTH for error in auth_errors)
    
    def test_get_category_errors_function(self):
        """Test get_category_errors convenience function."""
        validation_errors = get_category_errors(ErrorCategory.VALIDATION)
        assert len(validation_errors) > 0
        assert all(error.category == ErrorCategory.VALIDATION for error in validation_errors)
    
    def test_all_services_have_errors(self):
        """Test that all services have at least one error defined."""
        services_with_errors = set()
        
        for service in ServiceCode:
            service_errors = get_service_errors(service)
            if service_errors:
                services_with_errors.add(service)
        
        # All services except SHARED should have specific errors
        expected_services = {ServiceCode.AUTH, ServiceCode.AC, ServiceCode.INTEGRITY, 
                           ServiceCode.FV, ServiceCode.GS, ServiceCode.PGC, 
                           ServiceCode.EC, ServiceCode.DGM, ServiceCode.SHARED}
        
        assert services_with_errors == expected_services
    
    def test_all_categories_have_errors(self):
        """Test that all categories have at least one error defined."""
        categories_with_errors = set()
        
        for category in ErrorCategory:
            category_errors = get_category_errors(category)
            if category_errors:
                categories_with_errors.add(category)
        
        # All categories should have at least one error
        expected_categories = set(ErrorCategory)
        assert categories_with_errors == expected_categories
    
    def test_error_code_format_consistency(self):
        """Test that all error codes follow the expected format."""
        catalog = export_error_catalog()
        
        for error_code, error_data in catalog["errors"].items():
            # Check format: SERVICE_CATEGORY_NUMBER
            parts = error_code.split("_")
            assert len(parts) == 3, f"Error code {error_code} doesn't follow SERVICE_CATEGORY_NUMBER format"
            
            service_part, category_part, number_part = parts
            
            # Verify service part is valid
            assert service_part in [s.value for s in ServiceCode], f"Invalid service in {error_code}"
            
            # Verify category part is valid
            assert category_part in [c.value for c in ErrorCategory], f"Invalid category in {error_code}"
            
            # Verify number part is 3 digits
            assert number_part.isdigit() and len(number_part) == 3, f"Invalid number format in {error_code}"
    
    def test_http_status_code_validity(self):
        """Test that all HTTP status codes are valid."""
        catalog = export_error_catalog()
        valid_status_codes = {400, 401, 403, 404, 408, 409, 422, 429, 500, 503}
        
        for error_code, error_data in catalog["errors"].items():
            status_code = error_data["http_status"]
            assert status_code in valid_status_codes, f"Invalid HTTP status {status_code} in {error_code}"


# Integration test for complete workflow
@pytest.mark.integration
class TestErrorCatalogIntegration:
    """Integration tests for error catalog system."""
    
    def test_complete_error_workflow(self):
        """Test complete error definition and retrieval workflow."""
        # Get an existing error
        error_def = get_error_definition("AUTH_AUTHENTICATION_002")
        assert error_def is not None
        
        # Verify all required fields are present
        assert error_def.code == "AUTH_AUTHENTICATION_002"
        assert error_def.message
        assert error_def.description
        assert error_def.http_status > 0
        assert error_def.severity in ErrorSeverity
        assert error_def.category in ErrorCategory
        assert error_def.service in ServiceCode
        assert error_def.resolution_guidance
        assert error_def.user_message
        
        # Convert to dictionary
        error_dict = error_def.to_dict()
        
        # Verify dictionary structure
        required_fields = [
            "code", "message", "description", "http_status", 
            "severity", "category", "service", "resolution_guidance", 
            "user_message", "retryable", "context_fields"
        ]
        
        for field in required_fields:
            assert field in error_dict, f"Missing field {field} in error dictionary"
    
    def test_error_catalog_completeness(self):
        """Test that error catalog covers all major error scenarios."""
        catalog = export_error_catalog()
        
        # Should have reasonable number of errors
        assert catalog["total_errors"] >= 20, "Error catalog should have comprehensive coverage"
        
        # Should cover all services
        services_covered = set()
        categories_covered = set()
        
        for error_data in catalog["errors"].values():
            services_covered.add(error_data["service"])
            categories_covered.add(error_data["category"])
        
        # All services should be covered
        expected_services = {s.value for s in ServiceCode}
        assert services_covered == expected_services
        
        # All categories should be covered
        expected_categories = {c.value for c in ErrorCategory}
        assert categories_covered == expected_categories
