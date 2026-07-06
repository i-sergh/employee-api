import pytest_asyncio
from sqlalchemy import Select, Insert, Delete
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from typing import AsyncGenerator

from config import get_pg_async_link

Base: DeclarativeMeta = declarative_base()

DATABASE_URL = get_pg_async_link(test=True)

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, 
                                        class_=AsyncSession,
                                        expire_on_commit=False,)


async def sub_async_session_macker():
    async with async_session_maker() as session:      
        yield session


@pytest_asyncio.fixture(scope="function")
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    session = sub_async_session_macker().__anext__()
    return await session
