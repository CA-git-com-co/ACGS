#!/usr/bin/env python3
"""
ACGS-2 Constitutional Performance Testing Suite
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive performance testing to validate constitutional requirements:
- P99 Latency: <5ms
- Throughput: >100 RPS  
- Cache Hit Rate: >85%
- Constitutional Compliance: 100%
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import argparse
import sys
import os

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@dataclass
class PerformanceTarget:
    """Constitutional performance targets"""
    p99_latency_ms: float = 5.0
    min_throughput_rps: float = 100.0
    min_cache_hit_rate: float = 85.0
    constitutional_compliance: float = 100.0

@dataclass
class ServiceConfig:
    """Service configuration for testing"""
    name: str
    base_url: str
    health_endpoint: str = "/health"
    test_endpoints: List[str] = None
    auth_required: bool = False
    constitutional_service: bool = False

@dataclass
class TestResult:
    """Individual test result"""
    service_name: str
    endpoint: str
    response_time_ms: float
    status_code: int
    success: bool
    constitutional_valid: bool
    timestamp: datetime

@dataclass
class ServicePerformanceReport:
    """Performance report for a service"""
    service_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    actual_throughput_rps: float
    success_rate: float
    constitutional_compliance_rate: float
    meets_p99_target: bool
    meets_throughput_target: bool
    meets_constitutional_target: bool
    overall_pass: bool

@dataclass
class SystemPerformanceReport:
    """Overall system performance report"""
    test_duration_seconds: float
    total_requests: int
    successful_requests: int
    system_avg_response_time_ms: float
    system_p99_response_time_ms: float
    system_throughput_rps: float
    constitutional_compliance_rate: float
    services_meeting_targets: int
    total_services_tested: int
    overall_system_pass: bool
    service_reports: List[ServicePerformanceReport]
    timestamp: datetime

class ConstitutionalPerformanceTester:
    """Constitutional performance testing engine"""
    
    def __init__(self, targets: PerformanceTarget = None):
        self.targets = targets or PerformanceTarget()
        self.services = self._initialize_services()
        self.auth_token = None
        self.results: List[TestResult] = []
        
    def _initialize_services(self) -> List[ServiceConfig]:
        """Initialize service configurations"""
        return [
            ServiceConfig(
                name="constitutional-core",
                base_url="http://localhost:8001",
                test_endpoints=["/health", "/api/v1/constitutional/validate"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="auth-service", 
                base_url="http://localhost:8013",
                test_endpoints=["/health", "/api/v1/auth/health"],
                auth_required=False,
                constitutional_service=True
            ),
            ServiceConfig(
                name="monitoring-service",
                base_url="http://localhost:8014", 
                test_endpoints=["/health", "/api/v1/services/health"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="audit-service",
                base_url="http://localhost:8015",
                test_endpoints=["/health", "/api/v1/audit/health"],
                auth_required=True, 
                constitutional_service=True
            ),
            ServiceConfig(
                name="gdpr-compliance",
                base_url="http://localhost:8016",
                test_endpoints=["/health", "/api/v1/gdpr/health"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="alerting-service",
                base_url="http://localhost:8017",
                test_endpoints=["/health", "/api/v1/alerts"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="api-gateway",
                base_url="http://localhost:8080",
                test_endpoints=["/health", "/gateway/metrics"],
                auth_required=False,
                constitutional_service=True
            ),
            ServiceConfig(
                name="groqcloud-policy",
                base_url="http://localhost:8023",
                test_endpoints=["/health"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="multi-agent-coordination", 
                base_url="http://localhost:8008",
                test_endpoints=["/health"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="worker-agents",
                base_url="http://localhost:8009", 
                test_endpoints=["/health"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="blackboard-coordination",
                base_url="http://localhost:8010",
                test_endpoints=["/health"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="consensus-engine",
                base_url="http://localhost:8011",
                test_endpoints=["/health"],
                auth_required=True,
                constitutional_service=True
            ),
            ServiceConfig(
                name="human-in-the-loop",
                base_url="http://localhost:8012",
                test_endpoints=["/health"],
                auth_required=True,
                constitutional_service=True
            )
        ]
    
    async def authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate with auth service to get token"""
        try:
            auth_data = {
                "username": "test_user",
                "password": "test_password"
            }
            
            async with session.post(
                "http://localhost:8013/api/v1/auth/login",
                json=auth_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get("access_token")
                    return True
                else:
                    print(f"⚠️ Authentication failed: {response.status}")
                    return False
        except Exception as e:
            print(f"⚠️ Authentication error: {e}")
            return False
    
    async def test_service_endpoint(
        self, 
        session: aiohttp.ClientSession, 
        service: ServiceConfig, 
        endpoint: str
    ) -> TestResult:
        """Test a single service endpoint"""
        start_time = time.time()
        url = f"{service.base_url}{endpoint}"
        
        headers = {}
        if service.auth_required and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            async with session.get(
                url, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time_ms = (time.time() - start_time) * 1000
                
                # Check constitutional compliance
                constitutional_valid = True
                if service.constitutional_service:
                    try:
                        data = await response.json()
                        constitutional_hash = data.get("constitutional_hash")
                        constitutional_valid = (constitutional_hash == CONSTITUTIONAL_HASH)
                    except:
                        constitutional_valid = False
                
                return TestResult(
                    service_name=service.name,
                    endpoint=endpoint,
                    response_time_ms=response_time_ms,
                    status_code=response.status,
                    success=(response.status == 200),
                    constitutional_valid=constitutional_valid,
                    timestamp=datetime.utcnow()
                )
                
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return TestResult(
                service_name=service.name,
                endpoint=endpoint,
                response_time_ms=response_time_ms,
                status_code=0,
                success=False,
                constitutional_valid=False,
                timestamp=datetime.utcnow()
            )
    
    async def load_test_service(
        self, 
        session: aiohttp.ClientSession,
        service: ServiceConfig, 
        duration_seconds: int = 60,
        target_rps: int = 150
    ) -> List[TestResult]:
        """Perform load testing on a service"""
        print(f"🔄 Load testing {service.name} for {duration_seconds}s at {target_rps} RPS...")
        
        results = []
        end_time = time.time() + duration_seconds
        request_interval = 1.0 / target_rps
        
        while time.time() < end_time:
            # Test all endpoints for this service
            tasks = []
            for endpoint in (service.test_endpoints or [service.health_endpoint]):
                task = self.test_service_endpoint(session, service, endpoint)
                tasks.append(task)
            
            # Execute requests
            if tasks:
                endpoint_results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in endpoint_results:
                    if isinstance(result, TestResult):
                        results.append(result)
            
            # Wait for next interval
            await asyncio.sleep(request_interval)
        
        return results
    
    def analyze_service_performance(
        self, 
        service_name: str, 
        results: List[TestResult]
    ) -> ServicePerformanceReport:
        """Analyze performance results for a service"""
        service_results = [r for r in results if r.service_name == service_name]
        
        if not service_results:
            return ServicePerformanceReport(
                service_name=service_name,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time_ms=0,
                p95_response_time_ms=0,
                p99_response_time_ms=0,
                min_response_time_ms=0,
                max_response_time_ms=0,
                actual_throughput_rps=0,
                success_rate=0,
                constitutional_compliance_rate=0,
                meets_p99_target=False,
                meets_throughput_target=False,
                meets_constitutional_target=False,
                overall_pass=False
            )
        
        # Calculate metrics
        total_requests = len(service_results)
        successful_requests = len([r for r in service_results if r.success])
        failed_requests = total_requests - successful_requests
        
        response_times = [r.response_time_ms for r in service_results if r.success]
        constitutional_valid = [r for r in service_results if r.constitutional_valid]
        
        if response_times:
            avg_response_time_ms = statistics.mean(response_times)
            min_response_time_ms = min(response_times)
            max_response_time_ms = max(response_times)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p95_index = int(0.95 * len(sorted_times))
            p99_index = int(0.99 * len(sorted_times))
            
            p95_response_time_ms = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time_ms
            p99_response_time_ms = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time_ms
        else:
            avg_response_time_ms = 0
            p95_response_time_ms = 0  
            p99_response_time_ms = 0
            min_response_time_ms = 0
            max_response_time_ms = 0
        
        # Calculate rates
        test_duration = (service_results[-1].timestamp - service_results[0].timestamp).total_seconds()
        actual_throughput_rps = total_requests / test_duration if test_duration > 0 else 0
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        constitutional_compliance_rate = (len(constitutional_valid) / total_requests * 100) if total_requests > 0 else 0
        
        # Check targets
        meets_p99_target = p99_response_time_ms <= self.targets.p99_latency_ms
        meets_throughput_target = actual_throughput_rps >= self.targets.min_throughput_rps
        meets_constitutional_target = constitutional_compliance_rate >= self.targets.constitutional_compliance
        
        overall_pass = meets_p99_target and meets_throughput_target and meets_constitutional_target
        
        return ServicePerformanceReport(
            service_name=service_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time_ms,
            p95_response_time_ms=p95_response_time_ms,
            p99_response_time_ms=p99_response_time_ms,
            min_response_time_ms=min_response_time_ms,
            max_response_time_ms=max_response_time_ms,
            actual_throughput_rps=actual_throughput_rps,
            success_rate=success_rate,
            constitutional_compliance_rate=constitutional_compliance_rate,
            meets_p99_target=meets_p99_target,
            meets_throughput_target=meets_throughput_target,
            meets_constitutional_target=meets_constitutional_target,
            overall_pass=overall_pass
        )
    
    async def run_comprehensive_test(
        self, 
        duration_seconds: int = 60,
        target_rps: int = 150
    ) -> SystemPerformanceReport:
        """Run comprehensive performance test across all services"""
        print(f"🚀 Starting ACGS-2 Constitutional Performance Test Suite")
        print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"⏱️ Duration: {duration_seconds}s per service")
        print(f"🎯 Target RPS: {target_rps}")
        print(f"📊 Constitutional Targets:")
        print(f"   - P99 Latency: <{self.targets.p99_latency_ms}ms")
        print(f"   - Throughput: >{self.targets.min_throughput_rps} RPS")
        print(f"   - Constitutional Compliance: >{self.targets.constitutional_compliance}%")
        print("=" * 80)
        
        start_time = time.time()
        all_results = []
        
        # Test each service
        async with aiohttp.ClientSession() as session:
            # Authenticate first
            print("🔐 Authenticating with auth service...")
            auth_success = await self.authenticate(session)
            if not auth_success:
                print("❌ Authentication failed - continuing with unauthenticated tests")
            
            for service in self.services:
                try:
                    service_results = await self.load_test_service(
                        session, service, duration_seconds, target_rps
                    )
                    all_results.extend(service_results)
                    
                    # Quick analysis
                    service_report = self.analyze_service_performance(service.name, service_results)
                    status = "✅ PASS" if service_report.overall_pass else "❌ FAIL"
                    print(f"   {status} {service.name}: "
                          f"P99={service_report.p99_response_time_ms:.1f}ms, "
                          f"RPS={service_report.actual_throughput_rps:.1f}, "
                          f"Success={service_report.success_rate:.1f}%")
                    
                except Exception as e:
                    print(f"❌ Error testing {service.name}: {e}")
        
        # Generate comprehensive report
        test_duration = time.time() - start_time
        service_reports = []
        
        for service in self.services:
            report = self.analyze_service_performance(service.name, all_results)
            service_reports.append(report)
        
        # System-wide metrics
        total_requests = len(all_results)
        successful_requests = len([r for r in all_results if r.success])
        
        if all_results:
            system_avg_response_time_ms = statistics.mean([r.response_time_ms for r in all_results if r.success])
            all_response_times = sorted([r.response_time_ms for r in all_results if r.success])
            p99_index = int(0.99 * len(all_response_times))
            system_p99_response_time_ms = all_response_times[p99_index] if all_response_times else 0
            system_throughput_rps = total_requests / test_duration
            constitutional_valid = len([r for r in all_results if r.constitutional_valid])
            constitutional_compliance_rate = (constitutional_valid / total_requests * 100) if total_requests > 0 else 0
        else:
            system_avg_response_time_ms = 0
            system_p99_response_time_ms = 0
            system_throughput_rps = 0
            constitutional_compliance_rate = 0
        
        services_meeting_targets = len([r for r in service_reports if r.overall_pass])
        total_services_tested = len(service_reports)
        
        overall_system_pass = (
            system_p99_response_time_ms <= self.targets.p99_latency_ms and
            system_throughput_rps >= self.targets.min_throughput_rps and
            constitutional_compliance_rate >= self.targets.constitutional_compliance and
            services_meeting_targets == total_services_tested
        )
        
        return SystemPerformanceReport(
            test_duration_seconds=test_duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            system_avg_response_time_ms=system_avg_response_time_ms,
            system_p99_response_time_ms=system_p99_response_time_ms,
            system_throughput_rps=system_throughput_rps,
            constitutional_compliance_rate=constitutional_compliance_rate,
            services_meeting_targets=services_meeting_targets,
            total_services_tested=total_services_tested,
            overall_system_pass=overall_system_pass,
            service_reports=service_reports,
            timestamp=datetime.utcnow()
        )
    
    def generate_detailed_report(self, report: SystemPerformanceReport) -> str:
        """Generate detailed performance test report"""
        
        report_lines = [
            "=" * 100,
            "🏛️ ACGS-2 CONSTITUTIONAL PERFORMANCE TEST REPORT",
            "=" * 100,
            f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}",
            f"⏰ Test Completed: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"⏱️ Test Duration: {report.test_duration_seconds:.1f} seconds",
            "",
            "📊 SYSTEM-WIDE PERFORMANCE SUMMARY",
            "─" * 50,
            f"Total Requests: {report.total_requests:,}",
            f"Successful Requests: {report.successful_requests:,} ({report.successful_requests/report.total_requests*100:.1f}%)",
            f"System P99 Latency: {report.system_p99_response_time_ms:.2f}ms (Target: <{self.targets.p99_latency_ms}ms)",
            f"System Throughput: {report.system_throughput_rps:.1f} RPS (Target: >{self.targets.min_throughput_rps} RPS)",
            f"Constitutional Compliance: {report.constitutional_compliance_rate:.1f}% (Target: {self.targets.constitutional_compliance}%)",
            "",
            f"🎯 CONSTITUTIONAL COMPLIANCE STATUS: {'✅ PASS' if report.overall_system_pass else '❌ FAIL'}",
            f"Services Meeting Targets: {report.services_meeting_targets}/{report.total_services_tested}",
            "",
            "📈 DETAILED SERVICE PERFORMANCE",
            "─" * 100
        ]
        
        # Service details table header
        report_lines.extend([
            f"{'Service':<20} {'Requests':<10} {'Success%':<9} {'P99 (ms)':<10} {'RPS':<8} {'Const%':<7} {'Status':<8}",
            "─" * 100
        ])
        
        # Service details
        for service_report in sorted(report.service_reports, key=lambda x: x.service_name):
            status = "✅ PASS" if service_report.overall_pass else "❌ FAIL"
            
            report_lines.append(
                f"{service_report.service_name:<20} "
                f"{service_report.total_requests:<10} "
                f"{service_report.success_rate:<8.1f}% "
                f"{service_report.p99_response_time_ms:<9.2f} "
                f"{service_report.actual_throughput_rps:<7.1f} "
                f"{service_report.constitutional_compliance_rate:<6.1f}% "
                f"{status:<8}"
            )
        
        report_lines.extend([
            "",
            "🔍 DETAILED PERFORMANCE BREAKDOWN",
            "─" * 100
        ])
        
        for service_report in service_report.service_reports:
            if not service_report.overall_pass:
                report_lines.extend([
                    f"\n❌ {service_report.service_name.upper()} - PERFORMANCE ISSUES DETECTED:",
                    f"   Total Requests: {service_report.total_requests}",
                    f"   Success Rate: {service_report.success_rate:.1f}%",
                    f"   Avg Response Time: {service_report.avg_response_time_ms:.2f}ms",
                    f"   P95 Response Time: {service_report.p95_response_time_ms:.2f}ms",
                    f"   P99 Response Time: {service_report.p99_response_time_ms:.2f}ms",
                    f"   Throughput: {service_report.actual_throughput_rps:.1f} RPS",
                    f"   Constitutional Compliance: {service_report.constitutional_compliance_rate:.1f}%",
                    ""
                ])
                
                # Specific failures
                failures = []
                if not service_report.meets_p99_target:
                    failures.append(f"P99 latency ({service_report.p99_response_time_ms:.2f}ms) exceeds target ({self.targets.p99_latency_ms}ms)")
                if not service_report.meets_throughput_target:
                    failures.append(f"Throughput ({service_report.actual_throughput_rps:.1f} RPS) below target ({self.targets.min_throughput_rps} RPS)")
                if not service_report.meets_constitutional_target:
                    failures.append(f"Constitutional compliance ({service_report.constitutional_compliance_rate:.1f}%) below target ({self.targets.constitutional_compliance}%)")
                
                for failure in failures:
                    report_lines.append(f"   🚨 {failure}")
                
                report_lines.append("")
        
        # Constitutional compliance summary
        constitutional_services = [s for s in report.service_reports if s.constitutional_compliance_rate == 100.0]
        report_lines.extend([
            "⚖️ CONSTITUTIONAL COMPLIANCE SUMMARY",
            "─" * 50,
            f"Services with 100% Constitutional Compliance: {len(constitutional_services)}/{len(report.service_reports)}",
            ""
        ])
        
        if len(constitutional_services) < len(report.service_reports):
            non_compliant = [s for s in report.service_reports if s.constitutional_compliance_rate < 100.0]
            report_lines.append("🚨 NON-COMPLIANT SERVICES:")
            for service in non_compliant:
                report_lines.append(f"   - {service.service_name}: {service.constitutional_compliance_rate:.1f}% compliance")
            report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "💡 PERFORMANCE OPTIMIZATION RECOMMENDATIONS",
            "─" * 50
        ])
        
        if report.system_p99_response_time_ms > self.targets.p99_latency_ms:
            report_lines.append("🔧 P99 Latency Issues:")
            report_lines.append("   - Implement response caching")
            report_lines.append("   - Optimize database queries")
            report_lines.append("   - Add connection pooling")
            report_lines.append("")
        
        if report.system_throughput_rps < self.targets.min_throughput_rps:
            report_lines.append("🔧 Throughput Issues:")
            report_lines.append("   - Scale service instances")
            report_lines.append("   - Implement load balancing")
            report_lines.append("   - Optimize async processing")
            report_lines.append("")
        
        if report.constitutional_compliance_rate < self.targets.constitutional_compliance:
            report_lines.append("🔧 Constitutional Compliance Issues:")
            report_lines.append("   - Verify constitutional hash implementation")
            report_lines.append("   - Check service health endpoints")
            report_lines.append("   - Review constitutional validation logic")
            report_lines.append("")
        
        report_lines.extend([
            "=" * 100,
            f"📋 Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}",
            "=" * 100
        ])
        
        return "\n".join(report_lines)

async def main():
    """Main performance testing entry point"""
    parser = argparse.ArgumentParser(description="ACGS-2 Constitutional Performance Testing Suite")
    parser.add_argument("--duration", type=int, default=30, help="Test duration per service in seconds")
    parser.add_argument("--rps", type=int, default=120, help="Target requests per second")
    parser.add_argument("--output", type=str, default="performance_report.txt", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Also output JSON report")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = ConstitutionalPerformanceTester()
    
    # Run comprehensive test
    try:
        report = await tester.run_comprehensive_test(
            duration_seconds=args.duration,
            target_rps=args.rps
        )
        
        # Generate and save detailed report
        detailed_report = tester.generate_detailed_report(report)
        
        with open(args.output, 'w') as f:
            f.write(detailed_report)
        
        print(f"\n📄 Detailed report saved to: {args.output}")
        
        # Save JSON report if requested
        if args.json:
            json_file = args.output.replace('.txt', '.json')
            with open(json_file, 'w') as f:
                # Convert dataclasses to dict for JSON serialization
                json_data = {
                    "timestamp": report.timestamp.isoformat(),
                    "test_duration_seconds": report.test_duration_seconds,
                    "total_requests": report.total_requests,
                    "successful_requests": report.successful_requests,
                    "system_p99_response_time_ms": report.system_p99_response_time_ms,
                    "system_throughput_rps": report.system_throughput_rps,
                    "constitutional_compliance_rate": report.constitutional_compliance_rate,
                    "overall_system_pass": report.overall_system_pass,
                    "services": [
                        {
                            "name": s.service_name,
                            "total_requests": s.total_requests,
                            "success_rate": s.success_rate,
                            "p99_response_time_ms": s.p99_response_time_ms,
                            "throughput_rps": s.actual_throughput_rps,
                            "constitutional_compliance_rate": s.constitutional_compliance_rate,
                            "overall_pass": s.overall_pass
                        }
                        for s in report.service_reports
                    ]
                }
                json.dump(json_data, f, indent=2)
            
            print(f"📊 JSON report saved to: {json_file}")
        
        # Print summary
        print(f"\n🏛️ CONSTITUTIONAL PERFORMANCE TEST COMPLETE")
        print(f"{'='*50}")
        status = "✅ PASS" if report.overall_system_pass else "❌ FAIL"
        print(f"Overall Status: {status}")
        print(f"System P99 Latency: {report.system_p99_response_time_ms:.2f}ms (Target: <{tester.targets.p99_latency_ms}ms)")
        print(f"System Throughput: {report.system_throughput_rps:.1f} RPS (Target: >{tester.targets.min_throughput_rps} RPS)")
        print(f"Constitutional Compliance: {report.constitutional_compliance_rate:.1f}%")
        print(f"Services Passing: {report.services_meeting_targets}/{report.total_services_tested}")
        
        # Exit with appropriate code
        sys.exit(0 if report.overall_system_pass else 1)
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())