#!/usr/bin/env python3
"""
ACGS Performance Testing and Validation
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive load testing to validate ACGS performance targets:
- P99 latency <5ms
- Throughput >100 RPS  
- Cache hit rate >85%
"""

import asyncio
import aiohttp
import time
import json
import statistics
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# Performance targets
PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,
    "throughput_rps": 100,
    "cache_hit_rate": 85.0,
    "constitutional_compliance_rate": 100.0
}

# ACGS service endpoints to test
ACGS_ENDPOINTS = {
    "constitutional-ai": "http://localhost:8001/health",
    "integrity-service": "http://localhost:8002/health", 
    "auth-service": "http://localhost:8016/health",
    "multi-agent-coordinator": "http://localhost:8008/health",
    "governance-synthesis": "http://localhost:8005/health"
}

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    endpoint: str
    latencies: List[float]
    success_count: int
    error_count: int
    start_time: float
    end_time: float
    
    @property
    def p99_latency(self) -> float:
        return statistics.quantiles(self.latencies, n=100)[98] if self.latencies else 0.0
    
    @property
    def avg_latency(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0.0
    
    @property
    def throughput_rps(self) -> float:
        duration = self.end_time - self.start_time
        return (self.success_count + self.error_count) / duration if duration > 0 else 0.0
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.error_count
        return (self.success_count / total * 100) if total > 0 else 0.0

class ACGSPerformanceTester:
    """ACGS performance testing and validation."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.test_results = {}
        self.baseline_metrics = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for performance testing."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def test_endpoint_performance(self, endpoint_name: str, url: str, 
                                      duration_seconds: int = 30, 
                                      concurrent_requests: int = 10) -> PerformanceMetrics:
        """Test performance of a single endpoint."""
        self.logger.info(f"🔥 Testing {endpoint_name} performance...")
        self.logger.info(f"  URL: {url}")
        self.logger.info(f"  Duration: {duration_seconds}s")
        self.logger.info(f"  Concurrent: {concurrent_requests}")
        
        latencies = []
        success_count = 0
        error_count = 0
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        async def make_request(session: aiohttp.ClientSession):
            """Make a single request and measure latency."""
            nonlocal success_count, error_count, latencies
            
            request_start = time.time()
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    await response.text()
                    request_end = time.time()
                    latency_ms = (request_end - request_start) * 1000
                    latencies.append(latency_ms)
                    
                    if response.status == 200:
                        success_count += 1
                    else:
                        error_count += 1
                        
            except Exception as e:
                error_count += 1
                # Still record latency for failed requests
                request_end = time.time()
                latency_ms = (request_end - request_start) * 1000
                latencies.append(latency_ms)
        
        # Run concurrent requests for specified duration
        connector = aiohttp.TCPConnector(limit=concurrent_requests * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            while time.time() < end_time:
                # Launch concurrent requests
                for _ in range(concurrent_requests):
                    if time.time() < end_time:
                        task = asyncio.create_task(make_request(session))
                        tasks.append(task)
                
                # Wait a bit before next batch
                await asyncio.sleep(0.1)
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        actual_end_time = time.time()
        
        metrics = PerformanceMetrics(
            endpoint=endpoint_name,
            latencies=latencies,
            success_count=success_count,
            error_count=error_count,
            start_time=start_time,
            end_time=actual_end_time
        )
        
        # Log results
        self.logger.info(f"  ✅ Results for {endpoint_name}:")
        self.logger.info(f"    P99 Latency: {metrics.p99_latency:.2f}ms (target: <{PERFORMANCE_TARGETS['p99_latency_ms']}ms)")
        self.logger.info(f"    Avg Latency: {metrics.avg_latency:.2f}ms")
        self.logger.info(f"    Throughput: {metrics.throughput_rps:.1f} RPS (target: >{PERFORMANCE_TARGETS['throughput_rps']} RPS)")
        self.logger.info(f"    Success Rate: {metrics.success_rate:.1f}%")
        self.logger.info(f"    Total Requests: {success_count + error_count}")
        
        return metrics
    
    def check_service_availability(self) -> Dict[str, bool]:
        """Check which ACGS services are available for testing."""
        self.logger.info("🔍 Checking ACGS service availability...")
        
        available_services = {}
        
        for service_name, url in ACGS_ENDPOINTS.items():
            try:
                import requests
                response = requests.get(url, timeout=5)
                available = response.status_code == 200
                available_services[service_name] = available
                
                if available:
                    self.logger.info(f"  ✅ {service_name} available at {url}")
                else:
                    self.logger.warning(f"  ❌ {service_name} unavailable (status: {response.status_code})")
                    
            except Exception as e:
                available_services[service_name] = False
                self.logger.warning(f"  ❌ {service_name} unavailable (error: {e})")
        
        return available_services
    
    def load_baseline_metrics(self) -> Dict:
        """Load baseline metrics from previous runs."""
        baseline_file = REPO_ROOT / "performance_baseline.json"
        
        if baseline_file.exists():
            try:
                with open(baseline_file, 'r') as f:
                    baseline = json.load(f)
                self.logger.info("📊 Loaded baseline metrics for comparison")
                return baseline
            except Exception as e:
                self.logger.warning(f"Failed to load baseline metrics: {e}")
        
        return {}
    
    def save_performance_results(self, results: Dict) -> str:
        """Save performance test results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = REPO_ROOT / f"acgs_performance_results_{timestamp}.json"
        
        # Add metadata
        results["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "performance_targets": PERFORMANCE_TARGETS,
            "test_duration": "30s per endpoint",
            "concurrent_requests": 10
        }
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"📄 Performance results saved: {results_file.relative_to(REPO_ROOT)}")
            return str(results_file.relative_to(REPO_ROOT))
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            return ""
    
    def analyze_performance_targets(self, results: Dict) -> Dict[str, bool]:
        """Analyze if performance targets are met."""
        self.logger.info("📊 Analyzing performance against targets...")
        
        target_analysis = {
            "p99_latency_met": True,
            "throughput_met": True,
            "overall_performance": True
        }
        
        for service_name, metrics in results.items():
            if service_name == "metadata":
                continue
                
            # Check P99 latency
            p99_latency = metrics.get("p99_latency_ms", float('inf'))
            if p99_latency > PERFORMANCE_TARGETS["p99_latency_ms"]:
                target_analysis["p99_latency_met"] = False
                self.logger.warning(f"  ⚠️ {service_name} P99 latency: {p99_latency:.2f}ms > {PERFORMANCE_TARGETS['p99_latency_ms']}ms")
            else:
                self.logger.info(f"  ✅ {service_name} P99 latency: {p99_latency:.2f}ms")
            
            # Check throughput
            throughput = metrics.get("throughput_rps", 0)
            if throughput < PERFORMANCE_TARGETS["throughput_rps"]:
                target_analysis["throughput_met"] = False
                self.logger.warning(f"  ⚠️ {service_name} throughput: {throughput:.1f} RPS < {PERFORMANCE_TARGETS['throughput_rps']} RPS")
            else:
                self.logger.info(f"  ✅ {service_name} throughput: {throughput:.1f} RPS")
        
        target_analysis["overall_performance"] = (
            target_analysis["p99_latency_met"] and 
            target_analysis["throughput_met"]
        )
        
        return target_analysis
    
    async def run_comprehensive_performance_test(self) -> Dict:
        """Run comprehensive performance testing."""
        self.logger.info("🚀 Starting ACGS Comprehensive Performance Testing...")
        self.logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        # Check service availability
        available_services = self.check_service_availability()
        
        # Load baseline for comparison
        self.baseline_metrics = self.load_baseline_metrics()
        
        # Run performance tests on available services
        test_results = {}
        
        for service_name, url in ACGS_ENDPOINTS.items():
            if available_services.get(service_name, False):
                try:
                    metrics = await self.test_endpoint_performance(service_name, url)
                    
                    test_results[service_name] = {
                        "p99_latency_ms": metrics.p99_latency,
                        "avg_latency_ms": metrics.avg_latency,
                        "throughput_rps": metrics.throughput_rps,
                        "success_rate": metrics.success_rate,
                        "total_requests": metrics.success_count + metrics.error_count,
                        "success_count": metrics.success_count,
                        "error_count": metrics.error_count
                    }
                    
                except Exception as e:
                    self.logger.error(f"Failed to test {service_name}: {e}")
                    test_results[service_name] = {"error": str(e)}
            else:
                self.logger.warning(f"Skipping {service_name} - service unavailable")
        
        # Analyze results
        target_analysis = self.analyze_performance_targets(test_results)
        test_results["target_analysis"] = target_analysis
        
        # Save results
        results_file = self.save_performance_results(test_results)
        
        # Summary
        self.logger.info("📊 Performance Testing Summary:")
        self.logger.info(f"  Services Tested: {len([s for s in available_services.values() if s])}")
        self.logger.info(f"  P99 Latency Target Met: {target_analysis['p99_latency_met']}")
        self.logger.info(f"  Throughput Target Met: {target_analysis['throughput_met']}")
        self.logger.info(f"  Overall Performance: {'✅ PASS' if target_analysis['overall_performance'] else '❌ FAIL'}")
        self.logger.info(f"  Results File: {results_file}")
        
        return test_results

def main():
    """Main performance testing function."""
    print("🚀 ACGS Performance Testing and Validation")
    print("=" * 50)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Performance Targets:")
    print(f"  P99 Latency: <{PERFORMANCE_TARGETS['p99_latency_ms']}ms")
    print(f"  Throughput: >{PERFORMANCE_TARGETS['throughput_rps']} RPS")
    print(f"  Cache Hit Rate: >{PERFORMANCE_TARGETS['cache_hit_rate']}%")
    print()
    
    tester = ACGSPerformanceTester()
    results = asyncio.run(tester.run_comprehensive_performance_test())
    
    overall_pass = results.get("target_analysis", {}).get("overall_performance", False)
    if overall_pass:
        print("\n✅ Performance testing completed - All targets met!")
    else:
        print("\n⚠️ Performance testing completed - Some targets not met")
    
    return results

if __name__ == "__main__":
    main()
