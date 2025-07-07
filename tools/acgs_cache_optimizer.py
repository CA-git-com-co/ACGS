#!/usr/bin/env python3
"""
ACGS Cache Performance Optimizer
Constitutional Hash: cdd01ef066bc6cf2

Consolidates and optimizes cache-related tools for ACGS >85% cache hit rate target.

Features:
- Async Redis operations with connection pooling
- Real-time cache hit rate monitoring
- Cache warming strategies
- TTL optimization
- Memory usage optimization
- Constitutional compliance caching
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import aioredis
from pydantic import BaseModel

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Cache configuration
CACHE_CONFIG = {
    "url": "redis://localhost:6389/0",
    "encoding": "utf-8",
    "decode_responses": True,
    "max_connections": 20,
    "retry_on_timeout": True,
    "socket_keepalive": True,
    "socket_keepalive_options": {},
}

# Performance targets
CACHE_TARGETS = {
    "min_hit_rate": 0.85,  # 85% minimum hit rate
    "max_latency_ms": 2.0,  # 2ms maximum cache operation latency
    "max_memory_usage": 0.8,  # 80% maximum memory usage
    "ttl_default": 3600,  # 1 hour default TTL
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    timestamp: datetime
    hit_rate: float
    miss_rate: float
    avg_latency_ms: float
    memory_usage_bytes: int
    total_operations: int
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ACGSCacheOptimizer:
    """ACGS cache performance optimizer."""
    
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.metrics_history: List[CacheMetrics] = []
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "operations": 0,
            "total_latency": 0.0,
        }
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize Redis connection."""
        logger.info("🚀 Initializing ACGS Cache Optimizer...")
        
        try:
            self.redis_client = await aioredis.from_url(**CACHE_CONFIG)
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
            # Initialize cache with constitutional compliance
            await self._initialize_constitutional_cache()
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            raise
            
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("🧹 Cleaning up cache optimizer...")
        
        if self.redis_client:
            await self.redis_client.close()
            
        logger.info("✅ Cleanup completed")

    async def _initialize_constitutional_cache(self):
        """Initialize constitutional compliance cache."""
        logger.info("🏛️ Initializing constitutional compliance cache...")
        
        try:
            # Set constitutional hash
            await self.redis_client.set(
                "constitutional:hash",
                CONSTITUTIONAL_HASH,
                ex=86400  # 24 hours
            )
            
            # Initialize cache metadata
            cache_metadata = {
                "initialized_at": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "version": "1.0.0",
                "targets": CACHE_TARGETS,
            }
            
            await self.redis_client.set(
                "cache:metadata",
                json.dumps(cache_metadata),
                ex=86400
            )
            
            logger.info("✅ Constitutional cache initialized")
            
        except Exception as e:
            logger.error(f"❌ Constitutional cache initialization failed: {e}")

    async def optimize_cache_performance(self) -> Dict[str, Any]:
        """Run comprehensive cache optimization."""
        logger.info("⚡ Starting cache performance optimization...")
        
        results = {
            "optimization_start": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "baseline_metrics": {},
            "optimization_results": {},
            "final_metrics": {},
            "recommendations": [],
        }
        
        try:
            # Collect baseline metrics
            results["baseline_metrics"] = await self._collect_cache_metrics()
            
            # Run optimization strategies
            optimization_results = await self._run_optimization_strategies()
            results["optimization_results"] = optimization_results
            
            # Collect final metrics
            results["final_metrics"] = await self._collect_cache_metrics()
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results)
            
            # Save optimization results
            await self._save_optimization_results(results)
            
            logger.info("✅ Cache optimization completed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Cache optimization failed: {e}")
            raise

    async def _collect_cache_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive cache metrics."""
        logger.info("📊 Collecting cache metrics...")
        
        try:
            # Get Redis info
            info = await self.redis_client.info()
            memory_info = await self.redis_client.info("memory")
            stats_info = await self.redis_client.info("stats")
            
            # Calculate hit rate
            keyspace_hits = stats_info.get("keyspace_hits", 0)
            keyspace_misses = stats_info.get("keyspace_misses", 0)
            total_commands = keyspace_hits + keyspace_misses
            hit_rate = (keyspace_hits / total_commands) if total_commands > 0 else 0
            
            # Memory metrics
            used_memory = memory_info.get("used_memory", 0)
            max_memory = memory_info.get("maxmemory", 0)
            memory_usage_ratio = (used_memory / max_memory) if max_memory > 0 else 0
            
            # Performance test
            latency_results = await self._test_cache_latency()
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "hit_rate": round(hit_rate, 4),
                "miss_rate": round(1 - hit_rate, 4),
                "keyspace_hits": keyspace_hits,
                "keyspace_misses": keyspace_misses,
                "total_commands": total_commands,
                "used_memory_bytes": used_memory,
                "max_memory_bytes": max_memory,
                "memory_usage_ratio": round(memory_usage_ratio, 4),
                "avg_latency_ms": latency_results["avg_latency_ms"],
                "p99_latency_ms": latency_results["p99_latency_ms"],
                "connected_clients": info.get("connected_clients", 0),
                "meets_hit_rate_target": hit_rate >= CACHE_TARGETS["min_hit_rate"],
                "meets_latency_target": latency_results["avg_latency_ms"] <= CACHE_TARGETS["max_latency_ms"],
                "meets_memory_target": memory_usage_ratio <= CACHE_TARGETS["max_memory_usage"],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
            
        except Exception as e:
            logger.error(f"Cache metrics collection failed: {e}")
            return {"error": str(e)}

    async def _test_cache_latency(self, operations: int = 1000) -> Dict[str, Any]:
        """Test cache operation latency."""
        logger.info(f"⏱️ Testing cache latency with {operations} operations...")
        
        latencies = []
        
        try:
            # Test SET operations
            for i in range(operations // 2):
                start_time = time.perf_counter()
                await self.redis_client.set(
                    f"latency_test:{i}",
                    f"test_value_{i}_{CONSTITUTIONAL_HASH}",
                    ex=300  # 5 minutes
                )
                latency_ms = (time.perf_counter() - start_time) * 1000
                latencies.append(latency_ms)
            
            # Test GET operations
            for i in range(operations // 2):
                start_time = time.perf_counter()
                await self.redis_client.get(f"latency_test:{i}")
                latency_ms = (time.perf_counter() - start_time) * 1000
                latencies.append(latency_ms)
            
            # Calculate statistics
            avg_latency = sum(latencies) / len(latencies)
            latencies.sort()
            p99_index = int(len(latencies) * 0.99)
            p99_latency = latencies[p99_index] if p99_index < len(latencies) else latencies[-1]
            
            # Cleanup test keys
            test_keys = [f"latency_test:{i}" for i in range(operations // 2)]
            if test_keys:
                await self.redis_client.delete(*test_keys)
            
            return {
                "total_operations": operations,
                "avg_latency_ms": round(avg_latency, 3),
                "p99_latency_ms": round(p99_latency, 3),
                "min_latency_ms": round(min(latencies), 3),
                "max_latency_ms": round(max(latencies), 3),
            }
            
        except Exception as e:
            logger.error(f"Cache latency test failed: {e}")
            return {"error": str(e)}

    async def _run_optimization_strategies(self) -> Dict[str, Any]:
        """Run cache optimization strategies."""
        logger.info("🔧 Running cache optimization strategies...")
        
        optimization_results = {}
        
        try:
            # Strategy 1: Optimize TTL policies
            ttl_results = await self._optimize_ttl_policies()
            optimization_results["ttl_optimization"] = ttl_results
            
            # Strategy 2: Implement cache warming
            warming_results = await self._implement_cache_warming()
            optimization_results["cache_warming"] = warming_results
            
            # Strategy 3: Optimize memory usage
            memory_results = await self._optimize_memory_usage()
            optimization_results["memory_optimization"] = memory_results
            
            # Strategy 4: Configure eviction policies
            eviction_results = await self._configure_eviction_policies()
            optimization_results["eviction_optimization"] = eviction_results
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Cache optimization strategies failed: {e}")
            return {"error": str(e)}

    async def _optimize_ttl_policies(self) -> Dict[str, Any]:
        """Optimize TTL policies for better cache efficiency."""
        logger.info("⏰ Optimizing TTL policies...")
        
        try:
            # Analyze current TTL distribution
            ttl_analysis = await self._analyze_ttl_distribution()
            
            # Set optimized TTLs for different data types
            ttl_policies = {
                "constitutional:*": 86400,  # 24 hours for constitutional data
                "session:*": 3600,  # 1 hour for session data
                "user:*": 7200,  # 2 hours for user data
                "cache:*": 1800,  # 30 minutes for general cache
                "temp:*": 300,  # 5 minutes for temporary data
            }
            
            # Apply TTL policies
            policies_applied = 0
            for pattern, ttl in ttl_policies.items():
                keys = await self.redis_client.keys(pattern)
                for key in keys:
                    await self.redis_client.expire(key, ttl)
                    policies_applied += 1
            
            return {
                "ttl_analysis": ttl_analysis,
                "policies_applied": policies_applied,
                "ttl_policies": ttl_policies,
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"TTL optimization failed: {e}")
            return {"error": str(e)}

    async def _analyze_ttl_distribution(self) -> Dict[str, Any]:
        """Analyze current TTL distribution."""
        try:
            # Sample keys for TTL analysis
            all_keys = await self.redis_client.keys("*")
            sample_size = min(1000, len(all_keys))
            sample_keys = all_keys[:sample_size] if all_keys else []
            
            ttl_distribution = {
                "no_expiry": 0,
                "short_term": 0,  # < 1 hour
                "medium_term": 0,  # 1-24 hours
                "long_term": 0,  # > 24 hours
            }
            
            for key in sample_keys:
                ttl = await self.redis_client.ttl(key)
                if ttl == -1:  # No expiry
                    ttl_distribution["no_expiry"] += 1
                elif ttl < 3600:  # < 1 hour
                    ttl_distribution["short_term"] += 1
                elif ttl < 86400:  # 1-24 hours
                    ttl_distribution["medium_term"] += 1
                else:  # > 24 hours
                    ttl_distribution["long_term"] += 1
            
            return {
                "sample_size": sample_size,
                "total_keys": len(all_keys),
                "distribution": ttl_distribution,
            }
            
        except Exception as e:
            logger.error(f"TTL analysis failed: {e}")
            return {"error": str(e)}

    async def _implement_cache_warming(self) -> Dict[str, Any]:
        """Implement cache warming strategies."""
        logger.info("🔥 Implementing cache warming...")
        
        try:
            # Warm constitutional compliance cache
            constitutional_data = {
                "constitutional:hash": CONSTITUTIONAL_HASH,
                "constitutional:version": "1.0.0",
                "constitutional:status": "active",
                "constitutional:last_updated": datetime.now(timezone.utc).isoformat(),
            }
            
            warmed_keys = 0
            for key, value in constitutional_data.items():
                await self.redis_client.set(key, value, ex=86400)
                warmed_keys += 1
            
            # Warm frequently accessed patterns
            common_patterns = [
                "health:service:*",
                "metrics:performance:*",
                "config:system:*",
            ]
            
            for pattern in common_patterns:
                # Simulate warming with placeholder data
                for i in range(10):  # Warm 10 keys per pattern
                    key = pattern.replace("*", str(i))
                    value = f"warmed_data_{i}_{CONSTITUTIONAL_HASH}"
                    await self.redis_client.set(key, value, ex=3600)
                    warmed_keys += 1
            
            return {
                "warmed_keys": warmed_keys,
                "constitutional_data": len(constitutional_data),
                "patterns_warmed": len(common_patterns),
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            return {"error": str(e)}

    async def _optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize cache memory usage."""
        logger.info("💾 Optimizing memory usage...")

        try:
            # Get current memory info
            memory_info = await self.redis_client.info("memory")
            used_memory = memory_info.get("used_memory", 0)

            # Clean up expired keys
            expired_cleaned = 0
            all_keys = await self.redis_client.keys("*")

            for key in all_keys[:1000]:  # Limit to prevent blocking
                ttl = await self.redis_client.ttl(key)
                if ttl == -2:  # Key expired but not cleaned
                    await self.redis_client.delete(key)
                    expired_cleaned += 1

            # Optimize data structures
            optimized_keys = await self._optimize_data_structures()

            # Get final memory info
            final_memory_info = await self.redis_client.info("memory")
            final_used_memory = final_memory_info.get("used_memory", 0)

            memory_saved = used_memory - final_used_memory

            return {
                "initial_memory_bytes": used_memory,
                "final_memory_bytes": final_used_memory,
                "memory_saved_bytes": memory_saved,
                "expired_keys_cleaned": expired_cleaned,
                "optimized_keys": optimized_keys,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
            return {"error": str(e)}

    async def _optimize_data_structures(self) -> int:
        """Optimize Redis data structures for memory efficiency."""
        optimized_count = 0

        try:
            # Convert small hashes to strings if more efficient
            hash_keys = await self.redis_client.keys("hash:*")

            for key in hash_keys[:100]:  # Limit processing
                hash_len = await self.redis_client.hlen(key)
                if hash_len <= 5:  # Small hashes
                    # Get hash data
                    hash_data = await self.redis_client.hgetall(key)
                    # Convert to JSON string
                    json_data = json.dumps(hash_data)
                    # Replace with string
                    ttl = await self.redis_client.ttl(key)
                    await self.redis_client.delete(key)
                    if ttl > 0:
                        await self.redis_client.set(key, json_data, ex=ttl)
                    else:
                        await self.redis_client.set(key, json_data)
                    optimized_count += 1

            return optimized_count

        except Exception as e:
            logger.error(f"Data structure optimization failed: {e}")
            return 0

    async def _configure_eviction_policies(self) -> Dict[str, Any]:
        """Configure optimal eviction policies."""
        logger.info("🗑️ Configuring eviction policies...")

        try:
            # Get current configuration
            config_info = await self.redis_client.config_get("maxmemory-policy")
            current_policy = config_info.get("maxmemory-policy", "noeviction")

            # Set optimal eviction policy for ACGS
            optimal_policy = "allkeys-lru"  # LRU eviction for all keys

            # Configure eviction policy
            await self.redis_client.config_set("maxmemory-policy", optimal_policy)

            # Configure memory limit if not set
            memory_info = await self.redis_client.info("memory")
            max_memory = memory_info.get("maxmemory", 0)

            if max_memory == 0:
                # Set to 80% of available system memory (example: 1GB)
                suggested_max_memory = 1024 * 1024 * 1024  # 1GB
                await self.redis_client.config_set("maxmemory", suggested_max_memory)
                max_memory = suggested_max_memory

            return {
                "previous_policy": current_policy,
                "current_policy": optimal_policy,
                "max_memory_bytes": max_memory,
                "policy_changed": current_policy != optimal_policy,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Eviction policy configuration failed: {e}")
            return {"error": str(e)}

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        try:
            baseline = results.get("baseline_metrics", {})
            final = results.get("final_metrics", {})

            # Hit rate recommendations
            if not final.get("meets_hit_rate_target", False):
                hit_rate = final.get("hit_rate", 0)
                recommendations.append(
                    f"Improve cache hit rate from {hit_rate:.1%} to >85% target"
                )

            # Latency recommendations
            if not final.get("meets_latency_target", False):
                latency = final.get("avg_latency_ms", 0)
                recommendations.append(
                    f"Reduce cache latency from {latency:.2f}ms to <2ms target"
                )

            # Memory recommendations
            if not final.get("meets_memory_target", False):
                memory_ratio = final.get("memory_usage_ratio", 0)
                recommendations.append(
                    f"Optimize memory usage from {memory_ratio:.1%} to <80% target"
                )

            # TTL recommendations
            optimization_results = results.get("optimization_results", {})
            ttl_results = optimization_results.get("ttl_optimization", {})
            if ttl_results and not ttl_results.get("error"):
                recommendations.append("Continue TTL policy optimization")

            # General recommendations
            if not recommendations:
                recommendations.append("Cache performance meets all targets")
            else:
                recommendations.append("Consider implementing cache monitoring dashboard")
                recommendations.append("Schedule regular cache optimization maintenance")

            return recommendations

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Error generating recommendations"]

    async def _save_optimization_results(self, results: Dict[str, Any]):
        """Save optimization results."""
        logger.info("💾 Saving optimization results...")

        try:
            from pathlib import Path

            # Create results directory
            results_dir = Path("reports/cache_optimization")
            results_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"cache_optimization_{timestamp}.json"
            filepath = results_dir / filename

            # Save results
            with open(filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"✅ Results saved to {filepath}")

            # Also save to Redis for monitoring
            await self.redis_client.set(
                "cache:optimization:latest",
                json.dumps(results, default=str),
                ex=86400  # 24 hours
            )

        except Exception as e:
            logger.error(f"Failed to save optimization results: {e}")

    async def start_cache_monitoring(self, interval_seconds: int = 300):
        """Start continuous cache monitoring."""
        logger.info(f"🔄 Starting cache monitoring (interval: {interval_seconds}s)...")

        try:
            while True:
                # Collect metrics
                metrics = await self._collect_cache_metrics()

                # Log status
                if "error" not in metrics:
                    logger.info(
                        f"Cache Status: {metrics.get('hit_rate', 0):.1%} hit rate, "
                        f"{metrics.get('avg_latency_ms', 0):.2f}ms latency, "
                        f"{metrics.get('memory_usage_ratio', 0):.1%} memory usage"
                    )

                    # Check for performance issues
                    if not metrics.get("meets_hit_rate_target", True):
                        logger.warning("⚠️ Cache hit rate below target!")
                    if not metrics.get("meets_latency_target", True):
                        logger.warning("⚠️ Cache latency above target!")
                    if not metrics.get("meets_memory_target", True):
                        logger.warning("⚠️ Cache memory usage above target!")
                else:
                    logger.error(f"❌ Cache monitoring error: {metrics['error']}")

                # Save monitoring record
                await self._save_monitoring_record(metrics)

                # Wait for next interval
                await asyncio.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("🛑 Cache monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Cache monitoring failed: {e}")
            raise

    async def _save_monitoring_record(self, metrics: Dict[str, Any]):
        """Save cache monitoring record."""
        try:
            from pathlib import Path

            # Create monitoring directory
            monitoring_dir = Path("reports/cache_monitoring")
            monitoring_dir.mkdir(parents=True, exist_ok=True)

            # Append to daily monitoring log
            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            log_file = monitoring_dir / f"cache_monitoring_{date_str}.jsonl"

            with open(log_file, "a") as f:
                f.write(json.dumps(metrics, default=str) + "\n")

        except Exception as e:
            logger.error(f"Failed to save monitoring record: {e}")


async def main():
    """Main function for cache optimization."""
    logger.info("🚀 ACGS Cache Optimizer Starting...")

    async with ACGSCacheOptimizer() as optimizer:
        try:
            # Run cache optimization
            results = await optimizer.optimize_cache_performance()

            # Print summary
            baseline = results.get("baseline_metrics", {})
            final = results.get("final_metrics", {})
            recommendations = results.get("recommendations", [])

            print("\n" + "="*60)
            print("🗄️ ACGS CACHE OPTIMIZATION SUMMARY")
            print("="*60)
            print(f"Hit Rate: {baseline.get('hit_rate', 0):.1%} → {final.get('hit_rate', 0):.1%}")
            print(f"Latency: {baseline.get('avg_latency_ms', 0):.2f}ms → {final.get('avg_latency_ms', 0):.2f}ms")
            print(f"Memory Usage: {baseline.get('memory_usage_ratio', 0):.1%} → {final.get('memory_usage_ratio', 0):.1%}")

            # Print target status
            print(f"\n🎯 TARGET STATUS:")
            print(f"Hit Rate Target (>85%): {'✅' if final.get('meets_hit_rate_target', False) else '❌'}")
            print(f"Latency Target (<2ms): {'✅' if final.get('meets_latency_target', False) else '❌'}")
            print(f"Memory Target (<80%): {'✅' if final.get('meets_memory_target', False) else '❌'}")

            # Print recommendations
            if recommendations:
                print(f"\n📋 RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")

            print(f"\n🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
            print("="*60)

        except Exception as e:
            logger.error(f"❌ Cache optimization failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
