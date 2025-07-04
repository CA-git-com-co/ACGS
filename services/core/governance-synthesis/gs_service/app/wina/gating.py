from typing import Any

from .models import GatingDecision, GatingThresholdConfig, WINAWeightOutput

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



async def determine_gating_decision(
    wina_weights: WINAWeightOutput, gating_config: GatingThresholdConfig
) -> GatingDecision:
    """
    Determines which neurons/components should be active based on WINA weights
    and a gating threshold configuration.

    Args:
        wina_weights: The calculated WINA weights for neurons/components.
        gating_config: Configuration for the gating mechanism, including the threshold.

    Returns:
        A GatingDecision object representing the active/inactive state of each
        neuron/component.
    """
    gating_mask: dict[str, bool] = {}
    processed_ids = set()

    for neuron_id, weight in wina_weights.weights.items():
        gating_mask[neuron_id] = weight > gating_config.threshold
        processed_ids.add(neuron_id)

    # Consider any neuron IDs provided in metadata that were not in weights.
    all_neuron_ids_from_metadata = wina_weights.metadata.get("all_neuron_ids", [])
    for neuron_id in all_neuron_ids_from_metadata:
        if neuron_id not in processed_ids:
            gating_mask[neuron_id] = gating_config.default_gating_state
            processed_ids.add(neuron_id)

    decision_metadata: dict[str, Any] = {
        "gating_threshold_used": gating_config.threshold,
        "default_gating_state_used": gating_config.default_gating_state,
        "wina_calculation_method": wina_weights.metadata.get(
            "calculation_method", "unknown"
        ),
        "num_components_processed": len(processed_ids),
        "num_components_activated": sum(1 for active in gating_mask.values() if active),
    }

    return GatingDecision(gating_mask=gating_mask, metadata=decision_metadata)
