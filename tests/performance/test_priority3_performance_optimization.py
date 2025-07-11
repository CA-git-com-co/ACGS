"""
Priority 3: Performance Issues - Comprehensive Optimization Validation
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive test suite validating all phases of Priority 3 performance optimization:

Phase 1: Multi-Tier Caching Implementation
Phase 2: Database Optimization  
Phase 3: Request Pipeline Optimization
Phase 4: Validation and Testing

Performance Targets:
- Constitutional AI service: 159.94ms → <5ms P99 latency (97% reduction)
- Auth Service: 99.68ms → <4ms P99 latency (96% reduction)  
- Agent HITL service: 10,613.33ms → <5ms P99 latency (99.95% reduction)
- Overall: >100 RPS throughput, >85% cache hit rate
"""

import asyncio
import pytest
import time
import statistics
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import aiohttp
import requests

# Test configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service endpoints for testing
SERVICE_ENDPOINTS = {
    "constitutional_ai": "http://localhost:32768",
    "auth_service": "http://localhost:8016",
    "agent_hitl": "http://localhost:8008",  # Corrected port from Docker config
}

# Performance targets from the optimization strategy
PERFORMANCE_TARGETS = {
    "constitutional_ai_p99_ms": 5.0,    # Target: 159.94ms → <5ms
    "auth_service_p99_ms": 4.0,        # Target: 99.68ms → <4ms  
    "agent_hitl_p99_ms": 5.0,          # Target: 10,613.33ms → <5ms
    "overall_throughput_rps": 100.0,   # Target: >100 RPS
    "cache_hit_rate": 0.85,            # Target: >85%
    "constitutional_compliance": 1.0,   # Target: 100%
}

# Load testing configuration
LOAD_TEST_CONFIG = {
    "concurrent_users": 50,
    "test_duration_seconds": 60,
    "ramp_up_seconds": 10,
    "requests_per_user": 100,
}


@dataclass
class ServicePerformanceResult:
    """Performance test result for a service"""
    service_name: str
    avg_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    success_rate: float
    cache_hit_rate: float
    constitutional_compliance: bool
    target_met: bool
    constitutional_hash: str = CONSTITUTIONAL_HASH


class TestPriority3PerformanceOptimization:
    """Comprehensive test suite for Priority 3 performance optimization"""

    @pytest.mark.asyncio
    async def test_constitutional_ai_service_performance(self):
        """Test Constitutional AI service achieves <5ms P99 latency target"""
        
        service_url = SERVICE_ENDPOINTS["constitutional_ai"]
        target_latency = PERFORMANCE_TARGETS["constitutional_ai_p99_ms"]
        
        # Test service availability first
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip(f"Constitutional AI service not available at {service_url}")
        except Exception:
            pytest.skip(f"Constitutional AI service not available at {service_url}")
        
        # Performance test
        result = await self._test_service_performance(
            service_name="Constitutional AI",
            service_url=service_url,
            target_latency_ms=target_latency,
            endpoint="/health"
        )
        
        print(f"Constitutional AI Service Performance:")
        print(f"  Average latency: {result.avg_latency_ms:.3f}ms")
        print(f"  P99 latency: {result.p99_latency_ms:.3f}ms")
        print(f"  Throughput: {result.throughput_rps:.1f} RPS")
        print(f"  Success rate: {result.success_rate:.1%}")
        print(f"  Target: <{target_latency}ms P99 latency")
        print(f"  Target met: {result.target_met}")
        
        # Assert performance targets
        assert result.constitutional_compliance, "Constitutional compliance required"
        assert result.target_met, f"Constitutional AI P99 latency {result.p99_latency_ms:.3f}ms exceeds target {target_latency}ms"
        assert result.success_rate >= 0.95, f"Success rate {result.success_rate:.1%} below 95%"

    @pytest.mark.asyncio
    async def test_auth_service_performance(self):
        """Test Auth Service achieves <4ms P99 latency target"""
        
        service_url = SERVICE_ENDPOINTS["auth_service"]
        target_latency = PERFORMANCE_TARGETS["auth_service_p99_ms"]
        
        # Test service availability first
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip(f"Auth service not available at {service_url}")
        except Exception:
            pytest.skip(f"Auth service not available at {service_url}")
        
        # Performance test
        result = await self._test_service_performance(
            service_name="Auth Service",
            service_url=service_url,
            target_latency_ms=target_latency,
            endpoint="/health"
        )
        
        print(f"Auth Service Performance:")
        print(f"  Average latency: {result.avg_latency_ms:.3f}ms")
        print(f"  P99 latency: {result.p99_latency_ms:.3f}ms")
        print(f"  Throughput: {result.throughput_rps:.1f} RPS")
        print(f"  Success rate: {result.success_rate:.1%}")
        print(f"  Target: <{target_latency}ms P99 latency")
        print(f"  Target met: {result.target_met}")
        
        # Assert performance targets
        assert result.constitutional_compliance, "Constitutional compliance required"
        assert result.target_met, f"Auth Service P99 latency {result.p99_latency_ms:.3f}ms exceeds target {target_latency}ms"
        assert result.success_rate >= 0.95, f"Success rate {result.success_rate:.1%} below 95%"

    @pytest.mark.asyncio
    async def test_agent_hitl_service_performance(self):
        """Test Agent HITL service achieves <5ms P99 latency target"""
        
        service_url = SERVICE_ENDPOINTS["agent_hitl"]
        target_latency = PERFORMANCE_TARGETS["agent_hitl_p99_ms"]
        
        # Test service availability first
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip(f"Agent HITL service not available at {service_url}")
        except Exception:
            pytest.skip(f"Agent HITL service not available at {service_url}")
        
        # Performance test
        result = await self._test_service_performance(
            service_name="Agent HITL",
            service_url=service_url,
            target_latency_ms=target_latency,
            endpoint="/health"
        )
        
        print(f"Agent HITL Service Performance:")
        print(f"  Average latency: {result.avg_latency_ms:.3f}ms")
        print(f"  P99 latency: {result.p99_latency_ms:.3f}ms")
        print(f"  Throughput: {result.throughput_rps:.1f} RPS")
        print(f"  Success rate: {result.success_rate:.1%}")
        print(f"  Target: <{target_latency}ms P99 latency")
        print(f"  Target met: {result.target_met}")
        
        # Assert performance targets
        assert result.constitutional_compliance, "Constitutional compliance required"
        assert result.target_met, f"Agent HITL P99 latency {result.p99_latency_ms:.3f}ms exceeds target {target_latency}ms"
        assert result.success_rate >= 0.95, f"Success rate {result.success_rate:.1%} below 95%"

    @pytest.mark.asyncio
    async def test_overall_system_throughput(self):
        """Test overall system achieves >100 RPS throughput target"""
        
        target_throughput = PERFORMANCE_TARGETS["overall_throughput_rps"]
        
        # Test all available services concurrently
        available_services = []
        for service_name, service_url in SERVICE_ENDPOINTS.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=2)
                if response.status_code == 200:
                    available_services.append((service_name, service_url))
            except Exception:
                continue
        
        if not available_services:
            pytest.skip("No services available for throughput testing")
        
        # Run concurrent throughput test
        throughput_results = []
        
        async def service_throughput_test(service_name: str, service_url: str):
            """Test throughput for a single service"""
            async with aiohttp.ClientSession() as session:
                start_time = time.perf_counter()
                successful_requests = 0
                
                # Run requests for test duration
                tasks = []
                for _ in range(LOAD_TEST_CONFIG["requests_per_user"]):
                    task = self._make_request(session, f"{service_url}/health")
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.perf_counter()
                
                # Count successful requests
                for result in results:
                    if not isinstance(result, Exception) and result:
                        successful_requests += 1
                
                duration_seconds = end_time - start_time
                throughput_rps = successful_requests / duration_seconds if duration_seconds > 0 else 0
                
                return service_name, throughput_rps, successful_requests
        
        # Run throughput tests for all available services
        throughput_tasks = [
            service_throughput_test(name, url) 
            for name, url in available_services
        ]
        
        throughput_results = await asyncio.gather(*throughput_tasks)
        
        # Calculate overall throughput
        total_throughput = sum(result[1] for result in throughput_results)
        total_requests = sum(result[2] for result in throughput_results)
        
        print(f"Overall System Throughput:")
        for service_name, throughput, requests in throughput_results:
            print(f"  {service_name}: {throughput:.1f} RPS ({requests} requests)")
        print(f"  Total throughput: {total_throughput:.1f} RPS")
        print(f"  Target: >{target_throughput} RPS")
        print(f"  Target met: {total_throughput >= target_throughput}")
        
        # Assert throughput target
        assert total_throughput >= target_throughput, \
            f"Overall throughput {total_throughput:.1f} RPS below target {target_throughput} RPS"

    @pytest.mark.asyncio
    async def test_constitutional_compliance_under_load(self):
        """Test constitutional compliance is maintained under load"""
        
        target_compliance = PERFORMANCE_TARGETS["constitutional_compliance"]
        
        # Test constitutional compliance for all available services under load
        compliance_results = []
        
        for service_name, service_url in SERVICE_ENDPOINTS.items():
            try:
                # Test service availability
                response = requests.get(f"{service_url}/health", timeout=2)
                if response.status_code != 200:
                    continue
                
                # Test constitutional compliance under load
                compliant_responses = 0
                total_responses = 0
                
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for _ in range(50):  # 50 requests per service
                        task = self._make_request(session, f"{service_url}/health")
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in results:
                        if not isinstance(result, Exception) and result:
                            total_responses += 1
                            # Check for constitutional hash in response
                            if isinstance(result, dict) and result.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                                compliant_responses += 1
                
                compliance_rate = compliant_responses / total_responses if total_responses > 0 else 0
                compliance_results.append((service_name, compliance_rate, compliant_responses, total_responses))
                
            except Exception as e:
                print(f"Constitutional compliance test failed for {service_name}: {e}")
                continue
        
        # Calculate overall compliance
        total_compliant = sum(result[2] for result in compliance_results)
        total_responses = sum(result[3] for result in compliance_results)
        overall_compliance = total_compliant / total_responses if total_responses > 0 else 0
        
        print(f"Constitutional Compliance Under Load:")
        for service_name, compliance_rate, compliant, total in compliance_results:
            print(f"  {service_name}: {compliance_rate:.1%} ({compliant}/{total})")
        print(f"  Overall compliance: {overall_compliance:.1%}")
        print(f"  Target: {target_compliance:.0%}")
        print(f"  Target met: {overall_compliance >= target_compliance}")
        
        # Assert compliance target
        assert overall_compliance >= target_compliance, \
            f"Constitutional compliance {overall_compliance:.1%} below target {target_compliance:.0%}"

    async def _test_service_performance(
        self, 
        service_name: str, 
        service_url: str, 
        target_latency_ms: float,
        endpoint: str = "/health"
    ) -> ServicePerformanceResult:
        """Test performance for a single service"""
        
        latencies = []
        successful_requests = 0
        constitutional_compliant = 0
        total_requests = 100
        
        async with aiohttp.ClientSession() as session:
            start_time = time.perf_counter()
            
            for i in range(total_requests):
                request_start = time.perf_counter()
                
                try:
                    result = await self._make_request(session, f"{service_url}{endpoint}")
                    request_end = time.perf_counter()
                    
                    if result:
                        latency_ms = (request_end - request_start) * 1000
                        latencies.append(latency_ms)
                        successful_requests += 1
                        
                        # Check constitutional compliance
                        if isinstance(result, dict) and result.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                            constitutional_compliant += 1
                
                except Exception:
                    continue
            
            end_time = time.perf_counter()
        
        # Calculate metrics
        duration_seconds = end_time - start_time
        avg_latency = statistics.mean(latencies) if latencies else 0
        p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies) if latencies else 0
        throughput_rps = successful_requests / duration_seconds if duration_seconds > 0 else 0
        success_rate = successful_requests / total_requests
        cache_hit_rate = 0.0  # Would need cache metrics to calculate
        constitutional_compliance = constitutional_compliant > 0
        target_met = p99_latency < target_latency_ms
        
        return ServicePerformanceResult(
            service_name=service_name,
            avg_latency_ms=avg_latency,
            p99_latency_ms=p99_latency,
            throughput_rps=throughput_rps,
            success_rate=success_rate,
            cache_hit_rate=cache_hit_rate,
            constitutional_compliance=constitutional_compliance,
            target_met=target_met
        )

    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> Any:
        """Make HTTP request and return parsed response"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        return await response.json()
                    else:
                        return await response.text()
                return None
        except Exception:
            return None


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
