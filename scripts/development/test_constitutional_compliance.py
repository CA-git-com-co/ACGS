#!/usr/bin/env python3
"""
Constitutional Compliance Validation Script

Confirm constitutional compliance validation (hash: cdd01ef066bc6cf2) across all operations.
"""

import asyncio
import json
from datetime import datetime
from typing import Any

import httpx

# Expected constitutional hash
EXPECTED_CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service endpoints
SERVICES = {
    "auth_service": "http://localhost:8016",
    "hitl_service": "http://localhost:8008",
    "ac_service": "http://localhost:8001",
}


class ConstitutionalComplianceTester:
    def __init__(self):
        self.results = {
            "test_start": None,
            "test_end": None,
            "compliance_tests": {},
            "hash_validation": {},
            "policy_tests": {},
            "errors": [],
            "summary": {},
        }
        self.client = httpx.AsyncClient(timeout=30.0)

    async def test_service_constitutional_hash(
        self, service_name: str, service_url: str
    ) -> dict[str, Any]:
        """Test constitutional hash validation for a specific service."""
        print(f"⚖️ Testing constitutional hash validation for {service_name}...")

        test_results = {
            "service": service_name,
            "hash_found": False,
            "hash_matches": False,
            "hash_value": None,
            "endpoints_tested": [],
            "compliance_score": 0.0,
        }

        # Common endpoints that might return constitutional hash
        endpoints_to_test = [
            "/health",
            "/",
            "/api/v1/auth/info",
            "/api/v1/info",
            "/info",
        ]

        for endpoint in endpoints_to_test:
            try:
                response = await self.client.get(f"{service_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    test_results["endpoints_tested"].append(
                        {
                            "endpoint": endpoint,
                            "status": "success",
                            "constitutional_hash": data.get("constitutional_hash"),
                        }
                    )

                    # Check for constitutional hash
                    if "constitutional_hash" in data:
                        test_results["hash_found"] = True
                        test_results["hash_value"] = data["constitutional_hash"]
                        test_results["hash_matches"] = (
                            data["constitutional_hash"] == EXPECTED_CONSTITUTIONAL_HASH
                        )
                        break
                else:
                    test_results["endpoints_tested"].append(
                        {
                            "endpoint": endpoint,
                            "status": f"failed_{response.status_code}",
                        }
                    )

            except Exception as e:
                test_results["endpoints_tested"].append(
                    {"endpoint": endpoint, "status": "error", "error": str(e)}
                )

        # Calculate compliance score
        if test_results["hash_found"] and test_results["hash_matches"]:
            test_results["compliance_score"] = 1.0
        elif test_results["hash_found"]:
            test_results["compliance_score"] = 0.5
        else:
            test_results["compliance_score"] = 0.0

        return test_results

    async def test_constitutional_policy_validation(self) -> dict[str, Any]:
        """Test constitutional policy validation with various scenarios."""
        print("📋 Testing constitutional policy validation scenarios...")

        policy_tests = []

        # Test 1: Valid constitutional hash
        test_cases = [
            {
                "name": "valid_constitutional_hash",
                "description": "Test with valid constitutional hash",
                "data": {
                    "constitutional_hash": EXPECTED_CONSTITUTIONAL_HASH,
                    "operation": "test_operation",
                    "agent_id": "compliance_test_agent",
                },
                "expected_result": "approved",
            },
            {
                "name": "invalid_constitutional_hash",
                "description": "Test with invalid constitutional hash",
                "data": {
                    "constitutional_hash": "invalid_hash_12345",
                    "operation": "test_operation",
                    "agent_id": "compliance_test_agent",
                },
                "expected_result": "rejected_or_escalated",
            },
            {
                "name": "missing_constitutional_hash",
                "description": "Test with missing constitutional hash",
                "data": {
                    "operation": "test_operation",
                    "agent_id": "compliance_test_agent",
                },
                "expected_result": "rejected_or_escalated",
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
                # Test with HITL service (most likely to have constitutional validation)
                if test_case["name"] == "valid_constitutional_hash":
                    request_data = {
                        "agent_id": test_case["data"]["agent_id"],
                        "agent_type": "compliance_test",
                        "operation_type": "constitutional_validation",
                        "operation_description": test_case["description"],
                        "operation_context": {
                            "constitutional_hash": test_case["data"][
                                "constitutional_hash"
                            ],
                            "test_case": test_case["name"],
                        },
                    }

                    response = await self.client.post(
                        f"{SERVICES['hitl_service']}/api/v1/reviews/evaluate",
                        json=request_data,
                    )

                    if response.status_code == 200:
                        response_data = response.json()
                        test_result["response_data"] = response_data

                        # Check if constitutional compliance is validated
                        constitutional_compliance = response_data.get(
                            "constitutional_compliance_score", 0
                        )
                        if constitutional_compliance >= 0.95:
                            test_result["passed"] = True

                elif test_case["name"] == "invalid_constitutional_hash":
                    request_data = {
                        "agent_id": test_case["data"]["agent_id"],
                        "agent_type": "compliance_test",
                        "operation_type": "constitutional_validation",
                        "operation_description": test_case["description"],
                        "operation_context": {
                            "constitutional_hash": test_case["data"][
                                "constitutional_hash"
                            ],
                            "test_case": test_case["name"],
                        },
                    }

                    response = await self.client.post(
                        f"{SERVICES['hitl_service']}/api/v1/reviews/evaluate",
                        json=request_data,
                    )

                    if response.status_code == 200:
                        response_data = response.json()
                        test_result["response_data"] = response_data

                        # Should be escalated or rejected due to invalid hash
                        escalation_level = response_data.get("escalation_level", 1)
                        if escalation_level > 2:  # Escalated to higher level
                            test_result["passed"] = True

                else:  # missing_constitutional_hash
                    request_data = {
                        "agent_id": test_case["data"]["agent_id"],
                        "agent_type": "compliance_test",
                        "operation_type": "constitutional_validation",
                        "operation_description": test_case["description"],
                        "operation_context": {
                            "test_case": test_case["name"]
                            # No constitutional_hash provided
                        },
                    }

                    response = await self.client.post(
                        f"{SERVICES['hitl_service']}/api/v1/reviews/evaluate",
                        json=request_data,
                    )

                    if response.status_code == 200:
                        response_data = response.json()
                        test_result["response_data"] = response_data

                        # Should be escalated due to missing hash
                        escalation_level = response_data.get("escalation_level", 1)
                        if escalation_level > 1:  # Escalated
                            test_result["passed"] = True

            except Exception as e:
                test_result["error"] = str(e)
                self.results["errors"].append(
                    f"Policy test {test_case['name']} failed: {e!s}"
                )

            policy_tests.append(test_result)

        return {
            "total_tests": len(policy_tests),
            "passed_tests": sum(1 for test in policy_tests if test["passed"]),
            "test_results": policy_tests,
            "compliance_rate": sum(1 for test in policy_tests if test["passed"])
            / len(policy_tests),
        }

    async def test_cross_service_compliance(self) -> dict[str, Any]:
        """Test constitutional compliance across multiple services."""
        print("🔗 Testing cross-service constitutional compliance...")

        cross_service_results = {}

        # Test Auth Service compliance
        auth_token_test = await self._test_auth_service_compliance()
        cross_service_results["auth_service"] = auth_token_test

        # Test AC Service compliance
        ac_service_test = await self._test_ac_service_compliance()
        cross_service_results["ac_service"] = ac_service_test

        return cross_service_results

    async def _test_auth_service_compliance(self) -> dict[str, Any]:
        """Test Auth Service constitutional compliance."""
        try:
            # Test token generation includes constitutional hash
            response = await self.client.post(
                f"{SERVICES['auth_service']}/api/v1/auth/token",
                json={"username": "compliance_test", "password": "test"},
            )

            if response.status_code == 200:
                token_data = response.json()
                return {
                    "constitutional_hash_in_token": "constitutional_hash" in token_data,
                    "hash_matches": token_data.get("constitutional_hash")
                    == EXPECTED_CONSTITUTIONAL_HASH,
                    "compliance_score": (
                        1.0
                        if token_data.get("constitutional_hash")
                        == EXPECTED_CONSTITUTIONAL_HASH
                        else 0.0
                    ),
                }
            return {
                "error": f"Token generation failed: {response.status_code}",
                "compliance_score": 0.0,
            }

        except Exception as e:
            return {"error": str(e), "compliance_score": 0.0}

    async def _test_ac_service_compliance(self) -> dict[str, Any]:
        """Test AC Service constitutional compliance."""
        try:
            response = await self.client.get(f"{SERVICES['ac_service']}/health")

            if response.status_code == 200:
                health_data = response.json()
                return {
                    "constitutional_hash_in_health": "constitutional_hash"
                    in health_data,
                    "hash_matches": health_data.get("constitutional_hash")
                    == EXPECTED_CONSTITUTIONAL_HASH,
                    "compliance_score": (
                        1.0
                        if health_data.get("constitutional_hash")
                        == EXPECTED_CONSTITUTIONAL_HASH
                        else 0.0
                    ),
                }
            return {
                "error": f"Health check failed: {response.status_code}",
                "compliance_score": 0.0,
            }

        except Exception as e:
            return {"error": str(e), "compliance_score": 0.0}

    async def run_comprehensive_compliance_test(self) -> dict[str, Any]:
        """Run comprehensive constitutional compliance testing."""
        print("🧪 Starting comprehensive constitutional compliance testing...")
        self.results["test_start"] = datetime.utcnow().isoformat()

        # Test constitutional hash validation for each service
        for service_name, service_url in SERVICES.items():
            self.results["hash_validation"][service_name] = (
                await self.test_service_constitutional_hash(service_name, service_url)
            )

        # Test constitutional policy validation
        self.results["policy_tests"] = (
            await self.test_constitutional_policy_validation()
        )

        # Test cross-service compliance
        self.results["compliance_tests"] = await self.test_cross_service_compliance()

        self.results["test_end"] = datetime.utcnow().isoformat()

        # Calculate overall compliance score
        hash_scores = [
            result.get("compliance_score", 0)
            for result in self.results["hash_validation"].values()
        ]
        policy_score = self.results["policy_tests"].get("compliance_rate", 0)
        cross_service_scores = [
            result.get("compliance_score", 0)
            for result in self.results["compliance_tests"].values()
        ]

        all_scores = hash_scores + [policy_score] + cross_service_scores
        overall_compliance = sum(all_scores) / len(all_scores) if all_scores else 0

        self.results["summary"] = {
            "overall_compliance_score": overall_compliance,
            "hash_validation_score": (
                sum(hash_scores) / len(hash_scores) if hash_scores else 0
            ),
            "policy_validation_score": policy_score,
            "cross_service_score": (
                sum(cross_service_scores) / len(cross_service_scores)
                if cross_service_scores
                else 0
            ),
            "total_errors": len(self.results["errors"]),
            "constitutional_hash_expected": EXPECTED_CONSTITUTIONAL_HASH,
        }

        return self.results

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main test execution."""
    tester = ConstitutionalComplianceTester()

    try:
        results = await tester.run_comprehensive_compliance_test()

        # Print results
        print("\n" + "=" * 80)
        print("🎯 CONSTITUTIONAL COMPLIANCE TEST RESULTS")
        print("=" * 80)

        print("\n📊 Overall Summary:")
        summary = results["summary"]
        print(
            f"  • Overall Compliance Score: {summary['overall_compliance_score'] * 100:.1f}%"
        )
        print(
            f"  • Hash Validation Score: {summary['hash_validation_score'] * 100:.1f}%"
        )
        print(
            f"  • Policy Validation Score: {summary['policy_validation_score'] * 100:.1f}%"
        )
        print(f"  • Cross-Service Score: {summary['cross_service_score'] * 100:.1f}%")
        print(f"  • Expected Hash: {summary['constitutional_hash_expected']}")
        print(f"  • Total Errors: {summary['total_errors']}")

        print("\n🔍 Hash Validation Results:")
        for service, result in results["hash_validation"].items():
            status = (
                "✅"
                if result["compliance_score"] == 1.0
                else "⚠️" if result["compliance_score"] > 0 else "❌"
            )
            print(
                f"  • {service}: {status} Score: {result['compliance_score'] * 100:.0f}%"
            )
            if result["hash_found"]:
                print(
                    f"    Hash: {result['hash_value']} {'✅' if result['hash_matches'] else '❌'}"
                )

        print("\n📋 Policy Validation Results:")
        policy_results = results["policy_tests"]
        print(
            f"  • Tests Passed: {policy_results['passed_tests']}/{policy_results['total_tests']}"
        )
        print(f"  • Compliance Rate: {policy_results['compliance_rate'] * 100:.1f}%")

        for test in policy_results["test_results"]:
            status = "✅" if test["passed"] else "❌"
            print(f"    {status} {test['test_name']}: {test['description']}")

        print("\n🔗 Cross-Service Compliance:")
        for service, result in results["compliance_tests"].items():
            score = result.get("compliance_score", 0)
            status = "✅" if score == 1.0 else "⚠️" if score > 0 else "❌"
            print(f"  • {service}: {status} Score: {score * 100:.0f}%")

        if results["errors"]:
            print("\n❌ Errors Encountered:")
            for error in results["errors"][:5]:
                print(f"  • {error}")

        # Save detailed results
        with open("constitutional_compliance_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n💾 Detailed results saved to: constitutional_compliance_results.json")

    except Exception as e:
        print(f"❌ Compliance test execution failed: {e}")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
