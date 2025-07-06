"""
Enhanced Coordinator Agent with Hybrid Hierarchical-Blackboard Policy
Extends existing ACGS coordination capabilities with multi-agent governance.

Enhanced with full hierarchical structure supporting:
- Orchestrator agents (top-level coordination)
- Domain specialist agents (middle-tier expertise)
- Worker agents (bottom-tier execution)
- Complexity-based hierarchy creation
- Advanced performance monitoring and optimization
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4
from enum import Enum

from pydantic import BaseModel, Field

from ...shared.blackboard import BlackboardService, KnowledgeItem, TaskDefinition, ConflictItem
from ...shared.events.bus import EventBus
from ...shared.constitutional_safety_framework import ConstitutionalSafetyValidator
from ...shared.performance_monitoring import PerformanceMonitor
from ...shared.monitoring.enhanced_performance_monitor import (
    EnhancedPerformanceMonitor, MetricType
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class GovernanceRequest(BaseModel):
    """Represents a governance request that needs multi-agent coordination"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    request_type: str  # 'model_deployment', 'policy_enforcement', 'compliance_audit'
    priority: int = Field(default=3, ge=1, le=5)
    requester_id: str
    input_data: Dict[str, Any]
    constitutional_requirements: List[str] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    complexity_score: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskDecompositionStrategy:
    """Strategies for decomposing governance requests into tasks"""
    
    @staticmethod
    def decompose_model_deployment(request: GovernanceRequest) -> List[Dict[str, Any]]:
        """Decompose model deployment governance into sub-tasks"""
        tasks = []
        
        # Ethical analysis task
        tasks.append({
            'task_type': 'ethical_analysis',
            'priority': 1,
            'requirements': {
                'analysis_types': ['bias_assessment', 'fairness_evaluation', 'harm_potential'],
                'constitutional_principles': ['safety', 'transparency', 'consent']
            },
            'input_data': {
                'model_info': request.input_data.get('model_info', {}),
                'deployment_context': request.input_data.get('deployment_context', {}),
                'stakeholder_impact': request.input_data.get('stakeholder_impact', {})
            }
        })
        
        # Legal compliance task
        tasks.append({
            'task_type': 'legal_compliance',
            'priority': 1,
            'requirements': {
                'jurisdictions': request.input_data.get('jurisdictions', ['US', 'EU']),
                'compliance_frameworks': ['GDPR', 'CCPA', 'AI_Act'],
                'constitutional_principles': ['data_privacy', 'consent', 'transparency']
            },
            'input_data': {
                'model_info': request.input_data.get('model_info', {}),
                'data_sources': request.input_data.get('data_sources', {}),
                'user_interactions': request.input_data.get('user_interactions', {})
            }
        })
        
        # Operational validation task
        tasks.append({
            'task_type': 'operational_validation',
            'priority': 2,
            'requirements': {
                'performance_thresholds': request.input_data.get('performance_requirements', {}),
                'scalability_requirements': request.input_data.get('scalability_requirements', {}),
                'constitutional_principles': ['resource_limits', 'reversibility']
            },
            'input_data': {
                'model_info': request.input_data.get('model_info', {}),
                'infrastructure_constraints': request.input_data.get('infrastructure_constraints', {}),
                'performance_benchmarks': request.input_data.get('performance_benchmarks', {})
            },
            'dependencies': ['ethical_analysis']  # Wait for ethical analysis before operational validation
        })
        
        return tasks
    
    @staticmethod
    def decompose_policy_enforcement(request: GovernanceRequest) -> List[Dict[str, Any]]:
        """Decompose policy enforcement into sub-tasks"""
        tasks = []
        
        # Policy analysis task
        tasks.append({
            'task_type': 'policy_analysis',
            'priority': 1,
            'requirements': {
                'policy_scope': request.input_data.get('policy_scope', 'organizational'),
                'stakeholder_analysis': True,
                'constitutional_principles': ['transparency', 'consent', 'least_privilege']
            },
            'input_data': {
                'policy_document': request.input_data.get('policy_document', {}),
                'enforcement_context': request.input_data.get('enforcement_context', {}),
                'affected_systems': request.input_data.get('affected_systems', [])
            }
        })
        
        # Implementation planning task
        tasks.append({
            'task_type': 'implementation_planning',
            'priority': 2,
            'requirements': {
                'rollout_strategy': 'phased',
                'monitoring_requirements': True,
                'constitutional_principles': ['reversibility', 'least_privilege']
            },
            'input_data': {
                'policy_requirements': request.input_data.get('policy_requirements', {}),
                'system_architecture': request.input_data.get('system_architecture', {}),
                'resource_constraints': request.input_data.get('resource_constraints', {})
            },
            'dependencies': ['policy_analysis']
        })
        
        # Compliance monitoring task
        tasks.append({
            'task_type': 'compliance_monitoring',
            'priority': 3,
            'requirements': {
                'monitoring_frequency': 'continuous',
                'alert_thresholds': request.input_data.get('alert_thresholds', {}),
                'constitutional_principles': ['transparency', 'consent']
            },
            'input_data': {
                'monitoring_scope': request.input_data.get('monitoring_scope', {}),
                'compliance_metrics': request.input_data.get('compliance_metrics', {}),
                'reporting_requirements': request.input_data.get('reporting_requirements', {})
            },
            'dependencies': ['implementation_planning']
        })
        
        return tasks


# Enhanced Hierarchical Coordination Classes

class AgentTier(Enum):
    """Agent hierarchy tiers"""

    ORCHESTRATOR = "orchestrator"
    DOMAIN_SPECIALIST = "domain_specialist"
    WORKER = "worker"


class HierarchicalAgent(BaseModel):
    """Agent in hierarchical structure"""

    agent_id: str = Field(..., description="Unique agent identifier")
    tier: AgentTier = Field(..., description="Hierarchical tier")
    domain: str = Field(..., description="Domain of expertise")
    capabilities: List[str] = Field(default_factory=list)
    parent_agent_id: Optional[str] = Field(None, description="Parent in hierarchy")
    child_agent_ids: List[str] = Field(default_factory=list)
    workload_capacity: int = Field(default=5, description="Maximum concurrent tasks")
    current_workload: int = Field(default=0, description="Current active tasks")
    performance_score: float = Field(default=1.0, description="Performance rating")
    constitutional_compliance_score: float = Field(default=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HierarchyStructure(BaseModel):
    """Complete hierarchy structure"""

    hierarchy_id: str = Field(..., description="Unique hierarchy identifier")
    orchestrator: HierarchicalAgent = Field(..., description="Top-level orchestrator")
    domain_specialists: Dict[str, HierarchicalAgent] = Field(default_factory=dict)
    workers: Dict[str, HierarchicalAgent] = Field(default_factory=dict)
    complexity_level: int = Field(..., description="Task complexity (1-10)")
    created_for_task: str = Field(..., description="Task that triggered creation")
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class HierarchicalCoordinationManager:
    """
    Manages hierarchical agent coordination with complexity-based structure creation.
    Implements orchestrator -> domain specialists -> workers pattern.
    """

    def __init__(self,
                 blackboard_service: BlackboardService,
                 event_bus: EventBus,
                 safety_validator: ConstitutionalSafetyValidator):
        self.blackboard = blackboard_service
        self.event_bus = event_bus
        self.safety_validator = safety_validator
        self.performance_monitor = PerformanceMonitor()

        # Active hierarchies
        self.active_hierarchies: Dict[str, HierarchyStructure] = {}

        # Agent registry
        self.agent_registry: Dict[str, HierarchicalAgent] = {}

        # Performance tracking
        self.hierarchy_metrics = {
            "hierarchies_created": 0,
            "tasks_completed": 0,
            "average_completion_time": 0.0,
            "coordination_efficiency": 1.0,
            "constitutional_compliance_rate": 1.0
        }

        logger.info("Hierarchical Coordination Manager initialized")

    async def create_agent_hierarchy(self, task_description: str,
                                   complexity_level: int) -> HierarchyStructure:
        """Create hierarchical agent structure based on task complexity"""
        try:
            hierarchy_id = str(uuid4())

            if complexity_level <= 2:
                # Simple task - flat structure with minimal hierarchy
                return await self._create_flat_agent_team(hierarchy_id, task_description)
            elif complexity_level <= 5:
                # Medium complexity - two-tier hierarchy
                return await self._create_two_tier_hierarchy(hierarchy_id, task_description, complexity_level)
            else:
                # Complex task - full hierarchical structure
                return await self._create_full_hierarchy(hierarchy_id, task_description, complexity_level)

        except Exception as e:
            logger.error(f"Failed to create agent hierarchy: {e!s}")
            raise

    async def _create_flat_agent_team(self, hierarchy_id: str,
                                    task_description: str) -> HierarchyStructure:
        """Create a flat team structure for simple tasks"""
        try:
            # Create single orchestrator that also acts as worker
            orchestrator = HierarchicalAgent(
                agent_id=f"orchestrator_{hierarchy_id[:8]}",
                tier=AgentTier.ORCHESTRATOR,
                domain="general",
                capabilities=["task_coordination", "execution", "monitoring"],
                workload_capacity=3,
                constitutional_compliance_score=1.0
            )

            # Register orchestrator
            self.agent_registry[orchestrator.agent_id] = orchestrator

            # Create hierarchy structure
            hierarchy = HierarchyStructure(
                hierarchy_id=hierarchy_id,
                orchestrator=orchestrator,
                complexity_level=1,
                created_for_task=task_description,
                performance_metrics={"coordination_overhead": 0.1}
            )

            self.active_hierarchies[hierarchy_id] = hierarchy
            self.hierarchy_metrics["hierarchies_created"] += 1

            logger.info(f"Created flat agent team {hierarchy_id}")
            return hierarchy

        except Exception as e:
            logger.error(f"Failed to create flat agent team: {e!s}")
            raise

    async def _create_two_tier_hierarchy(self, hierarchy_id: str,
                                       task_description: str,
                                       complexity_level: int) -> HierarchyStructure:
        """Create a two-tier hierarchy for medium complexity tasks"""
        try:
            # Create orchestrator
            orchestrator = HierarchicalAgent(
                agent_id=f"orchestrator_{hierarchy_id[:8]}",
                tier=AgentTier.ORCHESTRATOR,
                domain="coordination",
                capabilities=["task_coordination", "resource_allocation", "monitoring"],
                workload_capacity=2,
                constitutional_compliance_score=1.0
            )

            # Create domain specialists based on task requirements
            domain_analysis = await self._analyze_task_domains(task_description)
            domain_specialists = {}

            for domain, requirements in domain_analysis.items():
                specialist = HierarchicalAgent(
                    agent_id=f"{domain}_specialist_{hierarchy_id[:8]}",
                    tier=AgentTier.DOMAIN_SPECIALIST,
                    domain=domain,
                    capabilities=requirements.get("capabilities", []),
                    parent_agent_id=orchestrator.agent_id,
                    workload_capacity=4,
                    constitutional_compliance_score=1.0
                )

                domain_specialists[domain] = specialist
                orchestrator.child_agent_ids.append(specialist.agent_id)
                self.agent_registry[specialist.agent_id] = specialist

            # Register orchestrator
            self.agent_registry[orchestrator.agent_id] = orchestrator

            # Create hierarchy structure
            hierarchy = HierarchyStructure(
                hierarchy_id=hierarchy_id,
                orchestrator=orchestrator,
                domain_specialists=domain_specialists,
                complexity_level=complexity_level,
                created_for_task=task_description,
                performance_metrics={
                    "coordination_overhead": 0.2,
                    "specialization_efficiency": 0.8
                }
            )

            self.active_hierarchies[hierarchy_id] = hierarchy
            self.hierarchy_metrics["hierarchies_created"] += 1

            logger.info(f"Created two-tier hierarchy {hierarchy_id} with {len(domain_specialists)} specialists")
            return hierarchy

        except Exception as e:
            logger.error(f"Failed to create two-tier hierarchy: {e!s}")
            raise

    async def _create_full_hierarchy(self, hierarchy_id: str,
                                   task_description: str,
                                   complexity_level: int) -> HierarchyStructure:
        """Create a full three-tier hierarchy for complex tasks"""
        try:
            # Create orchestrator
            orchestrator = HierarchicalAgent(
                agent_id=f"orchestrator_{hierarchy_id[:8]}",
                tier=AgentTier.ORCHESTRATOR,
                domain="strategic_coordination",
                capabilities=["strategic_planning", "resource_optimization", "quality_assurance"],
                workload_capacity=1,  # Focus on coordination only
                constitutional_compliance_score=1.0
            )

            # Create domain specialists
            domain_analysis = await self._analyze_task_domains(task_description)
            domain_specialists = {}
            workers = {}

            for domain, requirements in domain_analysis.items():
                # Create domain specialist
                specialist = HierarchicalAgent(
                    agent_id=f"{domain}_specialist_{hierarchy_id[:8]}",
                    tier=AgentTier.DOMAIN_SPECIALIST,
                    domain=domain,
                    capabilities=requirements.get("specialist_capabilities", []),
                    parent_agent_id=orchestrator.agent_id,
                    workload_capacity=3,
                    constitutional_compliance_score=1.0
                )

                domain_specialists[domain] = specialist
                orchestrator.child_agent_ids.append(specialist.agent_id)

                # Create workers for this domain
                worker_count = min(3, max(1, complexity_level - 3))  # 1-3 workers per domain
                for i in range(worker_count):
                    worker = HierarchicalAgent(
                        agent_id=f"{domain}_worker_{i}_{hierarchy_id[:8]}",
                        tier=AgentTier.WORKER,
                        domain=domain,
                        capabilities=requirements.get("worker_capabilities", []),
                        parent_agent_id=specialist.agent_id,
                        workload_capacity=5,
                        constitutional_compliance_score=1.0
                    )

                    workers[worker.agent_id] = worker
                    specialist.child_agent_ids.append(worker.agent_id)
                    self.agent_registry[worker.agent_id] = worker

                self.agent_registry[specialist.agent_id] = specialist

            # Register orchestrator
            self.agent_registry[orchestrator.agent_id] = orchestrator

            # Create hierarchy structure
            hierarchy = HierarchyStructure(
                hierarchy_id=hierarchy_id,
                orchestrator=orchestrator,
                domain_specialists=domain_specialists,
                workers=workers,
                complexity_level=complexity_level,
                created_for_task=task_description,
                performance_metrics={
                    "coordination_overhead": 0.3,
                    "specialization_efficiency": 0.9,
                    "parallel_execution_capability": 0.8
                }
            )

            self.active_hierarchies[hierarchy_id] = hierarchy
            self.hierarchy_metrics["hierarchies_created"] += 1

            logger.info(f"Created full hierarchy {hierarchy_id}: 1 orchestrator, {len(domain_specialists)} specialists, {len(workers)} workers")
            return hierarchy

        except Exception as e:
            logger.error(f"Failed to create full hierarchy: {e!s}")
            raise

    async def _analyze_task_domains(self, task_description: str) -> Dict[str, Dict[str, Any]]:
        """Analyze task to identify required domains and capabilities"""
        try:
            # Simplified domain analysis - in production this would use NLP/ML
            domains = {}

            # Check for common domain keywords
            if any(keyword in task_description.lower() for keyword in ["policy", "governance", "compliance"]):
                domains["governance"] = {
                    "specialist_capabilities": ["policy_analysis", "compliance_checking", "governance_design"],
                    "worker_capabilities": ["document_processing", "data_validation", "reporting"]
                }

            if any(keyword in task_description.lower() for keyword in ["security", "safety", "risk"]):
                domains["security"] = {
                    "specialist_capabilities": ["security_analysis", "risk_assessment", "threat_modeling"],
                    "worker_capabilities": ["vulnerability_scanning", "log_analysis", "monitoring"]
                }

            if any(keyword in task_description.lower() for keyword in ["performance", "optimization", "efficiency"]):
                domains["performance"] = {
                    "specialist_capabilities": ["performance_analysis", "optimization_design", "metrics_evaluation"],
                    "worker_capabilities": ["data_collection", "benchmarking", "testing"]
                }

            # Default domain if no specific domains identified
            if not domains:
                domains["general"] = {
                    "specialist_capabilities": ["task_analysis", "solution_design", "quality_control"],
                    "worker_capabilities": ["task_execution", "data_processing", "validation"]
                }

            return domains

        except Exception as e:
            logger.error(f"Failed to analyze task domains: {e!s}")
            return {"general": {"specialist_capabilities": [], "worker_capabilities": []}}


class CoordinatorAgent:
    """
    Enhanced Coordinator Agent implementing Hybrid Hierarchical-Blackboard Policy.
    Integrates with existing ACGS infrastructure while adding multi-agent coordination.
    """
    
    def __init__(
        self,
        agent_id: str = "acgs_coordinator",
        blackboard_service: Optional[BlackboardService] = None,
        event_bus: Optional[EventBus] = None,
        constitutional_framework: Optional[ConstitutionalSafetyValidator] = None,
        performance_monitor: Optional[PerformanceMonitor] = None
    ):
        self.agent_id = agent_id
        self.blackboard = blackboard_service or BlackboardService()
        self.event_bus = event_bus
        self.constitutional_framework = constitutional_framework
        self.performance_monitor = performance_monitor
        
        self.logger = logging.getLogger(__name__)
        self.active_requests: Dict[str, GovernanceRequest] = {}
        self.task_completion_tracking: Dict[str, Set[str]] = {}  # request_id -> completed_task_ids
        self.is_running = False
        
        # Task decomposition strategies
        self.decomposition_strategies = {
            'model_deployment': TaskDecompositionStrategy.decompose_model_deployment,
            'policy_enforcement': TaskDecompositionStrategy.decompose_policy_enforcement,
            'compliance_audit': self._decompose_compliance_audit
        }
        
        # Agent capability registry
        self.agent_capabilities = {
            'ethics_agent': ['ethical_analysis', 'bias_assessment', 'stakeholder_analysis'],
            'legal_agent': ['legal_compliance', 'regulatory_analysis', 'policy_analysis'],
            'operational_agent': ['operational_validation', 'performance_analysis', 'implementation_planning'],
            'monitoring_agent': ['compliance_monitoring', 'performance_monitoring', 'audit_analysis']
        }

        # Enhanced Hierarchical Coordination Manager
        self.hierarchy_manager = HierarchicalCoordinationManager(
            blackboard_service=self.blackboard,
            event_bus=self.event_bus,
            safety_validator=self.constitutional_framework
        )

        # Enhanced Performance Monitor for revolutionary metrics
        self.enhanced_performance_monitor = EnhancedPerformanceMonitor(retention_hours=24)

    async def initialize(self) -> None:
        """Initialize the Coordinator Agent"""
        await self.blackboard.initialize()

        # Initialize enhanced performance monitor
        await self.enhanced_performance_monitor.start()

        # Register with blackboard
        await self.blackboard.register_agent(
            agent_id=self.agent_id,
            agent_type='coordinator',
            capabilities=['task_decomposition', 'conflict_resolution', 'integration_management']
        )

        # Subscribe to relevant events
        if self.event_bus:
            await self.event_bus.subscribe('governance_request', self._handle_governance_request)
            await self.event_bus.subscribe('task_completed', self._handle_task_completion)
            await self.event_bus.subscribe('conflict_detected', self._handle_conflict_detection)

        self.logger.info(f"Coordinator Agent {self.agent_id} initialized successfully")

    async def start(self) -> None:
        """Start the coordinator agent main loop"""
        self.is_running = True
        
        # Start background tasks
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._conflict_resolution_loop())
        asyncio.create_task(self._heartbeat_loop())
        
        self.logger.info("Coordinator Agent started")

    async def stop(self) -> None:
        """Stop the coordinator agent"""
        self.is_running = False
        await self.blackboard.shutdown()
        self.logger.info("Coordinator Agent stopped")

    async def process_governance_request(self, request: GovernanceRequest) -> Dict[str, Any]:
        """
        Process a governance request using the Hybrid Hierarchical-Blackboard approach.

        1. Decompose request into sub-tasks
        2. Create tasks on blackboard
        3. Monitor task completion
        4. Integrate results and ensure constitutional compliance
        """
        start_time = time.time()

        # Store active request
        self.active_requests[request.id] = request
        self.task_completion_tracking[request.id] = set()

        try:
            # Step 1: Constitutional pre-check
            constitutional_compliance = await self._validate_constitutional_compliance_detailed(request)
            if not constitutional_compliance.get('compliant', False):
                return {
                    'request_id': request.id,
                    'success': False,
                    'error': 'Constitutional compliance check failed',
                    'constitutional_compliance': constitutional_compliance,
                    'processing_time': time.time() - start_time
                }

            # Step 2: Decompose request into tasks
            tasks = await self._decompose_request(request)

            # Step 3: Create tasks on blackboard
            task_ids = await self._create_tasks_on_blackboard(tasks, request.id)

            # Step 4: Add coordination knowledge to blackboard
            await self._add_coordination_knowledge(request, task_ids)

            # Step 4.5: Store constitutional compliance knowledge
            await self._store_constitutional_compliance_knowledge(request, constitutional_compliance)

            # Step 5: Notify agents about new governance workflow
            if self.event_bus:
                await self.event_bus.publish('governance_workflow_started', {
                    'request_id': request.id,
                    'request_type': request.request_type,
                    'task_count': len(task_ids),
                    'priority': request.priority,
                    'deadline': request.deadline.isoformat() if request.deadline else None
                })

            processing_time = time.time() - start_time
            self.logger.info(
                f"Governance request {request.id} decomposed into {len(task_ids)} tasks. "
                f"Processing time: {processing_time:.2f}s"
            )

            # Return comprehensive result structure
            return {
                'request_id': request.id,
                'success': True,
                'task_ids': task_ids,
                'task_count': len(task_ids),
                'constitutional_compliance': constitutional_compliance,
                'processing_time': processing_time,
                'request_type': request.request_type,
                'priority': request.priority,
                'status': 'tasks_created'
            }

        except Exception as e:
            self.logger.error(f"Error processing governance request {request.id}: {str(e)}")
            # Clean up
            if request.id in self.active_requests:
                del self.active_requests[request.id]
            if request.id in self.task_completion_tracking:
                del self.task_completion_tracking[request.id]

            return {
                'request_id': request.id,
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    async def _decompose_request(self, request: GovernanceRequest) -> List[Dict[str, Any]]:
        """Decompose governance request into sub-tasks"""
        if request.request_type not in self.decomposition_strategies:
            raise ValueError(f"Unknown request type: {request.request_type}")
        
        strategy = self.decomposition_strategies[request.request_type]
        tasks = strategy(request)
        
        # Add common metadata to all tasks
        for task in tasks:
            task.update({
                'governance_request_id': request.id,
                'deadline': request.deadline,
                'constitutional_requirements': request.constitutional_requirements
            })
        
        return tasks

    async def _create_tasks_on_blackboard(self, tasks: List[Dict[str, Any]], request_id: str) -> List[str]:
        """Create tasks on the blackboard and return task IDs"""
        task_ids = []
        
        for task_data in tasks:
            task = TaskDefinition(
                task_type=task_data['task_type'],
                priority=task_data['priority'],
                requirements=task_data['requirements'],
                input_data=task_data['input_data'],
                dependencies=task_data.get('dependencies', []),
                deadline=task_data.get('deadline')
            )
            
            task_id = await self.blackboard.create_task(task)
            task_ids.append(task_id)
        
        return task_ids

    async def _add_coordination_knowledge(self, request: GovernanceRequest, task_ids: List[str]) -> None:
        """Add coordination knowledge to the blackboard"""
        # Add governance context knowledge
        governance_knowledge = KnowledgeItem(
            space='governance',
            agent_id=self.agent_id,
            knowledge_type='governance_context',
            content={
                'request_id': request.id,
                'request_type': request.request_type,
                'task_ids': task_ids,
                'priority': request.priority,
                'complexity_score': request.complexity_score,
                'constitutional_requirements': request.constitutional_requirements,
                'coordination_strategy': 'hybrid_hierarchical_blackboard'
            },
            priority=request.priority,
            tags={'governance', 'coordination', request.request_type}
        )
        
        await self.blackboard.add_knowledge(governance_knowledge)
        
        # Add task dependency knowledge
        if any(task_ids):
            dependency_knowledge = KnowledgeItem(
                space='coordination',
                agent_id=self.agent_id,
                knowledge_type='task_dependencies',
                content={
                    'request_id': request.id,
                    'task_dependency_graph': await self._build_dependency_graph(task_ids),
                    'critical_path': await self._identify_critical_path(task_ids),
                    'parallel_execution_groups': await self._identify_parallel_groups(task_ids)
                },
                priority=request.priority,
                tags={'coordination', 'dependencies', 'workflow'}
            )
            
            await self.blackboard.add_knowledge(dependency_knowledge)

    async def _store_constitutional_compliance_knowledge(self, request: GovernanceRequest, compliance_result: Dict[str, Any]) -> None:
        """Store constitutional compliance knowledge in the blackboard"""
        compliance_knowledge = KnowledgeItem(
            space='governance',
            agent_id=self.agent_id,
            knowledge_type='constitutional_compliance',
            content={
                'request_id': request.id,
                'request_type': request.request_type,
                'compliance_result': compliance_result,
                'constitutional_hash': compliance_result.get('constitutional_hash', 'cdd01ef066bc6cf2'),
                'validation_timestamp': compliance_result.get('validation_timestamp'),
                'compliant': compliance_result.get('compliant', True),
                'violations': compliance_result.get('violations', []),
                'principle_adherence': compliance_result.get('principle_adherence', {})
            },
            priority=1,
            tags={'constitutional', 'compliance', 'validation'}
        )

        await self.blackboard.add_knowledge(compliance_knowledge)

    async def _build_dependency_graph(self, task_ids: List[str]) -> Dict[str, List[str]]:
        """Build task dependency graph"""
        dependency_graph = {}
        
        for task_id in task_ids:
            task = await self.blackboard.get_task(task_id)
            if task:
                dependency_graph[task_id] = task.dependencies
                
        return dependency_graph

    async def _identify_critical_path(self, task_ids: List[str]) -> List[str]:
        """Identify critical path through tasks"""
        # Simplified critical path identification
        # In production, this would use proper critical path algorithm
        dependency_graph = await self._build_dependency_graph(task_ids)
        
        # Find tasks with no dependencies (starting points)
        start_tasks = [task_id for task_id, deps in dependency_graph.items() if not deps]
        
        # For now, return the longest dependency chain
        longest_path = []
        for start_task in start_tasks:
            path = self._find_longest_path(start_task, dependency_graph)
            if len(path) > len(longest_path):
                longest_path = path
                
        return longest_path

    def _find_longest_path(self, task_id: str, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Find longest path from given task"""
        # Simplified implementation
        path = [task_id]
        
        # Find tasks that depend on current task
        dependent_tasks = [tid for tid, deps in dependency_graph.items() if task_id in deps]
        
        longest_sub_path = []
        for dependent_task in dependent_tasks:
            sub_path = self._find_longest_path(dependent_task, dependency_graph)
            if len(sub_path) > len(longest_sub_path):
                longest_sub_path = sub_path
                
        return path + longest_sub_path

    async def _identify_parallel_groups(self, task_ids: List[str]) -> List[List[str]]:
        """Identify groups of tasks that can be executed in parallel"""
        dependency_graph = await self._build_dependency_graph(task_ids)
        
        # Group tasks by their dependency level
        parallel_groups = []
        processed = set()
        
        while len(processed) < len(task_ids):
            current_group = []
            
            for task_id in task_ids:
                if task_id in processed:
                    continue
                    
                # Check if all dependencies are satisfied
                task_deps = dependency_graph.get(task_id, [])
                if all(dep in processed for dep in task_deps):
                    current_group.append(task_id)
            
            if current_group:
                parallel_groups.append(current_group)
                processed.update(current_group)
            else:
                # Break infinite loop if no progress
                break
        
        return parallel_groups

    async def _validate_constitutional_compliance(self, request: GovernanceRequest) -> bool:
        """Validate request against constitutional principles"""
        if not self.constitutional_framework:
            return True  # Skip if framework not available
        
        try:
            # Check constitutional compliance
            compliance_result = await self.constitutional_framework.validate_request(
                request_type=request.request_type,
                input_data=request.input_data,
                constitutional_requirements=request.constitutional_requirements
            )
            
            if not compliance_result.get('compliant', False):
                self.logger.warning(
                    f"Constitutional compliance failed for request {request.id}: "
                    f"{compliance_result.get('violations', [])}"
                )
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Constitutional compliance check failed: {str(e)}")
            return False

    async def _validate_constitutional_compliance_detailed(self, request: GovernanceRequest) -> Dict[str, Any]:
        """Validate constitutional compliance and return detailed results"""
        try:
            if not self.constitutional_framework:
                # Return basic compliance structure when no framework is available
                return {
                    'compliant': True,
                    'constitutional_hash': 'cdd01ef066bc6cf2',
                    'principle_adherence': {
                        'safety': True,
                        'transparency': True,
                        'consent': True,
                        'data_privacy': True
                    },
                    'violations': [],
                    'confidence': 0.8,
                    'validation_timestamp': datetime.now(timezone.utc).isoformat(),
                    'framework_available': False
                }

            # Validate against constitutional principles
            compliance_result = await self.constitutional_framework.validate_request(
                request_type=request.request_type,
                input_data=request.input_data,
                constitutional_requirements=request.constitutional_requirements
            )

            # Ensure required fields are present
            detailed_result = {
                'compliant': compliance_result.get('compliant', True),
                'constitutional_hash': 'cdd01ef066bc6cf2',
                'principle_adherence': compliance_result.get('principle_adherence', {
                    'safety': True,
                    'transparency': True,
                    'consent': True,
                    'data_privacy': True
                }),
                'violations': compliance_result.get('violations', []),
                'confidence': compliance_result.get('confidence', 0.8),
                'validation_timestamp': datetime.now(timezone.utc).isoformat(),
                'framework_available': True
            }

            return detailed_result

        except Exception as e:
            self.logger.error(f"Constitutional compliance check failed: {str(e)}")
            return {
                'compliant': False,
                'constitutional_hash': 'cdd01ef066bc6cf2',
                'principle_adherence': {},
                'violations': [f"Validation error: {str(e)}"],
                'confidence': 0.0,
                'validation_timestamp': datetime.now(timezone.utc).isoformat(),
                'framework_available': False,
                'error': str(e)
            }

    async def _handle_task_completion(self, event_data: Dict[str, Any]) -> None:
        """Handle task completion events"""
        task_id = event_data.get('task_id')
        if not task_id:
            return
        
        task = await self.blackboard.get_task(task_id)
        if not task:
            return
        
        request_id = task.requirements.get('governance_request_id')
        if not request_id or request_id not in self.active_requests:
            return
        
        # Track completion
        self.task_completion_tracking[request_id].add(task_id)
        
        # Check if all tasks for this request are completed
        await self._check_request_completion(request_id)

    async def _check_request_completion(self, request_id: str) -> None:
        """Check if all tasks for a governance request are completed"""
        if request_id not in self.active_requests:
            return
        
        # Get all tasks for this request
        governance_knowledge = await self.blackboard.query_knowledge(
            space='governance',
            knowledge_type='governance_context',
            tags={'governance', 'coordination'}
        )
        
        request_tasks = []
        for knowledge in governance_knowledge:
            if knowledge.content.get('request_id') == request_id:
                request_tasks = knowledge.content.get('task_ids', [])
                break
        
        completed_tasks = self.task_completion_tracking.get(request_id, set())
        
        if len(completed_tasks) >= len(request_tasks):
            # All tasks completed, integrate results
            await self._integrate_results(request_id, request_tasks)

    async def _integrate_results(self, request_id: str, task_ids: List[str]) -> None:
        """Integrate results from all completed tasks"""
        start_time = time.time()
        
        try:
            # Collect all task results
            task_results = {}
            for task_id in task_ids:
                task = await self.blackboard.get_task(task_id)
                if task and task.output_data:
                    task_results[task.task_type] = task.output_data
            
            # Validate integrated result for constitutional compliance
            integrated_result = await self._validate_integrated_result(request_id, task_results)
            
            # Store final result as knowledge
            result_knowledge = KnowledgeItem(
                space='governance',
                agent_id=self.agent_id,
                knowledge_type='governance_result',
                content={
                    'request_id': request_id,
                    'task_results': task_results,
                    'integrated_result': integrated_result,
                    'completion_time': datetime.now(timezone.utc).isoformat(),
                    'processing_duration': time.time() - start_time,
                    'constitutional_compliance': integrated_result.get('constitutional_compliance', {})
                },
                priority=1,
                tags={'governance', 'result', 'completed'}
            )
            
            await self.blackboard.add_knowledge(result_knowledge)
            
            # Publish completion event
            if self.event_bus:
                await self.event_bus.publish('governance_request_completed', {
                    'request_id': request_id,
                    'success': integrated_result.get('success', False),
                    'constitutional_compliant': integrated_result.get('constitutional_compliance', {}).get('compliant', False),
                    'processing_duration': time.time() - start_time,
                    'task_count': len(task_ids)
                })
            
            # Cleanup
            self._cleanup_request(request_id)
            
            self.logger.info(f"Governance request {request_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error integrating results for request {request_id}: {str(e)}")
            # Mark as failed and cleanup
            self._cleanup_request(request_id)

    async def _validate_integrated_result(self, request_id: str, task_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the integrated result meets all requirements"""
        request = self.active_requests.get(request_id)
        if not request:
            return {'success': False, 'error': 'Request not found'}
        
        # Check for conflicts between task results
        conflicts = await self._detect_result_conflicts(task_results)
        
        if conflicts:
            # Report conflicts to blackboard
            for conflict in conflicts:
                conflict_item = ConflictItem(
                    conflict_type='decision_conflict',
                    involved_agents=[self.agent_id],
                    involved_tasks=list(task_results.keys()),
                    description=conflict['description'],
                    severity=conflict.get('severity', 'medium')
                )
                await self.blackboard.report_conflict(conflict_item)
        
        # Constitutional compliance check
        constitutional_compliance = {'compliant': True, 'violations': []}
        if self.constitutional_framework:
            constitutional_compliance = await self.constitutional_framework.validate_integrated_result(
                request=request,
                task_results=task_results
            )
        
        # Build integrated result
        integrated_result = {
            'success': len(conflicts) == 0 and constitutional_compliance['compliant'],
            'request_id': request_id,
            'request_type': request.request_type,
            'conflicts': conflicts,
            'constitutional_compliance': constitutional_compliance,
            'recommendations': await self._generate_recommendations(request, task_results),
            'confidence_score': await self._calculate_confidence_score(task_results)
        }
        
        # Add specific result fields based on request type
        if request.request_type == 'model_deployment':
            integrated_result.update({
                'deployment_approved': integrated_result['success'],
                'ethical_assessment': task_results.get('ethical_analysis', {}),
                'legal_assessment': task_results.get('legal_compliance', {}),
                'operational_assessment': task_results.get('operational_validation', {})
            })
        elif request.request_type == 'policy_enforcement':
            integrated_result.update({
                'enforcement_approved': integrated_result['success'],
                'policy_analysis': task_results.get('policy_analysis', {}),
                'implementation_plan': task_results.get('implementation_planning', {}),
                'monitoring_plan': task_results.get('compliance_monitoring', {})
            })
        
        return integrated_result

    async def _detect_result_conflicts(self, task_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts between task results"""
        conflicts = []
        
        # Check for approval conflicts
        approvals = {}
        for task_type, result in task_results.items():
            if 'approved' in result:
                approvals[task_type] = result['approved']
        
        if len(set(approvals.values())) > 1:
            conflicts.append({
                'type': 'approval_conflict',
                'description': f"Conflicting approval decisions: {approvals}",
                'severity': 'high',
                'involved_tasks': list(approvals.keys())
            })
        
        # Check for risk level conflicts
        risk_levels = {}
        for task_type, result in task_results.items():
            if 'risk_level' in result:
                risk_levels[task_type] = result['risk_level']
        
        if len(set(risk_levels.values())) > 1:
            risk_values = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            max_risk = max(risk_levels.values(), key=lambda x: risk_values.get(x, 2))
            min_risk = min(risk_levels.values(), key=lambda x: risk_values.get(x, 2))
            
            if risk_values.get(max_risk, 2) - risk_values.get(min_risk, 2) > 1:
                conflicts.append({
                    'type': 'risk_assessment_conflict',
                    'description': f"Conflicting risk assessments: {risk_levels}",
                    'severity': 'medium',
                    'involved_tasks': list(risk_levels.keys())
                })
        
        return conflicts

    async def _generate_recommendations(self, request: GovernanceRequest, task_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on task results"""
        recommendations = []
        
        # Analyze each task result for recommendations
        for task_type, result in task_results.items():
            if 'recommendations' in result:
                recommendations.extend(result['recommendations'])
        
        # Add coordination-level recommendations
        if request.request_type == 'model_deployment':
            ethical_result = task_results.get('ethical_analysis', {})
            if ethical_result.get('bias_detected', False):
                recommendations.append("Consider bias mitigation strategies before deployment")
            
            operational_result = task_results.get('operational_validation', {})
            if operational_result.get('performance_concerns', False):
                recommendations.append("Address performance concerns before full deployment")
        
        return recommendations

    async def _calculate_confidence_score(self, task_results: Dict[str, Any]) -> float:
        """Calculate confidence score for the integrated result"""
        if not task_results:
            return 0.0
        
        confidence_scores = []
        for result in task_results.values():
            if 'confidence' in result:
                confidence_scores.append(result['confidence'])
        
        if not confidence_scores:
            return 0.7  # Default confidence
        
        # Use harmonic mean for conservative confidence estimate
        harmonic_mean = len(confidence_scores) / sum(1/score for score in confidence_scores if score > 0)
        return min(harmonic_mean, 1.0)

    def _cleanup_request(self, request_id: str) -> None:
        """Clean up completed request from tracking"""
        if request_id in self.active_requests:
            del self.active_requests[request_id]
        if request_id in self.task_completion_tracking:
            del self.task_completion_tracking[request_id]

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop for task progress and performance"""
        while self.is_running:
            try:
                # Check for stuck tasks
                await self._check_stuck_tasks()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Check agent health
                await self._check_agent_health()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _conflict_resolution_loop(self) -> None:
        """Background loop for handling conflicts"""
        while self.is_running:
            try:
                # Get open conflicts
                conflicts = await self.blackboard.get_open_conflicts(limit=10)
                
                for conflict in conflicts:
                    await self._resolve_conflict(conflict)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in conflict resolution loop: {str(e)}")
                await asyncio.sleep(30)

    async def _heartbeat_loop(self) -> None:
        """Background heartbeat loop"""
        while self.is_running:
            try:
                await self.blackboard.agent_heartbeat(self.agent_id)
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {str(e)}")
                await asyncio.sleep(60)

    async def _check_stuck_tasks(self) -> None:
        """Check for tasks that appear to be stuck"""
        # This would implement logic to identify and handle stuck tasks
        pass

    async def _update_performance_metrics(self) -> None:
        """Update performance metrics"""
        if self.performance_monitor:
            metrics = await self.blackboard.get_metrics()
            await self.performance_monitor.record_metrics('coordinator', metrics)

    async def _check_agent_health(self) -> None:
        """Check health of registered agents"""
        active_agents = await self.blackboard.get_active_agents()
        self.logger.debug(f"Active agents: {len(active_agents)}")

    async def _resolve_conflict(self, conflict: ConflictItem) -> None:
        """Resolve a conflict using appropriate strategy"""
        try:
            if conflict.conflict_type == 'decision_conflict':
                await self._resolve_decision_conflict(conflict)
            elif conflict.conflict_type == 'resource_conflict':
                await self._resolve_resource_conflict(conflict)
            elif conflict.conflict_type == 'policy_conflict':
                await self._resolve_policy_conflict(conflict)
            else:
                self.logger.warning(f"Unknown conflict type: {conflict.conflict_type}")
                
        except Exception as e:
            self.logger.error(f"Error resolving conflict {conflict.id}: {str(e)}")

    async def _resolve_decision_conflict(self, conflict: ConflictItem) -> None:
        """Resolve decision conflicts using voting or escalation"""
        # Implement voting mechanism or escalate to human oversight
        resolution_data = {
            'strategy': 'coordinator_override',
            'decision': 'escalate_to_human',
            'reasoning': 'Complex decision conflict requires human judgment'
        }
        
        await self.blackboard.resolve_conflict(
            conflict.id,
            'coordinator_override',
            resolution_data
        )

    async def _resolve_resource_conflict(self, conflict: ConflictItem) -> None:
        """Resolve resource conflicts using priority-based allocation"""
        resolution_data = {
            'strategy': 'priority_based_allocation',
            'allocation_decision': 'highest_priority_wins',
            'reasoning': 'Resource allocated based on task priority'
        }
        
        await self.blackboard.resolve_conflict(
            conflict.id,
            'priority_based_allocation',
            resolution_data
        )

    async def _resolve_policy_conflict(self, conflict: ConflictItem) -> None:
        """Resolve policy conflicts using constitutional principles"""
        resolution_data = {
            'strategy': 'constitutional_precedence',
            'decision': 'defer_to_constitutional_principles',
            'reasoning': 'Constitutional principles take precedence over conflicting policies'
        }
        
        await self.blackboard.resolve_conflict(
            conflict.id,
            'constitutional_precedence',
            resolution_data
        )

    async def _decompose_compliance_audit(self, request: GovernanceRequest) -> List[Dict[str, Any]]:
        """Decompose compliance audit requests into tasks"""
        tasks = []
        
        # Data compliance audit
        tasks.append({
            'task_type': 'data_compliance_audit',
            'priority': 1,
            'requirements': {
                'audit_scope': request.input_data.get('audit_scope', 'full'),
                'compliance_frameworks': request.input_data.get('frameworks', ['GDPR', 'CCPA']),
                'constitutional_principles': ['data_privacy', 'transparency', 'consent']
            },
            'input_data': {
                'data_sources': request.input_data.get('data_sources', {}),
                'processing_activities': request.input_data.get('processing_activities', {}),
                'data_subject_rights': request.input_data.get('data_subject_rights', {})
            }
        })
        
        # System compliance audit
        tasks.append({
            'task_type': 'system_compliance_audit',
            'priority': 2,
            'requirements': {
                'system_scope': request.input_data.get('system_scope', {}),
                'security_requirements': request.input_data.get('security_requirements', {}),
                'constitutional_principles': ['safety', 'least_privilege', 'reversibility']
            },
            'input_data': {
                'system_architecture': request.input_data.get('system_architecture', {}),
                'access_controls': request.input_data.get('access_controls', {}),
                'audit_logs': request.input_data.get('audit_logs', {})
            }
        })
        
        # Governance compliance audit
        tasks.append({
            'task_type': 'governance_compliance_audit',
            'priority': 3,
            'requirements': {
                'governance_framework': 'ACGS-PGP',
                'policy_compliance': True,
                'constitutional_principles': ['transparency', 'consent', 'safety']
            },
            'input_data': {
                'governance_policies': request.input_data.get('governance_policies', {}),
                'decision_logs': request.input_data.get('decision_logs', {}),
                'stakeholder_feedback': request.input_data.get('stakeholder_feedback', {})
            },
            'dependencies': ['data_compliance_audit', 'system_compliance_audit']
        })
        
        return tasks

    async def _handle_governance_request(self, event_data: Dict[str, Any]) -> None:
        """Handle incoming governance requests from event bus"""
        try:
            request_data = event_data.get('request', {})
            request = GovernanceRequest(**request_data)
            await self.process_governance_request(request)
        except Exception as e:
            self.logger.error(f"Error handling governance request: {str(e)}")

    async def _handle_conflict_detection(self, event_data: Dict[str, Any]) -> None:
        """Handle conflict detection events"""
        conflict_id = event_data.get('conflict_id')
        if conflict_id:
            conflict = await self.blackboard.get_conflict(conflict_id)
            if conflict:
                await self._resolve_conflict(conflict)

    async def decompose_governance_request(self, request: GovernanceRequest) -> str:
        """
        Decompose a governance request into tasks and return the request ID.
        This method is used by tests to initiate governance workflows.
        """
        # Process the request and return the request ID
        result = await self.process_governance_request(request)
        # Return the request ID regardless of the result structure
        return request.id

    async def detect_agent_conflicts(self, request_id: str) -> List[Dict[str, Any]]:
        """
        Detect conflicts between agent analyses for a given request.
        Returns a list of detected conflicts.
        """
        conflicts = []

        try:
            # Get all knowledge items related to this request
            knowledge_items = await self.blackboard.query_knowledge(
                space="governance",
                tags={"assessment", "risk"}
            )

            # Filter knowledge items for this request
            request_knowledge = []
            for item in knowledge_items:
                if isinstance(item.content, dict):
                    # Check both 'request_id' and 'governance_request_id' fields
                    item_request_id = item.content.get('request_id') or item.content.get('governance_request_id')
                    if item_request_id == request_id:
                        request_knowledge.append(item)

            # Analyze for conflicts between different agent assessments
            if len(request_knowledge) >= 2:
                # Check for conflicting risk assessments
                risk_levels = {}
                approvals = {}

                for item in request_knowledge:
                    agent_id = item.agent_id
                    content = item.content

                    if 'risk_level' in content:
                        risk_levels[agent_id] = content['risk_level']
                    if 'approved' in content:
                        approvals[agent_id] = content['approved']

                # Detect risk level conflicts
                if len(set(risk_levels.values())) > 1:
                    conflicts.append({
                        'type': 'risk_assessment_conflict',
                        'description': f"Conflicting risk assessments: {risk_levels}",
                        'severity': 'medium',
                        'involved_agents': list(risk_levels.keys()),
                        'details': risk_levels
                    })

                # Detect approval conflicts
                if len(set(approvals.values())) > 1:
                    conflicts.append({
                        'type': 'approval_conflict',
                        'description': f"Conflicting approval decisions: {approvals}",
                        'severity': 'high',
                        'involved_agents': list(approvals.keys()),
                        'details': approvals
                    })

        except Exception as e:
            self.logger.error(f"Error detecting conflicts for request {request_id}: {str(e)}")

        return conflicts

    async def _assign_task_to_agent(self, task: Dict[str, Any], agent_type: str) -> bool:
        """
        Assign a task to a specific agent type.
        Returns True if assignment was successful, False otherwise.
        """
        try:
            # Create task definition
            task_def = TaskDefinition(
                task_type=task.get('task_type', 'general'),
                priority=task.get('priority', 3),
                requirements=task.get('requirements', {}),
                input_data=task.get('input_data', {}),
                dependencies=task.get('dependencies', []),
                deadline=task.get('deadline')
            )

            # Create task on blackboard
            task_id = await self.blackboard.create_task(task_def)

            # Add agent assignment preference
            await self.blackboard.add_knowledge(KnowledgeItem(
                space='coordination',
                agent_id=self.agent_id,
                knowledge_type='task_assignment',
                content={
                    'task_id': task_id,
                    'preferred_agent_type': agent_type,
                    'assignment_timestamp': datetime.now(timezone.utc).isoformat()
                },
                priority=task.get('priority', 3),
                tags={'assignment', 'coordination'}
            ))

            return True

        except Exception as e:
            self.logger.error(f"Error assigning task to {agent_type}: {str(e)}")
            return False

    async def resolve_conflict_through_consensus(self, conflict: Dict[str, Any], algorithm=None) -> Dict[str, Any]:
        """
        Resolve a conflict using consensus mechanisms.
        Returns the resolution result.
        """
        try:
            # Import here to avoid circular imports
            from services.core.consensus_engine.consensus_mechanisms import ConsensusAlgorithm

            # Default to constitutional priority if no algorithm specified
            if algorithm is None:
                algorithm = ConsensusAlgorithm.CONSTITUTIONAL_PRIORITY

            # Create a consensus proposal for the conflict
            proposal_data = {
                'conflict_id': conflict.get('id', str(uuid4())),
                'conflict_type': conflict.get('type', 'unknown'),
                'involved_agents': conflict.get('involved_agents', []),
                'conflict_details': conflict.get('details', {}),
                'resolution_options': self._generate_resolution_options(conflict)
            }

            # Use consensus engine if available
            if hasattr(self, 'consensus_engine') and self.consensus_engine:
                consensus_result = await self.consensus_engine.reach_consensus(
                    proposal_data,
                    algorithm=algorithm,
                    participants=conflict.get('involved_agents', [])
                )

                resolution_result = {
                    'resolution': {
                        'success': consensus_result.get('consensus_reached', False),
                        'decision': consensus_result.get('final_decision', {}),
                        'algorithm_used': str(algorithm),
                        'confidence': consensus_result.get('confidence', 0.5)
                    },
                    'conflict_id': conflict.get('id'),
                    'resolution_timestamp': datetime.now(timezone.utc).isoformat()
                }
            else:
                # Fallback resolution using constitutional principles
                resolution_result = {
                    'resolution': {
                        'success': True,
                        'decision': self._apply_constitutional_resolution(conflict),
                        'algorithm_used': 'constitutional_fallback',
                        'confidence': 0.7
                    },
                    'conflict_id': conflict.get('id'),
                    'resolution_timestamp': datetime.now(timezone.utc).isoformat()
                }

            # Record resolution in blackboard
            await self.blackboard.add_knowledge(KnowledgeItem(
                space='coordination',
                agent_id=self.agent_id,
                knowledge_type='conflict_resolution',
                content=resolution_result,
                priority=1,
                tags={'resolution', 'conflict', 'consensus'}
            ))

            return resolution_result

        except Exception as e:
            self.logger.error(f"Error resolving conflict through consensus: {str(e)}")
            return {
                'resolution': {
                    'success': False,
                    'error': str(e),
                    'algorithm_used': str(algorithm) if algorithm else 'unknown'
                },
                'conflict_id': conflict.get('id'),
                'resolution_timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _generate_resolution_options(self, conflict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate possible resolution options for a conflict"""
        conflict_type = conflict.get('type', 'unknown')

        if conflict_type == 'risk_assessment_conflict':
            return [
                {'option': 'use_highest_risk', 'description': 'Use the highest risk assessment for safety'},
                {'option': 'use_average_risk', 'description': 'Use average of all risk assessments'},
                {'option': 'require_consensus', 'description': 'Require agents to reach consensus'}
            ]
        elif conflict_type == 'approval_conflict':
            return [
                {'option': 'require_unanimous_approval', 'description': 'Require all agents to approve'},
                {'option': 'majority_rule', 'description': 'Use majority decision'},
                {'option': 'constitutional_override', 'description': 'Apply constitutional principles'}
            ]
        else:
            return [
                {'option': 'escalate_to_human', 'description': 'Escalate to human oversight'},
                {'option': 'apply_constitutional_principles', 'description': 'Apply constitutional framework'}
            ]

    def _apply_constitutional_resolution(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply constitutional principles to resolve conflict"""
        conflict_type = conflict.get('type', 'unknown')

        if conflict_type == 'risk_assessment_conflict':
            # Constitutional principle: err on the side of caution
            return {
                'decision': 'use_highest_risk_assessment',
                'rationale': 'Constitutional safety principle requires conservative risk assessment',
                'constitutional_principle': 'safety_first'
            }
        elif conflict_type == 'approval_conflict':
            # Constitutional principle: require consensus for approval
            return {
                'decision': 'require_unanimous_approval',
                'rationale': 'Constitutional consensus principle requires agreement from all agents',
                'constitutional_principle': 'consensus_requirement'
            }
        else:
            return {
                'decision': 'escalate_to_human_oversight',
                'rationale': 'Unknown conflict type requires human intervention',
                'constitutional_principle': 'human_oversight'
            }

    # Enhanced Hierarchical Coordination Methods

    async def _calculate_task_complexity(self, request: GovernanceRequest,
                                       tasks: List[Dict[str, Any]]) -> int:
        """Calculate task complexity level (1-10) for hierarchy creation"""
        try:
            complexity_score = 0

            # Base complexity from request
            complexity_score += request.complexity_score * 5  # Scale to 0-5

            # Add complexity based on number of tasks
            complexity_score += min(3, len(tasks) / 2)  # Up to 3 points for task count

            # Add complexity based on dependencies
            total_dependencies = sum(len(task.get('dependencies', [])) for task in tasks)
            complexity_score += min(2, total_dependencies / 3)  # Up to 2 points for dependencies

            # Constitutional requirements add complexity
            if request.constitutional_requirements:
                complexity_score += min(1, len(request.constitutional_requirements) / 3)

            # Deadline pressure adds complexity
            if request.deadline:
                time_pressure = (request.deadline - datetime.now(timezone.utc)).total_seconds()
                if time_pressure < 3600:  # Less than 1 hour
                    complexity_score += 2
                elif time_pressure < 86400:  # Less than 1 day
                    complexity_score += 1

            # Ensure complexity is in valid range
            complexity_level = max(1, min(10, int(complexity_score)))

            self.logger.info(f"Calculated complexity level {complexity_level} for request {request.id}")
            return complexity_level

        except Exception as e:
            self.logger.error(f"Failed to calculate task complexity: {e!s}")
            return 5  # Default to medium complexity

    async def _coordinate_hierarchical_execution(self, hierarchy: HierarchyStructure,
                                               task_ids: List[str]) -> None:
        """Coordinate task execution using hierarchical structure"""
        try:
            # Assign tasks to hierarchy levels based on complexity and requirements
            orchestrator_tasks = []
            specialist_tasks = {}
            worker_tasks = {}

            # Get task details from blackboard
            for task_id in task_ids:
                task = await self.blackboard.get_task(task_id)
                if not task:
                    continue

                task_type = task.get('task_type', 'general')
                task_priority = task.get('priority', 3)

                # High-priority coordination tasks go to orchestrator
                if task_priority <= 2 or 'coordination' in task_type:
                    orchestrator_tasks.append(task_id)
                # Domain-specific tasks go to specialists
                elif any(domain in task_type for domain in hierarchy.domain_specialists.keys()):
                    for domain in hierarchy.domain_specialists.keys():
                        if domain in task_type:
                            if domain not in specialist_tasks:
                                specialist_tasks[domain] = []
                            specialist_tasks[domain].append(task_id)
                            break
                # Execution tasks go to workers
                else:
                    # Distribute among available workers
                    if hierarchy.workers:
                        worker_id = min(hierarchy.workers.keys(),
                                      key=lambda w: hierarchy.workers[w].current_workload)
                        if worker_id not in worker_tasks:
                            worker_tasks[worker_id] = []
                        worker_tasks[worker_id].append(task_id)
                    else:
                        # Fallback to specialists if no workers
                        domain = next(iter(hierarchy.domain_specialists.keys()), 'general')
                        if domain not in specialist_tasks:
                            specialist_tasks[domain] = []
                        specialist_tasks[domain].append(task_id)

            # Update workloads
            hierarchy.orchestrator.current_workload = len(orchestrator_tasks)
            for domain, tasks in specialist_tasks.items():
                hierarchy.domain_specialists[domain].current_workload = len(tasks)
            for worker_id, tasks in worker_tasks.items():
                hierarchy.workers[worker_id].current_workload = len(tasks)

            # Log task distribution
            self.logger.info(f"Hierarchical task distribution for {hierarchy.hierarchy_id}:")
            self.logger.info(f"  Orchestrator: {len(orchestrator_tasks)} tasks")
            self.logger.info(f"  Specialists: {sum(len(tasks) for tasks in specialist_tasks.values())} tasks")
            self.logger.info(f"  Workers: {sum(len(tasks) for tasks in worker_tasks.values())} tasks")

            # Store task assignments in blackboard
            await self._store_hierarchy_assignments(hierarchy, {
                'orchestrator_tasks': orchestrator_tasks,
                'specialist_tasks': specialist_tasks,
                'worker_tasks': worker_tasks
            })

        except Exception as e:
            self.logger.error(f"Failed to coordinate hierarchical execution: {e!s}")
            raise

    async def _store_hierarchy_assignments(self, hierarchy: HierarchyStructure,
                                         assignments: Dict[str, Any]) -> None:
        """Store hierarchy task assignments in blackboard"""
        try:
            knowledge_item = KnowledgeItem(
                id=f"hierarchy_assignments_{hierarchy.hierarchy_id}",
                space="coordination",
                knowledge_type="hierarchy_assignments",
                agent_id=self.agent_id,
                content={
                    "hierarchy_id": hierarchy.hierarchy_id,
                    "assignments": assignments,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "constitutional_hash": CONSTITUTIONAL_HASH
                },
                priority=2,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
            )

            await self.blackboard.add_knowledge(knowledge_item)

            self.logger.debug(f"Stored hierarchy assignments for {hierarchy.hierarchy_id}")

        except Exception as e:
            self.logger.error(f"Failed to store hierarchy assignments: {e!s}")

    def get_hierarchy_metrics(self) -> Dict[str, Any]:
        """Get hierarchical coordination performance metrics"""
        return {
            **self.hierarchy_manager.hierarchy_metrics,
            "active_hierarchies": len(self.hierarchy_manager.active_hierarchies),
            "total_agents_managed": len(self.hierarchy_manager.agent_registry),
            "coordination_efficiency": self.hierarchy_manager.hierarchy_metrics.get("coordination_efficiency", 1.0)
        }