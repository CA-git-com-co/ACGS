"""
Formal Verification Service Configuration

Manages configuration for formal verification and validation engine.
"""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Formal verification service configuration settings."""

    # Service identification
    SERVICE_NAME: str = "formal-verification-service"
    SERVICE_VERSION: str = "1.0.0"

    # Server configuration
    HOST: str = Field(default="0.0.0.0", env="FORMAL_VERIFICATION_HOST")
    PORT: int = Field(default=8010, env="FORMAL_VERIFICATION_PORT")
    DEBUG: bool = Field(default=False, env="FORMAL_VERIFICATION_DEBUG")

    # Constitutional configuration
    CONSTITUTIONAL_HASH: str = Field(
        default="cdd01ef066bc6cf2", env="CONSTITUTIONAL_HASH"
    )

    # Z3 SMT Solver configuration
    Z3_TIMEOUT_MS: int = Field(default=5000, env="Z3_TIMEOUT_MS")
    Z3_MAX_MEMORY_MB: int = Field(default=1024, env="Z3_MAX_MEMORY_MB")
    Z3_PARALLEL_CORES: int = Field(default=4, env="Z3_PARALLEL_CORES")

    # Verification configuration
    DEFAULT_VERIFICATION_TIMEOUT_S: int = Field(
        default=30, env="DEFAULT_VERIFICATION_TIMEOUT_S"
    )
    MAX_VERIFICATION_COMPLEXITY: int = Field(
        default=1000, env="MAX_VERIFICATION_COMPLEXITY"
    )
    ENABLE_PROOF_GENERATION: bool = Field(default=True, env="ENABLE_PROOF_GENERATION")
    ENABLE_UNSAT_CORE: bool = Field(default=True, env="ENABLE_UNSAT_CORE")

    # Cache configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/2", env="REDIS_URL")
    VERIFICATION_CACHE_TTL: int = Field(
        default=3600, env="VERIFICATION_CACHE_TTL"
    )  # 1 hour

    # Database configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost/formal_verification_db",
        env="DATABASE_URL",
    )

    # Service dependencies
    POLICY_GOVERNANCE_URL: str = Field(
        default="http://localhost:8003", env="POLICY_GOVERNANCE_URL"
    )
    CONSTITUTIONAL_AI_URL: str = Field(
        default="http://localhost:8002", env="CONSTITUTIONAL_AI_URL"
    )

    # Formal specification paths
    SPECS_DIRECTORY: str = Field(default="/app/specs", env="SPECS_DIRECTORY")
    PROOFS_DIRECTORY: str = Field(default="/app/proofs", env="PROOFS_DIRECTORY")

    # Constitutional principles definitions
    CONSTITUTIONAL_PRINCIPLES: dict[str, dict] = Field(
        default={
            "non_maleficence": {
                "id": "principle_001",
                "name": "Non-Maleficence",
                "description": "Agents must not cause harm to users, systems, or data",
                "formal_spec": "forall action. harmfulAction(action) -> not permitted(action)",
                "priority": 1,
            },
            "autonomy_respect": {
                "id": "principle_002",
                "name": "Human Autonomy",
                "description": "Agents must respect human decision-making authority",
                "formal_spec": "forall decision. humanDecision(decision) -> not override(agent, decision)",
                "priority": 2,
            },
            "transparency": {
                "id": "principle_003",
                "name": "Transparency",
                "description": "Agent actions must be auditable and explainable",
                "formal_spec": "forall action. agentAction(action) -> auditable(action) and explainable(action)",
                "priority": 3,
            },
            "least_privilege": {
                "id": "principle_004",
                "name": "Least Privilege",
                "description": "Agents must operate with minimum necessary permissions",
                "formal_spec": "forall agent permission. hasPermission(agent, permission) -> necessary(permission, agent.role)",
                "priority": 4,
            },
            "data_protection": {
                "id": "principle_005",
                "name": "Data Protection",
                "description": "Agents must protect sensitive data and privacy",
                "formal_spec": "forall data. sensitiveData(data) -> protected(data) and not leaked(data)",
                "priority": 5,
            },
        }
    )

    # Verification performance targets
    VERIFICATION_PERFORMANCE_TARGETS: dict[str, int] = Field(
        default={
            "simple_policy_verification_ms": 100,
            "complex_policy_verification_ms": 500,
            "batch_verification_s": 30,
            "incremental_verification_ms": 50,
        }
    )

    # Policy verification rules
    POLICY_VERIFICATION_RULES: dict[str, dict] = Field(
        default={
            "consistency": {
                "description": "No contradictory policies exist",
                "formal_rule": "not exists p1 p2. policy(p1) and policy(p2) and contradicts(p1, p2)",
            },
            "completeness": {
                "description": "All scenarios have applicable policies",
                "formal_rule": "forall scenario. exists policy. applicable(policy, scenario)",
            },
            "constitutional_compliance": {
                "description": "All policies comply with constitutional principles",
                "formal_rule": "forall policy principle. policy(policy) and principle(principle) -> complies(policy, principle)",
            },
            "termination": {
                "description": "Policy evaluation terminates in finite time",
                "formal_rule": "forall evaluation. terminates(evaluation) and bounded(evaluation.time)",
            },
        }
    )

    # Logging and monitoring
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9092, env="METRICS_PORT")

    # Development and testing
    ENABLE_TESTING_MODE: bool = Field(default=False, env="ENABLE_TESTING_MODE")
    GENERATE_VERIFICATION_REPORTS: bool = Field(
        default=True, env="GENERATE_VERIFICATION_REPORTS"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
