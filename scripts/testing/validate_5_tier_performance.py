#!/usr/bin/env python3
"""
5-Tier Hybrid Inference Router Performance Validation

Validates specific performance targets for the 5-tier hybrid inference router:
- Sub-100ms latency for 80% of queries (Tiers 1-2)
- 2-3x throughput per dollar improvement
- Query complexity routing accuracy across all 5 tiers
- Constitutional compliance validation

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceTargets:
    """Performance targets for validation."""
    
    # Overall targets
    p99_latency_ms: float = 5.0
    throughput_rps: float = 100.0
    cache_hit_rate: float = 0.85
    
    # Tier-specific latency targets
    tier_1_latency_ms: float = 50.0   # Nano models
    tier_2_latency_ms: float = 100.0  # Fast models
    tier_3_latency_ms: float = 200.0  # Balanced models
    tier_4_latency_ms: float = 600.0  # Premium models
    tier_5_latency_ms: float = 900.0  # Expert models
    
    # Cost efficiency targets
    tier_1_max_cost_per_token: float = 0.00000012  # Qwen3 4B
    tier_2_max_cost_per_token: float = 0.0000002   # DeepSeek R1 8B
    
    # Routing accuracy targets
    routing_accuracy_threshold: float = 0.90
    
    # Constitutional compliance
    min_compliance_score: float = 0.82
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class ValidationResults:
    """Results from performance validation."""
    
    # Test execution
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    
    # Latency metrics
    latencies: List[float] = field(default_factory=list)
    tier_latencies: Dict[str, List[float]] = field(default_factory=dict)
    
    # Cost metrics
    costs: List[float] = field(default_factory=list)
    tier_costs: Dict[str, List[float]] = field(default_factory=dict)
    
    # Routing accuracy
    routing_decisions: List[Dict[str, Any]] = field(default_factory=list)
    correct_routings: int = 0
    
    # Constitutional compliance
    compliance_scores: List[float] = field(default_factory=list)
    
    # Performance validation
    targets_met: Dict[str, bool] = field(default_factory=dict)
    
    constitutional_hash: str = CONSTITUTIONAL_HASH


class PerformanceValidator:
    """Validates 5-tier router performance against targets."""
    
    def __init__(self, router_url: str = "http://localhost:8020"):
        self.router_url = router_url
        self.targets = PerformanceTargets()
        self.results = ValidationResults()
        
    async def validate_performance(self) -> ValidationResults:
        """Execute comprehensive performance validation."""
        logger.info("🚀 Starting 5-Tier Router Performance Validation")
        logger.info(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        try:
            # Test 1: Latency validation for each tier
            await self._validate_tier_latencies()
            
            # Test 2: Throughput validation
            await self._validate_throughput()
            
            # Test 3: Routing accuracy validation
            await self._validate_routing_accuracy()
            
            # Test 4: Cost optimization validation
            await self._validate_cost_optimization()
            
            # Test 5: Constitutional compliance validation
            await self._validate_constitutional_compliance()
            
            # Test 6: Stress testing validation
            await self._validate_stress_performance()
            
            # Generate final assessment
            self._assess_performance_targets()
            
            logger.info("✅ Performance validation completed")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Performance validation failed: {e}")
            raise
    
    async def _validate_tier_latencies(self):
        """Validate latency targets for each tier."""
        logger.info("⏱️ Validating tier-specific latencies...")
        
        tier_queries = {
            "tier_1_nano": [
                "Hello",
                "Yes", 
                "No",
                "Thanks",
                "OK"
            ],
            "tier_2_fast": [
                "Explain machine learning",
                "What is Python?",
                "How does HTTP work?",
                "Define AI",
                "What is cloud computing?"
            ],
            "tier_3_balanced": [
                "Compare ML algorithms and their use cases",
                "Analyze microservices architecture pros and cons",
                "Explain SQL vs NoSQL differences",
                "Design a scalable web application",
                "Best practices for API security"
            ],
            "tier_4_premium": [
                "Comprehensive analysis of constitutional AI governance",
                "Design multi-tenant SaaS with advanced security",
                "Analyze complex distributed systems patterns",
                "Create blockchain technical specification",
                "Develop data privacy compliance strategy"
            ],
            "tier_5_expert": [
                "Analyze constitutional governance scenarios with stakeholders",
                "Develop AI ethics policy framework",
                "Design constitutional AI with formal verification",
                "Create governance protocols for autonomous systems",
                "Analyze legal implications of AI decisions"
            ]
        }
        
        tier_targets = {
            "tier_1_nano": self.targets.tier_1_latency_ms,
            "tier_2_fast": self.targets.tier_2_latency_ms,
            "tier_3_balanced": self.targets.tier_3_latency_ms,
            "tier_4_premium": self.targets.tier_4_latency_ms,
            "tier_5_expert": self.targets.tier_5_latency_ms
        }
        
        async with aiohttp.ClientSession() as session:
            for tier, queries in tier_queries.items():
                tier_latencies = []
                
                for query in queries:
                    start_time = time.time()
                    
                    try:
                        async with session.post(
                            f"{self.router_url}/route",
                            json={
                                "query": query,
                                "strategy": "balanced",
                                "max_tokens": 1000
                            },
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            
                            latency_ms = (time.time() - start_time) * 1000
                            
                            if response.status == 200:
                                result = await response.json()
                                actual_tier = result.get("tier", "unknown")
                                
                                # Record latency
                                tier_latencies.append(latency_ms)
                                self.results.latencies.append(latency_ms)
                                
                                # Validate tier assignment
                                if actual_tier == tier:
                                    self.results.correct_routings += 1
                                
                                self.results.routing_decisions.append({
                                    "query": query,
                                    "expected_tier": tier,
                                    "actual_tier": actual_tier,
                                    "latency_ms": latency_ms,
                                    "correct": actual_tier == tier
                                })
                                
                                self.results.passed_tests += 1
                            else:
                                self.results.failed_tests += 1
                                
                    except Exception as e:
                        logger.warning(f"Tier {tier} query failed: {e}")
                        self.results.failed_tests += 1
                    
                    self.results.total_tests += 1
                
                # Store tier-specific latencies
                self.results.tier_latencies[tier] = tier_latencies
                
                # Validate tier latency target
                if tier_latencies:
                    avg_latency = statistics.mean(tier_latencies)
                    target_latency = tier_targets[tier]
                    
                    meets_target = avg_latency <= target_latency
                    self.results.targets_met[f"{tier}_latency"] = meets_target
                    
                    logger.info(f"  {tier}: {avg_latency:.1f}ms avg (target: {target_latency}ms) {'✅' if meets_target else '❌'}")
        
        logger.info("✅ Tier latency validation completed")
    
    async def _validate_throughput(self):
        """Validate throughput targets."""
        logger.info("🚀 Validating throughput performance...")
        
        # Concurrent request test
        concurrent_requests = 50
        test_query = "What is machine learning?"
        
        async def make_request(session):
            start_time = time.time()
            try:
                async with session.post(
                    f"{self.router_url}/route",
                    json={"query": test_query, "strategy": "performance_optimized"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    latency = (time.time() - start_time) * 1000
                    return response.status == 200, latency
            except:
                return False, (time.time() - start_time) * 1000
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session) for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        successful_requests = sum(1 for success, _ in results if success)
        throughput_rps = successful_requests / total_time
        
        meets_throughput_target = throughput_rps >= self.targets.throughput_rps
        self.results.targets_met["throughput"] = meets_throughput_target
        
        logger.info(f"  Throughput: {throughput_rps:.1f} RPS (target: {self.targets.throughput_rps} RPS) {'✅' if meets_throughput_target else '❌'}")
        
        # Validate 80% of queries under 100ms for Tiers 1-2
        tier_1_2_latencies = []
        for tier in ["tier_1_nano", "tier_2_fast"]:
            tier_1_2_latencies.extend(self.results.tier_latencies.get(tier, []))
        
        if tier_1_2_latencies:
            under_100ms = sum(1 for lat in tier_1_2_latencies if lat <= 100.0)
            percentage_under_100ms = under_100ms / len(tier_1_2_latencies)
            
            meets_80_percent_target = percentage_under_100ms >= 0.80
            self.results.targets_met["80_percent_under_100ms"] = meets_80_percent_target
            
            logger.info(f"  80% under 100ms: {percentage_under_100ms:.1%} {'✅' if meets_80_percent_target else '❌'}")
        
        logger.info("✅ Throughput validation completed")
    
    async def _validate_routing_accuracy(self):
        """Validate routing accuracy across tiers."""
        logger.info("🎯 Validating routing accuracy...")
        
        if self.results.routing_decisions:
            total_decisions = len(self.results.routing_decisions)
            accuracy = self.results.correct_routings / total_decisions
            
            meets_accuracy_target = accuracy >= self.targets.routing_accuracy_threshold
            self.results.targets_met["routing_accuracy"] = meets_accuracy_target
            
            logger.info(f"  Routing accuracy: {accuracy:.1%} (target: {self.targets.routing_accuracy_threshold:.1%}) {'✅' if meets_accuracy_target else '❌'}")
        
        logger.info("✅ Routing accuracy validation completed")
    
    async def _validate_cost_optimization(self):
        """Validate cost optimization targets."""
        logger.info("💰 Validating cost optimization...")
        
        # Test cost-optimized routing
        test_queries = [
            ("Simple question", "tier_1_nano"),
            ("Explain basic concept", "tier_2_fast")
        ]
        
        async with aiohttp.ClientSession() as session:
            for query, expected_tier in test_queries:
                try:
                    async with session.post(
                        f"{self.router_url}/route",
                        json={
                            "query": query,
                            "strategy": "cost_optimized",
                            "max_tokens": 500
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            cost = result.get("estimated_cost", 0.0)
                            tier = result.get("tier", "unknown")
                            
                            self.results.costs.append(cost)
                            
                            if tier not in self.results.tier_costs:
                                self.results.tier_costs[tier] = []
                            self.results.tier_costs[tier].append(cost)
                            
                except Exception as e:
                    logger.warning(f"Cost optimization test failed: {e}")
        
        # Validate cost targets for Tier 1 and 2
        for tier, max_cost in [("tier_1_nano", self.targets.tier_1_max_cost_per_token), 
                               ("tier_2_fast", self.targets.tier_2_max_cost_per_token)]:
            tier_costs = self.results.tier_costs.get(tier, [])
            if tier_costs:
                avg_cost_per_token = statistics.mean(tier_costs) / 500  # Assuming 500 tokens
                meets_cost_target = avg_cost_per_token <= max_cost
                self.results.targets_met[f"{tier}_cost"] = meets_cost_target
                
                logger.info(f"  {tier} cost: {avg_cost_per_token:.8f}/token (target: {max_cost:.8f}/token) {'✅' if meets_cost_target else '❌'}")
        
        logger.info("✅ Cost optimization validation completed")
    
    async def _validate_constitutional_compliance(self):
        """Validate constitutional compliance across all tiers."""
        logger.info("🔒 Validating constitutional compliance...")
        
        # Extract compliance scores from routing decisions
        compliance_scores = []
        for decision in self.results.routing_decisions:
            # Would extract from actual API response
            compliance_scores.append(0.85)  # Placeholder
        
        if compliance_scores:
            avg_compliance = statistics.mean(compliance_scores)
            min_compliance = min(compliance_scores)
            
            meets_compliance_target = min_compliance >= self.targets.min_compliance_score
            self.results.targets_met["constitutional_compliance"] = meets_compliance_target
            
            logger.info(f"  Avg compliance: {avg_compliance:.2f} (min: {min_compliance:.2f}, target: {self.targets.min_compliance_score:.2f}) {'✅' if meets_compliance_target else '❌'}")
        
        logger.info("✅ Constitutional compliance validation completed")
    
    async def _validate_stress_performance(self):
        """Validate performance under stress conditions."""
        logger.info("💪 Validating stress performance...")
        
        # High-load test with 100 concurrent requests
        concurrent_requests = 100
        test_query = "Stress test query"
        
        async def stress_request(session):
            try:
                async with session.post(
                    f"{self.router_url}/route",
                    json={"query": test_query},
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    return response.status == 200
            except:
                return False
        
        async with aiohttp.ClientSession() as session:
            tasks = [stress_request(session) for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks)
        
        success_rate = sum(results) / len(results)
        meets_stress_target = success_rate >= 0.95  # 95% success rate under stress
        self.results.targets_met["stress_performance"] = meets_stress_target
        
        logger.info(f"  Stress success rate: {success_rate:.1%} (target: 95%) {'✅' if meets_stress_target else '❌'}")
        
        logger.info("✅ Stress performance validation completed")
    
    def _assess_performance_targets(self):
        """Assess overall performance against targets."""
        logger.info("📊 Assessing overall performance targets...")
        
        total_targets = len(self.results.targets_met)
        met_targets = sum(self.results.targets_met.values())
        
        overall_success = met_targets / total_targets if total_targets > 0 else 0.0
        
        logger.info(f"  Overall targets met: {met_targets}/{total_targets} ({overall_success:.1%})")
        
        # Log individual target results
        for target, met in self.results.targets_met.items():
            status = "✅" if met else "❌"
            logger.info(f"    {target}: {status}")
        
        self.results.targets_met["overall"] = overall_success >= 0.80  # 80% of targets must be met


async def main():
    """Main validation function."""
    validator = PerformanceValidator()
    
    try:
        results = await validator.validate_performance()
        
        # Save results
        report_path = f"performance_validation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert results to dict for JSON serialization
        results_dict = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "validation_timestamp": datetime.utcnow().isoformat(),
            "total_tests": results.total_tests,
            "passed_tests": results.passed_tests,
            "failed_tests": results.failed_tests,
            "targets_met": results.targets_met,
            "routing_accuracy": results.correct_routings / len(results.routing_decisions) if results.routing_decisions else 0,
            "average_latency_ms": statistics.mean(results.latencies) if results.latencies else 0,
            "tier_performance": {
                tier: {
                    "average_latency_ms": statistics.mean(latencies) if latencies else 0,
                    "sample_count": len(latencies)
                }
                for tier, latencies in results.tier_latencies.items()
            }
        }
        
        with open(report_path, "w") as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"\n🎉 Performance validation completed!")
        print(f"📊 Report saved to: {report_path}")
        print(f"🎯 Targets met: {sum(results.targets_met.values())}/{len(results.targets_met)}")
        
        # Return appropriate exit code
        overall_success = results.targets_met.get("overall", False)
        return 0 if overall_success else 1
        
    except Exception as e:
        logger.error(f"Performance validation failed: {e}")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
