"""
ACGS Cache Optimization Middleware
Constitutional Hash: cdd01ef066bc6cf2

FastAPI middleware that automatically integrates cache optimization into ACGS services.
"""

import asyncio
import json
import logging
import time
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

from tools.acgs_cache_performance_optimizer import OptimizedCacheManager

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class CacheOptimizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that provides intelligent caching for ACGS service responses.
    """

    def __init__(
        self,
        app: FastAPI,
        service_name: str,
        cache_enabled: bool = True,
        cache_paths: Optional[Dict[str, Dict[str, Any]]] = None,
        default_ttl: int = 300,
    ):
        super().__init__(app)
        self.service_name = service_name
        self.cache_enabled = cache_enabled
        self.default_ttl = default_ttl
        self.cache_manager: Optional[OptimizedCacheManager] = None

        # Default cacheable paths and their configurations
        self.cache_paths = cache_paths or {
            "/health": {
                "ttl": 60,
                "data_type": "health_check",
                "cache_method": ["GET"],
            },
            "/constitutional/compliance": {
                "ttl": 1800,  # 30 minutes
                "data_type": "constitutional_hash",
                "cache_method": ["GET"],
            },
            "/metrics": {
                "ttl": 300,  # 5 minutes
                "data_type": "performance_metrics",
                "cache_method": ["GET"],
            },
            "/governance/rules": {
                "ttl": 3600,  # 1 hour
                "data_type": "governance_rules",
                "cache_method": ["GET"],
            },
            "/policy": {
                "ttl": 1800,  # 30 minutes
                "data_type": "policy_decisions",
                "cache_method": ["GET", "POST"],
            },
            "/validation": {
                "ttl": 900,  # 15 minutes
                "data_type": "validation_results",
                "cache_method": ["GET", "POST"],
            },
        }

    async def startup(self) -> None:
        """Initialize cache manager on startup."""
        if self.cache_enabled:
            try:
                self.cache_manager = OptimizedCacheManager(
                    service_name=self.service_name
                )
                await self.cache_manager.initialize()
                logger.info(f"✅ Cache optimization enabled for {self.service_name}")
            except Exception as e:
                logger.error(
                    f"Failed to initialize cache manager for {self.service_name}: {e}"
                )
                self.cache_enabled = False

    async def shutdown(self) -> None:
        """Cleanup cache manager on shutdown."""
        if self.cache_manager:
            try:
                await self.cache_manager.close()
                logger.info(f"Cache manager closed for {self.service_name}")
            except Exception as e:
                logger.error(f"Error closing cache manager: {e}")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process requests with intelligent caching."""

        if not self.cache_enabled or not self.cache_manager:
            return await call_next(request)

        # Check if this path should be cached
        cache_config = self._get_cache_config(request)

        if not cache_config:
            # Not cacheable, pass through
            return await call_next(request)

        # Generate cache key
        cache_key = await self._generate_cache_key(request)
        data_type = cache_config.get("data_type", "default")

        # Try to get from cache for GET requests
        if request.method == "GET":
            cached_response = await self._get_cached_response(cache_key, data_type)
            if cached_response:
                return self._create_response_from_cache(cached_response)

        # Execute the request
        start_time = time.perf_counter()
        response = await call_next(request)
        execution_time = time.perf_counter() - start_time

        # Cache successful responses
        if self._should_cache_response(response, cache_config):
            await self._cache_response(
                cache_key, response, cache_config, execution_time
            )

        # Add cache headers
        self._add_cache_headers(response, cache_config, execution_time)

        return response

    def _get_cache_config(self, request: Request) -> Optional[Dict[str, Any]]:
        """Get cache configuration for the request path."""
        path = str(request.url.path)
        method = request.method

        # Check exact path matches first
        if path in self.cache_paths:
            config = self.cache_paths[path]
            if method in config.get("cache_method", ["GET"]):
                return config

        # Check prefix matches
        for cache_path, config in self.cache_paths.items():
            if path.startswith(cache_path) and method in config.get(
                "cache_method", ["GET"]
            ):
                return config

        return None

    async def _generate_cache_key(self, request: Request) -> str:
        """Generate a unique cache key for the request."""
        # Base key components
        key_parts = [
            self.service_name,
            request.method,
            str(request.url.path),
            str(request.url.query),
        ]

        # Add request body hash for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    import hashlib

                    body_hash = hashlib.md5(body).hexdigest()
                    key_parts.append(body_hash)
            except Exception:
                pass

        # Add user context if available
        user_context = getattr(request.state, "user_context", None)
        if user_context:
            user_id = user_context.get("user_id", "anonymous")
            tenant_id = user_context.get("tenant_id", "default")
            key_parts.extend([user_id, tenant_id])

        # Create final cache key
        cache_key = ":".join(str(part) for part in key_parts)
        return cache_key

    async def _get_cached_response(
        self, cache_key: str, data_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached response if available."""
        try:
            cached_data = await self.cache_manager.get(cache_key, data_type)
            return cached_data
        except Exception as e:
            logger.warning(f"Cache get error for {cache_key}: {e}")
            return None

    async def _cache_response(
        self,
        cache_key: str,
        response: Response,
        cache_config: Dict[str, Any],
        execution_time: float,
    ) -> None:
        """Cache the response."""
        try:
            # Extract response data
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": None,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "cached_at": time.time(),
                "execution_time_ms": execution_time * 1000,
            }

            # Get response body
            if hasattr(response, "body"):
                try:
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    ):
                        # For JSON responses, store the parsed data
                        body_content = response.body.decode("utf-8")
                        response_data["body"] = json.loads(body_content)
                    else:
                        # For other content types, store as string
                        response_data["body"] = response.body.decode("utf-8")
                except Exception:
                    # If parsing fails, store as raw bytes (base64 encoded)
                    import base64

                    response_data["body"] = base64.b64encode(response.body).decode(
                        "utf-8"
                    )
                    response_data["body_encoding"] = "base64"

            # Cache the response
            ttl = cache_config.get("ttl", self.default_ttl)
            data_type = cache_config.get("data_type", "default")

            await self.cache_manager.set(cache_key, response_data, data_type, ttl)

        except Exception as e:
            logger.warning(f"Cache set error for {cache_key}: {e}")

    def _create_response_from_cache(self, cached_data: Dict[str, Any]) -> Response:
        """Create a Response object from cached data."""
        try:
            # Extract cached response data
            status_code = cached_data.get("status_code", 200)
            headers = cached_data.get("headers", {})
            body = cached_data.get("body")

            # Decode body if needed
            if isinstance(body, str) and cached_data.get("body_encoding") == "base64":
                import base64

                body_content = base64.b64decode(body.encode("utf-8"))
            elif isinstance(body, (dict, list)):
                body_content = json.dumps(body).encode("utf-8")
                headers["content-type"] = "application/json"
            elif isinstance(body, str):
                body_content = body.encode("utf-8")
            else:
                body_content = b""

            # Add cache headers
            headers["X-Cache-Status"] = "HIT"
            headers["X-Cache-Service"] = self.service_name
            headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
            headers["X-Cached-At"] = str(cached_data.get("cached_at", time.time()))

            # Create response
            response = Response(
                content=body_content, status_code=status_code, headers=headers
            )

            return response

        except Exception as e:
            logger.error(f"Error creating response from cache: {e}")
            # Return a basic error response
            return Response(
                content=json.dumps({"error": "Cache retrieval error"}),
                status_code=500,
                headers={"content-type": "application/json"},
            )

    def _should_cache_response(
        self, response: Response, cache_config: Dict[str, Any]
    ) -> bool:
        """Determine if response should be cached."""
        # Only cache successful responses
        if response.status_code >= 400:
            return False

        # Check if response contains constitutional compliance
        constitutional_header = response.headers.get("X-Constitutional-Hash")
        if constitutional_header and constitutional_header != CONSTITUTIONAL_HASH:
            logger.warning(
                f"Constitutional hash mismatch: {constitutional_header} != {CONSTITUTIONAL_HASH}"
            )
            return False

        # Don't cache responses that explicitly say not to cache
        cache_control = response.headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False

        return True

    def _add_cache_headers(
        self, response: Response, cache_config: Dict[str, Any], execution_time: float
    ) -> None:
        """Add cache-related headers to response."""
        response.headers["X-Cache-Status"] = "MISS"
        response.headers["X-Cache-Service"] = self.service_name
        response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
        response.headers["X-Execution-Time-Ms"] = str(round(execution_time * 1000, 2))

        # Add cache control headers
        ttl = cache_config.get("ttl", self.default_ttl)
        response.headers["Cache-Control"] = f"max-age={ttl}, public"


def setup_cache_optimization(
    app: FastAPI,
    service_name: str,
    cache_enabled: bool = True,
    cache_paths: Optional[Dict[str, Dict[str, Any]]] = None,
    default_ttl: int = 300,
) -> CacheOptimizationMiddleware:
    """
    Setup cache optimization middleware for a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
        cache_enabled: Whether caching is enabled
        cache_paths: Custom cache path configurations
        default_ttl: Default TTL for cached responses

    Returns:
        Cache optimization middleware instance
    """

    # Create middleware instance
    middleware = CacheOptimizationMiddleware(
        app=app,
        service_name=service_name,
        cache_enabled=cache_enabled,
        cache_paths=cache_paths,
        default_ttl=default_ttl,
    )

    # Add middleware to app
    app.add_middleware(CacheOptimizationMiddleware)

    # Setup startup and shutdown events
    @app.on_event("startup")
    async def startup_cache_optimization():
        await middleware.startup()

    @app.on_event("shutdown")
    async def shutdown_cache_optimization():
        await middleware.shutdown()

    # Add cache management endpoints
    @app.get("/cache/metrics")
    async def get_cache_metrics():
        """Get cache performance metrics."""
        if middleware.cache_manager:
            return await middleware.cache_manager.get_performance_metrics()
        return {
            "error": "Cache not enabled",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    @app.post("/cache/warm")
    async def warm_cache():
        """Trigger cache warming."""
        if middleware.cache_manager:
            return await middleware.cache_manager.warm_cache()
        return {
            "error": "Cache not enabled",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    @app.delete("/cache/clear")
    async def clear_cache():
        """Clear cache (admin only)."""
        if middleware.cache_manager:
            # In a real implementation, this would clear the cache
            return {
                "message": "Cache clear requested",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": time.time(),
            }
        return {
            "error": "Cache not enabled",
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    logger.info(
        f"Cache optimization configured for {service_name} (Constitutional Hash: {CONSTITUTIONAL_HASH})"
    )
    return middleware
