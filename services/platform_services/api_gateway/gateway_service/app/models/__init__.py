"""
API Gateway Service Data Models

Core data models for API gateway operations, service routing,
load balancing, and constitutional compliance.
"""

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

from .gateway import (
    GatewayRequest,
    GatewayResponse,
    RouteConfig,
    ServiceEndpoint,
    ServiceHealth,
)
from .routing import (
    LoadBalancingStrategy,
    RouteMatch,
    RouteRule,
    RoutingDecision,
    ServiceInstance,
)

__all__ = [
    "GatewayRequest",
    "GatewayResponse",
    "RouteConfig",
    "ServiceEndpoint",
    "ServiceHealth",
    "LoadBalancingStrategy",
    "RouteMatch",
    "RouteRule",
    "RoutingDecision",
    "ServiceInstance",
]
