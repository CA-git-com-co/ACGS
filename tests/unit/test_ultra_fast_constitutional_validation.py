"""
Unit Tests for Ultra-Fast Constitutional Validation
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive test suite for the UltraFastConstitutionalValidator
covering all performance optimization features and edge cases.

Test Coverage:
- Hash validation performance and accuracy
- Batch validation functionality
- Context-aware validation
- Cache optimization and hit rates
- Performance metrics and monitoring
- Error handling and edge cases
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any

from services.shared.constitutional.validation import (
    UltraFastConstitutionalValidator,
    CONSTITUTIONAL_HASH,
    PERFORMANCE_TARGETS
)


class TestUltraFastConstitutionalValidator:
    """Test suite for UltraFastConstitutionalValidator."""

    @pytest.fixture
    def validator(self):
        """Create a fresh validator instance for each test."""
        return UltraFastConstitutionalValidator()

    def test_initialization(self, validator):
        """Test validator initialization."""
        assert validator.constitutional_hash == CONSTITUTIONAL_HASH
        assert validator._fast_path_enabled is True
        assert validator._batch_processing_enabled is True
        assert len(validator._known_good_hashes) >= 1
        assert CONSTITUTIONAL_HASH in validator._known_good_hashes

    def test_valid_hash_validation(self, validator):
        """Test validation of correct constitutional hash."""
        result = validator.validate_hash(CONSTITUTIONAL_HASH)
        assert result is True
        assert validator._cache_hits > 0

    def test_invalid_hash_validation(self, validator):
        """Test validation of incorrect hash."""
        invalid_hash = "invalid_hash_123"
        result = validator.validate_hash(invalid_hash)
        assert result is False
        assert validator._cache_misses > 0

    def test_malformed_hash_validation(self, validator):
        """Test validation of malformed hashes."""
        malformed_hashes = [
            "",
            "short",
            "toolongtobeavalidhash123456789",
            "contains-invalid-chars!",
            "UPPERCASE_HASH_123",
            None,
        ]
        
        for hash_value in malformed_hashes:
            if hash_value is not None:
                result = validator.validate_hash(hash_value)
                assert result is False

    def test_fast_path_optimization(self, validator):
        """Test fast-path optimization for known hashes."""
        # First validation should populate cache
        validator.validate_hash(CONSTITUTIONAL_HASH)
        initial_fast_path_hits = validator._fast_path_hits
        
        # Subsequent validations should use fast path
        for _ in range(10):
            result = validator.validate_hash(CONSTITUTIONAL_HASH)
            assert result is True
        
        assert validator._fast_path_hits > initial_fast_path_hits

    def test_performance_targets(self, validator):
        """Test that validation meets performance targets."""
        # Warm up the validator
        for _ in range(100):
            validator.validate_hash(CONSTITUTIONAL_HASH)
        
        # Measure performance
        start_time = time.perf_counter()
        for _ in range(1000):
            validator.validate_hash(CONSTITUTIONAL_HASH)
        elapsed = time.perf_counter() - start_time
        
        avg_time_ms = (elapsed / 1000) * 1000
        assert avg_time_ms < PERFORMANCE_TARGETS["validation_latency_ms"]

    @pytest.mark.asyncio
    async def test_async_validation(self, validator):
        """Test async validation functionality."""
        result = await validator.async_validate_hash(CONSTITUTIONAL_HASH)
        assert result is True
        
        result = await validator.async_validate_hash("invalid_hash")
        assert result is False

    @pytest.mark.asyncio
    async def test_batch_validation(self, validator):
        """Test batch validation functionality."""
        test_hashes = [
            CONSTITUTIONAL_HASH,
            CONSTITUTIONAL_HASH,
            "invalid_hash_1",
            CONSTITUTIONAL_HASH,
            "invalid_hash_2"
        ]
        
        results = await validator.batch_validate_hashes(test_hashes)
        
        assert len(results) == len(test_hashes)
        assert results[0] is True  # Valid hash
        assert results[1] is True  # Valid hash
        assert results[2] is False  # Invalid hash
        assert results[3] is True  # Valid hash
        assert results[4] is False  # Invalid hash
        
        assert validator._batch_validations > 0

    @pytest.mark.asyncio
    async def test_batch_validation_performance(self, validator):
        """Test batch validation performance."""
        # Large batch test
        large_batch = [CONSTITUTIONAL_HASH] * 100
        
        start_time = time.perf_counter()
        results = await validator.batch_validate_hashes(large_batch)
        elapsed = time.perf_counter() - start_time
        
        assert len(results) == 100
        assert all(results)
        
        # Should be faster than individual validations
        per_item_time = (elapsed / 100) * 1000
        assert per_item_time < PERFORMANCE_TARGETS["validation_latency_ms"]

    def test_context_validation(self, validator):
        """Test context-aware validation."""
        context = {"service": "test", "operation": "validate"}
        
        result = validator.validate_with_context(CONSTITUTIONAL_HASH, context)
        
        assert result["valid"] is True
        assert result["context"] == context
        assert "cached" in result

    def test_context_validation_caching(self, validator):
        """Test context validation caching."""
        context = {"service": "test", "operation": "validate"}
        
        # First call should not be cached
        result1 = validator.validate_with_context(CONSTITUTIONAL_HASH, context)
        assert result1["cached"] is False
        
        # Second call should be cached
        result2 = validator.validate_with_context(CONSTITUTIONAL_HASH, context)
        assert result2["cached"] is True

    def test_environment_validation(self, validator):
        """Test environment validation."""
        with patch.dict('os.environ', {'CONSTITUTIONAL_HASH': CONSTITUTIONAL_HASH}):
            result = validator.validate_environment()
            
            assert result["constitutional_compliance"] is True
            assert result["hash_value"] == CONSTITUTIONAL_HASH
            assert "performance_metrics" in result

    def test_environment_validation_missing_hash(self, validator):
        """Test environment validation with missing hash."""
        with patch.dict('os.environ', {}, clear=True):
            result = validator.validate_environment()
            
            assert result["constitutional_compliance"] is False
            assert result["hash_value"] == ""

    def test_performance_metrics(self, validator):
        """Test performance metrics collection."""
        # Generate some activity
        for _ in range(50):
            validator.validate_hash(CONSTITUTIONAL_HASH)
        for _ in range(10):
            validator.validate_hash("invalid_hash")
        
        metrics = validator.get_detailed_metrics()
        
        assert "performance_summary" in metrics
        assert "cache_statistics" in metrics
        assert "optimization_status" in metrics
        
        perf_summary = metrics["performance_summary"]
        assert perf_summary["total_validations"] == 60
        assert perf_summary["cache_hit_rate"] > 0
        assert perf_summary["fast_path_rate"] > 0

    def test_cache_statistics(self, validator):
        """Test cache statistics tracking."""
        # Generate cache hits and misses
        validator.validate_hash(CONSTITUTIONAL_HASH)  # Hit
        validator.validate_hash("invalid_hash")       # Miss
        validator.validate_hash(CONSTITUTIONAL_HASH)  # Hit
        
        metrics = validator.get_detailed_metrics()
        cache_stats = metrics["cache_statistics"]
        
        assert cache_stats["cache_hits"] >= 2
        assert cache_stats["cache_misses"] >= 1
        assert cache_stats["known_good_hashes"] >= 1
        assert cache_stats["known_bad_hashes"] >= 1

    def test_optimization_functionality(self, validator):
        """Test performance optimization."""
        # Generate some performance data
        for _ in range(100):
            validator.validate_hash(CONSTITUTIONAL_HASH)
        
        optimization_result = validator.optimize_performance()
        
        assert "optimizations_applied" in optimization_result
        assert "recommendations" in optimization_result
        assert "current_metrics" in optimization_result
        assert optimization_result["constitutional_hash"] == CONSTITUTIONAL_HASH

    def test_metrics_reset(self, validator):
        """Test metrics reset functionality."""
        # Generate some activity
        validator.validate_hash(CONSTITUTIONAL_HASH)
        validator.validate_hash("invalid_hash")
        
        # Verify metrics exist
        assert validator._validation_count > 0
        assert validator._cache_hits > 0
        
        # Reset metrics
        validator.reset_metrics()
        
        # Verify metrics are reset
        assert validator._validation_count == 0
        assert validator._cache_hits == 0
        assert validator._cache_misses == 0
        assert validator._fast_path_hits == 0
        assert validator._batch_validations == 0

    def test_cache_size_limits(self, validator):
        """Test cache size management."""
        # Fill up the context cache
        for i in range(60000):  # Exceed the 50000 limit
            context = {"test": f"value_{i}"}
            validator.validate_with_context(CONSTITUTIONAL_HASH, context)
        
        # Cache should be limited in size
        assert len(validator._validation_cache) <= 50000

    def test_concurrent_access(self, validator):
        """Test thread safety of validator."""
        import threading
        
        results = []
        errors = []
        
        def validate_worker():
            try:
                for _ in range(100):
                    result = validator.validate_hash(CONSTITUTIONAL_HASH)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=validate_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 1000
        assert all(results)

    def test_edge_cases(self, validator):
        """Test edge cases and error conditions."""
        # Test with None
        try:
            validator.validate_hash(None)
        except (TypeError, AttributeError):
            pass  # Expected to fail
        
        # Test with non-string types
        for invalid_input in [123, [], {}, object()]:
            try:
                result = validator.validate_hash(invalid_input)
                # If it doesn't raise an exception, it should return False
                assert result is False
            except (TypeError, AttributeError):
                pass  # Also acceptable

    def test_memory_efficiency(self, validator):
        """Test memory efficiency of caching."""
        import sys
        
        # Get initial memory usage
        initial_size = sys.getsizeof(validator._validation_cache)
        
        # Add many entries
        for i in range(1000):
            context = {"test": f"small_value_{i}"}
            validator.validate_with_context(CONSTITUTIONAL_HASH, context)
        
        # Memory should not grow excessively
        final_size = sys.getsizeof(validator._validation_cache)
        growth_ratio = final_size / max(initial_size, 1)
        
        # Should not grow more than 100x
        assert growth_ratio < 100

    @pytest.mark.asyncio
    async def test_batch_validation_edge_cases(self, validator):
        """Test batch validation edge cases."""
        # Empty batch
        results = await validator.batch_validate_hashes([])
        assert results == []
        
        # Single item batch
        results = await validator.batch_validate_hashes([CONSTITUTIONAL_HASH])
        assert results == [True]
        
        # Large batch
        large_batch = [CONSTITUTIONAL_HASH] * 1000
        results = await validator.batch_validate_hashes(large_batch)
        assert len(results) == 1000
        assert all(results)

    def test_performance_regression_detection(self, validator):
        """Test that performance doesn't regress."""
        # Baseline performance
        start_time = time.perf_counter()
        for _ in range(1000):
            validator.validate_hash(CONSTITUTIONAL_HASH)
        baseline_time = time.perf_counter() - start_time
        
        # Performance after heavy usage
        for _ in range(10000):
            validator.validate_hash(CONSTITUTIONAL_HASH)
        
        start_time = time.perf_counter()
        for _ in range(1000):
            validator.validate_hash(CONSTITUTIONAL_HASH)
        heavy_usage_time = time.perf_counter() - start_time
        
        # Performance should not degrade significantly
        performance_ratio = heavy_usage_time / baseline_time
        assert performance_ratio < 2.0  # Should not be more than 2x slower


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
