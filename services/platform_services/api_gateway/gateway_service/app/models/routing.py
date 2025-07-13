"""
Routing Data Models

Data models for service routing, load balancing strategies,
and routing decisions with constitutional compliance.
"""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    IP_HASH = "ip_hash"
    HEALTH_BASED = "health_based"


class MatchType(str, Enum):
    """Route matching types."""

    EXACT = "exact"
    PREFIX = "prefix"
    REGEX = "regex"
    WILDCARD = "wildcard"


class ServiceInstance(BaseModel):
    """Service instance for load balancing."""

    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Instance details
    service_name: str = Field(..., description="Service name")
    host: str = Field(..., description="Instance host")
    port: int = Field(..., ge=1, le=65535, description="Instance port")

    # Load balancing
    weight: int = Field(default=100, ge=0, le=1000, description="Load balancing weight")
    current_connections: int = Field(
        default=0, description="Current active connections"
    )
    max_connections: int = Field(default=1000, ge=1, description="Maximum connections")

    # Health status
    healthy: bool = Field(default=True, description="Whether instance is healthy")
    last_health_check: datetime = Field(default_factory=datetime.utcnow)
    consecutive_failures: int = Field(
        default=0, description="Consecutive health check failures"
    )

    # Performance metrics
    average_response_time_ms: float = Field(
        default=0.0, description="Average response time"
    )
    requests_per_second: float = Field(default=0.0, description="Current RPS")
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Error rate")

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    @property
    def base_url(self) -> str:
        """Get base URL for the instance."""
        return f"http://{self.host}:{self.port}"

    @property
    def load_score(self) -> float:
        """Calculate load score for load balancing."""
        if not self.healthy:
            return float("inf")

        # Simple load score based on connections and response time
        connection_ratio = self.current_connections / self.max_connections
        response_penalty = min(
            self.average_response_time_ms / 1000, 1.0
        )  # Cap at 1 second

        return connection_ratio + response_penalty + self.error_rate

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RouteMatch(BaseModel):
    """Route matching criteria."""

    match_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Matching criteria
    path: str | None = Field(None, description="Path to match")
    path_type: MatchType = Field(
        default=MatchType.PREFIX, description="Path matching type"
    )

    method: str | None = Field(None, description="HTTP method to match")
    headers: dict[str, str] = Field(
        default_factory=dict, description="Headers to match"
    )
    query_params: dict[str, str] = Field(
        default_factory=dict, description="Query params to match"
    )

    # Host matching
    host: str | None = Field(None, description="Host to match")
    host_type: MatchType = Field(
        default=MatchType.EXACT, description="Host matching type"
    )

    # Priority and weight
    priority: int = Field(default=100, ge=0, le=1000, description="Route priority")
    weight: int = Field(default=100, ge=0, le=1000, description="Route weight")

    # Constitutional compliance
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RouteRule(BaseModel):
    """Route rule for request routing."""

    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Rule details
    name: str = Field(..., description="Rule name")
    description: str = Field(default="", description="Rule description")

    # Matching criteria
    match: RouteMatch = Field(..., description="Route matching criteria")

    # Target configuration
    target_service: str = Field(..., description="Target service name")
    target_path: str | None = Field(None, description="Target path transformation")

    # Load balancing
    load_balancing_strategy: LoadBalancingStrategy = Field(
        default=LoadBalancingStrategy.ROUND_ROBIN, description="Load balancing strategy"
    )

    # Route configuration
    timeout_ms: int = Field(
        default=30000, ge=1000, le=300000, description="Request timeout"
    )
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Retry attempts")

    # Security and rate limiting
    auth_required: bool = Field(default=True, description="Authentication required")
    rate_limit_rpm: int | None = Field(None, ge=1, description="Rate limit per minute")

    # Constitutional compliance
    constitutional_compliance_required: bool = Field(default=True)

    # Rule status
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RoutingDecision(BaseModel):
    """Routing decision for a request."""

    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="Associated request ID")

    # Routing decision
    matched_rule: RouteRule | None = Field(None, description="Matched route rule")
    target_service: str = Field(..., description="Target service")
    target_instance: ServiceInstance = Field(
        ..., description="Selected service instance"
    )

    # Decision details
    load_balancing_strategy: LoadBalancingStrategy = Field(
        ..., description="Strategy used"
    )
    decision_reason: str = Field(..., description="Reason for routing decision")

    # Performance prediction
    estimated_response_time_ms: float = Field(
        default=0.0, description="Estimated response time"
    )
    confidence_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Decision confidence"
    )

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)

    # Metadata
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
