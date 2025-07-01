"""
Service-to-Service Authentication Configuration for ACGS-1
Production-grade authentication and authorization for inter-service communication
"""

import os
from enum import Enum

from .enhanced_auth import (
    ConstitutionalPermission,
    ServiceAuthManager,
    ServicePermission,
)


class ACGSService(Enum):
    """ACGS service identifiers."""

    AUTH_SERVICE = "auth_service"
    AC_SERVICE = "ac_service"
    INTEGRITY_SERVICE = "integrity_service"
    FV_SERVICE = "fv_service"
    GS_SERVICE = "gs_service"
    PGC_SERVICE = "pgc_service"
    EC_SERVICE = "ec_service"
    RESEARCH_SERVICE = "research_service"


# Service-specific permissions mapping
SERVICE_PERMISSIONS = {
    ACGSService.AUTH_SERVICE: [
        ConstitutionalPermission.SYSTEM_ADMIN,
        ServicePermission.AUTH_MANAGE_USERS,
        ServicePermission.AUTH_MANAGE_ROLES,
    ],
    ACGSService.AC_SERVICE: [
        ConstitutionalPermission.CONSTITUTIONAL_READ,
        ConstitutionalPermission.CONSTITUTIONAL_WRITE,
        ServicePermission.AC_VALIDATE_PRINCIPLES,
        ServicePermission.AC_MANAGE_CONSTITUTION,
    ],
    ACGSService.INTEGRITY_SERVICE: [
        ConstitutionalPermission.AUDIT_ACCESS,
        ServicePermission.INTEGRITY_CRYPTOGRAPHIC,
        ServicePermission.INTEGRITY_AUDIT_TRAIL,
    ],
    ACGSService.FV_SERVICE: [
        ConstitutionalPermission.POLICY_REVIEW,
        ServicePermission.FV_VERIFY_POLICIES,
        ServicePermission.FV_MATHEMATICAL_PROOF,
    ],
    ACGSService.GS_SERVICE: [
        ConstitutionalPermission.POLICY_CREATE,
        ConstitutionalPermission.GOVERNANCE_PARTICIPATE,
        ServicePermission.GS_SYNTHESIZE_POLICIES,
        ServicePermission.GS_MANAGE_WORKFLOWS,
    ],
    ACGSService.PGC_SERVICE: [
        ConstitutionalPermission.POLICY_ENFORCE,
        ConstitutionalPermission.GOVERNANCE_OVERSEE,
        ServicePermission.PGC_ENFORCE_POLICIES,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
    ],
    ACGSService.EC_SERVICE: [
        ConstitutionalPermission.WINA_OVERSIGHT,
        ConstitutionalPermission.WINA_INTERVENTION,
        ServicePermission.EC_WINA_OVERSIGHT,
        ServicePermission.EC_SYSTEM_EVOLUTION,
    ],
    ACGSService.RESEARCH_SERVICE: [
        ConstitutionalPermission.GOVERNANCE_PARTICIPATE,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
    ],
}

# Service endpoints configuration
SERVICE_ENDPOINTS = {
    ACGSService.AUTH_SERVICE: {
        "host": os.getenv("AUTH_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("AUTH_SERVICE_PORT", "8000")),
        "base_url": os.getenv("AUTH_SERVICE_URL", "http://localhost:8000"),
        "health_endpoint": "/health",
        "auth_required": False,  # Auth service doesn't require auth for its own endpoints
    },
    ACGSService.AC_SERVICE: {
        "host": os.getenv("AC_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("AC_SERVICE_PORT", "8001")),
        "base_url": os.getenv("AC_SERVICE_URL", "http://localhost:8001"),
        "health_endpoint": "/health",
        "auth_required": True,
    },
    ACGSService.INTEGRITY_SERVICE: {
        "host": os.getenv("INTEGRITY_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("INTEGRITY_SERVICE_PORT", "8002")),
        "base_url": os.getenv("INTEGRITY_SERVICE_URL", "http://localhost:8002"),
        "health_endpoint": "/health",
        "auth_required": True,
    },
    ACGSService.FV_SERVICE: {
        "host": os.getenv("FV_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("FV_SERVICE_PORT", "8003")),
        "base_url": os.getenv("FV_SERVICE_URL", "http://localhost:8003"),
        "health_endpoint": "/health",
        "auth_required": True,
    },
    ACGSService.GS_SERVICE: {
        "host": os.getenv("GS_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("GS_SERVICE_PORT", "8004")),
        "base_url": os.getenv("GS_SERVICE_URL", "http://localhost:8004"),
        "health_endpoint": "/health",
        "auth_required": True,
    },
    ACGSService.PGC_SERVICE: {
        "host": os.getenv("PGC_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("PGC_SERVICE_PORT", "8005")),
        "base_url": os.getenv("PGC_SERVICE_URL", "http://localhost:8005"),
        "health_endpoint": "/health",
        "auth_required": True,
    },
    ACGSService.EC_SERVICE: {
        "host": os.getenv("EC_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("EC_SERVICE_PORT", "8006")),
        "base_url": os.getenv("EC_SERVICE_URL", "http://localhost:8006"),
        "health_endpoint": "/health",
        "auth_required": True,
    },
    ACGSService.RESEARCH_SERVICE: {
        "host": os.getenv("RESEARCH_SERVICE_HOST", "localhost"),
        "port": int(os.getenv("RESEARCH_SERVICE_PORT", "8007")),
        "base_url": os.getenv("RESEARCH_SERVICE_URL", "http://localhost:8007"),
        "health_endpoint": "/health",
        "auth_required": True,
    },
}


class ServiceAuthConfig:
    """Configuration manager for service authentication."""

    @staticmethod
    def get_service_token(service: ACGSService) -> str:
        """Get authentication token for a service."""
        permissions = [perm.value for perm in SERVICE_PERMISSIONS.get(service, [])]
        return ServiceAuthManager.create_service_token(
            service_name=service.value, permissions=permissions
        )

    @staticmethod
    def get_service_endpoint(service: ACGSService) -> dict[str, any]:
        """Get endpoint configuration for a service."""
        return SERVICE_ENDPOINTS.get(service, {})

    @staticmethod
    def get_auth_headers(service: ACGSService) -> dict[str, str]:
        """Get authentication headers for service-to-service calls."""
        endpoint_config = SERVICE_ENDPOINTS.get(service, {})

        if not endpoint_config.get("auth_required", True):
            return {}

        token = ServiceAuthConfig.get_service_token(service)
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def is_service_healthy(service: ACGSService) -> bool:
        """Check if a service is healthy (placeholder for health check logic)."""
        # This would implement actual health checking logic
        # For now, return True as a placeholder
        return True


# Constitutional governance workflow permissions
GOVERNANCE_WORKFLOW_PERMISSIONS = {
    "policy_creation": [
        ConstitutionalPermission.POLICY_CREATE,
        ServicePermission.GS_SYNTHESIZE_POLICIES,
        ServicePermission.AC_VALIDATE_PRINCIPLES,
    ],
    "constitutional_compliance": [
        ConstitutionalPermission.CONSTITUTIONAL_READ,
        ConstitutionalPermission.POLICY_REVIEW,
        ServicePermission.PGC_VALIDATE_COMPLIANCE,
        ServicePermission.AC_VALIDATE_PRINCIPLES,
    ],
    "policy_enforcement": [
        ConstitutionalPermission.POLICY_ENFORCE,
        ServicePermission.PGC_ENFORCE_POLICIES,
        ServicePermission.INTEGRITY_AUDIT_TRAIL,
    ],
    "wina_oversight": [
        ConstitutionalPermission.WINA_OVERSIGHT,
        ConstitutionalPermission.WINA_INTERVENTION,
        ServicePermission.EC_WINA_OVERSIGHT,
    ],
    "audit_transparency": [
        ConstitutionalPermission.AUDIT_ACCESS,
        ServicePermission.INTEGRITY_AUDIT_TRAIL,
        ServicePermission.INTEGRITY_CRYPTOGRAPHIC,
    ],
}


def get_workflow_permissions(
    workflow_name: str,
) -> list[ConstitutionalPermission | ServicePermission]:
    """Get required permissions for a governance workflow."""
    return GOVERNANCE_WORKFLOW_PERMISSIONS.get(workflow_name, [])


# Export configuration
__all__ = [
    "GOVERNANCE_WORKFLOW_PERMISSIONS",
    "SERVICE_ENDPOINTS",
    "SERVICE_PERMISSIONS",
    "ACGSService",
    "ServiceAuthConfig",
    "get_workflow_permissions",
]
