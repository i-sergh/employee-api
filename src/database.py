from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import MetaData

from typing import AsyncGenerator

from config import get_pg_async_link


DATABASE_URL = get_pg_async_link()

Base: DeclarativeMeta = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        
        yield session