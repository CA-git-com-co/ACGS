#!/usr/bin/env python3
"""
ACGS-2 API Endpoint Testing Suite
Constitutional Hash: cdd01ef066bc6cf2
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class APIEndpoint:
    service_name: str
    base_url: str
    endpoints: List[Dict[str, Any]]
    auth_required: bool = False

@dataclass
class APITestResult:
    service: str
    endpoint: str
    method: str
    status: str
    response_time_ms: float
    status_code: int
    constitutional_compliance: bool
    details: Dict[str, Any]
    timestamp: str

class APIEndpointTestSuite:
    def __init__(self):
        self.results: List[APITestResult] = []
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Define API endpoints to test
        self.api_endpoints = [
            APIEndpoint(
                service_name="Constitutional AI",
                base_url="http://localhost:32768",  # Mapped port
                endpoints=[
                    {"path": "/health", "method": "GET", "expected_status": 200},
                    {"path": "/api/v1/constitutional/validate", "method": "POST", "expected_status": [200, 422], 
                     "payload": {"text": "test constitutional validation", "constitutional_hash": CONSTITUTIONAL_HASH}},
                    {"path": "/api/v1/constitutional/analyze", "method": "POST", "expected_status": [200, 422],
                     "payload": {"content": "test analysis", "constitutional_hash": CONSTITUTIONAL_HASH}},
                ]
            ),
            APIEndpoint(
                service_name="Auth Service",
                base_url="http://localhost:8016",
                endpoints=[
                    {"path": "/health", "method": "GET", "expected_status": 200},
                    {"path": "/api/v1/auth/status", "method": "GET", "expected_status": [200, 401]},
                    {"path": "/api/v1/auth/validate", "method": "POST", "expected_status": [200, 400, 422],
                     "payload": {"token": "test_token", "constitutional_hash": CONSTITUTIONAL_HASH}},
                ]
            ),
            APIEndpoint(
                service_name="Agent HITL",
                base_url="http://localhost:8008",
                endpoints=[
                    {"path": "/health", "method": "GET", "expected_status": 200},
                    {"path": "/api/v1/hitl/status", "method": "GET", "expected_status": [200, 404]},
                ]
            ),
        ]
    
    def log_result(self, service: str, endpoint: str, method: str, status: str, 
                   response_time_ms: float, status_code: int, constitutional_compliance: bool, 
                   details: Dict[str, Any]):
        """Log API test result"""
        result = APITestResult(
            service=service,
            endpoint=endpoint,
            method=method,
            status=status,
            response_time_ms=response_time_ms,
            status_code=status_code,
            constitutional_compliance=constitutional_compliance,
            details=details,
            timestamp=datetime.now().isoformat()
        )
        self.results.append(result)
        logger.info(f"{service} {method} {endpoint}: {status} ({status_code}) - {response_time_ms:.2f}ms (Constitutional: {constitutional_compliance})")
    
    def test_endpoint(self, api_endpoint: APIEndpoint, endpoint_config: Dict[str, Any]) -> bool:
        """Test individual API endpoint"""
        url = f"{api_endpoint.base_url}{endpoint_config['path']}"
        method = endpoint_config["method"]
        expected_status = endpoint_config["expected_status"]
        payload = endpoint_config.get("payload")
        
        if isinstance(expected_status, int):
            expected_status = [expected_status]
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                headers = {"Content-Type": "application/json"}
                response = self.session.post(url, json=payload, headers=headers)
            elif method == "PUT":
                headers = {"Content-Type": "application/json"}
                response = self.session.put(url, json=payload, headers=headers)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Check if status code is expected
            status_ok = response.status_code in expected_status
            
            # Check constitutional compliance in response
            constitutional_compliance = False
            response_data = {}
            
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    response_data = response.json()
                    constitutional_compliance = (
                        response_data.get("constitutional_hash") == CONSTITUTIONAL_HASH or
                        CONSTITUTIONAL_HASH in str(response_data)
                    )
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text[:500]}  # Truncate long responses
            
            # For health endpoints, always check constitutional compliance
            if endpoint_config["path"] == "/health":
                constitutional_compliance = response_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
            
            details = {
                "url": url,
                "expected_status_codes": expected_status,
                "actual_status_code": response.status_code,
                "response_size_bytes": len(response.content),
                "response_headers": dict(response.headers),
                "response_data": response_data,
                "payload_sent": payload
            }
            
            if status_ok:
                self.log_result(
                    api_endpoint.service_name,
                    endpoint_config["path"],
                    method,
                    "PASS",
                    response_time_ms,
                    response.status_code,
                    constitutional_compliance,
                    details
                )
                return True
            else:
                self.log_result(
                    api_endpoint.service_name,
                    endpoint_config["path"],
                    method,
                    "FAIL",
                    response_time_ms,
                    response.status_code,
                    False,
                    details
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                api_endpoint.service_name,
                endpoint_config["path"],
                method,
                "FAIL",
                0.0,
                0,
                False,
                {"error": str(e), "url": url, "payload_sent": payload}
            )
            return False
        except Exception as e:
            self.log_result(
                api_endpoint.service_name,
                endpoint_config["path"],
                method,
                "FAIL",
                0.0,
                0,
                False,
                {"error": f"Unexpected error: {str(e)}", "url": url, "payload_sent": payload}
            )
            return False
    
    def test_service_integration(self) -> Dict[str, Any]:
        """Test service-to-service communication"""
        integration_results = {}
        
        try:
            # Test Constitutional AI to Auth Service integration
            auth_health_response = self.session.get("http://localhost:8016/health", timeout=5)
            constitutional_health_response = self.session.get("http://localhost:32768/health", timeout=5)
            
            if auth_health_response.status_code == 200 and constitutional_health_response.status_code == 200:
                auth_data = auth_health_response.json()
                constitutional_data = constitutional_health_response.json()
                
                # Check if both services have the same constitutional hash
                hash_consistency = (
                    auth_data.get("constitutional_hash") == constitutional_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                )
                
                integration_results["auth_constitutional_integration"] = {
                    "status": "PASS" if hash_consistency else "FAIL",
                    "constitutional_hash_consistent": hash_consistency,
                    "auth_hash": auth_data.get("constitutional_hash"),
                    "constitutional_hash": constitutional_data.get("constitutional_hash"),
                    "expected_hash": CONSTITUTIONAL_HASH
                }
            else:
                integration_results["auth_constitutional_integration"] = {
                    "status": "FAIL",
                    "error": "One or both services not responding",
                    "auth_status": auth_health_response.status_code,
                    "constitutional_status": constitutional_health_response.status_code
                }
                
        except Exception as e:
            integration_results["auth_constitutional_integration"] = {
                "status": "FAIL",
                "error": str(e)
            }
        
        return integration_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API endpoint tests"""
        logger.info("Starting ACGS-2 API Endpoint Testing")
        logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        test_summary = {
            "start_time": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "services_tested": len(self.api_endpoints),
            "endpoints_tested": 0,
            "endpoints_passed": 0,
            "constitutional_compliance_rate": 0.0,
            "average_response_time_ms": 0.0,
            "integration_tests": {}
        }
        
        # Test all endpoints
        for api_endpoint in self.api_endpoints:
            for endpoint_config in api_endpoint.endpoints:
                test_summary["endpoints_tested"] += 1
                if self.test_endpoint(api_endpoint, endpoint_config):
                    test_summary["endpoints_passed"] += 1
        
        # Test service integration
        test_summary["integration_tests"] = self.test_service_integration()
        
        # Calculate metrics
        if self.results:
            compliant_tests = sum(1 for result in self.results if result.constitutional_compliance)
            test_summary["constitutional_compliance_rate"] = (compliant_tests / len(self.results)) * 100
            
            response_times = [result.response_time_ms for result in self.results if result.response_time_ms > 0]
            test_summary["average_response_time_ms"] = sum(response_times) / len(response_times) if response_times else 0
        
        test_summary["end_time"] = datetime.now().isoformat()
        return test_summary

def main():
    """Main test execution"""
    test_suite = APIEndpointTestSuite()
    summary = test_suite.run_all_tests()
    
    print("\n" + "="*80)
    print("ACGS-2 API ENDPOINT TEST RESULTS")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Services Tested: {summary['services_tested']}")
    print(f"Endpoints Tested: {summary['endpoints_tested']}")
    print(f"Endpoints Passed: {summary['endpoints_passed']}")
    print(f"Constitutional Compliance Rate: {summary['constitutional_compliance_rate']:.1f}%")
    print(f"Average Response Time: {summary['average_response_time_ms']:.2f}ms")
    
    print("\nDETAILED RESULTS:")
    for result in test_suite.results:
        compliance_status = "✅" if result.constitutional_compliance else "❌"
        print(f"{compliance_status} {result.service} {result.method} {result.endpoint}: {result.status} ({result.status_code}) - {result.response_time_ms:.2f}ms")
    
    print("\nINTEGRATION TEST RESULTS:")
    for test_name, test_result in summary["integration_tests"].items():
        status_icon = "✅" if test_result["status"] == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {test_result['status']}")
        if "constitutional_hash_consistent" in test_result:
            print(f"    Constitutional Hash Consistency: {test_result['constitutional_hash_consistent']}")
    
    # Save results
    with open("api_endpoint_results.json", "w") as f:
        json.dump({
            "summary": summary,
            "detailed_results": [
                {
                    "service": r.service,
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "status": r.status,
                    "response_time_ms": r.response_time_ms,
                    "status_code": r.status_code,
                    "constitutional_compliance": r.constitutional_compliance,
                    "details": r.details,
                    "timestamp": r.timestamp
                } for r in test_suite.results
            ]
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: api_endpoint_results.json")
    
    if summary["constitutional_compliance_rate"] < 80.0:  # Allow some flexibility for API endpoints
        print(f"\n⚠️  WARNING: Constitutional compliance rate is {summary['constitutional_compliance_rate']:.1f}% (target: >80%)")
        return 1
    else:
        print(f"\n✅ SUCCESS: API tests completed with {summary['constitutional_compliance_rate']:.1f}% constitutional compliance")
        return 0

if __name__ == "__main__":
    exit(main())
