"""
Optimized Performance Integration for Multi-Agent Coordinator
Constitutional Hash: cdd01ef066bc6cf2

High-performance monitoring and optimization with <5ms P99 latency targets,
connection pooling, batch operations, and intelligent coordination strategies.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

import redis.asyncio as redis

try:
    from ...shared.blackboard.optimized_blackboard_service import OptimizedBlackboardService, create_optimized_blackboard_service
    OPTIMIZED_BLACKBOARD_AVAILABLE = True
except ImportError:
    from ...shared.blackboard.blackboard_service import BlackboardService
    OPTIMIZED_BLACKBOARD_AVAILABLE = False

from ...shared.monitoring.enhanced_performance_monitor import EnhancedPerformanceMonitor
from ...shared.performance_monitoring import PerformanceMonitor

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class OptimizedCoordinationMetrics:
    """Enhanced metrics for coordination performance with sub-5ms tracking"""
    
    coordination_id: str
    start_time: float  # Use timestamps for higher precision
    end_time: Optional[float] = None
    task_count: int = 0
    agent_count: int = 0
    success_rate: float = 0.0
    p99_latency: float = 0.0
    avg_latency: float = 0.0
    constitutional_compliance: bool = True
    blackboard_operations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


class AgentCapabilityCache:
    """High-performance agent capability caching for fast task routing"""
    
    def __init__(self, max_size: int = 1000):
        self.capabilities: Dict[str, Set[str]] = {}
        self.task_type_agents: Dict[str, Set[str]] = defaultdict(set)
        self.agent_workload: Dict[str, int] = defaultdict(int)
        self.last_update = {}
        self.max_size = max_size
    
    def update_agent_capabilities(self, agent_id: str, capabilities: Set[str]) -> None:
        """Update agent capabilities with O(1) lookup optimization"""
        # Remove old mappings
        if agent_id in self.capabilities:
            for old_cap in self.capabilities[agent_id]:
                self.task_type_agents[old_cap].discard(agent_id)
        
        # Add new mappings
        self.capabilities[agent_id] = capabilities
        for capability in capabilities:
            self.task_type_agents[capability].add(agent_id)
        
        self.last_update[agent_id] = time.time()
    
    def get_capable_agents(self, task_type: str) -> List[str]:
        """Get agents capable of handling task type, sorted by workload"""
        capable_agents = list(self.task_type_agents.get(task_type, set()))
        
        # Sort by current workload (ascending)
        capable_agents.sort(key=lambda agent_id: self.agent_workload.get(agent_id, 0))
        return capable_agents
    
    def update_workload(self, agent_id: str, workload_delta: int) -> None:
        """Update agent workload for load balancing"""
        self.agent_workload[agent_id] = max(0, self.agent_workload.get(agent_id, 0) + workload_delta)


class OptimizedPerformanceIntegration:
    """
    High-performance monitoring and optimization for multi-agent coordination.
    
    Optimizations:
    - Sub-millisecond latency tracking
    - Batch operation monitoring
    - Intelligent agent routing
    - Connection pool monitoring
    - Cache hit rate optimization
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        
        # High-performance monitors
        self.performance_monitor = PerformanceMonitor()
        self.enhanced_monitor = EnhancedPerformanceMonitor()
        
        # Optimized storage with minimal overhead
        self.coordination_metrics: Dict[str, OptimizedCoordinationMetrics] = {}
        self.agent_performance: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))  # Reduced size for performance
        self.latency_samples = deque(maxlen=1000)  # For P99 calculation
        
        # Agent capability caching
        self.capability_cache = AgentCapabilityCache()
        
        # Performance targets (aggressive for optimization)
        self.coordination_latency_target = 5.0  # ms
        self.p99_latency_target = 5.0  # ms  
        self.throughput_target = 1000.0  # RPS
        self.success_rate_target = 0.99
        self.cache_hit_rate_target = 0.90
        
        # Connection pool for metrics storage
        self.redis_client: Optional[redis.Redis] = None
        
        # Optimized blackboard service
        self.blackboard_service: Optional[Any] = None
        
    async def initialize(self, blackboard_service: Optional[Any] = None) -> None:
        """Initialize optimized performance monitoring"""
        start_time = time.time()
        
        # Initialize Redis connection for high-performance metrics storage
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                max_connections=5,  # Small pool for metrics
                socket_keepalive=True,
                decode_responses=True
            )
            await self.redis_client.ping()
            
        except Exception as e:
            self.logger.warning(f"Redis metrics storage unavailable: {e}")
            self.redis_client = None
        
        # Initialize optimized blackboard if available
        if OPTIMIZED_BLACKBOARD_AVAILABLE and blackboard_service is None:
            try:
                self.blackboard_service = await create_optimized_blackboard_service(self.redis_url)
                self.logger.info("Using optimized blackboard service for performance integration")
            except Exception as e:
                self.logger.warning(f"Could not initialize optimized blackboard: {e}")
                self.blackboard_service = blackboard_service
        else:
            self.blackboard_service = blackboard_service
        
        initialization_time = (time.time() - start_time) * 1000
        self.logger.info(f"Optimized performance integration initialized in {initialization_time:.2f}ms")
    
    async def start_coordination_monitoring(self, coordination_id: str, agent_count: int, task_count: int) -> None:
        """Start high-precision coordination monitoring"""
        metrics = OptimizedCoordinationMetrics(
            coordination_id=coordination_id,
            start_time=time.time(),  # High precision timestamp
            agent_count=agent_count,
            task_count=task_count
        )
        self.coordination_metrics[coordination_id] = metrics
        
        # Update capability cache workload efficiently
        if agent_count > 0:
            # Use batch operation for workload updates
            batch_updates = []
            agents = self.capability_cache.get_capable_agents("coordination")
            for agent_id in agents[:agent_count]:
                batch_updates.append((agent_id, 1))
            
            for agent_id, delta in batch_updates:
                self.capability_cache.update_workload(agent_id, delta)
    
    async def record_agent_performance_batch(self, performance_records: List[Dict[str, Any]]) -> None:
        """Record multiple agent performance metrics in batch for efficiency"""
        current_time = time.time()
        
        # Batch process all records with minimal overhead
        for record in performance_records:
            agent_id = record['agent_id']
            latency = record['latency']
            success = record['success']
            task_type = record.get('task_type', 'unknown')
            
            # Minimal storage for performance - use shortened keys
            perf_data = {
                't': current_time,  # timestamp
                'l': latency,       # latency
                's': success,       # success
                'tt': task_type     # task_type
            }
            
            self.agent_performance[agent_id].append(perf_data)
            self.latency_samples.append(latency)
            
            # Update workload tracking
            self.capability_cache.update_workload(agent_id, -1 if success else 0)
        
        # Batch update enhanced monitor if available
        if hasattr(self.enhanced_monitor, 'record_batch_metrics'):
            await self.enhanced_monitor.record_batch_metrics('agent_performance', performance_records)
    
    async def record_blackboard_operation(self, coordination_id: str, operation_type: str, 
                                        latency: float, cache_hit: bool = False) -> None:
        """Record blackboard operation performance"""
        if coordination_id in self.coordination_metrics:
            metrics = self.coordination_metrics[coordination_id]
            metrics.blackboard_operations += 1
            
            if cache_hit:
                metrics.cache_hits += 1
            else:
                metrics.cache_misses += 1
        
        # Track latency for optimization
        self.latency_samples.append(latency)
    
    async def end_coordination_monitoring(self, coordination_id: str, success: bool) -> OptimizedCoordinationMetrics:
        """End monitoring with optimized metric calculation"""
        if coordination_id not in self.coordination_metrics:
            raise ValueError(f"Coordination {coordination_id} not found")
        
        metrics = self.coordination_metrics[coordination_id]
        metrics.end_time = time.time()
        
        # Calculate high-precision metrics
        duration_ms = (metrics.end_time - metrics.start_time) * 1000
        metrics.avg_latency = duration_ms
        
        # Calculate P99 latency efficiently
        if self.latency_samples:
            sorted_samples = sorted(list(self.latency_samples))
            p99_index = int(0.99 * len(sorted_samples))
            metrics.p99_latency = sorted_samples[min(p99_index, len(sorted_samples) - 1)]
        
        # Calculate cache hit rate
        total_ops = metrics.cache_hits + metrics.cache_misses
        cache_hit_rate = metrics.cache_hits / total_ops if total_ops > 0 else 0.0
        
        metrics.success_rate = 1.0 if success else 0.0
        
        # Batch update agent workloads
        workload_updates = []
        for i in range(metrics.agent_count):
            workload_updates.append((f"agent_{i}", -1))
        
        for agent_id, delta in workload_updates:
            self.capability_cache.update_workload(agent_id, delta)
        
        self.logger.debug(
            f"Coordination {coordination_id} completed: "
            f"{duration_ms:.2f}ms avg, {metrics.p99_latency:.2f}ms P99, "
            f"{cache_hit_rate*100:.1f}% cache hit rate"
        )
        
        return metrics
    
    async def get_intelligent_agent_assignment(self, task_type: str, required_count: int) -> List[str]:
        """Get optimal agent assignment using capability cache and load balancing"""
        capable_agents = self.capability_cache.get_capable_agents(task_type)
        
        if len(capable_agents) < required_count:
            # Log warning but return what we have
            self.logger.warning(
                f"Only {len(capable_agents)} agents available for {task_type}, "
                f"but {required_count} requested"
            )
        
        # Return up to required_count agents, sorted by workload
        return capable_agents[:required_count]
    
    async def batch_register_agent_capabilities(self, agent_capabilities: Dict[str, Set[str]]) -> None:
        """Batch register agent capabilities for efficiency"""
        start_time = time.time()
        
        for agent_id, capabilities in agent_capabilities.items():
            self.capability_cache.update_agent_capabilities(agent_id, capabilities)
        
        # Use optimized blackboard if available
        if OPTIMIZED_BLACKBOARD_AVAILABLE and hasattr(self.blackboard_service, 'register_agent_capabilities'):
            batch_tasks = []
            for agent_id, capabilities in agent_capabilities.items():
                batch_tasks.append(
                    self.blackboard_service.register_agent_capabilities(agent_id, list(capabilities))
                )
            
            await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        latency = (time.time() - start_time) * 1000
        self.logger.debug(f"Batch registered {len(agent_capabilities)} agent capabilities in {latency:.2f}ms")
    
    async def detect_performance_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks with sub-5ms focus"""
        bottlenecks = []
        current_time = time.time()
        
        # Calculate current P99 latency
        if self.latency_samples:
            sorted_samples = sorted(list(self.latency_samples))
            p99_index = int(0.99 * len(sorted_samples))
            current_p99 = sorted_samples[min(p99_index, len(sorted_samples) - 1)]
            
            if current_p99 > self.p99_latency_target:
                bottlenecks.append({
                    'type': 'p99_latency_exceeded',
                    'current_p99': current_p99,
                    'target_p99': self.p99_latency_target,
                    'severity': 'critical' if current_p99 > self.p99_latency_target * 2 else 'high',
                    'recommendation': 'Enable connection pooling and batch operations'
                })
        
        # Check cache hit rates
        total_cache_ops = sum(
            m.cache_hits + m.cache_misses 
            for m in self.coordination_metrics.values()
            if m.cache_hits + m.cache_misses > 0
        )
        total_cache_hits = sum(m.cache_hits for m in self.coordination_metrics.values())
        
        if total_cache_ops > 0:
            cache_hit_rate = total_cache_hits / total_cache_ops
            if cache_hit_rate < self.cache_hit_rate_target:
                bottlenecks.append({
                    'type': 'low_cache_hit_rate',
                    'current_rate': cache_hit_rate,
                    'target_rate': self.cache_hit_rate_target,
                    'severity': 'medium',
                    'recommendation': 'Optimize caching strategy and cache warming'
                })
        
        # Check agent workload distribution
        workloads = list(self.capability_cache.agent_workload.values())
        if workloads:
            max_workload = max(workloads)
            min_workload = min(workloads)
            
            if max_workload > min_workload * 3:  # High workload imbalance
                bottlenecks.append({
                    'type': 'workload_imbalance',
                    'max_workload': max_workload,
                    'min_workload': min_workload,
                    'severity': 'medium',
                    'recommendation': 'Improve load balancing algorithm'
                })
        
        return bottlenecks
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get specific optimization recommendations for <5ms targets"""
        recommendations = []
        bottlenecks = await self.detect_performance_bottlenecks()
        
        # Analyze bottlenecks and provide specific recommendations
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'p99_latency_exceeded':
                if OPTIMIZED_BLACKBOARD_AVAILABLE:
                    recommendations.append({
                        'type': 'immediate',
                        'category': 'blackboard_optimization',
                        'recommendation': 'Migrate to OptimizedBlackboardService with connection pooling',
                        'impact': 'high',
                        'effort': 'low',
                        'expected_improvement': '60-80% latency reduction'
                    })
                else:
                    recommendations.append({
                        'type': 'immediate', 
                        'category': 'connection_optimization',
                        'recommendation': 'Implement Redis connection pooling and batch operations',
                        'impact': 'high',
                        'effort': 'medium',
                        'expected_improvement': '40-60% latency reduction'
                    })
            
            elif bottleneck['type'] == 'low_cache_hit_rate':
                recommendations.append({
                    'type': 'optimization',
                    'category': 'caching_strategy',
                    'recommendation': 'Implement intelligent cache warming and longer TTL for stable data',
                    'impact': 'medium',
                    'effort': 'low',
                    'expected_improvement': '20-30% throughput increase'
                })
            
            elif bottleneck['type'] == 'workload_imbalance':
                recommendations.append({
                    'type': 'optimization',
                    'category': 'load_balancing',
                    'recommendation': 'Implement weighted round-robin with real-time workload monitoring',
                    'impact': 'medium',
                    'effort': 'medium',
                    'expected_improvement': '15-25% throughput increase'
                })
        
        return recommendations
    
    async def get_real_time_performance_data(self) -> Dict[str, Any]:
        """Get real-time performance data optimized for <5ms response"""
        current_time = time.time()
        
        # Calculate P99 efficiently
        p99_latency = 0.0
        if self.latency_samples:
            sorted_samples = sorted(list(self.latency_samples))
            p99_index = int(0.99 * len(sorted_samples))
            p99_latency = sorted_samples[min(p99_index, len(sorted_samples) - 1)]
        
        # Calculate cache hit rate
        total_cache_ops = sum(
            m.cache_hits + m.cache_misses 
            for m in self.coordination_metrics.values()
            if m.end_time and current_time - m.end_time < 300
        )
        total_cache_hits = sum(
            m.cache_hits 
            for m in self.coordination_metrics.values()
            if m.end_time and current_time - m.end_time < 300
        )
        cache_hit_rate = total_cache_hits / total_cache_ops if total_cache_ops > 0 else 0.0
        
        # Active vs completed coordinations
        active_count = len([m for m in self.coordination_metrics.values() if m.end_time is None])
        completed_count = len([m for m in self.coordination_metrics.values() if m.end_time is not None])
        
        return {
            'timestamp': current_time,
            'constitutional_hash': CONSTITUTIONAL_HASH,
            'performance_targets': {
                'p99_latency_target': self.p99_latency_target,
                'current_p99_latency': p99_latency,
                'p99_status': 'good' if p99_latency <= self.p99_latency_target else 'warning',
                'cache_hit_rate_target': self.cache_hit_rate_target,
                'current_cache_hit_rate': cache_hit_rate,
                'cache_status': 'good' if cache_hit_rate >= self.cache_hit_rate_target else 'warning'
            },
            'coordination_status': {
                'active_coordinations': active_count,
                'completed_coordinations': completed_count,
                'total_agents': len(self.capability_cache.capabilities)
            },
            'optimization_enabled': {
                'optimized_blackboard': OPTIMIZED_BLACKBOARD_AVAILABLE,
                'capability_caching': True,
                'batch_operations': True,
                'connection_pooling': self.redis_client is not None
            }
        }
    
    async def shutdown(self) -> None:
        """Cleanup optimized performance monitoring"""
        if self.redis_client:
            await self.redis_client.close()
        
        if self.blackboard_service and hasattr(self.blackboard_service, 'shutdown'):
            await self.blackboard_service.shutdown()
        
        self.logger.info("Optimized performance integration shut down")


# Factory function for easy integration
async def create_optimized_performance_integration(
    redis_url: str = "redis://localhost:6379",
    blackboard_service: Optional[Any] = None
) -> OptimizedPerformanceIntegration:
    """Create and initialize optimized performance integration"""
    integration = OptimizedPerformanceIntegration(redis_url)
    await integration.initialize(blackboard_service)
    return integration