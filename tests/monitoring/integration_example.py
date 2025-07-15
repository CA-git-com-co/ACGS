#!/usr/bin/env python3
"""
Test Monitoring Integration Example for ACGS-2
Constitutional Hash: cdd01ef066bc6cf2

This module demonstrates how to integrate the test monitoring system
with pytest and other testing frameworks.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import pytest
from test_result_monitor import (
    TestMetricsCollector, TestMonitor, TestReportGenerator, 
    TestMonitoringWebServer, TestResult, TestSuiteResult,
    create_test_monitoring_system
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ACGSTestMonitoringPlugin:
    """Pytest plugin for ACGS-2 test monitoring"""
    
    def __init__(self, metrics_collector: TestMetricsCollector, monitor: TestMonitor):
        self.metrics_collector = metrics_collector
        self.monitor = monitor
        self.suite_start_time = None
        self.test_results = []
        
    def pytest_sessionstart(self, session):
        """Called when test session starts"""
        self.suite_start_time = datetime.utcnow()
        self.monitor.start_monitoring()
        logger.info("🔒 ACGS-2 Test monitoring started")
        
    def pytest_sessionfinish(self, session, exitstatus):
        """Called when test session finishes"""
        self.monitor.stop_monitoring()
        
        # Record suite result
        if self.suite_start_time:
            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results if r.status == "passed")
            failed_tests = sum(1 for r in self.test_results if r.status == "failed")
            skipped_tests = sum(1 for r in self.test_results if r.status == "skipped")
            error_tests = sum(1 for r in self.test_results if r.status == "error")
            
            total_duration = sum(r.duration for r in self.test_results)
            constitutional_compliant = sum(1 for r in self.test_results if r.constitutional_compliant)
            compliance_rate = (constitutional_compliant / total_tests * 100) if total_tests > 0 else 0
            
            suite_result = TestSuiteResult(
                suite_name="acgs_test_suite",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                error_tests=error_tests,
                total_duration=total_duration,
                start_time=self.suite_start_time,
                end_time=datetime.utcnow(),
                coverage_percentage=85.0,  # Would need to get from coverage report
                constitutional_compliance_rate=compliance_rate
            )
            
            self.metrics_collector.record_test_suite_result(suite_result)
            self.monitor.check_test_suite_alerts(suite_result)
        
        logger.info("🔒 ACGS-2 Test monitoring stopped")
        
    def pytest_runtest_setup(self, item):
        """Called before each test runs"""
        self.test_start_time = time.time()
        
    def pytest_runtest_teardown(self, item, nextitem):
        """Called after each test runs"""
        if hasattr(self, 'test_start_time'):
            duration = time.time() - self.test_start_time
            
            # Determine test type from markers or path
            test_type = "unit"
            if item.get_closest_marker("integration"):
                test_type = "integration"
            elif item.get_closest_marker("e2e"):
                test_type = "e2e"
            elif item.get_closest_marker("security"):
                test_type = "security"
            elif item.get_closest_marker("performance"):
                test_type = "performance"
            
            # Get test result status
            status = "passed"  # Default, will be updated in pytest_runtest_logreport
            
            # Create test result
            result = TestResult(
                test_name=item.nodeid,
                test_type=test_type,
                status=status,
                duration=duration,
                timestamp=datetime.utcnow(),
                constitutional_compliant=True,  # Default, should be determined by test logic
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            self.test_results.append(result)
            
    def pytest_runtest_logreport(self, report):
        """Called for each test report (setup, call, teardown)"""
        if report.when == "call":
            # Update the last test result with the actual outcome
            if self.test_results:
                last_result = self.test_results[-1]
                
                if report.failed:
                    last_result.status = "failed"
                    last_result.error_message = str(report.longrepr)
                elif report.skipped:
                    last_result.status = "skipped"
                elif report.passed:
                    last_result.status = "passed"
                
                # Record the test result
                self.metrics_collector.record_test_result(last_result)
                self.monitor.check_test_result_alerts(last_result)

class TestMonitoringIntegration:
    """Main integration class for test monitoring"""
    
    def __init__(self):
        self.metrics_collector, self.monitor, self.report_generator = create_test_monitoring_system()
        self.web_server = TestMonitoringWebServer(self.report_generator)
        self.web_server_task = None
        
    async def start_monitoring_server(self):
        """Start the monitoring web server"""
        server = self.web_server.start_server()
        self.web_server_task = asyncio.create_task(server)
        logger.info("Test monitoring web server started")
        
    def stop_monitoring_server(self):
        """Stop the monitoring web server"""
        if self.web_server_task:
            self.web_server_task.cancel()
            logger.info("Test monitoring web server stopped")
            
    def create_pytest_plugin(self):
        """Create pytest plugin for monitoring"""
        return ACGSTestMonitoringPlugin(self.metrics_collector, self.monitor)
        
    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        return self.report_generator.generate_comprehensive_report(days)
        
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save report to file"""
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"test_monitoring_report_{timestamp}.json"
            
        filepath = Path(__file__).parent / "reports" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        logger.info(f"Test monitoring report saved to: {filepath}")
        return str(filepath)

def pytest_configure(config):
    """Configure pytest with monitoring plugin"""
    if not hasattr(config, '_acgs_monitoring'):
        integration = TestMonitoringIntegration()
        plugin = integration.create_pytest_plugin()
        config.pluginmanager.register(plugin, "acgs_monitoring")
        config._acgs_monitoring = integration
        
        # Start monitoring server if requested
        if config.getoption("--monitoring-server", default=False):
            asyncio.create_task(integration.start_monitoring_server())

def pytest_unconfigure(config):
    """Clean up monitoring when pytest exits"""
    if hasattr(config, '_acgs_monitoring'):
        integration = config._acgs_monitoring
        integration.stop_monitoring_server()

def pytest_addoption(parser):
    """Add command line options for monitoring"""
    group = parser.getgroup("acgs-monitoring")
    group.addoption(
        "--monitoring-server",
        action="store_true",
        default=False,
        help="Start monitoring web server during test execution"
    )
    group.addoption(
        "--monitoring-report",
        action="store",
        default=None,
        help="Generate monitoring report after tests (specify filename)"
    )

# Example usage functions

async def example_standalone_monitoring():
    """Example of running monitoring system standalone"""
    integration = TestMonitoringIntegration()
    
    try:
        # Start monitoring server
        await integration.start_monitoring_server()
        
        # Simulate some test execution
        logger.info("Simulating test execution...")
        
        # Create some example test results
        test_results = [
            TestResult(
                test_name="test_constitutional_compliance",
                test_type="unit",
                status="passed",
                duration=1.5,
                timestamp=datetime.utcnow(),
                constitutional_compliant=True,
                performance_metrics={"memory_usage": 45.2}
            ),
            TestResult(
                test_name="test_security_validation",
                test_type="security",
                status="passed",
                duration=3.2,
                timestamp=datetime.utcnow(),
                constitutional_compliant=True
            ),
            TestResult(
                test_name="test_performance_benchmark",
                test_type="performance",
                status="failed",
                duration=10.5,
                timestamp=datetime.utcnow(),
                constitutional_compliant=False,
                error_message="Performance threshold exceeded"
            )
        ]
        
        # Record test results
        for result in test_results:
            integration.metrics_collector.record_test_result(result)
            
        # Generate and save report
        report = integration.generate_report(days=1)
        report_path = integration.save_report(report)
        
        logger.info(f"Monitoring running... Open http://localhost:8080 to view dashboard")
        logger.info(f"Report saved to: {report_path}")
        
        # Keep server running
        await asyncio.sleep(60)  # Run for 1 minute
        
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    finally:
        integration.stop_monitoring_server()

def run_tests_with_monitoring():
    """Run pytest with monitoring enabled"""
    # Example command line usage
    test_command = [
        "pytest",
        "--monitoring-server",
        "--monitoring-report=test_report.json",
        "-v",
        "--tb=short",
        "tests/"
    ]
    
    logger.info(f"Running tests with monitoring: {' '.join(test_command)}")
    os.system(' '.join(test_command))

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS-2 Test Monitoring System")
    parser.add_argument("--mode", choices=["standalone", "pytest"], default="standalone",
                       help="Run in standalone mode or with pytest")
    parser.add_argument("--report-days", type=int, default=7,
                       help="Number of days to include in report")
    parser.add_argument("--output", type=str, default=None,
                       help="Output file for report")
    
    args = parser.parse_args()
    
    if args.mode == "standalone":
        asyncio.run(example_standalone_monitoring())
    elif args.mode == "pytest":
        run_tests_with_monitoring()
    else:
        # Generate report only
        integration = TestMonitoringIntegration()
        report = integration.generate_report(args.report_days)
        
        output_file = args.output or f"test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = integration.save_report(report, output_file)
        
        print(f"Report generated: {report_path}")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Report covers last {args.report_days} days")