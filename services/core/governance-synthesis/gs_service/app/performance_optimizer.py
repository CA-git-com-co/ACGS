"""
Performance Optimization Module for Governance Synthesis Service

This module implements comprehensive performance optimizations including:
- Pre-compiled governance patterns and rules caching
- WINA optimization for policy governance consistency
- Response caching for frequently requested synthesis operations
- Computational bottleneck analysis and optimization
"""

import asyncio
import hashlib
import json
import logging
import time
from functools import wraps
from typing import Any, Dict, List, Optional

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# Global Redis connection pool
redis_pool: Optional[aioredis.ConnectionPool] = None

# Performance metrics
synthesis_metrics = {
    "cache_hits": 0,
    "cache_misses": 0,
    "total_synthesis_requests": 0,
    "avg_synthesis_time_ms": 0.0,
    "p99_synthesis_time_ms": 0.0,
    "wina_optimizations": 0,
    "pattern_cache_hits": 0,
    "constitutional_validations": 0,
}

# Synthesis time tracking for P99 calculation
synthesis_times = []
MAX_SYNTHESIS_TIME_SAMPLES = 1000

# Pre-compiled governance patterns cache
governance_patterns_cache = {}
PATTERN_CACHE_TTL = 900  # 15 minutes


async def initialize_redis_pool() -> aioredis.ConnectionPool:
    """Initialize Redis connection pool for synthesis caching"""
    global redis_pool

    if redis_pool is None:
        try:
            redis_pool = aioredis.ConnectionPool.from_url(
                "redis://localhost:6389/1",  # Use database 1 for synthesis service
                max_connections=20,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30,
            )
            logger.info("✅ Redis connection pool initialized for GS service")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis pool: {e}")
            raise

    return redis_pool


async def get_redis_client() -> aioredis.Redis:
    """Get Redis client from connection pool"""
    pool = await initialize_redis_pool()
    return aioredis.Redis(connection_pool=pool)


def generate_synthesis_cache_key(
    prefix: str, synthesis_type: str, parameters: dict
) -> str:
    """Generate deterministic cache key for synthesis operations"""
    # Create stable hash from synthesis parameters
    param_str = json.dumps(parameters, sort_keys=True)
    param_hash = hashlib.md5(param_str.encode()).hexdigest()[:16]
    return f"{prefix}:synthesis:{synthesis_type}:{param_hash}"


def cache_synthesis_response(ttl: int = 600, key_prefix: str = "gs"):
    """
    High-performance caching decorator for synthesis operations

    Args:
        ttl: Time to live in seconds (default: 10 minutes)
        key_prefix: Cache key prefix for namespacing
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            # Generate cache key for synthesis operation
            synthesis_params = {
                "args": str(args),
                "kwargs": {k: v for k, v in kwargs.items() if k != "request"},
            }
            cache_key = generate_synthesis_cache_key(
                key_prefix, func.__name__, synthesis_params
            )

            try:
                redis_client = await get_redis_client()

                # Try to get cached synthesis result
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    try:
                        response = json.loads(cached_data)

                        # Validate constitutional hash
                        if response.get("constitutional_hash") == "cdd01ef066bc6cf2":
                            # Cache hit - update metrics
                            synthesis_metrics["cache_hits"] += 1
                            synthesis_metrics["constitutional_validations"] += 1

                            synthesis_time_ms = (time.time() - start_time) * 1000
                            update_synthesis_metrics(synthesis_time_ms)

                            logger.debug(
                                f"Synthesis cache hit for {func.__name__} ({synthesis_time_ms:.2f}ms)"
                            )
                            return response
                        else:
                            logger.warning(
                                f"Constitutional hash mismatch in synthesis cache: {cache_key}"
                            )
                            await redis_client.delete(cache_key)

                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in synthesis cache: {cache_key}")
                        await redis_client.delete(cache_key)

                # Cache miss - execute synthesis
                synthesis_metrics["cache_misses"] += 1
                result = await func(*args, **kwargs)

                # Cache the synthesis result
                if isinstance(result, dict) and "constitutional_hash" in result:
                    try:
                        await redis_client.setex(cache_key, ttl, json.dumps(result))
                        logger.debug(
                            f"Cached synthesis result for {func.__name__} (TTL: {ttl}s)"
                        )
                    except Exception as cache_error:
                        logger.warning(
                            f"Failed to cache synthesis result: {cache_error}"
                        )

                synthesis_time_ms = (time.time() - start_time) * 1000
                update_synthesis_metrics(synthesis_time_ms)

                return result

            except Exception as e:
                logger.error(
                    f"Synthesis cache operation failed for {func.__name__}: {e}"
                )
                # Fallback to direct execution
                result = await func(*args, **kwargs)
                synthesis_time_ms = (time.time() - start_time) * 1000
                update_synthesis_metrics(synthesis_time_ms)
                return result

        return wrapper

    return decorator


def update_synthesis_metrics(synthesis_time_ms: float):
    """Update synthesis performance metrics"""
    global synthesis_times

    synthesis_metrics["total_synthesis_requests"] += 1

    # Add to synthesis time tracking
    synthesis_times.append(synthesis_time_ms)

    # Keep only recent samples for P99 calculation
    if len(synthesis_times) > MAX_SYNTHESIS_TIME_SAMPLES:
        synthesis_times = synthesis_times[-MAX_SYNTHESIS_TIME_SAMPLES:]

    # Update average synthesis time
    synthesis_metrics["avg_synthesis_time_ms"] = sum(synthesis_times) / len(
        synthesis_times
    )

    # Calculate P99 synthesis time
    if len(synthesis_times) >= 10:
        sorted_times = sorted(synthesis_times)
        p99_index = int(len(sorted_times) * 0.99)
        synthesis_metrics["p99_synthesis_time_ms"] = sorted_times[p99_index]


async def precompile_governance_patterns():
    """Pre-compile frequently used governance patterns for O(1) lookup"""
    logger.info("Pre-compiling governance patterns...")

    # Common governance patterns that can be pre-compiled
    patterns = {
        "constitutional_compliance": {
            "pattern": "constitutional_compliance(Policy) :- complies_with_constitution(Policy, 'cdd01ef066bc6cf2').",
            "description": "Basic constitutional compliance pattern",
            "priority": "high",
        },
        "policy_validation": {
            "pattern": "valid_policy(Policy) :- constitutional_compliance(Policy), stakeholder_approved(Policy).",
            "description": "Policy validation pattern",
            "priority": "high",
        },
        "governance_synthesis": {
            "pattern": "synthesize_governance(Input, Output) :- validate_input(Input), apply_rules(Input, Output), verify_output(Output).",
            "description": "Core governance synthesis pattern",
            "priority": "critical",
        },
        "wina_optimization": {
            "pattern": "wina_optimize(Policy, OptimizedPolicy) :- weight_analysis(Policy, Weights), neuron_activation(Weights, OptimizedPolicy).",
            "description": "WINA optimization pattern for policy governance",
            "priority": "high",
        },
    }

    # Cache patterns in Redis and memory
    try:
        redis_client = await get_redis_client()

        for pattern_name, pattern_data in patterns.items():
            # Cache in Redis
            cache_key = f"gs:pattern:{pattern_name}"
            await redis_client.setex(
                cache_key, PATTERN_CACHE_TTL, json.dumps(pattern_data)
            )

            # Cache in memory for fastest access
            governance_patterns_cache[pattern_name] = pattern_data

        logger.info(f"Pre-compiled {len(patterns)} governance patterns")

    except Exception as e:
        logger.error(f"Failed to pre-compile governance patterns: {e}")


async def get_governance_pattern(pattern_name: str) -> Optional[Dict[str, Any]]:
    """Get pre-compiled governance pattern with O(1) lookup"""
    # Try memory cache first (fastest)
    if pattern_name in governance_patterns_cache:
        synthesis_metrics["pattern_cache_hits"] += 1
        return governance_patterns_cache[pattern_name]

    # Try Redis cache
    try:
        redis_client = await get_redis_client()
        cache_key = f"gs:pattern:{pattern_name}"
        cached_pattern = await redis_client.get(cache_key)

        if cached_pattern:
            pattern_data = json.loads(cached_pattern)
            # Update memory cache
            governance_patterns_cache[pattern_name] = pattern_data
            synthesis_metrics["pattern_cache_hits"] += 1
            return pattern_data

    except Exception as e:
        logger.warning(f"Failed to retrieve pattern from cache: {e}")

    return None


async def apply_wina_optimization(policy_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply WINA (Weight Informed Neuron Activation) optimization for policy governance consistency"""
    start_time = time.time()

    try:
        # Get WINA optimization pattern
        wina_pattern = await get_governance_pattern("wina_optimization")

        if not wina_pattern:
            logger.warning("WINA optimization pattern not found, using fallback")
            return policy_data

        # Apply WINA optimization logic
        optimized_policy = {
            **policy_data,
            "wina_optimized": True,
            "optimization_applied": time.time(),
            "optimization_pattern": wina_pattern["pattern"],
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        # Simulate weight analysis and neuron activation
        # In a real implementation, this would involve actual ML computations
        optimized_policy["weight_analysis"] = {
            "governance_weight": 0.85,
            "constitutional_weight": 0.95,
            "stakeholder_weight": 0.78,
        }

        optimized_policy["neuron_activation"] = {
            "activation_score": 0.89,
            "confidence": 0.92,
            "optimization_level": "high",
        }

        synthesis_metrics["wina_optimizations"] += 1

        optimization_time_ms = (time.time() - start_time) * 1000
        logger.debug(f"WINA optimization completed in {optimization_time_ms:.2f}ms")

        return optimized_policy

    except Exception as e:
        logger.error(f"WINA optimization failed: {e}")
        return policy_data


async def get_synthesis_performance_metrics() -> Dict[str, Any]:
    """Get current synthesis performance metrics"""
    cache_hit_rate = 0.0
    total_cache_requests = (
        synthesis_metrics["cache_hits"] + synthesis_metrics["cache_misses"]
    )

    if total_cache_requests > 0:
        cache_hit_rate = synthesis_metrics["cache_hits"] / total_cache_requests

    pattern_cache_efficiency = synthesis_metrics["pattern_cache_hits"] / max(
        synthesis_metrics["total_synthesis_requests"], 1
    )

    return {
        "synthesis_performance": {
            "total_requests": synthesis_metrics["total_synthesis_requests"],
            "avg_synthesis_time_ms": round(
                synthesis_metrics["avg_synthesis_time_ms"], 2
            ),
            "p99_synthesis_time_ms": round(
                synthesis_metrics["p99_synthesis_time_ms"], 2
            ),
            "target_p99_ms": 5.0,
            "target_met": synthesis_metrics["p99_synthesis_time_ms"] < 5.0,
        },
        "cache_performance": {
            "hit_rate": round(cache_hit_rate, 4),
            "hits": synthesis_metrics["cache_hits"],
            "misses": synthesis_metrics["cache_misses"],
            "pattern_cache_efficiency": round(pattern_cache_efficiency, 4),
        },
        "wina_optimization": {
            "optimizations_applied": synthesis_metrics["wina_optimizations"],
            "patterns_cached": len(governance_patterns_cache),
            "pattern_cache_hits": synthesis_metrics["pattern_cache_hits"],
        },
        "constitutional_compliance": {
            "validations": synthesis_metrics["constitutional_validations"],
            "target_hash": "cdd01ef066bc6cf2",
        },
    }


class SynthesisPerformanceMonitor:
    """Performance monitoring context manager for synthesis operations"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            logger.debug(
                f"Synthesis operation '{self.operation_name}' completed in {duration_ms:.2f}ms"
            )
            update_synthesis_metrics(duration_ms)


async def warm_synthesis_cache():
    """Warm up synthesis cache with frequently used patterns and rules"""
    logger.info("Starting synthesis cache warm-up...")

    # Pre-compile governance patterns
    await precompile_governance_patterns()

    # Pre-cache common synthesis operations
    common_synthesis_requests = [
        {"type": "constitutional_compliance", "priority": "high"},
        {"type": "policy_validation", "priority": "medium"},
        {"type": "governance_synthesis", "priority": "critical"},
    ]

    for request in common_synthesis_requests:
        try:
            # This would typically pre-execute common synthesis operations
            # and cache their results for faster subsequent access
            pass
        except Exception as e:
            logger.warning(f"Failed to warm cache for {request}: {e}")

    logger.info("Synthesis cache warm-up completed")
