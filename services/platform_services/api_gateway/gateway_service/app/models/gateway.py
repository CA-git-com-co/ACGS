"""
Gateway Data Models

Core data models for API gateway operations, service endpoints,
and health monitoring with constitutional compliance.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ServiceStatus(str, Enum):
    """Service health status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class RequestMethod(str, Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class GatewayRequest(BaseModel):
    """Gateway request model."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Request details
    method: RequestMethod = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    query_params: Dict[str, str] = Field(
        default_factory=dict, description="Query parameters"
    )
    body: Optional[str] = Field(None, description="Request body")

    # Client information
    client_ip: str = Field(..., description="Client IP address")
    user_agent: str = Field(default="", description="User agent")

    # Authentication
    auth_token: Optional[str] = Field(None, description="Authentication token")
    user_id: Optional[str] = Field(None, description="Authenticated user ID")

    # Constitutional compliance
    constitutional_compliance_required: bool = Field(default=True)

    # Metadata
    received_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class GatewayResponse(BaseModel):
    """Gateway response model."""

    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="Associated request ID")

    # Response details
    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(
        default_factory=dict, description="Response headers"
    )
    body: Optional[str] = Field(None, description="Response body")

    # Routing information
    target_service: str = Field(..., description="Target service name")
    service_instance: str = Field(..., description="Service instance ID")

    # Performance metrics
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    upstream_time_ms: float = Field(..., description="Upstream service time")

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)

    # Metadata
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ServiceEndpoint(BaseModel):
    """Service endpoint configuration."""

    endpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Service details
    service_name: str = Field(..., description="Service name")
    host: str = Field(..., description="Service host")
    port: int = Field(..., ge=1, le=65535, description="Service port")
    protocol: str = Field(default="http", description="Protocol (http/https)")

    # Endpoint configuration
    path_prefix: str = Field(default="/", description="Path prefix for routing")
    health_check_path: str = Field(
        default="/health", description="Health check endpoint"
    )

    # Load balancing
    weight: int = Field(default=100, ge=0, le=1000, description="Load balancing weight")
    max_connections: int = Field(default=1000, ge=1, description="Maximum connections")

    # Constitutional compliance
    constitutional_compliance_required: bool = Field(default=True)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    @property
    def base_url(self) -> str:
        """Get base URL for the service."""
        return f"{self.protocol}://{self.host}:{self.port}"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ServiceHealth(BaseModel):
    """Service health status."""

    health_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = Field(..., description="Service name")
    endpoint_id: str = Field(..., description="Service endpoint ID")

    # Health status
    status: ServiceStatus = Field(..., description="Health status")
    healthy: bool = Field(..., description="Whether service is healthy")

    # Health metrics
    response_time_ms: float = Field(..., description="Health check response time")
    last_check_at: datetime = Field(default_factory=datetime.utcnow)
    consecutive_failures: int = Field(
        default=0, description="Consecutive health check failures"
    )

    # Service metrics
    active_connections: int = Field(default=0, description="Active connections")
    requests_per_second: float = Field(default=0.0, description="Requests per second")
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Error rate")

    # Constitutional compliance
    constitutional_compliance_active: bool = Field(default=True)

    # Health details
    health_details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional health info"
    )

    # Metadata
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RouteConfig(BaseModel):
    """Route configuration for API gateway."""

    route_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Route matching
    path_pattern: str = Field(..., description="Path pattern for matching")
    methods: List[RequestMethod] = Field(
        default_factory=list, description="Allowed HTTP methods"
    )
    host_pattern: Optional[str] = Field(None, description="Host pattern for matching")

    # Target service
    target_service: str = Field(..., description="Target service name")
    target_path: Optional[str] = Field(None, description="Target path (if different)")

    # Route configuration
    timeout_ms: int = Field(
        default=30000, ge=1000, le=300000, description="Request timeout"
    )
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Retry attempts")

    # Security
    auth_required: bool = Field(default=True, description="Authentication required")
    rate_limit_rpm: Optional[int] = Field(
        None, ge=1, description="Rate limit per minute"
    )

    # Constitutional compliance
    constitutional_compliance_required: bool = Field(default=True)

    # Metadata
    enabled: bool = Field(default=True, description="Whether route is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
