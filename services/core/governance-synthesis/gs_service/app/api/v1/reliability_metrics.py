from typing import Any

from fastapi import APIRouter, HTTPException

from .core.llm_reliability_framework import (

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    EnhancedLLMReliabilityFramework,
)

router = APIRouter()

# In a real application, you would likely have a singleton instance
# of the framework or inject it via dependency injection.
# For simplicity, we'll create an instance here.
# This assumes the framework is initialized elsewhere or can be initialized on demand.
llm_reliability_framework_instance = EnhancedLLMReliabilityFramework()


@router.get("/reliability_metrics", response_model=dict[str, Any])
async def get_reliability_metrics():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Retrieves the current reliability metrics from the LLM Reliability Framework.
    """
    try:
        summary = llm_reliability_framework_instance.get_performance_summary()
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve reliability metrics: {e}"
        )


@router.get("/reliability_metrics/history", response_model=dict[str, Any])
async def get_reliability_metrics_history():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Retrieves the historical reliability metrics from the LLM Reliability Framework.
    """
    try:
        # Assuming performance_metrics stores a list of ReliabilityMetrics objects
        # We need to convert these dataclasses to dictionaries for JSON serialization
        history_data = [
            metric.__dict__
            for metric in llm_reliability_framework_instance.performance_metrics
        ]
        return {"history": history_data}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve historical reliability metrics: {e}",
        )
