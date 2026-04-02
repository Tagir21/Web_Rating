from django.db.models import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
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
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('telegram_data.id'))
    status: Mapped[str] = mapped_column(String(30), default='viewing')
    categories: Mapped[str] = mapped_column(String(300))
    file_path: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())')
    )

    user_tg = relationship('UserTg', back_populates='achievement')

class UserTg(Base):
    __tablename__ = 'telegram_data'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    is_banned: Mapped[bool] = mapped_column(default=False, server_default=text('false'))
    tg_name: Mapped[str] = mapped_column(String(255))

    user = relationship('UserModel', back_populates='user_tg')
    achievement = relationship('Achievement', back_populates='user_tg')

class AchievementAddSchema(BaseModel):
    user_tg_id: int
    status: str
    categories: str
    file_path: str
    file_type: str

class UserTgAddSchema(BaseModel):
    user_id: int
    is_banned: bool
    tg_name: str

async def add_bd_achievement(data: AchievementAddSchema):
    async with new_session() as session:
        new_achievement = Achievement(
            user_tg_id=data.user_tg_id,
            status=data.status,
            categories=data.categories,
            file_path=data.file_path,
            file_type=data.file_type
        )
        session.add(new_achievement)
        await session.commit()

        return {'ok': True}

async def add_user_tg(data: UserTgAddSchema):
    async with new_session() as session:
        new_tg = UserTg(
            user_id=data.user_id,
            is_banned=data.is_banned,
            tg_name=data.tg_name,
        )
        session.add(new_tg)
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