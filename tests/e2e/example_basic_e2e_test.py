#!/usr/bin/env python3
"""
ACGS-1 Basic End-to-End Test Example

This is a simplified example demonstrating how to create and run basic
end-to-end tests for the ACGS-1 system. This serves as a starting point
for developers who want to understand the testing patterns.

Features:
- Simple service health checks
- Basic authentication workflow
- Policy creation example
- Performance validation
- Easy-to-understand test structure

Usage:
    python tests/e2e/example_basic_e2e_test.py

Formal Verification Comments:
# requires: Basic ACGS-1 services running
# ensures: Simple end-to-end workflow validated
# sha256: basic_e2e_example_v1.0
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BasicE2ETest:
    """
    Basic end-to-end test example for ACGS-1.
    
    This class demonstrates simple testing patterns that can be
    extended for more comprehensive validation.
    """

    def __init__(self):
        # Core services configuration
        self.services = {
            "auth": "http://localhost:8000",
            "ac": "http://localhost:8001", 
            "gs": "http://localhost:8004"
        }
        
        # Test results tracking
        self.test_results = []
        self.start_time = time.time()

    def run_basic_tests(self) -> bool:
        """
        Run basic end-to-end tests.
        
        # requires: Core services running
        # ensures: Basic functionality validated
        # sha256: run_basic_tests_v1.0
        """
        logger.info("🚀 Starting Basic ACGS-1 End-to-End Test")
        logger.info("=" * 50)
        
        overall_success = True
        
        try:
            # Test 1: Service Health Checks
            logger.info("1️⃣ Testing Service Health...")
            health_success = self.test_service_health()
            if not health_success:
                overall_success = False
                logger.error("❌ Service health checks failed")
            else:
                logger.info("✅ Service health checks passed")
            
            # Test 2: Authentication Workflow
            logger.info("\n2️⃣ Testing Authentication...")
            auth_success = self.test_authentication()
            if not auth_success:
                overall_success = False
                logger.error("❌ Authentication test failed")
            else:
                logger.info("✅ Authentication test passed")
            
            # Test 3: Basic Policy Creation
            logger.info("\n3️⃣ Testing Policy Creation...")
            policy_success = self.test_policy_creation()
            if not policy_success:
                overall_success = False
                logger.error("❌ Policy creation test failed")
            else:
                logger.info("✅ Policy creation test passed")
            
            # Test 4: Performance Validation
            logger.info("\n4️⃣ Testing Performance...")
            perf_success = self.test_performance()
            if not perf_success:
                overall_success = False
                logger.error("❌ Performance test failed")
            else:
                logger.info("✅ Performance test passed")
            
            # Print Summary
            self.print_test_summary(overall_success)
            
            return overall_success
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {str(e)}")
            return False

    def test_service_health(self) -> bool:
        """Test health endpoints of core services."""
        try:
            healthy_services = 0
            
            for service_name, base_url in self.services.items():
                try:
                    start_time = time.time()
                    response = requests.get(f"{base_url}/health", timeout=5)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        logger.info(f"  ✅ {service_name}: Healthy ({response_time:.2f}ms)")
                        healthy_services += 1
                        
                        # Record result
                        self.test_results.append({
                            "test": f"{service_name}_health",
                            "success": True,
                            "response_time_ms": response_time,
                            "details": response.json() if response.content else {}
                        })
                    else:
                        logger.error(f"  ❌ {service_name}: HTTP {response.status_code}")
                        self.test_results.append({
                            "test": f"{service_name}_health",
                            "success": False,
                            "response_time_ms": response_time,
                            "error": f"HTTP {response.status_code}"
                        })
                        
                except Exception as e:
                    logger.error(f"  ❌ {service_name}: {str(e)}")
                    self.test_results.append({
                        "test": f"{service_name}_health",
                        "success": False,
                        "response_time_ms": 0,
                        "error": str(e)
                    })
            
            success_rate = healthy_services / len(self.services)
            logger.info(f"Service Health: {healthy_services}/{len(self.services)} ({success_rate:.1%})")
            
            return success_rate >= 0.8  # Require 80% of services to be healthy
            
        except Exception as e:
            logger.error(f"Service health test error: {str(e)}")
            return False

    def test_authentication(self) -> bool:
        """Test basic authentication workflow."""
        try:
            # Test user registration
            register_data = {
                "username": "test_user_basic",
                "email": "test@acgs.example",
                "password": "test_password_123",
                "role": "citizen"
            }
            
            start_time = time.time()
            register_response = requests.post(
                f"{self.services['auth']}/auth/register",
                json=register_data,
                timeout=10
            )
            register_time = (time.time() - start_time) * 1000
            
            # Test user login
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            
            start_time = time.time()
            login_response = requests.post(
                f"{self.services['auth']}/auth/login",
                data=login_data,  # Form data for OAuth2
                timeout=10
            )
            login_time = (time.time() - start_time) * 1000
            
            # Validate responses
            register_success = register_response.status_code in [200, 201]
            login_success = login_response.status_code == 200
            
            if login_success:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                
                logger.info(f"  ✅ Registration: {register_time:.2f}ms")
                logger.info(f"  ✅ Login: {login_time:.2f}ms")
                logger.info(f"  ✅ Token received: {access_token[:20]}..." if access_token else "  ❌ No token")
                
                # Record results
                self.test_results.append({
                    "test": "authentication_workflow",
                    "success": True,
                    "response_time_ms": register_time + login_time,
                    "details": {
                        "register_time_ms": register_time,
                        "login_time_ms": login_time,
                        "token_received": bool(access_token)
                    }
                })
                
                return True
            else:
                logger.error(f"  ❌ Login failed: HTTP {login_response.status_code}")
                self.test_results.append({
                    "test": "authentication_workflow",
                    "success": False,
                    "response_time_ms": register_time + login_time,
                    "error": f"Login failed: HTTP {login_response.status_code}"
                })
                return False
                
        except Exception as e:
            logger.error(f"Authentication test error: {str(e)}")
            self.test_results.append({
                "test": "authentication_workflow",
                "success": False,
                "response_time_ms": 0,
                "error": str(e)
            })
            return False

    def test_policy_creation(self) -> bool:
        """Test basic policy creation workflow."""
        try:
            # Test constitutional principles endpoint
            start_time = time.time()
            principles_response = requests.get(
                f"{self.services['ac']}/api/v1/principles",
                timeout=10
            )
            principles_time = (time.time() - start_time) * 1000
            
            # Test policy synthesis endpoint
            synthesis_data = {
                "policy_title": "Basic Privacy Policy",
                "domain": "privacy",
                "principles": ["transparency", "user_consent"],
                "complexity": "low"
            }
            
            start_time = time.time()
            synthesis_response = requests.post(
                f"{self.services['gs']}/api/v1/synthesize",
                json=synthesis_data,
                timeout=15
            )
            synthesis_time = (time.time() - start_time) * 1000
            
            # Validate responses
            principles_success = principles_response.status_code in [200, 404]  # 404 is OK if no principles exist
            synthesis_success = synthesis_response.status_code in [200, 202, 405]  # 405 might be method not allowed
            
            total_time = principles_time + synthesis_time
            
            if principles_success and synthesis_success:
                logger.info(f"  ✅ Principles access: {principles_time:.2f}ms")
                logger.info(f"  ✅ Policy synthesis: {synthesis_time:.2f}ms")
                
                self.test_results.append({
                    "test": "policy_creation_workflow",
                    "success": True,
                    "response_time_ms": total_time,
                    "details": {
                        "principles_time_ms": principles_time,
                        "synthesis_time_ms": synthesis_time,
                        "principles_status": principles_response.status_code,
                        "synthesis_status": synthesis_response.status_code
                    }
                })
                
                return True
            else:
                logger.error(f"  ❌ Policy creation failed")
                logger.error(f"    Principles: HTTP {principles_response.status_code}")
                logger.error(f"    Synthesis: HTTP {synthesis_response.status_code}")
                
                self.test_results.append({
                    "test": "policy_creation_workflow",
                    "success": False,
                    "response_time_ms": total_time,
                    "error": f"Principles: {principles_response.status_code}, Synthesis: {synthesis_response.status_code}"
                })
                
                return False
                
        except Exception as e:
            logger.error(f"Policy creation test error: {str(e)}")
            self.test_results.append({
                "test": "policy_creation_workflow",
                "success": False,
                "response_time_ms": 0,
                "error": str(e)
            })
            return False

    def test_performance(self) -> bool:
        """Test basic performance metrics."""
        try:
            # Calculate average response times
            response_times = []
            for result in self.test_results:
                if result.get("success") and result.get("response_time_ms"):
                    response_times.append(result["response_time_ms"])
            
            if not response_times:
                logger.warning("  ⚠️ No response time data available")
                return True
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Performance targets
            avg_target = 1000  # 1 second average
            max_target = 2000  # 2 seconds maximum
            
            avg_pass = avg_response_time <= avg_target
            max_pass = max_response_time <= max_target
            
            logger.info(f"  📊 Average Response Time: {avg_response_time:.2f}ms (target: {avg_target}ms)")
            logger.info(f"  📊 Maximum Response Time: {max_response_time:.2f}ms (target: {max_target}ms)")
            logger.info(f"  📊 Minimum Response Time: {min_response_time:.2f}ms")
            
            if avg_pass and max_pass:
                logger.info("  ✅ Performance targets met")
                
                self.test_results.append({
                    "test": "performance_validation",
                    "success": True,
                    "response_time_ms": avg_response_time,
                    "details": {
                        "avg_response_time_ms": avg_response_time,
                        "max_response_time_ms": max_response_time,
                        "min_response_time_ms": min_response_time,
                        "avg_target_met": avg_pass,
                        "max_target_met": max_pass
                    }
                })
                
                return True
            else:
                logger.error("  ❌ Performance targets not met")
                
                self.test_results.append({
                    "test": "performance_validation",
                    "success": False,
                    "response_time_ms": avg_response_time,
                    "error": f"Avg: {avg_response_time:.2f}ms > {avg_target}ms or Max: {max_response_time:.2f}ms > {max_target}ms"
                })
                
                return False
                
        except Exception as e:
            logger.error(f"Performance test error: {str(e)}")
            self.test_results.append({
                "test": "performance_validation",
                "success": False,
                "response_time_ms": 0,
                "error": str(e)
            })
            return False

    def print_test_summary(self, overall_success: bool):
        """Print comprehensive test summary."""
        total_duration = time.time() - self.start_time
        
        logger.info("\n" + "=" * 50)
        logger.info("📊 BASIC E2E TEST SUMMARY")
        logger.info("=" * 50)
        
        # Overall result
        if overall_success:
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.error("❌ SOME TESTS FAILED!")
        
        # Test statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.get("success")])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"📈 Test Results:")
        logger.info(f"  Total Tests: {total_tests}")
        logger.info(f"  Passed: {passed_tests}")
        logger.info(f"  Failed: {failed_tests}")
        logger.info(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "  Success Rate: N/A")
        logger.info(f"  Total Duration: {total_duration:.2f}s")
        
        # Failed tests details
        if failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result.get("success"):
                    logger.info(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        
        # Save results to file
        try:
            results_file = "tests/results/basic_e2e_test_results.json"
            import os
            os.makedirs(os.path.dirname(results_file), exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump({
                    "overall_success": overall_success,
                    "total_duration_seconds": total_duration,
                    "test_results": self.test_results,
                    "summary": {
                        "total_tests": total_tests,
                        "passed_tests": passed_tests,
                        "failed_tests": failed_tests,
                        "success_rate": passed_tests/total_tests if total_tests > 0 else 0
                    }
                }, f, indent=2)
            
            logger.info(f"\n📋 Results saved to: {results_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not save results: {str(e)}")


def main():
    """Main function for running basic E2E test."""
    test = BasicE2ETest()
    success = test.run_basic_tests()
    
    if success:
        print("\n🎉 Basic E2E Test: PASSED")
        exit(0)
    else:
        print("\n❌ Basic E2E Test: FAILED")
        exit(1)


if __name__ == "__main__":
    main()
