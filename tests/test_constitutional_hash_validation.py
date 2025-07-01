#!/usr/bin/env python3
"""
Automated Constitutional Hash Validation Tests
==============================================

Tests to verify constitutional hash presence and correctness in all service health endpoints.
Ensures 100% constitutional hash consistency across all ACGS services.
"""

import asyncio
from typing import Any

import aiohttp
import pytest

# Expected constitutional hash
EXPECTED_CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service endpoints to test
SERVICES = {
    "auth": {"url": "http://localhost:8000", "port": 8000},
    "ac": {"url": "http://localhost:8001", "port": 8001},
    "integrity": {"url": "http://localhost:8002", "port": 8002},
    "fv": {"url": "http://localhost:8003", "port": 8003},
    "gs": {"url": "http://localhost:8004", "port": 8004},
    "pgc": {"url": "http://localhost:8005", "port": 8005},
    "ec": {"url": "http://localhost:8006", "port": 8006},
}


class ConstitutionalHashValidator:
    """Automated constitutional hash validation test suite."""

    def __init__(self):
        self.results = {}
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def test_service_health_endpoint(
        self, service_name: str, service_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Test constitutional hash in service health endpoint."""
        url = f"{service_config['url']}/health"

        try:
            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check for constitutional hash in response body
                    constitutional_hash = data.get("constitutional_hash")

                    # Check for constitutional hash in response headers
                    header_hash = response.headers.get("X-Constitutional-Hash")

                    return {
                        "service": service_name,
                        "url": url,
                        "status": "healthy",
                        "response_status": response.status,
                        "constitutional_hash_in_body": constitutional_hash,
                        "constitutional_hash_in_headers": header_hash,
                        "body_hash_correct": constitutional_hash
                        == EXPECTED_CONSTITUTIONAL_HASH,
                        "header_hash_correct": header_hash
                        == EXPECTED_CONSTITUTIONAL_HASH,
                        "has_constitutional_hash": constitutional_hash is not None
                        or header_hash is not None,
                        "fully_compliant": (
                            constitutional_hash == EXPECTED_CONSTITUTIONAL_HASH
                            or header_hash == EXPECTED_CONSTITUTIONAL_HASH
                        ),
                    }
                return {
                    "service": service_name,
                    "url": url,
                    "status": "unhealthy",
                    "response_status": response.status,
                    "error": f"HTTP {response.status}",
                    "fully_compliant": False,
                }

        except Exception as e:
            return {
                "service": service_name,
                "url": url,
                "status": "error",
                "error": str(e),
                "fully_compliant": False,
            }

    async def test_all_services(self) -> dict[str, Any]:
        """Test constitutional hash consistency across all services."""
        print("🏛️ Testing Constitutional Hash Consistency Across All Services")
        print("=" * 70)

        results = {}

        for service_name, service_config in SERVICES.items():
            print(f"Testing {service_name} service...")
            result = await self.test_service_health_endpoint(
                service_name, service_config
            )
            results[service_name] = result

            # Print immediate feedback
            if result.get("fully_compliant", False):
                print(f"   ✅ {service_name}: Constitutional hash present and correct")
            else:
                print(f"   ❌ {service_name}: Constitutional hash missing or incorrect")
                if "error" in result:
                    print(f"      Error: {result['error']}")

        # Calculate overall metrics
        total_services = len(SERVICES)
        compliant_services = sum(
            1 for r in results.values() if r.get("fully_compliant", False)
        )
        compliance_rate = compliant_services / total_services

        summary = {
            "total_services": total_services,
            "compliant_services": compliant_services,
            "non_compliant_services": total_services - compliant_services,
            "compliance_rate": compliance_rate,
            "target_compliance_rate": 1.0,
            "meets_target": compliance_rate >= 1.0,
            "expected_hash": EXPECTED_CONSTITUTIONAL_HASH,
        }

        print("=" * 70)
        print("📊 Constitutional Hash Compliance Results:")
        print(f"   Compliant Services: {compliant_services}/{total_services}")
        print(f"   Compliance Rate: {compliance_rate:.1%}")
        print("   Target: 100% compliance")
        print(f"   Status: {'✅ PASSED' if summary['meets_target'] else '❌ FAILED'}")

        return {"service_results": results, "summary": summary}


# Pytest test functions
@pytest.mark.asyncio
async def test_constitutional_hash_consistency():
    """Test constitutional hash consistency across all services."""
    async with ConstitutionalHashValidator() as validator:
        results = await validator.test_all_services()

        # Assert that all services are compliant
        assert results["summary"]["meets_target"], (
            f"Constitutional hash compliance failed: "
            f"{results['summary']['compliant_services']}/{results['summary']['total_services']} "
            f"services compliant"
        )


@pytest.mark.asyncio
async def test_individual_service_compliance():
    """Test each service individually for constitutional hash compliance."""
    async with ConstitutionalHashValidator() as validator:
        for service_name, service_config in SERVICES.items():
            result = await validator.test_service_health_endpoint(
                service_name, service_config
            )

            assert result.get(
                "fully_compliant", False
            ), f"Service {service_name} is not constitutionally compliant: {result}"


@pytest.mark.asyncio
async def test_constitutional_hash_in_headers():
    """Test that constitutional hash is present in response headers."""
    async with aiohttp.ClientSession() as session:
        for service_name, service_config in SERVICES.items():
            url = f"{service_config['url']}/health"

            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        header_hash = response.headers.get("X-Constitutional-Hash")
                        assert header_hash == EXPECTED_CONSTITUTIONAL_HASH, (
                            f"Service {service_name} missing or incorrect constitutional hash in headers: "
                            f"got {header_hash}, expected {EXPECTED_CONSTITUTIONAL_HASH}"
                        )
            except Exception as e:
                pytest.fail(f"Failed to test {service_name}: {e}")


@pytest.mark.asyncio
async def test_constitutional_hash_in_response_body():
    """Test that constitutional hash is present in response body."""
    async with aiohttp.ClientSession() as session:
        for service_name, service_config in SERVICES.items():
            url = f"{service_config['url']}/health"

            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        body_hash = data.get("constitutional_hash")

                        # Allow services to have hash in either body or headers
                        header_hash = response.headers.get("X-Constitutional-Hash")

                        assert (
                            body_hash == EXPECTED_CONSTITUTIONAL_HASH
                            or header_hash == EXPECTED_CONSTITUTIONAL_HASH
                        ), (
                            f"Service {service_name} missing constitutional hash in both body and headers: "
                            f"body={body_hash}, header={header_hash}, expected={EXPECTED_CONSTITUTIONAL_HASH}"
                        )
            except Exception as e:
                pytest.fail(f"Failed to test {service_name}: {e}")


if __name__ == "__main__":

    async def main():
        """Run constitutional hash validation tests."""
        async with ConstitutionalHashValidator() as validator:
            results = await validator.test_all_services()

            # Save results
            import json

            with open(
                "tests/results/constitutional_hash_validation_results.json", "w"
            ) as f:
                json.dump(results, f, indent=2)

            return results["summary"]["meets_target"]

    # Run the tests
    success = asyncio.run(main())
    exit(0 if success else 1)
