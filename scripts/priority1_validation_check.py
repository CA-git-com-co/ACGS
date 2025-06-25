#!/usr/bin/env python3
"""
Priority 1 Validation Check
Validate that Priority 1 fixes have improved the system score

Tests:
1. All 7 services are accessible
2. Authentication service JWT validation works
3. Missing services (gs, pgc) are operational
4. Constitutional compliance is active
5. Calculate new system score
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Priority1Validator:
    """Priority 1 Fixes Validation System"""
    
    def __init__(self):
        self.services = {
            "auth": {"port": 8000, "name": "Authentication Service"},
            "ac": {"port": 8001, "name": "Constitutional AI Service"},
            "integrity": {"port": 8002, "name": "Integrity Service"},
            "fv": {"port": 8003, "name": "Formal Verification Service"},
            "gs": {"port": 8004, "name": "Governance Synthesis Service"},
            "pgc": {"port": 8005, "name": "Policy Governance & Compliance Service"},
            "ec": {"port": 8006, "name": "Executive Council Service"}
        }
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
    async def test_service_health(self, service_key: str) -> Dict[str, Any]:
        """Test individual service health"""
        service = self.services[service_key]
        url = f"http://localhost:{service['port']}/health"
        
        result = {
            "service": service_key,
            "name": service["name"],
            "port": service["port"],
            "healthy": False,
            "response_time_ms": 0,
            "constitutional_hash_present": False,
            "error": None
        }
        
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                result["response_time_ms"] = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    result["healthy"] = True
                    
                    # Check constitutional hash
                    if response.headers.get("x-constitutional-hash") == self.constitutional_hash:
                        result["constitutional_hash_present"] = True
                else:
                    result["error"] = f"HTTP {response.status_code}"
                    
        except Exception as e:
            result["error"] = str(e)
            result["response_time_ms"] = (time.time() - start_time) * 1000
        
        return result
    
    async def test_authentication_functionality(self) -> Dict[str, Any]:
        """Test authentication service JWT functionality"""
        logger.info("🔐 Testing authentication functionality...")
        
        auth_test = {
            "token_generation": False,
            "token_validation": False,
            "service_accessible": False,
            "errors": []
        }
        
        # Test 1: Service accessibility
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:8000/health")
                if response.status_code == 200:
                    auth_test["service_accessible"] = True
                else:
                    auth_test["errors"].append(f"Health check failed: {response.status_code}")
        except Exception as e:
            auth_test["errors"].append(f"Health check error: {e}")
        
        # Test 2: Token generation
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "http://localhost:8000/api/v1/auth/token",
                    data={"username": "test", "password": "test"},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                if response.status_code == 200:
                    auth_test["token_generation"] = True
                else:
                    auth_test["errors"].append(f"Token generation failed: {response.status_code}")
        except Exception as e:
            auth_test["errors"].append(f"Token generation error: {e}")
        
        # Test 3: Token validation
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "http://localhost:8000/api/v1/auth/validate",
                    json={"token": "test-token"},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    auth_test["token_validation"] = True
                else:
                    auth_test["errors"].append(f"Token validation failed: {response.status_code}")
        except Exception as e:
            auth_test["errors"].append(f"Token validation error: {e}")
        
        return auth_test
    
    async def test_missing_services_functionality(self) -> Dict[str, Any]:
        """Test gs-service and pgc-service functionality"""
        logger.info("🔧 Testing missing services functionality...")
        
        missing_services_test = {
            "gs_service": {"accessible": False, "api_functional": False, "errors": []},
            "pgc_service": {"accessible": False, "api_functional": False, "errors": []}
        }
        
        # Test GS service
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Health check
                response = await client.get("http://localhost:8004/health")
                if response.status_code == 200:
                    missing_services_test["gs_service"]["accessible"] = True
                
                # API functionality
                response = await client.post(
                    "http://localhost:8004/api/v1/synthesize",
                    json={"request": "test"},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    missing_services_test["gs_service"]["api_functional"] = True
                else:
                    missing_services_test["gs_service"]["errors"].append(f"API failed: {response.status_code}")
        except Exception as e:
            missing_services_test["gs_service"]["errors"].append(str(e))
        
        # Test PGC service
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Health check
                response = await client.get("http://localhost:8005/health")
                if response.status_code == 200:
                    missing_services_test["pgc_service"]["accessible"] = True
                
                # API functionality
                response = await client.post(
                    "http://localhost:8005/api/v1/validate",
                    json={"policy": "test"},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    missing_services_test["pgc_service"]["api_functional"] = True
                else:
                    missing_services_test["pgc_service"]["errors"].append(f"API failed: {response.status_code}")
        except Exception as e:
            missing_services_test["pgc_service"]["errors"].append(str(e))
        
        return missing_services_test
    
    async def calculate_new_system_score(self, all_results: Dict[str, Any]) -> float:
        """Calculate new system score after Priority 1 fixes"""
        logger.info("📊 Calculating new system score...")
        
        # Service health scores (40% weight)
        service_health_score = 0
        healthy_services = sum(1 for result in all_results["service_health"].values() if result["healthy"])
        service_health_score = (healthy_services / len(self.services)) * 100
        
        # Authentication functionality (25% weight)
        auth_score = 0
        auth_test = all_results["authentication_test"]
        auth_passed = sum([
            auth_test["service_accessible"],
            auth_test["token_generation"],
            auth_test["token_validation"]
        ])
        auth_score = (auth_passed / 3) * 100
        
        # Missing services functionality (25% weight)
        missing_services_score = 0
        missing_test = all_results["missing_services_test"]
        gs_score = (missing_test["gs_service"]["accessible"] + missing_test["gs_service"]["api_functional"]) / 2
        pgc_score = (missing_test["pgc_service"]["accessible"] + missing_test["pgc_service"]["api_functional"]) / 2
        missing_services_score = ((gs_score + pgc_score) / 2) * 100
        
        # Constitutional compliance (10% weight)
        constitutional_score = 0
        constitutional_services = sum(1 for result in all_results["service_health"].values() if result["constitutional_hash_present"])
        constitutional_score = (constitutional_services / len(self.services)) * 100
        
        # Calculate weighted score
        weighted_score = (
            service_health_score * 0.40 +
            auth_score * 0.25 +
            missing_services_score * 0.25 +
            constitutional_score * 0.10
        )
        
        return weighted_score
    
    async def run_priority1_validation(self) -> Dict[str, Any]:
        """Run comprehensive Priority 1 validation"""
        logger.info("🚀 Starting Priority 1 validation check...")
        
        results = {
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "service_health": {},
            "authentication_test": {},
            "missing_services_test": {},
            "system_score": 0,
            "improvements": {},
            "summary": {}
        }
        
        # Test 1: Service health for all 7 services
        logger.info("🏥 Testing all service health...")
        for service_key in self.services.keys():
            results["service_health"][service_key] = await self.test_service_health(service_key)
        
        # Test 2: Authentication functionality
        results["authentication_test"] = await self.test_authentication_functionality()
        
        # Test 3: Missing services functionality
        results["missing_services_test"] = await self.test_missing_services_functionality()
        
        # Calculate new system score
        results["system_score"] = await self.calculate_new_system_score(results)
        
        # Calculate improvements
        previous_score = 82.3  # From previous comprehensive report
        results["improvements"] = {
            "previous_system_score": previous_score,
            "new_system_score": results["system_score"],
            "improvement": results["system_score"] - previous_score,
            "improvement_percentage": ((results["system_score"] - previous_score) / previous_score) * 100
        }
        
        # Generate summary
        healthy_services = sum(1 for result in results["service_health"].values() if result["healthy"])
        auth_functional = all([
            results["authentication_test"]["service_accessible"],
            results["authentication_test"]["token_generation"],
            results["authentication_test"]["token_validation"]
        ])
        missing_services_functional = all([
            results["missing_services_test"]["gs_service"]["accessible"],
            results["missing_services_test"]["gs_service"]["api_functional"],
            results["missing_services_test"]["pgc_service"]["accessible"],
            results["missing_services_test"]["pgc_service"]["api_functional"]
        ])
        
        results["summary"] = {
            "healthy_services": f"{healthy_services}/{len(self.services)}",
            "authentication_functional": auth_functional,
            "missing_services_functional": missing_services_functional,
            "priority1_success": healthy_services >= 6 and auth_functional and missing_services_functional,
            "production_ready": results["system_score"] >= 90
        }
        
        return results

async def main():
    """Main execution function"""
    validator = Priority1Validator()
    
    try:
        results = await validator.run_priority1_validation()
        
        # Save results
        with open("priority1_validation_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*80)
        print("PRIORITY 1 VALIDATION RESULTS")
        print("="*80)
        print(f"New System Score: {results['system_score']:.1f}%")
        print(f"Previous Score: {results['improvements']['previous_system_score']:.1f}%")
        print(f"Improvement: +{results['improvements']['improvement']:.1f}% ({results['improvements']['improvement_percentage']:+.1f}%)")
        print(f"Constitutional Hash: {results['constitutional_hash']}")
        print("="*80)
        
        # Service health summary
        print(f"\nSERVICE HEALTH ({results['summary']['healthy_services']}):")
        for service_key, health in results["service_health"].items():
            status = "✅" if health["healthy"] else "❌"
            constitutional = "🏛️" if health["constitutional_hash_present"] else "⚪"
            print(f"  {status} {constitutional} {health['name']} (port {health['port']})")
        
        # Authentication test
        auth = results["authentication_test"]
        print(f"\nAUTHENTICATION SERVICE:")
        print(f"  Service Accessible: {'✅' if auth['service_accessible'] else '❌'}")
        print(f"  Token Generation: {'✅' if auth['token_generation'] else '❌'}")
        print(f"  Token Validation: {'✅' if auth['token_validation'] else '❌'}")
        print(f"  Overall: {'✅ FUNCTIONAL' if results['summary']['authentication_functional'] else '❌ ISSUES'}")
        
        # Missing services test
        missing = results["missing_services_test"]
        print(f"\nMISSING SERVICES:")
        print(f"  GS Service: {'✅' if missing['gs_service']['accessible'] and missing['gs_service']['api_functional'] else '❌'}")
        print(f"  PGC Service: {'✅' if missing['pgc_service']['accessible'] and missing['pgc_service']['api_functional'] else '❌'}")
        print(f"  Overall: {'✅ FUNCTIONAL' if results['summary']['missing_services_functional'] else '❌ ISSUES'}")
        
        # Overall status
        print(f"\nOVERALL STATUS:")
        print(f"  Priority 1 Success: {'✅ YES' if results['summary']['priority1_success'] else '❌ NO'}")
        print(f"  Production Ready: {'✅ YES' if results['summary']['production_ready'] else '⚠️ NOT YET'}")
        
        print("="*80)
        
        if results['summary']['priority1_success']:
            print("🎉 Priority 1 fixes completed successfully!")
            if results['summary']['production_ready']:
                print("🚀 System is now PRODUCTION READY!")
            else:
                print("📈 Significant improvement achieved - continue with Priority 2 items")
            return 0
        else:
            print("⚠️ Some Priority 1 issues remain")
            return 1
            
    except Exception as e:
        logger.error(f"Priority 1 validation failed: {e}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
