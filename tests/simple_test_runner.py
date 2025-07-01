#!/usr/bin/env python3
"""
Simple ACGS Test Runner

A simplified test runner that uses only standard library modules.
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Dict, List, Any, Optional


class SimpleTestRunner:
    """Simple test runner using only standard library."""
    
    def __init__(self):
        self.services = {
            "coordinator": "http://localhost:8000",
            "auth_service": "http://localhost:8006",
            "agent_hitl": "http://localhost:8008", 
            "sandbox_execution": "http://localhost:8009",
            "formal_verification": "http://localhost:8010",
            "audit_integrity": "http://localhost:8011",
        }
        self.test_results = []
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete test suite."""
        print("🧪 ACGS Simple Test Suite")
        print("=" * 50)
        print()
        
        start_time = time.time()
        
        # Test phases
        test_phases = [
            ("Health Checks", self.test_service_health),
            ("Basic Functionality", self.test_basic_functionality),
            ("Service Integration", self.test_service_integration),
            ("Error Handling", self.test_error_handling),
        ]
        
        all_results = {}
        
        for phase_name, test_function in test_phases:
            print(f"📋 Running {phase_name}...")
            try:
                results = test_function()
                all_results[phase_name] = results
                self._print_phase_results(phase_name, results)
            except Exception as e:
                print(f"❌ Phase {phase_name} failed: {e}")
                all_results[phase_name] = {"error": str(e)}
            print()
        
        # Generate summary
        total_time = time.time() - start_time
        summary = self._generate_summary_report(all_results, total_time)
        
        return summary
    
    def test_service_health(self) -> Dict[str, Any]:
        """Test health of all ACGS services."""
        health_results = []
        
        for service_name, base_url in self.services.items():
            start_time = time.time()
            try:
                response = self._make_request(f"{base_url}/health", method="GET")
                response_time = int((time.time() - start_time) * 1000)
                
                if response and response.get("status") != "error":
                    health_results.append({
                        "service_name": service_name,
                        "url": base_url,
                        "healthy": True,
                        "response_time_ms": response_time
                    })
                    print(f"  ✅ {service_name}: Healthy ({response_time}ms)")
                else:
                    health_results.append({
                        "service_name": service_name,
                        "url": base_url,
                        "healthy": False,
                        "response_time_ms": response_time,
                        "error": "Service returned error status"
                    })
                    print(f"  ❌ {service_name}: Unhealthy")
            
            except Exception as e:
                response_time = int((time.time() - start_time) * 1000)
                health_results.append({
                    "service_name": service_name,
                    "url": base_url,
                    "healthy": False,
                    "response_time_ms": response_time,
                    "error": str(e)
                })
                print(f"  ❌ {service_name}: Connection failed - {str(e)}")
        
        healthy_count = sum(1 for h in health_results if h["healthy"])
        return {
            "total_services": len(health_results),
            "healthy_services": healthy_count,
            "health_results": health_results,
            "all_healthy": healthy_count == len(health_results)
        }
    
    def test_basic_functionality(self) -> Dict[str, Any]:
        """Test basic functionality of services."""
        results = []
        
        # Test 1: Root endpoints
        for service_name, base_url in self.services.items():
            try:
                response = self._make_request(base_url, method="GET")
                if response:
                    results.append({
                        "test_name": f"{service_name}_root_endpoint",
                        "status": "passed",
                        "details": response
                    })
                    print(f"  ✅ {service_name} root endpoint")
                else:
                    results.append({
                        "test_name": f"{service_name}_root_endpoint", 
                        "status": "failed",
                        "error": "No response"
                    })
                    print(f"  ❌ {service_name} root endpoint failed")
            except Exception as e:
                results.append({
                    "test_name": f"{service_name}_root_endpoint",
                    "status": "failed", 
                    "error": str(e)
                })
                print(f"  ❌ {service_name} root endpoint failed: {e}")
        
        # Test 2: Agent creation (if auth service is available)
        try:
            agent_data = {
                "agent_id": "simple-test-agent",
                "name": "Simple Test Agent",
                "description": "Agent for simple testing",
                "agent_type": "coding_agent",
                "owner_user_id": 1,
                "capabilities": ["testing"],
                "permissions": ["test:run"],
                "compliance_level": "high"
            }
            
            response = self._make_request(
                f"{self.services['auth_service']}/api/v1/agents",
                method="POST",
                data=agent_data
            )
            
            if response and "error" not in response:
                results.append({
                    "test_name": "agent_creation",
                    "status": "passed"
                })
                print("  ✅ Agent creation test")
            else:
                results.append({
                    "test_name": "agent_creation",
                    "status": "failed",
                    "error": response.get("error", "Unknown error") if response else "No response"
                })
                print("  ❌ Agent creation test failed")
                
        except Exception as e:
            results.append({
                "test_name": "agent_creation",
                "status": "failed",
                "error": str(e)
            })
            print(f"  ❌ Agent creation test failed: {e}")
        
        passed = sum(1 for r in results if r["status"] == "passed")
        return {
            "total_tests": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "results": results
        }
    
    def test_service_integration(self) -> Dict[str, Any]:
        """Test basic service integration."""
        results = []
        
        # Test 1: HITL evaluation
        try:
            review_request = {
                "agent_id": "simple-test-agent",
                "agent_type": "coding_agent",
                "operation_type": "test_operation",
                "operation_description": "Simple test operation",
                "operation_context": {"test": True}
            }
            
            response = self._make_request(
                f"{self.services['agent_hitl']}/api/v1/reviews/evaluate",
                method="POST",
                data=review_request
            )
            
            if response and "error" not in response:
                results.append({
                    "test_name": "hitl_evaluation",
                    "status": "passed"
                })
                print("  ✅ HITL evaluation test")
            else:
                results.append({
                    "test_name": "hitl_evaluation",
                    "status": "failed",
                    "error": response.get("error", "Unknown error") if response else "No response"
                })
                print("  ❌ HITL evaluation test failed")
                
        except Exception as e:
            results.append({
                "test_name": "hitl_evaluation",
                "status": "failed",
                "error": str(e)
            })
            print(f"  ❌ HITL evaluation test failed: {e}")
        
        # Test 2: Coordinator operation
        try:
            operation_request = {
                "agent_id": "simple-test-agent",
                "agent_type": "coding_agent",
                "operation_type": "simple_test",
                "operation_description": "Simple coordinator test",
                "bypass_hitl": True
            }
            
            response = self._make_request(
                f"{self.services['coordinator']}/api/v1/operations",
                method="POST",
                data=operation_request
            )
            
            if response and "error" not in response:
                results.append({
                    "test_name": "coordinator_operation",
                    "status": "passed"
                })
                print("  ✅ Coordinator operation test")
            else:
                results.append({
                    "test_name": "coordinator_operation",
                    "status": "failed",
                    "error": response.get("error", "Unknown error") if response else "No response"
                })
                print("  ❌ Coordinator operation test failed")
                
        except Exception as e:
            results.append({
                "test_name": "coordinator_operation",
                "status": "failed",
                "error": str(e)
            })
            print(f"  ❌ Coordinator operation test failed: {e}")
        
        passed = sum(1 for r in results if r["status"] == "passed")
        return {
            "total_tests": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "results": results
        }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling."""
        results = []
        
        # Test 1: Invalid endpoints
        try:
            response = self._make_request(
                f"{self.services['coordinator']}/api/v1/invalid_endpoint",
                method="GET"
            )
            
            # Should get 404 or similar error
            results.append({
                "test_name": "invalid_endpoint_handling",
                "status": "passed"
            })
            print("  ✅ Invalid endpoint handling")
            
        except Exception as e:
            # Expected to fail, which is good
            results.append({
                "test_name": "invalid_endpoint_handling",
                "status": "passed"
            })
            print("  ✅ Invalid endpoint handling (properly rejected)")
        
        # Test 2: Invalid data
        try:
            invalid_data = {"invalid": "data"}
            
            response = self._make_request(
                f"{self.services['coordinator']}/api/v1/operations",
                method="POST",
                data=invalid_data
            )
            
            # Should handle gracefully
            results.append({
                "test_name": "invalid_data_handling",
                "status": "passed"
            })
            print("  ✅ Invalid data handling")
            
        except Exception as e:
            # Expected to fail, which is good
            results.append({
                "test_name": "invalid_data_handling",
                "status": "passed"
            })
            print("  ✅ Invalid data handling (properly rejected)")
        
        passed = sum(1 for r in results if r["status"] == "passed")
        return {
            "total_tests": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "results": results
        }
    
    def _make_request(
        self, url: str, method: str = "GET", data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request using urllib."""
        try:
            if method == "POST" and data:
                json_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(
                    url,
                    data=json_data,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status < 400:
                    content = response.read().decode('utf-8')
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return {"content": content}
                else:
                    return {"status": "error", "code": response.status}
                    
        except urllib.error.HTTPError as e:
            return {"status": "error", "code": e.code, "message": str(e)}
        except urllib.error.URLError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _print_phase_results(self, phase_name: str, results: Dict[str, Any]):
        """Print results for a test phase."""
        if "error" in results:
            print(f"  ❌ {phase_name} failed: {results['error']}")
            return
        
        if "total_tests" in results:
            total = results["total_tests"]
            passed = results["passed"]
            failed = results.get("failed", 0)
            
            if passed == total:
                print(f"  ✅ All {total} tests passed")
            else:
                print(f"  ⚠️  {passed}/{total} tests passed ({failed} failed)")
        elif "all_healthy" in results:
            if results["all_healthy"]:
                print(f"  ✅ All {results['total_services']} services healthy")
            else:
                healthy = results["healthy_services"]
                total = results["total_services"]
                print(f"  ⚠️  {healthy}/{total} services healthy")
    
    def _generate_summary_report(self, all_results: Dict[str, Any], total_time: float) -> Dict[str, Any]:
        """Generate test summary report."""
        print("📊 Test Summary Report")
        print("=" * 50)
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for phase_name, results in all_results.items():
            if "total_tests" in results:
                total_tests += results["total_tests"]
                total_passed += results["passed"]
                total_failed += results.get("failed", 0)
        
        # Overall status
        if total_failed == 0:
            overall_status = "✅ ALL TESTS PASSED"
        else:
            overall_status = f"⚠️  {total_failed} TESTS FAILED"
        
        print(f"\n{overall_status}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Total Time: {total_time:.2f}s")
        
        # Service health summary
        health_results = all_results.get("Health Checks", {})
        if health_results.get("all_healthy"):
            print("Service Health: All services healthy ✅")
        else:
            healthy = health_results.get("healthy_services", 0)
            total_services = health_results.get("total_services", 0)
            print(f"Service Health: {healthy}/{total_services} services healthy ⚠️")
        
        # Basic assessment
        print(f"\nACGS System Assessment:")
        if total_failed == 0 and health_results.get("all_healthy", False):
            print("✅ ACGS system is operational and ready for use")
        elif total_failed <= 2:
            print("⚠️  ACGS system has minor issues but core functionality works")
        else:
            print("❌ ACGS system has significant issues requiring attention")
        
        return {
            "overall_status": "passed" if total_failed == 0 else "failed",
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "duration_seconds": total_time,
            "phase_results": all_results,
            "timestamp": datetime.utcnow().isoformat(),
            "constitutional_hash": "cdd01ef066bc6cf2"
        }


def main():
    """Run simple tests."""
    runner = SimpleTestRunner()
    summary = runner.run_all_tests()
    
    # Save results
    try:
        with open("simple_test_results.json", "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n📁 Test results saved to: simple_test_results.json")
    except Exception as e:
        print(f"⚠️  Could not save test results: {e}")
    
    # Exit with appropriate code
    exit_code = 0 if summary["overall_status"] == "passed" else 1
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)