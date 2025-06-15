"""
Cache Manager for PGC Service - ACGS-1 Phase A3 Advanced Caching
Implements service-specific caching strategies for policy governance compliance operations
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional

import structlog

from services.shared.advanced_redis_client import (
    CACHE_TTL_POLICIES,
    AdvancedRedisClient,
    CacheConfig,
    cache_result,
    get_redis_client,
)

logger = structlog.get_logger(__name__)


class PGCCacheManager:
    """Cache manager for Policy Governance Compliance service operations."""

    def __init__(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        self.service_name = "pgc_service"
        self.redis_client: Optional[AdvancedRedisClient] = None
        self._initialized = False

    async def initialize(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Initialize cache manager."""
        if self._initialized:
            return

        try:
            # Configure Redis for PGC service
            config = CacheConfig(
                redis_url="redis://localhost:6379/2",  # Use DB 2 for PGC
                redis_password="acgs_redis_production_2024_secure_cache_key",
                max_connections=15,
                health_check_interval=30,
            )

            self.redis_client = await get_redis_client(self.service_name, config)
            self._initialized = True

            logger.info("PGC cache manager initialized")

        except Exception as e:
            logger.error("Failed to initialize PGC cache manager", error=str(e))
            raise

    async def cache_compliance_check(
        self, policy_id: str, compliance_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Cache compliance check results."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"compliance_check:{policy_id}"
        compliance_ttl = ttl or CACHE_TTL_POLICIES["compliance_checks"]

        # Add timestamp to compliance data
        compliance_data["cached_at"] = datetime.utcnow().isoformat()

        return await self.redis_client.set(
            cache_key, compliance_data, ttl=compliance_ttl, prefix="compliance"
        )

    async def get_compliance_check(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get cached compliance check results."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"compliance_check:{policy_id}"
        return await self.redis_client.get(cache_key, prefix="compliance")

    async def invalidate_compliance_check(self, policy_id: str) -> bool:
        """Invalidate compliance check cache."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"compliance_check:{policy_id}"
        return await self.redis_client.delete(cache_key, prefix="compliance")

    async def cache_policy_rules(
        self, policy_id: str, rules_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Cache policy rules."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"policy_rules:{policy_id}"
        rules_ttl = ttl or CACHE_TTL_POLICIES["governance_rules"]

        return await self.redis_client.set(
            cache_key, rules_data, ttl=rules_ttl, prefix="rules"
        )

    async def get_policy_rules(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get cached policy rules."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"policy_rules:{policy_id}"
        return await self.redis_client.get(cache_key, prefix="rules")

    async def cache_governance_framework(
        self, framework_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Cache governance framework configuration."""
        if not self.redis_client:
            await self.initialize()

        cache_key = "governance_framework"
        framework_ttl = ttl or CACHE_TTL_POLICIES["static_configuration"]

        return await self.redis_client.set(
            cache_key, framework_data, ttl=framework_ttl, prefix="framework"
        )

    async def get_governance_framework(self) -> Optional[Dict[str, Any]]:
        """Get cached governance framework configuration."""
        if not self.redis_client:
            await self.initialize()

        cache_key = "governance_framework"
        return await self.redis_client.get(cache_key, prefix="framework")

    async def cache_policy_decision(
        self, decision_id: str, decision_data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Cache policy decision results."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"policy_decision:{decision_id}"
        decision_ttl = ttl or CACHE_TTL_POLICIES["policy_decisions"]

        # Add decision metadata
        decision_data["decision_timestamp"] = datetime.utcnow().isoformat()
        decision_data["cached_at"] = datetime.utcnow().isoformat()

        return await self.redis_client.set(
            cache_key, decision_data, ttl=decision_ttl, prefix="decisions"
        )

    async def get_policy_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get cached policy decision results."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"policy_decision:{decision_id}"
        return await self.redis_client.get(cache_key, prefix="decisions")

    async def cache_opa_policy(
        self, policy_name: str, policy_content: str, ttl: Optional[int] = None
    ) -> bool:
        """Cache OPA policy content."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"opa_policy:{policy_name}"
        opa_ttl = ttl or CACHE_TTL_POLICIES["governance_rules"]

        policy_data = {
            "content": policy_content,
            "cached_at": datetime.utcnow().isoformat(),
            "policy_name": policy_name,
        }

        return await self.redis_client.set(
            cache_key, policy_data, ttl=opa_ttl, prefix="opa"
        )

    async def get_opa_policy(self, policy_name: str) -> Optional[Dict[str, Any]]:
        """Get cached OPA policy content."""
        if not self.redis_client:
            await self.initialize()

        cache_key = f"opa_policy:{policy_name}"
        return await self.redis_client.get(cache_key, prefix="opa")

    async def invalidate_policy_cache(self, policy_id: str) -> int:
        """Invalidate all cache entries related to a policy."""
        if not self.redis_client:
            await self.initialize()

        patterns = [
            f"*compliance_check:{policy_id}*",
            f"*policy_rules:{policy_id}*",
            f"*policy_decision:*{policy_id}*",
            f"*opa_policy:*{policy_id}*",
        ]

        total_deleted = 0
        for pattern in patterns:
            deleted = await self.redis_client.invalidate_pattern(pattern)
            total_deleted += deleted

        logger.info(
            "Policy cache invalidated",
            policy_id=policy_id,
            deleted_entries=total_deleted,
        )

        return total_deleted

    async def warm_cache(self):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
        """Warm cache with frequently accessed data."""
        if not self.redis_client:
            await self.initialize()

        try:
            # Pre-load governance framework configuration
            framework_config = {
                "compliance_threshold": 0.85,
                "policy_validation_enabled": True,
                "opa_integration_enabled": True,
                "real_time_monitoring": True,
                "constitutional_compliance_required": True,
                "max_policy_size_kb": 1024,
                "cache_policy_decisions": True,
            }

            await self.cache_governance_framework(framework_config)

            # Pre-load common OPA policies
            common_policies = [
                "constitutional_compliance",
                "policy_validation",
                "governance_rules",
                "access_control",
            ]

            for policy_name in common_policies:
                # This would normally load from OPA server
                policy_content = f"# {policy_name} policy placeholder"
                await self.cache_opa_policy(policy_name, policy_content)

            logger.info("PGC cache warmed successfully")

        except Exception as e:
            logger.error("PGC cache warming failed", error=str(e))

    async def get_cache_metrics(self) -> Dict[str, Any]:
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
            "cache_categories": {
                "compliance_checks": "15min TTL",
                "policy_rules": "1hour TTL",
                "governance_framework": "24hour TTL",
                "policy_decisions": "5min TTL",
                "opa_policies": "1hour TTL",
            },
        }


# Global cache manager instance
_pgc_cache_manager: Optional[PGCCacheManager] = None


async def get_pgc_cache_manager() -> PGCCacheManager:
    """Get or create PGC cache manager."""
    global _pgc_cache_manager
    if _pgc_cache_manager is None:
        _pgc_cache_manager = PGCCacheManager()
        await _pgc_cache_manager.initialize()
    return _pgc_cache_manager


# Cache decorators for PGC service
def cache_pgc_result(ttl: Optional[int] = None, cache_type: str = "compliance_checks"):
    // requires: Valid input parameters
    // ensures: Correct function execution
    // sha256: func_hash
    """Decorator for caching PGC service results."""
    return cache_result(
        ttl=ttl, key_prefix="pgc", cache_type=cache_type, service_name="pgc_service"
    )


def generate_compliance_cache_key(
    policy_id: str, validation_params: Dict[str, Any]
) -> str:
    """Generate cache key for compliance checks."""
    key_data = {
        "policy_id": policy_id,
        "validation_params": validation_params,
        "timestamp": datetime.utcnow().strftime(
            "%Y-%m-%d-%H"
        ),  # Hour-level granularity
    }

    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()
