#!/usr/bin/env python3
"""
ACGS-PGP Phase 5.2: Quick Concurrent Load Testing
Efficient concurrent request validation with shorter test duration

Features:
- Quick concurrent request testing (10-20 concurrent)
- Shorter test duration for faster completion
- Essential throughput validation
- Service stability check
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime, timezone
from typing import Dict, List, Any

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuickConcurrentTester:
    """Quick ACGS-PGP Concurrent Load Tester"""
    
    def __init__(self):
        self.services = {
            "ac": {"port": 8001, "name": "Constitutional AI Service"},
            "integrity": {"port": 8002, "name": "Integrity Service"},
            "fv": {"port": 8003, "name": "Formal Verification Service"},
            "ec": {"port": 8006, "name": "Executive Council Service"}
        }
        self.base_url = "http://localhost"
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
    async def quick_concurrent_test(self, service_key: str, concurrent_level: int, 
                                  num_batches: int = 10) -> Dict[str, Any]:
        """Quick concurrent test with limited batches"""
        service = self.services[service_key]
        logger.info(f"🔥 Quick concurrent test: {service['name']} - {concurrent_level} concurrent, {num_batches} batches")
        
        response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        
        async def make_request(session: httpx.AsyncClient, request_id: int):
            nonlocal successful_requests, failed_requests, response_times
            
            request_start = time.time()
            try:
                response = await session.get(
                    f"{self.base_url}:{service['port']}/health",
                    headers={"X-Concurrent-Test": str(concurrent_level)}
                )
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)
                
                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
                    
            except Exception:
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)
                failed_requests += 1
        
        # Run concurrent batches
        async with httpx.AsyncClient(timeout=5.0) as client:
            for batch in range(num_batches):
                tasks = [make_request(client, batch * concurrent_level + i) 
                        for i in range(concurrent_level)]
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(0.1)  # Small delay between batches
        
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        rps = total_requests / total_time if total_time > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        return {
            "service": service_key,
            "service_name": service["name"],
            "concurrent_level": concurrent_level,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "requests_per_second": rps,
            "avg_response_time_ms": avg_response_time,
            "test_duration_seconds": total_time,
            "meets_concurrent_target": concurrent_level >= 10 and success_rate >= 90,
            "meets_performance_target": avg_response_time <= 100  # 100ms threshold
        }
    
    async def test_concurrent_levels(self, service_key: str) -> Dict[str, Any]:
        """Test multiple concurrent levels quickly"""
        service = self.services[service_key]
        logger.info(f"📊 Testing concurrent levels for {service['name']}")
        
        levels_to_test = [10, 15, 20]
        level_results = {}
        
        for level in levels_to_test:
            result = await self.quick_concurrent_test(service_key, level, num_batches=5)
            level_results[f"level_{level}"] = result
            
            # Stop if service fails significantly
            if result["success_rate"] < 80:
                logger.warning(f"Service degradation at {level} concurrent requests")
                break
        
        # Find max stable level
        max_stable = 0
        for level_key, result in level_results.items():
            level = int(level_key.split('_')[1])
            if result["success_rate"] >= 90:
                max_stable = level
        
        return {
            "service": service_key,
            "service_name": service["name"],
            "level_results": level_results,
            "max_stable_concurrent": max_stable,
            "passes_concurrent_test": max_stable >= 10
        }
    
    async def quick_throughput_test(self, service_key: str) -> Dict[str, Any]:
        """Quick throughput test"""
        service = self.services[service_key]
        logger.info(f"🚀 Quick throughput test for {service['name']}")
        
        # Send 100 requests as fast as possible
        num_requests = 100
        response_times = []
        successful_requests = 0
        start_time = time.time()
        
        async def throughput_request(session: httpx.AsyncClient, request_id: int):
            nonlocal successful_requests, response_times
            
            request_start = time.time()
            try:
                response = await session.get(f"{self.base_url}:{service['port']}/health")
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)
                
                if response.status_code == 200:
                    successful_requests += 1
                    
            except Exception:
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            tasks = [throughput_request(client, i) for i in range(num_requests)]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        rps = num_requests / total_time if total_time > 0 else 0
        success_rate = (successful_requests / num_requests * 100)
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        return {
            "service": service_key,
            "service_name": service["name"],
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "requests_per_second": rps,
            "avg_response_time_ms": avg_response_time,
            "test_duration_seconds": total_time,
            "meets_throughput_target": rps >= 50  # Modest 50 RPS target
        }
    
    async def run_quick_tests(self) -> Dict[str, Any]:
        """Run quick concurrent and throughput tests"""
        logger.info("🚀 Starting Quick ACGS-PGP Concurrent Load Tests...")
        
        results = {
            "test_suite": "ACGS-PGP Quick Concurrent Load Testing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "results": {}
        }
        
        for service_key in self.services.keys():
            logger.info(f"\n--- Testing {self.services[service_key]['name']} ---")
            
            service_results = {}
            
            # Test 1: Concurrent levels
            concurrent_test = await self.test_concurrent_levels(service_key)
            service_results["concurrent_levels"] = concurrent_test
            
            # Test 2: Quick throughput
            throughput_test = await self.quick_throughput_test(service_key)
            service_results["throughput"] = throughput_test
            
            results["results"][service_key] = service_results
        
        # Calculate summary
        total_tests = 0
        passed_tests = 0
        
        for service_results in results["results"].values():
            # Concurrent test
            if service_results["concurrent_levels"]["passes_concurrent_test"]:
                passed_tests += 1
            total_tests += 1
            
            # Throughput test
            if service_results["throughput"]["meets_throughput_target"]:
                passed_tests += 1
            total_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "overall_status": "passed" if success_rate >= 75 else "failed"
        }
        
        return results

async def main():
    """Main execution function"""
    tester = QuickConcurrentTester()
    
    try:
        results = await tester.run_quick_tests()
        
        # Save results
        with open("phase5_2_concurrent_load_testing_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*80)
        print("ACGS-PGP Phase 5.2: Quick Concurrent Load Testing Results")
        print("="*80)
        print(f"Overall Success Rate: {results['summary']['success_rate']:.1f}%")
        print(f"Overall Status: {results['summary']['overall_status'].upper()}")
        print(f"Constitutional Hash: {results['constitutional_hash']}")
        print("="*80)
        
        for service_key, service_results in results["results"].items():
            service_name = tester.services[service_key]["name"]
            print(f"\n{service_name}:")
            
            concurrent = service_results["concurrent_levels"]
            print(f"  Max Stable Concurrent: {concurrent['max_stable_concurrent']}")
            print(f"  Passes Concurrent Test: {'YES' if concurrent['passes_concurrent_test'] else 'NO'}")
            
            throughput = service_results["throughput"]
            print(f"  Throughput: {throughput['requests_per_second']:.1f} RPS")
            print(f"  Success Rate: {throughput['success_rate']:.1f}%")
        
        print("="*80)
        
        if results['summary']['overall_status'] == 'passed':
            print("✅ Quick concurrent load testing passed!")
            return 0
        else:
            print("❌ Some concurrent load tests failed.")
            return 1
            
    except Exception as e:
        logger.error(f"Quick concurrent testing failed: {e}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
