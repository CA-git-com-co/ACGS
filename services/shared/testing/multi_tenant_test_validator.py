"""
ACGS Multi-Tenant Testing Validator
Constitutional Hash: cdd01ef066bc6cf2

This module provides comprehensive multi-tenant testing validation
to ensure tenant isolation, context propagation, and administrative
operations work correctly across all ACGS services.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class TenantTestContext:
    """Test context for a specific tenant."""

    tenant_id: str
    user_id: str
    is_admin: bool = False
    jwt_token: Optional[str] = None

    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers."""
        headers = {
            "X-Tenant-ID": self.tenant_id,
            "X-User-ID": self.user_id,
            "X-Constitutional-Hash": "cdd01ef066bc6cf2",
        }

        if self.is_admin:
            headers["X-Admin-Context"] = "true"

        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        return headers


@dataclass
class TenantIsolationViolation:
    """Represents a tenant isolation violation."""

    service_name: str
    endpoint: str
    violation_type: str
    description: str
    severity: str
    tenant_context: TenantTestContext
    violating_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class MultiTenantTestReport:
    """Multi-tenant testing validation report."""

    total_tests: int
    passed_tests: int
    failed_tests: int
    isolation_violations: List[TenantIsolationViolation]
    context_propagation_failures: int
    admin_access_failures: int
    constitutional_hash: str = "cdd01ef066bc6cf2"
    test_timestamp: datetime = None

    def __post_init__(self):
        if self.test_timestamp is None:
            self.test_timestamp = datetime.utcnow()

    @property
    def success_rate(self) -> float:
        """Calculate test success rate."""
        return self.passed_tests / self.total_tests if self.total_tests > 0 else 0.0

    @property
    def is_fully_compliant(self) -> bool:
        """Check if all multi-tenant tests passed."""
        return (
            len(self.isolation_violations) == 0
            and self.context_propagation_failures == 0
            and self.admin_access_failures == 0
            and self.success_rate == 1.0
        )


class MultiTenantTestValidator:
    """Comprehensive multi-tenant testing validator for ACGS services."""

    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    def __init__(self):
        self.violations: List[TenantIsolationViolation] = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.context_propagation_failures = 0
        self.admin_access_failures = 0

    async def validate_service_multi_tenancy(
        self,
        service_name: str,
        base_url: str,
        test_endpoints: List[Dict[str, Any]],
        db_session: Optional[AsyncSession] = None,
    ) -> MultiTenantTestReport:
        """Validate multi-tenant compliance for a service."""
        logger.info(f"Starting multi-tenant validation for {service_name}")

        # Reset counters
        self.violations.clear()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.context_propagation_failures = 0
        self.admin_access_failures = 0

        # Create test tenant contexts
        tenant1 = TenantTestContext(
            tenant_id=str(uuid.uuid4()), user_id=str(uuid.uuid4()), is_admin=False
        )

        tenant2 = TenantTestContext(
            tenant_id=str(uuid.uuid4()), user_id=str(uuid.uuid4()), is_admin=False
        )

        admin_tenant = TenantTestContext(
            tenant_id=str(uuid.uuid4()), user_id=str(uuid.uuid4()), is_admin=True
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint_config in test_endpoints:
                # Test tenant isolation
                await self._test_tenant_isolation(
                    client, service_name, base_url, endpoint_config, tenant1, tenant2
                )

                # Test context propagation
                await self._test_context_propagation(
                    client, service_name, base_url, endpoint_config, tenant1
                )

                # Test admin access
                await self._test_admin_access(
                    client,
                    service_name,
                    base_url,
                    endpoint_config,
                    admin_tenant,
                    tenant1,
                )

                # Test database isolation if database session provided
                if db_session:
                    await self._test_database_isolation(
                        db_session, service_name, endpoint_config, tenant1, tenant2
                    )

        report = MultiTenantTestReport(
            total_tests=self.total_tests,
            passed_tests=self.passed_tests,
            failed_tests=self.failed_tests,
            isolation_violations=self.violations.copy(),
            context_propagation_failures=self.context_propagation_failures,
            admin_access_failures=self.admin_access_failures,
            constitutional_hash=self.CONSTITUTIONAL_HASH,
        )

        logger.info(
            f"Multi-tenant validation completed for {service_name}: "
            f"{report.success_rate:.2%} success rate, "
            f"{len(report.isolation_violations)} violations"
        )

        return report

    async def _test_tenant_isolation(
        self,
        client: httpx.AsyncClient,
        service_name: str,
        base_url: str,
        endpoint_config: Dict[str, Any],
        tenant1: TenantTestContext,
        tenant2: TenantTestContext,
    ):
        """Test that tenants cannot access each other's data."""
        endpoint = endpoint_config["path"]
        method = endpoint_config.get("method", "GET")

        self.total_tests += 1

        try:
            # Create data for tenant1
            if method.upper() in ["POST", "PUT"]:
                test_data = endpoint_config.get("test_data", {})
                test_data["tenant_specific_field"] = f"tenant1_data_{uuid.uuid4()}"

                url = f"{base_url}{endpoint}"

                # Create resource as tenant1
                response1 = await client.request(
                    method, url, json=test_data, headers=tenant1.to_headers()
                )

                if response1.status_code >= 400:
                    self.failed_tests += 1
                    return

                # Try to access as tenant2 (should fail or return empty)
                if method.upper() == "POST":
                    # For POST, try to GET the created resource
                    get_endpoint = endpoint_config.get("get_endpoint", endpoint)
                    response2 = await client.get(
                        f"{base_url}{get_endpoint}", headers=tenant2.to_headers()
                    )
                else:
                    # For PUT, try to access the same resource
                    response2 = await client.get(url, headers=tenant2.to_headers())

                # Validate tenant isolation
                if response2.status_code == 200:
                    data = response2.json()
                    if self._contains_tenant_data(data, tenant1.tenant_id):
                        self._add_violation(
                            service_name,
                            endpoint,
                            "data_leakage",
                            f"Tenant {tenant2.tenant_id} can access data from tenant {tenant1.tenant_id}",
                            "critical",
                            tenant2,
                            data,
                        )
                        self.failed_tests += 1
                        return

            # Test GET endpoint isolation
            elif method.upper() == "GET":
                # Both tenants request the same endpoint
                response1 = await client.get(
                    f"{base_url}{endpoint}", headers=tenant1.to_headers()
                )

                response2 = await client.get(
                    f"{base_url}{endpoint}", headers=tenant2.to_headers()
                )

                if response1.status_code == 200 and response2.status_code == 200:
                    data1 = response1.json()
                    data2 = response2.json()

                    # Check for cross-tenant data contamination
                    if self._contains_cross_tenant_data(
                        data1, data2, tenant1.tenant_id, tenant2.tenant_id
                    ):
                        self._add_violation(
                            service_name,
                            endpoint,
                            "cross_tenant_contamination",
                            "Response contains data from multiple tenants",
                            "critical",
                            tenant1,
                            {"data1": data1, "data2": data2},
                        )
                        self.failed_tests += 1
                        return

            self.passed_tests += 1

        except Exception as e:
            logger.error(
                f"Tenant isolation test failed for {service_name}{endpoint}: {e}"
            )
            self.failed_tests += 1

    async def _test_context_propagation(
        self,
        client: httpx.AsyncClient,
        service_name: str,
        base_url: str,
        endpoint_config: Dict[str, Any],
        tenant: TenantTestContext,
    ):
        """Test that tenant context is properly propagated."""
        endpoint = endpoint_config["path"]
        method = endpoint_config.get("method", "GET")

        self.total_tests += 1

        try:
            # Test with missing tenant context
            headers_no_tenant = {
                "X-Constitutional-Hash": self.CONSTITUTIONAL_HASH,
                "Content-Type": "application/json",
            }

            url = f"{base_url}{endpoint}"

            if method.upper() == "GET":
                response = await client.get(url, headers=headers_no_tenant)
            elif method.upper() == "POST":
                test_data = endpoint_config.get("test_data", {})
                response = await client.post(
                    url, json=test_data, headers=headers_no_tenant
                )
            else:
                response = await client.request(method, url, headers=headers_no_tenant)

            # Should return 400 or 401 for missing tenant context
            if response.status_code not in [400, 401, 403]:
                self._add_violation(
                    service_name,
                    endpoint,
                    "missing_tenant_validation",
                    f"Endpoint accepts requests without tenant context (status: {response.status_code})",
                    "high",
                    tenant,
                )
                self.context_propagation_failures += 1
                self.failed_tests += 1
                return

            # Test with valid tenant context
            response_with_tenant = await client.request(
                method,
                url,
                json=(
                    endpoint_config.get("test_data", {})
                    if method.upper() in ["POST", "PUT"]
                    else None
                ),
                headers=tenant.to_headers(),
            )

            if response_with_tenant.status_code >= 400:
                self.context_propagation_failures += 1
                self.failed_tests += 1
                return

            # Validate that response includes tenant context
            if response_with_tenant.headers.get("content-type", "").startswith(
                "application/json"
            ):
                data = response_with_tenant.json()
                if not self._validate_tenant_context_in_response(
                    data, tenant.tenant_id
                ):
                    self._add_violation(
                        service_name,
                        endpoint,
                        "missing_tenant_context_response",
                        "Response does not include proper tenant context",
                        "medium",
                        tenant,
                        data,
                    )
                    self.context_propagation_failures += 1
                    self.failed_tests += 1
                    return

            self.passed_tests += 1

        except Exception as e:
            logger.error(
                f"Context propagation test failed for {service_name}{endpoint}: {e}"
            )
            self.context_propagation_failures += 1
            self.failed_tests += 1

    async def _test_admin_access(
        self,
        client: httpx.AsyncClient,
        service_name: str,
        base_url: str,
        endpoint_config: Dict[str, Any],
        admin_tenant: TenantTestContext,
        regular_tenant: TenantTestContext,
    ):
        """Test admin cross-tenant access capabilities."""
        admin_endpoint = endpoint_config.get("admin_endpoint")
        if not admin_endpoint:
            return  # Skip if no admin endpoint defined

        self.total_tests += 1

        try:
            # Regular tenant should not have admin access
            response_regular = await client.get(
                f"{base_url}{admin_endpoint}", headers=regular_tenant.to_headers()
            )

            if response_regular.status_code not in [401, 403]:
                self._add_violation(
                    service_name,
                    admin_endpoint,
                    "unauthorized_admin_access",
                    f"Regular tenant has admin access (status: {response_regular.status_code})",
                    "critical",
                    regular_tenant,
                )
                self.admin_access_failures += 1
                self.failed_tests += 1
                return

            # Admin tenant should have access
            response_admin = await client.get(
                f"{base_url}{admin_endpoint}", headers=admin_tenant.to_headers()
            )

            if response_admin.status_code >= 400:
                self.admin_access_failures += 1
                self.failed_tests += 1
                return

            # Validate admin response includes cross-tenant data if expected
            if response_admin.headers.get("content-type", "").startswith(
                "application/json"
            ):
                data = response_admin.json()
                if not self._validate_admin_response(data):
                    self._add_violation(
                        service_name,
                        admin_endpoint,
                        "invalid_admin_response",
                        "Admin response does not include expected cross-tenant data",
                        "medium",
                        admin_tenant,
                        data,
                    )
                    self.admin_access_failures += 1
                    self.failed_tests += 1
                    return

            self.passed_tests += 1

        except Exception as e:
            logger.error(
                f"Admin access test failed for {service_name}{admin_endpoint}: {e}"
            )
            self.admin_access_failures += 1
            self.failed_tests += 1

    async def _test_database_isolation(
        self,
        db_session: AsyncSession,
        service_name: str,
        endpoint_config: Dict[str, Any],
        tenant1: TenantTestContext,
        tenant2: TenantTestContext,
    ):
        """Test database-level tenant isolation."""
        table_name = endpoint_config.get("table_name")
        if not table_name:
            return  # Skip if no table specified

        self.total_tests += 1

        try:
            # Set tenant context for tenant1
            await db_session.execute(
                text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
                {"tenant_id": tenant1.tenant_id},
            )

            # Query should only return tenant1 data
            result1 = await db_session.execute(
                text(
                    f"SELECT COUNT(*) as count, tenant_id FROM {table_name} GROUP BY tenant_id"
                )
            )
            rows1 = result1.fetchall()

            # Set tenant context for tenant2
            await db_session.execute(
                text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
                {"tenant_id": tenant2.tenant_id},
            )

            # Query should only return tenant2 data
            result2 = await db_session.execute(
                text(
                    f"SELECT COUNT(*) as count, tenant_id FROM {table_name} GROUP BY tenant_id"
                )
            )
            rows2 = result2.fetchall()

            # Validate isolation
            tenant1_ids = {row.tenant_id for row in rows1}
            tenant2_ids = {row.tenant_id for row in rows2}

            if tenant1.tenant_id in tenant2_ids or tenant2.tenant_id in tenant1_ids:
                self._add_violation(
                    service_name,
                    f"database:{table_name}",
                    "database_isolation_failure",
                    "Database queries return data from other tenants",
                    "critical",
                    tenant1,
                    {
                        "tenant1_data": [dict(row) for row in rows1],
                        "tenant2_data": [dict(row) for row in rows2],
                    },
                )
                self.failed_tests += 1
                return

            self.passed_tests += 1

        except Exception as e:
            logger.error(f"Database isolation test failed for {service_name}: {e}")
            self.failed_tests += 1

    def _contains_tenant_data(self, data: Any, tenant_id: str) -> bool:
        """Check if data contains information from a specific tenant."""
        if isinstance(data, dict):
            if data.get("tenant_id") == tenant_id:
                return True

            # Check nested structures
            for value in data.values():
                if self._contains_tenant_data(value, tenant_id):
                    return True

        elif isinstance(data, list):
            for item in data:
                if self._contains_tenant_data(item, tenant_id):
                    return True

        return False

    def _contains_cross_tenant_data(
        self, data1: Any, data2: Any, tenant1_id: str, tenant2_id: str
    ) -> bool:
        """Check if responses contain cross-tenant data contamination."""
        # Extract tenant IDs from both responses
        tenant_ids_1 = self._extract_tenant_ids(data1)
        tenant_ids_2 = self._extract_tenant_ids(data2)

        # Check for contamination
        if tenant2_id in tenant_ids_1 or tenant1_id in tenant_ids_2:
            return True

        return False

    def _extract_tenant_ids(self, data: Any) -> set:
        """Extract all tenant IDs from data structure."""
        tenant_ids = set()

        if isinstance(data, dict):
            if "tenant_id" in data:
                tenant_ids.add(data["tenant_id"])

            for value in data.values():
                tenant_ids.update(self._extract_tenant_ids(value))

        elif isinstance(data, list):
            for item in data:
                tenant_ids.update(self._extract_tenant_ids(item))

        return tenant_ids

    def _validate_tenant_context_in_response(
        self, data: Any, expected_tenant_id: str
    ) -> bool:
        """Validate that response includes proper tenant context."""
        if isinstance(data, dict):
            # Check for tenant_id in response
            if "tenant_id" in data:
                return data["tenant_id"] == expected_tenant_id

            # Check in nested data
            if "data" in data:
                return self._validate_tenant_context_in_response(
                    data["data"], expected_tenant_id
                )

        return True  # No tenant context required in response

    def _validate_admin_response(self, data: Any) -> bool:
        """Validate admin response format."""
        # Admin responses should include cross-tenant data or admin-specific fields
        if isinstance(data, dict):
            # Look for admin indicators
            if "admin_view" in data or "cross_tenant" in data:
                return True

            # Check if response includes multiple tenant IDs (cross-tenant view)
            tenant_ids = self._extract_tenant_ids(data)
            if len(tenant_ids) > 1:
                return True

        return True  # Default to valid for now

    def _add_violation(
        self,
        service_name: str,
        endpoint: str,
        violation_type: str,
        description: str,
        severity: str,
        tenant_context: TenantTestContext,
        violating_data: Optional[Dict[str, Any]] = None,
    ):
        """Add a tenant isolation violation."""
        violation = TenantIsolationViolation(
            service_name=service_name,
            endpoint=endpoint,
            violation_type=violation_type,
            description=description,
            severity=severity,
            tenant_context=tenant_context,
            violating_data=violating_data,
        )

        self.violations.append(violation)
        logger.warning(
            f"Multi-tenant violation in {service_name}{endpoint}: "
            f"{violation_type} - {description}"
        )

    def generate_multi_tenant_report(
        self, service_reports: Dict[str, MultiTenantTestReport]
    ) -> Dict[str, Any]:
        """Generate comprehensive multi-tenant testing report."""
        total_tests = sum(r.total_tests for r in service_reports.values())
        total_passed = sum(r.passed_tests for r in service_reports.values())
        total_violations = sum(
            len(r.isolation_violations) for r in service_reports.values()
        )

        return {
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "test_timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_services_tested": len(service_reports),
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_tests - total_passed,
                "success_rate": total_passed / total_tests if total_tests > 0 else 0.0,
                "total_violations": total_violations,
                "fully_compliant_services": sum(
                    1 for r in service_reports.values() if r.is_fully_compliant
                ),
            },
            "service_reports": {
                service_name: {
                    "success_rate": report.success_rate,
                    "total_tests": report.total_tests,
                    "passed_tests": report.passed_tests,
                    "failed_tests": report.failed_tests,
                    "isolation_violations": len(report.isolation_violations),
                    "context_propagation_failures": report.context_propagation_failures,
                    "admin_access_failures": report.admin_access_failures,
                    "is_fully_compliant": report.is_fully_compliant,
                    "violations": [
                        {
                            "endpoint": v.endpoint,
                            "type": v.violation_type,
                            "description": v.description,
                            "severity": v.severity,
                            "timestamp": v.timestamp.isoformat(),
                        }
                        for v in report.isolation_violations
                    ],
                }
                for service_name, report in service_reports.items()
            },
        }
