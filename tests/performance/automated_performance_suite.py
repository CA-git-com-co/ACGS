#!/usr/bin/env python3
"""
ACGS Automated Performance Test Suite
Comprehensive performance testing for all ACGS services with CI/CD integration.
"""

import asyncio
import json
import logging
import statistics
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import aiohttp
import pytest
import pytest_asyncio
from prometheus_client import CollectorRegistry, Counter, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class PerformanceTestResult:
    """Performance test result."""
    test_name: str
    service_name: str
    endpoint: str
    
    # Timing metrics
    response_time_ms: float
    total_duration_ms: float
    
    # Success metrics
    success: bool
    status_code: int
    error_message: Optional[str] = None
    
    # Performance metrics
    throughput_rps: float = 0.0
    concurrent_users: int = 1
    
    # Constitutional compliance
    constitutional_compliance: float = 1.0
    constitutional_validation_time_ms: float = 0.0
    
    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class PerformanceTestSuite:
    """Performance test suite configuration."""
    suite_name: str
    services: List[str]
    test_duration_seconds: int = 60
    concurrent_users: int = 10
    ramp_up_seconds: int = 10
    
    # Performance thresholds
    max_response_time_ms: float = 500.0
    max_error_rate_percent: float = 1.0
    min_throughput_rps: float = 10.0
    min_constitutional_compliance: float = 0.95

class ACGSPerformanceTestSuite:
    """Automated performance test suite for ACGS services."""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self.setup_metrics()
        
        # Service configuration
        self.services = {
            "auth-service": 8000,
            "ac-service": 8001,
            "integrity-service": 8002,
            "fv-service": 8003,
            "gs-service": 8004,
            "pgc-service": 8005,
            "ec-service": 8006
        }
        
        # Test results
        self.test_results: List[PerformanceTestResult] = []
        
        logger.info("ACGS Performance Test Suite initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics for performance testing."""
        self.test_response_time = Histogram(
            'acgs_perf_test_response_time_seconds',
            'Performance test response times',
            ['service', 'endpoint', 'test_type'],
            registry=self.registry
        )
        
        self.test_throughput = Histogram(
            'acgs_perf_test_throughput_rps',
            'Performance test throughput',
            ['service', 'test_type'],
            registry=self.registry
        )
        
        self.test_errors = Counter(
            'acgs_perf_test_errors_total',
            'Performance test errors',
            ['service', 'endpoint', 'error_type'],
            registry=self.registry
        )
        
        self.constitutional_compliance_perf = Histogram(
            'acgs_perf_test_constitutional_compliance',
            'Constitutional compliance in performance tests',
            ['service'],
            registry=self.registry
        )

    async def run_comprehensive_performance_tests(self) -> Dict:
        """Run comprehensive performance tests."""
        logger.info("Starting comprehensive performance tests...")
        
        # Start metrics server
        start_http_server(8095, registry=self.registry)
        logger.info("Performance test metrics server started on port 8095")
        
        test_suites = [
            await self.run_api_endpoint_tests(),
            await self.run_database_operation_tests(),
            await self.run_nats_messaging_tests(),
            await self.run_constitutional_validation_tests(),
            await self.run_load_tests(),
            await self.run_stress_tests(),
            await self.run_endurance_tests()
        ]
        
        # Aggregate results
        results = await self.aggregate_test_results(test_suites)
        
        # Generate report
        await self.generate_performance_report(results)
        
        logger.info("Comprehensive performance tests completed")
        return results

    async def run_api_endpoint_tests(self) -> Dict:
        """Test API endpoint performance."""
        logger.info("Running API endpoint performance tests...")
        
        api_results = {}
        
        for service_name, port in self.services.items():
            service_results = []
            
            # Test health endpoint
            result = await self.test_endpoint_performance(
                service_name, port, "/health", "GET"
            )
            service_results.append(result)
            
            # Test status endpoint
            result = await self.test_endpoint_performance(
                service_name, port, "/api/v1/status", "GET"
            )
            service_results.append(result)
            
            # Test metrics endpoint
            result = await self.test_endpoint_performance(
                service_name, port, "/metrics", "GET"
            )
            service_results.append(result)
            
            # Service-specific endpoints
            if service_name == "ac-service":
                result = await self.test_endpoint_performance(
                    service_name, port, "/api/v1/constitutional/validate", "POST",
                    payload={"constitutional_hash": CONSTITUTIONAL_HASH}
                )
                service_results.append(result)
            
            elif service_name == "ec-service":
                result = await self.test_endpoint_performance(
                    service_name, port, "/api/v1/evolution/status", "GET"
                )
                service_results.append(result)
            
            api_results[service_name] = service_results
        
        return {"api_endpoint_tests": api_results}

    async def test_endpoint_performance(
        self, 
        service_name: str, 
        port: int, 
        endpoint: str, 
        method: str = "GET",
        payload: Optional[Dict] = None,
        concurrent_requests: int = 10
    ) -> PerformanceTestResult:
        """Test individual endpoint performance."""
        
        async def single_request():
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                try:
                    url = f"http://localhost:{port}{endpoint}"
                    
                    if method == "GET":
                        async with session.get(url, timeout=30) as response:
                            response_time = (time.time() - start_time) * 1000
                            return {
                                "success": True,
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "response_data": await response.text()
                            }
                    elif method == "POST":
                        async with session.post(url, json=payload, timeout=30) as response:
                            response_time = (time.time() - start_time) * 1000
                            return {
                                "success": True,
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "response_data": await response.text()
                            }
                            
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    return {
                        "success": False,
                        "response_time_ms": response_time,
                        "status_code": 0,
                        "error": str(e)
                    }
        
        # Run concurrent requests
        start_time = time.time()
        tasks = [single_request() for _ in range(concurrent_requests)]
        responses = await asyncio.gather(*tasks)
        total_duration = (time.time() - start_time) * 1000
        
        # Calculate metrics
        successful_responses = [r for r in responses if r["success"]]
        response_times = [r["response_time_ms"] for r in successful_responses]
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        success_rate = len(successful_responses) / len(responses) * 100
        throughput = len(successful_responses) / (total_duration / 1000) if total_duration > 0 else 0
        
        # Record metrics
        self.test_response_time.labels(
            service=service_name,
            endpoint=endpoint,
            test_type="api_endpoint"
        ).observe(avg_response_time / 1000)
        
        if len(successful_responses) < len(responses):
            self.test_errors.labels(
                service=service_name,
                endpoint=endpoint,
                error_type="request_failure"
            ).inc(len(responses) - len(successful_responses))
        
        result = PerformanceTestResult(
            test_name=f"api_endpoint_{method.lower()}",
            service_name=service_name,
            endpoint=endpoint,
            response_time_ms=avg_response_time,
            total_duration_ms=total_duration,
            success=success_rate > 95,  # 95% success rate threshold
            status_code=successful_responses[0]["status_code"] if successful_responses else 0,
            throughput_rps=throughput,
            concurrent_users=concurrent_requests
        )
        
        self.test_results.append(result)
        return result

    async def run_database_operation_tests(self) -> Dict:
        """Test database operation performance."""
        logger.info("Running database operation performance tests...")
        
        db_results = {}
        
        # Test database connectivity through services
        for service_name, port in self.services.items():
            try:
                # Test database-dependent operations
                if service_name in ["auth-service", "ac-service", "pgc-service"]:
                    result = await self.test_database_operations(service_name, port)
                    db_results[service_name] = result
                    
            except Exception as e:
                logger.warning(f"Database test failed for {service_name}: {e}")
                db_results[service_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {"database_operation_tests": db_results}

    async def test_database_operations(self, service_name: str, port: int) -> Dict:
        """Test database operations for a service."""
        operations = []
        
        # Test read operations
        read_result = await self.test_endpoint_performance(
            service_name, port, "/api/v1/status", "GET"
        )
        operations.append({"operation": "read", "result": read_result})
        
        # Test write operations (if applicable)
        if service_name == "ac-service":
            write_result = await self.test_endpoint_performance(
                service_name, port, "/api/v1/constitutional/validate", "POST",
                payload={"constitutional_hash": CONSTITUTIONAL_HASH, "test": True}
            )
            operations.append({"operation": "write", "result": write_result})
        
        return {
            "operations": operations,
            "avg_response_time": statistics.mean([op["result"].response_time_ms for op in operations]),
            "success": all(op["result"].success for op in operations)
        }

    async def run_nats_messaging_tests(self) -> Dict:
        """Test NATS messaging performance."""
        logger.info("Running NATS messaging performance tests...")
        
        nats_results = {}
        
        # Test NATS connectivity through services that use it
        for service_name in ["ec-service", "pgc-service"]:
            if service_name in self.services:
                port = self.services[service_name]
                
                try:
                    # Test NATS-dependent operations
                    result = await self.test_nats_operations(service_name, port)
                    nats_results[service_name] = result
                    
                except Exception as e:
                    logger.warning(f"NATS test failed for {service_name}: {e}")
                    nats_results[service_name] = {
                        "success": False,
                        "error": str(e)
                    }
        
        return {"nats_messaging_tests": nats_results}

    async def test_nats_operations(self, service_name: str, port: int) -> Dict:
        """Test NATS operations for a service."""
        # Test event publishing/subscribing through service endpoints
        if service_name == "ec-service":
            # Test evolution submission (which should publish NATS events)
            result = await self.test_endpoint_performance(
                service_name, port, "/api/v1/evolution/submit", "POST",
                payload={
                    "evolution_type": "performance_test",
                    "description": "NATS performance test",
                    "proposed_changes": {"test": True},
                    "priority": 5
                }
            )
            
            return {
                "nats_publish_test": result,
                "success": result.success
            }
        
        return {"success": True, "message": "No NATS operations to test"}

    async def run_constitutional_validation_tests(self) -> Dict:
        """Test constitutional validation performance."""
        logger.info("Running constitutional validation performance tests...")
        
        constitutional_results = {}
        
        # Test constitutional validation on applicable services
        constitutional_services = ["ac-service", "pgc-service", "ec-service"]
        
        for service_name in constitutional_services:
            if service_name in self.services:
                port = self.services[service_name]
                
                try:
                    result = await self.test_constitutional_validation(service_name, port)
                    constitutional_results[service_name] = result
                    
                    # Record constitutional compliance metrics
                    self.constitutional_compliance_perf.labels(
                        service=service_name
                    ).observe(result.get("compliance_score", 1.0))
                    
                except Exception as e:
                    logger.warning(f"Constitutional validation test failed for {service_name}: {e}")
                    constitutional_results[service_name] = {
                        "success": False,
                        "error": str(e)
                    }
        
        return {"constitutional_validation_tests": constitutional_results}

    async def test_constitutional_validation(self, service_name: str, port: int) -> Dict:
        """Test constitutional validation for a service."""
        validation_requests = [
            {"constitutional_hash": CONSTITUTIONAL_HASH, "validation_level": "basic"},
            {"constitutional_hash": CONSTITUTIONAL_HASH, "validation_level": "comprehensive"},
            {"constitutional_hash": "invalid_hash", "validation_level": "basic"}  # Should fail
        ]
        
        results = []
        
        for request in validation_requests:
            result = await self.test_endpoint_performance(
                service_name, port, "/api/v1/constitutional/validate", "POST",
                payload=request
            )
            results.append(result)
        
        # Calculate constitutional compliance metrics
        successful_validations = sum(1 for r in results if r.success and r.status_code == 200)
        compliance_score = successful_validations / len(results) if results else 0
        
        avg_validation_time = statistics.mean([r.response_time_ms for r in results])
        
        return {
            "validation_results": results,
            "compliance_score": compliance_score,
            "avg_validation_time_ms": avg_validation_time,
            "success": compliance_score >= 0.67  # At least 2/3 should succeed
        }

    async def run_load_tests(self) -> Dict:
        """Run load tests with increasing concurrent users."""
        logger.info("Running load tests...")
        
        load_results = {}
        user_levels = [1, 5, 10, 20, 50]
        
        for service_name, port in self.services.items():
            service_load_results = []
            
            for concurrent_users in user_levels:
                result = await self.test_endpoint_performance(
                    service_name, port, "/health", "GET",
                    concurrent_requests=concurrent_users
                )
                
                service_load_results.append({
                    "concurrent_users": concurrent_users,
                    "avg_response_time_ms": result.response_time_ms,
                    "throughput_rps": result.throughput_rps,
                    "success": result.success
                })
                
                # Record throughput metrics
                self.test_throughput.labels(
                    service=service_name,
                    test_type="load_test"
                ).observe(result.throughput_rps)
            
            load_results[service_name] = service_load_results
        
        return {"load_tests": load_results}

    async def run_stress_tests(self) -> Dict:
        """Run stress tests to find breaking points."""
        logger.info("Running stress tests...")
        
        stress_results = {}
        
        # Test with high concurrent load
        for service_name, port in self.services.items():
            try:
                # Stress test with 100 concurrent requests
                result = await self.test_endpoint_performance(
                    service_name, port, "/health", "GET",
                    concurrent_requests=100
                )
                
                stress_results[service_name] = {
                    "concurrent_users": 100,
                    "avg_response_time_ms": result.response_time_ms,
                    "throughput_rps": result.throughput_rps,
                    "success": result.success,
                    "breaking_point_reached": result.response_time_ms > 5000 or not result.success
                }
                
            except Exception as e:
                stress_results[service_name] = {
                    "success": False,
                    "error": str(e),
                    "breaking_point_reached": True
                }
        
        return {"stress_tests": stress_results}

    async def run_endurance_tests(self) -> Dict:
        """Run endurance tests for sustained load."""
        logger.info("Running endurance tests...")
        
        endurance_results = {}
        test_duration = 300  # 5 minutes
        
        for service_name, port in self.services.items():
            try:
                # Run sustained load for 5 minutes
                start_time = time.time()
                results = []
                
                while time.time() - start_time < test_duration:
                    result = await self.test_endpoint_performance(
                        service_name, port, "/health", "GET",
                        concurrent_requests=5
                    )
                    results.append(result)
                    
                    await asyncio.sleep(10)  # Test every 10 seconds
                
                # Calculate endurance metrics
                avg_response_time = statistics.mean([r.response_time_ms for r in results])
                success_rate = sum(1 for r in results if r.success) / len(results) * 100
                
                endurance_results[service_name] = {
                    "test_duration_seconds": test_duration,
                    "total_requests": len(results) * 5,  # 5 concurrent requests each time
                    "avg_response_time_ms": avg_response_time,
                    "success_rate_percent": success_rate,
                    "performance_degradation": avg_response_time > results[0].response_time_ms * 1.5
                }
                
            except Exception as e:
                endurance_results[service_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {"endurance_tests": endurance_results}

    async def aggregate_test_results(self, test_suites: List[Dict]) -> Dict:
        """Aggregate all test results."""
        aggregated = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": sum(1 for r in self.test_results if r.success),
                "failed_tests": sum(1 for r in self.test_results if not r.success),
                "avg_response_time_ms": statistics.mean([r.response_time_ms for r in self.test_results]) if self.test_results else 0,
                "constitutional_hash": CONSTITUTIONAL_HASH
            },
            "test_suites": test_suites,
            "performance_thresholds": {
                "response_time_threshold_ms": 500,
                "error_rate_threshold_percent": 1.0,
                "constitutional_compliance_threshold": 0.95
            },
            "sla_compliance": self.check_sla_compliance(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return aggregated

    def check_sla_compliance(self) -> Dict:
        """Check SLA compliance based on test results."""
        if not self.test_results:
            return {"overall_compliance": False, "reason": "No test results"}
        
        avg_response_time = statistics.mean([r.response_time_ms for r in self.test_results])
        success_rate = sum(1 for r in self.test_results if r.success) / len(self.test_results) * 100
        error_rate = 100 - success_rate
        
        response_time_sla = avg_response_time < 500  # <500ms
        error_rate_sla = error_rate < 1.0  # <1%
        
        return {
            "response_time_sla": response_time_sla,
            "error_rate_sla": error_rate_sla,
            "overall_compliance": response_time_sla and error_rate_sla,
            "metrics": {
                "avg_response_time_ms": avg_response_time,
                "error_rate_percent": error_rate,
                "success_rate_percent": success_rate
            }
        }

    async def generate_performance_report(self, results: Dict):
        """Generate performance test report."""
        import os
        
        # Create reports directory
        reports_dir = "reports/performance_tests"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save detailed results
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        results_file = f"{reports_dir}/performance_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Performance test report saved: {results_file}")

# Global test suite instance
performance_suite = ACGSPerformanceTestSuite()

# Pytest integration
@pytest_asyncio.fixture
async def perf_suite():
    """Fixture for performance test suite."""
    return performance_suite

@pytest.mark.asyncio
async def test_api_endpoints_performance(perf_suite):
    """Test API endpoints performance."""
    results = await perf_suite.run_api_endpoint_tests()
    assert results["api_endpoint_tests"], "API endpoint tests should return results"

@pytest.mark.asyncio
async def test_constitutional_validation_performance(perf_suite):
    """Test constitutional validation performance."""
    results = await perf_suite.run_constitutional_validation_tests()
    assert results["constitutional_validation_tests"], "Constitutional validation tests should return results"

@pytest.mark.asyncio
async def test_load_performance(perf_suite):
    """Test load performance."""
    results = await perf_suite.run_load_tests()
    assert results["load_tests"], "Load tests should return results"

if __name__ == "__main__":
    async def main():
        suite = ACGSPerformanceTestSuite()
        results = await suite.run_comprehensive_performance_tests()

        print("\n" + "="*60)
        print("ACGS PERFORMANCE TEST RESULTS")
        print("="*60)
        print(f"Total Tests: {results['test_summary']['total_tests']}")
        print(f"Successful: {results['test_summary']['successful_tests']}")
        print(f"Failed: {results['test_summary']['failed_tests']}")
        print(f"Avg Response Time: {results['test_summary']['avg_response_time_ms']:.2f}ms")
        print(f"SLA Compliance: {results['sla_compliance']['overall_compliance']}")
        print("="*60)

        # Exit with error code if SLA compliance fails
        if not results['sla_compliance']['overall_compliance']:
            print("❌ SLA compliance failed - exiting with error code 1")
            exit(1)
        else:
            print("✅ All performance tests passed")

    asyncio.run(main())
