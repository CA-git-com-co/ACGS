"""
ACGS-1 Comprehensive Integration Test Suite
Tests all service integrations and workflows
"""

import asyncio
import json
import pytest
import httpx
from typing import Dict, Any, List
import time

# Test configuration
TEST_CONFIG = {
    "services": {
        "auth_service": {"url": "http://localhost:8000", "timeout": 30},
        "ac_service": {"url": "http://localhost:8001", "timeout": 30},
        "integrity_service": {"url": "http://localhost:8002", "timeout": 30},
        "fv_service": {"url": "http://localhost:8003", "timeout": 30},
        "gs_service": {"url": "http://localhost:8004", "timeout": 30},
        "pgc_service": {"url": "http://localhost:8005", "timeout": 30},
        "ec_service": {"url": "http://localhost:8006", "timeout": 30},
        "workflow_service": {"url": "http://localhost:9007", "timeout": 30},
        "blockchain_bridge": {"url": "http://localhost:9008", "timeout": 30},
        "performance_optimizer": {"url": "http://localhost:9009", "timeout": 30},
        "external_apis": {"url": "http://localhost:9010", "timeout": 30},
    },
    "test_data": {
        "test_policy": {
            "title": "Test Constitutional Policy",
            "description": "Test policy for integration testing",
            "content": "This is a test policy for constitutional compliance validation"
        },
        "test_user": {
            "username": "test_user",
            "email": "test@acgs.local",
            "role": "council_member"
        }
    }
}


class ACGSIntegrationTester:
    """Comprehensive integration tester for ACGS services."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.test_results = {}
        self.service_health = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def check_service_health(self, service_name: str, service_config: Dict[str, Any]) -> bool:
        """Check if a service is healthy."""
        try:
            response = await self.http_client.get(
                f"{service_config['url']}/health",
                timeout=service_config['timeout']
            )
            is_healthy = response.status_code == 200
            self.service_health[service_name] = {
                "healthy": is_healthy,
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "timestamp": time.time()
            }
            return is_healthy
        except Exception as e:
            self.service_health[service_name] = {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time()
            }
            return False
    
    async def test_service_discovery(self) -> Dict[str, Any]:
        """Test service discovery and health checks."""
        results = {"passed": 0, "failed": 0, "services": {}}
        
        for service_name, config in TEST_CONFIG["services"].items():
            is_healthy = await self.check_service_health(service_name, config)
            results["services"][service_name] = self.service_health[service_name]
            
            if is_healthy:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        results["success_rate"] = results["passed"] / (results["passed"] + results["failed"])
        return results
    
    async def test_authentication_flow(self) -> Dict[str, Any]:
        """Test authentication service integration."""
        try:
            auth_url = TEST_CONFIG["services"]["auth_service"]["url"]
            
            # Test user registration
            register_response = await self.http_client.post(
                f"{auth_url}/api/v1/auth/register",
                json=TEST_CONFIG["test_data"]["test_user"]
            )
            
            # Test login
            login_response = await self.http_client.post(
                f"{auth_url}/api/v1/auth/login",
                json={
                    "username": TEST_CONFIG["test_data"]["test_user"]["username"],
                    "password": "test_password"
                }
            )
            
            return {
                "passed": True,
                "register_status": register_response.status_code,
                "login_status": login_response.status_code,
                "message": "Authentication flow completed successfully"
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "message": "Authentication flow failed"
            }
    
    async def test_constitutional_compliance_workflow(self) -> Dict[str, Any]:
        """Test end-to-end constitutional compliance workflow."""
        try:
            workflow_steps = []
            
            # Step 1: Submit policy to AC service
            ac_url = TEST_CONFIG["services"]["ac_service"]["url"]
            policy_response = await self.http_client.post(
                f"{ac_url}/api/v1/compliance/validate",
                json=TEST_CONFIG["test_data"]["test_policy"]
            )
            workflow_steps.append({
                "step": "policy_submission",
                "status": policy_response.status_code,
                "success": policy_response.status_code == 200
            })
            
            # Step 2: Formal verification
            fv_url = TEST_CONFIG["services"]["fv_service"]["url"]
            fv_response = await self.http_client.post(
                f"{fv_url}/api/v1/verify",
                json={"policy_id": "test_policy_001"}
            )
            workflow_steps.append({
                "step": "formal_verification",
                "status": fv_response.status_code,
                "success": fv_response.status_code == 200
            })
            
            # Step 3: Policy governance check
            pgc_url = TEST_CONFIG["services"]["pgc_service"]["url"]
            pgc_response = await self.http_client.post(
                f"{pgc_url}/api/v1/enforcement/validate",
                json={"policy_id": "test_policy_001"}
            )
            workflow_steps.append({
                "step": "governance_check",
                "status": pgc_response.status_code,
                "success": pgc_response.status_code == 200
            })
            
            # Calculate overall success
            successful_steps = sum(1 for step in workflow_steps if step["success"])
            success_rate = successful_steps / len(workflow_steps)
            
            return {
                "passed": success_rate >= 0.8,  # 80% success threshold
                "success_rate": success_rate,
                "workflow_steps": workflow_steps,
                "message": f"Constitutional compliance workflow completed with {success_rate:.1%} success rate"
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "message": "Constitutional compliance workflow failed"
            }
    
    async def test_performance_requirements(self) -> Dict[str, Any]:
        """Test performance requirements across services."""
        performance_results = {}
        
        for service_name, config in TEST_CONFIG["services"].items():
            try:
                start_time = time.time()
                response = await self.http_client.get(f"{config['url']}/")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                
                performance_results[service_name] = {
                    "response_time_ms": response_time_ms,
                    "meets_requirement": response_time_ms < 500,  # <500ms requirement
                    "status_code": response.status_code
                }
                
            except Exception as e:
                performance_results[service_name] = {
                    "error": str(e),
                    "meets_requirement": False
                }
        
        # Calculate overall performance compliance
        services_meeting_requirements = sum(
            1 for result in performance_results.values() 
            if result.get("meets_requirement", False)
        )
        compliance_rate = services_meeting_requirements / len(performance_results)
        
        return {
            "passed": compliance_rate >= 0.95,  # 95% compliance threshold
            "compliance_rate": compliance_rate,
            "service_performance": performance_results,
            "message": f"Performance requirements met by {compliance_rate:.1%} of services"
        }
    
    async def test_blockchain_integration(self) -> Dict[str, Any]:
        """Test blockchain event bridge integration."""
        try:
            bridge_url = TEST_CONFIG["services"]["blockchain_bridge"]["url"]
            
            # Test recent events endpoint
            events_response = await self.http_client.get(f"{bridge_url}/events/recent")
            
            # Test service health
            health_response = await self.http_client.get(f"{bridge_url}/health")
            
            return {
                "passed": events_response.status_code == 200 and health_response.status_code == 200,
                "events_status": events_response.status_code,
                "health_status": health_response.status_code,
                "message": "Blockchain integration test completed"
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "message": "Blockchain integration test failed"
            }
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete integration test suite."""
        test_suite_results = {
            "start_time": time.time(),
            "tests": {},
            "summary": {}
        }
        
        # Run all test categories
        test_categories = [
            ("service_discovery", self.test_service_discovery),
            ("authentication_flow", self.test_authentication_flow),
            ("constitutional_compliance", self.test_constitutional_compliance_workflow),
            ("performance_requirements", self.test_performance_requirements),
            ("blockchain_integration", self.test_blockchain_integration),
        ]
        
        passed_tests = 0
        total_tests = len(test_categories)
        
        for test_name, test_method in test_categories:
            print(f"Running {test_name} test...")
            test_result = await test_method()
            test_suite_results["tests"][test_name] = test_result
            
            if test_result.get("passed", False):
                passed_tests += 1
        
        # Calculate summary
        test_suite_results["end_time"] = time.time()
        test_suite_results["duration_seconds"] = (
            test_suite_results["end_time"] - test_suite_results["start_time"]
        )
        test_suite_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests,
            "overall_passed": passed_tests == total_tests
        }
        
        return test_suite_results


# Pytest fixtures and test functions
@pytest.fixture
async def integration_tester():
    """Fixture for integration tester."""
    async with ACGSIntegrationTester() as tester:
        yield tester


@pytest.mark.asyncio
async def test_service_health_checks(integration_tester):
    """Test all service health checks."""
    results = await integration_tester.test_service_discovery()
    assert results["success_rate"] >= 0.8, f"Service health check success rate too low: {results['success_rate']}"


@pytest.mark.asyncio
async def test_authentication_integration(integration_tester):
    """Test authentication service integration."""
    results = await integration_tester.test_authentication_flow()
    assert results["passed"], f"Authentication flow failed: {results.get('message', 'Unknown error')}"


@pytest.mark.asyncio
async def test_constitutional_workflow(integration_tester):
    """Test constitutional compliance workflow."""
    results = await integration_tester.test_constitutional_compliance_workflow()
    assert results["passed"], f"Constitutional workflow failed: {results.get('message', 'Unknown error')}"


@pytest.mark.asyncio
async def test_performance_compliance(integration_tester):
    """Test performance requirements compliance."""
    results = await integration_tester.test_performance_requirements()
    assert results["passed"], f"Performance requirements not met: {results.get('message', 'Unknown error')}"


@pytest.mark.asyncio
async def test_full_integration_suite():
    """Run the complete integration test suite."""
    async with ACGSIntegrationTester() as tester:
        results = await tester.run_comprehensive_test_suite()
        
        print(f"\n{'='*50}")
        print("ACGS-1 Integration Test Suite Results")
        print(f"{'='*50}")
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['passed_tests']}")
        print(f"Failed: {results['summary']['failed_tests']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1%}")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        print(f"Overall Result: {'✅ PASSED' if results['summary']['overall_passed'] else '❌ FAILED'}")
        
        assert results["summary"]["overall_passed"], "Integration test suite failed"


if __name__ == "__main__":
    # Run the test suite directly
    asyncio.run(test_full_integration_suite())
