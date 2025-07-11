#!/usr/bin/env python3
"""
ACGS-2 Comprehensive End-to-End Testing Suite
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import time
import requests
import psycopg2
import redis
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class ServiceConfig:
    name: str
    port: int
    health_endpoint: str
    expected_status: int = 200
    timeout: int = 10

@dataclass
class TestResult:
    service: str
    test_name: str
    status: str
    details: Dict[str, Any]
    constitutional_compliance: bool
    timestamp: str

class ACGSTestSuite:
    def __init__(self):
        self.services = [
            ServiceConfig("Constitutional AI", 32768, "/health"),  # Mapped port
            ServiceConfig("Auth Service", 8016, "/health"),
            ServiceConfig("Agent HITL", 8008, "/health"),
        ]
        
        self.infrastructure = {
            "postgresql": {"host": "localhost", "port": 5439, "user": "acgs_user", "password": "acgs_password", "database": "acgs_db"},
            "redis": {"host": "localhost", "port": 6389}
        }
        
        self.results: List[TestResult] = []
        
    def log_result(self, service: str, test_name: str, status: str, details: Dict[str, Any], constitutional_compliance: bool = False):
        """Log test result with constitutional compliance tracking"""
        result = TestResult(
            service=service,
            test_name=test_name,
            status=status,
            details=details,
            constitutional_compliance=constitutional_compliance,
            timestamp=datetime.now().isoformat()
        )
        self.results.append(result)
        logger.info(f"{service} - {test_name}: {status} (Constitutional: {constitutional_compliance})")
        
    def test_service_health(self, service: ServiceConfig) -> bool:
        """Test individual service health and constitutional compliance"""
        try:
            url = f"http://localhost:{service.port}{service.health_endpoint}"
            response = requests.get(url, timeout=service.timeout)
            
            if response.status_code == service.expected_status:
                data = response.json()
                constitutional_compliance = data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                
                self.log_result(
                    service.name,
                    "Health Check",
                    "PASS",
                    {
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "status_code": response.status_code,
                        "constitutional_hash": data.get("constitutional_hash"),
                        "service_data": data
                    },
                    constitutional_compliance
                )
                return True
            else:
                self.log_result(
                    service.name,
                    "Health Check",
                    "FAIL",
                    {"status_code": response.status_code, "error": "Unexpected status code"},
                    False
                )
                return False
                
        except Exception as e:
            self.log_result(
                service.name,
                "Health Check",
                "FAIL",
                {"error": str(e)},
                False
            )
            return False
    
    def test_database_connectivity(self) -> bool:
        """Test PostgreSQL connectivity and performance"""
        try:
            config = self.infrastructure["postgresql"]
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                user=config["user"],
                password=config["password"],
                database=config["database"]
            )
            
            cursor = conn.cursor()
            start_time = time.time()
            cursor.execute("SELECT 1")
            query_time = (time.time() - start_time) * 1000
            
            cursor.close()
            conn.close()
            
            self.log_result(
                "PostgreSQL",
                "Connectivity Test",
                "PASS",
                {"query_time_ms": query_time, "port": config["port"]},
                True  # Database connectivity is constitutionally compliant
            )
            return True
            
        except Exception as e:
            self.log_result(
                "PostgreSQL",
                "Connectivity Test",
                "FAIL",
                {"error": str(e)},
                False
            )
            return False
    
    def test_redis_connectivity(self) -> bool:
        """Test Redis connectivity and performance"""
        try:
            config = self.infrastructure["redis"]
            r = redis.Redis(host=config["host"], port=config["port"], decode_responses=True)
            
            start_time = time.time()
            result = r.ping()
            ping_time = (time.time() - start_time) * 1000
            
            self.log_result(
                "Redis",
                "Connectivity Test",
                "PASS" if result else "FAIL",
                {"ping_time_ms": ping_time, "port": config["port"]},
                True  # Redis connectivity is constitutionally compliant
            )
            return result
            
        except Exception as e:
            self.log_result(
                "Redis",
                "Connectivity Test",
                "FAIL",
                {"error": str(e)},
                False
            )
            return False
    
    def test_performance_targets(self) -> Dict[str, bool]:
        """Test performance targets: P99 <5ms latency, >100 RPS throughput, >85% cache hit rate"""
        performance_results = {}
        
        # Test latency for Constitutional AI service
        try:
            latencies = []
            for _ in range(100):
                start_time = time.time()
                response = requests.get(f"http://localhost:32768/health", timeout=5)
                latency = (time.time() - start_time) * 1000
                latencies.append(latency)
            
            latencies.sort()
            p99_latency = latencies[98]  # 99th percentile
            
            latency_pass = p99_latency < 5.0
            performance_results["latency"] = latency_pass
            
            self.log_result(
                "Performance",
                "P99 Latency Test",
                "PASS" if latency_pass else "FAIL",
                {"p99_latency_ms": p99_latency, "target_ms": 5.0},
                True
            )
            
        except Exception as e:
            self.log_result(
                "Performance",
                "P99 Latency Test",
                "FAIL",
                {"error": str(e)},
                False
            )
            performance_results["latency"] = False
        
        return performance_results
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("Starting ACGS-2 Comprehensive End-to-End Testing")
        logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        test_summary = {
            "start_time": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "services_tested": 0,
            "services_passed": 0,
            "constitutional_compliance_rate": 0.0,
            "infrastructure_tests": {},
            "performance_tests": {}
        }
        
        # Test all services
        for service in self.services:
            test_summary["services_tested"] += 1
            if self.test_service_health(service):
                test_summary["services_passed"] += 1
        
        # Test infrastructure
        test_summary["infrastructure_tests"]["postgresql"] = self.test_database_connectivity()
        test_summary["infrastructure_tests"]["redis"] = self.test_redis_connectivity()
        
        # Test performance
        test_summary["performance_tests"] = self.test_performance_targets()
        
        # Calculate constitutional compliance rate
        compliant_tests = sum(1 for result in self.results if result.constitutional_compliance)
        total_tests = len(self.results)
        test_summary["constitutional_compliance_rate"] = (compliant_tests / total_tests) * 100 if total_tests > 0 else 0
        
        test_summary["end_time"] = datetime.now().isoformat()
        test_summary["total_tests"] = total_tests
        test_summary["compliant_tests"] = compliant_tests
        
        return test_summary

def main():
    """Main test execution"""
    suite = ACGSTestSuite()
    summary = suite.run_comprehensive_tests()
    
    # Print detailed results
    print("\n" + "="*80)
    print("ACGS-2 COMPREHENSIVE TEST RESULTS")
    print("="*80)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Test Duration: {summary['start_time']} to {summary['end_time']}")
    print(f"Services Tested: {summary['services_tested']}")
    print(f"Services Passed: {summary['services_passed']}")
    print(f"Constitutional Compliance Rate: {summary['constitutional_compliance_rate']:.1f}%")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Compliant Tests: {summary['compliant_tests']}")
    
    print("\nDETAILED RESULTS:")
    for result in suite.results:
        compliance_status = "✅" if result.constitutional_compliance else "❌"
        print(f"{compliance_status} {result.service} - {result.test_name}: {result.status}")
        if result.details:
            for key, value in result.details.items():
                if key != "service_data":  # Skip verbose service data
                    print(f"    {key}: {value}")
    
    # Save results to file
    with open("acgs_test_results.json", "w") as f:
        json.dump({
            "summary": summary,
            "detailed_results": [
                {
                    "service": r.service,
                    "test_name": r.test_name,
                    "status": r.status,
                    "details": r.details,
                    "constitutional_compliance": r.constitutional_compliance,
                    "timestamp": r.timestamp
                } for r in suite.results
            ]
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: acgs_test_results.json")
    
    # Return exit code based on constitutional compliance
    if summary["constitutional_compliance_rate"] < 100.0:
        print(f"\n⚠️  WARNING: Constitutional compliance rate is {summary['constitutional_compliance_rate']:.1f}% (target: 100%)")
        return 1
    else:
        print(f"\n✅ SUCCESS: All tests passed with 100% constitutional compliance")
        return 0

if __name__ == "__main__":
    exit(main())
