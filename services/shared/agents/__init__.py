"""
Agents Module for ACGS Agentic Policy Generation Feature

This module contains the core components for dynamic agent creation and
policy generation within the ACGS constitutional AI system.
"""

# Constitutional Hash: cdd01ef066bc6cf2

from .apgf_orchestrator import APGFOrchestrator, PolicyGenerationWorkflow
from .dynamic_agent import AgentCapability, AgentCommunication, AgentTask, DynamicAgent
from .policy_builder import AgentConfig, GeneratedPolicy, PolicyBuilder, ToolConfig
from .tool_router import SafeToolExecutor, ToolDefinition, ToolRegistry, ToolRouter

__all__ = [
    "APGFOrchestrator",
    "AgentCapability",
    "AgentCommunication",
    "AgentConfig",
    "AgentTask",
    "DynamicAgent",
    "GeneratedPolicy",
    "PolicyBuilder",
    "PolicyGenerationWorkflow",
    "SafeToolExecutor",
    "ToolConfig",
    "ToolDefinition",
    "ToolRegistry",
    "ToolRouter",
]
