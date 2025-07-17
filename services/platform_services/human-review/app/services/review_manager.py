"""
Review Manager - Manages review tasks and workflow
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import redis
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..models.schemas import (
    ReviewTask,
    ReviewSubmission,
    ReviewerProfile,
    ReviewStatus,
    ReviewPriority,
    ReviewDecision,
    ReviewerRole,
    ContentType,
    ReviewTaskRequest,
    ReviewAnalytics,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

# Database models
Base = declarative_base()

class ReviewTaskDB(Base):
    __tablename__ = "review_tasks"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(String, nullable=False)
    content_data = Column(JSON)
    priority = Column(String, default="medium")
    status = Column(String, default="pending")
    assigned_to = Column(String)
    assigned_role = Column(String)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(DateTime)
    metadata = Column(JSON)
    constitutional_requirements = Column(JSON)
    constitutional_hash = Column(String, default=CONSTITUTIONAL_HASH)

class ReviewSubmissionDB(Base):
    __tablename__ = "review_submissions"
    
    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False)
    reviewer_id = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    confidence = Column(Integer)  # Store as percentage
    reasoning = Column(Text, nullable=False)
    detailed_feedback = Column(Text)
    constitutional_compliance = Column(JSON)
    flags = Column(JSON)
    recommendations = Column(JSON)
    time_spent_minutes = Column(Integer)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    constitutional_hash = Column(String, default=CONSTITUTIONAL_HASH)

class ReviewerProfileDB(Base):
    __tablename__ = "reviewer_profiles"
    
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    specializations = Column(JSON)
    certification_level = Column(String)
    active = Column(Boolean, default=True)
    availability = Column(JSON)
    performance_metrics = Column(JSON)
    constitutional_training = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    constitutional_hash = Column(String, default=CONSTITUTIONAL_HASH)

class ReviewManager:
    """
    Manages review tasks, assignments, and workflow with constitutional compliance.
    """
    
    def __init__(self, 
                 database_url: str = "sqlite:///review_system.db",
                 redis_url: str = "redis://localhost:6379/3"):
        """Initialize review manager with database and Redis."""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Database setup
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Redis for caching and notifications
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Assignment algorithm weights
        self.assignment_weights = {
            "workload": 0.4,
            "expertise": 0.3,
            "performance": 0.2,
            "availability": 0.1
        }
        
        logger.info("ReviewManager initialized")
    
    async def create_task(self, request: ReviewTaskRequest, created_by: str) -> ReviewTask:
        """Create a new review task."""
        try:
            task = ReviewTask(
                title=request.title,
                description=request.description,
                content_type=request.content_type,
                content_data=request.content_data,
                priority=request.priority,
                assigned_role=request.required_role,
                created_by=created_by,
                due_date=request.due_date,
                metadata=request.metadata,
                constitutional_requirements=request.constitutional_requirements,
                constitutional_hash=self.constitutional_hash
            )
            
            # Save to database
            with self.SessionLocal() as db:
                db_task = ReviewTaskDB(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    content_type=task.content_type.value,
                    content_data=task.content_data,
                    priority=task.priority.value,
                    status=task.status.value,
                    assigned_role=task.assigned_role.value if task.assigned_role else None,
                    created_by=task.created_by,
                    due_date=task.due_date,
                    metadata=task.metadata,
                    constitutional_requirements=task.constitutional_requirements,
                    constitutional_hash=task.constitutional_hash
                )
                db.add(db_task)
                db.commit()
            
            # Cache task for quick access
            await self._cache_task(task)
            
            # Auto-assign if no specific role required
            if not request.required_role:
                await self._auto_assign_task(task)
            
            logger.info(f"Created review task: {task.id}")
            return task
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[ReviewTask]:
        """Get a review task by ID."""
        try:
            # Try cache first
            cached_task = await self._get_cached_task(task_id)
            if cached_task:
                return cached_task
            
            # Get from database
            with self.SessionLocal() as db:
                db_task = db.query(ReviewTaskDB).filter(ReviewTaskDB.id == task_id).first()
                
                if not db_task:
                    return None
                
                task = ReviewTask(
                    id=db_task.id,
                    title=db_task.title,
                    description=db_task.description,
                    content_type=ContentType(db_task.content_type),
                    content_data=db_task.content_data or {},
                    priority=ReviewPriority(db_task.priority),
                    status=ReviewStatus(db_task.status),
                    assigned_to=db_task.assigned_to,
                    assigned_role=ReviewerRole(db_task.assigned_role) if db_task.assigned_role else None,
                    created_by=db_task.created_by,
                    created_at=db_task.created_at,
                    updated_at=db_task.updated_at,
                    due_date=db_task.due_date,
                    metadata=db_task.metadata or {},
                    constitutional_requirements=db_task.constitutional_requirements or {},
                    constitutional_hash=db_task.constitutional_hash
                )
                
                # Cache for future access
                await self._cache_task(task)
                
                return task
            
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None
    
    async def assign_task(self, task_id: str, reviewer_id: str) -> bool:
        """Assign a task to a reviewer."""
        try:
            with self.SessionLocal() as db:
                db_task = db.query(ReviewTaskDB).filter(ReviewTaskDB.id == task_id).first()
                
                if not db_task:
                    return False
                
                # Check if reviewer is available and qualified
                if not await self._is_reviewer_available(reviewer_id, db_task.assigned_role):
                    return False
                
                # Update assignment
                db_task.assigned_to = reviewer_id
                db_task.status = ReviewStatus.IN_PROGRESS.value
                db_task.updated_at = datetime.utcnow()
                
                db.commit()
                
                # Update cache
                await self._invalidate_task_cache(task_id)
                
                # Send notification
                await self._notify_reviewer_assignment(reviewer_id, task_id)
                
                logger.info(f"Assigned task {task_id} to reviewer {reviewer_id}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to assign task {task_id}: {e}")
            return False
    
    async def submit_review(self, submission: ReviewSubmission) -> bool:
        """Submit a review for a task."""
        try:
            # Validate submission
            if submission.constitutional_hash != self.constitutional_hash:
                raise ValueError("Invalid constitutional hash")
            
            # Save submission
            with self.SessionLocal() as db:
                db_submission = ReviewSubmissionDB(
                    id=submission.id,
                    task_id=submission.task_id,
                    reviewer_id=submission.reviewer_id,
                    decision=submission.decision.value,
                    confidence=int(submission.confidence * 100),
                    reasoning=submission.reasoning,
                    detailed_feedback=submission.detailed_feedback,
                    constitutional_compliance=submission.constitutional_compliance,
                    flags=submission.flags,
                    recommendations=submission.recommendations,
                    time_spent_minutes=submission.time_spent_minutes,
                    constitutional_hash=submission.constitutional_hash
                )
                db.add(db_submission)
                
                # Update task status
                db_task = db.query(ReviewTaskDB).filter(ReviewTaskDB.id == submission.task_id).first()
                if db_task:
                    if submission.decision == ReviewDecision.ESCALATE:
                        db_task.status = ReviewStatus.ESCALATED.value
                    elif submission.decision in [ReviewDecision.APPROVE, ReviewDecision.REJECT]:
                        db_task.status = ReviewStatus.COMPLETED.value
                    
                    db_task.updated_at = datetime.utcnow()
                
                db.commit()
            
            # Update caches
            await self._invalidate_task_cache(submission.task_id)
            await self._update_reviewer_performance(submission.reviewer_id, submission)
            
            # Send notifications
            await self._notify_review_completion(submission)
            
            logger.info(f"Submitted review for task {submission.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit review: {e}")
            return False
    
    async def get_reviewer_workload(self, reviewer_id: str) -> List[ReviewTask]:
        """Get active tasks for a reviewer."""
        try:
            with self.SessionLocal() as db:
                db_tasks = db.query(ReviewTaskDB).filter(
                    ReviewTaskDB.assigned_to == reviewer_id,
                    ReviewTaskDB.status.in_([ReviewStatus.PENDING.value, ReviewStatus.IN_PROGRESS.value])
                ).order_by(ReviewTaskDB.priority.desc(), ReviewTaskDB.created_at).all()
                
                tasks = []
                for db_task in db_tasks:
                    task = ReviewTask(
                        id=db_task.id,
                        title=db_task.title,
                        description=db_task.description,
                        content_type=ContentType(db_task.content_type),
                        content_data=db_task.content_data or {},
                        priority=ReviewPriority(db_task.priority),
                        status=ReviewStatus(db_task.status),
                        assigned_to=db_task.assigned_to,
                        assigned_role=ReviewerRole(db_task.assigned_role) if db_task.assigned_role else None,
                        created_by=db_task.created_by,
                        created_at=db_task.created_at,
                        updated_at=db_task.updated_at,
                        due_date=db_task.due_date,
                        metadata=db_task.metadata or {},
                        constitutional_requirements=db_task.constitutional_requirements or {},
                        constitutional_hash=db_task.constitutional_hash
                    )
                    tasks.append(task)
                
                return tasks
            
        except Exception as e:
            logger.error(f"Failed to get workload for reviewer {reviewer_id}: {e}")
            return []
    
    async def get_analytics(self) -> ReviewAnalytics:
        """Get review system analytics."""
        try:
            with self.SessionLocal() as db:
                # Total tasks
                total_tasks = db.query(ReviewTaskDB).count()
                
                # Pending tasks
                pending_tasks = db.query(ReviewTaskDB).filter(
                    ReviewTaskDB.status == ReviewStatus.PENDING.value
                ).count()
                
                # Completed tasks
                completed_tasks = db.query(ReviewTaskDB).filter(
                    ReviewTaskDB.status == ReviewStatus.COMPLETED.value
                ).count()
                
                # Approval rate
                approved_count = db.query(ReviewSubmissionDB).filter(
                    ReviewSubmissionDB.decision == ReviewDecision.APPROVE.value
                ).count()
                
                total_submissions = db.query(ReviewSubmissionDB).count()
                approval_rate = approved_count / total_submissions if total_submissions > 0 else 0.0
                
                # Priority distribution
                priority_distribution = {}
                for priority in ReviewPriority:
                    count = db.query(ReviewTaskDB).filter(
                        ReviewTaskDB.priority == priority.value
                    ).count()
                    priority_distribution[priority.value] = count
                
                # Content type distribution
                content_type_distribution = {}
                for content_type in ContentType:
                    count = db.query(ReviewTaskDB).filter(
                        ReviewTaskDB.content_type == content_type.value
                    ).count()
                    content_type_distribution[content_type.value] = count
                
                return ReviewAnalytics(
                    total_tasks=total_tasks,
                    pending_tasks=pending_tasks,
                    completed_tasks=completed_tasks,
                    avg_completion_time_hours=24.0,  # Mock value
                    approval_rate=approval_rate,
                    constitutional_compliance_rate=0.95,  # Mock value
                    priority_distribution=priority_distribution,
                    content_type_distribution=content_type_distribution,
                    constitutional_hash=self.constitutional_hash
                )
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return ReviewAnalytics(
                total_tasks=0,
                pending_tasks=0,
                completed_tasks=0,
                avg_completion_time_hours=0.0,
                approval_rate=0.0,
                constitutional_compliance_rate=0.0,
                constitutional_hash=self.constitutional_hash
            )
    
    async def _auto_assign_task(self, task: ReviewTask) -> bool:
        """Auto-assign task to best available reviewer."""
        try:
            # Get available reviewers
            available_reviewers = await self._get_available_reviewers(task.assigned_role)
            
            if not available_reviewers:
                return False
            
            # Score reviewers based on multiple criteria
            best_reviewer = None
            best_score = 0.0
            
            for reviewer in available_reviewers:
                score = await self._calculate_reviewer_score(reviewer, task)
                if score > best_score:
                    best_score = score
                    best_reviewer = reviewer
            
            if best_reviewer:
                return await self.assign_task(task.id, best_reviewer.user_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Auto-assignment failed: {e}")
            return False
    
    async def _get_available_reviewers(self, required_role: Optional[ReviewerRole]) -> List[ReviewerProfile]:
        """Get available reviewers with optional role filtering."""
        try:
            with self.SessionLocal() as db:
                query = db.query(ReviewerProfileDB).filter(ReviewerProfileDB.active == True)
                
                if required_role:
                    query = query.filter(ReviewerProfileDB.role == required_role.value)
                
                db_reviewers = query.all()
                
                reviewers = []
                for db_reviewer in db_reviewers:
                    reviewer = ReviewerProfile(
                        user_id=db_reviewer.user_id,
                        name=db_reviewer.name,
                        email=db_reviewer.email,
                        role=ReviewerRole(db_reviewer.role),
                        specializations=db_reviewer.specializations or [],
                        certification_level=db_reviewer.certification_level,
                        active=db_reviewer.active,
                        availability=db_reviewer.availability or {},
                        performance_metrics=db_reviewer.performance_metrics or {},
                        constitutional_training=db_reviewer.constitutional_training or {},
                        created_at=db_reviewer.created_at,
                        updated_at=db_reviewer.updated_at,
                        constitutional_hash=db_reviewer.constitutional_hash
                    )
                    reviewers.append(reviewer)
                
                return reviewers
            
        except Exception as e:
            logger.error(f"Failed to get available reviewers: {e}")
            return []
    
    async def _calculate_reviewer_score(self, reviewer: ReviewerProfile, task: ReviewTask) -> float:
        """Calculate reviewer assignment score."""
        try:
            score = 0.0
            
            # Workload factor (fewer active tasks = higher score)
            active_tasks = len(await self.get_reviewer_workload(reviewer.user_id))
            workload_score = max(0.0, 1.0 - (active_tasks / 10.0))
            score += workload_score * self.assignment_weights["workload"]
            
            # Expertise factor
            expertise_score = 0.5  # Base score
            if task.content_type.value in reviewer.specializations:
                expertise_score = 1.0
            score += expertise_score * self.assignment_weights["expertise"]
            
            # Performance factor
            performance_score = reviewer.performance_metrics.get("overall_rating", 0.5)
            score += performance_score * self.assignment_weights["performance"]
            
            # Availability factor
            availability_score = 1.0 if reviewer.availability.get("available", True) else 0.0
            score += availability_score * self.assignment_weights["availability"]
            
            return score
            
        except Exception as e:
            logger.error(f"Failed to calculate reviewer score: {e}")
            return 0.0
    
    async def _is_reviewer_available(self, reviewer_id: str, required_role: Optional[str]) -> bool:
        """Check if reviewer is available and qualified."""
        try:
            with self.SessionLocal() as db:
                reviewer = db.query(ReviewerProfileDB).filter(
                    ReviewerProfileDB.user_id == reviewer_id,
                    ReviewerProfileDB.active == True
                ).first()
                
                if not reviewer:
                    return False
                
                if required_role and reviewer.role != required_role:
                    return False
                
                return True
            
        except Exception as e:
            logger.error(f"Failed to check reviewer availability: {e}")
            return False
    
    async def _cache_task(self, task: ReviewTask):
        """Cache task for quick access."""
        try:
            task_key = f"task:{task.id}"
            task_data = task.dict()
            self.redis_client.setex(task_key, 3600, json.dumps(task_data, default=str))
        except Exception as e:
            logger.error(f"Failed to cache task: {e}")
    
    async def _get_cached_task(self, task_id: str) -> Optional[ReviewTask]:
        """Get task from cache."""
        try:
            task_key = f"task:{task_id}"
            cached_data = self.redis_client.get(task_key)
            
            if cached_data:
                task_data = json.loads(cached_data)
                return ReviewTask(**task_data)
            
            return None
        except Exception as e:
            logger.error(f"Failed to get cached task: {e}")
            return None
    
    async def _invalidate_task_cache(self, task_id: str):
        """Invalidate task cache."""
        try:
            task_key = f"task:{task_id}"
            self.redis_client.delete(task_key)
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
    
    async def _notify_reviewer_assignment(self, reviewer_id: str, task_id: str):
        """Notify reviewer of task assignment."""
        try:
            # TODO: Implement notification system
            logger.info(f"Notifying reviewer {reviewer_id} of task {task_id}")
        except Exception as e:
            logger.error(f"Failed to notify reviewer: {e}")
    
    async def _notify_review_completion(self, submission: ReviewSubmission):
        """Notify stakeholders of review completion."""
        try:
            # TODO: Implement notification system
            logger.info(f"Notifying completion of task {submission.task_id}")
        except Exception as e:
            logger.error(f"Failed to notify completion: {e}")
    
    async def _update_reviewer_performance(self, reviewer_id: str, submission: ReviewSubmission):
        """Update reviewer performance metrics."""
        try:
            # TODO: Implement performance tracking
            logger.info(f"Updating performance for reviewer {reviewer_id}")
        except Exception as e:
            logger.error(f"Failed to update performance: {e}")