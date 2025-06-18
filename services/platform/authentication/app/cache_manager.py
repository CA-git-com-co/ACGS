"""
Cache Manager for Auth Service - ACGS-1 Phase A3 Advanced Caching
Implements service-specific caching strategies for authentication operations
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Any

import structlog
from fastapi import Request

from services.shared.advanced_redis_client import (
    CACHE_TTL_POLICIES,
    AdvancedRedisClient,
    CacheConfig,
    cache_result,
    get_redis_client,
)

logger = structlog.get_logger(__name__)


class AuthCacheManager:
    """Cache manager for authentication service operations."""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.service_name = "auth_service"
        self.redis_client: AdvancedRedisClient | None = None
        self._initialized = False

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize cache manager."""
        if self._initialized:
            return

        try:
            # Configure Redis for auth service
            config = CacheConfig(
                redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/1"),  # Use DB 1 for auth
                redis_password=os.getenv("REDIS_PASSWORD", ""),
                max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
                health_check_interval=int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30")),
            )

            self.redis_client = await get_redis_client(self.service_name, config)
            self._initialized = True

            logger.info("Auth cache manager initialized")

        except Exception as e:
            logger.error("Failed to initialize auth cache manager", error=str(e))
            raise

    async def cache_user_session(
        self, user_id: str, session_data: dict[str, Any], ttl: int | None = None
    ) -> bool:
        """Cache user session data."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"user_session:{user_id}"
        session_ttl = ttl or CACHE_TTL_POLICIES["user_sessions"]

        return await self.redis_client.set(
            cache_key, session_data, ttl=session_ttl, prefix="sessions"
        )

    async def get_user_session(self, user_id: str) -> dict[str, Any] | None:
        """Get cached user session data."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"user_session:{user_id}"
        return await self.redis_client.get(cache_key, prefix="sessions")

    async def invalidate_user_session(self, user_id: str) -> bool:
        """Invalidate user session cache."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"user_session:{user_id}"
        return await self.redis_client.delete(cache_key, prefix="sessions")

    async def cache_auth_token(
        self, token_hash: str, token_data: dict[str, Any], ttl: int | None = None
    ) -> bool:
        """Cache authentication token data."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"auth_token:{token_hash}"
        token_ttl = ttl or CACHE_TTL_POLICIES["auth_tokens"]

        return await self.redis_client.set(
            cache_key, token_data, ttl=token_ttl, prefix="tokens"
        )

    async def get_auth_token(self, token_hash: str) -> dict[str, Any] | None:
        """Get cached authentication token data."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"auth_token:{token_hash}"
        return await self.redis_client.get(cache_key, prefix="tokens")

    async def invalidate_auth_token(self, token_hash: str) -> bool:
        """Invalidate authentication token cache."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"auth_token:{token_hash}"
        return await self.redis_client.delete(cache_key, prefix="tokens")

    async def cache_user_permissions(
        self, user_id: str, permissions: list[str], ttl: int | None = None
    ) -> bool:
        """Cache user permissions."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"user_permissions:{user_id}"
        permissions_ttl = ttl or CACHE_TTL_POLICIES["user_sessions"]

        return await self.redis_client.set(
            cache_key, permissions, ttl=permissions_ttl, prefix="permissions"
        )

    async def get_user_permissions(self, user_id: str) -> list[str] | None:
        """Get cached user permissions."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"user_permissions:{user_id}"
        return await self.redis_client.get(cache_key, prefix="permissions")

    async def invalidate_user_permissions(self, user_id: str) -> bool:
        """Invalidate user permissions cache."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"user_permissions:{user_id}"
        return await self.redis_client.delete(cache_key, prefix="permissions")

    async def cache_rate_limit(
        self, identifier: str, count: int, window_seconds: int
    ) -> bool:
        """Cache rate limiting data."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"rate_limit:{identifier}"

        return await self.redis_client.set(
            cache_key,
            {"count": count, "timestamp": datetime.utcnow().isoformat()},
            ttl=window_seconds,
            prefix="rate_limits",
        )

    async def get_rate_limit(self, identifier: str) -> dict[str, Any] | None:
        """Get cached rate limiting data."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"rate_limit:{identifier}"
        return await self.redis_client.get(cache_key, prefix="rate_limits")

    async def increment_rate_limit(self, identifier: str, window_seconds: int) -> int:
        """Increment rate limit counter."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"acgs:auth_service:rate_limits:rate_limit:{identifier}"

        try:
            # Use Redis INCR for atomic increment
            current_count = await self.redis_client.redis_client.incr(cache_key)

            # Set expiration on first increment
            if current_count == 1:
                await self.redis_client.redis_client.expire(cache_key, window_seconds)

            return current_count

        except Exception as e:
            logger.error(
                "Rate limit increment error", identifier=identifier, error=str(e)
            )
            return 0

    async def warm_cache(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Warm cache with frequently accessed data."""
        if not self.redis_client:
            await self.initialize()

        try:
            # Pre-load common configuration data
            config_data = {
                "jwt_algorithm": "HS256",
                "token_expire_minutes": 30,
                "refresh_expire_days": 7,
                "rate_limit_requests": 100,
                "rate_limit_window": 3600,
            }

            await self.redis_client.set(
                "auth_config",
                config_data,
                ttl=CACHE_TTL_POLICIES["static_configuration"],
                prefix="config",
            )

            logger.info("Auth cache warmed successfully")

        except Exception as e:
            logger.error("Cache warming failed", error=str(e))

    async def get_cache_metrics(self) -> dict[str, Any]:
        """Get cache performance metrics."""
        if not self.redis_client:
            await self.initialize()

        metrics = await self.redis_client.get_metrics()

        return {
            "service": self.service_name,
            "total_requests": metrics.total_requests,
            "cache_hits": metrics.cache_hits,
            "cache_misses": metrics.cache_misses,
            "hit_rate": metrics.hit_rate,
            "errors": metrics.errors,
            "avg_response_time_ms": metrics.avg_response_time_ms,
            "memory_usage_bytes": metrics.memory_usage_bytes,
            "active_connections": metrics.active_connections,
        }


# Global cache manager instance
_auth_cache_manager: AuthCacheManager | None = None


async def get_auth_cache_manager() -> AuthCacheManager:
    """Get or create auth cache manager."""
    global _auth_cache_manager
    if _auth_cache_manager is None:
        _auth_cache_manager = AuthCacheManager()
        await _auth_cache_manager.initialize()
    return _auth_cache_manager


# Cache decorators for auth service
def cache_auth_result(ttl: int | None = None, cache_type: str = "auth_tokens"):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Decorator for caching auth service results."""
    return cache_result(
        ttl=ttl, key_prefix="auth", cache_type=cache_type, service_name="auth_service"
    )


def generate_request_cache_key(
    request: Request, additional_params: dict[str, Any] = None
) -> str:
    """Generate cache key from request parameters."""
    key_data = {
        "path": request.url.path,
        "method": request.method,
        "query_params": dict(request.query_params),
    }

    if additional_params:
        key_data.update(additional_params)

    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()
