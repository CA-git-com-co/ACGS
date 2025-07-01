"""
Quantum Computing Module for ACGS-PGP v8

Provides quantum-inspired error correction and semantic fault tolerance
using real quantum computing principles and algorithms.
"""

from .qec_engine import (
    QuantumErrorCorrectionEngine,
    QuantumState,
    StabilizerCode,
)

__all__ = [
    "QuantumErrorCorrectionEngine",
    "QuantumState",
    "StabilizerCode",
]
