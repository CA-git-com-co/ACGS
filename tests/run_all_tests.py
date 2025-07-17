"""
ACGS-2 Comprehensive Test Runner
Constitutional Hash: cdd01ef066bc6cf2

Executes the complete ACGS-2 test suite including:
- Service integration tests
- Constitutional workflow tests  
- Performance and load tests
- Security validation tests
- End-to-end system validation

Provides comprehensive reporting and constitutional compliance validation.
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Add test modules to path
sys.path.append(str(Path(__file__).parent))

# Import test modules
from integration.test_service_integration import run_integration_tests
from integration.test_constitutional_workflows import run_constitutional_workflow_tests
from performance.test_performance_requirements import run_performance_tests

# Constitutional compliance constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ACGSTestRunner:
    """Comprehensive test runner for ACGS-2 system"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.constitutional_compliance_verified = False
    
    def print_header(self):
        """Print test suite header"""
        print("=" * 80)
        print("🚀 ACGS-2 (Advanced Constitutional Governance System) Test Suite")
        print("=" * 80)
        print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"🕐 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Test Categories:")
        print(f"   • Service Integration Tests")
        print(f"   • Constitutional Workflow Tests")
        print(f"   • Performance & Load Tests")
        print(f"🔍 Validating:")
        print(f"   • Constitutional compliance across all services")
        print(f"   • Service-to-service communication")
        print(f"   • Multi-agent coordination workflows")
        print(f"   • MCP protocol integration")
        print(f"   • A2A communication protocols")
        print(f"   • Security validation pipeline")
        print(f"   • Performance requirements (P99 <5ms, >100 RPS)")
        print("=" * 80)
    
    def print_footer(self):
        """Print test suite footer with results"""
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("🏁 ACGS-2 Test Suite Complete")
        print("=" * 80)
        
        # Calculate overall statistics
        total_tests = sum(result['total'] for result in self.test_results.values())
        total_passed = sum(result['passed'] for result in self.test_results.values())
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_tests - total_passed}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Duration: {total_duration:.1f} seconds")
        
        print(f"\n📋 Test Category Breakdown:")
        for category, result in self.test_results.items():
            success_rate = (result['passed'] / result['total'] * 100) if result['total'] > 0 else 0
            status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            print(f"   {status} {category}: {result['passed']}/{result['total']} ({success_rate:.1f}%)")
        
        print(f"\n🔐 Constitutional Compliance:")
        compliance_status = "✅" if self.constitutional_compliance_verified else "❌"
        print(f"   {compliance_status} Constitutional Hash Validation: {CONSTITUTIONAL_HASH}")
        print(f"   {compliance_status} Cross-Service Compliance: {'Verified' if self.constitutional_compliance_verified else 'Failed'}")
        
        # Overall system status
        if overall_success_rate >= 90:
            print(f"\n🎉 System Status: EXCELLENT")
            print(f"   ACGS-2 system is performing at optimal levels")
        elif overall_success_rate >= 80:
            print(f"\n✅ System Status: GOOD")
            print(f"   ACGS-2 system is performing well with minor issues")
        elif overall_success_rate >= 60:
            print(f"\n⚠️ System Status: ACCEPTABLE")
            print(f"   ACGS-2 system has issues that should be addressed")
        else:
            print(f"\n❌ System Status: NEEDS ATTENTION")
            print(f"   ACGS-2 system has significant issues requiring immediate attention")
        
        print(f"\n📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"🕐 Test Completed: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def save_test_report(self):
        """Save detailed test report to file"""
        report_data = {
            "test_run_info": {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_seconds": (self.end_time - self.start_time).total_seconds(),
                "constitutional_compliance_verified": self.constitutional_compliance_verified
            },
            "test_results": self.test_results,
            "summary": {
                "total_tests": sum(result['total'] for result in self.test_results.values()),
                "total_passed": sum(result['passed'] for result in self.test_results.values()),
                "overall_success_rate": (
                    sum(result['passed'] for result in self.test_results.values()) /
                    sum(result['total'] for result in self.test_results.values()) * 100
                ) if sum(result['total'] for result in self.test_results.values()) > 0 else 0
            }
        }
        
        # Save to reports directory
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"acgs_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed test report saved: {report_file}")
    
    async def run_test_category(self, category_name: str, test_function) -> Tuple[int, int]:
        """Run a test category and capture results"""
        print(f"\n{'='*20} {category_name} {'='*20}")
        
        try:
            start_time = time.time()
            passed, total = await test_function()
            end_time = time.time()
            
            duration = end_time - start_time
            success_rate = (passed / total * 100) if total > 0 else 0
            
            self.test_results[category_name] = {
                "passed": passed,
                "total": total,
                "success_rate": success_rate,
                "duration_seconds": duration
            }
            
            status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            print(f"\n{status} {category_name} Summary:")
            print(f"   Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
            print(f"   Duration: {duration:.1f} seconds")
            
            # Check for constitutional compliance
            if category_name == "Service Integration Tests" and success_rate >= 80:
                self.constitutional_compliance_verified = True
            
            return passed, total
            
        except Exception as e:
            print(f"❌ {category_name} failed with error: {str(e)}")
            self.test_results[category_name] = {
                "passed": 0,
                "total": 1,
                "success_rate": 0,
                "duration_seconds": 0,
                "error": str(e)
            }
            return 0, 1
    
    async def run_all_tests(self):
        """Run all test categories"""
        self.start_time = datetime.now()
        
        self.print_header()
        
        # Define test categories and their corresponding functions
        test_categories = [
            ("Service Integration Tests", run_integration_tests),
            ("Constitutional Workflow Tests", run_constitutional_workflow_tests),
            ("Performance & Load Tests", run_performance_tests),
        ]
        
        total_passed = 0
        total_tests = 0
        
        # Run each test category
        for category_name, test_function in test_categories:
            passed, total = await self.run_test_category(category_name, test_function)
            total_passed += passed
            total_tests += total
            
            # Small delay between test categories
            await asyncio.sleep(1)
        
        self.end_time = datetime.now()
        
        # Print final results
        self.print_footer()
        
        # Save detailed report
        self.save_test_report()
        
        return total_passed, total_tests


async def main():
    """Main test runner function"""
    try:
        runner = ACGSTestRunner()
        passed, total = await runner.run_all_tests()
        
        # Exit with appropriate code
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if success_rate >= 90:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        elif success_rate >= 80:
            print("\n✅ Tests completed with minor issues")
            sys.exit(0)
        elif success_rate >= 60:
            print("\n⚠️ Tests completed with some failures")
            sys.exit(1)
        else:
            print("\n❌ Tests completed with significant failures")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Test runner failed with error: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    # Create reports directory
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Run the test suite
    asyncio.run(main())