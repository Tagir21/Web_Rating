from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db_conn import get_users_rating_by_group, get_user_data_by_login, get_user_achievements, get_user_activity_info

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001"],
    allow_methods=["GET"]
)

@app.get('/get_api_all_users')
async def get_all_api_users():
    all_users = await get_users_rating_by_group()
    print("Я работаю, всё ок")
    return {'users': all_users}

@app.get('/get_api_user_data/{login}')
async def get_api_user_data_by_login(login):
    user_data = await get_user_data_by_login(login)

    return user_data

@app.get('/get_api_users_rating_by_group/{group_id}')
async def get_api_users_rating_by_group(group_id):
    users_in_group = await get_users_rating_by_group(group_id)

    return {'users':users_in_group}

@app.get('/get_api_user_achievements_by_login/{login}')
async def get_api_user_achievements_by_login(login):
    achievements = await get_user_achievements(login)

    return {'achievements': achievements}

@app.get('/get_api_users_activity_info_by_login/{login}')
async def get_api_users_activity_info_by_login(login):
    user_activity_info = await get_user_activity_info(login)

    return {'user_activity_info': user_activity_info}