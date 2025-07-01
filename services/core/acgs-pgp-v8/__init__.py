"""
ACGS-PGP v8: Quantum-Inspired Semantic Fault Tolerance (QEC-SFT) Architecture

This module implements a quantum-inspired policy generation platform that integrates
with the ACGS-1 Constitutional Governance System. It provides fault-tolerant policy
generation, semantic validation, and constitutional compliance checking.

Key Components:
- Generation Engine: Policy generation with multi-model LLM ensemble
- Stabilizer Execution Environment: Fault-tolerant execution context
- Syndrome Diagnostic Engine: ML-powered error detection and recovery

Constitution Hash: cdd01ef066bc6cf2
"""

__version__ = "8.0.0"
__author__ = "ACGS-1 Development Team"
__license__ = "MIT"

from .src.generation_engine.engine import GenerationConfig, GenerationEngine
from .src.generation_engine.models import (
    LSU,
    Representation,
    RepresentationSet,
    RepresentationType,
)
from .src.sde.engine import SyndromeDiagnosticEngine
from .src.see.environment import StabilizerExecutionEnvironment
from .src.see.models import StabilizerResult, StabilizerStatus, SyndromeVector

__all__ = [
    "LSU",
    "GenerationConfig",
    "GenerationEngine",
    "Representation",
    "RepresentationSet",
    "RepresentationType",
    "StabilizerExecutionEnvironment",
    "StabilizerResult",
    "StabilizerStatus",
    "SyndromeDiagnosticEngine",
    "SyndromeVector",
]
