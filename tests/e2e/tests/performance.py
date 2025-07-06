"""
ACGS Performance Tests

Comprehensive performance testing for P99 latency targets, cache hit rates,
throughput validation, and load testing with concurrent operations.
"""
# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import time
import statistics
from typing import List, Dict, Any, Optional

from ..framework.base import PerformanceTest, E2ETestResult, PerformanceMetrics
from ..framework.config import ServiceType
from ..framework.utils import TestDataGenerator


class LatencyPerformanceTest(PerformanceTest):
    """Test P99 latency requirements across all services."""
    
    test_type = "performance"
    tags = ["performance", "latency", "p99"]
    
    def __init__(self, config, load_duration_seconds: int = 60):
        super().__init__(config, load_duration_seconds)
        self.target_p99_latency_ms = 5.0
    
    async def run_test(self) -> List[E2ETestResult]:
        """Run latency performance tests."""
        results = []
        
        # Test each service latency
        for service_type in [ServiceType.AUTH, ServiceType.CONSTITUTIONAL_AI, ServiceType.POLICY_GOVERNANCE]:
            if self.config.is_service_enabled(service_type):
                result = await self._test_service_latency(service_type)
                results.append(result)
        
        # Test end-to-end workflow latency
        result = await self._test_e2e_workflow_latency()
        results.append(result)
        
        return results
    
    async def _test_service_latency(self, service_type: ServiceType) -> E2ETestResult:
        """Test latency for a specific service."""
        start_time = time.perf_counter()
        
        try:
            # Define service-specific test endpoints
            test_endpoints = {
                ServiceType.AUTH: "/health",
                ServiceType.CONSTITUTIONAL_AI: "/health",
                ServiceType.POLICY_GOVERNANCE: "/api/v1/governance/metrics"
            }
            
            endpoint = test_endpoints.get(service_type, "/health")
            
            # Measure latency over multiple requests
            latencies = []
            successful_requests = 0
            total_requests = 100
            
            for _ in range(total_requests):
                request_start = time.perf_counter()
                
                try:
                    response = await self.make_service_request(
                        service_type, "GET", endpoint
                    )
                    
                    request_end = time.perf_counter()
                    request_latency_ms = (request_end - request_start) * 1000
                    latencies.append(request_latency_ms)
                    
                    if response.status_code == 200:
                        successful_requests += 1
                
                except Exception:
                    request_end = time.perf_counter()
                    request_latency_ms = (request_end - request_start) * 1000
                    latencies.append(request_latency_ms)
            
            end_time = time.perf_counter()
            total_duration_ms = (end_time - start_time) * 1000
            
            # Calculate latency percentiles
            if latencies:
                latencies.sort()
                p50 = latencies[int(len(latencies) * 0.5)]
                p95 = latencies[int(len(latencies) * 0.95)]
                p99 = latencies[int(len(latencies) * 0.99)]
                avg_latency = statistics.mean(latencies)
                max_latency = max(latencies)
            else:
                p50 = p95 = p99 = avg_latency = max_latency = 0
            
            # Check performance targets
            p99_target_met = p99 <= self.target_p99_latency_ms
            success_rate = successful_requests / total_requests if total_requests > 0 else 0
            
            overall_success = p99_target_met and success_rate >= 0.95
            
            return E2ETestResult(
                test_name=f"latency_performance_{service_type.value}",
                success=overall_success,
                duration_ms=total_duration_ms,
                performance_metrics={
                    "p50_latency_ms": p50,
                    "p95_latency_ms": p95,
                    "p99_latency_ms": p99,
                    "average_latency_ms": avg_latency,
                    "max_latency_ms": max_latency,
                    "success_rate": success_rate,
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "p99_target_met": p99_target_met,
                    "target_p99_latency_ms": self.target_p99_latency_ms
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return E2ETestResult(
                test_name=f"latency_performance_{service_type.value}",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Latency test failed for {service_type.value}: {str(e)}"
            )
    
    async def _test_e2e_workflow_latency(self) -> E2ETestResult:
        """Test end-to-end workflow latency."""
        start_time = time.perf_counter()
        
        try:
            # Generate test data
            data_generator = TestDataGenerator(self.config.constitutional_hash)
            test_policy = data_generator.generate_policy_data("latency_test_policy")
            
            workflow_latencies = []
            successful_workflows = 0
            total_workflows = 20
            
            for i in range(total_workflows):
                workflow_start = time.perf_counter()
                workflow_success = True
                
                try:
                    # Step 1: Constitutional validation
                    if self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
                        response = await self.make_service_request(
                            ServiceType.CONSTITUTIONAL_AI,
                            "POST",
                            "/api/v1/constitutional/validate",
                            json={**test_policy, "policy_id": f"latency_test_{i}"}
                        )
                        if response.status_code != 200:
                            workflow_success = False
                    
                    # Step 2: Policy governance check
                    if self.config.is_service_enabled(ServiceType.POLICY_GOVERNANCE) and workflow_success:
                        response = await self.make_service_request(
                            ServiceType.POLICY_GOVERNANCE,
                            "GET",
                            f"/api/v1/policies/latency_test_{i}"
                        )
                        # Accept 404 as valid response for non-existent policy
                        if response.status_code not in [200, 404]:
                            workflow_success = False
                    
                    workflow_end = time.perf_counter()
                    workflow_latency_ms = (workflow_end - workflow_start) * 1000
                    workflow_latencies.append(workflow_latency_ms)
                    
                    if workflow_success:
                        successful_workflows += 1
                
                except Exception:
                    workflow_end = time.perf_counter()
                    workflow_latency_ms = (workflow_end - workflow_start) * 1000
                    workflow_latencies.append(workflow_latency_ms)
            
            end_time = time.perf_counter()
            total_duration_ms = (end_time - start_time) * 1000
            
            # Calculate workflow latency statistics
            if workflow_latencies:
                workflow_latencies.sort()
                p50 = workflow_latencies[int(len(workflow_latencies) * 0.5)]
                p95 = workflow_latencies[int(len(workflow_latencies) * 0.95)]
                p99 = workflow_latencies[int(len(workflow_latencies) * 0.99)]
                avg_latency = statistics.mean(workflow_latencies)
            else:
                p50 = p95 = p99 = avg_latency = 0
            
            # Check performance targets (more lenient for E2E workflows)
            e2e_target_latency_ms = 20.0  # 20ms for E2E workflow
            p99_target_met = p99 <= e2e_target_latency_ms
            success_rate = successful_workflows / total_workflows if total_workflows > 0 else 0
            
            overall_success = p99_target_met and success_rate >= 0.9
            
            return E2ETestResult(
                test_name="e2e_workflow_latency",
                success=overall_success,
                duration_ms=total_duration_ms,
                performance_metrics={
                    "p50_latency_ms": p50,
                    "p95_latency_ms": p95,
                    "p99_latency_ms": p99,
                    "average_latency_ms": avg_latency,
                    "success_rate": success_rate,
                    "total_workflows": total_workflows,
                    "successful_workflows": successful_workflows,
                    "p99_target_met": p99_target_met,
                    "target_p99_latency_ms": e2e_target_latency_ms
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return E2ETestResult(
                test_name="e2e_workflow_latency",
                success=False,
                duration_ms=duration_ms,
                error_message=f"E2E workflow latency test failed: {str(e)}"
            )


class ThroughputPerformanceTest(PerformanceTest):
    """Test throughput and RPS requirements."""
    
    test_type = "performance"
    tags = ["performance", "throughput", "rps"]
    
    def __init__(self, config, load_duration_seconds: int = 60):
        super().__init__(config, load_duration_seconds)
        self.target_throughput_rps = 100.0
    
    async def run_test(self) -> List[E2ETestResult]:
        """Run throughput performance tests."""
        results = []
        
        # Test service throughput
        result = await self._test_service_throughput()
        results.append(result)
        
        # Test concurrent load handling
        result = await self._test_concurrent_load_handling()
        results.append(result)
        
        return results
    
    async def _test_service_throughput(self) -> E2ETestResult:
        """Test service throughput under sustained load."""
        start_time = time.perf_counter()
        
        try:
            # Define load test function for constitutional AI service
            async def constitutional_validation_request():
                data_generator = TestDataGenerator(self.config.constitutional_hash)
                test_policy = data_generator.generate_policy_data()
                
                if self.config.is_service_enabled(ServiceType.CONSTITUTIONAL_AI):
                    response = await self.make_service_request(
                        ServiceType.CONSTITUTIONAL_AI,
                        "POST",
                        "/api/v1/constitutional/validate",
                        json=test_policy
                    )
                    return response.status_code == 200
                else:
                    # Mock success for offline testing
                    await asyncio.sleep(0.001)  # Simulate processing time
                    return True
            
            # Run load test
            metrics = await self.run_load_test(
                constitutional_validation_request, 
                concurrent_requests=10
            )
            
            end_time = time.perf_counter()
            total_duration_ms = (end_time - start_time) * 1000
            
            # Check performance targets
            throughput_target_met = metrics.throughput_rps >= self.target_throughput_rps
            latency_target_met = metrics.latency_p99_ms <= 10.0  # 10ms for throughput test
            success_rate_target_met = metrics.success_rate >= 0.95
            
            overall_success = throughput_target_met and latency_target_met and success_rate_target_met
            
            return E2ETestResult(
                test_name="service_throughput",
                success=overall_success,
                duration_ms=total_duration_ms,
                performance_metrics={
                    "throughput_rps": metrics.throughput_rps,
                    "p99_latency_ms": metrics.latency_p99_ms,
                    "success_rate": metrics.success_rate,
                    "throughput_target_met": throughput_target_met,
                    "latency_target_met": latency_target_met,
                    "success_rate_target_met": success_rate_target_met,
                    "target_throughput_rps": self.target_throughput_rps
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return E2ETestResult(
                test_name="service_throughput",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Service throughput test failed: {str(e)}"
            )
    
    async def _test_concurrent_load_handling(self) -> E2ETestResult:
        """Test concurrent load handling capabilities."""
        start_time = time.perf_counter()
        
        try:
            # Test with increasing concurrent load
            concurrent_levels = [5, 10, 20, 30]
            load_results = []
            
            for concurrent_requests in concurrent_levels:
                # Define load test function
                async def health_check_request():
                    if self.config.is_service_enabled(ServiceType.POLICY_GOVERNANCE):
                        response = await self.make_service_request(
                            ServiceType.POLICY_GOVERNANCE,
                            "GET",
                            "/health"
                        )
                        return response.status_code == 200
                    else:
                        await asyncio.sleep(0.001)
                        return True
                
                # Run load test with current concurrency level
                test_duration = 30  # 30 seconds per level
                metrics = await self.run_load_test(
                    health_check_request,
                    concurrent_requests=concurrent_requests
                )
                
                load_results.append({
                    "concurrent_requests": concurrent_requests,
                    "throughput_rps": metrics.throughput_rps,
                    "p99_latency_ms": metrics.latency_p99_ms,
                    "success_rate": metrics.success_rate,
                    "performance_degradation": metrics.latency_p99_ms > 10.0  # Check for degradation
                })
            
            end_time = time.perf_counter()
            total_duration_ms = (end_time - start_time) * 1000
            
            # Analyze load handling
            max_throughput = max(r["throughput_rps"] for r in load_results)
            acceptable_degradation = all(r["success_rate"] >= 0.9 for r in load_results)
            latency_stability = all(r["p99_latency_ms"] <= 20.0 for r in load_results)
            
            overall_success = max_throughput >= self.target_throughput_rps and acceptable_degradation and latency_stability
            
            return E2ETestResult(
                test_name="concurrent_load_handling",
                success=overall_success,
                duration_ms=total_duration_ms,
                performance_metrics={
                    "max_throughput_rps": max_throughput,
                    "acceptable_degradation": acceptable_degradation,
                    "latency_stability": latency_stability,
                    "load_results": load_results,
                    "target_throughput_rps": self.target_throughput_rps
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return E2ETestResult(
                test_name="concurrent_load_handling",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Concurrent load handling test failed: {str(e)}"
            )


class CachePerformanceTest(PerformanceTest):
    """Test cache performance and hit rate requirements."""
    
    test_type = "performance"
    tags = ["performance", "cache", "hit-rate"]
    
    async def run_test(self) -> List[E2ETestResult]:
        """Run cache performance tests."""
        results = []
        
        # Test cache hit rate
        result = await self._test_cache_hit_rate()
        results.append(result)
        
        # Test cache performance under load
        result = await self._test_cache_performance_load()
        results.append(result)
        
        return results
    
    async def _test_cache_hit_rate(self) -> E2ETestResult:
        """Test cache hit rate requirements."""
        start_time = time.perf_counter()
        
        try:
            if not self.config.is_service_enabled(ServiceType.POLICY_GOVERNANCE):
                return E2ETestResult(
                    test_name="cache_hit_rate",
                    success=False,
                    duration_ms=0,
                    error_message="Policy Governance service not enabled"
                )
            
            # Test policy lookups to generate cache activity
            test_policy_ids = [f"cache_test_policy_{i}" for i in range(20)]
            
            # First round: populate cache (expect cache misses)
            for policy_id in test_policy_ids:
                try:
                    await self.make_service_request(
                        ServiceType.POLICY_GOVERNANCE,
                        "GET",
                        f"/api/v1/policies/{policy_id}"
                    )
                except Exception:
                    pass  # Ignore errors for non-existent policies
            
            # Second round: should hit cache
            for policy_id in test_policy_ids:
                try:
                    await self.make_service_request(
                        ServiceType.POLICY_GOVERNANCE,
                        "GET",
                        f"/api/v1/policies/{policy_id}"
                    )
                except Exception:
                    pass
            
            # Check cache metrics
            try:
                response = await self.make_service_request(
                    ServiceType.POLICY_GOVERNANCE,
                    "GET",
                    "/api/v1/governance/metrics"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    cache_hit_rate = data.get("cache_hit_rate", 0)
                    cache_hits = data.get("cache_hits", 0)
                    cache_misses = data.get("cache_misses", 0)
                    
                    cache_target_met = cache_hit_rate >= self.config.performance.cache_hit_rate
                    
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    
                    return E2ETestResult(
                        test_name="cache_hit_rate",
                        success=cache_target_met,
                        duration_ms=duration_ms,
                        performance_metrics={
                            "cache_hit_rate": cache_hit_rate,
                            "cache_hits": cache_hits,
                            "cache_misses": cache_misses,
                            "cache_target_met": cache_target_met,
                            "target_cache_hit_rate": self.config.performance.cache_hit_rate
                        }
                    )
                else:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    
                    return E2ETestResult(
                        test_name="cache_hit_rate",
                        success=False,
                        duration_ms=duration_ms,
                        error_message=f"Metrics endpoint returned {response.status_code}"
                    )
            
            except Exception as e:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                return E2ETestResult(
                    test_name="cache_hit_rate",
                    success=False,
                    duration_ms=duration_ms,
                    error_message=f"Cache metrics check failed: {str(e)}"
                )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return E2ETestResult(
                test_name="cache_hit_rate",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Cache hit rate test failed: {str(e)}"
            )
    
    async def _test_cache_performance_load(self) -> E2ETestResult:
        """Test cache performance under load."""
        start_time = time.perf_counter()
        
        try:
            if not self.config.is_service_enabled(ServiceType.POLICY_GOVERNANCE):
                return E2ETestResult(
                    test_name="cache_performance_load",
                    success=False,
                    duration_ms=0,
                    error_message="Policy Governance service not enabled"
                )
            
            # Define cache-heavy load test
            async def cache_lookup_request():
                # Use a small set of policy IDs to maximize cache hits
                policy_ids = [f"cache_load_policy_{i}" for i in range(5)]
                policy_id = policy_ids[int(time.time() * 1000) % len(policy_ids)]
                
                response = await self.make_service_request(
                    ServiceType.POLICY_GOVERNANCE,
                    "GET",
                    f"/api/v1/policies/{policy_id}"
                )
                
                # Accept 404 as success for non-existent policies
                return response.status_code in [200, 404]
            
            # Run load test
            metrics = await self.run_load_test(
                cache_lookup_request,
                concurrent_requests=15
            )
            
            # Check final cache metrics
            try:
                response = await self.make_service_request(
                    ServiceType.POLICY_GOVERNANCE,
                    "GET",
                    "/api/v1/governance/metrics"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    final_cache_hit_rate = data.get("cache_hit_rate", 0)
                else:
                    final_cache_hit_rate = 0
            except Exception:
                final_cache_hit_rate = 0
            
            end_time = time.perf_counter()
            total_duration_ms = (end_time - start_time) * 1000
            
            # Check performance targets
            throughput_target_met = metrics.throughput_rps >= 50.0  # Lower threshold for cache test
            latency_target_met = metrics.latency_p99_ms <= 5.0  # Cache should be fast
            cache_target_met = final_cache_hit_rate >= self.config.performance.cache_hit_rate
            
            overall_success = throughput_target_met and latency_target_met and cache_target_met
            
            return E2ETestResult(
                test_name="cache_performance_load",
                success=overall_success,
                duration_ms=total_duration_ms,
                performance_metrics={
                    "throughput_rps": metrics.throughput_rps,
                    "p99_latency_ms": metrics.latency_p99_ms,
                    "success_rate": metrics.success_rate,
                    "final_cache_hit_rate": final_cache_hit_rate,
                    "throughput_target_met": throughput_target_met,
                    "latency_target_met": latency_target_met,
                    "cache_target_met": cache_target_met
                }
            )
        
        except Exception as e:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            return E2ETestResult(
                test_name="cache_performance_load",
                success=False,
                duration_ms=duration_ms,
                error_message=f"Cache performance load test failed: {str(e)}"
            )
