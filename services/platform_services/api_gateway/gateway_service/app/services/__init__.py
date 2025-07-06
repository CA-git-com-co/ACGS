"""
Service modules for ACGS API Gateway Service.

This package contains service layer components for API gateway operations,
service routing, load balancing, and constitutional compliance.
"""

from .gateway_service import GatewayService
from .load_balancer import LoadBalancerService
from .routing_service import RoutingService
from .service_discovery import ServiceDiscoveryService

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

__all__ = [
    "GatewayService",
    "LoadBalancerService",
    "RoutingService",
    "ServiceDiscoveryService",
]
