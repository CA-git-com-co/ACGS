"""
Service mesh implementation for ACGS-PGP microservices.

This module provides a unified service communication layer that eliminates
duplicate HTTP client implementations and provides consistent inter-service
communication patterns.
"""

from .circuit_breaker import CircuitBreaker, CircuitBreakerState
from .client import ACGSServiceClient, ServiceMesh
from .discovery import ServiceDiscovery
from .registry import ServiceConfig, ServiceRegistry

__all__ = [
    "ACGSServiceClient",
    "CircuitBreaker",
    "CircuitBreakerState",
    "ServiceConfig",
    "ServiceDiscovery",
    "ServiceMesh",
    "ServiceRegistry",
]
