"""Database connection and session management."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.database import Base

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync engine for migrations and initial setup
sync_engine = create_engine(
    settings.database_url_sync,
    echo=settings.debug,
    future=True,
)

# Sync session maker
SessionLocal = sessionmaker(
    sync_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """
    Get synchronous database session.

    Returns:
        Session: Database session
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        # Create vector extension if not exists
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all database tables (use with caution!)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Export engine for Alembic
engine = async_engine
