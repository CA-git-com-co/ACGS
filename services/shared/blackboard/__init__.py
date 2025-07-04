"""
Blackboard service for multi-agent coordination in ACGS.

This module provides a modular blackboard system with focused components:
- BlackboardService: Main coordination service
- KnowledgeManager: Knowledge storage and retrieval
- TaskManager: Task lifecycle management
- ConflictManager: Conflict detection and resolution
- EventPublisher: Event notification system

Example:
    from services.shared.blackboard import BlackboardService, KnowledgeItem
    
    service = BlackboardService()
    await service.initialize()
    
    knowledge = KnowledgeItem(
        space="governance",
        agent_id="ethics_agent",
        knowledge_type="policy",
        content={"rule": "transparency"}
    )
    await service.add_knowledge(knowledge)
"""

from .conflict_manager import ConflictManager
from .core_service import BlackboardService
from .event_publisher import EventPublisher
from .knowledge_manager import KnowledgeManager
from .models import ConflictItem, KnowledgeItem, TaskDefinition
from .task_manager import TaskManager

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


__all__ = [
    "BlackboardService",
    "ConflictItem",
    "ConflictManager",
    "EventPublisher",
    "KnowledgeItem",
    "KnowledgeManager",
    "TaskDefinition",
    "TaskManager",
]
