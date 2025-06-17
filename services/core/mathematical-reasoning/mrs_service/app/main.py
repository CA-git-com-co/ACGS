"""
Mathematical Reasoning Service (MRS) for ACGS-PGP v8
Integrates NeMo-Skills Tool-Integrated Reasoning with constitutional governance.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.config.service_config import get_service_config
from app.services.mathematical_reasoning_engine import MathematicalReasoningEngine
from app.services.constitutional_math_analyzer import ConstitutionalMathAnalyzer
from app.services.quantitative_governance_engine import QuantitativeGovernanceEngine
from app.models.mathematical_models import (
    MathematicalProblem,
    MathematicalSolution,
    PolicyAnalysisRequest,
    PolicyAnalysisResult,
    QuantitativeComplianceRequest,
    QuantitativeComplianceResult,
    MathematicalCapabilities,
    ServiceHealthStatus
)
from services.shared.metrics import get_metrics
from services.shared.auth import get_current_user
from services.shared.logging_config import setup_logging

# Setup logging
logger = setup_logging(__name__)

# Global service instances
mathematical_engine: Optional[MathematicalReasoningEngine] = None
constitutional_analyzer: Optional[ConstitutionalMathAnalyzer] = None
quantitative_engine: Optional[QuantitativeGovernanceEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global mathematical_engine, constitutional_analyzer, quantitative_engine
    
    logger.info("🚀 Starting Mathematical Reasoning Service...")
    
    try:
        # Initialize service configuration
        config = get_service_config()
        
        # Initialize core engines
        mathematical_engine = MathematicalReasoningEngine(config)
        constitutional_analyzer = ConstitutionalMathAnalyzer(config)
        quantitative_engine = QuantitativeGovernanceEngine(config)
        
        # Initialize engines
        await mathematical_engine.initialize()
        await constitutional_analyzer.initialize()
        await quantitative_engine.initialize()
        
        logger.info("✅ Mathematical Reasoning Service initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Mathematical Reasoning Service: {e}")
        raise
    finally:
        logger.info("🔄 Shutting down Mathematical Reasoning Service...")
        
        # Cleanup resources
        if mathematical_engine:
            await mathematical_engine.cleanup()
        if constitutional_analyzer:
            await constitutional_analyzer.cleanup()
        if quantitative_engine:
            await quantitative_engine.cleanup()
        
        logger.info("✅ Mathematical Reasoning Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Mathematical Reasoning Service",
    description="NeMo-Skills integrated mathematical reasoning for ACGS-PGP v8",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=ServiceHealthStatus)
async def health_check():
    """Service health check with detailed status."""
    try:
        # Check engine health
        math_engine_healthy = await mathematical_engine.health_check() if mathematical_engine else False
        constitutional_healthy = await constitutional_analyzer.health_check() if constitutional_analyzer else False
        quantitative_healthy = await quantitative_engine.health_check() if quantitative_engine else False
        
        # Overall health status
        overall_healthy = all([math_engine_healthy, constitutional_healthy, quantitative_healthy])
        
        return ServiceHealthStatus(
            status="healthy" if overall_healthy else "degraded",
            timestamp=datetime.now().isoformat(),
            components={
                "mathematical_engine": "healthy" if math_engine_healthy else "unhealthy",
                "constitutional_analyzer": "healthy" if constitutional_healthy else "unhealthy",
                "quantitative_engine": "healthy" if quantitative_healthy else "unhealthy"
            },
            version="1.0.0",
            uptime_seconds=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return ServiceHealthStatus(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            error_message=str(e),
            version="1.0.0"
        )


# Mathematical reasoning endpoints
@app.post("/math/solve", response_model=MathematicalSolution)
async def solve_mathematical_problem(
    problem: MathematicalProblem,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Solve mathematical problems using NeMo-Skills TIR.
    
    Args:
        problem: Mathematical problem to solve
        background_tasks: Background task queue
        current_user: Authenticated user context
        
    Returns:
        Mathematical solution with constitutional compliance validation
    """
    try:
        if not mathematical_engine:
            raise HTTPException(status_code=503, detail="Mathematical engine not available")
        
        logger.info(f"Solving mathematical problem: {problem.problem_type}")
        
        # Solve the mathematical problem
        solution = await mathematical_engine.solve_problem(
            problem_content=problem.content,
            problem_type=problem.problem_type,
            max_code_executions=problem.max_code_executions,
            timeout_ms=problem.timeout_ms,
            user_context=current_user
        )
        
        # Constitutional compliance validation
        if problem.require_constitutional_compliance:
            compliance_result = await constitutional_analyzer.validate_mathematical_compliance(
                solution=solution,
                constitutional_requirements=problem.constitutional_requirements or {}
            )
            solution.constitutional_compliance = compliance_result
        
        # Record metrics
        metrics = get_metrics()
        metrics.increment_counter(
            "mathematical_problems_solved_total",
            labels={"problem_type": problem.problem_type, "user_id": current_user.get("user_id")}
        )
        
        # Background task for result caching
        background_tasks.add_task(
            mathematical_engine.cache_solution,
            problem.content,
            solution
        )
        
        return solution
        
    except Exception as e:
        logger.error(f"Failed to solve mathematical problem: {e}")
        raise HTTPException(status_code=500, detail=f"Mathematical reasoning failed: {str(e)}")


@app.post("/math/validate", response_model=Dict[str, Any])
async def validate_mathematical_solution(
    problem: MathematicalProblem,
    proposed_solution: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate a proposed mathematical solution.
    
    Args:
        problem: Original mathematical problem
        proposed_solution: Proposed solution to validate
        current_user: Authenticated user context
        
    Returns:
        Validation result with correctness assessment
    """
    try:
        if not mathematical_engine:
            raise HTTPException(status_code=503, detail="Mathematical engine not available")
        
        logger.info(f"Validating mathematical solution for: {problem.problem_type}")
        
        # Validate the proposed solution
        validation_result = await mathematical_engine.validate_solution(
            problem_content=problem.content,
            proposed_solution=proposed_solution,
            problem_type=problem.problem_type,
            user_context=current_user
        )
        
        # Record metrics
        metrics = get_metrics()
        metrics.increment_counter(
            "mathematical_validations_total",
            labels={"problem_type": problem.problem_type, "is_correct": str(validation_result.is_correct)}
        )
        
        return validation_result.dict()
        
    except Exception as e:
        logger.error(f"Failed to validate mathematical solution: {e}")
        raise HTTPException(status_code=500, detail=f"Mathematical validation failed: {str(e)}")


@app.post("/math/policy-analysis", response_model=PolicyAnalysisResult)
async def analyze_policy_mathematics(
    request: PolicyAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze mathematical aspects of policy proposals.
    
    Args:
        request: Policy analysis request with mathematical context
        current_user: Authenticated user context
        
    Returns:
        Mathematical analysis of policy with compliance assessment
    """
    try:
        if not constitutional_analyzer:
            raise HTTPException(status_code=503, detail="Constitutional analyzer not available")
        
        logger.info(f"Analyzing policy mathematics for: {request.policy_id}")
        
        # Analyze mathematical aspects of the policy
        analysis_result = await constitutional_analyzer.analyze_policy_mathematics(
            policy_content=request.policy_content,
            mathematical_context=request.mathematical_context,
            compliance_requirements=request.compliance_requirements,
            user_context=current_user
        )
        
        # Record metrics
        metrics = get_metrics()
        metrics.increment_counter(
            "policy_mathematical_analyses_total",
            labels={"policy_type": request.policy_type, "user_id": current_user.get("user_id")}
        )
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Failed to analyze policy mathematics: {e}")
        raise HTTPException(status_code=500, detail=f"Policy mathematical analysis failed: {str(e)}")


@app.post("/math/quantitative-compliance", response_model=QuantitativeComplianceResult)
async def validate_quantitative_compliance(
    request: QuantitativeComplianceRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate governance decisions using quantitative mathematical models.
    
    Args:
        request: Quantitative compliance validation request
        current_user: Authenticated user context
        
    Returns:
        Quantitative compliance validation result
    """
    try:
        if not quantitative_engine:
            raise HTTPException(status_code=503, detail="Quantitative engine not available")
        
        logger.info(f"Validating quantitative compliance for: {request.governance_action_id}")
        
        # Validate quantitative compliance
        compliance_result = await quantitative_engine.validate_quantitative_compliance(
            governance_decision=request.governance_decision,
            mathematical_model=request.mathematical_model,
            confidence_threshold=request.confidence_threshold,
            user_context=current_user
        )
        
        # Record metrics
        metrics = get_metrics()
        metrics.increment_counter(
            "quantitative_compliance_validations_total",
            labels={
                "action_type": request.governance_decision.get("action_type"),
                "is_compliant": str(compliance_result.is_compliant)
            }
        )
        
        return compliance_result
        
    except Exception as e:
        logger.error(f"Failed to validate quantitative compliance: {e}")
        raise HTTPException(status_code=500, detail=f"Quantitative compliance validation failed: {str(e)}")


@app.get("/math/capabilities", response_model=MathematicalCapabilities)
async def get_mathematical_capabilities():
    """
    Get available mathematical reasoning capabilities.
    
    Returns:
        Available mathematical reasoning capabilities and configurations
    """
    try:
        capabilities = MathematicalCapabilities(
            supported_problem_types=[
                "arithmetic", "algebra", "geometry", "calculus", "statistics",
                "optimization", "linear_algebra", "differential_equations",
                "probability", "number_theory", "combinatorics", "graph_theory"
            ],
            supported_benchmarks=["gsm8k", "math", "aime24", "aime25", "amc23"],
            server_backends=["vllm", "trtllm", "sglang"],
            max_code_executions=16,
            max_timeout_ms=60000,
            constitutional_compliance_enabled=True,
            quantitative_governance_enabled=True,
            caching_enabled=True,
            concurrent_request_capacity=1024
        )
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Failed to get mathematical capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve capabilities: {str(e)}")


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_type": type(exc).__name__}
    )


if __name__ == "__main__":
    # Set start time for uptime calculation
    app.state.start_time = time.time()
    
    # Run the service
    config = get_service_config()
    uvicorn.run(
        "app.main:app",
        host=config.get("service", "host"),
        port=config.get("service", "port"),
        workers=config.get("service", "workers"),
        log_level=config.get("service", "log_level").lower(),
        reload=False  # Disable reload in production
    )
