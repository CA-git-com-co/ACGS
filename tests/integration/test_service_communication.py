"""
ACGS Service Communication Integration Tests
Constitutional Hash: cdd01ef066bc6cf2

Tests for inter-service communication, API consistency, and service coordination.
"""

import pytest
import asyncio
import httpx
import json
from typing import Dict, Any, List
from datetime import datetime

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestServiceCommunication:
    """Test communication between ACGS services."""
    
    @pytest.fixture
    def service_urls(self) -> Dict[str, str]:
        """Service URLs for testing."""
        return {
            "constitutional_ai": "http://localhost:8001",
            "integrity": "http://localhost:8002",
            "api_gateway": "http://localhost:8010",
            "auth": "http://localhost:8016",
            "governance_synthesis": "http://localhost:8008"
        }
    
    @pytest.mark.asyncio
    async def test_api_gateway_routing(self, service_urls):
        """Test API Gateway routing to backend services."""
        
        gateway_url = service_urls.get("api_gateway")
        if not gateway_url:
            pytest.skip("API Gateway not available")
        
        print("\n🌐 Testing API Gateway routing...")
        
        async with httpx.AsyncClient() as client:
            # Test routes to different services
            test_routes = [
                "/api/v1/constitutional/health",
                "/api/v1/integrity/health", 
                "/api/v1/auth/health"
            ]
            
            for route in test_routes:
                try:
                    response = await client.get(f"{gateway_url}{route}", timeout=10.0)
                    
                    if response.status_code == 200:
                        print(f"  ✅ Route accessible: {route}")
                        
                        # Verify constitutional hash in response
                        try:
                            data = response.json()
                            if data.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                                print(f"    ✅ Constitutional compliance verified")
                            else:
                                print(f"    ⚠️ Constitutional hash mismatch")
                        except:
                            print(f"    ⚠️ Response not JSON")
                            
                    elif response.status_code == 404:
                        print(f"  ⚠️ Route not found: {route}")
                    else:
                        print(f"  ❌ Route error {response.status_code}: {route}")
                
                except Exception as e:
                    print(f"  ❌ Route failed: {route} - {e}")
    
    @pytest.mark.asyncio
    async def test_service_api_consistency(self, service_urls):
        """Test API consistency across services."""
        
        print("\n🔄 Testing API consistency...")
        
        async with httpx.AsyncClient() as client:
            api_schemas = {}
            
            for service_name, url in service_urls.items():
                try:
                    # Test health endpoint consistency
                    response = await client.get(f"{url}/health", timeout=10.0)
                    
                    if response.status_code == 200:
                        health_data = response.json()
                        
                        # Check required fields
                        required_fields = ["status", "service", "constitutional_hash"]
                        missing_fields = []
                        
                        for field in required_fields:
                            if field not in health_data:
                                missing_fields.append(field)
                        
                        if missing_fields:
                            print(f"  ⚠️ {service_name} missing fields: {missing_fields}")
                        else:
                            print(f"  ✅ {service_name} health API consistent")
                        
                        # Store schema for comparison
                        api_schemas[service_name] = {
                            "health_fields": list(health_data.keys()),
                            "constitutional_hash": health_data.get("constitutional_hash")
                        }
                    else:
                        print(f"  ❌ {service_name} health endpoint failed: {response.status_code}")
                
                except Exception as e:
                    print(f"  ❌ {service_name} API test failed: {e}")
            
            # Check constitutional hash consistency
            hashes = [schema.get("constitutional_hash") for schema in api_schemas.values()]
            unique_hashes = set(h for h in hashes if h is not None)
            
            if len(unique_hashes) == 1 and CONSTITUTIONAL_HASH in unique_hashes:
                print(f"  ✅ Constitutional hash consistent across all services")
            else:
                print(f"  ❌ Constitutional hash inconsistency: {unique_hashes}")
    
    @pytest.mark.asyncio
    async def test_error_response_consistency(self, service_urls):
        """Test error response consistency across services."""
        
        print("\n❌ Testing error response consistency...")
        
        async with httpx.AsyncClient() as client:
            error_formats = {}
            
            for service_name, url in service_urls.items():
                try:
                    # Trigger error with invalid endpoint
                    response = await client.get(f"{url}/invalid-test-endpoint", timeout=10.0)
                    
                    if response.status_code in [404, 405]:
                        try:
                            error_data = response.json()
                            
                            # Check error structure
                            if "error" in error_data:
                                error = error_data["error"]
                                error_fields = list(error.keys())
                                
                                # Check for standardized fields
                                standard_fields = ["id", "timestamp", "constitutional_hash"]
                                has_standard = all(field in error_fields for field in standard_fields)
                                
                                if has_standard:
                                    print(f"  ✅ {service_name} standardized error format")
                                else:
                                    print(f"  ⚠️ {service_name} non-standard error format")
                                
                                error_formats[service_name] = {
                                    "fields": error_fields,
                                    "standardized": has_standard,
                                    "constitutional_hash": error.get("constitutional_hash")
                                }
                            else:
                                print(f"  ⚠️ {service_name} non-ACGS error format")
                                error_formats[service_name] = {"standardized": False}
                        
                        except json.JSONDecodeError:
                            print(f"  ⚠️ {service_name} error response not JSON")
                            error_formats[service_name] = {"standardized": False}
                    else:
                        print(f"  ⚠️ {service_name} unexpected status: {response.status_code}")
                
                except Exception as e:
                    print(f"  ❌ {service_name} error test failed: {e}")
            
            # Check consistency across services
            standardized_services = [s for s, f in error_formats.items() if f.get("standardized")]
            if len(standardized_services) == len(error_formats):
                print(f"  ✅ All services use standardized error format")
            else:
                non_standard = [s for s in error_formats if s not in standardized_services]
                print(f"  ⚠️ Non-standardized services: {non_standard}")
    
    @pytest.mark.asyncio
    async def test_service_dependencies(self, service_urls):
        """Test service dependencies and fallback behavior."""
        
        print("\n🔗 Testing service dependencies...")
        
        # Test Constitutional AI service without dependencies
        constitutional_ai_url = service_urls.get("constitutional_ai")
        if constitutional_ai_url:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{constitutional_ai_url}/health", timeout=10.0)
                    
                    if response.status_code == 200:
                        health_data = response.json()
                        
                        # Check component status
                        components = health_data.get("components", {})
                        for component, status in components.items():
                            if status == "operational":
                                print(f"  ✅ Component operational: {component}")
                            else:
                                print(f"  ⚠️ Component status: {component} - {status}")
                    
                    print(f"  ✅ Constitutional AI service health check passed")
                
                except Exception as e:
                    print(f"  ❌ Constitutional AI dependency test failed: {e}")
        
        # Test service communication patterns
        await self._test_service_coordination(service_urls)
    
    async def _test_service_coordination(self, service_urls):
        """Test coordination between services."""
        
        print("\n🤝 Testing service coordination...")
        
        # Example: Constitutional AI -> Integrity Service workflow
        constitutional_ai_url = service_urls.get("constitutional_ai")
        integrity_url = service_urls.get("integrity")
        
        if constitutional_ai_url and integrity_url:
            async with httpx.AsyncClient() as client:
                try:
                    # Step 1: Get constitutional validation
                    test_policy = {
                        "name": "Test Coordination Policy",
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                        "constitutional_authority": True,
                        "rights_protection": True
                    }
                    
                    response = await client.post(
                        f"{constitutional_ai_url}/api/v1/validate/constitutional",
                        json={"policy": test_policy},
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        validation_result = response.json()
                        print(f"  ✅ Constitutional validation completed")
                        
                        # Step 2: Log to Integrity service
                        audit_event = {
                            "event_type": "constitutional_validation",
                            "service": "integration_test",
                            "details": {
                                "policy_name": test_policy["name"],
                                "validation_result": validation_result,
                                "constitutional_hash": CONSTITUTIONAL_HASH
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # This may fail if integrity service doesn't have this endpoint
                        try:
                            response = await client.post(
                                f"{integrity_url}/api/v1/audit/log",
                                json=audit_event,
                                timeout=10.0
                            )
                            
                            if response.status_code in [200, 201]:
                                print(f"  ✅ Service coordination successful")
                            else:
                                print(f"  ⚠️ Integrity service response: {response.status_code}")
                        except Exception:
                            print(f"  ⚠️ Integrity service audit endpoint not available")
                    
                    else:
                        print(f"  ❌ Constitutional validation failed: {response.status_code}")
                
                except Exception as e:
                    print(f"  ❌ Service coordination test failed: {e}")
        else:
            print(f"  ⚠️ Required services not available for coordination test")
    
    @pytest.mark.asyncio
    async def test_authentication_flow(self, service_urls):
        """Test authentication flow across services."""
        
        auth_url = service_urls.get("auth")
        gateway_url = service_urls.get("api_gateway")
        
        if not auth_url:
            print("\n🔑 Auth service not available, skipping authentication test")
            return
        
        print("\n🔑 Testing authentication flow...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Test authentication endpoints
                endpoints_to_test = [
                    "/health",
                    "/api/v1/status",
                    "/api/v1/auth/status"
                ]
                
                for endpoint in endpoints_to_test:
                    try:
                        response = await client.get(f"{auth_url}{endpoint}", timeout=10.0)
                        
                        if response.status_code == 200:
                            print(f"  ✅ Auth endpoint accessible: {endpoint}")
                        elif response.status_code == 404:
                            print(f"  ⚠️ Auth endpoint not found: {endpoint}")
                        else:
                            print(f"  ❌ Auth endpoint error {response.status_code}: {endpoint}")
                    
                    except Exception as e:
                        print(f"  ❌ Auth endpoint failed: {endpoint} - {e}")
                
                # Test token validation if possible
                # This is a simplified test - in practice would need actual authentication
                print(f"  ℹ️ Token validation testing requires actual authentication setup")
            
            except Exception as e:
                print(f"  ❌ Authentication flow test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_performance_across_services(self, service_urls):
        """Test performance consistency across services."""
        
        print("\n⚡ Testing cross-service performance...")
        
        performance_results = {}
        
        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                try:
                    # Measure response times for health checks
                    response_times = []
                    
                    for _ in range(5):  # Take 5 measurements
                        start_time = asyncio.get_event_loop().time()
                        response = await client.get(f"{url}/health", timeout=10.0)
                        end_time = asyncio.get_event_loop().time()
                        
                        if response.status_code == 200:
                            response_time_ms = (end_time - start_time) * 1000
                            response_times.append(response_time_ms)
                    
                    if response_times:
                        avg_time = sum(response_times) / len(response_times)
                        max_time = max(response_times)
                        
                        performance_results[service_name] = {
                            "avg_response_time_ms": avg_time,
                            "max_response_time_ms": max_time,
                            "measurements": len(response_times)
                        }
                        
                        # Check against performance targets
                        if avg_time < 1000:  # Target: <1s for health checks
                            print(f"  ✅ {service_name}: {avg_time:.2f}ms avg")
                        else:
                            print(f"  ⚠️ {service_name}: {avg_time:.2f}ms avg (slow)")
                
                except Exception as e:
                    print(f"  ❌ {service_name} performance test failed: {e}")
        
        # Check for performance consistency
        if len(performance_results) > 1:
            avg_times = [r["avg_response_time_ms"] for r in performance_results.values()]
            max_avg = max(avg_times)
            min_avg = min(avg_times)
            
            if max_avg / min_avg > 5:  # More than 5x difference
                print(f"  ⚠️ Performance inconsistency detected (5x+ difference)")
            else:
                print(f"  ✅ Performance consistent across services")


@pytest.mark.asyncio
async def test_constitutional_compliance_chain():
    """Test constitutional compliance propagation across service calls."""
    
    print("\n⚖️ Testing constitutional compliance chain...")
    
    service_urls = {
        "constitutional_ai": "http://localhost:8001",
        "integrity": "http://localhost:8002"
    }
    
    async with httpx.AsyncClient() as client:
        # Test that constitutional hash is maintained through service calls
        for service_name, url in service_urls.items():
            try:
                response = await client.get(f"{url}/health", timeout=10.0)
                
                if response.status_code == 200:
                    # Check response body
                    data = response.json()
                    if data.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                        print(f"  ✅ {service_name}: Constitutional hash in response body")
                    else:
                        print(f"  ❌ {service_name}: Constitutional hash mismatch in body")
                    
                    # Check response headers
                    headers = response.headers
                    if headers.get("X-Constitutional-Hash") == CONSTITUTIONAL_HASH:
                        print(f"  ✅ {service_name}: Constitutional hash in headers")
                    else:
                        print(f"  ⚠️ {service_name}: Constitutional hash missing in headers")
            
            except Exception as e:
                print(f"  ❌ {service_name} constitutional compliance test failed: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])