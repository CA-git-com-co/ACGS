#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Test Runner
===============================

Unified test runner for all ACGS-1 test suites with coverage reporting,
performance metrics, and detailed analysis.
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveTestRunner:
    """Comprehensive test runner for ACGS-1"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.path.dirname(os.path.dirname(__file__)))
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "coverage": {},
            "performance": {},
            "summary": {}
        }
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests with coverage"""
        logger.info("🧪 Running unit tests...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/unit/", "-v", "-m", "unit",
                "--cov=services", "--cov=scripts",
                "--cov-report=json:tests/coverage/unit_coverage.json",
                "--tb=short"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            return {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": "N/A"
            }
            
        except Exception as e:
            logger.error(f"❌ Unit tests failed: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("🔗 Running integration tests...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/integration/", "-v", "-m", "integration",
                "--tb=short"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=600)
            
            return {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            logger.error(f"❌ Integration tests failed: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests"""
        logger.info("🎯 Running end-to-end tests...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/e2e/", "-v", "-m", "e2e",
                "--tb=short"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=900)
            
            return {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            logger.error(f"❌ E2E tests failed: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        logger.info("⚡ Running performance tests...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/performance/", "-v", "-m", "performance",
                "--tb=short"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=1200)
            
            return {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            logger.error(f"❌ Performance tests failed: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def run_security_tests(self) -> Dict[str, Any]:
        """Run security tests"""
        logger.info("🔒 Running security tests...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/security/", "-v", "-m", "security",
                "--tb=short"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=600)
            
            return {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            logger.error(f"❌ Security tests failed: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def run_blockchain_tests(self) -> Dict[str, Any]:
        """Run blockchain/Anchor tests"""
        logger.info("⛓️ Running blockchain tests...")
        
        try:
            # Check if Anchor is available
            anchor_check = subprocess.run([
                "anchor", "--version"
            ], capture_output=True, text=True)
            
            if anchor_check.returncode != 0:
                return {"status": "SKIPPED", "reason": "Anchor not available"}
            
            result = subprocess.run([
                "anchor", "test"
            ], cwd=self.project_root / "blockchain", capture_output=True, text=True, timeout=600)
            
            return {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            logger.error(f"❌ Blockchain tests failed: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def generate_coverage_report(self):
        """Generate comprehensive coverage report"""
        logger.info("📊 Generating coverage report...")
        
        try:
            # Run comprehensive coverage analysis
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/", "--cov=services", "--cov=scripts", "--cov=blockchain",
                "--cov-report=html:tests/coverage/html",
                "--cov-report=json:tests/coverage/coverage.json",
                "--cov-report=term-missing",
                "--tb=no", "-q"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            # Parse coverage results
            coverage_file = self.project_root / "tests" / "coverage" / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                self.test_results["coverage"] = {
                    "overall_percentage": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                    "lines_total": coverage_data.get("totals", {}).get("num_statements", 0),
                    "files_analyzed": len(coverage_data.get("files", {})),
                    "target_met": coverage_data.get("totals", {}).get("percent_covered", 0) >= 80
                }
                
                logger.info(f"✅ Coverage: {coverage_data.get('totals', {}).get('percent_covered', 0):.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Coverage report generation failed: {e}")
            self.test_results["coverage"] = {"error": str(e)}
    
    def run_all_tests(self, test_types: List[str] = None):
        """Run all specified test types"""
        if test_types is None:
            test_types = ["unit", "integration", "e2e", "performance", "security", "blockchain"]
        
        logger.info("🚀 Starting comprehensive test execution...")
        
        # Run each test suite
        if "unit" in test_types:
            self.test_results["test_suites"]["unit"] = self.run_unit_tests()
        
        if "integration" in test_types:
            self.test_results["test_suites"]["integration"] = self.run_integration_tests()
        
        if "e2e" in test_types:
            self.test_results["test_suites"]["e2e"] = self.run_e2e_tests()
        
        if "performance" in test_types:
            self.test_results["test_suites"]["performance"] = self.run_performance_tests()
        
        if "security" in test_types:
            self.test_results["test_suites"]["security"] = self.run_security_tests()
        
        if "blockchain" in test_types:
            self.test_results["test_suites"]["blockchain"] = self.run_blockchain_tests()
        
        # Generate coverage report
        self.generate_coverage_report()
        
        # Calculate summary
        self._calculate_summary()
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary()
    
    def _calculate_summary(self):
        """Calculate test execution summary"""
        total_suites = len(self.test_results["test_suites"])
        passed_suites = len([s for s in self.test_results["test_suites"].values() 
                           if s.get("status") == "PASSED"])
        failed_suites = len([s for s in self.test_results["test_suites"].values() 
                           if s.get("status") == "FAILED"])
        error_suites = len([s for s in self.test_results["test_suites"].values() 
                          if s.get("status") == "ERROR"])
        skipped_suites = len([s for s in self.test_results["test_suites"].values() 
                            if s.get("status") == "SKIPPED"])
        
        self.test_results["summary"] = {
            "total_suites": total_suites,
            "passed_suites": passed_suites,
            "failed_suites": failed_suites,
            "error_suites": error_suites,
            "skipped_suites": skipped_suites,
            "success_rate": (passed_suites / total_suites * 100) if total_suites > 0 else 0,
            "overall_status": "PASSED" if failed_suites == 0 and error_suites == 0 else "FAILED"
        }
    
    def _save_results(self):
        """Save test results to file"""
        results_file = self.project_root / "tests" / "results" / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"📋 Test results saved: {results_file}")
    
    def _print_summary(self):
        """Print test execution summary"""
        summary = self.test_results["summary"]
        coverage = self.test_results.get("coverage", {})
        
        print("\n" + "="*60)
        print("🧪 ACGS-1 TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"📊 Test Suites: {summary['total_suites']}")
        print(f"✅ Passed: {summary['passed_suites']}")
        print(f"❌ Failed: {summary['failed_suites']}")
        print(f"⚠️ Errors: {summary['error_suites']}")
        print(f"⏭️ Skipped: {summary['skipped_suites']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"📊 Coverage: {coverage.get('overall_percentage', 0):.1f}%")
        print(f"🎯 Coverage Target Met: {'✅ YES' if coverage.get('target_met', False) else '❌ NO'}")
        print(f"🏆 Overall Status: {summary['overall_status']}")

def main():
    parser = argparse.ArgumentParser(description="ACGS-1 Comprehensive Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run e2e tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--blockchain", action="store_true", help="Run blockchain tests only")
    parser.add_argument("--all", action="store_true", help="Run all test suites")
    
    args = parser.parse_args()
    
    # Determine which tests to run
    test_types = []
    if args.unit:
        test_types.append("unit")
    if args.integration:
        test_types.append("integration")
    if args.e2e:
        test_types.append("e2e")
    if args.performance:
        test_types.append("performance")
    if args.security:
        test_types.append("security")
    if args.blockchain:
        test_types.append("blockchain")
    
    if args.all or not test_types:
        test_types = ["unit", "integration", "e2e", "performance", "security", "blockchain"]
    
    # Run tests
    runner = ComprehensiveTestRunner()
    runner.run_all_tests(test_types)

if __name__ == "__main__":
    main()
