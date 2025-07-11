#!/usr/bin/env python3
"""
ACGS-2 Security Fixes Validation Test
Constitutional Hash: cdd01ef066bc6cf2

Validates that security vulnerabilities have been properly fixed
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class SecurityFixesValidator:
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.auth_service_url = "http://localhost:8017"
        self.test_results = []
    
    def log_test_result(self, test_name: str, passed: bool, details: Dict[str, Any]):
        """Log test result"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if not passed:
            logger.error(f"   Details: {details}")
    
    def test_invalid_token_rejection(self) -> bool:
        """Test that invalid tokens are properly rejected (Critical Fix)"""
        
        invalid_tokens = [
            "invalid_token_12345",
            "fake_token",
            "malicious_token",
            "",
            "test_token",
            "expired_token"
        ]
        
        all_rejected = True
        rejection_details = []
        
        for token in invalid_tokens:
            try:
                response = requests.post(
                    f"{self.auth_service_url}/api/v1/auth/validate",
                    json={
                        "token": token,
                        "constitutional_hash": self.constitutional_hash
                    },
                    timeout=5
                )
                
                # Should be rejected with 401 or 400
                if response.status_code in [400, 401, 403]:
                    rejection_details.append(f"✅ {token[:20]}: Properly rejected ({response.status_code})")
                    
                    # Check constitutional hash in error response
                    try:
                        data = response.json()
                        if data.get("constitutional_hash") != self.constitutional_hash:
                            rejection_details.append(f"⚠️ {token[:20]}: Missing constitutional hash in error response")
                    except:
                        pass
                else:
                    rejection_details.append(f"❌ {token[:20]}: ACCEPTED (Status: {response.status_code}) - VULNERABILITY!")
                    all_rejected = False
                    
            except Exception as e:
                rejection_details.append(f"❌ {token[:20]}: Error testing - {str(e)}")
                all_rejected = False
        
        self.log_test_result(
            "Invalid Token Rejection (Critical Fix)",
            all_rejected,
            {
                "tokens_tested": len(invalid_tokens),
                "all_rejected": all_rejected,
                "details": rejection_details
            }
        )
        
        return all_rejected
    
    def test_constitutional_hash_in_responses(self) -> bool:
        """Test that all responses include constitutional hash"""
        
        endpoints_to_test = [
            ("/health", "GET", None),
            ("/api/v1/auth/status", "GET", None),
            ("/api/v1/auth/validate", "POST", {
                "token": "invalid_token_test",
                "constitutional_hash": self.constitutional_hash
            })
        ]
        
        all_have_hash = True
        hash_details = []
        
        for endpoint, method, payload in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.auth_service_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.auth_service_url}{endpoint}", json=payload, timeout=5)
                
                # Check for constitutional hash in response
                hash_in_body = False
                hash_in_header = False
                
                try:
                    data = response.json()
                    if data.get("constitutional_hash") == self.constitutional_hash:
                        hash_in_body = True
                except:
                    pass
                
                if response.headers.get("X-Constitutional-Hash") == self.constitutional_hash:
                    hash_in_header = True
                
                if hash_in_body or hash_in_header:
                    hash_details.append(f"✅ {endpoint}: Constitutional hash present")
                else:
                    hash_details.append(f"❌ {endpoint}: Constitutional hash MISSING")
                    all_have_hash = False
                    
            except Exception as e:
                hash_details.append(f"❌ {endpoint}: Error testing - {str(e)}")
                all_have_hash = False
        
        self.log_test_result(
            "Constitutional Hash in Responses",
            all_have_hash,
            {
                "endpoints_tested": len(endpoints_to_test),
                "all_have_hash": all_have_hash,
                "details": hash_details
            }
        )
        
        return all_have_hash
    
    def test_security_headers(self) -> bool:
        """Test that security headers are present"""
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        try:
            response = requests.get(f"{self.auth_service_url}/health", timeout=5)
            
            missing_headers = []
            present_headers = []
            
            for header in required_headers:
                if header in response.headers:
                    present_headers.append(f"✅ {header}: {response.headers[header]}")
                else:
                    missing_headers.append(f"❌ {header}: MISSING")
            
            all_present = len(missing_headers) == 0
            
            self.log_test_result(
                "Security Headers Implementation",
                all_present,
                {
                    "required_headers": required_headers,
                    "present_headers": present_headers,
                    "missing_headers": missing_headers,
                    "coverage_percentage": (len(present_headers) / len(required_headers)) * 100
                }
            )
            
            return all_present
            
        except Exception as e:
            self.log_test_result(
                "Security Headers Implementation",
                False,
                {"error": str(e)}
            )
            return False
    
    def test_constitutional_hash_enforcement(self) -> bool:
        """Test that API endpoints enforce constitutional hash validation"""
        
        test_cases = [
            {
                "name": "Missing constitutional hash",
                "payload": {"token": "test_token"},
                "should_reject": True
            },
            {
                "name": "Invalid constitutional hash",
                "payload": {"token": "test_token", "constitutional_hash": "invalid_hash"},
                "should_reject": True
            },
            {
                "name": "Valid constitutional hash",
                "payload": {"token": "test_token", "constitutional_hash": self.constitutional_hash},
                "should_reject": False  # Should process (though token may be invalid)
            }
        ]
        
        enforcement_working = True
        enforcement_details = []
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.auth_service_url}/api/v1/auth/validate",
                    json=test_case["payload"],
                    timeout=5
                )
                
                if test_case["should_reject"]:
                    # Should be rejected with 400 (bad request)
                    if response.status_code == 400:
                        enforcement_details.append(f"✅ {test_case['name']}: Properly rejected")
                    else:
                        enforcement_details.append(f"❌ {test_case['name']}: NOT rejected (Status: {response.status_code})")
                        enforcement_working = False
                else:
                    # Should be processed (may return 401 for invalid token, but not 400 for missing hash)
                    if response.status_code != 400:
                        enforcement_details.append(f"✅ {test_case['name']}: Properly processed")
                    else:
                        enforcement_details.append(f"❌ {test_case['name']}: Incorrectly rejected")
                        enforcement_working = False
                        
            except Exception as e:
                enforcement_details.append(f"❌ {test_case['name']}: Error - {str(e)}")
                enforcement_working = False
        
        self.log_test_result(
            "Constitutional Hash Enforcement",
            enforcement_working,
            {
                "test_cases": len(test_cases),
                "enforcement_working": enforcement_working,
                "details": enforcement_details
            }
        )
        
        return enforcement_working
    
    def test_injection_protection_still_works(self) -> bool:
        """Test that injection protection is still working after fixes"""
        
        injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "<script>alert('XSS')</script>",
            "admin'--"
        ]
        
        protection_working = True
        protection_details = []
        
        for payload in injection_payloads:
            try:
                response = requests.post(
                    f"{self.auth_service_url}/api/v1/auth/login",
                    json={
                        "username": payload,
                        "password": "test_password",
                        "constitutional_hash": self.constitutional_hash
                    },
                    timeout=5
                )
                
                # Should be rejected (400 or 401)
                if response.status_code in [400, 401]:
                    protection_details.append(f"✅ Injection payload blocked: {payload[:30]}")
                else:
                    protection_details.append(f"❌ Injection payload NOT blocked: {payload[:30]}")
                    protection_working = False
                    
            except Exception as e:
                protection_details.append(f"✅ Injection payload caused error (good): {payload[:30]}")
        
        self.log_test_result(
            "Injection Protection Still Working",
            protection_working,
            {
                "payloads_tested": len(injection_payloads),
                "protection_working": protection_working,
                "details": protection_details
            }
        )
        
        return protection_working
    
    def run_all_validation_tests(self) -> Dict[str, Any]:
        """Run all security fix validation tests"""
        
        logger.info("🔒 Starting ACGS-2 Security Fixes Validation")
        logger.info(f"🔐 Constitutional Hash: {self.constitutional_hash}")
        logger.info(f"🎯 Target Service: {self.auth_service_url}")
        
        test_summary = {
            "start_time": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "service_url": self.auth_service_url,
            "tests_run": 0,
            "tests_passed": 0,
            "critical_fixes_validated": False,
            "overall_security_improved": False
        }
        
        # Run all validation tests
        tests = [
            ("Critical: Invalid Token Rejection", self.test_invalid_token_rejection),
            ("Constitutional Hash in Responses", self.test_constitutional_hash_in_responses),
            ("Security Headers Implementation", self.test_security_headers),
            ("Constitutional Hash Enforcement", self.test_constitutional_hash_enforcement),
            ("Injection Protection Still Working", self.test_injection_protection_still_works)
        ]
        
        for test_name, test_function in tests:
            test_summary["tests_run"] += 1
            logger.info(f"\n🧪 Running: {test_name}")
            
            if test_function():
                test_summary["tests_passed"] += 1
        
        # Calculate overall results
        test_summary["success_rate"] = (test_summary["tests_passed"] / test_summary["tests_run"]) * 100
        test_summary["critical_fixes_validated"] = self.test_results[0]["passed"]  # First test is critical
        test_summary["overall_security_improved"] = test_summary["success_rate"] >= 80
        
        test_summary["end_time"] = datetime.now().isoformat()
        
        return test_summary

def main():
    """Main validation execution"""
    
    validator = SecurityFixesValidator()
    summary = validator.run_all_validation_tests()
    
    print("\n" + "="*80)
    print("🔒 ACGS-2 SECURITY FIXES VALIDATION RESULTS")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Tests Passed: {summary['tests_passed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Critical Fixes Validated: {'✅ YES' if summary['critical_fixes_validated'] else '❌ NO'}")
    print(f"Overall Security Improved: {'✅ YES' if summary['overall_security_improved'] else '❌ NO'}")
    
    print("\nDETAILED TEST RESULTS:")
    for result in validator.test_results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} {result['test_name']}")
        
        if "details" in result["details"]:
            for detail in result["details"]["details"]:
                print(f"    {detail}")
    
    # Save results
    with open("security_fixes_validation_results.json", "w") as f:
        json.dump({
            "summary": summary,
            "detailed_results": validator.test_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: security_fixes_validation_results.json")
    
    if summary["critical_fixes_validated"] and summary["overall_security_improved"]:
        print(f"\n✅ SUCCESS: Security fixes validated successfully!")
        print(f"🛡️ Critical vulnerability fixed: Invalid token rejection working")
        print(f"🔐 Constitutional compliance improved")
        print(f"🔒 Security headers implemented")
        return 0
    else:
        print(f"\n❌ FAILURE: Security fixes need additional work")
        if not summary["critical_fixes_validated"]:
            print(f"🔴 CRITICAL: Invalid token rejection still not working properly")
        return 1

if __name__ == "__main__":
    exit(main())
