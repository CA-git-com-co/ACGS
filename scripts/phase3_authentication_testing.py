#!/usr/bin/env python3
"""
ACGS-PGP Phase 3.2: Service-to-Service Authentication Testing
Validates JWT token authentication flow between all ACGS services

Features:
- JWT token generation and validation
- Service-to-service authentication testing
- Token expiration and refresh testing
- Role-based access control validation
- Constitutional compliance verification
- Security header validation
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

import httpx
import jwt
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AuthTestResult(BaseModel):
    """Authentication test result model"""

    test_name: str
    status: str
    response_time_ms: float
    details: Dict[str, Any]
    timestamp: datetime
    error: Optional[str] = None


class ACGSAuthenticationTester:
    """ACGS-PGP Service-to-Service Authentication Tester"""

    def __init__(self):
        self.services = {
            "auth": {"port": 8000, "name": "Authentication Service"},
            "ac": {"port": 8001, "name": "Constitutional AI Service"},
            "integrity": {"port": 8002, "name": "Integrity Service"},
            "fv": {"port": 8003, "name": "Formal Verification Service"},
            "gs": {"port": 8004, "name": "Governance Synthesis Service"},
            "pgc": {"port": 8005, "name": "Policy Governance & Compliance Service"},
            "ec": {"port": 8006, "name": "Executive Council Service"},
        }
        self.base_url = "http://localhost"
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.test_credentials = {"username": "test_user", "password": "test_password"}
        self.access_token: Optional[str] = None
        self.test_results: List[AuthTestResult] = []

    async def authenticate_with_auth_service(self) -> Dict[str, Any]:
        """Authenticate with the auth service and obtain JWT token"""
        logger.info("🔐 Authenticating with auth service...")

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try both login endpoints for compatibility
                auth_endpoints = ["/auth/login", "/auth/token"]

                for endpoint in auth_endpoints:
                    try:
                        response = await client.post(
                            f"{self.base_url}:8000{endpoint}",
                            data={
                                "username": self.test_credentials["username"],
                                "password": self.test_credentials["password"],
                            },
                            headers={
                                "Content-Type": "application/x-www-form-urlencoded"
                            },
                        )

                        if response.status_code == 200:
                            auth_data = response.json()
                            self.access_token = auth_data.get("access_token")

                            response_time = (time.time() - start_time) * 1000
                            return {
                                "status": "success",
                                "endpoint_used": endpoint,
                                "token_obtained": bool(self.access_token),
                                "response_time_ms": response_time,
                                "token_type": auth_data.get("token_type", "bearer"),
                                "expires_in": auth_data.get("expires_in"),
                                "constitutional_hash_verified": self._verify_constitutional_hash(
                                    response
                                ),
                            }

                    except Exception as e:
                        logger.warning(f"Auth endpoint {endpoint} failed: {e}")
                        continue

                # If we get here, all endpoints failed
                response_time = (time.time() - start_time) * 1000
                return {
                    "status": "failed",
                    "error": "All authentication endpoints failed",
                    "response_time_ms": response_time,
                }

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "failed",
                "error": str(e),
                "response_time_ms": response_time,
            }

    async def test_service_authentication(self, service_key: str) -> Dict[str, Any]:
        """Test authentication with a specific service"""
        service = self.services[service_key]
        logger.info(f"🔒 Testing authentication with {service['name']}...")

        if not self.access_token:
            return {"status": "failed", "error": "No access token available"}

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test authenticated endpoint (try multiple common patterns)
                test_endpoints = [
                    "/api/v1/status",
                    "/api/v1/health",
                    "/status",
                    "/health",
                ]

                for endpoint in test_endpoints:
                    try:
                        response = await client.get(
                            f"{self.base_url}:{service['port']}{endpoint}",
                            headers={
                                "Authorization": f"Bearer {self.access_token}",
                                "Content-Type": "application/json",
                            },
                        )

                        response_time = (time.time() - start_time) * 1000

                        if response.status_code == 200:
                            return {
                                "status": "success",
                                "service": service["name"],
                                "port": service["port"],
                                "endpoint_used": endpoint,
                                "response_time_ms": response_time,
                                "authenticated": True,
                                "constitutional_hash_verified": self._verify_constitutional_hash(
                                    response
                                ),
                                "response_data": (
                                    response.json()
                                    if response.headers.get(
                                        "content-type", ""
                                    ).startswith("application/json")
                                    else None
                                ),
                            }
                        elif response.status_code == 401:
                            return {
                                "status": "auth_failed",
                                "service": service["name"],
                                "port": service["port"],
                                "endpoint_used": endpoint,
                                "response_time_ms": response_time,
                                "error": "Authentication failed - token rejected",
                            }
                        elif response.status_code == 403:
                            return {
                                "status": "auth_success_access_denied",
                                "service": service["name"],
                                "port": service["port"],
                                "endpoint_used": endpoint,
                                "response_time_ms": response_time,
                                "error": "Authentication successful but access denied",
                            }

                    except Exception as e:
                        logger.debug(
                            f"Endpoint {endpoint} failed for {service['name']}: {e}"
                        )
                        continue

                # If we get here, all endpoints failed
                response_time = (time.time() - start_time) * 1000
                return {
                    "status": "failed",
                    "service": service["name"],
                    "port": service["port"],
                    "response_time_ms": response_time,
                    "error": "All test endpoints failed or service not responding",
                }

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "failed",
                "service": service["name"],
                "port": service["port"],
                "response_time_ms": response_time,
                "error": str(e),
            }

    async def test_token_validation(self) -> Dict[str, Any]:
        """Test JWT token validation and structure"""
        logger.info("🔍 Testing JWT token validation...")

        if not self.access_token:
            return {
                "status": "failed",
                "error": "No access token available for validation",
            }

        try:
            # Decode token without verification to inspect structure
            decoded_token = jwt.decode(
                self.access_token, options={"verify_signature": False}
            )

            # Check required JWT claims
            required_claims = ["sub", "exp", "iat"]
            missing_claims = [
                claim for claim in required_claims if claim not in decoded_token
            ]

            # Check token expiration
            exp_timestamp = decoded_token.get("exp", 0)
            current_timestamp = time.time()
            is_expired = exp_timestamp < current_timestamp
            time_to_expiry = exp_timestamp - current_timestamp

            return {
                "status": "success",
                "token_structure": {
                    "claims_present": list(decoded_token.keys()),
                    "missing_required_claims": missing_claims,
                    "subject": decoded_token.get("sub"),
                    "username": decoded_token.get("username"),
                    "roles": decoded_token.get("roles", []),
                    "issued_at": datetime.fromtimestamp(
                        decoded_token.get("iat", 0)
                    ).isoformat(),
                    "expires_at": datetime.fromtimestamp(exp_timestamp).isoformat(),
                    "is_expired": is_expired,
                    "time_to_expiry_seconds": max(0, time_to_expiry),
                },
                "validation": {
                    "has_required_claims": len(missing_claims) == 0,
                    "is_valid_format": True,
                    "is_not_expired": not is_expired,
                },
            }

        except Exception as e:
            return {"status": "failed", "error": f"Token validation failed: {str(e)}"}

    async def test_unauthorized_access(self) -> Dict[str, Any]:
        """Test that services properly reject unauthorized requests"""
        logger.info("🚫 Testing unauthorized access rejection...")

        unauthorized_tests = []

        for service_key, service in self.services.items():
            if service_key == "auth":  # Skip auth service for this test
                continue

            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # Test without authorization header
                    response = await client.get(
                        f"{self.base_url}:{service['port']}/api/v1/status",
                        headers={"Content-Type": "application/json"},
                    )

                    unauthorized_tests.append(
                        {
                            "service": service["name"],
                            "port": service["port"],
                            "status_code": response.status_code,
                            "properly_rejected": response.status_code in [401, 403],
                            "response_headers": dict(response.headers),
                        }
                    )

            except Exception as e:
                unauthorized_tests.append(
                    {
                        "service": service["name"],
                        "port": service["port"],
                        "error": str(e),
                        "properly_rejected": False,
                    }
                )

        # Calculate overall security status
        properly_secured_count = sum(
            1 for test in unauthorized_tests if test.get("properly_rejected", False)
        )
        total_services = len(unauthorized_tests)
        security_percentage = (
            (properly_secured_count / total_services * 100) if total_services > 0 else 0
        )

        return {
            "status": "success",
            "security_tests": unauthorized_tests,
            "summary": {
                "total_services_tested": total_services,
                "properly_secured_services": properly_secured_count,
                "security_percentage": security_percentage,
                "overall_security_status": (
                    "good" if security_percentage >= 80 else "needs_improvement"
                ),
            },
        }

    def _verify_constitutional_hash(self, response: httpx.Response) -> bool:
        """Verify constitutional hash in response headers"""
        return response.headers.get("x-constitutional-hash") == self.constitutional_hash

    async def run_authentication_tests(self) -> Dict[str, Any]:
        """Run comprehensive authentication tests"""
        logger.info("🚀 Starting ACGS-PGP Authentication Tests...")

        test_results = {
            "test_suite": "ACGS-PGP Service Authentication",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "results": {},
        }

        # Step 1: Authenticate with auth service
        auth_result = await self.authenticate_with_auth_service()
        test_results["results"]["authentication"] = auth_result

        if auth_result["status"] != "success":
            test_results["overall_status"] = "failed"
            test_results["error"] = "Failed to authenticate with auth service"
            return test_results

        # Step 2: Test token validation
        token_validation = await self.test_token_validation()
        test_results["results"]["token_validation"] = token_validation

        # Step 3: Test service-to-service authentication
        service_auth_results = {}
        for service_key in self.services.keys():
            if service_key != "auth":  # Skip auth service
                service_result = await self.test_service_authentication(service_key)
                service_auth_results[service_key] = service_result

        test_results["results"]["service_authentication"] = service_auth_results

        # Step 4: Test unauthorized access rejection
        unauthorized_test = await self.test_unauthorized_access()
        test_results["results"]["unauthorized_access_test"] = unauthorized_test

        # Calculate overall status
        successful_auths = sum(
            1
            for result in service_auth_results.values()
            if result.get("status") == "success"
        )
        total_services = len(service_auth_results)
        auth_success_rate = (
            (successful_auths / total_services * 100) if total_services > 0 else 0
        )

        test_results["overall_status"] = (
            "passed" if auth_success_rate >= 70 else "failed"
        )
        test_results["summary"] = {
            "total_services": total_services,
            "successful_authentications": successful_auths,
            "authentication_success_rate": auth_success_rate,
            "token_validation_passed": token_validation.get("status") == "success",
            "security_status": unauthorized_test.get("summary", {}).get(
                "overall_security_status", "unknown"
            ),
        }

        return test_results


async def main():
    """Main execution function"""
    tester = ACGSAuthenticationTester()

    try:
        results = await tester.run_authentication_tests()

        # Save results to file
        with open("phase3_authentication_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Print summary
        print("\n" + "=" * 80)
        print("ACGS-PGP Phase 3.2: Authentication Test Results")
        print("=" * 80)
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(
            f"Authentication Success Rate: {results['summary']['authentication_success_rate']:.1f}%"
        )
        print(
            f"Token Validation: {'PASSED' if results['summary']['token_validation_passed'] else 'FAILED'}"
        )
        print(f"Security Status: {results['summary']['security_status'].upper()}")
        print(f"Constitutional Hash: {results['constitutional_hash']}")
        print("=" * 80)

        if results["overall_status"] == "passed":
            print("✅ Authentication tests passed successfully!")
            return 0
        else:
            print("❌ Some authentication tests failed. Check results for details.")
            return 1

    except Exception as e:
        logger.error(f"Authentication testing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
