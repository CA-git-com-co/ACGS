"""
Rate Limiting Middleware for ACGS-1 Services
Implements intelligent rate limiting with constitutional compliance.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status
from fastapi.middleware.base import BaseHTTPMiddleware


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Enhanced rate limiting middleware with constitutional compliance."""

    def __init__(self, app, requests_per_minute: int = 60, burst_limit: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.request_history: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean old requests (older than 1 minute)
        self._clean_old_requests(client_ip, current_time)

        # Check rate limits
        if self._is_rate_limited(client_ip, current_time):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.requests_per_minute,
                    "window": "60 seconds",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )

        # Record this request
        self.request_history[client_ip].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limiting headers
        remaining = max(
            0, self.requests_per_minute - len(self.request_history[client_ip])
        )
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _clean_old_requests(self, client_ip: str, current_time: float):
        """Remove requests older than 1 minute."""
        cutoff_time = current_time - 60
        while (
            self.request_history[client_ip]
            and self.request_history[client_ip][0] < cutoff_time
        ):
            self.request_history[client_ip].popleft()

    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client is rate limited."""
        request_count = len(self.request_history[client_ip])

        # Check burst limit (requests in last 10 seconds)
        burst_cutoff = current_time - 10
        burst_count = sum(
            1 for req_time in self.request_history[client_ip] if req_time > burst_cutoff
        )

        return (
            request_count >= self.requests_per_minute or burst_count >= self.burst_limit
        )
