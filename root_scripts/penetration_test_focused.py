#!/usr/bin/env python3
"""
ACGS-1 Focused Penetration Testing Script

Conducts targeted security testing against ACGS-1 services focusing on:
- Authentication bypass attempts
- Authorization vulnerabilities
- Input validation issues
- API endpoint security
- JWT token security
- Rate limiting effectiveness
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any
import httpx
import jwt as pyjwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ACGSPenetrationTester:
    def __init__(self):
        self.base_url = "http://localhost"
        self.services = {
            "auth": 8000,
            "ac": 8001,
            "integrity": 8002,
            "fv": 8003,
            "gs": 8004,
            "pgc": 8005,
            "ec": 8006,
        }
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "vulnerabilities": [],
            "security_score": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
        }

    async def test_authentication_bypass(self) -> List[Dict]:
        """Test for authentication bypass vulnerabilities."""
        logger.info("Testing authentication bypass...")
        vulnerabilities = []

        test_cases = [
            {"endpoint": "/api/admin", "method": "GET", "headers": {}},
            {"endpoint": "/api/users", "method": "GET", "headers": {}},
            {"endpoint": "/api/config", "method": "GET", "headers": {}},
            {
                "endpoint": "/api/health",
                "method": "GET",
                "headers": {},
            },  # Should be public
        ]

        for service_name, port in self.services.items():
            for test_case in test_cases:
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.request(
                            test_case["method"],
                            f"{self.base_url}:{port}{test_case['endpoint']}",
                            headers=test_case["headers"],
                        )

                        # Check if protected endpoints are accessible without auth
                        if (
                            test_case["endpoint"] != "/api/health"
                            and response.status_code == 200
                        ):
                            vulnerabilities.append(
                                {
                                    "severity": "HIGH",
                                    "type": "Authentication Bypass",
                                    "service": service_name,
                                    "endpoint": test_case["endpoint"],
                                    "description": f"Protected endpoint accessible without authentication",
                                    "status_code": response.status_code,
                                }
                            )

                except Exception as e:
                    # Service not running is expected for some services
                    logger.debug(f"Service {service_name} not accessible: {e}")

        return vulnerabilities

    async def test_jwt_security(self) -> List[Dict]:
        """Test JWT token security."""
        logger.info("Testing JWT security...")
        vulnerabilities = []

        # Test weak JWT secrets
        weak_secrets = ["secret", "123456", "password", "acgs", ""]
        test_payload = {
            "user_id": 1,
            "roles": ["admin"],
            "exp": int(time.time()) + 3600,
        }

        for secret in weak_secrets:
            try:
                token = pyjwt.encode(test_payload, secret, algorithm="HS256")

                # Try to access protected endpoints with weak token
                for service_name, port in self.services.items():
                    try:
                        async with httpx.AsyncClient(timeout=5.0) as client:
                            response = await client.get(
                                f"{self.base_url}:{port}/api/admin",
                                headers={"Authorization": f"Bearer {token}"},
                            )

                            if response.status_code == 200:
                                vulnerabilities.append(
                                    {
                                        "severity": "CRITICAL",
                                        "type": "Weak JWT Secret",
                                        "service": service_name,
                                        "description": f"JWT token with weak secret '{secret}' accepted",
                                        "secret": secret,
                                    }
                                )
                    except Exception:
                        pass

            except Exception as e:
                logger.debug(f"JWT test failed: {e}")

        return vulnerabilities

    async def test_input_validation(self) -> List[Dict]:
        """Test input validation vulnerabilities."""
        logger.info("Testing input validation...")
        vulnerabilities = []

        # SQL injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users --",
        ]

        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ]

        # Command injection payloads
        cmd_payloads = ["; ls -la", "| cat /etc/passwd", "&& whoami"]

        all_payloads = sql_payloads + xss_payloads + cmd_payloads

        for service_name, port in self.services.items():
            for payload in all_payloads:
                try:
                    # Test GET parameters
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.get(
                            f"{self.base_url}:{port}/api/search", params={"q": payload}
                        )

                        # Check for error messages that might indicate vulnerability
                        if response.status_code == 500:
                            response_text = response.text.lower()
                            if any(
                                keyword in response_text
                                for keyword in [
                                    "sql",
                                    "syntax",
                                    "mysql",
                                    "postgres",
                                    "error",
                                ]
                            ):
                                vulnerabilities.append(
                                    {
                                        "severity": "HIGH",
                                        "type": "SQL Injection",
                                        "service": service_name,
                                        "endpoint": "/api/search",
                                        "payload": payload,
                                        "description": "Potential SQL injection vulnerability detected",
                                    }
                                )

                        # Check for reflected XSS
                        if payload in response.text and "<script>" in payload:
                            vulnerabilities.append(
                                {
                                    "severity": "MEDIUM",
                                    "type": "Reflected XSS",
                                    "service": service_name,
                                    "endpoint": "/api/search",
                                    "payload": payload,
                                    "description": "Potential reflected XSS vulnerability detected",
                                }
                            )

                except Exception:
                    pass

        return vulnerabilities

    async def test_rate_limiting(self) -> List[Dict]:
        """Test rate limiting effectiveness."""
        logger.info("Testing rate limiting...")
        vulnerabilities = []

        for service_name, port in self.services.items():
            try:
                # Send rapid requests to test rate limiting
                requests_sent = 0
                successful_requests = 0

                async with httpx.AsyncClient(timeout=5.0) as client:
                    for i in range(20):  # Send 20 rapid requests
                        try:
                            response = await client.get(
                                f"{self.base_url}:{port}/api/health"
                            )
                            requests_sent += 1
                            if response.status_code == 200:
                                successful_requests += 1
                        except Exception:
                            pass

                # If all requests succeed, rate limiting might be missing
                if successful_requests == requests_sent and requests_sent > 15:
                    vulnerabilities.append(
                        {
                            "severity": "MEDIUM",
                            "type": "Missing Rate Limiting",
                            "service": service_name,
                            "description": f"No rate limiting detected - {successful_requests}/{requests_sent} requests succeeded",
                            "requests_sent": requests_sent,
                            "successful_requests": successful_requests,
                        }
                    )

            except Exception as e:
                logger.debug(f"Rate limiting test failed for {service_name}: {e}")

        return vulnerabilities

    async def test_cors_configuration(self) -> List[Dict]:
        """Test CORS configuration."""
        logger.info("Testing CORS configuration...")
        vulnerabilities = []

        for service_name, port in self.services.items():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.options(
                        f"{self.base_url}:{port}/api/health",
                        headers={"Origin": "https://evil.com"},
                    )

                    cors_headers = {
                        "access-control-allow-origin": response.headers.get(
                            "access-control-allow-origin", ""
                        ),
                        "access-control-allow-credentials": response.headers.get(
                            "access-control-allow-credentials", ""
                        ),
                        "access-control-allow-methods": response.headers.get(
                            "access-control-allow-methods", ""
                        ),
                    }

                    # Check for overly permissive CORS
                    if cors_headers["access-control-allow-origin"] == "*":
                        if cors_headers["access-control-allow-credentials"] == "true":
                            vulnerabilities.append(
                                {
                                    "severity": "HIGH",
                                    "type": "Insecure CORS Configuration",
                                    "service": service_name,
                                    "description": "CORS allows any origin with credentials",
                                    "headers": cors_headers,
                                }
                            )
                        else:
                            vulnerabilities.append(
                                {
                                    "severity": "LOW",
                                    "type": "Permissive CORS Configuration",
                                    "service": service_name,
                                    "description": "CORS allows any origin",
                                    "headers": cors_headers,
                                }
                            )

            except Exception:
                pass

        return vulnerabilities

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all penetration tests."""
        logger.info("Starting comprehensive penetration testing...")

        all_vulnerabilities = []

        # Run all test categories
        test_methods = [
            self.test_authentication_bypass,
            self.test_jwt_security,
            self.test_input_validation,
            self.test_rate_limiting,
            self.test_cors_configuration,
        ]

        for test_method in test_methods:
            try:
                vulnerabilities = await test_method()
                all_vulnerabilities.extend(vulnerabilities)
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed: {e}")

        # Categorize vulnerabilities by severity
        for vuln in all_vulnerabilities:
            severity = vuln.get("severity", "LOW")
            if severity == "CRITICAL":
                self.results["critical_issues"] += 1
            elif severity == "HIGH":
                self.results["high_issues"] += 1
            elif severity == "MEDIUM":
                self.results["medium_issues"] += 1
            else:
                self.results["low_issues"] += 1

        self.results["vulnerabilities"] = all_vulnerabilities

        # Calculate security score (100 - weighted vulnerability score)
        vulnerability_score = (
            self.results["critical_issues"] * 25
            + self.results["high_issues"] * 15
            + self.results["medium_issues"] * 8
            + self.results["low_issues"] * 3
        )

        self.results["security_score"] = max(0, 100 - vulnerability_score)
        self.results["tests_passed"] = len(test_methods) - len(all_vulnerabilities)
        self.results["tests_failed"] = len(all_vulnerabilities)

        return self.results


async def main():
    """Main execution function."""
    tester = ACGSPenetrationTester()
    results = await tester.run_all_tests()

    # Save results
    with open("penetration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("ACGS-1 PENETRATION TEST RESULTS")
    print("=" * 80)
    print(f"Security Score: {results['security_score']}/100")
    print(f"Critical Issues: {results['critical_issues']}")
    print(f"High Issues: {results['high_issues']}")
    print(f"Medium Issues: {results['medium_issues']}")
    print(f"Low Issues: {results['low_issues']}")
    print(f"Total Vulnerabilities: {len(results['vulnerabilities'])}")

    if results["vulnerabilities"]:
        print("\nVulnerabilities Found:")
        for vuln in results["vulnerabilities"]:
            print(
                f"  [{vuln['severity']}] {vuln['type']} in {vuln.get('service', 'Unknown')}"
            )
            print(f"      {vuln['description']}")
    else:
        print("\n✅ No vulnerabilities detected!")

    print("=" * 80)

    return results


if __name__ == "__main__":
    asyncio.run(main())
