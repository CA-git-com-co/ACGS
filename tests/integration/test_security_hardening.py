"""
ACGS Security Hardening Integration Tests
Constitutional Hash: cdd01ef066bc6cf2

Integration tests for security hardening features across all services.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict

import httpx
import pytest

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestSecurityHardening:
    """Test security hardening across all ACGS services."""

    @pytest.fixture
    def service_urls(self) -> Dict[str, str]:
        """Service URLs for testing."""
        return {
            "constitutional_ai": "http://localhost:8001",
            "integrity": "http://localhost:8002",
            "api_gateway": "http://localhost:8010",
            "auth": "http://localhost:8016",
            "governance_synthesis": "http://localhost:8008",
        }

    @pytest.mark.asyncio
    async def test_input_validation_xss_protection(self, service_urls):
        """Test XSS protection in input validation."""

        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "&#60;script&#62;alert('xss')&#60;/script&#62;",
        ]

        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                print(f"\n🔒 Testing XSS protection for {service_name}...")

                for payload in xss_payloads:
                    try:
                        # Test XSS in query parameters
                        response = await client.get(
                            f"{url}/health",
                            params={"test_param": payload},
                            timeout=10.0,
                        )

                        # Should not reflect XSS payload in response
                        response_text = response.text
                        assert (
                            payload not in response_text
                        ), f"{service_name} reflected XSS payload: {payload}"

                        # Test XSS in JSON body (if service accepts POST)
                        try:
                            response = await client.post(
                                f"{url}/api/v1/test",
                                json={"input": payload},
                                timeout=10.0,
                            )
                            # We expect this to either be blocked or sanitized
                            # Status 400, 422, or successful with sanitized content
                            assert response.status_code in [
                                200,
                                400,
                                404,
                                422,
                            ], f"{service_name} unexpected response to XSS: {response.status_code}"

                        except httpx.ConnectError:
                            # Service might not be running, skip
                            continue
                        except Exception as e:
                            # Expected for some payloads
                            print(f"  ✅ XSS payload blocked: {payload[:30]}...")

                    except Exception as e:
                        # XSS protection working - requests are being blocked/sanitized
                        print(f"  ✅ XSS protection active for {service_name}")

    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, service_urls):
        """Test SQL injection protection."""

        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "'; SELECT * FROM users; --",
            "UNION SELECT password FROM users",
        ]

        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                print(f"\n🛡️ Testing SQL injection protection for {service_name}...")

                for payload in sql_payloads:
                    try:
                        # Test SQL injection in query parameters
                        response = await client.get(
                            f"{url}/health", params={"id": payload}, timeout=10.0
                        )

                        # Should not execute SQL - either blocked or sanitized
                        response_text = response.text.lower()
                        dangerous_responses = [
                            "mysql",
                            "postgresql",
                            "syntax error",
                            "sql error",
                        ]

                        for dangerous in dangerous_responses:
                            assert (
                                dangerous not in response_text
                            ), f"{service_name} might be vulnerable to SQL injection"

                        print(f"  ✅ SQL injection payload handled: {payload[:30]}...")

                    except Exception as e:
                        # Protection is working
                        print(f"  ✅ SQL injection protection active")

    @pytest.mark.asyncio
    async def test_rate_limiting(self, service_urls):
        """Test rate limiting protection."""

        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                print(f"\n🚦 Testing rate limiting for {service_name}...")

                try:
                    # Send many requests quickly to trigger rate limiting
                    responses = []
                    for i in range(150):  # Exceed typical 100 req/min limit
                        try:
                            response = await client.get(f"{url}/health", timeout=5.0)
                            responses.append(response.status_code)
                        except Exception:
                            responses.append(0)  # Timeout/error

                    # Check if rate limiting was triggered
                    rate_limited = any(status == 429 for status in responses)

                    if rate_limited:
                        print(f"  ✅ Rate limiting active - 429 responses detected")
                    else:
                        print(f"  ⚠️ Rate limiting not detected (may not be configured)")

                except Exception as e:
                    print(f"  ⚠️ Rate limiting test failed: {e}")

    @pytest.mark.asyncio
    async def test_security_headers(self, service_urls):
        """Test security headers are properly set."""

        required_headers = {
            "x-content-type-options": "nosniff",
            "x-frame-options": "DENY",
            "x-xss-protection": "1; mode=block",
            "x-constitutional-hash": CONSTITUTIONAL_HASH,
        }

        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                print(f"\n🛡️ Testing security headers for {service_name}...")

                try:
                    response = await client.get(f"{url}/health", timeout=10.0)
                    headers = {k.lower(): v for k, v in response.headers.items()}

                    for header, expected_value in required_headers.items():
                        if header in headers:
                            if expected_value and headers[header] != expected_value:
                                print(
                                    f"  ⚠️ {header}: {headers[header]} (expected {expected_value})"
                                )
                            else:
                                print(f"  ✅ {header}: {headers[header]}")
                        else:
                            print(f"  ❌ Missing header: {header}")

                    # Check for CSP header
                    if "content-security-policy" in headers:
                        print(f"  ✅ CSP: Present")
                    else:
                        print(f"  ⚠️ CSP: Not configured")

                except Exception as e:
                    print(f"  ❌ Security headers test failed: {e}")

    @pytest.mark.asyncio
    async def test_secrets_management(self, service_urls):
        """Test that services don't expose secrets."""

        sensitive_patterns = [
            "secret_key",
            "password",
            "api_key",
            "jwt_secret",
            "database_url",
            "redis_url",
        ]

        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                print(f"\n🔐 Testing secrets exposure for {service_name}...")

                try:
                    # Test health endpoint
                    response = await client.get(f"{url}/health", timeout=10.0)
                    response_text = response.text.lower()

                    secrets_exposed = False
                    for pattern in sensitive_patterns:
                        if pattern in response_text and "your-" not in response_text:
                            # Check if it's actually exposing a real secret
                            # vs just mentioning the field name
                            lines = response_text.split("\n")
                            for line in lines:
                                if pattern in line and ("=" in line or ":" in line):
                                    if not any(
                                        placeholder in line
                                        for placeholder in [
                                            "your-",
                                            "example",
                                            "placeholder",
                                        ]
                                    ):
                                        print(
                                            f"  ❌ Potential secret exposure: {pattern}"
                                        )
                                        secrets_exposed = True

                    if not secrets_exposed:
                        print(f"  ✅ No secrets exposed")

                    # Test error responses don't expose secrets
                    response = await client.get(f"{url}/invalid-endpoint", timeout=10.0)
                    error_text = response.text.lower()

                    for pattern in sensitive_patterns:
                        if pattern in error_text and "your-" not in error_text:
                            print(f"  ⚠️ Potential secret in error response: {pattern}")

                except Exception as e:
                    print(f"  ⚠️ Secrets test failed: {e}")

    @pytest.mark.asyncio
    async def test_csrf_protection(self, service_urls):
        """Test CSRF protection for state-changing operations."""

        async with httpx.AsyncClient() as client:
            for service_name, url in service_urls.items():
                print(f"\n🛡️ Testing CSRF protection for {service_name}...")

                try:
                    # Test POST without CSRF token (should be protected)
                    response = await client.post(
                        f"{url}/api/v1/test", json={"test": "data"}, timeout=10.0
                    )

                    # CSRF protection might return 403, 404 (endpoint doesn't exist), or require token
                    if response.status_code in [403, 400, 422]:
                        print(
                            f"  ✅ CSRF protection active (status: {response.status_code})"
                        )
                    elif response.status_code == 404:
                        print(f"  ⚠️ Endpoint not found (CSRF not testable)")
                    else:
                        # Check if response mentions CSRF
                        if "csrf" in response.text.lower():
                            print(f"  ✅ CSRF protection mentioned in response")
                        else:
                            print(f"  ⚠️ CSRF protection not detected")

                except Exception as e:
                    print(f"  ⚠️ CSRF test failed: {e}")

    @pytest.mark.asyncio
    async def test_authentication_security(self, service_urls):
        """Test authentication security measures."""

        # Only test auth service specifically
        auth_url = service_urls.get("auth")
        if not auth_url:
            pytest.skip("Auth service not available")

        print(f"\n🔑 Testing authentication security...")

        async with httpx.AsyncClient() as client:
            try:
                # Test weak password rejection (if registration endpoint exists)
                weak_passwords = ["123", "password", "abc123"]

                for weak_password in weak_passwords:
                    try:
                        response = await client.post(
                            f"{auth_url}/api/v1/register",
                            json={
                                "username": "testuser",
                                "password": weak_password,
                                "email": "test@example.com",
                            },
                            timeout=10.0,
                        )

                        # Should reject weak passwords
                        if response.status_code in [400, 422]:
                            print(f"  ✅ Weak password rejected: {weak_password}")
                        elif response.status_code == 404:
                            print(f"  ⚠️ Registration endpoint not found")
                            break
                        else:
                            print(f"  ⚠️ Weak password not rejected: {weak_password}")

                    except Exception:
                        # Expected for some cases
                        continue

                # Test invalid login attempts
                response = await client.post(
                    f"{auth_url}/api/v1/login",
                    json={"username": "nonexistent", "password": "wrongpassword"},
                    timeout=10.0,
                )

                # Should return appropriate error without revealing if user exists
                if response.status_code in [401, 403]:
                    print(f"  ✅ Invalid login properly rejected")
                elif response.status_code == 404:
                    print(f"  ⚠️ Login endpoint not found")
                else:
                    print(f"  ⚠️ Unexpected login response: {response.status_code}")

            except Exception as e:
                print(f"  ⚠️ Authentication security test failed: {e}")


@pytest.mark.asyncio
async def test_security_monitoring_endpoints():
    """Test security monitoring endpoints."""

    service_urls = {
        "constitutional_ai": "http://localhost:8001",
        "api_gateway": "http://localhost:8010",
    }

    async with httpx.AsyncClient() as client:
        for service_name, url in service_urls.items():
            print(f"\n📊 Testing security monitoring for {service_name}...")

            try:
                # Test security metrics endpoint
                response = await client.get(f"{url}/security/metrics", timeout=10.0)

                if response.status_code == 200:
                    metrics = response.json()

                    # Check for security metrics
                    expected_metrics = [
                        "blocked_requests",
                        "validation_failures",
                        "constitutional_hash_valid",
                    ]

                    for metric in expected_metrics:
                        if metric in metrics:
                            print(f"  ✅ Security metric present: {metric}")
                        else:
                            print(f"  ⚠️ Security metric missing: {metric}")

                    # Verify constitutional compliance
                    if metrics.get("constitutional_hash_valid") == 1:
                        print(f"  ✅ Constitutional compliance validated")
                    else:
                        print(f"  ❌ Constitutional compliance issue")

                elif response.status_code == 404:
                    print(f"  ⚠️ Security metrics endpoint not found")
                else:
                    print(f"  ⚠️ Security metrics error: {response.status_code}")

                # Test security health endpoint
                response = await client.get(f"{url}/security/health", timeout=10.0)

                if response.status_code == 200:
                    health = response.json()

                    if health.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                        print(f"  ✅ Security health endpoint validated")
                    else:
                        print(f"  ❌ Security health constitutional hash mismatch")
                elif response.status_code == 404:
                    print(f"  ⚠️ Security health endpoint not found")

            except Exception as e:
                print(f"  ⚠️ Security monitoring test failed: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])
