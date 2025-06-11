"""
WINA (Weight Informed Neuron Activation) Integration for ACGS-PGP

This module implements Weight Informed Neuron Activation optimization for LLM inference
within the AlphaEvolve-ACGS framework. WINA provides significant GFLOPs reduction
(40-70%) while maintaining high synthesis accuracy (>95%).

Key Components:
    - WINACore: Core algorithm for neuron weighting and activation
    - SVDTransformation: SVD-based orthogonality protocol for model transformation
    - RuntimeGating: Dynamic neuron gating mechanism
    - WINAConfig: Configuration management for WINA parameters
    - WINAMetrics: Performance monitoring and GFLOPs tracking

Integration Points:
    1. Internal ACGS LLM Optimization (GS Engine)
    2. Governed System LLM Oversight (EC Layer)

Usage:
    >>> from wina import WINACore, WINAConfig
    >>> config = WINAConfig(target_sparsity=0.6, gflops_reduction_target=0.5)
    >>> wina = WINACore(config)
    >>> optimized_output = await wina.optimize_inference(model, input_data)
"""

from .config import WINAConfig, WINAIntegrationConfig
from .constitutional_integration import ConstitutionalWINASupport
from .core import WINACore, WINAOptimizer
from .exceptions import WINAConfigurationError, WINAError, WINAOptimizationError
from .gating import (
    GatingDecision,
    GatingPerformance,
    GatingStrategy,
    NeuronGate,
    RuntimeGating,
)
from .metrics import GFLOPsTracker, PerformanceMonitor, WINAMetrics
from .svd_transformation import OrthogonalityProtocol, SVDTransformation

__version__ = "1.0.0"
__author__ = "ACGS-PGP Development Team"

__all__ = [
    # Core components
    "WINACore",
    "WINAOptimizer",
    "SVDTransformation",
    "OrthogonalityProtocol",
    "RuntimeGating",
    "NeuronGate",
    "GatingStrategy",
    "GatingDecision",
    "GatingPerformance",
    # Configuration
    "WINAConfig",
    "WINAIntegrationConfig",
    # Monitoring
    "WINAMetrics",
    "GFLOPsTracker",
    "PerformanceMonitor",
    # Constitutional integration
    "ConstitutionalWINASupport",
    # Exceptions
    "WINAError",
    "WINAConfigurationError",
    "WINAOptimizationError",
]
