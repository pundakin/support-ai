from functools import lru_cache
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings


@lru_cache
def get_engine():
    """
    Creates and caches the async engine for database connection.

    lru_cache ensures that the engine is created once
    and reused throughout the application.
    """
    settings = get_settings()

    return create_async_engine(
        str(settings.DATABASE_URL),
        pool_pre_ping=True,  # Check connection before use
        pool_size=10,        # Connection pool size
        max_overflow=20,     # Additional connections under peak load
        echo=settings.is_dev # Log SQL queries in dev mode
    )


@lru_cache
def get_session_factory():
    """
    Creates and caches the session factory.

    Returns an async_sessionmaker that creates AsyncSession instances.
    """
    engine = get_engine()

    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: creates a session for a single request.

    Usage in endpoints:
    async with get_db_session() as session:
        # work with DB
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()