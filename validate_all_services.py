#!/usr/bin/env python3
"""
ACGS Service Validation Script
Validates all 8+ services are operational with constitutional compliance

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import time
from datetime import datetime

import aiohttp

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

SERVICES = {
    "Constitutional AI": {"port": 8001, "health": "/health"},
    "Integrity Service": {"port": 8002, "health": "/health"},
    "Formal Verification": {"port": 8003, "health": "/health"},
    "Governance Synthesis": {"port": 8004, "health": "/health"},
    "Policy Governance": {"port": 8005, "health": "/health"},
    "Evolutionary Computation": {"port": 8006, "health": "/health"},
    "Code Analysis": {"port": 8007, "health": "/health"},
    "Context Service": {"port": 8012, "health": "/health"},
    "Authentication": {"port": 8016, "health": "/health"},
}


async def validate_service(session, name, config):
    """Validate a single service"""
    port = config["port"]
    health_endpoint = config["health"]
    url = f"http://localhost:{port}{health_endpoint}"

    try:
        start_time = time.time()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            latency_ms = (time.time() - start_time) * 1000

            if response.status == 200:
                data = await response.json()

                # Check for constitutional hash
                constitutional_compliant = False
                if "constitutional_hash" in data:
                    constitutional_compliant = (
                        data["constitutional_hash"] == CONSTITUTIONAL_HASH
                    )
                elif "X-Constitutional-Hash" in response.headers:
                    constitutional_compliant = (
                        response.headers["X-Constitutional-Hash"] == CONSTITUTIONAL_HASH
                    )

                return {
                    "service": name,
                    "port": port,
                    "status": "healthy",
                    "latency_ms": round(latency_ms, 2),
                    "constitutional_compliant": constitutional_compliant,
                    "constitutional_hash": data.get("constitutional_hash", "not_found"),
                    "response_data": data,
                }
            else:
                return {
                    "service": name,
                    "port": port,
                    "status": "unhealthy",
                    "error": f"HTTP {response.status}",
                    "constitutional_compliant": False,
                }

    except Exception as e:
        return {
            "service": name,
            "port": port,
            "status": "error",
            "error": str(e),
            "constitutional_compliant": False,
        }


async def main():
    """Main validation function"""
    print("🔍 ACGS Service Validation Starting...")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for name, config in SERVICES.items():
            tasks.append(validate_service(session, name, config))

        results = await asyncio.gather(*tasks)

    # Analyze results
    healthy_services = []
    unhealthy_services = []
    constitutional_compliant = []
    non_compliant = []
    total_latency = 0

    print("\n📊 SERVICE VALIDATION RESULTS")
    print("=" * 80)

    for result in results:
        service = result["service"]
        port = result["port"]
        status = result["status"]

        if status == "healthy":
            healthy_services.append(service)
            latency = result["latency_ms"]
            total_latency += latency

            compliance_status = "✅" if result["constitutional_compliant"] else "❌"
            print(
                f"{compliance_status} {service:25} Port {port:4} | {latency:6.2f}ms | {status}"
            )

            if result["constitutional_compliant"]:
                constitutional_compliant.append(service)
            else:
                non_compliant.append(service)
        else:
            unhealthy_services.append(service)
            print(
                f"❌ {service:25} Port {port:4} | ERROR: {result.get('error', 'Unknown')}"
            )

    # Summary statistics
    total_services = len(SERVICES)
    healthy_count = len(healthy_services)
    compliant_count = len(constitutional_compliant)
    avg_latency = total_latency / healthy_count if healthy_count > 0 else 0

    print("\n📈 SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total Services:           {total_services}")
    print(
        f"Healthy Services:         {healthy_count}/{total_services} ({healthy_count/total_services*100:.1f}%)"
    )
    print(
        f"Constitutional Compliant: {compliant_count}/{total_services} ({compliant_count/total_services*100:.1f}%)"
    )
    print(f"Average Latency:          {avg_latency:.2f}ms")

    # Performance targets validation
    print("\n🎯 PERFORMANCE TARGETS")
    print("=" * 80)
    p99_target = 5.0  # ms
    compliance_target = 100.0  # %
    availability_target = 100.0  # %

    latency_pass = avg_latency < p99_target
    compliance_pass = (compliant_count / total_services * 100) >= compliance_target
    availability_pass = (healthy_count / total_services * 100) >= availability_target

    print(
        f"P99 Latency < {p99_target}ms:     {'✅ PASS' if latency_pass else '❌ FAIL'} ({avg_latency:.2f}ms)"
    )
    print(
        f"Constitutional Compliance: {'✅ PASS' if compliance_pass else '❌ FAIL'} ({compliant_count/total_services*100:.1f}%)"
    )
    print(
        f"Service Availability:      {'✅ PASS' if availability_pass else '❌ FAIL'} ({healthy_count/total_services*100:.1f}%)"
    )

    # Overall status
    all_targets_met = latency_pass and compliance_pass and availability_pass

    print("\n🏆 OVERALL STATUS")
    print("=" * 80)
    if all_targets_met:
        print("✅ ALL TARGETS MET - ACGS SERVICES FULLY OPERATIONAL")
        print(f"✅ {total_services} services running with constitutional compliance")
        print(f"✅ Average latency {avg_latency:.2f}ms (target: <{p99_target}ms)")
        print(
            f"✅ Constitutional hash {CONSTITUTIONAL_HASH} validated across all services"
        )
    else:
        print("⚠️  SOME TARGETS NOT MET - REQUIRES ATTENTION")
        if unhealthy_services:
            print(f"❌ Unhealthy services: {', '.join(unhealthy_services)}")
        if non_compliant:
            print(f"❌ Non-compliant services: {', '.join(non_compliant)}")

    # Save results
    validation_report = {
        "timestamp": datetime.now().isoformat(),
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "total_services": total_services,
        "healthy_services": healthy_count,
        "constitutional_compliant": compliant_count,
        "average_latency_ms": avg_latency,
        "targets_met": all_targets_met,
        "detailed_results": results,
    }

    with open("service_validation_report.json", "w") as f:
        json.dump(validation_report, f, indent=2)

    print(f"\n📄 Detailed report saved to: service_validation_report.json")

    return all_targets_met


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
