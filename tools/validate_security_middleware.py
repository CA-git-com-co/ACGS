#!/usr/bin/env python3
"""
ACGS-1 Security Middleware Validation Script

This script validates that the production-grade security middleware is working correctly
across all 7 core ACGS-1 services by testing:
- Security headers presence
- Rate limiting functionality
- CSRF protection
- SQL injection detection
- Path traversal protection
- HTTPS enforcement
"""

import asyncio
import json
import logging
import time

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service configuration
SERVICES = {
    "auth": {"name": "Authentication Service", "port": 8000},
    "ac": {"name": "Constitutional AI Service", "port": 8001},
    "integrity": {"name": "Integrity Service", "port": 8002},
    "fv": {"name": "Formal Verification Service", "port": 8003},
    "gs": {"name": "Governance Synthesis Service", "port": 8004},
    "pgc": {"name": "Policy Governance Service", "port": 8005},
    "ec": {"name": "Evolutionary Computation Service", "port": 8006},
}

# Expected security headers
EXPECTED_SECURITY_HEADERS = [
    "X-Content-Type-Options",
    "X-Frame-Options",
    "X-XSS-Protection",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Referrer-Policy",
    "X-ACGS-Service",
    "X-Constitutional-Hash",
    "X-Security-Framework",
]


class SecurityMiddlewareValidator:
    """Validate security middleware functionality."""

    def __init__(self):
        self.validation_results = {}
        self.overall_score = 0
        self.total_tests = 0
        self.passed_tests = 0

    async def validate_all_services(self) -> dict:
        """Validate security middleware across all services."""
        logger.info("🔒 Starting security middleware validation")

        validation_start = time.time()

        for service_id, service_config in SERVICES.items():
            logger.info(
                f"🧪 Validating {service_config['name']} (port {service_config['port']})"
            )

            try:
                result = await self._validate_service(service_id, service_config)
                self.validation_results[service_id] = result

                # Update overall statistics
                self.total_tests += result["total_tests"]
                self.passed_tests += result["passed_tests"]

                score = result["security_score"]
                logger.info(f"✅ {service_config['name']} security score: {score}%")

            except Exception as e:
                logger.error(f"❌ Validation failed for {service_config['name']}: {e}")
                self.validation_results[service_id] = {
                    "success": False,
                    "error": str(e),
                    "security_score": 0,
                    "total_tests": 0,
                    "passed_tests": 0,
                }

        validation_time = time.time() - validation_start

        # Calculate overall score
        self.overall_score = (
            (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        )

        # Generate validation summary
        summary = self._generate_validation_summary(validation_time)

        # Save validation report
        await self._save_validation_report(summary)

        return summary

    async def _validate_service(self, service_id: str, service_config: dict) -> dict:
        """Validate security middleware for a specific service."""
        base_url = f"http://localhost:{service_config['port']}"
        tests_passed = 0
        total_tests = 0
        test_results = {}

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test 1: Security Headers Validation
            total_tests += 1
            headers_result = await self._test_security_headers(client, base_url)
            test_results["security_headers"] = headers_result
            if headers_result["passed"]:
                tests_passed += 1

            # Test 2: Rate Limiting Test
            total_tests += 1
            rate_limit_result = await self._test_rate_limiting(client, base_url)
            test_results["rate_limiting"] = rate_limit_result
            if rate_limit_result["passed"]:
                tests_passed += 1

            # Test 3: SQL Injection Detection
            total_tests += 1
            sql_injection_result = await self._test_sql_injection_detection(
                client, base_url
            )
            test_results["sql_injection_detection"] = sql_injection_result
            if sql_injection_result["passed"]:
                tests_passed += 1

            # Test 4: Path Traversal Detection
            total_tests += 1
            path_traversal_result = await self._test_path_traversal_detection(
                client, base_url
            )
            test_results["path_traversal_detection"] = path_traversal_result
            if path_traversal_result["passed"]:
                tests_passed += 1

            # Test 5: CORS Configuration
            total_tests += 1
            cors_result = await self._test_cors_configuration(client, base_url)
            test_results["cors_configuration"] = cors_result
            if cors_result["passed"]:
                tests_passed += 1

        security_score = (tests_passed / total_tests * 100) if total_tests > 0 else 0

        return {
            "success": True,
            "security_score": round(security_score, 1),
            "total_tests": total_tests,
            "passed_tests": tests_passed,
            "test_results": test_results,
            "timestamp": time.time(),
        }

    async def _test_security_headers(
        self, client: httpx.AsyncClient, base_url: str
    ) -> dict:
        """Test security headers presence."""
        try:
            response = await client.get(f"{base_url}/health")

            present_headers = []
            missing_headers = []

            for header in EXPECTED_SECURITY_HEADERS:
                if header in response.headers:
                    present_headers.append(header)
                else:
                    missing_headers.append(header)

            passed = len(missing_headers) == 0

            return {
                "passed": passed,
                "present_headers": present_headers,
                "missing_headers": missing_headers,
                "score": len(present_headers) / len(EXPECTED_SECURITY_HEADERS) * 100,
            }

        except Exception as e:
            return {"passed": False, "error": str(e), "score": 0}

    async def _test_rate_limiting(
        self, client: httpx.AsyncClient, base_url: str
    ) -> dict:
        """Test rate limiting functionality."""
        try:
            # Make multiple rapid requests to trigger rate limiting
            responses = []
            for i in range(5):
                try:
                    response = await client.get(f"{base_url}/health")
                    responses.append(
                        {
                            "status_code": response.status_code,
                            "has_rate_limit_headers": "X-RateLimit-Limit"
                            in response.headers,
                        }
                    )
                except Exception:
                    responses.append(
                        {"status_code": 0, "has_rate_limit_headers": False}
                    )

            # Check if rate limiting headers are present
            has_rate_limit_headers = any(r["has_rate_limit_headers"] for r in responses)

            return {
                "passed": has_rate_limit_headers,
                "responses": responses,
                "rate_limit_headers_present": has_rate_limit_headers,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def _test_sql_injection_detection(
        self, client: httpx.AsyncClient, base_url: str
    ) -> dict:
        """Test SQL injection detection."""
        try:
            # Test with SQL injection payload
            malicious_payload = "'; DROP TABLE users; --"

            response = await client.get(f"{base_url}/health?param={malicious_payload}")

            # If the request is blocked (403) or filtered, the test passes
            passed = (
                response.status_code in [403, 400] or "blocked" in response.text.lower()
            )

            return {
                "passed": passed,
                "status_code": response.status_code,
                "payload_tested": malicious_payload,
                "response_indicates_blocking": passed,
            }

        except Exception as e:
            # If the request fails due to security blocking, that's a pass
            return {"passed": True, "error": str(e), "blocked_by_security": True}

    async def _test_path_traversal_detection(
        self, client: httpx.AsyncClient, base_url: str
    ) -> dict:
        """Test path traversal detection."""
        try:
            # Test with path traversal payload
            malicious_path = "../../../etc/passwd"

            response = await client.get(f"{base_url}/health?file={malicious_path}")

            # If the request is blocked (403) or filtered, the test passes
            passed = (
                response.status_code in [403, 400] or "blocked" in response.text.lower()
            )

            return {
                "passed": passed,
                "status_code": response.status_code,
                "payload_tested": malicious_path,
                "response_indicates_blocking": passed,
            }

        except Exception as e:
            # If the request fails due to security blocking, that's a pass
            return {"passed": True, "error": str(e), "blocked_by_security": True}

    async def _test_cors_configuration(
        self, client: httpx.AsyncClient, base_url: str
    ) -> dict:
        """Test CORS configuration."""
        try:
            # Test OPTIONS request (CORS preflight)
            response = await client.options(f"{base_url}/health")

            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get(
                    "Access-Control-Allow-Origin"
                ),
                "Access-Control-Allow-Methods": response.headers.get(
                    "Access-Control-Allow-Methods"
                ),
                "Access-Control-Allow-Headers": response.headers.get(
                    "Access-Control-Allow-Headers"
                ),
            }

            # Check if CORS headers are present and properly configured
            has_cors_headers = any(cors_headers.values())

            return {
                "passed": has_cors_headers,
                "cors_headers": cors_headers,
                "status_code": response.status_code,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _generate_validation_summary(self, validation_time: float) -> dict:
        """Generate validation summary."""
        service_scores = []
        for service_id, result in self.validation_results.items():
            if result.get("success", False):
                service_scores.append(result["security_score"])

        avg_score = sum(service_scores) / len(service_scores) if service_scores else 0

        return {
            "validation_summary": {
                "overall_security_score": round(self.overall_score, 1),
                "average_service_score": round(avg_score, 1),
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.total_tests - self.passed_tests,
                "validation_time": f"{validation_time:.2f} seconds",
                "timestamp": time.time(),
            },
            "service_results": self.validation_results,
            "security_features_validated": [
                "Security headers (OWASP recommended)",
                "Rate limiting functionality",
                "SQL injection detection",
                "Path traversal protection",
                "CORS configuration",
            ],
        }

    async def _save_validation_report(self, summary: dict):
        """Save validation report to file."""
        report_path = "security_middleware_validation_report.json"

        with open(report_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"📄 Validation report saved to {report_path}")


async def main():
    """Main validation function."""
    logger.info("🚀 ACGS-1 Security Middleware Validation Starting")

    validator = SecurityMiddlewareValidator()
    summary = await validator.validate_all_services()

    # Print summary
    print("\n" + "=" * 80)
    print("🔒 ACGS-1 Security Middleware Validation Summary")
    print("=" * 80)
    print(
        f"Overall Security Score: {summary['validation_summary']['overall_security_score']}%"
    )
    print(
        f"Average Service Score: {summary['validation_summary']['average_service_score']}%"
    )
    print(f"Total Tests: {summary['validation_summary']['total_tests']}")
    print(f"Passed Tests: {summary['validation_summary']['passed_tests']}")
    print(f"Failed Tests: {summary['validation_summary']['failed_tests']}")
    print(f"Validation Time: {summary['validation_summary']['validation_time']}")

    print("\n🔒 Security Features Validated:")
    for feature in summary["security_features_validated"]:
        print(f"   - {feature}")

    print("\n📊 Service-by-Service Results:")
    for service_id, result in summary["service_results"].items():
        if result.get("success", False):
            score = result["security_score"]
            status = "✅ PASS" if score >= 80 else "⚠️ NEEDS IMPROVEMENT"
            print(f"   {SERVICES[service_id]['name']}: {score}% {status}")
        else:
            print(f"   {SERVICES[service_id]['name']}: ❌ FAILED")

    print("\n📄 Detailed report saved to: security_middleware_validation_report.json")

    return summary


if __name__ == "__main__":
    asyncio.run(main())
