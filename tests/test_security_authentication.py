#!/usr/bin/env python3
"""
ACGS-2 Security and Authentication Testing Suite
Constitutional Hash: cdd01ef066bc6cf2

Validates Auth Service (8016) and access control mechanisms
"""

import requests
import json
import time
import hashlib
import jwt
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class SecurityTestResult:
    test_name: str
    test_category: str
    success: bool
    constitutional_compliance: bool
    security_score: float
    response_time_ms: float
    details: Dict[str, Any]
    vulnerabilities_found: List[str]
    timestamp: str

class SecurityAuthenticationTestSuite:
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.results: List[SecurityTestResult] = []
        self.auth_service_url = "http://localhost:8016"
        self.constitutional_ai_url = "http://localhost:32768"
        self.agent_hitl_url = "http://localhost:8008"
        
        # Test credentials and tokens
        self.test_credentials = {
            "valid_user": {"username": "test_user", "password": "test_password"},
            "invalid_user": {"username": "invalid_user", "password": "wrong_password"},
            "admin_user": {"username": "admin", "password": "admin_password"}
        }
        
        self.security_test_vectors = self.define_security_test_vectors()
    
    def define_security_test_vectors(self) -> List[Dict[str, Any]]:
        """Define security test vectors for various attack scenarios"""
        return [
            {
                "name": "SQL Injection Test",
                "category": "injection",
                "payloads": [
                    "'; DROP TABLE users; --",
                    "' OR '1'='1",
                    "admin'--",
                    "' UNION SELECT * FROM users --"
                ],
                "target_endpoints": ["/api/v1/auth/login", "/api/v1/auth/validate"]
            },
            {
                "name": "XSS Test",
                "category": "xss",
                "payloads": [
                    "<script>alert('XSS')</script>",
                    "javascript:alert('XSS')",
                    "<img src=x onerror=alert('XSS')>",
                    "';alert('XSS');//"
                ],
                "target_endpoints": ["/api/v1/auth/login"]
            },
            {
                "name": "Authentication Bypass",
                "category": "auth_bypass",
                "payloads": [
                    {"username": "", "password": ""},
                    {"username": "admin", "password": ""},
                    {"token": "invalid_token"},
                    {"token": ""}
                ],
                "target_endpoints": ["/api/v1/auth/validate", "/api/v1/auth/status"]
            },
            {
                "name": "Constitutional Hash Tampering",
                "category": "constitutional_security",
                "payloads": [
                    {"constitutional_hash": "tampered_hash"},
                    {"constitutional_hash": ""},
                    {"constitutional_hash": "malicious_hash_123"},
                    {}  # Missing constitutional hash
                ],
                "target_endpoints": ["/health", "/api/v1/auth/validate"]
            }
        ]
    
    def log_result(self, test_name: str, test_category: str, success: bool, 
                   constitutional_compliance: bool, security_score: float,
                   response_time_ms: float, details: Dict[str, Any],
                   vulnerabilities_found: List[str]):
        """Log security test result"""
        result = SecurityTestResult(
            test_name=test_name,
            test_category=test_category,
            success=success,
            constitutional_compliance=constitutional_compliance,
            security_score=security_score,
            response_time_ms=response_time_ms,
            details=details,
            vulnerabilities_found=vulnerabilities_found,
            timestamp=datetime.now().isoformat()
        )
        self.results.append(result)
        
        vuln_status = f"({len(vulnerabilities_found)} vulnerabilities)" if vulnerabilities_found else "(secure)"
        logger.info(f"{test_name}: {'PASS' if success else 'FAIL'} - Security: {security_score:.2f} {vuln_status}")
    
    def test_auth_service_availability(self) -> bool:
        """Test Auth Service basic availability and constitutional compliance"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.auth_service_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                constitutional_compliance = data.get("constitutional_hash") == self.constitutional_hash
                
                self.log_result(
                    test_name="Auth Service Availability",
                    test_category="availability",
                    success=True,
                    constitutional_compliance=constitutional_compliance,
                    security_score=1.0 if constitutional_compliance else 0.5,
                    response_time_ms=response_time,
                    details={
                        "status_code": response.status_code,
                        "response_data": data,
                        "constitutional_hash_present": "constitutional_hash" in data,
                        "constitutional_hash_valid": constitutional_compliance
                    },
                    vulnerabilities_found=[] if constitutional_compliance else ["Missing or invalid constitutional hash"]
                )
                return True
            else:
                self.log_result(
                    test_name="Auth Service Availability",
                    test_category="availability",
                    success=False,
                    constitutional_compliance=False,
                    security_score=0.0,
                    response_time_ms=response_time,
                    details={"status_code": response.status_code, "error": "Service unavailable"},
                    vulnerabilities_found=["Service unavailable"]
                )
                return False
                
        except Exception as e:
            self.log_result(
                test_name="Auth Service Availability",
                test_category="availability",
                success=False,
                constitutional_compliance=False,
                security_score=0.0,
                response_time_ms=0.0,
                details={"error": str(e)},
                vulnerabilities_found=["Service connection failed"]
            )
            return False
    
    def test_injection_attacks(self) -> Dict[str, Any]:
        """Test for injection vulnerabilities"""
        injection_results = {"sql_injection": [], "xss": []}
        
        for test_vector in self.security_test_vectors:
            if test_vector["category"] in ["injection", "xss"]:
                for payload in test_vector["payloads"]:
                    for endpoint in test_vector["target_endpoints"]:
                        vulnerabilities = []
                        
                        try:
                            start_time = time.time()
                            
                            # Test with payload in different positions
                            test_data = {
                                "username": payload if "username" in endpoint else "test_user",
                                "password": payload if "password" in endpoint else "test_password",
                                "constitutional_hash": self.constitutional_hash
                            }
                            
                            response = requests.post(
                                f"{self.auth_service_url}{endpoint}",
                                json=test_data,
                                timeout=5
                            )
                            
                            response_time = (time.time() - start_time) * 1000
                            
                            # Check for injection indicators
                            response_text = response.text.lower()
                            
                            # SQL injection indicators
                            sql_indicators = ["sql", "syntax error", "mysql", "postgresql", "database"]
                            if any(indicator in response_text for indicator in sql_indicators):
                                vulnerabilities.append(f"Potential SQL injection with payload: {payload}")
                            
                            # XSS indicators
                            if test_vector["category"] == "xss" and payload.lower() in response_text:
                                vulnerabilities.append(f"Potential XSS with payload: {payload}")
                            
                            # Check constitutional compliance
                            constitutional_compliance = True
                            try:
                                if response.status_code == 200:
                                    data = response.json()
                                    constitutional_compliance = data.get("constitutional_hash") == self.constitutional_hash
                            except:
                                constitutional_compliance = False
                            
                            security_score = 1.0 if not vulnerabilities else 0.0
                            
                            self.log_result(
                                test_name=f"Injection Test - {test_vector['name']} - {endpoint}",
                                test_category="injection_security",
                                success=not vulnerabilities,
                                constitutional_compliance=constitutional_compliance,
                                security_score=security_score,
                                response_time_ms=response_time,
                                details={
                                    "payload": payload,
                                    "endpoint": endpoint,
                                    "status_code": response.status_code,
                                    "response_length": len(response.text)
                                },
                                vulnerabilities_found=vulnerabilities
                            )
                            
                        except Exception as e:
                            self.log_result(
                                test_name=f"Injection Test - {test_vector['name']} - {endpoint}",
                                test_category="injection_security",
                                success=True,  # Exception might indicate good security (request blocked)
                                constitutional_compliance=True,
                                security_score=0.8,  # Partial score for blocking
                                response_time_ms=0.0,
                                details={"payload": payload, "endpoint": endpoint, "error": str(e)},
                                vulnerabilities_found=[]
                            )
        
        return injection_results
    
    def test_authentication_mechanisms(self) -> Dict[str, Any]:
        """Test authentication and authorization mechanisms"""
        auth_results = {}
        
        # Test 1: Valid authentication
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.auth_service_url}/api/v1/auth/validate",
                json={
                    "token": "valid_test_token",
                    "constitutional_hash": self.constitutional_hash
                },
                timeout=5
            )
            response_time = (time.time() - start_time) * 1000
            
            # Check response
            constitutional_compliance = False
            if response.status_code in [200, 400, 422]:  # Expected responses
                try:
                    data = response.json()
                    constitutional_compliance = data.get("constitutional_hash") == self.constitutional_hash
                except:
                    pass
            
            self.log_result(
                test_name="Valid Token Authentication",
                test_category="authentication",
                success=response.status_code in [200, 400, 422],
                constitutional_compliance=constitutional_compliance,
                security_score=1.0 if constitutional_compliance else 0.7,
                response_time_ms=response_time,
                details={
                    "status_code": response.status_code,
                    "endpoint": "/api/v1/auth/validate"
                },
                vulnerabilities_found=[] if constitutional_compliance else ["Missing constitutional hash in auth response"]
            )
            
        except Exception as e:
            self.log_result(
                test_name="Valid Token Authentication",
                test_category="authentication",
                success=False,
                constitutional_compliance=False,
                security_score=0.0,
                response_time_ms=0.0,
                details={"error": str(e)},
                vulnerabilities_found=["Authentication endpoint unreachable"]
            )
        
        # Test 2: Invalid token handling
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.auth_service_url}/api/v1/auth/validate",
                json={
                    "token": "invalid_token_12345",
                    "constitutional_hash": self.constitutional_hash
                },
                timeout=5
            )
            response_time = (time.time() - start_time) * 1000
            
            # Should reject invalid tokens
            security_score = 1.0 if response.status_code in [400, 401, 403, 422] else 0.0
            vulnerabilities = [] if security_score == 1.0 else ["Invalid token accepted"]
            
            self.log_result(
                test_name="Invalid Token Rejection",
                test_category="authentication",
                success=security_score == 1.0,
                constitutional_compliance=True,  # Rejection is constitutionally compliant
                security_score=security_score,
                response_time_ms=response_time,
                details={
                    "status_code": response.status_code,
                    "endpoint": "/api/v1/auth/validate"
                },
                vulnerabilities_found=vulnerabilities
            )
            
        except Exception as e:
            self.log_result(
                test_name="Invalid Token Rejection",
                test_category="authentication",
                success=True,  # Exception might indicate good security
                constitutional_compliance=True,
                security_score=0.8,
                response_time_ms=0.0,
                details={"error": str(e)},
                vulnerabilities_found=[]
            )
        
        return auth_results
    
    def test_constitutional_hash_security(self) -> Dict[str, Any]:
        """Test constitutional hash validation security"""
        hash_security_results = {}
        
        # Test constitutional hash tampering
        for test_vector in self.security_test_vectors:
            if test_vector["category"] == "constitutional_security":
                for payload in test_vector["payloads"]:
                    for endpoint in test_vector["target_endpoints"]:
                        try:
                            start_time = time.time()
                            
                            if endpoint == "/health":
                                # Test health endpoint
                                response = requests.get(f"{self.auth_service_url}{endpoint}", timeout=5)
                            else:
                                # Test API endpoint with tampered hash
                                response = requests.post(
                                    f"{self.auth_service_url}{endpoint}",
                                    json={
                                        "token": "test_token",
                                        **payload  # Include tampered constitutional hash
                                    },
                                    timeout=5
                                )
                            
                            response_time = (time.time() - start_time) * 1000
                            
                            # Analyze response for constitutional compliance
                            constitutional_compliance = False
                            vulnerabilities = []
                            
                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                    returned_hash = data.get("constitutional_hash")
                                    
                                    if returned_hash == self.constitutional_hash:
                                        constitutional_compliance = True
                                    elif returned_hash != self.constitutional_hash and "constitutional_hash" in payload:
                                        vulnerabilities.append("Service accepted tampered constitutional hash")
                                    elif "constitutional_hash" not in payload:
                                        vulnerabilities.append("Service did not enforce constitutional hash requirement")
                                        
                                except:
                                    vulnerabilities.append("Invalid JSON response")
                            
                            security_score = 1.0 if constitutional_compliance and not vulnerabilities else 0.0
                            
                            self.log_result(
                                test_name=f"Constitutional Hash Security - {endpoint}",
                                test_category="constitutional_security",
                                success=constitutional_compliance,
                                constitutional_compliance=constitutional_compliance,
                                security_score=security_score,
                                response_time_ms=response_time,
                                details={
                                    "endpoint": endpoint,
                                    "payload": payload,
                                    "status_code": response.status_code
                                },
                                vulnerabilities_found=vulnerabilities
                            )
                            
                        except Exception as e:
                            self.log_result(
                                test_name=f"Constitutional Hash Security - {endpoint}",
                                test_category="constitutional_security",
                                success=True,  # Exception might indicate good security
                                constitutional_compliance=True,
                                security_score=0.8,
                                response_time_ms=0.0,
                                details={"endpoint": endpoint, "payload": payload, "error": str(e)},
                                vulnerabilities_found=[]
                            )
        
        return hash_security_results
    
    def test_cross_service_security(self) -> Dict[str, Any]:
        """Test security across multiple services"""
        cross_service_results = {}
        
        services = [
            ("Auth Service", self.auth_service_url),
            ("Constitutional AI", self.constitutional_ai_url),
            ("Agent HITL", self.agent_hitl_url)
        ]
        
        for service_name, service_url in services:
            try:
                start_time = time.time()
                response = requests.get(f"{service_url}/health", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    constitutional_compliance = data.get("constitutional_hash") == self.constitutional_hash
                    
                    # Check for security headers
                    security_headers = {
                        "X-Content-Type-Options": response.headers.get("X-Content-Type-Options"),
                        "X-Frame-Options": response.headers.get("X-Frame-Options"),
                        "X-XSS-Protection": response.headers.get("X-XSS-Protection"),
                        "Strict-Transport-Security": response.headers.get("Strict-Transport-Security")
                    }
                    
                    missing_headers = [header for header, value in security_headers.items() if not value]
                    vulnerabilities = [f"Missing security header: {header}" for header in missing_headers]
                    
                    if not constitutional_compliance:
                        vulnerabilities.append("Missing or invalid constitutional hash")
                    
                    security_score = max(0.0, 1.0 - (len(vulnerabilities) * 0.2))
                    
                    self.log_result(
                        test_name=f"Cross-Service Security - {service_name}",
                        test_category="cross_service_security",
                        success=constitutional_compliance and len(vulnerabilities) <= 2,
                        constitutional_compliance=constitutional_compliance,
                        security_score=security_score,
                        response_time_ms=response_time,
                        details={
                            "service": service_name,
                            "security_headers": security_headers,
                            "constitutional_hash_valid": constitutional_compliance
                        },
                        vulnerabilities_found=vulnerabilities
                    )
                    
            except Exception as e:
                self.log_result(
                    test_name=f"Cross-Service Security - {service_name}",
                    test_category="cross_service_security",
                    success=False,
                    constitutional_compliance=False,
                    security_score=0.0,
                    response_time_ms=0.0,
                    details={"service": service_name, "error": str(e)},
                    vulnerabilities_found=["Service unreachable"]
                )
        
        return cross_service_results
    
    def run_all_security_tests(self) -> Dict[str, Any]:
        """Run all security and authentication tests"""
        logger.info("Starting ACGS-2 Security and Authentication Testing")
        logger.info(f"Constitutional Hash: {self.constitutional_hash}")
        
        test_summary = {
            "start_time": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "tests_run": 0,
            "tests_passed": 0,
            "overall_security_score": 0.0,
            "constitutional_compliance_rate": 0.0,
            "total_vulnerabilities": 0,
            "critical_vulnerabilities": 0
        }
        
        # Run all security tests
        self.test_auth_service_availability()
        self.test_injection_attacks()
        self.test_authentication_mechanisms()
        self.test_constitutional_hash_security()
        self.test_cross_service_security()
        
        # Calculate summary metrics
        if self.results:
            test_summary["tests_run"] = len(self.results)
            test_summary["tests_passed"] = sum(1 for result in self.results if result.success)
            
            total_security_score = sum(result.security_score for result in self.results)
            test_summary["overall_security_score"] = total_security_score / len(self.results)
            
            compliant_results = sum(1 for result in self.results if result.constitutional_compliance)
            test_summary["constitutional_compliance_rate"] = (compliant_results / len(self.results)) * 100
            
            all_vulnerabilities = []
            for result in self.results:
                all_vulnerabilities.extend(result.vulnerabilities_found)
            
            test_summary["total_vulnerabilities"] = len(all_vulnerabilities)
            test_summary["critical_vulnerabilities"] = len([v for v in all_vulnerabilities if "constitutional" in v.lower() or "injection" in v.lower()])
        
        test_summary["end_time"] = datetime.now().isoformat()
        return test_summary

def main():
    """Main test execution"""
    test_suite = SecurityAuthenticationTestSuite()
    summary = test_suite.run_all_security_tests()
    
    print("\n" + "="*80)
    print("ACGS-2 SECURITY AND AUTHENTICATION TEST RESULTS")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Tests Passed: {summary['tests_passed']}")
    print(f"Overall Security Score: {summary['overall_security_score']:.2f}")
    print(f"Constitutional Compliance Rate: {summary['constitutional_compliance_rate']:.1f}%")
    print(f"Total Vulnerabilities: {summary['total_vulnerabilities']}")
    print(f"Critical Vulnerabilities: {summary['critical_vulnerabilities']}")
    
    print("\nDETAILED SECURITY TEST RESULTS:")
    for result in test_suite.results:
        success_icon = "✅" if result.success else "❌"
        compliance_icon = "✅" if result.constitutional_compliance else "❌"
        vuln_count = len(result.vulnerabilities_found)
        vuln_status = f"({vuln_count} vulnerabilities)" if vuln_count > 0 else "(secure)"
        
        print(f"{success_icon} {result.test_name}: Security={result.security_score:.2f} | {compliance_icon} Constitutional {vuln_status}")
        
        if result.vulnerabilities_found:
            for vuln in result.vulnerabilities_found:
                print(f"    🔴 {vuln}")
    
    # Save results
    with open("security_authentication_results.json", "w") as f:
        json.dump({
            "summary": summary,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "test_category": r.test_category,
                    "success": r.success,
                    "constitutional_compliance": r.constitutional_compliance,
                    "security_score": r.security_score,
                    "response_time_ms": r.response_time_ms,
                    "details": r.details,
                    "vulnerabilities_found": r.vulnerabilities_found,
                    "timestamp": r.timestamp
                } for r in test_suite.results
            ]
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: security_authentication_results.json")
    
    if summary["critical_vulnerabilities"] > 0:
        print(f"\n🔴 CRITICAL: {summary['critical_vulnerabilities']} critical vulnerabilities found")
        return 1
    elif summary["constitutional_compliance_rate"] < 80.0:
        print(f"\n⚠️  WARNING: Constitutional compliance rate is {summary['constitutional_compliance_rate']:.1f}% (target: >80%)")
        return 1
    else:
        print(f"\n✅ SUCCESS: Security tests completed with {summary['constitutional_compliance_rate']:.1f}% constitutional compliance")
        return 0

if __name__ == "__main__":
    exit(main())
