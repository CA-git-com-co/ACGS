"""
Data models for the Blackboard service.

This module contains all Pydantic models used by the blackboard system
for knowledge items, tasks, and conflicts.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class KnowledgeItem(BaseModel):
    """
    Represents a piece of knowledge on the blackboard.

    Example:
        knowledge = KnowledgeItem(
            space="governance",
            agent_id="ethics_agent_001",
            knowledge_type="policy",
            content={"rule": "no_harm", "confidence": 0.95}
        )
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    space: str  # 'governance', 'compliance', 'performance', 'coordination'
    agent_id: str
    task_id: str | None = None
    knowledge_type: str  # 'task', 'result', 'policy', 'metric', 'conflict'
    content: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = Field(default=1, ge=1, le=5)  # 1=highest, 5=lowest
    expires_at: datetime | None = None
    dependencies: list[str] = Field(default_factory=list)
    tags: set[str] = Field(default_factory=set)


class TaskDefinition(BaseModel):
    """
    Represents a governance task on the blackboard.

    Example:
        task = TaskDefinition(
            task_type="ethical_analysis",
            requirements={"domain": "healthcare"},
            input_data={"proposal": "new_policy.json"}
        )
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    task_type: str  # 'ethical_analysis', 'legal_compliance', 'operational_validation'
    status: str = Field(
        default="pending"
    )  # 'pending', 'claimed', 'in_progress', 'completed', 'failed'
    agent_id: str | None = None  # Agent that claimed the task
    priority: int = Field(default=1, ge=1, le=5)
    requirements: dict[str, Any]
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None = None
    error_details: dict[str, Any] | None = None
    dependencies: list[str] = Field(default_factory=list)
    deadline: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    claimed_at: datetime | None = None
    completed_at: datetime | None = None
    retries: int = 0
    max_retries: int = 3


class ConflictItem(BaseModel):
    """
    Represents a conflict between agents or decisions.

    Example:
        conflict = ConflictItem(
            conflict_type="decision_conflict",
            involved_agents=["ethics_agent", "legal_agent"],
            description="Disagreement on policy interpretation"
        )
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    conflict_type: str  # 'decision_conflict', 'resource_conflict', 'policy_conflict'
    involved_agents: list[str]
    involved_tasks: list[str]
    description: str
    severity: str = "medium"  # 'low', 'medium', 'high', 'critical'
    status: str = "open"  # 'open', 'in_resolution', 'resolved', 'escalated'
    resolution_strategy: str | None = None
    resolution_data: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None
