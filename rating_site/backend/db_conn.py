from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db_models import Base
from db_create import create_database

import asyncio

#For local bd
engine = create_async_engine('mysql+asyncmy://root:1234@localhost/grades_db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def setup_grades():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await create_database()
    await setup_grades()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as ex:
        print(ex)