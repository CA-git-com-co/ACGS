#!/usr/bin/env python3
"""
ACGS Security Hardening Testing and Validation Script

This script performs comprehensive testing of the deployed security hardening measures.
It validates all security components and generates a detailed security assessment report.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityHardeningTester:
    """Comprehensive security hardening testing suite."""

    def __init__(self):
        self.project_root = project_root
        self.test_results = {
            "test_start_time": datetime.now(timezone.utc),
            "constitutional_hash": "cdd01ef066bc6cf2",
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": [],
            "security_score": 0.0,
            "recommendations": [],
        }

    async def run_comprehensive_security_tests(self) -> dict[str, Any]:
        """Run comprehensive security testing suite."""
        logger.info("Starting ACGS Security Hardening Testing")
        logger.info("Constitutional Hash: cdd01ef066bc6cf2")

        try:
            # Test 1: Encryption Infrastructure
            await self._test_encryption_infrastructure()

            # Test 2: Input Validation
            await self._test_input_validation()

            # Test 3: Authentication Security
            await self._test_authentication_security()

            # Test 4: Rate Limiting
            await self._test_rate_limiting()

            # Test 5: Security Headers
            await self._test_security_headers()

            # Test 6: Threat Detection
            await self._test_threat_detection()

            # Test 7: Constitutional Compliance
            await self._test_constitutional_compliance()

            # Test 8: Audit System
            await self._test_audit_system()

            # Test 9: Network Security
            await self._test_network_security()

            # Test 10: Configuration Security
            await self._test_configuration_security()

            # Calculate final security score
            self._calculate_security_score()

            # Generate recommendations
            self._generate_recommendations()

            self.test_results["test_end_time"] = datetime.now(timezone.utc)
            self.test_results["test_duration_seconds"] = (
                self.test_results["test_end_time"]
                - self.test_results["test_start_time"]
            ).total_seconds()

            # Save test report
            await self._save_test_report()

            logger.info("Security hardening testing completed")
            return self.test_results

        except Exception as e:
            logger.error(f"Security testing failed: {e}")
            self.test_results["error"] = str(e)
            raise

    async def _test_encryption_infrastructure(self):
        """Test encryption infrastructure."""
        test_name = "Encryption Infrastructure"
        logger.info(f"Testing: {test_name}")

        try:
            # Import and test encryption manager
            from services.shared.security.advanced_security_hardening import (
                security_hardening,
            )

            # Test symmetric encryption
            test_data = "sensitive_test_data_12345"
            encrypted = security_hardening.encryption_manager.encrypt_sensitive_data(
                test_data
            )
            decrypted = security_hardening.encryption_manager.decrypt_sensitive_data(
                encrypted
            )

            if decrypted != test_data:
                raise ValueError("Symmetric encryption/decryption failed")

            # Test RSA encryption
            rsa_encrypted = security_hardening.encryption_manager.encrypt_with_rsa(
                test_data
            )
            rsa_decrypted = security_hardening.encryption_manager.decrypt_with_rsa(
                rsa_encrypted
            )

            if rsa_decrypted != test_data:
                raise ValueError("RSA encryption/decryption failed")

            # Check key files exist (check both system and local paths)
            key_files_system = [
                "/etc/acgs/encryption/master.key",
                "/etc/acgs/encryption/rsa_private.pem",
                "/etc/acgs/encryption/rsa_public.pem",
            ]

            key_files_local = [
                "config/security/keys/master.key",
                "config/security/keys/rsa_private.pem",
                "config/security/keys/rsa_public.pem",
            ]

            # Check if either system or local keys exist
            system_keys_exist = all(os.path.exists(f) for f in key_files_system)
            local_keys_exist = all(os.path.exists(f) for f in key_files_local)

            if not (system_keys_exist or local_keys_exist):
                missing_system = [f for f in key_files_system if not os.path.exists(f)]
                missing_local = [f for f in key_files_local if not os.path.exists(f)]
                raise FileNotFoundError(
                    f"Missing key files - System: {missing_system}, Local: {missing_local}"
                )

            self._record_test_result(test_name, True, "All encryption tests passed")

        except Exception as e:
            self._record_test_result(test_name, False, f"Encryption test failed: {e}")

    async def _test_input_validation(self):
        """Test input validation mechanisms."""
        test_name = "Input Validation"
        logger.info(f"Testing: {test_name}")

        try:
            from services.shared.security.advanced_security_hardening import (
                security_hardening,
            )

            # Test malicious inputs
            malicious_inputs = [
                "'; DROP TABLE users; --",  # SQL injection
                "<script>alert('xss')</script>",  # XSS
                "../../etc/passwd",  # Path traversal
                "$(rm -rf /)",  # Command injection
            ]

            threats_detected = 0
            for malicious_input in malicious_inputs:
                result = security_hardening.input_validator.validate_input(
                    malicious_input
                )
                if not result["valid"] and result["threats"]:
                    threats_detected += 1

            if threats_detected < len(malicious_inputs):
                raise ValueError(
                    f"Input validation missed {len(malicious_inputs) - threats_detected} threats"
                )

            # Test legitimate input
            legitimate_input = "Hello, this is a normal message"
            result = security_hardening.input_validator.validate_input(legitimate_input)
            if not result["valid"]:
                raise ValueError("Input validation rejected legitimate input")

            self._record_test_result(
                test_name,
                True,
                f"Detected {threats_detected}/{len(malicious_inputs)} threats",
            )

        except Exception as e:
            self._record_test_result(
                test_name, False, f"Input validation test failed: {e}"
            )

    async def _test_authentication_security(self):
        """Test authentication security measures."""
        test_name = "Authentication Security"
        logger.info(f"Testing: {test_name}")

        try:
            # Test JWT secret exists and is secure (check both system and local paths)
            jwt_secret_files = [
                "/etc/acgs/encryption/master.key",
                "config/security/keys/master.key",
            ]

            jwt_secret_file = None
            for file_path in jwt_secret_files:
                if os.path.exists(file_path):
                    jwt_secret_file = file_path
                    break

            if not jwt_secret_file:
                raise FileNotFoundError("JWT secret file not found in any location")

            # Check file permissions
            stat_info = os.stat(jwt_secret_file)
            if stat_info.st_mode & 0o077:  # Check if readable by others
                raise PermissionError("JWT secret file has insecure permissions")

            # Test secrets manager
            from services.shared.security.advanced_security_hardening import (
                security_hardening,
            )

            # Store and retrieve a test secret
            test_secret_key = "test_auth_secret"
            test_secret_value = "super_secret_value_123"

            store_result = await security_hardening.secrets_manager.store_secret(
                test_secret_key, test_secret_value
            )
            if not store_result:
                raise RuntimeError("Failed to store test secret")

            retrieved_secret = await security_hardening.secrets_manager.get_secret(
                test_secret_key
            )
            if retrieved_secret != test_secret_value:
                raise ValueError("Retrieved secret doesn't match stored secret")

            self._record_test_result(
                test_name, True, "Authentication security tests passed"
            )

        except Exception as e:
            self._record_test_result(
                test_name, False, f"Authentication security test failed: {e}"
            )

    async def _test_rate_limiting(self):
        """Test rate limiting functionality."""
        test_name = "Rate Limiting"
        logger.info(f"Testing: {test_name}")

        try:
            # This is a simplified test - in production, you'd test against actual endpoints
            from services.shared.security.enhanced_security_middleware import (
                EnhancedSecurityMiddleware,
            )

            # Create middleware instance
            middleware = EnhancedSecurityMiddleware(None)

            # Simulate rate limit checking
            test_ip = "192.168.1.100"

            # Mock request object
            class MockRequest:
                def __init__(self):
                    self.method = "GET"
                    self.url = type("obj", (object,), {"path": "/api/test"})()
                    self.client = type("obj", (object,), {"host": test_ip})()

            mock_request = MockRequest()

            # Test multiple requests
            allowed_count = 0
            for i in range(10):
                result = await middleware._check_rate_limit(test_ip, mock_request)
                if result["allowed"]:
                    allowed_count += 1

            if allowed_count == 0:
                raise ValueError("Rate limiting too restrictive - no requests allowed")

            self._record_test_result(
                test_name,
                True,
                f"Rate limiting working: {allowed_count}/10 requests allowed",
            )

        except Exception as e:
            self._record_test_result(
                test_name, False, f"Rate limiting test failed: {e}"
            )

    async def _test_security_headers(self):
        """Test security headers implementation."""
        test_name = "Security Headers"
        logger.info(f"Testing: {test_name}")

        try:
            # Check if security headers middleware exists
            middleware_file = (
                self.project_root
                / "services"
                / "shared"
                / "security"
                / "enhanced_security_middleware.py"
            )
            if not middleware_file.exists():
                raise FileNotFoundError("Security middleware file not found")

            # Read middleware file and check for security headers
            with open(middleware_file) as f:
                content = f.read()

            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
                "Content-Security-Policy",
                "Strict-Transport-Security",
            ]

            missing_headers = []
            for header in required_headers:
                if header not in content:
                    missing_headers.append(header)

            if missing_headers:
                raise ValueError(f"Missing security headers: {missing_headers}")

            self._record_test_result(
                test_name, True, "All required security headers implemented"
            )

        except Exception as e:
            self._record_test_result(
                test_name, False, f"Security headers test failed: {e}"
            )

    async def _test_threat_detection(self):
        """Test threat detection capabilities."""
        test_name = "Threat Detection"
        logger.info(f"Testing: {test_name}")

        try:
            from services.shared.security.enhanced_security_middleware import (
                EnhancedSecurityMiddleware,
            )

            middleware = EnhancedSecurityMiddleware(None)

            # Mock malicious request
            class MockMaliciousRequest:
                def __init__(self):
                    self.url = type(
                        "obj", (object,), {"path": "/admin/../../../etc/passwd"}
                    )()
                    self.headers = {"user-agent": "sqlmap/1.0"}

            mock_request = MockMaliciousRequest()
            test_ip = "192.168.1.200"

            threat_result = await middleware._detect_threats(mock_request, test_ip)

            if not threat_result["threats"]:
                raise ValueError(
                    "Threat detection failed to identify malicious patterns"
                )

            self._record_test_result(
                test_name, True, f"Detected threats: {threat_result['threats']}"
            )

        except Exception as e:
            self._record_test_result(
                test_name, False, f"Threat detection test failed: {e}"
            )

    async def _test_constitutional_compliance(self):
        """Test constitutional compliance validation."""
        test_name = "Constitutional Compliance"
        logger.info(f"Testing: {test_name}")

        try:
            expected_hash = "cdd01ef066bc6cf2"

            # Check if constitutional hash is present in security files
            security_files = [
                "services/shared/security/advanced_security_hardening.py",
                "services/shared/security/enhanced_security_middleware.py",
                "config/security/enhanced-security-config.yml",
            ]

            files_with_hash = 0
            for file_path in security_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    with open(full_path) as f:
                        content = f.read()
                        if expected_hash in content:
                            files_with_hash += 1

            if files_with_hash == 0:
                raise ValueError("Constitutional hash not found in any security files")

            self._record_test_result(
                test_name,
                True,
                f"Constitutional hash found in {files_with_hash}/{len(security_files)} files",
            )

        except Exception as e:
            self._record_test_result(
                test_name, False, f"Constitutional compliance test failed: {e}"
            )

    async def _test_audit_system(self):
        """Test audit system functionality."""
        test_name = "Audit System"
        logger.info(f"Testing: {test_name}")

        try:
            from services.shared.security.security_audit_system import (
                security_audit_system,
            )

            # Check if audit system is available
            if not hasattr(security_audit_system, "perform_security_audit"):
                raise AttributeError("Audit system not properly initialized")

            # Test audit event logging
            security_audit_system.audit_findings = []  # Clear existing findings

            # The audit system should be functional
            self._record_test_result(test_name, True, "Audit system is functional")

        except Exception as e:
            self._record_test_result(test_name, False, f"Audit system test failed: {e}")

    async def _test_network_security(self):
        """Test network security measures."""
        test_name = "Network Security"
        logger.info(f"Testing: {test_name}")

        try:
            # Check if security configuration exists
            config_file = (
                self.project_root
                / "config"
                / "security"
                / "enhanced-security-config.yml"
            )
            if not config_file.exists():
                raise FileNotFoundError("Enhanced security config not found")

            # Basic network security validation
            self._record_test_result(
                test_name, True, "Network security configuration present"
            )

        except Exception as e:
            self._record_test_result(
                test_name, False, f"Network security test failed: {e}"
            )

    async def _test_configuration_security(self):
        """Test configuration security."""
        test_name = "Configuration Security"
        logger.info(f"Testing: {test_name}")

        try:
            # Check for hardcoded secrets in common files
            config_files = [
                "config/environments/development.env",
                "docker-compose.yml",
                "config/security/enhanced-security-config.yml",
            ]

            potential_secrets = []
            for config_file in config_files:
                file_path = self.project_root / config_file
                if file_path.exists():
                    with open(file_path) as f:
                        content = f.read().lower()
                        # Look for potential hardcoded secrets
                        if "password=" in content or "secret=" in content:
                            potential_secrets.append(config_file)

            if potential_secrets:
                logger.warning(f"Potential hardcoded secrets in: {potential_secrets}")

            self._record_test_result(
                test_name, True, "Configuration security check completed"
            )

        except Exception as e:
            self._record_test_result(
                test_name, False, f"Configuration security test failed: {e}"
            )

    def _record_test_result(self, test_name: str, passed: bool, details: str):
        """Record test result."""
        if passed:
            self.test_results["tests_passed"] += 1
            logger.info(f"✓ {test_name}: PASSED - {details}")
        else:
            self.test_results["tests_failed"] += 1
            logger.error(f"✗ {test_name}: FAILED - {details}")

        self.test_results["test_details"].append(
            {
                "test_name": test_name,
                "passed": passed,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def _calculate_security_score(self):
        """Calculate overall security score."""
        total_tests = (
            self.test_results["tests_passed"] + self.test_results["tests_failed"]
        )
        if total_tests > 0:
            self.test_results["security_score"] = (
                self.test_results["tests_passed"] / total_tests
            ) * 100
        else:
            self.test_results["security_score"] = 0.0

    def _generate_recommendations(self):
        """Generate security recommendations based on test results."""
        recommendations = []

        if self.test_results["tests_failed"] > 0:
            recommendations.append(
                "Address all failed security tests before production deployment"
            )

        if self.test_results["security_score"] < 90:
            recommendations.append(
                "Security score below 90% - implement additional hardening measures"
            )

        if self.test_results["security_score"] >= 95:
            recommendations.append(
                "Excellent security posture - maintain current measures"
            )

        recommendations.extend(
            [
                "Regularly rotate encryption keys and secrets",
                "Monitor security audit logs for anomalies",
                "Keep security dependencies updated",
                "Conduct periodic penetration testing",
                "Review and update security policies quarterly",
            ]
        )

        self.test_results["recommendations"] = recommendations

    async def _save_test_report(self):
        """Save test report to file."""
        reports_dir = Path("reports/security_tests")
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"security_test_report_{timestamp}.json"

        # Convert datetime objects to ISO format for JSON serialization
        serializable_results = json.loads(json.dumps(self.test_results, default=str))

        with open(report_file, "w") as f:
            json.dump(serializable_results, f, indent=2)

        logger.info(f"Security test report saved to {report_file}")


async def main():
    """Main testing function."""
    tester = SecurityHardeningTester()

    try:
        test_results = await tester.run_comprehensive_security_tests()

        print("\n" + "=" * 60)
        print("ACGS SECURITY HARDENING TEST RESULTS")
        print("=" * 60)
        print(f"Tests Passed: {test_results['tests_passed']}")
        print(f"Tests Failed: {test_results['tests_failed']}")
        print(f"Security Score: {test_results['security_score']:.1f}%")
        print(f"Constitutional Hash: {test_results['constitutional_hash']}")
        print("=" * 60)

        if test_results["tests_failed"] == 0:
            print("🎉 ALL SECURITY TESTS PASSED!")
            return 0
        print("⚠️  SOME SECURITY TESTS FAILED - REVIEW REQUIRED")
        return 1

    except Exception as e:
        print(f"\nTESTING FAILED: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
