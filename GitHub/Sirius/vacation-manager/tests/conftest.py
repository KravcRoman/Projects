import pytest
import pytest_asyncio # Use pytest_asyncio for async fixtures
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app # Import your FastAPI app
from app.core.db import Base, get_db
from app.core.config import settings
import os

# Determine Database URL for testing
# Prefer TEST_DATABASE_URL from env, fallback to DATABASE_URL, then default logic
TEST_DB_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DB_URL:
    # Append _test to the regular DB name if TEST_DATABASE_URL is not set
    # This requires careful splitting and rebuilding of the URL string
    if settings.DATABASE_URL:
        db_url_parts = str(settings.DATABASE_URL).split('/')
        db_name = db_url_parts[-1]
        test_db_name = f"{db_name}_test"
        db_url_parts[-1] = test_db_name
        TEST_DB_URL = "/".join(db_url_parts)
    else:
        # Fallback if even DATABASE_URL is somehow not assembled yet (shouldn't happen)
        test_db_name = f"{settings.POSTGRES_DB}_test"
        TEST_DB_URL = str(settings.DATABASE_URL).replace(settings.POSTGRES_DB, test_db_name)
        # More robust assembly might be needed depending on URL format complexity

# Ensure the test URL is different from the main DB URL
assert TEST_DB_URL != str(settings.DATABASE_URL), "Test database URL must be different from main DB URL"

# Create async engine for testing
test_engine = create_async_engine(TEST_DB_URL, echo=False)

# Create session factory for testing
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Creates and drops the test database tables for the entire test session."""
    async with test_engine.begin() as conn:
        # Drop all tables first (optional, clean slate)
        # await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield # Run the tests
    async with test_engine.begin() as conn:
        # Drop all tables after tests run
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields a database session that rolls back changes after the test."""
    async with TestingSessionLocal() as session:
        # Start a transaction
        await session.begin_nested() # Use nested transactions for rollback per test
        yield session
        # Rollback transaction after test finishes
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provides an async test client that uses the test database session."""

    # Dependency override for get_db
    def override_get_db():
        try:
            yield db_session
        finally:
            # The session rollback is handled by the db_session fixture
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Create and yield the test client
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    # Clean up dependency override
    del app.dependency_overrides[get_db]