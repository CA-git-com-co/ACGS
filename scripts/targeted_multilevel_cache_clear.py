#!/usr/bin/env python3
"""
Targeted Multi-Level Cache Clear

This script specifically targets the multi-level cache manager and clears
the exact cache entries that are causing the constitutional compliance issue.
"""

import asyncio
import logging
import sys
import time
import hashlib
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def clear_multilevel_cache_targeted():
    """Clear the multi-level cache in a targeted way."""
    logger.info("🎯 Targeted multi-level cache clearing...")

    try:
        from services.shared.multi_level_cache import MultiLevelCacheManager

        # Initialize cache manager
        config = {"constitutional_hash": "cdd01ef066bc6cf2"}
        cache_manager = MultiLevelCacheManager(config=config)
        await cache_manager.initialize()

        # Step 1: Clear L1 memory cache completely
        logger.info("🧹 Clearing L1 memory cache...")
        if hasattr(cache_manager, "l1_cache") and hasattr(
            cache_manager.l1_cache, "cache"
        ):
            before_count = len(cache_manager.l1_cache.cache)
            cache_manager.l1_cache.cache.clear()
            logger.info(f"✅ Cleared {before_count} L1 cache entries")

        # Step 2: Clear L2 process cache completely
        logger.info("🧹 Clearing L2 process cache...")
        if hasattr(cache_manager, "l2_cache") and hasattr(
            cache_manager.l2_cache, "cache"
        ):
            before_count = len(cache_manager.l2_cache.cache)
            cache_manager.l2_cache.cache.clear()
            if hasattr(cache_manager.l2_cache, "compiled_rules"):
                cache_manager.l2_cache.compiled_rules.clear()
            logger.info(f"✅ Cleared {before_count} L2 cache entries")

        # Step 3: Clear L3 Redis cache with specific patterns
        logger.info("🧹 Clearing L3 Redis cache...")
        if hasattr(cache_manager, "l3_cache") and cache_manager.l3_cache.redis_client:
            # Clear all keys in database 1
            await cache_manager.l3_cache.redis_client.flushdb()
            logger.info("✅ Cleared L3 Redis database")

            # Also clear specific patterns
            patterns = [
                "multimodal_ai:*",
                "multimodal:*",
                "constitutional_validation:*",
                "*constitutional*",
                "*926ad8db937b9470*",  # The specific cache key we saw
            ]

            for pattern in patterns:
                try:
                    keys = await cache_manager.l3_cache.redis_client.keys(pattern)
                    if keys:
                        await cache_manager.l3_cache.redis_client.delete(*keys)
                        logger.info(
                            f"✅ Cleared {len(keys)} keys for pattern: {pattern}"
                        )
                except Exception as e:
                    logger.warning(f"⚠️ Failed to clear pattern {pattern}: {e}")

        # Step 4: Reset Bloom filter
        logger.info("🧹 Resetting Bloom filter...")
        if hasattr(cache_manager, "bloom_filter"):
            cache_manager.bloom_filter.bit_array = [
                False
            ] * cache_manager.bloom_filter.bit_array_size
            cache_manager.bloom_filter.items_added = 0
            logger.info("✅ Bloom filter reset")

        # Step 5: Reset metrics
        if hasattr(cache_manager, "metrics"):
            from services.shared.multi_level_cache import CacheMetrics

            cache_manager.metrics = CacheMetrics()
            logger.info("✅ Cache metrics reset")

        # Step 6: Force a complete cache invalidation
        logger.info("🧹 Force complete cache invalidation...")
        await cache_manager.clear_all_caches()
        logger.info("✅ Complete cache invalidation done")

        return True

    except Exception as e:
        logger.error(f"❌ Targeted cache clearing failed: {e}")
        return False


async def verify_cache_cleared():
    """Verify that the cache is actually cleared."""
    logger.info("🔍 Verifying cache is cleared...")

    try:
        from services.shared.multi_level_cache import MultiLevelCacheManager

        # Initialize fresh cache manager
        config = {"constitutional_hash": "cdd01ef066bc6cf2"}
        cache_manager = MultiLevelCacheManager(config=config)
        await cache_manager.initialize()

        # Test the specific cache key that was causing issues
        test_cache_key = "multimodal:constitutional_validation:926ad8db937b9470"

        cache_result = await cache_manager.get_constitutional_ruling(
            "multimodal_ai", test_cache_key, {}
        )

        if cache_result.get("result"):
            logger.error(
                f"❌ Cache NOT cleared - still found entry for {test_cache_key}"
            )
            logger.error(f"   Cached data: {cache_result['result']}")
            return False
        else:
            logger.info(f"✅ Cache cleared - no entry found for {test_cache_key}")
            return True

    except Exception as e:
        logger.error(f"❌ Cache verification failed: {e}")
        return False


async def test_constitutional_compliance():
    """Test constitutional compliance after cache clearing."""
    logger.info("🔍 Testing constitutional compliance...")

    try:
        from services.shared.multimodal_ai_service import (
            get_multimodal_service,
            MultimodalRequest,
            RequestType,
            ContentType,
        )

        service = await get_multimodal_service()

        # Test with the exact same content that was failing
        test_content = "Citizens have the right to participate in democratic processes and transparent governance."
        request = MultimodalRequest(
            request_id=f"targeted_test_{int(time.time())}",
            request_type=RequestType.CONSTITUTIONAL_VALIDATION,
            content_type=ContentType.TEXT_ONLY,
            text_content=test_content,
            priority="high",
        )

        response = await service.process_request(request)

        success = response.constitutional_compliance == True

        if success:
            logger.info("✅ Constitutional compliance test PASSED")
            logger.info(f"   Compliant: {response.constitutional_compliance}")
            logger.info(f"   Confidence: {response.confidence_score:.3f}")
            logger.info(f"   Model: {response.model_used.value}")
        else:
            logger.error("❌ Constitutional compliance test FAILED")
            logger.error(
                f"   Expected: True, Actual: {response.constitutional_compliance}"
            )
            logger.error(f"   Confidence: {response.confidence_score:.3f}")

        return success

    except Exception as e:
        logger.error(f"❌ Constitutional compliance test failed: {e}")
        return False


async def main():
    """Main execution function."""
    logger.info("🎯 Targeted Multi-Level Cache Clear")
    logger.info("=" * 50)

    start_time = time.time()

    # Step 1: Clear multi-level cache
    logger.info("\n📋 Step 1: Clear Multi-Level Cache")
    clear_success = await clear_multilevel_cache_targeted()

    if not clear_success:
        logger.error("❌ Cache clearing failed")
        return 1

    # Step 2: Verify cache is cleared
    logger.info("\n📋 Step 2: Verify Cache Cleared")
    verify_success = await verify_cache_cleared()

    if not verify_success:
        logger.error("❌ Cache verification failed")
        return 1

    # Step 3: Test constitutional compliance
    logger.info("\n📋 Step 3: Test Constitutional Compliance")
    test_success = await test_constitutional_compliance()

    total_time = time.time() - start_time

    # Final results
    logger.info("\n" + "=" * 50)
    logger.info("🎯 RESULTS")
    logger.info("=" * 50)

    if test_success:
        logger.info("🎉 SUCCESS! Cache clearing resolved the issue!")
        logger.info("✅ Multi-level cache cleared successfully")
        logger.info("✅ Constitutional compliance test passing")
        logger.info("✅ Democratic content correctly identified as compliant")
        logger.info(f"⏱️ Total time: {total_time:.2f} seconds")
        return 0
    else:
        logger.error("❌ FAILED - Constitutional compliance still not working")
        logger.error("   Further investigation required")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
