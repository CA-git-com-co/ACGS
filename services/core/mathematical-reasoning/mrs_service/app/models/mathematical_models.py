"""
Mathematical reasoning data models for ACGS-PGP v8 integration.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class ProblemType(str, Enum):
    """Mathematical problem types supported by the system."""
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    CALCULUS = "calculus"
    STATISTICS = "statistics"
    OPTIMIZATION = "optimization"
    LINEAR_ALGEBRA = "linear_algebra"
    DIFFERENTIAL_EQUATIONS = "differential_equations"
    PROBABILITY = "probability"
    NUMBER_THEORY = "number_theory"
    COMBINATORICS = "combinatorics"
    GRAPH_THEORY = "graph_theory"
    POLICY_MATHEMATICS = "policy_mathematics"
    GOVERNANCE_OPTIMIZATION = "governance_optimization"


class SolutionStatus(str, Enum):
    """Status of mathematical solution processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    VALIDATION_REQUIRED = "validation_required"


class ComplianceLevel(str, Enum):
    """Constitutional compliance levels."""
    FULL_COMPLIANCE = "full_compliance"
    PARTIAL_COMPLIANCE = "partial_compliance"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"


class MathematicalProblem(BaseModel):
    """Mathematical problem specification."""
    
    problem_id: UUID = Field(default_factory=uuid4)
    content: str = Field(..., description="Mathematical problem statement")
    problem_type: ProblemType = Field(..., description="Type of mathematical problem")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional problem context")
    
    # Execution parameters
    max_code_executions: int = Field(default=8, ge=1, le=16, description="Maximum code executions allowed")
    timeout_ms: int = Field(default=30000, ge=1000, le=60000, description="Timeout in milliseconds")
    
    # Constitutional compliance requirements
    require_constitutional_compliance: bool = Field(default=True, description="Require constitutional compliance validation")
    constitutional_requirements: Optional[Dict[str, Any]] = Field(default=None, description="Specific constitutional requirements")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(default=None, description="User who created the problem")
    priority: int = Field(default=5, ge=1, le=10, description="Problem priority (1=lowest, 10=highest)")


class CodeExecution(BaseModel):
    """Code execution result within mathematical reasoning."""
    
    execution_id: UUID = Field(default_factory=uuid4)
    code_content: str = Field(..., description="Executed code content")
    execution_output: str = Field(..., description="Code execution output")
    execution_error: Optional[str] = Field(default=None, description="Execution error if any")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    memory_usage_mb: Optional[float] = Field(default=None, description="Memory usage in MB")
    success: bool = Field(..., description="Whether execution was successful")


class ConstitutionalCompliance(BaseModel):
    """Constitutional compliance assessment for mathematical solutions."""
    
    compliance_level: ComplianceLevel = Field(..., description="Overall compliance level")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Compliance score (0-1)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment")
    
    # Detailed compliance analysis
    fairness_score: float = Field(..., ge=0.0, le=1.0, description="Mathematical fairness assessment")
    transparency_score: float = Field(..., ge=0.0, le=1.0, description="Calculation transparency")
    accountability_score: float = Field(..., ge=0.0, le=1.0, description="Algorithmic accountability")
    privacy_score: float = Field(..., ge=0.0, le=1.0, description="Privacy preservation")
    
    # Compliance details
    violations: List[str] = Field(default_factory=list, description="Constitutional violations identified")
    recommendations: List[str] = Field(default_factory=list, description="Compliance improvement recommendations")
    review_required: bool = Field(default=False, description="Whether human review is required")
    
    assessed_at: datetime = Field(default_factory=datetime.now)
    assessed_by: str = Field(default="constitutional_analyzer", description="Assessment system")


class MathematicalSolution(BaseModel):
    """Complete mathematical solution with reasoning and compliance."""
    
    solution_id: UUID = Field(default_factory=uuid4)
    problem_id: UUID = Field(..., description="Associated problem ID")
    
    # Solution content
    solution_content: str = Field(..., description="Mathematical solution text")
    reasoning_steps: List[str] = Field(default_factory=list, description="Step-by-step reasoning")
    final_answer: str = Field(..., description="Final mathematical answer")
    
    # Code executions
    code_executions: List[CodeExecution] = Field(default_factory=list, description="Code execution results")
    
    # Validation and accuracy
    is_correct: Optional[bool] = Field(default=None, description="Solution correctness (if validated)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Solution confidence")
    mathematical_validity: bool = Field(..., description="Mathematical validity check")
    
    # Constitutional compliance
    constitutional_compliance: Optional[ConstitutionalCompliance] = Field(default=None, description="Constitutional compliance assessment")
    
    # Performance metrics
    total_execution_time_ms: int = Field(..., description="Total execution time")
    memory_usage_mb: float = Field(..., description="Peak memory usage")
    tokens_used: int = Field(..., description="LLM tokens consumed")
    
    # Status and metadata
    status: SolutionStatus = Field(default=SolutionStatus.COMPLETED)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)


class PolicyAnalysisRequest(BaseModel):
    """Request for mathematical analysis of policy proposals."""
    
    policy_id: UUID = Field(..., description="Policy identifier")
    policy_content: str = Field(..., description="Policy text content")
    policy_type: str = Field(..., description="Type of policy")
    
    # Mathematical context
    mathematical_context: Dict[str, Any] = Field(..., description="Mathematical data and constraints")
    numerical_requirements: Dict[str, Any] = Field(default_factory=dict, description="Numerical requirements")
    optimization_objectives: List[str] = Field(default_factory=list, description="Optimization objectives")
    
    # Compliance requirements
    compliance_requirements: List[str] = Field(default_factory=list, description="Constitutional compliance requirements")
    
    # Analysis parameters
    analysis_depth: str = Field(default="standard", description="Analysis depth: basic, standard, comprehensive")
    include_risk_assessment: bool = Field(default=True, description="Include mathematical risk assessment")
    
    # Metadata
    requested_by: Optional[str] = Field(default=None, description="User requesting analysis")
    requested_at: datetime = Field(default_factory=datetime.now)


class PolicyAnalysisResult(BaseModel):
    """Result of mathematical policy analysis."""
    
    analysis_id: UUID = Field(default_factory=uuid4)
    policy_id: UUID = Field(..., description="Associated policy ID")
    
    # Mathematical analysis results
    mathematical_validity: bool = Field(..., description="Mathematical validity of policy")
    quantitative_impact: Dict[str, float] = Field(..., description="Quantitative impact metrics")
    risk_assessment: Dict[str, Any] = Field(..., description="Mathematical risk assessment")
    optimization_recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    
    # Constitutional compliance
    constitutional_compliance: ConstitutionalCompliance = Field(..., description="Constitutional compliance assessment")
    
    # Generated mathematical rules
    mathematical_policy_rules: List[str] = Field(default_factory=list, description="Generated mathematical policy rules")
    
    # Performance and confidence
    analysis_confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence score")
    execution_time_ms: int = Field(..., description="Analysis execution time")
    
    # Status and metadata
    status: str = Field(default="completed", description="Analysis status")
    analyzed_at: datetime = Field(default_factory=datetime.now)
    analyzed_by: str = Field(default="constitutional_math_analyzer", description="Analysis system")


class QuantitativeComplianceRequest(BaseModel):
    """Request for quantitative compliance validation."""
    
    governance_action_id: UUID = Field(..., description="Governance action identifier")
    governance_decision: Dict[str, Any] = Field(..., description="Governance decision data")
    mathematical_model: str = Field(..., description="Mathematical model to use for validation")
    
    # Validation parameters
    confidence_threshold: float = Field(default=0.95, ge=0.5, le=1.0, description="Required confidence threshold")
    validation_criteria: List[str] = Field(default_factory=list, description="Specific validation criteria")
    
    # Context
    stakeholder_data: Dict[str, Any] = Field(default_factory=dict, description="Stakeholder impact data")
    historical_data: Dict[str, Any] = Field(default_factory=dict, description="Historical governance data")
    
    # Metadata
    requested_by: Optional[str] = Field(default=None, description="User requesting validation")
    requested_at: datetime = Field(default_factory=datetime.now)


class QuantitativeComplianceResult(BaseModel):
    """Result of quantitative compliance validation."""
    
    validation_id: UUID = Field(default_factory=uuid4)
    governance_action_id: UUID = Field(..., description="Associated governance action ID")
    
    # Compliance results
    is_compliant: bool = Field(..., description="Overall compliance status")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Quantitative compliance score")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Validation confidence")
    
    # Detailed metrics
    quantitative_metrics: Dict[str, float] = Field(..., description="Detailed quantitative metrics")
    mathematical_proofs: List[str] = Field(default_factory=list, description="Mathematical proofs of compliance")
    violation_indicators: List[str] = Field(default_factory=list, description="Compliance violation indicators")
    
    # Recommendations
    improvement_recommendations: List[str] = Field(default_factory=list, description="Compliance improvement recommendations")
    alternative_approaches: List[str] = Field(default_factory=list, description="Alternative mathematical approaches")
    
    # Performance
    validation_time_ms: int = Field(..., description="Validation execution time")
    model_accuracy: float = Field(..., ge=0.0, le=1.0, description="Mathematical model accuracy")
    
    # Status and metadata
    validated_at: datetime = Field(default_factory=datetime.now)
    validated_by: str = Field(default="quantitative_governance_engine", description="Validation system")


class MathematicalCapabilities(BaseModel):
    """Available mathematical reasoning capabilities."""
    
    supported_problem_types: List[str] = Field(..., description="Supported mathematical problem types")
    supported_benchmarks: List[str] = Field(..., description="Available evaluation benchmarks")
    server_backends: List[str] = Field(..., description="Available inference backends")
    
    # Configuration limits
    max_code_executions: int = Field(..., description="Maximum code executions per problem")
    max_timeout_ms: int = Field(..., description="Maximum timeout in milliseconds")
    concurrent_request_capacity: int = Field(..., description="Concurrent request handling capacity")
    
    # Feature availability
    constitutional_compliance_enabled: bool = Field(..., description="Constitutional compliance validation available")
    quantitative_governance_enabled: bool = Field(..., description="Quantitative governance analysis available")
    caching_enabled: bool = Field(..., description="Result caching enabled")
    
    # Performance characteristics
    average_response_time_ms: Optional[int] = Field(default=None, description="Average response time")
    accuracy_benchmarks: Dict[str, float] = Field(default_factory=dict, description="Accuracy on standard benchmarks")


class ServiceHealthStatus(BaseModel):
    """Service health status information."""
    
    status: str = Field(..., description="Overall service status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(default=0, description="Service uptime in seconds")
    
    # Component health
    components: Dict[str, str] = Field(default_factory=dict, description="Individual component health status")
    
    # Performance metrics
    active_requests: int = Field(default=0, description="Number of active requests")
    total_requests_processed: int = Field(default=0, description="Total requests processed")
    average_response_time_ms: float = Field(default=0, description="Average response time")
    
    # Error information
    error_message: Optional[str] = Field(default=None, description="Error message if unhealthy")
    last_error_at: Optional[datetime] = Field(default=None, description="Last error timestamp")


# Validation functions
@validator('confidence_score', 'compliance_score', pre=True, always=True)
def validate_score_range(cls, v):
    """Ensure scores are within valid range [0, 1]."""
    if v is not None and (v < 0.0 or v > 1.0):
        raise ValueError('Score must be between 0.0 and 1.0')
    return v
