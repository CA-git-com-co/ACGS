"""
Formal Verification Service Data Models

Core data models for formal verification processes, proof generation,
constitutional compliance validation, and Z3 SMT solver integration.
"""

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

from .constitutional import (
    ConstitutionalProof,
    ConstitutionalVerificationRequest,
    ConstitutionalVerificationResult,
    PolicyValidationRequest,
    PolicyValidationResult,
)
from .smt import (
    SMTFormula,
    SMTModel,
    SMTResult,
    SMTSolverRequest,
    SMTSolverResponse,
    Z3ProofResult,
)
from .verification import (
    ProofObligation,
    ProofResult,
    ProofStatus,
    VerificationRequest,
    VerificationResult,
    VerificationStatus,
)

__all__ = [
    "ConstitutionalProof",
    "ConstitutionalVerificationRequest",
    "ConstitutionalVerificationResult",
    "PolicyValidationRequest",
    "PolicyValidationResult",
    "ProofObligation",
    "ProofResult",
    "ProofStatus",
    "SMTFormula",
    "SMTModel",
    "SMTResult",
    "SMTSolverRequest",
    "SMTSolverResponse",
    "VerificationRequest",
    "VerificationResult",
    "VerificationStatus",
    "Z3ProofResult",
]
