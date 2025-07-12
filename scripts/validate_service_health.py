#!/usr/bin/env python3
"""
ACGS Service Health Validation Script

This script validates the health status of all core ACGS services
and provides a comprehensive status report.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import subprocess
from typing import Dict, List
import aiohttp

# Expected constitutional hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Core ACGS services and their expected ports
CORE_SERVICES = {
    "api_gateway": {"port": 8010, "path": "/health"},
    "constitutional_core": {"port": 32768, "path": "/health"},  # Dynamic port
    "auth_service": {"port": 8008, "path": "/health"},
    "code_analysis_engine": {"port": 8107, "path": "/health"},
}

# Additional services to check
ADDITIONAL_SERVICES = {
    "postgres": {"port": 5439, "type": "database"},
    "redis": {"port": 6389, "type": "cache"},
    "opa": {"port": 8181, "path": "/health"},
    "prometheus": {"port": 9091, "path": "/api/v1/query?query=up"},
    "grafana": {"port": 3001, "path": "/api/health"},
}

def get_docker_containers() -> List[Dict]:
    """Get status of all ACGS Docker containers."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json", "--filter", "name=acgs"],
            capture_output=True,
            text=True,
            check=True
        )
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))
        
        return containers
    except subprocess.CalledProcessError as e:
        print(f"Error getting Docker containers: {e}")
        return []

async def test_http_service(session: aiohttp.ClientSession, name: str, port: int, path: str = "/health") -> Dict:
    """Test an HTTP service endpoint."""
    url = f"http://localhost:{port}{path}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    constitutional_hash = data.get("constitutional_hash")
                    return {
                        "service": name,
                        "status": "healthy",
                        "port": port,
                        "constitutional_hash": constitutional_hash,
                        "constitutional_compliant": constitutional_hash == CONSTITUTIONAL_HASH,
                        "response": data
                    }
                except:
                    return {
                        "service": name,
                        "status": "healthy",
                        "port": port,
                        "constitutional_hash": None,
                        "constitutional_compliant": False,
                        "note": "Non-JSON response"
                    }
            else:
                return {
                    "service": name,
                    "status": "unhealthy",
                    "port": port,
                    "error": f"HTTP {response.status}"
                }
    except Exception as e:
        return {
            "service": name,
            "status": "error",
            "port": port,
            "error": str(e)
        }

async def test_tcp_service(name: str, port: int) -> Dict:
    """Test a TCP service (like database or cache)."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection('localhost', port),
            timeout=5.0
        )
        writer.close()
        await writer.wait_closed()
        
        return {
            "service": name,
            "status": "healthy",
            "port": port,
            "type": "tcp"
        }
    except Exception as e:
        return {
            "service": name,
            "status": "error",
            "port": port,
            "error": str(e),
            "type": "tcp"
        }

async def validate_all_services() -> Dict:
    """Validate all ACGS services."""
    print("🏥 ACGS Service Health Validation")
    print("=" * 60)
    
    results = {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "docker_containers": get_docker_containers(),
        "core_services": {},
        "additional_services": {},
        "summary": {
            "total_core_services": len(CORE_SERVICES),
            "healthy_core_services": 0,
            "constitutional_compliant_services": 0,
            "total_containers": 0,
            "running_containers": 0,
            "healthy_containers": 0
        }
    }
    
    # Analyze Docker containers
    print("\n🐳 Docker Container Status:")
    for container in results["docker_containers"]:
        name = container.get("Names", "unknown")
        status = container.get("Status", "unknown")
        state = container.get("State", "unknown")
        
        results["summary"]["total_containers"] += 1
        if state == "running":
            results["summary"]["running_containers"] += 1
        if "healthy" in status.lower():
            results["summary"]["healthy_containers"] += 1
            
        print(f"  {name}: {status} ({state})")
    
    # Test core services
    print(f"\n🔧 Core Services Health Check:")
    async with aiohttp.ClientSession() as session:
        for service_name, config in CORE_SERVICES.items():
            print(f"\n  Testing {service_name}...")
            
            result = await test_http_service(
                session, 
                service_name, 
                config["port"], 
                config["path"]
            )
            
            results["core_services"][service_name] = result
            
            if result["status"] == "healthy":
                results["summary"]["healthy_core_services"] += 1
                print(f"    ✅ Status: {result['status']}")
                
                if result.get("constitutional_compliant"):
                    results["summary"]["constitutional_compliant_services"] += 1
                    print(f"    ✅ Constitutional compliance: PASS")
                else:
                    print(f"    ❌ Constitutional compliance: FAIL")
            else:
                print(f"    ❌ Status: {result['status']} - {result.get('error', 'Unknown error')}")
    
    # Test additional services
    print(f"\n🔌 Additional Services:")
    async with aiohttp.ClientSession() as session:
        for service_name, config in ADDITIONAL_SERVICES.items():
            print(f"\n  Testing {service_name}...")
            
            if config.get("type") in ["database", "cache"]:
                result = await test_tcp_service(service_name, config["port"])
            else:
                result = await test_http_service(
                    session,
                    service_name,
                    config["port"],
                    config.get("path", "/health")
                )
            
            results["additional_services"][service_name] = result
            
            if result["status"] == "healthy":
                print(f"    ✅ Status: {result['status']}")
            else:
                print(f"    ❌ Status: {result['status']} - {result.get('error', 'Unknown error')}")
    
    return results

async def main():
    """Main validation function."""
    results = await validate_all_services()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 HEALTH VALIDATION SUMMARY")
    print("=" * 60)
    
    summary = results["summary"]
    
    print(f"Docker Containers:")
    print(f"  Total: {summary['total_containers']}")
    print(f"  Running: {summary['running_containers']}")
    print(f"  Healthy: {summary['healthy_containers']}")
    
    print(f"\nCore Services:")
    print(f"  Total: {summary['total_core_services']}")
    print(f"  Healthy: {summary['healthy_core_services']}")
    print(f"  Constitutional Compliant: {summary['constitutional_compliant_services']}")
    
    # Calculate health percentages
    core_health_rate = (summary['healthy_core_services'] / summary['total_core_services']) * 100 if summary['total_core_services'] > 0 else 0
    compliance_rate = (summary['constitutional_compliant_services'] / summary['healthy_core_services']) * 100 if summary['healthy_core_services'] > 0 else 0
    
    print(f"\n🎯 Core Service Health Rate: {core_health_rate:.1f}%")
    print(f"🏛️  Constitutional Compliance Rate: {compliance_rate:.1f}%")
    
    if core_health_rate == 100 and compliance_rate == 100:
        print("\n🎉 ALL CORE SERVICES ARE HEALTHY AND CONSTITUTIONALLY COMPLIANT!")
    elif core_health_rate >= 75:
        print("\n✅ Most core services are healthy.")
    else:
        print("\n🚨 CRITICAL: Multiple core services are unhealthy!")
    
    # Save results
    with open("service_health_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: service_health_report.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
