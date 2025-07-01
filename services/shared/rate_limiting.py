"""
ACGS-1 Phase A3: Production-Grade Rate Limiting and Security Middleware

This module provides comprehensive rate limiting, IP-based throttling,
and security middleware for all ACGS-1 services with Redis backend
and configurable limits per endpoint and user type.
"""

import logging
import time
from enum import Enum
from typing import Any

import redis.asyncio as redis
from fastapi import Request

logger = logging.getLogger(__name__)


class RateLimitType(str, Enum):
    """Rate limit types for different operations."""

    GLOBAL = "global"
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_ENDPOINT = "per_endpoint"
    PER_API_KEY = "per_api_key"


class SecurityThreatLevel(str, Enum):
    """Security threat levels for adaptive rate limiting."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RateLimitConfig:
    """Configuration for rate limiting rules."""

    def __init__(
        self,
        requests_per_minute: int = 100,
        burst_size: int = 20,
        window_size: int = 60,
        block_duration: int = 300,
        threat_multiplier: float = 0.5,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window_size = window_size  # seconds
        self.block_duration = block_duration  # seconds
        self.threat_multiplier = threat_multiplier  # Reduce limits for threats


class RateLimiter:
    """
    Production-grade rate limiter with Redis backend and adaptive security.

    Features:
    - Multiple rate limiting strategies (IP, user, endpoint, API key)
    - Sliding window algorithm for accurate rate limiting
    - Adaptive limits based on threat detection
    - Distributed rate limiting with Redis
    - Configurable per-endpoint limits
    - Automatic IP blocking for abuse
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        service_name: str = "acgs_service",
        default_config: RateLimitConfig | None = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.redis_url = redis_url
        self.service_name = service_name
        self.default_config = default_config or RateLimitConfig()
        self.redis_client: redis.Redis | None = None

        # Endpoint-specific configurations
        self.endpoint_configs: dict[str, RateLimitConfig] = {
            "/auth/login": RateLimitConfig(requests_per_minute=10, burst_size=3),
            "/auth/register": RateLimitConfig(requests_per_minute=5, burst_size=2),
            "/auth/token/refresh": RateLimitConfig(
                requests_per_minute=20, burst_size=5
            ),
            "/api/v1/policies": RateLimitConfig(requests_per_minute=200, burst_size=50),
            "/api/v1/principles": RateLimitConfig(
                requests_per_minute=100, burst_size=25
            ),
            "/api/v1/synthesis": RateLimitConfig(requests_per_minute=30, burst_size=10),
            "/api/v1/verification": RateLimitConfig(
                requests_per_minute=50, burst_size=15
            ),
            "/health": RateLimitConfig(requests_per_minute=1000, burst_size=100),
        }

        # User role-based multipliers
        self.role_multipliers = {
            "admin": 3.0,
            "policy_manager": 2.0,
            "auditor": 1.5,
            "user": 1.0,
            "anonymous": 0.5,
        }

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await self.redis_client.ping()
            logger.info(f"Rate limiter initialized for {self.service_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis for rate limiting: {e}")
            self.redis_client = None

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    def _get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier for rate limiting."""
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Try to get API key from request state
        api_key = getattr(request.state, "api_key", None)
        if api_key:
            return f"api_key:{api_key}"

        # Fall back to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        if request.client:
            return request.client.host

        return "unknown"

    def _get_endpoint_pattern(self, path: str) -> str:
        """Get endpoint pattern for configuration lookup."""
        # Normalize path by removing trailing slashes and query parameters
        normalized_path = path.rstrip("/").split("?")[0]

        # Check for exact matches first
        if normalized_path in self.endpoint_configs:
            return normalized_path

        # Check for pattern matches (e.g., /api/v1/policies/{id})
        for pattern in self.endpoint_configs.keys():
            if self._path_matches_pattern(normalized_path, pattern):
                return pattern

        # Return generic API pattern
        if normalized_path.startswith("/api/"):
            return "/api/*"

        return "*"

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches a pattern with wildcards."""
        if "*" not in pattern:
            return path == pattern

        # Simple wildcard matching
        pattern_parts = pattern.split("*")
        if len(pattern_parts) == 2:
            prefix, suffix = pattern_parts
            return path.startswith(prefix) and path.endswith(suffix)

        return False

    def _get_rate_limit_config(
        self, request: Request, endpoint_pattern: str
    ) -> RateLimitConfig:
        """Get rate limit configuration for request."""
        # Get base configuration
        config = self.endpoint_configs.get(endpoint_pattern, self.default_config)

        # Apply role-based multipliers
        user_role = getattr(request.state, "user_role", "anonymous")
        multiplier = self.role_multipliers.get(user_role, 1.0)

        # Apply threat-based adjustments
        threat_level = getattr(request.state, "threat_level", SecurityThreatLevel.LOW)
        if threat_level in [SecurityThreatLevel.HIGH, SecurityThreatLevel.CRITICAL]:
            multiplier *= config.threat_multiplier

        # Create adjusted configuration
        adjusted_config = RateLimitConfig(
            requests_per_minute=int(config.requests_per_minute * multiplier),
            burst_size=int(config.burst_size * multiplier),
            window_size=config.window_size,
            block_duration=config.block_duration,
            threat_multiplier=config.threat_multiplier,
        )

        return adjusted_config

    async def _is_blocked(self, client_id: str) -> bool:
        """Check if client is currently blocked."""
        if not self.redis_client:
            return False

        block_key = f"{self.service_name}:blocked:{client_id}"
        blocked_until = await self.redis_client.get(block_key)

        if blocked_until:
            if time.time() < float(blocked_until):
                return True
            else:
                # Block expired, remove it
                await self.redis_client.delete(block_key)

        return False

    async def _block_client(self, client_id: str, duration: int):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Block client for specified duration."""
        if not self.redis_client:
            return

        block_key = f"{self.service_name}:blocked:{client_id}"
        block_until = time.time() + duration

        await self.redis_client.setex(block_key, duration, str(block_until))
        logger.warning(f"Blocked client {client_id} for {duration} seconds")

    async def _check_rate_limit(
        self, client_id: str, endpoint_pattern: str, config: RateLimitConfig
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check rate limit using sliding window algorithm.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        if not self.redis_client:
            # If Redis is not available, allow request but log warning
            logger.warning("Redis not available for rate limiting")
            return True, {}

        current_time = time.time()
        window_start = current_time - config.window_size

        # Create keys for different rate limit types
        keys = {
            "requests": f"{self.service_name}:requests:{client_id}:{endpoint_pattern}",
            "burst": f"{self.service_name}:burst:{client_id}:{endpoint_pattern}",
            "violations": f"{self.service_name}:violations:{client_id}",
        }

        # Use Redis pipeline for atomic operations
        pipe = self.redis_client.pipeline()

        # Remove old entries from sliding window
        pipe.zremrangebyscore(keys["requests"], 0, window_start)

        # Count current requests in window
        pipe.zcard(keys["requests"])

        # Get current burst count
        pipe.get(keys["burst"])

        # Execute pipeline
        results = await pipe.execute()
        current_requests = results[1]
        current_burst = int(results[2] or 0)

        # Calculate limits
        requests_per_window = int(config.requests_per_minute * config.window_size / 60)

        # Check burst limit
        if current_burst >= config.burst_size:
            await self._record_violation(client_id, "burst_limit_exceeded")
            return False, {
                "error": "Burst limit exceeded",
                "limit": config.burst_size,
                "current": current_burst,
                "reset_time": current_time + 60,
            }

        # Check window limit
        if current_requests >= requests_per_window:
            await self._record_violation(client_id, "rate_limit_exceeded")
            return False, {
                "error": "Rate limit exceeded",
                "limit": requests_per_window,
                "current": current_requests,
                "window_size": config.window_size,
                "reset_time": current_time + config.window_size,
            }

        # Record this request
        pipe = self.redis_client.pipeline()
        pipe.zadd(keys["requests"], {str(current_time): current_time})
        pipe.expire(keys["requests"], config.window_size * 2)
        pipe.incr(keys["burst"])
        pipe.expire(keys["burst"], 60)  # Burst window is 1 minute
        await pipe.execute()

        return True, {
            "limit": requests_per_window,
            "remaining": requests_per_window - current_requests - 1,
            "reset_time": current_time + config.window_size,
            "burst_limit": config.burst_size,
            "burst_remaining": config.burst_size - current_burst - 1,
        }

    async def _record_violation(self, client_id: str, violation_type: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record rate limit violation and check for blocking."""
        if not self.redis_client:
            return

        violations_key = f"{self.service_name}:violations:{client_id}"
        current_time = time.time()

        # Add violation with timestamp
        await self.redis_client.zadd(
            violations_key, {f"{violation_type}:{current_time}": current_time}
        )

        # Remove old violations (older than 1 hour)
        await self.redis_client.zremrangebyscore(violations_key, 0, current_time - 3600)

        # Count recent violations
        recent_violations = await self.redis_client.zcard(violations_key)

        # Block client if too many violations
        if recent_violations >= 10:  # 10 violations in 1 hour
            await self._block_client(client_id, 3600)  # Block for 1 hour
        elif recent_violations >= 5:  # 5 violations in 1 hour
            await self._block_client(client_id, 900)  # Block for 15 minutes

    async def check_rate_limit(self, request: Request) -> tuple[bool, dict[str, Any]]:
        """
        Main rate limiting check for incoming requests.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        client_id = self._get_client_identifier(request)
        endpoint_pattern = self._get_endpoint_pattern(request.url.path)
        config = self._get_rate_limit_config(request, endpoint_pattern)

        # Check if client is blocked
        if await self._is_blocked(client_id):
            return False, {
                "error": "Client blocked due to abuse",
                "client_id": client_id,
                "retry_after": 3600,
            }

        # Check rate limits
        return await self._check_rate_limit(client_id, endpoint_pattern, config)
