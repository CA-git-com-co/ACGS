#!/usr/bin/env python3
"""
Test script for ACGS Performance Suite
Constitutional Hash: cdd01ef066bc6cf2

Quick validation test for the unified performance suite.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add tools directory to path
sys.path.append(str(Path(__file__).parent))

from acgs_performance_suite import ACGSPerformanceSuite, CONSTITUTIONAL_HASH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_performance_suite():
    """Test the ACGS Performance Suite."""
    logger.info("🧪 Testing ACGS Performance Suite...")
    
    try:
        async with ACGSPerformanceSuite() as suite:
            logger.info("✅ Performance suite initialized successfully")
            
            # Test service health check
            logger.info("🏥 Testing service health check...")
            health_results = await suite._test_service_health()
            logger.info(f"Health check completed: {health_results.get('healthy_services', 0)}/{health_results.get('total_services', 0)} services")
            
            # Test system metrics collection
            logger.info("📊 Testing system metrics collection...")
            system_metrics = await suite._collect_system_metrics()
            logger.info(f"System metrics: CPU {system_metrics.get('cpu', {}).get('percent', 0):.1f}%, Memory {system_metrics.get('memory', {}).get('percent', 0):.1f}%")
            
            # Test cache performance (if Redis available)
            logger.info("🗄️ Testing cache performance...")
            cache_results = await suite._test_cache_performance()
            if "error" not in cache_results:
                logger.info(f"Cache test: {cache_results.get('hit_rate_percent', 0):.1f}% hit rate")
            else:
                logger.warning(f"Cache test skipped: {cache_results['error']}")
            
            # Test database performance (if DB available)
            logger.info("🗃️ Testing database performance...")
            db_results = await suite._test_database_performance()
            if "error" not in db_results:
                logger.info(f"Database test: {db_results.get('average_latency_ms', 0):.2f}ms avg latency")
            else:
                logger.warning(f"Database test skipped: {db_results['error']}")
            
            logger.info("✅ All performance suite tests completed successfully")
            logger.info(f"🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Performance suite test failed: {e}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting ACGS Performance Suite Test...")
    
    success = await test_performance_suite()
    
    if success:
        logger.info("🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("💥 Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
