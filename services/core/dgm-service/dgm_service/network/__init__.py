"""
Network configuration and service communication for DGM Service.

This module handles:
- Service discovery and registration
- HTTP client configuration for ACGS services
- Circuit breaker patterns
- Load balancing and failover
- Network security and authentication
"""

from .service_client import ACGSServiceClient
from .service_registry import ServiceRegistry
from .circuit_breaker import CircuitBreaker
from .load_balancer import LoadBalancer

__all__ = [
    "ACGSServiceClient",
    "ServiceRegistry", 
    "CircuitBreaker",
    "LoadBalancer"
]
