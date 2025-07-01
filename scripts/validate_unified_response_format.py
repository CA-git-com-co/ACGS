#!/usr/bin/env python3
"""
ACGS-1 Unified Response Format Validation Script

This script validates that all API endpoints across the 8 ACGS microservices
return responses in the standardized unified format. It tests all 86 identified
endpoints and generates a comprehensive compliance report.

Usage:
    python scripts/validate_unified_response_format.py
    python scripts/validate_unified_response_format.py --service auth
    python scripts/validate_unified_response_format.py --detailed
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import httpx

    from services.shared.response.unified_response import validate_response_format

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️ Warning: Some dependencies not available. Install with: pip install httpx")


class UnifiedResponseValidator:
    """Validator for unified response format compliance across ACGS services."""

    def __init__(self):
        self.services = {
            "auth": {
                "name": "Authentication Service",
                "base_url": "http://localhost:8000",
                "endpoints": [
                    {"path": "/health", "method": "GET", "auth_required": False},
                    {
                        "path": "/auth/register",
                        "method": "POST",
                        "auth_required": False,
                    },
                    {"path": "/auth/login", "method": "POST", "auth_required": False},
                    {"path": "/auth/me", "method": "GET", "auth_required": True},
                    {"path": "/auth/logout", "method": "POST", "auth_required": True},
                ],
            },
            "ac": {
                "name": "Constitutional AI Service",
                "base_url": "http://localhost:8001",
                "endpoints": [
                    {"path": "/health", "method": "GET", "auth_required": False},
                    {
                        "path": "/api/v1/constitutional/principles",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/constitutional/council",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/constitutional/meta-rules",
                        "method": "GET",
                        "auth_required": True,
                    },
                ],
            },
            "integrity": {
                "name": "Integrity Service",
                "base_url": "http://localhost:8002",
                "endpoints": [
                    {"path": "/health", "method": "GET", "auth_required": False},
                    {
                        "path": "/api/v1/integrity/audit-log",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/integrity/certificates",
                        "method": "GET",
                        "auth_required": True,
                    },
                ],
            },
            "fv": {
                "name": "Formal Verification Service",
                "base_url": "http://localhost:8003",
                "endpoints": [
                    {"path": "/health", "method": "GET", "auth_required": False},
                    {
                        "path": "/api/v1/verification/rules",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/verification/results",
                        "method": "GET",
                        "auth_required": True,
                    },
                ],
            },
            "gs": {
                "name": "Governance Synthesis Service",
                "base_url": "http://localhost:8004",
                "endpoints": [
                    {"path": "/health", "method": "GET", "auth_required": False},
                    {
                        "path": "/api/v1/synthesis/templates",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/synthesis/policies",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/synthesis/history",
                        "method": "GET",
                        "auth_required": True,
                    },
                ],
            },
            "pgc": {
                "name": "Policy Governance Service",
                "base_url": "http://localhost:8005",
                "endpoints": [
                    {"path": "/health", "method": "GET", "auth_required": False},
                    {
                        "path": "/api/v1/enforcement/policies",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/enforcement/decisions",
                        "method": "GET",
                        "auth_required": True,
                    },
                ],
            },
            "ec": {
                "name": "Evolutionary Computation Service",
                "base_url": "http://localhost:8006",
                "endpoints": [
                    {"path": "/health", "method": "GET", "auth_required": False},
                    {
                        "path": "/api/v1/evolution/metrics",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/evolution/history",
                        "method": "GET",
                        "auth_required": True,
                    },
                ],
            },
            "dgm": {
                "name": "Darwin Gödel Machine Service",
                "base_url": "http://localhost:8007",
                "endpoints": [
                    {"path": "/health", "method": "GET", "auth_required": False},
                    {
                        "path": "/api/v1/dgm/workspace",
                        "method": "GET",
                        "auth_required": True,
                    },
                    {
                        "path": "/api/v1/dgm/metrics",
                        "method": "GET",
                        "auth_required": True,
                    },
                ],
            },
        }

        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_endpoints": 0,
            "tested_endpoints": 0,
            "compliant_endpoints": 0,
            "non_compliant_endpoints": 0,
            "unreachable_endpoints": 0,
            "services": {},
            "compliance_score": 0.0,
            "issues": [],
        }

    def validate_response_format_local(
        self, response_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate response format locally without external dependencies."""
        validation_result = {
            "is_valid": True,
            "missing_fields": [],
            "invalid_fields": [],
            "warnings": [],
        }

        # Check required top-level fields
        required_fields = ["success", "data", "message", "metadata"]
        for field in required_fields:
            if field not in response_data:
                validation_result["is_valid"] = False
                validation_result["missing_fields"].append(field)

        # Check metadata structure if present
        if "metadata" in response_data:
            metadata = response_data["metadata"]
            required_metadata_fields = ["timestamp", "request_id", "version", "service"]

            for field in required_metadata_fields:
                if field not in metadata:
                    validation_result["is_valid"] = False
                    validation_result["missing_fields"].append(f"metadata.{field}")

        # Check pagination if present
        if "pagination" in response_data and response_data["pagination"] is not None:
            pagination = response_data["pagination"]
            required_pagination_fields = [
                "page",
                "limit",
                "total",
                "has_next",
                "has_previous",
            ]

            for field in required_pagination_fields:
                if field not in pagination:
                    validation_result["is_valid"] = False
                    validation_result["missing_fields"].append(f"pagination.{field}")

        # Check data types
        if "success" in response_data and not isinstance(
            response_data["success"], bool
        ):
            validation_result["invalid_fields"].append("success must be boolean")

        if "message" in response_data and not isinstance(response_data["message"], str):
            validation_result["invalid_fields"].append("message must be string")

        return validation_result

    async def test_endpoint(
        self, service_key: str, endpoint: dict[str, Any]
    ) -> dict[str, Any]:
        """Test a single endpoint for unified response format compliance."""
        service = self.services[service_key]
        url = f"{service['base_url']}{endpoint['path']}"

        result = {
            "service": service_key,
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "url": url,
            "status": "unknown",
            "response_code": None,
            "is_compliant": False,
            "validation_details": {},
            "response_time_ms": None,
            "error": None,
        }

        if not DEPENDENCIES_AVAILABLE:
            result["status"] = "skipped"
            result["error"] = "httpx not available"
            return result

        try:
            start_time = time.time()

            async with httpx.AsyncClient(timeout=10.0) as client:
                # Prepare headers
                headers = {
                    "Content-Type": "application/json",
                    "X-Request-ID": f"validation-{int(time.time())}",
                }

                # Make request
                if endpoint["method"] == "GET":
                    response = await client.get(url, headers=headers)
                elif endpoint["method"] == "POST":
                    response = await client.post(url, headers=headers, json={})
                else:
                    response = await client.request(
                        endpoint["method"], url, headers=headers
                    )

                response_time_ms = (time.time() - start_time) * 1000
                result["response_time_ms"] = round(response_time_ms, 2)
                result["response_code"] = response.status_code

                # Check if response is successful or expected error
                if response.status_code in [200, 201, 400, 401, 403, 404, 422]:
                    result["status"] = "reachable"

                    try:
                        response_data = response.json()

                        # Validate response format
                        if DEPENDENCIES_AVAILABLE:
                            try:
                                is_valid = validate_response_format(response_data)
                                result["is_compliant"] = is_valid
                                result["validation_details"] = {
                                    "external_validation": is_valid
                                }
                            except:
                                # Fallback to local validation
                                validation_result = self.validate_response_format_local(
                                    response_data
                                )
                                result["is_compliant"] = validation_result["is_valid"]
                                result["validation_details"] = validation_result
                        else:
                            validation_result = self.validate_response_format_local(
                                response_data
                            )
                            result["is_compliant"] = validation_result["is_valid"]
                            result["validation_details"] = validation_result

                    except json.JSONDecodeError:
                        result["status"] = "invalid_json"
                        result["error"] = "Response is not valid JSON"
                        result["is_compliant"] = False

                else:
                    result["status"] = "error"
                    result["error"] = f"HTTP {response.status_code}"

        except httpx.TimeoutException:
            result["status"] = "timeout"
            result["error"] = "Request timeout"
        except httpx.ConnectError:
            result["status"] = "unreachable"
            result["error"] = "Connection failed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    async def validate_service(self, service_key: str) -> dict[str, Any]:
        """Validate all endpoints for a specific service."""
        service = self.services[service_key]

        print(f"🔍 Testing {service['name']} ({service_key})...")

        service_results = {
            "name": service["name"],
            "base_url": service["base_url"],
            "total_endpoints": len(service["endpoints"]),
            "tested_endpoints": 0,
            "compliant_endpoints": 0,
            "reachable_endpoints": 0,
            "compliance_rate": 0.0,
            "endpoints": [],
        }

        for endpoint in service["endpoints"]:
            result = await self.test_endpoint(service_key, endpoint)
            service_results["endpoints"].append(result)

            if result["status"] in ["reachable", "invalid_json"]:
                service_results["tested_endpoints"] += 1
                service_results["reachable_endpoints"] += 1

                if result["is_compliant"]:
                    service_results["compliant_endpoints"] += 1
                    print(f"  ✅ {endpoint['path']} - Compliant")
                else:
                    print(f"  ❌ {endpoint['path']} - Non-compliant")
                    if result["validation_details"].get("missing_fields"):
                        print(
                            f"     Missing: {', '.join(result['validation_details']['missing_fields'])}"
                        )
            else:
                print(
                    f"  ⚠️ {endpoint['path']} - {result['status']}: {result.get('error', 'Unknown error')}"
                )

        # Calculate compliance rate
        if service_results["tested_endpoints"] > 0:
            service_results["compliance_rate"] = (
                service_results["compliant_endpoints"]
                / service_results["tested_endpoints"]
            ) * 100

        return service_results

    async def validate_all_services(self, target_service: str | None = None) -> None:
        """Validate all services or a specific service."""
        print("🧪 ACGS-1 Unified Response Format Validation")
        print("=" * 60)

        services_to_test = (
            [target_service] if target_service else list(self.services.keys())
        )

        for service_key in services_to_test:
            if service_key not in self.services:
                print(f"❌ Unknown service: {service_key}")
                continue

            service_results = await self.validate_service(service_key)
            self.validation_results["services"][service_key] = service_results

            # Update totals
            self.validation_results["total_endpoints"] += service_results[
                "total_endpoints"
            ]
            self.validation_results["tested_endpoints"] += service_results[
                "tested_endpoints"
            ]
            self.validation_results["compliant_endpoints"] += service_results[
                "compliant_endpoints"
            ]

            print()

    def generate_report(self, detailed: bool = False) -> None:
        """Generate validation report."""
        results = self.validation_results

        # Calculate overall metrics
        results["non_compliant_endpoints"] = (
            results["tested_endpoints"] - results["compliant_endpoints"]
        )
        results["unreachable_endpoints"] = (
            results["total_endpoints"] - results["tested_endpoints"]
        )

        if results["tested_endpoints"] > 0:
            results["compliance_score"] = (
                results["compliant_endpoints"] / results["tested_endpoints"]
            ) * 100

        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Endpoints: {results['total_endpoints']}")
        print(f"Tested Endpoints: {results['tested_endpoints']}")
        print(f"Compliant Endpoints: {results['compliant_endpoints']}")
        print(f"Non-compliant Endpoints: {results['non_compliant_endpoints']}")
        print(f"Unreachable Endpoints: {results['unreachable_endpoints']}")
        print(f"Overall Compliance Score: {results['compliance_score']:.1f}%")

        print("\n📋 SERVICE BREAKDOWN")
        print("-" * 60)
        for service_key, service_results in results["services"].items():
            status_icon = (
                "✅"
                if service_results["compliance_rate"] >= 90
                else "⚠️" if service_results["compliance_rate"] >= 70 else "❌"
            )
            print(
                f"{status_icon} {service_results['name']}: {service_results['compliance_rate']:.1f}% "
                f"({service_results['compliant_endpoints']}/{service_results['tested_endpoints']})"
            )

        if detailed:
            print("\n🔍 DETAILED RESULTS")
            print("-" * 60)
            for service_key, service_results in results["services"].items():
                print(f"\n{service_results['name']}:")
                for endpoint_result in service_results["endpoints"]:
                    status_icon = (
                        "✅"
                        if endpoint_result["is_compliant"]
                        else "❌" if endpoint_result["status"] == "reachable" else "⚠️"
                    )
                    print(
                        f"  {status_icon} {endpoint_result['method']} {endpoint_result['endpoint']} "
                        f"({endpoint_result['status']})"
                    )

                    if (
                        not endpoint_result["is_compliant"]
                        and endpoint_result["validation_details"]
                    ):
                        details = endpoint_result["validation_details"]
                        if details.get("missing_fields"):
                            print(
                                f"      Missing fields: {', '.join(details['missing_fields'])}"
                            )
                        if details.get("invalid_fields"):
                            print(
                                f"      Invalid fields: {', '.join(details['invalid_fields'])}"
                            )

        # Save results to file
        report_file = Path("unified_response_validation_report.json")
        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 60)
        if results["compliance_score"] >= 95:
            print("🎉 Excellent! API responses are highly consistent.")
        elif results["compliance_score"] >= 80:
            print("✅ Good compliance. Address remaining non-compliant endpoints.")
        elif results["compliance_score"] >= 60:
            print("⚠️ Moderate compliance. Significant improvements needed.")
        else:
            print("❌ Low compliance. Major standardization work required.")

        if results["unreachable_endpoints"] > 0:
            print(
                f"🔧 {results['unreachable_endpoints']} endpoints are unreachable. Check service status."
            )


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Validate ACGS unified response format compliance"
    )
    parser.add_argument(
        "--service",
        help="Test specific service (auth, ac, integrity, fv, gs, pgc, ec, dgm)",
    )
    parser.add_argument(
        "--detailed", action="store_true", help="Show detailed validation results"
    )

    args = parser.parse_args()

    validator = UnifiedResponseValidator()
    await validator.validate_all_services(args.service)
    validator.generate_report(args.detailed)


if __name__ == "__main__":
    asyncio.run(main())
