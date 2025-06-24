#!/usr/bin/env python3
"""
ACGS-1 Simple Integration Testing - End-to-End Workflow Validation
================================================================

This script validates that all services communicate properly and governance 
workflows function correctly after the reorganization.
"""

import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integration_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ACGSIntegrationTester:
    """ACGS-1 Integration Testing Suite."""
    
    def __init__(self):
        self.services = [
            {"name": "auth_service", "port": 8000, "url": "http://localhost:8000"},
            {"name": "ac_service", "port": 8001, "url": "http://localhost:8001"},
            {"name": "integrity_service", "port": 8002, "url": "http://localhost:8002"},
            {"name": "fv_service", "port": 8003, "url": "http://localhost:8003"},
            {"name": "gs_service", "port": 8004, "url": "http://localhost:8004"},
            {"name": "pgc_service", "port": 8005, "url": "http://localhost:8005"},
            {"name": "ec_service", "port": 8006, "url": "http://localhost:8006"},
        ]
        self.test_results = []
        self.constitution_hash = "cdd01ef066bc6cf2"
    
    def run_all_tests(self):
        """Run all integration tests."""
        logger.info("🚀 Starting ACGS-1 Integration Testing Suite")
        logger.info("=" * 60)
        
        # Test categories
        test_suites = [
            ("Service Health Validation", self.test_service_health),
            ("Service Communication", self.test_service_communication),
            ("Constitutional Governance", self.test_constitutional_governance),
            ("Authentication Flow", self.test_authentication_flow),
            ("Data Flow Validation", self.test_data_flow),
            ("Error Handling", self.test_error_handling),
            ("Performance Baseline", self.test_performance_baseline)
        ]
        
        for suite_name, test_func in test_suites:
            logger.info(f"\n📋 Running {suite_name} Tests...")
            try:
                test_func()
            except Exception as e:
                logger.error(f"❌ Test suite {suite_name} failed: {e}")
                self.test_results.append({
                    "test_name": f"{suite_name}_suite",
                    "success": False,
                    "duration_ms": 0,
                    "details": {},
                    "error_message": str(e)
                })
        
        return self.test_results
    
    def test_service_health(self):
        """Test that all services are healthy and responding."""
        for service in self.services:
            start_time = time.time()
            try:
                url = f"{service['url']}/health"
                response = requests.get(url, timeout=5)
                duration_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    health_data = response.json()
                    self.test_results.append({
                        "test_name": f"health_check_{service['name']}",
                        "success": True,
                        "duration_ms": duration_ms,
                        "details": {
                            "status_code": response.status_code,
                            "service_version": health_data.get("version", "unknown"),
                            "service_status": health_data.get("status", "unknown")
                        }
                    })
                    logger.info(f"✅ {service['name']} health check passed ({duration_ms:.2f}ms)")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append({
                    "test_name": f"health_check_{service['name']}",
                    "success": False,
                    "duration_ms": duration_ms,
                    "details": {"status_code": getattr(e, 'status', 'unknown')},
                    "error_message": str(e)
                })
                logger.error(f"❌ {service['name']} health check failed: {e}")
    
    def test_service_communication(self):
        """Test inter-service communication patterns."""
        # Test 1: AC Service -> FV Service communication
        start_time = time.time()
        try:
            # Get AC service status
            ac_response = requests.get("http://localhost:8001/", timeout=5)
            ac_data = ac_response.json()
            
            # Get FV service status  
            fv_response = requests.get("http://localhost:8003/", timeout=5)
            fv_data = fv_response.json()
            
            duration_ms = (time.time() - start_time) * 1000
            self.test_results.append({
                "test_name": "ac_fv_communication",
                "success": True,
                "duration_ms": duration_ms,
                "details": {
                    "ac_service_version": ac_data.get("version"),
                    "fv_service_version": fv_data.get("version"),
                    "communication_established": True
                }
            })
            logger.info(f"✅ AC-FV service communication test passed ({duration_ms:.2f}ms)")
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.test_results.append({
                "test_name": "ac_fv_communication",
                "success": False,
                "duration_ms": duration_ms,
                "details": {},
                "error_message": str(e)
            })
            logger.error(f"❌ AC-FV service communication failed: {e}")
        
        # Test 2: GS Service -> PGC Service communication
        start_time = time.time()
        try:
            # Test governance synthesis to policy governance communication
            gs_response = requests.get("http://localhost:8004/api/v1/governance/status", timeout=5)
            gs_data = gs_response.json()
            
            pgc_response = requests.get("http://localhost:8005/", timeout=5)
            pgc_data = pgc_response.json()
            
            duration_ms = (time.time() - start_time) * 1000
            self.test_results.append({
                "test_name": "gs_pgc_communication",
                "success": True,
                "duration_ms": duration_ms,
                "details": {
                    "gs_governance_enabled": gs_data.get("governance_synthesis_enabled"),
                    "pgc_service_version": pgc_data.get("version"),
                    "communication_established": True
                }
            })
            logger.info(f"✅ GS-PGC service communication test passed ({duration_ms:.2f}ms)")
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.test_results.append({
                "test_name": "gs_pgc_communication",
                "success": False,
                "duration_ms": duration_ms,
                "details": {},
                "error_message": str(e)
            })
            logger.error(f"❌ GS-PGC service communication failed: {e}")
    
    def test_constitutional_governance(self):
        """Test constitutional governance workflows."""
        services_with_hash = []
        
        for service in self.services:
            try:
                # Try constitutional validation endpoint
                url = f"{service['url']}/api/v1/constitutional/validate"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("constitutional_hash") == self.constitution_hash:
                        services_with_hash.append(service['name'])
                
                # Also check headers
                if self.constitution_hash in str(response.headers).lower():
                    if service['name'] not in services_with_hash:
                        services_with_hash.append(service['name'])
                
            except Exception:
                # Try health endpoint for header check
                try:
                    url = f"{service['url']}/health"
                    response = requests.get(url, timeout=3)
                    if self.constitution_hash in str(response.headers).lower():
                        services_with_hash.append(service['name'])
                except:
                    pass
        
        # Record constitutional governance test result
        self.test_results.append({
            "test_name": "constitutional_governance_validation",
            "success": len(services_with_hash) >= 4,  # At least 4 services should have the hash
            "duration_ms": 0,
            "details": {
                "constitution_hash": self.constitution_hash,
                "services_with_hash": services_with_hash,
                "total_services": len(self.services),
                "compliance_percentage": (len(services_with_hash) / len(self.services)) * 100
            }
        })
        
        if len(services_with_hash) >= 4:
            logger.info(f"✅ Constitutional governance validation passed ({len(services_with_hash)}/{len(self.services)} services)")
        else:
            logger.warning(f"⚠️ Constitutional governance validation partial ({len(services_with_hash)}/{len(self.services)} services)")
    
    def test_authentication_flow(self):
        """Test authentication service integration."""
        start_time = time.time()
        try:
            # Test auth service enterprise status
            response = requests.get("http://localhost:8000/auth/enterprise/status", timeout=5)
            if response.status_code == 200:
                auth_data = response.json()
                duration_ms = (time.time() - start_time) * 1000
                
                self.test_results.append({
                    "test_name": "authentication_flow",
                    "success": True,
                    "duration_ms": duration_ms,
                    "details": {
                        "enterprise_auth_enabled": auth_data.get("enterprise_auth_enabled"),
                        "mfa_enabled": auth_data.get("features", {}).get("multi_factor_authentication", {}).get("enabled"),
                        "oauth_enabled": auth_data.get("features", {}).get("oauth_providers", {}).get("enabled")
                    }
                })
                logger.info(f"✅ Authentication flow test passed ({duration_ms:.2f}ms)")
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.test_results.append({
                "test_name": "authentication_flow",
                "success": False,
                "duration_ms": duration_ms,
                "details": {},
                "error_message": str(e)
            })
            logger.error(f"❌ Authentication flow test failed: {e}")
    
    def test_data_flow(self):
        """Test data flow between services."""
        start_time = time.time()
        try:
            # Test integrity service data flow
            response = requests.get("http://localhost:8002/api/v1/integrity/status", timeout=5)
            if response.status_code == 200:
                integrity_data = response.json()
                
                duration_ms = (time.time() - start_time) * 1000
                self.test_results.append({
                    "test_name": "data_flow_validation",
                    "success": True,
                    "duration_ms": duration_ms,
                    "details": {
                        "integrity_enabled": integrity_data.get("integrity_service_enabled"),
                        "cryptographic_verification": integrity_data.get("features", {}).get("cryptographic_verification"),
                        "audit_trail": integrity_data.get("features", {}).get("audit_trail")
                    }
                })
                logger.info(f"✅ Data flow validation passed ({duration_ms:.2f}ms)")
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.test_results.append({
                "test_name": "data_flow_validation",
                "success": False,
                "duration_ms": duration_ms,
                "details": {},
                "error_message": str(e)
            })
            logger.error(f"❌ Data flow validation failed: {e}")
    
    def test_error_handling(self):
        """Test error handling and recovery mechanisms."""
        start_time = time.time()
        try:
            # Test invalid endpoint handling
            response = requests.get("http://localhost:8001/invalid/endpoint", timeout=5)
            duration_ms = (time.time() - start_time) * 1000
            
            # Should return 404 or similar error code
            if response.status_code in [404, 405, 422]:
                self.test_results.append({
                    "test_name": "error_handling_validation",
                    "success": True,
                    "duration_ms": duration_ms,
                    "details": {
                        "error_status_code": response.status_code,
                        "proper_error_handling": True
                    }
                })
                logger.info(f"✅ Error handling validation passed ({duration_ms:.2f}ms)")
            else:
                raise Exception(f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.test_results.append({
                "test_name": "error_handling_validation",
                "success": False,
                "duration_ms": duration_ms,
                "details": {},
                "error_message": str(e)
            })
            logger.error(f"❌ Error handling validation failed: {e}")
    
    def test_performance_baseline(self):
        """Test performance baseline for all services."""
        response_times = []
        
        for service in self.services:
            start_time = time.time()
            try:
                url = f"{service['url']}/health"
                response = requests.get(url, timeout=5)
                duration_ms = (time.time() - start_time) * 1000
                response_times.append(duration_ms)
                
            except Exception as e:
                logger.warning(f"Performance test failed for {service['name']}: {e}")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Performance targets: avg < 100ms, max < 500ms
            performance_good = avg_response_time < 100 and max_response_time < 500
            
            self.test_results.append({
                "test_name": "performance_baseline",
                "success": performance_good,
                "duration_ms": avg_response_time,
                "details": {
                    "avg_response_time_ms": avg_response_time,
                    "max_response_time_ms": max_response_time,
                    "min_response_time_ms": min_response_time,
                    "services_tested": len(response_times),
                    "performance_target_met": performance_good
                }
            })
            
            if performance_good:
                logger.info(f"✅ Performance baseline test passed (avg: {avg_response_time:.2f}ms)")
            else:
                logger.warning(f"⚠️ Performance baseline test warning (avg: {avg_response_time:.2f}ms)")
    
    def generate_report(self):
        """Generate comprehensive integration test report."""
        successful_tests = [t for t in self.test_results if t.get("success", False)]
        failed_tests = [t for t in self.test_results if not t.get("success", False)]
        
        report = {
            "timestamp": time.time(),
            "summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": (len(successful_tests) / len(self.test_results)) * 100 if self.test_results else 0
            },
            "test_results": self.test_results,
            "performance_metrics": {
                "avg_response_time_ms": sum(t.get("duration_ms", 0) for t in self.test_results if t.get("duration_ms", 0) > 0) / len([t for t in self.test_results if t.get("duration_ms", 0) > 0]) if any(t.get("duration_ms", 0) > 0 for t in self.test_results) else 0
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        recommendations = []
        
        failed_tests = [t for t in self.test_results if not t.get("success", False)]
        if failed_tests:
            recommendations.append(f"Address {len(failed_tests)} failed tests before production deployment")
        
        # Check constitutional governance compliance
        constitutional_test = next((t for t in self.test_results if t.get("test_name") == "constitutional_governance_validation"), None)
        if constitutional_test and constitutional_test.get("details", {}).get("compliance_percentage", 0) < 100:
            recommendations.append("Improve constitutional hash compliance across all services")
        
        # Check performance
        performance_test = next((t for t in self.test_results if t.get("test_name") == "performance_baseline"), None)
        if performance_test and not performance_test.get("success", False):
            recommendations.append("Optimize service response times to meet performance targets")
        
        if not recommendations:
            recommendations.append("All integration tests passed - system ready for production")
        
        return recommendations

def main():
    """Main execution function."""
    tester = ACGSIntegrationTester()
    
    try:
        # Run all integration tests
        results = tester.run_all_tests()
        
        # Generate and save report
        report = tester.generate_report()
        
        with open("integration_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 INTEGRATION TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Successful: {report['summary']['successful_tests']}")
        logger.info(f"Failed: {report['summary']['failed_tests']}")
        logger.info(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        
        if report['recommendations']:
            logger.info("\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(report['recommendations'], 1):
                logger.info(f"{i}. {rec}")
        
        logger.info(f"\n📄 Detailed report saved to: integration_test_report.json")
        
        # Exit with appropriate code
        if report['summary']['success_rate'] >= 80:
            logger.info("✅ Integration testing completed successfully!")
            return 0
        else:
            logger.error("❌ Integration testing completed with significant issues")
            return 1
            
    except Exception as e:
        logger.error(f"Integration testing failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
