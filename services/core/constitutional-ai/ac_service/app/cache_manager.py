"""
Cache Manager for ac_service - ACGS-1 Phase A3 Advanced Caching
"""

import os
from typing import Any

import structlog

from services.shared.advanced_redis_client import (
    AdvancedRedisClient,
    CacheConfig,
    get_redis_client,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = structlog.get_logger(__name__)


class Ac_serviceCacheManager:
    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.service_name = "ac_service"
        self.redis_client: AdvancedRedisClient | None = None
        self._initialized = False

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        if self._initialized:
            return

        try:
            config = CacheConfig(
                redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                redis_password=os.getenv("REDIS_PASSWORD", ""),
                max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            )

            self.redis_client = await get_redis_client(self.service_name, config)
            self._initialized = True
            logger.info("Ac_service cache manager initialized")

        except Exception as e:
            logger.error("Failed to initialize cache manager", error=str(e))
            raise

    async def get_cache_metrics(self) -> dict[str, Any]:
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
        }


_cache_manager: Ac_serviceCacheManager | None = None


async def get_cache_manager() -> Ac_serviceCacheManager:
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = Ac_serviceCacheManager()
        await _cache_manager.initialize()
    return _cache_manager
