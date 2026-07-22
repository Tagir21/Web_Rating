from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from rating_site.env_loader import (
    db_username,
    db_password,
    db_hostname,
    db_name,
    db_port,
)

async def create_database():
    temp_engine = create_async_engine(f'mysql+asyncmy://{db_username}:{db_password}@{db_hostname}:{db_port}')
    try:
        async with temp_engine.connect() as conn:
            await conn.execute(text('CREATE DATABASE IF NOT EXISTS `%s`'), (db_name,))
            await conn.commit()
        return {'ok': True}
    finally:
        await temp_engine.dispose()

