#!/usr/bin/env python3
"""
Constitutional AI Services Integration Testing Script

Test end-to-end agent operation workflows with full ACGS governance.
"""

import asyncio
import json
from datetime import datetime
from typing import Any

import httpx

# Service endpoints
SERVICES = {
    "ac_service": "http://localhost:8001",
    "hitl_service": "http://localhost:8008",
    "auth_service": "http://localhost:8016",
}

# Expected constitutional hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalAIServicesTester:
    def __init__(self):
        self.results = {
            "test_start": None,
            "test_end": None,
            "service_discovery": {},
            "cross_service_integration": {},
            "end_to_end_workflows": {},
            "constitutional_governance": {},
            "errors": [],
            "summary": {},
        }
        self.client = httpx.AsyncClient(timeout=30.0)

    async def discover_services(self) -> dict[str, Any]:
        """Discover available services and their capabilities."""
        print("🔍 Discovering Constitutional AI services...")

        service_discovery = {}

        for service_name, service_url in SERVICES.items():
            try:
                # Test health endpoint
                health_response = await self.client.get(f"{service_url}/health")

                service_info = {
                    "available": health_response.status_code == 200,
                    "health_data": (
                        health_response.json()
                        if health_response.status_code == 200
                        else None
                    ),
                    "endpoints": [],
                    "constitutional_compliance": False,
                }

                if health_response.status_code == 200:
                    # Test common endpoints
                    endpoints_to_test = [
                        "/",
                        "/api/v1/info",
                        "/api/v1/constitutional/analyze",
                        "/api/v1/constitutional/compliance-score",
                        "/api/v1/auth/info",
                    ]

                    for endpoint in endpoints_to_test:
                        try:
                            response = await self.client.get(f"{service_url}{endpoint}")
                            if response.status_code == 200:
                                endpoint_data = response.json()
                                service_info["endpoints"].append(
                                    {
                                        "path": endpoint,
                                        "status": "available",
                                        "data": endpoint_data,
                                    }
                                )

                                # Check for constitutional hash
                                if "constitutional_hash" in endpoint_data:
                                    service_info["constitutional_compliance"] = (
                                        endpoint_data["constitutional_hash"]
                                        == CONSTITUTIONAL_HASH
                                    )
                        except:
                            pass

                service_discovery[service_name] = service_info

            except Exception as e:
                service_discovery[service_name] = {"available": False, "error": str(e)}

        return service_discovery

    async def test_constitutional_analysis(self) -> dict[str, Any]:
        """Test constitutional analysis capabilities."""
        print("⚖️ Testing constitutional analysis capabilities...")

        analysis_tests = []

        # Test 1: Constitutional compliance analysis
        test_cases = [
            {
                "name": "valid_code_analysis",
                "description": "Analyze constitutionally compliant code",
                "data": {
                    "code": "def safe_function():\n    return 'Hello, World!'",
                    "operation_type": "code_analysis",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            },
            {
                "name": "policy_violation_detection",
                "description": "Detect potential policy violations",
                "data": {
                    "code": "import os\nos.system('rm -rf /')",
                    "operation_type": "security_analysis",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            },
        ]

        for test_case in test_cases:
            test_result = {
                "test_name": test_case["name"],
                "description": test_case["description"],
                "passed": False,
                "response_data": None,
                "error": None,
            }

            try:
                # Test with AC Service
                response = await self.client.post(
                    f"{SERVICES['ac_service']}/api/v1/constitutional/analyze",
                    json=test_case["data"],
                )

                if response.status_code == 200:
                    response_data = response.json()
                    test_result["response_data"] = response_data
                    test_result["passed"] = True

                    # Validate response structure
                    if "compliance_score" in response_data:
                        test_result["compliance_score"] = response_data[
                            "compliance_score"
                        ]
                    if "violations" in response_data:
                        test_result["violations_detected"] = len(
                            response_data["violations"]
                        )

            except Exception as e:
                test_result["error"] = str(e)
                self.results["errors"].append(
                    f"Constitutional analysis test {test_case['name']} failed: {e!s}"
                )

            analysis_tests.append(test_result)

        return {
            "total_tests": len(analysis_tests),
            "passed_tests": sum(1 for test in analysis_tests if test["passed"]),
            "test_results": analysis_tests,
        }

    async def test_cross_service_integration(self) -> dict[str, Any]:
        """Test integration between Constitutional AI services."""
        print("🔗 Testing cross-service integration...")

        integration_tests = []

        # Test 1: Auth Service -> AC Service integration
        auth_ac_test = await self._test_auth_ac_integration()
        integration_tests.append(auth_ac_test)

        # Test 2: HITL Service -> AC Service integration
        hitl_ac_test = await self._test_hitl_ac_integration()
        integration_tests.append(hitl_ac_test)

        # Test 3: Full workflow integration
        full_workflow_test = await self._test_full_workflow_integration()
        integration_tests.append(full_workflow_test)

        return {
            "total_tests": len(integration_tests),
            "passed_tests": sum(
                1 for test in integration_tests if test.get("passed", False)
            ),
            "test_results": integration_tests,
        }

    async def _test_auth_ac_integration(self) -> dict[str, Any]:
        """Test Auth Service to AC Service integration."""
        try:
            # Get token from Auth Service
            auth_response = await self.client.post(
                f"{SERVICES['auth_service']}/api/v1/auth/token",
                json={"username": "integration_test", "password": "test"},
            )

            if auth_response.status_code != 200:
                return {
                    "test_name": "auth_ac_integration",
                    "passed": False,
                    "error": "Failed to get auth token",
                }

            token_data = auth_response.json()
            token = token_data.get("access_token")

            # Use token with AC Service
            ac_response = await self.client.post(
                f"{SERVICES['ac_service']}/api/v1/constitutional/analyze",
                json={
                    "code": "print('Integration test')",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            return {
                "test_name": "auth_ac_integration",
                "passed": ac_response.status_code == 200,
                "auth_token_received": token is not None,
                "ac_service_accepted_token": ac_response.status_code == 200,
                "response_data": (
                    ac_response.json() if ac_response.status_code == 200 else None
                ),
            }

        except Exception as e:
            return {
                "test_name": "auth_ac_integration",
                "passed": False,
                "error": str(e),
            }

    async def _test_hitl_ac_integration(self) -> dict[str, Any]:
        """Test HITL Service to AC Service integration."""
        try:
            # Submit request to HITL that should trigger AC Service consultation
            hitl_request = {
                "agent_id": "integration_test_agent",
                "agent_type": "constitutional_test",
                "operation_type": "constitutional_analysis",
                "operation_description": "Test constitutional analysis integration",
                "operation_context": {
                    "code": "def test_function(): return True",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "requires_ac_analysis": True,
                },
            }

            hitl_response = await self.client.post(
                f"{SERVICES['hitl_service']}/api/v1/reviews/evaluate", json=hitl_request
            )

            return {
                "test_name": "hitl_ac_integration",
                "passed": hitl_response.status_code == 200,
                "hitl_response_received": hitl_response.status_code == 200,
                "response_data": (
                    hitl_response.json() if hitl_response.status_code == 200 else None
                ),
            }

        except Exception as e:
            return {
                "test_name": "hitl_ac_integration",
                "passed": False,
                "error": str(e),
            }

    async def _test_full_workflow_integration(self) -> dict[str, Any]:
        """Test full end-to-end workflow integration."""
        try:
            # Step 1: Authenticate
            auth_response = await self.client.post(
                f"{SERVICES['auth_service']}/api/v1/auth/token",
                json={"username": "workflow_test", "password": "test"},
            )

            if auth_response.status_code != 200:
                return {
                    "test_name": "full_workflow_integration",
                    "passed": False,
                    "error": "Authentication failed",
                }

            token = auth_response.json().get("access_token")

            # Step 2: Submit code for constitutional analysis
            analysis_response = await self.client.post(
                f"{SERVICES['ac_service']}/api/v1/constitutional/analyze",
                json={
                    "code": "def workflow_test(): return 'constitutional compliance test'",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "operation_id": "workflow_test_001",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            # Step 3: Submit to HITL for review
            hitl_response = await self.client.post(
                f"{SERVICES['hitl_service']}/api/v1/reviews/evaluate",
                json={
                    "agent_id": "workflow_test_agent",
                    "agent_type": "full_workflow_test",
                    "operation_type": "constitutional_workflow",
                    "operation_description": "Full workflow integration test",
                    "operation_context": {
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                        "analysis_result": (
                            analysis_response.json()
                            if analysis_response.status_code == 200
                            else None
                        ),
                    },
                },
            )

            return {
                "test_name": "full_workflow_integration",
                "passed": all(
                    [
                        auth_response.status_code == 200,
                        analysis_response.status_code == 200,
                        hitl_response.status_code == 200,
                    ]
                ),
                "auth_success": auth_response.status_code == 200,
                "analysis_success": analysis_response.status_code == 200,
                "hitl_success": hitl_response.status_code == 200,
                "workflow_complete": True,
            }

        except Exception as e:
            return {
                "test_name": "full_workflow_integration",
                "passed": False,
                "error": str(e),
            }

    async def test_constitutional_governance(self) -> dict[str, Any]:
        """Test constitutional governance enforcement."""
        print("🏛️ Testing constitutional governance enforcement...")

        governance_tests = []

        # Test constitutional hash validation
        hash_validation_test = {
            "test_name": "constitutional_hash_validation",
            "passed": False,
            "valid_hash_accepted": False,
            "invalid_hash_rejected": False,
        }

        try:
            # Test valid hash
            valid_response = await self.client.post(
                f"{SERVICES['ac_service']}/api/v1/constitutional/analyze",
                json={
                    "code": "print('valid hash test')",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )
            hash_validation_test["valid_hash_accepted"] = (
                valid_response.status_code == 200
            )

            # Test invalid hash
            invalid_response = await self.client.post(
                f"{SERVICES['ac_service']}/api/v1/constitutional/analyze",
                json={
                    "code": "print('invalid hash test')",
                    "constitutional_hash": "invalid_hash_12345",
                },
            )
            # Should either reject (4xx) or flag for review
            hash_validation_test["invalid_hash_rejected"] = (
                invalid_response.status_code != 200
                or (
                    invalid_response.status_code == 200
                    and invalid_response.json().get("compliance_score", 1.0) < 0.5
                )
            )

            hash_validation_test["passed"] = (
                hash_validation_test["valid_hash_accepted"]
                and hash_validation_test["invalid_hash_rejected"]
            )

        except Exception as e:
            hash_validation_test["error"] = str(e)

        governance_tests.append(hash_validation_test)

        return {
            "total_tests": len(governance_tests),
            "passed_tests": sum(
                1 for test in governance_tests if test.get("passed", False)
            ),
            "test_results": governance_tests,
        }

    async def run_comprehensive_test(self) -> dict[str, Any]:
        """Run comprehensive Constitutional AI services testing."""
        print("🧪 Starting comprehensive Constitutional AI services testing...")
        self.results["test_start"] = datetime.utcnow().isoformat()

        # Service discovery
        self.results["service_discovery"] = await self.discover_services()

        # Constitutional analysis testing
        self.results["constitutional_analysis"] = (
            await self.test_constitutional_analysis()
        )

        # Cross-service integration testing
        self.results["cross_service_integration"] = (
            await self.test_cross_service_integration()
        )

        # Constitutional governance testing
        self.results["constitutional_governance"] = (
            await self.test_constitutional_governance()
        )

        self.results["test_end"] = datetime.utcnow().isoformat()

        # Calculate summary
        available_services = sum(
            1
            for service in self.results["service_discovery"].values()
            if service.get("available", False)
        )
        total_services = len(self.results["service_discovery"])

        total_tests = (
            self.results["constitutional_analysis"].get("total_tests", 0)
            + self.results["cross_service_integration"].get("total_tests", 0)
            + self.results["constitutional_governance"].get("total_tests", 0)
        )

        passed_tests = (
            self.results["constitutional_analysis"].get("passed_tests", 0)
            + self.results["cross_service_integration"].get("passed_tests", 0)
            + self.results["constitutional_governance"].get("passed_tests", 0)
        )

        self.results["summary"] = {
            "available_services": available_services,
            "total_services": total_services,
            "service_availability_rate": available_services / total_services,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "constitutional_compliance": all(
                service.get("constitutional_compliance", False)
                for service in self.results["service_discovery"].values()
                if service.get("available", False)
            ),
            "total_errors": len(self.results["errors"]),
        }

        return self.results

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main test execution."""
    tester = ConstitutionalAIServicesTester()

    try:
        results = await tester.run_comprehensive_test()

        # Print results
        print("\n" + "=" * 80)
        print("🎯 CONSTITUTIONAL AI SERVICES TEST RESULTS")
        print("=" * 80)

        print("\n📊 Overall Summary:")
        summary = results["summary"]
        print(
            f"  • Available Services: {summary['available_services']}/{summary['total_services']}"
        )
        print(
            f"  • Service Availability: {summary['service_availability_rate'] * 100:.1f}%"
        )
        print(f"  • Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"  • Test Pass Rate: {summary['test_pass_rate'] * 100:.1f}%")
        print(
            f"  • Constitutional Compliance: {'✅ YES' if summary['constitutional_compliance'] else '❌ NO'}"
        )
        print(f"  • Total Errors: {summary['total_errors']}")

        print("\n🔍 Service Discovery:")
        for service_name, service_info in results["service_discovery"].items():
            status = "✅" if service_info.get("available") else "❌"
            print(f"  • {service_name}: {status}")
            if service_info.get("available"):
                print(f"    Endpoints: {len(service_info.get('endpoints', []))}")
                print(
                    f"    Constitutional Compliance: {'✅' if service_info.get('constitutional_compliance') else '❌'}"
                )

        print("\n⚖️ Constitutional Analysis:")
        analysis = results["constitutional_analysis"]
        print(f"  • Tests Passed: {analysis['passed_tests']}/{analysis['total_tests']}")
        for test in analysis["test_results"]:
            status = "✅" if test["passed"] else "❌"
            print(f"    {status} {test['test_name']}: {test['description']}")

        print("\n🔗 Cross-Service Integration:")
        integration = results["cross_service_integration"]
        print(
            f"  • Tests Passed: {integration['passed_tests']}/{integration['total_tests']}"
        )
        for test in integration["test_results"]:
            status = "✅" if test.get("passed") else "❌"
            print(f"    {status} {test['test_name']}")

        print("\n🏛️ Constitutional Governance:")
        governance = results["constitutional_governance"]
        print(
            f"  • Tests Passed: {governance['passed_tests']}/{governance['total_tests']}"
        )
        for test in governance["test_results"]:
            status = "✅" if test.get("passed") else "❌"
            print(f"    {status} {test['test_name']}")

        if results["errors"]:
            print("\n❌ Errors Encountered:")
            for error in results["errors"][:5]:
                print(f"  • {error}")

        # Save detailed results
        with open("constitutional_ai_services_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n💾 Detailed results saved to: constitutional_ai_services_results.json")

    except Exception as e:
        print(f"❌ Constitutional AI services test execution failed: {e}")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
