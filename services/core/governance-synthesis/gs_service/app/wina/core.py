import numpy as np  # Added for type hinting and example matrix
from typing import Any

from .models import AnalyzedNeuronActivation, NeuronActivationInput, WINAWeightOutput
from .svd_utils import apply_svd_transformation  # Added SVD import


async def analyze_neuron_activations(
    activation_input: NeuronActivationInput,
) -> list[AnalyzedNeuronActivation]:
    """
    Analyzes raw neuron activations to compute summary statistics.

    Args:
        activation_input: Raw neuron activation data.

    Returns:
        A list of analyzed neuron activation objects, each containing
        statistics like mean and variance for a neuron.
    """
    analyzed_activations: list[AnalyzedNeuronActivation] = []

    for neuron_id, activations in activation_input.activations.items():
        if not activations:
            # Handle cases with no activations for a neuron, if necessary
            # For now, we might skip or assign default values
            mean_activation = 0.0
            variance_activation = 0.0
        else:
            n = len(activations)
            mean_activation = sum(activations) / n if n > 0 else 0.0

            # Calculate variance
            if n > 1:
                variance_activation = sum(
                    (x - mean_activation) ** 2 for x in activations
                ) / (n - 1)
            else:
                variance_activation = (
                    0.0  # Variance is undefined for a single data point or no data
                )

        analyzed_activations.append(
            AnalyzedNeuronActivation(
                neuron_id=neuron_id,
                mean_activation=mean_activation,
                variance_activation=variance_activation,
                raw_activations_sample=activations[:10],  # Store a small sample
            )
        )
    return analyzed_activations


async def calculate_wina_weights(
    analyzed_activations: list[AnalyzedNeuronActivation],
    weight_matrices: dict[str, Any] | None = None,
    # Alternatively, could take NeuronActivationInput directly
    # activation_input: NeuronActivationInput
) -> WINAWeightOutput:
    """
    Calculates WINA (Weight Informed Neuron Activation) weights based on
    analyzed neuron activations and weight matrices.

    Implements the true WINA algorithm: weight = |x_i * ||W_:,i||_2|
    where x_i is the hidden state and ||W_:,i||_2 is the column-wise L2 norm.

    Args:
        analyzed_activations: A list of analyzed neuron activation objects.
        weight_matrices: Optional weight matrices for column norm calculation.

    Returns:
        A WINAWeightOutput object containing the calculated WINA weights.
    """
    weights: dict[str, float] = {}

    # Pre-compute column norms for efficiency (cache for reuse)
    column_norms = (
        await _compute_column_norms(weight_matrices) if weight_matrices else {}
    )

    for analysis in analyzed_activations:
        # True WINA algorithm: |x_i * ||W_:,i||_2|
        activation_value = analysis.mean_activation
        column_norm = column_norms.get(
            analysis.neuron_id, 1.0
        )  # Default to 1.0 if no weight matrix

        # WINA weight calculation with absolute value for magnitude
        wina_weight = abs(activation_value * column_norm)
        weights[analysis.neuron_id] = wina_weight

        # Further considerations for a real WINA algorithm:
        # - How does variance play a role? Higher variance might mean less stable/reliable.
        # - Are there thresholds for activation?
        # - How are weights normalized across a layer or the network?
        # - Interaction with SVD and gating mechanisms (for later subtasks).

    return WINAWeightOutput(
        weights=weights,
        metadata={"calculation_method": "true_wina_algorithm"},
    )


async def _compute_column_norms(weight_matrices: dict[str, Any]) -> dict[str, float]:
    """
    Compute column-wise L2 norms for weight matrices.

    Args:
        weight_matrices: Dictionary of weight matrices by layer/neuron ID

    Returns:
        Dictionary of column norms by neuron ID
    """
    column_norms = {}

    for layer_id, weight_matrix in weight_matrices.items():
        try:
            # Compute column-wise L2 norms
            if hasattr(weight_matrix, "norm"):
                # PyTorch tensor
                norms = weight_matrix.norm(dim=0, p=2).cpu().numpy()
            elif hasattr(weight_matrix, "shape"):
                # NumPy array
                norms = np.linalg.norm(weight_matrix, axis=0)
            else:
                # Fallback for other types
                continue

            # Map norms to neuron IDs
            for i, norm_value in enumerate(norms):
                neuron_id = f"{layer_id}_{i}"
                column_norms[neuron_id] = float(norm_value)

        except Exception as e:
            # Log error but continue processing
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to compute column norms for layer {layer_id}: {e}")
            continue

    return column_norms


# Example usage (for testing or integration later)
async def process_neuron_data_for_wina(
    activation_input: NeuronActivationInput,
) -> WINAWeightOutput:
    """
    Orchestrates the analysis of neuron activations and calculation of WINA weights.
    """
    analyzed_data = await analyze_neuron_activations(activation_input)
    wina_weights = await calculate_wina_weights(analyzed_data)
    return wina_weights


async def transform_matrix_with_svd(matrix: np.ndarray, k: int) -> np.ndarray:
    """
    Applies SVD-based transformation to a given matrix.

    This is a wrapper function to demonstrate calling the SVD utility
    from within the WINA core logic.

    Args:
        matrix: The input matrix (e.g., W_k, W_gate from an LLM layer).
        k: The number of singular values/vectors to retain.

    Returns:
        The transformed matrix with reduced dimensionality.
    """
    if not isinstance(matrix, np.ndarray):
        # In a real scenario, matrix loading/retrieval would happen here or be passed in.
        # For this example, we expect a NumPy array.
        raise TypeError("Input 'matrix' must be a NumPy array.")

    # The actual SVD transformation is not async, but we keep the function
    # async to align with FastAPI patterns if it were to involve I/O
    # for loading matrices in a real application.
    # For pure computation, it could be synchronous.
    transformed_matrix = apply_svd_transformation(matrix, k)
    return transformed_matrix


# Example of how transform_matrix_with_svd might be called (for testing/demonstration)
# async def example_svd_usage():
# requires: Valid input parameters
# ensures: Correct function execution
# sha256: func_hash
#     # This would typically be a weight matrix from an LLM
#     example_weight_matrix = np.random.rand(100, 50) # e.g., 100 features, 50 neurons
#     num_components_to_keep = 10
#
#     print(f"Original matrix shape: {example_weight_matrix.shape}")
#
#     reduced_matrix = await transform_matrix_with_svd(
#         example_weight_matrix,
#         num_components_to_keep
#     )
#
#     print(f"Reduced matrix shape: {reduced_matrix.shape}")
#     # The shape will be the same, but the rank is reduced.
#     # Further steps would involve using this reduced_matrix or its components
#     # in the WINA algorithm.
#
# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(example_svd_usage())
