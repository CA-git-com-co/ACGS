"""
WINA (Weighted Intelligence Network Architecture) Package

This package provides the core WINA functionality for the evolutionary computation service,
including optimization, monitoring, and constitutional compliance integration.
"""

from .config import load_wina_config_from_env
from .core import WINACore
from .metrics import WINAMetrics
from .constitutional_integration import ConstitutionalWINASupport
from .gating import RuntimeGating, GatingStrategy
from .performance_monitoring import (
    WINAPerformanceCollector,
    WINAMonitoringLevel,
    WINAComponentType,
    WINASystemHealthMetrics,
    WINANeuronActivationMetrics,
    WINADynamicGatingMetrics,
    WINAIntegrationPerformanceMetrics,
    WINAConstitutionalComplianceMetrics
)
from .continuous_learning import (
    get_wina_learning_system,
    FeedbackSignal,
    FeedbackType
)

__version__ = "1.0.0"
__all__ = [
    "load_wina_config_from_env",
    "WINACore",
    "WINAMetrics", 
    "ConstitutionalWINASupport",
    "RuntimeGating",
    "GatingStrategy",
    "WINAPerformanceCollector",
    "WINAMonitoringLevel",
    "WINAComponentType",
    "WINASystemHealthMetrics",
    "WINANeuronActivationMetrics", 
    "WINADynamicGatingMetrics",
    "WINAIntegrationPerformanceMetrics",
    "WINAConstitutionalComplianceMetrics",
    "get_wina_learning_system",
    "FeedbackSignal",
    "FeedbackType"
]
