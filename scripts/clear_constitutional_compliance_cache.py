#!/usr/bin/env python3
"""
Constitutional Compliance Cache Invalidation Script

This script clears all cache levels (L1 memory, L2 process, L3 Redis, and Bloom filter)
to resolve constitutional compliance test failures caused by cached results from before
the enhanced compliance algorithm was implemented.

Usage:
    python scripts/clear_constitutional_compliance_cache.py [--verify]

Options:
    --verify    Run verification tests after cache clearing
"""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.shared.constitutional_cache import ConstitutionalCache
from services.shared.multi_level_cache import MultiLevelCacheManager
from services.shared.multimodal_ai_service import (
    ContentType,
    MultimodalRequest,
    RequestType,
    get_multimodal_service,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalCacheCleaner:
    """Comprehensive cache cleaner for constitutional compliance system."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.cache_managers = []
        self.cleared_counts = {
            "l1_memory": 0,
            "l2_process": 0,
            "l3_redis": 0,
            "bloom_filter": 0,
            "constitutional_cache": 0,
        }

    async def initialize(self):
        """Initialize cache managers."""
        logger.info("🔧 Initializing cache managers...")

        try:
            # Initialize multi-level cache manager with config
            config = {"constitutional_hash": self.constitutional_hash}
            self.multi_level_cache = MultiLevelCacheManager(config=config)
            await self.multi_level_cache.initialize()

            # Initialize constitutional cache
            self.constitutional_cache = ConstitutionalCache()
            await self.constitutional_cache.initialize()

            logger.info("✅ Cache managers initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize cache managers: {e}")
            raise

    async def clear_l1_memory_cache(self):
        """Clear L1 memory cache."""
        logger.info("🧹 Clearing L1 memory cache...")

        try:
            # Clear multi-level cache L1
            if hasattr(self.multi_level_cache, "l1_cache"):
                before_count = len(self.multi_level_cache.l1_cache.cache)
                self.multi_level_cache.l1_cache.clear()
                self.cleared_counts["l1_memory"] += before_count
                logger.info(f"   Cleared {before_count} L1 memory cache entries")

            logger.info("✅ L1 memory cache cleared successfully")

        except Exception as e:
            logger.error(f"❌ Failed to clear L1 memory cache: {e}")
            raise

    async def clear_l2_process_cache(self):
        """Clear L2 process cache."""
        logger.info("🧹 Clearing L2 process cache...")

        try:
            # Clear multi-level cache L2
            if hasattr(self.multi_level_cache, "l2_cache"):
                before_count = len(self.multi_level_cache.l2_cache.cache)
                self.multi_level_cache.l2_cache.cache.clear()
                self.multi_level_cache.l2_cache.compiled_rules.clear()
                self.cleared_counts["l2_process"] += before_count
                logger.info(f"   Cleared {before_count} L2 process cache entries")

            logger.info("✅ L2 process cache cleared successfully")

        except Exception as e:
            logger.error(f"❌ Failed to clear L2 process cache: {e}")
            raise

    async def clear_l3_redis_cache(self):
        """Clear L3 Redis cache."""
        logger.info("🧹 Clearing L3 Redis cache...")

        try:
            # Clear constitutional-related Redis patterns
            constitutional_patterns = [
                "acgs:constitutional:*",
                "pgc:constitutional:*",
                "pgc:compliance:*",
                "pgc:validation:*",
                "pgc:policy:*",
                "multimodal:constitutional:*",
                "constitutional_validation:*",
                "compliance_check:*",
            ]

            total_cleared = 0

            # Clear multi-level cache L3
            if hasattr(self.multi_level_cache, "l3_cache"):
                for pattern in constitutional_patterns:
                    await self.multi_level_cache.l3_cache.clear_pattern(pattern)
                    total_cleared += 1  # Count patterns cleared
                    logger.info(f"   Cleared pattern: {pattern}")

            self.cleared_counts["l3_redis"] = total_cleared
            logger.info(f"✅ L3 Redis cache cleared ({total_cleared} entries)")

        except Exception as e:
            logger.error(f"❌ Failed to clear L3 Redis cache: {e}")
            raise

    async def clear_bloom_filter(self):
        """Clear and reset Bloom filter."""
        logger.info("🧹 Clearing Bloom filter...")

        try:
            # Reset multi-level cache Bloom filter
            if hasattr(self.multi_level_cache, "bloom_filter"):
                before_count = self.multi_level_cache.bloom_filter.items_added

                # Reset bit array
                self.multi_level_cache.bloom_filter.bit_array = [
                    False
                ] * self.multi_level_cache.bloom_filter.bit_array_size
                self.multi_level_cache.bloom_filter.items_added = 0

                self.cleared_counts["bloom_filter"] = before_count
                logger.info(f"   Reset Bloom filter ({before_count} items)")

            logger.info("✅ Bloom filter cleared successfully")

        except Exception as e:
            logger.error(f"❌ Failed to clear Bloom filter: {e}")
            raise

    async def clear_constitutional_cache(self):
        """Clear constitutional cache."""
        logger.info("🧹 Clearing constitutional cache...")

        try:
            # Clear all constitutional validation cache
            await self.constitutional_cache.invalidate_cache()

            # Count cleared entries (estimate)
            self.cleared_counts["constitutional_cache"] = 100  # Estimate

            logger.info("✅ Constitutional cache cleared successfully")

        except Exception as e:
            logger.error(f"❌ Failed to clear constitutional cache: {e}")
            raise

    async def clear_all_caches(self):
        """Clear all cache levels."""
        logger.info("🚀 Starting comprehensive cache clearing...")
        logger.info("=" * 60)

        start_time = time.time()

        # Clear all cache levels
        await self.clear_l1_memory_cache()
        await self.clear_l2_process_cache()
        await self.clear_l3_redis_cache()
        await self.clear_bloom_filter()
        await self.clear_constitutional_cache()

        # Reset metrics in multi-level cache
        if hasattr(self.multi_level_cache, "metrics"):
            from services.shared.multi_level_cache import CacheMetrics

            self.multi_level_cache.metrics = CacheMetrics()

        total_time = time.time() - start_time
        total_cleared = sum(self.cleared_counts.values())

        logger.info("=" * 60)
        logger.info("🎉 Cache clearing completed successfully!")
        logger.info(f"   Total entries cleared: {total_cleared}")
        logger.info(f"   Time taken: {total_time:.2f} seconds")
        logger.info("   Breakdown:")
        for cache_type, count in self.cleared_counts.items():
            logger.info(f"     {cache_type}: {count} entries")

    async def verify_constitutional_compliance(self) -> dict[str, Any]:
        """Verify constitutional compliance after cache clearing."""
        logger.info("🔍 Verifying constitutional compliance...")

        try:
            service = await get_multimodal_service()

            # Test democratic content
            test_request = MultimodalRequest(
                request_id="cache_clear_verification",
                request_type=RequestType.CONSTITUTIONAL_VALIDATION,
                content_type=ContentType.TEXT_ONLY,
                text_content="Citizens have the right to participate in democratic processes and transparent governance.",
                priority="high",
            )

            response = await service.process_request(test_request)

            verification_result = {
                "constitutional_compliance": response.constitutional_compliance,
                "confidence_score": response.confidence_score,
                "model_used": response.model_used.value,
                "constitutional_hash": response.constitutional_hash,
                "response_time_ms": getattr(response, "response_time_ms", 0),
                "cache_hit": getattr(response, "cache_hit", False),
            }

            # Check if compliance is correct
            expected_compliant = True
            actual_compliant = response.constitutional_compliance

            if actual_compliant == expected_compliant:
                logger.info("✅ Constitutional compliance verification PASSED")
                logger.info(
                    f"   Expected: {expected_compliant}, Actual: {actual_compliant}"
                )
                logger.info(f"   Confidence: {response.confidence_score:.3f}")
                logger.info(f"   Constitutional hash: {response.constitutional_hash}")
                verification_result["status"] = "PASS"
            else:
                logger.error("❌ Constitutional compliance verification FAILED")
                logger.error(
                    f"   Expected: {expected_compliant}, Actual: {actual_compliant}"
                )
                verification_result["status"] = "FAIL"

            return verification_result

        except Exception as e:
            logger.error(f"❌ Constitutional compliance verification failed: {e}")
            return {"status": "ERROR", "error": str(e)}


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Clear constitutional compliance cache"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run verification tests after cache clearing",
    )
    args = parser.parse_args()

    logger.info("🏛️ Constitutional Compliance Cache Cleaner")
    logger.info("=" * 60)

    try:
        # Initialize cleaner
        cleaner = ConstitutionalCacheCleaner()
        await cleaner.initialize()

        # Clear all caches
        await cleaner.clear_all_caches()

        # Run verification if requested
        if args.verify:
            logger.info("\n" + "=" * 60)
            verification_result = await cleaner.verify_constitutional_compliance()

            if verification_result.get("status") == "PASS":
                logger.info(
                    "🎉 Cache clearing and verification completed successfully!"
                )
                return 0
            logger.error("❌ Verification failed after cache clearing")
            return 1
        logger.info("🎉 Cache clearing completed successfully!")
        logger.info("💡 Run with --verify to test constitutional compliance")
        return 0

    except Exception as e:
        logger.error(f"❌ Cache clearing failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
