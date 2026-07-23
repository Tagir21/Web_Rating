from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.engine import URL

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

database_url = URL.create(
    drivername="mysql+asyncmy",
    username=db_username,
    password=db_password,
    host=db_hostname,
    port=int(db_port),
    database=db_name,
    query={"charset": "utf8mb4",},
)

engine = create_async_engine(database_url, pool_pre_ping=True)

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