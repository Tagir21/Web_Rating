from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer
from pydantic import BaseModel
from sqlalchemy.sql.expression import text
from typing import Optional

import asyncio

#For local bd
engine = create_async_engine('mysql+asyncmy://root:1234@localhost/grades_db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Achievement(Base):
    __tablename__ = 'achievements'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default='viewing')
    categories: Mapped[str] = mapped_column(String(300))
    file_path: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())')
    )

class User()

class AchievementAddSchema(BaseModel):
    user_name: str
    status: str
    categories: str
    file_path: str
    file_type: str

async def add_bd_achievement(data: AchievementAddSchema):
    async with new_session() as session:
        new_achievement = Achievement(
            user_name=data.user_name,
            status=data.status,
            categories=data.categories,
            file_path=data.file_path,
            file_type=data.file_type
        )
        session.add(new_achievement)
        await session.commit()

        return {'ok': True}



async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as ex:
        print(ex)