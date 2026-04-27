from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload, joinedload,\
    with_loader_criteria
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
    study_group_id: Mapped[int] = mapped_column(ForeignKey('study_groups.id'))
    is_login: Mapped[bool] = mapped_column(default=False)
    last_event: Mapped[int] = mapped_column(
        Integer,
        server_default= text('(UNIX_TIMESTAMP())'),
        onupdate = text('UNIX_TIMESTAMP()')
    )

    study_group = relationship('StudyGroupModel', back_populates='user')
    akademy_grade = relationship('AkademyGradeModel', back_populates='user')
    dean_grade = relationship('DeanGradeModel', back_populates='user')
    user_tg = relationship('UserTgModel', back_populates='user')

class StudyGroupModel(Base):
    __tablename__ = 'study_groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    user = relationship('UserModel', back_populates='study_group')

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

class AchievementModel(Base):
    __tablename__ = 'achievements'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('telegram_data.id'))
    status: Mapped[str] = mapped_column(String(30), default='viewing')
    category: Mapped[str] = mapped_column(String(300))
    grade: Mapped[float] = mapped_column(default=0.0)
    description: Mapped[Optional[str]] = mapped_column(String(500), default=None, server_default=text('NULL'))
    file_path: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())')
    )

    user_tg = relationship('UserTgModel', back_populates='achievement')

class UserTgModel(Base):
    __tablename__ = 'telegram_data'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    is_banned: Mapped[bool] = mapped_column(default=False, server_default=text('false'))
    tg_name: Mapped[str] = mapped_column(String(255))

    user = relationship('UserModel', back_populates='user_tg')
    achievement = relationship('AchievementModel', back_populates='user_tg')

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

class AchievementAddSchema(BaseModel):
    user_tg_id: int
    status: str
    category: str
    grade: float
    description: Optional[str] = None
    file_path: str
    file_type: str

class UserTgAddSchema(BaseModel):
    user_id: int
    is_banned: bool
    tg_name: str


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

async def add_bd_achievement(data: AchievementAddSchema):
    async with new_session() as session:
        new_achievement = AchievementModel(
            user_tg_id=data.user_tg_id,
            status=data.status,
            category=data.category,
            grade=data.grade,
            description=data.description,
            file_path=data.file_path,
            file_type=data.file_type
        )
        session.add(new_achievement)
        await session.commit()

        return {'ok': True}

async def add_user_tg(data: UserTgAddSchema):
    async with new_session() as session:
        new_tg = UserTgModel(
            user_id=data.user_id,
            is_banned=data.is_banned,
            tg_name=data.tg_name,
        )
        session.add(new_tg)
        await session.commit()

        return {'ok': True}

async def get_users_rating_by_group(group_id=None): #Только для академика
    async with new_session() as session:
        query = select(UserModel).options(
            selectinload(UserModel.akademy_grade).joinedload(AkademyGradeModel.course),
            selectinload(UserModel.dean_grade).joinedload(DeanGradeModel.course),
            joinedload(UserModel.study_group),
            joinedload(UserModel.user_tg).joinedload(UserTgModel.achievement),
            with_loader_criteria(AchievementModel, AchievementModel.status == 'approve')
        )

        if group_id:
            query = query.where(UserModel.study_group_id == group_id)

        result_sql = await session.execute(query)

        users = result_sql.unique().scalars().all()
        result = []

        for user in users:
            sum_akademy_grades = 0.0
            sum_dean_grades = 0.0

            for grade in user.akademy_grade:
                sum_akademy_grades += grade.grade * grade.course.weight
            for grade in user.dean_grade:
                sum_dean_grades += grade.grade * grade.course.weight

            grade_group_by_activity = {
                'study_activity': sum_akademy_grades + sum_dean_grades,
                'science_activity': 0.0,
                'social_activity': 0.0,
                'culture_activity': 0.0,
                'general_rating': 0.0
            }

            for linked_telegram in user.user_tg:
                for achievement in linked_telegram.achievement:
                    if achievement.category == 'Учебная активность':
                        grade_group_by_activity['study_activity'] += achievement.grade
                    elif achievement.category == 'Научная активность':
                        grade_group_by_activity['science_activity'] += achievement.grade
                    elif achievement.category == 'Социальная активность':
                        grade_group_by_activity['social_activity'] += achievement.grade
                    else:
                        grade_group_by_activity['culture_activity'] += achievement.grade

                    grade_group_by_activity['general_rating'] += achievement.grade

            print(grade_group_by_activity)

            result.append({
                'id': user.id,
                'user_name': user.name,
                'grade_group_by_activity': grade_group_by_activity,
            })

        result.sort(key=lambda x: x['grade_group_by_activity']['general_rating'], reverse=True)

        return result

 # УБРАТЬ
async def get_user_data_by_login(login: str):
    async with new_session() as session:
        query = select(UserModel).options(
            joinedload(UserModel.user_tg),
            joinedload(UserModel.study_group)
        ).where(UserModel.login == login)

        result_sql = await session.execute(query)
        user_data = result_sql.unique().scalars().all()

        linked_telegrams = []

        for data in user_data:
            result = {
                'user_fio': data.name,
                'user_group': data.study_group.name
            }
            for tg_account in data.user_tg:
                linked_telegrams.append(tg_account.tg_name)

        result['linked_telegrams'] = linked_telegrams
        return result

async def get_user_achievements(login: str):
    async with new_session() as session:
        query = select(UserModel).options(
            joinedload(UserModel.user_tg).joinedload(UserTgModel.achievement),
        ).where(UserModel.login == login)

        result_sql = await session.execute(query)
        user_achievements = result_sql.unique().scalars().one()

        achievements = []
        for linked_telegram in user_achievements.user_tg:
            for achievement in linked_telegram.achievement:
                achievements.append({
                    'categories': achievement.category,
                    'status': achievement.status,
                    'grade': achievement.grade,
                    #Дописать с весом
                })

        return achievements

async def get_user_activity_info(login: str):
    async with new_session() as session:
        query = select(UserModel).options(
            joinedload(UserModel.akademy_grade),
            joinedload(UserModel.dean_grade),
            joinedload(UserModel.user_tg).joinedload(UserTgModel.achievement)
        ).where(UserModel.login == login)

        result_sql = await session.execute(query)
        user_activity_info = result_sql.unique().scalars().one()

        sum_akademy_grades = 0.0
        sum_dean_grades = 0.0

        for grade in user_activity_info.akademy_grade:
            sum_akademy_grades += grade.grade * grade.course.weight
        for grade in user_activity_info.dean_grade:
            sum_dean_grades += grade.grade * grade.course.weight

        activity_info = {
            'study_activity': sum_akademy_grades + sum_dean_grades,
            'science_activity': 0.0,
            'social_activity': 0.0,
            'culture_activity': 0.0,
            'general_rating': 0.0
        }

        for linked_telegram in user_activity_info.user_tg:
            for achievement in linked_telegram.achievement:
                if achievement.category == 'Учебная активность':
                    activity_info['study_activity'] += achievement.grade
                elif achievement.category == 'Научная активность':
                    activity_info['science_activity'] += achievement.grade
                elif achievement.category == 'Социальная активность':
                    activity_info['social_activity'] += achievement.grade
                else:
                    activity_info['culture_activity'] += achievement.grade

                activity_info['general_rating'] += achievement.grade

        return activity_info

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

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as ex:
        print(ex)
