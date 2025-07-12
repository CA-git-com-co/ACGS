#!/usr/bin/env python3
"""
ACGS-2 Service Performance Test

Tests actual running services to measure current performance and identify optimization opportunities.
Focuses on P99 latency targets while maintaining constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp
import structlog

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = structlog.get_logger(__name__)


class ServicePerformanceTester:
    """Tests performance of running ACGS-2 services."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.services = {
            "constitutional_ai": "http://localhost:8001",
            "integrity": "http://localhost:8002", 
            "governance_synthesis": "http://localhost:8003",
            "policy_governance": "http://localhost:8004",
            "formal_verification": "http://localhost:8005",
            "auth": "http://localhost:8016"
        }

    async def test_service_performance(self, service_name: str, base_url: str, num_requests: int = 100) -> Dict:
        """Test performance of a specific service."""
        logger.info(f"🧪 Testing {service_name} performance at {base_url}")
        
        latencies = []
        successful_requests = 0
        constitutional_compliance_count = 0
        errors = []

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            for i in range(num_requests):
                start_time = time.perf_counter()
                
                try:
                    # Test health endpoint
                    async with session.get(f"{base_url}/health") as response:
                        end_time = time.perf_counter()
                        latency_ms = (end_time - start_time) * 1000
                        latencies.append(latency_ms)
                        
                        if response.status == 200:
                            successful_requests += 1
                            
                            # Check constitutional compliance
                            try:
                                data = await response.json()
                                if data.get("constitutional_hash") == CONSTITUTIONAL_HASH:
                                    constitutional_compliance_count += 1
                            except:
                                pass  # Not all services return JSON
                        
                except Exception as e:
                    end_time = time.perf_counter()
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                    errors.append(str(e))

        if not latencies:
            return {
                "service": service_name,
                "error": "No successful requests",
                "constitutional_hash": CONSTITUTIONAL_HASH
            }

        # Calculate performance metrics
        latencies.sort()
        total_requests = len(latencies)
        avg_latency = sum(latencies) / total_requests
        p50_latency = latencies[int(0.50 * total_requests)]
        p95_latency = latencies[int(0.95 * total_requests)]
        p99_latency = latencies[int(0.99 * total_requests)]
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        success_rate = (successful_requests / num_requests) * 100
        compliance_rate = (constitutional_compliance_count / successful_requests * 100) if successful_requests > 0 else 0

        return {
            "service": service_name,
            "base_url": base_url,
            "performance_metrics": {
                "total_requests": num_requests,
                "successful_requests": successful_requests,
                "success_rate_percent": success_rate,
                "avg_latency_ms": avg_latency,
                "p50_latency_ms": p50_latency,
                "p95_latency_ms": p95_latency,
                "p99_latency_ms": p99_latency,
                "min_latency_ms": min_latency,
                "max_latency_ms": max_latency
            },
            "constitutional_compliance": {
                "compliant_responses": constitutional_compliance_count,
                "compliance_rate_percent": compliance_rate,
                "constitutional_hash": CONSTITUTIONAL_HASH
            },
            "target_analysis": {
                "p99_target_ms": 5.0,
                "p99_target_met": p99_latency < 5.0,
                "performance_gap_ms": max(0, p99_latency - 5.0),
                "improvement_needed_percent": max(0, ((p99_latency - 5.0) / 5.0) * 100)
            },
            "errors": errors[:10] if errors else []  # Limit error list
        }

    async def test_all_services(self) -> Dict:
        """Test performance of all ACGS-2 services."""
        logger.info("🚀 Starting comprehensive service performance testing")
        
        results = {}
        
        for service_name, base_url in self.services.items():
            try:
                result = await self.test_service_performance(service_name, base_url)
                results[service_name] = result
                
                if "error" not in result:
                    p99 = result["performance_metrics"]["p99_latency_ms"]
                    target_met = "✅" if p99 < 5.0 else "❌"
                    logger.info(f"{target_met} {service_name}: P99 {p99:.2f}ms")
                else:
                    logger.warning(f"⚠️ {service_name}: {result['error']}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to test {service_name}: {e}")
                results[service_name] = {
                    "service": service_name,
                    "error": str(e),
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }

        return results

    async def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report."""
        logger.info("📊 Generating service performance report")
        
        # Test all services
        service_results = await self.test_all_services()
        
        # Calculate overall metrics
        all_p99_latencies = []
        services_meeting_target = 0
        total_tested_services = 0
        overall_compliance_rate = 0
        compliance_count = 0
        
        for service, result in service_results.items():
            if "error" not in result and "performance_metrics" in result:
                p99 = result["performance_metrics"]["p99_latency_ms"]
                all_p99_latencies.append(p99)
                
                if p99 < 5.0:
                    services_meeting_target += 1
                total_tested_services += 1
                
                # Track constitutional compliance
                compliance = result["constitutional_compliance"]["compliance_rate_percent"]
                overall_compliance_rate += compliance
                compliance_count += 1

        # Calculate summary metrics
        worst_p99 = max(all_p99_latencies) if all_p99_latencies else 0
        avg_p99 = sum(all_p99_latencies) / len(all_p99_latencies) if all_p99_latencies else 0
        target_success_rate = (services_meeting_target / total_tested_services * 100) if total_tested_services > 0 else 0
        avg_compliance_rate = (overall_compliance_rate / compliance_count) if compliance_count > 0 else 0

        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(service_results)

        report = {
            "report_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "test_version": "1.0",
                "target_p99_latency_ms": 5.0
            },
            "executive_summary": {
                "services_tested": total_tested_services,
                "services_meeting_p99_target": services_meeting_target,
                "target_success_rate_percent": target_success_rate,
                "worst_p99_latency_ms": worst_p99,
                "average_p99_latency_ms": avg_p99,
                "overall_constitutional_compliance_percent": avg_compliance_rate,
                "performance_target_met": worst_p99 < 5.0
            },
            "service_results": service_results,
            "optimization_recommendations": recommendations
        }

        return report

    def _generate_optimization_recommendations(self, service_results: Dict) -> List[str]:
        """Generate optimization recommendations based on test results."""
        recommendations = []
        
        for service, result in service_results.items():
            if "error" in result:
                recommendations.append(f"🔧 {service}: Service unavailable - check deployment status")
                continue
                
            if "performance_metrics" not in result:
                continue
                
            p99 = result["performance_metrics"]["p99_latency_ms"]
            compliance = result["constitutional_compliance"]["compliance_rate_percent"]
            
            # Performance recommendations
            if p99 > 50.0:
                recommendations.append(f"🚨 {service}: Critical performance issue (P99: {p99:.1f}ms) - requires immediate optimization")
            elif p99 > 10.0:
                recommendations.append(f"⚠️ {service}: High latency (P99: {p99:.1f}ms) - implement caching and connection pooling")
            elif p99 > 5.0:
                recommendations.append(f"🔧 {service}: Above target (P99: {p99:.1f}ms) - fine-tune connection pools and async processing")
            else:
                recommendations.append(f"✅ {service}: Excellent performance (P99: {p99:.1f}ms)")
            
            # Constitutional compliance recommendations
            if compliance < 100.0:
                recommendations.append(f"🔒 {service}: Constitutional compliance issue ({compliance:.1f}%) - verify hash validation")

        # General recommendations
        if not recommendations:
            recommendations.append("🎉 All services performing optimally!")
        
        recommendations.append(f"🔒 Constitutional compliance maintained: {CONSTITUTIONAL_HASH}")
        
        return recommendations


async def main():
    """Main performance testing execution."""
    print("🚀 ACGS-2 Service Performance Testing")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    
    tester = ServicePerformanceTester()
    
    try:
        # Generate performance report
        report = await tester.generate_performance_report()
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"reports/service_performance_test_{timestamp}.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        summary = report["executive_summary"]
        print("\n📊 PERFORMANCE SUMMARY")
        print("=" * 40)
        print(f"Services Tested: {summary['services_tested']}")
        print(f"Meeting P99 Target (<5ms): {summary['services_meeting_p99_target']}/{summary['services_tested']}")
        print(f"Success Rate: {summary['target_success_rate_percent']:.1f}%")
        print(f"Worst P99 Latency: {summary['worst_p99_latency_ms']:.2f}ms")
        print(f"Average P99 Latency: {summary['average_p99_latency_ms']:.2f}ms")
        print(f"Constitutional Compliance: {summary['overall_constitutional_compliance_percent']:.1f}%")
        print(f"Overall Target Met: {'✅ YES' if summary['performance_target_met'] else '❌ NO'}")
        
        print("\n🔧 OPTIMIZATION RECOMMENDATIONS")
        print("=" * 40)
        for rec in report['optimization_recommendations']:
            print(f"  {rec}")
        
        print(f"\n📄 Full report saved to: {report_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Performance testing failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
