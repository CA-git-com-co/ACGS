#!/usr/bin/env python3
"""
Test script for ACGS-1 Self-Evolving AI Architecture Foundation Service.

This script performs comprehensive testing of the self-evolving AI service,
including API endpoints, core components, and integration functionality.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SelfEvolvingAITester:
    """Comprehensive tester for the Self-Evolving AI service."""
    
    def __init__(self, base_url: str = "http://localhost:8007"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None
        self.test_results: Dict[str, Any] = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def run_test(self, test_name: str, test_func):
        """Run a single test and record results."""
        logger.info(f"Running test: {test_name}")
        self.test_results["total_tests"] += 1
        
        try:
            start_time = time.time()
            result = await test_func()
            duration = time.time() - start_time
            
            if result.get("success", False):
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ {test_name} - PASSED ({duration:.2f}s)")
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {test_name} - FAILED ({duration:.2f}s): {result.get('error', 'Unknown error')}")
            
            self.test_results["test_details"].append({
                "test_name": test_name,
                "success": result.get("success", False),
                "duration": duration,
                "details": result,
            })
            
        except Exception as e:
            self.test_results["failed_tests"] += 1
            logger.error(f"❌ {test_name} - FAILED: {str(e)}")
            self.test_results["test_details"].append({
                "test_name": test_name,
                "success": False,
                "duration": 0,
                "error": str(e),
            })
    
    async def test_service_health(self) -> Dict[str, Any]:
        """Test service health endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "health_data": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Health check failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_root_endpoint(self) -> Dict[str, Any]:
        """Test root endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "service_info": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Root endpoint failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_evolution_health(self) -> Dict[str, Any]:
        """Test evolution engine health."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/evolution/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "evolution_health": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Evolution health check failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_security_health(self) -> Dict[str, Any]:
        """Test security manager health."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/security/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "security_health": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Security health check failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_observability_health(self) -> Dict[str, Any]:
        """Test observability framework health."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/observability/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "observability_health": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Observability health check failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_evolution_metrics(self) -> Dict[str, Any]:
        """Test evolution metrics endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/evolution/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "metrics": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Evolution metrics failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_security_status(self) -> Dict[str, Any]:
        """Test security status endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/security/status") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "security_status": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Security status failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_observability_status(self) -> Dict[str, Any]:
        """Test observability status endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/observability/status") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "observability_status": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Observability status failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_record_metric(self) -> Dict[str, Any]:
        """Test recording a metric."""
        try:
            metric_data = {
                "metric_name": "test_metric",
                "value": 42.0,
                "metric_type": "gauge",
                "unit": "count",
                "labels": {"test": "true"}
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/observability/metrics/record",
                json=metric_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "metric_response": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Record metric failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_start_span(self) -> Dict[str, Any]:
        """Test starting a trace span."""
        try:
            span_data = {
                "operation_name": "test_operation",
                "tags": {"test": "true", "component": "test_suite"}
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/observability/tracing/start-span",
                json=span_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "span_response": data,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Start span failed with status {response.status}",
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_all_tests(self):
        """Run all tests."""
        logger.info("🚀 Starting ACGS-1 Self-Evolving AI Service Tests")
        logger.info(f"Testing service at: {self.base_url}")
        
        # Core service tests
        await self.run_test("Service Health Check", self.test_service_health)
        await self.run_test("Root Endpoint", self.test_root_endpoint)
        
        # Component health tests
        await self.run_test("Evolution Engine Health", self.test_evolution_health)
        await self.run_test("Security Manager Health", self.test_security_health)
        await self.run_test("Observability Framework Health", self.test_observability_health)
        
        # Metrics and status tests
        await self.run_test("Evolution Metrics", self.test_evolution_metrics)
        await self.run_test("Security Status", self.test_security_status)
        await self.run_test("Observability Status", self.test_observability_status)
        
        # Functional tests
        await self.run_test("Record Metric", self.test_record_metric)
        await self.run_test("Start Trace Span", self.test_start_span)
        
        # Print results
        self.print_test_results()
    
    def print_test_results(self):
        """Print comprehensive test results."""
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info("=" * 60)
        logger.info("🧪 TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            logger.info("\n❌ FAILED TESTS:")
            for test in self.test_results["test_details"]:
                if not test["success"]:
                    logger.info(f"  - {test['test_name']}: {test.get('error', 'Unknown error')}")
        
        logger.info("=" * 60)
        
        if success_rate >= 80:
            logger.info("🎉 Service is functioning well!")
        elif success_rate >= 60:
            logger.info("⚠️  Service has some issues but is partially functional")
        else:
            logger.info("🚨 Service has significant issues")
        
        return success_rate >= 80


async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ACGS-1 Self-Evolving AI Service")
    parser.add_argument(
        "--url", 
        default="http://localhost:8007",
        help="Base URL of the service (default: http://localhost:8007)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async with SelfEvolvingAITester(args.url) as tester:
        success = await tester.run_all_tests()
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(tester.test_results, f, indent=2)
        
        logger.info("📄 Detailed results saved to test_results.json")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
