"""
WINA (Weighted Intelligence Network Architecture) Package

This package provides the core WINA functionality for the evolutionary computation service,
including optimization, monitoring, and constitutional compliance integration.
"""

from .config import load_wina_config_from_env
from .constitutional_integration import ConstitutionalWINASupport
from .continuous_learning import FeedbackSignal, FeedbackType, get_wina_learning_system
from .core import WINACore
from .gating import GatingStrategy, RuntimeGating
from .metrics import WINAMetrics
from .performance_monitoring import (
    WINAComponentType,
    WINAConstitutionalComplianceMetrics,
    WINADynamicGatingMetrics,
    WINAIntegrationPerformanceMetrics,
    WINAMonitoringLevel,
    WINANeuronActivationMetrics,
    WINAPerformanceCollector,
    WINASystemHealthMetrics,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

__version__ = "1.0.0"
__all__ = [
    "CONSTITUTIONAL_HASH",
    "ConstitutionalWINASupport",
    "FeedbackSignal",
    "FeedbackType",
    "GatingStrategy",
    "RuntimeGating",
    "WINAComponentType",
    "WINAConstitutionalComplianceMetrics",
    "WINACore",
    "WINADynamicGatingMetrics",
    "WINAIntegrationPerformanceMetrics",
    "WINAMetrics",
    "WINAMonitoringLevel",
    "WINANeuronActivationMetrics",
    "WINAPerformanceCollector",
    "WINASystemHealthMetrics",
    "get_wina_learning_system",
    "load_wina_config_from_env",
]
