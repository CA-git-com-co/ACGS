"""
ACGS API Gateway Service Application

Main application package for the API gateway service with constitutional compliance,
service mesh integration, load balancing, and ACGS framework integration.
"""

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

from .core.gateway_config import GatewayConfig
from .middleware.constitutional_compliance import ConstitutionalComplianceMiddleware
from .routing.service_router import ServiceRouter

__all__ = [
    "GatewayConfig",
    "ConstitutionalComplianceMiddleware", 
    "ServiceRouter",
]
