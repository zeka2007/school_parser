__all__ = ['BaseModel', 'Student', 'session_maker', 'create_database', 'async_engine']

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import config
from .base import BaseModel
from .student import Student

db_url = URL.create(
        "postgresql+asyncpg",
        username=config.postgres_username,
        password=config.postgres_password,
        host=config.postgres_host,
        port=config.postgres_port,
        database=config.postgres_db_name
    )

async_engine = create_async_engine(url=db_url, echo=config.debug)
session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def create_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)