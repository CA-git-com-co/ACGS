#!/usr/bin/env python3
"""
Constitutional Compliance Validation Script

This script validates that all ACGS services maintain constitutional compliance
and meet performance targets.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import time
from typing import Dict, List, Tuple
import aiohttp
import statistics

# Expected constitutional hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service endpoints to test
SERVICES = {
    "api_gateway": "http://localhost:8010/health",
    "constitutional_core": "http://localhost:32768/health",
    "auth_service": "http://localhost:8008/health",
    "code_analysis_engine": "http://localhost:8107/health",
}

# Performance targets
PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,
    "min_cache_hit_rate": 0.85,
    "min_rps": 100.0,
}

async def test_service_health(session: aiohttp.ClientSession, name: str, url: str) -> Dict:
    """Test a single service health endpoint."""
    try:
        start_time = time.time()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            if response.status == 200:
                data = await response.json()
                return {
                    "service": name,
                    "status": "healthy",
                    "latency_ms": latency_ms,
                    "constitutional_hash": data.get("constitutional_hash"),
                    "response": data
                }
            else:
                return {
                    "service": name,
                    "status": "unhealthy",
                    "latency_ms": latency_ms,
                    "error": f"HTTP {response.status}"
                }
    except Exception as e:
        return {
            "service": name,
            "status": "error",
            "error": str(e)
        }

async def measure_performance(session: aiohttp.ClientSession, url: str, requests: int = 100) -> Dict:
    """Measure performance metrics for a service."""
    latencies = []
    errors = 0
    
    print(f"  Measuring performance with {requests} requests...")
    
    start_time = time.time()
    
    # Send concurrent requests
    tasks = []
    for _ in range(requests):
        tasks.append(test_single_request(session, url))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    for result in results:
        if isinstance(result, Exception):
            errors += 1
        elif result.get("latency_ms"):
            latencies.append(result["latency_ms"])
        else:
            errors += 1
    
    if latencies:
        p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        avg_latency = statistics.mean(latencies)
        rps = len(latencies) / total_time
    else:
        p99_latency = float('inf')
        avg_latency = float('inf')
        rps = 0
    
    return {
        "total_requests": requests,
        "successful_requests": len(latencies),
        "errors": errors,
        "p99_latency_ms": p99_latency,
        "avg_latency_ms": avg_latency,
        "rps": rps,
        "total_time_s": total_time
    }

async def test_single_request(session: aiohttp.ClientSession, url: str) -> Dict:
    """Test a single request for performance measurement."""
    try:
        start_time = time.time()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            if response.status == 200:
                return {"latency_ms": latency_ms, "status": "success"}
            else:
                return {"error": f"HTTP {response.status}"}
    except Exception as e:
        return {"error": str(e)}

async def validate_constitutional_compliance() -> Dict:
    """Validate constitutional compliance across all services."""
    print("🔍 Validating Constitutional Compliance...")
    print(f"Expected Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    
    results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "services": {},
        "compliance_summary": {
            "total_services": 0,
            "compliant_services": 0,
            "non_compliant_services": 0,
            "error_services": 0
        },
        "performance_summary": {
            "services_meeting_p99_target": 0,
            "avg_p99_latency_ms": 0,
            "avg_rps": 0
        }
    }
    
    async with aiohttp.ClientSession() as session:
        # Test each service
        for service_name, service_url in SERVICES.items():
            print(f"\n📊 Testing {service_name}...")
            
            # Health check
            health_result = await test_service_health(session, service_name, service_url)
            
            # Performance test for healthy services
            performance_result = {}
            if health_result.get("status") == "healthy":
                performance_result = await measure_performance(session, service_url, 50)
            
            # Store results
            results["services"][service_name] = {
                "health": health_result,
                "performance": performance_result
            }
            
            # Update summary
            results["compliance_summary"]["total_services"] += 1
            
            if health_result.get("status") == "healthy":
                constitutional_hash = health_result.get("constitutional_hash")
                if constitutional_hash == CONSTITUTIONAL_HASH:
                    results["compliance_summary"]["compliant_services"] += 1
                    print(f"  ✅ Constitutional compliance: PASS")
                else:
                    results["compliance_summary"]["non_compliant_services"] += 1
                    print(f"  ❌ Constitutional compliance: FAIL (got: {constitutional_hash})")
                
                # Check performance
                if performance_result:
                    p99 = performance_result.get("p99_latency_ms", float('inf'))
                    rps = performance_result.get("rps", 0)
                    
                    if p99 <= PERFORMANCE_TARGETS["p99_latency_ms"]:
                        results["performance_summary"]["services_meeting_p99_target"] += 1
                        print(f"  ✅ P99 latency: {p99:.2f}ms (target: <{PERFORMANCE_TARGETS['p99_latency_ms']}ms)")
                    else:
                        print(f"  ❌ P99 latency: {p99:.2f}ms (target: <{PERFORMANCE_TARGETS['p99_latency_ms']}ms)")
                    
                    print(f"  📈 RPS: {rps:.2f} (target: >{PERFORMANCE_TARGETS['min_rps']})")
            else:
                results["compliance_summary"]["error_services"] += 1
                print(f"  ❌ Service health: {health_result.get('status')} - {health_result.get('error', 'Unknown error')}")
    
    return results

async def main():
    """Main validation function."""
    print("🏛️  ACGS Constitutional Compliance Validation")
    print("=" * 60)
    
    results = await validate_constitutional_compliance()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    compliance = results["compliance_summary"]
    performance = results["performance_summary"]
    
    print(f"Total Services Tested: {compliance['total_services']}")
    print(f"✅ Compliant Services: {compliance['compliant_services']}")
    print(f"❌ Non-Compliant Services: {compliance['non_compliant_services']}")
    print(f"🔥 Error Services: {compliance['error_services']}")
    
    compliance_rate = (compliance['compliant_services'] / compliance['total_services']) * 100 if compliance['total_services'] > 0 else 0
    print(f"\n🎯 Constitutional Compliance Rate: {compliance_rate:.1f}%")
    
    if compliance_rate == 100:
        print("🎉 ALL SERVICES ARE CONSTITUTIONALLY COMPLIANT!")
    elif compliance_rate >= 80:
        print("⚠️  Most services are compliant, but some need attention.")
    else:
        print("🚨 CRITICAL: Low compliance rate detected!")
    
    # Performance summary
    p99_target_rate = (performance['services_meeting_p99_target'] / compliance['compliant_services']) * 100 if compliance['compliant_services'] > 0 else 0
    print(f"\n⚡ Performance Target Achievement: {p99_target_rate:.1f}%")
    
    # Save results
    with open("constitutional_compliance_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: constitutional_compliance_report.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
