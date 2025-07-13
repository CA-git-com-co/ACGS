import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Load environment variables from .env file (especially for local development)
# In a containerized environment, these might be set directly.
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://youruser:yourpassword@postgres:5432/yourdatabase_auth",
)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_db():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_tables():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    # This is where you would import your models and call Base.metadata.create_all(engine)
    # For now, it's a placeholder. We'll call it from main.py
    # Actual table creation will be linked once models are fully in place and Base is confirmed.
    # For now, we are just setting up the structure.
    # We need to ensure all models that use a Base are imported before calling create_all.
    try:
        # If models are defined using the Base from services.shared.database, then:
        from services.shared.database import Base

        # Import all models here that should be created
        from services.shared.models import RefreshToken, User  # noqa

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        pass
        # For now, just continue without creating tables
