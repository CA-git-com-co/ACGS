"""
WINA Exception Classes

Custom exceptions for WINA (Weight Informed Neuron Activation) operations
within the ACGS-PGP framework.
"""


class WINAError(Exception):
    """Base exception for all WINA-related errors."""


class WINAConfigurationError(WINAError):
    """Raised when WINA configuration is invalid or incomplete."""


class WINAOptimizationError(WINAError):
    """Raised when WINA optimization fails or produces invalid results."""


class WINATransformationError(WINAError):
    """Raised when SVD transformation fails or produces invalid matrices."""


class WINAGatingError(WINAError):
    """Raised when runtime gating mechanism encounters errors."""


class WINAMetricsError(WINAError):
    """Raised when performance metrics collection or calculation fails."""


class WINAConstitutionalError(WINAError):
    """Raised when constitutional integration encounters conflicts or violations."""
