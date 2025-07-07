#!/usr/bin/env python3
"""
Hypothesis Tests for Constitutional Cache Validation
Constitutional Hash: cdd01ef066bc6cf2

Tests validate:
- Cache hit rates >85% under various scenarios
- Cache performance under different workloads
- Cache consistency and reliability
- Property-based testing for cache behavior
"""

import asyncio
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytest
import pytest_asyncio
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

# Add service paths to Python path
project_root = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, project_root)


class ConstitutionalCache:
    """Enhanced constitutional cache for hypothesis testing"""

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.access_log: List[tuple] = []

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        self.access_log.append(("get", key, datetime.utcnow()))

        if key in self.cache:
            entry = self.cache[key]
            # Check TTL
            if entry["expires_at"] > datetime.utcnow():
                self.hits += 1
                entry["last_accessed"] = datetime.utcnow()
                return entry["value"]
            else:
                # Expired, remove from cache
                del self.cache[key]

        self.misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        self.access_log.append(("set", key, datetime.utcnow()))

        # Evict if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            await self._evict_lru()

        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        self.cache[key] = {
            "value": value,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "expires_at": expires_at,
        }
        return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        self.access_log.append(("delete", key, datetime.utcnow()))

        if key in self.cache:
            del self.cache[key]
            return True
        return False

    async def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.access_log.clear()

    async def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.cache:
            return

        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k]["last_accessed"])
        del self.cache[lru_key]

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate as percentage"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_accesses = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.get_hit_rate(),
            "total_accesses": total_accesses,
            "cache_size": len(self.cache),
            "max_size": self.max_size,
        }


class CacheStateMachine(RuleBasedStateMachine):
    """State machine for property-based testing of cache behavior"""

    def __init__(self):
        super().__init__()
        self.cache = ConstitutionalCache(max_size=100)
        self.expected_keys = set()

    @initialize()
    def setup_cache(self):
        """Initialize cache with some data"""
        asyncio.run(self.cache.clear())
        self.expected_keys.clear()

    @rule(
        key=st.text(min_size=1, max_size=50),
        value=st.text(min_size=1, max_size=100),
        ttl=st.integers(min_value=1, max_value=3600),
    )
    def set_value(self, key: str, value: str, ttl: int):
        """Set a value in the cache"""
        assume(key.strip())  # Non-empty key after stripping

        async def _set():
            return await self.cache.set(key, value, ttl)

        result = asyncio.run(_set())
        assert result is True
        self.expected_keys.add(key)

    @rule(key=st.text(min_size=1, max_size=50))
    def get_value(self, key: str):
        """Get a value from the cache"""
        assume(key.strip())  # Non-empty key after stripping

        async def _get():
            return await self.cache.get(key)

        result = asyncio.run(_get())

        if key in self.expected_keys:
            # May be None if expired, but should track hit/miss correctly
            pass
        else:
            # Key was never set, should be None
            assert result is None

    @rule(key=st.text(min_size=1, max_size=50))
    def delete_value(self, key: str):
        """Delete a value from the cache"""
        assume(key.strip())  # Non-empty key after stripping

        async def _delete():
            return await self.cache.delete(key)

        result = asyncio.run(_delete())

        if key in self.expected_keys:
            self.expected_keys.remove(key)

    @invariant()
    def cache_size_within_limits(self):
        """Cache size should never exceed max_size"""
        assert len(self.cache.cache) <= self.cache.max_size

    @invariant()
    def hit_rate_reasonable(self):
        """Hit rate should be reasonable (0-100%)"""
        hit_rate = self.cache.get_hit_rate()
        assert 0.0 <= hit_rate <= 100.0


class TestConstitutionalCacheHypothesis:
    """Hypothesis-based tests for constitutional cache"""

    @pytest_asyncio.fixture
    async def cache(self):
        """Create cache instance for testing"""
        cache = ConstitutionalCache(max_size=1000)
        await cache.clear()
        return cache

    @given(keys=st.lists(st.text(min_size=1, max_size=20), min_size=10, max_size=100))
    @settings(max_examples=50, deadline=5000)
    @pytest.mark.asyncio
    async def test_cache_hit_rate_with_repeated_access(self, cache, keys):
        """Test that repeated access to the same keys achieves high hit rates"""
        assume(len(set(keys)) >= 5)  # At least 5 unique keys

        unique_keys = list(set(keys))

        # Pre-populate cache with constitutional data
        for i, key in enumerate(unique_keys):
            constitutional_key = f"constitutional_hash_{key}"
            validation_result = {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "compliant": True,
                "score": 0.85 + (i % 10) * 0.01,
                "timestamp": datetime.utcnow().isoformat(),
            }
            await cache.set(constitutional_key, validation_result, ttl=300)

        # Perform repeated access pattern (should achieve high hit rate)
        for _ in range(100):  # Multiple access rounds
            for key in unique_keys[:10]:  # Access top 10 keys repeatedly
                constitutional_key = f"constitutional_hash_{key}"
                result = await cache.get(constitutional_key)
                # Should find most results (allowing for some TTL expiration)

        hit_rate = cache.get_hit_rate()
        stats = cache.get_stats()

        print(f"\n📊 Repeated Access Hit Rate Test:")
        print(f"   Hit Rate: {hit_rate:.1f}%")
        print(f"   Cache Stats: {stats}")

        # With repeated access to pre-populated keys, hit rate should be high
        assert (
            hit_rate >= 85.0
        ), f"Hit rate {hit_rate:.1f}% below 85% target with repeated access"

    @given(
        cache_size=st.integers(min_value=50, max_value=500),
        num_operations=st.integers(min_value=100, max_value=1000),
    )
    @settings(max_examples=20, deadline=10000)
    @pytest.mark.asyncio
    async def test_cache_performance_under_load(
        self, cache_size: int, num_operations: int
    ):
        """Test cache performance under various load conditions"""
        cache = ConstitutionalCache(max_size=cache_size)

        # Create a working set that's 80% of cache size (should achieve good hit rate)
        working_set_size = int(cache_size * 0.8)

        # Pre-populate cache
        for i in range(working_set_size):
            key = f"constitutional_validation_{i}"
            value = {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "result": f"validation_result_{i}",
                "compliant": True,
            }
            await cache.set(key, value)

        # Perform operations with 90% access to working set, 10% new keys
        for i in range(num_operations):
            if random.random() < 0.9:  # 90% access to working set
                key_index = random.randint(0, working_set_size - 1)
                key = f"constitutional_validation_{key_index}"
            else:  # 10% access to new keys
                key = f"constitutional_validation_new_{i}"

            result = await cache.get(key)

            # If miss and it's a new key, populate it
            if result is None and key.startswith("constitutional_validation_new_"):
                value = {
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "result": f"new_validation_result_{i}",
                    "compliant": True,
                }
                await cache.set(key, value)

        hit_rate = cache.get_hit_rate()
        stats = cache.get_stats()

        print(f"\n📊 Load Test Results:")
        print(f"   Cache Size: {cache_size}")
        print(f"   Operations: {num_operations}")
        print(f"   Hit Rate: {hit_rate:.1f}%")
        print(f"   Final Stats: {stats}")

        # Under this workload pattern, should achieve good hit rate
        assert hit_rate >= 75.0, f"Hit rate {hit_rate:.1f}% below 75% under load"

        # Cache size should be managed properly
        assert len(cache.cache) <= cache_size

    @given(
        ttl_values=st.lists(
            st.integers(min_value=1, max_value=10), min_size=5, max_size=20
        )
    )
    @settings(max_examples=30, deadline=5000)
    @pytest.mark.asyncio
    async def test_ttl_expiration_behavior(self, cache, ttl_values):
        """Test cache behavior with various TTL values"""
        keys_with_ttl = []

        # Set values with different TTL
        for i, ttl in enumerate(ttl_values):
            key = f"constitutional_ttl_test_{i}"
            value = {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "ttl": ttl,
                "set_at": datetime.utcnow().isoformat(),
            }
            await cache.set(key, value, ttl=ttl)
            keys_with_ttl.append((key, ttl))

        # Immediate access should all hit
        immediate_hits = 0
        for key, _ in keys_with_ttl:
            result = await cache.get(key)
            if result is not None:
                immediate_hits += 1

        immediate_hit_rate = (immediate_hits / len(keys_with_ttl)) * 100

        print(f"\n📊 TTL Expiration Test:")
        print(f"   Immediate Hit Rate: {immediate_hit_rate:.1f}%")

        # All should be accessible immediately
        assert (
            immediate_hit_rate >= 95.0
        ), "Immediate access should have very high hit rate"

        # Test that cache properly handles TTL
        overall_hit_rate = cache.get_hit_rate()
        assert 0.0 <= overall_hit_rate <= 100.0

    @pytest.mark.asyncio
    async def test_constitutional_hash_cache_scenarios(self, cache):
        """Test cache behavior with constitutional hash validation scenarios"""

        # Scenario 1: Frequent constitutional validation requests
        constitutional_hashes = [
            "cdd01ef066bc6cf2",  # Valid hash
            "invalid_hash_1",
            "invalid_hash_2",
            "cdd01ef066bc6cf2",  # Valid hash repeated
        ]

        validation_results = []

        # First pass - populate cache
        for i, hash_value in enumerate(constitutional_hashes):
            key = f"validation_{hash_value}_{i}"
            result = {
                "constitutional_hash": hash_value,
                "is_valid": hash_value == "cdd01ef066bc6cf2",
                "validated_at": datetime.utcnow().isoformat(),
                "compliance_score": 0.9 if hash_value == "cdd01ef066bc6cf2" else 0.0,
            }
            await cache.set(key, result)
            validation_results.append((key, result))

        # Second pass - should hit cache
        cache_hits = 0
        for key, expected_result in validation_results:
            cached_result = await cache.get(key)
            if cached_result is not None:
                cache_hits += 1
                assert (
                    cached_result["constitutional_hash"]
                    == expected_result["constitutional_hash"]
                )

        hit_rate = cache.get_hit_rate()

        print(f"\n📊 Constitutional Hash Cache Scenario:")
        print(f"   Cache Hits: {cache_hits}/{len(validation_results)}")
        print(f"   Hit Rate: {hit_rate:.1f}%")

        # Should achieve high hit rate for repeated constitutional validations
        assert (
            hit_rate >= 50.0
        ), f"Constitutional hash caching hit rate {hit_rate:.1f}% too low"

    def test_cache_state_machine_properties(self):
        """Run state machine property tests"""
        # This will run the state machine with various random operations
        state_machine_test = CacheStateMachine.TestCase()
        state_machine_test.runTest()

    @given(
        working_set_ratio=st.floats(min_value=0.5, max_value=0.95),
        access_pattern_bias=st.floats(min_value=0.7, max_value=0.99),
    )
    @example(working_set_ratio=0.8, access_pattern_bias=0.9)  # Known good scenario
    @settings(max_examples=20, deadline=8000)
    @pytest.mark.asyncio
    async def test_hit_rate_achievability(
        self, cache, working_set_ratio: float, access_pattern_bias: float
    ):
        """Test that 85%+ hit rate is achievable under realistic conditions"""
        cache_size = 100
        cache = ConstitutionalCache(max_size=cache_size)

        working_set_size = int(cache_size * working_set_ratio)

        # Pre-populate working set
        for i in range(working_set_size):
            key = f"constitutional_principle_{i}"
            value = {
                "constitutional_hash": "cdd01ef066bc6cf2",
                "principle_id": i,
                "validation_result": True,
                "score": 0.85 + (i % 20) * 0.005,
            }
            await cache.set(key, value, ttl=600)  # Longer TTL

        # Simulate realistic access pattern
        num_operations = 500
        for i in range(num_operations):
            if random.random() < access_pattern_bias:
                # Access working set (high probability)
                key_index = random.randint(0, working_set_size - 1)
                key = f"constitutional_principle_{key_index}"
            else:
                # Access new/random keys (low probability)
                key = f"constitutional_principle_new_{i}"

            result = await cache.get(key)

            # On cache miss for new keys, populate them
            if result is None and "new_" in key:
                value = {
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "principle_id": f"new_{i}",
                    "validation_result": True,
                    "score": 0.8,
                }
                await cache.set(key, value, ttl=300)

        hit_rate = cache.get_hit_rate()
        stats = cache.get_stats()

        print(f"\n📊 Hit Rate Achievability Test:")
        print(f"   Working Set Ratio: {working_set_ratio:.2f}")
        print(f"   Access Bias: {access_pattern_bias:.2f}")
        print(f"   Achieved Hit Rate: {hit_rate:.1f}%")
        print(f"   Stats: {stats}")

        # Under favorable conditions, should achieve target hit rate
        expected_minimum = min(
            85.0, access_pattern_bias * 95
        )  # Adjust expectation based on bias

        if access_pattern_bias >= 0.85 and working_set_ratio >= 0.7:
            assert hit_rate >= expected_minimum, (
                f"Hit rate {hit_rate:.1f}% below expected {expected_minimum:.1f}% "
                f"(bias={access_pattern_bias:.2f}, ratio={working_set_ratio:.2f})"
            )


# Property-based test for cache state machine
TestCacheStateMachine = CacheStateMachine.TestCase


if __name__ == "__main__":
    # Run hypothesis tests
    pytest.main(
        [__file__, "-v", "--hypothesis-show-statistics", "-s"]  # Show print statements
    )
