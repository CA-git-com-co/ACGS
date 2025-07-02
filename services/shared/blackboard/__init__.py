"""
Blackboard Communication System for Multi-Agent Coordination
"""

from .blackboard_service import (
    BlackboardService,
    KnowledgeItem,
    TaskDefinition,
    ConflictItem
)

__all__ = [
    'BlackboardService',
    'KnowledgeItem', 
    'TaskDefinition',
    'ConflictItem'
]