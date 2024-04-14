"""
https://github.com/kvesteri/sqlalchemy-utils/issues/611#issuecomment-1448480978
"""
from functools import lru_cache
from contextlib import asynccontextmanager
from asyncio import current_task

from sqlalchemy.ext.asyncio import (create_async_engine, async_sessionmaker, AsyncSession,
                                    AsyncEngine, async_scoped_session)
from sqlalchemy.orm import DeclarativeBase

from data_base.settings import get_config


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> AsyncEngine:
    # return create_async_engine(get_config().connection_string, poolclass=NullPool)
    return create_async_engine(get_config().connection_string)


@lru_cache
def get_session_maker():
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncSession:
    async_session_maker = get_session_maker()
    session = async_session_maker(autoflush=False, autocommit=False)
    try:
        yield session
    finally:
        await session.close()


@asynccontextmanager
async def scoped_session():
    scoped_factory = async_scoped_session(
        get_session_maker(),
        scopefunc=current_task,
    )
    try:
        async with scoped_factory() as s:
            yield s
    finally:
        await scoped_factory.remove()
