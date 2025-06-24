#!/usr/bin/env python3
"""
ACGS-1 Service Status Checker
Check the health and status of all 7 core services
"""

import requests
import json
import time
from typing import Dict, List, Any

# Service definitions
SERVICES = [
    {"name": "auth_service", "port": 8000, "description": "Authentication Service"},
    {"name": "ac_service", "port": 8001, "description": "Constitutional AI Service"},
    {"name": "integrity_service", "port": 8002, "description": "Integrity Service"},
    {"name": "fv_service", "port": 8003, "description": "Formal Verification Service"},
    {"name": "gs_service", "port": 8004, "description": "Governance Synthesis Service"},
    {"name": "pgc_service", "port": 8005, "description": "Policy Governance Service"},
    {"name": "ec_service", "port": 8006, "description": "Evolutionary Computation Service"},
]

def check_service_health(service: Dict[str, Any]) -> Dict[str, Any]:
    """Check the health of a single service."""
    name = service["name"]
    port = service["port"]
    description = service["description"]
    
    result = {
        "name": name,
        "port": port,
        "description": description,
        "status": "unknown",
        "response_time_ms": None,
        "health_data": None,
        "error": None
    }
    
    try:
        start_time = time.time()
        
        # Try health endpoint first
        health_url = f"http://localhost:{port}/health"
        response = requests.get(health_url, timeout=5)
        
        response_time = (time.time() - start_time) * 1000
        result["response_time_ms"] = round(response_time, 2)
        
        if response.status_code == 200:
            result["status"] = "healthy"
            try:
                result["health_data"] = response.json()
            except:
                result["health_data"] = {"raw_response": response.text[:200]}
        else:
            result["status"] = "unhealthy"
            result["error"] = f"HTTP {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        result["status"] = "not_running"
        result["error"] = "Connection refused"
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "Request timeout"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def check_all_services() -> List[Dict[str, Any]]:
    """Check the health of all services."""
    results = []
    
    print("🔍 Checking ACGS-1 Service Health...")
    print("=" * 60)
    
    for service in SERVICES:
        print(f"Checking {service['name']} on port {service['port']}...", end=" ")
        result = check_service_health(service)
        results.append(result)
        
        # Print status with color coding
        status = result["status"]
        if status == "healthy":
            print(f"✅ {status} ({result['response_time_ms']}ms)")
        elif status == "not_running":
            print(f"❌ {status}")
        else:
            print(f"⚠️ {status} - {result.get('error', 'Unknown error')}")
    
    return results

def print_summary(results: List[Dict[str, Any]]):
    """Print a summary of service health."""
    print("\n" + "=" * 60)
    print("📊 ACGS-1 Service Health Summary")
    print("=" * 60)
    
    healthy = [r for r in results if r["status"] == "healthy"]
    not_running = [r for r in results if r["status"] == "not_running"]
    unhealthy = [r for r in results if r["status"] not in ["healthy", "not_running"]]
    
    print(f"✅ Healthy Services: {len(healthy)}/{len(results)}")
    print(f"❌ Not Running: {len(not_running)}")
    print(f"⚠️ Unhealthy: {len(unhealthy)}")
    
    if healthy:
        print(f"\n🟢 Healthy Services:")
        for service in healthy:
            version = "unknown"
            if service["health_data"] and isinstance(service["health_data"], dict):
                version = service["health_data"].get("version", "unknown")
            print(f"   • {service['name']} (port {service['port']}) - v{version}")
    
    if not_running:
        print(f"\n🔴 Not Running:")
        for service in not_running:
            print(f"   • {service['name']} (port {service['port']})")
    
    if unhealthy:
        print(f"\n🟡 Unhealthy:")
        for service in unhealthy:
            print(f"   • {service['name']} (port {service['port']}) - {service['error']}")

def check_constitution_hash():
    """Check if the constitution hash is preserved across services."""
    print(f"\n🔐 Checking Constitution Hash Preservation...")
    print("=" * 60)
    
    target_hash = "cdd01ef066bc6cf2"
    services_with_hash = []
    
    for service in SERVICES:
        try:
            # Try different endpoints that might have the hash
            endpoints = [
                f"http://localhost:{service['port']}/",
                f"http://localhost:{service['port']}/health",
                f"http://localhost:{service['port']}/api/v1/constitutional/validate"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=3)
                    if response.status_code == 200:
                        # Check both response text and headers
                        response_text = response.text.lower()
                        headers_text = str(response.headers).lower()

                        if target_hash in response_text or target_hash in headers_text:
                            services_with_hash.append(service['name'])
                            location = "headers" if target_hash in headers_text else "response"
                            print(f"✅ {service['name']} - Constitution hash found in {location}")
                            break
                except:
                    continue
            else:
                print(f"❌ {service['name']} - Constitution hash not found or service not responding")
                
        except Exception as e:
            print(f"⚠️ {service['name']} - Error checking hash: {e}")
    
    print(f"\n📊 Constitution Hash Summary:")
    print(f"   Services with hash: {len(services_with_hash)}/{len(SERVICES)}")
    print(f"   Target hash: {target_hash}")

if __name__ == "__main__":
    # Check all services
    results = check_all_services()
    
    # Print summary
    print_summary(results)
    
    # Check constitution hash
    check_constitution_hash()
    
    # Save results to file
    with open("service_health_report.json", "w") as f:
        json.dump({
            "timestamp": time.time(),
            "results": results,
            "summary": {
                "total_services": len(results),
                "healthy": len([r for r in results if r["status"] == "healthy"]),
                "not_running": len([r for r in results if r["status"] == "not_running"]),
                "unhealthy": len([r for r in results if r["status"] not in ["healthy", "not_running"]])
            }
        }, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: service_health_report.json")
