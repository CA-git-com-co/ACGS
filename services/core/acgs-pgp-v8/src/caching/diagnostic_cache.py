"""
Diagnostic Data Cache

Specialized caching for diagnostic results and system health data.
"""

import logging
from datetime import datetime
from typing import Any

from .cache_manager import CacheManager, get_cache_manager

logger = logging.getLogger(__name__)


class DiagnosticDataCache:
    """
    Specialized cache for diagnostic data and system health information.

    Provides intelligent caching for diagnostic results, error classifications,
    and recovery recommendations with health monitoring integration.
    """

    def __init__(self, cache_manager: CacheManager | None = None):
        """Initialize diagnostic data cache."""
        self.cache_manager = cache_manager or get_cache_manager()
        self.cache_prefix = "diagnostic"

        # Cache TTL settings (in seconds)
        self.ttl_settings = {
            "diagnostic_result": 900,  # 15 minutes
            "error_classification": 1800,  # 30 minutes
            "recovery_recommendation": 3600,  # 1 hour
            "system_health": 300,  # 5 minutes
            "error_patterns": 7200,  # 2 hours
        }

        logger.info("Diagnostic data cache initialized")

    async def cache_diagnostic_result(
        self, diagnostic_id: str, result_data: dict[str, Any], ttl: int | None = None
    ) -> bool:
        """
        Cache complete diagnostic result.

        Args:
            diagnostic_id: Unique diagnostic identifier
            result_data: Complete diagnostic result data
            ttl: Time to live in seconds (optional)

        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = f"result:{diagnostic_id}"
        ttl = ttl or self.ttl_settings["diagnostic_result"]

        # Add caching metadata
        cache_data = {
            **result_data,
            "cached_at": datetime.utcnow().isoformat(),
            "cache_ttl": ttl,
            "constitutional_hash": self.cache_manager.constitutional_hash,
        }

        success = await self.cache_manager.set(
            cache_key, cache_data, ttl=ttl, prefix=self.cache_prefix
        )

        if success:
            logger.info(f"✅ Cached diagnostic result: {diagnostic_id}")

            # Cache error classifications separately for pattern analysis
            if "errors_detected" in result_data:
                await self.cache_error_patterns(
                    result_data["target_system"], result_data["errors_detected"]
                )

        return success

    async def get_diagnostic_result(self, diagnostic_id: str) -> dict[str, Any] | None:
        """
        Retrieve cached diagnostic result.

        Args:
            diagnostic_id: Unique diagnostic identifier

        Returns:
            Cached diagnostic data or None if not found
        """
        cache_key = f"result:{diagnostic_id}"

        cached_data = await self.cache_manager.get(cache_key, prefix=self.cache_prefix)

        if cached_data:
            # Validate constitutional hash
            cached_hash = cached_data.get("constitutional_hash")
            if cached_hash != self.cache_manager.constitutional_hash:
                logger.warning(
                    f"Constitutional hash mismatch for cached diagnostic {diagnostic_id}"
                )
                await self.invalidate_diagnostic_result(diagnostic_id)
                return None

            logger.info(f"✅ Retrieved cached diagnostic result: {diagnostic_id}")
            return cached_data

        return None

    async def cache_error_classification(
        self,
        error_signature: str,
        classification_data: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        """
        Cache error classification for reuse.

        Args:
            error_signature: Unique error signature/hash
            classification_data: Error classification data
            ttl: Time to live in seconds (optional)

        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = f"error_class:{error_signature}"
        ttl = ttl or self.ttl_settings["error_classification"]

        cache_data = {
            **classification_data,
            "cached_at": datetime.utcnow().isoformat(),
            "constitutional_hash": self.cache_manager.constitutional_hash,
        }

        success = await self.cache_manager.set(
            cache_key, cache_data, ttl=ttl, prefix=self.cache_prefix
        )

        if success:
            logger.info(f"✅ Cached error classification: {error_signature}")

        return success

    async def get_error_classification(
        self, error_signature: str
    ) -> dict[str, Any] | None:
        """
        Retrieve cached error classification.

        Args:
            error_signature: Unique error signature/hash

        Returns:
            Cached classification data or None if not found
        """
        cache_key = f"error_class:{error_signature}"

        cached_data = await self.cache_manager.get(cache_key, prefix=self.cache_prefix)

        if cached_data:
            logger.info(f"✅ Retrieved cached error classification: {error_signature}")
            return cached_data

        return None

    async def cache_recovery_recommendation(
        self,
        error_category: str,
        recommendation_data: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        """
        Cache recovery recommendation for error category.

        Args:
            error_category: Error category identifier
            recommendation_data: Recovery recommendation data
            ttl: Time to live in seconds (optional)

        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = f"recovery:{error_category}"
        ttl = ttl or self.ttl_settings["recovery_recommendation"]

        cache_data = {
            **recommendation_data,
            "cached_at": datetime.utcnow().isoformat(),
            "constitutional_hash": self.cache_manager.constitutional_hash,
        }

        success = await self.cache_manager.set(
            cache_key, cache_data, ttl=ttl, prefix=self.cache_prefix
        )

        if success:
            logger.info(f"✅ Cached recovery recommendation: {error_category}")

        return success

    async def get_recovery_recommendation(
        self, error_category: str
    ) -> dict[str, Any] | None:
        """
        Retrieve cached recovery recommendation.

        Args:
            error_category: Error category identifier

        Returns:
            Cached recommendation data or None if not found
        """
        cache_key = f"recovery:{error_category}"

        cached_data = await self.cache_manager.get(cache_key, prefix=self.cache_prefix)

        if cached_data:
            logger.info(
                f"✅ Retrieved cached recovery recommendation: {error_category}"
            )
            return cached_data

        return None

    async def cache_system_health(
        self, system_name: str, health_data: dict[str, Any], ttl: int | None = None
    ) -> bool:
        """
        Cache system health status.

        Args:
            system_name: Name of the system
            health_data: System health data
            ttl: Time to live in seconds (optional)

        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = f"health:{system_name}"
        ttl = ttl or self.ttl_settings["system_health"]

        cache_data = {
            **health_data,
            "cached_at": datetime.utcnow().isoformat(),
            "constitutional_hash": self.cache_manager.constitutional_hash,
        }

        success = await self.cache_manager.set(
            cache_key, cache_data, ttl=ttl, prefix=self.cache_prefix
        )

        if success:
            logger.info(f"✅ Cached system health: {system_name}")

        return success

    async def get_system_health(self, system_name: str) -> dict[str, Any] | None:
        """
        Retrieve cached system health status.

        Args:
            system_name: Name of the system

        Returns:
            Cached health data or None if not found
        """
        cache_key = f"health:{system_name}"

        cached_data = await self.cache_manager.get(cache_key, prefix=self.cache_prefix)

        if cached_data:
            logger.info(f"✅ Retrieved cached system health: {system_name}")
            return cached_data

        return None

    async def cache_error_patterns(
        self,
        system_name: str,
        error_list: list[dict[str, Any]],
        ttl: int | None = None,
    ) -> bool:
        """
        Cache error patterns for trend analysis.

        Args:
            system_name: Name of the system
            error_list: List of error data
            ttl: Time to live in seconds (optional)

        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = f"patterns:{system_name}"
        ttl = ttl or self.ttl_settings["error_patterns"]

        # Extract patterns from error list
        patterns = {}
        for error in error_list:
            category = error.get("category", "unknown")
            severity = error.get("severity", "unknown")
            pattern_key = f"{category}:{severity}"

            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    "count": 0,
                    "category": category,
                    "severity": severity,
                    "first_seen": datetime.utcnow().isoformat(),
                    "last_seen": datetime.utcnow().isoformat(),
                }

            patterns[pattern_key]["count"] += 1
            patterns[pattern_key]["last_seen"] = datetime.utcnow().isoformat()

        cache_data = {
            "system_name": system_name,
            "patterns": patterns,
            "total_errors": len(error_list),
            "cached_at": datetime.utcnow().isoformat(),
            "constitutional_hash": self.cache_manager.constitutional_hash,
        }

        success = await self.cache_manager.set(
            cache_key, cache_data, ttl=ttl, prefix=self.cache_prefix
        )

        if success:
            logger.info(f"✅ Cached error patterns: {system_name}")

        return success

    async def get_error_patterns(self, system_name: str) -> dict[str, Any] | None:
        """
        Retrieve cached error patterns.

        Args:
            system_name: Name of the system

        Returns:
            Cached pattern data or None if not found
        """
        cache_key = f"patterns:{system_name}"

        cached_data = await self.cache_manager.get(cache_key, prefix=self.cache_prefix)

        if cached_data:
            logger.info(f"✅ Retrieved cached error patterns: {system_name}")
            return cached_data

        return None

    async def invalidate_diagnostic_result(self, diagnostic_id: str) -> bool:
        """
        Invalidate cached diagnostic result and related data.

        Args:
            diagnostic_id: Diagnostic ID to invalidate

        Returns:
            True if invalidated successfully, False otherwise
        """
        cache_key = f"result:{diagnostic_id}"

        success = await self.cache_manager.delete(cache_key, prefix=self.cache_prefix)

        if success:
            logger.info(f"✅ Invalidated diagnostic result cache: {diagnostic_id}")

        return success

    async def invalidate_system_health(self, system_name: str) -> bool:
        """
        Invalidate cached system health data.

        Args:
            system_name: System name to invalidate

        Returns:
            True if invalidated successfully, False otherwise
        """
        cache_key = f"health:{system_name}"

        success = await self.cache_manager.delete(cache_key, prefix=self.cache_prefix)

        if success:
            logger.info(f"✅ Invalidated system health cache: {system_name}")

        return success

    async def get_diagnostic_statistics(self) -> dict[str, Any]:
        """Get diagnostic cache statistics and performance metrics."""
        base_metrics = await self.cache_manager.get_metrics()

        # Add diagnostic-specific metrics
        diagnostic_metrics = {
            "diagnostic_cache_statistics": {
                "ttl_settings": self.ttl_settings,
                "constitutional_hash": self.cache_manager.constitutional_hash,
                "cache_prefix": self.cache_prefix,
            }
        }

        return {**base_metrics, **diagnostic_metrics}
