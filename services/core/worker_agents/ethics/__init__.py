"""
Ethics Agent module for multi-agent governance system.

This module provides specialized ethical analysis and bias assessment
capabilities through focused components:

- EthicsAgent: Main agent orchestrator
- EthicalAnalyzer: Core ethical analysis engine
- BiasDetector: Bias detection algorithms
- FairnessAnalyzer: Fairness evaluation tools

Example:
    from services.core.worker_agents.ethics import EthicsAgent
    
    agent = EthicsAgent()
    await agent.initialize()
    
    result = await agent.analyze_proposal({
        "policy": "data_collection",
        "scope": "user_behavior"
    })
"""

from .analyzers import EthicalAnalyzer
from .detectors import BiasDetector, FairnessAnalyzer
from .ethics_agent import EthicsAgent
from .models import (  # Constitutional compliance hash for ACGS
    CONSTITUTIONAL_HASH,
    BiasAssessment,
    EthicalAnalysisResult,
    FairnessEvaluation,
    HarmAssessment,
    StakeholderImpact,
    "cdd01ef066bc6cf2",
    =,
)

__all__ = [
    "BiasAssessment",
    "BiasDetector",
    "EthicalAnalysisResult",
    "EthicalAnalyzer",
    "EthicsAgent",
    "FairnessAnalyzer",
    "FairnessEvaluation",
    "HarmAssessment",
    "StakeholderImpact",
]
