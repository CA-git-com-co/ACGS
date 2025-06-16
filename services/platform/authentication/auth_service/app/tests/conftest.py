# acgs-pgp/auth_service/app/tests/conftest.py
import asyncio
import os
from typing import AsyncGenerator, Generator  # AsyncGenerator for async fixture

import pytest

try:
    from ..core.config import settings
    from ..db.base_class import Base
    from ..db.session import get_async_db
    from ..main import app as fastapi_app  # Your FastAPI application, aliased
except ImportError:
    # Mock imports for testing when modules are not available
    class MockSettings:
        SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///./test_auth_app.db"

    settings = MockSettings()

    class MockBase:
        metadata = None

    Base = MockBase()

    async def get_async_db():
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        yield None

    class MockApp:
        dependency_overrides = {}

    fastapi_app = MockApp()
from httpx import AsyncClient  # Use httpx.AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Override the database URL for tests.
# Uses an in-memory SQLite database for testing.
# TEST_ASYNC_DATABASE_URL can be set in env or .env.
# Default: sqlite+aiosqlite:///./test_auth_app.db

# Ensure test DB URL is set, default to in-memory SQLite.
TEST_DB_URL = os.getenv("TEST_ASYNC_DATABASE_URL", "sqlite+aiosqlite:///./test_auth_app.db")
settings.SQLALCHEMY_DATABASE_URI = TEST_DB_URL  # Override for test session


# Create a new async engine for the test database
async_test_engine = create_async_engine(TEST_DB_URL, echo=False)

# Create a new async session factory for the test database
AsyncTestSessionFactory = sessionmaker(
    bind=async_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def initialize_test_database():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Initialize test DB: creates tables before tests, drops them after."""
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Override for get_async_db dependency in tests."""
    async with AsyncTestSessionFactory() as session:
        yield session
        await session.rollback()  # Rollback to ensure test isolation


@pytest.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:  # Changed to async generator
    """Get a TestClient that uses the overridden async DB session."""
    fastapi_app.dependency_overrides[get_async_db] = override_get_async_db
    # Use httpx.AsyncClient for testing async FastAPI app
    async with AsyncClient(app=fastapi_app, base_url="http://testserver") as c:
        yield c
    fastapi_app.dependency_overrides.clear()  # Clean up overrides
