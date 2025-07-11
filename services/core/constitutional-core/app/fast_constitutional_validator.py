"""
Fast Constitutional Validator with Enhanced Caching
Constitutional Hash: cdd01ef066bc6cf2

Optimized constitutional validation service designed to achieve <1ms P99 latency
through aggressive caching, precomputed validation patterns, and optimized algorithms.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from functools import lru_cache

import asyncio
import aioredis
from pydantic import BaseModel

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Pre-compiled validation patterns for ultra-fast checks
HARMFUL_PATTERNS = frozenset([
    'harmful', 'dangerous', 'malicious', 'toxic', 'violent', 'illegal',
    'unethical', 'discriminatory', 'hateful', 'threatening', 'abusive'
])

COMPLIANCE_KEYWORDS = frozenset([
    'ethical', 'fair', 'transparent', 'accountable', 'responsible', 
    'constitutional', 'compliant', 'legitimate', 'beneficial', 'safe'
])


@dataclass(frozen=True)
class ValidationCacheKey:
    """Immutable cache key for validation results."""
    content_hash: str
    context_hash: str
    principles_hash: str


@dataclass
class FastValidationResult:
    """Lightweight validation result optimized for speed."""
    compliant: bool
    score: float
    violated_principles: List[str]
    reasoning: List[str]
    recommendations: List[str]
    constitutional_hash: str
    cache_hit: bool
    validation_time_us: int  # Microseconds for precision
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "compliant": self.compliant,
            "score": self.score,
            "violated_principles": self.violated_principles,
            "reasoning": self.reasoning,
            "recommendations": self.recommendations,
            "constitutional_hash": self.constitutional_hash,
            "metadata": {
                "cache_hit": self.cache_hit,
                "validation_time_us": self.validation_time_us,
                "evaluation_time": datetime.now(timezone.utc).isoformat(),
                "method": "fast_cached"
            }
        }


class MemoryCache:
    """High-performance in-memory LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._access_order: List[str] = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, return None if expired or missing."""
        if key not in self._cache:
            return None
            
        value, timestamp = self._cache[key]
        current_time = time.time()
        
        # Check TTL
        if current_time - timestamp > self.ttl_seconds:
            self._remove_key(key)
            return None
        
        # Update access order (LRU)
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp."""
        current_time = time.time()
        
        # Remove oldest if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[key] = (value, current_time)
        
        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def _remove_key(self, key: str) -> None:
        """Remove key from cache and access order."""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        valid_entries = sum(
            1 for _, timestamp in self._cache.values()
            if current_time - timestamp <= self.ttl_seconds
        )
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }


class FastConstitutionalValidator:
    """Ultra-fast constitutional validator with multi-level caching."""
    
    def __init__(self, redis_url: Optional[str] = None):
        # Multi-level cache architecture
        self.l1_cache = MemoryCache(max_size=5000, ttl_seconds=300)  # 5 min L1
        self.l2_cache = MemoryCache(max_size=20000, ttl_seconds=3600)  # 1 hr L2
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Pre-computed validation scores for common patterns
        self._precomputed_scores = self._build_precomputed_scores()
        
        # Performance metrics
        self.metrics = {
            "total_validations": 0,
            "l1_cache_hits": 0,
            "l2_cache_hits": 0,
            "redis_cache_hits": 0,
            "cache_misses": 0,
            "avg_validation_time_us": 0.0
        }
        
        # Initialize Redis connection if URL provided
        if redis_url:
            asyncio.create_task(self._init_redis(redis_url))
    
    async def _init_redis(self, redis_url: str) -> None:
        """Initialize Redis connection for L3 cache."""
        try:
            self.redis_client = await aioredis.from_url(redis_url)
            logger.info("Redis L3 cache initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
            self.redis_client = None
    
    def _build_precomputed_scores(self) -> Dict[str, float]:
        """Build precomputed validation scores for common patterns."""
        scores = {}
        
        # Harmful content patterns (low scores)
        for pattern in HARMFUL_PATTERNS:
            scores[pattern] = 0.1
        
        # Compliance patterns (high scores)
        for pattern in COMPLIANCE_KEYWORDS:
            scores[pattern] = 0.9
        
        # Length-based scoring
        for length in [10, 50, 100, 500, 1000]:
            scores[f"len_{length}"] = min(0.9, 0.5 + (length / 1000))
        
        return scores
    
    def _create_cache_key(
        self, 
        content: str, 
        context: Dict[str, Any], 
        principles: List[str]
    ) -> str:
        """Create a deterministic cache key from validation inputs."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        context_hash = hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()[:16]
        principles_hash = hashlib.md5(json.dumps(sorted(principles)).encode()).hexdigest()[:16]
        
        return f"cv:{content_hash}:{context_hash}:{principles_hash}"
    
    @lru_cache(maxsize=1000)
    def _fast_pattern_check(self, content_lower: str) -> Tuple[bool, float, List[str]]:
        """Ultra-fast pattern matching with LRU cache."""
        violated_principles = []
        base_score = 0.7
        
        # Check for harmful patterns
        harmful_found = any(pattern in content_lower for pattern in HARMFUL_PATTERNS)
        if harmful_found:
            violated_principles.append("non-maleficence")
            base_score = max(0.1, base_score - 0.6)
        
        # Check for compliance patterns
        compliance_found = any(pattern in content_lower for pattern in COMPLIANCE_KEYWORDS)
        if compliance_found:
            base_score = min(1.0, base_score + 0.2)
        
        # Length-based adjustment
        content_len = len(content_lower)
        if content_len < 10:
            violated_principles.append("adequacy")
            base_score = max(0.3, base_score - 0.2)
        else:
            length_bonus = min(0.2, content_len / 5000)
            base_score = min(1.0, base_score + length_bonus)
        
        is_compliant = len(violated_principles) == 0 and base_score >= 0.7
        
        return is_compliant, base_score, violated_principles
    
    async def _get_from_redis(self, cache_key: str) -> Optional[FastValidationResult]:
        """Get validation result from Redis L3 cache."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return FastValidationResult(**data)
        except Exception as e:
            logger.debug(f"Redis cache get error: {e}")
        
        return None
    
    async def _set_in_redis(self, cache_key: str, result: FastValidationResult) -> None:
        """Set validation result in Redis L3 cache."""
        if not self.redis_client:
            return
        
        try:
            # Convert to dict and exclude cache_hit for storage
            data = result.to_dict()
            data.pop("metadata", None)  # Remove metadata to save space
            
            await self.redis_client.setex(
                cache_key, 
                7200,  # 2 hour TTL for Redis
                json.dumps(data)
            )
        except Exception as e:
            logger.debug(f"Redis cache set error: {e}")
    
    async def validate_fast(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        principles: Optional[List[str]] = None
    ) -> FastValidationResult:
        """Ultra-fast constitutional validation with multi-level caching."""
        start_time = time.perf_counter_ns()
        
        # Normalize inputs
        content = content.strip()
        context = context or {}
        principles = principles or []
        
        # Create cache key
        cache_key = self._create_cache_key(content, context, principles)
        
        # L1 Cache check (fastest)
        cached_result = self.l1_cache.get(cache_key)
        if cached_result:
            self.metrics["l1_cache_hits"] += 1
            self.metrics["total_validations"] += 1
            cached_result.cache_hit = True
            cached_result.validation_time_us = (time.perf_counter_ns() - start_time) // 1000
            return cached_result
        
        # L2 Cache check
        cached_result = self.l2_cache.get(cache_key)
        if cached_result:
            self.metrics["l2_cache_hits"] += 1
            self.metrics["total_validations"] += 1
            self.l1_cache.set(cache_key, cached_result)  # Promote to L1
            cached_result.cache_hit = True
            cached_result.validation_time_us = (time.perf_counter_ns() - start_time) // 1000
            return cached_result
        
        # L3 Redis cache check
        cached_result = await self._get_from_redis(cache_key)
        if cached_result:
            self.metrics["redis_cache_hits"] += 1
            self.metrics["total_validations"] += 1
            self.l1_cache.set(cache_key, cached_result)  # Promote to L1
            self.l2_cache.set(cache_key, cached_result)  # Promote to L2
            cached_result.cache_hit = True
            cached_result.validation_time_us = (time.perf_counter_ns() - start_time) // 1000
            return cached_result
        
        # Cache miss - perform actual validation
        self.metrics["cache_misses"] += 1
        result = await self._perform_validation(content, context, principles)
        
        # Calculate timing
        validation_time_us = (time.perf_counter_ns() - start_time) // 1000
        result.validation_time_us = validation_time_us
        result.cache_hit = False
        
        # Update metrics
        self.metrics["total_validations"] += 1
        total_time = self.metrics["avg_validation_time_us"] * (self.metrics["total_validations"] - 1)
        self.metrics["avg_validation_time_us"] = (total_time + validation_time_us) / self.metrics["total_validations"]
        
        # Store in all cache levels
        self.l1_cache.set(cache_key, result)
        self.l2_cache.set(cache_key, result)
        await self._set_in_redis(cache_key, result)
        
        return result
    
    async def _perform_validation(
        self,
        content: str,
        context: Dict[str, Any],
        principles: List[str]
    ) -> FastValidationResult:
        """Perform actual constitutional validation (optimized)."""
        
        # Fast pattern matching
        content_lower = content.lower()
        is_compliant, score, violated_principles = self._fast_pattern_check(content_lower)
        
        # Generate reasoning and recommendations
        reasoning = []
        recommendations = []
        
        if violated_principles:
            if "non-maleficence" in violated_principles:
                reasoning.append("Content contains potentially harmful language")
                recommendations.append("Remove harmful content and rephrase positively")
            
            if "adequacy" in violated_principles:
                reasoning.append("Content is too brief for proper evaluation")
                recommendations.append("Provide more detailed content for evaluation")
        else:
            reasoning.append("Content meets constitutional compliance standards")
        
        # Apply context-specific adjustments
        if context.get("high_risk", False):
            score = max(0.1, score - 0.1)
            if score < 0.8:
                is_compliant = False
                reasoning.append("High-risk context requires elevated compliance standards")
        
        return FastValidationResult(
            compliant=is_compliant,
            score=score,
            violated_principles=violated_principles,
            reasoning=reasoning,
            recommendations=recommendations,
            constitutional_hash=CONSTITUTIONAL_HASH,
            cache_hit=False,
            validation_time_us=0  # Will be set by caller
        )
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache performance statistics."""
        total_validations = max(1, self.metrics["total_validations"])
        
        return {
            "performance_metrics": {
                "total_validations": self.metrics["total_validations"],
                "avg_validation_time_us": round(self.metrics["avg_validation_time_us"], 2),
                "avg_validation_time_ms": round(self.metrics["avg_validation_time_us"] / 1000, 3),
                "target_p99_ms": 1.0,
                "current_performance": "OPTIMAL" if self.metrics["avg_validation_time_us"] < 1000 else "SUBOPTIMAL"
            },
            "cache_performance": {
                "l1_hit_rate": round(self.metrics["l1_cache_hits"] / total_validations * 100, 2),
                "l2_hit_rate": round(self.metrics["l2_cache_hits"] / total_validations * 100, 2),
                "redis_hit_rate": round(self.metrics["redis_cache_hits"] / total_validations * 100, 2),
                "overall_hit_rate": round(
                    (self.metrics["l1_cache_hits"] + self.metrics["l2_cache_hits"] + self.metrics["redis_cache_hits"]) 
                    / total_validations * 100, 2
                ),
                "cache_miss_rate": round(self.metrics["cache_misses"] / total_validations * 100, 2)
            },
            "cache_details": {
                "l1_cache": self.l1_cache.stats(),
                "l2_cache": self.l2_cache.stats(),
                "redis_available": self.redis_client is not None
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    async def warmup_cache(self, sample_contents: List[str]) -> None:
        """Warm up the cache with common validation patterns."""
        logger.info(f"Warming up constitutional validation cache with {len(sample_contents)} samples")
        
        for content in sample_contents:
            await self.validate_fast(content)
        
        logger.info("Cache warmup completed")
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()


# Global fast validator instance
_fast_validator: Optional[FastConstitutionalValidator] = None


def get_fast_validator() -> FastConstitutionalValidator:
    """Get or create the global fast constitutional validator."""
    global _fast_validator
    if _fast_validator is None:
        # Use Redis URL from environment or Docker Compose setup
        redis_url = "redis://redis:6379/3"  # Database 3 for constitutional cache
        _fast_validator = FastConstitutionalValidator(redis_url)
    return _fast_validator


async def validate_constitutional_fast(
    content: str,
    context: Optional[Dict[str, Any]] = None,
    principles: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Convenience function for fast constitutional validation."""
    validator = get_fast_validator()
    result = await validator.validate_fast(content, context, principles)
    return result.to_dict()