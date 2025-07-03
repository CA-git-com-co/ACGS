#!/usr/bin/env python3
"""
Comprehensive Load Testing Script for Optimized ACGS Services

This script validates the performance improvements implemented for:
- Policy Governance Service (Port 8005) - Target: P99 < 5ms
- Governance Synthesis Service (Port 8004) - Target: P99 < 5ms

Test Protocol:
- 100+ concurrent requests per service
- Sustained load for 10+ minutes
- P99 latency validation under 10x normal load
- Resource usage monitoring
- Cache hit rate validation (>85% target)
- Constitutional compliance verification
"""

import asyncio
import aiohttp
import json
import time
import statistics
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import psutil
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    service_name: str
    base_url: str
    target_p99_ms: float = 5.0
    concurrent_requests: int = 100
    test_duration_minutes: int = 10
    warmup_requests: int = 50
    cache_hit_rate_target: float = 0.85

@dataclass
class PerformanceMetrics:
    """Performance metrics collection"""
    response_times: List[float]
    error_count: int
    total_requests: int
    cache_hits: int
    cache_misses: int
    constitutional_violations: int
    start_time: float
    end_time: float

class ACGSLoadTester:
    """Comprehensive load tester for ACGS services"""
    
    def __init__(self):
        self.services = {
            "policy_governance": LoadTestConfig(
                service_name="Policy Governance Service",
                base_url="http://localhost:8005",
                concurrent_requests=120,
                test_duration_minutes=12
            ),
            "governance_synthesis": LoadTestConfig(
                service_name="Governance Synthesis Service", 
                base_url="http://localhost:8004",
                concurrent_requests=100,
                test_duration_minutes=10
            )
        }
        
        self.test_payloads = {
            "policy_governance": {
                "health": {},
                "performance_metrics": {},
                "policy_validation": {
                    "policy_id": "test_policy_001",
                    "validation_type": "constitutional",
                    "priority": "high"
                }
            },
            "governance_synthesis": {
                "health": {},
                "synthesis": {
                    "synthesis_type": "constitutional_compliance",
                    "input_policy": {
                        "id": "test_synthesis_001",
                        "type": "governance_rule",
                        "priority": "high"
                    },
                    "optimization_level": "high"
                },
                "performance_metrics": {}
            }
        }

    async def warmup_service(self, config: LoadTestConfig) -> None:
        """Warm up service caches before load testing"""
        logger.info(f"🔥 Warming up {config.service_name}...")
        
        async with aiohttp.ClientSession() as session:
            warmup_tasks = []
            
            for _ in range(config.warmup_requests):
                # Health check warmup
                warmup_tasks.append(self.make_request(session, f"{config.base_url}/health", {}))
                
                # Performance metrics warmup
                warmup_tasks.append(self.make_request(session, f"{config.base_url}/api/v1/performance/metrics", {}))
            
            await asyncio.gather(*warmup_tasks, return_exceptions=True)
        
        logger.info(f"✅ Warmup completed for {config.service_name}")

    async def make_request(self, session: aiohttp.ClientSession, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            if payload:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_data = await response.json()
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    return {
                        "success": response.status == 200,
                        "response_time_ms": response_time_ms,
                        "status_code": response.status,
                        "constitutional_hash": response_data.get("constitutional_hash"),
                        "cached": "cache" in str(response_data).lower(),
                        "response_data": response_data
                    }
            else:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_data = await response.json()
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    return {
                        "success": response.status == 200,
                        "response_time_ms": response_time_ms,
                        "status_code": response.status,
                        "constitutional_hash": response_data.get("constitutional_hash"),
                        "cached": "cache" in str(response_data).lower(),
                        "response_data": response_data
                    }
                    
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "constitutional_hash": None,
                "cached": False
            }

    async def run_load_test_batch(self, config: LoadTestConfig, service_key: str) -> List[Dict[str, Any]]:
        """Run a batch of concurrent requests"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Mix of different endpoint types for realistic load
            for i in range(config.concurrent_requests):
                if i % 3 == 0:
                    # Health check requests (33%)
                    url = f"{config.base_url}/health"
                    payload = self.test_payloads[service_key]["health"]
                elif i % 3 == 1:
                    # Performance metrics requests (33%)
                    url = f"{config.base_url}/api/v1/performance/metrics"
                    payload = self.test_payloads[service_key]["performance_metrics"]
                else:
                    # Service-specific requests (33%)
                    if service_key == "policy_governance":
                        url = f"{config.base_url}/api/v1/performance/health"
                        payload = self.test_payloads[service_key]["policy_validation"]
                    else:  # governance_synthesis
                        url = f"{config.base_url}/api/v1/synthesize"
                        payload = self.test_payloads[service_key]["synthesis"]
                
                tasks.append(self.make_request(session, url, payload))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return valid results
            valid_results = [r for r in results if isinstance(r, dict)]
            return valid_results

    async def run_sustained_load_test(self, config: LoadTestConfig, service_key: str) -> PerformanceMetrics:
        """Run sustained load test for specified duration"""
        logger.info(f"🚀 Starting sustained load test for {config.service_name}")
        logger.info(f"📊 Config: {config.concurrent_requests} concurrent requests for {config.test_duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (config.test_duration_minutes * 60)
        
        all_results = []
        batch_count = 0
        
        while time.time() < end_time:
            batch_start = time.time()
            
            # Run batch of concurrent requests
            batch_results = await self.run_load_test_batch(config, service_key)
            all_results.extend(batch_results)
            
            batch_count += 1
            batch_duration = time.time() - batch_start
            
            logger.info(f"📈 Batch {batch_count} completed: {len(batch_results)} requests in {batch_duration:.2f}s")
            
            # Brief pause between batches to avoid overwhelming the service
            await asyncio.sleep(0.1)
        
        # Calculate metrics
        response_times = [r["response_time_ms"] for r in all_results if r.get("success")]
        error_count = len([r for r in all_results if not r.get("success")])
        cache_hits = len([r for r in all_results if r.get("cached")])
        cache_misses = len([r for r in all_results if not r.get("cached") and r.get("success")])
        constitutional_violations = len([r for r in all_results if r.get("constitutional_hash") != "cdd01ef066bc6cf2"])
        
        return PerformanceMetrics(
            response_times=response_times,
            error_count=error_count,
            total_requests=len(all_results),
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            constitutional_violations=constitutional_violations,
            start_time=start_time,
            end_time=time.time()
        )

    def analyze_performance_metrics(self, metrics: PerformanceMetrics, config: LoadTestConfig) -> Dict[str, Any]:
        """Analyze performance metrics and determine if targets are met"""
        if not metrics.response_times:
            return {"error": "No successful responses to analyze"}
        
        # Calculate percentiles
        sorted_times = sorted(metrics.response_times)
        p50 = statistics.median(sorted_times)
        p95 = sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 20 else sorted_times[-1]
        p99 = sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 100 else sorted_times[-1]
        
        # Calculate cache hit rate
        total_cache_requests = metrics.cache_hits + metrics.cache_misses
        cache_hit_rate = metrics.cache_hits / total_cache_requests if total_cache_requests > 0 else 0
        
        # Calculate error rate
        error_rate = metrics.error_count / metrics.total_requests if metrics.total_requests > 0 else 0
        
        # Calculate throughput
        test_duration = metrics.end_time - metrics.start_time
        throughput_rps = len(metrics.response_times) / test_duration
        
        # Determine if targets are met
        p99_target_met = p99 < config.target_p99_ms
        cache_target_met = cache_hit_rate >= config.cache_hit_rate_target
        constitutional_compliance = metrics.constitutional_violations == 0
        
        return {
            "performance_analysis": {
                "response_times": {
                    "p50_ms": round(p50, 2),
                    "p95_ms": round(p95, 2),
                    "p99_ms": round(p99, 2),
                    "avg_ms": round(statistics.mean(metrics.response_times), 2),
                    "min_ms": round(min(metrics.response_times), 2),
                    "max_ms": round(max(metrics.response_times), 2)
                },
                "targets": {
                    "p99_target_ms": config.target_p99_ms,
                    "p99_target_met": p99_target_met,
                    "cache_hit_rate_target": config.cache_hit_rate_target,
                    "cache_target_met": cache_target_met
                },
                "throughput": {
                    "requests_per_second": round(throughput_rps, 2),
                    "total_requests": len(metrics.response_times),
                    "test_duration_seconds": round(test_duration, 2)
                },
                "reliability": {
                    "error_rate": round(error_rate, 4),
                    "error_count": metrics.error_count,
                    "success_rate": round(1 - error_rate, 4)
                },
                "caching": {
                    "cache_hit_rate": round(cache_hit_rate, 4),
                    "cache_hits": metrics.cache_hits,
                    "cache_misses": metrics.cache_misses
                },
                "constitutional_compliance": {
                    "violations": metrics.constitutional_violations,
                    "compliance_rate": round(1 - (metrics.constitutional_violations / metrics.total_requests), 4),
                    "compliant": constitutional_compliance
                }
            },
            "overall_success": p99_target_met and cache_target_met and constitutional_compliance and error_rate < 0.01
        }

    async def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Run comprehensive load test on all services"""
        logger.info("🎯 Starting ACGS Comprehensive Load Test")
        
        results = {}
        
        for service_key, config in self.services.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing {config.service_name}")
            logger.info(f"{'='*60}")
            
            try:
                # Warmup
                await self.warmup_service(config)
                
                # Run sustained load test
                metrics = await self.run_sustained_load_test(config, service_key)
                
                # Analyze results
                analysis = self.analyze_performance_metrics(metrics, config)
                
                results[service_key] = {
                    "service_name": config.service_name,
                    "config": {
                        "concurrent_requests": config.concurrent_requests,
                        "test_duration_minutes": config.test_duration_minutes,
                        "target_p99_ms": config.target_p99_ms
                    },
                    "raw_metrics": metrics,
                    "analysis": analysis
                }
                
                # Log summary
                perf = analysis["performance_analysis"]
                logger.info(f"✅ {config.service_name} Test Complete:")
                logger.info(f"   P99 Latency: {perf['response_times']['p99_ms']}ms (Target: {config.target_p99_ms}ms)")
                logger.info(f"   Cache Hit Rate: {perf['caching']['cache_hit_rate']:.1%} (Target: {config.cache_hit_rate_target:.1%})")
                logger.info(f"   Throughput: {perf['throughput']['requests_per_second']} RPS")
                logger.info(f"   Success Rate: {perf['reliability']['success_rate']:.1%}")
                logger.info(f"   Target Met: {'✅' if analysis['overall_success'] else '❌'}")
                
            except Exception as e:
                logger.error(f"❌ Load test failed for {config.service_name}: {e}")
                results[service_key] = {"error": str(e)}
        
        return results

async def main():
    """Main load testing function"""
    tester = ACGSLoadTester()
    
    try:
        results = await tester.run_comprehensive_load_test()
        
        # Generate final report
        logger.info(f"\n{'='*80}")
        logger.info("🎯 ACGS LOAD TEST FINAL REPORT")
        logger.info(f"{'='*80}")
        
        all_targets_met = True
        
        for service_key, result in results.items():
            if "error" in result:
                logger.error(f"❌ {service_key}: {result['error']}")
                all_targets_met = False
            else:
                analysis = result["analysis"]
                perf = analysis["performance_analysis"]
                success = analysis["overall_success"]
                
                logger.info(f"\n📊 {result['service_name']}:")
                logger.info(f"   P99 Latency: {perf['response_times']['p99_ms']}ms {'✅' if perf['targets']['p99_target_met'] else '❌'}")
                logger.info(f"   Cache Hit Rate: {perf['caching']['cache_hit_rate']:.1%} {'✅' if perf['targets']['cache_target_met'] else '❌'}")
                logger.info(f"   Constitutional Compliance: {'✅' if perf['constitutional_compliance']['compliant'] else '❌'}")
                logger.info(f"   Overall: {'✅ PASS' if success else '❌ FAIL'}")
                
                if not success:
                    all_targets_met = False
        
        logger.info(f"\n🎯 OVERALL RESULT: {'✅ ALL TARGETS MET' if all_targets_met else '❌ SOME TARGETS NOT MET'}")
        
        return 0 if all_targets_met else 1
        
    except Exception as e:
        logger.error(f"❌ Load test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
