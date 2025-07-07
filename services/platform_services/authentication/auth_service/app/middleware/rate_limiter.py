"""
Advanced Rate Limiting for ACGS Auth Service

Provides sophisticated rate limiting with multiple algorithms,
user-based limits, and adaptive protection against attacks.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

import redis.asyncio as redis

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms."""

    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests: int  # Number of requests allowed
    window: int  # Time window in seconds
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    burst_limit: Optional[int] = None  # Burst allowance
    block_duration: int = 300  # Block duration in seconds


class AdvancedRateLimiter:
    """Advanced rate limiter with multiple algorithms and Redis support."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client: Optional[redis.Redis] = None
        self.redis_url = redis_url

        # In-memory storage for when Redis is not available
        self.memory_store = defaultdict(deque)
        self.blocked_ips = {}
        self.token_buckets = {}

        # Default configurations
        self.endpoint_configs = {
            "/api/v1/auth/login": RateLimitConfig(
                requests=5,
                window=300,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
                block_duration=600,  # 10 minutes for failed logins
            ),
            "/api/v1/auth/token": RateLimitConfig(
                requests=5,
                window=300,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
                block_duration=600,
            ),
            "/api/v1/auth/validate": RateLimitConfig(
                requests=100,
                window=60,
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                burst_limit=20,
            ),
            "/api/v1/auth/refresh": RateLimitConfig(
                requests=10, window=300, algorithm=RateLimitAlgorithm.SLIDING_WINDOW
            ),
            "/api/v1/auth/logout": RateLimitConfig(
                requests=20, window=60, algorithm=RateLimitAlgorithm.FIXED_WINDOW
            ),
            "default": RateLimitConfig(
                requests=20, window=60, algorithm=RateLimitAlgorithm.SLIDING_WINDOW
            ),
        }

        # User-specific limits (higher for authenticated users)
        self.user_configs = {
            "authenticated": RateLimitConfig(
                requests=200,
                window=60,
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                burst_limit=50,
            ),
            "admin": RateLimitConfig(
                requests=500,
                window=60,
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                burst_limit=100,
            ),
        }

    async def initialize(self):
        """Initialize Redis connection if available."""
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("Rate limiter connected to Redis")
            except Exception as e:
                logger.warning(
                    f"Failed to connect to Redis: {e}. Using in-memory storage."
                )
                self.redis_client = None

    async def is_allowed(
        self,
        client_ip: str,
        endpoint: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limits.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = time.time()

        # Check if IP is currently blocked
        if await self._is_ip_blocked(client_ip, now):
            return False, {
                "error": "IP temporarily blocked",
                "retry_after": await self._get_block_remaining_time(client_ip, now),
            }

        # Get appropriate configuration
        config = self._get_rate_limit_config(endpoint, user_role)

        # Create rate limit key
        key = self._create_rate_limit_key(client_ip, endpoint, user_id)

        # Apply rate limiting based on algorithm
        if config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            allowed, info = await self._sliding_window_check(key, config, now)
        elif config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            allowed, info = await self._token_bucket_check(key, config, now)
        else:  # FIXED_WINDOW
            allowed, info = await self._fixed_window_check(key, config, now)

        # If not allowed, potentially block IP
        if not allowed:
            await self._handle_rate_limit_violation(client_ip, endpoint, config, now)

        return allowed, info

    def _get_rate_limit_config(
        self, endpoint: str, user_role: Optional[str] = None
    ) -> RateLimitConfig:
        """Get rate limit configuration for endpoint and user."""
        # User-specific limits take precedence
        if user_role and user_role in self.user_configs:
            return self.user_configs[user_role]

        # Endpoint-specific limits
        return self.endpoint_configs.get(endpoint, self.endpoint_configs["default"])

    def _create_rate_limit_key(
        self, client_ip: str, endpoint: str, user_id: Optional[str] = None
    ) -> str:
        """Create unique key for rate limiting."""
        if user_id:
            return f"rate_limit:user:{user_id}:{endpoint}"
        return f"rate_limit:ip:{client_ip}:{endpoint}"

    async def _sliding_window_check(
        self, key: str, config: RateLimitConfig, now: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """Sliding window rate limit check."""
        if self.redis_client:
            return await self._redis_sliding_window_check(key, config, now)
        else:
            return await self._memory_sliding_window_check(key, config, now)

    async def _redis_sliding_window_check(
        self, key: str, config: RateLimitConfig, now: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """Redis-based sliding window implementation."""
        try:
            pipe = self.redis_client.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, now - config.window)

            # Count current requests
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(now): now})

            # Set expiration
            pipe.expire(key, config.window)

            results = await pipe.execute()
            current_count = results[1]

            if current_count >= config.requests:
                # Remove the request we just added since it's not allowed
                await self.redis_client.zrem(key, str(now))

                return False, {
                    "error": "Rate limit exceeded",
                    "limit": config.requests,
                    "window": config.window,
                    "current": current_count,
                    "retry_after": config.window,
                }

            return True, {
                "limit": config.requests,
                "window": config.window,
                "current": current_count + 1,
                "remaining": config.requests - current_count - 1,
            }

        except Exception as e:
            logger.error(f"Redis sliding window error: {e}")
            return await self._memory_sliding_window_check(key, config, now)

    async def _memory_sliding_window_check(
        self, key: str, config: RateLimitConfig, now: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """Memory-based sliding window implementation."""
        requests = self.memory_store[key]

        # Remove old requests
        while requests and requests[0] < now - config.window:
            requests.popleft()

        if len(requests) >= config.requests:
            return False, {
                "error": "Rate limit exceeded",
                "limit": config.requests,
                "window": config.window,
                "current": len(requests),
                "retry_after": config.window,
            }

        # Add current request
        requests.append(now)

        return True, {
            "limit": config.requests,
            "window": config.window,
            "current": len(requests),
            "remaining": config.requests - len(requests),
        }

    async def _token_bucket_check(
        self, key: str, config: RateLimitConfig, now: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """Token bucket rate limit check."""
        if self.redis_client:
            return await self._redis_token_bucket_check(key, config, now)
        else:
            return await self._memory_token_bucket_check(key, config, now)

    async def _memory_token_bucket_check(
        self, key: str, config: RateLimitConfig, now: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """Memory-based token bucket implementation."""
        if key not in self.token_buckets:
            self.token_buckets[key] = {"tokens": config.requests, "last_refill": now}

        bucket = self.token_buckets[key]

        # Calculate tokens to add
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * (config.requests / config.window)

        # Refill bucket
        bucket["tokens"] = min(config.requests, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

        # Check if request is allowed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, {
                "limit": config.requests,
                "window": config.window,
                "tokens_remaining": int(bucket["tokens"]),
            }

        return False, {
            "error": "Rate limit exceeded",
            "limit": config.requests,
            "window": config.window,
            "tokens_remaining": 0,
            "retry_after": int(
                (1 - bucket["tokens"]) * (config.window / config.requests)
            ),
        }

    async def _redis_token_bucket_check(
        self, key: str, config: RateLimitConfig, now: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """Redis-based token bucket implementation."""
        try:
            # Lua script for atomic token bucket operation
            lua_script = """
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            
            local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
            local tokens = tonumber(bucket[1]) or capacity
            local last_refill = tonumber(bucket[2]) or now
            
            local time_passed = now - last_refill
            local tokens_to_add = time_passed * refill_rate
            tokens = math.min(capacity, tokens + tokens_to_add)
            
            if tokens >= 1 then
                tokens = tokens - 1
                redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
                redis.call('EXPIRE', key, 3600)
                return {1, tokens}
            else
                redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
                redis.call('EXPIRE', key, 3600)
                return {0, tokens}
            end
            """

            refill_rate = config.requests / config.window
            result = await self.redis_client.eval(
                lua_script, 1, key, config.requests, refill_rate, now
            )

            allowed = bool(result[0])
            tokens_remaining = result[1]

            if allowed:
                return True, {
                    "limit": config.requests,
                    "window": config.window,
                    "tokens_remaining": int(tokens_remaining),
                }
            else:
                return False, {
                    "error": "Rate limit exceeded",
                    "limit": config.requests,
                    "window": config.window,
                    "tokens_remaining": int(tokens_remaining),
                    "retry_after": int(
                        (1 - tokens_remaining) * (config.window / config.requests)
                    ),
                }

        except Exception as e:
            logger.error(f"Redis token bucket error: {e}")
            return await self._memory_token_bucket_check(key, config, now)

    async def _fixed_window_check(
        self, key: str, config: RateLimitConfig, now: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """Fixed window rate limit check."""
        window_start = int(now // config.window) * config.window
        window_key = f"{key}:{window_start}"

        if self.redis_client:
            try:
                current_count = await self.redis_client.incr(window_key)
                if current_count == 1:
                    await self.redis_client.expire(window_key, config.window)

                if current_count > config.requests:
                    return False, {
                        "error": "Rate limit exceeded",
                        "limit": config.requests,
                        "window": config.window,
                        "current": current_count,
                        "retry_after": config.window - (now - window_start),
                    }

                return True, {
                    "limit": config.requests,
                    "window": config.window,
                    "current": current_count,
                    "remaining": config.requests - current_count,
                }

            except Exception as e:
                logger.error(f"Redis fixed window error: {e}")

        # Fallback to memory
        if window_key not in self.memory_store:
            self.memory_store[window_key] = deque([0])

        current_count = self.memory_store[window_key][0] + 1
        self.memory_store[window_key][0] = current_count

        if current_count > config.requests:
            return False, {
                "error": "Rate limit exceeded",
                "limit": config.requests,
                "window": config.window,
                "current": current_count,
                "retry_after": config.window - (now - window_start),
            }

        return True, {
            "limit": config.requests,
            "window": config.window,
            "current": current_count,
            "remaining": config.requests - current_count,
        }

    async def _is_ip_blocked(self, client_ip: str, now: float) -> bool:
        """Check if IP is currently blocked."""
        if self.redis_client:
            try:
                block_until = await self.redis_client.get(f"blocked_ip:{client_ip}")
                if block_until:
                    return float(block_until) > now
            except Exception:
                pass

        # Fallback to memory
        return client_ip in self.blocked_ips and self.blocked_ips[client_ip] > now

    async def _get_block_remaining_time(self, client_ip: str, now: float) -> int:
        """Get remaining block time for IP."""
        if self.redis_client:
            try:
                block_until = await self.redis_client.get(f"blocked_ip:{client_ip}")
                if block_until:
                    return max(0, int(float(block_until) - now))
            except Exception:
                pass

        # Fallback to memory
        if client_ip in self.blocked_ips:
            return max(0, int(self.blocked_ips[client_ip] - now))

        return 0

    async def _handle_rate_limit_violation(
        self, client_ip: str, endpoint: str, config: RateLimitConfig, now: float
    ):
        """Handle rate limit violation by potentially blocking IP."""
        block_until = now + config.block_duration

        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"blocked_ip:{client_ip}", config.block_duration, str(block_until)
                )
            except Exception:
                pass

        # Also store in memory as fallback
        self.blocked_ips[client_ip] = block_until

        logger.warning(
            f"IP {client_ip} blocked for {config.block_duration}s due to rate limit violation on {endpoint}"
        )

    async def unblock_ip(self, client_ip: str):
        """Manually unblock an IP address."""
        if self.redis_client:
            try:
                await self.redis_client.delete(f"blocked_ip:{client_ip}")
            except Exception:
                pass

        if client_ip in self.blocked_ips:
            del self.blocked_ips[client_ip]

        logger.info(f"IP {client_ip} manually unblocked")
