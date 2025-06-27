#!/usr/bin/env python3
"""
Comprehensive Load Testing for ACGS-PGP Multimodal AI System

Large-scale load testing (1000+ concurrent requests) across all three AI models:
- DeepSeek R1 (cost-optimized)
- Gemini Flash Full (high-quality)
- Gemini Flash Lite (balanced)

Features:
- Concurrent request simulation
- Performance metrics collection
- Cost analysis under load
- Constitutional compliance validation
- Cache performance testing
- System stability monitoring

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import aiohttp
import statistics

import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class LoadTestRequest:
    """Individual load test request configuration."""
    request_id: str
    content: str
    request_type: str
    priority: str
    expected_model: Optional[str] = None
    content_type: str = "text_only"


@dataclass
class LoadTestResult:
    """Result of a single load test request."""
    request_id: str
    success: bool
    response_time_ms: float
    model_used: str
    constitutional_compliance: bool
    confidence_score: float
    cost_estimate: float
    cache_hit: bool
    error: Optional[str] = None


@dataclass
class LoadTestSummary:
    """Summary of load test results."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    total_cost: float
    constitutional_compliance_rate: float
    cache_hit_rate: float
    requests_per_second: float
    model_distribution: Dict[str, int]
    error_rate: float


class ComprehensiveLoadTester:
    """Comprehensive load testing system for multimodal AI services."""
    
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.base_url = "http://localhost:8001"  # Constitutional AI service
        
        # Load test configuration
        self.test_scenarios = {
            "quick_analysis": {
                "request_type": "quick_analysis",
                "expected_model": "deepseek/deepseek-r1-0528:free",
                "content_templates": [
                    "Quick constitutional check for: {topic}",
                    "Rapid analysis needed for: {topic}",
                    "Fast review of: {topic}"
                ]
            },
            "content_moderation": {
                "request_type": "content_moderation", 
                "expected_model": "deepseek/deepseek-r1-0528:free",
                "content_templates": [
                    "Moderate this content: {topic}",
                    "Check policy compliance: {topic}",
                    "Review for violations: {topic}"
                ]
            },
            "constitutional_validation": {
                "request_type": "constitutional_validation",
                "expected_model": "google/gemini-2.5-flash-lite-preview-06-17",
                "content_templates": [
                    "Constitutional analysis of: {topic}",
                    "Democratic governance review: {topic}",
                    "Rights compliance check: {topic}"
                ]
            },
            "policy_analysis": {
                "request_type": "policy_analysis",
                "expected_model": "google/gemini-2.5-flash",
                "content_templates": [
                    "Comprehensive policy analysis: {topic}",
                    "Detailed constitutional review: {topic}",
                    "In-depth governance assessment: {topic}"
                ]
            }
        }
        
        # Test topics for content generation
        self.test_topics = [
            "democratic participation rights",
            "transparent governance principles", 
            "constitutional protections",
            "voting rights access",
            "due process guarantees",
            "equal protection standards",
            "freedom of expression",
            "representative democracy",
            "checks and balances",
            "rule of law principles",
            "citizen accountability",
            "democratic institutions",
            "constitutional amendments",
            "civil liberties protection",
            "government transparency"
        ]
        
        logger.info("Comprehensive Load Tester initialized")
    
    async def execute_load_test(self, concurrent_requests: int = 1000, 
                               duration_seconds: int = 300) -> Dict[str, Any]:
        """Execute comprehensive load test with specified parameters."""
        
        logger.info(f"🚀 Starting Comprehensive Load Test")
        logger.info(f"   Concurrent Requests: {concurrent_requests}")
        logger.info(f"   Duration: {duration_seconds} seconds")
        logger.info(f"   Target Models: 3 (DeepSeek R1, Flash Full, Flash Lite)")
        logger.info("=" * 70)
        
        start_time = time.time()
        
        # Generate test requests
        test_requests = self._generate_test_requests(concurrent_requests)
        
        # Execute load test in batches
        batch_size = 50  # Process in batches to avoid overwhelming the system
        results = []
        
        for i in range(0, len(test_requests), batch_size):
            batch = test_requests[i:i + batch_size]
            batch_start = time.time()
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(test_requests) + batch_size - 1)//batch_size}")
            
            # Execute batch concurrently
            batch_results = await self._execute_batch(batch)
            results.extend(batch_results)
            
            batch_time = time.time() - batch_start
            logger.info(f"Batch completed in {batch_time:.1f}s, {len(batch_results)} results")
            
            # Check if duration exceeded
            if time.time() - start_time > duration_seconds:
                logger.info(f"Duration limit reached, stopping test")
                break
            
            # Small delay between batches to prevent overwhelming
            await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        
        # Analyze results
        summary = self._analyze_results(results, total_time)
        
        # Generate comprehensive report
        report = {
            "test_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": total_time,
                "target_concurrent_requests": concurrent_requests,
                "actual_requests_processed": len(results),
                "constitutional_hash": self.constitutional_hash
            },
            "performance_summary": asdict(summary),
            "detailed_results": [asdict(result) for result in results[:100]],  # First 100 for analysis
            "model_performance": self._analyze_model_performance(results),
            "cost_analysis": self._analyze_cost_performance(results),
            "compliance_analysis": self._analyze_compliance_performance(results),
            "cache_analysis": self._analyze_cache_performance(results),
            "recommendations": self._generate_recommendations(summary)
        }
        
        return report
    
    def _generate_test_requests(self, count: int) -> List[LoadTestRequest]:
        """Generate test requests for load testing."""
        
        requests = []
        scenario_names = list(self.test_scenarios.keys())
        
        for i in range(count):
            # Distribute requests across scenarios
            scenario_name = scenario_names[i % len(scenario_names)]
            scenario = self.test_scenarios[scenario_name]
            
            # Select topic and template
            topic = self.test_topics[i % len(self.test_topics)]
            template = scenario["content_templates"][i % len(scenario["content_templates"])]
            
            content = template.format(topic=topic)
            
            request = LoadTestRequest(
                request_id=f"load_test_{i:04d}",
                content=content,
                request_type=scenario["request_type"],
                priority="normal" if i % 3 != 0 else "high",  # 1/3 high priority
                expected_model=scenario["expected_model"],
                content_type="text_only"
            )
            
            requests.append(request)
        
        return requests
    
    async def _execute_batch(self, batch: List[LoadTestRequest]) -> List[LoadTestResult]:
        """Execute a batch of requests concurrently."""
        
        tasks = [self._execute_single_request(request) for request in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(LoadTestResult(
                    request_id=batch[i].request_id,
                    success=False,
                    response_time_ms=0,
                    model_used="error",
                    constitutional_compliance=False,
                    confidence_score=0.0,
                    cost_estimate=0.0,
                    cache_hit=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single_request(self, request: LoadTestRequest) -> LoadTestResult:
        """Execute a single load test request."""
        
        start_time = time.time()
        
        try:
            # Map request types to API endpoints
            endpoint_mapping = {
                "quick_analysis": "/api/v1/multimodal/analyze",
                "content_moderation": "/api/v1/multimodal/moderate",
                "constitutional_validation": "/api/v1/multimodal/analyze",
                "policy_analysis": "/api/v1/multimodal/analyze"
            }
            
            endpoint = endpoint_mapping.get(request.request_type, "/api/v1/multimodal/analyze")
            
            payload = {
                "text_content": request.content,
                "priority": request.priority
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}{endpoint}",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        result_data = await response.json()
                        
                        return LoadTestResult(
                            request_id=request.request_id,
                            success=True,
                            response_time_ms=response_time,
                            model_used=result_data.get("model_used", "unknown"),
                            constitutional_compliance=result_data.get("constitutional_compliance", False),
                            confidence_score=result_data.get("confidence_score", 0.0),
                            cost_estimate=result_data.get("performance_metrics", {}).get("cost_estimate", 0.0),
                            cache_hit=result_data.get("performance_metrics", {}).get("cache_hit", False)
                        )
                    else:
                        error_text = await response.text()
                        return LoadTestResult(
                            request_id=request.request_id,
                            success=False,
                            response_time_ms=response_time,
                            model_used="error",
                            constitutional_compliance=False,
                            confidence_score=0.0,
                            cost_estimate=0.0,
                            cache_hit=False,
                            error=f"HTTP {response.status}: {error_text}"
                        )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return LoadTestResult(
                request_id=request.request_id,
                success=False,
                response_time_ms=response_time,
                model_used="error",
                constitutional_compliance=False,
                confidence_score=0.0,
                cost_estimate=0.0,
                cache_hit=False,
                error=str(e)
            )
    
    def _analyze_results(self, results: List[LoadTestResult], total_time: float) -> LoadTestSummary:
        """Analyze load test results and generate summary."""
        
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        if not successful_results:
            return LoadTestSummary(
                total_requests=len(results),
                successful_requests=0,
                failed_requests=len(failed_results),
                avg_response_time_ms=0,
                p95_response_time_ms=0,
                p99_response_time_ms=0,
                total_cost=0,
                constitutional_compliance_rate=0,
                cache_hit_rate=0,
                requests_per_second=0,
                model_distribution={},
                error_rate=100.0
            )
        
        # Response time analysis
        response_times = [r.response_time_ms for r in successful_results]
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times)
        p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times)
        
        # Cost analysis
        total_cost = sum(r.cost_estimate for r in successful_results)
        
        # Compliance analysis
        compliant_count = sum(1 for r in successful_results if r.constitutional_compliance)
        compliance_rate = (compliant_count / len(successful_results)) * 100
        
        # Cache analysis
        cache_hits = sum(1 for r in successful_results if r.cache_hit)
        cache_hit_rate = (cache_hits / len(successful_results)) * 100
        
        # Model distribution
        model_distribution = {}
        for result in successful_results:
            model = result.model_used
            model_distribution[model] = model_distribution.get(model, 0) + 1
        
        # Requests per second
        rps = len(results) / total_time if total_time > 0 else 0
        
        # Error rate
        error_rate = (len(failed_results) / len(results)) * 100
        
        return LoadTestSummary(
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            total_cost=total_cost,
            constitutional_compliance_rate=compliance_rate,
            cache_hit_rate=cache_hit_rate,
            requests_per_second=rps,
            model_distribution=model_distribution,
            error_rate=error_rate
        )

    def _analyze_model_performance(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Analyze performance by model type."""

        model_stats = {}
        successful_results = [r for r in results if r.success]

        for result in successful_results:
            model = result.model_used
            if model not in model_stats:
                model_stats[model] = {
                    "requests": 0,
                    "response_times": [],
                    "costs": [],
                    "compliance_count": 0,
                    "cache_hits": 0
                }

            stats = model_stats[model]
            stats["requests"] += 1
            stats["response_times"].append(result.response_time_ms)
            stats["costs"].append(result.cost_estimate)
            if result.constitutional_compliance:
                stats["compliance_count"] += 1
            if result.cache_hit:
                stats["cache_hits"] += 1

        # Calculate aggregated stats
        model_performance = {}
        for model, stats in model_stats.items():
            if stats["requests"] > 0:
                model_performance[model] = {
                    "total_requests": stats["requests"],
                    "avg_response_time_ms": statistics.mean(stats["response_times"]),
                    "p95_response_time_ms": statistics.quantiles(stats["response_times"], n=20)[18] if len(stats["response_times"]) > 20 else max(stats["response_times"]),
                    "total_cost": sum(stats["costs"]),
                    "avg_cost_per_request": statistics.mean(stats["costs"]) if stats["costs"] else 0,
                    "compliance_rate": (stats["compliance_count"] / stats["requests"]) * 100,
                    "cache_hit_rate": (stats["cache_hits"] / stats["requests"]) * 100
                }

        return model_performance

    def _analyze_cost_performance(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Analyze cost performance and savings."""

        successful_results = [r for r in results if r.success]

        # Calculate cost by model
        model_costs = {}
        for result in successful_results:
            model = result.model_used
            if model not in model_costs:
                model_costs[model] = []
            model_costs[model].append(result.cost_estimate)

        # Calculate potential savings
        deepseek_costs = model_costs.get("deepseek/deepseek-r1-0528:free", [])
        flash_full_costs = model_costs.get("google/gemini-2.5-flash", [])

        total_deepseek_cost = sum(deepseek_costs)
        total_flash_full_cost = sum(flash_full_costs)

        # Estimate savings if all requests used DeepSeek R1
        total_requests = len(successful_results)
        deepseek_requests = len(deepseek_costs)

        if deepseek_requests > 0:
            avg_deepseek_cost = total_deepseek_cost / deepseek_requests
            potential_total_deepseek_cost = avg_deepseek_cost * total_requests

            actual_total_cost = sum(r.cost_estimate for r in successful_results)
            potential_savings = actual_total_cost - potential_total_deepseek_cost
            savings_percent = (potential_savings / actual_total_cost) * 100 if actual_total_cost > 0 else 0
        else:
            potential_savings = 0
            savings_percent = 0

        return {
            "total_cost": sum(r.cost_estimate for r in successful_results),
            "cost_by_model": {model: sum(costs) for model, costs in model_costs.items()},
            "avg_cost_per_request": statistics.mean([r.cost_estimate for r in successful_results]) if successful_results else 0,
            "potential_deepseek_savings": potential_savings,
            "potential_savings_percent": savings_percent,
            "cost_distribution": {
                model: {
                    "total": sum(costs),
                    "avg": statistics.mean(costs) if costs else 0,
                    "requests": len(costs)
                } for model, costs in model_costs.items()
            }
        }

    def _analyze_compliance_performance(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Analyze constitutional compliance performance."""

        successful_results = [r for r in results if r.success]

        # Overall compliance
        compliant_count = sum(1 for r in successful_results if r.constitutional_compliance)
        total_count = len(successful_results)
        overall_compliance_rate = (compliant_count / total_count) * 100 if total_count > 0 else 0

        # Compliance by model
        model_compliance = {}
        for result in successful_results:
            model = result.model_used
            if model not in model_compliance:
                model_compliance[model] = {"compliant": 0, "total": 0}

            model_compliance[model]["total"] += 1
            if result.constitutional_compliance:
                model_compliance[model]["compliant"] += 1

        # Calculate compliance rates by model
        compliance_by_model = {}
        for model, stats in model_compliance.items():
            compliance_by_model[model] = {
                "compliance_rate": (stats["compliant"] / stats["total"]) * 100,
                "compliant_requests": stats["compliant"],
                "total_requests": stats["total"]
            }

        # Confidence score analysis
        confidence_scores = [r.confidence_score for r in successful_results]
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0

        return {
            "overall_compliance_rate": overall_compliance_rate,
            "compliant_requests": compliant_count,
            "total_requests": total_count,
            "compliance_by_model": compliance_by_model,
            "avg_confidence_score": avg_confidence,
            "meets_95_target": overall_compliance_rate >= 95.0
        }

    def _analyze_cache_performance(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Analyze cache performance."""

        successful_results = [r for r in results if r.success]

        cache_hits = sum(1 for r in successful_results if r.cache_hit)
        total_requests = len(successful_results)
        cache_hit_rate = (cache_hits / total_requests) * 100 if total_requests > 0 else 0

        # Cache performance by model
        model_cache_stats = {}
        for result in successful_results:
            model = result.model_used
            if model not in model_cache_stats:
                model_cache_stats[model] = {"hits": 0, "total": 0}

            model_cache_stats[model]["total"] += 1
            if result.cache_hit:
                model_cache_stats[model]["hits"] += 1

        cache_by_model = {}
        for model, stats in model_cache_stats.items():
            cache_by_model[model] = {
                "hit_rate": (stats["hits"] / stats["total"]) * 100,
                "hits": stats["hits"],
                "total": stats["total"]
            }

        return {
            "overall_cache_hit_rate": cache_hit_rate,
            "cache_hits": cache_hits,
            "total_requests": total_requests,
            "cache_by_model": cache_by_model,
            "meets_80_target": cache_hit_rate >= 80.0
        }

    def _generate_recommendations(self, summary: LoadTestSummary) -> List[str]:
        """Generate performance recommendations based on test results."""

        recommendations = []

        # Response time recommendations
        if summary.avg_response_time_ms > 2000:
            recommendations.append(f"Average response time ({summary.avg_response_time_ms:.1f}ms) exceeds 2s target - consider cache optimization")

        if summary.p99_response_time_ms > 5000:
            recommendations.append(f"P99 response time ({summary.p99_response_time_ms:.1f}ms) is high - investigate performance bottlenecks")

        # Error rate recommendations
        if summary.error_rate > 5:
            recommendations.append(f"Error rate ({summary.error_rate:.1f}%) exceeds 5% threshold - investigate system stability")

        # Compliance recommendations
        if summary.constitutional_compliance_rate < 95:
            recommendations.append(f"Constitutional compliance ({summary.constitutional_compliance_rate:.1f}%) below 95% target - review compliance logic")

        # Cache recommendations
        if summary.cache_hit_rate < 80:
            recommendations.append(f"Cache hit rate ({summary.cache_hit_rate:.1f}%) below 80% target - optimize cache strategy")

        # Model distribution recommendations
        deepseek_usage = summary.model_distribution.get("deepseek/deepseek-r1-0528:free", 0)
        total_requests = summary.successful_requests
        deepseek_percentage = (deepseek_usage / total_requests) * 100 if total_requests > 0 else 0

        if deepseek_percentage < 30:
            recommendations.append(f"DeepSeek R1 usage ({deepseek_percentage:.1f}%) is low - consider routing more requests for cost savings")

        # Performance recommendations
        if summary.requests_per_second < 10:
            recommendations.append(f"Throughput ({summary.requests_per_second:.1f} RPS) is low - consider scaling improvements")

        if not recommendations:
            recommendations.append("System performance is excellent - all targets met!")

        return recommendations

    def print_load_test_report(self, report: Dict[str, Any]):
        """Print formatted load test report."""

        print("\n" + "=" * 80)
        print("COMPREHENSIVE LOAD TEST REPORT - ACGS-PGP MULTIMODAL AI")
        print("=" * 80)

        info = report["test_info"]
        summary = report["performance_summary"]

        print(f"Timestamp: {info['timestamp']}")
        print(f"Duration: {info['duration_seconds']:.1f} seconds")
        print(f"Target Requests: {info['target_concurrent_requests']}")
        print(f"Processed Requests: {info['actual_requests_processed']}")
        print(f"Constitutional Hash: {info['constitutional_hash']}")

        print(f"\n📊 PERFORMANCE SUMMARY")
        print(f"Success Rate: {((summary['successful_requests'] / summary['total_requests']) * 100):.1f}%")
        print(f"Requests/Second: {summary['requests_per_second']:.1f}")
        print(f"Avg Response Time: {summary['avg_response_time_ms']:.1f}ms")
        print(f"P95 Response Time: {summary['p95_response_time_ms']:.1f}ms")
        print(f"P99 Response Time: {summary['p99_response_time_ms']:.1f}ms")

        print(f"\n💰 COST ANALYSIS")
        cost_analysis = report["cost_analysis"]
        print(f"Total Cost: ${cost_analysis['total_cost']:.6f}")
        print(f"Avg Cost/Request: ${cost_analysis['avg_cost_per_request']:.6f}")
        print(f"Potential Savings: {cost_analysis['potential_savings_percent']:.1f}%")

        print(f"\n🏛️ CONSTITUTIONAL COMPLIANCE")
        compliance = report["compliance_analysis"]
        print(f"Compliance Rate: {compliance['overall_compliance_rate']:.1f}%")
        print(f"Meets 95% Target: {'✅' if compliance['meets_95_target'] else '❌'}")
        print(f"Avg Confidence: {compliance['avg_confidence_score']:.2f}")

        print(f"\n💾 CACHE PERFORMANCE")
        cache = report["cache_analysis"]
        print(f"Cache Hit Rate: {cache['overall_cache_hit_rate']:.1f}%")
        print(f"Meets 80% Target: {'✅' if cache['meets_80_target'] else '❌'}")

        print(f"\n🤖 MODEL DISTRIBUTION")
        for model, count in summary['model_distribution'].items():
            percentage = (count / summary['successful_requests']) * 100
            print(f"  {model}: {count} requests ({percentage:.1f}%)")

        print(f"\n🎯 RECOMMENDATIONS")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 80)


async def main():
    """Main execution function."""

    # Initialize load tester
    tester = ComprehensiveLoadTester()

    # Execute load test
    print("🚀 Starting Comprehensive Load Test...")
    report = await tester.execute_load_test(
        concurrent_requests=1000,  # 1000 concurrent requests
        duration_seconds=300       # 5 minutes max
    )

    # Print report
    tester.print_load_test_report(report)

    # Save detailed report
    output_dir = Path("reports/load_testing")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"comprehensive_load_test_{timestamp}.json"

    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Return exit code based on results
    summary = report["performance_summary"]
    success_rate = (summary["successful_requests"] / summary["total_requests"]) * 100
    meets_targets = (
        summary["avg_response_time_ms"] < 2000 and
        summary["error_rate"] < 5 and
        success_rate > 90
    )

    return 0 if meets_targets else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
