from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create async engine
engine = create_async_engine(str(settings.DATABASE_URL), pool_pre_ping=True, echo=False) # echo=True for SQL logging

# Create session factory bound to the engine
AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Important for async context
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()

# Dependency to get DB session in FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # Optional: commit here if you want auto-commit per request
            # await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()