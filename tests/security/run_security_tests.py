#!/usr/bin/env python3
"""
Security Test Runner for ACGS-2
Constitutional Hash: cdd01ef066bc6cf2

This script runs comprehensive security tests and generates detailed reports.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.security.test_comprehensive_security_validation import SecurityTestSuite, SecurityTestConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class SecurityTestRunner:
    """Main security test runner"""
    
    def __init__(self):
        self.config = SecurityTestConfig()
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
    async def run_security_tests(self) -> Dict[str, Any]:
        """Run all security tests and generate report"""
        logger.info("🔒 Starting ACGS-2 Security Test Suite...")
        logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        start_time = datetime.utcnow()
        
        async with SecurityTestSuite(self.config) as suite:
            # Run all security tests
            results = await suite.run_all_security_tests()
            
            # Generate comprehensive report
            report = suite.generate_security_report(results)
            
            # Add execution metadata
            report["execution_metadata"] = {
                "start_time": start_time.isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "execution_duration": (datetime.utcnow() - start_time).total_seconds(),
                "test_environment": {
                    "base_url": self.config.base_url,
                    "auth_service_url": self.config.auth_service_url,
                    "constitutional_ai_url": self.config.constitutional_ai_url,
                    "integrity_service_url": self.config.integrity_service_url,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
            }
            
            return report
    
    def save_report(self, report: Dict[str, Any]) -> str:
        """Save security test report to file"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"security_test_report_{timestamp}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Security test report saved to: {filepath}")
        return str(filepath)
    
    def print_summary(self, report: Dict[str, Any]):
        """Print security test summary"""
        summary = report["summary"]
        severity = report["severity_breakdown"]
        
        print("\n" + "="*60)
        print("🔒 ACGS-2 SECURITY TEST SUMMARY")
        print("="*60)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Test Execution Time: {report['test_execution_time']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed Tests: {summary['passed_tests']}")
        print(f"Failed Tests: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Constitutional Compliance: {summary['constitutional_compliance_rate']}%")
        print(f"Vulnerabilities Found: {summary['vulnerabilities_found']}")
        print("\nSeverity Breakdown:")
        print(f"  Critical: {severity['critical']}")
        print(f"  High: {severity['high']}")
        print(f"  Medium: {severity['medium']}")
        print(f"  Low: {severity['low']}")
        
        # Print detailed results
        print("\nDetailed Test Results:")
        print("-" * 40)
        for result in report["test_results"]:
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            compliance = "✅ COMPLIANT" if result["constitutional_compliant"] else "❌ NON-COMPLIANT"
            vulnerability = "⚠️ VULNERABLE" if result["vulnerability_found"] else "✅ SECURE"
            
            print(f"{result['test_name']}: {status}")
            print(f"  Compliance: {compliance}")
            print(f"  Security: {vulnerability}")
            print(f"  Severity: {result['severity'].upper()}")
            print(f"  Details: {result['details']}")
            
            if result["recommendations"]:
                print("  Recommendations:")
                for rec in result["recommendations"]:
                    print(f"    - {rec}")
            print()
        
        # Security recommendations
        if report["recommendations"]["immediate_action"]:
            print("\n🚨 IMMEDIATE ACTION REQUIRED:")
            print("-" * 40)
            for actions in report["recommendations"]["immediate_action"]:
                for action in actions:
                    print(f"  - {action}")
        
        if report["recommendations"]["security_improvements"]:
            print("\n🔧 SECURITY IMPROVEMENTS:")
            print("-" * 40)
            for improvements in report["recommendations"]["security_improvements"]:
                for improvement in improvements:
                    print(f"  - {improvement}")
        
        print("\n" + "="*60)
        
        # Overall security assessment
        if summary["success_rate"] >= 95 and severity["critical"] == 0:
            print("🛡️ OVERALL SECURITY STATUS: EXCELLENT")
        elif summary["success_rate"] >= 85 and severity["critical"] == 0:
            print("🔒 OVERALL SECURITY STATUS: GOOD")
        elif summary["success_rate"] >= 70 and severity["critical"] <= 1:
            print("⚠️ OVERALL SECURITY STATUS: NEEDS IMPROVEMENT")
        else:
            print("🚨 OVERALL SECURITY STATUS: CRITICAL ISSUES FOUND")
        
        print("="*60)
    
    def check_service_availability(self) -> bool:
        """Check if required services are available"""
        import aiohttp
        import asyncio
        
        async def check_service(url: str) -> bool:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                        return response.status == 200
            except Exception:
                return False
        
        async def check_all_services():
            services = [
                self.config.base_url,
                self.config.auth_service_url,
                self.config.constitutional_ai_url,
                self.config.integrity_service_url
            ]
            
            results = await asyncio.gather(*[check_service(url) for url in services], return_exceptions=True)
            return all(isinstance(result, bool) and result for result in results)
        
        return asyncio.run(check_all_services())

async def main():
    """Main function to run security tests"""
    runner = SecurityTestRunner()
    
    # Check service availability
    logger.info("Checking service availability...")
    if not runner.check_service_availability():
        logger.warning("⚠️ Some services may not be available. Tests will continue but may have limited coverage.")
    
    # Run security tests
    try:
        report = await runner.run_security_tests()
        
        # Save report
        report_path = runner.save_report(report)
        
        # Print summary
        runner.print_summary(report)
        
        # Exit with appropriate code
        summary = report["summary"]
        if summary["success_rate"] >= 95 and report["severity_breakdown"]["critical"] == 0:
            logger.info("✅ All security tests passed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Security tests failed or vulnerabilities found!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Security test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())