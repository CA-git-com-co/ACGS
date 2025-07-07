#!/usr/bin/env python3
"""
Redis Cache Audit and Optimizer for ACGS

Audits current Redis caching implementations across all services and
provides optimizations to achieve >85% cache hit rate target.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    service_name: str
    cache_hits: int
    cache_misses: int
    hit_rate: float
    avg_latency_ms: float
    memory_usage_mb: float
    key_count: int
    expired_keys: int


@dataclass
class CacheOptimization:
    """Cache optimization recommendation."""

    service_name: str
    current_hit_rate: float
    target_hit_rate: float
    recommendations: List[str]
    estimated_improvement: float


class RedisCacheAuditor:
    """Comprehensive Redis cache auditor and optimizer."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.target_hit_rate = 85.0  # >85% target
        self.redis_clients: Dict[str, redis.Redis] = {}
        self.service_configs = {
            "auth_service": {
                "redis_url": "redis://localhost:6389/0",
                "key_patterns": ["auth:*", "session:*", "user:*"],
                "optimal_ttls": {
                    "auth_tokens": 3600,
                    "user_sessions": 1800,
                    "rbac_permissions": 7200,
                },
            },
            "constitutional_ai": {
                "redis_url": "redis://localhost:6389/1",
                "key_patterns": ["ac:*", "constitutional:*", "principles:*"],
                "optimal_ttls": {
                    "constitutional_principles": 86400,
                    "compliance_results": 1800,
                    "council_decisions": 3600,
                },
            },
            "policy_governance": {
                "redis_url": "redis://localhost:6389/2",
                "key_patterns": ["pgc:*", "policy:*", "governance:*"],
                "optimal_ttls": {
                    "policy_fragments": 300,
                    "validation_results": 600,
                    "governance_decisions": 1800,
                },
            },
            "governance_synthesis": {
                "redis_url": "redis://localhost:6389/3",
                "key_patterns": ["gs:*", "synthesis:*"],
                "optimal_ttls": {
                    "synthesis_results": 1800,
                    "aggregated_policies": 3600,
                },
            },
        }

    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive Redis cache audit across all services."""
        logger.info("🔍 Starting Redis Cache Audit for ACGS Services")
        logger.info(f"📋 Constitutional Hash: {self.constitutional_hash}")
        logger.info(f"🎯 Target Cache Hit Rate: {self.target_hit_rate}%")

        audit_results = {
            "audit_summary": {
                "timestamp": time.time(),
                "constitutional_hash": self.constitutional_hash,
                "target_hit_rate": self.target_hit_rate,
                "services_audited": 0,
                "total_optimizations": 0,
            },
            "service_metrics": {},
            "optimizations": [],
            "global_recommendations": [],
        }

        # Initialize Redis connections
        await self._initialize_redis_connections()

        # Audit each service
        for service_name, config in self.service_configs.items():
            logger.info(f"🔍 Auditing {service_name} cache performance...")

            try:
                metrics = await self._audit_service_cache(service_name, config)
                audit_results["service_metrics"][service_name] = metrics

                if metrics.hit_rate < self.target_hit_rate:
                    optimization = await self._generate_optimization_plan(
                        service_name, metrics, config
                    )
                    audit_results["optimizations"].append(optimization)
                    audit_results["audit_summary"]["total_optimizations"] += 1

                audit_results["audit_summary"]["services_audited"] += 1

                logger.info(
                    f"✅ {service_name}: Hit Rate {metrics.hit_rate:.1f}%, "
                    f"Latency {metrics.avg_latency_ms:.2f}ms"
                )

            except Exception as e:
                logger.error(f"❌ Failed to audit {service_name}: {e}")

        # Generate global recommendations
        audit_results["global_recommendations"] = self._generate_global_recommendations(
            audit_results["service_metrics"]
        )

        # Apply optimizations
        await self._apply_optimizations(audit_results["optimizations"])

        # Save audit report
        await self._save_audit_report(audit_results)

        return audit_results

    async def _initialize_redis_connections(self):
        """Initialize Redis connections for all services."""
        for service_name, config in self.service_configs.items():
            try:
                client = redis.from_url(
                    config["redis_url"],
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=2,
                )
                await client.ping()
                self.redis_clients[service_name] = client
                logger.info(f"✅ Connected to {service_name} Redis")
            except Exception as e:
                logger.warning(f"⚠️ Failed to connect to {service_name} Redis: {e}")

    async def _audit_service_cache(
        self, service_name: str, config: Dict[str, Any]
    ) -> CacheMetrics:
        """Audit cache performance for a specific service."""
        client = self.redis_clients.get(service_name)
        if not client:
            return CacheMetrics(
                service_name=service_name,
                cache_hits=0,
                cache_misses=0,
                hit_rate=0.0,
                avg_latency_ms=0.0,
                memory_usage_mb=0.0,
                key_count=0,
                expired_keys=0,
            )

        try:
            # Get Redis info
            info = await client.info()

            # Calculate metrics
            keyspace_hits = int(info.get("keyspace_hits", 0))
            keyspace_misses = int(info.get("keyspace_misses", 0))
            total_requests = keyspace_hits + keyspace_misses
            hit_rate = (
                (keyspace_hits / total_requests * 100) if total_requests > 0 else 0.0
            )

            # Get memory usage
            used_memory = int(info.get("used_memory", 0))
            memory_usage_mb = used_memory / (1024 * 1024)

            # Count keys for this service
            key_count = 0
            expired_keys = 0

            for pattern in config["key_patterns"]:
                keys = await client.keys(pattern)
                key_count += len(keys)

                # Check for expired keys
                for key in keys[:100]:  # Sample first 100 keys
                    ttl = await client.ttl(key)
                    if ttl == -1:  # No expiration set
                        expired_keys += 1

            # Measure latency
            start_time = time.time()
            await client.ping()
            latency_ms = (time.time() - start_time) * 1000

            return CacheMetrics(
                service_name=service_name,
                cache_hits=keyspace_hits,
                cache_misses=keyspace_misses,
                hit_rate=hit_rate,
                avg_latency_ms=latency_ms,
                memory_usage_mb=memory_usage_mb,
                key_count=key_count,
                expired_keys=expired_keys,
            )

        except Exception as e:
            logger.error(f"Error auditing {service_name}: {e}")
            return CacheMetrics(
                service_name=service_name,
                cache_hits=0,
                cache_misses=0,
                hit_rate=0.0,
                avg_latency_ms=0.0,
                memory_usage_mb=0.0,
                key_count=0,
                expired_keys=0,
            )

    async def _generate_optimization_plan(
        self, service_name: str, metrics: CacheMetrics, config: Dict[str, Any]
    ) -> CacheOptimization:
        """Generate optimization plan for service cache."""
        recommendations = []
        estimated_improvement = 0.0

        # Analyze hit rate
        if metrics.hit_rate < 50:
            recommendations.append(
                "CRITICAL: Implement cache warming for frequently accessed data"
            )
            recommendations.append("Review cache key design for better locality")
            estimated_improvement += 25.0
        elif metrics.hit_rate < 70:
            recommendations.append("Optimize TTL values for better cache retention")
            recommendations.append("Implement request-scoped caching")
            estimated_improvement += 15.0
        elif metrics.hit_rate < 85:
            recommendations.append("Fine-tune cache eviction policies")
            recommendations.append("Add predictive cache preloading")
            estimated_improvement += 10.0

        # Analyze latency
        if metrics.avg_latency_ms > 5.0:
            recommendations.append("Optimize Redis connection pooling")
            recommendations.append("Consider Redis cluster for better performance")
            estimated_improvement += 5.0

        # Analyze memory usage
        if metrics.memory_usage_mb > 1000:  # >1GB
            recommendations.append("Implement data compression for large cache entries")
            recommendations.append("Review cache size limits and eviction policies")

        # Analyze expired keys
        if metrics.expired_keys > metrics.key_count * 0.1:  # >10% expired
            recommendations.append("Optimize TTL values to reduce expired key overhead")
            recommendations.append("Implement background key cleanup")

        # Constitutional compliance recommendations
        recommendations.append(
            f"Ensure all cache entries validate constitutional hash: {self.constitutional_hash}"
        )
        recommendations.append("Implement constitutional compliance caching middleware")

        return CacheOptimization(
            service_name=service_name,
            current_hit_rate=metrics.hit_rate,
            target_hit_rate=self.target_hit_rate,
            recommendations=recommendations,
            estimated_improvement=min(
                estimated_improvement, self.target_hit_rate - metrics.hit_rate
            ),
        )

    def _generate_global_recommendations(
        self, service_metrics: Dict[str, CacheMetrics]
    ) -> List[str]:
        """Generate global optimization recommendations."""
        recommendations = []

        # Calculate overall hit rate
        total_hits = sum(m.cache_hits for m in service_metrics.values())
        total_requests = sum(
            m.cache_hits + m.cache_misses for m in service_metrics.values()
        )
        overall_hit_rate = (
            (total_hits / total_requests * 100) if total_requests > 0 else 0.0
        )

        if overall_hit_rate < self.target_hit_rate:
            recommendations.append(
                f"PRIORITY: Overall hit rate {overall_hit_rate:.1f}% below target {self.target_hit_rate}%"
            )
            recommendations.append(
                "Implement cross-service cache sharing for common data"
            )
            recommendations.append(
                "Deploy Redis cluster for improved performance and availability"
            )

        # Memory optimization
        total_memory = sum(m.memory_usage_mb for m in service_metrics.values())
        if total_memory > 2000:  # >2GB
            recommendations.append("Consider Redis memory optimization and compression")

        # Latency optimization
        avg_latency = sum(m.avg_latency_ms for m in service_metrics.values()) / len(
            service_metrics
        )
        if avg_latency > 2.0:  # >2ms average
            recommendations.append(
                "Optimize Redis network configuration and connection pooling"
            )

        recommendations.append("Implement unified cache monitoring and alerting")
        recommendations.append("Schedule regular cache performance reviews")

        return recommendations

    async def _apply_optimizations(self, optimizations: List[CacheOptimization]):
        """Apply cache optimizations where possible."""
        for optimization in optimizations:
            logger.info(f"🔧 Applying optimizations for {optimization.service_name}...")

            client = self.redis_clients.get(optimization.service_name)
            if not client:
                continue

            try:
                # Apply TTL optimizations
                service_config = self.service_configs[optimization.service_name]
                optimal_ttls = service_config.get("optimal_ttls", {})

                for cache_type, ttl in optimal_ttls.items():
                    # Update TTL for existing keys (sample approach)
                    pattern = f"{cache_type}:*"
                    keys = await client.keys(pattern)

                    for key in keys[:10]:  # Sample first 10 keys
                        current_ttl = await client.ttl(key)
                        if current_ttl != ttl:
                            await client.expire(key, ttl)

                logger.info(
                    f"✅ Applied TTL optimizations for {optimization.service_name}"
                )

            except Exception as e:
                logger.error(
                    f"❌ Failed to apply optimizations for {optimization.service_name}: {e}"
                )

    async def _save_audit_report(self, audit_results: Dict[str, Any]):
        """Save audit report to file."""
        report_path = Path("redis_cache_audit_report.json")

        try:
            # Convert metrics to serializable format
            serializable_results = audit_results.copy()
            serializable_results["service_metrics"] = {
                service: {
                    "service_name": metrics.service_name,
                    "cache_hits": metrics.cache_hits,
                    "cache_misses": metrics.cache_misses,
                    "hit_rate": metrics.hit_rate,
                    "avg_latency_ms": metrics.avg_latency_ms,
                    "memory_usage_mb": metrics.memory_usage_mb,
                    "key_count": metrics.key_count,
                    "expired_keys": metrics.expired_keys,
                }
                for service, metrics in audit_results["service_metrics"].items()
            }

            serializable_results["optimizations"] = [
                {
                    "service_name": opt.service_name,
                    "current_hit_rate": opt.current_hit_rate,
                    "target_hit_rate": opt.target_hit_rate,
                    "recommendations": opt.recommendations,
                    "estimated_improvement": opt.estimated_improvement,
                }
                for opt in audit_results["optimizations"]
            ]

            with open(report_path, "w") as f:
                json.dump(serializable_results, f, indent=2)

            logger.info(f"📊 Redis cache audit report saved to {report_path}")

        except Exception as e:
            logger.error(f"Failed to save audit report: {e}")

    async def cleanup(self):
        """Cleanup Redis connections."""
        for client in self.redis_clients.values():
            try:
                await client.close()
            except:
                pass


async def main():
    """Main audit entry point."""
    auditor = RedisCacheAuditor()

    try:
        results = await auditor.run_comprehensive_audit()

        # Print summary
        summary = results["audit_summary"]
        logger.info("=" * 60)
        logger.info("🎯 REDIS CACHE AUDIT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📊 Services Audited: {summary['services_audited']}")
        logger.info(f"🔧 Optimizations Generated: {summary['total_optimizations']}")
        logger.info(f"🔒 Constitutional Hash: {summary['constitutional_hash']}")

        # Show service metrics
        for service, metrics in results["service_metrics"].items():
            status = "✅" if metrics["hit_rate"] >= 85.0 else "⚠️"
            logger.info(
                f"{status} {service}: {metrics['hit_rate']:.1f}% hit rate, "
                f"{metrics['avg_latency_ms']:.2f}ms latency"
            )

        return 0

    except Exception as e:
        logger.error(f"Redis cache audit failed: {e}")
        return 1
    finally:
        await auditor.cleanup()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    exit(asyncio.run(main()))
