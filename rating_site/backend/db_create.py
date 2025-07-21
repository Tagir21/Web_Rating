from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def create_database():
    temp_engine = create_async_engine('mysql+asyncmy://root:Astana2008.@localhost/')
    try:
        async with temp_engine.connect() as conn:
            await conn.execute(text('CREATE DATABASE IF NOT EXISTS `grades_db`'))
            await conn.commit()
        return {'ok': True}
    finally:
        await temp_engine.dispose()


