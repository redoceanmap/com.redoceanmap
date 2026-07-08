from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> None:
    global engine, _session_factory
    if engine is not None:
        return
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
    _session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        init_engine()
    if _session_factory is None:
        raise RuntimeError("DB 엔진이 초기화되지 않았습니다.")
    async with _session_factory() as session:
        yield session


async def create_all_tables() -> None:
    if engine is None:
        init_engine()
    if engine is not None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    global engine, _session_factory
    if engine is not None:
        await engine.dispose()
    engine = None
    _session_factory = None
