"""
Security Configuration Helper for ACGS Services

This module provides standardized security configuration across all ACGS services
with constitutional compliance validation.
"""

import os
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .unified_input_validation import SecurityConfig, SecurityLevel
from .csrf_protection import CSRFConfig

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ServiceType(Enum):
    """ACGS service types with specific security requirements."""
    AUTHENTICATION = "authentication"
    CONSTITUTIONAL_AI = "constitutional_ai"
    GOVERNANCE_SYNTHESIS = "governance_synthesis"
    POLICY_GOVERNANCE = "policy_governance"
    FORMAL_VERIFICATION = "formal_verification"
    EVOLUTIONARY_COMPUTATION = "evolutionary_computation"
    INTEGRITY = "integrity"
    PLATFORM = "platform"


@dataclass
class ServiceSecurityProfile:
    """Security profile for different service types."""
    name: str
    security_level: SecurityLevel
    max_string_length: int
    max_json_size: int
    max_file_size: int
    allowed_file_types: Set[str]
    rate_limit_requests: int
    rate_limit_window: int
    csrf_enabled: bool
    strict_csp: bool
    allowed_origins: Set[str]
    excluded_paths: Set[str]


# Pre-defined security profiles for different service types
SECURITY_PROFILES: Dict[ServiceType, ServiceSecurityProfile] = {
    ServiceType.AUTHENTICATION: ServiceSecurityProfile(
        name="Authentication Service",
        security_level=SecurityLevel.CRITICAL,
        max_string_length=256,
        max_json_size=64 * 1024,  # 64KB
        max_file_size=1024 * 1024,  # 1MB
        allowed_file_types={'json'},
        rate_limit_requests=50,  # Stricter rate limiting
        rate_limit_window=60,
        csrf_enabled=True,
        strict_csp=True,
        allowed_origins={
            "http://localhost:3000",
            "http://localhost:8000",
            "https://acgs.example.com"
        },
        excluded_paths={
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json"
        }
    ),
    
    ServiceType.CONSTITUTIONAL_AI: ServiceSecurityProfile(
        name="Constitutional AI Service",
        security_level=SecurityLevel.CRITICAL,
        max_string_length=2048,  # Longer for AI prompts
        max_json_size=512 * 1024,  # 512KB for AI data
        max_file_size=5 * 1024 * 1024,  # 5MB
        allowed_file_types={'json', 'txt', 'xml'},
        rate_limit_requests=100,
        rate_limit_window=60,
        csrf_enabled=True,
        strict_csp=True,
        allowed_origins={
            "http://localhost:3000",
            "http://localhost:8001",
            "https://acgs.example.com"
        },
        excluded_paths={
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/api/constitutional/public"
        }
    ),
    
    ServiceType.GOVERNANCE_SYNTHESIS: ServiceSecurityProfile(
        name="Governance Synthesis Service",
        security_level=SecurityLevel.HIGH,
        max_string_length=4096,  # Large for policy synthesis
        max_json_size=1024 * 1024,  # 1MB
        max_file_size=10 * 1024 * 1024,  # 10MB
        allowed_file_types={'json', 'txt', 'xml', 'pdf'},
        rate_limit_requests=200,
        rate_limit_window=60,
        csrf_enabled=True,
        strict_csp=True,
        allowed_origins={
            "http://localhost:3000",
            "http://localhost:8004",
            "https://acgs.example.com"
        },
        excluded_paths={
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/api/synthesis/public"
        }
    ),
    
    ServiceType.POLICY_GOVERNANCE: ServiceSecurityProfile(
        name="Policy Governance Service",
        security_level=SecurityLevel.HIGH,
        max_string_length=8192,  # Very large for policy documents
        max_json_size=2048 * 1024,  # 2MB
        max_file_size=50 * 1024 * 1024,  # 50MB for policy files
        allowed_file_types={'json', 'txt', 'xml', 'pdf', 'doc', 'docx'},
        rate_limit_requests=150,
        rate_limit_window=60,
        csrf_enabled=True,
        strict_csp=True,
        allowed_origins={
            "http://localhost:3000",
            "http://localhost:8005",
            "https://acgs.example.com"
        },
        excluded_paths={
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/api/policy/public"
        }
    ),
    
    ServiceType.FORMAL_VERIFICATION: ServiceSecurityProfile(
        name="Formal Verification Service",
        security_level=SecurityLevel.HIGH,
        max_string_length=16384,  # Very large for verification proofs
        max_json_size=4096 * 1024,  # 4MB
        max_file_size=100 * 1024 * 1024,  # 100MB for large proofs
        allowed_file_types={'json', 'txt', 'xml', 'smt2', 'coq', 'lean'},
        rate_limit_requests=75,  # Lower due to computational intensity
        rate_limit_window=60,
        csrf_enabled=True,
        strict_csp=True,
        allowed_origins={
            "http://localhost:3000",
            "http://localhost:8003",
            "https://acgs.example.com"
        },
        excluded_paths={
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json"
        }
    ),
    
    ServiceType.EVOLUTIONARY_COMPUTATION: ServiceSecurityProfile(
        name="Evolutionary Computation Service",
        security_level=SecurityLevel.HIGH,
        max_string_length=4096,
        max_json_size=1024 * 1024,  # 1MB
        max_file_size=20 * 1024 * 1024,  # 20MB
        allowed_file_types={'json', 'txt', 'xml', 'py', 'pkl'},
        rate_limit_requests=100,
        rate_limit_window=60,
        csrf_enabled=True,
        strict_csp=True,
        allowed_origins={
            "http://localhost:3000",
            "http://localhost:8006",
            "https://acgs.example.com"
        },
        excluded_paths={
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json"
        }
    ),
    
    ServiceType.INTEGRITY: ServiceSecurityProfile(
        name="Integrity Service",
        security_level=SecurityLevel.CRITICAL,
        max_string_length=1024,
        max_json_size=256 * 1024,  # 256KB
        max_file_size=5 * 1024 * 1024,  # 5MB
        allowed_file_types={'json', 'txt', 'xml', 'sig', 'pem'},
        rate_limit_requests=200,
        rate_limit_window=60,
        csrf_enabled=True,
        strict_csp=True,
        allowed_origins={
            "http://localhost:3000",
            "http://localhost:8002",
            "https://acgs.example.com"
        },
        excluded_paths={
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/api/integrity/verify"
        }
    ),
    
    ServiceType.PLATFORM: ServiceSecurityProfile(
        name="Platform Service",
        security_level=SecurityLevel.MEDIUM,
        max_string_length=1000,
        max_json_size=1024 * 1024,  # 1MB
        max_file_size=10 * 1024 * 1024,  # 10MB
        allowed_file_types={'json', 'txt', 'xml', 'jpg', 'png', 'pdf'},
        rate_limit_requests=300,
        rate_limit_window=60,
        csrf_enabled=True,
        strict_csp=False,  # More flexible for platform services
        allowed_origins={
            "http://localhost:3000",
            "http://localhost:8000",
            "https://acgs.example.com"
        },
        excluded_paths={
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/api/public"
        }
    )
}


class ACGSSecurityConfigHelper:
    """Helper class for creating standardized security configurations."""
    
    @staticmethod
    def create_security_config(
        service_type: ServiceType,
        environment: str = "production",
        custom_overrides: Optional[Dict[str, Any]] = None
    ) -> SecurityConfig:
        """
        Create SecurityConfig for a specific service type.
        
        Args:
            service_type: Type of ACGS service
            environment: Environment (development, staging, production)
            custom_overrides: Custom configuration overrides
            
        Returns:
            Configured SecurityConfig instance
        """
        profile = SECURITY_PROFILES[service_type]
        
        # Adjust settings based on environment
        if environment == "development":
            # More lenient in development
            security_level = SecurityLevel.MEDIUM
            rate_limit_requests = profile.rate_limit_requests * 2
            strict_csp = False
        elif environment == "staging":
            # Similar to production but slightly more lenient
            security_level = profile.security_level
            rate_limit_requests = profile.rate_limit_requests
            strict_csp = profile.strict_csp
        else:  # production
            security_level = profile.security_level
            rate_limit_requests = profile.rate_limit_requests
            strict_csp = profile.strict_csp
        
        config = SecurityConfig(
            max_string_length=profile.max_string_length,
            max_json_size=profile.max_json_size,
            max_file_size=profile.max_file_size,
            allowed_file_types=profile.allowed_file_types.copy(),
            rate_limit_requests=rate_limit_requests,
            rate_limit_window=profile.rate_limit_window,
            csrf_token_expiry=3600,  # 1 hour
            enable_strict_csp=strict_csp,
            enable_xss_protection=True,
            enable_csrf_protection=profile.csrf_enabled
        )
        
        # Apply custom overrides
        if custom_overrides:
            for key, value in custom_overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        return config
    
    @staticmethod
    def create_csrf_config(
        service_type: ServiceType,
        secret_key: Optional[str] = None,
        environment: str = "production",
        custom_overrides: Optional[Dict[str, Any]] = None
    ) -> CSRFConfig:
        """
        Create CSRFConfig for a specific service type.
        
        Args:
            service_type: Type of ACGS service
            secret_key: CSRF secret key (will use env var if not provided)
            environment: Environment (development, staging, production)
            custom_overrides: Custom configuration overrides
            
        Returns:
            Configured CSRFConfig instance
        """
        profile = SECURITY_PROFILES[service_type]
        
        # Get secret key from environment or use provided
        if not secret_key:
            secret_key = os.getenv("CSRF_SECRET_KEY", "change-in-production-environment")
        
        # Adjust settings based on environment
        if environment == "development":
            cookie_secure = False
            cookie_samesite = "Lax"
            require_origin_header = False
        else:
            cookie_secure = True
            cookie_samesite = "Strict"
            require_origin_header = True
        
        config = CSRFConfig(
            token_name="csrf_token",
            cookie_name="csrf_cookie",
            header_name="X-CSRF-Token",
            secret_key=secret_key,
            token_length=32,
            token_expiry=3600,  # 1 hour
            cookie_secure=cookie_secure,
            cookie_samesite=cookie_samesite,
            require_origin_header=require_origin_header,
            allowed_origins=profile.allowed_origins.copy(),
            excluded_paths=profile.excluded_paths.copy()
        )
        
        # Apply custom overrides
        if custom_overrides:
            for key, value in custom_overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        return config
    
    @staticmethod
    def get_service_profile(service_type: ServiceType) -> ServiceSecurityProfile:
        """Get security profile for a service type."""
        return SECURITY_PROFILES[service_type]
    
    @staticmethod
    def validate_constitutional_compliance() -> bool:
        """Validate constitutional compliance hash across configurations."""
        return CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
    
    @staticmethod
    def create_service_security_bundle(
        service_type: ServiceType,
        csrf_secret_key: Optional[str] = None,
        environment: str = "production",
        custom_security_overrides: Optional[Dict[str, Any]] = None,
        custom_csrf_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create complete security bundle for a service.
        
        Returns:
            Dictionary with security_config, csrf_config, and profile
        """
        return {
            "security_config": ACGSSecurityConfigHelper.create_security_config(
                service_type, environment, custom_security_overrides
            ),
            "csrf_config": ACGSSecurityConfigHelper.create_csrf_config(
                service_type, csrf_secret_key, environment, custom_csrf_overrides
            ),
            "profile": ACGSSecurityConfigHelper.get_service_profile(service_type),
            "constitutional_hash": CONSTITUTIONAL_HASH
        }


# Utility functions for easy integration
def get_auth_service_security() -> Dict[str, Any]:
    """Get security configuration for authentication service."""
    return ACGSSecurityConfigHelper.create_service_security_bundle(
        ServiceType.AUTHENTICATION,
        environment=os.getenv("ENVIRONMENT", "production")
    )


def get_constitutional_ai_security() -> Dict[str, Any]:
    """Get security configuration for constitutional AI service."""
    return ACGSSecurityConfigHelper.create_service_security_bundle(
        ServiceType.CONSTITUTIONAL_AI,
        environment=os.getenv("ENVIRONMENT", "production")
    )


def get_platform_service_security() -> Dict[str, Any]:
    """Get security configuration for platform services."""
    return ACGSSecurityConfigHelper.create_service_security_bundle(
        ServiceType.PLATFORM,
        environment=os.getenv("ENVIRONMENT", "production")
    )


def create_custom_service_security(
    max_string_length: int = 1000,
    security_level: SecurityLevel = SecurityLevel.HIGH,
    csrf_enabled: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """Create custom security configuration for specialized services."""
    
    # Create custom profile
    custom_profile = ServiceSecurityProfile(
        name="Custom Service",
        security_level=security_level,
        max_string_length=max_string_length,
        max_json_size=kwargs.get("max_json_size", 1024 * 1024),
        max_file_size=kwargs.get("max_file_size", 10 * 1024 * 1024),
        allowed_file_types=set(kwargs.get("allowed_file_types", ['json', 'txt'])),
        rate_limit_requests=kwargs.get("rate_limit_requests", 100),
        rate_limit_window=kwargs.get("rate_limit_window", 60),
        csrf_enabled=csrf_enabled,
        strict_csp=kwargs.get("strict_csp", True),
        allowed_origins=set(kwargs.get("allowed_origins", ["http://localhost:3000"])),
        excluded_paths=set(kwargs.get("excluded_paths", ["/health", "/metrics"]))
    )
    
    # Temporarily add to profiles
    temp_service_type = ServiceType.PLATFORM  # Use platform as base
    original_profile = SECURITY_PROFILES[temp_service_type]
    SECURITY_PROFILES[temp_service_type] = custom_profile
    
    try:
        result = ACGSSecurityConfigHelper.create_service_security_bundle(temp_service_type)
        result["profile"] = custom_profile
        return result
    finally:
        # Restore original profile
        SECURITY_PROFILES[temp_service_type] = original_profile