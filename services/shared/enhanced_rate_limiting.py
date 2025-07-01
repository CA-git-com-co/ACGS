"""
Enhanced Rate Limiting and Request Queuing
==========================================

Advanced rate limiting and request queuing system to prevent performance degradation
under high concurrent load (currently degrades above 200 concurrent requests).
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable
from collections import defaultdict, deque
from dataclasses import dataclass
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_second: int = 1000
    burst_size: int = 200
    queue_size: int = 500
    timeout_seconds: float = 30.0
    enable_adaptive: bool = True
    min_rps: int = 100
    max_rps: int = 2000


class TokenBucket:
    """
    Token bucket algorithm for rate limiting with burst support.
    """

    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity  # maximum tokens
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False otherwise
        """
        async with self._lock:
            now = time.time()

            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now

            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    async def get_wait_time(self, tokens: int = 1) -> float:
        """Get the time to wait before tokens are available."""
        async with self._lock:
            if self.tokens >= tokens:
                return 0.0

            needed_tokens = tokens - self.tokens
            return needed_tokens / self.rate


class RequestQueue:
    """
    Async request queue with priority support.
    """

    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self.queue = asyncio.Queue(maxsize=max_size)
        self.processing = 0
        self.total_queued = 0
        self.total_processed = 0
        self.total_dropped = 0

    async def enqueue(self, request_id: str, priority: int = 0) -> bool:
        """
        Enqueue a request for processing.

        Args:
            request_id: Unique request identifier
            priority: Request priority (higher = more important)

        Returns:
            True if enqueued, False if queue is full
        """
        try:
            await self.queue.put((priority, time.time(), request_id))
            self.total_queued += 1
            return True
        except asyncio.QueueFull:
            self.total_dropped += 1
            return False

    async def dequeue(self) -> Optional[tuple]:
        """Dequeue the next request."""
        try:
            item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            self.processing += 1
            return item
        except asyncio.TimeoutError:
            return None

    def mark_done(self):
        """Mark a request as processed."""
        self.processing -= 1
        self.total_processed += 1
        self.queue.task_done()

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "queue_size": self.queue.qsize(),
            "processing": self.processing,
            "total_queued": self.total_queued,
            "total_processed": self.total_processed,
            "total_dropped": self.total_dropped,
            "queue_utilization": self.queue.qsize() / self.max_size,
        }


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts limits based on system performance.
    """

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.token_bucket = TokenBucket(config.requests_per_second, config.burst_size)
        self.request_queue = RequestQueue(config.queue_size)

        # Performance tracking
        self.response_times = deque(maxlen=1000)
        self.error_rates = deque(maxlen=100)
        self.current_rps = config.requests_per_second

        # Adaptive adjustment
        self.last_adjustment = time.time()
        self.adjustment_interval = 10.0  # seconds

    async def allow_request(self, request_id: str) -> tuple[bool, Optional[float]]:
        """
        Check if a request should be allowed.

        Args:
            request_id: Unique request identifier

        Returns:
            Tuple of (allowed, wait_time)
        """
        # Try to consume token immediately
        if await self.token_bucket.consume():
            return True, None

        # If adaptive mode is enabled, try queuing
        if self.config.enable_adaptive:
            if await self.request_queue.enqueue(request_id):
                wait_time = await self.token_bucket.get_wait_time()
                return False, wait_time

        # Request rejected
        return False, None

    async def record_response(self, response_time: float, success: bool):
        """Record response metrics for adaptive adjustment."""
        self.response_times.append(response_time)
        self.error_rates.append(0 if success else 1)

        # Perform adaptive adjustment if needed
        await self._adaptive_adjustment()

    async def _adaptive_adjustment(self):
        """Adjust rate limits based on performance metrics."""
        now = time.time()
        if now - self.last_adjustment < self.adjustment_interval:
            return

        if len(self.response_times) < 10:
            return

        # Calculate performance metrics
        avg_response_time = sum(self.response_times) / len(self.response_times)
        error_rate = (
            sum(self.error_rates) / len(self.error_rates) if self.error_rates else 0
        )

        # Adjust rate based on performance
        if avg_response_time > 2.0 or error_rate > 0.05:  # Performance degrading
            new_rps = max(self.config.min_rps, self.current_rps * 0.9)
        elif avg_response_time < 0.5 and error_rate < 0.01:  # Performance good
            new_rps = min(self.config.max_rps, self.current_rps * 1.1)
        else:
            new_rps = self.current_rps

        if new_rps != self.current_rps:
            self.current_rps = new_rps
            self.token_bucket.rate = new_rps
            logger.info(f"Adaptive rate limit adjusted to {new_rps} RPS")

        self.last_adjustment = now

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times
            else 0
        )
        error_rate = (
            sum(self.error_rates) / len(self.error_rates) if self.error_rates else 0
        )

        return {
            "current_rps": self.current_rps,
            "configured_rps": self.config.requests_per_second,
            "avg_response_time": avg_response_time,
            "error_rate": error_rate,
            "queue_stats": self.request_queue.get_stats(),
            "adaptive_enabled": self.config.enable_adaptive,
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting and request queuing.
    """

    def __init__(self, app, config: RateLimitConfig = None):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.rate_limiter = AdaptiveRateLimiter(self.config)
        self.request_counter = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        start_time = time.time()
        request_id = f"req_{self.request_counter}_{int(start_time * 1000)}"
        self.request_counter += 1

        # Check rate limit
        allowed, wait_time = await self.rate_limiter.allow_request(request_id)

        if not allowed:
            if wait_time is not None and wait_time < self.config.timeout_seconds:
                # Request queued, wait for processing
                await asyncio.sleep(min(wait_time, 1.0))  # Cap wait time
                allowed, _ = await self.rate_limiter.allow_request(request_id)

            if not allowed:
                # Request rejected
                return Response(
                    content='{"error": "Rate limit exceeded", "retry_after": 1}',
                    status_code=429,
                    headers={"Retry-After": "1", "Content-Type": "application/json"},
                )

        # Process request
        try:
            response = await call_next(request)
            success = response.status_code < 400

            # Record metrics
            response_time = time.time() - start_time
            await self.rate_limiter.record_response(response_time, success)

            # Add rate limit headers
            stats = self.rate_limiter.get_stats()
            response.headers["X-RateLimit-Limit"] = str(int(stats["current_rps"]))
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, int(stats["current_rps"] - stats["queue_stats"]["processing"]))
            )
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + 1))

            return response

        except Exception as e:
            # Record error
            response_time = time.time() - start_time
            await self.rate_limiter.record_response(response_time, False)
            raise


def add_rate_limiting(app, config: RateLimitConfig = None):
    """Add rate limiting middleware to FastAPI app."""
    app.add_middleware(RateLimitMiddleware, config=config)
    logger.info("Rate limiting middleware added")


# Service-specific rate limit configurations
SERVICE_RATE_CONFIGS = {
    "ac": RateLimitConfig(requests_per_second=1200, burst_size=300, queue_size=600),
    "auth": RateLimitConfig(requests_per_second=1500, burst_size=400, queue_size=500),
    "gs": RateLimitConfig(requests_per_second=1000, burst_size=250, queue_size=400),
    "pgc": RateLimitConfig(requests_per_second=800, burst_size=200, queue_size=300),
    "integrity": RateLimitConfig(
        requests_per_second=600, burst_size=150, queue_size=250
    ),
    "fv": RateLimitConfig(requests_per_second=400, burst_size=100, queue_size=200),
    "ec": RateLimitConfig(requests_per_second=300, burst_size=75, queue_size=150),
}

# Export key components
__all__ = [
    "RateLimitConfig",
    "AdaptiveRateLimiter",
    "RateLimitMiddleware",
    "add_rate_limiting",
    "SERVICE_RATE_CONFIGS",
]
