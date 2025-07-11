#!/usr/bin/env python3
"""
Quick performance check for ACGS-2 services
Constitutional Hash: cdd01ef066bc6cf2

Runs a shorter test (60 seconds) to quickly validate service performance
"""

import asyncio
import aiohttp
import time
import statistics
from typing import Dict, List

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

SERVICE_ENDPOINTS = {
    "constitutional_ai": "http://localhost:32768",
    "auth_service": "http://localhost:8016", 
    "agent_hitl": "http://localhost:8008",
}

async def quick_load_test(service_name: str, service_url: str, duration: int = 60, concurrent: int = 50):
    """Run a quick load test against a service"""
    
    print(f"\n🚀 Testing {service_name}")
    print(f"   Duration: {duration}s, Concurrent users: {concurrent}")
    
    latencies = []
    successful = 0
    failed = 0
    constitutional_compliant = 0
    start_time = time.perf_counter()
    
    async def user_session():
        """Single user session"""
        session_latencies = []
        async with aiohttp.ClientSession() as session:
            while (time.perf_counter() - start_time) < duration:
                try:
                    request_start = time.perf_counter()
                    async with session.get(f"{service_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                        latency_ms = (time.perf_counter() - request_start) * 1000
                        session_latencies.append(latency_ms)
                        
                        if response.status == 200:
                            # Check constitutional compliance
                            try:
                                data = await response.json()
                                if data.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                                    return True, session_latencies
                            except:
                                text = await response.text()
                                if CONSTITUTIONAL_HASH in text:
                                    return True, session_latencies
                except:
                    pass
                await asyncio.sleep(0.05)  # 50ms between requests
        return False, session_latencies
    
    # Run concurrent sessions
    tasks = [user_session() for _ in range(concurrent)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for result in results:
        if isinstance(result, tuple):
            compliant, session_latencies = result
            latencies.extend(session_latencies)
            if compliant:
                constitutional_compliant += 1
    
    # Calculate metrics
    if latencies:
        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        throughput = len(latencies) / duration
    else:
        avg_latency = p99_latency = throughput = 0
    
    print(f"   ✅ Results:")
    print(f"      Requests: {len(latencies)}")
    print(f"      Avg Latency: {avg_latency:.1f}ms")
    print(f"      P99 Latency: {p99_latency:.1f}ms")
    print(f"      Throughput: {throughput:.1f} RPS")
    print(f"      Constitutional Compliance: {constitutional_compliant}/{concurrent}")
    
    return {
        "service": service_name,
        "requests": len(latencies),
        "avg_latency_ms": avg_latency,
        "p99_latency_ms": p99_latency,
        "throughput_rps": throughput,
        "compliance_rate": constitutional_compliant / concurrent if concurrent > 0 else 0
    }

async def main():
    """Run quick performance check"""
    print("=" * 80)
    print("🎯 ACGS-2 Quick Performance Check")
    print("=" * 80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Check service availability
    available_services = []
    for name, url in SERVICE_ENDPOINTS.items():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        available_services.append((name, url))
                        print(f"✅ {name} is available")
                    else:
                        print(f"❌ {name} returned status {response.status}")
        except Exception as e:
            print(f"❌ {name} is unavailable: {type(e).__name__}")
    
    if not available_services:
        print("\n❌ No services available for testing")
        return
    
    # Run quick tests
    print("\n📊 Running quick performance tests...")
    
    results = []
    for name, url in available_services:
        result = await quick_load_test(name, url, duration=60, concurrent=50)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 PERFORMANCE SUMMARY")
    print("=" * 80)
    
    total_throughput = sum(r["throughput_rps"] for r in results)
    avg_compliance = statistics.mean([r["compliance_rate"] for r in results]) if results else 0
    
    print(f"Total System Throughput: {total_throughput:.1f} RPS")
    print(f"Average Constitutional Compliance: {avg_compliance:.1%}")
    
    print("\nPer-Service Performance:")
    for r in results:
        status = "✅" if r["p99_latency_ms"] < 5.0 else "⚠️"
        print(f"  {status} {r['service']}: {r['throughput_rps']:.1f} RPS, P99: {r['p99_latency_ms']:.1f}ms")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if all(r["p99_latency_ms"] < 5.0 for r in results):
        print("  ✅ All services meeting P99 <5ms target")
    else:
        print("  ⚠️  Some services exceed P99 5ms target under load")
        print("  📌 Enable horizontal scaling as configured in production prompts")
    
    if any(r["throughput_rps"] < 100 for r in results):
        print("  ⚠️  Low throughput detected - check service health")
    
    if avg_compliance < 1.0:
        print("  ❌ Constitutional compliance below 100% - investigate immediately")

if __name__ == "__main__":
    asyncio.run(main())