"""
Worker Agents for Multi-Agent Governance System
"""

from .ethics_agent import EthicalAnalysisResult, EthicsAgent
from .legal_agent import LegalAgent, LegalAnalysisResult
from .operational_agent import OperationalAgent, OperationalAnalysisResult

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


__all__ = [
    "EthicalAnalysisResult",
    "EthicsAgent",
    "LegalAgent",
    "LegalAnalysisResult",
    "OperationalAgent",
    "OperationalAnalysisResult",
]
