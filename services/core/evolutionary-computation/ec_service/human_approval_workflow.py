"""
Human-in-the-Loop Approval Workflow for ACGS Evolutionary Computation Service
Implements comprehensive human oversight and approval mechanisms.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

class ReviewerRole(Enum):
    """Reviewer roles for human approval workflow."""
    CONSTITUTIONAL_EXPERT = "constitutional_expert"
    SECURITY_SPECIALIST = "security_specialist"
    TECHNICAL_LEAD = "technical_lead"
    GOVERNANCE_COUNCIL = "governance_council"
    SYSTEM_ADMINISTRATOR = "system_administrator"

class ReviewDecision(Enum):
    """Review decision types."""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_MODIFICATION = "requires_modification"
    ESCALATE = "escalate"
    DEFER = "defer"

class ReviewPriority(Enum):
    """Review priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class ReviewerProfile:
    """Reviewer profile information."""
    reviewer_id: str
    name: str
    role: ReviewerRole
    expertise_areas: List[str]
    availability_status: str = "available"  # available, busy, offline
    max_concurrent_reviews: int = 5
    current_review_count: int = 0
    
    # Performance metrics
    average_review_time_hours: float = 24.0
    approval_rate: float = 0.0
    accuracy_score: float = 1.0

@dataclass
class ReviewTask:
    """Human review task."""
    task_id: str
    evolution_id: str
    reviewer_id: Optional[str] = None
    
    # Task metadata
    priority: ReviewPriority = ReviewPriority.MEDIUM
    required_expertise: List[str] = field(default_factory=list)
    estimated_review_time_hours: float = 24.0
    
    # Review content
    title: str = ""
    description: str = ""
    review_materials: Dict[str, Any] = field(default_factory=dict)
    
    # Decision tracking
    decision: Optional[ReviewDecision] = None
    justification: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None

@dataclass
class ReviewWorkflow:
    """Multi-stage review workflow."""
    workflow_id: str
    evolution_id: str
    workflow_type: str  # single_reviewer, multi_reviewer, consensus, escalation
    
    # Workflow stages
    stages: List[Dict[str, Any]] = field(default_factory=list)
    current_stage: int = 0
    
    # Overall workflow status
    status: str = "pending"  # pending, in_progress, completed, failed
    final_decision: Optional[ReviewDecision] = None
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class HumanApprovalWorkflow:
    """Human-in-the-loop approval workflow system."""
    
    def __init__(self):
        self.setup_metrics()
        
        # Workflow tracking
        self.active_workflows: Dict[str, ReviewWorkflow] = {}
        self.pending_tasks: Dict[str, ReviewTask] = {}
        self.reviewer_profiles: Dict[str, ReviewerProfile] = {}
        
        # Configuration
        self.auto_assignment_enabled = True
        self.escalation_timeout_hours = 48
        self.consensus_threshold = 0.67  # 67% agreement for consensus
        
        # Initialize default reviewers
        self.initialize_default_reviewers()
        
        logger.info("Human Approval Workflow system initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.review_tasks_total = Counter(
            'human_review_tasks_total',
            'Total human review tasks',
            ['priority', 'decision']
        )
        
        self.review_processing_time = Histogram(
            'human_review_processing_time_hours',
            'Time to complete human reviews',
            ['reviewer_role', 'priority']
        )
        
        self.active_reviews_gauge = Gauge(
            'human_reviews_active',
            'Number of active human reviews',
            ['priority']
        )
        
        self.reviewer_workload_gauge = Gauge(
            'reviewer_workload',
            'Current workload per reviewer',
            ['reviewer_id', 'role']
        )

    def initialize_default_reviewers(self):
        """Initialize default reviewer profiles."""
        default_reviewers = [
            {
                'reviewer_id': 'constitutional_expert_001',
                'name': 'Constitutional Expert',
                'role': ReviewerRole.CONSTITUTIONAL_EXPERT,
                'expertise_areas': ['constitutional_compliance', 'governance', 'policy_validation']
            },
            {
                'reviewer_id': 'security_specialist_001',
                'name': 'Security Specialist',
                'role': ReviewerRole.SECURITY_SPECIALIST,
                'expertise_areas': ['security_assessment', 'vulnerability_analysis', 'threat_modeling']
            },
            {
                'reviewer_id': 'technical_lead_001',
                'name': 'Technical Lead',
                'role': ReviewerRole.TECHNICAL_LEAD,
                'expertise_areas': ['system_architecture', 'performance_optimization', 'technical_review']
            },
            {
                'reviewer_id': 'governance_council_001',
                'name': 'Governance Council',
                'role': ReviewerRole.GOVERNANCE_COUNCIL,
                'expertise_areas': ['strategic_decisions', 'policy_approval', 'risk_management']
            }
        ]
        
        for reviewer_data in default_reviewers:
            profile = ReviewerProfile(**reviewer_data)
            self.reviewer_profiles[profile.reviewer_id] = profile

    async def create_review_workflow(self, evolution_id: str, 
                                   workflow_type: str = "single_reviewer",
                                   required_expertise: List[str] = None,
                                   priority: ReviewPriority = ReviewPriority.MEDIUM) -> str:
        """Create a new review workflow."""
        workflow_id = str(uuid.uuid4())
        
        # Determine workflow stages based on type
        stages = await self.design_workflow_stages(
            workflow_type, required_expertise or [], priority
        )
        
        workflow = ReviewWorkflow(
            workflow_id=workflow_id,
            evolution_id=evolution_id,
            workflow_type=workflow_type,
            stages=stages
        )
        
        self.active_workflows[workflow_id] = workflow
        
        # Start the workflow
        await self.start_workflow(workflow)
        
        logger.info(f"Created review workflow {workflow_id} for evolution {evolution_id}")
        return workflow_id

    async def design_workflow_stages(self, workflow_type: str, 
                                   required_expertise: List[str],
                                   priority: ReviewPriority) -> List[Dict[str, Any]]:
        """Design workflow stages based on requirements."""
        stages = []
        
        if workflow_type == "single_reviewer":
            stages.append({
                'stage_name': 'primary_review',
                'required_reviewers': 1,
                'required_expertise': required_expertise,
                'decision_threshold': 1.0,
                'parallel': False
            })
            
        elif workflow_type == "multi_reviewer":
            stages.append({
                'stage_name': 'parallel_review',
                'required_reviewers': 2,
                'required_expertise': required_expertise,
                'decision_threshold': self.consensus_threshold,
                'parallel': True
            })
            
        elif workflow_type == "consensus":
            stages.extend([
                {
                    'stage_name': 'initial_review',
                    'required_reviewers': 3,
                    'required_expertise': required_expertise,
                    'decision_threshold': self.consensus_threshold,
                    'parallel': True
                },
                {
                    'stage_name': 'consensus_validation',
                    'required_reviewers': 1,
                    'required_expertise': ['governance'],
                    'decision_threshold': 1.0,
                    'parallel': False
                }
            ])
            
        elif workflow_type == "escalation":
            stages.extend([
                {
                    'stage_name': 'technical_review',
                    'required_reviewers': 1,
                    'required_expertise': ['technical_review'],
                    'decision_threshold': 1.0,
                    'parallel': False
                },
                {
                    'stage_name': 'governance_review',
                    'required_reviewers': 1,
                    'required_expertise': ['governance'],
                    'decision_threshold': 1.0,
                    'parallel': False
                }
            ])
        
        return stages

    async def start_workflow(self, workflow: ReviewWorkflow):
        """Start executing a review workflow."""
        workflow.status = "in_progress"
        
        # Start first stage
        await self.execute_workflow_stage(workflow, 0)

    async def execute_workflow_stage(self, workflow: ReviewWorkflow, stage_index: int):
        """Execute a specific workflow stage."""
        if stage_index >= len(workflow.stages):
            await self.complete_workflow(workflow)
            return
        
        stage = workflow.stages[stage_index]
        workflow.current_stage = stage_index
        
        logger.info(f"Executing stage {stage_index} of workflow {workflow.workflow_id}")
        
        # Create review tasks for this stage
        tasks = await self.create_stage_review_tasks(workflow, stage)
        
        # Assign reviewers
        for task in tasks:
            await self.assign_reviewer(task)
        
        # Monitor stage completion
        asyncio.create_task(self.monitor_stage_completion(workflow, stage_index, tasks))

    async def create_stage_review_tasks(self, workflow: ReviewWorkflow, 
                                      stage: Dict[str, Any]) -> List[ReviewTask]:
        """Create review tasks for a workflow stage."""
        tasks = []
        
        for i in range(stage['required_reviewers']):
            task_id = str(uuid.uuid4())
            
            task = ReviewTask(
                task_id=task_id,
                evolution_id=workflow.evolution_id,
                required_expertise=stage['required_expertise'],
                title=f"Evolution Review - {workflow.evolution_id}",
                description=f"Stage: {stage['stage_name']} - Review evolution request",
                priority=ReviewPriority.HIGH if 'critical' in stage.get('tags', []) else ReviewPriority.MEDIUM
            )
            
            # Set deadline based on priority
            if task.priority == ReviewPriority.CRITICAL:
                task.deadline = task.created_at + timedelta(hours=12)
            elif task.priority == ReviewPriority.HIGH:
                task.deadline = task.created_at + timedelta(hours=24)
            else:
                task.deadline = task.created_at + timedelta(hours=48)
            
            self.pending_tasks[task_id] = task
            tasks.append(task)
        
        return tasks

    async def assign_reviewer(self, task: ReviewTask):
        """Assign a reviewer to a task."""
        if not self.auto_assignment_enabled:
            logger.info(f"Auto-assignment disabled, task {task.task_id} awaiting manual assignment")
            return
        
        # Find best reviewer based on expertise and availability
        best_reviewer = await self.find_best_reviewer(task)
        
        if best_reviewer:
            await self.assign_task_to_reviewer(task, best_reviewer.reviewer_id)
        else:
            logger.warning(f"No suitable reviewer found for task {task.task_id}")

    async def find_best_reviewer(self, task: ReviewTask) -> Optional[ReviewerProfile]:
        """Find the best reviewer for a task."""
        candidates = []
        
        for reviewer in self.reviewer_profiles.values():
            # Check availability
            if reviewer.availability_status != "available":
                continue
            
            # Check workload
            if reviewer.current_review_count >= reviewer.max_concurrent_reviews:
                continue
            
            # Check expertise match
            expertise_match = 0
            for required in task.required_expertise:
                if required in reviewer.expertise_areas:
                    expertise_match += 1
            
            if expertise_match == 0 and task.required_expertise:
                continue
            
            # Calculate score
            score = (
                expertise_match * 0.4 +
                (1.0 - reviewer.current_review_count / reviewer.max_concurrent_reviews) * 0.3 +
                reviewer.accuracy_score * 0.2 +
                (1.0 / max(reviewer.average_review_time_hours, 1.0)) * 0.1
            )
            
            candidates.append((reviewer, score))
        
        if candidates:
            # Sort by score and return best candidate
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None

    async def assign_task_to_reviewer(self, task: ReviewTask, reviewer_id: str):
        """Assign a task to a specific reviewer."""
        if reviewer_id not in self.reviewer_profiles:
            raise ValueError(f"Reviewer {reviewer_id} not found")
        
        reviewer = self.reviewer_profiles[reviewer_id]
        
        # Update task
        task.reviewer_id = reviewer_id
        task.assigned_at = datetime.now(timezone.utc)
        
        # Update reviewer workload
        reviewer.current_review_count += 1
        
        # Update metrics
        self.reviewer_workload_gauge.labels(
            reviewer_id=reviewer_id,
            role=reviewer.role.value
        ).set(reviewer.current_review_count)
        
        self.active_reviews_gauge.labels(
            priority=task.priority.name.lower()
        ).inc()
        
        logger.info(f"Assigned task {task.task_id} to reviewer {reviewer_id}")

    async def submit_review_decision(self, task_id: str, reviewer_id: str,
                                   decision: ReviewDecision, justification: str,
                                   recommendations: List[str] = None) -> bool:
        """Submit a review decision."""
        if task_id not in self.pending_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.pending_tasks[task_id]
        
        if task.reviewer_id != reviewer_id:
            raise ValueError(f"Task {task_id} not assigned to reviewer {reviewer_id}")
        
        # Update task
        task.decision = decision
        task.justification = justification
        task.recommendations = recommendations or []
        task.completed_at = datetime.now(timezone.utc)
        
        # Calculate review time
        if task.assigned_at:
            review_time = (task.completed_at - task.assigned_at).total_seconds() / 3600
            
            # Update metrics
            reviewer = self.reviewer_profiles[reviewer_id]
            self.review_processing_time.labels(
                reviewer_role=reviewer.role.value,
                priority=task.priority.name.lower()
            ).observe(review_time)
        
        # Update reviewer workload
        reviewer = self.reviewer_profiles[reviewer_id]
        reviewer.current_review_count = max(0, reviewer.current_review_count - 1)
        
        self.reviewer_workload_gauge.labels(
            reviewer_id=reviewer_id,
            role=reviewer.role.value
        ).set(reviewer.current_review_count)
        
        self.active_reviews_gauge.labels(
            priority=task.priority.name.lower()
        ).dec()
        
        # Record metrics
        self.review_tasks_total.labels(
            priority=task.priority.name.lower(),
            decision=decision.value
        ).inc()
        
        # Remove from pending tasks
        del self.pending_tasks[task_id]
        
        logger.info(f"Review decision submitted for task {task_id}: {decision.value}")
        
        # Check if this completes a workflow stage
        await self.check_stage_completion(task.evolution_id)
        
        return True

    async def monitor_stage_completion(self, workflow: ReviewWorkflow, 
                                     stage_index: int, tasks: List[ReviewTask]):
        """Monitor completion of a workflow stage."""
        stage = workflow.stages[stage_index]
        
        while True:
            await asyncio.sleep(60)  # Check every minute
            
            # Check if stage is complete
            completed_tasks = [t for t in tasks if t.completed_at is not None]
            
            if len(completed_tasks) >= stage['required_reviewers']:
                # Check decision threshold
                approvals = sum(1 for t in completed_tasks if t.decision == ReviewDecision.APPROVED)
                approval_rate = approvals / len(completed_tasks)
                
                if approval_rate >= stage['decision_threshold']:
                    # Stage approved, move to next stage
                    await self.execute_workflow_stage(workflow, stage_index + 1)
                else:
                    # Stage rejected
                    workflow.status = "completed"
                    workflow.final_decision = ReviewDecision.REJECTED
                    workflow.completed_at = datetime.now(timezone.utc)
                
                break
            
            # Check for timeouts
            current_time = datetime.now(timezone.utc)
            for task in tasks:
                if (task.deadline and current_time > task.deadline and 
                    task.completed_at is None):
                    await self.handle_task_timeout(task)

    async def complete_workflow(self, workflow: ReviewWorkflow):
        """Complete a review workflow."""
        workflow.status = "completed"
        workflow.final_decision = ReviewDecision.APPROVED
        workflow.completed_at = datetime.now(timezone.utc)
        
        logger.info(f"Workflow {workflow.workflow_id} completed with decision: {workflow.final_decision.value}")

    async def check_stage_completion(self, evolution_id: str):
        """Check if any workflow stages are completed."""
        # Find workflows for this evolution
        for workflow in self.active_workflows.values():
            if workflow.evolution_id == evolution_id and workflow.status == "in_progress":
                # Check current stage completion
                # This would be implemented based on specific stage completion logic
                pass

    async def handle_task_timeout(self, task: ReviewTask):
        """Handle task timeout."""
        logger.warning(f"Task {task.task_id} timed out")
        
        # Auto-escalate or assign to different reviewer
        # Implementation depends on escalation policies

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a review workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                'workflow_id': workflow_id,
                'evolution_id': workflow.evolution_id,
                'status': workflow.status,
                'current_stage': workflow.current_stage,
                'total_stages': len(workflow.stages),
                'final_decision': workflow.final_decision.value if workflow.final_decision else None,
                'created_at': workflow.created_at.isoformat(),
                'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None
            }
        
        return None

    def get_pending_tasks_for_reviewer(self, reviewer_id: str) -> List[Dict[str, Any]]:
        """Get pending tasks for a specific reviewer."""
        tasks = []
        
        for task in self.pending_tasks.values():
            if task.reviewer_id == reviewer_id and task.completed_at is None:
                tasks.append({
                    'task_id': task.task_id,
                    'evolution_id': task.evolution_id,
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority.name,
                    'assigned_at': task.assigned_at.isoformat() if task.assigned_at else None,
                    'deadline': task.deadline.isoformat() if task.deadline else None,
                    'required_expertise': task.required_expertise
                })
        
        return tasks

# Global human approval workflow instance
human_approval_workflow = HumanApprovalWorkflow()
