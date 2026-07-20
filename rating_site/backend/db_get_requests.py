from db_models import (
    UserModel,
    AkademyGradeModel,
    DeanGradeModel,
    UserTgModel,
    AchievementModel,
    StudyGroupModel,
    CategoryDataModel,
)

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, with_loader_criteria

from db_conn import new_session

async def get_user_tg_accounts(login: str):
    async with new_session() as session:
        query = select(UserModel).options(
            selectinload(UserModel.user_tg),
        ).where(UserModel.login == login)

        result_sql = await session.execute(query)
        user = result_sql.scalars().first()

        if user is None:
            return {
                'ok': False,
                'error': 'User_tg does not exist',
                'telegram_accounts': []
            }

        telegram_accounts = []
        for tg_account in user.user_tg:
            if not tg_account.is_banned:
                telegram_accounts.append({
                    'id': tg_account.id,
                    'tg_name': tg_account.tg_name,
                })

        return {
            'ok': True,
            'telegram_accounts': telegram_accounts
        }

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

        category_data_map = await get_category_data()

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
                'general_rating': sum_akademy_grades + sum_dean_grades
            }

            for linked_telegram in user.user_tg:
                for achievement in linked_telegram.achievement:
                    if achievement.category_id == (category_data_map.get('Учебная активность'))['id']:
                        grade_group_by_activity['study_activity'] += achievement.grade
                    elif achievement.category_id == (category_data_map.get('Научная активность'))['id']:
                        grade_group_by_activity['science_activity'] += achievement.grade
                    elif achievement.category_id == (category_data_map.get('Социальная активность'))['id']:
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
            selectinload(UserModel.akademy_grade).joinedload(AkademyGradeModel.course),
            selectinload(UserModel.dean_grade).joinedload(DeanGradeModel.course),
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
            'general_rating': sum_akademy_grades + sum_dean_grades
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

async def get_all_groups():
    async with new_session() as session:
        query = select(StudyGroupModel)

        result_sql = await session.execute(query)
        all_groups = result_sql.scalars().all()

        return all_groups

async def get_category_data():
    async with new_session() as session:
        query = select(CategoryDataModel)

        result_sql = await session.execute(query)
        category_data = result_sql.scalars().all()

        result = {}
        for category in category_data:
            result[category.title] = {
                'id': category.id,
                'alias': category.alias,
                'weight': category.weight,
            }

        return result