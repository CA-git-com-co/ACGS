"""
API Gateway Models
Constitutional Hash: cdd01ef066bc6cf2

Data models for API gateway functionality including rate limiting,
authentication, routing, and traffic management.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class RateLimitRule(BaseModel):
    """Rate limiting rule"""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    pattern: str  # URL pattern to match
    requests_per_minute: int = 100
    burst_allowance: int = 20
    window_size_seconds: int = 60
    enabled: bool = True
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RateLimitBucket(BaseModel):
    """Rate limit bucket for tracking requests"""
    client_id: str
    endpoint: str
    requests_count: int = 0
    last_request_time: datetime = Field(default_factory=datetime.utcnow)
    window_start: datetime = Field(default_factory=datetime.utcnow)
    blocked_until: Optional[datetime] = None

class APIPolicy(BaseModel):
    """API access policy"""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    rules: List[str] = []  # Rule expressions
    endpoints: List[str] = []  # Applicable endpoints
    user_roles: List[str] = []  # Required user roles
    rate_limits: Dict[str, int] = {}  # Custom rate limits
    enabled: bool = True
    priority: int = Field(ge=0, le=100, default=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuthPolicy(BaseModel):
    """Authentication policy"""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    auth_required: bool = True
    allowed_roles: List[str] = []
    require_mfa: bool = False
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 10
    ip_whitelist: List[str] = []
    ip_blacklist: List[str] = []
    constitutional_clearance_required: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SecurityPolicy(BaseModel):
    """Security policy configuration"""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    block_suspicious_ips: bool = True
    require_https: bool = True
    constitutional_hash_validation: bool = True
    max_request_size_mb: int = 10
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    blocked_user_agents: List[str] = []
    rate_limit_violations_before_block: int = 5
    ddos_protection_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CachePolicy(BaseModel):
    """Caching policy"""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    cache_enabled: bool = True
    ttl_seconds: int = 300
    cache_key_pattern: str = "{method}:{path}:{query}"
    cache_headers: List[str] = ["content-type", "content-length"]
    no_cache_patterns: List[str] = ["/auth/*", "/logout", "/health"]
    vary_on_headers: List[str] = ["authorization", "accept-language"]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LoadBalancingPolicy(BaseModel):
    """Load balancing policy"""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str
    algorithm: str = "round_robin"  # round_robin, least_connections, weighted, ip_hash
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: int = 5
    health_check_path: str = "/health"
    max_retries: int = 3
    retry_delay_seconds: int = 1
    circuit_breaker_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ServiceRoute(BaseModel):
    """Service routing configuration"""
    route_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pattern: str  # URL pattern
    service_name: str
    backend_url: str
    timeout_seconds: int = 30
    retries: int = 3
    auth_required: bool = True
    rate_limit_override: Optional[int] = None
    cache_enabled: bool = True
    load_balancing: bool = False
    circuit_breaker_enabled: bool = True
    request_transformation: Optional[Dict[str, Any]] = None
    response_transformation: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CircuitBreakerState(BaseModel):
    """Circuit breaker state"""
    service_name: str
    state: str = "closed"  # closed, open, half_open
    failure_count: int = 0
    consecutive_failures: int = 0
    failure_threshold: int = 5
    timeout_seconds: int = 60
    last_failure_time: float = 0.0
    last_request_time: float = 0.0
    success_count: int = 0
    total_requests: int = 0

class TrafficMetrics(BaseModel):
    """Traffic metrics"""
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str
    endpoint: str
    method: str
    request_count: int = 0
    error_count: int = 0
    total_response_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    bytes_sent: int = 0
    bytes_received: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RequestLog(BaseModel):
    """Request log entry"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_ip: str
    user_id: Optional[str] = None
    method: str
    path: str
    query_string: Optional[str] = None
    user_agent: str
    request_size_bytes: int = 0
    response_size_bytes: int = 0
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    service_name: Optional[str] = None
    error_message: Optional[str] = None
    rate_limited: bool = False
    cached_response: bool = False
    constitutional_hash: str = CONSTITUTIONAL_HASH
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GatewayConfig(BaseModel):
    """Gateway configuration"""
    config_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gateway_name: str = "ACGS-2 API Gateway"
    version: str = "1.0.0"
    rate_limiting_enabled: bool = True
    authentication_enabled: bool = True
    caching_enabled: bool = True
    circuit_breaker_enabled: bool = True
    load_balancing_enabled: bool = True
    request_logging_enabled: bool = True
    metrics_collection_enabled: bool = True
    security_scanning_enabled: bool = True
    default_timeout_seconds: int = 30
    max_request_size_mb: int = 10
    cors_enabled: bool = True
    cors_origins: List[str] = ["*"]
    constitutional_compliance_required: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)

class APIKey(BaseModel):
    """API key for service access"""
    key_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    api_key: str
    name: str
    description: Optional[str] = None
    user_id: Optional[str] = None
    service_name: Optional[str] = None
    permissions: List[str] = []
    rate_limit_override: Optional[int] = None
    ip_restrictions: List[str] = []
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ServiceHealth(BaseModel):
    """Backend service health status"""
    service_name: str
    status: str = "unknown"  # healthy, unhealthy, degraded, unknown
    response_time_ms: float = 0.0
    last_check: datetime = Field(default_factory=datetime.utcnow)
    consecutive_failures: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class RequestTransformation(BaseModel):
    """Request transformation rule"""
    transformation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    applies_to_patterns: List[str] = []
    header_transformations: Dict[str, str] = {}
    query_transformations: Dict[str, str] = {}
    body_transformations: Dict[str, Any] = {}
    add_headers: Dict[str, str] = {}
    remove_headers: List[str] = []
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResponseTransformation(BaseModel):
    """Response transformation rule"""
    transformation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    applies_to_patterns: List[str] = []
    applies_to_status_codes: List[int] = []
    header_transformations: Dict[str, str] = {}
    body_transformations: Dict[str, Any] = {}
    add_headers: Dict[str, str] = {}
    remove_headers: List[str] = []
    content_filtering: Dict[str, Any] = {}
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GatewayAlert(BaseModel):
    """Gateway alert"""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str  # rate_limit_exceeded, service_down, high_error_rate
    severity: str = "medium"  # low, medium, high, critical
    service_name: Optional[str] = None
    message: str
    details: Dict[str, Any] = {}
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None

class GatewayStatistics(BaseModel):
    """Gateway statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    cached_responses: int = 0
    average_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    bytes_transferred: int = 0
    unique_clients: int = 0
    active_connections: int = 0
    circuit_breaker_activations: int = 0
    security_violations: int = 0
    uptime_percentage: float = 100.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)