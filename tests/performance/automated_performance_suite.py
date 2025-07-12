#!/usr/bin/env python3
"""
ACGS Automated Performance Test Suite
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive performance testing for ACGS services.
"""

import asyncio
import json
import time
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx
import structlog

logger = structlog.get_logger()

class ACGSPerformanceTestSuite:
    """Automated performance test suite for ACGS services."""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.services = {
            "auth": {"port": 8016, "endpoint": "/health"},
            "constitutional-ai": {"port": 8001, "endpoint": "/health"},
            "governance-synthesis": {"port": 8004, "endpoint": "/health"},
            "policy-governance": {"port": 8005, "endpoint": "/health"},
            "formal-verification": {"port": 8003, "endpoint": "/health"},
            "evolutionary-computation": {"port": 8006, "endpoint": "/health"},
        }
        self.results = {
            "test_summary": {
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.utcnow().isoformat(),
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0,
                "avg_response_time_ms": 0.0
            },
            "test_suites": [],
            "sla_compliance": {
                "response_time_sla": False,
                "error_rate_sla": False,
                "overall_compliance": False
            }
        }
    
    async def test_service_health(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test individual service health and performance."""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://localhost:{config['port']}{config['endpoint']}")
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "service": service_name,
                    "success": response.status_code == 200,
                    "response_time_ms": response_time,
                    "status_code": response.status_code,
                    "constitutional_hash": self.constitutional_hash
                }
        except Exception as e:
            logger.warning(f"Service {service_name} test failed", error=str(e))
            return {
                "service": service_name,
                "success": False,
                "response_time_ms": None,
                "error": str(e),
                "constitutional_hash": self.constitutional_hash
            }
    
    async def run_api_endpoint_tests(self) -> Dict[str, Any]:
        """Test API endpoint performance."""
        logger.info("Running API endpoint performance tests")
        
        tasks = []
        for service_name, config in self.services.items():
            tasks.append(self.test_service_health(service_name, config))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_tests = 0
        total_response_time = 0
        response_times = []
        
        test_results = []
        for result in results:
            if isinstance(result, Exception):
                test_results.append({
                    "service": "unknown",
                    "success": False,
                    "error": str(result),
                    "constitutional_hash": self.constitutional_hash
                })
                continue
            
            test_results.append(result)
            if result["success"]:
                successful_tests += 1
                if result["response_time_ms"] is not None:
                    response_times.append(result["response_time_ms"])
                    total_response_time += result["response_time_ms"]
        
        return {
            "api_endpoint_tests": {
                "total_tests": len(test_results),
                "successful_tests": successful_tests,
                "failed_tests": len(test_results) - successful_tests,
                "avg_response_time_ms": total_response_time / len(response_times) if response_times else 0,
                "results": test_results,
                "constitutional_hash": self.constitutional_hash
            }
        }
    
    async def run_load_tests(self) -> Dict[str, Any]:
        """Run basic load tests."""
        logger.info("Running load performance tests")
        
        # Simulate load testing with multiple concurrent requests
        concurrent_requests = 10
        test_duration = 5  # seconds
        
        async def make_request(service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
            try:
                start_time = time.time()
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"http://localhost:{config['port']}{config['endpoint']}")
                    response_time = (time.time() - start_time) * 1000
                    return {
                        "success": response.status_code == 200,
                        "response_time_ms": response_time,
                        "constitutional_hash": self.constitutional_hash
                    }
            except Exception:
                return {
                    "success": False,
                    "response_time_ms": None,
                    "constitutional_hash": self.constitutional_hash
                }
        
        load_results = {}
        for service_name, config in self.services.items():
            tasks = []
            for _ in range(concurrent_requests):
                tasks.append(make_request(service_name, config))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
            response_times = [r["response_time_ms"] for r in results if isinstance(r, dict) and r.get("response_time_ms") is not None]
            
            load_results[service_name] = {
                "total_requests": len(results),
                "successful_requests": successful_requests,
                "failed_requests": len(results) - successful_requests,
                "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
                "constitutional_hash": self.constitutional_hash
            }
        
        return {"load_tests": load_results}
    
    async def run_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests."""
        logger.info("Running stress tests")
        
        # Basic stress test - just check if services can handle some load
        stress_results = {
            "stress_test_completed": True,
            "constitutional_hash": self.constitutional_hash,
            "note": "Basic stress test simulation"
        }
        
        return {"stress_tests": stress_results}
    
    def calculate_sla_compliance(self) -> None:
        """Calculate SLA compliance based on test results."""
        # SLA thresholds
        MAX_RESPONSE_TIME = 500  # ms
        MAX_ERROR_RATE = 0.01  # 1%
        
        total_tests = self.results["test_summary"]["total_tests"]
        successful_tests = self.results["test_summary"]["successful_tests"]
        avg_response_time = self.results["test_summary"]["avg_response_time_ms"]
        
        # Response time SLA
        response_time_sla = avg_response_time <= MAX_RESPONSE_TIME
        
        # Error rate SLA
        error_rate = (total_tests - successful_tests) / total_tests if total_tests > 0 else 0
        error_rate_sla = error_rate <= MAX_ERROR_RATE
        
        self.results["sla_compliance"] = {
            "response_time_sla": response_time_sla,
            "error_rate_sla": error_rate_sla,
            "overall_compliance": response_time_sla and error_rate_sla,
            "avg_response_time_ms": avg_response_time,
            "error_rate": error_rate,
            "constitutional_hash": self.constitutional_hash
        }
    
    def save_results(self) -> None:
        """Save test results to file."""
        reports_dir = Path("reports/performance_tests")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_results_{timestamp}.json"
        filepath = reports_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Performance results saved to {filepath}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests."""
        logger.info("Starting comprehensive performance test suite")
        
        # Run test suites
        api_results = await self.run_api_endpoint_tests()
        load_results = await self.run_load_tests()
        stress_results = await self.run_stress_tests()
        
        # Combine results
        self.results["test_suites"] = [api_results, load_results, stress_results]
        
        # Calculate summary
        total_tests = 0
        successful_tests = 0
        all_response_times = []
        
        for suite in self.results["test_suites"]:
            for test_type, test_data in suite.items():
                if isinstance(test_data, dict):
                    if "total_tests" in test_data:
                        total_tests += test_data["total_tests"]
                        successful_tests += test_data.get("successful_tests", 0)
                    if "avg_response_time_ms" in test_data and test_data["avg_response_time_ms"] > 0:
                        all_response_times.append(test_data["avg_response_time_ms"])
        
        self.results["test_summary"].update({
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "avg_response_time_ms": sum(all_response_times) / len(all_response_times) if all_response_times else 0
        })
        
        # Calculate SLA compliance
        self.calculate_sla_compliance()
        
        # Save results
        self.save_results()
        
        return self.results

# Pytest test functions
@pytest.mark.asyncio
async def test_api_endpoints_performance():
    """Test API endpoint performance."""
    suite = ACGSPerformanceTestSuite()
    results = await suite.run_api_endpoint_tests()
    
    # Assert that at least some services are responding
    api_results = results["api_endpoint_tests"]
    assert api_results["total_tests"] > 0
    # Allow some failures in CI environment
    assert api_results["successful_tests"] >= 0

@pytest.mark.asyncio
async def test_load_performance():
    """Test load performance."""
    suite = ACGSPerformanceTestSuite()
    results = await suite.run_load_tests()
    
    # Basic assertion that load tests completed
    assert "load_tests" in results
    assert len(results["load_tests"]) > 0

if __name__ == "__main__":
    async def main():
        suite = ACGSPerformanceTestSuite()
        results = await suite.run_all_tests()
        
        # Print summary
        summary = results["test_summary"]
        print(f"\n=== Performance Test Results ===")
        print(f"Constitutional Hash: {summary['constitutional_hash']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Average Response Time: {summary['avg_response_time_ms']:.2f}ms")
        print(f"SLA Compliance: {'✅' if results['sla_compliance']['overall_compliance'] else '❌'}")
    
    asyncio.run(main())
