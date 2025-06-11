"""
AlphaEvolve Governance System Engine
====================================

This package provides the core functionalities for the AlphaEvolve Governance System,
including data structures for constitutional principles, operational rules, amendments,
and various services for policy synthesis, validation, and cryptographic operations.

Modules:
    core: Defines the fundamental data structures of the governance system.
    services: Provides services for LLM interaction, cryptography, policy synthesis, and validation.
    utils: Contains utility functions, such as logging.

Key Classes:
    - ConstitutionalPrinciple: Represents a high-level governance principle.
    - OperationalRule: Represents a specific, enforceable rule.
    - Amendment: Represents a proposed change to a principle or rule.
    - PolicySynthesizer: Service for generating and refining policies.
    - Various Validators (Syntactic, Semantic, Safety, Bias, Conflict): Services for policy validation.
    - LLMService: Interface for interacting with large language models.
    - CryptoService: Provides cryptographic utilities.

Example:
    >>> from alphaevolve_gs_engine.core import ConstitutionalPrinciple
    >>> principle = ConstitutionalPrinciple("CP001", "Harm Prevention", "...", "Safety", "...")
    >>> print(principle)
"""

# Expose key classes and functions at the package level for easier access.

from .core.amendment import Amendment

# From 'core' module
from .core.constitutional_principle import ConstitutionalPrinciple
from .core.operational_rule import OperationalRule
from .services.crypto_service import CryptoService, hash_data

# From 'services' module
from .services.llm_service import (
    LLMService,
    MockLLMService,
    OpenAILLMService,
    get_llm_service,
)
from .services.policy_synthesizer import (
    LLMPolicyGenerator,
    PolicySuggestion,
    PolicySynthesisInput,
    PolicySynthesizer,
)
from .services.validation.bias_validator import (
    BiasMetric,
    BiasValidator,
    FairnessMetricValidator,
    LLMBiasReviewer,
)
from .services.validation.conflict_validator import (
    ConflictDefinition,
    ConflictValidator,
    OPAConflictDetector,
)
from .services.validation.formal_verifier import (
    FormalVerificationProperty,
    FormalVerifier,
    MockFormalVerifier,
)
from .services.validation.safety_validator import (
    PatternBasedSafetyValidator,
    SafetyAssertion,
    SafetyValidator,
    SimulationBasedSafetyValidator,
)
from .services.validation.semantic_validator import (
    ScenarioBasedSemanticValidator,
    SemanticTestCase,
    SemanticValidator,
)

# From 'services.validation' sub-package (expose main validator classes)
from .services.validation.syntactic_validator import SyntacticValidator

# From 'utils' module
from .utils.logging_utils import setup_logger

__version__ = "0.1.0"  # Placeholder for versioning

__all__ = [
    # Core
    "ConstitutionalPrinciple",
    "OperationalRule",
    "Amendment",
    # Services
    "LLMService",
    "OpenAILLMService",
    "MockLLMService",
    "get_llm_service",
    "CryptoService",
    "hash_data",
    "PolicySynthesizer",
    "LLMPolicyGenerator",
    "PolicySynthesisInput",
    "PolicySuggestion",
    # Validation Services & Data Structures
    "SyntacticValidator",
    "SemanticValidator",
    "ScenarioBasedSemanticValidator",
    "SemanticTestCase",
    "FormalVerifier",
    "MockFormalVerifier",
    "FormalVerificationProperty",
    "SafetyValidator",
    "PatternBasedSafetyValidator",
    "SimulationBasedSafetyValidator",
    "SafetyAssertion",
    "BiasValidator",
    "FairnessMetricValidator",
    "LLMBiasReviewer",
    "BiasMetric",
    "ConflictValidator",
    "OPAConflictDetector",
    "ConflictDefinition",
    # Utils
    "setup_logger",
    # Version
    "__version__",
]

logger = setup_logger(__name__)
logger.info(f"AlphaEvolve Governance System Engine version {__version__} loaded.")
