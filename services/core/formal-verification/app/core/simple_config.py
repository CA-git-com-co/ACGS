"""
Simple configuration for formal verification service testing.
Constitutional hash: cdd01ef066bc6cf2
"""


class Settings:
    """Simplified configuration settings for formal verification."""

    # Z3 Solver settings
    Z3_TIMEOUT_MS = 5000
    ENABLE_UNSAT_CORE = True
    ENABLE_PROOF_GENERATION = False  # Disabled for performance

    # Constitutional principles
    CONSTITUTIONAL_PRINCIPLES = {
        "non_maleficence": {
            "id": "non_maleficence",
            "name": "Non-maleficence",
            "formal_spec": "harmful actions are not permitted",
        },
        "human_autonomy": {
            "id": "human_autonomy",
            "name": "Human Autonomy",
            "formal_spec": "do not override human decisions",
        },
        "transparency": {
            "id": "transparency",
            "name": "Transparency",
            "formal_spec": "actions must be auditable and explainable",
        },
        "least_privilege": {
            "id": "least_privilege",
            "name": "Least Privilege",
            "formal_spec": "permissions must be necessary",
        },
        "data_protection": {
            "id": "data_protection",
            "name": "Data Protection",
            "formal_spec": "sensitive data must be protected",
        },
    }

    # Constitutional hash for compliance
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Global settings instance
settings = Settings()
