#!/usr/bin/env python3
"""
Standalone Priority 3: Performance Issues - Performance Validation
Constitutional Hash: cdd01ef066bc6cf2

Standalone performance test to validate optimization targets without pytest dependencies.

Performance Targets:
- Constitutional AI service: 159.94ms → <5ms P99 latency (97% reduction)
- Auth Service: 99.68ms → <4ms P99 latency (96% reduction)  
- Agent HITL service: 10,613.33ms → <5ms P99 latency (99.95% reduction)
- Overall: >100 RPS throughput, >85% cache hit rate
"""

import asyncio
import time
import statistics
import json
import sys
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import requests

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

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


@dataclass
class ServicePerformanceResult:
    """Performance test result for a service"""
    service_name: str
    avg_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    success_rate: float
    constitutional_compliance: bool
    target_met: bool
    constitutional_hash: str = CONSTITUTIONAL_HASH


class Priority3PerformanceValidator:
    """Standalone performance validator for Priority 3 optimization"""

    def __init__(self):
        self.results = []
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def test_service_performance(self, service_name: str, service_url: str, target_latency_ms: float) -> ServicePerformanceResult:
        """Test performance for a single service"""
        
        print(f"\n🔍 Testing {service_name} Performance")
        print(f"   Service URL: {service_url}")
        print(f"   Target P99 latency: <{target_latency_ms}ms")
        
        # Test service availability first
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            if response.status_code != 200:
                print(f"   ❌ Service not available (HTTP {response.status_code})")
                return self._create_failed_result(service_name, "Service unavailable")
        except Exception as e:
            print(f"   ❌ Service not available: {e}")
            return self._create_failed_result(service_name, f"Connection failed: {e}")
        
        # Performance test
        latencies = []
        successful_requests = 0
        constitutional_compliant = 0
        total_requests = 100
        
        print(f"   📊 Running {total_requests} performance test requests...")
        
        start_time = time.perf_counter()
        
        for i in range(total_requests):
            request_start = time.perf_counter()
            
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                request_end = time.perf_counter()
                
                if response.status_code == 200:
                    latency_ms = (request_end - request_start) * 1000
                    latencies.append(latency_ms)
                    successful_requests += 1
                    
                    # Check constitutional compliance
                    try:
                        response_data = response.json()
                        if isinstance(response_data, dict) and response_data.get("constitutional_hash") == self.constitutional_hash:
                            constitutional_compliant += 1
                    except:
                        # If not JSON, check if response contains hash
                        if self.constitutional_hash in response.text:
                            constitutional_compliant += 1
            
            except Exception as e:
                print(f"   ⚠️  Request {i+1} failed: {e}")
                continue
            
            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"   📈 Progress: {i+1}/{total_requests} requests completed")
        
        end_time = time.perf_counter()
        
        # Calculate metrics
        if not latencies:
            print(f"   ❌ No successful requests completed")
            return self._create_failed_result(service_name, "No successful requests")
        
        duration_seconds = end_time - start_time
        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        throughput_rps = successful_requests / duration_seconds if duration_seconds > 0 else 0
        success_rate = successful_requests / total_requests
        constitutional_compliance = constitutional_compliant > 0
        target_met = p99_latency < target_latency_ms
        
        result = ServicePerformanceResult(
            service_name=service_name,
            avg_latency_ms=avg_latency,
            p99_latency_ms=p99_latency,
            throughput_rps=throughput_rps,
            success_rate=success_rate,
            constitutional_compliance=constitutional_compliance,
            target_met=target_met
        )
        
        # Print results
        print(f"   📊 Performance Results:")
        print(f"      Average latency: {avg_latency:.3f}ms")
        print(f"      P99 latency: {p99_latency:.3f}ms")
        print(f"      Throughput: {throughput_rps:.1f} RPS")
        print(f"      Success rate: {success_rate:.1%}")
        print(f"      Constitutional compliance: {'✅' if constitutional_compliance else '❌'}")
        print(f"      Target met: {'✅' if target_met else '❌'}")
        
        return result

    def test_constitutional_ai_service(self) -> ServicePerformanceResult:
        """Test Constitutional AI service performance"""
        return self.test_service_performance(
            "Constitutional AI",
            SERVICE_ENDPOINTS["constitutional_ai"],
            PERFORMANCE_TARGETS["constitutional_ai_p99_ms"]
        )

    def test_auth_service(self) -> ServicePerformanceResult:
        """Test Auth Service performance"""
        return self.test_service_performance(
            "Auth Service",
            SERVICE_ENDPOINTS["auth_service"],
            PERFORMANCE_TARGETS["auth_service_p99_ms"]
        )

    def test_agent_hitl_service(self) -> ServicePerformanceResult:
        """Test Agent HITL service performance"""
        return self.test_service_performance(
            "Agent HITL",
            SERVICE_ENDPOINTS["agent_hitl"],
            PERFORMANCE_TARGETS["agent_hitl_p99_ms"]
        )

    def test_overall_system_throughput(self) -> Dict[str, Any]:
        """Test overall system throughput"""
        
        print(f"\n🚀 Testing Overall System Throughput")
        print(f"   Target: >{PERFORMANCE_TARGETS['overall_throughput_rps']} RPS")
        
        # Test all available services
        available_services = []
        for service_name, service_url in SERVICE_ENDPOINTS.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=2)
                if response.status_code == 200:
                    available_services.append((service_name, service_url))
                    print(f"   ✅ {service_name} available")
                else:
                    print(f"   ❌ {service_name} unavailable (HTTP {response.status_code})")
            except Exception as e:
                print(f"   ❌ {service_name} unavailable: {e}")
        
        if not available_services:
            print(f"   ❌ No services available for throughput testing")
            return {"total_throughput": 0, "target_met": False, "available_services": 0}
        
        # Test throughput for each available service
        throughput_results = []
        
        for service_name, service_url in available_services:
            print(f"   📊 Testing {service_name} throughput...")
            
            start_time = time.perf_counter()
            successful_requests = 0
            total_requests = 50  # Fewer requests for throughput test
            
            for i in range(total_requests):
                try:
                    response = requests.get(f"{service_url}/health", timeout=2)
                    if response.status_code == 200:
                        successful_requests += 1
                except:
                    continue
            
            end_time = time.perf_counter()
            duration_seconds = end_time - start_time
            throughput_rps = successful_requests / duration_seconds if duration_seconds > 0 else 0
            
            throughput_results.append((service_name, throughput_rps, successful_requests))
            print(f"      {service_name}: {throughput_rps:.1f} RPS ({successful_requests}/{total_requests} successful)")
        
        # Calculate overall throughput
        total_throughput = sum(result[1] for result in throughput_results)
        target_met = total_throughput >= PERFORMANCE_TARGETS["overall_throughput_rps"]
        
        print(f"   📊 Overall Throughput Results:")
        print(f"      Total throughput: {total_throughput:.1f} RPS")
        print(f"      Target: >{PERFORMANCE_TARGETS['overall_throughput_rps']} RPS")
        print(f"      Target met: {'✅' if target_met else '❌'}")
        
        return {
            "total_throughput": total_throughput,
            "target_met": target_met,
            "available_services": len(available_services),
            "service_results": throughput_results
        }

    def _create_failed_result(self, service_name: str, reason: str) -> ServicePerformanceResult:
        """Create a failed result for unavailable services"""
        return ServicePerformanceResult(
            service_name=service_name,
            avg_latency_ms=0.0,
            p99_latency_ms=float('inf'),
            throughput_rps=0.0,
            success_rate=0.0,
            constitutional_compliance=False,
            target_met=False
        )

    def run_comprehensive_performance_validation(self) -> Dict[str, Any]:
        """Run comprehensive performance validation"""
        
        print("=" * 80)
        print("🎯 ACGS-2 Priority 3: Performance Issues - Comprehensive Validation")
        print("=" * 80)
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test individual services
        service_results = []
        
        print(f"\n📋 Phase 1: Individual Service Performance Testing")
        
        # Test Constitutional AI service
        constitutional_ai_result = self.test_constitutional_ai_service()
        service_results.append(constitutional_ai_result)
        
        # Test Auth Service
        auth_service_result = self.test_auth_service()
        service_results.append(auth_service_result)
        
        # Test Agent HITL service
        agent_hitl_result = self.test_agent_hitl_service()
        service_results.append(agent_hitl_result)
        
        # Test overall system throughput
        print(f"\n📋 Phase 2: Overall System Throughput Testing")
        throughput_result = self.test_overall_system_throughput()
        
        # Generate summary
        print(f"\n📊 COMPREHENSIVE PERFORMANCE VALIDATION SUMMARY")
        print("=" * 80)
        
        services_tested = len(service_results)
        services_passed = sum(1 for result in service_results if result.target_met)
        constitutional_compliant = sum(1 for result in service_results if result.constitutional_compliance)
        
        print(f"Services Tested: {services_tested}")
        print(f"Services Meeting Performance Targets: {services_passed}/{services_tested}")
        print(f"Constitutional Compliance: {constitutional_compliant}/{services_tested}")
        print(f"Overall Throughput Target Met: {'✅' if throughput_result['target_met'] else '❌'}")
        
        # Detailed results
        print(f"\nDetailed Service Results:")
        for result in service_results:
            status = "✅ PASS" if result.target_met else "❌ FAIL"
            compliance = "✅" if result.constitutional_compliance else "❌"
            print(f"  {status} {result.service_name}")
            print(f"    P99 Latency: {result.p99_latency_ms:.3f}ms")
            print(f"    Success Rate: {result.success_rate:.1%}")
            print(f"    Constitutional Compliance: {compliance}")
        
        # Overall assessment
        all_targets_met = (services_passed == services_tested and 
                          constitutional_compliant == services_tested and 
                          throughput_result['target_met'])
        
        print(f"\n🎯 OVERALL ASSESSMENT: {'✅ ALL TARGETS MET' if all_targets_met else '❌ OPTIMIZATION REQUIRED'}")
        
        if not all_targets_met:
            print(f"\n🔧 OPTIMIZATION RECOMMENDATIONS:")
            for result in service_results:
                if not result.target_met:
                    print(f"  • {result.service_name}: Implement multi-tier caching (current P99: {result.p99_latency_ms:.3f}ms)")
                if not result.constitutional_compliance:
                    print(f"  • {result.service_name}: Fix constitutional hash validation")
            
            if not throughput_result['target_met']:
                print(f"  • System: Implement request pipeline optimization for throughput")
        
        # Save results
        results_summary = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "constitutional_hash": self.constitutional_hash,
            "services_tested": services_tested,
            "services_passed": services_passed,
            "constitutional_compliant": constitutional_compliant,
            "throughput_result": throughput_result,
            "all_targets_met": all_targets_met,
            "service_results": [
                {
                    "service_name": r.service_name,
                    "avg_latency_ms": r.avg_latency_ms,
                    "p99_latency_ms": r.p99_latency_ms,
                    "throughput_rps": r.throughput_rps,
                    "success_rate": r.success_rate,
                    "constitutional_compliance": r.constitutional_compliance,
                    "target_met": r.target_met
                } for r in service_results
            ]
        }
        
        with open("priority3_performance_validation_results.json", "w") as f:
            json.dump(results_summary, f, indent=2)
        
        print(f"\n💾 Results saved to: priority3_performance_validation_results.json")
        
        return results_summary


def main():
    """Main execution function"""
    validator = Priority3PerformanceValidator()
    results = validator.run_comprehensive_performance_validation()
    
    # Exit with appropriate code
    if results["all_targets_met"]:
        print(f"\n🎉 SUCCESS: All performance targets achieved!")
        sys.exit(0)
    else:
        print(f"\n⚠️  OPTIMIZATION REQUIRED: Performance targets not met")
        sys.exit(1)


if __name__ == "__main__":
    main()
