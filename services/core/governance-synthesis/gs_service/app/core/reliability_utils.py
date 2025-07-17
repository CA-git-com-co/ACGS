"""
Reliability Framework Utility Functions

Extracted from LLM Reliability Framework for better code organization
Constitutional Hash: cdd01ef066bc6cf2
"""

import hashlib
import json
import logging
import statistics
from math import sqrt
from typing import Any, Dict, List, Optional

from .reliability_enums import CONSTITUTIONAL_HASH

logger = logging.getLogger(__name__)


def calculate_wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """
    Calculate Wilson score interval for reliability confidence bounds.
    
    Args:
        successes: Number of successful operations
        trials: Total number of trials
        confidence: Confidence level (default 0.95)
        
    Returns:
        Tuple of (lower_bound, upper_bound) for confidence interval
    """
    if trials == 0:
        return 0.0, 0.0
    
    # Z-score for confidence level
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_scores.get(confidence, 1.96)
    
    p = successes / trials
    n = trials
    
    # Wilson score interval formula
    center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    margin = z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    
    lower_bound = max(0.0, center - margin)
    upper_bound = min(1.0, center + margin)
    
    return lower_bound, upper_bound


def calculate_reliability_score(
    consensus_rate: float,
    bias_score: float,
    semantic_score: float,
    response_time: float,
    max_response_time: float = 30.0,
) -> float:
    """
    Calculate overall reliability score from component metrics.
    
    Args:
        consensus_rate: Rate of consensus achievement (0-1)
        bias_score: Bias detection score (0-1, lower is better)
        semantic_score: Semantic faithfulness score (0-1)
        response_time: Average response time in seconds
        max_response_time: Maximum acceptable response time
        
    Returns:
        Overall reliability score (0-1)
    """
    # Weight factors for different components
    weights = {
        "consensus": 0.35,
        "bias": 0.25,
        "semantic": 0.25,
        "performance": 0.15,
    }
    
    # Calculate performance score (penalty for slow responses)
    performance_score = max(0.0, 1.0 - (response_time / max_response_time))
    
    # Invert bias score (lower bias is better)
    bias_reliability = 1.0 - bias_score
    
    # Calculate weighted score
    reliability_score = (
        weights["consensus"] * consensus_rate +
        weights["bias"] * bias_reliability +
        weights["semantic"] * semantic_score +
        weights["performance"] * performance_score
    )
    
    return max(0.0, min(1.0, reliability_score))


def generate_cache_key(content: str, config_hash: str) -> str:
    """
    Generate a consistent cache key for reliability results.
    
    Args:
        content: Content to be processed
        config_hash: Hash of the configuration
        
    Returns:
        Cache key string
    """
    combined = f"{content}:{config_hash}:{CONSTITUTIONAL_HASH}"
    return hashlib.sha256(combined.encode()).hexdigest()


def calculate_consensus_score(model_outputs: List[str], threshold: float = 0.8) -> float:
    """
    Calculate consensus score from multiple model outputs.
    
    Args:
        model_outputs: List of model output strings
        threshold: Minimum agreement threshold
        
    Returns:
        Consensus score (0-1)
    """
    if len(model_outputs) < 2:
        return 1.0
    
    # Simple string-based consensus (can be enhanced with semantic similarity)
    output_counts = {}
    for output in model_outputs:
        normalized = output.strip().lower()
        output_counts[normalized] = output_counts.get(normalized, 0) + 1
    
    # Find the most common output
    max_count = max(output_counts.values())
    consensus_rate = max_count / len(model_outputs)
    
    return consensus_rate


def calculate_semantic_faithfulness(original: str, processed: str) -> float:
    """
    Calculate semantic faithfulness score between original and processed text.
    
    Args:
        original: Original text
        processed: Processed text
        
    Returns:
        Semantic faithfulness score (0-1)
    """
    # Simple implementation - can be enhanced with semantic embeddings
    if not original or not processed:
        return 0.0
    
    # Basic overlap scoring
    original_words = set(original.lower().split())
    processed_words = set(processed.lower().split())
    
    if not original_words:
        return 0.0
    
    overlap = len(original_words.intersection(processed_words))
    faithfulness = overlap / len(original_words)
    
    return min(1.0, faithfulness)


def calculate_bias_score(content: str, bias_indicators: Optional[List[str]] = None) -> float:
    """
    Calculate bias score for content.
    
    Args:
        content: Content to analyze
        bias_indicators: List of bias indicator patterns
        
    Returns:
        Bias score (0-1, higher means more bias detected)
    """
    if not content:
        return 0.0
    
    # Default bias indicators
    if bias_indicators is None:
        bias_indicators = [
            "always", "never", "all", "none", "everyone", "nobody",
            "definitely", "certainly", "obviously", "clearly",
            "men", "women", "male", "female", "he", "she"
        ]
    
    content_lower = content.lower()
    bias_count = sum(1 for indicator in bias_indicators if indicator in content_lower)
    
    # Normalize by content length
    words = len(content.split())
    if words == 0:
        return 0.0
    
    bias_score = min(1.0, bias_count / words * 10)  # Scale factor
    return bias_score


def validate_constitutional_hash(provided_hash: str) -> bool:
    """
    Validate that the provided hash matches the constitutional hash.
    
    Args:
        provided_hash: Hash to validate
        
    Returns:
        True if hash is valid, False otherwise
    """
    return provided_hash == CONSTITUTIONAL_HASH


def create_metrics_summary(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a summary of reliability metrics.
    
    Args:
        metrics: Raw metrics dictionary
        
    Returns:
        Summarized metrics dictionary
    """
    summary = {
        "overall_health": "healthy",
        "reliability_score": metrics.get("overall_reliability_score", 0.0),
        "total_requests": metrics.get("total_requests", 0),
        "failure_rate": 0.0,
        "average_response_time": metrics.get("average_response_time", 0.0),
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }
    
    # Calculate failure rate
    total_requests = metrics.get("total_requests", 0)
    failed_requests = metrics.get("failed_requests", 0)
    
    if total_requests > 0:
        failure_rate = failed_requests / total_requests
        summary["failure_rate"] = failure_rate
        
        # Determine health status
        if failure_rate > 0.1:
            summary["overall_health"] = "degraded"
        elif failure_rate > 0.05:
            summary["overall_health"] = "warning"
    
    return summary