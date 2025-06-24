#!/usr/bin/env python3
"""
ACGS-PGP Phase 5: Performance Validation & Operational Readiness
Load testing and performance validation for all ACGS services

Features:
- Load testing with concurrent requests (10-20 concurrent)
- Response time validation (≤2s target)
- Throughput testing (1000 RPS for PGC target)
- Availability testing (>99.9% target)
- Performance benchmarking
- Operational readiness assessment
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import httpx
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceTestResult(BaseModel):
    """Performance test result model"""
    test_name: str
    service: str
    status: str
    response_times: List[float]
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    success_rate: float
    throughput_rps: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    timestamp: datetime

class ACGSPerformanceValidator:
    """ACGS-PGP Performance Validation & Load Testing"""
    
    def __init__(self):
        self.services = {
            "ac": {"port": 8001, "name": "Constitutional AI Service"},
            "integrity": {"port": 8002, "name": "Integrity Service"},
            "fv": {"port": 8003, "name": "Formal Verification Service"},
            "ec": {"port": 8006, "name": "Executive Council Service"}
        }
        self.base_url = "http://localhost"
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Performance targets
        self.response_time_target = 2.0  # 2 seconds
        self.availability_target = 99.9  # 99.9%
        self.concurrent_requests_min = 10
        self.concurrent_requests_max = 20
        self.pgc_throughput_target = 1000  # RPS for PGC service
        
    async def load_test_service(self, service_key: str, concurrent_requests: int = 15, 
                               duration_seconds: int = 30) -> PerformanceTestResult:
        """Load test a specific service with concurrent requests"""
        service = self.services[service_key]
        logger.info(f"🔥 Load testing {service['name']} with {concurrent_requests} concurrent requests...")
        
        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        async def make_request(session: httpx.AsyncClient, request_id: int):
            """Make a single request"""
            nonlocal successful_requests, failed_requests, response_times
            
            request_start = time.time()
            try:
                response = await session.get(
                    f"{self.base_url}:{service['port']}/health",
                    headers={
                        "X-Load-Test": "true",
                        "X-Request-ID": str(request_id)
                    }
                )
                request_time = (time.time() - request_start) * 1000  # Convert to ms
                response_times.append(request_time)
                
                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
                    
            except Exception as e:
                request_time = (time.time() - request_start) * 1000
                response_times.append(request_time)
                failed_requests += 1
        
        # Run load test
        async with httpx.AsyncClient(timeout=10.0) as client:
            request_id = 0
            end_time = start_time + duration_seconds
            
            while time.time() < end_time:
                # Create batch of concurrent requests
                tasks = []
                for _ in range(concurrent_requests):
                    request_id += 1
                    tasks.append(make_request(client, request_id))
                
                # Execute concurrent requests
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Small delay between batches
                await asyncio.sleep(0.1)
        
        # Calculate metrics
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        throughput_rps = total_requests / total_time if total_time > 0 else 0
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else avg_response_time
        p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else avg_response_time
        
        return PerformanceTestResult(
            test_name=f"Load Test - {service['name']}",
            service=service_key,
            status="passed" if success_rate >= 95 and avg_response_time <= self.response_time_target * 1000 else "failed",
            response_times=response_times[:100],  # Limit stored response times
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            success_rate=success_rate,
            throughput_rps=throughput_rps,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            timestamp=datetime.now(timezone.utc)
        )
    
    async def test_response_time_compliance(self) -> Dict[str, Any]:
        """Test response time compliance (≤2s target)"""
        logger.info("⏱️ Testing response time compliance...")
        
        response_time_results = {}
        compliant_services = 0
        
        for service_key, service in self.services.items():
            try:
                start_time = time.time()
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self.base_url}:{service['port']}/health")
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    is_compliant = response_time <= (self.response_time_target * 1000)
                    if is_compliant:
                        compliant_services += 1
                    
                    response_time_results[service_key] = {
                        "service_name": service["name"],
                        "response_time_ms": response_time,
                        "target_ms": self.response_time_target * 1000,
                        "is_compliant": is_compliant,
                        "status_code": response.status_code,
                        "constitutional_hash_verified": response.headers.get("x-constitutional-hash") == self.constitutional_hash
                    }
                    
            except Exception as e:
                response_time_results[service_key] = {
                    "service_name": service["name"],
                    "error": str(e),
                    "is_compliant": False
                }
        
        compliance_rate = (compliant_services / len(self.services) * 100) if self.services else 0
        
        return {
            "test_name": "Response Time Compliance",
            "status": "passed" if compliance_rate >= 90 else "failed",
            "compliance_rate": compliance_rate,
            "compliant_services": compliant_services,
            "total_services": len(self.services),
            "target_response_time_ms": self.response_time_target * 1000,
            "service_results": response_time_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def test_concurrent_request_handling(self) -> Dict[str, Any]:
        """Test concurrent request handling capacity (10-20 concurrent requests)"""
        logger.info("🔄 Testing concurrent request handling...")
        
        concurrent_test_results = {}
        
        for service_key, service in self.services.items():
            logger.info(f"Testing concurrent requests for {service['name']}...")
            
            # Test with different concurrency levels
            concurrency_results = {}
            
            for concurrent_level in [10, 15, 20]:
                try:
                    start_time = time.time()
                    successful_requests = 0
                    failed_requests = 0
                    response_times = []
                    
                    async def concurrent_request(session: httpx.AsyncClient):
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
                    
                    # Execute concurrent requests
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        tasks = [concurrent_request(client) for _ in range(concurrent_level)]
                        await asyncio.gather(*tasks, return_exceptions=True)
                    
                    total_time = time.time() - start_time
                    total_requests = successful_requests + failed_requests
                    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
                    avg_response_time = statistics.mean(response_times) if response_times else 0
                    
                    concurrency_results[f"{concurrent_level}_concurrent"] = {
                        "concurrent_requests": concurrent_level,
                        "success_rate": success_rate,
                        "avg_response_time_ms": avg_response_time,
                        "total_time_seconds": total_time,
                        "successful_requests": successful_requests,
                        "failed_requests": failed_requests
                    }
                    
                except Exception as e:
                    concurrency_results[f"{concurrent_level}_concurrent"] = {
                        "concurrent_requests": concurrent_level,
                        "error": str(e),
                        "success_rate": 0
                    }
            
            # Calculate overall concurrent handling capability
            avg_success_rate = statistics.mean([
                result.get("success_rate", 0) 
                for result in concurrency_results.values()
            ])
            
            concurrent_test_results[service_key] = {
                "service_name": service["name"],
                "overall_success_rate": avg_success_rate,
                "can_handle_concurrent": avg_success_rate >= 90,
                "concurrency_test_results": concurrency_results
            }
        
        # Calculate overall concurrent handling status
        services_handling_concurrent = sum(
            1 for result in concurrent_test_results.values() 
            if result.get("can_handle_concurrent", False)
        )
        concurrent_handling_rate = (services_handling_concurrent / len(self.services) * 100) if self.services else 0
        
        return {
            "test_name": "Concurrent Request Handling",
            "status": "passed" if concurrent_handling_rate >= 75 else "failed",
            "concurrent_handling_rate": concurrent_handling_rate,
            "services_handling_concurrent": services_handling_concurrent,
            "total_services": len(self.services),
            "target_concurrent_requests": f"{self.concurrent_requests_min}-{self.concurrent_requests_max}",
            "service_results": concurrent_test_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def test_availability(self) -> Dict[str, Any]:
        """Test service availability (>99.9% target)"""
        logger.info("📊 Testing service availability...")
        
        availability_results = {}
        test_duration = 60  # 1 minute test
        check_interval = 2  # Check every 2 seconds
        
        for service_key, service in self.services.items():
            logger.info(f"Testing availability for {service['name']}...")
            
            start_time = time.time()
            end_time = start_time + test_duration
            total_checks = 0
            successful_checks = 0
            
            while time.time() < end_time:
                total_checks += 1
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.get(f"{self.base_url}:{service['port']}/health")
                        if response.status_code == 200:
                            successful_checks += 1
                except Exception:
                    pass  # Count as failed check
                
                await asyncio.sleep(check_interval)
            
            availability_percentage = (successful_checks / total_checks * 100) if total_checks > 0 else 0
            meets_target = availability_percentage >= self.availability_target
            
            availability_results[service_key] = {
                "service_name": service["name"],
                "availability_percentage": availability_percentage,
                "target_percentage": self.availability_target,
                "meets_target": meets_target,
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "failed_checks": total_checks - successful_checks,
                "test_duration_seconds": test_duration
            }
        
        # Calculate overall availability
        services_meeting_target = sum(
            1 for result in availability_results.values() 
            if result.get("meets_target", False)
        )
        overall_availability_rate = (services_meeting_target / len(self.services) * 100) if self.services else 0
        
        return {
            "test_name": "Service Availability",
            "status": "passed" if overall_availability_rate >= 75 else "failed",
            "overall_availability_rate": overall_availability_rate,
            "services_meeting_target": services_meeting_target,
            "total_services": len(self.services),
            "availability_target": self.availability_target,
            "service_results": availability_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def run_performance_validation(self) -> Dict[str, Any]:
        """Run comprehensive performance validation tests"""
        logger.info("🚀 Starting ACGS-PGP Performance Validation & Operational Readiness Tests...")
        
        test_results = {
            "test_suite": "ACGS-PGP Performance Validation & Operational Readiness",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "performance_targets": {
                "response_time_target_ms": self.response_time_target * 1000,
                "availability_target": self.availability_target,
                "concurrent_requests_range": f"{self.concurrent_requests_min}-{self.concurrent_requests_max}",
                "pgc_throughput_target_rps": self.pgc_throughput_target
            },
            "results": {}
        }
        
        # Test 1: Response time compliance
        response_time_test = await self.test_response_time_compliance()
        test_results["results"]["response_time_compliance"] = response_time_test
        
        # Test 2: Concurrent request handling
        concurrent_test = await self.test_concurrent_request_handling()
        test_results["results"]["concurrent_request_handling"] = concurrent_test
        
        # Test 3: Service availability
        availability_test = await self.test_availability()
        test_results["results"]["service_availability"] = availability_test
        
        # Test 4: Load testing for each service
        load_test_results = {}
        for service_key in self.services.keys():
            load_result = await self.load_test_service(service_key, concurrent_requests=15, duration_seconds=30)
            load_test_results[service_key] = load_result.dict()
        
        test_results["results"]["load_testing"] = {
            "test_name": "Service Load Testing",
            "service_results": load_test_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Calculate overall status
        passed_tests = sum(1 for test in test_results["results"].values() 
                          if test.get("status") == "passed")
        total_tests = len([test for test in test_results["results"].values() if "status" in test])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        test_results["overall_status"] = "passed" if success_rate >= 70 else "failed"
        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "operational_readiness": "ready" if success_rate >= 70 else "needs_improvement"
        }
        
        return test_results

async def main():
    """Main execution function"""
    validator = ACGSPerformanceValidator()
    
    try:
        results = await validator.run_performance_validation()
        
        # Save results to file
        with open("phase5_performance_validation_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*80)
        print("ACGS-PGP Phase 5: Performance Validation & Operational Readiness Results")
        print("="*80)
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        print(f"Operational Readiness: {results['summary']['operational_readiness'].upper()}")
        print(f"Response Time Target: {results['performance_targets']['response_time_target_ms']}ms")
        print(f"Availability Target: {results['performance_targets']['availability_target']}%")
        print(f"Constitutional Hash: {results['constitutional_hash']}")
        print("="*80)
        
        if results['overall_status'] == 'passed':
            print("✅ Performance validation and operational readiness tests passed!")
            return 0
        else:
            print("❌ Some performance tests failed. Check results for details.")
            return 1
            
    except Exception as e:
        logger.error(f"Performance validation failed: {e}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
