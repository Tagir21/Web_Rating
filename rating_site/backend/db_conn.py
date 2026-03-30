from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy import String, Integer, ForeignKey, select
from pydantic import BaseModel
from sqlalchemy.sql.expression import text
from typing import Optional

from db_create import create_database

import asyncio

#For local bd
engine = create_async_engine('mysql+asyncmy://root:1234@localhost/grades_db')

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

    akademy_grade = relationship('AkademyGradeModel', back_populates='user')
    dean_grade = relationship('DeanGradeModel', back_populates='user')

class AkademyGradeModel(Base):
    __tablename__ = 'academy_grades'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    grade: Mapped[float] = mapped_column(default=0.0)
    last_update: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())'),
        onupdate=text('(UNIX_TIMESTAMP())')
    )

    user = relationship('UserModel', back_populates='akademy_grade')
    course = relationship('CourseModel', back_populates='akademy_grade')

class DeanGradeModel(Base):
    __tablename__ = 'dean_grades'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    count_of_retake: Mapped[int] = mapped_column(default=0)
    grade: Mapped[float] = mapped_column(default=0.0)
    last_update: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())'),
        onupdate=text('(UNIX_TIMESTAMP())')
    )

    user = relationship('UserModel', back_populates='dean_grade')
    course = relationship('CourseModel', back_populates='dean_grade')

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

    akademy_grade = relationship('AkademyGradeModel', back_populates='course')
    dean_grade = relationship('DeanGradeModel', back_populates='course')

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

class DeanGradeAddSchema(BaseModel):
    user_id: int
    course_id: int
    count_of_retake: int
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

async def add_dean_grade(data: DeanGradeAddSchema):
    async with new_session() as session:
        new_grade = DeanGradeModel(
            user_id = data.user_id,
            course_id = data.course_id,
            count_of_retake = data.count_of_retake,
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

async def get_all_users(): #Только для академика
    async with new_session() as session:
        query = select(UserModel).options(
            selectinload(UserModel.akademy_grade).joinedload(AkademyGradeModel.course),
            selectinload(UserModel.dean_grade).joinedload(DeanGradeModel.course)
        )
        result_sql = await session.execute(query)

        users = result_sql.scalars().all()
        result = []

        for user in users:
            sum_akademy_grades = 0.0
            sum_dean_grade = 0.0
            for grade in user.akademy_grade:
                sum_akademy_grades += grade.grade * grade.course.weight
            for grade in user.dean_grade:
                sum_dean_grade += grade.grade * grade.course.weight

            result.append({
                'id': user.id,
                'user_name': user.name,
                'grade': sum_akademy_grades + sum_dean_grade
            })

        return result

async def main():
    await create_database()
    await setup_grades()
    # await add_user(UserAddSchema(name='Батталов Тагир Вадимович', login='student134235', password='Testik=56'))
    # await add_user(UserAddSchema(name='Акишин Илья Сергеевич', login='student134231', password='Testik=56'))
    # await add_course(CourseAddSchema(course=2, teacher_name='Светлана Сергеевна', course_name='BigData', weight=2))
    # await add_akademy_grade(AkademyGradeAddSchema(user_id=1, course_id=1, grade=50.000))
    # await add_akademy_grade(AkademyGradeAddSchema(user_id=2, course_id=1, grade=74.000))
    # await add_akademy_grade(AkademyGradeAddSchema(user_id=2, course_id=1, grade=34.540))
    # await add_dean_grade(DeanGradeAddSchema(user_id=1, course_id=1, count_of_retake=4, grade=11.11))

    print(await get_all_users())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as ex:
        print(ex)

