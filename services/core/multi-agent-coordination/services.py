"""
Multi-Agent Coordination Services
Constitutional Hash: cdd01ef066bc6cf2

Core business logic for multi-agent coordination including task distribution,
team formation, and coordination pattern implementation.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
import random
import logging
from asyncio import Queue

from .models import (
    AgentProfile, AgentType, AgentStatus, CoordinationPattern,
    CoordinationTask, TaskStatus, TaskPriority, CoordinationPlan,
    AgentMessage, CoordinationMetrics, WorkloadDistribution,
    TeamFormation, BlackboardEntry, NegotiationProtocol,
    ConflictResolution, AgentHealth, CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class AgentRegistry:
    """Registry for managing agent lifecycle"""
    
    def __init__(self):
        self.agents: Dict[str, AgentProfile] = {}
        self.agent_health: Dict[str, AgentHealth] = {}
        self.capability_index: Dict[str, Set[str]] = defaultdict(set)
        
    async def register_agent(self, agent: AgentProfile) -> bool:
        """Register a new agent"""
        if agent.agent_id in self.agents:
            logger.warning(f"Agent {agent.agent_id} already registered")
            return False
            
        self.agents[agent.agent_id] = agent
        
        # Index capabilities for fast lookup
        for capability in agent.capabilities:
            self.capability_index[capability.name].add(agent.agent_id)
            
        # Initialize health monitoring
        self.agent_health[agent.agent_id] = AgentHealth(
            agent_id=agent.agent_id,
            status=agent.status,
            cpu_usage=0.0,
            memory_usage_mb=0.0,
            active_connections=0,
            task_queue_size=0,
            error_rate=0.0,
            response_time_ms=0.0
        )
        
        logger.info(f"Registered agent {agent.agent_id} ({agent.agent_type})")
        return True
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update agent status"""
        if agent_id not in self.agents:
            return False
            
        self.agents[agent_id].status = status
        self.agents[agent_id].last_heartbeat = datetime.utcnow()
        
        if agent_id in self.agent_health:
            self.agent_health[agent_id].status = status
            
        return True
    
    async def find_agents_by_capability(self, capability: str) -> List[AgentProfile]:
        """Find agents with specific capability"""
        agent_ids = self.capability_index.get(capability, set())
        return [
            self.agents[aid] for aid in agent_ids 
            if aid in self.agents and self.agents[aid].status != AgentStatus.OFFLINE
        ]
    
    async def get_available_agents(self, agent_type: Optional[AgentType] = None) -> List[AgentProfile]:
        """Get available agents optionally filtered by type"""
        available = []
        for agent in self.agents.values():
            if agent.status in [AgentStatus.IDLE, AgentStatus.BUSY]:
                if agent_type is None or agent.agent_type == agent_type:
                    available.append(agent)
        return available

class TaskScheduler:
    """Advanced task scheduling with multiple strategies"""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.task_queue: Queue[CoordinationTask] = Queue()
        self.active_tasks: Dict[str, CoordinationTask] = {}
        self.task_history: List[CoordinationTask] = []
        
    async def schedule_task(
        self,
        task: CoordinationTask,
        pattern: CoordinationPattern
    ) -> Optional[CoordinationPlan]:
        """Schedule task using specified coordination pattern"""
        
        # Validate constitutional compliance
        if not await self._validate_constitutional_compliance(task):
            logger.error(f"Task {task.task_id} failed constitutional validation")
            return None
            
        if pattern == CoordinationPattern.HIERARCHICAL:
            return await self._hierarchical_scheduling(task)
        elif pattern == CoordinationPattern.FLAT:
            return await self._flat_scheduling(task)
        elif pattern == CoordinationPattern.BLACKBOARD:
            return await self._blackboard_scheduling(task)
        elif pattern == CoordinationPattern.CONTRACT_NET:
            return await self._contract_net_scheduling(task)
        elif pattern == CoordinationPattern.AUCTION:
            return await self._auction_scheduling(task)
        elif pattern == CoordinationPattern.TEAM:
            return await self._team_scheduling(task)
        else:
            logger.error(f"Unknown coordination pattern: {pattern}")
            return None
    
    async def _validate_constitutional_compliance(self, task: CoordinationTask) -> bool:
        """Validate task against constitutional requirements"""
        # Check for required constitutional hash
        if task.requirements.get("constitutional_hash") != CONSTITUTIONAL_HASH:
            return False
            
        # Validate performance requirements
        if "performance_requirements" in task.requirements:
            perf_reqs = task.requirements["performance_requirements"]
            if perf_reqs.get("p99_latency_ms", 0) > 5.0:
                return False
            if perf_reqs.get("min_throughput_rps", 0) < 100:
                return False
                
        task.constitutional_validation = True
        return True
    
    async def _hierarchical_scheduling(self, task: CoordinationTask) -> CoordinationPlan:
        """Hierarchical scheduling with coordinator-worker pattern"""
        # Find coordinator
        coordinators = await self.registry.get_available_agents(AgentType.COORDINATOR)
        if not coordinators:
            logger.error("No coordinators available")
            return None
            
        coordinator = min(coordinators, key=lambda a: len(a.current_tasks))
        
        # Find workers based on task requirements
        required_capabilities = task.requirements.get("capabilities", [])
        workers = []
        
        for capability in required_capabilities:
            capable_agents = await self.registry.find_agents_by_capability(capability)
            workers.extend([a for a in capable_agents if a.agent_type == AgentType.WORKER])
        
        if not workers:
            logger.error("No suitable workers found")
            return None
            
        # Create hierarchical plan
        plan = CoordinationPlan(
            pattern=CoordinationPattern.HIERARCHICAL,
            tasks=[task],
            agent_assignments={
                coordinator.agent_id: [task.task_id],
                **{w.agent_id: [] for w in workers[:3]}  # Assign up to 3 workers
            },
            dependencies={},
            optimization_metrics={
                "coordinator_load": len(coordinator.current_tasks),
                "worker_count": len(workers)
            },
            constitutional_compliance_score=1.0 if task.constitutional_validation else 0.0
        )
        
        return plan
    
    async def _flat_scheduling(self, task: CoordinationTask) -> CoordinationPlan:
        """Flat scheduling with peer-to-peer coordination"""
        # Find all eligible agents
        agents = await self.registry.get_available_agents()
        
        # Filter by capabilities
        required_capabilities = set(task.requirements.get("capabilities", []))
        eligible_agents = []
        
        for agent in agents:
            agent_capabilities = {cap.name for cap in agent.capabilities}
            if required_capabilities.issubset(agent_capabilities):
                eligible_agents.append(agent)
        
        if not eligible_agents:
            return None
            
        # Select agents with best performance scores
        eligible_agents.sort(
            key=lambda a: sum(c.performance_score for c in a.capabilities) / len(a.capabilities),
            reverse=True
        )
        
        selected_agents = eligible_agents[:min(5, len(eligible_agents))]
        
        plan = CoordinationPlan(
            pattern=CoordinationPattern.FLAT,
            tasks=[task],
            agent_assignments={a.agent_id: [task.task_id] for a in selected_agents},
            dependencies={},
            optimization_metrics={
                "agent_count": len(selected_agents),
                "avg_performance": sum(
                    sum(c.performance_score for c in a.capabilities) / len(a.capabilities)
                    for a in selected_agents
                ) / len(selected_agents)
            },
            constitutional_compliance_score=1.0 if task.constitutional_validation else 0.0
        )
        
        return plan
    
    async def _blackboard_scheduling(self, task: CoordinationTask) -> CoordinationPlan:
        """Blackboard-based scheduling with shared workspace"""
        # This would integrate with the Blackboard service
        # For now, create a simplified plan
        agents = await self.registry.get_available_agents()
        
        if len(agents) < 2:
            return None
            
        # Select diverse agent types for blackboard collaboration
        selected_agents = []
        agent_types_seen = set()
        
        for agent in agents:
            if agent.agent_type not in agent_types_seen:
                selected_agents.append(agent)
                agent_types_seen.add(agent.agent_type)
                if len(selected_agents) >= 4:
                    break
        
        plan = CoordinationPlan(
            pattern=CoordinationPattern.BLACKBOARD,
            tasks=[task],
            agent_assignments={a.agent_id: [] for a in selected_agents},
            dependencies={},
            optimization_metrics={
                "agent_diversity": len(agent_types_seen),
                "collaboration_potential": len(selected_agents)
            },
            constitutional_compliance_score=1.0 if task.constitutional_validation else 0.0
        )
        
        return plan
    
    async def _contract_net_scheduling(self, task: CoordinationTask) -> CoordinationPlan:
        """Contract Net Protocol scheduling"""
        # Announce task to all capable agents
        required_capabilities = set(task.requirements.get("capabilities", []))
        capable_agents = []
        
        for agent in self.registry.agents.values():
            agent_capabilities = {cap.name for cap in agent.capabilities}
            if required_capabilities.issubset(agent_capabilities):
                capable_agents.append(agent)
        
        if not capable_agents:
            return None
            
        # Simulate bidding process (in real implementation, would be async messaging)
        bids = []
        for agent in capable_agents:
            if agent.status == AgentStatus.IDLE:
                bid_score = sum(c.performance_score for c in agent.capabilities) / len(agent.capabilities)
                bid_score *= (1.0 - len(agent.current_tasks) / 10.0)  # Penalize busy agents
                bids.append((agent, bid_score))
        
        if not bids:
            return None
            
        # Select winning bid
        bids.sort(key=lambda x: x[1], reverse=True)
        winner = bids[0][0]
        
        plan = CoordinationPlan(
            pattern=CoordinationPattern.CONTRACT_NET,
            tasks=[task],
            agent_assignments={winner.agent_id: [task.task_id]},
            dependencies={},
            optimization_metrics={
                "winning_bid": bids[0][1],
                "total_bids": len(bids)
            },
            constitutional_compliance_score=1.0 if task.constitutional_validation else 0.0
        )
        
        return plan
    
    async def _auction_scheduling(self, task: CoordinationTask) -> CoordinationPlan:
        """Auction-based task allocation"""
        # Similar to contract net but with competitive bidding
        return await self._contract_net_scheduling(task)
    
    async def _team_scheduling(self, task: CoordinationTask) -> CoordinationPlan:
        """Team-based scheduling for complex tasks"""
        # Form a team based on complementary capabilities
        required_capabilities = set(task.requirements.get("capabilities", []))
        team_size = task.requirements.get("team_size", 3)
        
        # Build optimal team
        team = []
        covered_capabilities = set()
        
        for _ in range(team_size):
            best_agent = None
            best_score = -1
            
            for agent in self.registry.agents.values():
                if agent.status == AgentStatus.OFFLINE or agent in team:
                    continue
                    
                agent_capabilities = {cap.name for cap in agent.capabilities}
                new_capabilities = agent_capabilities - covered_capabilities
                
                if new_capabilities:
                    score = len(new_capabilities) / len(required_capabilities - covered_capabilities)
                    if score > best_score:
                        best_score = score
                        best_agent = agent
            
            if best_agent:
                team.append(best_agent)
                covered_capabilities.update({cap.name for cap in best_agent.capabilities})
            
            if covered_capabilities >= required_capabilities:
                break
        
        if not team:
            return None
            
        plan = CoordinationPlan(
            pattern=CoordinationPattern.TEAM,
            tasks=[task],
            agent_assignments={a.agent_id: [task.task_id] for a in team},
            dependencies={},
            optimization_metrics={
                "team_size": len(team),
                "capability_coverage": len(covered_capabilities & required_capabilities) / len(required_capabilities)
            },
            constitutional_compliance_score=1.0 if task.constitutional_validation else 0.0
        )
        
        return plan

class WorkloadBalancer:
    """Dynamic workload balancing across agents"""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.load_threshold_high = 0.8
        self.load_threshold_low = 0.2
        
    async def analyze_workload(self) -> WorkloadDistribution:
        """Analyze current workload distribution"""
        agent_workloads = {}
        total_tasks = 0
        
        for agent in self.registry.agents.values():
            task_count = len(agent.current_tasks)
            agent_workloads[agent.agent_id] = task_count
            total_tasks += task_count
        
        if not agent_workloads:
            return WorkloadDistribution(
                agent_workloads={},
                load_balance_score=1.0,
                rebalancing_needed=False
            )
        
        # Calculate load balance score
        avg_load = total_tasks / len(agent_workloads)
        variance = sum((load - avg_load) ** 2 for load in agent_workloads.values()) / len(agent_workloads)
        load_balance_score = 1.0 / (1.0 + variance)
        
        # Identify overloaded and underutilized agents
        overloaded = []
        underutilized = []
        
        for agent_id, load in agent_workloads.items():
            agent = self.registry.agents[agent_id]
            max_capacity = max(cap.max_concurrent_tasks for cap in agent.capabilities)
            
            utilization = load / max_capacity if max_capacity > 0 else 0
            
            if utilization > self.load_threshold_high:
                overloaded.append(agent_id)
            elif utilization < self.load_threshold_low:
                underutilized.append(agent_id)
        
        return WorkloadDistribution(
            agent_workloads=agent_workloads,
            load_balance_score=load_balance_score,
            overloaded_agents=overloaded,
            underutilized_agents=underutilized,
            rebalancing_needed=len(overloaded) > 0 and len(underutilized) > 0
        )
    
    async def rebalance_workload(self, distribution: WorkloadDistribution) -> bool:
        """Rebalance workload across agents"""
        if not distribution.rebalancing_needed:
            return True
            
        # This would implement actual task migration
        # For now, just log the need for rebalancing
        logger.info(
            f"Workload rebalancing needed: "
            f"{len(distribution.overloaded_agents)} overloaded, "
            f"{len(distribution.underutilized_agents)} underutilized"
        )
        
        return True

class ConflictResolver:
    """Resolve conflicts between agents"""
    
    def __init__(self):
        self.active_conflicts: Dict[str, ConflictResolution] = {}
        self.resolution_history: List[ConflictResolution] = []
        
    async def detect_conflict(
        self,
        agents: List[str],
        subject: Dict[str, Any]
    ) -> Optional[ConflictResolution]:
        """Detect and create conflict resolution"""
        conflict = ConflictResolution(
            conflicting_agents=agents,
            conflict_type=subject.get("type", "resource_contention"),
            conflict_subject=subject,
            resolution_strategy="constitutional_priority"
        )
        
        self.active_conflicts[conflict.conflict_id] = conflict
        return conflict
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        mediator_id: Optional[str] = None
    ) -> bool:
        """Resolve active conflict"""
        if conflict_id not in self.active_conflicts:
            return False
            
        conflict = self.active_conflicts[conflict_id]
        
        # Apply constitutional priority resolution
        if conflict.resolution_strategy == "constitutional_priority":
            # Tasks with constitutional validation get priority
            solutions = []
            
            for i, agent_id in enumerate(conflict.conflicting_agents):
                solutions.append({
                    "agent_id": agent_id,
                    "priority": i,
                    "constitutional_weight": 1.0 if i == 0 else 0.5
                })
            
            conflict.proposed_solutions = solutions
            conflict.selected_solution = solutions[0]
            conflict.mediator_id = mediator_id
            
        # Move to history
        self.resolution_history.append(conflict)
        del self.active_conflicts[conflict_id]
        
        return True

class MultiAgentCoordinator:
    """Main coordinator for multi-agent systems"""
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.scheduler = TaskScheduler(self.registry)
        self.balancer = WorkloadBalancer(self.registry)
        self.resolver = ConflictResolver()
        self.metrics = CoordinationMetrics()
        self.message_queue: Queue[AgentMessage] = Queue()
        
    async def coordinate(
        self,
        task: CoordinationTask,
        pattern: CoordinationPattern = CoordinationPattern.HIERARCHICAL
    ) -> Optional[CoordinationPlan]:
        """Main coordination entry point"""
        start_time = datetime.utcnow()
        
        try:
            # Schedule task
            plan = await self.scheduler.schedule_task(task, pattern)
            if not plan:
                self.metrics.failed_tasks += 1
                return None
            
            # Check workload balance
            distribution = await self.balancer.analyze_workload()
            if distribution.rebalancing_needed:
                await self.balancer.rebalance_workload(distribution)
            
            # Update metrics
            self.metrics.total_tasks += 1
            
            # Calculate latency
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_latency_metrics(latency_ms)
            
            return plan
            
        except Exception as e:
            logger.error(f"Coordination failed: {e}")
            self.metrics.failed_tasks += 1
            return None
    
    def _update_latency_metrics(self, latency_ms: float):
        """Update latency metrics"""
        # Simple P99 calculation (would use proper percentile in production)
        if latency_ms > self.metrics.p99_latency_ms:
            self.metrics.p99_latency_ms = latency_ms * 0.99 + self.metrics.p99_latency_ms * 0.01
    
    async def get_metrics(self) -> CoordinationMetrics:
        """Get current coordination metrics"""
        # Update agent utilization
        agent_utils = {}
        for agent in self.registry.agents.values():
            if agent.capabilities:
                max_capacity = max(cap.max_concurrent_tasks for cap in agent.capabilities)
                utilization = len(agent.current_tasks) / max_capacity if max_capacity > 0 else 0
                agent_utils[agent.agent_id] = utilization
        
        self.metrics.agent_utilization = agent_utils
        
        # Calculate efficiency
        if self.metrics.total_tasks > 0:
            self.metrics.coordination_efficiency = (
                self.metrics.completed_tasks / self.metrics.total_tasks
            )
        
        return self.metrics