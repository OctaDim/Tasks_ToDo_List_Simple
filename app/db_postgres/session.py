from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine)

from app.core.configs_postgres import get_postgres_configs

postgres_engine_url = get_postgres_configs().database_url
engine = create_async_engine(url=postgres_engine_url, future=True)
async_session_factory = async_sessionmaker(bind=engine,
                                           expire_on_commit=False,
                                           class_=AsyncSession)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
