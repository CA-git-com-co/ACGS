"""
Auth module for ACGS shared services.

This module provides authentication and authorization utilities
for multi-tenant operations.

Constitutional Hash: cdd01ef066bc6cf2
"""

from .multi_tenant_jwt import MultiTenantJWTHandler

__all__ = [
    "MultiTenantJWTHandler",
]

# Note: tenant_auth imports are commented out due to circular dependency issues
# If you need TenantAuthenticationService, import it directly:
# from services.shared.auth.tenant_auth import TenantAuthenticationService