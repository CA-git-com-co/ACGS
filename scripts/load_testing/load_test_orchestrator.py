#!/usr/bin/env python3
"""
ACGS Load Testing Orchestrator
Enterprise-grade load testing orchestration and management system.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class LoadTestConfiguration:
    """Load test configuration."""
    test_name: str
    test_type: str  # smoke, load, stress, spike, volume, endurance
    duration_minutes: int
    max_vus: int
    ramp_up_duration: str
    target_rps: Optional[int] = None
    
    # SLA thresholds
    max_response_time_ms: float = 500.0
    max_error_rate_percent: float = 1.0
    min_constitutional_compliance: float = 0.95
    
    # Test parameters
    test_data_size: str = "small"  # small, medium, large
    include_constitutional_tests: bool = True
    include_evolution_tests: bool = True
    
    # Environment
    base_url: str = "http://localhost"
    services: Dict[str, int] = field(default_factory=lambda: {
        "auth-service": 8000,
        "ac-service": 8001,
        "integrity-service": 8002,
        "fv-service": 8003,
        "gs-service": 8004,
        "pgc-service": 8005,
        "ec-service": 8006
    })

@dataclass
class LoadTestResult:
    """Load test result."""
    test_id: str
    test_name: str
    test_type: str
    start_time: datetime
    end_time: datetime
    
    # Performance metrics
    total_requests: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    max_response_time_ms: float
    requests_per_second: float
    error_rate_percent: float
    
    # Constitutional compliance
    constitutional_compliance_rate: float
    
    # SLA compliance
    response_time_sla_pass: bool
    error_rate_sla_pass: bool
    constitutional_compliance_sla_pass: bool
    overall_sla_pass: bool
    
    # Additional data
    service_status: Dict[str, Dict] = field(default_factory=dict)
    detailed_results: Optional[Dict] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH

class LoadTestOrchestrator:
    """Enterprise-grade load testing orchestrator."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_results: List[LoadTestResult] = []
        
        # Predefined test configurations
        self.test_configurations = self.setup_test_configurations()
        
        logger.info("Load Test Orchestrator initialized")

    def setup_test_configurations(self) -> Dict[str, LoadTestConfiguration]:
        """Setup predefined test configurations."""
        return {
            "smoke": LoadTestConfiguration(
                test_name="Smoke Test",
                test_type="smoke",
                duration_minutes=2,
                max_vus=1,
                ramp_up_duration="30s",
                max_response_time_ms=200.0,
                max_error_rate_percent=0.1
            ),
            
            "load": LoadTestConfiguration(
                test_name="Load Test",
                test_type="load",
                duration_minutes=15,
                max_vus=20,
                ramp_up_duration="2m",
                target_rps=100,
                max_response_time_ms=300.0,
                max_error_rate_percent=0.5
            ),
            
            "stress": LoadTestConfiguration(
                test_name="Stress Test",
                test_type="stress",
                duration_minutes=30,
                max_vus=100,
                ramp_up_duration="5m",
                target_rps=500,
                max_response_time_ms=1000.0,
                max_error_rate_percent=2.0
            ),
            
            "spike": LoadTestConfiguration(
                test_name="Spike Test",
                test_type="spike",
                duration_minutes=5,
                max_vus=200,
                ramp_up_duration="10s",
                max_response_time_ms=2000.0,
                max_error_rate_percent=5.0
            ),
            
            "volume": LoadTestConfiguration(
                test_name="Volume Test",
                test_type="volume",
                duration_minutes=20,
                max_vus=50,
                ramp_up_duration="2m",
                test_data_size="large",
                max_response_time_ms=500.0,
                max_error_rate_percent=1.0
            ),
            
            "endurance": LoadTestConfiguration(
                test_name="Endurance Test",
                test_type="endurance",
                duration_minutes=60,
                max_vus=30,
                ramp_up_duration="5m",
                max_response_time_ms=400.0,
                max_error_rate_percent=0.5
            )
        }

    async def run_comprehensive_load_tests(self) -> List[LoadTestResult]:
        """Run comprehensive load testing suite."""
        logger.info("Starting comprehensive load testing suite...")
        
        # Pre-flight checks
        await self.perform_preflight_checks()
        
        # Create reports directory
        reports_dir = self.project_root / "reports/load_tests"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # Run test suite in order
        test_order = ["smoke", "load", "stress", "spike", "volume", "endurance"]
        
        for test_type in test_order:
            if test_type in self.test_configurations:
                try:
                    logger.info(f"Running {test_type} test...")
                    result = await self.run_load_test(test_type)
                    results.append(result)
                    
                    # Wait between tests
                    if test_type != test_order[-1]:
                        logger.info("Waiting 2 minutes between tests...")
                        await asyncio.sleep(120)
                        
                except Exception as e:
                    logger.error(f"Failed to run {test_type} test: {e}")
                    continue
        
        # Generate comprehensive report
        await self.generate_comprehensive_report(results)
        
        logger.info("Comprehensive load testing completed")
        return results

    async def run_load_test(self, test_type: str) -> LoadTestResult:
        """Run a specific load test."""
        if test_type not in self.test_configurations:
            raise ValueError(f"Unknown test type: {test_type}")
        
        config = self.test_configurations[test_type]
        test_id = f"{test_type}_{int(time.time())}"
        
        logger.info(f"Starting {config.test_name} (ID: {test_id})")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Run K6 test
            k6_result = await self.run_k6_test(config, test_id)
            
            end_time = datetime.now(timezone.utc)
            
            # Parse results
            result = await self.parse_test_results(
                test_id, config, start_time, end_time, k6_result
            )
            
            self.test_results.append(result)
            
            logger.info(f"Completed {config.test_name}: "
                       f"RPS={result.requests_per_second:.1f}, "
                       f"P95={result.p95_response_time_ms:.1f}ms, "
                       f"Errors={result.error_rate_percent:.2f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Load test {test_type} failed: {e}")
            raise

    async def run_k6_test(self, config: LoadTestConfiguration, test_id: str) -> Dict:
        """Run K6 load test."""
        k6_script = self.project_root / "tests/load/k6_load_tests.js"
        
        if not k6_script.exists():
            raise FileNotFoundError(f"K6 script not found: {k6_script}")
        
        # Prepare K6 command
        k6_cmd = [
            "k6", "run",
            "--out", f"json=reports/load_tests/k6_raw_{test_id}.json",
            "--summary-export", f"reports/load_tests/k6_summary_{test_id}.json"
        ]
        
        # Set environment variables
        env = os.environ.copy()
        env.update({
            "TEST_TYPE": config.test_type,
            "MAX_VUS": str(config.max_vus),
            "DURATION": f"{config.duration_minutes}m",
            "RAMP_UP": config.ramp_up_duration,
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH
        })
        
        # Add test-specific scenarios
        if config.test_type == "smoke":
            k6_cmd.extend(["--scenario", "smoke_test"])
        elif config.test_type == "load":
            k6_cmd.extend(["--scenario", "load_test"])
        elif config.test_type == "stress":
            k6_cmd.extend(["--scenario", "stress_test"])
        elif config.test_type == "spike":
            k6_cmd.extend(["--scenario", "spike_test"])
        elif config.test_type == "volume":
            k6_cmd.extend(["--scenario", "volume_test"])
        elif config.test_type == "endurance":
            k6_cmd.extend(["--scenario", "endurance_test"])
        
        k6_cmd.append(str(k6_script))
        
        # Run K6 test
        logger.info(f"Running K6 command: {' '.join(k6_cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *k6_cmd,
            env=env,
            cwd=str(self.project_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"K6 test failed: {stderr.decode()}")
            raise RuntimeError(f"K6 test failed with return code {process.returncode}")
        
        # Parse K6 output
        try:
            summary_file = self.project_root / f"reports/load_tests/k6_summary_{test_id}.json"
            if summary_file.exists():
                with open(summary_file) as f:
                    return json.load(f)
            else:
                # Fallback to parsing stdout
                return {"stdout": stdout.decode(), "stderr": stderr.decode()}
                
        except Exception as e:
            logger.warning(f"Failed to parse K6 results: {e}")
            return {"stdout": stdout.decode(), "stderr": stderr.decode()}

    async def parse_test_results(
        self, 
        test_id: str, 
        config: LoadTestConfiguration, 
        start_time: datetime, 
        end_time: datetime, 
        k6_result: Dict
    ) -> LoadTestResult:
        """Parse test results from K6 output."""
        
        # Extract metrics from K6 result
        test_summary = k6_result.get("test_summary", {})
        performance_metrics = k6_result.get("performance_metrics", {})
        sla_compliance = k6_result.get("sla_compliance", {})
        
        # Create result object
        result = LoadTestResult(
            test_id=test_id,
            test_name=config.test_name,
            test_type=config.test_type,
            start_time=start_time,
            end_time=end_time,
            
            # Performance metrics
            total_requests=test_summary.get("total_requests", 0),
            avg_response_time_ms=performance_metrics.get("avg_response_time", 0),
            p95_response_time_ms=performance_metrics.get("p95_response_time", 0),
            p99_response_time_ms=performance_metrics.get("p99_response_time", 0),
            max_response_time_ms=performance_metrics.get("max_response_time", 0),
            requests_per_second=performance_metrics.get("requests_per_second", 0),
            error_rate_percent=test_summary.get("error_rate", 0) * 100,
            
            # Constitutional compliance
            constitutional_compliance_rate=test_summary.get("constitutional_compliance_rate", 1.0),
            
            # SLA compliance
            response_time_sla_pass=sla_compliance.get("response_time_sla", False),
            error_rate_sla_pass=sla_compliance.get("error_rate_sla", False),
            constitutional_compliance_sla_pass=sla_compliance.get("constitutional_compliance_sla", False),
            overall_sla_pass=all([
                sla_compliance.get("response_time_sla", False),
                sla_compliance.get("error_rate_sla", False),
                sla_compliance.get("constitutional_compliance_sla", False)
            ]),
            
            # Additional data
            service_status=k6_result.get("service_status", {}),
            detailed_results=k6_result
        )
        
        return result

    async def perform_preflight_checks(self):
        """Perform pre-flight checks before load testing."""
        logger.info("Performing pre-flight checks...")
        
        # Check K6 installation
        try:
            process = await asyncio.create_subprocess_exec(
                "k6", "version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"K6 version: {stdout.decode().strip()}")
            else:
                raise RuntimeError("K6 not found or not working")
                
        except FileNotFoundError:
            raise RuntimeError("K6 not installed. Please install K6 load testing tool.")
        
        # Check ACGS services availability
        import aiohttp
        
        services_status = {}
        for service_name, port in self.test_configurations["load"].services.items():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://localhost:{port}/health", timeout=10) as response:
                        services_status[service_name] = {
                            "available": response.status == 200,
                            "status_code": response.status
                        }
            except Exception as e:
                services_status[service_name] = {
                    "available": False,
                    "error": str(e)
                }
        
        available_services = sum(1 for status in services_status.values() if status["available"])
        total_services = len(services_status)
        
        if available_services < total_services * 0.8:  # At least 80% services should be available
            raise RuntimeError(f"Only {available_services}/{total_services} services available")
        
        logger.info(f"✓ Pre-flight checks passed: {available_services}/{total_services} services available")

    async def generate_comprehensive_report(self, results: List[LoadTestResult]):
        """Generate comprehensive load testing report."""
        logger.info("Generating comprehensive load testing report...")
        
        # Create comprehensive report
        report = {
            "load_test_suite_summary": {
                "total_tests": len(results),
                "successful_tests": sum(1 for r in results if r.overall_sla_pass),
                "failed_tests": sum(1 for r in results if not r.overall_sla_pass),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "test_duration": str(max(r.end_time for r in results) - min(r.start_time for r in results)) if results else "0:00:00"
            },
            "test_results": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "test_type": r.test_type,
                    "duration": str(r.end_time - r.start_time),
                    "performance_metrics": {
                        "total_requests": r.total_requests,
                        "avg_response_time_ms": r.avg_response_time_ms,
                        "p95_response_time_ms": r.p95_response_time_ms,
                        "requests_per_second": r.requests_per_second,
                        "error_rate_percent": r.error_rate_percent,
                        "constitutional_compliance_rate": r.constitutional_compliance_rate
                    },
                    "sla_compliance": {
                        "response_time_sla": r.response_time_sla_pass,
                        "error_rate_sla": r.error_rate_sla_pass,
                        "constitutional_compliance_sla": r.constitutional_compliance_sla_pass,
                        "overall_sla": r.overall_sla_pass
                    }
                }
                for r in results
            ],
            "performance_summary": {
                "max_throughput_rps": max((r.requests_per_second for r in results), default=0),
                "best_response_time_ms": min((r.avg_response_time_ms for r in results), default=0),
                "worst_response_time_ms": max((r.avg_response_time_ms for r in results), default=0),
                "overall_error_rate": sum(r.error_rate_percent for r in results) / len(results) if results else 0,
                "overall_constitutional_compliance": sum(r.constitutional_compliance_rate for r in results) / len(results) if results else 1.0
            },
            "recommendations": self.generate_recommendations(results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Save comprehensive report
        report_file = self.project_root / f"reports/load_tests/comprehensive_load_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate markdown report
        markdown_report = self.generate_markdown_report(report)
        markdown_file = self.project_root / f"reports/load_tests/load_test_report_{int(time.time())}.md"
        with open(markdown_file, 'w') as f:
            f.write(markdown_report)
        
        logger.info(f"Comprehensive report saved: {report_file}")
        logger.info(f"Markdown report saved: {markdown_file}")

    def generate_recommendations(self, results: List[LoadTestResult]) -> List[str]:
        """Generate performance recommendations based on test results."""
        recommendations = []
        
        if not results:
            return ["No test results available for analysis"]
        
        # Analyze response times
        avg_response_times = [r.avg_response_time_ms for r in results]
        max_response_time = max(avg_response_times)
        
        if max_response_time > 500:
            recommendations.append(f"High response times detected (max: {max_response_time:.1f}ms). Consider optimizing service performance.")
        
        # Analyze error rates
        error_rates = [r.error_rate_percent for r in results]
        max_error_rate = max(error_rates)
        
        if max_error_rate > 1:
            recommendations.append(f"High error rates detected (max: {max_error_rate:.1f}%). Investigate error sources and improve error handling.")
        
        # Analyze constitutional compliance
        compliance_rates = [r.constitutional_compliance_rate for r in results]
        min_compliance = min(compliance_rates)
        
        if min_compliance < 0.95:
            recommendations.append(f"Low constitutional compliance detected (min: {min_compliance:.1%}). Review constitutional validation implementation.")
        
        # Analyze SLA compliance
        sla_failures = [r for r in results if not r.overall_sla_pass]
        if sla_failures:
            recommendations.append(f"{len(sla_failures)} test(s) failed SLA requirements. Review performance optimization strategies.")
        
        if not recommendations:
            recommendations.append("All load tests passed successfully. System performance is within acceptable parameters.")
        
        return recommendations

    def generate_markdown_report(self, report: Dict) -> str:
        """Generate markdown report."""
        markdown = f"""# ACGS Load Testing Report

## Summary
- **Total Tests**: {report['load_test_suite_summary']['total_tests']}
- **Successful Tests**: {report['load_test_suite_summary']['successful_tests']}
- **Failed Tests**: {report['load_test_suite_summary']['failed_tests']}
- **Test Duration**: {report['load_test_suite_summary']['test_duration']}
- **Constitutional Hash**: `{report['load_test_suite_summary']['constitutional_hash']}`

## Performance Summary
- **Max Throughput**: {report['performance_summary']['max_throughput_rps']:.1f} RPS
- **Best Response Time**: {report['performance_summary']['best_response_time_ms']:.1f}ms
- **Worst Response Time**: {report['performance_summary']['worst_response_time_ms']:.1f}ms
- **Overall Error Rate**: {report['performance_summary']['overall_error_rate']:.2f}%
- **Constitutional Compliance**: {report['performance_summary']['overall_constitutional_compliance']:.1%}

## Test Results

"""
        
        for test in report['test_results']:
            sla_status = "✅ PASS" if test['sla_compliance']['overall_sla'] else "❌ FAIL"
            
            markdown += f"""### {test['test_name']} ({test['test_type']})
- **Duration**: {test['duration']}
- **Total Requests**: {test['performance_metrics']['total_requests']:,}
- **Avg Response Time**: {test['performance_metrics']['avg_response_time_ms']:.1f}ms
- **P95 Response Time**: {test['performance_metrics']['p95_response_time_ms']:.1f}ms
- **Throughput**: {test['performance_metrics']['requests_per_second']:.1f} RPS
- **Error Rate**: {test['performance_metrics']['error_rate_percent']:.2f}%
- **Constitutional Compliance**: {test['performance_metrics']['constitutional_compliance_rate']:.1%}
- **SLA Compliance**: {sla_status}

"""
        
        markdown += "## Recommendations\n\n"
        for rec in report['recommendations']:
            markdown += f"- {rec}\n"
        
        return markdown

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS Load Testing Orchestrator")
    parser.add_argument("--test-type", choices=["smoke", "load", "stress", "spike", "volume", "endurance", "all"], 
                       default="all", help="Type of load test to run")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    
    args = parser.parse_args()
    
    orchestrator = LoadTestOrchestrator()
    
    try:
        if args.test_type == "all":
            results = await orchestrator.run_comprehensive_load_tests()
        else:
            result = await orchestrator.run_load_test(args.test_type)
            results = [result]
        
        # Print summary
        print("\n" + "="*60)
        print("ACGS LOAD TESTING RESULTS")
        print("="*60)
        
        for result in results:
            sla_status = "PASS" if result.overall_sla_pass else "FAIL"
            print(f"{result.test_name}: {sla_status}")
            print(f"  RPS: {result.requests_per_second:.1f}")
            print(f"  P95: {result.p95_response_time_ms:.1f}ms")
            print(f"  Errors: {result.error_rate_percent:.2f}%")
            print(f"  Constitutional Compliance: {result.constitutional_compliance_rate:.1%}")
        
        print("="*60)
        
        # Exit with error if any tests failed
        if any(not r.overall_sla_pass for r in results):
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Load testing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
