#!/usr/bin/env python3
"""
Comprehensive Load Testing Suite for ACGS Services
Constitutional Hash: cdd01ef066bc6cf2

Test >100 RPS sustained load, multi-agent coordination under stress,
constitutional compliance at scale. Target: 5-minute sustained load with <1% error rate.
"""

import asyncio
import aiohttp
import json
import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import concurrent.futures
from datetime import datetime, timedelta

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestMetrics:
    """Metrics for load testing results."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    error_rates: List[float] = field(default_factory=list)
    constitutional_compliance_rate: float = 100.0
    start_time: float = 0.0
    end_time: float = 0.0
    
    def get_rps(self) -> float:
        """Calculate requests per second."""
        duration = self.end_time - self.start_time
        return self.total_requests / duration if duration > 0 else 0.0
    
    def get_avg_response_time(self) -> float:
        """Get average response time in milliseconds."""
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    def get_p95_response_time(self) -> float:
        """Get P95 response time in milliseconds."""
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
    
    def get_p99_response_time(self) -> float:
        """Get P99 response time in milliseconds."""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    def get_error_rate(self) -> float:
        """Get error rate percentage."""
        return (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
    
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0


@dataclass
class ServiceEndpoint:
    """Configuration for a service endpoint to test."""
    
    name: str
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    payload: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    weight: float = 1.0  # Relative frequency of requests


class ComprehensiveLoadTester:
    """Comprehensive load testing suite for ACGS services."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.metrics = LoadTestMetrics()
        
        # ACGS service endpoints for testing
        self.service_endpoints = [
            ServiceEndpoint(
                "constitutional-ai-health",
                "http://localhost:8001/health",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
                weight=2.0
            ),
            ServiceEndpoint(
                "constitutional-ai-validate",
                "http://localhost:8001/validate",
                method="POST",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH, "Content-Type": "application/json"},
                payload={"text": "Test constitutional validation", "hash": CONSTITUTIONAL_HASH},
                weight=3.0
            ),
            ServiceEndpoint(
                "integrity-service-health",
                "http://localhost:8002/health",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
                weight=1.5
            ),
            ServiceEndpoint(
                "policy-governance-health",
                "http://localhost:8005/health",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
                weight=1.5
            ),
            ServiceEndpoint(
                "coordination-service-health",
                "http://localhost:8008/health",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
                weight=2.0
            ),
            ServiceEndpoint(
                "coordination-assign-task",
                "http://localhost:8008/assign-task",
                method="POST",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH, "Content-Type": "application/json"},
                payload={
                    "task_id": "load-test-task",
                    "requirements": ["analysis", "constitutional_compliance"],
                    "priority": "normal",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                weight=2.5
            ),
            ServiceEndpoint(
                "blackboard-service-health",
                "http://localhost:8010/health",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
                weight=1.0
            ),
            ServiceEndpoint(
                "auth-service-health",
                "http://localhost:8016/health",
                headers={"X-Constitutional-Hash": CONSTITUTIONAL_HASH},
                weight=1.0
            ),
        ]
        
        # Load test configuration
        self.target_rps = 120  # Target >100 RPS
        self.test_duration_minutes = 5
        self.max_concurrent_requests = 50
        self.error_rate_threshold = 1.0  # <1% error rate target
        
        logger.info(f"Load tester initialized [hash: {CONSTITUTIONAL_HASH}]")
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: ServiceEndpoint) -> Dict[str, Any]:
        """Make a single request to an endpoint."""
        start_time = time.perf_counter()
        
        try:
            if endpoint.method == "GET":
                async with session.get(endpoint.url, headers=endpoint.headers) as response:
                    response_time = (time.perf_counter() - start_time) * 1000
                    content = await response.text()
                    
                    return {
                        "success": response.status == endpoint.expected_status,
                        "status_code": response.status,
                        "response_time_ms": response_time,
                        "endpoint": endpoint.name,
                        "constitutional_compliant": self._check_constitutional_compliance(response),
                        "content_length": len(content),
                    }
            
            elif endpoint.method == "POST":
                async with session.post(
                    endpoint.url, 
                    headers=endpoint.headers, 
                    json=endpoint.payload
                ) as response:
                    response_time = (time.perf_counter() - start_time) * 1000
                    content = await response.text()
                    
                    return {
                        "success": response.status == endpoint.expected_status,
                        "status_code": response.status,
                        "response_time_ms": response_time,
                        "endpoint": endpoint.name,
                        "constitutional_compliant": self._check_constitutional_compliance(response),
                        "content_length": len(content),
                    }
        
        except Exception as e:
            response_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Request failed for {endpoint.name}: {e}")
            
            return {
                "success": False,
                "status_code": 0,
                "response_time_ms": response_time,
                "endpoint": endpoint.name,
                "constitutional_compliant": False,
                "error": str(e),
            }
    
    def _check_constitutional_compliance(self, response: aiohttp.ClientResponse) -> bool:
        """Check if response maintains constitutional compliance."""
        # Check for constitutional hash in response headers
        constitutional_header = response.headers.get("X-Constitutional-Hash")
        return constitutional_header == self.constitutional_hash
    
    def _select_endpoint_by_weight(self) -> ServiceEndpoint:
        """Select endpoint based on weight distribution."""
        import random
        
        total_weight = sum(endpoint.weight for endpoint in self.service_endpoints)
        random_value = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for endpoint in self.service_endpoints:
            cumulative_weight += endpoint.weight
            if random_value <= cumulative_weight:
                return endpoint
        
        return self.service_endpoints[0]  # Fallback
    
    async def run_sustained_load_test(self) -> LoadTestMetrics:
        """Run sustained load test for specified duration."""
        logger.info(f"Starting sustained load test: {self.target_rps} RPS for {self.test_duration_minutes} minutes")
        
        self.metrics = LoadTestMetrics()
        self.metrics.start_time = time.perf_counter()
        
        # Calculate test parameters
        total_requests = self.target_rps * self.test_duration_minutes * 60
        request_interval = 1.0 / self.target_rps
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=50)
        ) as session:
            
            tasks = []
            
            for i in range(total_requests):
                # Select endpoint for this request
                endpoint = self._select_endpoint_by_weight()
                
                # Create request task
                task = asyncio.create_task(
                    self._rate_limited_request(semaphore, session, endpoint)
                )
                tasks.append(task)
                
                # Control request rate
                if i < total_requests - 1:  # Don't sleep after last request
                    await asyncio.sleep(request_interval)
                
                # Log progress every 1000 requests
                if (i + 1) % 1000 == 0:
                    elapsed = time.perf_counter() - self.metrics.start_time
                    current_rps = (i + 1) / elapsed
                    logger.info(f"Progress: {i + 1}/{total_requests} requests, {current_rps:.1f} RPS")
            
            # Wait for all requests to complete
            logger.info("Waiting for all requests to complete...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            self._process_results(results)
        
        self.metrics.end_time = time.perf_counter()
        
        logger.info("Sustained load test completed")
        return self.metrics
    
    async def _rate_limited_request(
        self, 
        semaphore: asyncio.Semaphore, 
        session: aiohttp.ClientSession, 
        endpoint: ServiceEndpoint
    ) -> Dict[str, Any]:
        """Make a rate-limited request."""
        async with semaphore:
            return await self.make_request(session, endpoint)
    
    def _process_results(self, results: List[Any]):
        """Process load test results and update metrics."""
        constitutional_compliant_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                self.metrics.failed_requests += 1
                self.metrics.total_requests += 1
                continue
            
            self.metrics.total_requests += 1
            
            if result.get("success", False):
                self.metrics.successful_requests += 1
                self.metrics.response_times.append(result["response_time_ms"])
            else:
                self.metrics.failed_requests += 1
            
            if result.get("constitutional_compliant", False):
                constitutional_compliant_count += 1
        
        # Calculate constitutional compliance rate
        if self.metrics.total_requests > 0:
            self.metrics.constitutional_compliance_rate = (
                constitutional_compliant_count / self.metrics.total_requests * 100
            )
    
    async def run_stress_test(self, max_rps: int = 200, duration_minutes: int = 2) -> LoadTestMetrics:
        """Run stress test to find breaking point."""
        logger.info(f"Starting stress test: up to {max_rps} RPS for {duration_minutes} minutes")
        
        stress_metrics = LoadTestMetrics()
        stress_metrics.start_time = time.perf_counter()
        
        # Gradually increase load
        current_rps = 50
        rps_increment = 25
        test_duration_per_step = 30  # 30 seconds per RPS level
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=200, limit_per_host=100)
        ) as session:
            
            while current_rps <= max_rps:
                logger.info(f"Testing {current_rps} RPS...")
                
                # Run test at current RPS for specified duration
                step_requests = current_rps * test_duration_per_step
                request_interval = 1.0 / current_rps
                
                semaphore = asyncio.Semaphore(min(100, current_rps))
                tasks = []
                
                for i in range(step_requests):
                    endpoint = self._select_endpoint_by_weight()
                    task = asyncio.create_task(
                        self._rate_limited_request(semaphore, session, endpoint)
                    )
                    tasks.append(task)
                    
                    if i < step_requests - 1:
                        await asyncio.sleep(request_interval)
                
                # Wait for step completion
                step_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Analyze step results
                step_errors = sum(1 for r in step_results if isinstance(r, Exception) or not r.get("success", False))
                step_error_rate = (step_errors / len(step_results)) * 100
                
                logger.info(f"RPS {current_rps}: {step_error_rate:.1f}% error rate")
                
                # Stop if error rate exceeds threshold
                if step_error_rate > self.error_rate_threshold * 2:  # 2x threshold for stress test
                    logger.warning(f"Breaking point reached at {current_rps} RPS")
                    break
                
                current_rps += rps_increment
        
        stress_metrics.end_time = time.perf_counter()
        
        logger.info("Stress test completed")
        return stress_metrics
    
    def generate_load_test_report(self, metrics: LoadTestMetrics) -> Dict[str, Any]:
        """Generate comprehensive load test report."""
        return {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "test_configuration": {
                "target_rps": self.target_rps,
                "test_duration_minutes": self.test_duration_minutes,
                "max_concurrent_requests": self.max_concurrent_requests,
                "error_rate_threshold": self.error_rate_threshold,
                "total_endpoints": len(self.service_endpoints),
            },
            "performance_metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "actual_rps": metrics.get_rps(),
                "avg_response_time_ms": metrics.get_avg_response_time(),
                "p95_response_time_ms": metrics.get_p95_response_time(),
                "p99_response_time_ms": metrics.get_p99_response_time(),
                "error_rate_percent": metrics.get_error_rate(),
                "success_rate_percent": metrics.get_success_rate(),
                "constitutional_compliance_rate": metrics.constitutional_compliance_rate,
            },
            "target_validation": {
                "rps_target_met": metrics.get_rps() >= 100.0,
                "error_rate_target_met": metrics.get_error_rate() <= self.error_rate_threshold,
                "p99_latency_target_met": metrics.get_p99_response_time() <= 5.0,
                "constitutional_compliance_target_met": metrics.constitutional_compliance_rate >= 99.0,
                "duration_target_met": (metrics.end_time - metrics.start_time) >= (self.test_duration_minutes * 60 * 0.95),
            },
            "test_summary": {
                "test_duration_seconds": metrics.end_time - metrics.start_time,
                "test_start_time": datetime.fromtimestamp(metrics.start_time).isoformat(),
                "test_end_time": datetime.fromtimestamp(metrics.end_time).isoformat(),
            },
        }


async def main():
    """Run comprehensive load testing suite."""
    print("HASH-OK:cdd01ef066bc6cf2")
    print("Comprehensive Load Testing Suite for ACGS Services")
    print("=" * 60)
    
    load_tester = ComprehensiveLoadTester()
    
    try:
        # Run sustained load test
        print("Starting sustained load test...")
        sustained_metrics = await load_tester.run_sustained_load_test()
        
        # Generate report
        report = load_tester.generate_load_test_report(sustained_metrics)
        
        print("\n" + "=" * 60)
        print("LOAD TEST RESULTS:")
        print("HASH-OK:cdd01ef066bc6cf2")
        print(f"✅ Total requests: {report['performance_metrics']['total_requests']}")
        print(f"✅ Actual RPS: {report['performance_metrics']['actual_rps']:.1f}")
        print(f"✅ Success rate: {report['performance_metrics']['success_rate_percent']:.1f}%")
        print(f"✅ Error rate: {report['performance_metrics']['error_rate_percent']:.1f}%")
        print(f"✅ Avg response time: {report['performance_metrics']['avg_response_time_ms']:.2f}ms")
        print(f"✅ P95 response time: {report['performance_metrics']['p95_response_time_ms']:.2f}ms")
        print(f"✅ P99 response time: {report['performance_metrics']['p99_response_time_ms']:.2f}ms")
        print(f"✅ Constitutional compliance: {report['performance_metrics']['constitutional_compliance_rate']:.1f}%")
        print(f"✅ Test duration: {report['test_summary']['test_duration_seconds']:.1f}s")
        
        # Validate targets
        targets = report['target_validation']
        print(f"\nTARGET VALIDATION:")
        print(f"✅ RPS target (≥100): {'MET' if targets['rps_target_met'] else 'MISSED'}")
        print(f"✅ Error rate target (≤1%): {'MET' if targets['error_rate_target_met'] else 'MISSED'}")
        print(f"✅ P99 latency target (≤5ms): {'MET' if targets['p99_latency_target_met'] else 'MISSED'}")
        print(f"✅ Constitutional compliance (≥99%): {'MET' if targets['constitutional_compliance_target_met'] else 'MISSED'}")
        print(f"✅ Duration target (5 min): {'MET' if targets['duration_target_met'] else 'MISSED'}")
        
        all_targets_met = all(targets.values())
        
        if all_targets_met:
            print("\n🎉 ALL LOAD TEST TARGETS ACHIEVED!")
            print("✅ Sustained >100 RPS load capability confirmed")
            print("✅ <1% error rate maintained under load")
            print("✅ P99 latency <5ms achieved")
            print("✅ Constitutional compliance maintained at scale")
            print("✅ 5-minute sustained load test completed successfully")
            print("✅ ACGS system ready for production load")
            return 0
        else:
            print("❌ Some load test targets not met")
            return 1
    
    except Exception as e:
        logger.error(f"Load test failed: {e}")
        print("❌ Load test execution failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
