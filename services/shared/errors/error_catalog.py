"""
ACGS-1 Standardized Error Code Catalog

This module provides a comprehensive, hierarchical error code system for all ACGS microservices.
Error codes follow the format: {SERVICE}_{CATEGORY}_{NUMBER}

Services:
- AUTH: Authentication Service
- AC: Constitutional AI Service  
- INTEGRITY: Integrity Service
- FV: Formal Verification Service
- GS: Governance Synthesis Service
- PGC: Policy Governance Service
- EC: Evolutionary Computation Service
- DGM: Darwin Gödel Machine Service

Categories:
- VALIDATION: Input validation and data format errors
- AUTHENTICATION: Authentication and token-related errors
- AUTHORIZATION: Permission and access control errors
- BUSINESS_LOGIC: Domain-specific business rule violations
- EXTERNAL_SERVICE: External API and service integration errors
- SYSTEM_ERROR: Internal system and infrastructure errors
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path


class ErrorSeverity(str, Enum):
    """Error severity levels for proper escalation."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for hierarchical organization."""
    VALIDATION = "VALIDATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    SYSTEM_ERROR = "SYSTEM_ERROR"


class ServiceCode(str, Enum):
    """Service codes for error identification."""
    AUTH = "AUTH"
    AC = "AC"
    INTEGRITY = "INTEGRITY"
    FV = "FV"
    GS = "GS"
    PGC = "PGC"
    EC = "EC"
    DGM = "DGM"
    SHARED = "SHARED"


@dataclass
class ErrorDefinition:
    """Complete error definition with metadata."""
    code: str
    message: str
    description: str
    http_status: int
    severity: ErrorSeverity
    category: ErrorCategory
    service: ServiceCode
    resolution_guidance: str
    user_message: str
    retryable: bool = False
    context_fields: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "code": self.code,
            "message": self.message,
            "description": self.description,
            "http_status": self.http_status,
            "severity": self.severity.value,
            "category": self.category.value,
            "service": self.service.value,
            "resolution_guidance": self.resolution_guidance,
            "user_message": self.user_message,
            "retryable": self.retryable,
            "context_fields": self.context_fields or []
        }


class ErrorCodeRegistry:
    """Registry for managing error codes and preventing conflicts."""
    
    def __init__(self):
        self._error_definitions: Dict[str, ErrorDefinition] = {}
        self._service_counters: Dict[str, Dict[str, int]] = {}
        self._initialize_error_catalog()
    
    def _get_next_code_number(self, service: ServiceCode, category: ErrorCategory) -> int:
        """Get next available error code number for service/category combination."""
        service_key = service.value
        category_key = category.value
        
        if service_key not in self._service_counters:
            self._service_counters[service_key] = {}
        
        if category_key not in self._service_counters[service_key]:
            self._service_counters[service_key][category_key] = 0
        
        self._service_counters[service_key][category_key] += 1
        return self._service_counters[service_key][category_key]
    
    def register_error(
        self,
        service: ServiceCode,
        category: ErrorCategory,
        message: str,
        description: str,
        http_status: int,
        severity: ErrorSeverity,
        resolution_guidance: str,
        user_message: str,
        retryable: bool = False,
        context_fields: Optional[List[str]] = None,
        custom_number: Optional[int] = None
    ) -> str:
        """Register a new error and return the generated error code."""
        
        # Generate error code
        if custom_number:
            code_number = custom_number
        else:
            code_number = self._get_next_code_number(service, category)
        
        error_code = f"{service.value}_{category.value}_{code_number:03d}"
        
        # Check for conflicts
        if error_code in self._error_definitions:
            raise ValueError(f"Error code {error_code} already exists")
        
        # Create error definition
        error_def = ErrorDefinition(
            code=error_code,
            message=message,
            description=description,
            http_status=http_status,
            severity=severity,
            category=category,
            service=service,
            resolution_guidance=resolution_guidance,
            user_message=user_message,
            retryable=retryable,
            context_fields=context_fields
        )
        
        self._error_definitions[error_code] = error_def
        return error_code
    
    def get_error_definition(self, error_code: str) -> Optional[ErrorDefinition]:
        """Get error definition by code."""
        return self._error_definitions.get(error_code)
    
    def get_errors_by_service(self, service: ServiceCode) -> List[ErrorDefinition]:
        """Get all errors for a specific service."""
        return [
            error_def for error_def in self._error_definitions.values()
            if error_def.service == service
        ]
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorDefinition]:
        """Get all errors for a specific category."""
        return [
            error_def for error_def in self._error_definitions.values()
            if error_def.category == category
        ]
    
    def export_catalog(self) -> Dict[str, Any]:
        """Export complete error catalog."""
        return {
            "version": "1.0.0",
            "generated_at": "2025-06-22T10:30:00Z",
            "total_errors": len(self._error_definitions),
            "errors": {
                code: error_def.to_dict()
                for code, error_def in self._error_definitions.items()
            }
        }
    
    def _initialize_error_catalog(self):
        """Initialize the complete error catalog for all services."""
        
        # ===== SHARED ERRORS =====
        self.register_error(
            ServiceCode.SHARED, ErrorCategory.VALIDATION, 
            "Invalid request format", 
            "The request body or parameters are malformed or missing required fields",
            400, ErrorSeverity.ERROR,
            "Check request format and ensure all required fields are provided",
            "Please check your request and try again",
            context_fields=["field_name", "expected_format"]
        )
        
        self.register_error(
            ServiceCode.SHARED, ErrorCategory.VALIDATION,
            "Request validation failed",
            "One or more request parameters failed validation rules",
            422, ErrorSeverity.ERROR,
            "Review validation errors and correct the invalid fields",
            "Please correct the highlighted fields and try again",
            context_fields=["validation_errors", "invalid_fields"]
        )
        
        self.register_error(
            ServiceCode.SHARED, ErrorCategory.SYSTEM_ERROR,
            "Internal server error",
            "An unexpected error occurred while processing the request",
            500, ErrorSeverity.CRITICAL,
            "Check server logs and contact system administrator if issue persists",
            "An unexpected error occurred. Please try again later",
            retryable=True,
            context_fields=["error_id", "timestamp"],
            custom_number=1
        )

        self.register_error(
            ServiceCode.SHARED, ErrorCategory.SYSTEM_ERROR,
            "Service temporarily unavailable",
            "The service is temporarily unavailable due to maintenance or high load",
            503, ErrorSeverity.WARNING,
            "Wait for service to become available or check service status",
            "Service is temporarily unavailable. Please try again in a few minutes",
            retryable=True,
            context_fields=["retry_after", "service_status"],
            custom_number=2
        )
        
        # ===== AUTHENTICATION SERVICE ERRORS =====
        self.register_error(
            ServiceCode.AUTH, ErrorCategory.VALIDATION,
            "Invalid credentials format",
            "Username or password format is invalid",
            400, ErrorSeverity.ERROR,
            "Ensure username and password meet format requirements",
            "Please check your username and password format",
            context_fields=["field_name", "format_requirements"]
        )
        
        self.register_error(
            ServiceCode.AUTH, ErrorCategory.AUTHENTICATION,
            "Invalid credentials",
            "The provided username or password is incorrect",
            401, ErrorSeverity.WARNING,
            "Verify username and password are correct",
            "Invalid username or password",
            context_fields=["username", "attempt_count"]
        )
        
        self.register_error(
            ServiceCode.AUTH, ErrorCategory.AUTHENTICATION,
            "Account locked",
            "User account has been locked due to multiple failed login attempts",
            401, ErrorSeverity.WARNING,
            "Wait for lockout period to expire or contact administrator",
            "Your account has been temporarily locked. Please try again later",
            context_fields=["lockout_duration", "unlock_time"]
        )
        
        self.register_error(
            ServiceCode.AUTH, ErrorCategory.AUTHENTICATION,
            "Token expired",
            "The authentication token has expired and needs to be refreshed",
            401, ErrorSeverity.INFO,
            "Refresh the authentication token or login again",
            "Your session has expired. Please login again",
            context_fields=["token_type", "expired_at"]
        )
        
        self.register_error(
            ServiceCode.AUTH, ErrorCategory.AUTHENTICATION,
            "Invalid token",
            "The authentication token is malformed or invalid",
            401, ErrorSeverity.ERROR,
            "Ensure token is properly formatted and not tampered with",
            "Authentication failed. Please login again",
            context_fields=["token_type", "validation_error"]
        )
        
        self.register_error(
            ServiceCode.AUTH, ErrorCategory.AUTHORIZATION,
            "Insufficient permissions",
            "User does not have required permissions for this operation",
            403, ErrorSeverity.WARNING,
            "Ensure user has appropriate role and permissions",
            "You don't have permission to perform this action",
            context_fields=["required_permission", "user_role"]
        )
        
        self.register_error(
            ServiceCode.AUTH, ErrorCategory.BUSINESS_LOGIC,
            "User already exists",
            "A user with this username or email already exists",
            409, ErrorSeverity.ERROR,
            "Use a different username or email address",
            "This username or email is already taken",
            context_fields=["conflicting_field", "existing_value"]
        )
        
        # ===== CONSTITUTIONAL AI SERVICE ERRORS =====
        self.register_error(
            ServiceCode.AC, ErrorCategory.VALIDATION,
            "Invalid principle format",
            "Constitutional principle format is invalid or missing required fields",
            400, ErrorSeverity.ERROR,
            "Ensure principle follows required schema and includes all mandatory fields",
            "Please check the principle format and required fields",
            context_fields=["missing_fields", "invalid_fields"]
        )
        
        self.register_error(
            ServiceCode.AC, ErrorCategory.BUSINESS_LOGIC,
            "Principle conflict detected",
            "The proposed principle conflicts with existing constitutional principles",
            409, ErrorSeverity.WARNING,
            "Review conflicting principles and resolve contradictions",
            "This principle conflicts with existing constitutional rules",
            context_fields=["conflicting_principles", "conflict_type"]
        )
        
        self.register_error(
            ServiceCode.AC, ErrorCategory.BUSINESS_LOGIC,
            "Constitutional compliance violation",
            "The operation violates constitutional compliance requirements",
            422, ErrorSeverity.ERROR,
            "Ensure operation complies with constitutional principles",
            "This action violates constitutional compliance requirements",
            context_fields=["violated_principles", "compliance_score"]
        )
        
        # ===== INTEGRITY SERVICE ERRORS =====
        self.register_error(
            ServiceCode.INTEGRITY, ErrorCategory.VALIDATION,
            "Invalid signature format",
            "Digital signature format is invalid or corrupted",
            400, ErrorSeverity.ERROR,
            "Ensure signature is properly formatted and not corrupted",
            "Invalid signature format provided",
            context_fields=["signature_type", "format_error"]
        )
        
        self.register_error(
            ServiceCode.INTEGRITY, ErrorCategory.BUSINESS_LOGIC,
            "Signature verification failed",
            "Digital signature verification failed - signature is invalid",
            422, ErrorSeverity.ERROR,
            "Verify signature was created with correct key and data",
            "Signature verification failed",
            context_fields=["signature_algorithm", "key_id"]
        )
        
        self.register_error(
            ServiceCode.INTEGRITY, ErrorCategory.BUSINESS_LOGIC,
            "Certificate expired",
            "The cryptographic certificate has expired",
            422, ErrorSeverity.WARNING,
            "Renew the certificate or use a valid certificate",
            "Certificate has expired and needs to be renewed",
            context_fields=["certificate_id", "expired_at"]
        )
        
        # ===== FORMAL VERIFICATION SERVICE ERRORS =====
        self.register_error(
            ServiceCode.FV, ErrorCategory.VALIDATION,
            "Invalid verification query",
            "The formal verification query is malformed or invalid",
            400, ErrorSeverity.ERROR,
            "Check query syntax and ensure it follows Z3 SMT format",
            "Invalid verification query format",
            context_fields=["query_syntax_error", "line_number"]
        )
        
        self.register_error(
            ServiceCode.FV, ErrorCategory.EXTERNAL_SERVICE,
            "Z3 solver timeout",
            "Z3 SMT solver timed out while processing the verification query",
            408, ErrorSeverity.WARNING,
            "Simplify query or increase timeout limit",
            "Verification is taking too long. Please try a simpler query",
            retryable=True,
            context_fields=["timeout_duration", "query_complexity"]
        )
        
        self.register_error(
            ServiceCode.FV, ErrorCategory.BUSINESS_LOGIC,
            "Verification failed",
            "Formal verification failed - the property cannot be proven",
            422, ErrorSeverity.INFO,
            "Review the property and constraints for correctness",
            "The property could not be formally verified",
            context_fields=["property_name", "counterexample"]
        )
        
        # ===== GOVERNANCE SYNTHESIS SERVICE ERRORS =====
        self.register_error(
            ServiceCode.GS, ErrorCategory.VALIDATION,
            "Invalid synthesis parameters",
            "Policy synthesis parameters are invalid or missing",
            400, ErrorSeverity.ERROR,
            "Provide valid synthesis parameters including principles and constraints",
            "Invalid policy synthesis parameters",
            context_fields=["missing_parameters", "invalid_values"]
        )
        
        self.register_error(
            ServiceCode.GS, ErrorCategory.EXTERNAL_SERVICE,
            "LLM service unavailable",
            "External LLM service is unavailable or returned an error",
            503, ErrorSeverity.WARNING,
            "Check LLM service status and retry request",
            "Policy synthesis service is temporarily unavailable",
            retryable=True,
            context_fields=["llm_provider", "error_details"]
        )
        
        self.register_error(
            ServiceCode.GS, ErrorCategory.BUSINESS_LOGIC,
            "Synthesis quality insufficient",
            "Generated policy does not meet quality thresholds",
            422, ErrorSeverity.WARNING,
            "Adjust synthesis parameters or provide more detailed principles",
            "Generated policy quality is insufficient. Please refine your requirements",
            context_fields=["quality_score", "quality_threshold"]
        )
        
        # ===== POLICY GOVERNANCE SERVICE ERRORS =====
        self.register_error(
            ServiceCode.PGC, ErrorCategory.VALIDATION,
            "Invalid policy format",
            "Policy format is invalid or does not conform to OPA Rego syntax",
            400, ErrorSeverity.ERROR,
            "Ensure policy follows OPA Rego syntax and format requirements",
            "Invalid policy format provided",
            context_fields=["syntax_errors", "line_numbers"]
        )
        
        self.register_error(
            ServiceCode.PGC, ErrorCategory.BUSINESS_LOGIC,
            "Policy compilation failed",
            "Policy compilation failed due to syntax or logical errors",
            422, ErrorSeverity.ERROR,
            "Fix policy syntax and logical errors",
            "Policy compilation failed. Please check for errors",
            context_fields=["compilation_errors", "error_locations"]
        )
        
        self.register_error(
            ServiceCode.PGC, ErrorCategory.SYSTEM_ERROR,
            "Policy evaluation timeout",
            "Policy evaluation exceeded maximum allowed time",
            408, ErrorSeverity.WARNING,
            "Optimize policy complexity or increase timeout",
            "Policy evaluation is taking too long",
            retryable=True,
            context_fields=["evaluation_time", "timeout_limit"]
        )
        
        # ===== EVOLUTIONARY COMPUTATION SERVICE ERRORS =====
        self.register_error(
            ServiceCode.EC, ErrorCategory.VALIDATION,
            "Invalid optimization parameters",
            "Evolutionary computation parameters are invalid or out of range",
            400, ErrorSeverity.ERROR,
            "Provide valid optimization parameters within acceptable ranges",
            "Invalid optimization parameters provided",
            context_fields=["invalid_parameters", "valid_ranges"]
        )
        
        self.register_error(
            ServiceCode.EC, ErrorCategory.BUSINESS_LOGIC,
            "Optimization convergence failed",
            "Evolutionary algorithm failed to converge to a solution",
            422, ErrorSeverity.WARNING,
            "Adjust algorithm parameters or increase iteration limit",
            "Optimization failed to find a suitable solution",
            context_fields=["convergence_criteria", "iterations_completed"]
        )
        
        # ===== DARWIN GÖDEL MACHINE SERVICE ERRORS =====
        self.register_error(
            ServiceCode.DGM, ErrorCategory.VALIDATION,
            "Invalid improvement proposal",
            "Self-improvement proposal format is invalid or incomplete",
            400, ErrorSeverity.ERROR,
            "Ensure improvement proposal includes all required fields and validation",
            "Invalid self-improvement proposal format",
            context_fields=["missing_fields", "validation_errors"]
        )
        
        self.register_error(
            ServiceCode.DGM, ErrorCategory.BUSINESS_LOGIC,
            "Constitutional safety violation",
            "Proposed improvement violates constitutional safety constraints",
            422, ErrorSeverity.CRITICAL,
            "Ensure improvement complies with constitutional safety requirements",
            "Proposed improvement violates safety constraints",
            context_fields=["violated_constraints", "safety_score"]
        )
        
        self.register_error(
            ServiceCode.DGM, ErrorCategory.BUSINESS_LOGIC,
            "Improvement validation failed",
            "Self-improvement proposal failed validation tests",
            422, ErrorSeverity.WARNING,
            "Review improvement proposal and ensure it passes all validation tests",
            "Improvement proposal failed validation",
            context_fields=["failed_tests", "validation_results"]
        )


# Global error registry instance
error_registry = ErrorCodeRegistry()

# Convenience functions for common operations
def get_error_definition(error_code: str) -> Optional[ErrorDefinition]:
    """Get error definition by code."""
    return error_registry.get_error_definition(error_code)

def get_service_errors(service: ServiceCode) -> List[ErrorDefinition]:
    """Get all errors for a service."""
    return error_registry.get_errors_by_service(service)

def get_category_errors(category: ErrorCategory) -> List[ErrorDefinition]:
    """Get all errors for a category."""
    return error_registry.get_errors_by_category(category)

def export_error_catalog() -> Dict[str, Any]:
    """Export complete error catalog."""
    return error_registry.export_catalog()

# Export main classes and functions
__all__ = [
    "ErrorSeverity",
    "ErrorCategory", 
    "ServiceCode",
    "ErrorDefinition",
    "ErrorCodeRegistry",
    "error_registry",
    "get_error_definition",
    "get_service_errors",
    "get_category_errors",
    "export_error_catalog"
]
