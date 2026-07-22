from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from rating_site.backend.db_models import Base
from rating_site.backend.db_create import create_database

import asyncio

from rating_site.env_loader import (
    db_username,
    db_password,
    db_hostname,
    db_name,
    db_port,
)

engine = create_async_engine(f'mysql+asyncmy://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}')

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