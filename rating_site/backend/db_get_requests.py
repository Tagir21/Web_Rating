from rating_site.backend.db_models import (
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

from rating_site.backend.db_conn import new_session

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
                'error': 'Данные об аккаунтах не найдены',
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

async def rating_calculate(user, category_data_map):
    sum_akademy_grades = 0.0
    sum_weighted_akademy_grades = 0.0
    sum_dean_grades = 0.0
    sum_weighted_dean_grades = 0.0

    for grade in user.akademy_grade:
        sum_akademy_grades += grade.grade
        sum_weighted_akademy_grades += grade.grade * grade.course.weight
    for grade in user.dean_grade:
        sum_dean_grades += grade.grade
        sum_weighted_dean_grades += grade.grade * grade.course.weight

    grade_group_by_activity = {
        'study_activity': sum_akademy_grades + sum_dean_grades,
        'science_activity': 0.0,
        'social_activity': 0.0,
        'culture_activity': 0.0,
        'general_rating': sum_akademy_grades + sum_dean_grades,
    }

    weighted_grade_group_by_activity = {
        'study_activity': sum_weighted_akademy_grades + sum_weighted_dean_grades,
        'science_activity': 0.0,
        'social_activity': 0.0,
        'culture_activity': 0.0,
        'general_weighted_rating': sum_weighted_akademy_grades + sum_weighted_dean_grades
    }

    for linked_telegram in user.user_tg:
        for achievement in linked_telegram.achievement:
            category_id = achievement.category_id
            if type(category_id) != int:
                category_id = category_id[0]

            if category_id == (category_data_map.get('Учебная активность'))['id']:
                grade = achievement.grade
                weighted_grade = grade * category_data_map.get('Учебная активность')['weight']
                grade_group_by_activity['study_activity'] += grade
                weighted_grade_group_by_activity['study_activity'] += weighted_grade
            elif category_id == (category_data_map.get('Научная активность'))['id']:
                grade = achievement.grade
                weighted_grade = grade * category_data_map.get('Научная активность')['weight']
                grade_group_by_activity['science_activity'] += grade
                weighted_grade_group_by_activity['science_activity'] += weighted_grade
            elif category_id == (category_data_map.get('Социальная активность'))['id']:
                grade = achievement.grade
                weighted_grade = grade * category_data_map.get('Социальная активность')['weight']
                grade_group_by_activity['social_activity'] += grade
                weighted_grade_group_by_activity['social_activity'] += weighted_grade
            else:
                grade = achievement.grade
                weighted_grade = grade * category_data_map.get('Культурно досуговая активность')['weight']
                grade_group_by_activity['culture_activity'] += grade
                weighted_grade_group_by_activity['culture_activity'] += weighted_grade

            grade_group_by_activity['general_rating'] += grade
            weighted_grade_group_by_activity['general_weighted_rating'] += weighted_grade

    return grade_group_by_activity, weighted_grade_group_by_activity

async def get_users_rating_by_group(group_id=None):
    async with (new_session() as session):
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
            grade_group_by_activity, weighted_grade_group_by_activity = await rating_calculate(user, category_data_map)

            result.append({
                'id': user.id,
                'user_name': user.name,
                'grade_group_by_activity': grade_group_by_activity,
                'weighted_grade_group_by_activity': weighted_grade_group_by_activity
            })

        result.sort(key=lambda x: x['weighted_grade_group_by_activity']['general_weighted_rating'], reverse=True)

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

        if not user_data:
            return {
                'ok': False,
                'error': 'Пользователь не найден'
            }

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
        user_achievements = result_sql.unique().scalars().one_or_none()

        if user_achievements is None:
            return {
                'ok': False,
                'error': f'Пользователя {login} не существует'
            }

        category_data_map = await get_category_data()

        achievements = []
        for linked_telegram in user_achievements.user_tg:
            for achievement in linked_telegram.achievement:
                if achievement.status == 'viewing':
                    achievements.append({
                        'categories': 'Заявка на модерации',
                        'status': 'На рассмотрении',
                        'grade': 0,
                        'weighted_grade': 0
                    })
                elif achievement.status == 'deny':
                    achievements.append({
                        'categories': 'Категории не валидны',
                        'status': 'Отклонена',
                        'grade': 0,
                        'weighted_grade': 0
                    })
                else:
                    category_id = achievement.category_id
                    if type(category_id) != int:
                        category_id = achievement.category_id[0]

                    category = [category for category, category_data in category_data_map.items() if (category_data['id'] == category_id)]
                    achievements.append({
                        'categories': category,
                        'status': 'Одобрена',
                        'grade': achievement.grade,
                        'weighted_grade': achievement.grade * category_data_map[category[0]]['weight']
                    })

        return achievements

async def get_user_activity_info(login: str):
    async with new_session() as session:
        query = select(UserModel).options(
            selectinload(UserModel.akademy_grade).joinedload(AkademyGradeModel.course),
            selectinload(UserModel.dean_grade).joinedload(DeanGradeModel.course),
            joinedload(UserModel.user_tg).joinedload(UserTgModel.achievement),
            with_loader_criteria(AchievementModel, AchievementModel.status == 'approve')
        ).where(UserModel.login == login)

        result_sql = await session.execute(query)
        user = result_sql.unique().scalars().one_or_none()

        if user is None:
            return {
                'ok': False,
                'error': f'Пользователя {login} не существует'
            }

        category_data_map = await get_category_data()

        grade_group_by_activity, weighted_grade_group_by_activity = await rating_calculate(user, category_data_map)

        return grade_group_by_activity

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