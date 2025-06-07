#!/usr/bin/env python3
"""
Post-merge validation script for httpx upgrade (PR #102)
Validates HTTP client functionality across all services
"""

import asyncio
import httpx
import logging
import sys
import time
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HttpxValidationSuite:
    """Comprehensive validation suite for httpx upgrade"""
    
    def __init__(self):
        self.services = {
            "auth": "http://localhost:8001",
            "ac": "http://localhost:8002", 
            "gs": "http://localhost:8003",
            "fv": "http://localhost:8004",
            "integrity": "http://localhost:8005",
            "pgc": "http://localhost:8006"
        }
        self.results = {}
        
    async def validate_basic_connectivity(self) -> Dict[str, bool]:
        """Test basic HTTP connectivity with new httpx version"""
        logger.info("🔍 Testing basic HTTP connectivity...")
        
        results = {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, base_url in self.services.items():
                try:
                    response = await client.get(f"{base_url}/health")
                    results[service_name] = {
                        "status": "success",
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds() if response.elapsed else 0
                    }
                    logger.info(f"✅ {service_name}: {response.status_code}")
                except Exception as e:
                    results[service_name] = {
                        "status": "error", 
                        "error": str(e)
                    }
                    logger.error(f"❌ {service_name}: {e}")
                    
        return results
    
    async def validate_ssl_configuration(self) -> Dict[str, Any]:
        """Validate SSL/TLS configuration works correctly"""
        logger.info("🔒 Testing SSL/TLS configuration...")
        
        ssl_tests = {}
        
        # Test HTTPS endpoints (if available)
        https_endpoints = [
            "https://httpbin.org/get",
            "https://api.github.com/zen"
        ]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in https_endpoints:
                try:
                    response = await client.get(endpoint)
                    ssl_tests[endpoint] = {
                        "status": "success",
                        "status_code": response.status_code,
                        "tls_version": getattr(response, 'tls_version', 'unknown')
                    }
                    logger.info(f"✅ SSL test {endpoint}: {response.status_code}")
                except Exception as e:
                    ssl_tests[endpoint] = {
                        "status": "error",
                        "error": str(e)
                    }
                    logger.error(f"❌ SSL test {endpoint}: {e}")
                    
        return ssl_tests
    
    async def validate_timeout_handling(self) -> Dict[str, Any]:
        """Test timeout configuration and handling"""
        logger.info("⏱️ Testing timeout handling...")
        
        timeout_tests = {}
        
        # Test various timeout configurations
        timeout_configs = [
            httpx.Timeout(5.0),
            httpx.Timeout(10.0, connect=5.0),
            httpx.Timeout(30.0, read=10.0, write=5.0, connect=5.0)
        ]
        
        for i, timeout_config in enumerate(timeout_configs):
            try:
                async with httpx.AsyncClient(timeout=timeout_config) as client:
                    response = await client.get("https://httpbin.org/delay/1")
                    timeout_tests[f"timeout_config_{i}"] = {
                        "status": "success",
                        "status_code": response.status_code
                    }
                    logger.info(f"✅ Timeout config {i}: {response.status_code}")
            except Exception as e:
                timeout_tests[f"timeout_config_{i}"] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"❌ Timeout config {i}: {e}")
                
        return timeout_tests
    
    async def validate_connection_pooling(self) -> Dict[str, Any]:
        """Test connection pooling and limits"""
        logger.info("🔗 Testing connection pooling...")
        
        pool_tests = {}
        
        # Test connection limits
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        
        try:
            async with httpx.AsyncClient(limits=limits) as client:
                # Make multiple concurrent requests
                tasks = []
                for i in range(10):
                    task = client.get("https://httpbin.org/get")
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful_requests = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
                
                pool_tests["concurrent_requests"] = {
                    "status": "success",
                    "successful_requests": successful_requests,
                    "total_requests": len(tasks)
                }
                logger.info(f"✅ Connection pooling: {successful_requests}/{len(tasks)} successful")
                
        except Exception as e:
            pool_tests["concurrent_requests"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"❌ Connection pooling: {e}")
            
        return pool_tests
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        logger.info("🚀 Starting httpx upgrade validation...")
        
        start_time = time.time()
        
        validation_results = {
            "timestamp": time.time(),
            "httpx_version": httpx.__version__,
            "tests": {}
        }
        
        # Run all validation tests
        validation_results["tests"]["connectivity"] = await self.validate_basic_connectivity()
        validation_results["tests"]["ssl_configuration"] = await self.validate_ssl_configuration()
        validation_results["tests"]["timeout_handling"] = await self.validate_timeout_handling()
        validation_results["tests"]["connection_pooling"] = await self.validate_connection_pooling()
        
        validation_results["execution_time"] = time.time() - start_time
        
        # Calculate overall success rate
        total_tests = 0
        successful_tests = 0
        
        for test_category, test_results in validation_results["tests"].items():
            if isinstance(test_results, dict):
                for test_name, test_result in test_results.items():
                    total_tests += 1
                    if isinstance(test_result, dict) and test_result.get("status") == "success":
                        successful_tests += 1
        
        validation_results["success_rate"] = successful_tests / total_tests if total_tests > 0 else 0
        validation_results["overall_status"] = "PASS" if validation_results["success_rate"] >= 0.8 else "FAIL"
        
        logger.info(f"🎯 Validation complete: {validation_results['success_rate']:.1%} success rate")
        logger.info(f"📊 Overall status: {validation_results['overall_status']}")
        
        return validation_results

async def main():
    """Main validation execution"""
    validator = HttpxValidationSuite()
    results = await validator.run_full_validation()
    
    # Print summary
    print("\n" + "="*60)
    print("HTTPX UPGRADE VALIDATION SUMMARY")
    print("="*60)
    print(f"httpx Version: {results['httpx_version']}")
    print(f"Success Rate: {results['success_rate']:.1%}")
    print(f"Overall Status: {results['overall_status']}")
    print(f"Execution Time: {results['execution_time']:.2f}s")
    print("="*60)
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_status'] == 'PASS' else 1)

if __name__ == "__main__":
    asyncio.run(main())
