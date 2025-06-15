"""Common type definitions for ACGS service-mesh.
Splitting these out avoids circular imports between discovery.py and
failover_circuit_breaker.py
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ServiceType(str, Enum):
    AUTH = "auth"
    AC = "ac"
    INTEGRITY = "integrity"
    FV = "formal_verification"
    GS = "governance_synthesis"
    PGC = "policy_governance"
    EC = "evolutionary_computation"


class ServiceWeight(Enum):
    """Service weight categories for load balancing."""

    LOW = 50
    NORMAL = 100
    HIGH = 150
    CRITICAL = 200


class LoadBalancingStrategy(Enum):
    """Load balancing strategies for service selection."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    CONSISTENT_HASH = "consistent_hash"
    RANDOM = "random"


@dataclass
class ServiceInstance:
    """Represents a discovered service instance with load balancing capabilities."""

    service_type: ServiceType
    instance_id: str
    base_url: str
    port: int
    health_url: str
    status: str = "unknown"  # healthy, unhealthy, unknown
    last_check: Optional[float] = None
    response_time: Optional[float] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    # Load balancing attributes
    weight: int = ServiceWeight.NORMAL.value
    current_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    last_selected: Optional[float] = None
    priority: int = 1  # Lower number = higher priority

    @property
    def is_healthy(self) -> bool:
        """Check if service instance is healthy."""
        return self.status == "healthy"

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this instance."""
        if self.total_requests == 0:
            return 1.0
        return (self.total_requests - self.failed_requests) / self.total_requests

    @property
    def load_factor(self) -> float:
        """Calculate current load factor (0.0 to 1.0)."""
        # Simple load factor based on current connections and weight
        max_connections = self.weight * 2  # Assume weight * 2 as max capacity
        return min(self.current_connections / max_connections, 1.0)

    def increment_connections(self):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
        """Increment current connection count."""
        self.current_connections += 1
        self.total_requests += 1
        self.last_selected = time.time()

    def decrement_connections(self):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
        """Decrement current connection count."""
        self.current_connections = max(0, self.current_connections - 1)

    def record_failure(self):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
        """Record a failed request."""
        self.failed_requests += 1
