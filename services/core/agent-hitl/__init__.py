"""
ACGS-2 Agent Human-in-the-Loop (HITL) Service
Constitutional Hash: cdd01ef066bc6cf2

Multi-agent coordination service with human oversight capabilities.
Provides real-time intervention and guidance for AI agent decision-making.
"""

__version__ = "1.0.0"
__constitutional_hash__ = "cdd01ef066bc6cf2"

from .main import AgentHITLService

__all__ = ["AgentHITLService"]