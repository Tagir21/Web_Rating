from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, select
from pydantic import BaseModel
from sqlalchemy.sql.expression import text
from typing import Optional

from db_create import create_database

import asyncio

engine = create_async_engine('mysql+asyncmy://root:Astana2008.@localhost/grades_db')

new_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    is_login: Mapped[bool] = mapped_column(default=False)
    last_event: Mapped[int] = mapped_column(
        Integer,
        server_default= text('(UNIX_TIMESTAMP())'),
        onupdate = text('UNIX_TIMESTAMP()')
    )

    grade = relationship('AkademyGradeModel', back_populates='user')

class AkademyGradeModel(Base):
    __tablename__ = 'academy_grades'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    grade: Mapped[float]
    last_update: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())'),
        onupdate=text('(UNIX_TIMESTAMP())')
    )

    user = relationship('UserModel', back_populates='grade')
    course = relationship('CourseModel', back_populates='grade')

class CourseModel(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    course: Mapped[int]
    teacher_name: Mapped[str] = mapped_column(String(255))
    course_name: Mapped[str] = mapped_column(String(255))
    weight: Mapped[float]
    last_update: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())'),
        onupdate=text('(UNIX_TIMESTAMP())')
    )

    grade = relationship('AkademyGradeModel', back_populates='course')

async def setup_grades():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all(engine, tables=[Base.metadata.tables['grades']]))
        # await conn.run_sync(Base.metadata.drop_all(engine, tables=[Base.metadata.tables['users']]))
        await conn.run_sync(Base.metadata.create_all)

# class GeneralSchema(BaseModel):
#     id: int

class AkademyGradeAddSchema(BaseModel):
    user_id: int
    course_id: int
    grade: float

class UserAddSchema(BaseModel):
    name: str
    login: str
    password: str
    is_login: Optional[bool] = None

class CourseAddSchema(BaseModel):
    course: int
    teacher_name: str
    course_name: str
    weight: float


async def add_akademy_grade(data: AkademyGradeAddSchema):
    async with new_session() as session:
        new_grade = AkademyGradeModel(
            user_id = data.user_id,
            course_id = data.course_id,
            grade = data.grade
        )
        session.add(new_grade)
        await session.commit()

        return {'ok': True}

async def add_user(data: UserAddSchema):
    async with new_session() as session:
        new_user = UserModel(
            name = data.name,
            login = data.login,
            password = data.password,
            is_login = data.is_login,
        )
        session.add(new_user)
        await session.commit()

        return {'ok': True}

async def add_course(data: CourseAddSchema):
    async with new_session() as session:
        new_course = CourseModel(
            course = data.course,
            teacher_name = data.teacher_name,
            course_name = data.course_name,
            weight = data.weight
        )
        session.add(new_course)
        await session.commit()

        return {'ok': True}

async def get_all_grades(): #Только для академика
    async with new_session() as session:
        query = select(AkademyGradeModel)
        result_sql = await session.execute(query)

        result = [{
            'id': grade.id,
            'user_id': grade.user_id,
            'course_id': grade.course_id,
            'grade': grade.grade,
            'last_update': grade.last_update
        } for grade in result_sql.scalars().all()]

        return result

async def main():
    await create_database()
    await setup_grades()
    # await add_user(UserAddSchema(name='Батталов Тагир Вадимович', login='student134235', password='Testik=56'))
    # await add_user(UserAddSchema(name='Акишин Илья Сергеевич', login='student134231', password='Testik=56'))
    # await add_course(CourseAddSchema(course=2, teacher_name='Светлана Сергеевна', course_name='BigData', weight=2))
    # await add_akademy_grade(AkademyGradeAddSchema(user_id=4, course_id=1, grade=100.000))

    print(await get_all_grades())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as ex:
        print(ex)

