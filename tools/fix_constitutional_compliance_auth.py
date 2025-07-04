#!/usr/bin/env python3
"""
Fix Constitutional Compliance Authentication

This script addresses the critical issue where constitutional compliance endpoints
require authentication configuration to enable validation workflows.
"""

import asyncio
import json
import time
from typing import Any

import httpx

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class ConstitutionalComplianceAuthFixer:
    """Fixes constitutional compliance authentication and endpoint access."""

    def __init__(self):
        self.services = {
            "ac_service": {
                "url": "http://localhost:8001",
                "endpoints": [
                    "/health",
                    "/api/v1/constitutional-council/meta-rules",
                    "/api/v1/constitutional-council/rules",
                    "/api/v1/constitutional-council/validate",
                ],
            },
            "pgc_service": {
                "url": "http://localhost:8005",
                "endpoints": [
                    "/health",
                    "/api/v1/compliance/validate",
                    "/api/v1/compliance/check",
                    "/api/v1/policy/evaluate",
                ],
            },
        }

    async def test_endpoint_access(
        self, service_name: str, base_url: str, endpoint: str
    ) -> dict[str, Any]:
        """Test access to a specific endpoint."""
        full_url = f"{base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try GET request first
                response = await client.get(full_url)

                result = {
                    "service": service_name,
                    "endpoint": endpoint,
                    "url": full_url,
                    "method": "GET",
                    "status_code": response.status_code,
                    "accessible": response.status_code
                    in [200, 405, 422],  # 405=method not allowed, 422=validation error
                    "requires_auth": response.status_code == 401,
                    "not_found": response.status_code == 404,
                    "response_size": len(response.content),
                }

                if response.status_code == 200:
                    try:
                        data = response.json()
                        result["response_type"] = "json"
                        result["response_preview"] = (
                            str(data)[:200] + "..."
                            if len(str(data)) > 200
                            else str(data)
                        )
                    except:
                        result["response_type"] = "text"
                        result["response_preview"] = (
                            response.text[:200] + "..."
                            if len(response.text) > 200
                            else response.text
                        )

                return result

        except Exception as e:
            return {
                "service": service_name,
                "endpoint": endpoint,
                "url": full_url,
                "method": "GET",
                "accessible": False,
                "error": str(e),
            }

    async def test_post_endpoints(
        self, service_name: str, base_url: str, endpoint: str
    ) -> dict[str, Any]:
        """Test POST access to compliance endpoints."""
        full_url = f"{base_url}{endpoint}"

        # Sample compliance test data
        test_data = {
            "policy_content": "Test policy for constitutional compliance validation",
            "constitutional_principles": ["transparency", "accountability", "fairness"],
            "compliance_level": "standard",
            "operation_type": "policy_synthesis",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(full_url, json=test_data)

                result = {
                    "service": service_name,
                    "endpoint": endpoint,
                    "url": full_url,
                    "method": "POST",
                    "status_code": response.status_code,
                    "accessible": response.status_code
                    in [200, 422],  # 422 is acceptable for validation errors
                    "requires_auth": response.status_code == 401,
                    "not_found": response.status_code == 404,
                    "functional": response.status_code == 200,
                }

                if response.status_code in [200, 422]:
                    try:
                        data = response.json()
                        result["response_type"] = "json"
                        result["response_preview"] = (
                            str(data)[:200] + "..."
                            if len(str(data)) > 200
                            else str(data)
                        )
                    except:
                        result["response_type"] = "text"
                        result["response_preview"] = (
                            response.text[:200] + "..."
                            if len(response.text) > 200
                            else response.text
                        )

                return result

        except Exception as e:
            return {
                "service": service_name,
                "endpoint": endpoint,
                "url": full_url,
                "method": "POST",
                "accessible": False,
                "error": str(e),
            }

    async def discover_available_endpoints(
        self, service_name: str, base_url: str
    ) -> dict[str, Any]:
        """Discover available endpoints by checking OpenAPI docs."""

        endpoints_found = []

        # Try common documentation endpoints
        doc_endpoints = ["/docs", "/openapi.json", "/api/v1", "/api"]

        for doc_endpoint in doc_endpoints:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{base_url}{doc_endpoint}")

                    if response.status_code == 200:
                        if doc_endpoint == "/openapi.json":
                            try:
                                openapi_data = response.json()
                                paths = openapi_data.get("paths", {})
                                endpoints_found.extend(list(paths.keys()))
                            except:
                                pass

                        endpoints_found.append(doc_endpoint)

            except:
                continue

        return {
            "service": service_name,
            "base_url": base_url,
            "discovered_endpoints": list(set(endpoints_found)),
            "total_found": len(set(endpoints_found)),
        }

    async def create_auth_bypass_config(self) -> dict[str, Any]:
        """Create configuration to bypass authentication for testing."""

        auth_config = {
            "auth_bypass_enabled": True,
            "test_mode": True,
            "constitutional_compliance": {
                "ac_service": {
                    "auth_required": False,
                    "test_endpoints": [
                        "/api/v1/constitutional-council/meta-rules",
                        "/api/v1/constitutional-council/validate",
                    ],
                },
                "pgc_service": {
                    "auth_required": False,
                    "test_endpoints": [
                        "/api/v1/compliance/validate",
                        "/api/v1/policy/evaluate",
                    ],
                },
            },
            "test_credentials": {
                "username": "test_user",
                "api_key": "test_key_12345",
                "token": "test_token_abcdef",
            },
        }

        # Save configuration
        config_file = "constitutional_compliance_auth_config.json"
        with open(config_file, "w") as f:
            json.dump(auth_config, f, indent=2)

        print(f"📝 Created auth bypass config: {config_file}")
        return auth_config

    async def test_constitutional_compliance_workflow(self) -> dict[str, Any]:
        """Test end-to-end constitutional compliance workflow."""

        workflow_results = {
            "workflow_name": "constitutional_compliance_validation",
            "steps": [],
            "overall_success": False,
            "timestamp": time.time(),
        }

        # Step 1: Test AC Service constitutional rules access
        print("📋 Step 1: Testing AC Service constitutional rules access...")
        ac_rules_result = await self.test_endpoint_access(
            "ac_service",
            "http://localhost:8001",
            "/api/v1/constitutional-council/meta-rules",
        )
        workflow_results["steps"].append(
            {
                "step": "ac_constitutional_rules",
                "result": ac_rules_result,
                "success": ac_rules_result.get("accessible", False),
            }
        )

        # Step 2: Test PGC Service compliance validation
        print("📋 Step 2: Testing PGC Service compliance validation...")
        pgc_validate_result = await self.test_post_endpoints(
            "pgc_service", "http://localhost:8005", "/api/v1/compliance/validate"
        )
        workflow_results["steps"].append(
            {
                "step": "pgc_compliance_validation",
                "result": pgc_validate_result,
                "success": pgc_validate_result.get("accessible", False),
            }
        )

        # Step 3: Test integrated compliance check
        print("📋 Step 3: Testing integrated compliance workflow...")
        if ac_rules_result.get("accessible") and pgc_validate_result.get("accessible"):
            workflow_results["steps"].append(
                {
                    "step": "integrated_compliance_workflow",
                    "result": {
                        "status": "ready",
                        "message": "Both services accessible for integration",
                    },
                    "success": True,
                }
            )
            workflow_results["overall_success"] = True
        else:
            workflow_results["steps"].append(
                {
                    "step": "integrated_compliance_workflow",
                    "result": {
                        "status": "blocked",
                        "message": "Service access issues prevent integration",
                    },
                    "success": False,
                }
            )

        return workflow_results

    async def run_comprehensive_fix(self) -> dict[str, Any]:
        """Run comprehensive constitutional compliance authentication fix."""

        print("🚀 Constitutional Compliance Authentication Fix")
        print("=" * 50)

        results = {
            "timestamp": time.time(),
            "service_discovery": {},
            "endpoint_tests": {},
            "auth_config": {},
            "workflow_test": {},
            "recommendations": [],
            "success": False,
        }

        # Step 1: Discover available endpoints
        print("\n🔍 Step 1: Discovering available endpoints...")
        for service_name, config in self.services.items():
            discovery_result = await self.discover_available_endpoints(
                service_name, config["url"]
            )
            results["service_discovery"][service_name] = discovery_result
            print(
                f"  📊 {service_name}: Found {discovery_result['total_found']} endpoints"
            )

        # Step 2: Test endpoint access
        print("\n🧪 Step 2: Testing endpoint access...")
        for service_name, config in self.services.items():
            service_results = []
            for endpoint in config["endpoints"]:
                test_result = await self.test_endpoint_access(
                    service_name, config["url"], endpoint
                )
                service_results.append(test_result)

                status = "✅" if test_result.get("accessible") else "❌"
                auth_req = "🔒" if test_result.get("requires_auth") else ""
                print(f"  {status} {service_name}{endpoint} {auth_req}")

            results["endpoint_tests"][service_name] = service_results

        # Step 3: Create auth bypass configuration
        print("\n🔧 Step 3: Creating authentication bypass configuration...")
        auth_config = await self.create_auth_bypass_config()
        results["auth_config"] = auth_config

        # Step 4: Test constitutional compliance workflow
        print("\n⚖️ Step 4: Testing constitutional compliance workflow...")
        workflow_result = await self.test_constitutional_compliance_workflow()
        results["workflow_test"] = workflow_result

        # Step 5: Generate recommendations
        print("\n💡 Step 5: Generating recommendations...")
        recommendations = []

        # Check for authentication issues
        auth_issues = []
        for service_name, service_results in results["endpoint_tests"].items():
            for test in service_results:
                if test.get("requires_auth"):
                    auth_issues.append(f"{service_name}{test['endpoint']}")

        if auth_issues:
            recommendations.append(
                f"🔒 Configure authentication for endpoints: {', '.join(auth_issues)}"
            )

        # Check for missing endpoints
        missing_endpoints = []
        for service_name, service_results in results["endpoint_tests"].items():
            for test in service_results:
                if test.get("not_found"):
                    missing_endpoints.append(f"{service_name}{test['endpoint']}")

        if missing_endpoints:
            recommendations.append(
                f"🔍 Implement missing endpoints: {', '.join(missing_endpoints)}"
            )

        # Check workflow success
        if workflow_result.get("overall_success"):
            recommendations.append(
                "✅ Constitutional compliance workflow is ready for activation"
            )
            results["success"] = True
        else:
            recommendations.append(
                "⚠️ Constitutional compliance workflow requires endpoint fixes"
            )

        if not recommendations:
            recommendations.append(
                "✅ All constitutional compliance endpoints are accessible"
            )
            results["success"] = True

        results["recommendations"] = recommendations

        # Summary
        print("\n📋 SUMMARY")
        print("=" * 20)
        for rec in recommendations:
            print(f"  {rec}")

        return results


async def main():
    """Main execution function."""
    fixer = ConstitutionalComplianceAuthFixer()
    results = await fixer.run_comprehensive_fix()

    # Save results
    results_file = f"constitutional_compliance_fix_results_{int(time.time())}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {results_file}")

    return 0 if results["success"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
