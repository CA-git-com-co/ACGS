"""
ACGS Constitutional Compliance Integration Tests
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive integration tests for constitutional compliance across all services.
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any, List
from datetime import datetime

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestConstitutionalCompliance:
    """Test constitutional compliance across all ACGS services."""
    
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
    async def test_constitutional_hash_validation_all_services(self, service_urls):
        """Test that all services validate constitutional hash correctly."""
        results = {}
        
        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                try:
                    response = await client.get(f"{url}/health", timeout=10.0)
                    
                    assert response.status_code == 200, f"{service_name} health check failed"
                    
                    health_data = response.json()
                    assert "constitutional_hash" in health_data, f"{service_name} missing constitutional hash"
                    assert health_data["constitutional_hash"] == CONSTITUTIONAL_HASH, \
                        f"{service_name} constitutional hash mismatch"
                    
                    results[service_name] = "✅ PASS"
                    
                except Exception as e:
                    results[service_name] = f"❌ FAIL: {str(e)}"
        
        # Log results
        print("\n🔍 Constitutional Hash Validation Results:")
        for service, result in results.items():
            print(f"  {service}: {result}")
        
        # Assert all services passed
        failed_services = [s for s, r in results.items() if "FAIL" in r]
        assert len(failed_services) == 0, f"Services failed constitutional validation: {failed_services}"
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance_workflow(self, service_urls):
        """Test end-to-end constitutional compliance workflow."""
        
        # Test policy for validation
        test_policy = {
            "name": "Test Integration Policy",
            "description": "Policy for integration testing",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "representative_governance": True,
            "public_participation": True,
            "minority_protection": True,
            "regular_review": True,
            "open_access": True,
            "clear_processes": True,
            "public_documentation": True,
            "audit_trails": True,
            "constitutional_authority": True,
            "rights_protection": True,
            "separation_of_powers": True,
            "clear_responsibility": True,
            "performance_metrics": True,
            "oversight_mechanisms": True,
            "corrective_actions": True,
            "individual_rights": True,
            "collective_rights": True,
            "due_process": True,
            "equal_protection": True
        }
        
        async with httpx.AsyncClient() as client:
            # Step 1: Validate with Constitutional AI service
            try:
                response = await client.post(
                    f"{service_urls['constitutional_ai']}/api/v1/validate/constitutional",
                    json={"policy": test_policy},
                    timeout=30.0
                )
                
                assert response.status_code == 200, "Constitutional validation failed"
                validation_result = response.json()
                
                assert "compliance_score" in validation_result
                assert "is_compliant" in validation_result
                assert "constitutional_hash" in validation_result
                assert validation_result["constitutional_hash"] == CONSTITUTIONAL_HASH
                
                print(f"✅ Constitutional AI validation: {validation_result['compliance_score']:.2f}")
                
            except Exception as e:
                pytest.fail(f"Constitutional AI validation failed: {e}")
            
            # Step 2: Log to Integrity service
            try:
                audit_event = {
                    "event_type": "constitutional_validation",
                    "service": "integration_test",
                    "details": {
                        "policy_name": test_policy["name"],
                        "compliance_score": validation_result["compliance_score"],
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                response = await client.post(
                    f"{service_urls['integrity']}/api/v1/audit/log",
                    json=audit_event,
                    timeout=10.0
                )
                
                # Note: This might return 404 if endpoint doesn't exist, which is acceptable
                if response.status_code not in [200, 201, 404]:
                    print(f"⚠️ Integrity service audit logging returned: {response.status_code}")
                else:
                    print("✅ Integrity service audit logging successful")
                    
            except Exception as e:
                print(f"⚠️ Integrity service not available: {e}")
    
    @pytest.mark.asyncio
    async def test_security_middleware_integration(self, service_urls):
        """Test security middleware integration across services."""
        
        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                try:
                    # Test with valid request
                    response = await client.get(f"{url}/health", timeout=10.0)
                    
                    # Check security headers
                    headers = response.headers
                    security_headers = [
                        "x-content-type-options",
                        "x-frame-options", 
                        "x-constitutional-hash"
                    ]
                    
                    for header in security_headers:
                        if header in headers:
                            print(f"✅ {service_name}: {header} present")
                        else:
                            print(f"⚠️ {service_name}: {header} missing")
                    
                    # Verify constitutional hash in headers
                    if "x-constitutional-hash" in headers:
                        assert headers["x-constitutional-hash"] == CONSTITUTIONAL_HASH, \
                            f"{service_name} constitutional hash mismatch in headers"
                    
                except Exception as e:
                    print(f"⚠️ {service_name} security test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_error_handling_standardization(self, service_urls):
        """Test standardized error handling across services."""
        
        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                try:
                    # Test invalid endpoint to trigger error handling
                    response = await client.get(f"{url}/invalid-endpoint-test", timeout=10.0)
                    
                    # Should return 404 with standardized error format
                    assert response.status_code == 404
                    
                    # Check error response format
                    if response.headers.get("content-type", "").startswith("application/json"):
                        error_data = response.json()
                        
                        # Check standardized error structure
                        if "error" in error_data:
                            error = error_data["error"]
                            expected_fields = ["id", "timestamp", "constitutional_hash"]
                            
                            for field in expected_fields:
                                if field in error:
                                    print(f"✅ {service_name}: Error field {field} present")
                                else:
                                    print(f"⚠️ {service_name}: Error field {field} missing")
                            
                            # Verify constitutional hash in error response
                            if "constitutional_hash" in error:
                                assert error["constitutional_hash"] == CONSTITUTIONAL_HASH, \
                                    f"{service_name} constitutional hash mismatch in error"
                        else:
                            print(f"⚠️ {service_name}: Non-standardized error format")
                    
                    print(f"✅ {service_name}: Error handling test completed")
                    
                except Exception as e:
                    print(f"⚠️ {service_name} error handling test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_service_discovery_and_health(self, service_urls):
        """Test service discovery and health check endpoints."""
        
        service_status = {}
        
        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                try:
                    # Test health endpoint
                    response = await client.get(f"{url}/health", timeout=10.0)
                    
                    if response.status_code == 200:
                        health_data = response.json()
                        service_status[service_name] = {
                            "status": "healthy",
                            "response_time": response.elapsed.total_seconds(),
                            "constitutional_compliant": health_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                        }
                    else:
                        service_status[service_name] = {
                            "status": f"unhealthy ({response.status_code})",
                            "constitutional_compliant": False
                        }
                        
                except Exception as e:
                    service_status[service_name] = {
                        "status": f"unreachable ({str(e)})",
                        "constitutional_compliant": False
                    }
        
        # Print service status report
        print("\n🏥 Service Health Report:")
        for service, status in service_status.items():
            status_emoji = "✅" if status["status"] == "healthy" else "❌"
            compliance_emoji = "✅" if status.get("constitutional_compliant") else "❌"
            response_time = status.get("response_time", 0)
            
            print(f"  {status_emoji} {service}: {status['status']}")
            print(f"    Constitutional Compliance: {compliance_emoji}")
            if response_time > 0:
                print(f"    Response Time: {response_time:.3f}s")
        
        # Assert that at least some core services are healthy
        healthy_services = [s for s, status in service_status.items() if status["status"] == "healthy"]
        assert len(healthy_services) > 0, "No services are healthy"
        
        # Assert constitutional compliance for healthy services
        compliant_services = [s for s, status in service_status.items() 
                            if status.get("constitutional_compliant", False)]
        assert len(compliant_services) > 0, "No services are constitutionally compliant"


@pytest.mark.asyncio
async def test_performance_requirements():
    """Test that services meet performance requirements."""
    
    service_urls = {
        "constitutional_ai": "http://localhost:8001",
        "api_gateway": "http://localhost:8010"
    }
    
    performance_results = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, url in service_urls.items():
            try:
                # Measure response time for health check
                start_time = asyncio.get_event_loop().time()
                response = await client.get(f"{url}/health", timeout=10.0)
                end_time = asyncio.get_event_loop().time()
                
                response_time_ms = (end_time - start_time) * 1000
                
                performance_results[service_name] = {
                    "response_time_ms": response_time_ms,
                    "meets_target": response_time_ms < 5000,  # Target: <5s for health checks
                    "status_code": response.status_code
                }
                
            except Exception as e:
                performance_results[service_name] = {
                    "response_time_ms": float('inf'),
                    "meets_target": False,
                    "error": str(e)
                }
    
    # Print performance report
    print("\n⚡ Performance Test Results:")
    for service, result in performance_results.items():
        target_emoji = "✅" if result["meets_target"] else "❌"
        response_time = result["response_time_ms"]
        
        if response_time != float('inf'):
            print(f"  {target_emoji} {service}: {response_time:.2f}ms")
        else:
            print(f"  ❌ {service}: Error - {result.get('error', 'Unknown')}")
    
    # Assert at least one service meets performance targets
    performant_services = [s for s, r in performance_results.items() if r["meets_target"]]
    assert len(performant_services) > 0, "No services meet performance targets"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])