"""
Advanced Multi-Tenant Architecture Optimization System

This module implements advanced optimization for multi-tenant architecture with:
- Advanced isolation patterns and security
- Tenant-specific performance tuning
- Dynamic resource allocation optimization
- Intelligent tenant placement and scaling

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class TenantTier(str, Enum):
    """Enhanced tenant service tiers."""
    BASIC = "basic"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"
    CONSTITUTIONAL = "constitutional"
    PREMIUM = "premium"


class IsolationLevel(str, Enum):
    """Tenant isolation levels."""
    SHARED = "shared"
    DEDICATED_PROCESS = "dedicated_process"
    DEDICATED_INSTANCE = "dedicated_instance"
    DEDICATED_CLUSTER = "dedicated_cluster"


class ResourceType(str, Enum):
    """Resource types for allocation."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE_CONNECTIONS = "database_connections"
    CACHE_MEMORY = "cache_memory"


@dataclass
class TenantResourceLimits:
    """Resource limits for a tenant."""
    tenant_id: str
    tier: TenantTier
    cpu_cores: float
    memory_gb: float
    storage_gb: float
    network_mbps: float
    max_db_connections: int
    cache_memory_mb: int
    max_requests_per_second: int
    max_concurrent_users: int
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class TenantPerformanceProfile:
    """Performance profile for tenant optimization."""
    tenant_id: str
    avg_response_time_ms: float
    p99_response_time_ms: float
    throughput_rps: float
    cpu_utilization: float
    memory_utilization: float
    cache_hit_rate: float
    error_rate: float
    peak_usage_hours: List[int]
    seasonal_patterns: Dict[str, float]
    constitutional_compliance_score: float
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class IsolationPattern:
    """Advanced isolation pattern configuration."""
    pattern_id: str
    name: str
    isolation_level: IsolationLevel
    security_features: List[str]
    performance_overhead: float
    resource_efficiency: float
    compliance_score: float
    suitable_tiers: List[TenantTier]
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class ResourceAllocationStrategy:
    """Resource allocation strategy for tenants."""
    strategy_id: str
    name: str
    allocation_algorithm: str
    rebalancing_frequency: str
    performance_weight: float
    cost_weight: float
    isolation_weight: float
    constitutional_compliance_weight: float
    constitutional_hash: str = CONSTITUTIONAL_HASH


class AdvancedIsolationManager:
    """Manages advanced tenant isolation patterns."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Define advanced isolation patterns
        self.isolation_patterns = {
            "shared_optimized": IsolationPattern(
                pattern_id="shared_opt",
                name="Shared Optimized",
                isolation_level=IsolationLevel.SHARED,
                security_features=["rls", "namespace_isolation", "rate_limiting"],
                performance_overhead=0.05,
                resource_efficiency=0.95,
                compliance_score=0.85,
                suitable_tiers=[TenantTier.BASIC, TenantTier.STANDARD]
            ),
            "process_isolated": IsolationPattern(
                pattern_id="proc_iso",
                name="Process Isolated",
                isolation_level=IsolationLevel.DEDICATED_PROCESS,
                security_features=["process_isolation", "memory_protection", "cpu_quotas"],
                performance_overhead=0.15,
                resource_efficiency=0.80,
                compliance_score=0.92,
                suitable_tiers=[TenantTier.STANDARD, TenantTier.ENTERPRISE]
            ),
            "instance_dedicated": IsolationPattern(
                pattern_id="inst_ded",
                name="Instance Dedicated",
                isolation_level=IsolationLevel.DEDICATED_INSTANCE,
                security_features=["vm_isolation", "network_segmentation", "dedicated_storage"],
                performance_overhead=0.25,
                resource_efficiency=0.70,
                compliance_score=0.96,
                suitable_tiers=[TenantTier.ENTERPRISE, TenantTier.CONSTITUTIONAL]
            ),
            "cluster_dedicated": IsolationPattern(
                pattern_id="clust_ded",
                name="Cluster Dedicated",
                isolation_level=IsolationLevel.DEDICATED_CLUSTER,
                security_features=["cluster_isolation", "dedicated_infrastructure", "air_gapped"],
                performance_overhead=0.35,
                resource_efficiency=0.60,
                compliance_score=0.99,
                suitable_tiers=[TenantTier.CONSTITUTIONAL, TenantTier.PREMIUM]
            )
        }
        
        logger.info("Initialized Advanced Isolation Manager")

    def select_optimal_isolation_pattern(
        self, 
        tenant_tier: TenantTier,
        performance_requirements: Dict[str, float],
        compliance_requirements: float
    ) -> IsolationPattern:
        """Select optimal isolation pattern for tenant."""
        
        suitable_patterns = [
            pattern for pattern in self.isolation_patterns.values()
            if tenant_tier in pattern.suitable_tiers
        ]
        
        if not suitable_patterns:
            # Fallback to shared optimized
            return self.isolation_patterns["shared_optimized"]
        
        # Score patterns based on requirements
        best_pattern = None
        best_score = 0.0
        
        for pattern in suitable_patterns:
            # Calculate composite score
            performance_score = 1.0 - pattern.performance_overhead
            efficiency_score = pattern.resource_efficiency
            compliance_score = pattern.compliance_score
            
            # Weight based on requirements
            composite_score = (
                performance_score * performance_requirements.get("performance_weight", 0.3) +
                efficiency_score * performance_requirements.get("efficiency_weight", 0.3) +
                compliance_score * performance_requirements.get("compliance_weight", 0.4)
            )
            
            # Bonus for meeting compliance requirements
            if pattern.compliance_score >= compliance_requirements:
                composite_score += 0.1
            
            if composite_score > best_score:
                best_score = composite_score
                best_pattern = pattern
        
        return best_pattern or self.isolation_patterns["shared_optimized"]

    def get_isolation_recommendations(
        self, 
        tenant_profiles: List[TenantPerformanceProfile]
    ) -> Dict[str, Dict[str, Any]]:
        """Get isolation recommendations for multiple tenants."""
        
        recommendations = {}
        
        for profile in tenant_profiles:
            # Determine tier based on performance profile
            tier = self._infer_tenant_tier(profile)
            
            # Performance requirements based on profile
            perf_requirements = {
                "performance_weight": 0.4 if profile.p99_response_time_ms > 100 else 0.3,
                "efficiency_weight": 0.3,
                "compliance_weight": 0.5 if profile.constitutional_compliance_score > 0.95 else 0.3
            }
            
            # Select optimal pattern
            optimal_pattern = self.select_optimal_isolation_pattern(
                tier, perf_requirements, profile.constitutional_compliance_score
            )
            
            recommendations[profile.tenant_id] = {
                "current_tier": tier,
                "recommended_pattern": optimal_pattern.__dict__,
                "performance_impact": optimal_pattern.performance_overhead,
                "resource_efficiency": optimal_pattern.resource_efficiency,
                "compliance_improvement": max(0, optimal_pattern.compliance_score - profile.constitutional_compliance_score),
                "constitutional_hash": self.constitutional_hash
            }
        
        return recommendations

    def _infer_tenant_tier(self, profile: TenantPerformanceProfile) -> TenantTier:
        """Infer tenant tier from performance profile."""
        
        if profile.constitutional_compliance_score > 0.98:
            return TenantTier.CONSTITUTIONAL
        elif profile.throughput_rps > 1000 or profile.p99_response_time_ms < 10:
            return TenantTier.ENTERPRISE
        elif profile.throughput_rps > 100:
            return TenantTier.STANDARD
        else:
            return TenantTier.BASIC


class DynamicResourceAllocator:
    """Manages dynamic resource allocation for tenants."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Resource allocation strategies
        self.allocation_strategies = {
            "performance_optimized": ResourceAllocationStrategy(
                strategy_id="perf_opt",
                name="Performance Optimized",
                allocation_algorithm="priority_based",
                rebalancing_frequency="real_time",
                performance_weight=0.5,
                cost_weight=0.2,
                isolation_weight=0.2,
                constitutional_compliance_weight=0.1
            ),
            "cost_optimized": ResourceAllocationStrategy(
                strategy_id="cost_opt",
                name="Cost Optimized",
                allocation_algorithm="bin_packing",
                rebalancing_frequency="hourly",
                performance_weight=0.2,
                cost_weight=0.5,
                isolation_weight=0.2,
                constitutional_compliance_weight=0.1
            ),
            "compliance_first": ResourceAllocationStrategy(
                strategy_id="comp_first",
                name="Compliance First",
                allocation_algorithm="constitutional_priority",
                rebalancing_frequency="continuous",
                performance_weight=0.2,
                cost_weight=0.1,
                isolation_weight=0.3,
                constitutional_compliance_weight=0.4
            )
        }
        
        logger.info("Initialized Dynamic Resource Allocator")

    def calculate_optimal_allocation(
        self,
        tenant_profiles: List[TenantPerformanceProfile],
        available_resources: Dict[ResourceType, float],
        strategy: str = "performance_optimized"
    ) -> Dict[str, TenantResourceLimits]:
        """Calculate optimal resource allocation for tenants."""
        
        allocation_strategy = self.allocation_strategies.get(strategy, 
                                                           self.allocation_strategies["performance_optimized"])
        
        # Sort tenants by priority
        prioritized_tenants = self._prioritize_tenants(tenant_profiles, allocation_strategy)
        
        # Allocate resources
        allocations = {}
        remaining_resources = available_resources.copy()
        
        for profile in prioritized_tenants:
            allocation = self._allocate_tenant_resources(
                profile, remaining_resources, allocation_strategy
            )
            
            allocations[profile.tenant_id] = allocation
            
            # Update remaining resources
            remaining_resources[ResourceType.CPU] -= allocation.cpu_cores
            remaining_resources[ResourceType.MEMORY] -= allocation.memory_gb
            remaining_resources[ResourceType.STORAGE] -= allocation.storage_gb
            remaining_resources[ResourceType.NETWORK] -= allocation.network_mbps
            remaining_resources[ResourceType.DATABASE_CONNECTIONS] -= allocation.max_db_connections
            remaining_resources[ResourceType.CACHE_MEMORY] -= allocation.cache_memory_mb
        
        return allocations

    def _prioritize_tenants(
        self, 
        profiles: List[TenantPerformanceProfile],
        strategy: ResourceAllocationStrategy
    ) -> List[TenantPerformanceProfile]:
        """Prioritize tenants based on allocation strategy."""
        
        def calculate_priority(profile: TenantPerformanceProfile) -> float:
            # Base priority factors
            performance_factor = 1.0 / max(profile.p99_response_time_ms, 1.0)
            compliance_factor = profile.constitutional_compliance_score
            utilization_factor = (profile.cpu_utilization + profile.memory_utilization) / 2
            
            # Weighted priority
            priority = (
                performance_factor * strategy.performance_weight +
                compliance_factor * strategy.constitutional_compliance_weight +
                utilization_factor * 0.3  # Resource efficiency
            )
            
            return priority
        
        return sorted(profiles, key=calculate_priority, reverse=True)

    def _allocate_tenant_resources(
        self,
        profile: TenantPerformanceProfile,
        available_resources: Dict[ResourceType, float],
        strategy: ResourceAllocationStrategy
    ) -> TenantResourceLimits:
        """Allocate resources for a specific tenant."""
        
        # Infer tier
        tier = self._infer_tier_from_profile(profile)
        
        # Base allocation based on tier
        base_allocations = self._get_base_allocation(tier)
        
        # Adjust based on performance profile and available resources
        cpu_cores = min(
            base_allocations["cpu"] * (1 + profile.cpu_utilization * 0.5),
            available_resources[ResourceType.CPU] * 0.3  # Max 30% of available
        )
        
        memory_gb = min(
            base_allocations["memory"] * (1 + profile.memory_utilization * 0.5),
            available_resources[ResourceType.MEMORY] * 0.3
        )
        
        storage_gb = min(
            base_allocations["storage"],
            available_resources[ResourceType.STORAGE] * 0.2
        )
        
        network_mbps = min(
            base_allocations["network"] * (1 + profile.throughput_rps / 1000),
            available_resources[ResourceType.NETWORK] * 0.25
        )
        
        max_db_connections = min(
            base_allocations["db_connections"],
            int(available_resources[ResourceType.DATABASE_CONNECTIONS] * 0.2)
        )
        
        cache_memory_mb = min(
            base_allocations["cache"] * (2.0 - profile.cache_hit_rate),  # More cache if low hit rate
            available_resources[ResourceType.CACHE_MEMORY] * 0.3
        )
        
        # Calculate RPS limit based on performance
        max_rps = int(profile.throughput_rps * 1.5)  # 50% headroom
        
        # Estimate concurrent users
        max_concurrent_users = max(10, int(profile.throughput_rps * 2))
        
        return TenantResourceLimits(
            tenant_id=profile.tenant_id,
            tier=tier,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            storage_gb=storage_gb,
            network_mbps=network_mbps,
            max_db_connections=max_db_connections,
            cache_memory_mb=int(cache_memory_mb),
            max_requests_per_second=max_rps,
            max_concurrent_users=max_concurrent_users
        )

    def _infer_tier_from_profile(self, profile: TenantPerformanceProfile) -> TenantTier:
        """Infer tenant tier from performance profile."""
        if profile.constitutional_compliance_score > 0.98:
            return TenantTier.CONSTITUTIONAL
        elif profile.throughput_rps > 1000:
            return TenantTier.ENTERPRISE
        elif profile.throughput_rps > 100:
            return TenantTier.STANDARD
        else:
            return TenantTier.BASIC

    def _get_base_allocation(self, tier: TenantTier) -> Dict[str, float]:
        """Get base resource allocation for tier."""
        allocations = {
            TenantTier.BASIC: {
                "cpu": 0.5, "memory": 1.0, "storage": 10.0, "network": 10.0,
                "db_connections": 5, "cache": 50
            },
            TenantTier.STANDARD: {
                "cpu": 2.0, "memory": 4.0, "storage": 50.0, "network": 50.0,
                "db_connections": 20, "cache": 200
            },
            TenantTier.ENTERPRISE: {
                "cpu": 8.0, "memory": 16.0, "storage": 200.0, "network": 200.0,
                "db_connections": 50, "cache": 500
            },
            TenantTier.CONSTITUTIONAL: {
                "cpu": 16.0, "memory": 32.0, "storage": 500.0, "network": 500.0,
                "db_connections": 100, "cache": 1000
            },
            TenantTier.PREMIUM: {
                "cpu": 32.0, "memory": 64.0, "storage": 1000.0, "network": 1000.0,
                "db_connections": 200, "cache": 2000
            }
        }
        
        return allocations.get(tier, allocations[TenantTier.BASIC])


class TenantPerformanceTuner:
    """Performs tenant-specific performance tuning."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        logger.info("Initialized Tenant Performance Tuner")

    def analyze_tenant_performance(
        self, 
        profile: TenantPerformanceProfile
    ) -> Dict[str, Any]:
        """Analyze tenant performance and identify optimization opportunities."""
        
        optimizations = []
        performance_score = 0.0
        
        # Analyze response time
        if profile.p99_response_time_ms > 100:
            optimizations.append({
                "type": "latency_optimization",
                "priority": "high",
                "recommendation": "Implement caching and database query optimization",
                "expected_improvement": "30-50% latency reduction"
            })
            performance_score += 0.2
        elif profile.p99_response_time_ms > 50:
            optimizations.append({
                "type": "latency_optimization",
                "priority": "medium",
                "recommendation": "Optimize critical path operations",
                "expected_improvement": "15-25% latency reduction"
            })
            performance_score += 0.1
        
        # Analyze cache performance
        if profile.cache_hit_rate < 0.8:
            optimizations.append({
                "type": "cache_optimization",
                "priority": "high",
                "recommendation": "Increase cache size and optimize cache keys",
                "expected_improvement": f"Improve hit rate from {profile.cache_hit_rate:.1%} to 85%+"
            })
            performance_score += 0.3
        
        # Analyze resource utilization
        if profile.cpu_utilization > 0.8:
            optimizations.append({
                "type": "cpu_optimization",
                "priority": "high",
                "recommendation": "Scale CPU resources or optimize CPU-intensive operations",
                "expected_improvement": "Reduce CPU bottlenecks"
            })
            performance_score += 0.25
        
        if profile.memory_utilization > 0.8:
            optimizations.append({
                "type": "memory_optimization",
                "priority": "high",
                "recommendation": "Increase memory allocation or optimize memory usage",
                "expected_improvement": "Reduce memory pressure"
            })
            performance_score += 0.25
        
        # Analyze error rate
        if profile.error_rate > 0.01:  # > 1%
            optimizations.append({
                "type": "reliability_optimization",
                "priority": "critical",
                "recommendation": "Investigate and fix error sources",
                "expected_improvement": f"Reduce error rate from {profile.error_rate:.2%} to <0.5%"
            })
            performance_score += 0.4
        
        # Constitutional compliance optimization
        if profile.constitutional_compliance_score < 0.95:
            optimizations.append({
                "type": "compliance_optimization",
                "priority": "high",
                "recommendation": "Enhance constitutional compliance mechanisms",
                "expected_improvement": f"Improve compliance from {profile.constitutional_compliance_score:.1%} to 95%+"
            })
            performance_score += 0.3
        
        return {
            "tenant_id": profile.tenant_id,
            "performance_score": min(1.0, performance_score),
            "optimization_opportunities": optimizations,
            "priority_actions": [opt for opt in optimizations if opt["priority"] in ["critical", "high"]],
            "estimated_improvement_potential": min(50, len(optimizations) * 10),  # % improvement
            "constitutional_hash": self.constitutional_hash
        }

    def generate_tuning_recommendations(
        self, 
        profiles: List[TenantPerformanceProfile]
    ) -> Dict[str, Any]:
        """Generate comprehensive tuning recommendations for multiple tenants."""
        
        tenant_analyses = {}
        global_patterns = {
            "common_issues": {},
            "optimization_priorities": {},
            "resource_trends": {}
        }
        
        for profile in profiles:
            analysis = self.analyze_tenant_performance(profile)
            tenant_analyses[profile.tenant_id] = analysis
            
            # Track global patterns
            for opt in analysis["optimization_opportunities"]:
                opt_type = opt["type"]
                global_patterns["common_issues"][opt_type] = global_patterns["common_issues"].get(opt_type, 0) + 1
        
        # Identify most common issues
        most_common_issues = sorted(
            global_patterns["common_issues"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "tenant_analyses": tenant_analyses,
            "global_recommendations": {
                "most_common_issues": most_common_issues,
                "infrastructure_recommendations": self._generate_infrastructure_recommendations(profiles),
                "constitutional_compliance_status": self._assess_global_compliance(profiles)
            },
            "constitutional_hash": self.constitutional_hash
        }

    def _generate_infrastructure_recommendations(
        self, 
        profiles: List[TenantPerformanceProfile]
    ) -> List[Dict[str, Any]]:
        """Generate infrastructure-level recommendations."""
        
        recommendations = []
        
        # Analyze aggregate metrics
        avg_cpu = np.mean([p.cpu_utilization for p in profiles])
        avg_memory = np.mean([p.memory_utilization for p in profiles])
        avg_cache_hit = np.mean([p.cache_hit_rate for p in profiles])
        
        if avg_cpu > 0.7:
            recommendations.append({
                "type": "infrastructure_scaling",
                "component": "cpu",
                "recommendation": "Consider adding more CPU capacity to the cluster",
                "urgency": "high" if avg_cpu > 0.8 else "medium"
            })
        
        if avg_memory > 0.7:
            recommendations.append({
                "type": "infrastructure_scaling",
                "component": "memory",
                "recommendation": "Consider adding more memory capacity to the cluster",
                "urgency": "high" if avg_memory > 0.8 else "medium"
            })
        
        if avg_cache_hit < 0.8:
            recommendations.append({
                "type": "infrastructure_optimization",
                "component": "cache",
                "recommendation": "Optimize global caching strategy and increase cache capacity",
                "urgency": "medium"
            })
        
        return recommendations

    def _assess_global_compliance(
        self, 
        profiles: List[TenantPerformanceProfile]
    ) -> Dict[str, Any]:
        """Assess global constitutional compliance status."""
        
        compliance_scores = [p.constitutional_compliance_score for p in profiles]
        
        return {
            "average_compliance": np.mean(compliance_scores),
            "min_compliance": np.min(compliance_scores),
            "max_compliance": np.max(compliance_scores),
            "compliant_tenants": sum(1 for score in compliance_scores if score >= 0.95),
            "total_tenants": len(profiles),
            "compliance_rate": sum(1 for score in compliance_scores if score >= 0.95) / len(profiles),
            "needs_attention": [
                profiles[i].tenant_id for i, score in enumerate(compliance_scores) 
                if score < 0.95
            ]
        }


class MultiTenantArchitectureOptimizer:
    """Main optimizer for multi-tenant architecture."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Initialize components
        self.isolation_manager = AdvancedIsolationManager()
        self.resource_allocator = DynamicResourceAllocator()
        self.performance_tuner = TenantPerformanceTuner()
        
        logger.info("Initialized Multi-Tenant Architecture Optimizer")

    async def optimize_architecture(
        self,
        tenant_profiles: List[TenantPerformanceProfile],
        available_resources: Dict[ResourceType, float],
        optimization_strategy: str = "performance_optimized"
    ) -> Dict[str, Any]:
        """Perform comprehensive multi-tenant architecture optimization."""
        
        logger.info("🚀 Starting Multi-Tenant Architecture Optimization")
        logger.info(f"📊 Optimizing {len(tenant_profiles)} tenants")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        start_time = time.time()
        
        # Step 1: Isolation pattern optimization
        logger.info("🔒 Optimizing isolation patterns...")
        isolation_recommendations = self.isolation_manager.get_isolation_recommendations(tenant_profiles)
        
        # Step 2: Resource allocation optimization
        logger.info("📊 Optimizing resource allocation...")
        resource_allocations = self.resource_allocator.calculate_optimal_allocation(
            tenant_profiles, available_resources, optimization_strategy
        )
        
        # Step 3: Performance tuning recommendations
        logger.info("⚡ Generating performance tuning recommendations...")
        tuning_recommendations = self.performance_tuner.generate_tuning_recommendations(tenant_profiles)
        
        # Step 4: Generate comprehensive optimization report
        optimization_time = time.time() - start_time
        
        optimization_report = {
            "optimization_summary": {
                "total_tenants": len(tenant_profiles),
                "optimization_time_seconds": optimization_time,
                "strategy_used": optimization_strategy,
                "constitutional_hash": self.constitutional_hash
            },
            "isolation_optimization": {
                "recommendations": isolation_recommendations,
                "patterns_applied": len(set(rec["recommended_pattern"]["pattern_id"] 
                                          for rec in isolation_recommendations.values()))
            },
            "resource_optimization": {
                "allocations": {tid: alloc.__dict__ for tid, alloc in resource_allocations.items()},
                "total_cpu_allocated": sum(alloc.cpu_cores for alloc in resource_allocations.values()),
                "total_memory_allocated": sum(alloc.memory_gb for alloc in resource_allocations.values()),
                "resource_utilization": self._calculate_resource_utilization(resource_allocations, available_resources)
            },
            "performance_optimization": tuning_recommendations,
            "constitutional_compliance": {
                "average_compliance": np.mean([p.constitutional_compliance_score for p in tenant_profiles]),
                "compliant_tenants": sum(1 for p in tenant_profiles if p.constitutional_compliance_score >= 0.95),
                "optimization_impact": self._estimate_compliance_improvement(isolation_recommendations)
            }
        }
        
        logger.info(f"✅ Multi-Tenant Architecture Optimization completed in {optimization_time:.2f} seconds")
        logger.info(f"📊 Resource utilization: {optimization_report['resource_optimization']['resource_utilization']:.1%}")
        logger.info(f"🔒 Average compliance: {optimization_report['constitutional_compliance']['average_compliance']:.2%}")
        
        return optimization_report

    def _calculate_resource_utilization(
        self, 
        allocations: Dict[str, TenantResourceLimits],
        available_resources: Dict[ResourceType, float]
    ) -> float:
        """Calculate overall resource utilization."""
        
        total_cpu_allocated = sum(alloc.cpu_cores for alloc in allocations.values())
        total_memory_allocated = sum(alloc.memory_gb for alloc in allocations.values())
        
        cpu_utilization = total_cpu_allocated / available_resources[ResourceType.CPU]
        memory_utilization = total_memory_allocated / available_resources[ResourceType.MEMORY]
        
        return (cpu_utilization + memory_utilization) / 2

    def _estimate_compliance_improvement(
        self, 
        isolation_recommendations: Dict[str, Dict[str, Any]]
    ) -> float:
        """Estimate compliance improvement from isolation recommendations."""
        
        total_improvement = sum(
            rec.get("compliance_improvement", 0) 
            for rec in isolation_recommendations.values()
        )
        
        return total_improvement / len(isolation_recommendations) if isolation_recommendations else 0.0
