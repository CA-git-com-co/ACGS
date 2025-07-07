#!/usr/bin/env python3
"""
ACGS Comprehensive Test Runner
Constitutional Hash: cdd01ef066bc6cf2

This script runs all ACGS test categories and generates a comprehensive
test report for production readiness validation.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveTestRunner:
    """Comprehensive test runner for all ACGS test categories."""
    
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
    
    def __init__(self, args):
        self.args = args
        self.test_results = {}
        self.start_time = datetime.utcnow()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories and generate comprehensive report."""
        logger.info("🚀 Starting ACGS Comprehensive Test Suite")
        logger.info(f"Constitutional Hash: {self.CONSTITUTIONAL_HASH}")
        
        try:
            # 1. Constitutional Compliance Tests
            if not self.args.skip_constitutional:
                logger.info("⚖️ Running Constitutional Compliance Tests...")
                constitutional_results = await self._run_constitutional_tests()
                self.test_results["constitutional_compliance"] = constitutional_results
            
            # 2. Unit Tests
            if not self.args.skip_unit:
                logger.info("🧪 Running Unit Tests...")
                unit_results = await self._run_unit_tests()
                self.test_results["unit_tests"] = unit_results
            
            # 3. Integration Tests
            if not self.args.skip_integration:
                logger.info("🔗 Running Integration Tests...")
                integration_results = await self._run_integration_tests()
                self.test_results["integration_tests"] = integration_results
            
            # 4. Performance Tests
            if not self.args.skip_performance:
                logger.info("⚡ Running Performance Tests...")
                performance_results = await self._run_performance_tests()
                self.test_results["performance_tests"] = performance_results
            
            # 5. Multi-Tenant Tests
            if not self.args.skip_multi_tenant:
                logger.info("🏢 Running Multi-Tenant Tests...")
                multi_tenant_results = await self._run_multi_tenant_tests()
                self.test_results["multi_tenant_tests"] = multi_tenant_results
            
            # 6. Security Tests
            if not self.args.skip_security:
                logger.info("🔒 Running Security Tests...")
                security_results = await self._run_security_tests()
                self.test_results["security_tests"] = security_results
            
            # 7. Generate Summary
            summary = self._generate_test_summary()
            self.test_results["summary"] = summary
            
            logger.info("✅ Comprehensive test suite completed")
            return self.test_results
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            self.test_results["error"] = str(e)
            return self.test_results
    
    async def _run_constitutional_tests(self) -> Dict[str, Any]:
        """Run constitutional compliance tests."""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                "-v", "-m", "constitutional",
                "--tb=short",
                "--json-report", "--json-report-file=constitutional-report.json"
            ], capture_output=True, text=True, timeout=600)
            
            # Parse JSON report if available
            report_data = {}
            try:
                with open("constitutional-report.json", "r") as f:
                    report_data = json.load(f)
            except FileNotFoundError:
                pass
            
            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr if result.returncode != 0 else None,
                "report_data": report_data,
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
            
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Constitutional tests timed out",
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
    
    async def _run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests with coverage."""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                "-v", "-m", "unit",
                "--cov=services",
                "--cov-report=json:unit-coverage.json",
                "--cov-report=term-missing",
                "--tb=short",
                "--json-report", "--json-report-file=unit-report.json"
            ], capture_output=True, text=True, timeout=1800)
            
            # Parse coverage data
            coverage_data = {}
            try:
                with open("unit-coverage.json", "r") as f:
                    coverage_data = json.load(f)
            except FileNotFoundError:
                pass
            
            # Parse test report
            report_data = {}
            try:
                with open("unit-report.json", "r") as f:
                    report_data = json.load(f)
            except FileNotFoundError:
                pass
            
            coverage_percentage = coverage_data.get("totals", {}).get("percent_covered", 0)
            
            return {
                "passed": result.returncode == 0,
                "coverage_percentage": coverage_percentage,
                "meets_coverage_target": coverage_percentage >= 80.0,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr if result.returncode != 0 else None,
                "coverage_data": coverage_data,
                "report_data": report_data,
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
            
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Unit tests timed out",
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                "-v", "-m", "integration",
                "--tb=short",
                "--json-report", "--json-report-file=integration-report.json"
            ], capture_output=True, text=True, timeout=1800)
            
            # Parse test report
            report_data = {}
            try:
                with open("integration-report.json", "r") as f:
                    report_data = json.load(f)
            except FileNotFoundError:
                pass
            
            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr if result.returncode != 0 else None,
                "report_data": report_data,
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
            
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Integration tests timed out",
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
    
    async def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                "-v", "-m", "performance",
                "--tb=short",
                "--json-report", "--json-report-file=performance-report.json"
            ], capture_output=True, text=True, timeout=2400)  # 40 minutes
            
            # Parse test report
            report_data = {}
            try:
                with open("performance-report.json", "r") as f:
                    report_data = json.load(f)
            except FileNotFoundError:
                pass
            
            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr if result.returncode != 0 else None,
                "report_data": report_data,
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
            
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Performance tests timed out",
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
    
    async def _run_multi_tenant_tests(self) -> Dict[str, Any]:
        """Run multi-tenant tests."""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                "-v", "-m", "multi_tenant",
                "--tb=short",
                "--json-report", "--json-report-file=multi-tenant-report.json"
            ], capture_output=True, text=True, timeout=1200)
            
            # Parse test report
            report_data = {}
            try:
                with open("multi-tenant-report.json", "r") as f:
                    report_data = json.load(f)
            except FileNotFoundError:
                pass
            
            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr if result.returncode != 0 else None,
                "report_data": report_data,
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
            
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Multi-tenant tests timed out",
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
    
    async def _run_security_tests(self) -> Dict[str, Any]:
        """Run security tests."""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                "-v", "-m", "security",
                "--tb=short",
                "--json-report", "--json-report-file=security-report.json"
            ], capture_output=True, text=True, timeout=1200)
            
            # Parse test report
            report_data = {}
            try:
                with open("security-report.json", "r") as f:
                    report_data = json.load(f)
            except FileNotFoundError:
                pass
            
            return {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr if result.returncode != 0 else None,
                "report_data": report_data,
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
            
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Security tests timed out",
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "constitutional_hash": self.CONSTITUTIONAL_HASH
            }
    
    def _generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        # Count passed/failed tests
        test_categories = [
            "constitutional_compliance",
            "unit_tests", 
            "integration_tests",
            "performance_tests",
            "multi_tenant_tests",
            "security_tests"
        ]
        
        passed_categories = 0
        total_categories = 0
        
        for category in test_categories:
            if category in self.test_results:
                total_categories += 1
                if self.test_results[category].get("passed", False):
                    passed_categories += 1
        
        success_rate = passed_categories / total_categories if total_categories > 0 else 0.0
        
        # Get coverage from unit tests
        unit_coverage = self.test_results.get("unit_tests", {}).get("coverage_percentage", 0)
        
        # Determine overall status
        if success_rate == 1.0 and unit_coverage >= 80.0:
            overall_status = "PASS"
            production_ready = True
        elif success_rate >= 0.8:
            overall_status = "CONDITIONAL_PASS"
            production_ready = False
        else:
            overall_status = "FAIL"
            production_ready = False
        
        return {
            "overall_status": overall_status,
            "production_ready": production_ready,
            "success_rate": success_rate,
            "passed_categories": passed_categories,
            "total_categories": total_categories,
            "overall_coverage": unit_coverage,
            "test_duration_seconds": duration,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "constitutional_hash": self.CONSTITUTIONAL_HASH
        }
    
    def save_test_report(self, filename: str = "comprehensive-test-report.json"):
        """Save comprehensive test report."""
        try:
            with open(filename, "w") as f:
                json.dump(self.test_results, f, indent=2, default=str)
            logger.info(f"📄 Test report saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save test report: {e}")
    
    def print_test_summary(self):
        """Print test summary to console."""
        summary = self.test_results.get("summary", {})
        
        print("\n" + "="*80)
        print("🧪 ACGS COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        print(f"Constitutional Hash: {self.CONSTITUTIONAL_HASH}")
        print(f"Test Duration: {summary.get('test_duration_seconds', 0):.1f} seconds")
        print(f"Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        print(f"Test Coverage: {summary.get('overall_coverage', 0):.1f}%")
        print(f"Production Ready: {summary.get('production_ready', False)}")
        print("="*80)
        
        # Print individual test results
        for category, results in self.test_results.items():
            if category != "summary" and isinstance(results, dict):
                status = "✅ PASS" if results.get("passed", False) else "❌ FAIL"
                print(f"{category.replace('_', ' ').title()}: {status}")
        
        print("="*80)
        
        if summary.get("production_ready", False):
            print("✅ ALL TESTS PASSED - ACGS IS PRODUCTION READY")
        else:
            print("❌ SOME TESTS FAILED - ADDITIONAL WORK REQUIRED")
        
        print("="*80 + "\n")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="ACGS Comprehensive Test Runner")
    parser.add_argument("--skip-constitutional", action="store_true", help="Skip constitutional compliance tests")
    parser.add_argument("--skip-unit", action="store_true", help="Skip unit tests")
    parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--skip-performance", action="store_true", help="Skip performance tests")
    parser.add_argument("--skip-multi-tenant", action="store_true", help="Skip multi-tenant tests")
    parser.add_argument("--skip-security", action="store_true", help="Skip security tests")
    parser.add_argument("--output", default="comprehensive-test-report.json", help="Output file for test report")
    
    args = parser.parse_args()
    
    async def run_tests():
        runner = ComprehensiveTestRunner(args)
        
        try:
            results = await runner.run_all_tests()
            runner.save_test_report(args.output)
            runner.print_test_summary()
            
            # Exit with appropriate code
            summary = results.get("summary", {})
            if summary.get("production_ready", False):
                sys.exit(0)  # Success
            else:
                sys.exit(1)  # Failure
                
        except Exception as e:
            logger.error(f"Test runner failed: {e}")
            sys.exit(1)
    
    asyncio.run(run_tests())


if __name__ == "__main__":
    main()
