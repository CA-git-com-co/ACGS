#!/usr/bin/env python3
"""
ACGS-2 Infrastructure Validation and Performance Testing
HASH-OK:cdd01ef066bc6cf2

This script validates the current ACGS-2 infrastructure and performs
comprehensive performance testing with constitutional compliance validation.
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class ServiceEndpoint:
    name: str
    url: str
    port: int
    expected_response_keys: List[str]
    timeout: float = 5.0

@dataclass
class PerformanceMetrics:
    service_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency_ms: float
    p99_latency_ms: float
    p95_latency_ms: float
    throughput_rps: float
    constitutional_compliance_rate: float
    errors: List[str]

class ACGSInfrastructureValidator:
    def __init__(self):
        self.services = [
            ServiceEndpoint(
                name="auth_service",
                url="http://localhost:8016/health",
                port=8016,
                expected_response_keys=["status", "constitutional_hash"]
            ),
            ServiceEndpoint(
                name="constitutional_ai",
                url="http://localhost:32768/health",
                port=32768,
                expected_response_keys=["status", "constitutional_hash"]
            ),
            ServiceEndpoint(
                name="agent_hitl",
                url="http://localhost:8008/health",
                port=8008,
                expected_response_keys=["status", "constitutional_hash"]
            ),
        ]
        
        # Additional endpoints for testing
        self.test_endpoints = [
            ServiceEndpoint(
                name="auth_service_validate",
                url="http://localhost:8016/api/v1/validate",
                port=8016,
                expected_response_keys=["valid"],
                timeout=10.0
            ),
        ]
        
        self.performance_targets = {
            "p99_latency_ms": 5.0,
            "throughput_rps": 100.0,
            "cache_hit_rate": 0.85,
            "constitutional_compliance_rate": 1.0
        }

    async def validate_service_health(self, session: aiohttp.ClientSession, service: ServiceEndpoint) -> Dict[str, Any]:
        """Validate individual service health and constitutional compliance."""
        try:
            start_time = time.time()
            async with session.get(service.url, timeout=aiohttp.ClientTimeout(total=service.timeout)) as response:
                latency_ms = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate constitutional hash
                    constitutional_compliant = data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                    
                    # Check expected response structure
                    has_expected_keys = all(key in data for key in service.expected_response_keys)
                    
                    return {
                        "service": service.name,
                        "status": "healthy",
                        "latency_ms": latency_ms,
                        "constitutional_compliant": constitutional_compliant,
                        "has_expected_keys": has_expected_keys,
                        "response_data": data,
                        "error": None
                    }
                else:
                    return {
                        "service": service.name,
                        "status": "unhealthy",
                        "latency_ms": latency_ms,
                        "constitutional_compliant": False,
                        "has_expected_keys": False,
                        "response_data": None,
                        "error": f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            return {
                "service": service.name,
                "status": "error",
                "latency_ms": None,
                "constitutional_compliant": False,
                "has_expected_keys": False,
                "response_data": None,
                "error": str(e)
            }

    async def run_performance_test(self, session: aiohttp.ClientSession, service: ServiceEndpoint, 
                                 duration_seconds: int = 30, concurrent_requests: int = 10) -> PerformanceMetrics:
        """Run performance test against a service endpoint."""
        print(f"🚀 Running performance test for {service.name} ({duration_seconds}s, {concurrent_requests} concurrent)")
        
        latencies = []
        successful_requests = 0
        failed_requests = 0
        constitutional_compliant = 0
        errors = []
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        async def make_request():
            nonlocal successful_requests, failed_requests, constitutional_compliant
            
            try:
                request_start = time.time()
                async with session.get(service.url, timeout=aiohttp.ClientTimeout(total=service.timeout)) as response:
                    request_latency = (time.time() - request_start) * 1000
                    latencies.append(request_latency)
                    
                    if response.status == 200:
                        successful_requests += 1
                        try:
                            data = await response.json()
                            if data.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                                constitutional_compliant += 1
                        except:
                            pass
                    else:
                        failed_requests += 1
                        errors.append(f"HTTP {response.status}")
                        
            except Exception as e:
                failed_requests += 1
                errors.append(str(e))
        
        # Run concurrent requests for the specified duration
        tasks = []
        while time.time() < end_time:
            # Launch concurrent requests
            batch_tasks = [make_request() for _ in range(concurrent_requests)]
            tasks.extend(batch_tasks)
            await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Small delay to control request rate
            await asyncio.sleep(0.1)
        
        # Calculate metrics
        total_requests = successful_requests + failed_requests
        actual_duration = time.time() - start_time
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        else:
            avg_latency = p95_latency = p99_latency = 0
        
        throughput_rps = total_requests / actual_duration if actual_duration > 0 else 0
        constitutional_compliance_rate = constitutional_compliant / total_requests if total_requests > 0 else 0
        
        return PerformanceMetrics(
            service_name=service.name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_latency_ms=avg_latency,
            p99_latency_ms=p99_latency,
            p95_latency_ms=p95_latency,
            throughput_rps=throughput_rps,
            constitutional_compliance_rate=constitutional_compliance_rate,
            errors=list(set(errors))  # Remove duplicates
        )

    async def validate_infrastructure(self) -> Dict[str, Any]:
        """Validate complete ACGS-2 infrastructure."""
        print("=" * 80)
        print("🎯 ACGS-2 Infrastructure Validation & Performance Testing")
        print("=" * 80)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print()
        
        async with aiohttp.ClientSession() as session:
            # 1. Health Check Validation
            print("📊 Running health checks...")
            health_results = []
            for service in self.services:
                result = await self.validate_service_health(session, service)
                health_results.append(result)
                
                status_icon = "✅" if result["status"] == "healthy" else "❌"
                compliance_icon = "✅" if result["constitutional_compliant"] else "❌"
                
                print(f"   {status_icon} {service.name}: {result['status']}")
                if result["latency_ms"]:
                    print(f"      Latency: {result['latency_ms']:.1f}ms")
                print(f"      Constitutional Compliance: {compliance_icon}")
                if result["error"]:
                    print(f"      Error: {result['error']}")
                print()
            
            # 2. Performance Testing
            print("🚀 Running performance tests...")
            performance_results = []
            for service in self.services:
                if any(h["service"] == service.name and h["status"] == "healthy" for h in health_results):
                    metrics = await self.run_performance_test(session, service, duration_seconds=15, concurrent_requests=5)
                    performance_results.append(metrics)
                    
                    # Performance evaluation
                    p99_status = "✅" if metrics.p99_latency_ms <= self.performance_targets["p99_latency_ms"] else "⚠️"
                    throughput_status = "✅" if metrics.throughput_rps >= self.performance_targets["throughput_rps"] else "⚠️"
                    compliance_status = "✅" if metrics.constitutional_compliance_rate >= self.performance_targets["constitutional_compliance_rate"] else "❌"
                    
                    print(f"   📈 {service.name} Results:")
                    print(f"      Requests: {metrics.total_requests} (Success: {metrics.successful_requests}, Failed: {metrics.failed_requests})")
                    print(f"      {p99_status} P99 Latency: {metrics.p99_latency_ms:.1f}ms (Target: ≤{self.performance_targets['p99_latency_ms']}ms)")
                    print(f"      {throughput_status} Throughput: {metrics.throughput_rps:.1f} RPS (Target: ≥{self.performance_targets['throughput_rps']} RPS)")
                    print(f"      {compliance_status} Constitutional Compliance: {metrics.constitutional_compliance_rate:.1%}")
                    if metrics.errors:
                        print(f"      Errors: {metrics.errors[:3]}")  # Show first 3 errors
                    print()
            
            # 3. Generate Summary Report
            return self.generate_summary_report(health_results, performance_results)

    def generate_summary_report(self, health_results: List[Dict], performance_results: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Generate comprehensive summary report."""
        print("=" * 80)
        print("📋 INFRASTRUCTURE VALIDATION SUMMARY")
        print("=" * 80)
        
        # Health Summary
        healthy_services = sum(1 for r in health_results if r["status"] == "healthy")
        total_services = len(health_results)
        constitutional_compliant_services = sum(1 for r in health_results if r["constitutional_compliant"])
        
        print(f"🏥 Health Status: {healthy_services}/{total_services} services healthy")
        print(f"⚖️  Constitutional Compliance: {constitutional_compliant_services}/{total_services} services compliant")
        
        # Performance Summary
        if performance_results:
            avg_p99_latency = statistics.mean([m.p99_latency_ms for m in performance_results])
            avg_throughput = statistics.mean([m.throughput_rps for m in performance_results])
            avg_compliance_rate = statistics.mean([m.constitutional_compliance_rate for m in performance_results])
            
            p99_meets_target = avg_p99_latency <= self.performance_targets["p99_latency_ms"]
            throughput_meets_target = avg_throughput >= self.performance_targets["throughput_rps"]
            compliance_meets_target = avg_compliance_rate >= self.performance_targets["constitutional_compliance_rate"]
            
            print(f"\n📊 Performance Metrics:")
            print(f"   {'✅' if p99_meets_target else '⚠️'} Average P99 Latency: {avg_p99_latency:.1f}ms")
            print(f"   {'✅' if throughput_meets_target else '⚠️'} Average Throughput: {avg_throughput:.1f} RPS")
            print(f"   {'✅' if compliance_meets_target else '❌'} Average Constitutional Compliance: {avg_compliance_rate:.1%}")
        
        # Overall Assessment
        overall_healthy = healthy_services == total_services
        overall_compliant = constitutional_compliant_services == total_services
        overall_performant = all([
            avg_p99_latency <= self.performance_targets["p99_latency_ms"] if performance_results else True,
            avg_throughput >= self.performance_targets["throughput_rps"] if performance_results else True,
            avg_compliance_rate >= self.performance_targets["constitutional_compliance_rate"] if performance_results else True
        ]) if performance_results else True
        
        overall_status = "EXCELLENT" if all([overall_healthy, overall_compliant, overall_performant]) else \
                        "GOOD" if overall_healthy and overall_compliant else \
                        "NEEDS_ATTENTION"
        
        print(f"\n🎯 Overall System Status: {overall_status}")
        print(f"Constitutional Hash Validation: {CONSTITUTIONAL_HASH}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "overall_status": overall_status,
            "health_summary": {
                "healthy_services": healthy_services,
                "total_services": total_services,
                "constitutional_compliant_services": constitutional_compliant_services
            },
            "performance_summary": {
                "avg_p99_latency_ms": avg_p99_latency if performance_results else None,
                "avg_throughput_rps": avg_throughput if performance_results else None,
                "avg_constitutional_compliance_rate": avg_compliance_rate if performance_results else None,
                "meets_performance_targets": overall_performant
            },
            "detailed_health_results": health_results,
            "detailed_performance_results": [
                {
                    "service_name": m.service_name,
                    "total_requests": m.total_requests,
                    "successful_requests": m.successful_requests,
                    "failed_requests": m.failed_requests,
                    "avg_latency_ms": m.avg_latency_ms,
                    "p99_latency_ms": m.p99_latency_ms,
                    "throughput_rps": m.throughput_rps,
                    "constitutional_compliance_rate": m.constitutional_compliance_rate,
                    "errors": m.errors
                } for m in performance_results
            ]
        }

async def main():
    """Main execution function."""
    validator = ACGSInfrastructureValidator()
    
    try:
        report = await validator.validate_infrastructure()
        
        # Save detailed report
        report_file = f"acgs_infrastructure_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print(f"HASH-OK:{CONSTITUTIONAL_HASH}")
        
        return 0 if report["overall_status"] in ["EXCELLENT", "GOOD"] else 1
        
    except Exception as e:
        print(f"❌ Infrastructure validation failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
