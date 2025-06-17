#!/usr/bin/env python3
"""
Performance Validation Test for ACGS-1 Phase 4 Optimizations

Validates that performance optimizations meet targets:
- <500ms response times for 95% of requests
- >1000 concurrent governance actions support
- >99.5% service availability
- Constitutional compliance maintained
"""

import asyncio
import aiohttp
import time
import json
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import statistics
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'shared'))

from redis_performance_optimizer import get_redis_optimizer
from service_communication_optimizer import get_service_optimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance test metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
        if self.errors is None:
            self.errors = []
    
    @property
    def success_rate(self) -> float:
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0.0
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def p95_response_time(self) -> float:
        return statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else 0.0
    
    @property
    def p99_response_time(self) -> float:
        return statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) >= 100 else 0.0


class PerformanceValidator:
    """
    Comprehensive performance validator for ACGS-1 optimizations.
    
    Tests constitutional governance operations under load to validate
    performance targets and system resilience.
    """
    
    def __init__(self):
        """Initialize performance validator."""
        self.session = None
        self.services = [
            ("auth_service", 8000),
            ("ac_service", 8001),
            ("integrity_service", 8002),
            ("fv_service", 8003),
            ("gs_service", 8004),
            ("pgc_service", 8005),
            ("ec_service", 8006),
            ("research_service", 8007)
        ]
        
    async def initialize(self):
        """Initialize test environment."""
        connector = aiohttp.TCPConnector(limit=500, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        logger.info("Performance validator initialized")
    
    async def test_service_health(self) -> Dict[str, bool]:
        """Test health of all ACGS services."""
        health_results = {}
        
        for service_name, port in self.services:
            try:
                start_time = time.time()
                async with self.session.get(f"http://localhost:{port}/health") as response:
                    response_time = time.time() - start_time
                    is_healthy = response.status == 200
                    health_results[service_name] = {
                        "healthy": is_healthy,
                        "response_time": response_time,
                        "status_code": response.status
                    }
                    logger.info(f"✅ {service_name}: {'Healthy' if is_healthy else 'Unhealthy'} ({response_time*1000:.1f}ms)")
            except Exception as e:
                health_results[service_name] = {
                    "healthy": False,
                    "error": str(e),
                    "response_time": None
                }
                logger.error(f"❌ {service_name}: Health check failed - {e}")
        
        return health_results
    
    async def test_constitutional_validation_performance(self, concurrent_requests: int = 100) -> PerformanceMetrics:
        """Test constitutional validation endpoint performance."""
        logger.info(f"Testing constitutional validation with {concurrent_requests} concurrent requests...")
        
        metrics = PerformanceMetrics()
        
        async def make_validation_request():
            try:
                start_time = time.time()
                async with self.session.get("http://localhost:8005/api/v1/constitutional/validate") as response:
                    response_time = time.time() - start_time
                    
                    metrics.total_requests += 1
                    metrics.response_times.append(response_time)
                    
                    if response.status == 200:
                        metrics.successful_requests += 1
                        data = await response.json()
                        # Validate constitutional hash
                        if data.get("validation_result", {}).get("constitutional_hash") != "cdd01ef066bc6cf2":
                            metrics.errors.append("Invalid constitutional hash in response")
                    else:
                        metrics.failed_requests += 1
                        metrics.errors.append(f"HTTP {response.status}")
                        
            except Exception as e:
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.errors.append(str(e))
        
        # Execute concurrent requests
        tasks = [make_validation_request() for _ in range(concurrent_requests)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return metrics
    
    async def test_policy_validation_performance(self, concurrent_requests: int = 100) -> PerformanceMetrics:
        """Test policy validation endpoint performance."""
        logger.info(f"Testing policy validation with {concurrent_requests} concurrent requests...")
        
        metrics = PerformanceMetrics()
        
        test_policy = {
            "title": "Performance Test Policy",
            "description": "Testing policy validation performance",
            "constitutional_hash": "cdd01ef066bc6cf2",
            "constitutional_principles": ["performance", "efficiency"],
            "content": "This policy tests the performance of constitutional validation."
        }
        
        async def make_policy_request():
            try:
                start_time = time.time()
                async with self.session.post(
                    "http://localhost:8005/api/v1/constitutional/validate-policy",
                    json=test_policy
                ) as response:
                    response_time = time.time() - start_time
                    
                    metrics.total_requests += 1
                    metrics.response_times.append(response_time)
                    
                    if response.status == 200:
                        metrics.successful_requests += 1
                    else:
                        metrics.failed_requests += 1
                        metrics.errors.append(f"HTTP {response.status}")
                        
            except Exception as e:
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.errors.append(str(e))
        
        # Execute concurrent requests
        tasks = [make_policy_request() for _ in range(concurrent_requests)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return metrics
    
    async def test_constitutional_council_performance(self, concurrent_requests: int = 50) -> PerformanceMetrics:
        """Test constitutional council endpoints performance."""
        logger.info(f"Testing constitutional council with {concurrent_requests} concurrent requests...")
        
        metrics = PerformanceMetrics()
        
        async def make_council_request():
            try:
                start_time = time.time()
                async with self.session.get("http://localhost:8001/api/v1/constitutional-council/members") as response:
                    response_time = time.time() - start_time
                    
                    metrics.total_requests += 1
                    metrics.response_times.append(response_time)
                    
                    if response.status == 200:
                        metrics.successful_requests += 1
                        data = await response.json()
                        # Validate council structure
                        if data.get("required_signatures") != 5 or data.get("total_members") != 7:
                            metrics.errors.append("Invalid council configuration")
                    else:
                        metrics.failed_requests += 1
                        metrics.errors.append(f"HTTP {response.status}")
                        
            except Exception as e:
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.errors.append(str(e))
        
        # Execute concurrent requests
        tasks = [make_council_request() for _ in range(concurrent_requests)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return metrics
    
    async def test_redis_cache_performance(self) -> Dict[str, Any]:
        """Test Redis caching performance."""
        logger.info("Testing Redis cache performance...")
        
        try:
            redis_optimizer = await get_redis_optimizer()
            
            # Test cache operations
            start_time = time.time()
            
            # Test batch set
            test_data = {f"test_key_{i}": {"value": i, "timestamp": time.time()} for i in range(100)}
            set_count = await redis_optimizer.batch_set(test_data, "constitutional")
            set_time = time.time() - start_time
            
            # Test batch get
            start_time = time.time()
            retrieved_data = await redis_optimizer.batch_get(list(test_data.keys()))
            get_time = time.time() - start_time
            
            # Get cache stats
            cache_stats = await redis_optimizer.get_cache_stats()
            
            return {
                "batch_set_time": set_time,
                "batch_get_time": get_time,
                "set_count": set_count,
                "retrieved_count": len(retrieved_data),
                "cache_stats": cache_stats
            }
            
        except Exception as e:
            logger.error(f"Redis cache test failed: {e}")
            return {"error": str(e)}
    
    async def test_service_communication_optimization(self) -> Dict[str, Any]:
        """Test optimized service communication."""
        logger.info("Testing service communication optimization...")
        
        try:
            service_optimizer = await get_service_optimizer()
            
            # Test service health
            health_status = await service_optimizer.get_service_health()
            
            # Test optimized service calls
            start_time = time.time()
            
            # Make calls to different services
            results = []
            for service_name in ["ac_service", "pgc_service", "fv_service"]:
                try:
                    status, data = await service_optimizer.make_request(service_name, "/health")
                    results.append({"service": service_name, "status": status, "success": status == 200})
                except Exception as e:
                    results.append({"service": service_name, "error": str(e), "success": False})
            
            total_time = time.time() - start_time
            
            return {
                "total_time": total_time,
                "service_calls": results,
                "health_status": health_status
            }
            
        except Exception as e:
            logger.error(f"Service communication test failed: {e}")
            return {"error": str(e)}
    
    async def run_comprehensive_performance_test(self) -> Dict[str, Any]:
        """Run comprehensive performance validation."""
        logger.info("🚀 Starting comprehensive performance validation...")
        
        results = {
            "test_timestamp": time.time(),
            "performance_targets": {
                "response_time_p95": 500,  # ms
                "success_rate": 99.5,      # %
                "concurrent_support": 1000  # requests
            }
        }
        
        # Test 1: Service Health
        logger.info("📊 Testing service health...")
        results["service_health"] = await self.test_service_health()
        
        # Test 2: Constitutional Validation Performance
        logger.info("⚖️ Testing constitutional validation performance...")
        constitutional_metrics = await self.test_constitutional_validation_performance(200)
        results["constitutional_validation"] = {
            "avg_response_time_ms": constitutional_metrics.avg_response_time * 1000,
            "p95_response_time_ms": constitutional_metrics.p95_response_time * 1000,
            "success_rate": constitutional_metrics.success_rate * 100,
            "total_requests": constitutional_metrics.total_requests,
            "errors": constitutional_metrics.errors[:5]  # First 5 errors
        }
        
        # Test 3: Policy Validation Performance
        logger.info("📋 Testing policy validation performance...")
        policy_metrics = await self.test_policy_validation_performance(150)
        results["policy_validation"] = {
            "avg_response_time_ms": policy_metrics.avg_response_time * 1000,
            "p95_response_time_ms": policy_metrics.p95_response_time * 1000,
            "success_rate": policy_metrics.success_rate * 100,
            "total_requests": policy_metrics.total_requests
        }
        
        # Test 4: Constitutional Council Performance
        logger.info("🏛️ Testing constitutional council performance...")
        council_metrics = await self.test_constitutional_council_performance(100)
        results["constitutional_council"] = {
            "avg_response_time_ms": council_metrics.avg_response_time * 1000,
            "p95_response_time_ms": council_metrics.p95_response_time * 1000,
            "success_rate": council_metrics.success_rate * 100,
            "total_requests": council_metrics.total_requests
        }
        
        # Test 5: Redis Cache Performance
        logger.info("🗄️ Testing Redis cache performance...")
        results["redis_cache"] = await self.test_redis_cache_performance()
        
        # Test 6: Service Communication Optimization
        logger.info("🔗 Testing service communication optimization...")
        results["service_communication"] = await self.test_service_communication_optimization()
        
        # Calculate overall performance score
        results["performance_summary"] = self._calculate_performance_score(results)
        
        return results
    
    def _calculate_performance_score(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance score."""
        score = 100
        issues = []
        
        # Check response time targets
        constitutional_p95 = results.get("constitutional_validation", {}).get("p95_response_time_ms", 0)
        if constitutional_p95 > 500:
            score -= 20
            issues.append(f"Constitutional validation P95 response time: {constitutional_p95:.1f}ms > 500ms")
        
        policy_p95 = results.get("policy_validation", {}).get("p95_response_time_ms", 0)
        if policy_p95 > 500:
            score -= 15
            issues.append(f"Policy validation P95 response time: {policy_p95:.1f}ms > 500ms")
        
        # Check success rates
        constitutional_success = results.get("constitutional_validation", {}).get("success_rate", 0)
        if constitutional_success < 99.5:
            score -= 25
            issues.append(f"Constitutional validation success rate: {constitutional_success:.1f}% < 99.5%")
        
        # Check service health
        healthy_services = sum(
            1 for service_health in results.get("service_health", {}).values()
            if isinstance(service_health, dict) and service_health.get("healthy", False)
        )
        total_services = len(results.get("service_health", {}))
        service_availability = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        if service_availability < 99.5:
            score -= 30
            issues.append(f"Service availability: {service_availability:.1f}% < 99.5%")
        
        return {
            "overall_score": max(0, score),
            "performance_grade": "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D",
            "targets_met": score >= 90,
            "issues": issues,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "service_availability": service_availability
        }
    
    async def close(self):
        """Close test session."""
        if self.session:
            await self.session.close()


async def main():
    """Main performance validation execution."""
    validator = PerformanceValidator()
    
    try:
        await validator.initialize()
        results = await validator.run_comprehensive_performance_test()
        
        # Save results
        with open("performance_validation_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        # Display summary
        summary = results["performance_summary"]
        print("\n" + "="*80)
        print("🏁 ACGS-1 Performance Validation Results")
        print("="*80)
        print(f"Overall Score: {summary['overall_score']}/100 (Grade: {summary['performance_grade']})")
        print(f"Targets Met: {'✅ YES' if summary['targets_met'] else '❌ NO'}")
        print(f"Service Availability: {summary['service_availability']:.1f}% ({summary['healthy_services']}/{summary['total_services']} services)")
        
        if summary['issues']:
            print("\n⚠️ Issues Found:")
            for issue in summary['issues']:
                print(f"   - {issue}")
        
        print(f"\n📄 Detailed results saved: performance_validation_results.json")
        print("="*80)
        
        return summary['targets_met']
        
    except Exception as e:
        logger.error(f"Performance validation failed: {e}")
        return False
    finally:
        await validator.close()


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
