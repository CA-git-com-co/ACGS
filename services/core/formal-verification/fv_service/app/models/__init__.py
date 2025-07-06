"""
Formal Verification Service Data Models

Core data models for formal verification processes, proof generation,
constitutional compliance validation, and Z3 SMT solver integration.
"""

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

from .verification import (
    ProofObligation,
    ProofResult,
    ProofStatus,
    VerificationRequest,
    VerificationResult,
    VerificationStatus,
)
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

__all__ = [
    "ProofObligation",
    "ProofResult",
    "ProofStatus",
    "VerificationRequest",
    "VerificationResult",
    "VerificationStatus",
    "ConstitutionalProof",
    "ConstitutionalVerificationRequest",
    "ConstitutionalVerificationResult",
    "PolicyValidationRequest",
    "PolicyValidationResult",
    "SMTFormula",
    "SMTModel",
    "SMTResult",
    "SMTSolverRequest",
    "SMTSolverResponse",
    "Z3ProofResult",
]
