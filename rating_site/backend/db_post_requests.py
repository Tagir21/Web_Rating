from schems import (
    AkademyGradeAddSchema,
    DeanGradeAddSchema,
    UserAddSchema,
    CourseAddSchema,
    AchievementAddSchema,
    WebAchievementAddSchema,
    UserTgAddSchema,

)

from db_models import (
    AkademyGradeModel,
    DeanGradeModel,
    UserModel,
    CourseModel,
    AchievementModel,
    UserTgModel
)

from db_get_requests import (
    get_category_data,
)

from sqlalchemy import select

from maps import CATEGORY_MAP

from db_conn import new_session

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
            category_id=data.category_id,
            file_path=data.file_info.file_path,
            file_type=data.file_info.file_type
        )
        session.add(new_achievement)
        await session.commit()

        return {'ok': True}

async def add_web_achievement(data: WebAchievementAddSchema):
    async with (new_session() as session):
        query = (select(UserTgModel)
        .join(UserModel)
        .where(UserModel.login == data.login)
        .where(UserTgModel.id == data.user_tg_id)
        .where(UserTgModel.is_banned == False))

        result_sql = await session.execute(query)
        tg_account = result_sql.scalars().first()


        if not tg_account:
            return {
                'ok': False,
                'error': 'User_tg does not exist'
            }

        category_ids_list = []

        category_data_map = await get_category_data()

        for category in data.categories:
            category_name = CATEGORY_MAP.get(category, category)
            category_id = (category_data_map.get(category_name))['id']

            category_ids_list.append(category_id)

        new_achievement = AchievementModel(
            user_tg_id = data.user_tg_id,
            status = 'viewing',
            category_id = tuple(category_ids_list),
            grade = 0.0,
            description = data.description,
            file_path = data.file_info.file_path,
            file_type = data.file_info.file_type,
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