#!/usr/bin/env python3
"""
Comprehensive Constitutional Compliance Cache Invalidation Script

This script specifically targets and clears all constitutional validation cache entries
across all cache levels to resolve the issue where cached results with incorrect
compliance values are being returned after the enhanced compliance algorithm fix.

Usage:
    python scripts/comprehensive_constitutional_cache_clear.py [--test]

Options:
    --test    Run immediate verification test after cache clearing
"""

import asyncio
import argparse
import logging
import sys
import time
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.shared.multi_level_cache import MultiLevelCacheManager
from services.shared.multimodal_ai_service import (
    get_multimodal_service,
    MultimodalRequest,
    RequestType,
    ContentType,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ComprehensiveConstitutionalCacheCleaner:
    """Targeted cache cleaner for constitutional validation entries."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.cleared_counts = {
            "multimodal_cache": 0,
            "l1_memory": 0,
            "l2_process": 0,
            "l3_redis": 0,
            "bloom_filter": 0,
            "specific_keys": 0,
        }

    async def initialize(self):
        """Initialize cache managers."""
        logger.info("🔧 Initializing cache managers...")

        try:
            # Initialize multi-level cache manager
            config = {"constitutional_hash": self.constitutional_hash}
            self.multi_level_cache = MultiLevelCacheManager(config=config)
            await self.multi_level_cache.initialize()

            logger.info("✅ Cache managers initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize cache managers: {e}")
            raise

    def _generate_constitutional_validation_cache_keys(self) -> List[str]:
        """Generate cache keys for known constitutional validation content."""

        test_contents = [
            "Citizens have the right to participate in democratic processes and transparent governance.",
            "The constitution protects individual rights and ensures democratic representation.",
        ]

        cache_keys = []

        for content in test_contents:
            # Generate cache keys for both multimodal service and multi-level cache

            # 1. Multimodal service cache key format
            content_parts = [
                "CONSTITUTIONAL_VALIDATION",  # request_type.value
                "TEXT_ONLY",  # content_type.value
                content,  # text_content
                "",  # image_url
                "",  # image_data
                "{}",  # constitutional_context
                self.constitutional_hash,
            ]

            content_string = "|".join(content_parts)
            cache_key_hash = hashlib.sha256(content_string.encode()).hexdigest()[:16]
            multimodal_cache_key = (
                f"multimodal:CONSTITUTIONAL_VALIDATION:{cache_key_hash}"
            )
            cache_keys.append(multimodal_cache_key)

            # 2. Multi-level cache key format (used by get_constitutional_ruling)
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            multilevel_cache_key = (
                f"multimodal_ai:{content_hash}:{self.constitutional_hash}"
            )
            cache_keys.append(multilevel_cache_key)

            logger.info(f"Generated multimodal cache key: {multimodal_cache_key}")
            logger.info(f"Generated multilevel cache key: {multilevel_cache_key}")

        return cache_keys

    async def clear_specific_constitutional_validation_entries(self):
        """Clear specific constitutional validation cache entries."""
        logger.info("🎯 Clearing specific constitutional validation cache entries...")

        try:
            # Generate specific cache keys for known test content
            cache_keys = self._generate_constitutional_validation_cache_keys()

            # Clear from multi-level cache
            for cache_key in cache_keys:
                # Clear from L1
                if hasattr(self.multi_level_cache, "l1_cache"):
                    if cache_key in self.multi_level_cache.l1_cache.cache:
                        del self.multi_level_cache.l1_cache.cache[cache_key]
                        self.cleared_counts["specific_keys"] += 1
                        logger.info(f"   Cleared L1 entry: {cache_key}")

                # Clear from L2
                if hasattr(self.multi_level_cache, "l2_cache"):
                    if cache_key in self.multi_level_cache.l2_cache.cache:
                        del self.multi_level_cache.l2_cache.cache[cache_key]
                        self.cleared_counts["specific_keys"] += 1
                        logger.info(f"   Cleared L2 entry: {cache_key}")

                # Clear from L3 Redis
                if (
                    hasattr(self.multi_level_cache, "l3_cache")
                    and self.multi_level_cache.l3_cache.redis_client
                ):
                    try:
                        # Try different Redis key patterns
                        redis_patterns = [
                            f"acgs:l3:{cache_key}",
                            cache_key,
                            f"multimodal_ai:{cache_key}",
                        ]

                        for pattern in redis_patterns:
                            keys = (
                                await self.multi_level_cache.l3_cache.redis_client.keys(
                                    pattern
                                )
                            )
                            if keys:
                                await self.multi_level_cache.l3_cache.redis_client.delete(
                                    *keys
                                )
                                self.cleared_counts["specific_keys"] += len(keys)
                                logger.info(
                                    f"   Cleared {len(keys)} Redis entries for pattern: {pattern}"
                                )
                    except Exception as e:
                        logger.warning(
                            f"   Failed to clear Redis entry {cache_key}: {e}"
                        )

            logger.info(
                f"✅ Cleared {self.cleared_counts['specific_keys']} specific cache entries"
            )

        except Exception as e:
            logger.error(f"❌ Failed to clear specific cache entries: {e}")
            raise

    async def clear_multimodal_constitutional_patterns(self):
        """Clear all multimodal constitutional validation patterns."""
        logger.info("🧹 Clearing multimodal constitutional patterns...")

        try:
            # Patterns to clear
            patterns = [
                "multimodal:CONSTITUTIONAL_VALIDATION:*",
                "multimodal:constitutional_validation:*",
                "acgs:l3:multimodal:CONSTITUTIONAL_VALIDATION:*",
                "acgs:l3:multimodal:constitutional_validation:*",
                "multimodal_ai:*:cdd01ef066bc6cf2",  # Multi-level cache pattern
                "multimodal_ai:*",  # Broader multi-level cache pattern
                f"multimodal_ai:*:{self.constitutional_hash}",  # Specific constitutional hash
            ]

            total_cleared = 0

            if (
                hasattr(self.multi_level_cache, "l3_cache")
                and self.multi_level_cache.l3_cache.redis_client
            ):
                for pattern in patterns:
                    try:
                        keys = await self.multi_level_cache.l3_cache.redis_client.keys(
                            pattern
                        )
                        if keys:
                            await self.multi_level_cache.l3_cache.redis_client.delete(
                                *keys
                            )
                            total_cleared += len(keys)
                            logger.info(
                                f"   Cleared {len(keys)} entries for pattern: {pattern}"
                            )
                    except Exception as e:
                        logger.warning(f"   Failed to clear pattern {pattern}: {e}")

            self.cleared_counts["multimodal_cache"] = total_cleared
            logger.info(
                f"✅ Cleared {total_cleared} multimodal constitutional cache entries"
            )

        except Exception as e:
            logger.error(f"❌ Failed to clear multimodal patterns: {e}")
            raise

    async def clear_all_cache_levels(self):
        """Clear all cache levels comprehensively."""
        logger.info("🧹 Clearing all cache levels...")

        try:
            # Clear L1 memory cache
            if hasattr(self.multi_level_cache, "l1_cache"):
                before_count = len(self.multi_level_cache.l1_cache.cache)
                self.multi_level_cache.l1_cache.clear()
                self.cleared_counts["l1_memory"] = before_count
                logger.info(f"   Cleared {before_count} L1 memory cache entries")

            # Clear L2 process cache
            if hasattr(self.multi_level_cache, "l2_cache"):
                before_count = len(self.multi_level_cache.l2_cache.cache)
                self.multi_level_cache.l2_cache.cache.clear()
                self.multi_level_cache.l2_cache.compiled_rules.clear()
                self.cleared_counts["l2_process"] = before_count
                logger.info(f"   Cleared {before_count} L2 process cache entries")

            # Reset Bloom filter
            if hasattr(self.multi_level_cache, "bloom_filter"):
                before_count = self.multi_level_cache.bloom_filter.items_added
                self.multi_level_cache.bloom_filter.bit_array = [
                    False
                ] * self.multi_level_cache.bloom_filter.bit_array_size
                self.multi_level_cache.bloom_filter.items_added = 0
                self.cleared_counts["bloom_filter"] = before_count
                logger.info(f"   Reset Bloom filter ({before_count} items)")

            # Reset metrics
            if hasattr(self.multi_level_cache, "metrics"):
                from services.shared.multi_level_cache import CacheMetrics

                self.multi_level_cache.metrics = CacheMetrics()

            logger.info("✅ All cache levels cleared successfully")

        except Exception as e:
            logger.error(f"❌ Failed to clear cache levels: {e}")
            raise

    async def comprehensive_cache_clear(self):
        """Perform comprehensive cache clearing."""
        logger.info("🚀 Starting comprehensive constitutional cache clearing...")
        logger.info("=" * 70)

        start_time = time.time()

        # Step 1: Clear specific constitutional validation entries
        await self.clear_specific_constitutional_validation_entries()

        # Step 2: Clear multimodal constitutional patterns
        await self.clear_multimodal_constitutional_patterns()

        # Step 3: Clear all cache levels
        await self.clear_all_cache_levels()

        total_time = time.time() - start_time
        total_cleared = sum(self.cleared_counts.values())

        logger.info("=" * 70)
        logger.info("🎉 Comprehensive cache clearing completed!")
        logger.info(f"   Total entries cleared: {total_cleared}")
        logger.info(f"   Time taken: {total_time:.2f} seconds")
        logger.info("   Breakdown:")
        for cache_type, count in self.cleared_counts.items():
            logger.info(f"     {cache_type}: {count} entries")

    async def test_constitutional_compliance(self) -> bool:
        """Test constitutional compliance after cache clearing."""
        logger.info("🔍 Testing constitutional compliance after cache clearing...")

        try:
            service = await get_multimodal_service()

            # Test the specific democratic content
            test_request = MultimodalRequest(
                request_id=f"cache_clear_test_{int(time.time())}",
                request_type=RequestType.CONSTITUTIONAL_VALIDATION,
                content_type=ContentType.TEXT_ONLY,
                text_content="Citizens have the right to participate in democratic processes and transparent governance.",
                priority="high",
            )

            response = await service.process_request(test_request)

            success = response.constitutional_compliance == True

            if success:
                logger.info("✅ Constitutional compliance test PASSED")
                logger.info(f"   Content: Citizens have the right to participate...")
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
    parser = argparse.ArgumentParser(
        description="Comprehensive constitutional cache clearing"
    )
    parser.add_argument(
        "--test", action="store_true", help="Run verification test after cache clearing"
    )
    args = parser.parse_args()

    logger.info("🏛️ Comprehensive Constitutional Cache Cleaner")
    logger.info("=" * 70)

    try:
        # Initialize cleaner
        cleaner = ComprehensiveConstitutionalCacheCleaner()
        await cleaner.initialize()

        # Perform comprehensive cache clearing
        await cleaner.comprehensive_cache_clear()

        # Run test if requested
        if args.test:
            logger.info("\n" + "=" * 70)
            success = await cleaner.test_constitutional_compliance()

            if success:
                logger.info(
                    "🎉 Cache clearing and verification completed successfully!"
                )
                return 0
            else:
                logger.error("❌ Verification failed after cache clearing")
                return 1
        else:
            logger.info("🎉 Cache clearing completed successfully!")
            logger.info("💡 Run with --test to verify constitutional compliance")
            return 0

    except Exception as e:
        logger.error(f"❌ Cache clearing failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
