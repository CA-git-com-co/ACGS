#!/usr/bin/env python3
"""
Comprehensive Security Testing Suite for ACGS-2
Constitutional Hash: cdd01ef066bc6cf2

This module provides extensive security testing coverage including:
- Authentication and authorization testing
- Input validation and injection attack prevention
- Cryptographic security validation
- Constitutional compliance security
- Multi-tenant isolation security
- Network security and communication protocols
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

import pytest
import aiohttp
import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class SecurityTestConfig:
    """Configuration for security tests"""
    base_url: str = "http://localhost:8010"
    auth_service_url: str = "http://localhost:8016"
    constitutional_ai_url: str = "http://localhost:8001"
    integrity_service_url: str = "http://localhost:8002"
    test_timeout: int = 30
    max_retries: int = 3
    constitutional_hash: str = CONSTITUTIONAL_HASH

@dataclass
class SecurityTestResult:
    """Result of a security test"""
    test_name: str
    passed: bool
    vulnerability_found: bool
    severity: str  # critical, high, medium, low
    details: str
    recommendations: List[str]
    constitutional_compliant: bool

class SecurityTestSuite:
    """Comprehensive security testing suite"""
    
    def __init__(self, config: SecurityTestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: List[SecurityTestResult] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.test_timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def test_authentication_security(self) -> SecurityTestResult:
        """Test authentication security vulnerabilities"""
        test_name = "Authentication Security Test"
        vulnerabilities = []
        recommendations = []
        
        try:
            # Test 1: Brute force protection
            logger.info("Testing brute force protection...")
            auth_data = {
                "username": "nonexistent_user",
                "password": "wrong_password",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            failed_attempts = 0
            for attempt in range(10):
                try:
                    async with self.session.post(
                        f"{self.config.auth_service_url}/auth/login",
                        json=auth_data
                    ) as response:
                        if response.status == 401:
                            failed_attempts += 1
                        elif response.status == 429:  # Rate limited
                            logger.info("✅ Rate limiting detected - brute force protection active")
                            break
                except Exception as e:
                    logger.debug(f"Auth attempt {attempt + 1} failed: {e}")
                    
                await asyncio.sleep(0.1)
            
            if failed_attempts >= 5:
                vulnerabilities.append("No brute force protection detected")
                recommendations.append("Implement rate limiting for failed login attempts")
            
            # Test 2: SQL injection in authentication
            logger.info("Testing SQL injection in authentication...")
            sql_payloads = [
                "admin' OR '1'='1",
                "admin'; DROP TABLE users; --",
                "admin' UNION SELECT * FROM users --",
                "admin' OR '1'='1' /*",
                "admin' OR 1=1 #"
            ]
            
            for payload in sql_payloads:
                auth_data = {
                    "username": payload,
                    "password": "any_password",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                
                try:
                    async with self.session.post(
                        f"{self.config.auth_service_url}/auth/login",
                        json=auth_data
                    ) as response:
                        if response.status == 200:
                            vulnerabilities.append(f"SQL injection vulnerability with payload: {payload}")
                            recommendations.append("Implement parameterized queries and input validation")
                except Exception as e:
                    logger.debug(f"SQL injection test failed: {e}")
            
            # Test 3: JWT token security
            logger.info("Testing JWT token security...")
            valid_token = await self._get_valid_token()
            if valid_token:
                # Test token tampering
                try:
                    decoded = jwt.decode(valid_token, options={"verify_signature": False})
                    decoded["roles"] = ["admin", "super_admin"]
                    
                    # Try to create tampered token
                    tampered_token = jwt.encode(decoded, "fake_secret", algorithm="HS256")
                    
                    # Test if tampered token is accepted
                    headers = {"Authorization": f"Bearer {tampered_token}"}
                    async with self.session.get(
                        f"{self.config.base_url}/health",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            vulnerabilities.append("JWT token tampering not detected")
                            recommendations.append("Implement proper JWT signature verification")
                except Exception as e:
                    logger.debug(f"JWT tampering test failed: {e}")
            
            # Test 4: Password strength validation
            logger.info("Testing password strength validation...")
            weak_passwords = [
                "123456",
                "password",
                "admin",
                "12345678",
                "qwerty",
                "a",
                "",
                "password123"
            ]
            
            for weak_password in weak_passwords:
                user_data = {
                    "username": f"testuser_{secrets.token_hex(8)}",
                    "email": f"test_{secrets.token_hex(8)}@example.com",
                    "password": weak_password,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                
                try:
                    async with self.session.post(
                        f"{self.config.auth_service_url}/auth/register",
                        json=user_data
                    ) as response:
                        if response.status == 201:
                            vulnerabilities.append(f"Weak password accepted: {weak_password}")
                            recommendations.append("Implement strong password requirements")
                except Exception as e:
                    logger.debug(f"Password strength test failed: {e}")
            
            return SecurityTestResult(
                test_name=test_name,
                passed=len(vulnerabilities) == 0,
                vulnerability_found=len(vulnerabilities) > 0,
                severity="high" if vulnerabilities else "low",
                details=f"Found {len(vulnerabilities)} authentication vulnerabilities",
                recommendations=recommendations,
                constitutional_compliant=True
            )
            
        except Exception as e:
            logger.error(f"Authentication security test failed: {e}")
            return SecurityTestResult(
                test_name=test_name,
                passed=False,
                vulnerability_found=True,
                severity="critical",
                details=f"Authentication security test failed: {e}",
                recommendations=["Fix authentication security test infrastructure"],
                constitutional_compliant=False
            )
    
    async def test_input_validation_security(self) -> SecurityTestResult:
        """Test input validation and injection attack prevention"""
        test_name = "Input Validation Security Test"
        vulnerabilities = []
        recommendations = []
        
        try:
            # Test 1: XSS (Cross-Site Scripting) attacks
            logger.info("Testing XSS vulnerability...")
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg/onload=alert('XSS')>",
                "<iframe src=javascript:alert('XSS')></iframe>",
                "';alert('XSS');//",
                "\"><script>alert('XSS')</script>",
                "<body onload=alert('XSS')>"
            ]
            
            for payload in xss_payloads:
                test_data = {
                    "title": payload,
                    "description": f"Test description with {payload}",
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                
                try:
                    async with self.session.post(
                        f"{self.config.base_url}/api/v1/test",
                        json=test_data
                    ) as response:
                        if response.status == 200:
                            response_text = await response.text()
                            if payload in response_text and "<script>" in response_text:
                                vulnerabilities.append(f"XSS vulnerability with payload: {payload}")
                                recommendations.append("Implement output encoding and input sanitization")
                except Exception as e:
                    logger.debug(f"XSS test failed: {e}")
            
            # Test 2: Command injection
            logger.info("Testing command injection...")
            command_payloads = [
                "; ls -la",
                "& dir",
                "| cat /etc/passwd",
                "`whoami`",
                "$(id)",
                "&& rm -rf /",
                "; cat /etc/hosts",
                "| nc -l -p 4444"
            ]
            
            for payload in command_payloads:
                test_data = {
                    "command": payload,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                
                try:
                    async with self.session.post(
                        f"{self.config.base_url}/api/v1/execute",
                        json=test_data
                    ) as response:
                        if response.status == 200:
                            response_text = await response.text()
                            if any(indicator in response_text.lower() for indicator in 
                                   ["root:", "administrator", "total ", "volume "]):
                                vulnerabilities.append(f"Command injection with payload: {payload}")
                                recommendations.append("Implement command input validation and sanitization")
                except Exception as e:
                    logger.debug(f"Command injection test failed: {e}")
            
            # Test 3: Path traversal
            logger.info("Testing path traversal...")
            path_payloads = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "..%252f..%252f..%252fetc%252fpasswd",
                "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd"
            ]
            
            for payload in path_payloads:
                try:
                    async with self.session.get(
                        f"{self.config.base_url}/api/v1/file?path={payload}"
                    ) as response:
                        if response.status == 200:
                            response_text = await response.text()
                            if "root:" in response_text or "administrator" in response_text:
                                vulnerabilities.append(f"Path traversal with payload: {payload}")
                                recommendations.append("Implement proper file path validation")
                except Exception as e:
                    logger.debug(f"Path traversal test failed: {e}")
            
            # Test 4: LDAP injection
            logger.info("Testing LDAP injection...")
            ldap_payloads = [
                "*)(uid=*))(|(uid=*",
                "*)(|(password=*))",
                "admin)(&(password=*))",
                "admin)(|(cn=*))",
                "*)|(|(objectclass=*"
            ]
            
            for payload in ldap_payloads:
                test_data = {
                    "username": payload,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                
                try:
                    async with self.session.post(
                        f"{self.config.base_url}/api/v1/ldap/search",
                        json=test_data
                    ) as response:
                        if response.status == 200:
                            response_text = await response.text()
                            if "ldap" in response_text.lower() or "directory" in response_text.lower():
                                vulnerabilities.append(f"LDAP injection with payload: {payload}")
                                recommendations.append("Implement LDAP query parameterization")
                except Exception as e:
                    logger.debug(f"LDAP injection test failed: {e}")
            
            return SecurityTestResult(
                test_name=test_name,
                passed=len(vulnerabilities) == 0,
                vulnerability_found=len(vulnerabilities) > 0,
                severity="high" if vulnerabilities else "low",
                details=f"Found {len(vulnerabilities)} input validation vulnerabilities",
                recommendations=recommendations,
                constitutional_compliant=True
            )
            
        except Exception as e:
            logger.error(f"Input validation security test failed: {e}")
            return SecurityTestResult(
                test_name=test_name,
                passed=False,
                vulnerability_found=True,
                severity="critical",
                details=f"Input validation security test failed: {e}",
                recommendations=["Fix input validation security test infrastructure"],
                constitutional_compliant=False
            )
    
    async def test_cryptographic_security(self) -> SecurityTestResult:
        """Test cryptographic security implementation"""
        test_name = "Cryptographic Security Test"
        vulnerabilities = []
        recommendations = []
        
        try:
            # Test 1: Constitutional hash validation
            logger.info("Testing constitutional hash validation...")
            
            # Test with invalid constitutional hash
            invalid_hashes = [
                "invalid_hash",
                "1234567890abcdef",
                "",
                "cdd01ef066bc6cf3",  # Similar but wrong
                "CDD01EF066BC6CF2",  # Wrong case
                "cdd01ef066bc6cf2 "  # Extra space
            ]
            
            for invalid_hash in invalid_hashes:
                test_data = {
                    "constitutional_hash": invalid_hash,
                    "data": "test_data"
                }
                
                try:
                    async with self.session.post(
                        f"{self.config.constitutional_ai_url}/validate",
                        json=test_data
                    ) as response:
                        if response.status == 200:
                            vulnerabilities.append(f"Invalid constitutional hash accepted: {invalid_hash}")
                            recommendations.append("Implement strict constitutional hash validation")
                except Exception as e:
                    logger.debug(f"Constitutional hash test failed: {e}")
            
            # Test 2: Encryption strength
            logger.info("Testing encryption strength...")
            
            # Test weak encryption
            weak_keys = [
                "weak_key",
                "12345678",
                "password",
                "a" * 16,  # Repeated character
                "1234567890123456"  # Sequential
            ]
            
            for weak_key in weak_keys:
                try:
                    # Test if weak key is accepted
                    key_data = {
                        "encryption_key": weak_key,
                        "constitutional_hash": CONSTITUTIONAL_HASH
                    }
                    
                    async with self.session.post(
                        f"{self.config.integrity_service_url}/encrypt",
                        json=key_data
                    ) as response:
                        if response.status == 200:
                            vulnerabilities.append(f"Weak encryption key accepted: {weak_key}")
                            recommendations.append("Implement strong encryption key requirements")
                except Exception as e:
                    logger.debug(f"Encryption strength test failed: {e}")
            
            # Test 3: Digital signature verification
            logger.info("Testing digital signature verification...")
            
            # Test signature tampering
            test_message = "Test message for signature verification"
            try:
                # Create a fake signature
                fake_signature = base64.b64encode(b"fake_signature").decode()
                
                signature_data = {
                    "message": test_message,
                    "signature": fake_signature,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                
                async with self.session.post(
                    f"{self.config.integrity_service_url}/verify_signature",
                    json=signature_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("valid", False):
                            vulnerabilities.append("Invalid signature accepted")
                            recommendations.append("Implement proper digital signature verification")
            except Exception as e:
                logger.debug(f"Digital signature test failed: {e}")
            
            # Test 4: Hash collision resistance
            logger.info("Testing hash collision resistance...")
            
            # Test for hash collisions (simplified test)
            test_strings = [
                "constitutional_hash_test_1",
                "constitutional_hash_test_2",
                "different_string_same_hash",
                "another_test_string"
            ]
            
            hashes = []
            for test_string in test_strings:
                hash_value = hashlib.sha256(test_string.encode()).hexdigest()
                if hash_value in hashes:
                    vulnerabilities.append(f"Hash collision detected: {test_string}")
                    recommendations.append("Use stronger hash algorithms")
                hashes.append(hash_value)
            
            return SecurityTestResult(
                test_name=test_name,
                passed=len(vulnerabilities) == 0,
                vulnerability_found=len(vulnerabilities) > 0,
                severity="high" if vulnerabilities else "low",
                details=f"Found {len(vulnerabilities)} cryptographic vulnerabilities",
                recommendations=recommendations,
                constitutional_compliant=True
            )
            
        except Exception as e:
            logger.error(f"Cryptographic security test failed: {e}")
            return SecurityTestResult(
                test_name=test_name,
                passed=False,
                vulnerability_found=True,
                severity="critical",
                details=f"Cryptographic security test failed: {e}",
                recommendations=["Fix cryptographic security test infrastructure"],
                constitutional_compliant=False
            )
    
    async def test_constitutional_compliance_security(self) -> SecurityTestResult:
        """Test constitutional compliance security measures"""
        test_name = "Constitutional Compliance Security Test"
        vulnerabilities = []
        recommendations = []
        
        try:
            # Test 1: Constitutional hash bypass attempts
            logger.info("Testing constitutional hash bypass attempts...")
            
            bypass_attempts = [
                {},  # Missing constitutional hash
                {"constitutional_hash": None},
                {"constitutional_hash": ""},
                {"constitutional_hash": "bypass"},
                {"constitutional_hash": CONSTITUTIONAL_HASH[::-1]},  # Reversed
                {"constitutional_hash": CONSTITUTIONAL_HASH.upper()},  # Wrong case
                {"constitutional_hash": f"{CONSTITUTIONAL_HASH}extra"}  # Extra chars
            ]
            
            for attempt in bypass_attempts:
                test_data = {
                    "data": "test_data",
                    **attempt
                }
                
                try:
                    async with self.session.post(
                        f"{self.config.constitutional_ai_url}/validate",
                        json=test_data
                    ) as response:
                        if response.status == 200:
                            vulnerabilities.append(f"Constitutional hash bypass: {attempt}")
                            recommendations.append("Implement mandatory constitutional hash validation")
                except Exception as e:
                    logger.debug(f"Constitutional bypass test failed: {e}")
            
            # Test 2: Constitutional compliance tampering
            logger.info("Testing constitutional compliance tampering...")
            
            tampered_requests = [
                {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "compliance_override": True,
                    "data": "non_compliant_data"
                },
                {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "force_approve": True,
                    "data": "test_data"
                },
                {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "skip_validation": True,
                    "data": "test_data"
                }
            ]
            
            for tampered_request in tampered_requests:
                try:
                    async with self.session.post(
                        f"{self.config.constitutional_ai_url}/validate",
                        json=tampered_request
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get("compliant", False):
                                vulnerabilities.append(f"Constitutional tampering successful: {tampered_request}")
                                recommendations.append("Prevent constitutional compliance tampering")
                except Exception as e:
                    logger.debug(f"Constitutional tampering test failed: {e}")
            
            # Test 3: Audit trail manipulation
            logger.info("Testing audit trail manipulation...")
            
            manipulation_attempts = [
                {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "audit_action": "delete",
                    "target": "previous_audit_entry"
                },
                {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "audit_action": "modify",
                    "target": "audit_timestamp"
                },
                {
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "audit_action": "create",
                    "fake_entry": "unauthorized_action"
                }
            ]
            
            for attempt in manipulation_attempts:
                try:
                    async with self.session.post(
                        f"{self.config.integrity_service_url}/audit",
                        json=attempt
                    ) as response:
                        if response.status == 200:
                            vulnerabilities.append(f"Audit trail manipulation: {attempt}")
                            recommendations.append("Implement immutable audit trail protection")
                except Exception as e:
                    logger.debug(f"Audit manipulation test failed: {e}")
            
            return SecurityTestResult(
                test_name=test_name,
                passed=len(vulnerabilities) == 0,
                vulnerability_found=len(vulnerabilities) > 0,
                severity="critical" if vulnerabilities else "low",
                details=f"Found {len(vulnerabilities)} constitutional compliance vulnerabilities",
                recommendations=recommendations,
                constitutional_compliant=len(vulnerabilities) == 0
            )
            
        except Exception as e:
            logger.error(f"Constitutional compliance security test failed: {e}")
            return SecurityTestResult(
                test_name=test_name,
                passed=False,
                vulnerability_found=True,
                severity="critical",
                details=f"Constitutional compliance security test failed: {e}",
                recommendations=["Fix constitutional compliance security test infrastructure"],
                constitutional_compliant=False
            )
    
    async def test_multi_tenant_security(self) -> SecurityTestResult:
        """Test multi-tenant security isolation"""
        test_name = "Multi-Tenant Security Test"
        vulnerabilities = []
        recommendations = []
        
        try:
            # Test 1: Tenant isolation
            logger.info("Testing tenant isolation...")
            
            # Create test data for different tenants
            tenant_a_data = {
                "tenant_id": "tenant_a",
                "data": "confidential_data_a",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            tenant_b_data = {
                "tenant_id": "tenant_b",
                "data": "confidential_data_b",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            # Try to access tenant A data with tenant B credentials
            try:
                # First create data for tenant A
                async with self.session.post(
                    f"{self.config.base_url}/api/v1/tenant/data",
                    json=tenant_a_data
                ) as response:
                    if response.status == 201:
                        # Now try to access with tenant B credentials
                        headers = {"X-Tenant-ID": "tenant_b"}
                        async with self.session.get(
                            f"{self.config.base_url}/api/v1/tenant/data",
                            headers=headers
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                if "confidential_data_a" in str(data):
                                    vulnerabilities.append("Tenant isolation breach detected")
                                    recommendations.append("Implement proper tenant data isolation")
            except Exception as e:
                logger.debug(f"Tenant isolation test failed: {e}")
            
            # Test 2: Cross-tenant privilege escalation
            logger.info("Testing cross-tenant privilege escalation...")
            
            escalation_attempts = [
                {"tenant_id": "tenant_a", "escalate_to": "tenant_b"},
                {"tenant_id": "*", "access_all": True},
                {"tenant_id": "admin", "global_access": True}
            ]
            
            for attempt in escalation_attempts:
                test_data = {
                    **attempt,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                
                try:
                    async with self.session.post(
                        f"{self.config.base_url}/api/v1/tenant/escalate",
                        json=test_data
                    ) as response:
                        if response.status == 200:
                            vulnerabilities.append(f"Privilege escalation successful: {attempt}")
                            recommendations.append("Prevent cross-tenant privilege escalation")
                except Exception as e:
                    logger.debug(f"Privilege escalation test failed: {e}")
            
            # Test 3: Tenant enumeration
            logger.info("Testing tenant enumeration...")
            
            # Try to enumerate all tenants
            try:
                async with self.session.get(
                    f"{self.config.base_url}/api/v1/tenants"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list) and len(data) > 0:
                            vulnerabilities.append("Tenant enumeration possible")
                            recommendations.append("Restrict tenant enumeration to authorized users")
            except Exception as e:
                logger.debug(f"Tenant enumeration test failed: {e}")
            
            return SecurityTestResult(
                test_name=test_name,
                passed=len(vulnerabilities) == 0,
                vulnerability_found=len(vulnerabilities) > 0,
                severity="high" if vulnerabilities else "low",
                details=f"Found {len(vulnerabilities)} multi-tenant security vulnerabilities",
                recommendations=recommendations,
                constitutional_compliant=True
            )
            
        except Exception as e:
            logger.error(f"Multi-tenant security test failed: {e}")
            return SecurityTestResult(
                test_name=test_name,
                passed=False,
                vulnerability_found=True,
                severity="critical",
                details=f"Multi-tenant security test failed: {e}",
                recommendations=["Fix multi-tenant security test infrastructure"],
                constitutional_compliant=False
            )
    
    async def _get_valid_token(self) -> Optional[str]:
        """Get a valid JWT token for testing"""
        try:
            auth_data = {
                "username": "test_user",
                "password": "test_password",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
            
            async with self.session.post(
                f"{self.config.auth_service_url}/auth/login",
                json=auth_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("access_token")
        except Exception as e:
            logger.debug(f"Failed to get valid token: {e}")
        
        return None
    
    async def run_all_security_tests(self) -> List[SecurityTestResult]:
        """Run all security tests and return results"""
        logger.info("🔒 Starting comprehensive security testing...")
        
        # Run all security tests
        test_methods = [
            self.test_authentication_security,
            self.test_input_validation_security,
            self.test_cryptographic_security,
            self.test_constitutional_compliance_security,
            self.test_multi_tenant_security
        ]
        
        results = []
        for test_method in test_methods:
            try:
                result = await test_method()
                results.append(result)
                logger.info(f"✅ {result.test_name}: {'PASSED' if result.passed else 'FAILED'}")
            except Exception as e:
                logger.error(f"❌ {test_method.__name__} failed: {e}")
                results.append(SecurityTestResult(
                    test_name=test_method.__name__,
                    passed=False,
                    vulnerability_found=True,
                    severity="critical",
                    details=f"Test execution failed: {e}",
                    recommendations=["Fix test execution environment"],
                    constitutional_compliant=False
                ))
        
        return results
    
    def generate_security_report(self, results: List[SecurityTestResult]) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        
        vulnerabilities_found = sum(1 for r in results if r.vulnerability_found)
        critical_issues = sum(1 for r in results if r.severity == "critical")
        high_issues = sum(1 for r in results if r.severity == "high")
        medium_issues = sum(1 for r in results if r.severity == "medium")
        low_issues = sum(1 for r in results if r.severity == "low")
        
        constitutional_compliant = sum(1 for r in results if r.constitutional_compliant)
        
        report = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "test_execution_time": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round(passed_tests / total_tests * 100, 2) if total_tests > 0 else 0,
                "vulnerabilities_found": vulnerabilities_found,
                "constitutional_compliance_rate": round(constitutional_compliant / total_tests * 100, 2) if total_tests > 0 else 0
            },
            "severity_breakdown": {
                "critical": critical_issues,
                "high": high_issues,
                "medium": medium_issues,
                "low": low_issues
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "vulnerability_found": r.vulnerability_found,
                    "severity": r.severity,
                    "details": r.details,
                    "recommendations": r.recommendations,
                    "constitutional_compliant": r.constitutional_compliant
                }
                for r in results
            ],
            "recommendations": {
                "immediate_action": [
                    r.recommendations for r in results 
                    if r.severity in ["critical", "high"] and r.recommendations
                ],
                "security_improvements": [
                    r.recommendations for r in results 
                    if r.severity in ["medium", "low"] and r.recommendations
                ]
            }
        }
        
        return report

# pytest fixtures and test functions

@pytest.fixture
def security_config():
    """Provide security test configuration"""
    return SecurityTestConfig()

@pytest.mark.security
@pytest.mark.asyncio
async def test_authentication_security(security_config):
    """Test authentication security vulnerabilities"""
    async with SecurityTestSuite(security_config) as suite:
        result = await suite.test_authentication_security()
        assert result.constitutional_compliant, "Authentication security must be constitutionally compliant"
        if result.vulnerability_found:
            pytest.fail(f"Authentication security vulnerabilities found: {result.details}")

@pytest.mark.security
@pytest.mark.asyncio
async def test_input_validation_security(security_config):
    """Test input validation security"""
    async with SecurityTestSuite(security_config) as suite:
        result = await suite.test_input_validation_security()
        assert result.constitutional_compliant, "Input validation security must be constitutionally compliant"
        if result.vulnerability_found:
            pytest.fail(f"Input validation security vulnerabilities found: {result.details}")

@pytest.mark.security
@pytest.mark.asyncio
async def test_cryptographic_security(security_config):
    """Test cryptographic security implementation"""
    async with SecurityTestSuite(security_config) as suite:
        result = await suite.test_cryptographic_security()
        assert result.constitutional_compliant, "Cryptographic security must be constitutionally compliant"
        if result.vulnerability_found:
            pytest.fail(f"Cryptographic security vulnerabilities found: {result.details}")

@pytest.mark.security
@pytest.mark.asyncio
async def test_constitutional_compliance_security(security_config):
    """Test constitutional compliance security measures"""
    async with SecurityTestSuite(security_config) as suite:
        result = await suite.test_constitutional_compliance_security()
        assert result.constitutional_compliant, "Constitutional compliance security must be constitutionally compliant"
        if result.vulnerability_found:
            pytest.fail(f"Constitutional compliance security vulnerabilities found: {result.details}")

@pytest.mark.security
@pytest.mark.asyncio
async def test_multi_tenant_security(security_config):
    """Test multi-tenant security isolation"""
    async with SecurityTestSuite(security_config) as suite:
        result = await suite.test_multi_tenant_security()
        assert result.constitutional_compliant, "Multi-tenant security must be constitutionally compliant"
        if result.vulnerability_found:
            pytest.fail(f"Multi-tenant security vulnerabilities found: {result.details}")

@pytest.mark.security
@pytest.mark.asyncio
async def test_comprehensive_security_suite(security_config):
    """Run comprehensive security test suite"""
    async with SecurityTestSuite(security_config) as suite:
        results = await suite.run_all_security_tests()
        report = suite.generate_security_report(results)
        
        # Validate overall security posture
        assert report["summary"]["constitutional_compliance_rate"] >= 95, "Constitutional compliance rate must be >= 95%"
        assert report["severity_breakdown"]["critical"] == 0, "No critical security vulnerabilities allowed"
        assert report["severity_breakdown"]["high"] <= 2, "Maximum 2 high severity vulnerabilities allowed"
        
        # Log security report
        logger.info("🔒 Security Test Report:")
        logger.info(f"   Success Rate: {report['summary']['success_rate']}%")
        logger.info(f"   Constitutional Compliance: {report['summary']['constitutional_compliance_rate']}%")
        logger.info(f"   Vulnerabilities Found: {report['summary']['vulnerabilities_found']}")
        logger.info(f"   Critical Issues: {report['severity_breakdown']['critical']}")
        logger.info(f"   High Issues: {report['severity_breakdown']['high']}")

if __name__ == "__main__":
    # Run security tests
    pytest.main([__file__, "-v", "--tb=short", "-m", "security"])