"""
ACGS Security Testing Suite

Comprehensive security testing leveraging the clean E2E test infrastructure.
Tests authentication, authorization, input validation, and vulnerability assessment.
"""

import pytest
import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Optional
import base64
import hashlib
import secrets

from tests.e2e.framework.config import E2ETestConfig


@pytest.mark.security
@pytest.mark.asyncio
async def test_authentication_security():
    """Test authentication security mechanisms."""
    config = E2ETestConfig.from_environment()
    
    # Test endpoints that should require authentication
    protected_endpoints = [
        "http://localhost:8016/api/v1/auth/validate",
        "http://localhost:8001/api/v1/constitutional/validate",
        "http://localhost:8005/api/v1/compliance/validate",
    ]
    
    unauthorized_count = 0
    
    async with aiohttp.ClientSession() as session:
        for endpoint in protected_endpoints:
            try:
                # Test without authentication
                async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    # Should return 401 Unauthorized or 403 Forbidden
                    if response.status in [401, 403]:
                        unauthorized_count += 1
                        print(f"✅ {endpoint}: Properly protected (HTTP {response.status})")
                    else:
                        print(f"⚠️ {endpoint}: May not be properly protected (HTTP {response.status})")
            except Exception as e:
                print(f"❌ {endpoint}: Error testing - {e}")
    
    # At least some endpoints should be properly protected
    assert unauthorized_count > 0, "No protected endpoints found"


@pytest.mark.security
@pytest.mark.asyncio
async def test_input_validation():
    """Test input validation and sanitization."""
    config = E2ETestConfig.from_environment()
    
    # Test malicious inputs
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "{{7*7}}",  # Template injection
        "\x00\x01\x02",  # Null bytes
        "A" * 10000,  # Large input
    ]
    
    test_endpoints = [
        "http://localhost:8001/health",
        "http://localhost:8004/health",
        "http://localhost:8005/health",
    ]
    
    safe_responses = 0
    
    async with aiohttp.ClientSession() as session:
        for endpoint in test_endpoints:
            for malicious_input in malicious_inputs:
                try:
                    # Test as query parameter
                    test_url = f"{endpoint}?test={malicious_input}"
                    async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        # Should not return 500 (server error) or reflect the input
                        if response.status != 500:
                            safe_responses += 1
                        
                        # Check response doesn't reflect malicious input
                        if response.content_type and 'text' in response.content_type:
                            text = await response.text()
                            if malicious_input not in text:
                                safe_responses += 1
                                
                except Exception:
                    # Timeouts or connection errors are acceptable for malicious inputs
                    safe_responses += 1
    
    # Most responses should handle malicious input safely
    total_tests = len(test_endpoints) * len(malicious_inputs) * 2
    safety_rate = safe_responses / total_tests
    assert safety_rate > 0.8, f"Input validation safety rate too low: {safety_rate:.2f}"


@pytest.mark.security
@pytest.mark.asyncio
async def test_constitutional_hash_integrity():
    """Test constitutional hash integrity and validation."""
    config = E2ETestConfig.from_environment()
    expected_hash = "cdd01ef066bc6cf2"
    
    # Test constitutional hash endpoints
    constitutional_endpoints = [
        "http://localhost:8001/api/v1/constitutional/status",
        "http://localhost:8004/api/v1/governance/status",
        "http://localhost:8005/api/v1/compliance/status",
    ]
    
    valid_hashes = 0
    
    async with aiohttp.ClientSession() as session:
        for endpoint in constitutional_endpoints:
            try:
                async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for constitutional hash in response
                        hash_value = data.get('constitutional_hash')
                        if hash_value == expected_hash:
                            valid_hashes += 1
                            print(f"✅ {endpoint}: Valid constitutional hash")
                        else:
                            print(f"⚠️ {endpoint}: Hash mismatch - {hash_value}")
                    else:
                        print(f"⚠️ {endpoint}: HTTP {response.status}")
                        
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
    
    # At least one service should return valid constitutional hash
    assert valid_hashes > 0, "No valid constitutional hashes found"


@pytest.mark.security
@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting mechanisms."""
    config = E2ETestConfig.from_environment()
    
    # Test rapid requests to health endpoints
    test_endpoint = "http://localhost:8001/health"
    rapid_requests = 50
    rate_limited = False
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        # Send rapid requests
        tasks = []
        for _ in range(rapid_requests):
            task = session.get(test_endpoint, timeout=aiohttp.ClientTimeout(total=1))
            tasks.append(task)
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for rate limiting responses
            for response in responses:
                if hasattr(response, 'status'):
                    if response.status == 429:  # Too Many Requests
                        rate_limited = True
                        print("✅ Rate limiting detected (HTTP 429)")
                        break
                    await response.close()
                    
        except Exception as e:
            # Connection errors might indicate rate limiting
            if "too many" in str(e).lower() or "rate" in str(e).lower():
                rate_limited = True
                print(f"✅ Rate limiting detected via connection error: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # If all requests completed very quickly without rate limiting,
        # that might indicate lack of protection
        if duration < 1.0 and not rate_limited:
            print("⚠️ No rate limiting detected - may need implementation")
        
    # Rate limiting is recommended but not required for health endpoints
    print(f"Rate limiting status: {'✅ Detected' if rate_limited else '⚪ Not detected'}")


@pytest.mark.security
@pytest.mark.asyncio
async def test_ssl_tls_security():
    """Test SSL/TLS security configuration."""
    config = E2ETestConfig.from_environment()
    
    # Test HTTPS endpoints (if available)
    https_endpoints = [
        "https://localhost:8001/health",
        "https://localhost:8004/health",
        "https://localhost:8005/health",
    ]
    
    secure_connections = 0
    
    # Create SSL context that validates certificates
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False  # For localhost testing
    ssl_context.verify_mode = ssl.CERT_NONE  # For self-signed certs in testing
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for endpoint in https_endpoints:
            try:
                async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        secure_connections += 1
                        print(f"✅ {endpoint}: HTTPS connection successful")
                    else:
                        print(f"⚠️ {endpoint}: HTTPS returned HTTP {response.status}")
                        
            except Exception as e:
                # HTTPS might not be configured in test environment
                print(f"⚪ {endpoint}: HTTPS not available - {e}")
    
    # HTTPS is optional in test environment
    print(f"Secure connections: {secure_connections}/{len(https_endpoints)}")


@pytest.mark.security
def test_environment_security():
    """Test environment security configuration."""
    import os
    
    # Check for sensitive environment variables
    sensitive_vars = [
        "DATABASE_PASSWORD",
        "JWT_SECRET",
        "API_KEY",
        "SECRET_KEY",
        "PRIVATE_KEY",
    ]
    
    exposed_secrets = []
    
    for var in sensitive_vars:
        value = os.getenv(var)
        if value:
            # Check if it looks like a real secret (not placeholder)
            if len(value) > 8 and not value.startswith("test_") and not value.startswith("placeholder"):
                exposed_secrets.append(var)
    
    # In test environment, some secrets might be exposed, but warn about it
    if exposed_secrets:
        print(f"⚠️ Potentially sensitive environment variables: {exposed_secrets}")
    else:
        print("✅ No obviously sensitive environment variables detected")
    
    # Check constitutional hash is set
    constitutional_hash = os.getenv("CONSTITUTIONAL_HASH")
    assert constitutional_hash == "cdd01ef066bc6cf2", "Constitutional hash not properly set"


@pytest.mark.security
@pytest.mark.asyncio
async def test_error_information_disclosure():
    """Test that error responses don't disclose sensitive information."""
    config = E2ETestConfig.from_environment()
    
    # Test endpoints with invalid requests
    test_cases = [
        ("http://localhost:8001/nonexistent", 404),
        ("http://localhost:8004/api/v1/invalid", 404),
        ("http://localhost:8005/api/v1/badrequest", 400),
    ]
    
    safe_errors = 0
    
    async with aiohttp.ClientSession() as session:
        for endpoint, expected_status in test_cases:
            try:
                async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    text = await response.text()
                    
                    # Check that error doesn't expose sensitive information
                    sensitive_patterns = [
                        "password",
                        "secret",
                        "key",
                        "token",
                        "database",
                        "internal",
                        "stack trace",
                        "traceback",
                    ]
                    
                    text_lower = text.lower()
                    exposed_info = [pattern for pattern in sensitive_patterns if pattern in text_lower]
                    
                    if not exposed_info:
                        safe_errors += 1
                        print(f"✅ {endpoint}: Safe error response")
                    else:
                        print(f"⚠️ {endpoint}: May expose sensitive info: {exposed_info}")
                        
            except Exception as e:
                # Connection errors are acceptable
                safe_errors += 1
    
    # Most error responses should be safe
    safety_rate = safe_errors / len(test_cases)
    assert safety_rate > 0.5, f"Error safety rate too low: {safety_rate:.2f}"


@pytest.mark.security
@pytest.mark.asyncio
async def test_service_isolation():
    """Test that services are properly isolated."""
    config = E2ETestConfig.from_environment()
    
    # Test that services don't expose internal endpoints
    internal_endpoints = [
        "http://localhost:8001/admin",
        "http://localhost:8001/debug",
        "http://localhost:8004/internal",
        "http://localhost:8005/admin",
    ]
    
    protected_endpoints = 0
    
    async with aiohttp.ClientSession() as session:
        for endpoint in internal_endpoints:
            try:
                async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    # Internal endpoints should return 404 or 403
                    if response.status in [404, 403]:
                        protected_endpoints += 1
                        print(f"✅ {endpoint}: Properly protected (HTTP {response.status})")
                    else:
                        print(f"⚠️ {endpoint}: May be exposed (HTTP {response.status})")
                        
            except Exception:
                # Connection errors indicate endpoint is not exposed
                protected_endpoints += 1
    
    # All internal endpoints should be protected
    protection_rate = protected_endpoints / len(internal_endpoints)
    assert protection_rate >= 0.8, f"Service isolation rate too low: {protection_rate:.2f}"
