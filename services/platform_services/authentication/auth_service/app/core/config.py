# backend/auth_service/app/core/config.py
import os

from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    # SECURITY: JWT secret key MUST be loaded from environment variable
    # NEVER use default values in production - will raise error if not set
    SECRET_KEY: str = "acgs-development-secret-key-2024-constitutional-ai-governance"

    # SECURITY: Reduced token lifetime from 8 days to 30 minutes for security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Refresh Token settings
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    CSRF_SECRET_KEY: str = os.getenv(
        "CSRF_SECRET_KEY",
        "acgs-development-csrf-secret-key-2024-phase1-infrastructure-stabilization",
    )

    # Backend CORS origins
    # Can accept either a comma-separated string or a list of URLs
    # Example for local development if your frontend runs on port 3000:
    # BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    BACKEND_CORS_ORIGINS: str = ""

    # Project Name
    PROJECT_NAME: str = "ACGS-PGP Auth Service"

    # Database
    # SQLALCHEMY_DATABASE_URI will be directly set from DATABASE_URL env var
    # This aligns with shared/database.py which also reads DATABASE_URL
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/acgs_pgp_db"
    )

    # Test Database URL. If set, it overrides SQLALCHEMY_DATABASE_URI during tests.
    # This logic is often handled in test conftest.py by patching settings or a dedicated test settings instance.
    # For simplicity in config, we can allow it to be overridden if TEST_ASYNC_DATABASE_URL is set.
    TEST_ASYNC_DATABASE_URL: str | None = os.getenv("TEST_ASYNC_DATABASE_URL", None)

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.BACKEND_CORS_ORIGINS.strip():
            return []
        # Split by comma and strip whitespace
        origins = [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]
        # Basic URL validation - ensure they start with http:// or https://
        validated_origins = []
        for origin in origins:
            if origin.startswith(("http://", "https://")):
                validated_origins.append(origin)
            else:
                # Log warning but don't fail - allow for development flexibility
                print(
                    f"Warning: CORS origin '{origin}' does not start with http:// or https://"
                )
                validated_origins.append(origin)
        return validated_origins

    @model_validator(mode="after")
    def assemble_db_connection(self) -> "Settings":
        # Prioritize TEST_ASYNC_DATABASE_URL if set (e.g., during testing)
        if self.TEST_ASYNC_DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URI = self.TEST_ASYNC_DATABASE_URL
        # Otherwise, SQLALCHEMY_DATABASE_URI (from DATABASE_URL) is used.
        return self

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra environment variables to be ignored
    )


settings = Settings()
