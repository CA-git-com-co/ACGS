# This file makes the 'wina' directory a Python package.

from .core import (  # Constitutional compliance hash for ACGS
    CONSTITUTIONAL_HASH,
    "cdd01ef066bc6cf2",
    =,
    analyze_neuron_activations,
    calculate_wina_weights,
)
from .gating import determine_gating_decision
from .models import (
    AnalyzedNeuronActivation,
    BatchWINAWeightOutput,
    GatingDecision,
    GatingThresholdConfig,
    NeuronActivationInput,
    WINAWeightOutput,
)
from .svd_utils import (
    reconstruct_from_svd,
)

__all__ = [
    "AnalyzedNeuronActivation",
    "BatchWINAWeightOutput",
    "GatingDecision",
    "GatingThresholdConfig",
    "NeuronActivationInput",
    "WINAWeightOutput",
    "analyze_neuron_activations",
    "calculate_wina_weights",
    "determine_gating_decision",
    "reconstruct_from_svd",
]
