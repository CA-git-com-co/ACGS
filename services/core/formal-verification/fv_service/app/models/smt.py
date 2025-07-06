"""
SMT Solver Data Models

Data models for SMT solver integration, Z3 proof generation,
and satisfiability checking with constitutional compliance.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class SMTSolverType(str, Enum):
    """Types of SMT solvers."""
    Z3 = "z3"
    CVC4 = "cvc4"
    YICES = "yices"
    MATHSAT = "mathsat"


class SMTResult(str, Enum):
    """SMT solver results."""
    SAT = "sat"
    UNSAT = "unsat"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"
    ERROR = "error"


class SMTLogic(str, Enum):
    """SMT-LIB logics."""
    QF_LIA = "QF_LIA"  # Quantifier-free linear integer arithmetic
    QF_LRA = "QF_LRA"  # Quantifier-free linear real arithmetic
    QF_NIA = "QF_NIA"  # Quantifier-free non-linear integer arithmetic
    QF_NRA = "QF_NRA"  # Quantifier-free non-linear real arithmetic
    QF_BV = "QF_BV"    # Quantifier-free bit-vectors
    QF_ABV = "QF_ABV"  # Quantifier-free arrays and bit-vectors
    LIA = "LIA"        # Linear integer arithmetic
    LRA = "LRA"        # Linear real arithmetic
    ALL = "ALL"        # All supported theories


class SMTFormula(BaseModel):
    """SMT formula representation."""
    
    formula_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Formula content
    formula: str = Field(..., description="SMT-LIB formula")
    logic: SMTLogic = Field(default=SMTLogic.ALL, description="SMT logic")
    variables: List[str] = Field(default_factory=list, description="Formula variables")
    
    # Formula metadata
    formula_type: str = Field(default="assertion", description="Type of formula")
    complexity_estimate: int = Field(default=1, ge=1, le=10)
    expected_result: Optional[SMTResult] = Field(None, description="Expected solver result")
    
    # Constitutional compliance
    constitutional_relevance: bool = Field(default=False)
    safety_critical: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SMTModel(BaseModel):
    """SMT model (satisfying assignment)."""
    
    model_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    formula_id: str = Field(..., description="Associated formula ID")
    
    # Model content
    assignments: Dict[str, Union[int, float, bool, str]] = Field(
        ..., description="Variable assignments"
    )
    model_string: str = Field(..., description="Model in SMT-LIB format")
    
    # Model validation
    model_valid: bool = Field(..., description="Whether model is valid")
    satisfies_formula: bool = Field(..., description="Whether model satisfies formula")
    
    # Model metrics
    model_size: int = Field(default=0, description="Number of assignments")
    generation_time_ms: float = Field(..., description="Model generation time")
    
    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(..., description="Solver that generated model")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SMTSolverRequest(BaseModel):
    """Request for SMT solver."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    solver_type: SMTSolverType = Field(default=SMTSolverType.Z3)
    
    # Solver input
    formulas: List[SMTFormula] = Field(..., description="Formulas to solve")
    logic: SMTLogic = Field(default=SMTLogic.ALL, description="SMT logic to use")
    
    # Solver parameters
    timeout_ms: int = Field(default=30000, ge=1000, le=300000, description="Solver timeout")
    memory_limit_mb: int = Field(default=1024, ge=128, le=8192, description="Memory limit")
    generate_model: bool = Field(default=True, description="Generate satisfying model")
    generate_proof: bool = Field(default=False, description="Generate unsatisfiability proof")
    
    # Solver options
    solver_options: Dict[str, Any] = Field(
        default_factory=dict, description="Solver-specific options"
    )
    
    # Constitutional compliance
    constitutional_compliance_required: bool = Field(default=True)
    safety_critical: bool = Field(default=False)
    
    # Context
    verification_context: Dict[str, Any] = Field(default_factory=dict)
    requester_id: str = Field(..., description="Requester ID")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Z3ProofResult(BaseModel):
    """Z3 proof result for unsatisfiable formulas."""
    
    proof_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="SMT solver request ID")
    
    # Proof content
    proof_object: str = Field(..., description="Z3 proof object")
    proof_steps: List[str] = Field(default_factory=list, description="Proof steps")
    proof_core: List[str] = Field(default_factory=list, description="Unsatisfiable core")
    
    # Proof validation
    proof_valid: bool = Field(..., description="Whether proof is valid")
    proof_complete: bool = Field(..., description="Whether proof is complete")
    
    # Proof metrics
    proof_size: int = Field(default=0, description="Proof size")
    proof_depth: int = Field(default=0, description="Proof depth")
    generation_time_ms: float = Field(..., description="Proof generation time")
    
    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SMTSolverResponse(BaseModel):
    """Response from SMT solver."""
    
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="SMT solver request ID")
    
    # Solver result
    result: SMTResult = Field(..., description="Solver result")
    solver_used: SMTSolverType = Field(..., description="Solver that was used")
    
    # Result details
    satisfiable: Optional[bool] = Field(None, description="Whether formulas are satisfiable")
    model: Optional[SMTModel] = Field(None, description="Satisfying model if SAT")
    proof: Optional[Z3ProofResult] = Field(None, description="Proof if UNSAT")
    
    # Solver metrics
    solving_time_ms: float = Field(..., description="Solving time in milliseconds")
    memory_used_mb: float = Field(default=0.0, description="Memory used in MB")
    solver_calls: int = Field(default=1, description="Number of solver calls")
    
    # Performance metrics
    formula_complexity: int = Field(default=1, description="Formula complexity estimate")
    solver_efficiency: float = Field(default=0.0, ge=0.0, le=1.0, description="Solver efficiency")
    
    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)
    constitutional_compliance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Error handling
    errors: List[str] = Field(default_factory=list, description="Solver errors")
    warnings: List[str] = Field(default_factory=list, description="Solver warnings")
    
    # Metadata
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
